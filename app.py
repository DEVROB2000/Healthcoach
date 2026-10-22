import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import date

st.set_page_config(page_title="MONSTER.OS // Performance Hub", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #07080a; color: #f1f4f9; }
    div[data-testid="stMetricValue"] { color: #d2ff28; font-family: monospace; font-weight: 900; }
    div[data-testid="stMetricLabel"] { color: #828ea2; font-weight: 700; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

STATE_FILE = os.path.expanduser("~/.monster_os_state.json")

default_state = {
    "gtg": {"pullups": 85, "dips": 110, "core": 60},
    "garmin": {"hrv": 71, "rhr": 47, "bb": 91, "sleep": 88, "steps": 13240},
    "body_comp": [
        {"date": "10 Sep", "weight": 84.8, "fat": 14.8, "lbm": 72.2},
        {"date": "24 Sep", "weight": 84.1, "fat": 14.2, "lbm": 72.1},
        {"date": "08 Okt", "weight": 83.6, "fat": 13.9, "lbm": 72.0},
        {"date": "15 Okt", "weight": 83.4, "fat": 13.8, "lbm": 71.9}
    ],
    "sports": [
        {"date": "2026-10-20", "sport": "Wingfoil (IJmeer)", "duration": 105, "calories": 820, "detail": "Max 35.8 km/u • HR 146"},
        {"date": "2026-10-17", "sport": "Padel Match", "duration": 90, "calories": 940, "detail": "Club Match • HR 154"}
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

st.sidebar.title("⚡ MONSTER.OS")
st.sidebar.caption("Speediance GM2 × Garmin Fenix 7S")

total_tonnage = sum([w["volume"] for w in state["workouts"]])
latest_body = state["body_comp"][-1]
g_data = state["garmin"]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("GM2 Week Tonnage", f"{int(total_tonnage):,} kg".replace(",", "."), f"{len(state['workouts'])} sessies geladen")
c2.metric("Garmin Readiness", f"BB {g_data['bb']}% | HRV {g_data['hrv']}ms", f"RHR {g_data['rhr']} bpm")
c3.metric("Stappen Vandaag", f"{g_data['steps']:,}".replace(",", "."), "Doel: 12.000")
c4.metric("Fitdays Compositie", f"{latest_body['weight']} kg ({latest_body['fat']}%)", f"LBM: {latest_body['lbm']} kg")
c5.metric("Grease the Groove", f"{state['gtg']['pullups']} Pulls / {state['gtg']['dips']} Dips", f"Core: {state['gtg']['core']} reps")

t1, t2, t3, t4 = st.tabs([
    "📊 1. Kracht, PR's & Speediance Deep-Dive",
    "⚖️ 2. Fitdays Recomposition & Galpin Matrix",
    "🏄‍♂️ 3. Garmin, Wingfoil, Padel & GTG",
    "🧠 4. AI Coach & Data Briefing"
])

with t1:
    st.subheader("Speediance Gym Monster 2 — Diepe Rep & Wattage Analyse")
    all_ex = []
    for w in state["workouts"]:
        for ex in w["exercises"]:
            all_ex.append({
                "Datum": w["date"],
                "Workout": w["title"],
                "Oefening": ex["name"],
                "Spiergroep": ex["muscle"],
                "Sets": ex["sets"],
                "Max Gewicht (kg)": ex["max_weight"],
                "Est. 1RM (kg)": ex["est_1rm"],
                "Piek Vermogen (Watt)": ex["max_watts"],
                "Laatste Rep Snelheid (m/s)": ex["min_speed"],
                "Symmetrie (L/R)": ex["lr_balance"]
            })
    df_ex = pd.DataFrame(all_ex)
    st.dataframe(df_ex, use_container_width=True, hide_index=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pr = px.bar(df_ex, x="Oefening", y="Est. 1RM (kg)", color="Spiergroep", title="Personal Records — Berekende 1RM (kg)", template="plotly_dark")
        st.plotly_chart(fig_pr, use_container_width=True)
    with col_b:
        fig_watts = px.bar(df_ex, x="Oefening", y="Piek Vermogen (Watt)", color="Workout", title="Explosieve Kracht — Piek Wattage", template="plotly_dark")
        st.plotly_chart(fig_watts, use_container_width=True)

with t2:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Fitdays Lichaamsrecompositie")
        df_body = pd.DataFrame(state["body_comp"])
        fig_body = go.Figure()
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["weight"], name="Gewicht (kg)", line=dict(color="#d2ff28", width=3)))
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["lbm"], name="Droge Spiermassa LBM (kg)", line=dict(color="#00f0ff", width=3)))
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["fat"], name="Vetpercentage (%)", line=dict(color="#ff6d2e", width=3), yaxis="y2"))
        fig_body.update_layout(template="plotly_dark", yaxis=dict(title="Kilo (kg)"), yaxis2=dict(title="Vet %", overlaying="y", side="right"), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_body, use_container_width=True)
    with col_r:
        st.subheader("Andy Galpin Hypertrofie Matrix (Doel: 10-20 Sets)")
        vol_map = {"Borst": 0, "Rug": 0, "Schouders": 0, "Benen": 0, "Armen": 0, "Core": 0}
        for ex in all_ex:
            m = ex["Spiergroep"]
            if m in vol_map:
                vol_map[m] += ex["Sets"]
        vol_map["Rug"] += round(state["gtg"]["pullups"] / 10)
        vol_map["Borst"] += round(state["gtg"]["dips"] / 12)
        df_vol = pd.DataFrame([{"Spiergroep": k, "Wekelijkse Sets": v} for k, v in vol_map.items()])
        fig_vol = px.bar(df_vol, x="Wekelijkse Sets", y="Spiergroep", orientation="h", title="Totaal Wekelijkse Sets", template="plotly_dark", color="Wekelijkse Sets", color_continuous_scale="Viridis")
        st.plotly_chart(fig_vol, use_container_width=True)

with t3:
    st.subheader("Grease the Groove Quick-Logger")
    g1, g2, g3 = st.columns(3)
    if g1.button("➕ +5 Pull-ups"):
        state["gtg"]["pullups"] += 5
        save_state(state)
        st.rerun()
    if g2.button("➕ +8 Dips"):
        state["gtg"]["dips"] += 8
        save_state(state)
        st.rerun()
    if g3.button("➕ +10 Core"):
        state["gtg"]["core"] += 10
        save_state(state)
        st.rerun()
    st.divider()
    st.subheader("Garmin Outdoor Sessies")
    st.dataframe(pd.DataFrame(state["sports"]), use_container_width=True, hide_index=True)

with t4:
    st.subheader("Data Briefing voor Google AI Studio")
    briefing = {
        "garmin_readiness": state["garmin"],
        "fitdays_laatste_meting": state["body_comp"][-1],
        "grease_the_groove": state["gtg"],
        "recente_sport": state["sports"],
        "speediance_analyse": all_ex
    }
    st.code(json.dumps(briefing, indent=2), language="json")
