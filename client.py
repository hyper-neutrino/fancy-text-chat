import os, sys, hashlib, requests, time

from current_url import URL

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen. From http://code.activestate.com/recipes/134892/"""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchMacCarbon()
            except(AttributeError, ImportError):
                self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt #see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

def getKey():
    inkey = _Getch()
    for i in range(sys.maxsize):
        k = inkey()
        if k != '': break
    return k

def getOption(options):
    code = 0
    while True:
        code = ord(getKey())
        if code in options: return code

size = os.get_terminal_size()

def clear():
    sys.stdout.write("\033[0;0H" + "\n".join([" " * size.columns] * size.lines) + "\033[0;0H")

def getInput(mask = False):
    data = ""
    while True:
        key = getKey()
        if ord(key) == 13:
            break
        elif ord(key) == 127:
            if len(data) > 0:
                data = data[:-1]
                sys.stdout.write("\033[1D \033[1D")
                sys.stdout.flush()
        elif ord(key) == 27:
            return ""
        else:
            data += key
            sys.stdout.write("*" if mask else key)
            sys.stdout.flush()
    return data

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
        password = hashstr(getInput(True))
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
        username = getInput()
        if username == "": continue
        print("\nDisplay Name:", end = " ")
        sys.stdout.flush()
        displayn = getInput()
        if displayn == "": continue
        print("\nPassword:", end = " ")
        sys.stdout.flush()
        password = getInput(True)
        print("\nPassword Again:", end = " ")
        sys.stdout.flush()
        repeat = getInput(True)
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
    print("[q]uit")
    code = getOption([112, 97, 106, 113])
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
            name = getInput()
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
            pwd = getInput(True)
            if pwd == "": continue
            print("\nEnter new password:", end = " ")
            sys.stdout.flush()
            np = getInput(True)
            if np == "": continue
            print("\nRepeat new password:", end = " ")
            if getInput(True) != np:
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
            while name.startswith("\033["):
                code = name[2]
                name = name[4:]
                mode |= 2 ** "134".index(code)
            print("[b]old: " + "NY"[mode & 1])
            print("[i]talic: " + "NY"[(mode & 2) >> 1])
            print("[u]nderline: " + "NY"[(mode & 4) >> 2])
            while True:
                code = getOption([98, 105, 117, 13, 27])
                if code == 13:
                    prefix = ""
                    if mode & 1: prefix += "\033[1m"
                    if mode & 2: prefix += "\033[3m"
                    if mode & 4: prefix += "\033[4m"
                    suffix = "\033[0m" * bool(prefix)
                    _display = prefix + name + suffix
                    r = requests.post(URL + "/changename", json = { "username": ID["username"], "password": ID["password"], "displayn": displayn })
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
                    clear()
                    print(bold("=== Change Name Formatting [esc aborts, enter saves] ==="))
                    print()
                    print("[b]old: " + "NY"[mode & 1])
                    print("[i]talic: " + "NY"[(mode & 2) >> 1])
                    print("[u]nderline: " + "NY"[(mode & 4) >> 2])
            continue
        elif code == 113:
            continue
    break
