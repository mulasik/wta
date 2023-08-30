class Match:
    ruleId: str
    message: str
    replacements: list[str]
    offsetInContext: int
    context: str
    offset: int
    errorLength: int
    category: str
    ruleIssueType: str
    sentecne: str

class LanguageTool:
    def __init__(self, language: str = ...) -> None: ...
    def check(self, text: str) -> list[Match]: ...
