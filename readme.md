# README.md

# MiniVault API

## Overview

A lightweight local REST API that accepts a text prompt and returns a generated response using a local LLM (via Ollama).

## Project Structure

minivault-api/
├── app.py # FastAPI application code
├── logs/
│ └── log.jsonl # Log file (JSON Lines format)
├── requirements.txt # Python dependencies
└── README.md # Setup instructions and notes

## Features

- POST /generate endpoint
- Uses local LLM via Ollama
- Logs interactions to logs/log.jsonl

## Setup Instructions

1. Clone the repository and navigate into it:

   ```bash
   git clone <your-repo-url>
   cd minivault-api
   ```

2. Create and activate a virtual environment (optional):

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure Ollama is running and has a model like llama2 available:

   ```bash
   ollama run llama2
   ```

5. Run the API:

   ```bash
   uvicorn app:app --reload
   ```

6. Test the endpoint:
   ```bash
   curl -X POST "http://localhost:8000/generate" \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Sing AC/DC"}'
   ```

## Sample Request

```json
POST /generate
{
  "prompt": "let there be light..."
}
```

## Sample Response

```json
{
  "response": "... let there be rock!"
}
```

##Design Choices and Trade-offs

###FastAPI vs. Flask
I chose FastAPI for its speed and built-in data validation capabilities. FastAPI automatically generates interactive API documentation at /docs, which is useful for manual testing. The use of Pydantic models ensures that if the client JSON is missing required fields or contains incorrect types, the API will return a clear 422 error by default—enhancing robustness.

While Flask could have been sufficient for a simple project, it would have required manually parsing JSON and implementing validation and error handling. FastAPI offered a cleaner, more structured solution with less boilerplate.

###Local LLM via Ollama
Using Ollama’s REST API decouples the application from the specifics of the model implementation. This eliminates the need to manage model loading or inference in-process, which can be resource-intensive. The trade-off is a dependency on an external service (Ollama) being available. In a production setting, I might consider directly integrating the model using libraries like Hugging Face Transformers or managing the Ollama service via Docker or a process supervisor. For this assignment, running a local model satisfied the requirement to avoid cloud APIs.

###Synchronous Call Inside Async Endpoint
The FastAPI endpoint is asynchronous, but it calls the blocking requests.post function to interact with Ollama. This is a minor anti-pattern since it could block the event loop. Given the expected low traffic and interactive testing use case, I accepted this trade-off for simplicity. A more scalable approach would involve using httpx.AsyncClient or offloading the request to a background thread or task.

###Logging to File
Logging each request and response to a file meets the assignment requirements and is straightforward to implement. However, in a long-running or concurrent environment, the log file could grow large or face write conflicts. For this context, a single flat file suffices. I chose the .jsonl (JSON Lines) format for a balance between human readability and machine parsing. More advanced logging strategies (e.g., rotation, structured logging frameworks) could be implemented as needed.

##Potential Improvements

###Streaming Responses
To enhance the user experience, the API could stream generated text token-by-token instead of waiting for the full response. FastAPI supports streaming responses, which would allow clients to receive output incrementally—similar to how ChatGPT works. This would require integration with Ollama’s streaming capabilities or manually generating text in chunks. While more complex, it would improve perceived responsiveness.

###Model Selection and Management
Currently, the model name is hardcoded. The API could be extended to allow clients to specify a model via an optional "model" field in the request. Additional endpoints could list available models or trigger downloads of new ones using Ollama’s management features. For example:

- GET /models: Return available model names

- POST /models/download: Download a new model

This would bring the API closer to a miniature version of ModelVault.

###Conversation History / Chat Mode
The API currently treats each prompt independently. A potential extension is to support session-based multi-turn conversations by storing previous messages in memory or a database keyed by session ID. This would allow implementing a chat-like experience.

###Enhanced Logging & Monitoring
Logging could be improved by including timestamps, request IDs, or client IP addresses for better observability. Asynchronous logging could be introduced if performance becomes a concern. Basic metrics (e.g., request count, average latency) could also be added to monitor the system's usage.

###Error Handling and Validation
Basic error handling for model calls has been implemented. This could be expanded to return more informative messages and appropriate HTTP status codes depending on the type of error (e.g., model not found, invalid prompt). FastAPI already provides good defaults, such as returning a 422 for missing fields.

###Testing
With more time, I would implement unit and integration tests. FastAPI’s TestClient allows simulating requests and verifying expected behavior. Tests could validate:

- Stubbed model responses

- Log file contents

- Input validation errors

- Testing ensures that future changes do not introduce regressions.

###Client Tooling (CLI/Postman)
To simplify testing, I could provide a small CLI (e.g., cli.py) that accepts a prompt and prints the API’s response. Alternatively, a Postman collection with sample requests would make it easier for others to interact with the API during development and review.
