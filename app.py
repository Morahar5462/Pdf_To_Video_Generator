import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from PIL import Image, ImageDraw, ImageFont
from mutagen.mp3 import MP3
from mutagen import MutagenError
from gtts import gTTS
import io
import os
import re
import json
import tempfile
import subprocess
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(page_title="AI Video Lecture Generator", page_icon="🎬", layout="wide")

# --- Predefined Color Palettes for Visuals ---
COLOR_PALETTES = [
    # 1. Academic & Warm (Cream & Burgundy)
    # Evokes a feeling of warmth, tradition, and scholarly content.
    {'bg': '#FAF3E0', 'text': '#4E342E', 'title': '#800000'},

    # 2. Tech Dark Mode (Charcoal & Gold)
    # A modern, high-contrast dark theme that feels premium.
    {'bg': '#121212', 'text': '#E0E0E0', 'title': '#FFD700'},

    # 3. Clean & Minimalist (White & Teal)
    # Crisp, clean, and professional. The teal title adds a touch of modern elegance.
    {'bg': '#FFFFFF', 'text': '#212121', 'title': '#008060'},
    
    # 4. Cool Slate (Muted Blue & Slate)
    # A calm, cool, and collected palette that's very easy on the eyes.
    {'bg': '#EDF2F7', 'text': '#2D3748', 'title': '#2B6CB0'},

    # 5. Forest & Amber (Deep Green & Gold)
    # Elegant and natural, this palette feels sophisticated and grounded.
    {'bg': '#004D40', 'text': '#F1F1F1', 'title': '#F2C94C'},

    # 6. Earthy & Natural (Beige & Sage)
    # A soft, organic palette that feels approachable and calm.
    {'bg': '#F4F1DE', 'text': '#5D4037', 'title': '#81A684'},

    # 7. Deep Indigo & Cyan (Blueprint)
    # Inspired by classic blueprints, this palette is technical and authoritative.
    {'bg': '#002244', 'text': '#FFFFFF', 'title': '#66B2FF'},

    # 8. Slate & Orange (Modern & Energetic)
    # A popular combination in modern design, balancing professionalism with energy.
    {'bg': '#34495E', 'text': '#ECF0F1', 'title': '#F39C12'},
    
    # 9. Soft & Professional (Light Gray & Purple)
    # A gentle, light theme that uses a muted purple for a creative but professional touch.
    {'bg': '#F8F9FA', 'text': '#343A40', 'title': '#6F42C1'},

    # 10. Rich Plum (Deep Purple & Lavender)
    # A unique and sophisticated dark theme that conveys creativity and depth.
    {'bg': '#241B2F', 'text': '#D1C4E9', 'title': '#90CAF9'},
]

# Check for video creation capabilities
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False

FFMPEG_AVAILABLE = check_ffmpeg()

# --- Initialize Session State ---
if 'slides' not in st.session_state:
    st.session_state.slides = []
if 'slide_audio_files' not in st.session_state:
    st.session_state.slide_audio_files = []
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None

# --- Helper Functions ---

def cleanup_temp_files(files):
    for f in files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass

def extract_text_from_pdf(pdf_file_bytes):
    try:
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def generate_slide_content(text, model):
    prompt = f"""
    Convert this text into presentation slides with teaching scripts. Return JSON format:
    {{
        "slides": [
            {{
                "title": "Slide Title",
                "bullet_points": ["Point 1", "Point 2", "Point 3"],
                "teaching_script": "Brief explanation of this slide content in 50-80 words."
            }}
        ]
    }}
    
    Make each teaching_script concise (50-80 words) and educational.
    
    Text: {text[:4000]}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_response = re.sub(r'```json|```', '', response.text).strip()
        return json.loads(cleaned_response)
    except Exception as e:
        st.error(f"Error generating slides: {e}")
        return {"slides": []}

def generate_individual_slide_audio(slides, api_key):
    """Generate separate audio for each slide with proper timing"""
    slide_audio_data = []
    temp_files = []
    
    progress_bar = st.progress(0, text="Generating audio for each slide...")
    
    for i, slide in enumerate(slides):
        # Create script for this specific slide
        slide_script = f"Let's discuss {slide['title']}. {slide.get('teaching_script', ' '.join(slide['bullet_points']))}"
        
        # Try ElevenLabs first, fallback to gTTS
        if api_key:
            try:
                audio_path, duration = generate_elevenlabs_single_audio(slide_script, api_key, i)
            except Exception as e:
                st.warning(f"ElevenLabs failed for slide {i+1}, using gTTS")
                audio_path, duration = generate_gtts_single_audio(slide_script, i)
        else:
            audio_path, duration = generate_gtts_single_audio(slide_script, i)
        
        if audio_path:
            slide_audio_data.append({
                'path': audio_path,
                'duration': duration,
                'slide_index': i
            })
            temp_files.append(audio_path)
        
        progress_bar.progress((i + 1) / len(slides), text=f"Generated audio for slide {i+1}/{len(slides)}")
    
    progress_bar.empty()
    return slide_audio_data, temp_files

def generate_elevenlabs_single_audio(script, api_key, slide_index):
    """Generate audio for a single slide using ElevenLabs"""
    VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}
    }

    response = requests.post(url, json=data, headers=headers, timeout=120)
    response.raise_for_status()

    temp_dir = tempfile.gettempdir()
    audio_path = os.path.join(temp_dir, f"slide_{slide_index}_audio.mp3")
    
    with open(audio_path, "wb") as f:
        f.write(response.content)
    
    # Get duration
    try:
        duration = MP3(audio_path).info.length
    except:
        duration = 5.0  # Default fallback
    
    return audio_path, duration

def generate_gtts_single_audio(script, slide_index):
    """Generate audio for a single slide using gTTS"""
    try:
        tts = gTTS(text=script, lang='en', slow=False)
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"slide_{slide_index}_gtts.mp3")
        tts.save(audio_path)
        
        # Get duration
        try:
            duration = MP3(audio_path).info.length
        except:
            duration = len(script) * 0.1  # Rough estimate: 0.1 seconds per character
        
        return audio_path, duration
    except Exception as e:
        st.error(f"Failed to generate gTTS audio for slide {slide_index}: {e}")
        return None, 0

def create_slide_image(slide_content, palette, size=(1920, 1080)):
    img = Image.new('RGB', size, color=palette['bg'])
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        text_font = ImageFont.truetype("arial.ttf", 40)
    except OSError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw title
    title = slide_content['title']
    draw.text((100, 100), title, fill=palette['title'], font=title_font)
    
    # Draw bullet points
    y_offset = 250
    for point in slide_content['bullet_points']:
        draw.text((150, y_offset), f"• {point}", fill=palette['text'], font=text_font)
        y_offset += 80
    
    return img

def create_synced_video_with_ffmpeg(slides, slide_audio_data):
    """Create video with each slide synced to its specific audio duration using different color palettes"""
    if not FFMPEG_AVAILABLE:
        st.error("FFmpeg not available. Please install FFmpeg for video generation.")
        return None
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_files = []
        
        progress_bar = st.progress(0, text="Creating synced video with varied colors...")
        
        # Create individual video segments for each slide
        video_segments = []
        
        for i, (slide, audio_data) in enumerate(zip(slides, slide_audio_data)):
            # Use different color palette for each slide (cycle through available palettes)
            palette_index = i % len(COLOR_PALETTES)
            palette = COLOR_PALETTES[palette_index]
            
            # Create slide image with unique color palette
            img = create_slide_image(slide, palette)
            img_path = os.path.join(temp_dir, f"slide_{i}.png")
            img.save(img_path)
            temp_files.append(img_path)
            
            # Create video segment for this slide with its specific audio duration
            segment_path = os.path.join(temp_dir, f"segment_{i}.mp4")
            
            # FFmpeg command to create video segment with exact audio duration
            cmd = [
                'ffmpeg', '-loop', '1', '-i', img_path,
                '-i', audio_data['path'],
                '-c:v', 'libx264', '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',  # This ensures video matches audio duration exactly
                segment_path, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                video_segments.append(segment_path)
                temp_files.append(segment_path)
            else:
                st.error(f"Failed to create segment {i}: {result.stderr}")
                return None
            
            progress_bar.progress(0.7 * (i + 1) / len(slides), text=f"Created segment {i+1}/{len(slides)}")
        
        # Combine all video segments
        progress_bar.progress(0.8, text="Combining video segments...")
        
        # Create file list for concatenation
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for segment in video_segments:
                f.write(f"file '{segment}'\n")
        temp_files.append(concat_file)
        
        # Final video path
        output_path = os.path.join(temp_dir, "synced_lecture_video.mp4")
        
        # Concatenate all segments
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_path, '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            progress_bar.progress(1.0, text="Video created successfully!")
            progress_bar.empty()
            
            # Cleanup temporary files
            cleanup_temp_files(temp_files)
            
            return output_path
        else:
            st.error(f"Failed to combine segments: {result.stderr}")
            return None
            
    except Exception as e:
        st.error(f"Error creating synced video: {e}")
        return None

def run_processing_pipeline(gemini_key, elevenlabs_key, uploaded_file_bytes):
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Extract text from PDF
        st.info("Extracting text from PDF...")
        text = extract_text_from_pdf(uploaded_file_bytes)
        
        if not text.strip():
            st.error("No text found in PDF")
            return False
        
        # Generate slides
        st.info("Generating slide content...")
        slide_data = generate_slide_content(text, model)
        st.session_state.slides = slide_data.get('slides', [])
        
        if not st.session_state.slides:
            st.error("No slides generated")
            return False
        
        # Generate individual audio for each slide
        st.info("Generating audio for each slide...")
        slide_audio_data, temp_audio_files = generate_individual_slide_audio(st.session_state.slides, elevenlabs_key)
        
        if slide_audio_data:
            st.session_state.slide_audio_files = slide_audio_data
            
            if FFMPEG_AVAILABLE:
                # Generate synced video
                st.info("Creating synced video lecture...")
                video_path = create_synced_video_with_ffmpeg(
                    st.session_state.slides, 
                    slide_audio_data
                )
                
                if video_path:
                    st.session_state.video_path = video_path
                    st.success("✅ Synced video lecture generated successfully!")
                    return True
                else:
                    st.error("Failed to create synced video")
                    return False
            else:
                st.warning("⚠️ Video generation not available - FFmpeg not found")
                st.success(f"✅ Generated {len(st.session_state.slides)} slides with individual audio!")
                return True
        else:
            return False
            
    except Exception as e:
        st.error(f"Pipeline error: {e}")
        return False

# --- UI Layout & Main Logic ---
st.title("📄➡️🎬 PDF to Video Lecture Generator")


# Sidebar
with st.sidebar:
    st.header("🔑 API Configuration")
    gemini_key = st.text_input("Gemini API Key", type="password")
    elevenlabs_key = st.text_input("ElevenLabs API Key (optional)", type="password")
    
    st.header("🔧 Environment Status")
    if FFMPEG_AVAILABLE:
        st.success("✅ FFmpeg available - Synced video generation enabled")
    else:
        st.error("❌ FFmpeg not available - Audio only mode")
        st.info("📝 To enable video generation:")
        st.code("Download FFmpeg from https://ffmpeg.org/download.html", language="text")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and gemini_key:
        if st.button("🚀 Generate Synced Video Lecture", type="primary"):
            with st.spinner("Processing..."):
                success = run_processing_pipeline(
                    gemini_key, 
                    elevenlabs_key, 
                    uploaded_file.read()
                )
                
                if success:
                    st.balloons()

with col2:
    st.header("📊 Status")
    if st.session_state.slides:
        st.success(f"✅ {len(st.session_state.slides)} slides generated")
        
        # Video download button
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            st.subheader("🎬 Download Synced Video")
            with open(st.session_state.video_path, "rb") as video_file:
                st.download_button(
                    label="📥 Download Synced Video Lecture",
                    data=video_file.read(),
                    file_name="synced_lecture_video.mp4",
                    mime="video/mp4",
                    type="primary"
                )
        elif st.session_state.slide_audio_files:
            st.subheader("🎧 Individual Slide Audio")
            for i, audio_data in enumerate(st.session_state.slide_audio_files):
                if os.path.exists(audio_data['path']):
                    with open(audio_data['path'], "rb") as audio_file:
                        st.download_button(
                            label=f"📥 Slide {i+1} Audio ({audio_data['duration']:.1f}s)",
                            data=audio_file.read(),
                            file_name=f"slide_{i+1}_audio.mp3",
                            mime="audio/mpeg",
                            key=f"audio_{i}"
                        )
        
        # Display slides preview with timing and color info
        st.subheader("Lecture Content Preview")
        for i, slide in enumerate(st.session_state.slides):
            duration_info = ""
            if i < len(st.session_state.slide_audio_files):
                duration_info = f" ({st.session_state.slide_audio_files[i]['duration']:.1f}s)"
            
            # Show color palette for this slide
            palette_index = i % len(COLOR_PALETTES)
            palette = COLOR_PALETTES[palette_index]
            
            with st.expander(f"Slide {i+1}: {slide['title']}{duration_info}"):
                # Color palette preview
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<div style='background-color: {palette['bg']}; padding: 10px; border-radius: 5px; text-align: center; color: white;'>Background</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div style='background-color: {palette['title']}; padding: 10px; border-radius: 5px; text-align: center; color: white;'>Title</div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div style='background-color: {palette['text']}; padding: 10px; border-radius: 5px; text-align: center; color: white;'>Text</div>", unsafe_allow_html=True)
                
                st.write("**Key Points:**")
                for point in slide['bullet_points']:
                    st.write(f"• {point}")
                if 'teaching_script' in slide:
                    st.write("**Teaching Script:**")
                    st.write(slide['teaching_script'])
    
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
