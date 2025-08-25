import os, json, time, uuid
from pathlib import Path
import streamlit as st
import requests   # <-- API call ke liye
from ui2 import API_BASE_URL   # <-- yaha se updated BASE URL ayega

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
REPORTS_PATH = DATA_DIR / "reports.jsonl"

st.title("Evaluate a Startup Idea")
st.caption("Paste your idea or deck summary. We’ll score & suggest next steps.")

with st.form("eval_form"):
    idea = st.text_area("Idea / Problem / Solution (or paste deck notes)", height=180)
    market = st.text_input("Target market / geography (optional)", placeholder="e.g., SMBs in MENA fintech")
    extras = st.text_area("Anything to emphasize? (optional)", height=80, placeholder="Traction, team, unit economics, etc.")
    submitted = st.form_submit_button("Run Evaluation", use_container_width=True)

if submitted and idea.strip():
    # --- Status: user-visible progress ---
    with st.status("Evaluating…", expanded=True) as status:
        st.write("🔎 Sending request to evaluator API…")
        time.sleep(0.3)

        try:
            # 🔗 Call backend API
            payload = {
                "idea": idea,
                "market": market,
                "extras": extras
            }
            response = requests.post(f"{API_BASE_URL}/evaluate", json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                st.write("✅ Got response from API")
            else:
                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                result = None

        except Exception as e:
            st.error(f"⚡ Connection failed: {e}")
            result = None

        status.update(label="Done", state="complete")

    if result:
        # --- Pretty Output ---
        s1, s2 = st.columns([1,1])
        with s1:
            st.metric("Overall Score", f"{result.get('overall_score', 0)}/100")
            st.write("### Breakdown")
            for k,v in result.get("scores", {}).items():
                st.progress(v/100.0, text=f"{k}: {v}")

        with s2:
            st.write("### Strengths")
            for s in result.get("strengths", []):
                st.success(s)
            st.write("### Key Risks")
            for r in result.get("risks", []):
                st.warning(r)

        st.write("### 7-day Action Plan")
        for i, step in enumerate(result.get("actions", []), 1):
            st.write(f"**{i}.** {step}")

        # Save report
        record = {
            "id": str(uuid.uuid4()),
            "ts": time.time(),
            "idea": idea, "market": market, "extras": extras,
            "result": result
        }
        with open(REPORTS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        st.download_button(
            "Download JSON report",
            data=json.dumps(record, indent=2, ensure_ascii=False),
            file_name="startup_evaluation.json",
            use_container_width=True
        )

else:
    st.info("Fill the form and click **Run Evaluation** to generate a report.")
