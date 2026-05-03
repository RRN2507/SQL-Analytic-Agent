import os
import time
import json
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from backend.app.database import get_db, get_schema_context
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# In-memory session store
# Stores last 5 messages per session_id
session_store: dict = {}

def get_agent():
    db = get_db()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    schema = get_schema_context()

    system_prompt = f"""
You are an expert SQL analyst connected to a PostgreSQL database.

DATABASE SCHEMA:
{schema}

YOUR RULES:
1. Only generate SELECT queries. NEVER use INSERT, UPDATE, DELETE, DROP.
2. Always use exact column names from the schema above.
3. Always explain what SQL you ran and what the result means.
4. Remember the conversation history and use it for follow-up questions.
5. Keep answers concise and clear.
"""

    memory = MemorySaver()
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
        checkpointer=memory
    )
    return agent

# Single agent instance reused across requests
agent = get_agent()

def run_query(question: str, session_id: str = "default"):
    start = time.time()

    # Build message history for this session
    history = session_store.get(session_id, [])

    # Add current question
    messages = history + [HumanMessage(content=question)]

    # Run agent with session thread
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke({"messages": messages}, config=config)

    elapsed = round(time.time() - start, 2)
    answer = result["messages"][-1].content

    # Update session memory — keep last 5 turns (10 messages)
    all_messages = result["messages"]
    session_store[session_id] = all_messages[-10:]

    # Log to file
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "execution_time_sec": elapsed
    }
    with open("data/query_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {
        "answer": answer,
        "execution_time_sec": elapsed,
        "session_id": session_id
    }