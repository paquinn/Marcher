# combinator.py
from marcher.march import *

def make_object():
    shape = vec2(0.5, 2)
    cross = Union(CylinderX(shape),
                  Union(CylinderY(shape),
                        CylinderZ(shape)))
    rounded_box = Intersect(Box(vec3(1, 1, 1)), Sphere(1.3))
    return Subtract(rounded_box, cross)

@Object.register()
def MyScene(self):
    obj = make_object()
    self.res(Union, obj.at(vec3(1, 1, 1)))
    self.res(Union, obj.at(vec3(1, 2, 1.5)))
    self.res(Union, obj.at(vec3(2, 1.5, 1)))

c = Camera((650, 380), AA=2)
c.save(Object.MyScene, "gen.glsl")
c.view(Object.MyScene)