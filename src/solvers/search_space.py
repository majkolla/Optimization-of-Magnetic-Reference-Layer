"""
General parameter and just search space abstractions used by ther opt framework 

- param 
- cont. param 
- int param 
- cat param 
- search space 

Each parameter is a "scalar" in the opt. vector. And the search space holds the list of the parameters 
and it provides helping functions to unpack and pack the vals to their numeric vector repr. used by the solver. 


NOTE: The clip functions works as a strong correction thing for when solver finds solutions outside the bounds 
This is a first implementation and it's NOT a sound way of doing it. 


SOI 
MRL 
CAP -


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
        return np.random.uniform(self.lo, self.hi, size=n)

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

    def pack(self, value) -> float:
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
    

@dataclass
class CategoricalParam(Param): 
    """
    Categorical parameter with a set of discrete choices repr as strings
    """
    choices: Sequence[Any]

    def pack(self, value: Any) -> float: 
        idx = self.choices.index(value)
        return float(idx)
    
    def unpack(self, scalar: float) -> Any: 
        idx = int(np.clip(round(float(scalar)), 0, len(self.choices) - 1))
        return self.choices[idx]
    
    def clip(self, scalar: float) -> float:
        idx = int(np.clip(round(float(scalar)), 0, len(self.choices) - 1))
        return float(idx)
    
    def sample(self, n: int = 1) -> np.ndarray: 
        k = len(self.choices)
        return np.random.randint(0, k, size=n).astype(float)
    


@dataclass
class SearchSpace: 
    """
    Search space is composed of an ordered list of parameters, where 
    each parameters is a sclar in the opt vector 

    params: list[param]
    """

    def __init__(self, params: Sequence[Param]):
        self.params: List[Param] = list(params)
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
    
    def pack(self, values: Mapping[str, Any]) -> np.ndarray: 
        """
        Pack a mapping of a param val into a vector 
        parameters are like dict

        and then return a vector with numerical values we can optimze
        """
        theta = np.empty(len(self.params), dtype=float)
        for i, p in enumerate(self.params): 
            theta[i] = p.pack(values[p.name])
        return theta

    def unpack(self, theta: np.ndarray) -> Dict[str, Any]:
        """
        unpack a numeric vector into a dict

        theta np.ndarray 
            1D array with all the parameter in float form kinda 

        returns a Dict[str, Any]
            so we map from parameters name to the unpacked thing
        """
        arr = np.asarray(theta, dtype=float)
        result: Dict[str, Any] = {}

        for i, p in enumerate(self.params): 
            result[p.name] = p.unpack(arr[i])
        return result
    
    def clip(self, theta: np.ndarray) -> np.ndarray: 
        """
        clip a numeric vector to a feasible domain of the seachspace 

        we get the parameter 
        tehta as an array 1D
        and return a new array with each parameter clipped using it's 
        own clip method 
        """
        arr = np.asarray(theta)
        clipped = np.empty_like(arr)
        for i, p in enumerate(self.params): 
            clipped[i] = p.clip(arr[i])
        return clipped
    
    def sample(self, n: int) -> np.ndarray: 
        """
        Draw random feasible samples from the search space 

        parameters: n amount of samples to draw  
        
        return: 
        a 2D arr where row i is a sample vector 
        """
        num_params = len(self.params)
        samples = np.empty((n, num_params), dtype=float)
        for i, p in enumerate(self.params): 
            samples[:, i] = p.sample(n)
        return samples 
    



if __name__ == "__main__": 
    ## implement some testing stuff
    space = SearchSpace(
        [
            ContinuousParam("x_coti", lo=0.0, hi=1.0),
            ContinuousParam("d_mrl", lo=20.0, hi=300.0),
            CategoricalParam("cap", choices=["Al2O3", "SiO2", "Au"]),
        ]
    )

    values = {"x_coti": 0.73, "d_mrl": 100.0, "cap": "Al2O3"}
    theta = space.pack(values)
    print(theta)