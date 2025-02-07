const API_BASE_URL = 'http://localhost:5000';

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const audioPlayer = document.getElementById('audioPlayer');
const transcriptionText = document.getElementById('transcriptionText');
const responseStatus = document.getElementById('responseStatus');
const audioVisualizer = document.getElementById('audioVisualizer');

let mediaRecorder;
let audioChunks = [];
let recognition;
let fullTranscription = [];
let speakerID = "speaker";
let interimText = "";
let audioContext;
let isProcessing = false;

// Create audio context immediately
audioContext = new (window.AudioContext || window.webkitAudioContext)();

if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
  alert('Your browser does not support speech recognition. Please try Chrome or Edge.');
} else {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'hi-IN'; // Set language to Hindi (India)

  recognition.onresult = async (event) => {
    interimText = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      if (result.isFinal) {
        const text = result[0].transcript.trim();
        const timestamp = getTimestamp();
        fullTranscription.push({ speaker_id: speakerID, timestamp, text });

        // Send the final transcription to the API
        await processTranscription(text);
        
        transcriptionText.innerText = fullTranscription.map(item => item.text).join(' ');
      } else {
        interimText += result[0].transcript;
      }
    }

    transcriptionText.innerText =
      fullTranscription.map(item => item.text).join(' ') + " " + interimText.trim();
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
  };
}

// File: app.js

async function processTranscription(text) {
  if (isProcessing) return;
  
  try {
    isProcessing = true;
    responseStatus.textContent = 'Processing...';
    audioVisualizer.classList.add('active');

    const response = await fetch(`${API_BASE_URL}/process_stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Instead of streaming, wait for the complete response.
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();
    
  } catch (error) {
    console.error('Error processing transcription:', error);
    responseStatus.textContent = 'Error processing audio';
  } finally {
    isProcessing = false;
    audioVisualizer.classList.remove('active');
    responseStatus.textContent = 'Ready for next input';
  }
}


// Multipart stream parser helper class
class MultipartStreamParser {
  constructor() {
    this.buffer = new Uint8Array(0);
    this.boundary = '--frame';
  }

  append(chunk) {
    const newBuffer = new Uint8Array(this.buffer.length + chunk.length);
    newBuffer.set(this.buffer);
    newBuffer.set(chunk, this.buffer.length);
    this.buffer = newBuffer;
  }

  hasChunk() {
    return this.buffer.length > 0;
  }

  getChunk() {
    const boundaryIndex = this.findBoundary();
    if (boundaryIndex === -1) return null;

    const headerEnd = this.findHeaderEnd(boundaryIndex);
    if (headerEnd === -1) return null;

    const nextBoundary = this.findBoundary(headerEnd);
    if (nextBoundary === -1) return null;

    const chunk = this.buffer.slice(headerEnd, nextBoundary);
    this.buffer = this.buffer.slice(nextBoundary);
    return chunk;
  }

  findBoundary(startIndex = 0) {
    const boundaryBytes = new TextEncoder().encode(this.boundary);
    for (let i = startIndex; i < this.buffer.length - boundaryBytes.length; i++) {
      let found = true;
      for (let j = 0; j < boundaryBytes.length; j++) {
        if (this.buffer[i + j] !== boundaryBytes[j]) {
          found = false;
          break;
        }
      }
      if (found) return i;
    }
    return -1;
  }

  findHeaderEnd(startIndex) {
    const separator = new TextEncoder().encode('\r\n\r\n');
    for (let i = startIndex; i < this.buffer.length - separator.length; i++) {
      let found = true;
      for (let j = 0; j < separator.length; j++) {
        if (this.buffer[i + j] !== separator[j]) {
          found = false;
          break;
        }
      }
      if (found) return i + separator.length;
    }
    return -1;
  }
}

startBtn.addEventListener('click', () => {
  responseStatus.textContent = 'Waiting for speech...';
  audioVisualizer.classList.remove('active');
  
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];
      fullTranscription = [];
      startTime = Date.now();

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioPlayer.src = URL.createObjectURL(audioBlob);
      };

      mediaRecorder.start();
      startBtn.disabled = true;
      stopBtn.disabled = false;

      if (recognition) recognition.start();
    })
    .catch((error) => {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions.');
    });
});

stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }

  if (recognition) recognition.stop();

  startBtn.disabled = false;
  stopBtn.disabled = true;
  responseStatus.textContent = 'Recording stopped';
});

function getTimestamp() {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
  const seconds = (elapsed % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}