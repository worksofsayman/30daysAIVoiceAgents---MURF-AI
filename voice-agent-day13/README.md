# 🎙️ AI Voice Agent — Gemini + Flask/FastAPI

An AI-powered conversational voice assistant built as part of the **30 Days of AI Voice Agents Challenge**.  
This project enables natural, real-time conversations with **Google's Gemini AI**, powered by Python backend services and a lightweight, responsive frontend.

## 🚀 Features
- **🎤 Speech-to-Text (STT)** — Real-time voice conversion to text
- **🤖 Gemini-Powered AI** — Google's Gemini API for query processing
- **🗣️ Text-to-Speech (TTS)** — Natural voice responses
- **🌐 Web UI** — Minimal, responsive interface
- **⚡ Low Latency** — Optimized audio streaming

## 🛠️ Tech Stack
**Frontend:** HTML/CSS/JavaScript (or React)  
**Backend:** Python (Flask/FastAPI)  
**AI Model:** Google Gemini API  
**Speech Recognition:** SpeechRecognition/Web Speech API  
**Text-to-Speech:** gTTS/Google Cloud TTS/pyttsx3  

## 📐 Architecture
```mermaid
graph LR
    User -->|Voice Input| Browser
    Browser -->|Audio| STT
    STT -->|Text| Backend
    Backend -->|LLM Request| Gemini
    Gemini -->|Response| Backend
    Backend -->|Text| TTS
    TTS -->|Audio| Browser