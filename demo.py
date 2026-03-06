"""
Demo script for the custom text analysis tool.

This script simulates how an AI agent might call the tool in two scenarios:

1. Successful execution with a realistic business/news style text.
2. Error handling when invalid input is provided.

Run this file directly:

    python demo.py
"""

from __future__ import annotations

from pprint import pprint

from tool import text_analysis_tool


def demo_success() -> None:
    """Demonstrate a successful call to the text analysis tool."""
    print("=== Successful analysis ===")
    sample_text = (
        "Our quarterly earnings report shows strong growth in subscription "
        "revenue, driven by increased customer retention and expanded sales "
        "in North America. However, macroeconomic uncertainty continues to "
        "impact advertising budgets in key markets."
    )

    result = text_analysis_tool.execute(
        text=sample_text,
        max_keywords=5,
        max_keyphrases=5,
        max_phrase_words=3,
    )
    pprint(result)
    print()


def demo_error() -> None:
    """
    Demonstrate how the tool responds to invalid input.

    In this example we intentionally pass an empty string to trigger
    input validation and a structured error response.
    """
    print("=== Error handling example ===")
    result = text_analysis_tool.execute(text="   ", max_keywords=5)
    pprint(result)
    print()


def main() -> None:
    demo_success()
    demo_error()


if __name__ == "__main__":
    main()

