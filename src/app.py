from flask import Flask, request, Response, stream_with_context
from dotenv import load_dotenv
import os
from asr.speech_recognition_handler import FreeSpeechRecognition
from tts.tts_handler import FreeTTS
from llama_index.llms.ollama import Ollama
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app) 
# Initialize components with environment variables
asr_processor = FreeSpeechRecognition(language=os.getenv('ASR_LANGUAGE'))
tts_processor = FreeTTS(language=os.getenv('TTS_LANGUAGE'))
llm=llm = Ollama(model=os.getenv("LLM_MODEL_NAME"), request_timeout=120.0)

@app.route('/process_stream', methods=['POST'])
def process_stream():
    # Get input text from request
    data = request.get_json()
    text = data.get("text")
    if not text:
        return Response("No text provided", status=400)

    try:
        # Get complete LLM response
        llm_response = llm.complete(text)
        print(llm_response.text)
        # Convert LLM response to audio
        audio_stream = tts_processor.text_to_audio(llm_response.text)
        
        # Create response with audio data
        return Response(
            audio_stream.read(),
            mimetype='audio/wav',  # Use appropriate MIME type for your TTS output
            headers={
                'Content-Disposition': 'attachment; filename=response.wav',
                'Cache-Control': 'no-cache'
            }
        )
    
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return Response("Internal server error", status=500)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True, threaded=True)