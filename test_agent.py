from backend.app.agent import run_query

questions = [
    "How many customers are in the database?",
    "What is the churn rate as a percentage?",
    "Which contract type has the highest average monthly charge?",
]

for q in questions:
    print(f"\n{'='*50}")
    print(f"QUESTION: {q}")
    result = run_query(q)
    print(f"ANSWER: {result['answer']}")
    print(f"TIME: {result['execution_time_sec']}s")