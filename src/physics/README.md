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




