import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import os
from datetime import datetime
from gtts import gTTS
import base64
import speech_recognition as sr
from io import BytesIO
import tempfile
import re

# Page configuration
st.set_page_config(
    page_title="JalMitra AI - Drought Resilience Assistant",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .chat-message {
        color: black !important;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196F3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left-color: #4CAF50;
    }
    .stButton>button {
        width: 100%;
        background-color: #2196F3;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #fff3cd;
        color: black !important;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .voice-button {
        background-color: #4CAF50 !important;
        margin-top: 0.5rem;
    }
    .stop-button {
        background-color: #f44336 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'language' not in st.session_state:
    st.session_state.language = 'english'
if 'farm_context' not in st.session_state:
    st.session_state.farm_context = {}
if 'auto_play_tts' not in st.session_state:
    st.session_state.auto_play_tts = True
if 'audio_cache' not in st.session_state:
    st.session_state.audio_cache = {}
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = False
if 'current_audio_id' not in st.session_state:
    st.session_state.current_audio_id = None
if 'processed_audio_id' not in st.session_state:
    st.session_state.processed_audio_id = None
if 'last_auto_played_msg' not in st.session_state:
    st.session_state.last_auto_played_msg = -1

# Drought resilience knowledge base
KNOWLEDGE_BASE = """
You are JalMitra AI, a helpful assistant for farmers in Saurashtra, Gujarat facing drought conditions.

CONTEXT:
- Saurashtra receives only 200-400mm annual rainfall
- Groundwater declining at 4m/year
- Up to 95% crop losses due to drought
- You provide practical, actionable advice in simple language

KEY TOPICS YOU HELP WITH:
1. Drought-resistant crop selection (millets, pulses, groundnut)
2. Water conservation techniques (drip irrigation, mulching)
3. Rainwater harvesting methods
4. Soil moisture retention
5. Crop diversification strategies
6. Government schemes for drought relief

GUIDELINES:
- Keep answers simple and practical
- Use local context (Saurashtra region)
- Provide step-by-step instructions when needed
- Always add ethical disclaimer for critical decisions
- Be encouraging and supportive
- Consider farm size and resources when giving advice

ETHICAL DISCLAIMER (add when giving critical advice):
"આ માહિતી સામાન્ય માર્ગદર્શન માટે છે. મહત્વપૂર્ણ નિર્ણયો લેતા પહેલા કૃષિ વિશેષજ્ઞ સાથે સલાહ લો."
(This information is for general guidance. Consult agricultural experts before making important decisions.)
"""

def initialize_gemini(api_key):
    """Initialize Gemini API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def translate_text(text, to_gujarati=True):
    """Translate text using deep-translator with chunking for long text"""
    def translate_chunk(text, to_gujarati=True):
        """Translate a single chunk of text"""
        import time
        
        try:
            if not text or len(text.strip()) < 2:
                return text
            
            # Add small delay to avoid rate limiting
            time.sleep(0.3)
            
            if to_gujarati:
                translator = GoogleTranslator(source='auto', target='gu')
            else:
                translator = GoogleTranslator(source='auto', target='en')
            
            # Retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    result = translator.translate(text)
                    return result if result else text
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                    else:
                        raise retry_error
        except Exception as e:
            # Return original text on error
            return text
    
    try:
        # Split very long text into chunks to avoid API limits
        max_length = 4500  # Google Translate API limit is ~5000 chars
        if len(text) > max_length:
            # Split by paragraphs first
            paragraphs = text.split('\n\n')
            translated_paragraphs = []
            
            for para in paragraphs:
                if len(para) > max_length:
                    # Split long paragraphs by sentences
                    sentences = para.split('. ')
                    translated_sentences = []
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk + sentence) < max_length:
                            current_chunk += sentence + ". "
                        else:
                            if current_chunk:
                                translated_sentences.append(translate_chunk(current_chunk.strip(), to_gujarati))
                            current_chunk = sentence + ". "
                    
                    if current_chunk:
                        translated_sentences.append(translate_chunk(current_chunk.strip(), to_gujarati))
                    
                    translated_paragraphs.append(" ".join(translated_sentences))
                else:
                    translated_paragraphs.append(translate_chunk(para, to_gujarati))
            
            return "\n\n".join(translated_paragraphs)
        else:
            return translate_chunk(text, to_gujarati)
            
    except Exception as e:
        # Silently return original text - translation is optional
        return text

def clean_text_for_speech(text):
    """Clean text by removing symbols that TTS shouldn't read aloud"""
    # Remove common symbols and special characters (but keep numbers and periods for lists)
    symbols_to_remove = r'[\*_~`#@$%^&()\[\]{}<>|\\=+]'
    text = re.sub(symbols_to_remove, '', text)
    
    # Replace multiple asterisks (markdown bold/italic) with space
    text = re.sub(r'\*+', ' ', text)
    
    # Replace dashes/hyphens that are not part of words (like bullet points)
    text = re.sub(r'^\s*[-–—]\s+', '', text, flags=re.MULTILINE)  # Remove line-starting dashes
    text = re.sub(r'\s+[-–—]\s+', ' ', text)  # Remove dashes with spaces around them
    
    # Clean up markdown formatting
    text = re.sub(r'#{1,6}\s+', '', text)  # Remove markdown headers
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Convert [text](link) to just text
    
    # Replace underscores used for emphasis with spaces
    text = re.sub(r'_+', ' ', text)
    
    # Clean up quotation marks - keep them but normalize
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def text_to_speech(text, language='english'):
    """Convert text to speech using gTTS with caching"""
    try:
        # Clean text before creating cache key and generating speech
        cleaned_text = clean_text_for_speech(text)
        
        # Create a cache key from cleaned text and language
        cache_key = f"{language}_{hash(cleaned_text)}"
        
        # Check if audio is already cached
        if cache_key in st.session_state.audio_cache:
            return st.session_state.audio_cache[cache_key]
        
        # Set language code for gTTS
        lang_code = 'gu' if language == 'gujarati' else 'en'
        
        # Generate speech with cleaned text
        tts = gTTS(text=cleaned_text, lang=lang_code, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            
            # Read the file and encode to base64
            with open(fp.name, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Clean up temp file
            os.unlink(fp.name)
            
            # Cache the audio
            st.session_state.audio_cache[cache_key] = audio_bytes
            
            return audio_bytes
    except Exception as e:
        st.warning(f"TTS Error: {str(e)}")
        return None

def autoplay_audio(audio_bytes, show_controls=False):
    """Auto-play audio in Streamlit with optional controls"""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        controls_attr = "controls" if show_controls else ""
        audio_html = f"""
            <audio autoplay {controls_attr} id="audio-player">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

def stop_audio():
    """Stop any currently playing audio"""
    stop_script = """
        <script>
            var audioElements = document.querySelectorAll('audio');
            audioElements.forEach(function(audio) {
                audio.pause();
                audio.currentTime = 0;
            });
        </script>
    """
    st.markdown(stop_script, unsafe_allow_html=True)
    st.session_state.audio_playing = False
    st.session_state.current_audio_id = None

def speech_to_text_from_file(audio_bytes, language='english'):
    """Convert audio file to text using speech_recognition"""
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Save audio bytes to temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        # Load audio file
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Recognize speech
        lang_code = 'gu-IN' if language == 'gujarati' else 'en-IN'
        text = recognizer.recognize_google(audio_data, language=lang_code)
        
        return text
        
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        st.error(f"Speech recognition error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None

def get_ai_response(model, user_message, farm_context, language):
    """Get response from Gemini AI"""
    try:
        # Build context-aware prompt
        context_info = ""
        if farm_context:
            context_info = f"\n\nFARMER CONTEXT:\n"
            for key, value in farm_context.items():
                if value != "Not specified":
                    context_info += f"- {key}: {value}\n"
        
        # Build conversation history
        conversation_history = ""
        if len(st.session_state.messages) > 0:
            conversation_history = "\n\nCONVERSATION HISTORY:\n"
            for msg in st.session_state.messages[-6:]:  # Last 3 exchanges
                role = "Farmer" if msg["role"] == "user" else "JalMitra"
                conversation_history += f"{role}: {msg['content']}\n"
        
        # Create full prompt
        system_prompt = f"""{KNOWLEDGE_BASE}

IMPORTANT INSTRUCTIONS:
- Respond ONLY in {'Gujarati language' if language == 'gujarati' else 'English language'}
- Be conversational and helpful
- Give practical, actionable advice
- Keep responses concise (2-4 paragraphs)
- Use simple language that farmers can understand
{context_info}
{conversation_history}

Current question: {user_message}

Provide a helpful response in {'Gujarati' if language == 'gujarati' else 'English'}:"""
        
        # Get response from Gemini
        response = model.generate_content(system_prompt)
        return response.text
        
    except Exception as e:
        error_msg = f"Error getting AI response: {str(e)}"
        st.error(error_msg)
        return "I encountered an error. Please try again." if language == 'english' else "ભૂલ થઈ. ફરીથી પ્રયાસ કરો."

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>💧 JalMitra AI - Drought Resilience Assistant</h1>
            <p>Empowering Saurashtra Farmers with AI-Driven Solutions</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1163/1163451.png", width=100)
        st.title("⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            help="Get your free API key from https://aistudio.google.com/apikey"
        )
        
        if api_key:
            st.success("✅ API Key configured!")
        else:
            st.warning("⚠️ Please enter your API key to start chatting")
        
        st.markdown("---")
        
        # Language selection
        st.subheader("🌐 Language / ભાષા")
        language = st.radio(
            "Select Language",
            options=['english', 'gujarati'],
            format_func=lambda x: 'English' if x == 'english' else 'ગુજરાતી (Gujarati)',
            key='language_selector'
        )
        st.session_state.language = language
        
        st.markdown("---")
        
        # TTS Settings
        st.subheader("🔊 Voice Settings")
        auto_play = st.checkbox(
            "Auto-play responses" if language == 'english' else "જવાબ આપોઆપ વગાડો",
            value=st.session_state.auto_play_tts
        )
        st.session_state.auto_play_tts = auto_play
        
        st.markdown("---")
        
        # Farm context
        st.subheader("🌾 Farm Details")
        st.caption("Help us provide better advice")
        
        farm_size = st.selectbox(
            "Farm Size" if language == 'english' else "ખેતરનું કદ",
            ["Not specified", "Small (< 2 acres)", "Medium (2-5 acres)", "Large (> 5 acres)"]
        )
        
        soil_type = st.selectbox(
            "Soil Type" if language == 'english' else "માટીનો પ્રકાર",
            ["Not specified", "Sandy", "Clay", "Loamy", "Black soil"]
        )
        
        water_source = st.selectbox(
            "Water Source" if language == 'english' else "પાણીનો સ્રોત",
            ["Not specified", "Borewell", "Well", "Canal", "Rainwater only"]
        )
        
        # Update farm context
        st.session_state.farm_context = {
            "Farm Size": farm_size,
            "Soil Type": soil_type,
            "Water Source": water_source
        }
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.audio_cache = {}
            st.session_state.audio_playing = False
            st.session_state.current_audio_id = None
            st.session_state.processed_audio_id = None
            st.session_state.last_auto_played_msg = -1
            st.rerun()
        
        # Info section
        st.markdown("---")
        st.info("**About JalMitra AI**\n\nBuilt for Saurashtra farmers facing drought. Get expert advice on:\n- Drought-resistant crops\n- Water conservation\n- Rainwater harvesting\n- Soil management")
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat with JalMitra" if language == 'english' else "💬 જલમિત્ર સાથે વાત કરો")
    
    with col2:
        if st.button("⏹️ Stop Audio" if language == 'english' else "⏹️ ઓડિયો બંધ કરો", key="stop_audio_btn"):
            stop_audio()
    
    # Display ethical disclaimer
    if language == 'english':
        st.markdown("""
            <div class="info-box">
                <strong>⚠️ Important:</strong> This AI provides general guidance only. 
                Please consult with agricultural experts before making critical farming decisions.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-box">
                <strong>⚠️ મહત્વપૂર્ણ:</strong> આ AI સામાન્ય માર્ગદર્શન આપે છે. 
                મહત્વપૂર્ણ ખેતી સંબંધિત નિર્ણયો લેતા પહેલા કૃષિ વિશેષજ્ઞની સલાહ લો.
            </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        role_class = "user-message" if message["role"] == "user" else "bot-message"
        role_emoji = "👨‍🌾" if message["role"] == "user" else "💧"
        
        st.markdown(f"""
            <div class="chat-message {role_class}">
                <strong>{role_emoji} {message["role"].title()}:</strong><br>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)
        
        # Add TTS button for assistant messages
        if message["role"] == "assistant":
            col_audio1, col_audio2 = st.columns([1, 5])
            with col_audio1:
                if st.button(f"🔊 Play", key=f"tts_{idx}"):
                    audio_bytes = text_to_speech(message["content"], language)
                    if audio_bytes:
                        st.session_state.audio_playing = True
                        st.session_state.current_audio_id = f"msg_{idx}"
                        autoplay_audio(audio_bytes, show_controls=True)
    
    # Auto-play the last assistant message if enabled
    if st.session_state.auto_play_tts and len(st.session_state.messages) > 0:
        last_idx = len(st.session_state.messages) - 1
        last_message = st.session_state.messages[last_idx]
        
        # Only auto-play if it's an assistant message and hasn't been played yet
        if (last_message["role"] == "assistant" and 
            st.session_state.last_auto_played_msg < last_idx):
            audio_bytes = text_to_speech(last_message["content"], language)
            if audio_bytes:
                st.session_state.last_auto_played_msg = last_idx
                st.session_state.audio_playing = True
                st.session_state.current_audio_id = f"auto_msg_{last_idx}"
                autoplay_audio(audio_bytes, show_controls=True)
    
    # Sample questions
    if len(st.session_state.messages) == 0:
        st.markdown("### 🌟 Sample Questions" if language == 'english' else "### 🌟 નમૂનાના પ્રશ્નો")
        
        sample_questions = {
            'english': [
                "Which crops are best for drought conditions in Saurashtra?",
                "How can I save water using drip irrigation?",
                "What is rainwater harvesting and how do I implement it?",
                "How to improve soil moisture retention?",
                "What government schemes are available for drought relief?"
            ],
            'gujarati': [
                "સૌરાષ્ટ્રમાં સૂકાની પરિસ્થિતિમાં કયા પાક શ્રેષ્ઠ છે?",
                "ટપક સિંચાઈ વડે પાણી કેવી રીતે બચાવી શકાય?",
                "વરસાદી પાણીનો સંગ્રહ શું છે અને કેવી રીતે કરવો?",
                "જમીનમાં ભેજ જાળવવા શું કરવું?",
                "સૂકા માટે કઈ સરકારી યોજનાઓ ઉપલબ્ધ છે?"
            ]
        }
        
        cols = st.columns(2)
        for idx, question in enumerate(sample_questions[language]):
            with cols[idx % 2]:
                if st.button(question, key=f"sample_{idx}"):
                    if not api_key:
                        st.error("⚠️ Please enter your API key first!")
                    else:
                        # Add to messages
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        # Get AI response
                        model = initialize_gemini(api_key)
                        if model:
                            with st.spinner("જલમિત્ર વિચારી રહ્યો છે..." if language == 'gujarati' else "JalMitra is thinking..."):
                                response = get_ai_response(model, question, st.session_state.farm_context, language)
                                st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
    
    # Voice input section
    st.markdown("---")
    
    col_voice1, col_voice2, col_voice3 = st.columns([2, 3, 1])
    with col_voice1:
        st.markdown("### 🎤 Voice Input" if language == 'english' else "### 🎤 અવાજ ઇનપુટ")
    with col_voice3:
        if st.button("⏹️ Stop" if language == 'english' else "⏹️ બંધ કરો", key="stop_recording"):
            st.session_state.processed_audio_id = None
            st.rerun()
    
    # Audio recorder
    audio_file = st.audio_input(
        "Click to record, click again to stop" if language == 'english' else "રેકોર્ડ કરવા ક્લિક કરો, બંધ કરવા ફરી ક્લિક કરો",
        key="audio_recorder"
    )
    
    if audio_file is not None:
        # Create unique ID for this audio file
        audio_id = f"{audio_file.name}_{audio_file.size}"
        
        # Only process if this is a new audio file
        if audio_id != st.session_state.processed_audio_id:
            if not api_key:
                st.error("⚠️ Please enter your API key first!")
            else:
                # Mark this audio as processed
                st.session_state.processed_audio_id = audio_id
                
                # Read audio bytes
                audio_bytes = audio_file.read()
                
                with st.spinner("Processing audio..." if language == 'english' else "ઓડિયો પ્રોસેસ કરી રહ્યા છીએ..."):
                    # Convert speech to text
                    transcribed_text = speech_to_text_from_file(audio_bytes, language)
                    
                    if transcribed_text:
                        st.success(f"**You said:** {transcribed_text}" if language == 'english' else f"**તમે કહ્યું:** {transcribed_text}")
                        
                        # Add to messages
                        st.session_state.messages.append({"role": "user", "content": transcribed_text})
                        
                        # Get AI response
                        model = initialize_gemini(api_key)
                        if model:
                            with st.spinner("જલમિત્ર વિચારી રહ્યો છે..." if language == 'gujarati' else "JalMitra is thinking..."):
                                response = get_ai_response(model, transcribed_text, st.session_state.farm_context, language)
                                st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        st.rerun()
                    else:
                        st.error("Could not understand audio. Please try again." if language == 'english' else "અવાજ સમજી શક્યા નહીં. ફરીથી પ્રયાસ કરો.")
    
    st.markdown("---")
    
    # Chat input
    user_input = st.chat_input(
        "તમારો પ્રશ્ન અહીં લખો..." if language == 'gujarati' else "Type your question here..."
    )
    
    if user_input:
        if not api_key:
            st.error("⚠️ Please enter your Google Gemini API key in the sidebar first!")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Initialize Gemini and get response
            model = initialize_gemini(api_key)
            if model:
                with st.spinner("જલમિત્ર વિચારી રહ્યો છે..." if language == 'gujarati' else "JalMitra is thinking..."):
                    response = get_ai_response(model, user_input, st.session_state.farm_context, language)
                    st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.85rem;">
            <p>💧 <strong>JalMitra AI</strong> - Empowering Saurashtra Farmers | Built by Team MADD</p>
            <p>Atmiya AI Summit 2026 | <em>Free & Accessible Drought Resilience Education</em></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
