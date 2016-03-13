import elphie

slides = elphie.Slides("example.pdf")

slide = slides.new_title_slide("Elphie")
slide.text("Stanislav Böhm\n~tt{http://github.com/spirali/elphie}")

slide = slides.new_slide()

slide.h2("Elphie is a presentation framework\n"
         "based on ~emph{Python} and ~emph{Inkscape}")


slide = slides.new_slide("Introduction")

slide.text("The following code ...")
slide.code("""import elphie

slides = elphie.Slides()
slide = slides.new_slide("The first slide")
slide.text("Hello world!")
slides.render()""", "python")

slide.text("will produce ~tt{slide.pdf}")
slide.text("You can see the result at next slide")

slide = slides.new_slide("The first slide")
slide.text("Hello world!")

slide = slides.new_slide("Text fragments")
slide.text("Let us continue with the demonstration ...", show=1)
slide.text("Elphie ...", show=2)
slide.text("... supports ...", show=3)
slide.text("... fragments.", show=4)

slide = slides.new_slide("Image fragments")
slide.image("fragments.svg")

slide = slides.new_slide("List")
slide.h2("Example of a list:")
lst = slide.list()
lst.item().text("Apple")
lst.item().text("Orange")
lst.item().text("Banana")

slide = slides.new_slide("Code")
code = slide.code("""#include <stdio.h>

/* Hello world program */

int main() {
    printf("Hello world!\\n");
    return 0;
}""", "c")

code.line_emphasis(1, show=(2, 2))
code.line_emphasis(5, show=3)
code.line_emphasis(show=4, prefix="printf")
code.line_emphasis(7, show=5)

code = slide.code("""#include <stdio.h>

/* Hello world program */

int main() {
    printf("Hello world!\\n");
    return 0;
}""", "c")
code.text_style = elphie.TextStyle(size=20)
code.line_emphasis([5, 6, 7], show=6, color="#f0c080")

slide = slides.new_slide("Shell")
shell = slide.shell(
    "~shell_prompt{/path/to/elphie/example$} ~shell_cmd{ls}\n"
    "python3 example.py\n\n"
    "~shell_prompt{/path/to/elphie/example$} ~shell_cmd{python3 example.py}\n"
    "Preprocessing................. done\n"
    "Building...................... done\n"
    "Creating 'example.pdf'........ done\n")
shell.line_emphasis(5, show=(2, 2))
shell.line_emphasis(6, show=(3, 3))

subslide = slide.box()
subslide.text("Preprocessing is cached", show=(2, 2))
subslide.new_layer()
subslide.text("Building is also cached", show=(3, 3))
subslide.new_layer()
subslide.text("This is demonstration of ~emph{layers}", show=4)


slide = slides.new_slide("Columns")
slide.text("Columns demonstration")
columns = slide.columns()
lst = columns.column().list()
lst.item().text("First item")
lst.item().text("Second item")
lst.item().text("Third item")

columns.column().code("""#include <stdio.h>"

int main() {
    printf("Hello world!\\n");
    return 0;
}""", "c")

slide = slides.new_slide("Frame")
frame = slide.frame("Title of the frame")
frame.text("This text is in the frame!")
lst = frame.list()
lst.item().text("First bullet")
lst.item().text("Second bullet")


slide = slides.new_slide("Text styles")
slide.h1("Header 1")
slide.h2("Header 2")
slide.h3("Header 3")
text = "Normal text | ~tt{Type writer} | ~emph{emphasis} | ~alert{alert}"
slide.text(text)
text = slide.text("Fixed size 15, ignore theme: " + text)
text.text_style = elphie.TextStyle(size=15)

slides.set_style("my_red", elphie.TextStyle(color="red"))
slides.set_style("my_blue", elphie.TextStyle(color="blue"))
slides.set_style("my_green", elphie.TextStyle(color="green"))
slide.text("~my_red{red} ~my_green{green} ~my_blue{blue}")

slide = slides.new_slide("Proceduraly generated elements")


class MyElement(elphie.Element):

    def get_size_request(self, ctx):
        return elphie.SizeRequest(500, 100)

    def render_body(self, ctx, rect):
        for i, color in enumerate(("red", "green", "blue")):
            if ctx.step <= i:
                break
            w = rect.width / 3.0
            r = elphie.Rect(rect.x + i * w, rect.y,
                            w, rect.height)
            ctx.renderer.draw_rect(r, color)

slide.code("""class MyElement(elphie.Element):

    def get_size_request(self, ctx):
        return elphie.SizeRequest(500, 100)

    def render_body(self, ctx, rect):
        colors = ("red", "green", "blue")
        for i, color in enumerate(colors)[:ctx.step]:
            w = rect.width / 3.0
            r = elphie.Rect(rect.x + i * w, rect.y,
                            w, rect.height)
            ctx.renderer.draw_rect(r, color)
""", "python")

slide.add(MyElement(show=(1, 3)))


slide = slides.new_slide("Themes", elphie.BlueTheme())
slide.text("This slide is rendered by a different theme")

slide = slides.new_slide()
slide.h2("Have a nice day!")

slides.render()
