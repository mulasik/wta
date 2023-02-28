import re

TRAILING_WS_RE = re.compile(r"(\s+|\n+|\t+)$")
ONLY_WS_RE = re.compile(r"^(\s+|\n+|\t+)$")
INITIAL_WS_RE = re.compile(r"^(\s+|\n+|\t+)")
