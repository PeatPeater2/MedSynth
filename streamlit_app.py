import streamlit as st
import os
import time
import pandas as pd
import json
import numpy as np

from medsynth.generator import GeneratorOptions
from medsynth.geography import Geography
from medsynth.exporters import Exporter
from medsynth.cli import get_available_diseases, setup_generator
from medsynth.validator import validate_module

st.set_page_config(page_title="MedSynth", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_geo():
    geo = Geography()
    return geo.states, geo.lgas_by_state

def inject_custom_css():
    st.markdown("""
    <style>
    /* Dark Mode Aware Base Colors */
    :root {
        --card-bg: var(--background-color);
        --app-bg: var(--secondary-background-color);
        --border-color: rgba(128, 128, 128, 0.2);
    }
    
    /* Force main app background to secondary, leaving cards as primary */
    [data-testid="stAppViewContainer"] {
        background-color: var(--app-bg) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    
    /* Force Radio buttons in sidebar to look native but bright text */
    [data-testid="stSidebar"] .stRadio label {
        color: #F8FAFC !important;
        font-weight: 500;
    }

    /* Form styling to look like a card */
    [data-testid="stForm"] {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    /* Custom HTML Cards */
    .ms-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .ms-header-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .kpi-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .action-tile {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1.5rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .action-tile a {
        color: #2563EB !important;
        text-decoration: none;
        font-weight: 600;
        margin-top: 1rem;
    }

    /* Primary Button override */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Hide top padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_kpi(icon, icon_bg, title, value, subtext):
    html = f"""<div class="kpi-card">
<div style="background-color: {icon_bg}; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;">
{icon}
</div>
<div>
<div style="font-size: 0.8rem; color: var(--text-color); opacity: 0.7; font-weight: 600;">{title}</div>
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-color); line-height: 1.2;">{value}</div>
<div style="font-size: 0.75rem; color: var(--text-color); opacity: 0.6;">{subtext}</div>
</div>
</div>"""
    return html

def main():
    inject_custom_css()
    
    # Handle Navigation Query Params (makes bottom tiles work)
    try:
        q_nav = st.query_params.get("nav")
        if q_nav:
            st.session_state.nav_radio = q_nav
            st.query_params.clear()
    except:
        pass
    
    if 'generation_completed' not in st.session_state:
        st.session_state.generation_completed = False
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = None
    if 'summary' not in st.session_state:
        st.session_state.summary = {}
        
    # State tracking
    if 'ui_num_patients' not in st.session_state:
        st.session_state.ui_num_patients = 100
    if 'ui_target_state' not in st.session_state:
        st.session_state.ui_target_state = "Osun"
    if 'ui_target_sex' not in st.session_state:
        st.session_state.ui_target_sex = "All"
    if 'ui_min_age' not in st.session_state:
        st.session_state.ui_min_age = 0
    if 'ui_max_age' not in st.session_state:
        st.session_state.ui_max_age = 100
    if 'ui_target_lga' not in st.session_state:
        st.session_state.ui_target_lga = "All LGAs"

    # Sidebar
    st.sidebar.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h1 style='color: #FFFFFF; margin-bottom: 0; display: flex; align-items: center; gap: 10px;'>
                <span style='color: #38BDF8;'>∿</span> MedSynth
            </h1>
            <p style='color: #94A3B8; font-size: 0.8rem; margin-top: 0;'>Nigerian Synthetic Healthcare Data Generator</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    nav_options = {
        " Generate": "Generate",
        " Results": "Results",
        
        " Patient Explorer": "Patient Explorer"
    }
    
    # Reverse lookup for session state
    current_nav = " Generate"
    if 'nav_radio' in st.session_state:
        for k, v in nav_options.items():
            if v == st.session_state.nav_radio:
                current_nav = k
                break
                
    selected_nav = st.sidebar.radio("Navigation", list(nav_options.keys()), index=list(nav_options.keys()).index(current_nav), label_visibility="collapsed")
    page = nav_options[selected_nav]
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div style="background-color: #1E293B; border-radius: 8px; padding: 15px; margin-top: 20px;">
        <div style="display: flex; gap: 10px;">
            <div style="color: #38BDF8;">ⓘ</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">MedSynth generates synthetic healthcare data for research, testing and education.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if page == "Generate":
        render_generate()
    elif page == "Results":
        render_results()
    
        
    elif page == "Patient Explorer":
        render_patient_explorer()

def render_generate():
    # 1. Main Header Card
    st.markdown("""
    <div class="ms-header-card">
        <div style="border-left: 4px solid #2563EB; padding-left: 1.5rem;">
            <h1 style="margin: 0; color: var(--text-color); font-size: 2.5rem;">MedSynth</h1>
            <h3 style="margin: 0.5rem 0; color: var(--text-color); opacity: 0.8; font-weight: 600;">Nigerian Synthetic Healthcare Data Generator</h3>
            <p style="margin: 0; color: var(--text-color); opacity: 0.7; max-width: 600px;">Generate statistically accurate synthetic patient populations and health records based on Nigerian demographics, geography and healthcare facilities.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Top KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(render_kpi("👥", "#CFE7D5", "Population Size", f"{st.session_state.ui_num_patients}", "patients"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi("📍", "#CFE7D5", "Location", f"{st.session_state.ui_target_state}", "(configured)"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi("👤", "#CFE7D5gene", "Sex", f"{st.session_state.ui_target_sex}", "(configured)"), unsafe_allow_html=True)
    with k4:
        st.markdown(render_kpi("📅", "#CFE7D5", "Age Range", f"{st.session_state.ui_min_age} - {st.session_state.ui_max_age}", "(configured)"), unsafe_allow_html=True)

    st.write("") # Spacing
    
    # 3. Two Column Core
    col_left, col_right = st.columns([1.5, 1], gap="large")
    
    states, lgas_by_state = load_geo()
    
    with col_left:
        with st.container():
            st.markdown("<h4 style='margin-top:0;'>Generation Configuration</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.9rem; opacity: 0.7; margin-bottom: 2rem;'>Set your parameters for synthetic data generation.</p>", unsafe_allow_html=True)
            
            st.markdown("**Population Configuration**")
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                num_patients = st.number_input("Number of patients", min_value=1, key="ui_num_patients")
            with f2:
                state_opts = ["All States"] + states
                target_state = st.selectbox("State", state_opts, key="ui_target_state")
            with f3:
                lga_opts = ["All LGAs"] if target_state == "All States" else ["All LGAs"] + lgas_by_state.get(target_state, [])
                if st.session_state.get("ui_target_lga") not in lga_opts:
                    st.session_state["ui_target_lga"] = "All LGAs"
                target_lga = st.selectbox("LGA", lga_opts, key="ui_target_lga")
            with f4:
                target_sex = st.selectbox("Sex", ["All", "Male", "Female"], key="ui_target_sex")
                
            st.markdown("<br>**Demographics & Geography**", unsafe_allow_html=True)
            d1, d2, d3 = st.columns([1,1,1])
            with d1:
                min_age = st.number_input("Minimum Age", min_value=0, max_value=120, key="ui_min_age")
                use_random_seed = st.checkbox("Use Random Seed", value=True)
            with d2:
                max_age = st.number_input("Maximum Age", min_value=0, max_value=120, key="ui_max_age")
                seed_val = int(time.time() * 1000) if use_random_seed else st.number_input("Seed", value=42, disabled=use_random_seed)
            
            st.markdown("<br>**Disease Modules**", unsafe_allow_html=True)
            all_diseases = get_available_diseases()
            selected_diseases = st.multiselect(
                "Select diseases to simulate",
                options=all_diseases,
                default=[],
                format_func=lambda x: "HIV" if x.lower() == "hiv" else x.replace('_', ' ').title()
            )

            st.markdown("<br>**Output Configuration**", unsafe_allow_html=True)
            formats = st.multiselect("Output Formats", ["CSV", "JSON", "FHIR R4"], default=["CSV"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.button("▶ Generate Patients", use_container_width=True, type="primary")

    with col_right:
        # Ready Banner
        st.markdown("""
        """, unsafe_allow_html=True)
        
        # Configuration Summary Card
        st.markdown("""
        <div class="ms-card">
            <h4 style="margin-top: 0; display: flex; align-items: center; gap: 0.5rem;"><span></span> Configuration Summary</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;"> Population Size</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_num_patients) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;"> State</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_target_state) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;"> LGA</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_target_lga) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;"> Sex</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_target_sex) + """</td></tr>
                <tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 0.75rem 0; opacity: 0.7;"> Age Range</td><td style="text-align: right; font-weight: 600;">""" + str(st.session_state.ui_min_age) + """ - """ + str(st.session_state.ui_max_age) + """</td></tr>
                <tr><td style="padding: 0.75rem 0; opacity: 0.7;"> Output Formats</td><td style="text-align: right; font-weight: 600;">CSV, JSON, FHIR</td></tr>
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
    


    # Execution Block
    if submitted:
        # Values are automatically synced via widget keys
        
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
            
        diseases = get_available_diseases()
        target_diseases = ",".join(selected_diseases) if len(selected_diseases) > 0 else 'all'
        try:
            generator = setup_generator(opts, target_diseases, diseases)
        except Exception as e:
            st.error(f"Configuration is invalid: {e}")
            return
            
        out_dir = os.path.abspath(os.path.join("MedSynthOutput", "streamlit"))
        os.makedirs(out_dir, exist_ok=True)
        
        out_formats = [f.replace(" R4", "") for f in formats]
        exporter = Exporter(out_dir, out_formats)
        exporter.begin()
        
        start_t = time.time()
        generated = 0
        
        with st.status("Generating MedSynth Population...", expanded=True) as status:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                for p in generator.generate_stream(workers=1):
                    exporter.export_patient(p)
                    generated += 1
                    if generated % 10 == 0 or generated == num_patients:
                        pct = generated / num_patients
                        progress_bar.progress(pct)
                        status_text.text(f"Processed {generated} / {num_patients} patients...")
                exporter.end()
                status.update(label="Generation Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Generation Failed", state="error", expanded=True)
                st.error(f"Error details: {e}")
                return
            
        duration = time.time() - start_t
        
        st.session_state.generation_completed = True
        st.session_state.output_dir = out_dir
        st.session_state.summary = {
            'total': generated,
            'state': target_state,
            'lga': target_lga,
            'sex': target_sex,
            'age': f"{min_age}-{max_age}",
            'seed': seed_val,
            'formats': out_formats,
            'duration': duration,
            'reference_time': opts.reference_time
        }
        st.rerun()

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
                    df = pd.read_csv(csv_path, nrows=10000)
                    # Make raw column headers read like normal names
                    df.columns = [c.replace('_', ' ').title() if c.isupper() else c for c in df.columns]
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

def render_results():
    st.title("Analytics & Results")
    st.info("MedSynth generates synthetic healthcare data. The displayed records do not represent real patients. Synthetic statistics should not be interpreted as real-world Nigerian epidemiological estimates.")
    if not st.session_state.generation_completed or not st.session_state.output_dir:
        st.warning("No generation results found. Please go to Generate and run a simulation first.")
        return
    out_dir = st.session_state.output_dir
    ref_time = st.session_state.summary.get('reference_time', time.time()*1000)
    st.write("### Filters")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        states, _ = load_geo()
        f_state = st.selectbox("Filter by State", ["All"] + states)
    with f_col2:
        f_sex = st.selectbox("Filter by Sex", ["All", "Male", "Female"])
    with st.spinner("Processing analytics directly from generated CSVs..."):
        stats = compute_analytics(out_dir, ref_time, f_state, f_sex)
    if not stats:
        st.error("No CSV output found to analyze. Please ensure you generated with CSV format enabled.")
        return
    st.header("Population Generated")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Patients", stats['total'])
    c2.metric("Male", stats['males'])
    c3.metric("Female", stats['females'])
    if stats['ages']:
        ages_arr = np.array(stats['ages'])
        c4.metric("Mean Age", f"{np.mean(ages_arr):.1f}")
        st.caption(f"**Age Range:** {np.min(ages_arr)} to {np.max(ages_arr)} (Median: {np.median(ages_arr):.1f})")
    st.markdown("---")
    res_tab1, res_tab2, res_tab3, res_tab4, res_tab5 = st.tabs(["Demographics", "Geography", "Diseases", "Socioeconomics", "Facilities & Vitals"])
    with res_tab1:
        st.subheader("Demographic Distribution")
        colA, colB = st.columns(2)
        with colA:
            st.write("**Sex Distribution**")
            st.bar_chart({'Male': [stats['males']], 'Female': [stats['females']]})
        with colB:
            st.write("**Age Groups**")
            df_age = pd.DataFrame(list(stats['age_groups'].items()), columns=['Age Group', 'Count']).set_index('Age Group')
            sort_order = ['0-4','5-9','10-14','15-19','20-24','25-29','30-39','40-49','50-59','60-69','70-79','80+']
            df_age = df_age.reindex(sort_order).fillna(0)
            st.bar_chart(df_age)
    with res_tab2:
        st.subheader("Geographic Analytics")
        colC, colD = st.columns(2)
        with colC:
            st.write("**State Distribution**")
            st.dataframe(pd.DataFrame(list(stats['states'].items()), columns=['State', 'Patients']).sort_values('Patients', ascending=False), use_container_width=True)
        with colD:
            st.write("**LGA Distribution**")
            st.dataframe(pd.DataFrame(list(stats['lgas'].items()), columns=['LGA', 'Patients']).sort_values('Patients', ascending=False), use_container_width=True)
    with res_tab3:
        st.subheader("Disease Analytics")
        if stats['diseases']:
            st.dataframe(pd.DataFrame(list(stats['diseases'].items()), columns=['Condition', 'Cases']).sort_values('Cases', ascending=False), use_container_width=True)
            c_dis1, c_dis2 = st.columns(2)
            with c_dis1:
                st.write("**Disease by Age Group**")
                df_dba = pd.DataFrame(stats['disease_by_age']).fillna(0)
                if not df_dba.empty:
                    st.dataframe(df_dba, use_container_width=True)
            with c_dis2:
                st.write("**Disease by Sex**")
                df_dbs = pd.DataFrame(stats['disease_by_sex']).fillna(0)
                if not df_dbs.empty:
                    st.dataframe(df_dbs, use_container_width=True)
        else:
            st.write("No conditions found.")
    with res_tab4:
        st.subheader("Socioeconomic Analytics")
        colE, colF = st.columns(2)
        with colE:
            st.write("**Wealth Quintiles**")
            st.bar_chart(pd.DataFrame(list(stats['wealth'].items()), columns=['Quintile', 'Count']).set_index('Quintile'))
        with colF:
            st.write("**Insurance Status**")

    with res_tab5:
        st.subheader("Care-Seeking Analytics")
        if stats.get('encounter_classes'):
            st.write("Encounters by Class")
            st.bar_chart(pd.DataFrame(list(stats['encounter_classes'].items()), columns=['Class', 'Count']).set_index('Class'))
        else:
            st.write("No care-seeking data found.")
        st.subheader("Facility Analytics")
        if stats['facilities']:
            st.write("Top Facilities by Generated Encounters")
            df_fac = pd.DataFrame(list(stats['facilities'].items()), columns=['Facility', 'Encounters']).sort_values('Encounters', ascending=False).head(10)
            st.dataframe(df_fac, use_container_width=True)
        else:
            st.write("No facility encounters found.")
        st.subheader("Physiological Summary")
        if stats['vitals']:
            vit_data = []
            for k, v_list in stats['vitals'].items():
                arr = np.array(v_list)
                vit_data.append({
                    'Metric': k,
                    'Mean': round(np.mean(arr), 2),
                    'Median': round(np.median(arr), 2),
                    'Min': round(np.min(arr), 2),
                    'Max': round(np.max(arr), 2)
                })
            st.dataframe(pd.DataFrame(vit_data), use_container_width=True)
        else:
            st.write("No vital signs generated.")



def render_patient_explorer():
    st.title("Patient Explorer")
    if not st.session_state.generation_completed or not st.session_state.output_dir:
        st.info("No generation results found. Please generate patients first.")
        return
    out_dir = st.session_state.output_dir
    csv_dir = os.path.join(out_dir, "csv")
    jsonl_path = os.path.join(out_dir, "patients.jsonl")
    if not os.path.exists(jsonl_path):
        jsonl_path = os.path.join(out_dir, "json", "patients.jsonl")
    sample_pids = []
    has_csv = os.path.exists(os.path.join(csv_dir, "patients.csv"))
    has_json = os.path.exists(jsonl_path)
    if not has_csv and not has_json:
        st.error("Neither CSV nor JSON patient data found.")
        return
    if has_csv:
        try:
            sample_df = pd.read_csv(os.path.join(csv_dir, "patients.csv"), usecols=['Id'], nrows=100)
            sample_pids = sample_df['Id'].tolist()
        except: pass
    if not sample_pids and has_json:
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for _ in range(100):
                    line = f.readline()
                    if not line: break
                    p = json.loads(line)
                    sample_pids.append(p['id'])
        except: pass
    sample_opts = ["Select a patient..."] + sample_pids
    search_pid = st.text_input("Or enter an exact Patient ID to search for:")
    selected_dropdown = st.selectbox("Select from generated sample", sample_opts, key="patient_select")
    target_pid = None
    if search_pid:
        target_pid = search_pid.strip()
    elif selected_dropdown != "Select a patient...":
        target_pid = selected_dropdown
    if target_pid:
        with st.spinner(f"Fetching record for {target_pid}..."):
            record_data = fetch_patient_record(out_dir, target_pid)
        if not record_data:
            st.error(f"Patient {target_pid} not found in output files.")
            return
        attrs = record_data.get('attributes', {})
        record = record_data.get('record', {})
        pid = record_data.get('id', target_pid)
        ref_time = st.session_state.summary.get('reference_time', time.time()*1000)
        try:
            bdate = float(attrs.get('birthdate', ref_time))
            ddate = attrs.get('deathdate')
            if ddate is not None and str(ddate).lower() != 'nan' and str(ddate).strip() != '':
                age_end = float(ddate)
                is_dead = True
            else:
                age_end = ref_time
                is_dead = False
            age = int((age_end - bdate) / (365.25 * 24 * 60 * 60 * 1000))
        except Exception as e:
            age = "Unknown"
            is_dead = False
        st.header(f"Patient: {pid}")
        status_badge = " (Deceased)" if is_dead else ""
        st.subheader(f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}{status_badge}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sex", attrs.get('gender', 'Unknown'))
        c2.metric("Age", age)
        c3.metric("State", attrs.get('state', 'Unknown'))
        c4.metric("LGA", attrs.get('lga', 'Unknown'))
        st.markdown("---")
        t_sum, t_time, t_fhir = st.tabs(["Clinical Summary", "Chronological Timeline", "Raw FHIR Data"])
        with t_sum:
            ov1, ov2 = st.columns(2)
            with ov1:
                st.write("**Demographics:**")
                st.write(f"Ethnicity: {attrs.get('ethnicity', 'Unknown')}")
            with ov2:
                st.write("**Socioeconomic Information:**")


            st.info(f"Generated patient with {len(record.get('encounters', []))} clinical encounters.")
            if record.get('conditions'):
                st.write("### Active & Historical Conditions")
                c_data = []
                for c in record['conditions']:
                    end_str = time.strftime('%Y-%m-%d', time.gmtime(c['end']/1000)) if 'end' in c else 'Ongoing'
                    c_data.append({
                        'Onset': time.strftime('%Y-%m-%d', time.gmtime(c['start']/1000)),
                        'Condition': c['description'],
                        'Resolution': end_str
                    })
                st.dataframe(pd.DataFrame(c_data), use_container_width=True)
            if record.get('encounters'):
                st.write("### Encounter History")
                e_data = []
                for e in record['encounters']:
                    e_data.append({
                        'Date': time.strftime('%Y-%m-%d', time.gmtime(e['start']/1000)),
                        'Class': e['encounter_class'],
                        'Reason': e.get('description', 'Unknown')
                    })
                st.dataframe(pd.DataFrame(e_data), use_container_width=True)
            if record.get('observations'):
                st.write("### Observations & Vitals")
                o_data = []
                for o in record['observations']:
                    o_data.append({
                        'Date': time.strftime('%Y-%m-%d', time.gmtime(o['date']/1000)),
                        'Observation': o['description'],
                        'Value': f"{o['value']} {o.get('units', '')}"
                    })
                st.dataframe(pd.DataFrame(o_data), use_container_width=True)
            if record.get('medications'):
                st.write("### Medications")
                m_data = []
                for m in record['medications']:
                    end_str = time.strftime('%Y-%m-%d', time.gmtime(m['stop']/1000)) if 'stop' in m and m['stop'] else 'Ongoing'
                    m_data.append({
                        'Started': time.strftime('%Y-%m-%d', time.gmtime(m['start']/1000)),
                        'Medication': m['description'],
                        'Stopped': end_str
                    })
                st.dataframe(pd.DataFrame(m_data), use_container_width=True)
        with t_time:
            st.write("### Patient Timeline")
            events = []
            events.append((attrs.get('birthdate', 0), "Demographic", "Birth"))
            if is_dead:
                events.append((attrs.get('deathdate'), "Demographic", "Death"))
            for e in record.get('encounters', []):
                events.append((e['start'], "Encounter", f"Visited for {e.get('description', 'general care')}"))
            for c in record.get('conditions', []):
                events.append((c['start'], "Condition", f"Diagnosed with {c['description']}"))
            for m in record.get('medications', []):
                events.append((m['start'], "Medication", f"Prescribed {m['description']}"))
            events.sort(key=lambda x: x[0])
            for t_ms, e_type, desc in events:
                t_str = time.strftime('%Y-%m-%d', time.gmtime(t_ms/1000))
                if e_type == "Demographic":
                    st.markdown(f"**{t_str}**  *{desc}*")
                elif e_type == "Encounter":
                    st.markdown(f"**{t_str}**  {desc}")
                elif e_type == "Condition":
                    st.markdown(f"**{t_str}**  {desc}")
                elif e_type == "Medication":
                    st.markdown(f"**{t_str}**  {desc}")
        with t_fhir:
            fhir_dir = os.path.join(out_dir, "fhir")
            if os.path.exists(fhir_dir):
                fhir_path = None
                for f in os.listdir(fhir_dir):
                    if f.endswith('.json'):
                        try:
                            with open(os.path.join(fhir_dir, f), 'r') as bfile:
                                bundle = json.load(bfile)
                                for entry in bundle.get('entry', []):
                                    if entry.get('resource', {}).get('resourceType') == 'Patient':
                                        if entry['resource'].get('id') == target_pid:
                                            fhir_path = os.path.join(fhir_dir, f)
                                            break
                        except: pass
                        if fhir_path: break
                if fhir_path:
                    st.write("### FHIR Bundle Preview")
                    with open(fhir_path, 'r') as bf:
                        st.json(json.load(bf))
                else:
                    st.info("FHIR bundle for this patient could not be located in the FHIR output directory.")
            else:
                st.info("FHIR output was not generated for this population.")


def get_age_group(age):
    if age < 5: return "0-4"
    if age < 10: return "5-9"
    if age < 15: return "10-14"
    if age < 20: return "15-19"
    if age < 25: return "20-24"
    if age < 30: return "25-29"
    if age < 40: return "30-39"
    if age < 50: return "40-49"
    if age < 60: return "50-59"
    if age < 70: return "60-69"
    if age < 80: return "70-79"
    return "80+"

@st.cache_data(show_spinner=False)
def compute_analytics(out_dir, ref_time, f_state="All", f_sex="All"):
    csv_dir = os.path.join(out_dir, "csv")
    if not os.path.exists(csv_dir):
        return None
        
    stats = {
        'total': 0, 'males': 0, 'females': 0,
        'ages': [],
        'age_groups': {},
        'states': {}, 'lgas': {},
        'wealth': {}, 'insurance': {},
        'diseases': {}, 'disease_by_age': {}, 'disease_by_sex': {},
        'facilities': {}, 'vitals': {}, 'encounter_classes': {}
    }
    
    patient_demographics = {}
    valid_pids = set()
    
    pat_file = os.path.join(csv_dir, "patients.csv")
    if os.path.exists(pat_file):
        for chunk in pd.read_csv(pat_file, chunksize=50000):
            if f_state != "All":
                chunk = chunk[chunk['STATE'] == f_state]
            if f_sex != "All":
                # Assuming f_sex is 'Male' or 'Female'
                sex_code = 'M' if f_sex == 'Male' else 'F'
                chunk = chunk[chunk['GENDER'] == sex_code]
                
            stats['total'] += len(chunk)
            
            for _, row in chunk.iterrows():
                pid = row.get('Id')
                valid_pids.add(pid)
                gender = row.get('GENDER', 'U')
                if gender == 'M': stats['males'] += 1
                elif gender == 'F': stats['females'] += 1
                
                bdate = row.get('BIRTHDATE', ref_time)
                try:
                    age = int((ref_time - float(bdate)) / (365.25 * 24 * 60 * 60 * 1000))
                except:
                    age = 0
                    
                stats['ages'].append(age)
                ag = get_age_group(age)
                stats['age_groups'][ag] = stats['age_groups'].get(ag, 0) + 1
                
                state = row.get('STATE', 'Unknown')
                stats['states'][state] = stats['states'].get(state, 0) + 1
                
                lga = row.get('LGA', 'Unknown')
                stats['lgas'][lga] = stats['lgas'].get(lga, 0) + 1
                
                wq = row.get('WEALTH_QUINTILE', 'Unknown')
                stats['wealth'][wq] = stats['wealth'].get(wq, 0) + 1
                
                ins = row.get('INSURANCE', 'None')
                stats['insurance'][ins] = stats['insurance'].get(ins, 0) + 1
                
                patient_demographics[pid] = {'sex': gender, 'age_group': ag}
                
    cond_file = os.path.join(csv_dir, "conditions.csv")
    if os.path.exists(cond_file):
        for chunk in pd.read_csv(cond_file, chunksize=50000):
            if valid_pids:
                chunk = chunk[chunk['PATIENT'].isin(valid_pids)]
            for _, row in chunk.iterrows():
                desc = row.get('DESCRIPTION', 'Unknown')
                stats['diseases'][desc] = stats['diseases'].get(desc, 0) + 1
                
                pid = row.get('PATIENT')
                if pid in patient_demographics:
                    ag = patient_demographics[pid]['age_group']
                    sex = patient_demographics[pid]['sex']
                    
                    if desc not in stats['disease_by_age']: stats['disease_by_age'][desc] = {}
                    stats['disease_by_age'][desc][ag] = stats['disease_by_age'][desc].get(ag, 0) + 1
                    
                    if desc not in stats['disease_by_sex']: stats['disease_by_sex'][desc] = {}
                    stats['disease_by_sex'][desc][sex] = stats['disease_by_sex'][desc].get(sex, 0) + 1
                    
    enc_file = os.path.join(csv_dir, "encounters.csv")
    if os.path.exists(enc_file):
        for chunk in pd.read_csv(enc_file, chunksize=50000):
            if valid_pids:
                chunk = chunk[chunk['PATIENT'].isin(valid_pids)]
            for _, row in chunk.iterrows():
                fac = row.get('FACILITY_NAME')
                if pd.notna(fac) and fac != "":
                    stats['facilities'][fac] = stats['facilities'].get(fac, 0) + 1
                    
                eclass = row.get('ENCOUNTERCLASS')
                if pd.notna(eclass) and eclass != "":
                    stats['encounter_classes'][eclass] = stats['encounter_classes'].get(eclass, 0) + 1
                    
    obs_file = os.path.join(csv_dir, "observations.csv")
    if os.path.exists(obs_file):
        for chunk in pd.read_csv(obs_file, chunksize=50000):
            if valid_pids:
                chunk = chunk[chunk['PATIENT'].isin(valid_pids)]
            vital_chunk = chunk[chunk['CATEGORY'] == 'vital-signs']
            for _, row in vital_chunk.iterrows():
                desc = row.get('DESCRIPTION', 'Unknown')
                val = row.get('VALUE')
                if pd.notna(val):
                    try:
                        v = float(val)
                        if desc not in stats['vitals']: stats['vitals'][desc] = []
                        if len(stats['vitals'][desc]) < 10000:
                            stats['vitals'][desc].append(v)
                    except:
                        pass
                        
    return stats

def render_results():
    st.title("Analytics & Results")
    st.info("MedSynth generates synthetic healthcare data. The displayed records do not represent real patients. Synthetic statistics should not be interpreted as real-world Nigerian epidemiological estimates.")
    
    if not st.session_state.generation_completed or not st.session_state.output_dir:
        st.warning("No generation results found. Please go to Generate and run a simulation first.")
        return
        
    out_dir = st.session_state.output_dir
    ref_time = st.session_state.summary.get('reference_time', time.time()*1000)
    
    st.write("### Filters")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        states, _ = load_geo()
        f_state = st.selectbox("Filter by State", ["All"] + states)
    with f_col2:
        f_sex = st.selectbox("Filter by Sex", ["All", "Male", "Female"])
    
    with st.spinner("Processing analytics directly from generated CSVs..."):
        stats = compute_analytics(out_dir, ref_time, f_state, f_sex)
        
    if not stats:
        st.error("No CSV output found to analyze. Please ensure you generated with CSV format enabled.")
        return
        
    st.header("Population Generated")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Patients", stats['total'])
    c2.metric("Male", stats['males'])
    c3.metric("Female", stats['females'])
    
    if stats['ages']:
        ages_arr = np.array(stats['ages'])
        c4.metric("Mean Age", f"{np.mean(ages_arr):.1f}")
        st.caption(f"**Age Range:** {np.min(ages_arr)} to {np.max(ages_arr)} (Median: {np.median(ages_arr):.1f})")
        
    st.markdown("---")
    res_tab1, res_tab2, res_tab3, res_tab4, res_tab5 = st.tabs(["Demographics", "Geography", "Diseases", "Socioeconomics", "Facilities & Vitals"])
    
    with res_tab1:
        st.subheader("Demographic Distribution")
        colA, colB = st.columns(2)
        with colA:
            st.write("**Sex Distribution**")
            st.bar_chart({'Male': [stats['males']], 'Female': [stats['females']]})
        with colB:
            st.write("**Age Groups**")
            df_age = pd.DataFrame(list(stats['age_groups'].items()), columns=['Age Group', 'Count']).set_index('Age Group')
            sort_order = ['0-4','5-9','10-14','15-19','20-24','25-29','30-39','40-49','50-59','60-69','70-79','80+']
            df_age = df_age.reindex(sort_order).fillna(0)
            st.bar_chart(df_age)
            
    with res_tab2:
        st.subheader("Geographic Analytics")
        colC, colD = st.columns(2)
        with colC:
            st.write("**State Distribution**")
            st.dataframe(pd.DataFrame(list(stats['states'].items()), columns=['State', 'Patients']).sort_values('Patients', ascending=False), use_container_width=True)
        with colD:
            st.write("**LGA Distribution**")
            st.dataframe(pd.DataFrame(list(stats['lgas'].items()), columns=['LGA', 'Patients']).sort_values('Patients', ascending=False), use_container_width=True)
            
    with res_tab3:
        st.subheader("Disease Analytics")
        if stats['diseases']:
            st.dataframe(pd.DataFrame(list(stats['diseases'].items()), columns=['Condition', 'Cases']).sort_values('Cases', ascending=False), use_container_width=True)
            
            c_dis1, c_dis2 = st.columns(2)
            with c_dis1:
                st.write("**Disease by Age Group**")
                df_dba = pd.DataFrame(stats['disease_by_age']).fillna(0)
                if not df_dba.empty:
                    st.dataframe(df_dba, use_container_width=True)
            with c_dis2:
                st.write("**Disease by Sex**")
                df_dbs = pd.DataFrame(stats['disease_by_sex']).fillna(0)
                if not df_dbs.empty:
                    st.dataframe(df_dbs, use_container_width=True)
        else:
            st.write("No conditions found.")
            
    with res_tab4:
        st.subheader("Socioeconomic Analytics")
        colE, colF = st.columns(2)
        with colE:
            st.write("**Wealth Quintiles**")
            st.bar_chart(pd.DataFrame(list(stats['wealth'].items()), columns=['Quintile', 'Count']).set_index('Quintile'))
        with colF:
            st.write("**Insurance Status**")

            
    with res_tab5:
        st.subheader("Care-Seeking Analytics")
        if stats.get('encounter_classes'):
            st.write("Encounters by Class")
            st.bar_chart(pd.DataFrame(list(stats['encounter_classes'].items()), columns=['Class', 'Count']).set_index('Class'))
        else:
            st.write("No care-seeking data found.")
            
        st.subheader("Facility Analytics")
        if stats['facilities']:
            st.write("Top Facilities by Generated Encounters")
            df_fac = pd.DataFrame(list(stats['facilities'].items()), columns=['Facility', 'Encounters']).sort_values('Encounters', ascending=False).head(10)
            st.dataframe(df_fac, use_container_width=True)
        else:
            st.write("No facility encounters found.")
            
        st.subheader("Physiological Summary")
        if stats['vitals']:
            vit_data = []
            for k, v_list in stats['vitals'].items():
                arr = np.array(v_list)
                vit_data.append({
                    'Metric': k,
                    'Mean': round(np.mean(arr), 2),
                    'Median': round(np.median(arr), 2),
                    'Min': round(np.min(arr), 2),
                    'Max': round(np.max(arr), 2)
                })
            st.dataframe(pd.DataFrame(vit_data), use_container_width=True)
        else:
            st.write("No vital signs generated.")



@st.cache_data(show_spinner=False)
def get_sample_patients(out_dir, ref_time):
    samples = []
    # Try JSONL first (note standard exporter puts it in out_dir directly or out_dir/json)
    json_path = os.path.join(out_dir, "json", "patients.jsonl")
    if not os.path.exists(json_path):
        json_path = os.path.join(out_dir, "patients.jsonl")
        
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            for _ in range(100):
                line = f.readline()
                if not line: break
                try:
                    p = json.loads(line)
                    pid = p['id']
                    name = f"{p['attributes'].get('first_name', '')} {p['attributes'].get('last_name', '')}"
                    samples.append((pid, name))
                except:
                    pass
        return samples
        
    # Fallback CSV
    csv_path = os.path.join(out_dir, "csv", "patients.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, nrows=100)
            for _, row in df.iterrows():
                samples.append((row['Id'], f"{row.get('FIRST', '')} {row.get('LAST', '')}"))
        except:
            pass
    return samples

@st.cache_data(show_spinner=False)
def fetch_patient_record(out_dir, pid, ref_time):
    json_path = os.path.join(out_dir, "json", "patients.jsonl")
    if not os.path.exists(json_path):
        json_path = os.path.join(out_dir, "patients.jsonl")
        
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            for line in f:
                if pid in line: # fast check
                    try:
                        p = json.loads(line)
                        if p['id'] == pid:
                            return p
                    except:
                        pass
    
    # Fallback to CSV (slower, but necessary if JSON not generated)
    csv_dir = os.path.join(out_dir, "csv")
    if not os.path.exists(csv_dir):
        return None
        
    pat_data = {}
    pat_file = os.path.join(csv_dir, "patients.csv")
    if os.path.exists(pat_file):
        for chunk in pd.read_csv(pat_file, chunksize=10000):
            match = chunk[chunk['Id'] == pid]
            if not match.empty:
                pat_data = match.iloc[0].to_dict()
                break
    if not pat_data:
        return None
        
    record = {
        'encounters': [], 'conditions': [], 'observations': [], 'medications': []
    }
    
    def fetch_csv_events(filename, list_name):
        fpath = os.path.join(csv_dir, filename)
        if os.path.exists(fpath):
            for chunk in pd.read_csv(fpath, chunksize=50000):
                if 'PATIENT' in chunk.columns:
                    match = chunk[chunk['PATIENT'] == pid]
                    for _, row in match.iterrows():
                        record[list_name].append(row.to_dict())
                        
    fetch_csv_events("conditions.csv", "conditions")
    fetch_csv_events("encounters.csv", "encounters")
    fetch_csv_events("observations.csv", "observations")
    fetch_csv_events("medications.csv", "medications")
    
    # Restructure CSV dict to look like JSON dict roughly
    return {
        'id': pid,
        'attributes': {
            'state': pat_data.get('STATE'),
            'lga': pat_data.get('LGA'),
            'birthdate': pat_data.get('BIRTHDATE'),
            'gender': pat_data.get('GENDER'),
            'first_name': pat_data.get('FIRST'),
            'last_name': pat_data.get('LAST'),


            'deathdate': pat_data.get('DEATHDATE'),
        },
        'record': record,
        '_source': 'csv' # flag that it's from CSV so rendering adapts if fields differ slightly
    }

@st.cache_data(show_spinner=False)
def fetch_fhir_record(out_dir, pid, ref_time):
    fhir_dir = os.path.join(out_dir, "fhir")
    if not os.path.exists(fhir_dir):
        return None
        
    # Search bundles for the patient ID
    for f_name in os.listdir(fhir_dir):
        if not f_name.endswith('.json'): continue
        path = os.path.join(fhir_dir, f_name)
        
        # Fast text scan before parsing full json
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if pid not in content:
                continue
                
        # If ID is in string, parse and extract relevant resources
        try:
            with open(path, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
                
            patient_resources = []
            for entry in bundle.get('entry', []):
                res = entry.get('resource', {})
                if res.get('id') == pid or res.get('subject', {}).get('reference') == f"urn:uuid:{pid}":
                    patient_resources.append(res)
                    
            if patient_resources:
                return {"resourceType": "Bundle", "type": "collection", "entry": [{"resource": r} for r in patient_resources]}
        except:
            pass
            
    return None

def render_patient_explorer():
    st.title("Patient Explorer")
    
    if not st.session_state.generation_completed or not st.session_state.output_dir:
        st.info("No generation results found. Please go to Generate and run a simulation first.")
        return
        
    out_dir = st.session_state.output_dir
    ref_time = st.session_state.summary.get('reference_time', time.time()*1000)
    
    samples = get_sample_patients(out_dir, ref_time)
    sample_opts = ["--- Select a Patient ---"] + [f"{pid} ({name})" for pid, name in samples]
    
    st.write("### Patient Selection")
    col1, col2 = st.columns(2)
    with col1:
        selected_dropdown = st.selectbox("Select from generated sample", sample_opts)
    with col2:
        search_id = st.text_input("Or search exact Patient ID")
        
    pid = None
    if search_id.strip():
        pid = search_id.strip()
    elif selected_dropdown != "--- Select a Patient ---":
        pid = selected_dropdown.split(" (")[0]
        
    if not pid:
        return
        
    with st.spinner("Loading patient record..."):
        p = fetch_patient_record(out_dir, pid, ref_time)
        
    if not p:
        st.error(f"Patient ID {pid} not found in output files.")
        return
        
    # Extractor helpers based on JSON vs CSV source
    attrs = p['attributes']
    rec = p['record']
    is_csv = p.get('_source') == 'csv'
    
    # 5. PATIENT HEADER
    st.markdown("---")
    try:
        bdate = float(attrs.get('birthdate', ref_time))
        ddate = attrs.get('deathdate')
        # Handle pandas NaN
        if ddate is not None and str(ddate).lower() != 'nan' and str(ddate).strip() != '':
            age_end = float(ddate)
            is_dead = True
        else:
            age_end = ref_time
            is_dead = False
        age = int((age_end - bdate) / (365.25 * 24 * 60 * 60 * 1000))
    except Exception as e:
        age = "Unknown"
        is_dead = False
        
    st.header(f"Patient: {pid}")
    status_badge = " (Deceased)" if is_dead else ""
    st.subheader(f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}{status_badge}")
    
    # Overview
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sex", attrs.get('gender', 'Unknown'))
    c2.metric("Age", age)
    c3.metric("State", attrs.get('state', 'Unknown'))
    c4.metric("LGA", attrs.get('lga', 'Unknown'))
    
    st.write("### Overview")
    ov1, ov2 = st.columns(2)
    with ov1:
        st.write("**Location:**")
        st.write(f"Nigeria > {attrs.get('state')} > {attrs.get('lga')}")
        fac = attrs.get('primary_facility_name') or attrs.get('FACILITY_NAME')
        if fac:
            st.write(f"**Facility:** {fac}")
    with ov2:
        st.write("**Socioeconomic Information:**")


        
    # Patient Summary
    st.info(f"""
    **Patient Summary**
    
    This synthetic patient is a {age}-year-old {attrs.get('gender')} from {attrs.get('lga')}, {attrs.get('state')}.
    
    Conditions recorded: {len(rec.get('conditions', []))}
    Healthcare encounters: {len(rec.get('encounters', []))}
    Observations: {len(rec.get('observations', []))}
    Medications: {len(rec.get('medications', []))}
    """)
    
    st.markdown("---")
    st.write("### Clinical Summary")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Conditions", "Encounters", "Observations", "Medications", "HealthRecord", "Clinical Timeline"])
    
    def format_ts(ts):
        if not ts or pd.isna(ts): return "Present"
        try:
            return pd.to_datetime(ts, unit='ms').strftime('%Y-%m-%d')
        except:
            return str(ts)
            
    with tab1:
        conds = rec.get('conditions', [])
        if conds:
            c_data = []
            for c in conds:
                if is_csv:
                    name = c.get('DESCRIPTION')
                    start = c.get('START')
                    stop = c.get('STOP')
                else:
                    name = c['codes'][0]['display'] if c.get('codes') else 'Unknown'
                    start = c.get('start')
                    stop = c.get('stop')
                c_data.append({"Condition": name, "Onset": format_ts(start), "Resolution": format_ts(stop)})
            st.dataframe(pd.DataFrame(c_data), use_container_width=True)
        else:
            st.write("No conditions recorded.")
            
    with tab2:
        encs = rec.get('encounters', [])
        if encs:
            e_data = []
            for e in encs:
                if is_csv:
                    name = e.get('DESCRIPTION')
                    start = e.get('START')
                    cls = e.get('ENCOUNTERCLASS')
                    fac = e.get('FACILITY_NAME')
                else:
                    name = e['codes'][0]['display'] if e.get('codes') else 'Unknown'
                    start = e.get('start')
                    cls = e.get('encounter_class')
                    fac = e.get('facility_name')
                e_data.append({"Date": format_ts(start), "Type": cls, "Description": name, "Facility": fac})
            st.dataframe(pd.DataFrame(e_data), use_container_width=True)
        else:
            st.write("No encounters recorded.")
            
    with tab3:
        obs = rec.get('observations', [])
        if obs:
            o_data = []
            for o in obs:
                if is_csv:
                    name = o.get('DESCRIPTION')
                    start = o.get('DATE')
                    val = o.get('VALUE')
                else:
                    name = o['codes'][0]['display'] if o.get('codes') else 'Unknown'
                    start = o.get('start')
                    val = o.get('value')
                o_data.append({"Date": format_ts(start), "Observation": name, "Value": val})
            st.dataframe(pd.DataFrame(o_data), use_container_width=True)
        else:
            st.write("No observations recorded.")
            
    with tab4:
        meds = rec.get('medications', [])
        if meds:
            m_data = []
            for m in meds:
                if is_csv:
                    name = m.get('DESCRIPTION')
                    start = m.get('START')
                    stop = m.get('STOP')
                else:
                    name = m['codes'][0]['display'] if m.get('codes') else 'Unknown'
                    start = m.get('start')
                    stop = m.get('stop')
                m_data.append({"Medication": name, "Start": format_ts(start), "Stop": format_ts(stop)})
            st.dataframe(pd.DataFrame(m_data), use_container_width=True)
        else:
            st.write("No medications recorded.")
            
    with tab5:
        st.write("### HealthRecord JSON/Dict Dump")
        st.json(rec)
            
    with tab6:
        st.write("### Chronological HealthRecord Timeline")
        # Build timeline
        events = []
        events.append((attrs.get('birthdate', 0), "Demographic", "Birth"))
        if is_dead:
            events.append((attrs.get('deathdate'), "Demographic", "Death"))
        
        for c in rec.get('conditions', []):
            start = c.get('START') if is_csv else c.get('start')
            name = c.get('DESCRIPTION') if is_csv else (c['codes'][0]['display'] if c.get('codes') else 'Unknown')
            if pd.notna(start): events.append((start, "Condition", name))
            
        for e in rec.get('encounters', []):
            start = e.get('START') if is_csv else e.get('start')
            name = e.get('DESCRIPTION') if is_csv else (e['codes'][0]['display'] if e.get('codes') else 'Unknown')
            if pd.notna(start): events.append((start, "Encounter", name))
            
        for o in rec.get('observations', []):
            start = o.get('DATE') if is_csv else o.get('start')
            name = o.get('DESCRIPTION') if is_csv else (o['codes'][0]['display'] if o.get('codes') else 'Unknown')
            val = o.get('VALUE') if is_csv else o.get('value')
            if pd.notna(start): events.append((start, "Observation", f"{name}: {val}"))
            
        for m in rec.get('medications', []):
            start = m.get('START') if is_csv else m.get('start')
            name = m.get('DESCRIPTION') if is_csv else (m['codes'][0]['display'] if m.get('codes') else 'Unknown')
            if pd.notna(start): events.append((start, "Medication", name))
            
        events.sort(key=lambda x: float(x[0]) if x[0] else 0)
        
        filter_type = st.selectbox("Filter Timeline", ["All Events", "Condition", "Encounter", "Observation", "Medication"])
        
        for ts, ev_type, desc in events:
            if filter_type == "All Events" or filter_type == ev_type:
                st.write(f"**{format_ts(ts)}** | {ev_type} | {desc}")

    st.markdown("---")
    st.write("### Physiology")
    obs = rec.get('observations', [])
    vitals = {}
    for o in obs:
        if is_csv and o.get('CATEGORY') != 'vital-signs': continue
        if not is_csv: # simple heuristic for JSON: LOINC codes or common names
            name = o['codes'][0]['display'] if o.get('codes') else 'Unknown'
            # Check if name looks like a vital sign (JSON format doesn't natively tag 'vital-signs' in our simplistic export)
            if "pressure" not in name.lower() and "height" not in name.lower() and "weight" not in name.lower() and "mass" not in name.lower():
                continue
        else:
            name = o.get('DESCRIPTION')
            
        start = o.get('DATE') if is_csv else o.get('start')
        val = o.get('VALUE') if is_csv else o.get('value')
        
        if pd.notna(start) and pd.notna(val):
            try:
                v = float(val)
                if name not in vitals: vitals[name] = []
                vitals[name].append((float(start), v))
            except: pass
            
    if vitals:
        # Sort each vital sign chronologically
        for k in vitals:
            vitals[k].sort(key=lambda x: x[0])
            
        vital_name = st.selectbox("Select Vital Sign to Plot", list(vitals.keys()))
        if vital_name:
            v_data = vitals[vital_name]
            df_v = pd.DataFrame(v_data, columns=['TimeMs', 'Value'])
            df_v['Date'] = pd.to_datetime(df_v['TimeMs'], unit='ms')
            st.line_chart(df_v.set_index('Date')['Value'])
    else:
        st.write("No longitudinal physiological data available.")
        
    st.markdown("---")
    st.write("### FHIR R4")
    with st.expander("View FHIR Bundle"):
        fhir_rec = fetch_fhir_record(out_dir, pid, ref_time)
        if fhir_rec:
            st.json(fhir_rec)
        else:
            st.write("FHIR export not found for this patient.")
            
    st.markdown("---")
    
    if False:
        v_results = []
        v_results.append(("Patient ID valid", True))
        
        bdate = attrs.get('birthdate')
        if pd.notna(bdate) and float(bdate) <= time.time()*1000:
            v_results.append(("Date of birth valid", True))
        else:
            v_results.append(("Date of birth valid", False))
            
        v_results.append(("Geographic relationship valid", attrs.get('state') is not None and attrs.get('lga') is not None))
        
        chrono_valid = True
        for c in rec.get('conditions', []):
            start = c.get('START') if is_csv else c.get('start')
            if pd.notna(start) and pd.notna(bdate) and float(start) < float(bdate):
                chrono_valid = False
        v_results.append(("Condition chronology valid", chrono_valid))
        
        chrono_valid = True
        for e in rec.get('encounters', []):
            start = e.get('START') if is_csv else e.get('start')
            if pd.notna(start) and pd.notna(bdate) and float(start) < float(bdate):
                chrono_valid = False
        v_results.append(("Encounter chronology valid", chrono_valid))
        
        v_results.append(("FHIR references valid", fhir_rec is not None))
        
        all_pass = all(res for _, res in v_results)
        if all_pass: st.success("Patient Validation PASSED")
        else: st.error("Patient Validation FAILED")
        
        for desc, res in v_results:
            st.write(f"{'' if res else ''} {desc}")
            
    st.markdown("---")
    st.write("### Downloads")
    patient_json = json.dumps(p, indent=2)
    st.download_button("Download Patient JSON", data=patient_json, file_name=f"patient_{pid}.json", mime="application/json")
    if fhir_rec:
        st.download_button("Download Patient FHIR", data=json.dumps(fhir_rec, indent=2), file_name=f"patient_{pid}_fhir.json", mime="application/json")


if __name__ == "__main__":
    main()
