# testing.py
from abc import abstractmethod, ABCMeta
from collections import defaultdict
from typing import Tuple
import inspect

vec3 = Tuple[float, float, float]
vec2 = Tuple[float, float]

class Primitive:
    def __init__(self, name, args, location):
        self.name = name
        self.args = args
        self.location = location
        print(name, args, 'at', location)

    def __str__(self):
        args_list = ','.join([str(arg) for arg in self.args])
        return

class Function:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        pass

    def __str__(self):
        args_list = ','.join([str(arg) for arg in self.args])
        return self.name + '(' + args_list + ')'


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

class Scene:
    primitives = {}
    combinators = {}

    @classmethod
    def primitive(cls, *dependencies):
        def decorator(fn):
            register_function(fn, dependencies, cls.primitives)

            def wrapper(*args, at=None):
                primitive = Primitive(fn.__name__, args, at)
                return primitive

            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator

    @classmethod
    def combinators(cls, *glsl_params):
        def decorator(fn):
            name = fn.__name__

            assert name not in cls.primitives, "Combinator %r has already been defined" % name
            params = fn.__annotations__
            split = inspect.getsource(fn).split('"""')

            return fn
        return decorator

    @classmethod
    def operators(cls, *args):
        def decorator(fn):
            return fn
        return decorator

class Program(object):

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def settings(self):
        pass


    @Scene.primitive
    def Plane(p: vec3): """
        return p.y;
    """

    @Scene.primitive()
    def Sphere(p: vec3, r: float): """
        return length(p) - r;
    """

    @Scene.primitive()
    def Box(p: vec3, b: vec3): """
        vec3 d = abs(p) - b;
        return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
    """

    @Scene.primitive()
    def Union(d1: float, d2: float): """
        return min(d1, d2);
    """

    def Intersect(d1: float, d2: float): """
        return max(d1, d2);
    """

    def Subtract(d1: float, d2: float): """
        return max(d1, -d2);
    """


class MySketch(Program):

    @Scene.primitive()
    def MyBox(p: vec3, b: vec3): """
        vec3 d = abs(p) - b;
        return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
    """

    def LadyBug(self):
        pass

def main():
    # print(Sphere(0.5))
    # print(Registry.r)
    # Registry.Box2((0., 0., 0.))
    # Registry.Sphere(0.)
    s = Scene.Sphere(0.4)
    s2 = Scene.Sphere(0.3, at=(1., 2., 4.))
    pass

def primitive(*params):
    def wrapper(f):
        def inner(*args):
            print(params)
            print(f.__name__)
            print(f.__code__.co_varnames)
            print(f.__annotations__)
            print(f(args))
            # f._props = args
            return "d1 = SomeFunc(...)"
        return inner
    return wrapper


# @primitive("p")
# def Sphere(r: float):
#     """
#     return length(p) - r;
#     """

if __name__ == "__main__":
    main()