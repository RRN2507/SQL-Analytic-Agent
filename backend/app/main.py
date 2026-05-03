from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.agent import run_query
from backend.app.database import get_schema_context
import json
import os
import re
app = FastAPI(
    title="SQL Analytics Agent",
    description="Ask questions in plain English, get SQL + results",
    version="1.0.0"
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    question: str

# Health check
@app.get("/")
def root():
    return {"status": "SQL Analytics Agent is running"}

# Endpoint 1 — POST /query
@app.post("/query")
def query(request: QueryRequest):
    result = run_query(request.question)
    return {
        "question": request.question,
        "answer": result["answer"],
        "execution_time_sec": result["execution_time_sec"]
    }

# Endpoint 2 — GET /history
@app.get("/history")
def history():
    log_path = "data/query_log.jsonl"
    if not os.path.exists(log_path):
        return {"history": []}
    with open(log_path, "r") as f:
        lines = f.readlines()
    entries = [json.loads(line) for line in lines if line.strip()]
    return {"history": entries[-20:]}  # last 20 queries

# Endpoint 3 — GET /schema
@app.get("/schema")
def schema():
    return {"schema": get_schema_context()}
@app.post("/query")
def query(request: QueryRequest):
    # Safety guard — block dangerous keywords
    dangerous = ["drop", "delete", "insert", "update", "truncate"]
    question_lower = request.question.lower()
    for word in dangerous:
        if word in question_lower:
            return {
                "error": f"Questions containing '{word}' are not allowed.",
                "question": request.question
            }

    result = run_query(request.question)
    return {
        "question": request.question,
        "answer": result["answer"],
        "execution_time_sec": result["execution_time_sec"]
    }