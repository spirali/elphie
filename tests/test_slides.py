import utils  # noqa

from elphie.slides import Slides


def test_slide_render():
    slides = Slides(utils.output_name("slides.pdf"),
                    cache_dir=utils.output_name("cache"))
    """
    slide = slides.new_slide("Text")
    slide.h1("This is nice text slide!")
    slide.text("This is ~emph{testing} slide!\n!!!", show=(2, 3))
    slide.text("Last text", show=4)

    slide = slides.new_slide("Test slide (img)")
    slide.image("testdata.svg", scale=0.4)
    slide.image("testdata.svg", scale=0.2)

    slide = slides.new_slide("List")

    slide.h1("List:")
    lst = slide.list()
    lst.item().text("Line 1")
    lst.item().text("Line 2.1\nLine2.2")
    lst.item().text("Line 3")
    lst.item().text("Line 4 is very very long")

    slide = slides.new_slide("Frame")

    frame = slide.frame("This is FRAME!")
    frame.text("My text1")
    frame.text("My text2 looooooooooooooooong line is here!")
    lst = frame.list()
    lst.item().text("Red")
    lst.item().text("Green")
    lst.item().text("Blue")

    frame = slide.frame("Looong title frame")
    frame.text("Shor text")

    slide = slides.new_slide("Code")
    slide.code("if x == 0:\n    print('Hello world')", "python")

    """

    slide = slides.new_slide("Columns")

    slide.h1("Example of two clumns")
    columns = slide.columns()

    c1 = columns.column()
    c1.text("This is a smaller column")
    c1.code("c1 = columns.column()", "python")

    c2 = columns.column()
    c2.text("This is a bigger column\n")

    c2.h2("Inner columns")
    cc = c2.columns()

    cc.column().text("Hello\nfrom the\n~emph{first}\ncolumn")
    cc.column().text("Hello\nfrom the\n~emph{second}\ncolumn")

    slides.render()
