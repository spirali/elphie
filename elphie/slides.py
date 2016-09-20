
from elphie.svg import RendererSVG, run_inkscape
from elphie.elements import Box
from elphie.theme import Theme
from elphie.textstyle import TextStyle

import hashlib
import subprocess
import os
import sys
import pickle
from concurrent.futures import ThreadPoolExecutor


class Slide:

    role = None
    extra_data = None

    def __init__(self, title, theme):
        self.title = title
        self.element = Box("main")
        self.theme = theme

    def get_max_step(self):
        return self.element.get_max_step()

    def gather_queries(self, ctx):
        queries = []
        self.element.gather_queries(ctx, queries)
        return queries


class Context(object):

    def __init__(self,
                 renderer,
                 theme,
                 slide,
                 step,
                 query_cache,
                 text_styles):
        self.renderer = renderer
        self.theme = theme
        self.slide = slide
        self.step = step
        self.stack = []
        self.query_cache = query_cache
        self.text_styles = theme.text_styles.copy()
        for name, style in text_styles.items():
            self.text_styles[name] = style

    def get_query(self, key):
        try:
            return self.query_cache[key]
        except KeyError:
            print("Queries:")
            for q in self.query_cache:
                print (q)
            print("Searching for: ", key)
            raise Exception("Invalid query key")

    def push(self, obj):
        self.stack.append(obj)

    def pop(self):
        self.stack.pop()


class Slides:

    debug = False

    def __init__(self,
                 filename,
                 theme=None,
                 width=1024,
                 height=768,
                 cache_dir="./elphie-cache"):
        self.filename = filename
        self.slides = []
        if theme:
            self.theme = theme
        else:
            self.theme = Theme()
        self.width = width
        self.height = height
        self.cache_dir = cache_dir
        self.user_defined_text_styles = {}

    def new_slide(self, title=None, theme=None):
        return self._make_slide(title, theme).element

    def new_title_slide(self, title, theme=None):
        slide = self._make_slide(title, theme)
        slide.role = "title"
        return slide.element

    def _make_slide(self, title, theme):
        if theme is None:
            theme = self.theme
        slide = Slide(title, theme)
        self.slides.append(slide)
        return slide

    def _show_progress(
            self, name, value=0, max_value=0, first=False, last=False):
        if not first:
            prefix = "\r"
        else:
            prefix = ""
        if last:
            progress = "done"
            suffix = "\n"
        else:
            if max_value != 0 and not first:
                progress = str(int(value * 100.0 / max_value)) + "%"
            else:
                progress = ""
            suffix = ""
        if self.debug:
            prefix = ""
            suffix = "\n"
        name = name.ljust(30, ".")
        sys.stdout.write("{}{} {}{}".format(prefix, name, progress, suffix))
        sys.stdout.flush()

    def render(self):
        if not os.path.isdir(self.cache_dir):
            print("Creating cache directory: ", self.cache_dir)
            os.makedirs(self.cache_dir)

        if not self.slides:
            raise Exception("No slides to render")

        # Gather slide queries
        renderer = RendererSVG()
        queries = []
        old_query_cache = self._load_query_cache()
        query_cache = {}

        for slide in self.slides:
            ctx = Context(renderer, slide.theme, slide, None, None,
                          self.user_defined_text_styles)
            for query in slide.gather_queries(ctx):
                key = query[0]
                value = old_query_cache.get(key)
                if value is not None:
                    query_cache[key] = value
                else:
                    queries.append(query)
        queries = dict(queries)

        # Create threads
        workers = os.cpu_count() or 1
        pool = ThreadPoolExecutor(workers)

        # Process new queries
        self._show_progress("Preprocessing", first=True)
        count = 0
        for key, result in pool.map(
                lambda query: (query[0], query[1]()), queries.items()):
            query_cache[key] = result
            count += 1
            self._show_progress("Preprocessing", count, len(queries))
        self._show_progress("Preprocessing", count, len(queries), last=True)
        self._save_query_cache(query_cache)

        # Create context of uncached slides
        cached_pdf = self._get_cached_pdf()
        contexts = []
        for i, slide in enumerate(self.slides):
            for step in range(slide.get_max_step()):
                renderer = RendererSVG()
                renderer.begin(self.width, self.height)
                ctx = Context(
                    renderer, slide.theme, slide, step + 1, query_cache,
                    self.user_defined_text_styles)
                contexts.append(ctx)

        # Build uncached slides
        self._show_progress("Building", first=True)
        filenames = []
        count = 0
        for filename in pool.map(
                lambda ctx: self.render_slide(ctx, cached_pdf),
                contexts):
            filenames.append(filename)
            count += 1
            self._show_progress("Building", count, len(contexts))
        self._show_progress("Building", count, len(contexts), last=True)

        # Clean old cached files
        if not self.debug:
            for filename in set(cached_pdf) - set(filenames):
                os.remove(os.path.join(self.cache_dir, filename))

        # Join everything into one file
        self._show_progress("Creating '{}'".format(self.filename), first=True)
        args = ["pdftk"]
        args += [os.path.join(self.cache_dir, filename)
                 for filename in filenames]
        args += ["cat", "output", self.filename]
        subprocess.call(args)
        self._show_progress("Creating '{}'".format(self.filename), last=True)

    def set_style(self, name, style):
        assert isinstance(name, str)
        assert isinstance(style, TextStyle)
        self.user_defined_text_styles[name] = style

    def convert_to_pdf(self, source, target):
        run_inkscape(("-A", target), stdin=source)

    def render_slide(self, ctx, cached_pdf):
        ctx.renderer.begin(self.width, self.height)
        ctx.theme.render_slide(ctx)
        ctx.renderer.end()

        if self.debug:
            filename = os.path.join(self.cache_dir, "slide-{}-{}.svg".format(
                self.slides.index(ctx.slide), ctx.step))
            ctx.renderer.write(filename)

        string = ctx.renderer.to_string()
        h = hashlib.sha1()
        h.update(string.encode())
        filename = h.hexdigest() + ".pdf"
        if filename not in cached_pdf:
            full_filename = os.path.join(self.cache_dir, filename)
            self.convert_to_pdf(ctx.renderer.to_string(), full_filename)
        return filename

    def _load_query_cache(self):
        filename = os.path.join(self.cache_dir, "queries")
        try:
            with open(filename, "rb") as f:
                query_cache = pickle.load(f)
                print("Cache loaded")
                return query_cache
        except FileNotFoundError:  # noqa
            print("No cache file found")
            return {}

    def _save_query_cache(self, query_cache):
        filename = os.path.join(self.cache_dir, "queries")
        try:
            with open(filename, "wb") as f:
                pickle.dump(query_cache, f)
        except:
            print("Cache cannot be written")

    def _get_cached_pdf(self):
        return [filename for filename in os.listdir(self.cache_dir)
                if filename.endswith(".pdf")]
