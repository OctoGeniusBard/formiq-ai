"""
File: main.py

Purpose:
    Main entry point for the FormIQ FastAPI backend.

What this file does:
    - Creates the FastAPI application.
    - Defines FormIQ REST API endpoints.
    - Receives user requirements.
    - Calls form generation services.
    - Calls the validation engine.
    - Handles human approval.
    - Creates approved Google Forms.

Current workflow:

    Requirement
        ↓
    Generate Form
        ↓
    Validate Form
        ↓
    Human Review
        ↓
    Approve
        ↓
    Create Google Form

This file acts as the API/application layer.

Business logic is kept inside service modules rather than
being implemented directly inside the API endpoints.
"""

from fastapi import FastAPI, HTTPException

from app.schemas.api import (
    ApprovalResponse,
    ApproveFormRequest,
    FormGenerationResponse,
    FormRequest,
    FormValidationResponse,
    FormValidationRequest,
    GenerateAndValidateRequest,
    GenerateAndValidateResponse,
    GoogleFormResponse,
    PublishResponse,
)

from app.services.gemini_service import generate_form

from app.services.google_forms_service import (
    create_google_form,
)

from app.services.validation.quality_engine import (
    validate_form,
)


app = FastAPI(
    title="FormIQ",
    description="AI Form Intelligence & Automation Platform",
    version="0.4.0",
)


# ============================================================
# HEALTH / ROOT ENDPOINTS
# ============================================================


@app.get("/")
def root():
    """
    Basic API information endpoint.
    """

    return {
        "message": "FormIQ API is running"
    }


@app.get("/health")
def health():
    """
    Health-check endpoint used to verify that the backend
    is running correctly.
    """

    return {
        "status": "healthy",
        "service": "FormIQ",
        "version": "0.4.0",
    }


# ============================================================
# FORM GENERATION
# ============================================================


@app.post(
    "/api/v1/forms/generate",
    response_model=FormGenerationResponse,
)
def generate_form_endpoint(
    request: FormRequest,
):
    """
    Generate a structured form from a natural-language requirement.
    """

    if not request.requirement.strip():

        raise HTTPException(
            status_code=400,
            detail="Form requirement cannot be empty",
        )

    try:

        form = generate_form(
            request.requirement
        )

        return FormGenerationResponse(
            success=True,
            form=form,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# FORM VALIDATION
# ============================================================


@app.post(
    "/api/v1/forms/validate",
    response_model=FormValidationResponse,
)
def validate_form_endpoint(
    request: FormValidationRequest,
):
    """
    Validate an existing generated form.
    """

    try:

        result = validate_form(
            form=request.form,
            requirement=request.requirement,
        )

        return FormValidationResponse(
            success=True,
            validation=result,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GENERATE + VALIDATE
# ============================================================


@app.post(
    "/api/v1/forms/generate-and-validate",
    response_model=GenerateAndValidateResponse,
)
def generate_and_validate_form(
    request: GenerateAndValidateRequest,
):
    """
    Generate a form from the user's requirement and immediately
    run the FormIQ validation engine.

    The generated form is returned with status REVIEW_REQUIRED.
    """

    if not request.requirement.strip():

        raise HTTPException(
            status_code=400,
            detail="Form requirement cannot be empty",
        )

    try:

        form = generate_form(
            request.requirement
        )

        validation = validate_form(
            form=form,
            requirement=request.requirement,
        )

        return GenerateAndValidateResponse(
            success=True,
            status="REVIEW_REQUIRED",
            form=form,
            validation=validation,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# APPROVAL
# ============================================================


@app.post(
    "/api/v1/forms/approve",
    response_model=ApprovalResponse,
)
def approve_form(
    request: ApproveFormRequest,
):
    """
    Validate and approve a generated form.

    A form containing CRITICAL validation issues cannot be approved.
    """

    try:

        validation = validate_form(
            form=request.form,
            requirement=request.requirement,
        )

        critical_issues = [
            issue
            for issue in validation.issues
            if issue.severity == "CRITICAL"
        ]

        if critical_issues:

            return ApprovalResponse(
                success=False,
                status="REJECTED",
                message=(
                    "Form cannot be approved because "
                    "critical validation issues exist."
                ),
                form=request.form,
                validation=validation,
            )

        return ApprovalResponse(
            success=True,
            status="APPROVED",
            message=(
                "Form approved successfully. "
                "It is ready to be published to Google Forms."
            ),
            form=request.form,
            validation=validation,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# APPROVE + CREATE GOOGLE FORM
# ============================================================


@app.post(
    "/api/v1/forms/approve-and-create",
    response_model=PublishResponse,
)
def approve_and_create_google_form(
    request: ApproveFormRequest,
):
    """
    Validate a form and create the corresponding Google Form
    if no critical validation issues are present.
    """

    try:

        validation = validate_form(
            form=request.form,
            requirement=request.requirement,
        )

        critical_issues = [
            issue
            for issue in validation.issues
            if issue.severity == "CRITICAL"
        ]

        if critical_issues:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Form cannot be published because "
                    "critical validation issues exist."
                ),
            )

        google_form = create_google_form(
            request.form
        )

        return PublishResponse(
            success=True,
            status="PUBLISHED",
            message=(
                "Form approved and Google Form "
                "created successfully."
            ),
            form=request.form,
            validation=validation,
            google_form=GoogleFormResponse(
                form_id=google_form.get("formId"),
                responder_uri=google_form.get(
                    "responderUri"
                ),
            ),
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# DIRECT GENERATE + CREATE
# ============================================================


@app.post(
    "/api/v1/forms/generate-and-create",
    response_model=PublishResponse,
)
def generate_and_create_google_form(
    request: FormRequest,
):
    """
    Legacy/demo endpoint.

    Generates a form and directly creates the Google Form.

    Production workflow should preferably use:

        generate-and-validate
                ↓
            review/edit
                ↓
             approve
                ↓
          approve-and-create
    """

    if not request.requirement.strip():

        raise HTTPException(
            status_code=400,
            detail="Form requirement cannot be empty",
        )

    try:

        form = generate_form(
            request.requirement
        )

        google_form = create_google_form(
            form
        )

        validation = validate_form(
            form=form,
            requirement=request.requirement,
        )

        return PublishResponse(
            success=True,
            status="PUBLISHED",
            message=(
                "Google Form created successfully."
            ),
            form=form,
            validation=validation,
            google_form=GoogleFormResponse(
                form_id=google_form.get("formId"),
                responder_uri=google_form.get(
                    "responderUri"
                ),
            ),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )