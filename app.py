import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import date

# PAGE CONFIG & CYBERPUNK / OBSIDIAN STYLING
st.set_page_config(
    page_title="MONSTER.OS // Apex Performance Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Obsidian Dark Theme */
    .stApp { background-color: #07080a; color: #f3f5f8; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #0f1115; border-right: 1px solid #232834; }
    
    /* Metrics override */
    div[data-testid="stMetric"] { background: #0f1115; border: 1px solid #232834; padding: 16px; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
    div[data-testid="stMetricValue"] { color: #d2ff28 !important; font-family: monospace; font-weight: 900; font-size: 28px !important; }
    div[data-testid="stMetricLabel"] { color: #8a93a6 !important; font-weight: 700; text-transform: uppercase; font-size: 11px !important; letter-spacing: 0.8px; }
    
    /* Headers & Text */
    h1, h2, h3 { color: #f3f5f8; letter-spacing: -0.5px; }
    p, span, label { color: #c0c8d8; }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #0f1115; padding: 10px; border-radius: 12px; border: 1px solid #232834; }
    .stTabs [data-baseweb="tab"] { background-color: #161920; border-radius: 8px; color: #8a93a6; font-weight: 700; padding: 10px 18px; border: 1px solid #232834; }
    .stTabs [aria-selected="true"] { background-color: rgba(210, 255, 40, 0.12) !important; color: #d2ff28 !important; border-color: rgba(210, 255, 40, 0.4) !important; }
</style>
""", unsafe_allow_html=True)

STATE_FILE = os.path.expanduser("~/.monster_os_state.json")

default_state = {
    "gtg": {"pullups": 85, "dips": 110, "core": 60},
    "garmin": {"hrv": 71, "rhr": 47, "bb": 91, "sleep": 88, "steps": 13240},
    "body_comp": [
        {"date": "10 Sep", "weight": 84.8, "fat": 14.8, "lbm": 72.2},
        {"date": "17 Sep", "weight": 84.4, "fat": 14.5, "lbm": 72.1},
        {"date": "24 Sep", "weight": 84.1, "fat": 14.2, "lbm": 72.1},
        {"date": "01 Okt", "weight": 83.9, "fat": 14.0, "lbm": 72.1},
        {"date": "08 Okt", "weight": 83.6, "fat": 13.9, "lbm": 72.0},
        {"date": "15 Okt", "weight": 83.4, "fat": 13.8, "lbm": 71.9}
    ],
    "sports": [
        {"date": "2026-10-20", "sport": "Wingfoil (IJmeer)", "duration": 105, "calories": 820, "detail": "Max 35.8 km/u • HR 146"},
        {"date": "2026-10-17", "sport": "Padel Club Match", "duration": 90, "calories": 940, "detail": "Match • HR 154"}
    ],
    "workouts": [
        {
            "date": "2026-10-21", "title": "Rob PPL - Day 2: Pull", "volume": 5325.5, "duration": 53, "calories": 364,
            "exercises": [
                {"name": "Incline Single-Arm 45-Degree Row", "muscle": "Rug", "sets": 8, "max_weight": 28.5, "est_1rm": 36.1, "max_watts": 228.5, "min_speed": 0.40, "lr_balance": "98% (L: 28.5kg / R: 28.5kg)"},
                {"name": "Standing Tricep Rope Face Pull", "muscle": "Schouders", "sets": 3, "max_weight": 16.5, "est_1rm": 23.1, "max_watts": 169.0, "min_speed": 0.79, "lr_balance": "100% Dual"},
                {"name": "Seated Single-Arm High Row", "muscle": "Rug", "sets": 4, "max_weight": 24.5, "est_1rm": 33.5, "max_watts": 195.1, "min_speed": 0.56, "lr_balance": "94% (L: 23kg / R: 24.5kg)"},
                {"name": "Standing High-to-Low Woodchops", "muscle": "Core", "sets": 4, "max_weight": 16.5, "est_1rm": 23.1, "max_watts": 232.3, "min_speed": 0.74, "lr_balance": "100% (L: 16.5kg / R: 16.5kg)"},
                {"name": "Standing Dual-Handle Biceps Curl", "muscle": "Armen", "sets": 3, "max_weight": 17.0, "est_1rm": 22.7, "max_watts": 162.9, "min_speed": 0.54, "lr_balance": "97% (L: 16.5kg / R: 17kg)"},
                {"name": "Weighted Leg Lift", "muscle": "Core", "sets": 4, "max_weight": 14.0, "est_1rm": 18.2, "max_watts": 110.0, "min_speed": 0.50, "lr_balance": "100%"}
            ]
        },
        {
            "date": "2026-10-19", "title": "Rob PPL - Day 1: Push", "volume": 8036.0, "duration": 79, "calories": 500,
            "exercises": [
                {"name": "Barbell Bench Press", "muscle": "Borst", "sets": 6, "max_weight": 73.0, "est_1rm": 85.2, "max_watts": 193.7, "min_speed": 0.15, "lr_balance": "99% (L: 36.5kg / R: 36.5kg)"},
                {"name": "Incline Dual-Handle Chest Press", "muscle": "Borst", "sets": 3, "max_weight": 22.5, "est_1rm": 30.0, "max_watts": 193.0, "min_speed": 0.45, "lr_balance": "99% (L: 22.5kg / R: 22.5kg)"},
                {"name": "Supine Dual-Handle Chest Fly", "muscle": "Borst", "sets": 3, "max_weight": 16.0, "est_1rm": 22.4, "max_watts": 93.2, "min_speed": 0.33, "lr_balance": "100% (L: 16kg / R: 16kg)"},
                {"name": "Seated Dual-Handle Shoulder Press", "muscle": "Schouders", "sets": 3, "max_weight": 20.0, "est_1rm": 25.3, "max_watts": 139.6, "min_speed": 0.45, "lr_balance": "98% (L: 20kg / R: 20kg)"},
                {"name": "Standing Dual-Handle Lateral Raise", "muscle": "Schouders", "sets": 3, "max_weight": 8.0, "est_1rm": 10.7, "max_watts": 77.2, "min_speed": 0.49, "lr_balance": "100% (L: 8kg / R: 8kg)"}
            ]
        }
    ]
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return default_state

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=2)

state = load_state()

# SIDEBAR CONTROLS
st.sidebar.title("⚡ MONSTER.OS APEX")
st.sidebar.caption("Speediance GM2 • Garmin Fenix 7S")

with st.sidebar.expander("⚖️ Fitdays Lichaam Loggen", expanded=False):
    w_in = st.number_input("Gewicht (kg)", value=float(state["body_comp"][-1]["weight"]), step=0.1)
    f_in = st.number_input("Vet %", value=float(state["body_comp"][-1]["fat"]), step=0.1)
    if st.button("Opslaan Meting"):
        lbm = round(w_in * (100.0 - f_in) / 100.0, 1)
        state["body_comp"].append({"date": date.today().strftime("%d %b"), "weight": w_in, "fat": f_in, "lbm": lbm})
        save_state(state)
        st.success("Opgeslagen!")
        st.rerun()

with st.sidebar.expander("🏄‍♂️ Sport Toevoegen", expanded=False):
    sp_type = st.selectbox("Type", ["Wingfoil (IJmeer)", "Padel Match", "Rucking"])
    sp_dur = st.number_input("Duur (min)", value=90)
    sp_det = st.text_input("Details", value="Max 35.8 km/u")
    if st.button("Voeg Toe"):
        state["sports"].insert(0, {"date": date.today().isoformat(), "sport": sp_type, "duration": sp_dur, "calories": 850, "detail": sp_det})
        save_state(state)
        st.success("Toegevoegd!")
        st.rerun()

# MAIN HEADER METRICS
total_tonnage = sum([w["volume"] for w in state["workouts"]])
latest_body = state["body_comp"][-1]
g_data = state["garmin"]

st.title("⚡ MONSTER.OS // PERFORMANCE COCKPIT")
st.caption("Live Cloud Dashboard voor Robertus Kok • Almere Duin")

c1, c2, c3, c4 = st.columns(4)
c1.metric("GM2 Week Tonnage", f"{int(total_tonnage):,} kg".replace(",", "."), "Push & Pull geladen")
c2.metric("Garmin Readiness", f"BB {g_data['bb']}%", f"HRV {g_data['hrv']} ms")
c3.metric("Fitdays Gewicht", f"{latest_body['weight']} kg", f"Vet: {latest_body['fat']}%")
c4.metric("Grease the Groove", f"{state['gtg']['pullups']} Pulls", f"{state['gtg']['dips']} Dips")

st.divider()

# TABS
t1, t2, t3, t4 = st.tabs([
    "📊 1. Kracht & Speediance Deep-Dive",
    "⚖️ 2. Lichaamscompositie & Galpin Matrix",
    "🏄‍♂️ 3. Outdoor Sport & GTG Tellers",
    "🧠 4. AI Data Briefing (Voor AI Studio)"
])

with t1:
    st.subheader("Geverifieerde Speediance Gym Monster 2 Historie")
    all_ex = []
    for w in state["workouts"]:
        for ex in w["exercises"]:
            all_ex.append({
                "Datum": w["date"],
                "Workout": w["title"],
                "Oefening": ex["name"],
                "Spier": ex["muscle"],
                "Sets": ex["sets"],
                "Max Kilo": ex["max_weight"],
                "Est. 1RM": ex["est_1rm"],
                "Piek Watt": ex["max_watts"],
                "Min Snelheid": ex["min_speed"]
            })
    df_ex = pd.DataFrame(all_ex)
    st.dataframe(df_ex, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(df_ex, x="Oefening", y="Est. 1RM", color="Spier", title="Berekende 1RM per Oefening (kg)", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(df_ex, x="Oefening", y="Piek Watt", color="Workout", title="Piek Vermogen (Watt)", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

with t2:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Gewicht & Vetpercentage Trend")
        df_body = pd.DataFrame(state["body_comp"])
        fig_body = go.Figure()
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["weight"], name="Gewicht (kg)", line=dict(color="#d2ff28", width=3)))
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["lbm"], name="Spiermassa LBM (kg)", line=dict(color="#00f0ff", width=3)))
        fig_body.update_layout(template="plotly_dark", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_body, use_container_width=True)
    with col_r:
        st.subheader("Andy Galpin Sets Matrix (Doel: 10-20 Sets)")
        vol_map = {"Borst": 8, "Rug": 12, "Schouders": 7, "Benen": 6, "Armen": 5, "Core": 6}
        df_vol = pd.DataFrame([{"Spiergroep": k, "Sets": v} for k, v in vol_map.items()])
        fig_vol = px.bar(df_vol, x="Sets", y="Spiergroep", orientation="h", template="plotly_dark", color="Sets", color_continuous_scale="Viridis")
        fig_vol.add_vline(x=10, line_dash="dash", line_color="#d2ff28")
        fig_vol.add_vline(x=20, line_dash="dash", line_color="#ff2e63")
        st.plotly_chart(fig_vol, use_container_width=True)

with t3:
    st.subheader("Grease the Groove Quick-Logger")
    b1, b2, b3 = st.columns(3)
    if b1.button("➕ +5 Pull-ups", use_container_width=True):
        state["gtg"]["pullups"] += 5
        save_state(state)
        st.rerun()
    if b2.button("➕ +8 Dips", use_container_width=True):
        state["gtg"]["dips"] += 8
        save_state(state)
        st.rerun()
    if b3.button("➕ +10 Core", use_container_width=True):
        state["gtg"]["core"] += 10
        save_state(state)
        st.rerun()
        
    st.divider()
    st.subheader("Garmin Outdoor Sessies (Wingfoil & Padel)")
    st.dataframe(pd.DataFrame(state["sports"]), use_container_width=True, hide_index=True)

with t4:
    st.subheader("Directe Data Briefing voor Google AI Studio")
    st.caption("Kopieer deze data en plak het in AI Studio om gerichte analyses te krijgen.")
    briefing = {
        "garmin_readiness": state["garmin"],
        "fitdays_laatste": state["body_comp"][-1],
        "grease_the_groove": state["gtg"],
        "outdoor_sport": state["sports"]
    }
    st.code(json.dumps(briefing, indent=2), language="json")
    
