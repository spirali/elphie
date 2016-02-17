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
slide.code("""#include <stdio.h>

/* Hello world program */

int main() {
    printf("Hello world!\\n");
    return 0;
}""", "c")

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
slide.text("Normal text | ~tt{Type writer} | ~emph{emphasis} | ~alert{alert}")

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
