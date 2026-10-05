"""
File: quality_engine.py

Purpose:
    Provides the central FormIQ form quality and validation engine.

What this file does:
    - Runs deterministic validation checks.
    - Runs AI-based requirement coverage validation.
    - Runs Gemini semantic validation.
    - Combines all validation results.
    - Calculates the final FormIQ quality score.
    - Collects validation issues, passed checks, and strengths.

Architecture:

    GeneratedForm
          ↓
    Deterministic Validators
          ↓
    AI Requirement Coverage Review
          ↓
    Gemini Semantic Review
          ↓
    Quality Score Calculation
          ↓
    ValidationResult

This file is the main orchestration layer for form validation.

This file does NOT:
    - Generate forms.
    - Modify generated forms.
    - Create Google Forms.
    - Store validation results in the database.

Those responsibilities belong to other FormIQ services.
"""

from typing import List

from app.schemas.form import GeneratedForm

from app.schemas.validation import (
    RequirementCoverageItem,
    RequirementCoverageResult,
    ValidationIssue,
    ValidationResult,
)

from app.services.validation.gemini_reviewer import (
    review_form_semantically,
)

from app.services.validation.question_validator import (
    validate_questions,
)

from app.services.validation.duplicate_validator import (
    validate_duplicates,
)

from app.services.validation.pii_validator import (
    validate_pii,
)

from app.services.validation.requirement_validator import (
    validate_requirement_coverage,
)

from app.services.validation.requirement_coverage_reviewer import (
    review_requirement_coverage,
)


def validate_required_fields(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

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

    total = len(form.questions)

    percentage = (
        required_count / total
    ) * 100

    # Everything required can make a feedback form
    # unnecessarily restrictive.

    if percentage == 100 and total >= 5:

        return (
            90,
            [
                ValidationIssue(
                    category="Required Fields",
                    severity="WARNING",
                    message=(
                        "Every question is required. "
                        "Consider making open-ended feedback "
                        "questions optional."
                    ),
                )
            ],
            [],
        )

    passed.append(
        "Required field configuration appears reasonable."
    )

    return 100, issues, passed


def validate_form_length(
    form: GeneratedForm,
) -> tuple[int, List[ValidationIssue], List[str]]:

    count = len(form.questions)

    if count == 0:

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

    if count <= 15:

        return (
            100,
            [],
            ["Form length is appropriate."],
        )

    if count <= 25:

        return (
            80,
            [
                ValidationIssue(
                    category="Form Length",
                    severity="WARNING",
                    message=(
                        f"Form contains {count} questions. "
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
                    f"Form contains {count} questions. "
                    "The form may be too long."
                ),
            )
        ],
        [],
    )


def validate_form(
    form: GeneratedForm,
    requirement: str = "",
) -> ValidationResult:

    all_issues: List[ValidationIssue] = []
    passed_checks: List[str] = []
    strengths: List[str] = []

    # --------------------------------------------------------
    # 1. Question Validation
    # --------------------------------------------------------

    question_score, issues, passed = validate_questions(form)

    all_issues.extend(issues)
    passed_checks.extend(passed)

    # --------------------------------------------------------
    # 2. Duplicate Question Validation
    # --------------------------------------------------------

    duplicate_score, issues, passed = validate_duplicates(form)

    all_issues.extend(issues)
    passed_checks.extend(passed)

    # --------------------------------------------------------
    # 3. PII Validation
    # --------------------------------------------------------

    pii_score, issues, passed = validate_pii(form)

    all_issues.extend(issues)
    passed_checks.extend(passed)

    # --------------------------------------------------------
    # 4. Deterministic Requirement Coverage
    # --------------------------------------------------------

    requirement_score, issues, passed = (
        validate_requirement_coverage(
            form,
            requirement,
        )
    )

    all_issues.extend(issues)
    passed_checks.extend(passed)

    # --------------------------------------------------------
    # 5. AI Requirement Coverage Review
    # --------------------------------------------------------
    #
    # Gemini evaluates semantic coverage between the user's
    # original requirement and the generated form.
    #
    # Deterministic coverage = 30%
    # AI semantic coverage = 70%
    #
    # This prevents simple keyword matching from dominating
    # requirement coverage.
        
    requirement_coverage_result = None

    if requirement.strip():

        ai_requirement_review = review_requirement_coverage(
            form=form,
            requirement=requirement,
        )

        ai_requirement_score = int(
            ai_requirement_review.get(
                "coverage_score",
                requirement_score,
            )
        )

        requirement_items = []

        for item in ai_requirement_review.get(
            "requirements",
            []
        ):

            requirement_items.append(
                RequirementCoverageItem(
                    requirement=item.get(
                        "requirement",
                        "",
                    ),
                    status=item.get(
                        "status",
                        "MISSING",
                    ),
                    question=item.get(
                        "question"
                    ),
                    explanation=item.get(
                        "explanation"
                    ),
                )
            )

        requirement_coverage_result = (
            RequirementCoverageResult(
                score=ai_requirement_score,
                requirements=requirement_items,
                summary=ai_requirement_review.get(
                    "summary"
                ),
            )
        )

        ai_requirement_issues = []

        for item in ai_requirement_review.get(
            "requirements",
            []
        ):

            if item.get("status") == "MISSING":

                ai_requirement_issues.append(
                    ValidationIssue(
                        category="Requirement Coverage",
                        severity="WARNING",
                        message=(
                            "Requested requirement appears to be "
                            f"missing: {item.get('requirement')}"
                        ),
                        question=item.get("question"),
                        suggestion=item.get("explanation"),
                    )
                )

            elif item.get("status") == "PARTIALLY_COVERED":

                ai_requirement_issues.append(
                    ValidationIssue(
                        category="Requirement Coverage",
                        severity="WARNING",
                        message=(
                            "Requested requirement is only "
                            "partially covered: "
                            f"{item.get('requirement')}"
                        ),
                        question=item.get("question"),
                        suggestion=item.get("explanation"),
                    )
                )

        all_issues.extend(
            ai_requirement_issues
        )

        passed_checks.append(
            "AI requirement coverage score: "
            f"{ai_requirement_score}/100."
        )

        requirement_score = round(
            (
                requirement_score * 0.30
                + ai_requirement_score * 0.70
            )
        )

    # --------------------------------------------------------
    # 6. Required Field Validation
    # --------------------------------------------------------

    required_score, issues, passed = (
        validate_required_fields(form)
    )

    all_issues.extend(issues)
    passed_checks.extend(passed)

    # --------------------------------------------------------
    # 7. Form Length Validation
    # --------------------------------------------------------

    length_score, issues, passed = (
        validate_form_length(form)
    )

    all_issues.extend(issues)
    passed_checks.extend(passed)

    # --------------------------------------------------------
    # 8. Gemini Semantic Validation
    # --------------------------------------------------------

    semantic_result = review_form_semantically(
        form=form,
        requirement=requirement,
    )

    semantic_score = semantic_result.semantic_score

    all_issues.extend(
        semantic_result.issues
    )

    strengths.extend(
        semantic_result.strengths
    )

    passed_checks.append(
        f"Gemini semantic quality score: {semantic_score}/100."
    )

    # --------------------------------------------------------
    # 9. Question Type Score
    # --------------------------------------------------------

    # Currently question validation already evaluates
    # whether supported question types are being used.
    #
    # Later this can become a dedicated question-type
    # suitability engine.

    type_score = question_score

    # --------------------------------------------------------
    # 10. Final FormIQ Quality Score
    # --------------------------------------------------------

    overall_score = round(
        (
            requirement_score * 0.20
            + question_score * 0.10
            + type_score * 0.10
            + duplicate_score * 0.10
            + required_score * 0.10
            + length_score * 0.05
            + pii_score * 0.05
            + semantic_score * 0.30
        )
    )

    # --------------------------------------------------------
    # 11. Final Structured Validation Result
    # --------------------------------------------------------

    return ValidationResult(
        overall_score=overall_score,

        requirement_coverage_score=requirement_score,

        requirement_coverage=requirement_coverage_result,

        question_quality_score=question_score,

        question_type_score=type_score,

        duplicate_score=duplicate_score,

        required_field_score=required_score,

        form_length_score=length_score,

        pii_score=pii_score,

        semantic_score=semantic_score,

        passed_checks=passed_checks,

        issues=all_issues,

        strengths=strengths,
    )