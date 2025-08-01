# main.py
from fastapi import FastAPI, Query
import azure.cognitiveservices.speech as speechsdk
import base64, uuid
from dotenv import load_dotenv
import os
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()
app = FastAPI()
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SERVICE_REGION")

@app.get("/")
async def root():
    return {"message": "Python API service point is live."}

@app.get("/tts")
async def tts(text: str = Query(...)):
    print(f"[DEBUG] Requested text: {text}")
    filename = f"{uuid.uuid4()}.wav"
    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_language = "az-AZ"
        speech_config.speech_synthesis_voice_name = "az-AZ-BabekNeural"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()
        print(f"[DEBUG] Synthesis result: {result.reason}")
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"[ERROR] CANCELED: Reason={cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"[ERROR] Error details: {cancellation_details.error_details}")
            return {"audio_base64": ""}
        with open(filename, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        print(f"[DEBUG] Base64 length: {len(audio_base64)}")
        return {"audio_base64": audio_base64}
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return {"audio_base64": ""}

@app.get("/embeddings")
async def embeddings(text: str = Query(...)):
    print(f"[DEBUG] Requested text for embedding: {text}")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode([text])[0]
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        embedding_base64 = base64.b64encode(embedding_bytes).decode("utf-8")
        print(f"[DEBUG] Embedding base64 length: {len(embedding_base64)}")
        return {"embedding_base64": embedding_base64}
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return {"embedding_base64": ""}
