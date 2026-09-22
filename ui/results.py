import streamlit as st
import pandas as pd
import numpy as np
from services.analytics_service import compute_analytics

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
        states, _ = st.session_state.geo_data
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