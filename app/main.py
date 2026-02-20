from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.incident_agent import create_agent, run_agent

app = FastAPI()

# Initialize agent once at startup
agent_instance = create_agent()


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/query")
def query_agent(request: QueryRequest):
    response = run_agent(agent_instance, request.question)
    return {"response": response}

import os
from dotenv import load_dotenv
from livekit import api

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")