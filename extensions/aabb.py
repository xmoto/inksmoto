import logging, log

class AABB:
    def __init__(self):
        self.reinit()

    def reinit(self):
        inf = 1e500
        self.xmin = inf
        self.xmax = -inf
        self.ymin = inf
        self.ymax = -inf

    def addPoint(self, x, y):
        if x < self.xmin:
            self.xmin = x
        if x > self.xmax:
            self.xmax = x
        if y < self.ymin:
            self.ymin = y
        if y > self.ymax:
            self.ymax = y

    def width(self):
        return self.xmax - self.xmin

    def height(self):
        return self.ymax - self.ymin

    def x(self):
        return self.xmin

    def y(self):
        return self.ymin
