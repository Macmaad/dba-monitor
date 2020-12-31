from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_cors import CORS

from schema import RegistrationFormValidator, LoginFormValidator

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginFormValidator(request.form)
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationFormValidator(request.form)
    if request.method == "POST" and form.validate():
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


if __name__ == "__main__":
    app.secret_key = "ultra_secret_123"
    app.run(debug=True)
