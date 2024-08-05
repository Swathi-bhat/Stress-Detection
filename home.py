import streamlit as st
import pandas as pd
import models
import pytz
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def home():
    page = st.sidebar.radio("Go to", ["Home","About Us", "Stress Assessment", "History",  "Logout"])
    
    if 'username' in st.session_state:
        name=st.session_state['username']
        credentials_df=pd.read_csv('credentials.csv')
        user_row=credentials_df[credentials_df['UserName']==name]
        database_name=user_row['Database'].iloc[0]
        database=pd.read_csv('Database/{}'.format(database_name))

    if page == "Home":
        if 'username' in st.session_state:
            st.title(f"Welcome, {st.session_state['username']}!")

            st.write("Select the language and speak into the microphone.")
            language = st.radio("Select language:", ("English", "Kannada"))
            if st.button("Recognize and Analyze"):
                recognized_text, translated_text = models.recognize_and_translate(language)
                if recognized_text and translated_text:
                    st.write(f"**Recognized {language} text:** {recognized_text}")
                    st.write(f"**Translated text:** {translated_text}")
                
                    sentiment_score = models.sentiment_analysis(translated_text)
                    st.write(sentiment_score)
                    if sentiment_score in [1,2,3]:  # Scores 1,2,3 indicate negative sentiment
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





    elif page == "Stress Assessment":
        st.title("Stress Assessment")
        st.subheader("Before Taking the Test")
        st.write("""
        - Find a quiet place where you won't be disturbed.
        - Ensure your microphone is working correctly.
        - Sit comfortably and relax.
        - Make sure there is minimal background noise.
        """)

        st.subheader("Instructions")
        st.write("""
        - **Begin by taking a deep breath.** This helps you relax and speak clearly.
        - **Click the 'Start' button to begin recording your voice.** Speak naturally and clearly.
        - **Speak for a few seconds.** Talk about anything you like or describe how you feel.
        - **Wait for the system to analyze your voice.** The analysis will determine if you might be experiencing depression.
        - **Review your results.** The system will display your state of depression and detected emotions.
        """)

        st.subheader("After the Test")
        st.write("""
        - You can view the analysis of your emotional state.
        - Your test records will be saved and can be accessed in the 'History' section for future reference.
        - Regular assessments can help you monitor your stress levels over time.
        """)


    elif page == "History":
        st.title("History")
        database=pd.read_csv('Database/{}'.format(database_name))
        st.table(database)

        # Convert timestamp column to datetime
        database['timestamp'] = pd.to_datetime(database['timestamp'])

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

    elif page == "About Us":
        st.title("About us  ")
        st.write("""
        ## Why Stress Analysis?
        Stress is a prevalent issue affecting individuals worldwide, contributing to a variety of physical and mental health challenges. Prolonged exposure to stress can lead to serious conditions such as anxiety, depression, cardiovascular diseases, and weakened immune response. Therefore, understanding and managing stress is essential for maintaining overall health and well-being.
        Our mission is to provide a user-friendly tool that leverages advanced natural language processing (NLP) techniques to assess stress levels from speech. By harnessing the power of machine learning and artificial intelligence, we aim to help individuals identify their stress levels and take proactive steps towards better mental health.

        ## What We Are Doing
        Our innovative stress analysis tool integrates several state-of-the-art technologies to offer a comprehensive evaluation of stress. Here’s how it works:

        #### Speech Recognition and Translation
        Our tool starts by capturing spoken words using a microphone. We utilize Google's Speech Recognition API to accurately convert spoken language into text. For users who speak Kannada, we provide seamless translation to English using a robust translation API. This ensures that the analysis is precise and accessible to a broader audience.

        #### Sentiment Analysis
        Once the speech is converted to text, we employ a BERT-based model fine-tuned for sentiment analysis. BERT (Bidirectional Encoder Representations from Transformers) is a cutting-edge NLP model that excels in understanding the context and nuances of text. Our sentiment analysis model evaluates the emotional tone of the spoken words, classifying them into categories such as positive, neutral, or negative. This helps in determining the overall sentiment and identifying potential signs of stress or depression.

        #### Emotion Detection
        In addition to sentiment analysis, we use a specialized emotion detection model to pinpoint specific emotions expressed in the speech. The model identifies and quantifies emotions such as happiness, anger, and sadness. By standardizing these detected emotions, we provide a clear and comprehensible picture of the emotional state. This multi-faceted approach ensures that we capture a wide range of emotional cues, offering a more accurate and holistic assessment of stress levels.

        #### Comprehensive Analysis
        By combining speech recognition, translation, sentiment analysis, and emotion detection, our tool offers a comprehensive analysis of the user’s emotional state. This multi-layered approach allows us to provide detailed insights into whether a person might be experiencing stress, depression, or other emotional challenges. Our goal is to empower users with the information they need to understand their mental health better and seek appropriate support if necessary.

        #### User-Friendly Interface
        Our platform is designed to be intuitive and user-friendly, making it accessible to individuals with varying levels of technical expertise. Whether you are a healthcare professional seeking to monitor patients' stress levels or an individual looking to understand your emotional well-being, our tool is here to assist you.

        #### Future Developments
        We are continuously working to enhance our stress analysis tool by integrating new features and improving existing functionalities. Our future plans include adding support for more languages, expanding the range of detectable emotions, and incorporating additional stress indicators such as voice tone and speech patterns. We are committed to staying at the forefront of NLP and AI research to provide the best possible stress assessment solutions.
        We believe that by leveraging technology, we can make a significant impact on mental health awareness and support. Thank you for choosing our stress analysis tool. We are here to help you on your journey towards better mental health and well-being.
        """)
    
    elif page == "Logout":
        st.session_state.page = 'login'
        st.rerun()
    

        


if __name__ == "__main__":
    home()
