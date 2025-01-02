import streamlit as st
import pandas as pd
import models
import pytz
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_chat import message
import time

def chatbot_response(user_input):
    user_input = user_input.lower()

    if "hello" in user_input or "hi" in user_input:
        return "Hi there! 😊 How can I assist you today?"
    elif "stressed" in user_input or "depressed" in user_input or "not feeling good" in user_input:
        return "I'm really sorry to hear that. 🌼 Managing stress can be challenging. You can find some helpful tips and strategies in the Explore page."
    elif "overcome my stress" in user_input or "relieve stress" in user_input:
        return "That's a great question! 🎶 Listening to music can be a wonderful way to alleviate stress. You can find song recommendations based on your current stress level."
    elif "help" in user_input:
        return "Of course! 🤗 Feel free to ask me about stress management techniques, music recommendations, or how to navigate this app."
    elif "bye" in user_input:
        return "Goodbye! 👋 Take care, and don’t hesitate to return if you need anything else!"
    
    elif "thank you" in user_input:
        return "You’re welcome! If you have any more questions or need further assistance in the future, feel free to reach out. 😊"
    else:
        return "I'm sorry, I didn't quite catch that. Could you please rephrase your question?"

def chatbot_page():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    st.title("Chatbot")
    user_input = st.text_input("You: ", "")

    if user_input:
        response = chatbot_response(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "bot", "content": response})

    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=(msg["role"] == "user"), key=str(i))


def recommend_music(stress_level):
    if stress_level <= 3:
        return[
            ("Happy Day", "music/4.mp3","images/G.jpg"),
            ("Island Breeze", "music/5.mp3","images/H.jpg"),
            ("Playing in colours", "music/6.mp3","images/I.jpg"),
        ]
    
    elif stress_level <= 6:
        return[
            ("Sunrise Serenade", "music/7.mp3","images/D.jpg"),
            ("Rock Music", "music/9.mp3","images/E.jpg"),
            ("Sunshine Whistle", "music/8.mp3","images/F.jpg"),
        ]
    else:
        return[
            ("Breeze Groove", "music/1.mp3","images/A.jpg"),
            ("Good Times", "music/3.mp3","images/B.jpg"),
            ("Endless party", "music/2.mp3","images/C.jpg"),
        ]

def home():
    
    tab1, tab2, tab5, tab4, tab6= st.tabs(["Home", "AI Assistant","Stress Diary","History","Explore"])
    # page = st.sidebar.radio("Go to", ["Home","AI Assistant","Emotion Detection","Stress Diary", "Explore", "History", "Logout"])
    
    if 'username' in st.session_state:
        name=st.session_state['username']
        credentials_df=pd.read_csv('credentials.csv')
        user_row=credentials_df[credentials_df['UserName']==name]
        database_name=user_row['Database'].iloc[0]
        database=pd.read_csv('Database/{}'.format(database_name))

    with tab1:
        if 'username' in st.session_state:
            st.title(f"Welcome, {st.session_state['username']}!")
            st.subheader("How to take the test")
            st.write("""
            - **Begin by taking a deep breath.** This helps you relax and speak clearly.
            - **Click the 'Recognize and Analyse' button to begin recording your voice.** Speak naturally and clearly.
            - **Speak for a few seconds.** Talk about anything you like or describe how you feel.
            - **Wait for the system to analyze your voice.** The analysis will determine if you might be experiencing depression.
            - **Review your results.** The system will display your state of depression and detected emotions.
            """)

            st.subheader("Select the language and speak into the microphone.")
            language = st.radio("Choose:", ("English", "Kannada"))
            if st.button("Recognize and Analyze"):
                recognized_text, translated_text = models.recognize_and_translate(language)
                if recognized_text and translated_text:
                    st.write(f"**Recognized {language} text:** {recognized_text}")
                    st.write(f"**Translated text:** {translated_text}")
                
                    sentiment_score = models.sentiment_analysis(translated_text)
                    st.write(sentiment_score)
                    if sentiment_score in [1,2,3]:  
                        st.warning("Signs of Depression found")
                        depression='Depression'
                        
                    else:
                        st.success("No signs of depression")
                        depression='No Depression'
                    detected_emotions = models.emotion_analysis(translated_text)
                    st.write("**Detected Emotions :**")
                    for emotion, score in detected_emotions.items():
                        st.write(f"{emotion.capitalize()}: {score:.2f}%")
                    


                    new_row = pd.DataFrame({
                        'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                        'depression': [depression],
                        'happy': [detected_emotions['happy']],
                        'angry': [detected_emotions['angry']],
                        'sad': [detected_emotions['sad']]
                    })
                    
                    database = pd.concat([new_row, database], ignore_index=True)
                    database.to_csv('Database/{}'.format(database_name), index=False) 
    with tab2:
        chatbot_page()  
               
    with tab4:
        # Streamlit app
        st.title("Depression Analysis Over Time")

        # Count occurrences of each depression status
        status_counts = database['depression'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']

        # Plot the bar chart
        fig = px.bar(status_counts, x='Status', y='Count', title='Depression Status Count')

        st.plotly_chart(fig)

        # Create a combined line chart for happy, angry, and sad
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=database['timestamp'], y=database['happy'], mode='lines', name='Happy'))
        fig.add_trace(go.Scatter(x=database['timestamp'], y=database['angry'], mode='lines', name='Angry'))
        fig.add_trace(go.Scatter(x=database['timestamp'], y=database['sad'], mode='lines', name='Sad'))

        fig.update_layout(
            title='Emotional Analysis Over Time',
            xaxis_title='Time',
            yaxis_title='Emotion Score',
            legend_title='Emotions'
        )

        st.plotly_chart(fig)
        
         
        database=pd.read_csv('Database/{}'.format(database_name))
        st.table(database)

        # Convert timestamp column to datetime
        database['timestamp'] = pd.to_datetime(database['timestamp'])
        
    with tab5:
        st.title("Stress Diary")
        st.write("Log your daily stress levels and notes below.")

        diary_file_path = 'Database/{}_stress_diary.csv'.format(database_name)  # Define the path here
        diary_entry = st.text_area("Notes", "")
        stress_level = st.slider("Stress Level (0-10)", 0, 10)

        if st.button("Save Entry"):
            new_entry = pd.DataFrame({
                'timestamp': [datetime.now().strftime('%d-%m-%Y %H:%M:%S')],
                'stress_level': [stress_level],
                'notes': [diary_entry]
            })

            # Check if diary file exists, if not, create it
            try:
                diary_database = pd.read_csv(diary_file_path)
            except FileNotFoundError:
                diary_database = pd.DataFrame(columns=['timestamp', 'stress_level', 'notes'])

            diary_database = pd.concat([new_entry, diary_database], ignore_index=True)
            diary_database.to_csv(diary_file_path, index=False)
            st.success("Diary entry saved!")

        # Display previous entries
        st.subheader("Previous Entries")
        try:
            diary_database = pd.read_csv(diary_file_path)
            st.table(diary_database)
        except FileNotFoundError:
            st.write("No entries found yet.")
            
    with tab6:

        # Mind Exercises Section
        st.title("Mind Exercises")
        st.write("Try these simple exercises to calm your mind")

        # Example exercises
        exercises = [
            {
                "title": "Easy Pose",
                "description": "Sit cross-legged with your back straight and shoulders relaxed. Rest your hands on your knees or in your lap, palms facing up. Close your eyes and focus on your breath, allowing your mind to calm and your body to relax. This pose promotes a sense of peace and stability.",
                "video": "https://www.youtube.com/watch?v=1iDTARK8Zrg" 
                
            },
            {
                "title": "Surya Namaskara",
                "description": "Surya Namaskara (Sun Salutation) is a series of 12 yoga poses performed in a flowing sequence, typically starting from a standing position and moving through forward bends, lunges, and backbends.",
                "video": "https://www.youtube.com/watch?v=ktqaQ1oTfYI   "  
            },
            {
                "title": "Upward Facing Dog",
                "description": "Begin by lying face down, then place your palms on the ground beneath your shoulders. Press into your hands, lifting your chest and thighs off the floor while arching your back. Keep your shoulders relaxed and gaze forward, allowing your heart to open. This pose strengthens the spine, stretches the chest, and improves posture. Hold for several breaths, feeling the invigorating energy flow through your body.",
                "video": "https://www.youtube.com/watch?v=pVmOOluGAv8"  # Add a path to your video
            },
            {
                "title": "Corpse Pose",
                "description": "Lie flat on your back with your legs extended and arms relaxed alongside your body, palms facing up. Close your eyes and take deep breaths, allowing your body to fully relax and release tension. Focus on your breath and let go of any thoughts. Hold for several minutes, embracing the stillness and calm.",
                "video": "https://www.youtube.com/watch?v=1VYlOKUdylM"  
            },
        ]

        for exercise in exercises:
            st.subheader(exercise["title"])
            st.video(exercise["video"])
            st.write(exercise["description"])
            st.write("---")  # Separator
  
        # Meditation Resources Section
        st.subheader("Guided Meditation")
        st.write("Here are some guided meditation resources to help you relax:")
        
        meditation_links = [
            {"title": "The Body Scan Meditation", "link": "music/Body.mp3"},
            {"title": "Mindful Meditation", "link": "music/Breathing.mp3"},
            {"title": "Connection Meditation", "link": "music/Connection.mp3"},
        ]

        for meditation in meditation_links:
            st.write(f"- {meditation['title']}")
            st.audio(meditation["link"])

        diary_file_path = 'Database/{}_stress_diary.csv'.format(database_name)
        
        try:
            diary_database = pd.read_csv(diary_file_path)           
            diary_database['timestamp'] = pd.to_datetime(diary_database['timestamp'], format="%d-%m-%Y %H:%M:%S")

            # diary_database['timestamp'] = pd.to_datetime(diary_database['timestamp'])
            diary_database = diary_database.sort_values(by='timestamp')
            latest_entry = diary_database.iloc[-1]
            stress_level = latest_entry['stress_level']
            st.write(f"Your latest recorded stress level is: {stress_level}/10")
            st.write("---")  # Separator

            # Recommend music based on the latest stress level
            st.subheader("Music Recommendations Based on Stress Levels")
            recommended_songs = recommend_music(stress_level)
            
            num_columns = 3 
           
            cols = st.columns(num_columns)  # Create columns

            for i, (song, link, img_url) in enumerate(recommended_songs):
                col_index = i % num_columns  # Determine the current column index
                with cols[col_index]:
                    st.image(img_url,use_column_width=True)  # Display album art
                    st.write(f"**{song}**")  # Display song title
                    st.audio(link)  # Audio player

# Adjust the layout to handle the last row if it has fewer than num_columns songs
            if len(recommended_songs) % num_columns != 0:
                st.write("")

        except FileNotFoundError:
            st.write("No stress diary entries found. Please log your stress levels in the 'Stress Diary' section.")
        st.write("---")  # Separator
    # with tab7:
    #     st.session_state.page = 'login'
    #     st.rerun()
    

        


if __name__ == "__main__":
    home()
