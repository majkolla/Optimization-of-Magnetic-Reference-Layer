from dataclasses import dataclass
import numpy as np
from ..physics.reflectometry import reflectivity, spin_sld
from ..physics.fom import sensitivity, sfm, mcf, tsf


@dataclass
class Bounds:
    lo: float
    hi: float



class Base2OptimizationProblem:
    pass 
