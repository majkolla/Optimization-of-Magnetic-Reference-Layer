
import numpy as np
from itertools import product
from typing import List, Sequence, Any
from solvers.base import Solver

class GridSearchSolver(Solver):
    """
    GridSearchSolver that discretizes the search space and evaluates all points.
    """
    def __init__(self, problem, n_points: int = 5, maximize: bool = True):
        super().__init__(problem, maximize)
        self.n_points = n_points
        self._grid_iterator = None

    def reset(self) -> None:
        super().reset()
        # Create a grid for each continuous parameter
        # For categorical, use all choices.
        # For integer, use linspace and round.
        
        # Build a list of arrays
        param_grids = []
        for p in self.space.params:
            if hasattr(p, 'choices'): # Categorical
                packed_choices = [p.pack(c) for c in p.choices]
                param_grids.append(packed_choices)
            else:
                lo = p.lo
                hi = p.hi
                
                # Generate n_points
                grid = np.linspace(lo, hi, self.n_points)
                param_grids.append(grid)
        
        # Create cartesian product
        self._grid = list(product(*param_grids))
        self._grid_idx = 0

    def ask(self, n: int = 1) -> List[np.ndarray]:
        if self._grid_iterator is None:
            # We initialize lazily or in reset. 
            # If reset wasnt called manually, rely on run() calling reset()
            if not hasattr(self, '_grid'):
                self.reset()
        
        points = []
        for _ in range(n):
            if self._grid_idx < len(self._grid):
                point = np.array(self._grid[self._grid_idx])
                points.append(point)
                self._grid_idx += 1
            else:
                # Return random to keep loop going if budget > grid size
                return [self.space.sample(1)[0]]
        
        return points

    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        # Update best
        for theta, val in zip(thetas, values):
            x_dict = self.space.unpack(theta)
            self._update_best(x_dict, val)
