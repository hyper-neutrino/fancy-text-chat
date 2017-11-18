def removeFormatting(string):
    while string.endswith("\033[0m"):
        string = string[:-4]
    while string.startswith("\033["):
        string = string[4:]
    return string
