from elphie.sxml import Xml

import xml.etree.ElementTree as et
import subprocess


class RendererSVG:

    def __init__(self):
        self.xml = None

    def begin(self, width, height):
        self.width = width
        self.height = height
        self.xml = Xml()
        self.xml.element("svg")
        self.xml.set("xmlns", "http://www.w3.org/2000/svg")
        self.xml.set("width", width)
        self.xml.set("height", height)

    def end(self):
        self.xml.close("svg")

    def draw_text(self, x, y, parsed_text, style, styles):
        render_text(self.xml, x, y, parsed_text, style, styles)

    def draw_rect(self,
                  rect,
                  fill_color=None,
                  color=None,
                  stroke_width=None,
                  rx=None,
                  ry=None):
        xml = self.xml
        xml.element("rect")
        xml.set("x", rect.x)
        xml.set("y", rect.y)
        if rx is not None:
            xml.set("rx", rx)
        if ry is not None:
            xml.set("ry", ry)
        xml.set("width", rect.width)
        xml.set("height", rect.height)

        style = []
        if fill_color is None and color is None:
            color = "black"
        if fill_color is not None:
            style.append("fill:" + str(fill_color))
        if color is not None:
            style.append("stroke:" + str(color))
        if stroke_width is not None:
            style.append("stoke-width:" + str(stroke_width))
        xml.set("style", ";".join(style))
        xml.close()

    def write(self, filename):
        self.xml.write(filename)

    def to_string(self):
        return self.xml.to_string()

    def get_text_size_query_key(self, style, styles, text):
        xml = Xml()
        xml.element("svg")
        render_text(xml, 0, 0, text, style, styles, id="t1")
        xml.close()
        self.svg = xml.to_string()
        self.style = style
        return ("textsize", self.svg)

    def get_text_size_query(self, style, styles, text):
        key = self.get_text_size_query_key(style, styles, text)
        svg = key[1]

        def compute():
            width = float(run_inkscape(("--query-id=t1", "-W"), None, svg))
            line_height = style.size * style.line_spacing
            lines = 1
            for (token, value) in text:
                if token == "newline":
                    lines += value
            height = lines * line_height
            return width, height

        return key, compute

    def draw_image(self, svgstring, x, y, scale=1.0):
        self.xml.element("g")
        transform = ["translate({}, {})".format(x, y)]
        if scale != 1.0 and scale is not None:
            transform.append("scale({})".format(scale))
        self.xml.set("transform", " ".join(transform))
        self.xml.raw_text(svgstring)
        self.xml.close()

    def get_image_size(self, filename, scale):
        root = et.parse(filename).getroot()
        width = float(root.get("width"))
        height = float(root.get("height"))
        return width, height


def set_font_from_style(xml, style):
    if style.font:
        xml.set("font-family", style.font)
    if style.size:
        xml.set("font-size", style.size)
    s = ""
    if style.color:
        s += "fill:{};".format(style.color)
    if style.bold:
        s += "font-weight: bold;"
    if style.italic:
        s += "font-style: italic;"
    if s:
        xml.set("style", s)


def render_text(xml, x, y, parsed_text, style, styles, id=None):

    xml.element("text")

    if id is not None:
        xml.set("id", id)
    xml.set("x", x)
    xml.set("y", y)

    if style.align == "center":
        xml.set("text-anchor", "middle")
    elif style.align == "right":
        xml.set("text-anchor", "end")
    elif style.align == "left":
        xml.set("text-anchor", "left")

    set_font_from_style(xml, style)
    line_size = style.size * style.line_spacing
    active_styles = [style]
    xml.element("tspan")
    for token_type, value in parsed_text:
        if token_type == "text":
            xml.text(value)
        elif token_type == "newline":
            for s in active_styles:
                xml.close()  # tspan
            for i, s in enumerate(active_styles):
                xml.element("tspan")
                xml.set("xml:space", "preserve")
                if i == 0:
                    xml.set("x", x)
                    xml.set("dy", line_size * value)
                set_font_from_style(xml, s)
        elif token_type == "begin":
            s = styles[value]
            active_styles.append(s)
            xml.element("tspan")
            xml.set("xml:space", "preserve")
            set_font_from_style(xml, s)
        elif token_type == "end":
            xml.close()
            active_styles.pop()
        else:
            raise Exception("Invalid token")

    for s in active_styles:
        xml.close()  # tspan
    xml.close("text")  # text


def run_inkscape(extra_args, filename=None, stdin=None):
    if filename is None:
        filename = "/dev/stdin"
    with open("/dev/null", "w") as devnull:
        args = ("/usr/bin/inkscape",
                "--without-gui") + extra_args + (filename,)
        p = subprocess.Popen(args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=devnull)
        stdout, stderr = p.communicate(stdin.encode("utf-8"))
        return stdout


def string_to_pixels(text):
    suffix = ""
    while text and text[-1].isalpha():
        suffix = text[-1] + suffix
        text = text[:-1]
    if suffix == "mm":
        factor = 3.543307
    elif suffix == "cm":
        factor = 35.43307
    else:
        factor = 1.0
    return float(text) * factor
