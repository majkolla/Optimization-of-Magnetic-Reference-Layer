from dataclasses import dataclass
import numpy as np


from ..physics.reflectometry import reflectivity, spin_sld
from ..physics.fom import sensitivity, sfm, mcf, tsf



@dataclass
class Bounds:
    lo: float
    hi: float



class Base2OptimizationProblem:
    """
    Base2 problem [See base2 problem in report/main.tex for more information]:
    x = [x_Co, d_MRL, sigma_MRL/sub, sigma_MRL/cap, d_cap,
        sigma_cap/SOI, cap_material_id, B, lambda, bkg]
    """
    def __init__(self, materials, soi_scenarios, q_grid, bounds, weights=None):
        """
        materials: represented in a multilevel disctionary,     
        with nuclear SLDs and magnetic model hooks. 
    
        
        Consider materials['MRL'] has a callable rho_n(x_Co), rho_m(x_Co, B).

        soi_scenarios: list of dicts, where each {'rho_n':..., 'd':..., 'sigma_SOI':...}
        q_grid: np.array of Q
        bounds: dict name->Bounds

        May implement a weight dict to optimize a weighted sum instead. 
        """
        self.materials = materials
        self.T = soi_scenarios          
        self.Q = q_grid
        self.bounds = bounds
        
        # self.weights = weights (currently not implemented)
