from flask      import Flask
from flask      import request
from flask_cors import CORS

import utils

app = Flask(__name__)
CORS(app)

users = {}

names = {}

class Chatroom:
    def __init__(self, owner, ident):
        self.owner = owner
        self.mods = []
        self.difflist = []
        self.mode = 0 # 0 is blacklist, 1 is whitelist
        self.ident = ident
        self.messages = []

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
    if len(request.json["username"]) > 16:
        return "Usernames cannot be longer than 16 characters"
    elif len(request.json["displayn"]) > 16:
        return "Display names cannot be longer than 16 characters"
    elif request.json["username"] not in users:
        users[request.json["username"]] = request.json["password"]
        names[request.json["username"]] = request.json["displayn"]
        return "Y"
    else:
        return "That user already exists"

@app.route("/changename", methods = ["POST"])
def changename():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            if len(utils.removeFormatting(request.json["displayn"])) > 16:
                return "Display names cannot be longer than 16 characters"
            else:
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
