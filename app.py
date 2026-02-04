import json
from datetime import datetime

import streamlit as st

from classifier import classify_po
from taxonomy import TAXONOMY

st.set_page_config(page_title="PO Category Classifier", layout="wide")

EXAMPLES = {
    "DocuSign subscription": {
        "po_description": "DocuSign Inc - eSignature Enterprise Pro Subscription",
        "supplier": "DocuSign Inc",
    },
    "Laptop purchase": {
        "po_description": "Dell Latitude laptops for new hires",
        "supplier": "Dell",
    },
    "Security services": {
        "po_description": "Monthly office security services",
        "supplier": "Guardian Security",
    },
}

MAX_HISTORY = 20

if "history" not in st.session_state:
    st.session_state.history = []
if "po_description" not in st.session_state:
    st.session_state.po_description = ""
if "supplier" not in st.session_state:
    st.session_state.supplier = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_raw" not in st.session_state:
    st.session_state.last_raw = None
if "show_raw" not in st.session_state:
    st.session_state.show_raw = False

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@400;500;700&display=swap');

:root {
  --bg: #f5f2ed;
  --panel: #ffffff;
  --ink: #1f1f1f;
  --muted: #5b5b5b;
  --accent: #0a7f6f;
  --accent-2: #f0a500;
  --line: #e6e0d7;
  --shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
  --radius: 16px;
}

.stApp {
  background: radial-gradient(circle at top left, #fff7e5 0%, #f5f2ed 45%, #ecf3f1 100%);
  color: var(--ink);
  font-family: "Space Grotesk", sans-serif;
}

h1, h2, h3 {
  font-family: "Fraunces", serif;
  color: var(--ink);
}

p, label, span, div {
  font-family: "Space Grotesk", sans-serif;
}

div[data-testid="stForm"] {
  background: var(--panel);
  padding: 20px;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

div[data-testid="stSidebar"] {
  background: #0f2d2a;
}

div[data-testid="stSidebar"] h2, 
div[data-testid="stSidebar"] h3, 
div[data-testid="stSidebar"] p, 
div[data-testid="stSidebar"] label {
  color: #f8f5ef;
}

div[data-testid="stSidebar"] .stButton button {
  background: #f0a500;
  color: #0f2d2a;
}

.stButton > button {
  background: var(--accent);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 8px 18px;
  font-weight: 600;
}

.stButton > button:hover {
  background: #075e52;
}

.stTextArea textarea,
.stTextInput input {
  border-radius: 10px;
  border: 1px solid var(--line);
}

.hero {
  background: var(--panel);
  padding: 24px 28px;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}

.hero-kicker {
  text-transform: uppercase;
  letter-spacing: 2px;
  font-size: 12px;
  color: var(--muted);
}

.hero-title {
  font-size: 34px;
  margin: 6px 0 6px 0;
}

.hero-sub {
  color: var(--muted);
  font-size: 16px;
}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <div class="hero-kicker">Procurement Intelligence</div>
  <div class="hero-title">PO L1-L2-L3 Classifier</div>
  <div class="hero-sub">Classify purchase order descriptions into your approved taxonomy in seconds.</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("## Quick Actions")
st.sidebar.markdown("Use an example to see how classifications look.")
example_name = st.sidebar.selectbox(
    "Example inputs",
    ["Select an example"] + list(EXAMPLES.keys()),
)
if st.sidebar.button("Apply Example", use_container_width=True):
    if example_name != "Select an example":
        st.session_state.po_description = EXAMPLES[example_name]["po_description"]
        st.session_state.supplier = EXAMPLES[example_name]["supplier"]
        st.session_state.last_result = None
        st.session_state.last_raw = None
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("## Model Info")
st.sidebar.markdown("Model: `openai/gpt-oss-120b`")
st.sidebar.markdown("Temperature: `0.0`")

st.sidebar.markdown("---")
st.sidebar.markdown("## Output")
st.session_state.show_raw = st.sidebar.checkbox(
    "Show raw response", value=st.session_state.show_raw
)

classifier_tab, taxonomy_tab, history_tab = st.tabs(
    ["Classifier", "Taxonomy", "History"]
)

with classifier_tab:
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        with st.form("classifier_form", clear_on_submit=False):
            po_description = st.text_area(
                "PO Description",
                height=160,
                key="po_description",
                placeholder="Describe the item or service to classify.",
            )
            supplier = st.text_input(
                "Supplier (optional)",
                key="supplier",
                placeholder="Supplier name if available.",
            )

            cols = st.columns(2)
            submitted = cols[0].form_submit_button("Classify")
            cleared = cols[1].form_submit_button("Clear")

        if cleared:
            st.session_state.po_description = ""
            st.session_state.supplier = ""
            st.session_state.last_result = None
            st.session_state.last_raw = None
            st.rerun()

        if submitted:
            if not po_description.strip():
                st.warning("Please enter a PO description.")
            else:
                supplier_value = supplier.strip() or "Not provided"
                with st.spinner("Classifying..."):
                    raw_result = classify_po(po_description.strip(), supplier_value)

                parsed_result = None
                try:
                    parsed_result = json.loads(raw_result)
                except Exception:
                    parsed_result = None

                st.session_state.last_raw = raw_result
                st.session_state.last_result = parsed_result

                history_entry = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "PO Description": po_description.strip(),
                    "Supplier": supplier_value,
                }

                if parsed_result:
                    history_entry.update(
                        {
                            "L1": parsed_result.get("L1", ""),
                            "L2": parsed_result.get("L2", ""),
                            "L3": parsed_result.get("L3", ""),
                        }
                    )
                else:
                    history_entry.update({"L1": "Invalid JSON", "L2": "", "L3": ""})

                st.session_state.history.insert(0, history_entry)
                st.session_state.history = st.session_state.history[:MAX_HISTORY]

        if po_description.strip():
            word_count = len(po_description.strip().split())
            char_count = len(po_description.strip())
            st.caption(f"Input length: {word_count} words, {char_count} characters")

    with right_col:
        st.subheader("Classification Output")

        if st.session_state.last_result is None and st.session_state.last_raw is None:
            st.info("Run a classification to see results here.")
        elif st.session_state.last_result:
            l1_value = st.session_state.last_result.get("L1", "")
            l2_value = st.session_state.last_result.get("L2", "")
            l3_value = st.session_state.last_result.get("L3", "")

            metric_cols = st.columns(3)
            metric_cols[0].metric("L1", l1_value or "-")
            metric_cols[1].metric("L2", l2_value or "-")
            metric_cols[2].metric("L3", l3_value or "-")

            if any(
                str(value).strip().lower() == "not sure"
                for value in [l1_value, l2_value, l3_value]
            ):
                st.warning("Some levels are not confident. Consider adding more detail.")

            st.markdown("#### JSON")
            st.json(st.session_state.last_result)

            st.download_button(
                "Download JSON",
                data=json.dumps(st.session_state.last_result, indent=2),
                file_name="po_classification.json",
                mime="application/json",
            )
        else:
            st.error("The model returned invalid JSON.")
            if st.session_state.show_raw:
                st.code(st.session_state.last_raw, language="json")

        if st.session_state.show_raw and st.session_state.last_raw:
            st.markdown("#### Raw response")
            st.code(st.session_state.last_raw, language="text")

with taxonomy_tab:
    st.subheader("Taxonomy Explorer")
    filter_text = st.text_input("Filter taxonomy", placeholder="Search by L1, L2, or L3")

    rows = []
    for line in TAXONOMY.splitlines():
        line = line.strip()
        if not line or line.startswith("L1") or set(line) == {"-"}:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 3:
            row = {"L1": parts[0], "L2": parts[1], "L3": parts[2]}
            rows.append(row)

    if filter_text.strip():
        rows = [
            row
            for row in rows
            if filter_text.lower() in " ".join(row.values()).lower()
        ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No taxonomy rows match your filter.")

with history_tab:
    st.subheader("Recent Classifications")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("History is empty. Run a classification to populate it.")
