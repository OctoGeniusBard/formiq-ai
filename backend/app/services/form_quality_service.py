import re
from typing import List

from app.schemas.form import GeneratedForm
from app.schemas.validation import (
    ValidationIssue,
    ValidationResult,
)


ALLOWED_TYPES = {
    "SHORT_ANSWER",
    "PARAGRAPH",
    "MULTIPLE_CHOICE",
    "CHECKBOX",
    "LINEAR_SCALE",
    "DROPDOWN",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def check_question_quality(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    score = 100
    issues = []
    passed = []

    for question in form.questions:

        title = question.title.strip()

        if not title:
            score -= 15

            issues.append(
                ValidationIssue(
                    category="Question Quality",
                    severity="CRITICAL",
                    message="Question title cannot be empty.",
                )
            )

        elif len(title) < 5:
            score -= 5

            issues.append(
                ValidationIssue(
                    category="Question Quality",
                    severity="WARNING",
                    message="Question text appears too short.",
                    question=title,
                )
            )

    if not issues:
        passed.append("All questions have valid question text.")

    return max(score, 0), issues, passed


def check_question_types(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    score = 100
    issues = []
    passed = []

    for question in form.questions:

        question_type = question.type.upper()

        if question_type not in ALLOWED_TYPES:

            score -= 20

            issues.append(
                ValidationIssue(
                    category="Question Type",
                    severity="CRITICAL",
                    message=f"Unsupported question type: {question.type}",
                    question=question.title,
                )
            )

        if question_type in {
            "MULTIPLE_CHOICE",
            "CHECKBOX",
            "DROPDOWN",
        }:

            if not question.options:

                score -= 10

                issues.append(
                    ValidationIssue(
                        category="Question Type",
                        severity="ERROR",
                        message=(
                            f"{question_type} question must have options."
                        ),
                        question=question.title,
                    )
                )

    if not issues:
        passed.append("All question types are valid.")

    return max(score, 0), issues, passed


def check_duplicates(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    questions = [
        normalize_text(question.title)
        for question in form.questions
    ]

    duplicates = set()

    for question in questions:
        if questions.count(question) > 1:
            duplicates.add(question)

    issues = []

    for duplicate in duplicates:

        issues.append(
            ValidationIssue(
                category="Duplicate Detection",
                severity="ERROR",
                message="Duplicate question detected.",
                question=duplicate,
            )
        )

    if duplicates:
        score = max(0, 100 - (len(duplicates) * 20))
        passed = []
    else:
        score = 100
        passed = ["No duplicate questions detected."]

    return score, issues, passed


def check_required_fields(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    score = 100
    issues = []
    passed = []

    if not form.questions:
        return (
            0,
            [
                ValidationIssue(
                    category="Required Fields",
                    severity="CRITICAL",
                    message="Form contains no questions.",
                )
            ],
            [],
        )

    required_count = sum(
        1
        for question in form.questions
        if question.required
    )

    required_percentage = (
        required_count / len(form.questions)
    ) * 100

    if required_percentage == 100 and len(form.questions) >= 5:

        score -= 10

        issues.append(
            ValidationIssue(
                category="Required Fields",
                severity="WARNING",
                message=(
                    "Every question is required. "
                    "Consider making feedback/comment questions optional."
                ),
            )
        )

    else:
        passed.append("Required fields appear reasonable.")

    return max(score, 0), issues, passed


def check_form_length(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    question_count = len(form.questions)

    if question_count == 0:

        return (
            0,
            [
                ValidationIssue(
                    category="Form Length",
                    severity="CRITICAL",
                    message="Form contains no questions.",
                )
            ],
            [],
        )

    if question_count <= 15:

        return (
            100,
            [],
            ["Form length is appropriate."],
        )

    if question_count <= 25:

        return (
            80,
            [
                ValidationIssue(
                    category="Form Length",
                    severity="WARNING",
                    message=(
                        f"Form contains {question_count} questions. "
                        "Consider reducing the form length."
                    ),
                )
            ],
            [],
        )

    return (
        60,
        [
            ValidationIssue(
                category="Form Length",
                severity="ERROR",
                message=(
                    f"Form contains {question_count} questions. "
                    "The form may be too long."
                ),
            )
        ],
        [],
    )


def check_pii(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    pii_patterns = {
        "email": r"\bemail\b",
        "phone": r"\b(phone|mobile|contact number)\b",
        "address": r"\b(address|home address)\b",
        "aadhaar": r"\b(aadhaar|aadhar)\b",
        "pan": r"\bpan number\b",
    }

    issues = []

    for question in form.questions:

        title = question.title.lower()

        for pii_type, pattern in pii_patterns.items():

            if re.search(pattern, title):

                issues.append(
                    ValidationIssue(
                        category="PII Safety",
                        severity="WARNING",
                        message=(
                            f"Potential personal information field detected: "
                            f"{pii_type}."
                        ),
                        question=question.title,
                    )
                )

                break

    if issues:

        return 90, issues, []

    return (
        100,
        [],
        ["No obvious sensitive personal information fields detected."],
    )


def calculate_requirement_coverage(
    form: GeneratedForm,
    requirement: str,
) -> tuple[int, List[ValidationIssue], List[str]]:

    requirement_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            requirement.lower(),
        )
    )

    if not requirement_words:

        return 100, [], ["Requirement coverage could not be assessed."]

    form_text = " ".join(
        question.title.lower()
        for question in form.questions
    )

    matched_words = sum(
        1
        for word in requirement_words
        if word in form_text
    )

    coverage = int(
        min(
            100,
            (matched_words / len(requirement_words)) * 100,
        )
    )

    if coverage >= 60:

        return (
            coverage,
            [],
            [f"Requirement coverage is {coverage}%."],
        )

    return (
        coverage,
        [
            ValidationIssue(
                category="Requirement Coverage",
                severity="WARNING",
                message=(
                    f"Only {coverage}% of requirement keywords "
                    "appear to be covered by the generated questions."
                ),
            )
        ],
        [],
    )


def validate_form(
    form: GeneratedForm,
    requirement: str = "",
) -> ValidationResult:

    all_issues = []
    passed_checks = []

    question_quality_score, issues, passed = check_question_quality(form)
    all_issues.extend(issues)
    passed_checks.extend(passed)

    question_type_score, issues, passed = check_question_types(form)
    all_issues.extend(issues)
    passed_checks.extend(passed)

    duplicate_score, issues, passed = check_duplicates(form)
    all_issues.extend(issues)
    passed_checks.extend(passed)

    required_field_score, issues, passed = check_required_fields(form)
    all_issues.extend(issues)
    passed_checks.extend(passed)

    form_length_score, issues, passed = check_form_length(form)
    all_issues.extend(issues)
    passed_checks.extend(passed)

    pii_score, issues, passed = check_pii(form)
    all_issues.extend(issues)
    passed_checks.extend(passed)

    requirement_coverage_score, issues, passed = (
        calculate_requirement_coverage(
            form,
            requirement,
        )
    )

    all_issues.extend(issues)
    passed_checks.extend(passed)

    overall_score = round(
        (
            requirement_coverage_score
            + question_quality_score
            + question_type_score
            + duplicate_score
            + required_field_score
            + form_length_score
            + pii_score
        ) / 7
    )

    return ValidationResult(
        overall_score=overall_score,
        requirement_coverage_score=requirement_coverage_score,
        question_quality_score=question_quality_score,
        question_type_score=question_type_score,
        duplicate_score=duplicate_score,
        required_field_score=required_field_score,
        form_length_score=form_length_score,
        pii_score=pii_score,
        passed_checks=passed_checks,
        issues=all_issues,
    )