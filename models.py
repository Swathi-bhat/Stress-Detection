import streamlit as st
import speech_recognition as sr
from translate import Translator
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from pydub import AudioSegment
import io

# Load BERT tokenizer and model for sentiment analysis
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# Load emotion recognition tokenizer and model
emotion_tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-emotion')
emotion_model = AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-emotion')

def convert_mp3_to_wav(mp3_file):
    """
    Convert MP3 file to WAV format.
    """
    audio = AudioSegment.from_mp3(mp3_file)
    wav_file = io.BytesIO()
    audio.export(wav_file, format="wav")
    wav_file.seek(0)
    return wav_file

def recognize_and_translate(uploaded_file, language='en'):
    """
    Recognize speech from an uploaded audio file and translate if necessary.
    """
    recognizer = sr.Recognizer()
    translator = Translator(from_lang='kn', to_lang='en') if language == 'Kannada' else None
    
    # Check if the uploaded file is in the correct format
    if isinstance(uploaded_file, io.BytesIO):  # Ensure the uploaded file is in the expected format
        # If the uploaded file is MP3, convert it to WAV first
        if uploaded_file.name.endswith('.mp3'):
            uploaded_file = convert_mp3_to_wav(uploaded_file)
        
        with sr.AudioFile(uploaded_file) as source:
            st.info("Processing audio...")
            audio = recognizer.record(source)  # Read the entire audio file

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
    else:
        st.error("Uploaded file is not in the correct format.")
        return None, None

def sentiment_analysis(text):
    """
    Perform sentiment analysis using the pre-trained BERT model.
    """
    try:
        tokens = tokenizer.encode(text, return_tensors='pt', truncation=True, max_length=512)
        result = model(tokens)
        sentiment_score = int(torch.argmax(result.logits)) + 1
        return sentiment_score
    except Exception as e:
        st.error(f"Sentiment analysis error: {e}")
        return None

def emotion_analysis(text):
    """
    Perform emotion analysis using the pre-trained emotion recognition model.
    """
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

        for item in relevant_emotions:
            relevant_emotions[item] = relevant_emotions[item] * 100
            
        return relevant_emotions
    except Exception as e:
        st.error(f"Emotion analysis error: {e}")
        return None

def main():
    """
    Main function to handle Streamlit UI and processing.
    """
    # File uploader to allow users to upload an audio file
    uploaded_file = st.file_uploader("Upload an Audio File", type=["wav", "mp3"])

    if uploaded_file is not None:
        st.write(f"File uploaded: {uploaded_file.name}")

        # Display the audio file
        st.audio(uploaded_file)

        # Recognize and translate the speech in the uploaded audio
        recognized_text, translated_text = recognize_and_translate(uploaded_file)

        if recognized_text:
            st.write("Recognized Text:", recognized_text)
            st.write("Translated Text:", translated_text)

            # Sentiment analysis on the recognized text
            sentiment_score = sentiment_analysis(recognized_text)
            if sentiment_score:
                st.write(f"Sentiment Score: {sentiment_score}")

            # Emotion analysis on the recognized text
            emotions = emotion_analysis(recognized_text)
            if emotions:
                st.write(f"Detected Emotions: {emotions}")

if __name__ == "__main__":
    main()
