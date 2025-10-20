# Hiya Guard - Quick Start Guide

Get up and running in 15 minutes.

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Microphone connected
- [ ] Headphones recommended (prevent audio feedback)
- [ ] Assembly AI API key
- [ ] OpenAI API key
- [ ] ElevenLabs API key
- [ ] Google account for Calendar API

## 5-Step Setup

### Step 1: Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

**Windows users:** If pyaudio fails:
```bash
pip install pipwin
pipwin install pyaudio
```

### Step 2: Configure API Keys (3 min)

Create `.env` file:
```
Assembly AI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
USER_NAME=<Your Name>
```

### Step 3: Google Calendar Setup (5 min)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Enable Calendar API
3. Create OAuth credentials (Desktop app)
4. Download `credentials.json` to project folder

Full guide: `GOOGLE_CALENDAR_SETUP.md`

### Step 4: Verify Setup (1 min)

```bash
python verify_setup.py
```

Fix any issues reported.

### Step 5: Run! (1 min)

```bash
python main.py
```

First run:
- Browser opens for Google Calendar auth
- Greeting audio generates (cached for future use)
- Takes ~30 seconds

## First Test Call

1. Press Enter when prompted
2. Speak: "Hi, this is Sarah from TechCorp calling about a partnership"
3. Listen to AI response
4. Continue conversation naturally
5. AI will schedule a callback on your calendar

## Common Issues

**"No module named X"**
→ Run: `pip install -r requirements.txt`

**"credentials.json not found"**
→ Download from Google Cloud Console

**Audio feedback**
→ Use headphones

**API errors**
→ Check `.env` file has correct keys

**Silence timeout**
→ Adjust `SILENCE_TIMEOUT_SECONDS` in `config.py`

## Next Steps

- Review test scenarios: `test_scenarios.md`
- Test spam detection with sample scripts
- Customize system prompt in `llm_service.py`
- Adjust voice settings in `config.py`

## Quick Commands

```bash
python verify_setup.py    # Check setup
python main.py            # Run agent
```

## Getting API Keys

**Assembly AI:** https://console.Assembly AI.com/
- Sign up → Create API key → Copy

**OpenAI:** https://platform.openai.com/api-keys
- Sign up → Create new key → Copy

**ElevenLabs:** https://elevenlabs.io/
- Sign up → Profile → API keys → Generate

## Support

Check these files for help:
- `README.md` - Full documentation
- `GOOGLE_CALENDAR_SETUP.md` - Calendar API guide
- `test_scenarios.md` - Test scripts
- `troubleshooting.md` - Common problems

## Architecture Overview

```
Microphone → Assembly AI STT → GPT-4o → ElevenLabs TTS → Speakers
                               ↓
                        Google Calendar
```

Real-time streaming: <2.5s response time

