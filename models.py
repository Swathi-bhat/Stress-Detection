import os
import streamlit as st
from google.cloud import speech
from translate import Translator
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import io

# Load BERT tokenizer and model for sentiment analysis
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# Load emotion recognition tokenizer and model
emotion_tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-emotion')
emotion_model = AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-emotion')

# Set Google Cloud credentials path (ensure this environment variable is set on your server)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/google-cloud-credentials.json"

def recognize_and_translate(language):
    # Initialize Google Cloud Speech client
    client = speech.SpeechClient()

    # Record audio (replace with your own audio capture mechanism)
    st.info("Please speak something...")

    # In a real implementation, you'd record audio and save it to a file, e.g., "audio.wav".
    # Here, you need to upload an audio file or use a microphone input, for this example
    # we assume you have an audio file called "audio.wav"
    audio_file_path = "path/to/your/audio.wav"

    with open(audio_file_path, "rb") as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # Make sure your audio file has the correct sample rate
        language_code="en-US" if language != "Kannada" else "kn-IN",
    )

    response = client.recognize(config=config, audio=audio)

    # Process the recognized text
    try:
        if response.results:
            recognized_text = response.results[0].alternatives[0].transcript
            st.write(f"Recognized Text: {recognized_text}")

            # Translate if needed
            if language == 'Kannada':
                translator = Translator(from_lang='kn', to_lang='en')
                translated_text = translator.translate(recognized_text)
                st.write(f"Translated Text: {translated_text}")
            else:
                translated_text = recognized_text

            return recognized_text, translated_text
        else:
            st.error("No speech detected.")
            return None, None
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None, None

def sentiment_analysis(text):
    try:
        tokens = tokenizer.encode(text, return_tensors='pt', truncation=True, max_length=512)
        result = model(tokens)
        sentiment_score = int(torch.argmax(result.logits)) + 1  # BERT returns a score from 0, hence adding 1
        return sentiment_score
    except Exception as e:
        st.error(f"Sentiment analysis error: {e}")
        return None

def emotion_analysis(text):
    try:
        tokens = emotion_tokenizer.encode(text, return_tensors='pt', truncation=True, max_length=512)
        result = emotion_model(tokens)
        emotion_scores = torch.softmax(result.logits, dim=1).detach().numpy()[0]
        emotions = ['anger', 'joy', 'optimism', 'sadness']
        detected_emotions = {emotions[i]: emotion_scores[i] for i in range(len(emotions))}

        # Extract relevant emotions (joy as happiness)
        relevant_emotions = {
            'happy': detected_emotions['joy'],
            'angry': detected_emotions['anger'],
            'sad': detected_emotions['sadness']
        }

        # Convert emotion scores to percentage
        for item in relevant_emotions:
            relevant_emotions[item] = relevant_emotions[item] * 100
            
        return relevant_emotions
    except Exception as e:
        st.error(f"Emotion analysis error: {e}")
        return None
