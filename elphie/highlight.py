
from elphie.textstyle import TextStyle
from elphie.textparser import normalize_tokens

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.formatter import Formatter


class ElphieFormatter(Formatter):

    def __init__(self):
        super().__init__()
        self.stream = []

    def format(self, tokensource, outfile):
        stream = self.stream
        for ttype, value in tokensource:
            if value == "\n":
                stream.append(("newline", 1))
            else:
                stream.append(("begin", str(ttype)))
                stream.append(("text", value))
                stream.append(("end", None))

def highlight_code(code, language):
    lexer = get_lexer_by_name(language)
    formatter = ElphieFormatter()
    highlight(code, lexer, formatter)
    stream = formatter.stream
    if stream and stream[-1] == (("newline", None)):
        stream = stream[:-1]
    return normalize_tokens(stream)

def make_style(style_name):
    results = {}
    for token, s in get_style_by_name(style_name):
        style = TextStyle()
        if s["color"]:
            style.color = "#" + s["color"]
        if s["bold"]:
            style.bold = True
        if s["italic"]:
            style.italic = True
        results[str(token)] = style
    return results
