# FormIQ — AI-Powered Form Intelligence & Automation

> Transform natural-language requirements into validated Google Forms using Generative AI.

[![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google)](https://ai.google.dev/)
[![Google Forms API](https://img.shields.io/badge/Google%20Forms-API-7248B9?logo=google)](https://developers.google.com/forms)
[![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063)](https://docs.pydantic.dev/)
[![Status](https://img.shields.io/badge/Status-Working%20MVP-success)]()

---

## Overview

**FormIQ** is an AI-powered application that converts natural-language form requirements into structured, validated Google Forms.

A user describes what they need in natural language. FormIQ uses **Google Gemini** to understand the requirement, design appropriate questions, validate the generated form, identify potential quality issues, and—after human approval—create the actual Google Form through the **Google Forms API**.

### Core Workflow

```text
Natural Language Requirement
            |
            v
        Gemini AI
            |
            v
    Structured Form JSON
            |
            v
    Pydantic Validation
            |
            v
   Form Quality Engine
            |
      +-----+-----+
      |           |
      v           v
Deterministic   AI Semantic
Validation      Review
      |           |
      +-----+-----+
            |
            v
      Human Approval
            |
            v
     Google Forms API
            |
            v
     Published Form
```

---

# Problem Statement

Creating a useful form is more than generating a list of questions.

A good form needs to consider:

- What information is actually required?
- Are the questions relevant to the requirement?
- Are questions duplicated?
- Is a question ambiguous?
- Is the selected question type appropriate?
- Is potentially sensitive information being collected?
- Are rating questions configured correctly?
- Does the generated form actually cover the user's requirement?

A simple:

```text
Prompt -> LLM -> Google Form
```

pipeline does not provide enough control.

FormIQ introduces a validation and human-review layer:

```text
Prompt
  |
  v
AI Generation
  |
  v
Structured Validation
  |
  v
Quality Analysis
  |
  v
Human Review
  |
  v
Google Form
```

---

# What FormIQ Does

The current MVP supports:

- Natural-language form requirements
- Gemini-powered form generation
- Structured JSON form output
- Pydantic schema validation
- Question validation
- Duplicate-question detection
- PII detection
- Requirement validation
- Requirement coverage review
- AI semantic review
- Form quality scoring
- Human approval before external action
- Google OAuth authentication
- Google Forms API integration
- Google Form creation and publishing

---

# AI-Powered Form Generation

FormIQ uses Gemini as the form-designing intelligence layer.

The LLM is instructed to return a controlled JSON structure rather than free-form text.

Example:

```json
{
  "title": "Python Workshop Faculty Feedback",
  "description": "Feedback form for the Python workshop.",
  "questions": [
    {
      "title": "Faculty Name",
      "type": "SHORT_ANSWER",
      "required": true,
      "options": null
    },
    {
      "title": "Department",
      "type": "DROPDOWN",
      "required": true,
      "options": [
        "Computer Science",
        "Management",
        "Commerce",
        "Engineering"
      ]
    },
    {
      "title": "Overall Workshop Rating",
      "type": "LINEAR_SCALE",
      "required": true,
      "options": [
        "1",
        "2",
        "3",
        "4",
        "5"
      ]
    }
  ]
}
```

The structured output is validated using Pydantic before it is used by the application.

---

# Form Quality & Validation

FormIQ does not blindly trust AI-generated output.

The validation layer includes:

| Validation | Purpose |
|---|---|
| Question Validation | Checks generated question structure |
| Duplicate Detection | Identifies duplicate or similar questions |
| PII Detection | Identifies potentially sensitive personal information |
| Requirement Validation | Checks the generated form against the original requirement |
| Requirement Coverage Review | Evaluates how well requirements are covered |
| Semantic AI Review | Evaluates question quality and potential issues |
| Quality Engine | Combines validation and review results |

---

# Form Quality Score

FormIQ produces a quality assessment for a generated form.

Example:

```text
FORM QUALITY SCORE
--------------------------------
Overall Score           96/100
Requirement Coverage   100
Question Quality        92
Question Type Accuracy  94
Duplicate Detection    100
Ambiguity Detection     88
PII Safety              90
Semantic Review         90
```

The exact score depends on the generated form and validation results.

The score is intended to help the user identify areas that deserve review. It does not claim that an AI-generated form is automatically perfect.

---

# Human-in-the-Loop

FormIQ follows a **human approval before external action** principle.

```text
AI Generates
     |
     v
System Validates
     |
     v
Issues / Suggestions
     |
     v
Human Reviews
     |
     v
Human Approves
     |
     v
Google Forms API
```

This prevents an AI-generated form from being automatically published without user review.

---

# Architecture

The current MVP follows a service-oriented FastAPI architecture.

```text
+---------------------------------------------+
|                  FormIQ                     |
|                                             |
|  +---------------------------------------+  |
|  |             FastAPI API               |  |
|  +-------------------+-------------------+  |
|                      |                      |
|          +-----------+-----------+          |
|          |                       |          |
|          v                       v          |
|   +--------------+       +--------------+  |
|   | Gemini       |       | Form Quality |  |
|   | Service      |       | Service      |  |
|   +------+-------+       +------+-------+  |
|          |                      |           |
|          v             +--------+--------+  |
|   Structured Form      | Validation      |  |
|                        | Services        |  |
|                        +--------+--------+  |
|                                 |           |
|                                 v           |
|                         Human Approval      |
|                                 |           |
|                                 v           |
|                      +------------------+   |
|                      | Google Forms     |   |
|                      | Service          |   |
|                      +--------+---------+   |
+-------------------------------+-------------+
                                |
                                v
                       Google Forms API
```

---

# Project Structure

```text
FormIQ/
|
├── .gitignore
├── README.md
|
├── backend/
|   |
|   ├── app/
|   |   ├── __init__.py
|   |   ├── main.py
|   |   |
|   |   ├── schemas/
|   |   |   ├── __init__.py
|   |   |   ├── api.py
|   |   |   ├── form.py
|   |   |   └── validation.py
|   |   |
|   |   └── services/
|   |       ├── __init__.py
|   |       ├── form_quality_service.py
|   |       ├── gemini_service.py
|   |       ├── google_forms_service.py
|   |       |
|   |       └── validation/
|   |           ├── __init__.py
|   |           ├── duplicate_validator.py
|   |           ├── gemini_reviewer.py
|   |           ├── pii_validator.py
|   |           ├── quality_engine.py
|   |           ├── question_validator.py
|   |           ├── requirement_coverage_reviewer.py
|   |           └── requirement_validator.py
|   |
|   ├── test_create_complete_form.py
|   ├── test_create_google_form.py
|   └── test_google_forms.py
|
└── docs/
    └── Testing_Input.txt
```

---

# Component Responsibilities

### `app/main.py`

Entry point for the FastAPI application and API configuration.

### `schemas/form.py`

Defines the structured form representation used by the application.

Core models include:

```text
FormQuestion
GeneratedForm
```

### `services/gemini_service.py`

Responsible for:

```text
Requirement
    |
    v
Gemini
    |
    v
Structured JSON
    |
    v
GeneratedForm
```

### `services/google_forms_service.py`

Responsible for Google Forms integration, including:

- OAuth authentication
- Google Forms API communication
- Form creation
- Question creation
- Form publishing/output information

### `services/form_quality_service.py`

Coordinates form-quality validation and review.

### `services/validation/`

Contains individual validation and review components.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13+ |
| API Framework | FastAPI |
| LLM | Google Gemini |
| Data Validation | Pydantic |
| Google Integration | Google Forms API |
| Authentication | Google OAuth 2.0 |
| API Documentation | Swagger / OpenAPI |
| Testing | Python test scripts |
| Version Control | Git |
| Repository | GitHub |

---

# Installation & Setup

## Prerequisites

Install:

- Python 3.13+
- Git
- Google account
- Google Cloud project
- Gemini API access
- Google Forms API access

---

## 1. Clone the Repository

```powershell
git clone https://github.com/OctoGeniusBard/formiq-ai.git
cd formiq-ai
```

---

## 2. Create a Virtual Environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

If `backend/requirements.txt` is available:

```powershell
pip install -r backend/requirements.txt
```

> Note: The initial repository snapshot does not currently include a `requirements.txt` in the confirmed project structure. Add one before claiming the repository is fully reproducible from a clean clone.

---

# Environment Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit `.env` to GitHub.

The repository `.gitignore` is configured to exclude environment variables and credentials.

---

# Google Forms OAuth Setup

FormIQ requires Google OAuth to create Google Forms.

### 1. Create a Google Cloud Project

Create or select a Google Cloud project.

### 2. Enable Google Forms API

Enable the Google Forms API.

### 3. Configure OAuth

Configure the OAuth consent screen and add the development Google account as a test user when required.

### 4. Create OAuth Credentials

Download the OAuth client credentials and save them as:

```text
backend/credentials.json
```

### 5. Authenticate

During the first Google Forms operation, OAuth authentication will be performed.

A token file may then be generated:

```text
backend/token.json
```

These files contain sensitive authentication information and must never be committed to GitHub.

---

# Running FormIQ

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Move into the backend:

```powershell
cd backend
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

The application normally runs at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI can be used to:

- Inspect available endpoints
- Submit form requirements
- Generate forms
- Validate forms
- Review validation results
- Approve forms
- Create Google Forms
- Inspect API responses

---

# Example Use Case

### Requirement

```text
Create a feedback form for a Python workshop conducted for faculty members.

Collect:
- Faculty Name
- Department
- Email Address
- Overall Workshop Rating
- Topics Covered
- Suggestions for Improvement
```

### FormIQ Process

```text
1. User submits requirement
             |
             v
2. Gemini understands requirement
             |
             v
3. Form structure generated
             |
             v
4. Pydantic validates structure
             |
             v
5. Quality validators execute
             |
             v
6. AI semantic review executes
             |
             v
7. Quality score generated
             |
             v
8. Human reviews result
             |
             v
9. User approves
             |
             v
10. Google Forms API creates form
```

### Output

The application can return information such as:

```json
{
  "form_id": "GOOGLE_FORM_ID",
  "responder_uri": "https://docs.google.com/forms/d/e/..."
}
```

---

# Testing

The repository contains test scripts for major parts of the workflow:

```text
backend/
├── test_google_forms.py
├── test_create_google_form.py
└── test_create_complete_form.py
```

Sample input:

```text
docs/Testing_Input.txt
```

Example commands:

```powershell
python backend/test_google_forms.py
```

```powershell
python backend/test_create_google_form.py
```

```powershell
python backend/test_create_complete_form.py
```

---

# Security Considerations

The following files must never be committed:

```text
.env
credentials.json
token.json
*.key
*.pem
```

The repository `.gitignore` excludes these files.

FormIQ follows an important architectural principle:

> **AI output should be validated before it is used to perform external actions.**

Therefore:

```text
Gemini
   |
   v
Structured Output
   |
   v
Pydantic Validation
   |
   v
Business Validation
   |
   v
Human Approval
   |
   v
Google Forms API
```

---

# Current MVP Scope

This repository represents the **first working FormIQ version**.

### Implemented

- [x] Natural-language form requirements
- [x] Gemini-powered form generation
- [x] Structured JSON output
- [x] Pydantic validation
- [x] Question validation
- [x] Duplicate detection
- [x] PII detection
- [x] Requirement validation
- [x] Requirement coverage review
- [x] AI semantic review
- [x] Form quality scoring
- [x] Human approval workflow
- [x] Google OAuth
- [x] Google Forms API integration
- [x] Google Form creation
- [x] Google Form publishing/output
- [x] Backend test scripts

---

# Future Roadmap

The current Google Form generator is the foundation for the broader FormIQ platform.

## Phase 2 — Document Intelligence

```text
PDF / DOCX / TXT
       |
       v
Document Processing
       |
       v
Requirement Extraction
       |
       v
AI Form Generation
```

## Phase 3 — Form Quality & Governance

Planned capabilities:

- Advanced requirement coverage
- Governance rules
- Organization policies
- Bias detection
- Advanced PII controls
- Explainable validation reports

## Phase 4 — Organization Knowledge + RAG

```text
Policies
Forms
Templates
SOPs
Question Banks
Documents
       |
       v
Knowledge Base
       |
       v
RAG
       |
       v
Context-Aware Form Generation
```

## Phase 5 — Natural-Language Form Editing

Future users will be able to give instructions such as:

```text
"Make the rating question optional."

"Change the rating scale to 1–5."

"Add an Other option to the topics question."

"Remove the email question."

"Make the department question a dropdown."
```

Workflow:

```text
Generated Form
      |
      v
Validation
      |
      v
User Correction
      |
      v
AI Interprets Instruction
      |
      v
Form Updated
      |
      v
Re-validation
      |
      v
Human Approval
```

## Phase 6 — Response Intelligence

```text
Google Form Responses
          |
          v
Response Processing
          |
          v
Statistical Analysis
          |
          v
AI Analysis
          |
          v
Insights
          |
          v
Recommendations
```

Potential capabilities:

- Response summaries
- Rating analysis
- Trends
- Sentiment
- Themes
- Common complaints
- Positive feedback
- Repeated requests
- Action recommendations

## Phase 7 — Agentic AI

Planned architecture:

```text
                Supervisor Agent
                       |
       +---------------+----------------+
       v               v                v
 Requirement      Knowledge          Policy
   Agent            Agent             Agent
       |               |                |
       +---------------+----------------+
                       |
                       v
                 Form Designer
                     Agent
                       |
                       v
                 Quality Agent
                       |
                       v
                 Human Review
                       |
                       v
              Google Forms Agent
                       |
                       v
             Response Analyzer
                       |
                       v
                Insight Agent
```

## Phase 8 — MCP Integration

The long-term architecture will use the **Model Context Protocol (MCP)** for standardized access to tools and organizational data.

Potential tool categories:

```text
Google Workspace
Organization Knowledge
Validation
Analytics
```

MCP will complement—not replace—the application's API, business services, and agent orchestration layers.

---

# Long-Term Product Vision

The first version of FormIQ answers:

> **"Can AI create a Google Form from a requirement?"**

The long-term FormIQ platform aims to answer a much bigger question:

> **"Can AI understand an organization's requirements, knowledge, policies and data, intelligently design and validate forms, automate their lifecycle, analyze responses, and recommend actions?"**

Long-term architecture:

```text
                    FormIQ
                      |
       +--------------+--------------+
       v              v              v
 Requirements     Organization     Documents
                   Knowledge
       |              |              |
       +--------------+--------------+
                      |
                      v
                AI Understanding
                      |
                      v
                Form Intelligence
                      |
                      v
              Quality & Governance
                      |
                      v
                Human Approval
                      |
                      v
             Form Automation
                      |
                      v
             Response Intelligence
                      |
                      v
                AI Insights
                      |
                      v
              Recommendations
```

---

# Why This Project?

FormIQ demonstrates practical application of Generative AI beyond a basic chatbot.

The project combines:

- LLM-based structured generation
- Prompt engineering
- Pydantic schema validation
- Deterministic validation
- AI semantic evaluation
- Human-in-the-loop design
- External API integration
- OAuth authentication
- FastAPI backend development
- AI-assisted workflow automation
- Validation before external actions

The project is intentionally designed as a foundation for more advanced:

**RAG -> Agentic AI -> MCP -> AI Automation**

architecture.

---

# Screenshots & Demo

Recommended screenshots:

1. FastAPI Swagger UI
2. Form generation request
3. Generated form structure
4. Validation result
5. Form quality score
6. Human approval
7. Generated Google Form

Recommended structure:

```text
docs/
└── screenshots/
    ├── swagger.png
    ├── generated-form.png
    ├── validation.png
    ├── quality-score.png
    └── google-form.png
```

---

# Engineering Principles

### 1. Structured AI Output

LLMs should produce structured data whenever downstream software needs to consume the result.

### 2. Validate Before Acting

AI output should not directly trigger external actions.

### 3. Human-in-the-Loop

Important external actions should have an approval stage.

### 4. Separation of Responsibilities

LLM reasoning, validation, business logic, and external integrations are separated into different services.

### 5. Incremental Architecture

Complex agentic infrastructure should be introduced only after the deterministic foundation is stable.

---

# Author

## Revati Pawar

**Data Science Practitioner & Professor**

MKSSS's AIT Center for Data Science, ML & AI, Pune

### Areas of Interest

- Data Science
- Machine Learning
- Generative AI
- Large Language Models
- Agentic AI
- AI Application Engineering
- Intelligent Automation

---

# Project Status

**Status:** 🟢 Working MVP

**Current capability:** AI-powered Google Form generation and validation

**Next direction:** Document Intelligence -> RAG -> Human-in-the-Loop Editing -> Response Intelligence -> Agentic AI -> MCP

---

> **FormIQ is an evolving AI engineering project focused on building intelligent, validated, and human-controlled automation workflows—not simply generating forms with an LLM.**
