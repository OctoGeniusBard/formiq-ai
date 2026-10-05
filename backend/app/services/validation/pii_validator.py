import re
from typing import List

from app.schemas.form import GeneratedForm
from app.schemas.validation import ValidationIssue


PII_PATTERNS = {
    "email": r"\bemail\b",
    "phone": r"\b(phone|mobile|contact number)\b",
    "address": r"\b(address|home address)\b",
    "aadhaar": r"\b(aadhaar|aadhar)\b",
    "pan": r"\bpan number\b",
    "date of birth": r"\b(date of birth|dob)\b",
}


def validate_pii(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    issues: List[ValidationIssue] = []
    passed: List[str] = []

    for question in form.questions:

        title = question.title.lower()

        for pii_type, pattern in PII_PATTERNS.items():

            if re.search(pattern, title):

                issues.append(
                    ValidationIssue(
                        category="PII Safety",
                        severity="WARNING",
                        message=(
                            f"Potential personal information field "
                            f"detected: {pii_type}."
                        ),
                        question=question.title,
                    )
                )

                break

    if not issues:

        passed.append(
            "No obvious personal information fields detected."
        )

        return 100, issues, passed

    # PII is not automatically a problem.
    # We flag it for human review rather than rejecting the form.

    return 90, issues, passed