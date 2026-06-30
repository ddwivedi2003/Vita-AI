import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
import time
import calendar
from streamlit_lottie import st_lottie
from streamlit_js_eval import get_geolocation

from .auth import AuthManager
from .data import DataManager
from .config import DISEASE_OPTIONS, CITY_COORDINATES
from .utils import calculate_distance, get_nearest_city_name, get_weather_health_analysis
from .ai import generate_daily_briefing, generate_trend_analysis, generate_ai_response


def login_user(username):
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.messages = []
    if "daily_briefing" in st.session_state: del st.session_state["daily_briefing"]


def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.messages = []
    if "daily_briefing" in st.session_state: del st.session_state["daily_briefing"]
    st.rerun()


def show_login_page(auth_db):
    # Centered layout using columns
    _, col_center, _ = st.columns([1, 1.5, 1])
    
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Main Card Container
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🛡️ Vita AI</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 20px;'>Intelligent Health Surveillance</p>", unsafe_allow_html=True)
            
            # Use tabs for a clean switch between Login and Signup
            tabs = st.tabs(["🔐 Login", "📝 Sign Up"])
            
            with tabs[0]:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("login_form"):
                    user = st.text_input("Username", placeholder="Enter your username")
                    pw = st.text_input("Password", type="password", placeholder="Enter your password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Access Dashboard", type="primary", use_container_width=True):
                        if auth_db.login(user, pw):
                            login_user(user)
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
            
            with tabs[1]:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("signup_form"):
                    new_user = st.text_input("New Username")
                    new_pw = st.text_input("New Password", type="password")
                    c1, c2 = st.columns(2)
                    with c1: new_age = st.number_input("Age", min_value=0, max_value=120, value=25)
                    with c2: new_gender = st.selectbox("Gender", ["Male", "Female", "Other", "N/A"])
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                        success, msg = auth_db.signup(new_user, new_pw, age=new_age, gender=new_gender)
                        if success: st.success(msg)
                        else: st.error(msg)
        
        # Bottom text
        st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #94a3b8; margin-top: 20px;'>Powered by Azure OpenAI & Streamlit</p>", unsafe_allow_html=True)


def show_dashboard(data_db):
    st.session_state.data_db = DataManager()
    data_db = st.session_state.data_db

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"### 👋 Hi, {st.session_state.username}")
        st.caption("📍 LOCATION")
        location_mode = st.radio("Locate By", ["Auto (GPS)", "Manual"], label_visibility="collapsed")
        
        user_lat, user_lng = 28.6139, 77.2090
        display_city_name = "Unknown"

        if location_mode == "Auto (GPS)":
            loc_data = get_geolocation(component_key='get_geo')
            if loc_data:
                user_lat = loc_data['coords']['latitude']
                user_lng = loc_data['coords']['longitude']
                display_city_name = get_nearest_city_name(user_lat, user_lng)
                st.success(f"GPS: {display_city_name}")
            else:
                st.warning("Waiting for GPS...")
                if st.button("🔄 Refresh GPS"): st.rerun()
        else:
            selected_city = st.selectbox("City", list(CITY_COORDINATES.keys()))
            if selected_city:
                user_lat, user_lng = CITY_COORDINATES[selected_city]
                display_city_name = selected_city
            with st.expander("Coordinates"):
                user_lat = st.number_input("Lat", value=user_lat, format="%.4f")
                user_lng = st.number_input("Lng", value=user_lng, format="%.4f")

        st.caption("🔍 FILTERS")
        scope = st.selectbox("Map Scope", ["Nearby (5-200km)", "Global"]) 
        radius_km = 5.0
        if scope.startswith("Nearby"):
            radius_km = st.slider("Radius (km)", 1.0, 200.0, 5.0, step=1.0)

        view_mode = st.radio("Data", ["Live", "History"]) 
        lookback_days = 30
        selected_year, selected_month = None, None
        if view_mode == "Live":
            lookback_days = st.slider("Past Days", 1, 365, 30)
        else:
            col_y, col_m = st.columns(2)
            with col_y:
                current_year = datetime.datetime.now().year
                selected_year = st.selectbox("Year", range(current_year, current_year - 6, -1))
            with col_m:
                month_names = list(calendar.month_name)[1:]
                selected_month_name = st.selectbox("Month", month_names)
                selected_month = month_names.index(selected_month_name) + 1
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary"): logout_user()

    # --- DATA & ANALYSIS ---
    if scope == "Global":
        all_df = data_db.get_data()
        if all_df.empty:
            nearby_df, risk_score, risk_label, map_df = pd.DataFrame(), 0, "Safe", pd.DataFrame()
        else:
            if view_mode == "History" and selected_year and selected_month:
                map_df = all_df[(all_df['timestamp'].dt.year == selected_year) & (all_df['timestamp'].dt.month == selected_month)].copy()
            else:
                cutoff_date = datetime.datetime.now() - datetime.timedelta(days=lookback_days)
                map_df = all_df[all_df['timestamp'] >= cutoff_date].copy()
            
            if not map_df.empty:
                map_df['distance_km'] = map_df.apply(lambda row: calculate_distance(user_lat, user_lng, row['lat'], row['lng']), axis=1)
                nearby_df = map_df[map_df['distance_km'] <= radius_km].copy()
            else:
                nearby_df = pd.DataFrame()
            
            total_risk = nearby_df['weight'].sum() if not nearby_df.empty else 0
            risk_label = 'Safe' if total_risk == 0 else ('High' if total_risk > 15 else 'Moderate')
            risk_score = round(total_risk,1)
    else:
        nearby_df, risk_score, risk_label, df_filtered = data_db.get_filtered_data(
            user_lat, user_lng, radius_km, "Historical Archive" if view_mode == "History" else "Live", lookback_days, selected_year, selected_month
        )
        map_df = df_filtered.copy() if not df_filtered.empty else nearby_df.copy()

    weather_data = get_weather_health_analysis(user_lat, user_lng)

    if "daily_briefing" not in st.session_state:
        user_profile = data_db.get_user_profile(st.session_state.username)
        if weather_data:
            with st.spinner("Analyzing health risks..."):
                st.session_state.daily_briefing = generate_daily_briefing(weather_data, nearby_df, user_profile)
        else: st.session_state.daily_briefing = "Waiting for weather data..."

    # --- MAIN UI ---
    col_t1, col_t2 = st.columns([0.8, 0.2])
    with col_t1: st.title("🛡️ Health Surveillance Dashboard")
    with col_t2: 
        if st.button("🔄 Refresh", type="primary"):
            if "daily_briefing" in st.session_state: del st.session_state["daily_briefing"]
            st.rerun()

    row1_c1, row1_c2, row1_c3 = st.columns([1, 1.3, 1])
    with row1_c1:
        st.markdown(f"""
        <div class="risk-box risk-{risk_label}">
            <div style="font-size:0.9rem; opacity:0.9; text-transform:uppercase; letter-spacing:1px; margin-bottom: 5px;">Risk Level</div>
            <h1 style="margin:0; font-size: 2.8rem; font-weight:800;">{risk_label}</h1>
            <div style="background:rgba(255,255,255,0.2); border-radius:8px; padding:4px 12px; margin-top:10px; font-weight:600;">Score: {risk_score}</div>
        </div>
        """, unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f"""
        <div class="dashboard-card" style="height: 100%; display: flex; flex-direction: column; justify-content: flex-start; margin-bottom:0;">
            <div class="card-title" style="color:#3b82f6;">🤖 AI Daily Outlook</div>
            <div style="font-size: 0.95rem; line-height: 1.6; color: #475569;">
                {st.session_state.get('daily_briefing', 'Loading...')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with row1_c3:
        if weather_data:
            st.markdown(f"""
            <div class="dashboard-card" style="height: 100%; margin-bottom:0; padding: 20px;">
                 <div class="card-title">🌤️ Biometeorology</div>
                 <div style="font-size:0.9rem; color:#64748b; margin-bottom:10px; font-weight:500;">📍 {display_city_name}</div>
                 <div class="weather-grid">
                    <div class="weather-item"><div class="weather-val">{weather_data['temp']}°C</div><div class="weather-label">Temp</div></div>
                    <div class="weather-item"><div class="weather-val">{weather_data['humidity']}%</div><div class="weather-label">Humid</div></div>
                    <div class="weather-item"><div class="weather-val">{weather_data['uv']}</div><div class="weather-label">UV</div></div>
                 </div>
            </div>
            """, unsafe_allow_html=True)
        else:
             st.markdown("""<div class="dashboard-card" style="height: 100%;"><div class="card-title">Weather</div>Offline</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_map, tab_chat, tab_trends, tab_alerts, tab_report, tab_profile = st.tabs([
        "📍 Live Map", "🤖 AI Doctor", "📈 Analytics", "⚠️ Alerts", "📢 Report Case", "👤 Profile"
    ])

    # MAP TAB - FIXED VISIBILITY
    with tab_map:
        st.caption("Visualizing disease clusters and user location.")
        user_layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame([{"lat": user_lat, "lng": user_lng, "disease": "You"}]),
            get_position="[lng, lat]",
            get_color="[0, 128, 255, 200]",
            get_radius=200,
            pickable=False
        )
        layers = [user_layer]
        if not map_df.empty:
            map_df['render_radius'] = map_df['weight'].fillna(1).clip(1,10) * (20000 if scope=="Global" else 100)
            layers.append(pdk.Layer(
                "ScatterplotLayer", 
                data=map_df, 
                get_position="[lng, lat]", 
                get_color="[220, 38, 38, 160]", 
                get_radius="render_radius", 
                pickable=True
            ))

        # View State Logic
        if scope == "Global" and not map_df.empty:
            view_lat = float(map_df['lat'].mean())
            view_lng = float(map_df['lng'].mean())
            zoom_level = 3
        else:
            view_lat = float(user_lat)
            view_lng = float(user_lng)
            zoom_level = 11

        view = pdk.ViewState(latitude=view_lat, longitude=view_lng, zoom=zoom_level)

        # FIXED MAP: Removed Mapbox style URL to force default rendering (avoids missing API key errors)
        st.pydeck_chart(
            pdk.Deck(
                map_style=None, 
                layers=layers, 
                initial_view_state=view, 
                tooltip={"html": "<div style='background:white; color:black; padding:5px; border-radius:5px;'><b>{disease}</b><br>Severity: {weight}</div>"}
            ),
            use_container_width=True
        )

    # OTHER TABS
    with tab_chat:
        col_main, col_info = st.columns([3, 1])
        with col_info:
            st.markdown("**Quick Check**")
            if st.button("🌡️ Fever", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "I have a fever, what should I do?"})
                st.rerun()
            if st.button("🤕 Headache", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "I have a severe headache."})
                st.rerun()
        with col_main:
            for msg in st.session_state.get('messages', []):
                avatar = "🧑‍💻" if msg['role'] == 'user' else "🤖"
                st.chat_message(msg['role'], avatar=avatar).write(msg['content'])
            prompt = st.chat_input("Describe your symptoms...")
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user", avatar="🧑‍💻").write(prompt)
                with st.spinner("Dr. Vita is thinking..."):
                    resp = generate_ai_response(prompt, risk_label, data_db)
                st.session_state.messages.append({"role": "assistant", "content": resp})
                st.chat_message("assistant", avatar="🤖").write(resp)

    with tab_trends:
        if not nearby_df.empty:
            nearby_df['date'] = nearby_df['timestamp'].dt.date
            daily_counts = nearby_df.groupby('date').size()
            c_g, c_a = st.columns([2,1])
            with c_g:
                st.markdown("##### Disease Spread")
                st.line_chart(daily_counts, color="#e11d48")
            with c_a:
                with st.container(border=True):
                    st.markdown("##### 🩺 AI Analysis")
                    if "trend_analysis" not in st.session_state:
                        st.session_state.trend_analysis = generate_trend_analysis({str(k):v for k,v in daily_counts.items()})
                    st.markdown(st.session_state.trend_analysis)
                    if st.button("Update", type="secondary"):
                        del st.session_state["trend_analysis"]
                        st.rerun()
        else: st.info("Insufficient data for trends.")

    with tab_alerts:
        if not nearby_df.empty:
            st.dataframe(nearby_df[["disease", "timestamp", "weight", "distance_km"]].sort_values("distance_km"), use_container_width=True, hide_index=True)
        else: st.success("No active disease alerts nearby.")

    with tab_report:
        c1, c2 = st.columns([1, 1])
        with c1:
            with st.form("report_form"):
                disease = st.selectbox("Disease", DISEASE_OPTIONS)
                severity = st.slider("Severity", 1, 10, 5)
                if st.form_submit_button("Submit Report", type="primary"):
                    success, msg = data_db.add_report(user_lat, user_lng, disease, severity, st.session_state.username)
                    if success:
                        st.success("Report added.")
                        st.session_state.data_db = DataManager()
                        time.sleep(1); st.rerun()
                    else: st.error(msg)
        with c2: st.info(f"Reporting for: **{display_city_name}**")

    with tab_profile:
        c1, c2 = st.columns([1, 1])
        with c1:
            hist = data_db.get_user_profile(st.session_state.username)
            auth_info = st.session_state.auth_db.get_user_info(st.session_state.username)
            with st.form("prof_form"):
                col_p1, col_p2 = st.columns(2)
                with col_p1: age_input = st.number_input("Age", value=auth_info.get("age") or 25)
                with col_p2: gender_input = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
                txt = st.text_area("Medical History", value=hist if hist else "")
                if st.form_submit_button("Save Profile", type="primary"):
                    data_db.update_user_profile(st.session_state.username, txt)
                    st.session_state.auth_db.update_user_info(st.session_state.username, age=age_input, gender=gender_input)
                    st.success("Saved!")
                    time.sleep(1); st.rerun()
        with c2:
            my_reports = data_db.get_data(user_filter=st.session_state.username)
            if not my_reports.empty: st.dataframe(my_reports[["disease", "timestamp"]], use_container_width=True, hide_index=True)
            else: st.info("No reports submitted.")
