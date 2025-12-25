import pandas as pd
import streamlit as st
import os

DATA_PATH = "data/ntsb_data.csv"

# Self-healing: Create dummy data if file is missing
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DATA_PATH):
    # Mock data for immediate demo
    mock_df = pd.DataFrame({
        'Airport_Code': ['KADS', 'KADS', 'KSFO'],
        'Wind_Speed_Kt': [15, 18, 25],
        'Wind_Dir_Deg': [180, 170, 270],
        'Injury_Severity': ['Non-Fatal', 'Non-Fatal', 'Fatal']
    })
    mock_df.to_csv(DATA_PATH, index=False)

@st.cache_data
def load_accident_data():
    try:
        return pd.read_csv(DATA_PATH)
    except Exception:
        return pd.DataFrame()

def get_historical_context(airport_code, wind_spd, wind_dir):
    df = load_accident_data()
    
    if df.empty:
        return 0, "None", "Database unavailable."

    # 1. Filter by Airport
    df = df[df['Airport_Code'] == airport_code.upper()]
    if df.empty:
        return 0, "None", "No recorded accidents at this airport."

    # 2. Fuzzy Match
    df['Wind_Speed_Kt'] = df['Wind_Speed_Kt'].fillna(0)
    
    matches = df[
        (df['Wind_Speed_Kt'] >= (wind_spd - 5)) & 
        (df['Wind_Speed_Kt'] <= (wind_spd + 5))
    ]
    
    count = len(matches)
    if count == 0:
        return 0, "None", "No accidents under these wind conditions."
        
    severity = "Fatal" if "Fatal" in matches['Injury_Severity'].values else "Non-Fatal"
    return count, severity, f"{count} similar accidents in past records."
