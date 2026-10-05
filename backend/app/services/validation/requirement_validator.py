"""
File: requirement_validator.py

Purpose:
    Validates how well an AI-generated form covers the user's original
    form requirement.

What this file does:
    - Extracts meaningful concepts from the user's requirement.
    - Compares those concepts with generated form questions.
    - Uses flexible phrase matching instead of relying only on exact words.
    - Calculates a requirement coverage score.
    - Reports requirements that appear to be missing.

Architecture:
    This file belongs to FormIQ's deterministic validation layer.

    It does NOT:
    - Generate forms.
    - Call Gemini directly.
    - Create Google Forms.
    - Modify the generated form.

The goal is to provide a reliable baseline that can later be combined
with AI-based semantic evaluation.
"""

import re
from typing import List

from app.schemas.form import GeneratedForm
from app.schemas.validation import ValidationIssue


# Common words that do not provide useful information when evaluating
# requirement coverage.
STOP_WORDS = {
    "create",
    "form",
    "please",
    "make",
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "should",
    "ask",
    "about",
    "want",
    "have",
    "using",
    "simple",
    "professional",
    "include",
    "including",
    "following",
    "information",
    "questions",
}


# Related words are grouped together so that conceptually similar
# wording can still be recognized.
#
# Example:
# "rate" and "rating" represent the same concept.
WORD_GROUPS = {
    "rate": {
        "rate",
        "rating",
        "rated",
        "score",
        "scoring",
    },
    "suggestion": {
        "suggestion",
        "suggestions",
        "improvement",
        "improvements",
        "recommendation",
        "recommendations",
    },
    "topic": {
        "topic",
        "topics",
        "subject",
        "subjects",
    },
    "useful": {
        "useful",
        "helpful",
        "beneficial",
        "valuable",
    },
    "department": {
        "department",
        "departments",
    },
    "faculty": {
        "faculty",
        "teacher",
        "teachers",
        "instructor",
        "instructors",
    },
    "email": {
        "email",
        "mail",
    },
    "name": {
        "name",
        "full",
    },
    "session": {
        "session",
        "workshop",
        "training",
        "program",
    },
}


def normalize_text(text: str) -> str:
    """
    Normalize text before comparison.

    Converts text to lowercase and removes unnecessary punctuation.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_keywords(text: str) -> set[str]:
    """
    Extract meaningful keywords from text.

    Very short words and common instruction words are ignored.
    """

    normalized = normalize_text(text)

    words = re.findall(
        r"\b[a-z]{3,}\b",
        normalized,
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def expand_keyword(keyword: str) -> set[str]:
    """
    Return related words for a keyword.

    If a keyword belongs to a predefined semantic group,
    all words from that group are returned.
    """

    for group in WORD_GROUPS.values():

        if keyword in group:
            return group

    return {keyword}


def keyword_matches_form(
    keyword: str,
    form_text: str,
) -> bool:
    """
    Check whether a requirement keyword or one of its related words
    appears in the generated form.
    """

    normalized_form = normalize_text(form_text)

    related_words = expand_keyword(keyword)

    return any(
        re.search(
            rf"\b{re.escape(word)}\b",
            normalized_form,
        )
        for word in related_words
    )


def calculate_keyword_coverage(
    requirement: str,
    form: GeneratedForm,
) -> tuple[int, set[str], set[str]]:
    """
    Calculate coverage using keyword/concept matching.

    Returns:
        coverage score
        matched concepts
        missing concepts
    """

    requirement_keywords = extract_keywords(
        requirement
    )

    form_text = " ".join(
        question.title
        for question in form.questions
    )

    if not requirement_keywords:
        return 100, set(), set()

    matched = set()
    missing = set()

    for keyword in requirement_keywords:

        if keyword_matches_form(
            keyword,
            form_text,
        ):
            matched.add(keyword)
        else:
            missing.add(keyword)

    coverage = round(
        len(matched)
        / len(requirement_keywords)
        * 100
    )

    coverage = min(
        coverage,
        100,
    )

    return (
        coverage,
        matched,
        missing,
    )


def validate_requirement_coverage(
    form: GeneratedForm,
    requirement: str,
) -> tuple[int, List[ValidationIssue], List[str]]:
    """
    Validate how well the generated form covers the requirement.

    The current implementation uses deterministic concept matching.

    Later this result can be combined with a dedicated Gemini
    requirement-coverage reviewer.
    """

    if not requirement.strip():

        return (
            100,
            [],
            [
                "Requirement coverage was not evaluated."
            ],
        )

    (
        coverage,
        matched,
        missing,
    ) = calculate_keyword_coverage(
        requirement,
        form,
    )

    if coverage >= 85:

        return (
            coverage,
            [],
            [
                f"Requirement coverage is {coverage}%."
            ],
        )

    if coverage >= 70:

        return (
            coverage,
            [
                ValidationIssue(
                    category="Requirement Coverage",
                    severity="WARNING",
                    message=(
                        f"Requirement coverage appears to be "
                        f"{coverage}%. Some requested concepts "
                        "may not be explicitly represented "
                        "in the form."
                    ),
                )
            ],
            [],
        )

    missing_text = ", ".join(
        sorted(missing)
    )

    return (
        coverage,
        [
            ValidationIssue(
                category="Requirement Coverage",
                severity="WARNING",
                message=(
                    f"Requirement coverage appears to be "
                    f"{coverage}%. Some requested concepts "
                    "may not be represented in the form."
                ),
                suggestion=(
                    f"Review the form for missing concepts: "
                    f"{missing_text}."
                ),
            )
        ],
        [],
    )