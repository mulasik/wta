import re

# TODO: consider converting text to unicode


INITIAL_WS_RE = re.compile(r"\A((\s+\n*\t*)+|(\n+\t*)+|(\t+\n*)+)")
TRAILING_WS_RE = re.compile(r"((\s+\n*\t*)+|(\n+\t*)+|(\t+\n*)+)\Z")
ONLY_WS_RE = re.compile(r"\A((\s+\n*\t*)+|(\n+\t*)+|(\t+\n*)+)\Z")
MIDDLE_WS_RE = re.compile(r"(\n+\t*)+|(\r+\n*\t*)+|(\t+\n*)+|(\t+\r*)+")
