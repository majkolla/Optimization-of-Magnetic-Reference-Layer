from dataclasses import dataclass
import numpy as np
from ..physics.reflectometry import reflectivity, spin_sld
from ..physics.fom import sensitivity, sfm, mcf, tsf
from typing import Optional


@dataclass
class Bounds:
    lo: float
    hi: float

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


@dataclass
class CapSpec: 
    """
    capping layer 
    """
    name: str #name 
    rho_n: float # nuclear SLD 
    thickness: float # fixed in Base 1 
    sigma: float 

@dataclass 
class SubstrateSpec: 
    """ ALWAYS SI"""
    name: str = "Si"
    rho_n: float # = check it later 
    sigma: float 

@dataclass 
class MRL: 
    """
    Ingredients for a CoTi alloy MRL
    """
    rho_n_Co: float
    rho_n_Ti: float

    m_sld_from_x = None 


    # Interface width between substrate and MRL & MRL and cap
    sigma_sub_mrl : float = 5.0
    sigma_mrl_cap: float = 5.0

@dataclass 
class Materials: 
    """ help class to construct the stacks"""
    substrate: SubstrateSpec
    caps: dict[str: CapSpec]
    mrl: MRL

class Base1OptimizationProblem:
    """
    Base1 problem [See base1 problem in report/main.tex for more information]:
    x = [x_co-ti, d_MRL,cap_material]

    TSF(x)
        s.t.
        x_coti \in [0,1]
        d_MRL > 0 
        c \in {Al_2O_3, SiO_2, Au} (for example)


    ----------------------------------------------
    Parameters: 
    materials: Materials 
        Substrate, Co/Ti data for MRL and avaible caps 
    soi_list: list[SOISpecs]
        we can create random numbers or just look at the most relevant reserach
    q_grid: np.ndarry
        just a interval 
    bounds_x: 
        bounds for example for x_coti between 0-1
    bounds_d: 
        for thickness 
    weights_fn: 
        a weight for Q, potentially to optimze for particular Q vals
    
    """ 
    def __init__(self, 
                 materials: Materials, 
                 soi_list: list[SOISpec], 
                 q_grid: np.ndarray, 
                 bounds_x: Bounds, 
                 bounds_d: Bounds, 
                 weight_fn):
        
        self.materials = materials 
        self.soi_list = list(soi_list)
        self.Q = np.asarray(q_grid, dtype=float)
        self.bounds_x = bounds_x
        self.bounds_d = bounds_d
        # Ill think about the implementation of weights for now
        

        pass
    def _layers(self): 
        pass
    def evaulate_objective():
        pass