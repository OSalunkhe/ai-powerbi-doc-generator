from pbixray import PBIXRay
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

model = PBIXRay("model.pbix")
measures = model.dax_measures

PROMPT_TEMPLATE = """You are a senior BI developer writing documentation for a colleague.

Here is a DAX measure from a Power BI model:

Table: {table}
Measure name: {name}
DAX expression:
{dax}

Write:
1. A one-sentence plain-English description of what this measure calculates (for a non-technical reader).
2. A one-line note on anything that looks risky, unclear, or worth double-checking (hardcoded values, missing error handling, ambiguous logic). If nothing stands out, say "No obvious issues."

Keep the whole answer under 60 words. Do not repeat the DAX code back."""

results = []

for index, row in measures.iterrows():
    table = row["TableName"]
    name = row["Name"]
    dax = row["Expression"]

    print(f"Documenting: [{table}] {name} ...")

    prompt = PROMPT_TEMPLATE.format(table=table, name=name, dax=dax)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.content[0].text.strip()
    except Exception as e:
        explanation = f"(Could not generate documentation - error: {e})"

    results.append({
        "table": table,
        "name": name,
        "dax": dax,
        "explanation": explanation
    })

# --- Write everything to a Markdown file ---
with open("model_documentation.md", "w", encoding="utf-8") as f:
    f.write("# Power BI Model Documentation\n\n")
    f.write("_Auto-generated with Claude - review before treating as final._\n\n")

    current_table = None
    for item in results:
        if item["table"] != current_table:
            current_table = item["table"]
            f.write(f"\n## Table: {current_table}\n\n")

        f.write(f"### {item['name']}\n\n")
        f.write(f"```dax\n{item['dax']}\n```\n\n")
        f.write(f"{item['explanation']}\n\n")
        f.write("---\n")

print(f"\nDone. Documented {len(results)} measures -> model_documentation.md")