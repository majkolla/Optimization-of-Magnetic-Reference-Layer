# MRL Optimization System: Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Physics Engine](#physics-engine)
3. [Figure of Merit (FOM)](#figure-of-merit-fom)
4. [Optimization Framework](#optimization-framework)
5. [Constraints and Search Space](#constraints-and-search-space)
6. [Implementation Details](#implementation-details)

---

## System Overview

This system optimizes **Magnetic Reference Layer (MRL)** designs for neutron reflectometry applications. The goal is to maximize sensitivity to various samples of interest (SOIs) while maintaining physical constraints.

### Key Components
- **Physics Engine**: Parratt recursion for neutron reflectometry
- **FOM Calculator**: Spin-flip metrics and sensitivity measures
- **Optimizer**: Two-stage optimization (Differential Evolution + L-BFGS-B)
- **Problem Definition**: Multilayer stack configuration and constraints

### Design Variables
- `x_coti`: Co:Ti atomic fraction in MRL (0 to 1)
- `d_mrl`: MRL layer thickness (Å)
- `d_cap`: Capping layer thickness (Å)
- `cap`: Choice of capping material (categorical)

---

## Physics Engine

### The Parratt Recursion Algorithm

**Location**: `src/physics/reflectometry.py`

The Parratt formalism calculates neutron reflectivity from a stratified multilayer structure.

#### Mathematical Foundation

For a multilayer stack, neutrons experience:
1. **Fresnel reflection** at each interface
2. **Phase shifts** due to layer thickness
3. **Multiple reflections** between interfaces

#### Wave Vector Calculation

$$k_z = \sqrt{\frac{Q^2}{4} - 4\pi\rho}$$

where:
- $Q$: momentum transfer (scattering vector) in $\text{Å}^{-1}$
- $\rho$: scattering length density (SLD) in $\text{Å}^{-2}$

#### Recursion Formula

Starting from the substrate (bottom), work upward:

$$\Gamma_j = \frac{r_j + \Gamma_{j+1} \cdot \exp(2ik_{z,j+1}d_{j+1})}{1 + r_j\Gamma_{j+1} \cdot \exp(2ik_{z,j+1}d_{j+1})}$$

where:
- $\Gamma_j$: complex reflection amplitude at interface $j$
- $r_j = \frac{k_{z,j} - k_{z,j+1}}{k_{z,j} + k_{z,j+1}}$: Fresnel coefficient
- $d_{j+1}$: thickness of layer $j+1$
- Initial condition: $\Gamma_{\text{substrate}} = 0$

#### Roughness Correction (Nevot-Croce)

Interface roughness is incorporated via:

$$r_j \rightarrow r_j \cdot \exp(-2\sigma_j^2 \cdot k_{z,j} \cdot k_{z,j+1})$$

where $\sigma_j$ is the RMS roughness at interface $j$.

#### Final Reflectivity

$$R(Q) = |\Gamma_0|^2 + \text{bkg}$$

where $\text{bkg}$ is a constant background ($\sim 10^{-3}$).

### Spin-Dependent Scattering

For magnetic layers (MRL), the SLD depends on neutron spin:

**Spin-Up**: $\rho_+ = \rho_n + \rho_m$  
**Spin-Down**: $\rho_- = \rho_n - \rho_m$

where:
- $\rho_n$: nuclear SLD (material property)
- $\rho_m$: magnetic SLD (depends on magnetization)

This creates **spin asymmetry**, enabling sensitivity to magnetic films.

### Magnetic SLD Calculation for Binary Alloys

**Location**: `src/physics/magnetic_sld.py`

The magnetic scattering length density ($\rho_m$) for binary alloys is calculated using a **physically accurate model** that accounts for real atomic density changes as elements mix.

#### Previous Approach (Simplified Linear)

Earlier implementations used a simple linear interpolation:

$$\rho_{\text{mag}} \approx x \cdot \rho_{\text{mag}}(A) + (1-x) \cdot \rho_{\text{mag}}(B)$$

**Problem**: This ignores the fact that atomic packing density changes as you vary composition.

#### Current Approach (Inspired by GenX)

**Location**: `calculate_binary_alloy_magnetic_sld()` function

The new implementation follows the GenX approach with three key steps:

**Calculate Alloy Density**

Use ideal mixing theory to compute molar volume:

$$V_{\text{mol}}(\text{alloy}) = x \cdot \frac{MM_A}{\rho_A} + (1-x) \cdot \frac{MM_B}{\rho_B}$$

where:
- $MM_A$, $MM_B$: Molar masses (g/mol)
- $\rho_A$, $\rho_B$: Pure element densities (g/cm³)
- $x$: Atomic fraction of element A

**Convert to Number Density**

Calculate atoms per unit volume:

$$N = \frac{0.6022}{V_{\text{mol}}(\text{alloy})} \quad [\text{atoms/Å}^2]$$

The factor $0.6022 = N_A / 10^{24}$ converts from mol/cm^3 to atoms/Å^2.

**Calculate Magnetic SLD**

$$\rho_{\text{mag}} = C_{\text{mag}} \cdot N \cdot \mu_{\text{avg}}$$

where:
- $C_{\text{mag}} = 2.645 \times 10^{-5}$ Å²/μB: Fundamental constant relating magnetic moment to SLD
- $\mu_{\text{avg}} = x \cdot \mu_A + (1-x) \cdot \mu_B$: Average magnetic moment per atom (in Bohr magnetons)

**Final units**: $10^{-6}$ $\text{Å}^{-2}$

#### Implementation Details

**Default Co-Ti Parameters**:
```python
Co: MM = 58.933 g/mol, ρ = 8.86 g/cm³, μ = 1.72 μB
Ti: MM = 47.867 g/mol, ρ = 4.506 g/cm³, μ = 0.0 μB (non-magnetic)
```

**Example Calculation** (73% Co, 27% Ti):
```python
from physics.magnetic_sld import coti_magnetic_sld
rho_mag = coti_magnetic_sld(x_co=0.73)  # Returns ~2.59 × 10^-6 UÅ^2
```   

#### Available Functions

1. **`calculate_binary_alloy_magnetic_sld(x_element_A, ...)`**  
   Generic function for any binary alloy with full control over all parameters.

2. **`coti_magnetic_sld(x_co, mu_co=1.72)`**  
   Convenience function specifically for Co-Ti alloys with pre-set parameters.

3. **`create_alloy_sld_function(element_A, element_B)`**  
   Factory function that creates specialized SLD calculators for any binary alloy pair using the built-in `ELEMENT_DATA` database.

4. **`vectorized_magnetic_sld(x_values, ...)`**  
   Vectorized version for efficiently computing SLD across arrays of compositions (useful for plotting).

#### Element Database

The module includes physical properties for common magnetic alloy elements:

| Element | Molar Mass (g/mol) | Density (g/cm³) | Magnetic Moment (μB) |
|---------|-------------------|-----------------|---------------------|
| Co | 58.933 | 8.86 | 1.72 |
| Ti | 47.867 | 4.506 | 0.0 |
| Fe | 55.845 | 7.874 | 2.22 |
| Ni | 58.693 | 8.902 | 0.606 |
| Pt | 195.084 | 21.45 | 0.0 |
| Pd | 106.42 | 12.023 | 0.0 |
| Ta | 180.948 | 16.65 | 0.0 |
| Cu | 63.546 | 8.96 | 0.0 |

**Extension**: New alloys can be easily added to `ELEMENT_DATA` dictionary (potentially add things in the data json file)


### Layer Stack Structure

**Standard Configuration** (top to bottom):
1. **Air/Vacuum**: $\rho = 0$ (reference medium)
2. **Sample of Interest (SOI)**: Variable $\rho_n$, thickness, roughness
3. **Capping Layer**: Protects MRL ($\text{Al}_2\text{O}_3$, $\text{SiO}_2$, Au, etc.)
4. **Magnetic Reference Layer (MRL)**: $\text{Co}_{1-x}\text{Ti}_x$ alloy
5. **Substrate**: Si (semi-infinite)

---

## Figure of Merit (FOM)

**Location**: `src/physics/fom.py`

### Sensitivity Metrics

The optimization targets **three key metrics** for each SOI:

#### 1. Spin-Flip Mirror (SFM)

Measures asymmetry between spin-up and spin-down channels:

$$\text{SFM} = \sum_Q w(Q) \cdot |R_+(Q) - R_-(Q)|$$

**Physical meaning**: Sensitivity to magnetic contrast  
**Higher is better**: Large spin asymmetry

#### 2. Spin-Flip Non-Mirror (SFNM)

Not currently computed in the codebase (set to 0).

#### 3. Magnetic Contrast Factor (MCF)

Normalized sensitivity metric:

$$\text{MCF} = \sum_Q w(Q) \cdot \frac{|R_+(Q) - R_-(Q)|}{R_+(Q) + R_-(Q)}$$

**Physical meaning**: Relative magnetic sensitivity  
**Normalized**: Accounts for total signal level

### Weighting Function

**Location**: `src/physics/fom.py` function `default_weight(Q)`

$$w(Q) = \frac{1}{1 + \exp\left(\frac{Q - Q_0}{\Delta Q}\right)}$$

**Parameters**:
- $Q_0 = 0.12$ $\text{Å}^{-1}$: transition point
- $\Delta Q = 0.02$ $\text{Å}^{-1}$: transition width

**Purpose**: Down-weight high-Q regions where signal is weak

### Total Sensitivity Factor (TSF)

The **objective function** combines metrics across all SOIs:

$$\text{TSF} = \sum_{\text{SOI}} \left(w_{\text{sfm}} \cdot \text{SFM}_i + w_{\text{mcf}} \cdot \text{MCF}_i\right)$$

**Default weights** (in code):
- $w_{\text{sfm}} = 0.5$
- $w_{\text{mcf}} = 0.5$

**Currently**: TSF = sum of SFM across all SOIs

---

## Optimization Framework

### Two-Stage Optimization Strategy

**Location**: `src/Notebooks/presentation.ipynb`

#### Stage 1: Differential Evolution (Global Search)

**Algorithm**: `scipy.optimize.differential_evolution`

**Purpose**: Find global optimum basin in rough search space

**Key Parameters**:
- `strategy = "best1bin"`: Mutation strategy
- `popsize = 25`: Population size (25 × n_vars)
- `maxiter = 10000`: Maximum iterations
- `mutation = (0.5, 1.0)`: Adaptive mutation rate
- `recombination = 0.7`: Crossover probability
- `polish = False`: Don't use L-BFGS-B at end (we do it manually)

**Termination**: Time budget (120s per material) OR convergence

**How it works**:
1. Initialize random population of candidate solutions
2. For each generation:
   - Create mutant vectors by combining population members
   - Cross over mutant with target
   - Keep if better than target
3. Best solution → Stage 2

#### Stage 2: L-BFGS-B (Local Refinement)

**Algorithm**: `scipy.optimize.minimize` with `method="L-BFGS-B"`

**Purpose**: Fine-tune solution from Stage 1

**Key Parameters**:
- `maxiter = 5000`: Maximum iterations
- `ftol = 1e-12`: Function tolerance
- `gtol = 1e-10`: Gradient tolerance

**Why L-BFGS-B?**:
- **Bound-constrained**: Respects box constraints
- **Quasi-Newton**: Uses gradient information (fast convergence)
- **Limited memory**: Efficient for moderate dimensions

**Initial guess**: Best solution from Differential Evolution

### Objective Function

**Location**: `src/problems/base1.py` → `evaluate_objective()`

```python
def evaluate_objective(x_coti, d_mrl, d_cap, cap) -> float:
    """
    Returns: TSF (Total Sensitivity Factor)
    Higher is better.
    """
    # For each SOI:
    #   1. Build layer stack
    #   2. Compute R_up(Q) and R_dn(Q) via Parratt
    #   3. Calculate SFM and MCF
    # Return: sum of all metrics
```

**Optimization setup**:
- Minimize $-\text{TSF}$ (convert maximization to minimization)
- Return negative score to scipy optimizers

---

## Constraints and Search Space

**Location**: `src/problems/base1.py` → `SearchSpace` class

### Box Constraints (Bounds)

All variables have simple lower/upper bounds:

```python
bounds_x:   [0.0, 1.0]      # Co atomic fraction
bounds_d:   [1.0, 1200.0]   # MRL thickness (Å)
bounds_cap: [1.0, 100.0]    # Cap thickness (Å)
```

**Type**: Simple box constraints (no nonlinear constraints)

**Enforced by**: Optimization algorithms (DE and L-BFGS-B support bounds natively)

### Physical Interpretation

#### Co:Ti Ratio (`x_coti`)
- $x_{\text{coti}} = 0$: Pure Ti (low nuclear SLD, negative)
- $x_{\text{coti}} = 1$: Pure Co (high nuclear SLD, positive)
- **Typical**: 0.73 (73% Co, 27% Ti) based on prior work

**Nuclear SLD calculation**:

$$\rho_n(\text{MRL}) = x_{\text{coti}} \cdot \rho_n(\text{Co}) + (1 - x_{\text{coti}}) \cdot \rho_n(\text{Ti})$$
$$= x_{\text{coti}} \cdot 2.265 + (1 - x_{\text{coti}}) \cdot (-1.95) \quad [\times 10^{-6} \text{ Å}^{-2}]$$

#### Thickness Bounds
- **MRL**: 1-1200 Å (very wide range to explore thin vs. thick regimes)
- **Cap**: 1-100 Å (protection layer, typically thin)

**Physical limits**:
- Too thin: Poor coverage, pinholes
- Too thick: Reduced sensitivity, cost

### Discrete Choice: Capping Material

**Materials** (from `data.json`):
- $\text{Al}_2\text{O}_3$: $\rho_n = 5.7 \times 10^{-6}$ $\text{Å}^{-2}$
- $\text{SiO}_2$: $\rho_n = 3.47 \times 10^{-6}$ $\text{Å}^{-2}$
- Au: $\rho_n = 4.5 \times 10^{-6}$ $\text{Å}^{-2}$
- (Plus others in extended database)

**Handled by**: Running separate optimizations for each material, then comparing TSF

---

## Implementation Details

### Material Properties

**Location**: `src/data/data.json`

**Storage convention**: All SLD values in **$10^{-6}$ $\text{Å}^{-2}$** units

**Example**:
```json
{
  "substrate": {"name": "Si", "rho_n": 2.07},
  "caps": {
    "Al2O3": {"rho_n": 5.7, "thickness": 16.0, "sigma": 8.0}
  },
  "mrl": {
    "rho_n_Co": 2.265,
    "rho_n_Ti": -1.95
  }
}
```

**Unit conversion**: `_rho(rho_in_1e6)` multiplies by `SLD_SCALE = 1e-6`

### Samples of Interest (SOI)

**Location**: `src/Notebooks/presentation.ipynb`

Five test cases representing different film types:

| Name | $\rho_n$ ($\times 10^{-6}$ $\text{Å}^{-2}$) | Thickness (Å) | $\sigma$ (Å) |
|------|------------------|---------------|-------|
| Film_LowDensity | 1.0 | 400 | 2 |
| Film_HighDensity | 4.0 | 600 | 5 |
| Film_Thick | 2.0 | 150 | 3 |
| Film_Thin | 3.0 | 200 | 2 |
| build_like | 2.0 | 500 | 15 |

**Purpose**: Ensure MRL performs well across diverse samples

### Q-Grid

**Scattering vector values**: Logarithmically spaced from ~0.009 to 0.3 $\text{Å}^{-1}$

**Typical**: 200 points

**Physical range**:
- Low Q (< 0.05 $\text{Å}^{-1}$): Total reflection regime
- Mid Q (0.05-0.15 $\text{Å}^{-1}$): Most sensitive region
- High Q (> 0.15 $\text{Å}^{-1}$): Weak signal, importance down-weighted

### Code Architecture

```
src/
├── physics/
│   ├── reflectometry.py    # Parratt recursion engine
│   └── fom.py              # SFM, MCF calculations
├── problems/
│   └── base1.py            # Optimization problem definition
├── data/
│   ├── data.json           # Material properties
│   └── materials_loader.py # Load materials from JSON
└── Notebooks/
    └── presentation.ipynb  # Main optimization script
```

### Key Classes

**`Base1OptimizationProblem`**:
- Builds layer stacks
- Calls Parratt engine
- Computes FOM
- Returns TSF


**`Materials`**: Container for substrate, caps, MRL specs

**`SOISpec`**: Defines a sample of interest

**`Bounds`**: Simple (lo, hi) pair for constraints

---

## Algorithm Summary

### Complete Optimization Workflow

1. **Initialize Problem**
   - Load materials from `data.json`
   - Define SOI configurations
   - Set Q-grid (200 points)
   - Set bounds: $x \in [0,1]$, $d \in [1,1200]$, $d_{\text{cap}} \in [1,100]$

2. **For Each Capping Material**:

   **Global Search (Differential Evolution)**
   - Population size: 25 × 2 = 50 (for 2 variables: d_mrl, d_cap)
   - Time budget: 120 seconds
   - Objective: Minimize `-TSF(x_coti=0.73, d_mrl, d_cap, cap)`
   
   **Local Refinement (L-BFGS-B)**
   - Start from DE solution
   - Gradient-based local search
   - Convergence tolerance: ftol=1e-12
   
3. **Select Best Material**
   - Compare TSF across all cap choices
   - Report optimal (x_coti, d_mrl, d_cap, cap)

### Computational Cost

- **Per evaluation**: ~0.01-0.1 seconds (depends on Q-grid size)
- **DE iterations**: ~100-1000 evaluations
- **L-BFGS-B iterations**: ~10-100 evaluations
- **Total per material**: ~2-5 minutes
- **Total for 8 materials**: ~16-40 minutes

## References

- **Parratt, L.G.** (1954). *Surface Studies of Solids by Total Reflection of X-Rays*. Physical Review, 95(2), 359.
- **Differential Evolution**: Storn, R. & Price, K. (1997). *Differential Evolution – A Simple and Efficient Heuristic for Global Optimization*. Journal of Global Optimization, 11, 341-359.
- **L-BFGS-B**: Byrd, R.H., Lu, P., Nocedal, J., & Zhu, C. (1995). *A Limited Memory Algorithm for Bound Constrained Optimization*. SIAM Journal on Scientific Computing, 16(5), 1190-1208.

---
