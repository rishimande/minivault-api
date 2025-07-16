from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, json, os

app = FastAPI()

# Pydantic model for the request body
class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_text(input_data: PromptRequest):
    prompt_text = input_data.prompt
    try:
        # Send prompt to local Ollama LLM API (assuming Ollama is running on localhost:11434)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": prompt_text}
        )
        response.raise_for_status()  # Raise error if the Ollama API call failed
    except requests.RequestException as e:
        # Return an HTTP 500 error if we cannot get a response from the local model
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {e}")
    # If successful, parse the generated text from Ollama's response JSON
    generated_text = response.json().get("response", "")
    # Log the input and output to a file in JSONL format (one record per line)
    os.makedirs("logs", exist_ok=True)
    with open("logs/log.jsonl", "a") as log_file:
        log_entry = {"prompt": prompt_text, "response": generated_text}
        log_file.write(json.dumps(log_entry) + "\n")
    # Return the generated text in the expected JSON format
    return {"response": generated_text}

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app with Uvicorn (development server)
    uvicorn.run(app, host="0.0.0.0", port=8000)
