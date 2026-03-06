## Text Analysis Tool – Mini-Assignment 2

### What the tool does

The custom tool is a **lightweight text analysis utility** designed for business and news-style text.  
Given a text input, it returns:

- **Basic statistics**: character count, word count, sentence count.
- **Structure metrics**: average words per sentence.
- **Reading time estimate**: approximate minutes to read (200 words per minute).
- **Keyword + keyphrase extraction**:
  - Top single-word keywords by frequency (excluding stopwords)
  - Top multi-word keyphrases using a lightweight **RAKE-style** heuristic

It is implemented as a function (`analyze_text`) plus a small `Tool` wrapper that an AI agent can call with keyword arguments. Results and errors are **JSON-serializable dicts**, suitable for tool/function-calling setups.

### How to run the demo

1. Ensure you are in the assignment directory:
   ```bash
   cd /Users/saahilalam/Documents/IIMT3688/Assignment2-ToolDesign
   ```

2. (Optional) Create and activate a virtual environment (no external packages are required, only the Python standard library):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Run the demo script:
   ```bash
   python demo.py
   ```

4. You should see:
   - A **successful analysis** of a sample business-style paragraph.
   - An **error handling example** where an empty string triggers a structured validation error.

### Design decisions

- **Scope and purpose**: Focused on **quick, interpretable text statistics** useful in business/news analysis, rather than heavy NLP – this keeps the tool easy to understand and deterministic.
- **Input/parameter schema**:
  - `text` (str, required): non-empty input text.
  - `max_keywords` (int, optional, default 5): 1–50, controls how many keywords are returned.
  - `max_keyphrases` (int | None, optional, default None): 1–50; if None, uses `max_keywords`.
  - `max_phrase_words` (int, optional, default 3): 2–6; controls max length of returned phrases.
- **Output schema**: A `TextAnalysisResult` dict with `ok`, `error`, counts, averages, reading time, plus:
  - `top_keywords`: list of keyword dicts (`word`, `count`, `relative_frequency`)
  - `top_keyphrases`: list of keyphrase dicts (`phrase`, `score`, `count`)
- **Error handling**:
  - Validation lives in `AnalyzeTextParams.validate()`.
  - Errors are returned as a **structured `error` object** with `code`, `message`, and `details`, while `ok` is set to `False`.
  - The wrapper `Tool.execute()` also catches unexpected exceptions and converts them into `INTERNAL_ERROR` results.
- **Heuristic algorithms**:
  - Sentences are split with a simple regex on `.?!`.
  - Words are alphabetic tokens; a small stopword list removes high-frequency function words before keyword ranking.
  - Keyphrases are extracted using a lightweight RAKE-style approach (stopword splitting + n-grams + degree/frequency scoring).
  - Reading time is a simple function of word count (200 wpm).

### Limitations

- **Language/locale**: Optimised for English and may behave poorly on other languages or very informal text.
- **Naive sentence/word segmentation**: Does not handle complex punctuation, abbreviations, or multi-sentence structures perfectly.
- **Heuristic keywords/keyphrases**: Still heuristic; does not perform true entity recognition, lemmatization, or domain-specific term weighting.
- **Prompt log**: `prompt-log.md` is provided as a file; you should paste your **full chat history with the AI** into it before submission to satisfy the assignment requirement.

