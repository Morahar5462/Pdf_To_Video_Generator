
# 📄➡️🎬 AI Video Lecture Generator

> Transform Static PDFs into Dynamic, Narrated Video Presentations.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)

## 🚀 Overview

The AI Video Lecture Generator is an innovative application that leverages cutting-edge AI technologies to automatically convert PDF documents into comprehensive video lectures. The system intelligently extracts content, generates educational slides with teaching scripts, creates synchronized narration, and produces professional-quality videos with dynamic visual themes.

### Key Features

- **🤖 AI-Powered Content Generation**: Utilizes Google's Gemini 2.5 Flash model for intelligent slide creation and educational script generation
- **🎙️ Premium Voice Synthesis**: Dual audio engine supporting ElevenLabs premium voices with automatic fallback to Google Text-to-Speech
- **⏱️ Perfect Audio-Video Synchronization**: Each slide displays for exactly the duration of its corresponding narration
- **📱 Interactive Web Interface**: Clean, responsive Streamlit-based UI with real-time progress tracking
- **🔄 Robust Error Handling**: Graceful fallbacks and comprehensive error management

## 🛠️ Tech Stack

### Core Technologies
- **Frontend**: Streamlit (Interactive web application)
- **Backend**: Python 3.8+
- **AI/ML Models**: 
  - Google Gemini 2.5 Flash (Content generation)
  - ElevenLabs API (Premium voice synthesis)
  - Google Text-to-Speech (Fallback audio generation)

### Key Libraries & Dependencies
```
streamlit>=1.28.0          # Web application framework
google-generativeai>=0.3.0 # Gemini AI integration
PyMuPDF>=1.23.0            # PDF text extraction
requests>=2.31.0           # HTTP client for API calls
Pillow>=10.0.0             # Image processing and slide generation
mutagen>=1.47.0            # Audio metadata handling
gtts>=2.4.0                # Google Text-to-Speech fallback
```

### System Dependencies
- **FFmpeg**: Video processing and synchronization engine
- **Python Virtual Environment**: Isolated dependency management

## 🏗️ Architecture & Approach

### 1. Content Extraction & Processing
```
PDF Document → PyMuPDF → Raw Text → Content Chunking (4000 chars)
```

### 2. AI-Driven Slide Generation
```
Raw Text → Gemini 2.5 Flash → Structured JSON → Slide Objects
```
- Intelligent content segmentation
- Educational script generation (50-80 words per slide)
- Bullet point extraction and organization

### 3. Audio Synthesis Pipeline
```
Teaching Scripts → ElevenLabs API → High-Quality MP3
                ↓ (Fallback)
                gTTS → Standard Quality MP3
```
- Individual audio generation per slide
- Precise duration measurement for synchronization
- Automatic quality fallback system

### 4. Visual Design System
```
Slide Content → PIL Image Processing → 10 Color Palettes → PNG Frames
```
- Dynamic color palette rotation
- Professional typography (Arial with fallbacks)
- 1920x1080 HD resolution
- Optimized contrast ratios

### 5. Video Synthesis & Synchronization
```
PNG Frames + MP3 Audio → FFmpeg Processing → Synchronized MP4
```
- Frame-perfect audio-video alignment
- Individual segment creation and concatenation
- Professional encoding (H.264/AAC)

## 🎯 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed and accessible in PATH
- Google Gemini API key
- ElevenLabs API key (optional, for premium voices)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/pdf2video.git
cd pdf2video

# Create virtual environment
python -m venv myvenv
myvenv\Scripts\activate  # Windows
# source myvenv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Alternative Launch Methods
```bash
# Using batch file (Windows)
run_app.bat

# Direct execution
python -m streamlit run app.py
```

## 📊 Usage Workflow

1. **Launch Application**: Start the Streamlit interface
2. **Configure APIs**: Enter Gemini API key (ElevenLabs optional)
3. **Upload PDF**: Select your document (max 200MB)
4. **Generate Content**: Click "Generate Synced Video Lecture"
5. **Monitor Progress**: Real-time progress bars for each stage
6. **Download Results**: Get your synchronized MP4 video

## ⚡ Performance Metrics

- **Processing Speed**: ~30-60 seconds per slide (depending on content length)
- **Audio Quality**: 
  - ElevenLabs: Studio-quality (22kHz, 128kbps)
  - gTTS: Standard quality (22kHz, 64kbps)
- **Video Output**: 1080p HD, H.264 encoding, 24fps
- **File Size**: ~5-15MB per minute of content

## 🔒 Limitations & Considerations

### Current Limitations

1. **Content Scope**: 
   - Optimized for text-heavy PDFs
   - Limited support for image-heavy documents
   - 4000 character limit per processing chunk

2. **Language Support**:
   - Primary: English (optimized)
   - Limited: Other languages (basic support via gTTS)

3. **API Dependencies**:
   - Requires active internet connection
   - Subject to API rate limits and quotas
   - ElevenLabs quota limitations may trigger fallback

4. **System Requirements**:
   - FFmpeg dependency for video generation
   - Minimum 4GB RAM recommended
   - Temporary storage requirements (~100MB per video)

### Technical Constraints

- **Slide Complexity**: Basic text-based slides only
- **Animation**: Static slides (no transitions or animations)
- **Customization**: Limited font and layout options
- **Batch Processing**: Single document processing only

## 🚀 Future Improvements & Roadmap

### Short-term Enhancements (v2.0)
- [ ] **Multi-language Support**: Extended language detection and synthesis
- [ ] **Custom Voice Training**: User-uploaded voice samples
- [ ] **Advanced Slide Layouts**: Multiple template options
- [ ] **Batch Processing**: Multiple PDF processing queue
- [ ] **Export Formats**: PowerPoint, PDF slides, audio-only options

### Medium-term Features (v3.0)
- [ ] **Image Integration**: Automatic image extraction and placement
- [ ] **Interactive Elements**: Clickable slides and navigation
- [ ] **Cloud Storage**: Direct integration with Google Drive, Dropbox
- [ ] **Collaboration Tools**: Shared workspaces and review systems
- [ ] **Analytics Dashboard**: Usage metrics and performance insights

### Long-term Vision (v4.0+)
- [ ] **AI Presenter Avatars**: Virtual presenter integration
- [ ] **Real-time Editing**: Live slide modification during generation
- [ ] **Advanced AI Models**: GPT-4, Claude integration options
- [ ] **Mobile Application**: iOS/Android companion apps
- [ ] **Enterprise Features**: SSO, team management, API access



## 🙏 Acknowledgments

- **Google AI**: Gemini 2.5 Flash model capabilities
- **ElevenLabs**: Premium voice synthesis technology
- **Streamlit Team**: Excellent web application framework
- **FFmpeg Project**: Robust video processing engine
- **Open Source Community**: Various supporting libraries
