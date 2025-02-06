import wave
import io
import numpy as np
import soundfile as sf

def raw_audio_to_wav_bytes(raw_data, channels=1, sample_width=2, sample_rate=16000):
    """
    Convert raw audio bytes to WAV format in-memory
    Args:
        raw_data: Raw audio bytes
        channels: Number of audio channels
        sample_width: Bytes per sample (2 = 16-bit PCM)
        sample_rate: Sampling rate in Hz
    Returns:
        BytesIO object containing WAV data
    """
    try:
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(raw_data)
        wav_io.seek(0)
        return wav_io
    except Exception as e:
        print(f"Audio conversion error: {str(e)}")
        return None

def validate_audio_parameters(audio_data, expected_sample_rate=16000, expected_channels=1):
    """
    Validate audio format and parameters
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        with wave.open(io.BytesIO(audio_data)) as wav_file:
            if wav_file.getframerate() != expected_sample_rate:
                return False, f"Invalid sample rate: {wav_file.getframerate()} != {expected_sample_rate}"
            if wav_file.getnchannels() != expected_channels:
                return False, f"Invalid channels: {wav_file.getnchannels()} != {expected_channels}"
            return True, ""
    except Exception as e:
        return False, f"Invalid audio format: {str(e)}"

def convert_sample_rate(audio_data, original_rate, target_rate=16000):
    """
    Resample audio data using numpy
    Args:
        audio_data: Raw audio bytes
        original_rate: Original sample rate
        target_rate: Target sample rate
    Returns:
        Resampled audio bytes
    """
    try:
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate resampling ratio
        ratio = target_rate / original_rate
        
        # Resample using linear interpolation
        resampled = np.interp(
            np.arange(0, len(audio_array), ratio),
            np.arange(0, len(audio_array)),
            audio_array
        ).astype(np.int16)
        
        return resampled.tobytes()
    except Exception as e:
        print(f"Resampling error: {str(e)}")
        return audio_data

def bytes_to_float_array(audio_bytes):
    """
    Convert audio bytes to float32 numpy array
    """
    return np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

def float_array_to_bytes(float_array):
    """
    Convert float32 numpy array to PCM16 bytes
    """
    int16_array = (float_array * 32767).astype(np.int16)
    return int16_array.tobytes()