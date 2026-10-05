"""
File: validation.py

Purpose:
    Defines Pydantic schemas for FormIQ's form validation system.

What this file does:
    - Represents individual validation issues.
    - Represents Gemini semantic validation results.
    - Represents the complete FormIQ quality report.

The validation report combines:
    - Deterministic rule-based validation.
    - Gemini semantic validation.
    - Requirement coverage.
    - PII checks.
    - Duplicate detection.
    - Question quality checks.
    - Form length checks.

This file contains schemas only.
It does not execute validation logic.
"""

from typing import List, Optional
from pydantic import BaseModel


class ValidationIssue(BaseModel):
    """
    Represents one problem detected during form validation.
    """

    category: str
    severity: str
    message: str
    question: Optional[str] = None
    suggestion: Optional[str] = None


class SemanticValidationResult(BaseModel):
    """
    Represents the result returned by Gemini's semantic reviewer.
    """

    semantic_score: int
    issues: List[ValidationIssue]
    strengths: List[str]


class RequirementCoverageItem(BaseModel):
    """
    Represents how one user requirement is covered by the generated form.

    This schema is used to explain the AI requirement coverage score
    by mapping individual requirements to generated questions.

    Status values:
        COVERED
        PARTIALLY_COVERED
        MISSING
    """

    requirement: str
    status: str
    question: Optional[str] = None
    explanation: Optional[str] = None


class RequirementCoverageResult(BaseModel):
    """
    Represents the complete AI requirement coverage evaluation.

    This schema contains:
        - Overall semantic coverage score.
        - Requirement-by-requirement coverage mapping.
        - AI-generated summary.

    It allows the React frontend to explain why a form received
    its requirement coverage score.
    """

    score: int
    requirements: List[RequirementCoverageItem]
    summary: Optional[str] = None

class ValidationResult(BaseModel):
    """
    Represents the complete FormIQ form quality report.

    This is the final validation result returned by the API.

    It combines:
        - Deterministic validation.
        - AI requirement coverage.
        - Gemini semantic validation.
        - Quality scoring.
        - Validation issues.
        - Explainable requirement mapping.
    """

    overall_score: int

    requirement_coverage_score: int

    requirement_coverage: Optional[
        RequirementCoverageResult
    ] = None

    question_quality_score: int

    question_type_score: int

    duplicate_score: int

    required_field_score: int

    form_length_score: int

    pii_score: int

    semantic_score: int

    passed_checks: List[str]

    issues: List[ValidationIssue]

    strengths: List[str]