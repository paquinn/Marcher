from marcher.operators import *


def cond_offset(c: vec3) -> str:
    if np.count_nonzero(c):
        return str(Translate('p', vec3_str(c)))
    return 'p'


class Primitive:
    def __init__(self, name, c=None):
        self.name = name
        self.c = c if c else (0, 0, 0)


class Plane(Primitive):
    def __init__(self, c=None):
        super().__init__('sdPlane', c)

    def __str__(self):
        return self.name+params(cond_offset(self.c))


class Sphere(Primitive):
    def __init__(self, r, c=None):
        super().__init__('sdSphere', c)
        self.r = r

    def __str__(self):
        return self.name+params(cond_offset(self.c), self.r)


class Box(Primitive):
    def __init__(self, b, c=None):
        super().__init__('sdBox', c)
        self.b = b

    def __str__(self):
        return self.name+params(cond_offset(self.c), vec3_str(self.b))
