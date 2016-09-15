
from elphie.textparser import parse_text
import lxml.etree as et
import elphie.svg as svg
from elphie.highlight import highlight_code
from elphie.utils import SizeRequest

from copy import deepcopy


def normalize_show(value):
    if isinstance(value, int):
        return (value, None)
    if isinstance(value, tuple) and len(value) == 2:
        return value
    raise Exception("Invalid show value: '{}'".format(repr(value)))


class Element:

    childs = ()
    text_style = None

    def __init__(self, show):
        self.show = show

    def get_max_step(self):
        start, end = normalize_show(self.show)
        if end is None:
            return start
        else:
            return end

    def is_visible(self, ctx):
        start, end = normalize_show(self.show)
        return start <= ctx.step and (end is None or ctx.step <= end)

    def render(self, ctx, rect):
        if self.is_visible(ctx):
            ctx.push(self)
            self.render_body(ctx, rect)
            ctx.pop()

    def gather_queries(self, ctx, queries):
        ctx.push(self)
        self._gather_queries(ctx, queries)
        for child in self.childs:
            child.gather_queries(ctx, queries)
        ctx.pop()

    def _gather_queries(self, ctx, queries):
        pass


class TextBase(Element):

    def __init__(self, show, text):
        super().__init__(show)
        self.text = text
        self.emphasis = []

    def get_max_step(self):
        start, end = normalize_show(self.show)
        ends = [e if e is not None else s
                for line_number, (s, e), color in self.emphasis]
        ends.append(start)
        if end:
            ends.append(end)
        return max(ends)

    def consecutive_line_emphasis(
            self, start=1, predicate_fn=None, color=None):
        step = start
        for i, line in enumerate(self.text.split("\n")):
            if predicate_fn is None or predicate_fn(i, line):
                self.line_emphasis(i + 1, (step, step), color=color)
                step += 1

    def line_emphasis(self,
                      line_numbers=None,
                      show=1,
                      color=None,
                      prefix=None,
                      infix=None):
        if isinstance(line_numbers, int):
            line_numbers = (line_numbers,)
        elif line_numbers is None:
            line_numbers = tuple(range(1, self.text.count("\n") + 2))
        else:
            line_numbers = tuple(line_numbers)

        if prefix is not None:
            lines = self.text.split("\n")
            line_numbers = tuple(i for i in line_numbers
                                 if lines[i - 1].lstrip().startswith(prefix))
        if infix is not None:
            lines = self.text.split("\n")
            line_numbers = tuple(i for i in line_numbers
                                 if infix in lines[i - 1])
        if line_numbers:
            self.emphasis.append((line_numbers, normalize_show(show), color))


class Text(TextBase):

    def __init__(self, text, role, show):
        text = text.strip()
        super().__init__(show, text)
        self.content = parse_text(text)
        self.role = role
        self.show = show

    def get_size_request(self, ctx):
        return ctx.theme.get_text_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_text(ctx, rect, self)

    def _gather_queries(self, ctx, queries):
        ctx.theme.gather_text_queries(ctx, queries, self)


class Code(TextBase):

    def __init__(self, code, language, show):
        code = code.strip()
        super().__init__(show, code)
        self.content = highlight_code(code, language)
        self.language = language

    def get_size_request(self, ctx):
        return ctx.theme.get_code_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_code(ctx, rect, self)

    def _gather_queries(self, ctx, queries):
        ctx.theme.gather_code_queries(ctx, queries, self)


class Shell(TextBase):

    def __init__(self, text, show):
        text = text.strip()
        super().__init__(show, text)
        self.content = parse_text(text)
        self.show = show
        self.size_cache = None

    def get_size_request(self, ctx):
        return ctx.theme.get_shell_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_shell(ctx, rect, self)

    def _gather_queries(self, ctx, queries):
        ctx.theme.gather_shell_queries(ctx, queries, self)


class Box(Element):

    def __init__(self, role, show=1):
        super().__init__(show)
        self.role = role
        self.layers = [[]]

    @property
    def childs(self):
        return sum(self.layers, [])

    def get_max_step(self):
        steps = [element.get_max_step()
                 for layer in self.layers
                 for element in layer]
        steps.append(super().get_max_step())
        return max(steps)

    def new_layer(self):
        self.layers.append([])
        return self

    def add(self, element):
        self.layers[-1].append(element)

    def box(self, show=1):
        element = Box(show)
        self.add(element)
        return element

    def text(self, text, role=None, show=1):
        element = Text(text, role, show)
        self.add(element)
        return element

    def h1(self, text, show=1):
        return self.text(text, role="h1", show=show)

    def h2(self, text, show=1):
        return self.text(text, role="h2", show=show)

    def h3(self, text, show=1):
        return self.text(text, role="h3", show=show)

    def image(self, filename, scale=None, show=1):
        element = Image(filename, scale, show)
        self.add(element)
        return element

    def list(self, show=1):
        element = List(show)
        self.add(element)
        return element

    def frame(self, title, show=1):
        element = Frame(title, show)
        self.add(element)
        return element.box

    def code(self, code, language, show=1):
        element = Code(code, language, show)
        self.add(element)
        return element

    def shell(self, text, show=1):
        element = Shell(text, show)
        self.add(element)
        return element

    def columns(self, show=1):
        element = Columns(show)
        self.add(element)
        return element

    def space(self, height, width=0):
        element = Space(width, height)
        self.add(element)
        return element

    def separator(self, thickness=None, show=1):
        element = Separator(True, thickness, show)
        self.add(element)
        return element

    def get_size_request(self, ctx):
        return ctx.theme.get_box_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_box(ctx, rect, self)


def _parse_label(element):
    label = element.get("{http://www.inkscape.org/namespaces/inkscape}label")
    if label is None:
        return None
    pos = label.find("**")
    if pos == -1:
        return None
    label = label[pos + 2:].strip()
    if label.isdigit():
        return int(label), None
    parts = label.split("-")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0]), int(parts[1])
    return None


class Image(Element):

    def __init__(self, filename, scale, show):
        self.filename = filename
        self.root = et.parse(filename).getroot()
        self.scale = scale
        self.width = svg.string_to_pixels(self.root.get("width"))
        self.height = svg.string_to_pixels(self.root.get("height"))
        if scale is not None:
            self.width *= scale
            self.height *= scale

        global_start, global_end = normalize_show(show)
        inner_max_step = 1
        for element in self.root.iter():
            value = _parse_label(element)
            if value is None:
                continue
            start, max_step = value
            if max_step is None and start >= inner_max_step:
                inner_max_step = start
            if max_step is not None and max_step >= inner_max_step:
                inner_max_step = max_step

        self.max_step = inner_max_step + global_start - 1
        self.has_inner_steps = inner_max_step > 1
        self.start_step = global_start
        super().__init__(show)

    def get_max_step(self):
        return self.max_step

    def get_data(self, step):
        hidden = []
        def find_hidden_elements(element):
            for child in list(element):
                value = _parse_label(child)
                if value is not None:
                    start, end = value
                    if step < start or (end is not None and step > end):
                        hidden.append((element, child))
                        continue
                else:
                    find_hidden_elements(child)

        if not self.has_inner_steps:
            return et.tostring(self.root).decode()

        step -= self.start_step - 1
        root = deepcopy(self.root)
        find_hidden_elements(root)
        for element, child in hidden:
            element.remove(child)
        return et.tostring(root).decode()

    def get_size_request(self, ctx):
        return ctx.theme.get_image_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_image(ctx, rect, self)

    def _gather_queries(self, ctx, queries):
        ctx.theme.gather_image_queries(ctx, queries, self)


class List(Element):

    def __init__(self, show):
        super().__init__(show)
        self.elements = []
        self.show = show

    def get_max_step(self):
        steps = [element.get_max_step() for element in self.elements]
        steps.append(super().get_max_step())
        return max(steps)

    @property
    def childs(self):
        return self.elements

    def item(self, show=1):
        box = Box("list_item", show)
        self.elements.append(box)
        return box

    def render_body(self, ctx, rect):
        ctx.theme.render_list(ctx, rect, self)

    def get_size_request(self, ctx):
        return ctx.theme.get_list_size_request(ctx, self)

    def _gather_queries(self, ctx, queries):
        ctx.theme.gather_list_queries(ctx, queries, self)


class Frame(Element):

    def __init__(self, title, show):
        super().__init__(show)
        self.box = Box("frame_body")
        self.title = title

    @property
    def childs(self):
        return (self.box,)

    def get_size_request(self, ctx):
        return ctx.theme.get_frame_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_frame(ctx, rect, self)

    def _gather_queries(self, ctx, queries):
        ctx.theme.gather_frame_queries(ctx, queries, self)


class Columns(Element):

    def __init__(self, show):
        super().__init__(show)
        self.elements = []
        self.ratios = []

    @property
    def childs(self):
        return self.elements

    def get_max_step(self):
        steps = [element.get_max_step() for element in self.elements]
        steps.append(super().get_max_step())
        return max(steps)

    def column(self, ratio=1, show=1):
        box = Box("list_item", show)
        self.elements.append(box)
        self.ratios.append(ratio)
        return box

    def space(self, width, height=0):
        element = Space(width, height)
        self.elements.append(element)
        self.ratios.append(0)
        return element

    def separator(self, thickness=None, show=1):
        separator = Separator(False, thickness, show)
        self.elements.append(separator)
        self.ratios.append(0)
        return separator

    def get_size_request(self, ctx):
        return ctx.theme.get_columns_size_request(ctx, self)

    def render_body(self, ctx, rect):
        ctx.theme.render_columns(ctx, rect, self)


class Separator(Element):

    def __init__(self, horizontal, thickness, show):
        super().__init__(show)
        self.horizontal = horizontal
        self.thickness = thickness

    def get_size_request(self, ctx):
        return ctx.theme.get_separator_size_request(ctx, self)

    def render_body(self, ctx, rect):
        return ctx.theme.render_separator(ctx, rect, self)


class Space(Element):

    def __init__(self, width, height):
        super().__init__(1)
        self.width = width
        self.height = height

    def get_size_request(self, ctx):
        return SizeRequest(self.width, self.height)

    def render_body(self, ctx, rect):
        pass
