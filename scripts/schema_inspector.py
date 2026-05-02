import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_schema_context():
    insp = inspect(engine)
    tables = insp.get_table_names()
    lines = ["DATABASE SCHEMA\n" + "="*40]

    for table in tables:
        cols = insp.get_columns(table)
        with engine.connect() as conn:
            count = conn.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar()

        lines.append(f"\nTable: {table}  ({count:,} rows)")
        lines.append("-" * 30)
        for col in cols:
            nullable = "" if col["nullable"] else " NOT NULL"
            lines.append(
                f"  {col['name']:<25} {str(col['type']):<20}{nullable}"
            )
    return "\n".join(lines)

if __name__ == "__main__":
    schema = get_schema_context()
    print(schema)

    with open("data/schema_context.txt", "w") as f:
        f.write(schema)
    print("\nSaved to data/schema_context.txt")