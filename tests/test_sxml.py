import utils  # noqa

from elphie.sxml import Xml


def test_empty_element():
    xml = Xml()
    xml.element("test")
    xml.close()
    assert xml.to_string() == "<test />"


def test_element_with_attributes():
    xml = Xml()
    xml.element("test")
    xml.set("x", 10)
    xml.set("abc-xyz", 20)
    xml.close()
    assert xml.to_string() == "<test x='10' abc-xyz='20' />"


def test_element_child_with_text():
    xml = Xml()
    xml.element("test")

    xml.element("a")
    xml.text("<not-a-tag>")
    xml.close()

    xml.text("abc")

    xml.element("a")
    xml.text("xyz")
    xml.close()

    xml.text("123")

    xml.close()

    assert xml.to_string() == \
        ("<test>"
         "<a>"
         "&lt;not-a-tag&gt;</a>"
         "abc<a>"
         "xyz</a>"
         "123</test>")
