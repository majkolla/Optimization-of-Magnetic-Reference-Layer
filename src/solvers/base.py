from dataclasses import dataclass, field 
from typing import Any, Dict, List, Tuple, Optional, Sequence, Protocol
from abc import ABC, abstractmethod
import numpy as np 
import json
from problems.interfaces import OptimizationProblemProtocol
from solvers.search_space import SearchSpace


"""
Common interface for all problem types
Result container 

"""

class OptimizationProblemProtocol(Protocol): 
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
    history: List[Dict[str, Any]] = field(default_factory=list)
    n_evals: int = 0 
    meta: Dict[str, Any] = field(default_factory=list)

    @staticmethod
    def _to_json_safe(obj: Any) -> Any:
        """Recursively convert an object to something JSON serializable."""
        if isinstance(obj, dict):
            return {str(k): RunResults._to_json_safe(v) for k, v in obj.items()}

        if isinstance(obj, (list, tuple)):
            return [RunResults._to_json_safe(v) for v in obj]

        # numpy arrays
        if hasattr(obj, "tolist") and callable(obj.tolist):
            return obj.tolist()

        # numpy scalars
        if hasattr(obj, "item") and callable(obj.item):
            try:
                return obj.item()
            except Exception:
                pass

        return obj

    def to_dict(self) -> Dict[str, Any]:
        return self._to_json_safe({
            "x_best": self.x_best,
            "y_best": self.y_best,
            "history": self.history,
            "n_evals": self.n_evals,
            "meta": self.meta,
        })

    def to_json(self, path: str, indent: int = 2) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=indent)

    def summary(self, max_history: int = 3) -> str:
        lines: list[str] = []
        lines.append("=== RunResults ===")
        lines.append(f"n_evals : {self.n_evals}")
        lines.append(f"y_best  : {self.y_best}")
        lines.append("x_best  :")
        for k, v in self.x_best.items():
            lines.append(f"  {k:10s} = {v}")

        lines.append(f"history : {len(self.history)} entries")
        if self.history:
            lines.append("history (first/last):")
            head = self.history[:max_history]
            tail = self.history[-max_history:] if len(self.history) > max_history else []
            for i, h in enumerate(head):
                lines.append(f"  [{i}] y={h.get('y')} x={h.get('x')}")
            if tail:
                lines.append("  ...")
                offset = len(self.history) - len(tail)
                for i, h in enumerate(tail, start=offset):
                    lines.append(f"  [{i}] y={h.get('y')} x={h.get('x')}")

        if self.meta:
            lines.append(f"meta    : {self.meta}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()

    def __repr__(self) -> str:
        return (
            f"RunResults(y_best={self.y_best}, n_evals={self.n_evals}, "
            f"x_best={self.x_best}, history_len={len(self.history)})"
        )
class Solver: 
    """
    Core solver API (ask/tell + run) 
    """
    def __init__(self, 
                 problem: OptimizationProblemProtocol, 
                 maximize: bool = True,) -> None: 
        self.problem = problem
        self.space: SearchSpace = problem.search_space
        self.maximize = maximize

        self._X: List[Dict[str, Any]] = []
        self._Y: List[Any] = []
        self._x_best: Optional[Dict[str, Any]] = None
        self._y_best: Optional[Any] = None
    
    # ------------- abstract tings ----------------
    @abstractmethod
    def ask(self, n: int = 1) -> List[np.ndarray]:
        """
        Docstring for ask
        
        :param self: Description
        :param n: Description
        :type n: int
        :return: Description
        :rtype: List[ndarray[_AnyShape, dtype[Any]]]
        
        Propose n new candidate points in packed search space 
        Each element is a 1D np.ndarray of length == number of params 
        """
    @abstractmethod
    def tell(self, thetas: List[np.ndarray], values: Sequence[Any]) ->None: 
        """
        Docstring for tell
        
        :param self: Description
        :param thetas: Description
        :type thetas: List[np.ndarray]
        :param values: Description
        :type values: Sequence[Any]
        
        Inform the solver about evaled points and their obj val
        also updates best so far
        """
        ...

    @abstractmethod
    def reset(self) -> None: 
        """
        Docstring for reset
        
        :param self: Description
        
        reset all internal state but keep the ref to the prob
        """
        ...

    # --------- helpers --------------
    def best(self) ->Tuple[Dict[str, Any], Any]: 
        return self._x_best, self._y_best
    
    def _update_best(
            self, 
            x_dict: Dict[str, Any], 
            value: Any, 
            ) -> None:
        if self._y_best is None: 
            self._x_best = dict(x_dict)
            self._y_best = value
            return 
        # simple scalar comp. 

        if self.maximize:
            if float(value) > float(self._y_best): 
                self._x_best = dict(x_dict)
                self._y_best = value
        else:
            if float(value) < float(self._y_best):
                self._x_best = dict(x_dict)
                self._y_best = value

    # -------- defalt run 

    def run(self, evals: int) -> RunResults: 
        """
        Docstring for run
        
        :param self: Description
        :param evals: Description
        :type evals: int
        :return: Description
        :rtype: RunResults
        
        Simple eval loop. More sophisticated solver can override this
        """
        self.reset()
        history: List[Dict[str, Any]] = []
        n_evals = 0 
        
        while n_evals < evals: 
            thetas = self.ask(1)
            theta = thetas[0]

            # clip + unpack -> dict

            theta = self.space.clip(theta)
            x_dict = self.space.unpack(theta)

            y = self.problem.evaluate_objective(**x_dict)

            self.tell([theta], [y])
            n_evals += 1 

            history.append(
                {
                    "theta": theta.copy(), 
                    "x": dict(x_dict), 
                    "y": y,
                }
            )
        x_best, y_best = self.best()

        return RunResults(
            x_best= x_best, 
            y_best = y_best, 
            history=history, 
            n_evals=n_evals, 
            meta={"problem_name": self.problem.name, "Maximize": self.maximize}
        ) 