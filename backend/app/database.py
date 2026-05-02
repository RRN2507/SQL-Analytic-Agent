import os
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    db = SQLDatabase.from_uri(
        DATABASE_URL,
        include_tables=["customers", "plans"],
        sample_rows_in_table_info=3
    )
    return db

def get_schema_context():
    schema_path = "data/schema_context.txt"
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            return f.read()
    return ""

engine = create_engine(DATABASE_URL)