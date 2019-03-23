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

# print(Function.registry.keys())
# Object.MyScene.evaluate()
# print(Object.MyScene.get_dependencies())
# print(Object.MyObject.get_dependencies())
# for var, statement in Object.MyScene.lines:
#     print(statement)
# print(Object.MyScene.get_dependencies())
# c = Camera((650, 380), AA=2)
# c.save(Object.MyScene, "gen.glsl")
# c.view(Object.MyScene)

# u = Union(Intersect(Sphere(1.), Box(vec3(1, 1, 1))), Sphere(2.))(Var('p'))
# print(u.get_usage())

stack = []
Object.MyScene.toposort(set(), set(), stack)
print(stack)