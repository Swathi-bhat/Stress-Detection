import streamlit as st
import pandas as pd




def login():
    # Initialize session state if it doesn't exist
    if 'phone' not in st.session_state:
        st.session_state['phone'] = ""
    if 'password' not in st.session_state:
        st.session_state['password'] = ""
    if 'login_message' not in st.session_state:
        st.session_state['login_message'] = ""

    col1, col2, col3 = st.columns(3)
    with col2:
        login_placeholder = st.empty()
        st.subheader("Login")
        login_phone = st.text_input("Phone Number", value=st.session_state['phone'], key="phone_input")
        login_password = st.text_input("Password", type="password", value=st.session_state['password'], key="password_input")

        if st.session_state['login_message']:
            login_placeholder.error(st.session_state['login_message'])

        subcol1, subcol2 = st.columns(2)
        with subcol1:
            login_clicked = st.button("Login")
            if login_clicked:
                if login_phone and login_password:
                    try:
                        df = pd.read_csv("credentials.csv")
                        df['Phone'] = df['Phone'].astype(str)  # Ensure Phone column is treated as string
                        user_exists = df[df.Phone == login_phone]

                        if not user_exists.empty:
                            if not df[(df.Phone == login_phone) & (df.Password == login_password)].empty:
                                st.session_state.page = 'home'
                                st.session_state['username'] = df[(df.Phone == login_phone) & (df.Password == login_password)].iloc[0]['UserName']
                                st.session_state['login_message'] = ""
                                st.session_state['phone'] = ""
                                st.session_state['password'] = ""
                                st.rerun()
                            else:
                                st.session_state['login_message'] = "Wrong password."
                                st.session_state['password'] = ""
                                st.rerun()
                        else:
                            st.session_state['login_message'] = "User not found."
                            st.session_state['phone'] = ""
                            st.session_state['password'] = ""
                            st.rerun()
                    except FileNotFoundError:
                        st.error("No users found. Please sign up first.")
                else:
                    st.session_state['login_message'] = "Please enter both phone number and password."
                    st.session_state['phone'] = login_phone
                    st.session_state['password'] = login_password
                    st.rerun()

        with subcol2:
            signup_clicked = st.button("Signup")
            if signup_clicked:
                st.session_state.page = 'signup'
                st.rerun()

if __name__ == "__main__":
    login()
