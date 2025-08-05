# main.py
from fastapi import FastAPI, Query, HTTPException
import azure.cognitiveservices.speech as speechsdk
import base64, uuid
from dotenv import load_dotenv
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from transformers import AutoTokenizer
import logging

load_dotenv()
# Initialize FastAPI app
app = FastAPI()

speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SERVICE_REGION")
 
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Azerbaijani tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained("heziyevv/aze-bert-tokenizer-middle")
except Exception as e:
    logger.error(f"Failed to load tokenizer: {e}")
    raise Exception("Tokenizer initialization failed")

# Define input model for FastAPI
class QAPair(BaseModel):
    question: str
    answer: str
    intent: str

# Helper function to check token count
def get_token_count(text: str) -> int:
    tokens = tokenizer.encode(text, add_special_tokens=True)
    return len(tokens)

# Helper function to split text if it exceeds token limit
def split_text_by_tokens(text: str, max_tokens: int = 500) -> list:
    """Split text into chunks respecting max token limit."""
    tokens = tokenizer.encode(text, add_special_tokens=True)
    chunks = []
    current_chunk = []
    current_count = 0

    for token in tokens:
        current_chunk.append(token)
        current_count += 1
        if current_count >= max_tokens:
            chunk_text = tokenizer.decode(current_chunk, skip_special_tokens=True)
            chunks.append(chunk_text.strip())
            current_chunk = []
            current_count = 0

    if current_chunk:
        chunk_text = tokenizer.decode(current_chunk, skip_special_tokens=True)
        chunks.append(chunk_text.strip())

    return chunks
    
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

@app.post("/qasplit")
async def qasplit(qapair: QAPair):
    """
    Endpoint to split Q&A pair based on token limits for embedding.
    Input: question, answer, intent
    Output: List of split texts with metadata
    """
    try:
        # Combine question and answer for splitting
        combined_text = f"Q: {qapair.question} A: {qapair.answer}"
        
        # Check token count
        token_count = get_token_count(combined_text)
        max_tokens = 500  # Slightly below ada-002's typical limit to be safe

        if token_count <= max_tokens:
            # If within limit, return as single chunk
            result = [{
                "text": combined_text,
                "intent": qapair.intent,
                "token_count": token_count
            }]
        else:
            # Split text if it exceeds token limit
            split_texts = split_text_by_tokens(combined_text, max_tokens)
            result = [
                {
                    "text": chunk,
                    "intent": qapair.intent,
                    "token_count": get_token_count(chunk)
                }
                for chunk in split_texts
            ]

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        logger.error(f"Error processing Q&A pair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

