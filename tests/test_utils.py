import utils  # noqa

from elphie.utils import Rect


def test_rect():

    r = Rect(12, 340, 80, 60)

    assert r.x == 12
    assert r.y == 340
    assert r.width == 80
    assert r.height == 60

    assert r.x2 == 92
    assert r.y2 == 400

    assert r.middle_x == 52
    assert r.middle_y == 370

    assert r.position == (12, 340)
    assert r.size == (80, 60)

    r2 = r.shrink(2, 0, 20, 5)
    assert r2.x == 14
    assert r2.y == 360
    assert r2.width == 78
    assert r2.height == 35

    r3 = Rect(14, 360, 78, 35)
    assert r2 == r3
    assert r != r3
