from dotenv import load_dotenv
import os
import speech_recognition as sr
from gtts import gTTS
import io
import pygame
from llama_index.llms.ollama import Ollama
import time
# Load environment variables
load_dotenv()

llm = Ollama(
    model="llama3.2:3b",  # Replace with the correct model name supported by Ollama
    request_timeout=120.0,
)
system_prompt=(
        "You must always respond in Hindi. Your character is female, so use female-oriented Hindi. \n"
        "Do not use *, #, or any other special characters to create points or markdown. \n"
        "Respond in clear and natural Hindi sentences.\n"
        "The response should be conscise and very informative.\n"
        "Below is the user query and keep in mind the above reasons when giving response-\n"
    )
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
            query = listen()
            print(f"You said: {query}")
            
            if query.lower() == "विराम":
                speak("ठीक है, अब मैं जा रही हूँ।")
                break
            if "could not understand audio" in query.lower():
                continue

            # Hindi-specific settings
            delimiter = "।"  # Hindi full stop
            max_pause = 2    # Max pause between chunks in seconds
            accumulated_text = ""
            last_received_time = time.time()

            # Stream processing with proper sentence splitting
            for chunk in llm.stream_complete(system_prompt+query):
                print(chunk.delta,end="")
                delta = chunk.delta
                accumulated_text += delta
                current_time = time.time()

                # Check for delimiter in new text
                while delimiter in accumulated_text:
                    split_index = accumulated_text.index(delimiter) + 1
                    sentence, accumulated_text = accumulated_text.split(delimiter, 1)
                    # print(sentence)
                    sentence = sentence.strip() + delimiter  # Add delimiter back
                    speak(sentence)
                    last_received_time = current_time


            # Speak any remaining text after streaming completes
            if accumulated_text.strip():
                speak(accumulated_text.strip())

    except KeyboardInterrupt:
        speak("Program terminated")
    except Exception as e:
        print(f"Error: {str(e)}")
        speak("An error occurred")