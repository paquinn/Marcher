import numpy as np
from typing import Tuple

vec3 = Tuple[float, float, float]


def float_str(f: float) -> str:
    return str(f)


def vec3_str(v: vec3) -> str:
    return 'vec3(' + float_str(v[0]) + ',' + float_str(v[1]) + ',' + float_str(v[2]) + ')'


def params(*ps):
    return '('+','.join(str(p) for p in ps)+')'


def insert(into, outside, at):
    split = outside.index(at)
    return outside[:split] + into + outside[split:]
