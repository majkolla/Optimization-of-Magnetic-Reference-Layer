# Optimization of Magnetic Reference Layer Design in Polarized Neutron Reflectometry


## Repo structure 

The structure here is going to be a problem class, where all the functions are defined and TSF etc are defined with all parameters, then ill have a solver class that takes in the problem class and finds the optimum for the parameters.



### Consider the base2 optimzation: 


In source: 

base2opt/
  __init__.py
  problems/ # problem defintion 
    __init__.py
    base2.py
  physics/  # the physics 
    __init__.py
    reflectometry.py 
  solvers/ # solvers for that problem 
    __init__.py
            # not decided the algorthims yet

#### physics 
In the physics part i'd define the reflecitivty functions, sfm, mcf, tsf, sensitivity etc. All the physics stuff would be define there, and ill try to implement it myself to gain understanding. 

#### Base2 
Will contains the problem class, bounds, SOI:s constraints etc. 
