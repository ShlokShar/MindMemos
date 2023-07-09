import flask
from flask import Flask
from authentication import *
from backend import *
import datetime

app = Flask(__name__)
app.secret_key = "TheANS"


@app.route('/')
def index():
    if not flask.session.get("user"):
        return flask.render_template("index.html")
    else:
        name = getName(flask.session.get("user"))
        return flask.render_template("dashboard.html", name=name)


@app.route("/write", methods=["POST", "GET"])
def write():
    title = datetime.datetime.now().strftime("%B %d, %Y %I:%H:%M %p")
    if flask.request.method == "POST":
        postEntry(flask.session.get("user"), flask.request.form["entry"], getEmotions(flask.request.form["entry"]),
                  title)
        return flask.redirect("/")
    else:
        if flask.session.get("user"):
            return flask.render_template("write.html", title=title)
        else:
            return flask.redirect("/login")


@app.route("/genesis/<text>")
def genesis(text):
    questions = getQuestions(text)
    questions = "\n\n".join(questions)
    print(questions)

    return flask.jsonify(questions)


@app.route("/entries")
def show_entries():
    if flask.session.get("user"):
        entries = getEntries(flask.session["user"])[::-1]
        return flask.render_template("entries.html", entries=entries)
    else:
        return flask.redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    if flask.request.method == "POST":
        try:
            email = flask.request.form["email"]
            password = flask.request.form["password"]

            user = authentication.sign_in_with_email_and_password(email, password)
            flask.session["user"] = user["localId"]
            return flask.render_template("dashboard.html")
        except:
            return flask.render_template("login.html", error="Account does not exist!")

    else:
        return flask.render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if flask.request.method == "POST":
        try:
            email = flask.request.form["email"]
            password = flask.request.form["password"]

            user = authentication.create_user_with_email_and_password(email, password)
            createUser(flask.request.form["name"], user["localId"])

            flask.session["user"] = user["localId"]

            return flask.redirect("/")
        except:
            return flask.render_template("signup.html", error=" Account already exists!")
    else:
        return flask.render_template("signup.html")


@app.route("/logout")
def logout():
    if flask.session.get("user"):
        flask.session.pop("user", None)
    return flask.redirect("/login")


@app.route("/analyze")
def analyze():
    if flask.session.get("user"):
        emotions = totalStats(flask.session["user"])

        plotPie(emotions.keys(), emotions.values())

        return flask.render_template("data.html", emotions=emotions, pie_path="static/img/pie.png")
    else:
        return flask.redirect("/login")


if __name__ == '__main__':
    app.run()
