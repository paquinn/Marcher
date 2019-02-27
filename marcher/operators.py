from marcher.util import *


class Operator:
    def __init__(self, name, *ds):
        self.name = name
        self.ds = ds

    def __str__(self):
        return self.name+params(*self.ds)


class Translate(Operator):
    def __init__(self, p, t):
        super().__init__('opTranslate', p, t)


def make_smooth(name, d1, d2, k):
    if k:
        return 'opSmooth'+name, d1, d2, k
    else:
        return 'op'+name, d1, d2


class Union(Operator):
    def __init__(self, d1, d2, k=None):
        super().__init__(*make_smooth('Union', d1, d2, k))


class Intersect(Operator):
    def __init__(self, d1, d2, k=None):
        super().__init__(*make_smooth('Intersect', d1, d2, k))


class Subtract(Operator):
    def __init__(self, d1, d2, k=None):
        super().__init__(*make_smooth('Subtract', d1, d2, k))
