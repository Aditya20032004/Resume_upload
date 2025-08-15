# AgentsAI - Voice Assistant

A sophisticated AI-powered voice assistant built with Flask, featuring complete voice-to-voice conversation capabilities using modern AI services.

## 🎯 Overview

AgentsAI is a production-ready voice assistant that combines Speech-to-Text, Large Language Models, and Text-to-Speech to create natural voice conversations. Built with clean architecture and comprehensive error handling for reliable performance.

## ✨ Key Features

- **🎙️ Voice-to-Voice Conversations** - Complete audio pipeline from speech input to voice response
- **🧠 AI-Powered Responses** - Google Gemini AI for intelligent, context-aware conversations
- **💾 Session Memory** - Persistent conversation history with context awareness
- **🛡️ Bulletproof Error Handling** - Three-layer fallback system ensures zero-failure experience
- **🎨 Modern UI** - Glassmorphism design with accessibility features
- **📱 Responsive Design** - Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

```
AgentsAI/
├── 📁 config/                    # Configuration management
│   ├── __init__.py              
│   └── settings.py              # Environment validation & logging
├── 📁 models/                   # Pydantic data models
│   ├── __init__.py
│   └── schemas.py               # Request/response validation
├── 📁 services/                 # AI service integrations
│   ├── __init__.py
│   ├── stt.py                  # Speech-to-Text (AssemblyAI)
│   ├── llm.py                  # Large Language Model (Gemini)
│   └── tts.py                  # Text-to-Speech (Murf)
├── 📁 utils/                    # Utility functions
│   ├── __init__.py
│   ├── chat_history.py         # Session management
│   └── error_handling.py       # Error utilities
├── 📁 static/                   # Frontend assets
│   ├── css/style.css           # Modern glassmorphism design
│   └── js/
│       ├── voice-button.js     # Voice interaction
│       └── error-handling.js   # Client-side error recovery
├── 📁 templates/                # HTML templates
│   └── index.html              # Main interface
├── app.py                       # Flask application
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Aditya20032004/murfaivoiceagent.git
cd murfaivoiceagent
```

### 2. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys:
# ASSEMBLYAI_API_KEY=your_assemblyai_key
# GEMINI_API_KEY=your_gemini_key
# MURF_API_KEY=your_murf_key
# MURF_API_URL=your_murf_url
```

### 4. Run Application
```bash
python app.py
```

Visit `http://localhost:5000` to start using the voice assistant!

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main voice assistant interface |
| `/api/health` | GET | Service health check |
| `/llm/query` | POST | Complete voice processing pipeline |
| `/api/tts` | POST | Text-to-speech conversion |
| `/api/transcribe` | POST | Speech-to-text conversion |

## 🛠️ Tech Stack

- **Backend**: Flask + Pydantic + Professional Logging
- **AI Services**: 
  - Google Gemini AI (LLM)
  - AssemblyAI (Speech-to-Text)
  - Murf API (Text-to-Speech)
- **Frontend**: HTML5 + CSS3 + JavaScript + MediaRecorder API
- **Architecture**: Service-oriented design with comprehensive error handling

## 🎯 Core Capabilities

### Voice Processing Pipeline
1. **Audio Capture** → MediaRecorder API captures user speech
2. **Speech-to-Text** → AssemblyAI transcribes audio to text
3. **AI Processing** → Google Gemini generates intelligent response
4. **Text-to-Speech** → Murf API synthesizes natural voice response
5. **Audio Playback** → Browser plays AI response

### Error Handling System
- **Layer 1**: Service-level error recovery
- **Layer 2**: Application-level fallbacks
- **Layer 3**: Emergency client-side responses

## 📊 Features

### ✅ Production Ready
- Modular architecture with clean separation of concerns
- Type-safe API contracts with Pydantic validation
- Comprehensive logging and monitoring
- Health check endpoints for service monitoring

### ✅ User Experience
- Single-button voice interface
- Real-time processing feedback
- Responsive design for all devices
- Accessibility features (keyboard shortcuts, ARIA labels)

### ✅ AI Integration
- Context-aware conversations with memory
- Natural language understanding and generation
- High-accuracy speech recognition
- Natural-sounding voice synthesis

## 🔐 Security & Privacy

- Environment variables for secure API key management
- Input validation and sanitization
- Error logging without exposing sensitive data
- File upload restrictions and validation

## 📈 Performance

- Optimized processing pipeline with parallel service calls
- Session-based conversation caching
- Automatic cleanup of temporary files
- Performance monitoring with detailed timing metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced language processing
- **AssemblyAI** for accurate speech-to-text transcription
- **Murf AI** for high-quality text-to-speech synthesis
- **Flask** for the robust web framework

## 📞 Support

For questions or issues:
- 📧 Create an issue in this repository
- 📖 Check the [Development Journey](DEVELOPMENT_JOURNEY.md) for detailed implementation
- 🔧 Review API documentation in the code

---

**Built with ❤️ for the AI Voice Agents Challenge**