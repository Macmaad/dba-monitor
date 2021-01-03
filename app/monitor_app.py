import os
import json
from uuid import uuid4
from functools import wraps
from datetime import datetime as dt

from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_cors import CORS
from passlib.hash import sha256_crypt

from utils.database_interactions import execute_query
from schema import RegistrationFormValidator, LoginFormValidator
from utils.app_utils import (
    logger,
    read_json_file,
    send_google_chat_message,
    add_background_cron,
)

SECRETS = read_json_file("app/utils/secrets.json")
app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)


def send_bin_to_txt(files):
    for file in files:
        file_data = os.popen(
            f"echo {SECRETS['sudo_password']}| sudo -S mysqlbinlog /usr/local/mysql/data/{file}"
        ).read()
        with open("app/bin_logs.txt", "a") as append_file:
            append_file.write(file_data)

        query = """
            INSERT INTO 
                binlog_files
            (
                file_name
            )
            VALUES 
            (
                ?
            )
        """
        execute_query(query, (str(file),))


def get_known_binlog_files():
    query = """
        SELECT 
            file_name 
        FROM 
            binlog_files
    """
    result = execute_query(query)
    result = [x[0] for x in result]
    os.system(
        f"echo {SECRETS['sudo_password']} | sudo -S mysql.server restart >/dev/null 2>&1"
    )
    return result


def get_binlog_data():
    new_files = []
    bin_log_file = (
        os.popen(
            f"echo {SECRETS['sudo_password']} | sudo -S ls /usr/local/mysql/data | grep binlog"
        )
        .read()
        .split("\n")
    )

    existing_binlogs = get_known_binlog_files()
    for file in bin_log_file:
        if file not in existing_binlogs and file != "":
            new_files.append(file)
    logger.info("Sending new file", extra={"file_name": new_files})
    send_bin_to_txt(new_files)


def is_logged_in(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return function(*args, **kwargs)
        else:
            flash("Unauthorized, please login", "danger")
            return redirect(url_for("login"))

    return wrap


def feed_db_activity():
    status = os.system(
        f"echo {SECRETS['sudo_password']} | sudo -S mysql.server status >/dev/null 2>&1"
    )
    status = status if status == 0 else 1
    if status:
        send_google_chat_message(f"DB DOWN AT {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")

    query = """
        INSERT INTO 
            db_active
        (
            db_status
        )
        VALUES(
            ? 
        )
    """
    execute_query(query, (status,))


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
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out.", "success")
    return redirect(url_for("login"))


@app.route(
    "/monitor/dashboard",
    defaults={"initial_date": None, "final_date": None},
)
@app.route("/monitor/dashboard/<initial_date>", defaults={"final_date": None})
@app.route("/monitor/dashboard/<initial_date>/<final_date>")
def monitor_dashboard_data(initial_date, final_date):
    status_code = 500
    if initial_date and final_date:
        query = {
            "query_string": """
                SELECT 
                    db_status
                    , created_tms 
                FROM 
                    db_active 
                WHERE
                    created_tms >= ? 
                    AND
                    created_tms <= ?  
            """,
            "params": (
                initial_date,
                final_date,
            ),
        }

    elif initial_date:
        query = {
            "query_string": """
                SELECT 
                    db_status
                    , created_tms 
                FROM 
                    db_active 
                WHERE
                    created_tms >= ? 
            """,
            "params": (initial_date,),
        }

    else:
        query = {
            "query_string": """
                SELECT 
                    db_status
                    , created_tms 
                FROM 
                    db_active 
                ORDER BY 
                    created_tms 
                DESC 
                LIMIT 
                    10 
            """,
            "params": (),
        }

    result = execute_query(query["query_string"], query["params"])

    if len(result) > 0:
        status_code = 200

    response = {"status_code": status_code, "body": result}
    return response


@app.route("/monitor")
@is_logged_in
def monitor():
    return render_template("monitor.html")


@app.route("/binlogs", methods=["POST"])
def binlogs():
    rows = json.loads(request.data)
    rows = int(rows.get("rows", 10))
    file_data = os.popen(f"tail -{rows} app/bin_logs.txt").read()
    return {"body": file_data}


def app_handler():
    add_background_cron(feed_db_activity, "interval", 60 * 10)
    add_background_cron(get_binlog_data, "interval", 60 * 30)
    app.secret_key = "ultra_secret_123"
    app.run(debug=True)


if __name__ == "__main__":
    app_handler()
