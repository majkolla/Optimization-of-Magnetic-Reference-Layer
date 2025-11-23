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

The motion of a netruon is described by s.e. $-\frac{\hbar^2}{2m}\Delta^2 + V(r) = E\Phi$. Inside matter, neutron experience a nuclear potential that can be described by coherent scattering length b and number density N. The SLD is $\rho = Nb$ and $V = 2\pi\hbar^2/m Nb$. And if we have multicomponent materials we just sum over them. They get Helmholtz wave equation, so finally we get that all material information is encoded in $\rho$ where the netron is a wave that propagate in a medium with an index that depends on $\rho$. Then they define a refractive index that is similar to *normal* optics. This is basically a refractive index and we get that neutrons see most materials as slighty lower index than vacuum, so everything reflects below a crtiical angle (Q). 


So now we can look into a flat film, uniform in plane with thichness L, infinite in x, y. Let's assume that we have: $\rho(x,y,z) = \rho(z)$. They do some shit and utilize that wehave $k_x, k_y$ are unchanged and independent so they sepearet them and find the solutions for a constant $\rho$. We can then combine multiple regions and solve it using the usual matrix form for refraction stuff. 

We can also look into a nonuniform SLD profile. This would basically mean that we're dropping the basic assumption of $\rho$ being constant. Here they suggest that we approximate $\rho$ by creating many thin bins of thickness dL where each of those has a constant SLD (Figure 1.6). 

The point is: 
- divide the film into N bins 
- Each bin j has constant $\rho$
- for each bin, we have a 2x2 transfer matrix of the form eq 1.24 in the article. This is what I've been trying to implement in python. 


So generally they say a good rule of thumb is $dL \sim \pi/Q_{max}$. They also note that there is an inverse problem here. We get a measure of intensity from the experiment: $|r|^2$ and we want $\rho$. So we cannot simply do direct inversion becuase the phase of r is lost. Thus they do fitting of nonlinear least squares to fit $\rho$ to the data, and then the solutions may not be unique. They also do mention that reference layer methods can give the full complex r(Q) and give a uniqe inversion. My good friend is working on an inverse problem library in python, and i might just write something there that could solve this, we'll see. 

My understanding of part 1.3 is simply the fact that we're adding spin and we thus get two internal states, we get magnetic moment $\mu$ and the wavefunction becomes a 2 component spinor. However they usea polarization vector as a way to more intuitively think about the spin state. 

There is an explicit form of spin dependent neutron wave function, where we have a complex coeff. that abs square describes the probaility amplitudes for each spin state, and we have spatial wave function for spin up and down, this is how they construct it, i dont feel like writing it, but it's intersting, they also have these complex coefficients with the sum of their conjugates are 1. They call them probability amplitudes and i find it very intersting. 
Finally i understand that i have two $\rho$, one that is spin independent and one that is dependent. They then talk about the pauli group, as a operator basis for spin. Then they use the spin rotation op. which is used for the polarization part. 

I find this part intersting, trying to make it more intuitive by introducing an polarization vector object. I'll not write the math here, but basically, they define $P = (P_x, P_y, P_z)$ that can represent the spin orientation. then they introduce the density matrix for one neutron. (See eq. 1.42 and 1.43). They show that you can write the density matrix using the polarization vecotr and pauli matrices. 