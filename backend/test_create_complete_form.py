from app.schemas.form import GeneratedForm, FormQuestion
from app.services.google_forms_service import create_google_form


def main():

    form = GeneratedForm(
        title="FormIQ Faculty Feedback Form",
        description="Feedback form for faculty training sessions.",
        questions=[
            FormQuestion(
                title="Name",
                type="SHORT_ANSWER",
                required=True
            ),

            FormQuestion(
                title="Department",
                type="DROPDOWN",
                required=True,
                options=[
                    "AIT",
                    "HNIMR",
                    "Cummins",
                    "KBJoshi",
                    "Siddhivinakyak"
                ]
            ),

            FormQuestion(
                title="How would you rate the session?",
                type="LINEAR_SCALE",
                required=True,
                options=["1", "2", "3", "4", "5"]
            ),

            FormQuestion(
                title="What did you like about the session?",
                type="PARAGRAPH",
                required=False
            ),

            FormQuestion(
                title="Which topics would you like to learn more about?",
                type="CHECKBOX",
                required=False,
                options=[
                    "Python",
                    "Machine Learning",
                    "Generative AI",
                    "Agentic AI",
                    "Data Analytics"
                ]
            )
        ]
    )

    print("Creating Google Form...")

    result = create_google_form(form)

    print("\n===================================")
    print("Google Form Created Successfully!")
    print("===================================")

    print("Form ID:", result["formId"])

    if "responderUri" in result:
        print("Form URL:", result["responderUri"])

    print("===================================")


if __name__ == "__main__":
    main()