from dataclasses import dataclass
import numpy as np
from ..physics.reflectometry import reflectivity, spin_sld
from ..physics.fom import sensitivity, sfm, mcf, tsf


@dataclass
class Bounds:
    lo: float
    hi: float



class Base1OptimizationProblem:
    """
    Base1 problem [See base1 problem in report/main.tex for more information]:
    x = [x_co-ti, d_MRL,cap_material]

    TSF(x)
        s.t.
        x_coti \in [0,1]
        d_MRL > 0 
        c \in {Al_2O_3, SiO_2, Au} (for example)
    """ 
    def __init__(self, materials, soi, q_grid, bounds):
        """
        materials: data in a dictionary 

        """
        pass
    def _layers(self): 
        pass
    def evaulate_objective():
        pass

@dataclass
class SOISpec: 
    """
    One SOI scenario 
    a dataclass for this 
    """
    name: str                    
    rho_n: float     
    thickness: float 
    sigma: float 
