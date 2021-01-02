from wtforms import Form, StringField, PasswordField, validators

GOOGLE_CHAT_WEBHOOK = "https://chat.googleapis.com/v1/spaces/AAAA9dMeL0g/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=03y0q7CqGrReKW2xSi9CDfnTCaBKscfhRjc9Eg2EP98%3D"


class RegistrationFormValidator(Form):
    """
    Class to verify data and render values on jinja html.
    """

    name = StringField(
        "Name", [validators.DataRequired(), validators.Length(min=1, max=50)]
    )
    username = StringField(
        "Username",
        [
            validators.DataRequired(),
            validators.Length(min=5, max=25, message="Minimum 5 characters"),
        ],
    )
    email = StringField(
        "Email", [validators.DataRequired(), validators.Length(min=5, max=50)]
    )
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.Length(min=8, max=50),
            validators.EqualTo("confirm", message="Passwords do not match"),
        ],
    )
    confirm = PasswordField("Confirm password")


class LoginFormValidator(Form):
    username = StringField(
        "Username",
        [
            validators.DataRequired(),
            validators.Length(min=5, max=25, message="Minimum 5 characters"),
        ],
    )
    password = PasswordField(
        "Password",
        [validators.DataRequired()],
    )
