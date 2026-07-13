# AI-Powered Power BI Assistant

A two-part project that uses the Claude API to make a Power BI model easier to understand and query. **Part 1** automatically documents every DAX measure in plain English. **Part 2** lets you ask questions about the model's data in plain English and get back a real, computed answer.

## Why

Power BI models accumulate DAX measures faster than anyone documents them, and getting an answer out of a model usually means already knowing DAX or SQL. This project treats both problems as generation problems: extract the model's structure programmatically, then use an LLM either to explain what's already there (Part 1) or to translate a plain-English question into a query against it (Part 2).

## Tech stack

| Piece | Tool |
|---|---|
| PBIX metadata & data extraction | [pbixray](https://github.com/Hugoberry/pbixray) |
| LLM | Claude API (`claude-haiku-4-5` for short text generation, `claude-sonnet-5` for SQL generation) via the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) |
| Local data store (Part 2) | SQLite (built into Python) via `pandas` |
| Demo UI | [Streamlit](https://streamlit.io/) |
| Secrets management | `python-dotenv` |

## Setup

```bash
git clone https://github.com/YOUR-USERNAME/ai-powerbi-doc-generator.git
cd ai-powerbi-doc-generator
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your own Claude API key (get one at [platform.claude.com](https://platform.claude.com/)):

```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Add your own `.pbix` file to the project folder as `model.pbix`, or use the free [Sales & Returns Sample](https://github.com/microsoft/powerbi-desktop-samples/blob/main/Sample%20Reports/Sales%20%26%20Returns%20Sample%20v201912.pbix) from Microsoft to try it out.

---

## Part 1: Documentation generator

```
model.pbix
    │
    ▼
pbixray  →  extracts tables, DAX measures, relationships
    │
    ▼
Claude API  →  generates a plain-English description + risk flag per measure
    │
    ▼
model_documentation.md   (or the Streamlit app, for an interactive view)
```

**Generate a Markdown doc for the whole model:**

```bash
python generate_docs.py
```

Outputs `model_documentation.md`, organized by table, with each measure's DAX code and Claude's explanation.

**Or run the interactive demo app:**

```bash
streamlit run app.py
```

Upload any `.pbix` file in the browser and generate documentation live, one measure at a time, in an expandable panel.

<video controls src="https://github.com/user-attachments/assets/708815ab-a59a-468c-a128-24a64e66b5b5" title="Part 1 demo"></video>

### Part 1 evaluation

I manually reviewed a sample of the generated explanations against my own understanding of the model's DAX logic:

- For straightforward measures (single aggregations, simple `CALCULATE`/`FILTER` combinations), the generated descriptions were accurate and clearly written.
- For measures with **nested logic** — several `CALCULATE`/`FILTER` layers stacked inside one another — the explanations were still directionally correct but occasionally **omitted one intermediate step** in the calculation chain, describing the overall result without fully accounting for every filter applied along the way. The model didn't get these wrong so much as under-explain them.
- No hallucinated logic was observed — errors were omissions, not fabrications, which is a meaningfully safer failure mode for a documentation tool.

**Takeaway:** this tool is reliable as a first-pass documentation generator, especially for models with many simple-to-moderate measures, but output on deeply nested measures should be spot-checked by whoever owns the model rather than treated as final. A natural next step would be prompting the model to explicitly enumerate each nested step before summarizing, rather than jumping straight to a one-sentence description.

---

## Part 2: Ask your data in plain English

Beyond static documentation, this project also supports natural-language querying against the model's actual data.

```
Question ("What were total sales by region?")
    │
    ▼
schema_context.py  →  describes tables/columns/relationships as text
    │
    ▼
Claude  →  generates a single read-only SQL SELECT query
    │
    ▼
safety check  →  rejects anything that isn't a plain, single SELECT
    │
    ▼
SQLite  →  runs the query against data exported from the .pbix (read-only)
    │
    ▼
Claude  →  turns the result table into a plain-English answer
```

**Architecture note:** this is a text-to-SQL system, not classic RAG — the LLM generates a query against a known schema rather than retrieving documents. Table data is exported from the .pbix file into a local SQLite database rather than querying Power BI Service directly, since a live connection would require the XMLA endpoint (Premium/PPU workspace + Azure AD auth).

**Run it:**

```bash
python export_to_sqlite.py    # one-time export of your model's data
python ask_question.py        # ask a single question from the terminal
# or:
streamlit run nl_query_app.py # interactive version
```

<video controls src="https://github.com/user-attachments/assets/87916e55-779e-4b6c-8ee9-daa9363e3893" title="Part 2 demo"></video>

### Part 2 evaluation

Testing this against my own model surfaced four distinct failure modes, each of which led to a specific fix. I'm documenting all four because each represents a different category of thing that can go wrong with an LLM-generated-query system, not just "it sometimes gets things wrong":

**1. Silent semantic substitution.** Asking "What were total sales by region?" against a schema with no `region` column, the model didn't say it couldn't answer the question — it silently picked the closest-sounding column (`Store.Type`, whose values are "External"/"Internal", a store classification, not a geography) and labeled it `Region` in the output. The SQL ran, the numbers were real, and nothing about the result signaled that "region" here didn't mean what the user would assume.

*Fix:* added a prompt rule requiring the model to add a one-line SQL comment flagging any such substitution (e.g. `-- Note: no "region" column exists; using Store.Type as a proxy`), extracted and surfaced separately in both the CLI and the Streamlit app.

**2. Non-deterministic instruction-following.** Running the exact same question multiple times after adding the rule above showed it isn't followed reliably: one run correctly added the comment, another run substituted a *different* column (the store's name instead of its type) with no comment at all. This is a direct, reproducible demonstration that a prompt rule shapes model behavior probabilistically, not deterministically — which is exactly why the safety check in `is_safe_select()` is implemented as plain Python logic rather than another instruction the model is asked to follow.

**3. A caveat that didn't survive the pipeline.** Even on runs where the SQL layer correctly flagged the `Store.Type` substitution, that caveat initially never reached the final answer — `summarize_result()` only received the raw result table, not the note, so it wrote a fully confident sentence with no caveat. Separately, the note-extraction and display logic had only been wired into the CLI script and not into the Streamlit app built on the same underlying functions, so the same question behaved differently depending on which interface it was asked through.

*Fix:* threaded the assumption note explicitly through to the summarization prompt, and wired the same display logic into both the CLI and the Streamlit app rather than assuming shared functions guarantee shared behavior.

**4. A join-semantics bug that hid real data.** Asking for "total sales for each store" returned only 13 rows, while a separate query confirmed 14 stores exist in the model. The generated SQL used a plain (inner) `JOIN` between `Sales` and `Store`, which silently drops any store with zero matching sales rows instead of showing it with a `$0` total — an entire store disappeared from the results with no indication anything was missing. Unlike the findings above, this isn't an ambiguous interpretation, it's a straightforward correctness bug: the answer was confidently wrong by omission.

*Fix:* added a prompt rule requiring `LEFT JOIN` with `COALESCE(..., 0)` whenever a question implies "every" or "each" entity. Verified by re-running the same question and confirming all 14 stores now appear, including the previously-hidden store shown correctly at `$0`. This pairing (a "how many X exist" question alongside a "for each X" question) is now a permanent regression check in `evaluate.py`, so this specific bug can't silently reappear unnoticed if the prompt changes later.

**Takeaway:** the failures here split into two real categories — ambiguous interpretation (findings 1-3, where the model made a reasonable-sounding but under-communicated choice) and outright correctness bugs (finding 4, where default SQL behavior silently discarded real data). Both matter, but they need different kinds of fixes: the first category is mitigated with better prompting and caveats surfaced to the user, while the second needed an explicit, testable rule and a regression check, because "the model usually gets this right" isn't good enough when the failure mode is a silently incomplete answer.

---

## Limitations & next steps

- Nested DAX logic (Part 1) can lose a step in translation — worth revisiting the prompt to ask for a step-by-step breakdown on complex measures specifically.
- Both parts currently process one `.pbix`/one export per run; no caching, so re-running re-generates (and re-pays for) output even when nothing has changed.
- Part 2's assumption-flagging is probabilistic, not guaranteed (see evaluation above) — a question involving an ambiguous concept should always be spot-checked, not trusted blindly, even when no caveat is shown.
- `evaluate.py` currently covers a small, manually-written benchmark; a larger and more systematic question set (and automated comparison against known-correct answers) would make Part 2's evaluation more rigorous.
- Potential extension: feed Part 1's generated documentation into Part 2's schema context, so the query-generation step has a plain-English description of ambiguous columns (like `Type`) up front, rather than only raw column names — this could catch issues like the region substitution before they happen, not just after.

## License

MIT — feel free to use or adapt this for your own models.