import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from livekit import api

from app.agent.incident_agent import create_agent, run_agent

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


app = FastAPI()

agent_instance = create_agent()




class QueryRequest(BaseModel):
    question: str


class TokenRequest(BaseModel):
    identity: str
    room: str



@app.get("/health")
def health_check():
    return {"status": "ok"}



@app.post("/query")
def query_agent(request: QueryRequest):
    response = run_agent(agent_instance, request.question)
    return {"response": response}


@app.post("/create-token")
def create_token(request: TokenRequest):
    token = api.AccessToken(
        LIVEKIT_API_KEY,
        LIVEKIT_API_SECRET
    ).with_identity(
        request.identity
    ).with_name(
        request.identity
    ).with_grants(
        api.VideoGrants(
            room_join=True,
            room=request.room,
        )
    ).to_jwt()

    return {
        "token": token,
        "url": LIVEKIT_URL
    }