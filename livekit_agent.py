import os
import requests
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    inference,
)

load_dotenv()

FASTAPI_URL = "http://127.0.0.1:8000/query"


# 🔥 This connects LiveKit voice to YOUR existing agent logic
class IncidentVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are an AI Production Incident Triage Assistant."
        )

    async def on_user_message(self, message):
        user_text = message.text

        print("User said:", user_text)

        try:
            response = requests.post(
                FASTAPI_URL,
                json={"question": user_text},
                timeout=60,
            )
            answer = response.json()["response"]

        except Exception as e:
            print("Error calling FastAPI:", e)
            answer = "Sorry, I could not process that request."

        print("Agent reply:", answer)

        await self.say(answer)


server = AgentServer()


@server.rtc_session(agent_name="incident-agent")
async def entrypoint(ctx: JobContext):

    session = AgentSession(
        # ✅ Replace Whisper with Deepgram
        stt=inference.STT(
            model="deepgram/nova-3"
        ),

        # Required internally but not used
        llm=inference.LLM(
            model="openai/gpt-4o-mini"
        ),

        # ✅ Replace Edge TTS with Cartesia
        tts=inference.TTS(
            model="cartesia/sonic-3"
        ),
    )

    await session.start(
        agent=IncidentVoiceAgent(),
        room=ctx.room,
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)