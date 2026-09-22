import streamlit as st
import os
import json
import time
import pandas as pd
from services.analytics_service import fetch_patient_record

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
                    st.markdown(f"**{t_str}** 👶 *{desc}*")
                elif e_type == "Encounter":
                    st.markdown(f"**{t_str}** 🏥 {desc}")
                elif e_type == "Condition":
                    st.markdown(f"**{t_str}** ⚠️ {desc}")
                elif e_type == "Medication":
                    st.markdown(f"**{t_str}** 💊 {desc}")
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