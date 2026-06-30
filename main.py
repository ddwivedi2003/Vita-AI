import streamlit as st

from vita_ai.auth import AuthManager
from vita_ai.data import DataManager
from vita_ai.ui import show_login_page, show_dashboard


if __name__ == "__main__":
    st.set_page_config(page_title="Vita AI Health", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

    if "auth_db" not in st.session_state: st.session_state.auth_db = AuthManager()
    if "data_db" not in st.session_state: st.session_state.data_db = DataManager()
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "messages" not in st.session_state: st.session_state.messages = []

    if st.session_state.logged_in:
        show_dashboard(st.session_state.data_db)
    else:
        show_login_page(st.session_state.auth_db)