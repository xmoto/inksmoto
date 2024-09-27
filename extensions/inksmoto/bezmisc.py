#!/usr/bin/env python3
import math, cmath
from inkex import Effect, PathElement, Transform, bezier

class MyExtension(Effect):
    def __init__(self):
        super().__init__()

    def rootWrapper(self, a, b, c, d):
        if a:
            # Cubic solver can be added here
            return ()
        elif b:
            det = c**2.0 - 4.0 * b * d
            if det:
                return (-c + cmath.sqrt(det)) / (2.0 * b), (-c - cmath.sqrt(det)) / (2.0 * b)
            else:
                return -c / (2.0 * b),
        elif c:
            return 1.0 * (-d / c),
        return ()

    def bezierparameterize(self, curve):
        # Curve is now expected as a list of PathElements
        (bx0, by0), (bx1, by1), (bx2, by2), (bx3, by3) = curve
        cx = 3 * (bx1 - bx0)
        bx = 3 * (bx2 - bx1) - cx
        ax = bx3 - bx0 - cx - bx
        cy = 3 * (by1 - by0)
        by = 3 * (by2 - by1) - cy
        ay = by3 - by0 - cy - by
        return ax, ay, bx, by, cx, cy, bx0, by0

    def effect(self):
        # Work on selected elements (modern inkex)
        for element in self.svg.selected.values():
            if isinstance(element, PathElement):
                # Apply transformations if needed using the new Transform API
                transform = element.composed_transform
                element.path = PathElement().apply_transform(transform)
                # Further path manipulations can be added here
                self.svg.getElementById(element.get_id())  # Example of element lookup by ID

if __name__ == '__main__':
    MyExtension().run()
