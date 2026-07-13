from ask_question import generate_sql, is_safe_select, run_query, summarize_result, extract_assumption_note

# Replace these with questions specific to your own schema - mix easy, joined,
# intentionally-ambiguous, and filtered questions. See the guide for what makes
# a good spread.
TEST_QUESTIONS = [
    "How many stores are in the Store table?",     # ground truth count - should always be 14
    "What were total sales for each store?",       # should return 14 rows, not 13, after the LEFT JOIN fix
    "What is the total number of rows in the Sales table?",
    "What were total sales by region?",
]

for question in TEST_QUESTIONS:
    print("=" * 70)
    print(f"Q: {question}")

    sql = generate_sql(question)
    print(f"SQL:\n{sql}")

    note = extract_assumption_note(sql)
    if note:
        print(f"ASSUMPTION FLAGGED: {note}")

    if not is_safe_select(sql):
        print("BLOCKED by safety check")
        continue

    try:
        result = run_query(sql)
        print(f"RESULT:\n{result}")

        answer = summarize_result(question, result, note)
        print(f"ANSWER: {answer}")
    except Exception as e:
        print(f"FAILED: {e}")

    print()