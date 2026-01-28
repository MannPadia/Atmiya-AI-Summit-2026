# 💧 JalMitra AI - Drought Resilience Assistant

**Empowering Saurashtra Farmers with AI-Driven Solutions**

JalMitra AI is an intelligent chatbot designed to help farmers in Saurashtra, Gujarat facing drought conditions. Built for the Atmiya AI Summit 2026, this application provides practical, actionable advice on drought-resistant farming techniques.

---

## Features

### Voice Interaction
- **Voice Input**: Record questions using your microphone
- **Text-to-Speech**: Responses are automatically read aloud in your chosen language
- **Auto-play**: Toggle automatic audio playback on/off
- **Stop Controls**: Stop audio playback anytime

### Bilingual Support
- **English**: Full support for English language
- **Gujarati (ગુજરાતી)**: Native Gujarati language support for local farmers

### AI-Powered Assistance
- Powered by **Google Gemini 2.5 Flash** model
- Context-aware conversations
- Farm-specific recommendations based on:
  - Farm size
  - Soil type
  - Water source availability

### Knowledge Areas
1. **Drought-resistant crop selection** (millets, pulses, groundnut)
2. **Water conservation techniques** (drip irrigation, mulching)
3. **Rainwater harvesting methods**
4. **Soil moisture retention**
5. **Crop diversification strategies**
6. **Government schemes for drought relief**

### User Experience
- Clean, modern interface
- Sample questions for quick start
- Conversation history
- Audio caching for faster playback
- Symbol-free TTS for natural speech

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get it here](https://aistudio.google.com/apikey))

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd jalmitra-ai

# Or download and extract the ZIP file
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
streamlit run jalmitra_integrated.py
```

The application will open in your default web browser at `http://localhost:8501`

---

## Usage Guide

### Getting Started

1. **Enter API Key**
   - Open the sidebar (left panel)
   - Enter your Google Gemini API key
   - Click outside the input field to save

2. **Select Language**
   - Choose between English or Gujarati (ગુજરાતી)
   - The interface and responses will adapt to your choice

3. **Configure Voice Settings**
   - Toggle "Auto-play responses" on/off
   - When enabled, AI responses play automatically

4. **Add Farm Details (Optional)**
   - Select your farm size
   - Choose soil type
   - Specify water source
   - This helps provide personalized recommendations

### Asking Questions

#### Method 1: Type Your Question
- Use the chat input at the bottom: "Type your question here..."
- Press Enter to send

#### Method 2: Use Sample Questions
- Click any of the sample questions displayed
- Great for getting started quickly

#### Method 3: Voice Input 🎤
1. Click the **microphone icon** under "Voice Input"
2. Allow microphone access when prompted
3. Speak your question clearly
4. Click the microphone icon again to stop recording
5. The app will transcribe and process your question
6. Use the **⏹ Stop** button to reset recording if needed

### Listening to Responses

#### Auto-play (Recommended)
- Enable "Auto-play responses" in sidebar
- New responses play automatically
- Audio continues while you read

#### Manual Playback
- Click the **🔊 Play** button below any AI response
- Audio player appears with controls
- Replay any previous response anytime

#### Stopping Audio
- Click **⏹ Stop Audio** button (top right)
- Stops all currently playing audio

---

## Configuration

### API Key
Get your free Google Gemini API key:
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Get API Key"
4. Copy and paste into JalMitra AI sidebar

### Language Settings
- **English**: Default language, best for technical terms
- **Gujarati**: For local farmers, natural conversation

### Farm Context
Providing farm details helps the AI give better recommendations:
- **Small farm** (< 2 acres): Budget-friendly solutions
- **Medium farm** (2-5 acres): Balanced approaches
- **Large farm** (> 5 acres): Scalable techniques

---

## Tips for Best Results

### Voice Input
- Speak clearly and at normal pace
- Use a quiet environment for better recognition
- Wait for the "Processing audio..." message
- Gujarati speech recognition works best with standard pronunciation

### Getting Better Answers
- Be specific in your questions
- Mention your current situation
- Ask follow-up questions for clarification
- Use the conversation history to build context

### Audio Quality
- Use headphones to avoid feedback
- Adjust system volume before starting
- Audio is cached - replaying is instant
- Symbols are automatically removed for natural speech

---

## Troubleshooting

### Audio Not Playing
- **Check browser settings**: Ensure autoplay is enabled
- **Click Play manually**: Use 🔊 Play buttons
- **Try different browser**: Chrome/Edge work best
- **Check volume**: System and browser volume should be up

### Voice Recording Not Working
- **Allow microphone access**: Check browser permissions
- **Check microphone**: Test in system settings
- **Try the Stop button**: Reset recording state
- **Reload page**: Refresh if recording is stuck

### API Errors
- **Invalid API key**: Double-check your key
- **Rate limits**: Wait a moment, then retry
- **Network issues**: Check internet connection

### Translation Issues
- **Long responses**: May take time to translate
- **Special terms**: Some agricultural terms translate better manually
- **Mixed language**: Choose one language for consistency

---

## Technical Details

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **AI Model**: Google Gemini 2.5 Flash
- **Translation**: Google Translator (deep-translator)
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Speech Recognition**: Google Speech Recognition API

### Features Implementation
- **Audio Caching**: Stores generated speech to avoid regeneration
- **Symbol Cleaning**: Removes markdown/special characters for natural TTS
- **State Management**: Prevents loops and duplicate processing
- **Error Handling**: Graceful fallbacks for all operations

### Browser Compatibility
- ✅ Chrome (Recommended)
- ✅ Edge (Recommended)
- ✅ Firefox (Good)
- ⚠️ Safari (Limited autoplay support)

---

## About the Project

### Context
Saurashtra, Gujarat faces severe drought conditions:
- Only 200-400mm annual rainfall
- Groundwater declining at 4m/year
- Up to 95% crop losses in extreme years

### Mission
Provide free, accessible agricultural guidance to help farmers:
- Adapt to drought conditions
- Implement water conservation
- Improve crop yields sustainably
- Access government support schemes

### Team
**Built by Team MADD** for Atmiya AI Summit 2026

---

## Important Disclaimer

**This AI provides general guidance only.**

Please consult with agricultural experts before making critical farming decisions. JalMitra AI is designed to supplement, not replace, professional agricultural advice.

**In Gujarati:**
આ માહિતી સામાન્ય માર્ગદર્શન માટે છે. મહત્વપૂર્ણ નિર્ણયો લેતા પહેલા કૃષિ વિશેષજ્ઞ સાથે સલાહ લો.

---

## Support & Feedback

### Getting Help
- Check this README first
- Review the Troubleshooting section
- Use the Clear Chat button to reset
- Reload the page if issues persist

### Providing Feedback
- Use the thumbs up/down (if available)
- Report issues through proper channels
- Suggest new features
- Share success stories!

---

## License

This project is built for educational and humanitarian purposes to support farmers in drought-affected regions.

---

## Acknowledgments

- **Atmiya AI Summit 2026**: For the platform and opportunity
- **Google**: For Gemini API and Speech services
- **Farmers of Saurashtra**: For inspiration and feedback
- **Open Source Community**: For the amazing tools and libraries

---

## Future Enhancements

Planned features:
- [ ] Weather integration
- [ ] Crop price monitoring
- [ ] Community forum
- [ ] Expert consultation booking
- [ ] Offline mode
- [ ] Mobile app version
- [ ] Image-based crop disease detection
- [ ] Multilingual support (Hindi, Marathi)

---

**💧 JalMitra AI - Your Companion in Drought Resilience**

*Free & Accessible Drought Resilience Education for All Farmers*
