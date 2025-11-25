# Problem Layer 
This part is about defining the optimzation problem, we may define multiple optimzation problems, as i've called them base 1, base 2 etc. This part will also contian a OP-protocol  (optimzation problem protocol), which simply is a small interface that any problem must satisfy, By writing it like this we gain generality such that the solver can solve all problem types, and thus more intricate optimzation problems in the future will be solvable by this solver. 


- OptimzizationProblemProtocol 
An interface that all problem classes must satisfy. 
    - Eval obj 
    - search space 
    - name 

- Base1OptProblem 
    - The concrete implementation for the Base-1 design. We only optimze Co-Ti, MRL thickness and cap material. 
    - it builds the layer stacks (Si, MRL(x,d), cap, SOI)
    - owns and returns searchspace with x_coti, d_mrl and cap 

- Base2OptProblem 
    -   Basically the same, but with more vars

# The domain
- SearchSpace 
    - This is a container for parameters, this is for holding all parameters with their constraicts and all that. 

# Solver 
- Solver (Abstract class)
    - run()
    - ask()
    - best()
    - reset()
    