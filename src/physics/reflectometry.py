import numpy as np

def _kz(Q, rho):
    return np.sqrt((Q**2)/4.0 - 4.0*np.pi*rho + 0j)

def parratt_amplitude(Q, layers):
    # k_z in each layer (uses your existing _kz)
    k = [_kz(Q, float(L["rho"])) for L in layers]

    # Start from substrate: r_N-1 = 0
    Gamma = np.zeros_like(Q, dtype=np.complex128)
    N = len(layers) - 1  # number of interfaces

    # Recurse upward across interfaces j = N-1 ... 0
    for j in range(N-1, -1, -1):
        k_i, k_j = k[j], k[j+1]

        # Fresnel coefficient
        rj = (k_i - k_j) / (k_i + k_j)

        # Nevot–Croce roughness factor: take sigma from the *upper* layer j
        sigma_j = float(layers[j].get("sigma", 0.0))
        if sigma_j != 0.0:
            rj *= np.exp(-2.0 * k_i * k_j * (sigma_j**2))

        # Phase through the *lower* layer (j+1)
        d_lower = float(layers[j+1].get("thickness", 0.0))
        phase = np.exp(2j * k_j * d_lower)

        Gamma = (rj + Gamma * phase) / (1.0 + rj * Gamma * phase)

    return Gamma

def reflectivity(Q, layers, bkg=0.0):
    return np.abs(parratt_amplitude(Q, layers))**2 + float(bkg)

def spin_sld(rho_n, rho_m, spin='up'):
    return rho_n + (rho_m if spin == 'up' else -rho_m)
