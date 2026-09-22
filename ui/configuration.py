import streamlit as st
import os
import time
import pandas as pd
import json
from medsynth.generator import GeneratorOptions
from ui.cards import render_kpi, render_main_header
from services.generation_service import run_generation

def render_generate():
    # 1. Main Header Card
    st.markdown("""
    <div class="ms-header-card">
        <div style="border-left: 4px solid #2563EB; padding-left: 1.5rem;">
            <h1 style="margin: 0; color: var(--text-color); font-size: 2.5rem;">MedSynth</h1>
            <h3 style="margin: 0.5rem 0; color: var(--text-color); opacity: 0.8; font-weight: 600;">Nigerian Synthetic Healthcare Data Generator</h3>
            <p style="margin: 0; color: var(--text-color); opacity: 0.7; max-width: 600px;">Generate statistically accurate synthetic patient populations and health records based on Nigerian demographics, geography and healthcare facilities.</p>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.9rem; color: var(--text-color); opacity: 0.8;">
            <div>🗄️ Better Data</div>
            <div>📈 Better Insights</div>
            <div>❤️ Healthier Communities</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Top KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(render_kpi("👥", "#DBEAFE", "Population Size", f"{st.session_state.ui_num_patients}", "patients"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi("📍", "#D1FAE5", "Target State", f"{st.session_state.ui_target_state}", "(configured)"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi("👤", "#CCFBF1", "Sex", f"{st.session_state.ui_target_sex}", "(configured)"), unsafe_allow_html=True)
    with k4:
        st.markdown(render_kpi("📅", "#E0E7FF", "Age Range", f"{st.session_state.ui_min_age} - {st.session_state.ui_max_age}", "(configured)"), unsafe_allow_html=True)

    st.write("") # Spacing
    
    # 3. Two Column Core
    col_left, col_right = st.columns([1.5, 1], gap="large")
    
    states, lgas_by_state = st.session_state.geo_data
    
    with col_left:
        with st.form("generation_form", clear_on_submit=False):
            st.markdown("<h4 style='margin-top:0;'>⚙️ Generation Configuration</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.9rem; opacity: 0.7; margin-bottom: 2rem;'>Set your parameters for synthetic data generation.</p>", unsafe_allow_html=True)
            
            st.markdown("**👤 1. Population Configuration**")
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                num_patients = st.number_input("Number of patients", min_value=1, value=st.session_state.ui_num_patients)
            with f2:
                state_opts = ["All States"] + states
                def_idx = state_opts.index(st.session_state.ui_target_state) if st.session_state.ui_target_state in state_opts else 0
                target_state = st.selectbox("State", state_opts, index=def_idx)
            with f3:
                lga_opts = ["All LGAs"] if target_state == "All States" else ["All LGAs"] + lgas_by_state.get(target_state, [])
                target_lga = st.selectbox("LGA", lga_opts)
            with f4:
                target_sex = st.selectbox("Sex", ["All", "Male", "Female"])
                
            st.markdown("<br>**📍 2. Demographics & Geography**", unsafe_allow_html=True)
            d1, d2, d3 = st.columns([1,1,1])
            with d1:
                min_age = st.number_input("Minimum Age", min_value=0, max_value=120, value=st.session_state.ui_min_age)
                use_random_seed = st.checkbox("Use Random Seed", value=True)
            with d2:
                max_age = st.number_input("Maximum Age", min_value=0, max_value=120, value=st.session_state.ui_max_age)
                seed_val = int(time.time() * 1000) if use_random_seed else st.number_input("Seed", value=42, disabled=use_random_seed)
            
            st.markdown("<br>**📄 3. Output Configuration**", unsafe_allow_html=True)
            formats = st.multiselect("Export Formats", ["CSV", "JSON", "FHIR R4"], default=["CSV"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("▶ Generate Patients")

    with col_right:
        # Ready Banner
        st.markdown("""
        <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 0.5rem; padding: 1.5rem; display: flex; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="background-color: #10B981; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
            <div>
                <strong style="color: #059669; font-size: 1.1rem;">Ready to Generate</strong>
                <p style="margin: 0; margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-color); opacity: 0.8;">Configure your parameters and click the button below to start generating synthetic data.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration Summary Card
        st.markdown("""
        <div class="ms-card">
            <h4 style="margin-top: 0; display: flex; align-items: center; gap: 0.5rem;"><span>📊</span> Configuration Summary</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;">✦ Population Size</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_num_patients) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;">✦ State</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_target_state) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;">✦ LGA</td><td style="text-align: right; font-weight: 600;">All LGAs</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;">✦ Sex</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_target_sex) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;">✦ Age Range</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_min_age) + """ - """ + str(st.session_state.ui_max_age) + """</td></tr>
                <tr><td style="padding: 0.75rem 0; opacity: 0.7;">✦ Output Formats</td><td style="text-align: right; font-weight: 600;">CSV, JSON, FHIR</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # About Card
        st.markdown("""
        <div style="background-color: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 0.5rem; padding: 1.5rem; display: flex; gap: 1rem;">
            <div style="background-color: #0284c7; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold; font-family: serif;">i</div>
            <div>
                <strong style="color: var(--text-color); font-size: 1.1rem;">About MedSynth</strong>
                <p style="margin: 0; margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-color); opacity: 0.8;">This tool generates synthetic healthcare data for research, testing and education purposes.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # 4. Bottom Action Tiles
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown("""
        <div class="action-tile">
            <h4 style="margin-top:0; display:flex; align-items:center; gap:0.5rem;">⚡ Generate Data</h4>
            <p style="margin:0; font-size:0.9rem; opacity:0.8; flex-grow:1;">Create synthetic patient populations and health records.</p>
            <a href="?nav=Generate" target="_self">Get Started &rarr;</a>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown("""
        <div class="action-tile">
            <h4 style="margin-top:0; display:flex; align-items:center; gap:0.5rem;">📊 View Results</h4>
            <p style="margin:0; font-size:0.9rem; opacity:0.8; flex-grow:1;">Explore analytics and insights from generated data.</p>
            <a href="?nav=Results" target="_self">Go to Results &rarr;</a>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown("""
        <div class="action-tile">
            <h4 style="margin-top:0; display:flex; align-items:center; gap:0.5rem;">🛡️ Run Validation</h4>
            <p style="margin:0; font-size:0.9rem; opacity:0.8; flex-grow:1;">Check data quality and integrity of generated records.</p>
            <a href="?nav=Validation" target="_self">Go to Validation &rarr;</a>
        </div>
        """, unsafe_allow_html=True)
    with t4:
        st.markdown("""
        <div class="action-tile">
            <h4 style="margin-top:0; display:flex; align-items:center; gap:0.5rem;">👤 Explore Patients</h4>
            <p style="margin:0; font-size:0.9rem; opacity:0.8; flex-grow:1;">Browse individual patient records, timelines and clinical data.</p>
            <a href="?nav=Patient Explorer" target="_self">Go to Patient Explorer &rarr;</a>
        </div>
        """, unsafe_allow_html=True)

    # Execution Block
    if submitted:
        # Sync state variables so KPIs update correctly on next run
        st.session_state.ui_num_patients = num_patients
        st.session_state.ui_target_state = target_state
        st.session_state.ui_target_sex = target_sex
        st.session_state.ui_min_age = min_age
        st.session_state.ui_max_age = max_age
        
        if min_age > max_age:
            st.error("Minimum age cannot be greater than maximum age.")
            return
        if not formats:
            st.error("Please select at least one output format.")
            return
            
        st.session_state.generation_completed = False
        st.session_state.output_dir = None
        
        opts = GeneratorOptions()
        opts.population_size = int(num_patients)
        opts.seed = int(seed_val)
        opts.min_age = int(min_age)
        opts.max_age = int(max_age)
        
        if target_state != "All States":
            opts.target_state = target_state
        if target_lga != "All LGAs":
            opts.target_lga = target_lga
            
        if target_sex == "Male":
            opts.target_sex = "M"
        elif target_sex == "Female":
            opts.target_sex = "F"
            
        
        try:
            with st.status("Generating MedSynth Population...", expanded=True) as status:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total):
                    if current % 10 == 0 or current == total:
                        progress_bar.progress(current / total)
                        status_text.text(f"Processed {current} / {total} patients...")
                        
                summary = run_generation(opts, formats, update_progress)
                status.update(label="Generation Complete!", state="complete", expanded=False)
                
            st.session_state.generation_completed = True
            st.session_state.output_dir = summary['out_dir']
            st.session_state.summary = summary
            st.rerun()
        except Exception as e:
            st.error(f"Generation Failed: {e}")
            return


    if st.session_state.generation_completed:
        summ = st.session_state.summary
        out_dir = st.session_state.output_dir
        st.success("Simulation finished successfully.")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Patients Generated", summ['total'])
        mc2.metric("Generation Time", f"{summ['duration']:.2f}s")
        mc3.metric("Seed", summ['seed'])
        mc4.metric("Formats", " + ".join(summ['formats']))
        st.write("### Quick Data Preview")
        previewed = False
        if "CSV" in summ['formats']:
            csv_path = os.path.join(out_dir, "csv", "patients.csv")
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path, nrows=5)
                    st.dataframe(df, use_container_width=True)
                    previewed = True
                except: pass
        if not previewed and "JSON" in summ['formats']:
            jsonl_path = os.path.join(out_dir, "patients.jsonl")
            if not os.path.exists(jsonl_path):
                jsonl_path = os.path.join(out_dir, "json", "patients.jsonl")
            if os.path.exists(jsonl_path):
                try:
                    with open(jsonl_path, 'r', encoding='utf-8') as f:
                        line = f.readline()
                        if line: st.json(json.loads(line))
                except: pass
        st.info("Head over to the **Results** or **Patient Explorer** tabs to analyze this population!")
