# object.py
from marcher.march import *

@Object.register()
def MyObject(self):
    self.res(Union, Box(vec3(1, 1, 1)))
    self.res(Intersect, Sphere(1.3))
    r = 0.5
    l = 2
    self.res(Subtract, CylinderX(vec2(r, l)))
    self.res(Subtract, CylinderY(vec2(r, l)))
    self.res(Subtract, CylinderZ(vec2(r, l)))

@Object.register()
def MyScene(self):
    for i in range(-1, 2):
        for j in range(-1, 2):
            self.res(Union, MyObject().at(2 * vec3(i, j, 0)))

c = Camera((650, 380), AA=2)
c.save(Object.MyScene, "gen.glsl")
c.view(Object.MyScene)