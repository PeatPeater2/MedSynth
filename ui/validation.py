import streamlit as st
from services.validation_service import run_validation

def render_validation():
    st.title("Validation Report")
    if not st.session_state.generation_completed or not st.session_state.output_dir:
        st.info("No generation results found. Please go to Generate and run a simulation first.")
        return
    out_dir = st.session_state.output_dir
    with st.spinner("Running structural and referential validation checks..."):
        results = run_validation(out_dir)
    for name, status, msg in results:
        if status == "PASS":
            st.success(f"**{name}**: {msg}")
        else:
            st.error(f"**{name}**: {msg}")