
class Rect:

    def __init__(self,
                 x=None,
                 y=None,
                 width=None,
                 height=None,
                 position=None, size=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if position:
            self.x, self.y = position

        if size:
            self.width, self.height = size

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def middle_x(self):
        return self.x + self.width / 2

    @property
    def middle_y(self):
        return self.y + self.height / 2

    @property
    def x2(self):
        return self.x + self.width

    @property
    def y2(self):
        return self.y + self.height

    def shrink(self, left=0, right=0, top=0, bottom=0):
        return Rect(self.x + left,
                    self.y + top,
                    self.width - left - right,
                    self.height - top - bottom)

    def __eq__(self, other):
        if not isinstance(other, Rect):
            return False
        return self.x == other.x and \
            self.y == other.y and \
            self.width == other.width and \
            self.height == other.height

    def __repr__(self):
        return "<Rect x={0.x} y={0.y} w={0.width} h={0.height}>".format(self)


class SizeRequest(object):

    def __init__(self, width, height, fill_x=0, fill_y=0):
        assert width >= 0
        assert height >= 0
        self.width = width
        self.height = height
        self.fill_x = fill_x
        self.fill_y = fill_y

    def ensure(self, width, height):
        if self.width > width:
            width = self.width
        if self.height > height:
            height = self.height
        return SizeRequest(width, height, self.fill_x, self.fill_y)

    def resize(self, x, y):
        return SizeRequest(self.width + x, self.height + y,
                           self.fill_x, self.fill_y)

    def __repr__(self):
        return "<SizeRequest {0.width}x{0.height} " \
               "{0.fill_x}x{0.fill_y}>".format(self)


def merge_size_requests(requests):
    if len(requests) == 1:
        return requests[0]
    width = max(r.width for r in requests)
    height = max(r.height for r in requests)
    fill_x = max(r.fill_x for r in requests)
    fill_y = max(r.fill_y for r in requests)
    return SizeRequest(width, height, fill_x, fill_y)
