# physics.magnetic_sld Module

Generic magnetic SLD calculator for binary alloys with Co-Ti defaults.

## Quick Start

```python
from physics.magnetic_sld import coti_magnetic_sld

# Calculate magnetic SLD for 73% Co, 27% Ti
sld = coti_magnetic_sld(0.73)
print(f"{sld:.4f} × 10^-6 U^-2")  # Output: 2.5893 × 10^-6 U^-2
```

## Functions

### 1. `coti_magnetic_sld(x_co, mu_co=1.72)`
**Convenience function for Co-Ti alloys** (most common use case)

```python
from physics.magnetic_sld import coti_magnetic_sld

# Default Co magnetic moment (1.72 micro B)
sld = coti_magnetic_sld(0.73)

# Custom Co magnetic moment 
sld = coti_magnetic_sld(0.73, mu_co=1.6)
```

### 2. `calculate_binary_alloy_magnetic_sld(...)`
**Generic function for any binary alloy**

```python
from physics.magnetic_sld import calculate_binary_alloy_magnetic_sld

# Fe-Pt alloy with 50% Fe
sld = calculate_binary_alloy_magnetic_sld(
    x_element_A=0.5,
    mu_A=2.22,      # Fe magnetic moment
    mu_B=0.0,       # Pt non-magnetic
    MM_A=55.845,    # Fe molar mass
    Rho_A=7.874,    # Fe density
    MM_B=195.084,   # Pt molar mass
    Rho_B=21.45     # Pt density
)
```

### 3. `create_alloy_sld_function(element_A, element_B)`
**Factory function using element database**

```python
from physics.magnetic_sld import create_alloy_sld_function

# Create a Fe-Pt SLD calculator
fe_pt_sld = create_alloy_sld_function('Fe', 'Pt')
sld = fe_pt_sld(0.5)  # 50% Fe

# With custom magnetic moment
co_ti_sld = create_alloy_sld_function('Co', 'Ti', mu_A=1.6)
sld = co_ti_sld(0.73)
```

### 4. `vectorized_magnetic_sld(x_values, ...)`
**For plotting/analysis of SLD vs composition**

```python
from physics.magnetic_sld import vectorized_magnetic_sld
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 1, 100)
sld = vectorized_magnetic_sld(x)  # Uses Co-Ti defaults

plt.plot(x, sld)
plt.xlabel('Co Fraction')
plt.ylabel('Magnetic SLD (10⁻⁶ Ų⁻²)')
plt.show()
```

## Element Database

Available elements in `ELEMENT_DATA`:

| Element | Molar Mass (g/mol) | Density (g/cm³) | Mag. Moment (μB) |
|---------|-------------------|-----------------|------------------|
| Co      | 58.933            | 8.86            | 1.72             |
| Ti      | 47.867            | 4.506           | 0.0              |
| Fe      | 55.845            | 7.874           | 2.22             |
| Ni      | 58.693            | 8.902           | 0.606            |
| Pt      | 195.084           | 21.45           | 0.0              |
| Pd      | 106.42            | 12.023          | 0.0              |
| Ta      | 180.948           | 16.65           | 0.0              |
| Cu      | 63.546            | 8.96            | 0.0              |

```python
from physics.magnetic_sld import ELEMENT_DATA

print(ELEMENT_DATA['Co'])
# {'MM': 58.933, 'rho': 8.86, 'mu': 1.72}
```

## Example: Using in Optimization

```python
from physics.magnetic_sld import coti_magnetic_sld
from problems.base1 import MRL

# Define MRL with magnetic SLD function
mrl = MRL(
    rho_n_Co=1.21,
    rho_n_Ti=-1.94,
    m_sld_from_x=coti_magnetic_sld,  # Pass the function!
    sigma_sub_mrl=5.0,
    sigma_mrl_cap=5.0
)
```

## Physics Behind It

The calculation accounts for:

1. **Atomic packing density** - Co and Ti have different sizes
2. **Number density** - atoms per U changes non linearly  
3. **Magnetic moments** - weighted average by composition

Formula: **ρ_mag = C × N × micro_avg**

Where:
- C = 2.645 × 10⁻⁵ U·micro B^2 (constant)
- N = number density (atoms/U)
- micro_avg = composition-weighted magnetic moment

## Validation

```python
from physics.magnetic_sld import coti_magnetic_sld

# Pure Co should be ~4.2 × 10^-6 U^-2
sld_pure_co = coti_magnetic_sld(1.0)
print(f"{sld_pure_co:.2f}")  # 4.12 

# Literature value: 4.20 × 10^-6 U^-2
# Error: 1.9% 
```

## Adding New Elements

Edit `ELEMENT_DATA` in `physics/magnetic_sld.py`:

```python
ELEMENT_DATA = {
    # ... existing elements ...
    'Cr': {'MM': 51.996, 'rho': 7.19, 'mu': 0.0},  # Add Chromium
}
```

Then use:
```python
co_cr_sld = create_alloy_sld_function('Co', 'Cr')
```
