# DSL.py
from abc import abstractmethod, ABCMeta
from collections import defaultdict
from typing import Tuple
import inspect

function_stack = []

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


def make_param(arg_type):
    if arg_type is float:
        return 'float'
    elif arg_type is vec3:
        return 'vec3'


def make_function(return_type, name, params, body):
    fun = make_param(return_type) + ' ' + name + '(' + ','.join([make_param(arg_type) + ' ' + arg for arg, arg_type in params.items()]) + ')\n'
    fun += '{\n'
    fun += body
    fun += '\n}'
    return fun


def register_function(fn, dependencies, registry):
    name = fn.__name__
    assert name not in registry, "Primitive %r has already been defined" % name
    params = fn.__annotations__
    assert 'return' in params, "Function has no return type"
    return_type = fn.__annotations__['return']
    fn.__annotations__.pop('return')
    split = inspect.getsource(fn).split('"""')
    assert(len(split) == 3), "%r has no body" % name
    body = split[1].strip()

    registry[name] = {
        'function': make_function(return_type, name, params, body),
        'dependencies': list(dependencies)
    }


# Base case for recursive compilation
class Var:
    def __init__(self, name):
        self.name = name

    def __call__(self):
        return self

    def __str__(self):
        return self.name


class Function:
    registry = {}

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            register_function(fn, dependencies, cls.registry)

            def wrapper(*args):
                combinator = Function(fn.__name__, args)
                return combinator

            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator

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
    dependencies = {}

    @classmethod
    def register(cls, fn):
        def wrapper(*args, at=None, f=None):
            cls.dependencies[fn.__name__] = set()
            partial = Object(fn.__name__, args, at, f)

            return partial

        setattr(cls, fn.__name__, wrapper)

        return wrapper

    def __init__(self, name, args, location, f=None):
        super().__init__(name, args)
        self.location = location
        self.f = f

    def __call__(self, f):
        apply = f if not self.f else self.f(f)
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

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            if 'return' not in fn.__annotations__:
                fn.__annotations__['return'] = float
            register_function(fn, dependencies, cls.registry)

            def wrapper(*args):
                combinator = Combinator(fn.__name__, args)
                return combinator

            setattr(cls, fn.__name__, wrapper)

            # TODO hard-coding only two objects can be combined
            def partial(self, d2, *args):
                Object.dependencies[self.name].add(fn.__name__)

                def inner(d1):
                    all_args = [d1] + [d2] + list(args)
                    return Combinator(fn.__name__, all_args)
                return inner

            setattr(Object, fn.__name__, partial)

            return wrapper
        return decorator

    def at(self, location: vec3):
        return Combinator(self.name, [arg.at(location) for arg in self.args])

    def __call__(self, f):
        return Combinator(self.name, [arg(f) for arg in self.args])


class Operator(Function):

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            if 'return' not in fn.__annotations__:
                fn.__annotations__['return'] = vec3
            register_function(fn, dependencies, cls.registry)

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
        apply = f if not self.f else self.f(f)
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
    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):

            if 'return' not in fn.__annotations__:
                fn.__annotations__['return'] = float
            register_function(fn, dependencies, cls.registry)

            def wrapper(*args, at=None, f=None):
                partial = Primitive(fn.__name__, args, at, f)

                return partial
            setattr(cls, fn.__name__, wrapper)

            return wrapper
        return decorator


def make_object_body():
    pass

# -------------------------- #
#      Standard Library      #
# -------------------------- #

# --- Primitives --- #
@Primitive.register()
def Plane(p: vec3): """
    return p.y;
"""

@Primitive.register()
def Sphere(p: vec3, r: float) -> float: """
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
def Subtract(d1: float, d2: float): """
    return max(d1, -d2);
"""


@Operator.register()
def Translate(p: vec3, t: vec3): """
    return p - t; 
"""

@Operator.register()
def Repeat(p: vec3, n: float): """
    return mod(p * n) - n * 0.5; 
"""

@Object.register
def MySphere(self):
    self.Union(Sphere(0.5))


@Object.register
def MySphere2(self):
    self.Union(Sphere(0.6))


@Object.register
def MySketch(self):
    s1 = MySphere()
    s2 = MySphere2()

    u = Union(s1, s2)

    self.Union(s1)
    self.Union(s2)
    self.Union(u)

def main():
    s1 = Sphere(0.5)(Translate(vec3(1, 1, 1)))
    s2 = Sphere(0.6, at=vec3(2, 2, 2))

    print(Union(s1, s2)(Var('p')))

if __name__ == "__main__":
    main()