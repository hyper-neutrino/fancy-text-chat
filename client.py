import os, sys, hashlib, requests, time, pickle, socket, threading, utils

from current_url import URL

from getch import *

def cols():
    return os.get_terminal_size().columns

def rows():
    return os.get_terminal_size().lines

def clear(rowdiff = 0):
    sys.stdout.write("\033[1;1H" + "\n".join([" " * cols()] * (rows() - rowdiff)) + "\033[1;1H")

ID = None

hashstr = lambda s: hashlib.sha384(bytearray(s, "UTF8")).hexdigest()

bold = lambda s: "\033[1m" + s + "\033[0m"
italic = lambda s: "\033[3m" + s + "\033[0m"
underline = lambda s: "\033[4m" + s + "\033[0m"
blink = lambda s: "\033[5m" + s + "\033[0m"

while True:
    clear()
    print(bold("Welcome to Neutrino Chat!"))
    print()
    print("[l]ogin")
    print("[n]ew user")
    print("[q]uit")
    code = getOption([113, 108, 110])
    if code == 113:
        exit(0)
    if code == 108:
        clear()
        print(bold("=== Login [empty username aborts] ==="))
        print()
        print("Username:", end = " ")
        sys.stdout.flush()
        username = getInput()
        if username == "": continue
        print("\nPassword:", end = " ")
        sys.stdout.flush()
        password = hashstr(getInput(mask = True))
        cred = { "username": username, "password": password }
        r = requests.post(URL + "/login", json = cred)
        if r.text == "Y":
            ID = cred
        else:
            print("\n" + r.text)
            time.sleep(1)
            continue
        break
    elif code == 110:
        clear()
        print(bold("=== New User [empty username aborts] ==="))
        print()
        print("Username:", end = " ")
        sys.stdout.flush()
        username = getInput(maxchars = 30)
        if username == "": continue
        print("\nDisplay Name:", end = " ")
        sys.stdout.flush()
        displayn = getInput(maxchars = 30)
        if displayn == "": continue
        print("\nPassword:", end = " ")
        sys.stdout.flush()
        password = getInput(mask = True)
        print("\nPassword Again:", end = " ")
        sys.stdout.flush()
        repeat = getInput(mask = True)
        if password != repeat:
            print("\nPasswords did not match")
            time.sleep(1)
            continue
        password = hashstr(password)
        cred = { "username": username, "password": password, "displayn": displayn }
        r = requests.post(URL + "/newuser", json = cred)
        if r.text == "Y":
            ID = { "username": username, "password": password }
        else:
            print("\n" + r.text)
            time.sleep(1)
            continue
        break

displayn = requests.get(URL + "/nameof/" + ID["username"]).text

while True:
    clear()
    print("Welcome, " + displayn + "!")
    print()
    print("[p]references")
    print("[a]ccount settings")
    print("[j]oin chatroom")
    print("[c]reate chatroom")
    print("[q]uit")
    code = getOption([112, 97, 106, 99, 113])
    if code == 112:
        clear()
        print(bold("=== Preferences ==="))
        print()
        print("[q]uit")
        code = getOption([113])
        if code == 113:
            continue
    elif code == 97:
        clear()
        print(bold("=== Account Settings ==="))
        print()
        print("[c]hange display name")
        print("[p]assword change")
        print("[f]ormatting options for display name")
        print("[q]uit")
        code = getOption([99, 112, 102, 113])
        if code == 99:
            clear()
            print(bold("=== Change Display Name [esc aborts] ==="))
            print()
            print("Display Name:", end = " ")
            sys.stdout.flush()
            name = getInput(maxchars = 30)
            if name == "": continue
            r = requests.post(URL + "/changename", json = { "username": ID["username"], "password": ID["password"], "displayn": name })
            if r.text == "Y":
                displayn = name
                continue
            else:
                print("\n" + r.text)
                time.sleep(1)
                continue
        elif code == 112:
            clear()
            print(bold("=== Change Password [esc aborts] ==="))
            print()
            print("Enter current password:", end = " ")
            sys.stdout.flush()
            pwd = getInput(mask = True)
            if pwd == "": continue
            print("\nEnter new password:", end = " ")
            sys.stdout.flush()
            np = getInput(mask = True)
            if np == "": continue
            print("\nRepeat new password:", end = " ")
            if getInput(mask = True) != np:
                print("\nPasswords don't match!")
                time.sleep(1)
                continue
            r = requests.post(URL + "/changepwd", json = { "username": ID["username"], "password": hashstr(pwd), "newpass": hashstr(np) })
            if r.text == "Y":
                continue
            else:
                print("\n" + r.text)
                time.sleep(1)
                continue
        elif code == 102:
            clear()
            print(bold("=== Change Name Formatting [esc aborts, enter saves] ==="))
            print()
            name = displayn
            while name.endswith("\033[0m"):
                name = name[:-4]
            mode = 0
            color = "-1"
            colors = ["32", "34", "35", "36", "37", "90", "92", "93", "94", "95", "96", "97", "-1"]
            c_to_names = {
                "32": "Dark Green",
                "34": "Dark Blue",
                "35": "Magenta",
                "36": "Cyan",
                "37": "Grey",
                "90": "Dark Grey",
                "92": "Light Green",
                "93": "Light Yellow",
                "94": "Light Blue",
                "95": "Bright Pink",
                "96": "Light Aqua",
                "97": "White",
                "-1": "Default (Console Specific)"
            }
            while name.startswith("\033["):
                code = name[2:name.find("m")]
                name = name[3 + len(code):]
                if code in colors:
                    color = code
                else:
                    mode |= 2 ** "134".index(code)
            print("[b]old: " + "NY"[mode & 1])
            print("[i]talic: " + "NY"[(mode & 2) >> 1])
            print("[u]nderline: " + "NY"[(mode & 4) >> 2])
            print("[c]ycle color: " + ("\033[%sm" % color) * (color != "-1") + c_to_names[color] + "\033[0m" * (color != "-1"))
            while True:
                code = getOption([98, 105, 117, 99, 13, 27])
                if code == 13:
                    prefix = ""
                    if mode & 1: prefix += "\033[1m"
                    if mode & 2: prefix += "\033[3m"
                    if mode & 4: prefix += "\033[4m"
                    if color != "-1": prefix += "\033[%sm" % color
                    suffix = "\033[0m" * bool(prefix)
                    _display = prefix + name + suffix
                    time.sleep(1)
                    r = requests.post(URL + "/changename", json = { "username": ID["username"], "password": ID["password"], "displayn": _display })
                    if r.text != "Y":
                        print("\n" + r.text)
                        time.sleep(1)
                    else:
                        displayn = _display
                    break
                elif code == 27:
                    break
                else:
                    if code == 98:
                        mode ^= 1
                    elif code == 105:
                        mode ^= 2
                    elif code == 117:
                        mode ^= 4
                    elif code == 99:
                        color = colors[(colors.index(color) + 1) % len(colors)]
                    clear()
                    print(bold("=== Change Name Formatting [esc aborts, enter saves] ==="))
                    print()
                    print("[b]old: " + "NY"[mode & 1])
                    print("[i]talic: " + "NY"[(mode & 2) >> 1])
                    print("[u]nderline: " + "NY"[(mode & 4) >> 2])
                    print("[c]ycle color: " + ("\033[%sm" % color) * (color != "-1") + c_to_names[color] + "\033[0m" * (color != "-1"))
            continue
        elif code == 113:
            continue
    elif code == 99:
        clear()
        print(bold("=== Make a Chatroom [empty ID aborts] ==="))
        print()
        print("Enter room ID:", end = " ")
        sys.stdout.flush()
        room = getInput(maxchars = 30)
        if room == "":
            continue
        print("\nEnter name:", end = " ")
        sys.stdout.flush()
        name = getInput(maxchars = 30)
        if name == "":
            continue
        print("\nEnter default permission level (- = no access, 0 = read, 1 = post, 2 = edit, 3 = delete, 4 = moderate, 5 = owner):", end = " ")
        sys.stdout.flush()
        def_perm = getInput(allowed = ["-", "0", "1", "2", "3", "4", "5"], maxchars = 1)
        if def_perm == "":
            continue
        def_perm = -1 if def_perm == "-" else int(def_perm)
        r = requests.post(URL + "/makeroom", json = {
            "username": ID["username"],
            "password": ID["password"],
            "ident": room,
            "name": name,
            "def_perm": def_perm
        })
        if r.text != "Y":
            print("\n" + r.text)
            time.sleep(1)
        continue
    elif code == 106:
        clear()
        print(bold("=== Join a Chatroom [empty ID aborts] ==="))
        print()
        print("Enter room ID:", end = " ")
        sys.stdout.flush()
        room = getInput()
        if room == "":
            continue
        r = requests.post(URL + "/getmessages", json = { "username": ID["username"], "password": ID["password"], "ident": room })
        if r.text[0] == "Y":
            messages = pickle.loads(bytearray(map(ord, r.text[1:])))
            temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp.connect(("8.8.8.8", 80))
            host = temp.getsockname()[0]
            temp.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("", 0))
            port = sock.getsockname()[1]
            sock.listen(1)
            requests.post(URL + "/bind", json = { "username": ID["username"], "password": ID["password"], "ident": room, "host": host, "port": port })
            conn, addr = sock.accept()
            roomname = requests.get(URL + "/roomname/" + room).text
            prefix, suffix = "", ""
            display_names = {}
            def draw():
                clear()
                print(roomname)
                print()
                colcount = cols()
                avail = rows() + (-len(roomname) // colcount) + ((-len(prefix) - len(suffix)) // colcount) - 2
                lines = []
                for message in messages:
                    if message[0] not in display_names:
                        display_names[message[0]] = requests.get(URL + "/nameof/" + message[0]).text
                    name = display_names[message[0]]
                    cost = -(-(len(name) + len(utils.removeFormatting(message[1])) + 2) // colcount)
                    if cost > avail:
                        break
                    avail -= cost
                    lines.append(name + ": " + message[1])
                print("\n".join(lines))
                print(prefix + suffix + "\033[1D" * len(suffix))
            draw()
            def poll():
                while True:
                    incoming = ["", "", ""]
                    data = chr(conn.recv(1)[0])
                    incoming[0] = data
                    for i in [1, 2]:
                        while True:
                            data = "".join(map(chr, conn.recv(1)))
                            if data == "\x00":
                                break
                            else:
                                incoming[i] += data
                    if incoming[0] == "X": break
                    if incoming[0] == "P": messages.append((incoming[1], incoming[2]))
                    draw()
            thread = threading.Thread(target = poll)
            thread.start()
            while True:
                message = 0
                for message in getInputLive(maxchars = 500, clearafter = True, escapes = {"\033": 0}, prefix = prefix, suffix = suffix):
                    if isinstance(message, tuple):
                        prefix, suffix = message
                prefix, suffix = "", ""
                if message:
                    requests.post(URL + "/msg", json = { "username": ID["username"], "password": ID["password"], "ident": room, "message": message })
                if message == 0:
                    break
            requests.post(URL + "/unbind", json = { "username": ID["username"], "password": ID["password"], "ident": room, "host": host, "port": port })
            thread.join()
            continue
        else:
            print("\n" + r.text)
            time.sleep(1)
            continue
    break
