import numpy as np

def _kz(Q, rho):
    return np.sqrt((Q**2)/4.0 - 4.0*np.pi*(1e-6)*rho + 0j)

def parratt_amplitude(Q, layers):
    k = [_kz(Q, float(L["rho"])) for L in layers]

    Gamma = np.zeros_like(Q, dtype=np.complex128)  # start at substrate
    N = len(layers) - 1

    for j in range(N-1, -1, -1):
        k_i, k_j = k[j], k[j+1]
        rj = (k_i - k_j) / (k_i + k_j)

        # Stable Nevot–Croce (damping only)
        sigma_j = float(layers[j].get("sigma", 0.0))
        if sigma_j:
            # exponent = -2 * sigma^2 * Re(k_i * k_j)  (clip to <= 0)
            expo = -2.0 * (sigma_j**2) * np.real(k_i * k_j)
            expo = np.minimum(expo, 0.0)
            rj *= np.exp(expo)

        # Phase through the *lower* layer (j+1)
        d_lower = float(layers[j+1].get("thickness", 0.0))
        phase = np.exp(2j * k_j * d_lower)

        Gamma = (rj + Gamma * phase) / (1.0 + rj * Gamma * phase)

    return Gamma

def reflectivity(Q, layers, bkg=0.0):
    return np.abs(parratt_amplitude(Q, layers))**2 + float(bkg)

def spin_sld(rho_n, rho_m, spin='up'):
    return rho_n + (rho_m if spin == 'up' else -rho_m)
