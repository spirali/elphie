
from elphie.utils import SizeRequest, Rect, merge_size_requests
from elphie.textstyle import TextStyle, merge
from elphie.textparser import parse_text
from elphie.elements import Frame, Box
from elphie.highlight import make_style


class Theme:

    bg_color = "white"
    major_color = "#86c800"
    minor_color = "#d2d9bd"
    text_color = "#86b800"
    text_emph_color = "#f6b800"
    text_alert_color = "#ff2800"

    frame_title_color = major_color
    frame_title_text_color = "white"
    frame_bg_color = "#f2ffcb"

    code_background_color = "#F0F0F0"
    code_background_emph_color = "#96d820"

    shell_background_color = "#101010"
    shell_background_emph_color = "#76a810"

    separator_thickness = 2
    separator_color = "#005000"

    def __init__(self):
        default_style = TextStyle()
        default_style.font = "Ubuntu"
        default_style.color = self.text_color
        default_style.size = 30
        default_style.line_spacing = 1.10
        default_style.align = "center"

        tt_style = TextStyle()
        tt_style.font = "Ubuntu Mono"

        code_style = TextStyle()
        code_style.font = "Ubuntu Mono"
        code_style.align = "left"
        code_style.color = "#222"

        shell_style = code_style.copy()
        shell_style.color = "white"

        shell_prompt_style = TextStyle()
        shell_prompt_style.color = "#7070F0"

        shell_cmd_style = TextStyle()
        shell_cmd_style.color = "#F0F070"
        shell_cmd_style.bold = True

        emph_style = TextStyle()
        emph_style.color = self.text_emph_color
        emph_style.italic = True

        alert_style = TextStyle()
        alert_style.color = self.text_alert_color
        alert_style.bold = True

        h1_style = TextStyle()
        h1_style.size = 60

        h2_style = TextStyle()
        h2_style.size = 40

        h3_style = TextStyle()
        h3_style.size = 35

        frame_style = TextStyle()

        frame_title_style = TextStyle()
        frame_title_style.color = self.frame_title_text_color
        frame_title_style.size = 35
        frame_title_style.align = "right"

        list_item_style = TextStyle()
        list_item_style.align = "left"

        self.text_styles = {
            "default": default_style,
            "tt": tt_style,
            "emph": emph_style,
            "alert": alert_style,
            "h1": h1_style,
            "h2": h2_style,
            "h3": h3_style,
            "code": code_style,
            "shell": shell_style,
            "shell_prompt": shell_prompt_style,
            "shell_cmd": shell_cmd_style,
            "frame": frame_style,
            "frame_title": frame_title_style,
            "list_item": list_item_style
        }

        for name, value in make_style("default").items():
            self.text_styles[name] = value

        self.title_style = default_style.copy()
        self.title_style.color = "white"
        self.title_style.align = "right"

        self.main_title_style = default_style.copy()
        self.main_title_style.color = "white"
        self.main_title_style.align = "center"
        self.main_title_style.size = 60

    def draw_text(self, ctx, x, y, text, style):
        if isinstance(text, str):
            text = parse_text(text)
        offset_x, offset_y = self.get_text_offset(style)
        if style.align == "left":
            x += offset_x
        elif style.align == "right":
            x -= offset_x
        ctx.renderer.draw_text(x,
                               y + style.size + offset_y,
                               text,
                               style,
                               ctx.text_styles)

    def render_slide(self, ctx):
        slide = ctx.slide
        renderer = ctx.renderer
        width = renderer.width
        height = renderer.height

        slide_rect = Rect(0, 0, width, height)
        renderer.draw_rect(slide_rect, self.bg_color)

        if slide.role == "title":
            title = slide.title
            if title is None:
                title = ""

            style = self.main_title_style
            rect = Rect(0, height / 2 - style.size * 1.2,
                        width, style.size * 2.4)
            renderer.draw_rect(rect, self.minor_color)
            rect = Rect(0, height / 2 - style.size, width, style.size * 2)
            renderer.draw_rect(rect, self.major_color)
            self.draw_text(ctx,
                           width / 2,
                           height / 2 - style.size * 0.8,
                           slide.title,
                           style)
            top = height / 2 + style.size
            slide_rect = Rect(0, top, width, height - top)
            ctx.slide.element.render(ctx, slide_rect)
            return

        if slide.title is None:
            ctx.slide.element.render(ctx, slide_rect)
            return

        top = 80
        rect = Rect(0, 0, width, top)
        renderer.draw_rect(rect, self.major_color)

        rect = Rect(0, top - 10, width, 10)
        renderer.draw_rect(rect, self.minor_color)

        self.draw_text(ctx, width - 40, 10,
                       ctx.slide.title, self.title_style)
        rect = Rect(0, top, width, height - top)
        ctx.slide.element.render(ctx, rect)

    # Text

    def get_text_offset(self, style):
        size = style.size
        return size / 4.0, size / 6.0

    def get_text_size_request(self, ctx, text):
        width, height = self._get_text_size(ctx, text.content, text.role)
        return SizeRequest(width, height, 1, 0)

    def render_text(self, ctx, rect, text):
        style = self._get_text_style(ctx, text.role)
        if style.align == "center":
            x = rect.middle_x
        elif style.align == "left":
            x = rect.x
        elif style.align == "right":
            x = rect.x2
        else:
            raise Exception("Invalid align")
        self.draw_text(ctx, x, rect.y, text.content, style)

    def gather_text_queries(self, ctx, queries, text):
        query = self._get_text_size_query(ctx, text.content, text.role)
        queries.append(query)

    # Shell

    def get_shell_size_request(self, ctx, shell):
        width, height = self._get_text_size(ctx, shell.content, "shell")
        return SizeRequest(width, height, 0, 0)

    def render_shell(self, ctx, rect, shell):
        ctx.renderer.draw_rect(rect, self.shell_background_color)
        style = self._get_text_style(ctx, "shell")
        self._draw_line_emphasis(
            ctx, rect, style, shell.emphasis, self.shell_background_emph_color)
        self.draw_text(ctx, rect.x, rect.y, shell.content, style)

    def gather_shell_queries(self, ctx, queries, shell):
        query = self._get_text_size_query(ctx, shell.content, "shell")
        queries.append(query)

    # Code

    def get_code_size_request(self, ctx, code):
        width, height = self._get_text_size(ctx, code.content, "code")
        return SizeRequest(width, height, 0, 0)

    def render_code(self, ctx, rect, code):
        ctx.renderer.draw_rect(rect, self.code_background_color)
        style = self._get_text_style(ctx, "code")
        self._draw_line_emphasis(
            ctx, rect, style, code.emphasis, self.code_background_emph_color)
        self.draw_text(ctx, rect.x, rect.y, code.content, style)

    def gather_code_queries(self, ctx, queries, code):
        query = self._get_text_size_query(ctx, code.content, "code")
        queries.append(query)

    # Box

    def render_box(self, ctx, rect, box):
        for layer in box.layers:
            self._make_rects_vertical(
                ctx, rect, layer, 10, False,
                lambda e, r: e.render(ctx, r))

    def get_box_size_request(self, ctx, box):
        requests = [self._get_size_request_of_elements(ctx, layer, 10)
                    for layer in box.layers]
        return merge_size_requests(requests)

    # Columns

    def render_columns(self, ctx, rect, box):
        self._make_rects_horizontal(
            ctx, rect, box.elements, 30, False, lambda e, r: e.render(ctx, r))

    def get_columns_size_request(self, ctx, box):
        request = self._get_size_request_of_elements_horizontal(
            ctx, box.elements, 30)
        request.fill_x = 1
        return request

    # Image

    def render_image(self, ctx, rect, image):
        ctx.renderer.draw_image(
            image.get_data(ctx.step), rect.x, rect.y, image.scale)

    def get_image_size_request(self, ctx, image):
        return SizeRequest(image.width, image.height)

    def gather_image_queries(self, ctx, queries, image):
        pass

    # List

    def get_list_size_request(self, ctx, lst):
        request = self._get_size_request_of_elements(ctx, lst.elements, 10)
        return request.resize(15, 0)

    def render_list(self, ctx, rect, lst):
        style = self._get_text_style(ctx, None)

        def draw_item(element, r):
            if element.is_visible(ctx):
                self.draw_text(ctx, rect.x, r.y, "\u2022", style)
            element.render(ctx, r)

        left_padding = 15
        r = rect.shrink(left_padding, 0, 0, 0)
        self._make_rects_vertical(ctx, r, lst.elements, 10, True, draw_item)

    def gather_list_queries(self, ctx, queries, lst):
        pass

    # Frame

    def get_frame_size_request(self, ctx, frame):
        request = frame.box.get_size_request(ctx)
        width, height = self._get_text_size(ctx, frame.title, "frame_title")
        request = request.ensure(width, 0)
        return request.resize(20, height + 20)

    def render_frame(self, ctx, rect, frame):
        ctx.renderer.draw_rect(rect, self.frame_bg_color)
        r = Rect(rect.x, rect.y, rect.width, 60)
        ctx.renderer.draw_rect(r, self.frame_title_color)
        style = self._get_text_style(ctx, "frame_title")
        self.draw_text(
            ctx, rect.x + rect.width - 20, rect.y + 5, frame.title, style)
        rect = rect.shrink(0, 0, 80, 0)
        frame.box.render(ctx, rect)

    def gather_frame_queries(self, ctx, queries, frame):
        query = self._get_text_size_query(ctx, frame.title, "frame_title")
        queries.append(query)

    # Separator

    def get_separator_size_request(self, ctx, separator):
        thickness = separator.thickness
        if thickness is None:
            thickness = self.separator_thickness
        if separator.horizontal:
            return SizeRequest(0, thickness, 1, 0)
        else:
            return SizeRequest(thickness, 0, 0, 1)

    def render_separator(self, ctx, rect, separator):
        thickness = separator.thickness
        if thickness is None:
            thickness = self.separator_thickness
        if separator.horizontal:
            r = Rect(rect.x, rect.y, rect.width, thickness)
        else:
            r = Rect(rect.x, rect.y, thickness, rect.height)
        ctx.renderer.draw_rect(r, self.separator_color)

    # Elements helping functions

    def _get_size_requests(self, ctx, elements):
        results = []
        for e in elements:
            ctx.push(e)
            results.append(e.get_size_request(ctx))
            ctx.pop()
        return results

    def _get_size_request_of_elements(self, ctx, elements, padding):
        requests = self._get_size_requests(ctx, elements)
        height = sum(rq.height for rq in requests) + len(elements) * padding
        width = max(rq.width for rq in requests)
        return SizeRequest(width, height)

    def _get_size_request_of_elements_horizontal(
            self, ctx, elements, padding):
        requests = self._get_size_requests(ctx, elements)
        height = max(rq.height for rq in requests)
        width = sum(rq.width for rq in requests) + len(elements) * padding
        return SizeRequest(width, height)

    def _make_rects_vertical(
            self, ctx, rect, elements, padding, fill_x, callback_fn):
        requests = self._get_size_requests(ctx, elements)
        height = sum(rq.height for rq in requests) + len(elements) * padding
        fill_y = sum(rq.fill_y for rq in requests)
        results = []
        assert fill_y == 0

        y = rect.y + (rect.height - height) / 2.0
        for rq, e in zip(requests, elements):
            if rq.fill_x or fill_x:
                w = rect.width
                x = rect.x
            else:
                w = rq.width
                x = rect.x + (rect.width - rq.width) / 2.0
            h = rq.height
            callback_fn(e, Rect(x, y, w, h))
            y += h + padding
        return results

    def _make_rects_horizontal(
            self, ctx, rect, elements, padding, fill_y, callback_fn):
        requests = self._get_size_requests(ctx, elements)
        width = sum(rq.width for rq in requests) + len(elements) * padding
        fill_x = sum(rq.fill_x for rq in requests)
        results = []
        assert fill_x == 0
        x = rect.x + (rect.width - width) / 2.0
        for rq, e in zip(requests, elements):
            if rq.fill_y or fill_y:
                h = rect.height
                y = rect.y
            else:
                h = rq.height
                y = rect.y + (rect.height - rq.height) / 2.0
            w = rq.width
            callback_fn(e, Rect(x, y, w, h))
            x += w + padding
        return results

    def _get_text_size(self, ctx, text, role):
        if isinstance(text, str):
            text = parse_text(text)
        style = self._get_text_style(ctx, role)
        key = ctx.renderer.get_text_size_query_key(
            style, ctx.text_styles, text)
        width, height = ctx.get_query(key)
        offset_x, offset_y = self.get_text_offset(style)
        return width + offset_x * 2, height + offset_y * 2

    def _get_text_size_query(self, ctx, text, role):
        if isinstance(text, str):
            text = parse_text(text)
        style = self._get_text_style(ctx, role)
        return ctx.renderer.get_text_size_query(style, ctx.text_styles, text)

    def _draw_line_emphasis(self, ctx, rect, style, emphasis, default_color):
        for line_numbers, (start, end), color in emphasis:
            if start <= ctx.step and (end is None or ctx.step <= end):
                if color is None:
                    color = default_color
                for line_number in line_numbers:
                    offset_x, offset_y = self.get_text_offset(style)
                    line_size = style.size * style.line_spacing
                    y = rect.y + offset_y + line_size * (line_number - 1)
                    r = Rect(rect.x, y, rect.width, line_size + offset_y)
                    ctx.renderer.draw_rect(r, color)

    def _get_text_style(self, ctx, role):
        styles = [ctx.text_styles["default"]]
        for obj in ctx.stack:
            if isinstance(obj, Frame):
                styles.append(ctx.text_styles["frame"])
            if isinstance(obj, Box) and obj.role == "list_item":
                styles.append(ctx.text_styles["list_item"])
        if role is not None:
            styles.append(ctx.text_styles[role])
        if ctx.stack[-1].text_style:
            styles.append(ctx.stack[-1].text_style)
        return merge(styles)


class BlueTheme(Theme):

    major_color = "#4040aa"
    minor_color = "#404088"
    text_color = "#000080"
    text_emph_color = "#60b8f0"

    frame_title_color = major_color
    frame_bg_color = "#aaaaff"

    code_background_color = "#F0F0F0"
    code_background_emph_color = "#c0c0FF"

    separator_color = "#000060"


class BlueTheme2(Theme):

    major_color = "#004455"
    minor_color = "#37abc8"
    text_color = major_color
    text_emph_color = "#60b8f0"

    frame_title_color = major_color
    frame_bg_color = "#aaaaff"

    code_background_color = "#F0F0F0"
    code_background_emph_color = "#c0c0FF"

    separator_color = "#000060"
