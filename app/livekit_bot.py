import os

os.environ["PATH"] += os.pathsep + r"C:\Users\ADMIN\Downloads\ffmpeg-8.0.1-essentials_build\bin"

import asyncio
import requests
import numpy as np
import whisper
import soundfile as sf
import edge_tts
import uuid

from dotenv import load_dotenv
from livekit import rtc

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
API_BASE = "http://127.0.0.1:8000"

print("Loading Whisper...")
stt_model = whisper.load_model("base")

audio_buffer = []

async def text_to_speech(text: str) -> str:
    filename = f"{uuid.uuid4()}.wav"
    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )
    await communicate.save(filename)
    return filename


async def speak(room: rtc.Room, wav_path: str):

    data, sample_rate = sf.read(wav_path)

    if len(data.shape) > 1:
        data = data[:, 0]

    if data.dtype != np.int16:
        data = (data * 32767).astype(np.int16)

    source = rtc.AudioSource(sample_rate, 1)
    track = rtc.LocalAudioTrack.create_audio_track("bot-voice", source)

    publication = await room.local_participant.publish_track(track)

    frame_duration = 0.02
    samples_per_frame = int(sample_rate * frame_duration)

    for i in range(0, len(data), samples_per_frame):
        chunk = data[i:i + samples_per_frame]

        if len(chunk) == 0:
            continue

        frame = rtc.AudioFrame(
            data=chunk.tobytes(),
            sample_rate=sample_rate,
            num_channels=1,
            samples_per_channel=len(chunk)
        )

        await source.capture_frame(frame)
        await asyncio.sleep(frame_duration)

    await asyncio.sleep(0.3)
    await room.local_participant.unpublish_track(publication.sid)


async def process_audio(room: rtc.Room, frames):

    print("Processing audio...")

    audio_np = np.concatenate(frames).astype(np.float32) / 32768.0
    sf.write("temp.wav", audio_np, 16000)

  
    result = stt_model.transcribe("temp.wav")
    user_text = result["text"].strip()

    if not user_text:
        return

    print("User said:", user_text)

    response = requests.post(
        f"{API_BASE}/query",
        json={"question": user_text},
    )

    answer = response.json()["response"]
    print("Agent reply:", answer)

    wav_file = await text_to_speech(answer)

    print("Speaking reply...")
    await speak(room, wav_file)


async def main(room_name: str, token: str):

    room = rtc.Room()

    @room.on("participant_connected")
    def on_participant_connected(participant):
        print("Participant connected:", participant.identity)

    @room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):

        if track.kind == rtc.TrackKind.KIND_AUDIO:

            async def read_audio():

                stream = rtc.AudioStream(track)
                silence_counter = 0

                async for event in stream:

                    pcm = np.frombuffer(event.frame.data, dtype=np.int16)
                    volume = np.abs(pcm).mean()

                    if volume > 500:
                        audio_buffer.append(pcm)
                        silence_counter = 0
                    else:
                        silence_counter += 1

                    if silence_counter > 50 and len(audio_buffer) > 100:
                        await process_audio(room, audio_buffer.copy())
                        audio_buffer.clear()
                        silence_counter = 0

            asyncio.create_task(read_audio())

    print("Connecting to LiveKit...")
    await room.connect(LIVEKIT_URL, token)
    print("Bot connected.")

    await asyncio.Event().wait()


if __name__ == "__main__":
    import sys
    asyncio.run(main(sys.argv[1], sys.argv[2]))