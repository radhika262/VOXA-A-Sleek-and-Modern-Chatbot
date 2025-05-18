# ============================
# FRONTEND: Streamlit App (voxa_app.py)
# ============================

import time
import os
import streamlit as st
import pygame
from gtts import gTTS
import requests

# -------------------------------
# Streamlit UI Setup
# -------------------------------
# Configure the page title and layout for the Streamlit app
st.set_page_config(page_title="Voxa Chatbot", layout="centered")

# Main heading and description for the app
st.title("💬 Voxa - Your AI Customer Support Assistant")
st.write("Ask your question using text. Voxa is ready to help you!")

# -------------------------------
# Session State Initialization
# -------------------------------
# Use Streamlit's session_state to remember user input across reruns of the app
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Create a text input box for the user to type their query
# Pre-fill it with any previous input stored in session_state
st.session_state.user_input = st.text_input("⌨ Type your question here:", st.session_state.user_input)

# -------------------------------
# Handling User Query Submission
# -------------------------------
# When the user clicks the "Get Answer" button and has typed something,
# send the input to the backend API to get a response
if st.button("💬 Get Answer") and st.session_state.user_input:
    with st.spinner("🤖 Voxa is thinking..."):  # Show a spinner while waiting for response
        try:
            # Make a POST request to the local backend Flask API with user input as JSON
            response = requests.post(
                "http://localhost:5000/chat",
                json={"message": st.session_state.user_input},
                timeout=60  # Increased timeout to 60 seconds to allow for slower responses
            )

            # Extract the generated response text from the JSON response
            result = response.json()["response"]

            # Display the chatbot's answer and token count (word count) to the user
            st.success(f"🤖 Voxa says: '{result}'")
            st.info(f"🧠 Token count: {len(result.split())}")

            # -------------------------------
            # Text-to-Speech Playback
            # -------------------------------
            try:
                # Convert the chatbot's text response to speech using gTTS
                tts = gTTS(text=result)
                tts_path = "voxa_response.mp3"
                tts.save(tts_path)

                # Initialize pygame mixer for audio playback
                pygame.mixer.init()
                pygame.mixer.music.load(tts_path)
                pygame.mixer.music.play()

                # Wait while audio is playing to prevent early termination
                while pygame.mixer.music.get_busy():
                    time.sleep(0.5)

                # Stop and unload mixer after playback to free resources
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.quit()

                # Try removing the audio file to clean up, retrying if file is locked
                for _ in range(3):
                    try:
                        os.remove(tts_path)
                        break
                    except PermissionError:
                        time.sleep(0.5)

            except Exception as audio_error:
                # Show error message if text-to-speech or audio playback fails
                st.error(f"🔊 Audio playback error: {audio_error}")

        except requests.exceptions.RequestException as net_err:
            # Handle errors related to network issues or backend unavailability
            st.error(f"Network error: {net_err}")

# -------------------------------
# Footer / Credits
# -------------------------------
st.markdown("---")
st.markdown("Made with ❤ by the Voxa Team - Powered by FLAN-T5, Streamlit, Flask, and gTTS")
