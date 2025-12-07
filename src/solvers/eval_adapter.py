
from typing import Callable, Dict, Any, Sequence, Iterable, List 
import numpy as np

from problems.interfaces import OptimizationProblemProtocol
from solvers.search_space import SearchSpace


def make_single_objective_fn(
        problem: OptimizationProblemProtocol,
        objective: str= "TSF",
        ) -> Callable[[np.ndarray], float]: 
    """
    Docstring for make_single_objective_fn
    
    :param problem: Description
    :type problem: OptimizationProblemProtocol
    :param objective: Description
    :type objective: str
    :return: Description
    :rtype: Callable[[ndarray[_AnyShape, dtype[Any]]], float]
    
    theta: 1D array in packed seachspace coord.
    """

    def f(theta: np.ndarray) -> float: 
        space: SearchSpace = problem.search_space

        theta = np.asarray(theta, dtype=float)
        theta = space.clip(theta)
        x_dict: Dict[str, Any] = space.unpack(theta)

        # Base1: x_coti, d_mrl, d_cap, cap

        val = problem.evaluate_objective(objective=objective, **x_dict)
        if type(val) == dict: 
            return float(val["value"])
        return float(val)
    return f


#NOTE: NOT PROPERLY IMPLEMENTED!
def make_multi_objective_fn(
    problem: OptimizationProblemProtocol,
    objectives: Sequence[str],
) -> Callable[[np.ndarray], np.ndarray]:
    """
    Docstring for make_multi_objective_fn
    
    :param problem: Description
    :type problem: OptimizationProblemProtocol
    :param objectives: Description
    :type objectives: Sequence[str]
    :return: Description
    :rtype: Callable[[ndarray[_AnyShape, dtype[Any]]], ndarray[_AnyShape, dtype[Any]]]
    
    returns(F(theta)) -> np.ndarray of shape n_objectives, 
    I assume that problem.evaluate_objective can be called witrh the 
    obj function 
    """
    space: SearchSpace = problem.search_space
    obj: List[str] = list(objectives)

    def F(theta: np.ndarray) -> np.ndarray: 
        theta = np.asarray(theta, dtype=float)
        theta = space.clip(theta)
        x_dict = space.unpack(theta)
        #assumption (CUZ NOT IMPLEMENTED) 
        # problem gives us a dict per obj func
        vals: List[float] = []

        for obj_name in obj: 
            v = problem.evaluate_objective(objective=obj_name, **x_dict)
            if type(v) == dict: 
                vals.append(float(v["value"]))
            else: 
                vals.append(float(v))
        return np.asarray(vals, dtype=float)
    return F
    


