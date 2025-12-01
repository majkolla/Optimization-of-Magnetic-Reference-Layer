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
    ## maybe should implememt soething to check if lo is higher then hi and give error idk 

    def pack(self, value: Any):
        return float(value)
      
    def unpack(self, scalar: float) -> float:
        return float(scalar)
    

    def clip(self, scalar):
        return float(np.clip(scalar, self.lo, self.hi))

    def sample(self, n = 1):
        return super().sample(n)
    
class IntegerParam(Param): 
    hi: float 
    lo: float 

    def pack(self, value):
        return float(int(value)) # perhaps not the best method to find the optimum, but for now itll do. 

    def unpack(self, scalar: float) -> int: 
        """ 
        convert a float representation to a python int

        rounds the nearest int. 
        
        REALLY NOT IMPRESSIVE OPTIMZATION METHODS BUT FOR NOW ITLL DO 
        """
        return int(round(float(scalar)))
    
    def clip(self, scalar):
        """
        clamp a scalar to the allowed interval then round to the neareest int

        returns a float 
        """
        clamped = float(np.clip(scalar, self.lo, self.hi))
        rounded = float(np.round(clamped))

        return rounded 
    
    def sample(self, n: int = 1) -> np.ndarray:
        raise NotImplementedError
    


class CategoricalParam(Param): ...
"""Categorical parameter with a set of discrete choices repr as strings"""

@dataclass
class SearchSpace: 
    """
    Search space is composed of an ordered list of parameters, where 
    each parameters is a sclar in the opt vector 

    params: list[param]
    """

    def __init__(self, params: Sequence[Param]):
        self._name_to_index: Dict[str, int] = {}
        for idx, p in enumerate(self.params): 
            self._name_to_index[p.name] = idx 

    def __len__(self) -> int: 
        """ The dimension of the search space """
        return len(self.params)

    @property
    def names(self) -> List[str]: 
        """Return the lst of param names"""
        return [p.name for p in self.params]
    
    def pack(self): 
        raise NotImplementedError
    def unpack(self): 
        raise NotImplementedError
    def clip(self): 
        raise NotImplementedError
    