from flask      import Flask
from flask      import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users = {}

names = {}

@app.route("/")
def serveRoot():
    return "Nothing to see here!"

@app.route("/login", methods = ["POST"])
def login():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            return "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/newuser", methods = ["POST"])
def newuser():
    if request.json["username"] not in users:
        users[request.json["username"]] = request.json["password"]
        names[request.json["username"]] = request.json["displayn"]
        return "Y"
    else:
        return "That user already exists"

@app.route("/changename", methods = ["POST"])
def changename():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            names[request.json["username"]] = request.json["displayn"]
            return "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/changepwd", methods = ["POST"])
def changepwd():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            users[request.json["username"]] = request.json["newpass"]
            return "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/nameof/<username>")
def nameof(username):
    return names[username] if username in names else ""

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = False)
