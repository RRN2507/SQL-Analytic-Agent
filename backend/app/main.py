from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.agent import run_query
from backend.app.database import get_schema_context
from typing import Optional
import json, os, re

app = FastAPI(
    title="SQL Analytics Agent",
    description="Ask questions in plain English, get SQL + results",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"

@app.get("/")
def root():
    return {"status": "SQL Analytics Agent is running"}

@app.post("/query")
def query(request: QueryRequest):
    # Safety guard
    dangerous = ["drop", "delete", "insert", "update", "truncate"]
    for word in dangerous:
        if word in request.question.lower():
            return {"error": f"Questions containing '{word}' are not allowed."}

    result = run_query(request.question, request.session_id)
    return {
        "question": request.question,
        "answer": result["answer"],
        "execution_time_sec": result["execution_time_sec"],
        "session_id": result["session_id"]
    }

@app.get("/history")
def history():
    log_path = "data/query_log.jsonl"
    if not os.path.exists(log_path):
        return {"history": []}
    with open(log_path, "r") as f:
        lines = f.readlines()
    entries = [json.loads(l) for l in lines if l.strip()]
    return {"history": entries[-20:]}

@app.get("/schema")
def schema():
    return {"schema": get_schema_context()}

@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    from backend.app.agent import session_store
    session_store.pop(session_id, None)
    return {"message": f"Session {session_id} cleared"}