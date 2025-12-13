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
    -   Basically the same, but with more parameters

# The domain
- SearchSpace 
    - This is a container for parameters, this is for holding all parameters with their constraicts and all that. 

# Solver 
## Solver (Abstract class)
    - run()
    - ask()
    - best()
    - reset()

## Subclasses single obj
    - Different implemented algorthims for solving the problem 
    - these will be

## Subclasses multi obj 
These are either treating the SFM and MCF separatly giving a pareto solution, or they're combining TSF with other things such as cost and stability. 



    - something 
    - some other alg etc 

## Mixed discrete 
This will iterate over each choice in cap material for example and runs a continouous solver then compare. The reaosn for this design is to keep all the continuous algorthims simple and not mix it all together. 

## Constraints and Robustness 
This is for solvers that doesnt have constraints built in, sort of acts like a langrangian for them.

    - PenaltyAdapter
    - RepairAdapter
    - MCRobustness 

## Callback and stopping 
Logging, hooks for progress etc. Also stopping rules and timilimit and no improvement stuff. 

## Eval adapters
Builds a scalar callable the solver than can use to compute for single obj func. For multi we just return a tuple. 

## Utils 
Basically the stuff we use for reproducability, for example seeds. 

# Flow 
We define a problem as a class that implements physics and has a eval objective function, and publishes a searchspace. The solver get's the problem and reads the searchspace and preps all the representation inside like samplings embeddings and other stuff. We can wrap the prblem eval via single obj or multi obj to compute eval. Also we haev room for more wrappers such as constraints and MC robustness etc. Then we simply run the loop and get the results. Another good thing about the structure is taht we can implement new solver very easily and fast to see the different solutions, we can of course do the same for the problems and see the solutions we get there.

