import speech_recognition as sr
from utils.audio_handler import raw_audio_to_wav_bytes

class FreeSpeechRecognition:
    def __init__(self, language='hi-IN'):
        self.recognizer = sr.Recognizer()
        self.language = language

    def audio_to_text(self, audio_data):
        try:
            wav_bytes = raw_audio_to_wav_bytes(audio_data)
            with sr.AudioFile(wav_bytes) as source:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio, language=self.language)
        except Exception as e:
            print(f"Speech Recognition Error: {str(e)}")
            return None