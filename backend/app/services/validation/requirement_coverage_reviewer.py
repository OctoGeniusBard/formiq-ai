"""
File: requirement_coverage_reviewer.py

Purpose:
    Uses Gemini to evaluate how completely a generated FormIQ form
    satisfies the user's original requirement.

What this file does:
    - Breaks the user's requirement into meaningful requirements.
    - Maps each requirement to one or more generated questions.
    - Determines whether each requirement is COVERED, PARTIALLY_COVERED,
      or MISSING.
    - Calculates a semantic requirement coverage score.
    - Provides explanations for the coverage decision.

Why this is needed:
    Simple keyword matching cannot reliably understand that phrases such as:

        "overall session rating from 1 to 5"

    and:

        "How would you rate the overall session?"

    represent the same requirement.

Architecture:

    User Requirement
           ↓
    Generated Form
           ↓
    Gemini Requirement Coverage Reviewer
           ↓
    Requirement-to-Question Mapping
           ↓
    Coverage Score
           ↓
    Form Quality Engine

This service only evaluates requirement coverage.
It does not modify the form or create Google Forms.
"""

import json
import re

from dotenv import load_dotenv
from google import genai

from app.schemas.form import GeneratedForm


load_dotenv()


def get_gemini_client():
    """
    Create the Gemini client using the FormIQ API key.
    """

    import os

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in .env"
        )

    return genai.Client(
        api_key=api_key
    )


def clean_json_response(
    raw_output: str,
) -> str:
    """
    Remove Markdown code fences if Gemini returns JSON
    wrapped inside ```json ... ```.

    This makes JSON parsing more robust.
    """

    if not raw_output:
        raise ValueError(
            "Gemini returned an empty requirement coverage response."
        )

    cleaned = raw_output.strip()

    cleaned = re.sub(
        r"^```json\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"^```\s*",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return cleaned.strip()


def review_requirement_coverage(
    form: GeneratedForm,
    requirement: str,
) -> dict:
    """
    Evaluate semantic coverage between the user's requirement
    and the generated form.

    Returns a dictionary containing:

        coverage_score
        requirements
        summary
    """

    client = get_gemini_client()

    questions = []

    for index, question in enumerate(
        form.questions,
        start=1,
    ):
        questions.append(
            {
                "number": index,
                "title": question.title,
                "type": question.type,
                "required": question.required,
                "options": question.options,
            }
        )

    prompt = f"""
You are a senior requirements analyst and survey-design expert.

You are evaluating whether an AI-generated form completely satisfies
the user's original form requirement.

USER REQUIREMENT:
{requirement}

GENERATED FORM:
{json.dumps(questions, indent=2)}

Your task:

1. Identify the distinct information requirements in the user's request.

2. Map each requirement to the generated question that satisfies it.

3. Classify every requirement as exactly one of:

   COVERED
   PARTIALLY_COVERED
   MISSING

4. Consider semantic meaning, not exact word matching.

For example:

Requirement:
"overall session rating from 1 to 5"

Question:
"Overall Session Rating"

This should be considered COVERED if the question uses a 1–5
linear scale.

Another example:

Requirement:
"topics they found useful"

Question:
"Topics You Found Most Useful"

This is COVERED.

Do not penalize the form merely because the wording differs.

Do not invent requirements that were not requested.

Do not require additional questions simply because they might
be useful.

Only evaluate whether the generated form satisfies the user's
actual request.

SCORING:

COVERED = full credit
PARTIALLY_COVERED = partial credit
MISSING = zero credit

Calculate an overall coverage score from 0 to 100.

OUTPUT REQUIREMENTS:

Return ONLY valid JSON.

Do NOT use Markdown.
Do NOT wrap the JSON in ```json.
Do NOT add explanations outside the JSON.

Use exactly this structure:

{{
    "coverage_score": 100,
    "requirements": [
        {{
            "requirement": "Faculty name",
            "status": "COVERED",
            "question": "Faculty Name",
            "explanation": "The form contains a required faculty name field."
        }}
    ],
    "summary": "All requested information is covered by the generated form."
}}
"""

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    raw_output = response.output_text

    cleaned_output = clean_json_response(
        raw_output
    )

    try:

        return json.loads(
            cleaned_output
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            "Gemini requirement coverage reviewer "
            f"returned invalid JSON: {e}\n"
            f"Cleaned response: {cleaned_output}"
        )