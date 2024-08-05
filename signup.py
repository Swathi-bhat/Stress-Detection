import streamlit as st
import pandas as pd
import os

def signup():
    col1, col2, col3 = st.columns(3)
    placeholder=st.empty()
    with col2:
        st.subheader("Sign Up")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        emergency_contact = st.text_input("Emergency Contact")
        
        subcol1, subcol2 = st.columns(2)

        with subcol1:
            if st.button("Signup"):
                if username and password and phone and gender and emergency_contact:
                    df_existing = pd.read_csv('credentials.csv')
                    if phone in df_existing['Phone'].astype(str).values:
                        st.error("Phone number already exists.")
                    else:
                        data = {
                            "UserName": [username],
                            "Password": [password],
                            "Phone": [str(phone)],  # Ensure phone number is treated as a string
                            "Gender": [gender],
                            "Emergency Contact": [emergency_contact],
                            "Database":[str(phone) + ".csv"]
                        }
                        df_new = pd.DataFrame(data)
                        
                        # Append to CSV or create new one if it doesn't exist
                        df_new.to_csv('credentials.csv', mode='a', header=not os.path.isfile('credentials.csv'), index=False)
                            
                        database_df = pd.DataFrame(columns=['timestamp', 'depression', 'happy', 'angry', 'sad'])
                        database_df.to_csv('Database\{}.csv'.format(phone), index=False)
                        
                        st.success("Signup successful! Please log in.")
                        st.session_state.page = 'login'
                        st.rerun()
                else:
                    st.error("Please fill all the fields.")
        
        with subcol2:
            if st.button("Go to Login"):
                st.session_state.page = 'login'
                st.rerun()

if __name__ == "__main__":
    signup()
