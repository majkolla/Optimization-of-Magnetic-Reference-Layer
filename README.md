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



## Theory 
These are my personal notes for understanding the material, and not a part of the final report, I might take inspo from this, but i'll have very low writing standards.

### Basic understanding 
- [Polarized Neutron Reflectometry](https://ncnr.nist.gov/programs/reflect/references/pnrchapti.pdf)
- [Understanding interlayer coupling and buried interfacial magnetism using polarized neutron reflectometry](https://www.nist.gov/ncnr/acns-2020-tutorial-ii-practical-approach-fitting-neutron-reflectometry-data/understanding)
- [Neutron Reflectometry](https://neutrons.ornl.gov/sites/default/files/XNS_school_NR_CFM_AUG_2023_images_1_to_50.pdf)
- [A Brief Introduction to Polarised Neutron Reflectivity](https://indico.stfc.ac.uk/event/355/contributions/2208/attachments/786/1380/NR%20Group%20Training%20course%20PNR%20Lecture.pdf)

### Math 
- [Surface Studies of Solids by Total Reflection of X-Rays](https://journals.aps.org/pr/abstract/10.1103/PhysRev.95.359)
- [Influence of surface and interface roughness on X-ray and extreme ultraviolet reflectance](https://opg.optica.org/osac/fulltext.cfm?uri=osac-4-5-1497)
- [Measurement and modeling of polarized specular neutron reflectivity in large magnetic fields](https://pmc.ncbi.nlm.nih.gov/articles/PMC4970493)


### Building the software for fitting stacks
- [ GenX: an extensible X-ray reflectivity refinement program utilizing differential evolution](https://onlinelibrary.wiley.com/doi/abs/10.1107/S0021889807045086)
- [GenX 3: the latest generation of an established tool](https://journals.iucr.org/j/issues/2022/04/00/ge5118/ge5118.pdf)

### Polarized Neutron Reflectometry
We can describe a netron as a QM wave and work with it's reflections from layered materials. So we're intersted in the reflectivity function: $R(Q) = |r(Q)|^2$ as a function of momentum transfew Q and how it's connected to the SLD profile $\rho(z)$.


First represent the neutron as a plane wave: $\Phi(k,r) = e^{ikr}$. 
- k = (k_x, k_y, k_z)
- r = (x,y,z)
- $|\Phi|^2$ is the probability density of finding the neutron at r with momentum p. Howeverm note that a real neutron is a wavepacket, meaning that it's a superposiition of plane waves, but for this problem a single wave approx. is good enough. 

The motion of a netruon is described by s.e. $-\frac{\hbar^2}{2m}\Delta^2 + V(r) = E\Phi$. Inside matter, neutron experience a nuclear potential that can be described by coherent scattering length b and number density N. The SLD is $\rho = Nb$ and $V = 2\pi\hbar^2/m Nb$. And if we have multicomponent materials we just sum over them. They get Helmholtz wave equation, so finally we get that all material information is encoded in $\rho$ where the netron is a wave that propagate in a medium with an index that depends on $\rho$