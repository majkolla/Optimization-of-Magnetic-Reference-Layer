from typing import Protocol, runtime_checkable, Dict, Any
from solvers.search_space import SearchSpace 



@runtime_checkable
class OptimizationProblemProtocol(Protocol): 
    """
    Interface for OptmzationProblem
    """
    @property
    def name(self) -> str: ...

    @property
    def search_space(self) -> SearchSpace: ...

    def evaluate_objective(
        self,
        *,
        objective: str = "TSF",
        return_breakdown: bool = False,
        **kwargs: Any,
    ) -> float | Dict[str, Any]:
        ...