from typing import List

from app.schemas.form import GeneratedForm
from app.schemas.validation import ValidationIssue


def normalize(text: str) -> str:

    return " ".join(
        text.lower().strip().split()
    )


def calculate_similarity(
    first: str,
    second: str,
) -> float:

    first_words = set(normalize(first).split())
    second_words = set(normalize(second).split())

    if not first_words or not second_words:
        return 0.0

    intersection = first_words.intersection(second_words)
    union = first_words.union(second_words)

    return len(intersection) / len(union)


def validate_duplicates(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    issues: List[ValidationIssue] = []
    passed: List[str] = []

    questions = form.questions

    for i in range(len(questions)):

        for j in range(i + 1, len(questions)):

            first = questions[i].title
            second = questions[j].title

            similarity = calculate_similarity(
                first,
                second,
            )

            # Exact duplicate
            if normalize(first) == normalize(second):

                issues.append(
                    ValidationIssue(
                        category="Duplicate Detection",
                        severity="ERROR",
                        message="Duplicate question detected.",
                        question=first,
                    )
                )

            # Near duplicate
            elif similarity >= 0.70:

                issues.append(
                    ValidationIssue(
                        category="Duplicate Detection",
                        severity="WARNING",
                        message=(
                            "Question may be very similar to another "
                            "question."
                        ),
                        question=(
                            f"{first} | Similar to: {second}"
                        ),
                    )
                )

    if not issues:

        passed.append(
            "No duplicate or highly similar questions detected."
        )

    if any(
        issue.severity == "ERROR"
        for issue in issues
    ):

        score = 60

    elif issues:

        score = 85

    else:

        score = 100

    return score, issues, passed