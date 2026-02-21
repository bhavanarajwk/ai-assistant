import whisper
import requests
from TTS.api import TTS

print("Loading Whisper...")
model = whisper.load_model("base")

print("Loading TTS...")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
    )
    return response.json()["response"]

# Step 1: Use any short wav file you have
audio_file = "input.wav"

print("Transcribing...")
text = model.transcribe(audio_file)["text"]
print("User:", text)

print("Querying Ollama...")
reply = query_ollama(text)
print("Bot:", reply)

print("Generating speech...")
tts.tts_to_file(text=reply, file_path="output.wav")

print("Done. Check output.wav")