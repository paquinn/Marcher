# testing.py
from abc import abstractmethod, ABCMeta
from collections import defaultdict
from typing import Tuple
import inspect

generator_set = set()


class vec:
    def __init__(self, *floats):
        self.floats = []
        # Able to build vecs out of other vecs as in glsl
        for f in floats:
            if type(f) is float or type(f) is int:
                # Make sure everything is a float here
                self.floats.append(float(f))
            elif type(f) is vec:
                self.floats.extend(f.floats)
        self.dim = len(self.floats)

    def __str__(self):
        return 'vec' + str(self.dim) + '(' + ','.join([str(f) for f in self.floats]) + ')'

    def __mul__(self, scalar):
        # Make sure its a float
        scalar = float(scalar)
        return vec(*[scalar * f for f in self.floats])

    __rmul__ = __mul__


# For when you want to be sure of a vec dimension
def vec2(f1, f2):
    return vec(f1, f2)


def vec3(f1, f2, f3):
    return vec(f1, f2, f3)


def register_function(fn, dependencies, registry):
    name = fn.__name__
    assert name not in registry, "Primitive %r has already been defined" % name
    params = fn.__annotations__
    split = inspect.getsource(fn).split('"""')
    assert(len(split) == 3), "%r has no body" % name
    body = split[1].strip()
    registry[name] = {
        'name': name,
        'dependencies': dependencies,
        'params': params,
        'body': body
    }


# Base case for recursive compilation
class _Var:
    def __init__(self, name):
        self.name = name

    def __call__(self):
        return self

    def __str__(self):
        return self.name


class Function:
    def __init__(self, name, args):
        self.name = name
        self.args = list(args)

    def make_call(self):
        args_list = ','.join([str(arg) for arg in self.args])
        return self.name + '(' + args_list + ')'

    def __str__(self):
        return self.make_call()


class Object(Function):
    objects = {}

    @classmethod
    def register(cls):
        def decorator(fn):
            # register_function(fn, dependencies, cls.objects)

            def wrapper(*args, at=None, f=None):
                partial = Object(fn.__name__, args, at, f)

                return partial

            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator

    def __init__(self, name, args, location, f=None):
        super().__init__(name, args)
        self.location = location
        self.f = f

    def __call__(self, f):
        apply = f() if not self.f else self.f(f())
        return Primitive(self.name, self.args.copy(), self.location, apply)

    def at(self, location: vec3):
        return Primitive(self.name, self.args.copy(), location, self.f)

    def __str__(self):
        assert self.f, "Compiling a partial"
        if self.location:
            # TODO Convert to function multiplication
            self.args.insert(0, Translate(self.location, f=self.f))
        else:
            self.args.insert(0, self.f)
        ret = super().__str__()
        self.args.pop(0)
        return ret


class Combinator(Function):
    combinators = {}

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            register_function(fn, dependencies, cls.combinators)

            def wrapper(*args):
                combinator = Combinator(fn.__name__, args)
                return combinator

            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator

    def __call__(self, f):
        return Combinator(self.name, [arg(f) for arg in self.args])


class Operator(Function):
    operators = {}

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            register_function(fn, dependencies, cls.operators)

            def wrapper(*args, f=None):
                operator = Operator(fn.__name__, args, f)
                return operator
            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator

    def __init__(self, name, args, f=None):
        super().__init__(name, args)
        self.f = f

    def __call__(self, f):
        apply = f() if not self.f else self.f(f())
        return Operator(self.name, self.args.copy(), apply)

    # TODO Wrong way around
    def __mul__(self, other):
        return Operator(other.name, other.args.copy(), self)

    # __rmul__ = __mul__

    def __str__(self):
        assert self.f, "Compiling a partial"
        self.args.insert(0, self.f)
        ret = super().__str__()
        self.args.pop(0)
        return ret


class Primitive(Object):
    primitives = {}

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            register_function(fn, dependencies, cls.primitives)

            def wrapper(*args, at=None, f=None):
                partial = Primitive(fn.__name__, args, at, f)

                return partial
            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator


# -------------------------- #
#      Standard Library      #
# -------------------------- #

# --- Primitives --- #
@Primitive.register()
def Plane(p: vec3): """
    return p.y;
"""

@Primitive.register()
def Sphere(p: vec3, r: float): """
    return length(p) - r;
"""

@Primitive.register()
def Box(p: vec3, b: vec3): """
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
"""

# --- Combinators --- #
@Combinator.register()
def Union(d1: float, d2: float): """
    return min(d1, d2);
"""

@Combinator.register()
def Intersect(d1: float, d2: float): """
    return max(d1, d2);
"""

@Combinator.register()
def Subtract(d1: float, d2: float):  """
    return max(d1, -d2);
"""

@Operator.register()
def Translate(p: vec3, t: vec3): """
    return p - t; 
"""


def main():
    # print(Sphere(0.5))
    # print(Registry.r)
    # Registry.Box2((0., 0., 0.))
    # Registry.Sphere(0.)
    # s1 = Primitive.Sphere(0.4)('p')
    # s2 = Primitive.Sphere(0.3, at=vec3(1., 2., 4.))('p')
    # t1 = Operator.Translate(vec3(0., 0., 0.), vec3(3., 2., 1.))
    # print(t1)
    # print(s1)
    # print(s2)

    s = Sphere(0.4, f=Translate(vec3(1, 2, 3)))

    t1 = Translate(vec3(1, 2, 3))
    t2 = Translate(vec3(3, 2, 1), f=t1)

    term = _Var('p')

    # t3 = Translate('a') * Translate('b') * Translate('c')
    # print(Translate('a', f=Translate('b', f=Translate('c'))))
    # print(Translate('a') * Translate('b') * Translate('c'))

    t1 = Translate('a') * Translate('b') * Translate('c')

    s = Sphere(0.5, at=vec3(1, 2, 3))

    # print(s(term))
    # s = s(term)
    # print(s)
    # print(Sphere(0.5, f=t4).at(vec3(1, 2, 3))(_Var('p')))
    # print(Sphere(0.5, at=vec3(1, 2, 3), f=t4)(_Var('p')))

    # print(Sphere(0.5, f=t4).at(vec3(1, 2, 3)))
    # print(t1(_Var('p')))
    # print(t2(_Var('p')))

    # s3 = s2.at(vec3(1, 2, 3))
    # print(Translate(vec3(1, 2, 3))(Translate(vec3(1, 2, 3))))
    # print(s2('p'))
    # print(s3('p'))


    # print(vec(1., 3, vec2(1., 3), 4., vec(2., 1.)))
    # print(2. * vec(1., 3, vec2(1., 3), 4., vec(2., 1.)) * 4)

    u = Union(Intersect(Sphere(1), Sphere(3)), Sphere(2.).at(vec(1, 2, 3)))
    print(u(term))
    # print(Sphere(2., at=vec(1, 2, 3))(term))
if __name__ == "__main__":
    main()