from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

app = FastAPI(title="Agentic Dispatch API")

# This allows your teammates' frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/logs")
async def get_audit_logs():
    """
    Streams the audit_log.jsonl file to the custom GUI.
    """
    def log_streamer():
        try:
            with open("audit_log.jsonl", "r", encoding="utf-8") as f:
                for line in f:
                    yield line
        except FileNotFoundError:
            yield json.dumps({"error": "No logs found yet"})

    return StreamingResponse(log_streamer(), media_type="application/jsonl")