import streamlit as st
from db import get_connection
from auth import check_password, hash_password
from file_import import import_csv_with_mapping
from reed_analysis import show_analysis,show_analysis_date_range
from datetime import datetime
from user_manage import log_event, login, create_user, manage_users, view_logs



def admin_panel():

    admin_option = st.sidebar.radio("Admin", ["Create User", "Manage Users", "Logs", "Import CSV"], key="admin_page")

    if admin_option == "Create User":
        create_user()
    elif admin_option == "Manage Users":
        manage_users()
    elif admin_option == "Logs":
        view_logs()
    elif admin_option == "Import CSV":
        import_csv_with_mapping()

def reed_analysis_dashboard():

    reed_dash = st.sidebar.radio("Reed Analysis", ["Data By Date", "Data By Date Range"], key="reed_dash_page")

    if reed_dash == "Data By Date":
        show_analysis()
    elif reed_dash == "Data By Date Range":
        show_analysis_date_range()



# App Entry Point
if 'logged_in' not in st.session_state:
    login()
elif st.session_state['logged_in']:
    st.sidebar.write(f"👤 Logged in as: {st.session_state['username']} ({st.session_state['role']})")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    menu_option = st.sidebar.radio("Navigation", ["Dashboard", "Analysis"], key="main_nav")

    if menu_option == "Analysis":
        reed_analysis_dashboard()

    elif menu_option == "Dashboard":
        if st.session_state['role'] == 'admin':
            admin_panel()
        else:
            st.header("User Dashboard")
            st.info("Welcome! No admin privileges.")
