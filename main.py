import streamlit as st
import signup
import login
import home

st.set_page_config(page_title="Multi-page App", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'login'

def main():
    if st.session_state.page == 'signup':
        signup.signup()
    elif st.session_state.page == 'login':
        login.login()
    elif st.session_state.page == 'home':
        home.home()

if __name__ == "__main__":
    main()
