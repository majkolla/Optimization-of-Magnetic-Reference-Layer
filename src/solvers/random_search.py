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

    def ask(self, n: int = 1) -> List[np.ndarray]:
        # Generate n random samples from the search space
        samples_2d = self.space.sample(n)
        # Convert to list of 1D arrays as expected by Solver.ask protocol
        return [row for row in samples_2d]
    
    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        # No state, but track best result
        for theta, val in zip(thetas, values):
            x_dict = self.space.unpack(theta)
            self._update_best(x_dict, val)
