# basic.py
from marcher.march import *

@Object.register()
def Basic(self):
    self.res(Union, Sphere(2.0))

Camera((600, 350), AA=2).view(Object.Basic)