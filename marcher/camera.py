from marcher.util import *


class Camera:
    def __init__(self, **kwargs):
        default = {"MAX_STEPS": 100,
                   "MAX_DISTANCE": 100.0,
                   "MIN_DISTANCE": 0.001,
                   "AA": 1,
                   "BACKGROUND": 0.5,
                   "RO": vec3_str((1, 1, 1)),
                   "TA": vec3_str((0, 0, 0)),
                   "LIGHT_POS": vec3_str((1, 4, 1)),
                   "LOOK": 1}

        self.params = {**default, **kwargs}

    def __str__(self):
        s = ''
        for param, value in self.params.items():
            s += '#define '+param+' '+str(value)+'\n'
        return s

