from app.services.google_forms_service import get_google_forms_service


def create_test_form():

    service = get_google_forms_service()

    # Step 1: Create an empty Google Form
    form_body = {
        "info": {
            "title": "FormIQ Test Form"
        }
    }

    result = service.forms().create(
        body=form_body
    ).execute()

    form_id = result["formId"]

    print("\nGoogle Form created successfully!")
    print("Form ID:", form_id)

    # Google Forms API returns the responder URL
    if "responderUri" in result:
        print("Form URL:", result["responderUri"])

    return result


if __name__ == "__main__":
    create_test_form()