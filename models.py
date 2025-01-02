import streamlit as st
import speech_recognition as sr
import sounddevice as sd
import numpy as np
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

def recognize_and_translate(language):
    # Initialize recognizer and translator
    recognizer = sr.Recognizer()
    translator = Translator(from_lang='kn', to_lang='en') if language == 'Kannada' else None
    
    # Use sounddevice to record audio
    st.info("Please speak something...")
    samplerate = 16000  # Set the sample rate
    duration = 5  # Max duration in seconds to record
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait until the recording is finished

    # Convert the audio to AudioData
    audio = sr.AudioData(recording.tobytes(), samplerate, 2)

    try:
        # Recognize speech using Google Web Speech API
        if language == 'Kannada':
            recognized_text = recognizer.recognize_google(audio, language='kn-IN')
            translated_text = translator.translate(recognized_text)
        else:
            recognized_text = recognizer.recognize_google(audio, language='en-US')
            translated_text = recognized_text

        return recognized_text, translated_text

    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand the audio")
        return None, None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
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
