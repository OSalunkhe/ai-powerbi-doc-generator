# AI-Powered Power BI Documentation Generator

Automatically generates plain-English documentation for every DAX measure in a Power BI model, using the Claude API. Point it at a `.pbix` file and get back a readable Markdown doc (or an interactive web app) explaining what each measure does — no manual documentation required.

## Why

Power BI models accumulate DAX measures faster than anyone documents them. This project treats documentation as a generation problem: extract the model's structure programmatically, then use an LLM to translate each DAX expression into a description a non-technical stakeholder could actually understand.

## How it works

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

## Tech stack

| Piece | Tool |
|---|---|
| PBIX metadata extraction | [pbixray](https://github.com/Hugoberry/pbixray) |
| LLM | Claude API (`claude-haiku-4-5`) via the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) |
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

## Usage

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

<video controls src="https://github.com/user-attachments/assets/42cd77b1-f81d-4bf5-ab8b-1e16732e5b0f" title="Demo"></video>

## Evaluation

I manually reviewed a sample of the generated explanations against my own understanding of the model's DAX logic:

- For straightforward measures (single aggregations, simple `CALCULATE`/`FILTER` combinations), the generated descriptions were accurate and clearly written.
- For measures with **nested logic** — several `CALCULATE`/`FILTER` layers stacked inside one another — the explanations were still directionally correct but occasionally **omitted one intermediate step** in the calculation chain, describing the overall result without fully accounting for every filter applied along the way. The model didn't get these wrong so much as under-explain them.
- No hallucinated logic was observed — errors were omissions, not fabrications, which is a meaningfully safer failure mode for a documentation tool.

**Takeaway:** this tool is reliable as a first-pass documentation generator, especially for models with many simple-to-moderate measures, but output on deeply nested measures should be spot-checked by whoever owns the model rather than treated as final. A natural next step would be prompting the model to explicitly enumerate each nested step before summarizing, rather than jumping straight to a one-sentence description.

## Limitations & next steps

- Nested DAX logic (see Evaluation above) can lose a step in translation — worth revisiting the prompt to ask for a step-by-step breakdown on complex measures specifically.
- Currently processes one `.pbix` file per run; no caching, so re-running re-generates (and re-pays for) every measure even if unchanged.
- No automated tests yet — evaluation so far has been manual spot-checking.
- Potential extension: reuse the same metadata extraction to support natural-language querying against the model (ask a question, get a DAX query back) rather than static documentation only.

## License

MIT — feel free to use or adapt this for your own models.