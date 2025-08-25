import json
from pathlib import Path
import streamlit as st

REPORTS_PATH = Path("data/reports.jsonl")
st.title("Saved Reports")
if not REPORTS_PATH.exists():
    st.info("No reports yet.")
else:
    rows = [json.loads(line) for line in REPORTS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in reversed(rows[-50:]):
        with st.expander(f"📄 {row['result']['overall_score']}/100 • {row['idea'][:60]}…"):
            st.json(row)
