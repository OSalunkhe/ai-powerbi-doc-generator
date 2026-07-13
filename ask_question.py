import sqlite3
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic
from schema_context import get_schema_context

load_dotenv()
client = Anthropic()

SCHEMA = get_schema_context()

SQL_PROMPT_TEMPLATE = """You are a SQL expert. Given a database schema and a question, write ONE SQLite SELECT query that answers it.

Schema:
{schema}

Rules:
- Only write a single SELECT statement. Never write INSERT, UPDATE, DELETE, DROP, ALTER, or multiple statements separated by semicolons.
- Use only the table and column names shown above, exactly as written.
- When a question asks for a breakdown "for each" or "every" entity (e.g. each store, every product), use a LEFT JOIN from that entity's table to the related data table, and wrap aggregates in COALESCE(..., 0) so entities with no matching rows still appear in the results with a value of 0, rather than being silently excluded.
- If the question references a concept (like "region") that has no exact matching column, add a one-line SQL comment at the very top explaining the closest substitute you used, e.g. -- Note: no "region" column exists; using Store.Type as a proxy.
- Return ONLY the raw SQL query - no explanation, no markdown code fences, no other commentary.

Question: {question}

SQL query:"""


def generate_sql(question):
    prompt = SQL_PROMPT_TEMPLATE.format(schema=SCHEMA, question=question)
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    sql = next(block.text for block in response.content if block.type == "text").strip()
    # Strip accidental code fences, just in case the model adds them anyway
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def extract_assumption_note(sql):
    """Pull out any leading '--' comment line so it can be shown separately."""
    notes = [line.strip() for line in sql.splitlines() if line.strip().startswith("--")]
    return "\n".join(notes) if notes else None


def is_safe_select(sql):
    """Belt-and-suspenders check - never trust generated SQL just because the prompt asked nicely."""
    # Strip leading comment lines (e.g. an assumption note) before checking structure
    code_lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    body = "\n".join(code_lines).strip().rstrip(";")
    upper = body.upper()

    if not upper.startswith("SELECT"):
        return False

    banned_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "ATTACH", "PRAGMA", "CREATE", "REPLACE"]
    if any(word in upper for word in banned_keywords):
        return False

    if ";" in body:
        return False

    return True


def run_query(sql):
    # Open in read-only mode as an extra safety net, even though is_safe_select already checked
    conn = sqlite3.connect("file:model_data.db?mode=ro", uri=True)
    try:
        result = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return result


def summarize_result(question, result_df, note=None):
    if result_df is None or result_df.empty:
        return "No results were returned for this question."

    caveat = f"\n\nImportant: {note.replace('-- ', '')}" if note else ""

    prompt = f"""A user asked: "{question}"

The query returned this data:
{result_df.to_string(index=False)}{caveat}

Write a one to two sentence plain-English answer to the user's question based on this data.
Do not mention SQL, databases, or queries.
Do not add a title, heading, or any markdown formatting like # or ** - just plain sentences.
If an "Important" note is given above, work its caveat naturally into your answer so the user isn't misled about what the data actually represents."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return next(block.text for block in response.content if block.type == "text").strip()


def answer_question(question):
    sql = generate_sql(question)
    print(f"Generated SQL:\n{sql}\n")

    note = extract_assumption_note(sql)
    if note:
        print(f"Assumption made by the model:\n{note}\n")

    if not is_safe_select(sql):
        print("Blocked: the generated query did not pass the safety check.")
        return None

    try:
        result = run_query(sql)
    except Exception as e:
        print(f"Query failed to run: {e}")
        return None

    print("Result:")
    print(result)

    summary = summarize_result(question, result, note)
    print(f"\nAnswer: {summary}")

    return result


if __name__ == "__main__":
    question = input("Ask a question about your data: ")
    answer_question(question)