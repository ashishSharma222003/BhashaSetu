from flask import Flask, request, Response, stream_with_context
from dotenv import load_dotenv
import os
from src.asr.speech_recognition_handler import FreeSpeechRecognition
from src.tts.tts_handler import FreeTTS
from llama_index.llms.ollama import Ollama

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components with environment variables
asr_processor = FreeSpeechRecognition(language=os.getenv('ASR_LANGUAGE'))
tts_processor = FreeTTS(language=os.getenv('TTS_LANGUAGE'))
llm=llm = Ollama(model=os.getenv("LLM_MODEL_NAME"), request_timeout=120.0)

@app.route('/process_stream', methods=['POST'])
def process_stream():
    def generate():
        # Step 1: Speech Recognition
        audio_data = request.get_data()
        recognized_text = asr_processor.audio_to_text(audio_data)
        
        if not recognized_text:
            yield b''
            return

        # Step 2: Process with LLM using streaming
        accumulated_text = ""
        delimiter = "।"  # Hindi sentence delimiter
        
        for response in llm.stream_complete(recognized_text):
            if response.delta:
                accumulated_text += response.delta
                
                # Check if we have a complete sentence
                if delimiter in accumulated_text:
                    # Convert the complete sentence to audio and stream it
                    audio_stream = tts_processor.text_to_audio(accumulated_text)
                    if audio_stream:
                        while True:
                            chunk = audio_stream.read(int(os.getenv("AUDIO_CHUNK_SIZE", "1024")))
                            if not chunk:
                                break
                            yield b'--frame\r\n'
                            yield b'Content-Type: audio/wav\r\n\r\n'
                            yield chunk
                            yield b'\r\n'
                    
                    # Reset accumulated text
                    accumulated_text = ""
        
        # Process any remaining text
        if accumulated_text:
            audio_stream = tts_processor.text_to_audio(accumulated_text)
            if audio_stream:
                while True:
                    chunk = audio_stream.read(int(os.getenv("AUDIO_CHUNK_SIZE", "1024")))
                    if not chunk:
                        break
                    yield b'--frame\r\n'
                    yield b'Content-Type: audio/wav\r\n\r\n'
                    yield chunk
                    yield b'\r\n'

    return Response(
        stream_with_context(generate()),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)