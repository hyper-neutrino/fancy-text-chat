import sys

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
        return chr(msvcrt.getch())

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

def getInput(**kwargs):
    return list(getInputLive(**kwargs))[-1]

def getInputLive(mask = False, allowed = [], disallowed = [], escapes = {}, maxchars = -1, clearafter = False, prefix = "", suffix = ""):
    sys.stdout.write("*" * len(prefix + suffix) if mask else prefix + suffix)
    sys.stdout.write("\033[1D" * len(suffix))
    sys.stdout.flush()
    while True:
        key = getKey()
        op = len(prefix)
        os = len(suffix)
        if ord(key) == 13:
            break
        elif ord(key) == 127:
            if prefix:
                prefix = prefix[:-1]
        elif ord(key) == 126:
            if suffix:
                suffix = suffix[1:]
        elif ord(key) == 27:
            next = getKey()
            if next in escapes:
                yield escapes[next]
                raise StopIteration
            elif ord(next) == 27:
                yield ""
                raise StopIteration
            elif next == "[":
                next = getKey()
                if next == "C":
                    if suffix:
                        prefix += suffix[0]
                        suffix = suffix[1:]
                elif next == "D":
                    if prefix:
                        suffix = prefix[-1] + suffix
                        prefix = prefix[:-1]
                elif next == "H":
                    suffix = prefix + suffix
                    prefix = ""
                elif next == "F":
                    prefix += suffix
                    suffix = ""
        elif (allowed == [] or key in allowed) and (key not in disallowed) and (maxchars == -1 or len(prefix) + len(suffix) < maxchars):
            prefix += key
        sys.stdout.write("\033[1C" * os + "\033[1D \033[1D" * (os + op))
        sys.stdout.write("*" * len(prefix + suffix) if mask else prefix + suffix)
        sys.stdout.write("\033[1D" * len(suffix))
        sys.stdout.flush()
        yield (prefix, suffix)
    if clearafter:
        sys.stdout.write("\033[1C" * len(suffix) + "\033[1D \033[1D" * (len(suffix) + len(prefix)))
        sys.stdout.flush()
    yield prefix + suffix

if __name__ == '__main__':
    for i in range(10): print(ord(getKey()))
