
from typing import Callable, Dict, Any, Sequence, Iterable, List 
import numpy as np

from problems.interfaces import OptimizationProblemProtocol
from solvers.search_space import SearchSpace


def make_single_objective_fn(
        problem: OptimizationProblemProtocol,
        objective: str= "TSF",
        ) -> Callable[[np.ndarray], float]: 
    ...

def make_multi_objective_fn(
    problem: OptimizationProblemProtocol,
    objectives: Sequence[str],
) -> Callable[[np.ndarray], np.ndarray]:
    ...
    