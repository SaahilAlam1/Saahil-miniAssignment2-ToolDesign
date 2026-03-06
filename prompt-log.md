## Initial Prompt
Design and implement one custom tool for an AI agent, demonstrating understanding of tool architecture and integration.
Requirements
1. Tool Design (40%)
Design a custom tool that: - Has a clear, specific purpose - Is useful for business/news/text analysis - Includes proper documentation (docstring) - Has a
clear parameter schema (inputs/outputs)
Example tool ideas: - Keyword extractor - Date parser/normalizer - URL
validator - Text statistics (word count, readability) - Simple sentiment scorer
(heuristic)
2. Implementation (40%)
Implement your tool with: - Clear function signature with type hints - Comprehensive docstring - Input validation - Error handling (return structured errors or
raise and catch in wrapper) - Meaningful return value (prefer JSON-serializable
dict)
3. Integration Demo (20%)
Create a demo showing: - Tool being called by an agent/workflow - Successful
execution - Error handling (bad input)
Suggested Structure
You may implement a simple wrapper class:
class Tool:
def __init__(self, name: str, description: str, fn):
self.name = name
self.description = description
self.fn = fn
def execute(self, **kwargs):
return self.fn(**kwargs)

## AI Response 
I'll first design a simple, useful text-analysis tool, then implement tool.py, a small agent-style demo.py, and a concise README.md and prompt-log.md scaffold, making sure error handling and integration are clear. Then I'll briefly summarize how everything fits your rubric so you can run and adapt it.
•  Design a clear, well-scoped text analysis tool with parameters and outputs
•  Implement the tool with type hints, validation, and error handling in tool.py
•  Implement an integration demo script in demo.py
•  Write README.md documenting the tool, how to run demo, and design decisions
•  Create prompt-log.md scaffold for including full chat history
tool.py
+326
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, TypedDict
I’ve implemented the core tool.py with a text analysis tool and will now add a demo script, README, and prompt-log scaffold. Then I’ll give you a quick overview of how to run and adapt everything.
demo.py
+57
"""
Demo script for the custom text analysis tool.
This script simulates how an AI agent might call the tool in two scenarios:
README.md
+60
prompt-log.md
+13
Paste your **complete chat history with the AI** for Mini-Assignment 2 into this file.
What I’ve set up for you
•	tool.py
•	Implements a text analysis tool for business/news-style text.
•	Core components:
•	AnalyzeTextParams dataclass with validation (text: str, max_keywords: int = 5).
•	analyze_text(params: AnalyzeTextParams) -> TextAnalysisResult:
•	Returns a JSON-serializable dict with:
•	ok, error
•	num_chars, num_words, num_sentences
•	avg_words_per_sentence
•	reading_time_minutes (assuming 200 wpm)
•	top_keywords (list of {word, count, relative_frequency})
•	Uses simple regex-based sentence splitting and word tokenization.
•	Frequency-based keyword extraction ignoring a small English stopword list.
•	Tool wrapper class with execute(**kwargs):
•	Builds AnalyzeTextParams from kwargs.
•	Returns structured validation errors (INVALID_PARAMETERS, EMPTY_TEXT, etc.).
•	Catches unexpected exceptions and wraps them as INTERNAL_ERROR.
•	text_analysis_tool instance:
•	Name: "analyze_text"
•	Description: explains purpose for an AI agent.
•	demo.py
•	Simulates an agent calling the tool:
•	demo_success():
•	Calls text_analysis_tool.execute(text=sample_text, max_keywords=5) with a realistic business paragraph.
•	Prints the structured result (using pprint).
•	demo_error():
•	Calls text_analysis_tool.execute(text=" ", max_keywords=5) to trigger the empty-text validation.
•	Shows the structured error response.
•	main() runs both; guarded by if __name__ == "__main__": main().
•	README.md
•	Explains:
•	What the tool does (statistics, structure metrics, reading time, keywords).
•	How to run the demo (including optional venv).
•	Design decisions (schema, error handling, heuristics).
•	Limitations (English-only focus, naive tokenization, heuristic keywords).
•	This directly supports your grading rubric’s design + documentation sections.
•	prompt-log.md
•	Scaffold file with instructions:
•	You should paste your full chat history with the AI into this file before submitting.
•	This will satisfy the “prompt-log” requirement in the rubric.
How to run and what to submit
•	Run the demo:
cd /Users/saahilalam/Documents/IIMT3688/Assignment2-ToolDesign
python demo.py
You should see:
•	A “Successful analysis” output with a populated result dict.
•	An “Error handling example” output with ok: False and a structured error.
•	Submission checklist (zip contents):
•	tool.py
•	demo.py
•	README.md
•	prompt-log.md (after you paste in the complete chat)
•	(Optional) requirements.txt – not strictly needed because only stdlib is used.
If you’d like, I can next:
•	Adjust the tool to a slightly different idea (e.g., sentiment heuristic, date parser) while keeping this structure, or
•	Add inline comments in the code explaining how it maps to the rubric, for easier grading.
does my script use any AI API calls
can you add more sophisticated kekyword extraction
No — your current tool.py/demo.py don’t call any AI APIs (no OpenAI/Claude/etc, no HTTP requests). It’s all local Python (standard library only). Next I’ll upgrade the keyword extraction to a more sophisticated keyphrase-based approach (RAKE-style) while keeping your demo and README in sync.
I’ve confirmed your current keyword extraction is simple single-word frequency. Next I’ll upgrade it to produce higher-quality multi-word keyphrases (RAKE-style) while keeping the existing top_keywords output for backward compatibility, then I’ll rerun the demo to show both success and error cases still work.
tool.py
+143-2
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, asdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict
demo.py
+6-1
    result = text_analysis_tool.execute(text=sample_text, max_keywords=5)
    result = text_analysis_tool.execute(text=sample_text, max_keywords=5)
    result = text_analysis_tool.execute(
        text=sample_text,
        max_keywords=5,
README.md
+10-3
- **Reading time estimate**: approximate minutes to read (200 words per minute).
- **Simple keyword extraction**: most frequent non-stopwords with counts and relative frequencies.
- **Simple keyword extraction**: most frequent non-stopwords with counts and relative frequencies.
- **Reading time estimate**: approximate minutes to read (200 words per minute).
- **Keyword + keyphrase extraction**:
  - Top single-word keywords by frequency (excluding stopwords)
  - Top multi-word keyphrases using a lightweight **RAKE-style** heuristic
Now I’ll quickly run the demo to confirm the upgraded keyphrase extraction works and that the error path still returns a structured response.
python /Users/saahilalam/Documents/IIMT3688/Assignment2-ToolDesign/demo.py
 'reading_time_minutes': 0.0,
 'top_keyphrases': [],
 'top_keywords': []}

## Second Prompt
does my script use any AI API calls

## AI Response
AI API calls?
No. Your scripts (tool.py, demo.py) do not make any AI API calls (no OpenAI/Anthropic SDK usage, no HTTP/network calls). They run entirely locally using Python’s standard library.

## Third Prompt
can you add more sophisticated kekyword extraction

## AI Response
Upgraded “more sophisticated” keyword extraction
Yes — I added RAKE-style multi-word keyphrase extraction in tool.py.
•	New output field: top_keyphrases (list of {phrase, score, count})
•	Still keeps: top_keywords (single-word frequency keywords) for backward compatibility
•	New optional parameters (all validated):
•	max_keyphrases: int | None = None (defaults to max_keywords)
•	max_phrase_words: int = 3 (2–6)
Verified
Running python demo.py now prints:
•	A successful result including both top_keywords and top_keyphrases
•	An error case (empty text) returning ok: False with a structured error object
If you want the keyphrases to look more “human” (e.g., avoid crossing sentence boundaries or reduce phrases like “america however macroeconomic”), I can tighten the candidate-phrase splitting to respect sentence breaks and punctuation more aggressively.
Fix docstring in analyze_text, it doesn't mention the top_keyphrases return value:


tool.py
+2
              and `relative_frequency` fields.
    """
              and `relative_frequency` fields.
            - top_keyphrases: A list of keyphrase dictionaries with `phrase`,
              `score`, and `count` fields (RAKE-style multi-word extraction).
    """
Updated the analyze_text docstring so the Returns section also documents top_keyphrases: a list of keyphrase dicts with phrase, score, and count (RAKE-style multi-word extraction).

