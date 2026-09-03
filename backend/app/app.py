import sys
import os
import asyncio
import streamlit as st

# make "app.pipeline" and "app.ingestion..." importable
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.pipeline import run_luna_pipeline
from app.ingestion.file_parser import extract_text_from_file

st.set_page_config(page_title="LUNA", layout="wide")

st.title("🔍 LUNA")
st.caption("Law-enforcement Unified Network for Advanced Investigation")

# ------------------------------------------------------------
# INPUT: text or file
# ------------------------------------------------------------

tab1, tab2 = st.tabs(["Enter Case Text", "Upload File"])

case_text = ""

with tab1:
    case_text_input = st.text_area("Case details", height=200)
    if case_text_input.strip():
        case_text = case_text_input.strip()

with tab2:
    uploaded_file = st.file_uploader("Upload a case file")
    if uploaded_file is not None:
        contents = uploaded_file.read()
        extracted = extract_text_from_file(contents, uploaded_file.name)
        if extracted:
            st.text_area("Extracted text", extracted, height=200)
            case_text = extracted.strip()

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if st.button("🚨 Investigate", type="primary"):
    if not case_text:
        st.error("Case text cannot be empty.")
    else:
        with st.spinner("Running LUNA pipeline..."):
            try:
                result = asyncio.run(run_luna_pipeline(case_text=case_text))
                st.success("Investigation complete")
                st.json(result)
            except Exception as e:
                st.error(f"Investigation failed: {type(e).__name__}: {e}")