from flask import Flask, render_template, request, jsonify, abort
from peewee import SqliteDatabase, Model, DateTimeField, CharField
from datetime import datetime

db = SqliteDatabase("passwords.db")

class Password(Model):
    password = CharField(unique = True)
    created = DateTimeField()

    class Meta:
        database = db

db.connect()


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def leak_api():
    if request.method == "POST":
        passwords = set(request.form.get('passwords', []).split(","))
        pws = []
        for p in passwords:
            pass_obj = Password.get_or_none(Password.password == p)
            if pass_obj:
                pws.append(f"Hash '{p}' Found! Leaked: {pass_obj.created}")

        return render_template("passwords.html", pws = pws)
    else:
        return render_template("home.html")

@app.route("/api_get", methods=["POST"])
def api_get():
    json = request.json

    passwords = set(json.get("passwords", None))

    if not passwords:
        return "{}"

    pws = { str(p): f"{Password.get_or_none(Password.password == p).created}"  if Password.get_or_none(Password.password == p) else "Not found" for p in passwords }
    return jsonify(pws)

@app.route("/api_put", methods=["POST"])
def api_put():
    json = request.json

    passwords = json.get("passwords", None)

    if json.get("user.secret", None) != "PasswordIsLeaked":
        abort(401)

    if not passwords:
        return "{}"
    
    passwords = set(passwords)

    pws = { }
    for p in passwords:
        pass_obj = Password.get_or_none(Password.password == p)
        if pass_obj:
            pws[p] = (f"Found! Added: {pass_obj.created}")
        else:
            Password.create(password = p, created = datetime.now())
            pws[p] = (f"Added!")
    
    return jsonify(pws)

def create_db():
    db.create_tables([Password])
    Password.create(password = "TestPass", created = datetime.now())
