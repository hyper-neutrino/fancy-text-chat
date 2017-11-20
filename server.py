from flask      import Flask
from flask      import request
from flask_cors import CORS

import utils, pickle, time, socket

app = Flask(__name__)
CORS(app)

users = {}
names = {}
rooms = {}

PERM_READ = 0
PERM_POST = 1
PERM_EDIT = 2
PERM_DELT = 3
PERM_MODR = 4
PERM_OWNR = 5

class Chatroom:
    def __init__(self, owner, name, def_perm):
        self.perms = { owner: 4 }
        self.name = name
        self.def_perm = def_perm
        self.messages = []
        self.listeners = {}
    def getPermissions(self, user):
        if user in self.perms:
            return self.perms[user]
        else:
            return self.def_perm
    def getMessages(self, user):
        if self.getPermissions(user) >= PERM_READ:
            return self.messages
        else:
            return "You do not have permission to access this room's messages"
    def sendUpdate(self, update):
        for listener in self.listeners:
            try:
                self.listeners[listener].sendall(update)
            except:
                del self.listeners[listener]
    def post(self, user, message):
        if self.getPermissions(user) >= PERM_POST:
            self.messages.append((user, message))
            self.sendUpdate(b"P" + bytearray(user, "UTF8") + b"\x00" + bytearray(message, "UTF8") + b"\x00")
        else:
            return "You do not have permission to post messages to this room"
    def edit(self, user, index, content):
        if self.getPermissions(user) >= PERM_EDIT or self.messages[index][0] == user:
            self.messages[index][1] = content
        else:
            return "You do not have permission to edit messages in this room"
    def delt(self, user, index, content):
        if self.getPermissions(user) >= PERM_DELT or self.messages[index][0] == user:
            self.messages[index][1] = ""
        else:
            return "You do not have permission to delete messages in this room"
    def mod(self, user, target, perm):
        if self.getPermissions(user) >= PERM_MODR:
            if self.getPermissions(target) < PERM_OWNR:
                self.perms[target] = perm
            else:
                return "You cannot modify the permission level of a room owner"
        else:
            return "You do not have permission to modify users' permission levels in this room"
    def kick(self, user, target):
        if self.getPermissions(user) >= PERM_MODR:
            if self.getPermissions(target) < PERM_OWNR:
                pass # TODO
            else:
                return "You cannot kick a room owner"
        else:
            return "You do not have permission to kick users in this room"
    def ban(self, user, target, reason):
        if self.getPermissions(user) >= PERM_MODR:
            if self.getPermissions(target) < PERM_OWNR:
                pass # TODO
            else:
                return "You cannot ban a room owner"
        else:
            return "You do not have permission to ban users in this room"

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

@app.route("/makeroom", methods = ["POST"])
def makeroom():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            if request.json["ident"] in rooms:
                return "That room already exists"
            rooms[request.json["ident"]] = Chatroom(request.json["username"], request.json["name"], request.json["def_perm"])
            return "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/getmessages", methods = ["POST"])
def getmessages():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            if request.json["ident"] not in rooms:
                return "That room was not found"
            messages = rooms[request.json["ident"]].getMessages(request.json["username"])
            if isinstance(messages, list):
                return "Y" + "".join(map(chr, pickle.dumps(messages)))
            else:
                return messages
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/bind", methods = ["POST"])
def bind():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            if request.json["ident"] not in rooms:
                return "That room was not found"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((request.json["host"], request.json["port"]))
            rooms[request.json["ident"]].listeners[(request.json["host"], request.json["port"])] = sock
            return "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/unbind", methods = ["POST"])
def unbind():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            if request.json["ident"] not in rooms:
                return "That room was not found"
            gid = (request.json["host"], request.json["port"])
            rooms[request.json["ident"]].listeners[gid].sendall(b"X\x00\x00")
            del rooms[request.json["ident"]].listeners[gid]
            return "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/msg", methods = ["POST"])
def msg():
    if request.json["username"] in users:
        if request.json["password"] == users[request.json["username"]]:
            if request.json["ident"] not in rooms:
                return "That room was not found"
            response = rooms[request.json["ident"]].post(request.json["username"], request.json["message"])
            return response or "Y"
        else:
            return "Incorrect password"
    else:
        return "That user was not found"

@app.route("/nameof/<username>")
def nameof(username):
    return names[username] if username in names else ""

@app.route("/roomname/<room>")
def roomname(room):
    return rooms[room].name if room in rooms else ""

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = False)
