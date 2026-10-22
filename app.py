pip3 install streamlit pandas plotly garminconnect google-generativeai && cat << 'EOF' > ~/monster_os.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import date, datetime

st.set_page_config(page_title="MONSTER.OS // Performance Hub", layout="wide", initial_sidebar_state="expanded")

# Custom Dark High-Contrast Styling
st.markdown("""
<style>
    .stApp { background-color: #07080a; color: #f1f4f9; }
    div[data-testid="stMetricValue"] { color: #d2ff28; font-family: monospace; font-weight: 900; }
    div[data-testid="stMetricLabel"] { color: #828ea2; font-weight: 700; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

STATE_FILE = os.path.expanduser("~/.monster_os_state.json")
GARMIN_TOKENS = os.path.expanduser("~/.garmin_tokens")

default_state = {
    "gtg": {"pullups": 85, "dips": 110, "core": 60},
    "garmin": {"hrv": 71, "rhr": 47, "bb": 91, "sleep": 88, "steps": 13240},
    "body_comp": [
        {"date": "2026-09-10", "weight": 84.8, "fat": 14.8, "lbm": 72.2},
        {"date": "2026-09-24", "weight": 84.1, "fat": 14.2, "lbm": 72.1},
        {"date": "2026-10-08", "weight": 83.6, "fat": 13.9, "lbm": 72.0},
        {"date": "2026-10-21", "weight": 83.4, "fat": 13.8, "lbm": 71.9}
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

def parse_speediance_json(raw_text):
    data = json.loads(raw_text)
    records = data.get("records", [])
    parsed_workouts = []
    part_map = {11: "Borst", 12: "Schouders", 13: "Rug", 14: "Benen", 15: "Benen", 16: "Armen", 17: "Core"}
    
    for r in records:
        summ = r.get("summary", {})
        if not summ or summ.get("totalCapacity", 0) == 0:
            continue
        w_date = str(summ.get("startTime", summ.get("createTime", "2026-10-21")))[:10]
        w_title = summ.get("title") or summ.get("name") or "Speediance GM2 Workout"
        w_vol = float(summ.get("totalCapacity", 0))
        w_dur = round(float(summ.get("trainingTime", 0)) / 60)
        w_cal = int(summ.get("calorie", 0))
        
        ex_list = []
        details = (r.get("detail") or {}).get("detail") or []
        for d in details:
            ex_name = d.get("actionLibraryName", "Oefening")
            part_id = d.get("trainingPartId2", 11)
            muscle = part_map.get(part_id, "Overig")
            reps_list = d.get("finishedReps") or []
            sets_cnt = len(reps_list)
            max_w = float(d.get("maxWeight", 0))
            
            # Extract deep watts & speed
            max_watts = 0.0
            min_speed = 99.0
            best_1rm = max_w * 1.25
            
            for rep_obj in reps_list:
                rep_cnt = int(rep_obj.get("finishedCount", 8))
                td = rep_obj.get("trainingInfoDetail") or {}
                weights = td.get("weights") or [max_w]
                top_set_w = max([float(x) for x in weights]) if weights else max_w
                est = round(top_set_w * (1 + rep_cnt / 30.0), 1)
                if est > best_1rm:
                    best_1rm = est
                
                lw = td.get("leftWatts") or []
                rw = td.get("rightWatts") or []
                for val in (lw + rw):
                    if float(val) > max_watts:
                        max_watts = round(float(val), 1)
                        
                ls = td.get("leftRopeSpeeds") or []
                rs = td.get("rightRopeSpeeds") or []
                for s_val in (ls + rs):
                    if 0.05 < float(s_val) < min_speed:
                        min_speed = round(float(s_val), 2)
                        
            if min_speed == 99.0:
                min_speed = 0.45
                
            l_max = d.get("leftMaxWeight", max_w)
            r_max = d.get("rightMaxWeight", max_w)
            lr_str = f"L: {l_max}kg / R: {r_max}kg" if d.get("isLeftRight") else "Dual / Symmetrisch"
            
            ex_list.append({
                "name": ex_name,
                "muscle": muscle,
                "sets": sets_cnt,
                "max_weight": max_w,
                "est_1rm": best_1rm,
                "max_watts": max_watts,
                "min_speed": min_speed,
                "lr_balance": lr_str
            })
            
        parsed_workouts.append({
            "date": w_date,
            "title": w_title,
            "volume": w_vol,
            "duration": w_dur,
            "calories": w_cal,
            "exercises": ex_list
        })
    return parsed_workouts

# SIDEBAR: DATA INGESTION & LIVE SYNC
st.sidebar.title("⚡ MONSTER.OS")
st.sidebar.caption("Speediance GM2 × Garmin Fenix 7S × Fitdays")

with st.sidebar.expander("📂 1. Speediance JSON Dropzone", expanded=False):
    sp_file = st.file_uploader("Sleep workout_history_deep.json hierheen", type=["json"])
    if sp_file is not None:
        try:
            new_w = parse_speediance_json(sp_file.read().decode("utf-8"))
            if new_w:
                state["workouts"] = new_w
                save_state(state)
                st.success(f"{len(new_w)} Speediance workouts diep ingeladen!")
        except Exception as e:
            st.error(f"Fout bij inlezen: {e}")

with st.sidebar.expander("⌚ 2. Garmin Fenix 7S Live Sync", expanded=False):
    g_email = st.text_input("Garmin E-mail", value="rhjakok@gmail.com")
    g_pass = st.text_input("Garmin Wachtwoord", type="password")
    if st.button("🔄 Nu Synchroniseren met Garmin"):
        try:
            from garminconnect import Garmin
            client = Garmin(g_email, g_pass)
            if os.path.exists(GARMIN_TOKENS):
                try:
                    client.login(GARMIN_TOKENS)
                except Exception:
                    client.login()
                    client.garth.dump(GARMIN_TOKENS)
            else:
                client.login()
                os.makedirs(GARMIN_TOKENS, exist_ok=True)
                client.garth.dump(GARMIN_TOKENS)
            today_str = date.today().isoformat()
            stats = client.get_user_summary(today_str) or {}
            acts = client.get_activities(0, 10) or []
            
            state["garmin"]["steps"] = stats.get("totalSteps") or state["garmin"]["steps"]
            state["garmin"]["rhr"] = stats.get("restingHeartRate") or state["garmin"]["rhr"]
            state["garmin"]["bb"] = stats.get("bodyBatteryMostRecentValue") or state["garmin"]["bb"]
            
            new_sports = []
            for a in acts:
                new_sports.append({
                    "date": str(a.get("startTimeLocal", ""))[:10],
                    "sport": a.get("activityName", "Garmin Sport"),
                    "duration": round((a.get("duration") or 0) / 60),
                    "calories": round(a.get("calories") or 0),
                    "detail": f"Max {round((a.get('maxSpeed') or 0)*3.6, 1)} km/u • HR {round(a.get('averageHR') or 0)}"
                })
            if new_sports:
                state["sports"] = new_sports
            save_state(state)
            st.success("Garmin Connect succesvol gesynchroniseerd!")
        except Exception as e:
            st.error(f"Garmin login melding: {e}")

with st.sidebar.expander("⚖️ 3. Fitdays / Lichaamsmeting", expanded=False):
    w_in = st.number_input("Gewicht (kg)", value=float(state["body_comp"][-1]["weight"]), step=0.1)
    f_in = st.number_input("Vetpercentage (%)", value=float(state["body_comp"][-1]["fat"]), step=0.1)
    if st.button("+ Log Fitdays Meting"):
        lbm = round(w_in * (100.0 - f_in) / 100.0, 1)
        state["body_comp"].append({"date": date.today().isoformat(), "weight": w_in, "fat": f_in, "lbm": lbm})
        save_state(state)
        st.success("Meting opgeslagen!")

# TOP KPI ROW
total_tonnage = sum([w["volume"] for w in state["workouts"]])
latest_body = state["body_comp"][-1]
g_data = state["garmin"]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("GM2 Week Tonnage", f"{int(total_tonnage):,} kg".replace(",", "."), f"{len(state['workouts'])} sessies geladen")
c2.metric("Garmin Readiness", f"BB {g_data['bb']}% | HRV {g_data['hrv']}ms", f"RHR {g_data['rhr']} bpm")
c3.metric("Stappen Vandaag", f"{g_data['steps']:,}".replace(",", "."), "Doel: 12.000")
c4.metric("Fitdays Compositie", f"{latest_body['weight']} kg ({latest_body['fat']}%)", f"LBM: {latest_body['lbm']} kg")
c5.metric("Grease the Groove", f"{state['gtg']['pullups']} Pulls / {state['gtg']['dips']} Dips", f"Core: {state['gtg']['core']} reps")

# TABS
t1, t2, t3, t4 = st.tabs([
    "📊 1. Kracht, PR's & Speediance Deep-Dive",
    "⚖️ 2. Fitdays Recomposition & Galpin Matrix",
    "🏄‍♂️ 3. Garmin, Wingfoil, Padel & GTG",
    "🧠 4. AI Coach & 1-Klik AI Studio Export"
])

with t1:
    st.subheader("Speediance Gym Monster 2 — Diepe Rep, Wattage & Snelheidsanalyse")
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
                "Symmetrie (L/R)": ex["lr_balance"],
                "Coach Advies Volgende Sessie": f"Verhoog naar {ex['max_weight'] + 2.0} kg" if ex["min_speed"] >= 0.35 else f"Houd op {ex['max_weight']} kg (0 RIR bereikt op {ex['min_speed']} m/s)"
            })
    df_ex = pd.DataFrame(all_ex)
    st.dataframe(df_ex, use_container_width=True, hide_index=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pr = px.bar(df_ex, x="Oefening", y="Est. 1RM (kg)", color="Spiergroep", title="Personal Records — Berekende 1RM per Oefening (kg)", template="plotly_dark")
        st.plotly_chart(fig_pr, use_container_width=True)
    with col_b:
        fig_watts = px.bar(df_ex, x="Oefening", y="Piek Vermogen (Watt)", color="Workout", title="Explosieve Kracht — Piek Wattage op de GM2 Kabels", template="plotly_dark")
        st.plotly_chart(fig_watts, use_container_width=True)

with t2:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Fitdays Lichaamsrecompositie (Lean & Mean)")
        df_body = pd.DataFrame(state["body_comp"])
        fig_body = go.Figure()
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["weight"], name="Gewicht (kg)", line=dict(color="#d2ff28", width=3)))
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["lbm"], name="Droge Spiermassa LBM (kg)", line=dict(color="#00f0ff", width=3)))
        fig_body.add_trace(go.Scatter(x=df_body["date"], y=df_body["fat"], name="Vetpercentage (%)", line=dict(color="#ff6d2e", width=3), yaxis="y2"))
        fig_body.update_layout(
            template="plotly_dark",
            yaxis=dict(title="Kilo (kg)"),
            yaxis2=dict(title="Vet %", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_body, use_container_width=True)
        
    with col_r:
        st.subheader("Andy Galpin Hypertrofie Matrix (Doel: 10-20 Sets/Week)")
        vol_map = {"Borst": 0, "Rug": 0, "Schouders": 0, "Benen": 0, "Armen": 0, "Core": 0}
        for ex in all_ex:
            m = ex["Spiergroep"]
            if m in vol_map:
                vol_map[m] += ex["Sets"]
        vol_map["Rug"] += round(state["gtg"]["pullups"] / 10)
        vol_map["Borst"] += round(state["gtg"]["dips"] / 12)
        vol_map["Core"] += round(state["gtg"]["core"] / 10)
        
        df_vol = pd.DataFrame([{"Spiergroep": k, "Wekelijkse Sets": v} for k, v in vol_map.items()])
        fig_vol = px.bar(df_vol, x="Wekelijkse Sets", y="Spiergroep", orientation="h", title="Totaal Wekelijkse Sets (Speediance + Pull-up/Dip Station)", template="plotly_dark", color="Wekelijkse Sets", color_continuous_scale="Viridis")
        fig_vol.add_vline(x=10, line_dash="dash", line_color="#d2ff28", annotation_text="Min (10)")
        fig_vol.add_vline(x=20, line_dash="dash", line_color="#ff2e63", annotation_text="Max (20)")
        st.plotly_chart(fig_vol, use_container_width=True)

with t3:
    st.subheader("Pull-up & Dip Station — Grease the Groove Quick-Logger")
    g1, g2, g3, g4 = st.columns(4)
    if g1.button("➕ +5 Strict Pull-ups", use_container_width=True):
        state["gtg"]["pullups"] += 5
        save_state(state)
        st.rerun()
    if g2.button("➕ +8 Parallel Bar Dips", use_container_width=True):
        state["gtg"]["dips"] += 8
        save_state(state)
        st.rerun()
    if g3.button("➕ +10 Hanging Leg Raises", use_container_width=True):
        state["gtg"]["core"] += 10
        save_state(state)
        st.rerun()
    if g4.button("🔄 Reset Week Tellers", use_container_width=True):
        state["gtg"] = {"pullups": 0, "dips": 0, "core": 0}
        save_state(state)
        st.rerun()
        
    st.divider()
    st.subheader("Wingfoil (IJmeer), Padel & Garmin Outdoor Sessies")
    df_sp = pd.DataFrame(state["sports"])
    st.dataframe(df_sp, use_container_width=True, hide_index=True)
    
    with st.expander("➕ Handmatig Wingfoil / Padel Sessie Toevoegen"):
        sp_type = st.selectbox("Sport", ["Wingfoil (IJmeer)", "Padel Match", "Rucking (Gewichtswandeling)"])
        sp_dur = st.number_input("Duur (minuten)", value=90)
        sp_cal = st.number_input("Calorieën (kcal)", value=850)
        sp_det = st.text_input("Details (Snelheid / HR)", value="Max 35.8 km/u • HR 148")
        if st.button("Sessie Opslaan"):
            state["sports"].insert(0, {"date": date.today().isoformat(), "sport": sp_type, "duration": sp_dur, "calories": sp_cal, "detail": sp_det})
            save_state(state)
            st.rerun()

with t4:
    st.subheader("1-Klik Data Briefing voor Google AI Studio & Gemini")
    st.caption("Kopieer het onderstaande blok met 1 klik rechtsboven in het tekstvak en plak het in Google AI Studio of onze Gemini chat voor een diepe analyse.")
    
    briefing = {
        "datum_export": date.today().isoformat(),
        "garmin_readiness": state["garmin"],
        "fitdays_laatste_meting": state["body_comp"][-1],
        "grease_the_groove_deze_week": state["gtg"],
        "recente_wingfoil_padel_sessies": state["sports"][:4],
        "speediance_gm2_diepe_analyse": all_ex
    }
    briefing_str = "Analyseer mijn actuele status en geef mijn exacte gewichten, reps en GM2 kabelmodus voor mijn training van vandaag:\n\n" + json.dumps(briefing, indent=2)
    st.code(briefing_str, language="json")
EOF
streamlit run ~/monster_os.py