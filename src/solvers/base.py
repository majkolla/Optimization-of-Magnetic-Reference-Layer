from dataclasses import dataclass
from typing import Protocol

"""
Common interface for all problem types
Result container 

"""

class OptimzationProblemProtocol(Protocol): 
    """
    An interface both Base1 and Base2 (in the future base3) must satisfy
    """
    def evaluate_objective(self, *args, **kwargs) -> float: 
        pass 

    @property 
    def search_space(self): 
        pass 
    @property
    def name(self): 
        pass 


@dataclass 
class RunResults: 
    """ Final outcome """
    x_best: dict[str: any]
    y_best: float | tuple[float] # single or multi obj
    n_evals: int 


class Solver: 
    """
    Base class API shared by all other solvers
    """