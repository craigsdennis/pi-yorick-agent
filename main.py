from dotenv import load_dotenv

import os
import signal
import sys

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

import yorick

load_dotenv()

def main():
    AGENT_ID=os.environ.get('AGENT_ID')
    API_KEY=os.environ.get('ELEVENLABS_API_KEY')

    if not AGENT_ID:
        sys.stderr.write("AGENT_ID environment variable must be set\n")
        sys.exit(1)
    
    if not API_KEY:
        sys.stderr.write("ELEVENLABS_API_KEY not set, assuming the agent is public\n")

    # PATCH for mac
    MAC = False
    if MAC:
        import sounddevice as sd

        # Pick the current default input/output devices and lock to their native rate
        in_dev  = sd.query_devices(kind='input')
        out_dev = sd.query_devices(kind='output')

        sd.default.device     = (in_dev['name'], out_dev['name'])  # or use indices
        sd.default.samplerate = int(out_dev['default_samplerate'] or 48000)
        sd.default.channels   = (1, 1)     # (in, out) mono is simplest
        sd.default.blocksize  = 1024       # stable CoreAudio buffer
    
    audio = DefaultAudioInterface()

    client = ElevenLabs(api_key=API_KEY)
    conversation = Conversation(
        client,
        AGENT_ID,
        # Assume auth is required when API_KEY is set
        requires_auth=bool(API_KEY),
        audio_interface=audio,
        callback_agent_response=lambda response: print(f"Agent: {response}"),
        callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
        callback_agent_chat_response_part=lambda part: yorick.move_randomly()
        # callback_latency_measurement=lambda latency: print(f"Latency: {latency}ms"),
    )
    conversation.start_session()

    # Run until Ctrl+C is pressed.
    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

    conversation_id = conversation.wait_for_session_end()
    print(f"Conversation ID: {conversation_id}")

if __name__ == '__main__':
    main()
