from dotenv import load_dotenv
import os
import speech_recognition as sr
from gtts import gTTS
from ollama import Client
import io
import pygame
from llama_index.llms.ollama import Ollama
import time
# Load environment variables
load_dotenv()

llm = Ollama(model="llama3.2:3b", request_timeout=120.0, prompt_key="You must always respond in Hindi. Your character is female so use feamle oriented hindi.")

recognizer = sr.Recognizer()

def listen():
    """Listen to microphone input and return text"""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
    try:
        print("Processing...")
        return recognizer.recognize_google(audio, language="hi-IN")
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "API unavailable"

def speak(text):
    """Convert text to speech and play immediately"""
    tts = gTTS(text=text, lang='hi')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    
    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(audio_buffer)
    pygame.mixer.music.play()
    
    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)



if __name__ == "__main__":
    try:
        while True:
            # Step 1: Listen for voice input
            query = listen()
            print(f"You said: {query}")
            
            if query.lower() =="विराम":
                speak("ठीक है, अब मैं जा रही हूँ।")
                break
            if query.lower()=="could not understand audio":
                continue 
            # Step 2: Process with LLM
            

            accumulated_text = ""  # Initialize a variable to accumulate text
            delimiter = "।"  # The Devanagari full stop, typically used in Hindi sentences
            timeout = 5  # Set a timeout to wait for the stream to generate text (in seconds)
            start_time = time.time()  # Record the start time

            for r in llm.stream_complete(query):
                accumulated_text += r.delta  # Accumulate the streamed text
                
                # Check if the accumulated text contains the delimiter
                if delimiter in accumulated_text:
                    # Speak the accumulated text up to the delimiter and reset
                    speak(accumulated_text)
                    accumulated_text = ""  # Reset the accumulated text
                    start_time = time.time()  # Reset the timeout timer

            # After the loop, check if there's any remaining text and speak it
            if accumulated_text:
                speak(accumulated_text)
            # # Step 3: Speak the response
            # speak(response.text)
            
    except KeyboardInterrupt:
        speak("Program terminated")
    except Exception as e:
        print(f"Error: {str(e)}")
        speak("An error occurred")