from dotenv import load_dotenv

import os
import signal
import sys
import threading

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

import yorick


class AgentMotionController:
    def __init__(self, interval_seconds: float = 2.5):
        self.interval_seconds = interval_seconds
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop_event.set()
            thread = self._thread
            self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=0.1)

    def _run(self):
        while not self._stop_event.is_set():
            yorick.move_randomly()
            if self._stop_event.wait(self.interval_seconds):
                break

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

    motion_controller = AgentMotionController()

    def handle_agent_response(response: str):
        print(f"Agent: {response}")
        if response:
            motion_controller.start()

    def handle_user_transcript(transcript: str):
        print(f"User: {transcript}")
        motion_controller.stop()

    client = ElevenLabs(api_key=API_KEY)
    conversation = Conversation(
        client,
        AGENT_ID,
        # Assume auth is required when API_KEY is set
        requires_auth=bool(API_KEY),
        audio_interface=audio,
        callback_agent_response=handle_agent_response,
        callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
        callback_user_transcript=handle_user_transcript,
        callback_end_session=motion_controller.stop,
        # callback_latency_measurement=lambda latency: print(f"Latency: {latency}ms"),
    )
    conversation.start_session()

    def shutdown_handler(sig, frame):
        motion_controller.stop()
        conversation.end_session()

    signal.signal(signal.SIGINT, shutdown_handler)

    conversation_id = conversation.wait_for_session_end()
    motion_controller.stop()
    print(f"Conversation ID: {conversation_id}")

if __name__ == '__main__':
    main()
