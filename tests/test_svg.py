import utils  # noqa

from elphie.svg import RendererSVG
from elphie.textstyle import TextStyle
from elphie.textparser import parse_text
from elphie.utils import Rect


def test_svg_text():
    r = RendererSVG()
    r.begin(300, 300)

    style = TextStyle()
    style.font = "Ubuntu"
    style.line_spacing = 1.2

    sizes = (10, 20, 30)
    colors = ("red", "green", "#0000FF")

    emph = TextStyle()
    emph.color = "orange"

    tt = TextStyle()
    tt.font = "Ubuntu Mono"

    styles = {
        "emph": emph,
        "tt": tt
    }

    text = parse_text("This ~emph{is\nWide}~tt{ Window~emph{!}}")

    for i, (s, c) in enumerate(zip(sizes, colors)):
        st = style.copy()
        st.size = s
        st.color = c
        r.draw_text(5, 70 * i + 20, text, st, styles)

    r.end()
    r.write(utils.output_name("text.svg"))


def test_svg_rect():
    r = RendererSVG()
    r.begin(300, 300)

    rc = Rect(0, 0, 100, 300)
    r.draw_rect(rc, "red")

    rc = Rect(100, 0, 100, 300)
    r.draw_rect(rc, "green")

    rc = Rect(20, 50, 260, 40)
    r.draw_rect(rc, fill_color="white", color="#000055", stroke_width=20)

    rc = Rect(20, 150, 260, 40)
    r.draw_rect(
        rc, fill_color="white", color="#000055", stroke_width=20, rx=50, ry=20)

    r.end()
    r.write(utils.output_name("rect.svg"))
