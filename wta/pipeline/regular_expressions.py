import re

TRAILING_WS_RE = re.compile(r"(\s+|\n+|\t+)\Z")
ONLY_WS_RE = re.compile(r"\A(\s+|\n+|\t+)\Z")
INITIAL_WS_RE = re.compile(r"\A(\s+|\n+|\t+)")
