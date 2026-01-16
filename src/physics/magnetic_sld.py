"""
Magnetic Scattering Length Density (SLD) Calculations

This module provides physically accurate calculations of magnetic SLD for binary
alloys, following the GenX approach. The functions account for:
- Atomic density changes as elements mix
- Physical magnetic moments per atom
- Proper unit conversions

Default parameters are provided for common magnetic alloys.
"""

import numpy as np
from typing import Optional


# Physical Constants
C_MAG = 2.645e-5  # Magnetic SLD constant in Ų * μB⁻¹


# Common Element Properties (Molar Mass in g/mol, Density in g/cm³, Magnetic Moment in μB)
ELEMENT_DATA = {
    'Co': {'MM': 58.933, 'rho': 8.86, 'mu': 1.72},
    'Ti': {'MM': 47.867, 'rho': 4.506, 'mu': 0.0},
    'Fe': {'MM': 55.845, 'rho': 7.874, 'mu': 2.22},
    'Ni': {'MM': 58.693, 'rho': 8.902, 'mu': 0.606},
    'Pt': {'MM': 195.084, 'rho': 21.45, 'mu': 0.0},
    'Pd': {'MM': 106.42, 'rho': 12.023, 'mu': 0.0},
    'Ta': {'MM': 180.948, 'rho': 16.65, 'mu': 0.0},
    'Cu': {'MM': 63.546, 'rho': 8.96, 'mu': 0.0},
}


def calculate_binary_alloy_magnetic_sld(
    x_element_A: float,
    mu_A: float = 1.72,        # Co default
    mu_B: float = 0.0,         # Ti default (non-magnetic)
    MM_A: float = 58.933,      # Co molar mass (g/mol)
    Rho_A: float = 8.86,       # Co density (g/cm³)
    MM_B: float = 47.867,      # Ti molar mass (g/mol)
    Rho_B: float = 4.506,      # Ti density (g/cm³)
) -> float:
    """
    Calculate magnetic SLD for a binary alloy with physical accuracy.
    
    This function accounts for density changes as the two elements mix,
    using ideal mixing theory to calculate the alloy density and then
    computing the magnetic SLD from the number density and magnetic moments.
    
    Parameters:
        x_element_A: Fraction of element A (0.0 to 1.0)
                     0.0 = pure B, 1.0 = pure A
        mu_A: Magnetic moment of element A in Bohr magnetons (μB)
              Default: 1.72 (bulk Co)
        mu_B: Magnetic moment of element B in Bohr magnetons (μB)
              Default: 0.0 (Ti is non-magnetic)
        MM_A: Molar mass of element A (g/mol)
              Default: 58.933 (Co)
        Rho_A: Density of element A (g/cm³)
               Default: 8.86 (Co)
        MM_B: Molar mass of element B (g/mol)
              Default: 47.867 (Ti)
        Rho_B: Density of element B (g/cm³)
               Default: 4.506 (Ti)
    
    Returns:
        float: Magnetic SLD in units of 10⁻⁶ Ų⁻²
    
    Example:
        >>> # Co-Ti alloy with 73% Co
        >>> sld = calculate_binary_alloy_magnetic_sld(0.73)
        >>> print(f"{sld:.4f} × 10⁻⁶ Ų⁻²")
        2.5893 × 10⁻⁶ Ų⁻²
        
        >>> # Fe-Pt alloy with 50% Fe
        >>> sld = calculate_binary_alloy_magnetic_sld(
        ...     0.5,
        ...     mu_A=2.22, MM_A=55.845, Rho_A=7.874,  # Fe
        ...     mu_B=0.0, MM_B=195.084, Rho_B=21.45    # Pt
        ... )
    """
    # Calculate molar volumes (cm³/mol)
    vol_mol_A = MM_A / Rho_A
    vol_mol_B = MM_B / Rho_B
    
    # Average molar volume assuming ideal mixing
    # As composition changes, atomic packing changes non-linearly
    vol_mol_alloy = (x_element_A * vol_mol_A) + ((1 - x_element_A) * vol_mol_B)
    
    # Convert to number density (atoms per Ų)
    # Factor 0.6022 = (Avogadro 6.022e23) / (1e24 Ų/cm³)
    number_density = 0.6022 / vol_mol_alloy
    
    # Calculate average magnetic moment
    # Weighted by composition
    mu_avg = (x_element_A * mu_A) + ((1 - x_element_A) * mu_B)
    
    # Calculate magnetic SLD: ρ_mag = C × N × μ
    rho_mag_raw = C_MAG * number_density * mu_avg
    
    # Return in standard units of 10⁻⁶ Ų⁻²
    return rho_mag_raw * 1e6


def coti_magnetic_sld(x_co: float, mu_co: float = 1.72) -> float:
    """
    Convenience function for Co-Ti alloy magnetic SLD.
    
    This is a specialized wrapper around calculate_binary_alloy_magnetic_sld
    with Co-Ti parameters pre-set.
    
    Parameters:
        x_co: Fraction of Cobalt (0.0 to 1.0)
        mu_co: Magnetic moment per Co atom in μB (default: 1.72)
    
    Returns:
        float: Magnetic SLD in units of 10⁻⁶ Ų⁻²
    """
    return calculate_binary_alloy_magnetic_sld(
        x_element_A=x_co,
        mu_A=mu_co,
        mu_B=0.0,
        MM_A=ELEMENT_DATA['Co']['MM'],
        Rho_A=ELEMENT_DATA['Co']['rho'],
        MM_B=ELEMENT_DATA['Ti']['MM'],
        Rho_B=ELEMENT_DATA['Ti']['rho'],
    )


def create_alloy_sld_function(element_A: str, element_B: str, mu_A: Optional[float] = None, mu_B: Optional[float] = None):
    """
    Create a magnetic SLD function for a specific alloy using element names.
    
    This factory function returns a callable that computes magnetic SLD
    for a binary alloy using predefined element properties.
    
    Parameters:
        element_A: Symbol of element A (e.g., 'Co', 'Fe', 'Ni')
        element_B: Symbol of element B (e.g., 'Ti', 'Pt', 'Ta')
        mu_A: Optional override for magnetic moment of A (default: use ELEMENT_DATA)
        mu_B: Optional override for magnetic moment of B (default: use ELEMENT_DATA)
    
    Returns:
        function: A callable f(x_A, mu_A_override=None) that returns magnetic SLD
    
    Example:
        >>> # Create a Fe-Pt SLD function
        >>> fe_pt_sld = create_alloy_sld_function('Fe', 'Pt')
        >>> sld = fe_pt_sld(0.5)  # 50% Fe
        
        >>> # With custom magnetic moment
        >>> co_ti_sld = create_alloy_sld_function('Co', 'Ti', mu_A=1.6)
        >>> sld = co_ti_sld(0.73)
    """
    if element_A not in ELEMENT_DATA:
        raise ValueError(f"Element '{element_A}' not found in ELEMENT_DATA. Available: {list(ELEMENT_DATA.keys())}")
    if element_B not in ELEMENT_DATA:
        raise ValueError(f"Element '{element_B}' not found in ELEMENT_DATA. Available: {list(ELEMENT_DATA.keys())}")
    
    data_A = ELEMENT_DATA[element_A]
    data_B = ELEMENT_DATA[element_B]
    
    # Use provided mu values or defaults from element data
    mu_A_default = mu_A if mu_A is not None else data_A['mu']
    mu_B_default = mu_B if mu_B is not None else data_B['mu']
    
    def alloy_sld(x_A: float, mu_A_override: Optional[float] = None) -> float:
        """Calculate magnetic SLD for this specific alloy."""
        return calculate_binary_alloy_magnetic_sld(
            x_element_A=x_A,
            mu_A=mu_A_override if mu_A_override is not None else mu_A_default,
            mu_B=mu_B_default,
            MM_A=data_A['MM'],
            Rho_A=data_A['rho'],
            MM_B=data_B['MM'],
            Rho_B=data_B['rho'],
        )
    
    return alloy_sld


def vectorized_magnetic_sld(
    x_values: np.ndarray,
    mu_A: float = 1.72,
    mu_B: float = 0.0,
    MM_A: float = 58.933,
    Rho_A: float = 8.86,
    MM_B: float = 47.867,
    Rho_B: float = 4.506,
) -> np.ndarray:
    """
    Vectorized version of magnetic SLD calculation for arrays of compositions.
    
    Useful for plotting or analyzing SLD vs composition.
    
    Parameters:
        x_values: Array of composition values (0.0 to 1.0)
        Other parameters: Same as calculate_binary_alloy_magnetic_sld
    
    Returns:
        np.ndarray: Array of magnetic SLD values
    
    Example:
        >>> x = np.linspace(0, 1, 100)
        >>> sld = vectorized_magnetic_sld(x)
        >>> plt.plot(x, sld)
    """
    return np.array([
        calculate_binary_alloy_magnetic_sld(
            x, mu_A, mu_B, MM_A, Rho_A, MM_B, Rho_B
        ) for x in x_values
    ])


# Export main functions
__all__ = [
    'calculate_binary_alloy_magnetic_sld',
    'coti_magnetic_sld',
    'create_alloy_sld_function',
    'vectorized_magnetic_sld',
    'ELEMENT_DATA',
    'C_MAG',
]
