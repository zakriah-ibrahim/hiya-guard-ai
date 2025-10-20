# Hiya Guard - Troubleshooting Guide

## Installation Issues

### PyAudio Installation Fails

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Other Dependencies Fail

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## API Configuration Issues

### "Missing API keys" Error

Check `.env` file exists and contains:
```
Assembly AI_API_KEY=actual_key_here
OPENAI_API_KEY=actual_key_here
ELEVENLABS_API_KEY=actual_key_here
```

No quotes needed around values.

### API Key Invalid/Unauthorized

1. Verify keys are copied correctly (no extra spaces)
2. Check API key is active in respective dashboards
3. Ensure billing is set up (if required)

**Test each API:**
- Assembly AI: https://console.Assembly AI.com/
- OpenAI: https://platform.openai.com/
- ElevenLabs: https://elevenlabs.io/

## Google Calendar Issues

### "credentials.json not found"

1. Ensure file is in project root directory
2. Check filename is exactly `credentials.json`
3. Re-download from Google Cloud Console if needed

### OAuth Authentication Fails

**"Access blocked: Authorization Error"**
- Add your email as test user in OAuth consent screen
- Or set consent screen to "Internal" (Google Workspace only)

**Browser doesn't open:**
```bash
python -c "from calendar_service import GoogleCalendarService; g = GoogleCalendarService(); g.authenticate()"
```

### Token Expired

Delete token and re-authenticate:
```bash
rm token.pickle
python main.py
```

## Audio Issues

### No Microphone Detected

**Check devices:**
```bash
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(p.get_device_info_by_index(i)['name']) for i in range(p.get_device_count())]"
```

**Set default device:** System sound settings

### Audio Feedback/Echo

1. Use headphones (strongly recommended)
2. Lower speaker volume
3. Increase distance between mic and speakers
4. Disable speaker output in system settings temporarily

### Poor Audio Quality

- Check microphone permissions
- Close other audio applications
- Adjust input levels in system settings
- Use better quality microphone if available

### "sounddevice" Errors

```bash
pip uninstall sounddevice
pip install sounddevice --no-cache-dir
```

## Runtime Errors

### WebSocket Connection Fails

**Assembly AI connection issues:**
1. Check internet connection
2. Verify Assembly AI_API_KEY is valid
3. Check firewall/proxy settings
4. Assembly AI service status: https://status.Assembly AI.com/

### OpenAI API Errors

**Rate limit exceeded:**
- Wait a few minutes
- Check usage limits in OpenAI dashboard
- Consider upgrading plan

**Model not found:**
- Ensure you have access to GPT-4o
- Try fallback: Change `OPENAI_MODEL` in `config.py` to `"gpt-4"` or `"gpt-3.5-turbo"`

### ElevenLabs Errors

**Voice ID not found:**
- Default: `21m00Tcm4TlvDq8ikWAM` (Rachel)
- Get your voices: https://elevenlabs.io/voice-library
- Update `ELEVENLABS_VOICE_ID` in `.env`

**Character limit reached:**
- ElevenLabs free tier has monthly limits
- Check usage: https://elevenlabs.io/subscription

## Performance Issues

### High Latency (>3s responses)

1. Check internet speed (min 5 Mbps recommended)
2. Close bandwidth-heavy applications
3. Use Ethernet instead of WiFi if possible
4. Check API status pages

### Agent Responses Too Slow

Adjust in `config.py`:
```python
OPENAI_TEMPERATURE = 0.5  # Lower = faster, less creative
ELEVENLABS_MODEL_ID = "eleven_turbo_v2"  # Use turbo model
```

### Silence Detection Too Aggressive

In `config.py`:
```python
SILENCE_TIMEOUT_SECONDS = 15  # Increase from 10
```

## Conversation Quality Issues

### Agent Doesn't Understand Caller

1. Speak clearly and at moderate pace
2. Reduce background noise
3. Check microphone positioning
4. Adjust VAD sensitivity in `config.py`:
```python
VAD_AGGRESSIVENESS = 1  # Less aggressive (0-3)
```

### Agent Interrupts Too Much

Increase utterance detection:
In `stt_service.py`, line 35:
```python
utterance_end_ms="2000"  # Increase from 1000
```

### Poor Spam Detection

1. Review `llm_service.py` system prompt
2. Add specific spam indicators for your use case
3. Increase confidence threshold for actions

## Calendar Issues

### Events Not Creating

**Check calendar access:**
1. Verify authentication succeeded
2. Check calendar permissions in Google account
3. Test manually:
```bash
python -c "from calendar_service import GoogleCalendarService; g = GoogleCalendarService(); g.authenticate(); print(g.get_free_slots())"
```

### Wrong Time Zone

Calendar service uses UTC by default. To change:
In `calendar_service.py`, update timezone in `create_event()`.

### No Available Slots Found

1. Check your calendar has free time in next 3 days
2. Adjust business hours in `calendar_service.py`:
```python
business_hours_start = 8  # Change from 9
business_hours_end = 18   # Change from 17
```

## Logging and Debugging

### Enable Detailed Logging

Add to top of `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

**Test STT:**
```bash
python -c "import asyncio; from stt_service import Assembly AISTTService; s = Assembly AISTTService(lambda t, f: print(t)); asyncio.run(s.connect())"
```

**Test TTS:**
```bash
python -c "import asyncio; from tts_service import ElevenLabsTTSService; t = ElevenLabsTTSService(); asyncio.run(t.speak_text('Hello world'))"
```

**Test LLM:**
```bash
python -c "import asyncio; from llm_service import ConversationEngine; e = ConversationEngine(); e.initialize_conversation(); asyncio.run(e.process_transcript('Hello'))"
```

## Common Error Messages

### "Event loop is closed"

Windows-specific asyncio issue:
Add to top of `main.py`:
```python
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

### "SSL: CERTIFICATE_VERIFY_FAILED"

```bash
pip install --upgrade certifi
```

macOS specific:
```bash
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Import Errors Despite Installing

Check Python version:
```bash
python --version  # Should be 3.11+
```

Use correct pip:
```bash
python -m pip install -r requirements.txt
```

## Still Having Issues?

1. Run verification script:
```bash
python verify_setup.py
```

2. Check API service status:
   - Assembly AI: https://status.Assembly AI.com/
   - OpenAI: https://status.openai.com/
   - ElevenLabs: Check their website

3. Review logs and error messages carefully

4. Test with simpler scenarios first

5. Verify all files are present:
```bash
ls -la
```

## Performance Optimization

### Reduce Latency

1. Use closest API regions
2. Pre-generate common responses
3. Reduce audio quality slightly:
```python
AUDIO_SAMPLE_RATE = 8000  # Lower quality, faster
```

### Reduce API Costs

1. Use `gpt-3.5-turbo` instead of `gpt-4o`
2. Cache TTS responses for common phrases
3. Reduce conversation history length

## System Requirements

Minimum:
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Internet: 5 Mbps
- Storage: 500 MB

Recommended:
- CPU: Quad-core 2.5 GHz+
- RAM: 8 GB+
- Internet: 10+ Mbps
- Storage: 1 GB

