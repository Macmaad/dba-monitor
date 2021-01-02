from uuid import uuid4
from http import HTTPStatus

from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_cors import CORS
from passlib.hash import sha256_crypt
import requests

from utils.database_interactions import execute_query
from schema import RegistrationFormValidator, LoginFormValidator, GOOGLE_CHAT_WEBHOOK
from utils.app_utils import logger

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationFormValidator(request.form)
    if request.method == "POST" and form.validate():
        query = """
            INSERT INTO
                users 
            (
                user_uuid
                , name
                , username
                , email
                , password
            )
            VALUES (
                ?
                , ?
                , ?
                , ?
                , ?
            )
        """

        execute_query(
            query,
            (
                str(uuid4()),
                form.name.data,
                form.username.data,
                form.email.data,
                sha256_crypt.encrypt(str(form.password.data)),
            ),
        )

        flash("Register success", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginFormValidator(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password_candidate = form.password.data
        query = """
            SELECT  
                password 
            FROM 
                users 
            WHERE 
                username = ?
        """

        result = execute_query(query, (username,))

        if len(result) > 0:
            if sha256_crypt.verify(password_candidate, result[0][0]):
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("monitor"))

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out.", "success")
    return redirect(url_for("login"))


@app.route("/monitor")
def monitor():
    return render_template("monitor.html")


@app.route("/messages/google-chat", methods=["POST"])
def send_google_chat_message():
    message = request.json.get("message")
    response = {"statusCode": HTTPStatus.BAD_REQUEST}

    if message:
        res = requests.post(
            GOOGLE_CHAT_WEBHOOK,
            json={"text": message},
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )

        if res.status_code == HTTPStatus.OK:
            logger.info("Message was sent successful", extra={"response": res.json()})
            response = {"statusCode": HTTPStatus.OK}

        else:
            logger.error(
                "Something went wrong sending the message",
                extra={"response": res.json()},
            )
            response = {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR}

    return response


if __name__ == "__main__":
    app.secret_key = "ultra_secret_123"
    app.run(debug=True)
