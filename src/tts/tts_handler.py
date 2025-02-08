from gtts import gTTS
import io
import numpy as np
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
    def add_silence(self, audio_data, silence_ms=100):
        """Add silence padding to audio"""
        sample_rate = 22050  # adjust based on your TTS sample rate
        silence_samples = int(silence_ms * sample_rate / 1000)
        silence = np.zeros(silence_samples, dtype=np.float32)
        return np.concatenate([audio_data, silence])

    def normalize_audio(self, audio_data):
        """Normalize audio volume"""
        max_volume = np.abs(audio_data).max()
        if max_volume > 0:
            normalized = audio_data / max_volume
            return normalized * 0.9  # Slight reduction to prevent clipping
        return audio_data