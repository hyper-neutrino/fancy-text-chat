import re

def removeFormatting(string):
    return re.sub("\033\\[\\d+m", "", string)
