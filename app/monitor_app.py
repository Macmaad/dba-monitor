from flask import Flask, render_template, session
from flask_cors import CORS

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.secret_key = "ultra_secret_123"
    app.run(debug=True, use_reloader=False)
