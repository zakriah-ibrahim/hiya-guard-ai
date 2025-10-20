import os
import sys

def verify_env_file():
    print("Checking .env file...")
    if not os.path.exists('.env'):
        print("  .env file not found")
        print("    Create a .env file with your API keys")
        return False
    
    required_keys = [
        'DEEPGRAM_API_KEY',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing = []
    for key in required_keys:
        if not os.getenv(key):
            missing.append(key)
    
    if missing:
        print(f"  Missing API keys: {', '.join(missing)}")
        return False
    
    print("  .env file configured")
    return True

def verify_credentials():
    print("\nChecking Google Calendar credentials...")
    if not os.path.exists('credentials.json'):
        print("  credentials.json not found")
        print("    Follow GOOGLE_CALENDAR_SETUP.md to set up Calendar API")
        return False
    
    print("  credentials.json found")
    return True

def verify_dependencies():
    print("\nChecking dependencies...")
    required_packages = [
        'pyaudio',
        'webrtcvad',
        'deepgram',
        'openai',
        'elevenlabs',
        'sounddevice',
        'google',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"  Missing packages: {', '.join(missing)}")
        print("    Run: pip install -r requirements.txt")
        return False
    
    print("  All dependencies installed")
    return True

def verify_audio():
    print("\nChecking audio devices...")
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        input_devices = 0
        output_devices = 0
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices += 1
            if info['maxOutputChannels'] > 0:
                output_devices += 1
        
        p.terminate()
        
        if input_devices == 0:
            print("  No microphone detected")
            return False
        if output_devices == 0:
            print("  No speakers detected")
            return False
        
        print(f"  Audio devices found ({input_devices} input, {output_devices} output)")
        return True
        
    except Exception as e:
        print(f"  Audio check failed: {e}")
        return False

def main():
    print("="*60)
    print("VoiceGuard AI - Setup Verification")
    print("="*60)
    
    checks = [
        verify_dependencies(),
        verify_env_file(),
        verify_credentials(),
        verify_audio()
    ]
    
    print("\n" + "="*60)
    if all(checks):
        print("All checks passed! You're ready to run VoiceGuard AI")
        print("  Run: python main.py")
    else:
        print("Some checks failed. Please fix the issues above.")
    print("="*60)

if __name__ == "__main__":
    main()

