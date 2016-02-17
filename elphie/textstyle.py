
from copy import copy


class TextStyle:

    font = None
    size = None
    align = None
    line_spacing = None
    color = None
    bold = None
    italic = None

    attributes = ("font",
                  "size",
                  "align",
                  "line_spacing",
                  "color",
                  "bold",
                  "italic")

    def copy(self):
        return copy(self)

    def __repr__(self):
        s = ["<TextStyle"]
        for a in self.attributes:
            if getattr(self, a) is not None:
                s.append(" {}={}".format(a, getattr(self, a)))
        s.append(">")
        return "".join(s)


def merge(styles):
    if len(styles) == 1:
        return styles[0]

    t = TextStyle()
    for a in t.attributes:
        for style in reversed(styles):
            if getattr(style, a) is not None:
                setattr(t, a, getattr(style, a))
                break
    return t
