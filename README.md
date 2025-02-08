# BhashaSetu - Hindi Language Conversational AI Pipeline

![Project Structure](https://img.shields.io/badge/Project%20Structure-Modular-brightgreen)
![Language](https://img.shields.io/badge/Language-Hindi%20Only-important)

BhashaSetu is an end-to-end conversational AI pipeline that operates exclusively in Hindi, combining Automatic Speech Recognition (ASR), Natural Language Processing (NLP) using LLMs, and Text-to-Speech (TTS) conversion.

## 🌟 Features

- **Hindi-Only Conversational Pipeline**  
- **Modular Architecture** (ASR, NLP, TTS handlers)
- Dual Interface:  
  - Terminal-based testing (`testing.py`)  
  - Web interface with browser-based ASR  
- Ollama-powered Llama3-3B model for NLP  
- gTTS for Hindi speech synthesis  

## 📦 Installation

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/BhashaSetu.git
cd BhashaSetu
```

2. **Create Virtual Environment**  
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Ollama**  
Install [Ollama](https://ollama.ai/) and pull the model:
```bash
ollama pull llama3:3b
```

## 🚀 Usage

### Terminal Interface
```bash
python testing.py
```
- Speaks into microphone for input
- Processes through ASR → NLP → TTS
- Outputs audio response

### Web Interface
1. Start Flask Server:
```bash
python src/app.py
```

2. Open in Browser:
```
http://localhost:5000
```
- Chrome/Edge recommended
- Click microphone icon to speak
- Receive audio response

## 💂️ Project Structure

```
BhashaSetu/
├── src/
│   ├── app.py               # Flask API endpoints
│   ├── asr/                 # Speech recognition
│   ├── llm/                 # Language model handling
│   ├── tts/                 # Text-to-speech
│   └── utils/               # Audio processing
├── index.html               # Frontend UI
├── script.js                # Browser interactions
├── style.css                # UI styling
├── testing.py               # CLI interface
└── requirements.txt         # Dependencies
```

## 🔧 Components

### ASR (Speech Recognition)
- Browser Web Speech API (frontend)
- Python speech recognition library (CLI)

### NLP (Llama3-3B)
- Local inference via Ollama
- Hindi language processing
- Conversation context management

### TTS (Text-to-Speech)
- gTTS Hindi synthesis
- Audio streaming for web interface
- MP3 file generation for CLI

## 🌐 API Endpoint

`POST /process_stream`
- Accepts JSON: `{"text": "हिंदी टेक्सट"}`
- Returns: 
  ```json
  {
    "audio_url": "/generated/audio.mp3",
    "response_text": "हिंदी प्रतिक्रिया"
  }
  ```

## 💡 Notes

- **Browser Compatibility**  
  Requires Chrome/Edge for Web Speech API
- **Ollama Requirements**  
  Ensure Ollama service is running:
  ```bash
  ollama serve
  ```
- **Environment Variables**  
  Create `.env` for custom configurations:
  ```
  OLLAMA_ENDPOINT=http://localhost:11434
  TEMP_AUDIO_PATH=./generated
  ```

## 🤝 Contributing

1. Fork repository
2. Create feature branch:
```bash
git checkout -b feature/your-feature
```
3. Commit changes:
```bash
git commit -m 'Add awesome feature'
```
4. Push to branch:
```bash
git push origin feature/your-feature
```
5. Open Pull Request

## 📄 License

Distributed under MIT License. See `LICENSE` for details.

---

Made with ❤️ in India | Powered by Ollama & gTTS | [Contribute](#contributing)
