from gtts import gTTS
import io

class FreeTTS:
    def __init__(self, language='hi'):
        self.language = language

    def text_to_audio(self, text):
        try:
            tts = gTTS(text=text, lang=self.language)
            audio_io = io.BytesIO()
            tts.write_to_fp(audio_io)
            audio_io.seek(0)
            return audio_io
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return None