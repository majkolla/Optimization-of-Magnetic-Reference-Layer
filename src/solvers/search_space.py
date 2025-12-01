"""
General parameter and just search space abstractions used by ther opt framework 

- param 
- cont. param 
- int param 
- cat param 
- search space 

Each parameter is a "scalar" in the opt. vector. And the search space holds the list of the parameters 
and it provides helping functions to unpack and pack the vals to their numeric vector repr. used by the solver. 
"""

import numpy as np 
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Sequence, List


@dataclass
class Param:
    """
    Base (abstract) class for a single scalar parameter dim

    subclasses: 
        - pack: Any -> float 
        - unpack: float -> float
        - clip(scalar): float -> float 
        - sample(n): 
    """
    name: str 

    def pack(self, value: Any) -> float: 
        """ Convert a python value to its float representation """
        raise NotImplementedError
    
    def unpack(self, scalar: float) -> Any: 
        """ Convert a float representation back to a python value """
        raise NotImplementedError
    
    def clip(self, scalar: float) -> float: 
        """
        Project a float repr. inot the valid domain 
        
        Returns a new float: does not modify the input 
        """
        raise NotImplementedError

    def sample(self, n: int = 1) -> np.ndarray: 
        raise NotImplementedError

@dataclass
class ContinuousParam(Param): 
    lo: float
    hi: float 


class IntegerParam(Param): 
    pass 

class CategoricalParam(Param): 
    pass 

class SearchSpace: 
    """
    Holds the param and can pack and unpack helpers 
    """
    def __init__(self):
        pass
    def pack(self): 
        pass 
    def unpack(self): 
        pass 
    def clip(self): 
        pass 
    