
from solvers.base import Solver
from typing import List, Sequence, Any, Optional
import numpy as np

class GradientSolver(Solver):
    """
    Placeholder for Gradient-based solver (e.g. BFGS, Adam)
    """
    def ask(self, n: int = 1) -> List[np.ndarray]:
        return [self.space.sample(1)[0] for _ in range(n)]

    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        pass
    
    def reset(self) -> None:
        super().reset()

class CMASolver(Solver):
    """
    Placeholder for CMA-ES Solver
    """
    def ask(self, n: int = 1) -> List[np.ndarray]:
        return [self.space.sample(1)[0] for _ in range(n)]

    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        pass
    
    def reset(self) -> None:
        super().reset()

class BayesianSolver(Solver):
    """
    Placeholder for Bayesian Optimization Solver (Gaussian Processes)
    """
    def ask(self, n: int = 1) -> List[np.ndarray]:
        return [self.space.sample(1)[0] for _ in range(n)]

    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        pass
    
    def reset(self) -> None:
        super().reset()

class NSGA2Solver(Solver):
    """
    Placeholder for NSGA-II Multi-objective Solver
    """
    def ask(self, n: int = 1) -> List[np.ndarray]:
        return [self.space.sample(1)[0] for _ in range(n)]

    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        pass
    
    def reset(self) -> None:
        super().reset()

class ParEGOSolver(Solver):
    """
    Placeholder for ParEGO Multi-objective Solver
    """
    def ask(self, n: int = 1) -> List[np.ndarray]:
        return [self.space.sample(1)[0] for _ in range(n)]

    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) -> None:
        pass
    
    def reset(self) -> None:
        super().reset()
