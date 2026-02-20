import os
import asyncio
import requests
from dotenv import load_dotenv

from livekit import rtc

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
API_BASE = "http://127.0.0.1:8000"


async def handle_data(room, data):
    user_text = data.data.decode()
    print("User said:", user_text)

    # Call FastAPI backend
    response = requests.post(
        f"{API_BASE}/query",
        json={"question": user_text},
    )

    answer = response.json()["response"]

    # Send response back
    await room.local_participant.publish_data(
        answer.encode()
    )


async def main(room_name: str, token: str):
    room = rtc.Room()

    @room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"Participant connected: {participant.identity}")

    @room.on("data_received")
    def on_data_received(data):
        # Cannot use async here directly
        asyncio.create_task(handle_data(room, data))

    print("Connecting to LiveKit room...")
    await room.connect(LIVEKIT_URL, token)
    print("Bot connected.")

    await asyncio.Event().wait()


if __name__ == "__main__":
    import sys

    room_name = sys.argv[1]
    token = sys.argv[2]

    asyncio.run(main(room_name, token))