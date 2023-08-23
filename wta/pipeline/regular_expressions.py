import re

# TODO: consider converting text to unicode


# INITIAL_WS_RE = re.compile(r"\A((\s+\n*\t*)+|(\n+\t*)+|(\t+\n*)+)")
# TRAILING_WS_RE = re.compile(r"((\s+\n*\t*)+|(\n+\t*)+|(\t+\n*)+)\Z")
# ONLY_WS_RE = re.compile(r"\A((\s+\n*\t*)+|(\n+\t*)+|(\t+\n*)+)\Z")
# MIDDLE_WS_RE = re.compile(r"(\n+\t*)+|(\r+\n*\t*)+|(\t+\n*)+|(\t+\r*)+")
PRECEDING_END_CITATION = re.compile(r"\A»")

# SIN
S_RE = r"[^\S^\n^\t^\r^\v]+"
PRECEDING_S_RE = re.compile(fr"\A{S_RE}")
TRAILING_S_RE = re.compile(fr"{S_RE}\Z")
ONLY_S_RE = re.compile(fr"\A{S_RE}\Z")

# PIN
PWS_RE = r"((\n+\t*)+|(\r+\n*\t*)+|(\t+\r*\n*)+|(\v+\r*\n*)+)"  # paragraph whitespace characters (pws): \r - carriage return, \n - newline, \t - tab, \v - vertical tab
PRECEDING_PWS_RE = re.compile(fr"\A{PWS_RE}")
TRAILING_PWS_RE = re.compile(fr"{PWS_RE}\Z")
ONLY_PWS_RE = re.compile(fr"\A{PWS_RE}\Z")
MIDDLE_PWS_RE = re.compile(PWS_RE)

