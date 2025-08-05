# EasyPanel Python Service Integration Guide

## Switch from Nixpacks to Dockerfile in EasyPanel

To migrate your app from Nixpacks to a Dockerfile setup in EasyPanel:

1. **Go to your App settings.**
2. **Change Build Pack:**  
   Select **Dockerfile** instead of **Python (Nixpacks)**.
3. **Set the Build Context:**  
   Use `/` (the root of your repository).
4. **Set the Dockerfile Path:**  
   Enter `Dockerfile` (assuming the file is located in the root of your repo).

---

## Integration of `/qapslit` Endpoint with n8n

### HTTP Request Node Setup

- **URL:**  
  `http://<your-fastapi-server>:8000/qasplit`
- **Method:**  
  `POST`
- **Body:**  
  Pass a JSON payload from Google Sheets, for example:
  ```json
  {
    "question": "What is the capital of Azerbaijan?",
    "answer": "The capital of Azerbaijan is Baku, a vibrant city on the Caspian Sea.",
    "intent": "Geography"
  }
  ```
- **Headers:**  
  Ensure `Content-Type: application/json`

---

### Output Handling

The endpoint returns a response like:
```json
{
  "status": "success",
  "data": [
    {
      "text": "Q: What is the capital of Azerbaijan? A: The capital of Azerbaijan is Baku, a vibrant city on the Caspian Sea.",
      "intent": "Geography",
      "token_count": 25
    }
  ]
}
```

In n8n, pass the `data` array to the embedding node, using the `text` field for each chunk.

---

### Embedding Node Setup

- **Model:**  
  Use the `text-embedding-ada-002` model to embed each `text` field.
- **Metadata:**  
  Store the `intent` and `token_count` as metadata in your vector database (e.g., Pinecone, FAISS) for retrieval.

---

## Example Workflow

1. **Receive data from Google Sheets.**
2. **Send HTTP POST request to `/qapslit` endpoint.**
3. **Parse the response and extract the `data` array.**
4. **Embed each `text` field using your embedding model.**
5. **Store embeddings along with `intent` and `token_count` metadata.**

---

## References

- [EasyPanel Documentation](https://easypanel.io/docs/)
- [n8n Documentation](https://docs.n8n.io/)
- [OpenAI text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings)
