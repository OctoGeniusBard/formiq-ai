import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/forms.body"
]

DISCOVERY_DOC = (
    "https://forms.googleapis.com/$discovery/rest?version=v1"
)


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials.json"
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "token.json"
)


# ---------------------------------------------------------
# Google Forms Authentication
# ---------------------------------------------------------

def get_google_forms_service():

    credentials = None

    # Load existing OAuth token
    if os.path.exists(TOKEN_FILE):

        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # If credentials are missing or invalid
    if not credentials or not credentials.valid:

        # Refresh existing token
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):

            credentials.refresh(Request())

        # Start OAuth flow
        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            credentials = flow.run_local_server(
                port=8090
            )

        # Save token
        with open(TOKEN_FILE, "w") as token:

            token.write(
                credentials.to_json()
            )

    # Create Google Forms API service
    service = build(
        "forms",
        "v1",
        credentials=credentials,
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False
    )

    return service


# ---------------------------------------------------------
# Create Google Form
# ---------------------------------------------------------

def create_google_form(form):

    service = get_google_forms_service()

    # -----------------------------------------------------
    # 1. Create empty Google Form
    # -----------------------------------------------------

    form_body = {
        "info": {
            "title": form.title,
            "documentTitle": form.title
        }
    }

    created_form = service.forms().create(
        body=form_body
    ).execute()

    form_id = created_form["formId"]

    # -----------------------------------------------------
    # 2. Prepare question requests
    # -----------------------------------------------------

    requests = []

    for index, question in enumerate(form.questions):

        question_type = question.type.upper()

        # ---------------------------------------------
        # SHORT ANSWER
        # ---------------------------------------------

        if question_type == "SHORT_ANSWER":

            request = {
                "createItem": {
                    "item": {
                        "title": question.title,
                        "questionItem": {
                            "question": {
                                "required": question.required,
                                "textQuestion": {
                                    "paragraph": False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }

        # ---------------------------------------------
        # PARAGRAPH
        # ---------------------------------------------

        elif question_type == "PARAGRAPH":

            request = {
                "createItem": {
                    "item": {
                        "title": question.title,
                        "questionItem": {
                            "question": {
                                "required": question.required,
                                "textQuestion": {
                                    "paragraph": True
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }

        # ---------------------------------------------
        # MULTIPLE CHOICE
        # ---------------------------------------------

        elif question_type == "MULTIPLE_CHOICE":

            options = [
                {
                    "value": option
                }
                for option in (question.options or [])
            ]

            request = {
                "createItem": {
                    "item": {
                        "title": question.title,
                        "questionItem": {
                            "question": {
                                "required": question.required,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": options
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }

        # ---------------------------------------------
        # CHECKBOX
        # ---------------------------------------------

        elif question_type == "CHECKBOX":

            options = [
                {
                    "value": option
                }
                for option in (question.options or [])
            ]

            request = {
                "createItem": {
                    "item": {
                        "title": question.title,
                        "questionItem": {
                            "question": {
                                "required": question.required,
                                "choiceQuestion": {
                                    "type": "CHECKBOX",
                                    "options": options
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }

        # ---------------------------------------------
        # DROPDOWN
        # ---------------------------------------------

        elif question_type == "DROPDOWN":

            options = [
                {
                    "value": option
                }
                for option in (question.options or [])
            ]

            request = {
                "createItem": {
                    "item": {
                        "title": question.title,
                        "questionItem": {
                            "question": {
                                "required": question.required,
                                "choiceQuestion": {
                                    "type": "DROP_DOWN",
                                    "options": options
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }

        # ---------------------------------------------
        # LINEAR SCALE
        # ---------------------------------------------

        elif question_type == "LINEAR_SCALE":

            request = {
                "createItem": {
                    "item": {
                        "title": question.title,
                        "questionItem": {
                            "question": {
                                "required": question.required,
                                "scaleQuestion": {
                                    "low": 1,
                                    "high": 5,
                                    "lowLabel": "Poor",
                                    "highLabel": "Excellent"
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }

        else:

            raise ValueError(
                f"Unsupported question type: {question.type}"
            )

        requests.append(request)

    # -----------------------------------------------------
    # 3. Add questions to Google Form
    # -----------------------------------------------------

    if requests:

        service.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": requests
            }
        ).execute()

    # -----------------------------------------------------
    # 4. Get final form
    # -----------------------------------------------------

    final_form = service.forms().get(
        formId=form_id
    ).execute()

    return final_form