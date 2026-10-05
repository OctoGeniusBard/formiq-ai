"""
File: api.py

Purpose:
    Defines Pydantic request and response schemas for FormIQ's REST API.

What this file does:
    - Defines request bodies received by FastAPI endpoints.
    - Defines structured responses returned by FastAPI.
    - Provides a clear API contract between the React frontend
      and the FormIQ backend.

Architecture:

    React Frontend
          ↓
       FastAPI
          ↓
       API Schemas
          ↓
       FormIQ Services

Why this file exists:
    Keeping API schemas separate from business/domain schemas makes
    the backend easier to maintain and allows the frontend and backend
    to communicate using predictable response structures.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.schemas.form import GeneratedForm
from app.schemas.validation import ValidationResult


# ============================================================
# REQUEST SCHEMAS
# ============================================================


class FormRequest(BaseModel):
    """
    Request used when generating a form from a natural-language
    requirement.
    """

    requirement: str


class FormValidationRequest(BaseModel):
    """
    Request used to validate an existing generated form.
    """

    form: GeneratedForm
    requirement: str = ""


class GenerateAndValidateRequest(BaseModel):
    """
    Request used to generate a form and immediately validate it.
    """

    requirement: str


class ApproveFormRequest(BaseModel):
    """
    Request used to approve a reviewed form.

    The form is revalidated before approval.
    """

    form: GeneratedForm
    requirement: str = ""


# ============================================================
# COMMON RESPONSE SCHEMAS
# ============================================================


class GoogleFormResponse(BaseModel):
    """
    Information returned after a Google Form is created.
    """

    form_id: Optional[str] = None
    responder_uri: Optional[str] = None


# ============================================================
# FORM GENERATION RESPONSES
# ============================================================


class FormGenerationResponse(BaseModel):
    """
    Response returned after successful form generation.
    """

    success: bool
    form: GeneratedForm


class FormValidationResponse(BaseModel):
    """
    Response returned after validating an existing form.
    """

    success: bool
    validation: ValidationResult


class GenerateAndValidateResponse(BaseModel):
    """
    Response returned when FormIQ generates and validates
    a form in one operation.
    """

    success: bool
    status: str
    form: GeneratedForm
    validation: ValidationResult


# ============================================================
# APPROVAL RESPONSES
# ============================================================


class ApprovalResponse(BaseModel):
    """
    Response returned after a form goes through the approval
    process.
    """

    success: bool
    status: str
    message: str
    form: Optional[GeneratedForm] = None
    validation: ValidationResult


class PublishResponse(BaseModel):
    """
    Response returned after an approved form is published
    to Google Forms.
    """

    success: bool
    status: str
    message: str
    form: GeneratedForm
    validation: ValidationResult
    google_form: GoogleFormResponse


class SimpleMessageResponse(BaseModel):
    """
    Generic response for simple API operations.
    """

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None