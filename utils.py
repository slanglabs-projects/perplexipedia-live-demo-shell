import re

class SourceItem:
    def __init__(self, id, url, snippet, content=None, index=-1):
        self.id = id
        self.url = url
        self.snippet = snippet
        self.content = content
        self.index = index


def escape_braces(text: str) -> str:
    text = re.sub(r"(?<!\{)\{(?!\{)", r"{{", text)  # noqa
    text = re.sub(r"(?<!\})\}(?!\})", r"}}", text)  # noqa
    return text


def get_md_normal_text(text):
    return "<p> {} </p>".format(text)


def get_md_hyperlink(text):
    return "<a href={}>{}</a>".format(text, text)


def get_md_list(arr):
    lis = ""
    for elem in arr:
        if "$" in elem:
            elem = elem.replace("$", "\\$")
        lis += "<li> {} </li>".format(elem)
    return "<list> {} </list>".format(lis)


def extract_citations(text):
    # Find all occurrences of strings within square brackets
    matches = re.findall(r"\[(.*?)\]", text)  # noqa
    # Split each match by comma and strip whitespace
    citations = [citation.strip() for match in matches for citation in match.split(",")]
    return citations
