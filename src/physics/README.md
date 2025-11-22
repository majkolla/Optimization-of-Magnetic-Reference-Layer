## Kinematics

$Q = \frac{4\pi}{\lambda} \sin\theta$

For layer $( j = 0, \ldots, N )$
define the *spin-dependent SLD* in the layer:

$
\rho^{(\uparrow)}_j(z) = \rho_{n,j}(z) + \rho_{m,j}(z),
\qquad
\rho^{(\downarrow)}_j(z) = \rho_{n,j}(z) - \rho_{m,j}(z).
$

Here
$
\rho_n = \sum_i N_i b_i, 
\qquad
\rho_m = C M
$


Define the z component wavevector in layer $j$ 

$
k_{j,s}(Q) =
\sqrt{\frac{Q^2}{4} - 4\pi \rho^{(s)}_j},
\qquad
s \in \{\uparrow,\downarrow\}$

## Interface Fresnel coefficient with roughness (Nevot--Croce)

$
r_{j,j+1,s}(Q) =
\frac{k_{j,s} - k_{j+1,s}}{k_{j,s} + k_{j+1,s}}
\exp\!\left(
-2 k_{j,s} k_{j+1,s} \, \sigma_{j,j+1}^2
\right),
$

where $(sigma_{j,j+1})$ is the rms roughness of interface \( j|j+1 \).  


## Parratt recursion (propagate phases through thickness $d_j$

For the semi-infinite substrate:

$
\Gamma_{N,s}(Q) = 0
$

For layer (j)

$
Gamma_{j,s}(Q) =
\frac{
r_{j,j+1,s}(Q)
+
\Gamma_{j+1,s}(Q)
\exp\!\left(2 i k_{j+1,s}(Q) d_{j+1}\right)
}{
1
+
r_{j,j+1,s}(Q)\,
\Gamma_{j+1,s}(Q)
\exp\!\left(2 i k_{j+1,s}(Q) d_{j+1}\right)
}.
$

## Specular reflectivity

With optional footprint $F(Q) \le 1$ and background $b$:

$
R_s(Q; x) =
F(Q)\, \left| \Gamma_{0,s}(Q) \right|^2 + b.
$




# Theory

### Basic understanding 
- https://ncnr.nist.gov/programs/reflect/references/pnrchapti.pdf?utm_source=chatgpt.com
- https://www.nist.gov/ncnr/acns-2020-tutorial-ii-practical-approach-fitting-neutron-reflectometry-data/understanding?utm_source=chatgpt.com
- https://neutrons.ornl.gov/sites/default/files/XNS_school_NR_CFM_AUG_2023_images_1_to_50.pdf?utm_source=chatgpt.com
- https://indico.stfc.ac.uk/event/355/contributions/2208/attachments/786/1380/NR%20Group%20Training%20course%20PNR%20Lecture.pdf?utm_source=chatgpt.com

### Math 
- https://journals.aps.org/pr/abstract/10.1103/PhysRev.95.359?utm_source=chatgpt.com
- https://opg.optica.org/osac/fulltext.cfm?uri=osac-4-5-1497
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4970493/?utm_source=chatgpt.com


### Building the software for fitting stacks
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4970493/?utm_source=chatgpt.com
- https://journals.iucr.org/j/issues/2022/04/00/ge5118/ge5118.pdf?utm_source=chatgpt.com