# Optimization of Magnetic Reference Layer Design in Polarized Neutron Reflectometry


## Repo structure 
- **src**
  - data
  - physics
    - fom.py
    - reflectometry.py
  - problems 
    - base1.py
    - base2.py
  - solvers 
    - base.py
    - callback.py
    - constraints.py
    - evaluation.py 
    - multi_objective.py
    - robustness.py 
    - search_space.py
    - single_obj.py


## Optimzation problem 
There may be multiple configurations that returns similar results, thus getting the *best* configurations is about finding a configurations that does more than simply perform well with some metric. We may have errors in construction, we may have stability or robustness problems.  

For problem defintion *base1* we have:

${\rm TSF}(x_{\text{CoTi}},\; d_{\text{MRL}},\; c)\\$
s.t.
$\\x_{\text{CoTi}}\in [0,1]$, $d_{\text{MRL}} > 0$, $c\in{\text{Al}_2\text{O}_3,\;
\text{SiO}_2,\text{Au}}$

## Finihsed product
- problem = Base1OptimizationProblem(...)
- solver = Alg1Solver(problem)
- result = solver.run(evals=500)
