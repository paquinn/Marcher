# object.py
from marcher.march import *

@Object.register()
def MyObject(self):
    self.res(Union, Box(vec3(1, 1, 1)))
    self.res(Intersect, Sphere(1.3))
    shape = vec2(0.5, 2)
    self.res(Subtract, CylinderX(shape))
    self.res(Subtract, CylinderY(shape))
    self.res(Subtract, CylinderZ(shape))

@Object.register()
def MyScene(self):
    mo = MyObject()
    for i in range(-1, 2):
        for j in range(-1, 2):
            pos = 2 * vec3(i, j, 0)
            self.res(Union, mo.at(pos))

c = Camera((650, 380), AA=2)
c.save(Object.MyScene, "gen.glsl")
c.view(Object.MyScene)
