Switch from Nixpacks to Dockerfile in EasyPanel
In EasyPanel:

Go to your App settings.

Change Build Pack from Python (Nixpacks) to Dockerfile.

Set the Build Context to '/'.

Set the Dockerfile path to Dockerfile (assuming you have it in the root of your repo).
# Integration of /qapslit endpoint with n8n
HTTP Request Node Setup:

URL: http://<your-fastapi-server>:8000/qasplit

Method: POST

Body: JSON payload from Google Sheets, e.g.:

{

  "question": "What is the capital of Azerbaijan?",
  
  "answer": "The capital of Azerbaijan is Baku, a vibrant city on the Caspian Sea.",
  
  "intent": "Geography"

}

Headers: Ensure Content-Type: application/json.


Output Handling:

The endpoint returns a response like:

{
  
  "status": "success",
  
  "data": 
  
  [
    {
    
      "text": "Q: What is the capital of Azerbaijan? A: The capital of Azerbaijan is Baku, a vibrant city on the Caspian Sea.",
    
      "intent": "Geography",
      
      "token_count": 25
    
    }
  ]
}

In n8n, pass the data array to the embedding node, using the text field for each chunk.


Embedding Node:

Use the text-embedding-ada-002 model to embed each text field.
Store the intent and token_count as metadata in your vector database (e.g., Pinecone, FAISS) for retrieval.
