import os
import time
import json
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from backend.app.database import get_db, get_schema_context
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq LLM — free and fast
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

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
4. Keep answers concise and clear.

Answer the user's question by querying the database.
"""

    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt
    )
    return agent

def run_query(question: str):
    agent = get_agent()
    start = time.time()

    result = agent.invoke({
        "messages": [HumanMessage(content=question)]
    })

    elapsed = round(time.time() - start, 2)
    answer = result["messages"][-1].content

    # Log to file
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "execution_time_sec": elapsed
    }
    with open("data/query_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {
        "answer": answer,
        "execution_time_sec": elapsed
    }