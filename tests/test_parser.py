import utils  # noqa

from elphie.textparser import parse_text


def test_parser_simple():

    result = parse_text("ABC")
    assert result == [("text", "ABC")]


def test_parse_lines():
    result = parse_text("ABC XYZ\nX\n\nY\n")
    assert result == [("text", "ABC XYZ"),
                      ("newline", 1),
                      ("text", "X"),
                      ("newline", 2),
                      ("text", "Y")]


def test_parse_attributes():
    result = parse_text("This line is ~emph{nice}.\nSecond line")
    assert result == [("text", "This line is "),
                      ("begin", "emph"),
                      ("text", "nice"),
                      ("end", None),
                      ("text", "."),
                      ("newline", 1),
                      ("text", "Second line")]

    result = parse_text("This line is ^emph|nice|.\nSecond line",
                        '^', '|', '|')
    assert result == [("text", "This line is "),
                      ("begin", "emph"),
                      ("text", "nice"),
                      ("end", None),
                      ("text", "."),
                      ("newline", 1),
                      ("text", "Second line")]
