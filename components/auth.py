import streamlit as st
from auth_manager import sign_in, sign_up
from scheduler import TaskScheduler

def render_auth():
    if st.session_state.logged_in:
        return
        
    st.markdown("""
    <div style='text-align:center; padding-top: 40px;'>
        <h1>📋 Task Scheduler</h1>
        <p style='color:#6c7086'>Powered by Min-Heap DSA</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        st.write("")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        st.write("")
        if st.button("Login", use_container_width=True, type="primary"):
            if login_user and login_pass:
                result = sign_in(login_user, login_pass)
                if result["success"]:
                    st.session_state.logged_in  = True
                    st.session_state.username   = result["user"]["username"]
                    st.session_state.user_id    = str(result["user"]["id"])
                    st.session_state.scheduler  = TaskScheduler(
                        user_id=st.session_state.user_id
                    )
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error(result["error"])
            else:
                st.warning("Please fill in all fields")

    with tab_signup:
        st.write("")
        new_user  = st.text_input("Username", key="signup_user")
        new_email = st.text_input("Email", key="signup_email")
        new_pass  = st.text_input("Password", type="password", key="signup_pass")
        new_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2")
        st.write("")
        if st.button("Create Account", use_container_width=True, type="primary"):
            if new_user and new_email and new_pass and new_pass2:
                if new_pass != new_pass2:
                    st.error("Passwords don't match!")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = sign_up(new_user, new_email, new_pass)
                    if result["success"]:
                        st.success("Account created! Please login.")
                    else:
                        st.error(result["error"])
            else:
                st.warning("Please fill in all fields")

    st.stop()
