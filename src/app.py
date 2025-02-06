from flask import Flask, request, Response, stream_with_context
from dotenv import load_dotenv
import os
from src.asr.speech_recognition_handler import FreeSpeechRecognition
from src.tts.tts_handler import FreeTTS


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components with environment variables
asr_processor = FreeSpeechRecognition(language=os.getenv('ASR_LANGUAGE'))
tts_processor = FreeTTS(language=os.getenv('TTS_LANGUAGE'))
llm_processor = CustomLLM()

@app.route('/process_stream', methods=['POST'])
def process_stream():
    def generate():
        # Step 1: Speech Recognition
        audio_data = request.get_data()
        recognized_text = asr_processor.audio_to_text(audio_data)
        
        if not recognized_text:
            yield b''
            return

        # Step 2: Custom LLM Processing
        for llm_response in llm_processor.generate_response(recognized_text):
            if llm_response:
                # Step 3: Text-to-Speech Conversion
                audio_stream = tts_processor.text_to_audio(llm_response)
                if audio_stream:
                    while True:
                        chunk = audio_stream.read(os.getenv("AUDIO_CHUNK_SIZE"))
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