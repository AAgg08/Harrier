import streamlit as st
import pandas as pd
from backend.data_fetcher import get_metar_data
from backend.risk_model import RiskModel
from backend.historical import get_historical_context
from backend.utils import celsius_to_fahrenheit

# --- CONFIGURATION ---
st.set_page_config(
    page_title="HARRIER Safety", 
    page_icon="🦅", 
    layout="wide"
)

# --- MILITARY THEME (CSS) ---
st.markdown("""
    <style>
    h1 {color: #4CAF50;} 
    h2, h3 {color: #81C784;}
    .stProgress > div > div > div { background-color: #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None

# --- SIDEBAR ---
st.sidebar.header("🦅 HARRIER System")
st.sidebar.caption("Hazard Analysis & Real-time Risk Intelligence Evaluator")
page = st.sidebar.radio("Mission Control", ["Risk Analysis", "Flight Logs", "About"])

# --- MODULE 1: RISK ANALYSIS ---
if page == "Risk Analysis":
    st.title("HARRIER") 
    st.markdown("**Real-Time Hazard Assessment & NTSB Historical Cross-Check**")
    
    # Inputs
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            # 1. Get Input
            raw_input = st.text_input("Target Airport (ICAO)", "KADS", max_chars=4).upper()
            
            # 2. Auto-Fix Logic (Input "ADS" -> Converts to "KADS")
            if len(raw_input) == 3:
                icao = "K" + raw_input
            else:
                icao = raw_input
                
        with col2:
            st.write("") 
            st.write("") 
            analyze = st.button("EXECUTE ANALYSIS", type="primary")

    # Processing Logic
    if analyze:
        with st.spinner(f"Establishing Link to NOAA Satellite for {icao}..."):
            # Fetch Real Data (Free NOAA API)
            st.session_state.weather_data = get_metar_data(icao)

    # Display Logic
    if st.session_state.weather_data:
        data = st.session_state.weather_data
        
        # Check if we actually got data
        if not data:
            st.error(f"Connection Failed: No data found for {icao}. Check ICAO code.")
        else:
            # A. Tactical Dashboard
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Wind Velocity", f"{data['wind_speed_kt']} kt", f"{data['wind_direction_deg']}°")
            m2.metric("Visibility", f"{data['visibility_sm']} SM")
            cloud_str = data['clouds'][0] if data['clouds'] else "CLR"
            m3.metric("Ceiling", cloud_str)
            
            # B. Historical Context (NTSB Data)
            st.divider()
            count, sev, desc = get_historical_context(
                data['icao'], data['wind_speed_kt'], data['wind_direction_deg']
            )
            
            if count > 0:
                color = "#FF5252" if sev == "Fatal" else "#FFB74D" # Red or Orange
                st.markdown(
                    f"""
                    <div style="padding: 15px; border-radius: 5px; background-color: rgba(255, 0, 0, 0.1); border-left: 5px solid {color};">
                        <h4 style="color: {color}; margin:0;">⚠️ HISTORICAL ALERT TRIGGERED</h4>
                        <p style="margin:0;">{desc}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.success("HISTORICAL CHECK: CLEAR. No matching accidents in database.")

            # C. Risk Model Calculation
            model = RiskModel()
            score, factors, level = model.predict(data)
            
            st.subheader("Mission Risk Profile")
            
            # Dynamic Color Bar
            bar_color = "#4CAF50" if score < 30 else "#FF9800" if score < 60 else "#F44336"
            st.markdown(f"<style>.stProgress > div > div > div {{ background-color: {bar_color}; }}</style>", unsafe_allow_html=True)
            st.progress(score / 100)
            
            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric("Risk Score", f"{score}/100", level)
            with c2:
                if factors:
                    st.write("**Identified Hazards:**")
                    for f in factors:
                        st.markdown(f"- 🔸 {f}")
                else:
                    st.write("*Conditions Nominal. No significant hazards detected.*")

# --- MODULE 2: FLIGHT LOGS ---
elif page == "Flight Logs":
    st.title("📂 Mission Logs")
    st.write("Upload pilot logbook (.csv) for post-mission analysis.")
    
    uploaded_file = st.file_uploader("Upload Log File", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Logbook Decrypted Successfully.")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Decryption Error: {e}")

# --- MODULE 3: ABOUT ---
elif page == "About":
    st.title("About HARRIER")
    st.info("H.A.R.R.I.E.R. (Hazard Analysis & Real-time Risk Intelligence EvaluatoR) is a student project designed to enhance aviation safety decision making.")