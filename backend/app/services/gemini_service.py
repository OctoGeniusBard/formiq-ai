import os
import json

from dotenv import load_dotenv
from google import genai

from app.schemas.form import GeneratedForm


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_form(requirement: str) -> GeneratedForm:

    prompt = f"""
You are an expert AI form designer for an application called FormIQ.

Convert the user's natural-language requirement into a structured form.

USER REQUIREMENT:
{requirement}

Return ONLY valid JSON in exactly this structure:

{{
  "title": "Form title",
  "description": "Short form description",
  "questions": [
    {{
      "title": "Question text",
      "type": "SHORT_ANSWER",
      "required": true,
      "options": null
    }}
  ]
}}

Allowed question types:

SHORT_ANSWER
PARAGRAPH
MULTIPLE_CHOICE
CHECKBOX
LINEAR_SCALE
DROPDOWN

Rules:

1. Generate only questions relevant to the user's requirement.
2. Use SHORT_ANSWER for names, departments, email, etc.
3. Use PARAGRAPH for detailed feedback.
4. Use MULTIPLE_CHOICE when one option should be selected.
5. Use CHECKBOX when multiple options can be selected.
6. Use DROPDOWN for a list where one option should be selected.
7. Use LINEAR_SCALE for ratings.
8. For LINEAR_SCALE, use options ["1", "2", "3", "4", "5"].
9. Mark important questions as required.
10. Do not invent unnecessary questions.
11. Return valid JSON only.

USER REQUEST:
{requirement}
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    raw_output = interaction.output_text

    try:
        data = json.loads(raw_output)
        return GeneratedForm.model_validate(data)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini did not return valid JSON: {e}\n"
            f"Raw response: {raw_output}"
        )

    except Exception as e:
        raise ValueError(
            f"Generated form validation failed: {e}\n"
            f"Raw response: {raw_output}"
        )