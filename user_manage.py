import streamlit as st
from db import get_connection
from auth import check_password, hash_password
from datetime import datetime


def login():
    # st.title("Login")
    # username = st.text_input("Username")
    # password = st.text_input("Password", type="password")

    # if st.button("Login"):
    #     conn = get_connection()
    #     cursor = conn.cursor(dictionary=True)
    #     cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    #     user = cursor.fetchone()
    #     cursor.close()
    #     conn.close()

    #     if user and check_password(password, user['password_hash']):
    #         st.session_state['logged_in'] = True
    #         st.session_state['username'] = user['username']
    #         st.session_state['role'] = user['role']
    #         st.success(f"Welcome, {user['username']} ({user['role']})")
    #         st.rerun()
    #     else:
    #         st.error("Invalid username or password")

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 1])
    login_clicked = col1.button("Login")
    register_clicked = col2.button("Register")

    if login_clicked:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password(password, user['password_hash']):
            st.session_state['logged_in'] = True
            st.session_state['username'] = user['username']
            st.session_state['role'] = user['role']
            log_event("login", user['username'], "User logged in")
            st.success(f"Welcome, {user['username']} ({user['role']})")
            st.rerun()
        else:
            st.error("Invalid username or password")

    if register_clicked:
        st.session_state["show_register"] = False


def create_user():
    st.subheader("Create New User")
    with st.form("create_user"):
        new_username = st.text_input("New Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["user", "admin"])
        submitted = st.form_submit_button("Create User")

        if submitted:
            if not new_username or not new_email or not new_password:
                st.warning("All fields are required.")
                return

            hashed = hash_password(new_password)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (new_username, new_email))
            if cursor.fetchone():
                st.error("Username or email already exists.")
            else:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (new_username, new_email, hashed, new_role)
                )
                conn.commit()
                st.success("User created successfully.")
            cursor.close()
            conn.close()

def manage_users():
    st.subheader("Manage Users")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()

    for user in users:
        st.markdown(f"**{user['username']} ({user['role']})**")
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            new_email = st.text_input("Email", value=user['email'], key=f"email_{user['id']}")
        with col2:
            new_role = st.selectbox("Role", ["user", "admin"], index=["user", "admin"].index(user['role']), key=f"role_{user['id']}")
        with col3:
            if st.button("Update", key=f"update_{user['id']}"):
                cursor.execute(
                    "UPDATE users SET email = %s, role = %s WHERE id = %s",
                    (new_email, new_role, user['id'])
                )
                conn.commit()
                st.success("User updated.")

        with col4:
            if st.button("Delete", key=f"delete_{user['id']}"):
                cursor.execute("DELETE FROM users WHERE id = %s", (user['id'],))
                conn.commit()
                st.warning("User deleted.")

        # Change password row
        with st.expander(f"Change Password for {user['username']}"):
            new_pass = st.text_input("New Password", type="password", key=f"pass_{user['id']}")
            if st.button("Save Password", key=f"save_pass_{user['id']}") and new_pass:
                hashed = hash_password(new_pass)
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user['id']))
                conn.commit()
                st.success("Password changed.")

    cursor.close()
    conn.close()
