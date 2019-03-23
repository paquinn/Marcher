# mirror.py
from marcher.march import *

@Operator.register()
def Mirror(p: vec3): """
    return abs(p);
"""

@Object.register()
def MyObject(self):
    self.p(Mirror())
    self.res(Union, Sphere(1.).at(vec3(.5, 1, 0.5)))
    self.res(Union, Sphere(1.).at(vec3(1.1, 0, 0.5)))


c = Camera((650, 380), AA=2)
c.save(Object.MyObject, "gen.glsl")
c.view(Object.MyObject)