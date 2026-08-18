import json
import uuid
from datetime import datetime
import pandas as pd
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Requirements Traceability Matrix",
    page_icon="🔗",
    layout="wide"
)

# Schema & constants
REQUIREMENT_TYPES = ["User Story", "Technical Spec", "Compliance", "Non-Functional"]
REQUIREMENT_PRIORITIES = ["Low", "Medium", "High", "Critical"]
REQUIREMENT_STATUSES = ["Draft", "Approved", "Implemented", "Verified"]

MITIGATION_STATUSES = ["Not Started", "Planned", "In Progress", "Implemented", "Verified"]
TEST_STATUSES = ["Not Run", "Passed", "Failed", "Blocked"]

RTM_LINKS_COLUMNS = [
    "Link_ID", "Requirement_ID", "Risk_ID", "Link_Type", "Confidence",
    "Rationale", "Review_Status", "Mitigation_Status", "Test_Status", "Created_At",
]

_HEALTH_COLOR = {"Healthy": "🟢", "At Risk": "🟠", "Gap": "🔴", "Orphan": "⚪"}

def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

def _init_rtm_session_state():
    if "rtm_links" not in st.session_state:
        st.session_state["rtm_links"] = pd.DataFrame(columns=RTM_LINKS_COLUMNS)

def _load_requirements_register() -> pd.DataFrame:
    req_template = pd.DataFrame({
        "ID": ["REQ-001", "REQ-002"],
        "Title": ["User file upload", "Admin audit logging"],
        "Category": ["Technical", "Compliance"],
        "Type": ["User Story", "Compliance"],
        "Priority": ["High", "Critical"],
        "Status": ["Implemented", "Approved"],
    })

    col_dl, col_up = st.columns([1, 2])

      with col_up:
        uploaded_req_file = st.file_uploader(
            "Upload filled-in Requirements CSV/Excel:", type=["csv", "xlsx"], key="rtm_req_up"
        )
          
    with col_dl:
        req_csv = req_template.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Requirements Template",
            data=req_csv,
            file_name="requirements_template.csv",
            mime="text/csv",
            key="rtm_req_template_dl",
        )

  

    if uploaded_req_file is not None:
        try:
            data_requirements = (
                pd.read_csv(uploaded_req_file)
                if uploaded_req_file.name.endswith(".csv")
                else pd.read_excel(uploaded_req_file)
            )
            st.success("Requirements register loaded successfully!")
        except Exception:
            data_requirements = req_template.copy()
    else:
        data_requirements = pd.DataFrame({
            "ID": ["REQ-001", "REQ-002", "REQ-003", "REQ-004"],
            "Title": [
                "User file upload", "Admin audit logging",
                "Payment card tokenization", "Dark mode toggle",
            ],
            "Category": ["Technical", "Compliance", "Technical", "Product"],
            "Type": ["User Story", "Compliance", "Technical Spec", "User Story"],
            "Priority": ["High", "Critical", "Critical", "Low"],
            "Status": ["Implemented", "Approved", "Implemented", "Draft"],
        })

    return data_requirements

# Shared fallback risk dataset
data_risks = pd.DataFrame({
    "ID": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
    "Title": [
        "API Gateway Latency", "Key Developer Turnover",
        "Third-party Vendor Delay", "Compliance Scope Creep",
        "Database Scalability Limit",
    ],
    "Category": ["Technical", "Resource", "Supply Chain", "Legal", "Technical"],
    "Probability": ["High", "Medium", "Low", "High", "Medium"],
    "Impact": ["Critical", "High", "Medium", "High", "Critical"],
    "Score": [15, 9, 4, 12, 10],
    "Status": ["Open", "Open", "Mitigated", "Open", "Materialized"],
})

def _confirmed_links() -> pd.DataFrame:
    links = st.session_state["rtm_links"]
    return links[links["Review_Status"] == "Confirmed"]

def _risks_for_requirement(req_id: str, data_risks: pd.DataFrame) -> pd.DataFrame:
    links = _confirmed_links()
    risk_ids = links.loc[links["Requirement_ID"] == req_id, "Risk_ID"]
    return data_risks[data_risks["ID"].isin(risk_ids)]

def _compute_requirement_health(req_id: str, data_reqs: pd.DataFrame) -> str:
    links = _confirmed_links()
    req_links = links[links["Requirement_ID"] == req_id]
    if req_links.empty:
        return "Orphan"
    healthy = (req_links["Mitigation_Status"].isin(["Implemented", "Verified"])
               & (req_links["Test_Status"] == "Passed")).any()
    if healthy:
        return "Healthy"
    in_progress = req_links["Mitigation_Status"].isin(["Planned", "In Progress", "Implemented", "Verified"]).any()
    return "At Risk" if in_progress else "Gap"

def _find_orphan_requirements(data_requirements: pd.DataFrame) -> pd.DataFrame:
    linked_ids = set(_confirmed_links()["Requirement_ID"])
    return data_requirements[~data_requirements["ID"].isin(linked_ids)]

def _find_unmapped_risks(data_risks: pd.DataFrame) -> pd.DataFrame:
    linked_ids = set(_confirmed_links()["Risk_ID"])
    return data_risks[~data_risks["ID"].isin(linked_ids)]

def _find_unmitigated_linked_risks(data_risks: pd.DataFrame) -> pd.DataFrame:
    links = _confirmed_links()
    linked_ids = set(links["Risk_ID"])
    mitigated_ids = set(links.loc[links["Mitigation_Status"].isin(["Implemented", "Verified"]), "Risk_ID"])
    return data_risks[data_risks["ID"].isin(linked_ids - mitigated_ids)]

_RTM_SYSTEM_PROMPT = """You are a risk-mapping assistant inside a Requirements \
Traceability Matrix tool. Given one requirement and a shortlist of candidate \
risks, identify which risks this requirement genuinely implicates - i.e. \
implementing or failing to implement it could plausibly cause, increase, or \
be threatened by that risk.

Rules:
- Only return risks with a real causal or exposure relationship.
- Return an empty list if none of the candidates are relevant.
- confidence is 0.0-1.0: use 0.9+ only for an unambiguous, direct relationship.
- rationale must be one concise sentence.

Respond with ONLY valid JSON, no markdown fences, no preamble:
{"matches": [{"risk_id": "RSK-001", "confidence": 0.0, "rationale": "..."}]}
"""

def _shortlist_candidate_risks(req_row: pd.Series, data_risks: pd.DataFrame, top_k: int = 6) -> pd.DataFrame:
    stopwords = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "user", "users", "system", "should", "must", "can", "is", "are"}
    def tokens(text):
        return {w.lower() for w in str(text).split() if w.lower() not in stopwords and len(w) > 2}

    req_tokens = tokens(req_row["Title"]) | tokens(req_row.get("Category", ""))
    scored = []
    for _, risk in data_risks.iterrows():
        risk_tokens = tokens(risk["Title"]) | tokens(risk.get("Category", ""))
        overlap = len(req_tokens & risk_tokens)
        scored.append((risk, overlap))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    top = [r for r, score in scored if score > 0][:top_k]
    if not top:
        top = data_risks[data_risks["Category"] == req_row.get("Category", "")].head(top_k).to_dict("records")
        top = [pd.Series(r) for r in top]
    return pd.DataFrame(top) if top else data_risks.head(0)

def run_ai_mapping_pass(data_requirements: pd.DataFrame, data_risks: pd.DataFrame, confidence_floor: float = 0.5) -> int:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    orphans = _find_orphan_requirements(data_requirements)
    new_rows = []

    for _, req in orphans.iterrows():
        candidates = _shortlist_candidate_risks(req, data_risks)
        if candidates.empty:
            continue

        candidates_block = "\n".join(
            f"- {r['ID']}: {r['Title']} (category: {r.get('Category', 'n/a')})"
            for _, r in candidates.iterrows()
        )
        prompt = (f"Requirement {req['ID']}: {req['Title']}\n"
                  f"Category: {req.get('Category', 'n/a')}\n\nCandidate risks:\n{candidates_block}")

        try:
            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {"role": "system", "content": _RTM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception as e:
            st.error(f"API Error scoring {req['ID']}: {e}")
            continue

        raw = response.choices[0].message.content.strip()
        cleaned = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            continue

        valid_ids = set(candidates["ID"])
        for m in parsed.get("matches", []):
            if m.get("risk_id") not in valid_ids or float(m.get("confidence", 0)) < confidence_floor:
                continue
            new_rows.append({
                "Link_ID": _new_id("LNK"), "Requirement_ID": req["ID"], "Risk_ID": m["risk_id"],
                "Link_Type": "AI Suggested", "Confidence": float(m["confidence"]),
                "Rationale": m["rationale"], "Review_Status": "Pending Review",
                "Mitigation_Status": "Not Started", "Test_Status": "Not Run",
                "Created_At": datetime.now().isoformat(),
            })

    if new_rows:
        st.session_state["rtm_links"] = pd.concat(
            [st.session_state["rtm_links"], pd.DataFrame(new_rows)], ignore_index=True
        )
    return len(new_rows)


def render_requirements_traceability_section():
    _init_rtm_session_state()

    st.title("🔗 Requirements Traceability Matrix")
    st.markdown(
        "Trace each requirement to the risks it creates or depends on, and see at a glance "
        "which requirements have a real mitigation and passing test behind them."
    )

    st.markdown("##### 📁 Requirements Register")
    data_requirements = _load_requirements_register()

    reqs_with_health = data_requirements.copy()
    reqs_with_health["Health"] = reqs_with_health["ID"].apply(lambda r_id: _compute_requirement_health(r_id, data_requirements))
    total = len(reqs_with_health)
    healthy_pct = round(100 * (reqs_with_health["Health"] == "Healthy").sum() / total, 1) if total else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Coverage Health", f"{healthy_pct}%")
    k2.metric("Orphan Requirements", len(_find_orphan_requirements(data_requirements)))
    k3.metric("Unmapped Risks", len(_find_unmapped_risks(data_risks)))
    k4.metric("Unmitigated Linked Risks", len(_find_unmitigated_linked_risks(data_risks)))

    st.markdown("---")

    st.markdown("##### 🤖 AI-Powered Mapping")
    st.caption("Runs Groq against every requirement with no linked risk yet and proposes matches for review below.")
    if st.button("Run AI Mapping Pass on Orphan Requirements", type="primary", key="rtm_ai_map_btn"):
        with st.spinner("Querying Groq to map requirements to risks..."):
            count = run_ai_mapping_pass(data_requirements, data_risks)
        st.success(f"Generated {count} new suggestion(s) — review them below.")

    st.markdown("---")

    tab_matrix, tab_gaps, tab_ai = st.tabs([
        "Traceability Matrix", "Gap Analysis",
        f"AI Suggestions ({len(st.session_state['rtm_links'][st.session_state['rtm_links']['Review_Status'] == 'Pending Review'])})",
    ])

    with tab_matrix:
        priority_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        view = reqs_with_health.assign(
            _rank=reqs_with_health["Priority"].map(priority_rank).fillna(9)
        ).sort_values("_rank").drop(columns="_rank")

        for _, req in view.iterrows():
            icon = _HEALTH_COLOR.get(req["Health"], "")
            with st.expander(f"{icon} **{req['Title']}**  ·  `{req['ID']}`  ·  {req['Priority']} priority  ·  {req['Health']}"):
                linked_risks = _risks_for_requirement(req["ID"], data_risks)
                if linked_risks.empty:
                    st.warning("No risk mapped yet.")
                else:
                    links = _confirmed_links()
                    for _, risk in linked_risks.iterrows():
                        link_row = links[(links["Requirement_ID"] == req["ID"]) & (links["Risk_ID"] == risk["ID"])].iloc[0]
                        st.markdown(
                            f"→ **{risk['Title']}** (`{risk['ID']}`, score {risk['Score']})  \n"
                            f"&nbsp;&nbsp;&nbsp;&nbsp;Mitigation: *{link_row['Mitigation_Status']}*  |  Test: *{link_row['Test_Status']}*"
                        )

                with st.form(key=f"rtm_form_{req['ID']}", border=False):
                    c1, c2, c3 = st.columns(3)
                    risk_choice = c1.selectbox("Link risk", data_risks["ID"] + " — " + data_risks["Title"], key=f"rtm_risk_{req['ID']}")
                    mit_status = c2.selectbox("Mitigation status", MITIGATION_STATUSES, key=f"rtm_mit_{req['ID']}")
                    test_status = c3.selectbox("Test status", TEST_STATUSES, key=f"rtm_test_{req['ID']}")
                    if st.form_submit_button("Save link"):
                        risk_id = risk_choice.split(" — ")[0]
                        new_row = {
                            "Link_ID": _new_id("LNK"), "Requirement_ID": req["ID"], "Risk_ID": risk_id,
                            "Link_Type": "Manual", "Confidence": None, "Rationale": "",
                            "Review_Status": "Confirmed", "Mitigation_Status": mit_status,
                            "Test_Status": test_status, "Created_At": datetime.now().isoformat(),
                        }
                        st.session_state["rtm_links"] = pd.concat(
                            [st.session_state["rtm_links"], pd.DataFrame([new_row])], ignore_index=True
                        )
                        st.rerun()

    with tab_gaps:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Orphan requirements** — no risk coverage at all")
            orphans = _find_orphan_requirements(data_requirements)
            st.dataframe(orphans[["ID", "Title", "Priority"]], hide_index=True, use_container_width=True)
        with col_b:
            st.markdown("**Unmapped risks** — not traced to any requirement")
            unmapped = _find_unmapped_risks(data_risks)
            st.dataframe(unmapped[["ID", "Title", "Category", "Score"]], hide_index=True, use_container_width=True)

        unmitigated = _find_unmitigated_linked_risks(data_risks)
        if not unmitigated.empty:
            st.markdown("**Linked risks with no mitigation in progress**")
            st.dataframe(unmitigated[["ID", "Title", "Score"]], hide_index=True, use_container_width=True)

    with tab_ai:
        st.caption("AI-proposed links wait here until confirmed or rejected — nothing here counts toward coverage yet.")
        links = st.session_state["rtm_links"]
        pending = links[links["Review_Status"] == "Pending Review"]

        if pending.empty:
            st.info("No pending AI suggestions.")
        else:
            req_lookup = data_requirements.set_index("ID")["Title"]
            risk_lookup = data_risks.set_index("ID")["Title"]
            for _, s in pending.iterrows():
                req_title = req_lookup.get(s["Requirement_ID"], s["Requirement_ID"])
                risk_title = risk_lookup.get(s["Risk_ID"], s["Risk_ID"])
                with st.container(border=True):
                    st.markdown(f"**{req_title}** → **{risk_title}**")
                    st.caption(s["Rationale"])
                    st.progress(float(s["Confidence"]), text=f"{round(s['Confidence'] * 100)}% confidence")
                    c1, c2 = st.columns(2)
                    if c1.button("✓ Confirm", key=f"confirm_{s['Link_ID']}"):
                        idx = links.index[links["Link_ID"] == s["Link_ID"]]
                        st.session_state["rtm_links"].loc[idx, "Review_Status"] = "Confirmed"
                        st.session_state["rtm_links"].loc[idx, "Link_Type"] = "AI Confirmed"
                        st.rerun()
                    if c2.button("✗ Reject", key=f"reject_{s['Link_ID']}"):
                        st.session_state["rtm_links"] = links[links["Link_ID"] != s["Link_ID"]]
                        st.rerun()

    st.markdown("---")
    st.download_button(
        "📥 Download RTM Links (CSV)",
        data=st.session_state["rtm_links"].to_csv(index=False).encode("utf-8"),
        file_name="rtm_links.csv",
        mime="text/css",
        key="rtm_links_dl",
    )
    reload_file = st.file_uploader("Reload previously saved RTM Links CSV", type=["csv"], key="rtm_links_reload")
    if reload_file is not None and st.button("Reload links", key="rtm_links_reload_btn"):
        st.session_state["rtm_links"] = pd.read_csv(reload_file)
        st.rerun()

render_requirements_traceability_section()
