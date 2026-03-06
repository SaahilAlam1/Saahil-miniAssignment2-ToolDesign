from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict
import re


class TextAnalysisError(TypedDict):
    """Structured error information returned by the text analysis tool."""

    code: str
    message: str
    details: Dict[str, Any]


class TextAnalysisResult(TypedDict):
    """Structured result returned by the text analysis tool."""

    ok: bool
    error: Optional[TextAnalysisError]
    num_chars: int
    num_words: int
    num_sentences: int
    avg_words_per_sentence: float
    reading_time_minutes: float
    top_keywords: List[Dict[str, Any]]
    top_keyphrases: List[Dict[str, Any]]


@dataclass
class AnalyzeTextParams:
    """
    Parameters for the `analyze_text` tool function.

    Attributes:
        text: The input text to analyze. Must be a non-empty string.
        max_keywords: Maximum number of keywords to return, based on simple
            frequency analysis. Must be between 1 and 50 (inclusive).
        max_keyphrases: Maximum number of keyphrases to return, using a RAKE-style
            heuristic. If None, defaults to `max_keywords`. Must be between 1 and
            50 (inclusive) when provided.
        max_phrase_words: Maximum words per returned keyphrase (2 to 6 inclusive).
    """

    text: str
    max_keywords: int = 5
    max_keyphrases: Optional[int] = None
    max_phrase_words: int = 3

    def validate(self) -> Optional[TextAnalysisError]:
        """
        Validate the parameters and return a structured error if invalid.

        Returns:
            A `TextAnalysisError` dict if validation fails, otherwise `None`.
        """
        if not isinstance(self.text, str):
            return TextAnalysisError(
                code="INVALID_TYPE",
                message="Parameter 'text' must be a string.",
                details={"received_type": type(self.text).__name__},
            )

        stripped = self.text.strip()
        if not stripped:
            return TextAnalysisError(
                code="EMPTY_TEXT",
                message="Parameter 'text' must be a non-empty string.",
                details={},
            )

        if not isinstance(self.max_keywords, int):
            return TextAnalysisError(
                code="INVALID_TYPE",
                message="Parameter 'max_keywords' must be an integer.",
                details={"received_type": type(self.max_keywords).__name__},
            )

        if not (1 <= self.max_keywords <= 50):
            return TextAnalysisError(
                code="OUT_OF_RANGE",
                message="Parameter 'max_keywords' must be between 1 and 50.",
                details={"received_value": self.max_keywords},
            )

        if self.max_keyphrases is not None:
            if not isinstance(self.max_keyphrases, int):
                return TextAnalysisError(
                    code="INVALID_TYPE",
                    message="Parameter 'max_keyphrases' must be an integer or None.",
                    details={"received_type": type(self.max_keyphrases).__name__},
                )
            if not (1 <= self.max_keyphrases <= 50):
                return TextAnalysisError(
                    code="OUT_OF_RANGE",
                    message="Parameter 'max_keyphrases' must be between 1 and 50.",
                    details={"received_value": self.max_keyphrases},
                )

        if not isinstance(self.max_phrase_words, int):
            return TextAnalysisError(
                code="INVALID_TYPE",
                message="Parameter 'max_phrase_words' must be an integer.",
                details={"received_type": type(self.max_phrase_words).__name__},
            )
        if not (2 <= self.max_phrase_words <= 6):
            return TextAnalysisError(
                code="OUT_OF_RANGE",
                message="Parameter 'max_phrase_words' must be between 2 and 6.",
                details={"received_value": self.max_phrase_words},
            )

        return None


def _split_sentences(text: str) -> List[str]:
    """
    Heuristically split text into sentences.

    This is a deliberately simple splitter suitable for business/news text.
    It is not intended to be linguistically perfect.
    """
    # Split on ., ?, ! followed by whitespace or end of string.
    raw_sentences = re.split(r"[.!?]+(?:\s+|$)", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences


def _tokenize_words(text: str) -> List[str]:
    """
    Tokenize text into lowercase word tokens using a simple regex.

    Only alphabetic sequences are considered words. Numbers and punctuation
    are ignored for keyword statistics.
    """
    return re.findall(r"[A-Za-z]+", text.lower())


_STOP_WORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "will",
    "would",
    "could",
    "should",
    "about",
    "into",
    "over",
    "under",
    "after",
    "before",
    "while",
    "where",
    "when",
    "what",
    "which",
    "who",
    "whom",
    "why",
    "how",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "a",
    "an",
    "in",
    "on",
    "at",
    "by",
    "of",
    "to",
    "as",
    "it",
    "its",
    "we",
    "our",
    "you",
    "your",
    "they",
    "their",
}


def _compute_keywords(
    words: List[str], max_keywords: int
) -> List[Dict[str, Any]]:
    """
    Compute simple keyword frequencies, excluding common stop words.
    """
    freq: Dict[str, int] = {}
    for w in words:
        if w in _STOP_WORDS:
            continue
        freq[w] = freq.get(w, 0) + 1

    sorted_items = sorted(
        freq.items(),
        key=lambda item: (-item[1], item[0]),
    )

    top = []
    total_keyword_tokens = sum(freq.values()) or 1
    for word, count in sorted_items[:max_keywords]:
        top.append(
            {
                "word": word,
                "count": count,
                "relative_frequency": count / total_keyword_tokens,
            }
        )
    return top


def _extract_candidate_phrases(
    text: str, *, max_phrase_words: int
) -> List[List[str]]:
    """
    Extract candidate phrases as token lists.

    Uses stopwords to split text into content-word runs, then generates
    n-grams (2..max_phrase_words) from each run. This yields multi-word
    keyphrases that are often more informative in business/news text.
    """
    # Keep only simple word-like tokens (allow basic hyphen/apostrophe usage).
    tokens = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", text.lower())

    # Split into runs of non-stopwords.
    runs: List[List[str]] = []
    current: List[str] = []
    for tok in tokens:
        if tok in _STOP_WORDS:
            if current:
                runs.append(current)
                current = []
            continue
        current.append(tok)
    if current:
        runs.append(current)

    # Generate candidate n-grams from each run (n >= 2).
    phrases: List[List[str]] = []
    for run in runs:
        run_len = len(run)
        if run_len < 2:
            continue
        max_n = min(max_phrase_words, run_len)
        for n in range(2, max_n + 1):
            for i in range(0, run_len - n + 1):
                phrases.append(run[i : i + n])
    return phrases


def _compute_keyphrases_rake(
    text: str, *, max_keyphrases: int, max_phrase_words: int
) -> List[Dict[str, Any]]:
    """
    Compute RAKE-style keyphrases (multi-word keywords).

    This is a lightweight adaptation of Rapid Automatic Keyword Extraction:
    - Candidate phrases are built from non-stopword runs and n-grams.
    - Each word receives a score based on degree and frequency.
    - Phrase score is the sum of its word scores.
    """
    candidates = _extract_candidate_phrases(text, max_phrase_words=max_phrase_words)
    if not candidates:
        return []

    word_freq: Dict[str, int] = {}
    word_degree: Dict[str, int] = {}
    phrase_counts: Dict[str, int] = {}

    for phrase_tokens in candidates:
        phrase_str = " ".join(phrase_tokens)
        phrase_counts[phrase_str] = phrase_counts.get(phrase_str, 0) + 1

        degree_increment = len(phrase_tokens) - 1
        for w in phrase_tokens:
            word_freq[w] = word_freq.get(w, 0) + 1
            word_degree[w] = word_degree.get(w, 0) + degree_increment

    word_score: Dict[str, float] = {}
    for w, freq in word_freq.items():
        degree = word_degree.get(w, 0)
        # Common RAKE variant: (degree + freq) / freq.
        word_score[w] = (degree + freq) / float(freq)

    phrase_score: Dict[str, float] = {}
    for phrase_tokens in candidates:
        phrase_str = " ".join(phrase_tokens)
        if phrase_str in phrase_score:
            continue
        phrase_score[phrase_str] = sum(word_score.get(w, 0.0) for w in phrase_tokens)

    ranked = sorted(
        phrase_score.items(),
        key=lambda item: (-item[1], -phrase_counts.get(item[0], 0), item[0]),
    )

    top: List[Dict[str, Any]] = []
    for phrase, score in ranked[:max_keyphrases]:
        top.append(
            {
                "phrase": phrase,
                "score": score,
                "count": phrase_counts.get(phrase, 0),
            }
        )
    return top


def analyze_text(params: AnalyzeTextParams) -> TextAnalysisResult:
    """
    Analyze a piece of business/news/text content and return summary statistics.

    This function is intended to be used as a custom "tool" by an AI agent
    for quick, heuristic analysis of textual inputs. It returns only
    JSON-serializable data structures so it can be used directly in
    function-calling / tool-calling setups.

    Args:
        params: An `AnalyzeTextParams` instance containing the text to analyze
            and configuration options.

    Returns:
        A `TextAnalysisResult` dictionary with:
            - ok: Whether the analysis succeeded.
            - error: Structured error information if `ok` is False, otherwise None.
            - num_chars: Total number of characters in the input text.
            - num_words: Total number of word tokens.
            - num_sentences: Number of heuristic sentences.
            - avg_words_per_sentence: Average words per sentence (0.0 if no sentences).
            - reading_time_minutes: Approximate reading time assuming
              200 words per minute.
            - top_keywords: A list of keyword dictionaries with `word`, `count`,
              and `relative_frequency` fields.
            - top_keyphrases: A list of keyphrase dictionaries with `phrase`,
              `score`, and `count` fields (RAKE-style multi-word extraction).
    """
    validation_error = params.validate()
    if validation_error is not None:
        # For invalid input, return a result with ok=False and minimal fields.
        return TextAnalysisResult(
            ok=False,
            error=validation_error,
            num_chars=0,
            num_words=0,
            num_sentences=0,
            avg_words_per_sentence=0.0,
            reading_time_minutes=0.0,
            top_keywords=[],
            top_keyphrases=[],
        )

    text = params.text.strip()
    sentences = _split_sentences(text)
    words = _tokenize_words(text)

    num_chars = len(text)
    num_words = len(words)
    num_sentences = len(sentences)
    avg_words_per_sentence = (
        float(num_words) / num_sentences if num_sentences > 0 else 0.0
    )
    reading_time_minutes = num_words / 200.0 if num_words > 0 else 0.0

    top_keywords = _compute_keywords(words, params.max_keywords)
    max_keyphrases = params.max_keyphrases or params.max_keywords
    top_keyphrases = _compute_keyphrases_rake(
        text,
        max_keyphrases=max_keyphrases,
        max_phrase_words=params.max_phrase_words,
    )

    return TextAnalysisResult(
        ok=True,
        error=None,
        num_chars=num_chars,
        num_words=num_words,
        num_sentences=num_sentences,
        avg_words_per_sentence=avg_words_per_sentence,
        reading_time_minutes=reading_time_minutes,
        top_keywords=top_keywords,
        top_keyphrases=top_keyphrases,
    )


class Tool:
    """
    Simple wrapper class representing a callable tool for an AI agent.

    This mirrors the suggested structure in the assignment and can be
    instantiated by an agent or workflow manager.
    """

    def __init__(self, name: str, description: str, fn):
        self.name = name
        self.description = description
        self.fn = fn

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the wrapped function, converting kwargs into `AnalyzeTextParams`.

        This method performs basic error handling and always returns a
        JSON-serializable dictionary. Unexpected exceptions are caught and
        wrapped in a structured error response.
        """
        try:
            params = AnalyzeTextParams(**kwargs)
        except TypeError as exc:
            # Handle missing or unexpected arguments.
            return TextAnalysisResult(
                ok=False,
                error=TextAnalysisError(
                    code="INVALID_PARAMETERS",
                    message=str(exc),
                    details={"received_kwargs": kwargs},
                ),
                num_chars=0,
                num_words=0,
                num_sentences=0,
                avg_words_per_sentence=0.0,
                reading_time_minutes=0.0,
                top_keywords=[],
                top_keyphrases=[],
            )

        try:
            return analyze_text(params)
        except Exception as exc:  # pragma: no cover - defensive programming
            return TextAnalysisResult(
                ok=False,
                error=TextAnalysisError(
                    code="INTERNAL_ERROR",
                    message="Unexpected error while analyzing text.",
                    details={"exception_type": type(exc).__name__},
                ),
                num_chars=0,
                num_words=0,
                num_sentences=0,
                avg_words_per_sentence=0.0,
                reading_time_minutes=0.0,
                top_keywords=[],
                top_keyphrases=[],
            )


# Default instance that an agent could import and use directly.
text_analysis_tool = Tool(
    name="analyze_text",
    description=(
        "Analyze business/news text and return summary statistics including "
        "word counts, sentence counts, approximate reading time, and simple "
        "keyword frequencies and RAKE-style keyphrases."
    ),
    fn=analyze_text,
)

