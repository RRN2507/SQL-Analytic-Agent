import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# Load churn CSV
df = pd.read_csv("data/churn.csv")

# Clean column names
df.columns = [c.lower().replace(" ", "_").replace("-", "_")
              for c in df.columns]

# Load into PostgreSQL
df.to_sql("customers", engine,
          if_exists="replace",
          index=False)

print(f"Loaded {len(df)} rows into 'customers' table")

# Verify
row = pd.read_sql("SELECT COUNT(*) FROM customers", engine)
print("Verified:", row.iloc[0, 0], "rows in DB")

# Create plans table
plans_sql = """
CREATE TABLE IF NOT EXISTS plans (
  plan_id SERIAL PRIMARY KEY,
  plan_name VARCHAR(50),
  monthly_fee NUMERIC(8,2),
  data_limit_gb INTEGER,
  category VARCHAR(20)
);

INSERT INTO plans (plan_name, monthly_fee, data_limit_gb, category)
VALUES
  ('Basic',    19.99,  5,   'prepaid'),
  ('Standard', 39.99,  20,  'postpaid'),
  ('Premium',  69.99,  100, 'postpaid'),
  ('Unlimited',89.99,  999, 'postpaid')
ON CONFLICT DO NOTHING;
"""

with engine.connect() as conn:
    conn.execute(text(plans_sql))
    conn.commit()
    print("Plans table created")