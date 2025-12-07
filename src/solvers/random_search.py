from typing import Any, List, Sequence
import numpy as np 
from solvers.base import Solver 

class RandomSearchSolver(Solver):
    """
    Docstring for RandomSearchSolver
    
    random sampling in seach sapce! 
    Simplest version of opt, just for testing and shit 
    """

    def reset(self) -> None: 
        self._X = []
        self._Y = []
        self._x_best = None
        self._y_best = None

    def ask(self, n = 1):
        return super().ask(n)
    
    def tell(self, thetas, values):
        return super().tell(thetas, values)
