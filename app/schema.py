from wtforms import Form, StringField, PasswordField, validators


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
        "Email", [validators.DataRequired(), validators.Length(min=5, max=25)]
    )
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
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
