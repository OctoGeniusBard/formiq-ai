from typing import List

from app.schemas.form import GeneratedForm
from app.schemas.validation import ValidationIssue


ALLOWED_TYPES = {
    "SHORT_ANSWER",
    "PARAGRAPH",
    "MULTIPLE_CHOICE",
    "CHECKBOX",
    "LINEAR_SCALE",
    "DROPDOWN",
}


def validate_questions(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    score = 100
    issues: List[ValidationIssue] = []
    passed: List[str] = []

    if not form.questions:

        return (
            0,
            [
                ValidationIssue(
                    category="Question Quality",
                    severity="CRITICAL",
                    message="Form contains no questions.",
                )
            ],
            [],
        )

    for question in form.questions:

        title = question.title.strip()
        question_type = question.type.upper()

        # Empty question
        if not title:

            score -= 20

            issues.append(
                ValidationIssue(
                    category="Question Quality",
                    severity="CRITICAL",
                    message="Question title cannot be empty.",
                )
            )

            continue

        # Very short question
        if len(title) < 5:

            score -= 5

            issues.append(
                ValidationIssue(
                    category="Question Quality",
                    severity="WARNING",
                    message="Question text appears too short.",
                    question=title,
                )
            )

        # Unsupported question type
        if question_type not in ALLOWED_TYPES:

            score -= 20

            issues.append(
                ValidationIssue(
                    category="Question Type",
                    severity="CRITICAL",
                    message=f"Unsupported question type: {question.type}",
                    question=title,
                )
            )

            continue

        # Choice questions need options
        if question_type in {
            "MULTIPLE_CHOICE",
            "CHECKBOX",
            "DROPDOWN",
        }:

            if not question.options:

                score -= 15

                issues.append(
                    ValidationIssue(
                        category="Question Type",
                        severity="ERROR",
                        message=(
                            f"{question_type} question must contain "
                            "at least one option."
                        ),
                        question=title,
                    )
                )

        # Linear scale validation
        if question_type == "LINEAR_SCALE":

            if not question.options:

                score -= 10

                issues.append(
                    ValidationIssue(
                        category="Question Type",
                        severity="ERROR",
                        message=(
                            "LINEAR_SCALE question should define "
                            "scale options."
                        ),
                        question=title,
                    )
                )

            elif len(question.options) < 2:

                score -= 10

                issues.append(
                    ValidationIssue(
                        category="Question Type",
                        severity="ERROR",
                        message=(
                            "Linear scale must contain at least "
                            "two scale values."
                        ),
                        question=title,
                    )
                )

    if not issues:

        passed.append(
            "All questions have valid text and supported types."
        )

    return max(score, 0), issues, passed