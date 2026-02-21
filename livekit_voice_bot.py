import os
import asyncio
import tempfile
import numpy as np
import soundfile as sf
import whisper
from TTS.api import TTS
from dotenv import load_dotenv
from livekit import rtc

from app.agent.incident_agent import create_agent, run_agent

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")

# ---------------------------
# Load Models Once
# ---------------------------

print("Loading Whisper...")
stt_model = whisper.load_model("base")

print("Loading TTS...")
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

print("Loading Agent...")
agent_instance = create_agent()


# ---------------------------
# Audio Utilities
# ---------------------------

async def transcribe_audio(audio_np, sample_rate):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_np, sample_rate)
        result = stt_model.transcribe(tmpfile.name)
    return result["text"]


async def synthesize_speech(text):
    wav = tts_model.tts(text)
    return np.array(wav), 22050


# ---------------------------
# Voice Handler
# ---------------------------

async def handle_audio(room, track):
    print("Receiving audio...")

    audio_frames = []

    async for frame in track:
        audio_frames.append(frame.data)

        # Collect 3 seconds of audio
        if len(audio_frames) > 150:
            audio_np = np.concatenate(audio_frames)

            print("Transcribing...")
            text = await transcribe_audio(audio_np, 48000)

            print("User said:", text)

            print("Running agent...")
            response = run_agent(agent_instance, text)

            print("Agent:", response)

            print("Synthesizing speech...")
            wav, sr = await synthesize_speech(response)

            # Publish back to room
            source = rtc.AudioSource(sr, 1)
            await room.local_participant.publish_track(source)

            await source.capture_frame(
                rtc.AudioFrame(
                    wav.astype(np.float32).tobytes(),
                    sample_rate=sr,
                    num_channels=1,
                )
            )

            audio_frames = []


# ---------------------------
# Main
# ---------------------------

async def main(room_name: str, token: str):
    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        if track.kind == rtc.TrackKind.AUDIO:
            asyncio.create_task(handle_audio(room, track))

    print("Connecting to LiveKit room...")
    await room.connect(LIVEKIT_URL, token)
    print("Voice Bot connected.")

    await asyncio.Event().wait()


if __name__ == "__main__":
    import sys
    room_name = sys.argv[1]
    token = sys.argv[2]
    asyncio.run(main(room_name, token))