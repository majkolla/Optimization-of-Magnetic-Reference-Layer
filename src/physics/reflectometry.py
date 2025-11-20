import numpy as np

def _kz(Q, rho):
    # z-wavevector; allow complex in total reflection region
    return np.sqrt((Q**2)/4.0 - 4.0*np.pi*rho + 0j)

def parratt_amplitude(Q, layers, sigmas):
    """w
    layers: [{'rho': float, 'd': float}, ...] from (0) to substrate (N);
            ambient/substrate thickness ignored
    sigmas: [sigma_0|1, sigma_1|2, ..., sigma_{N-1}|N]
    Returns Gamma_0(Q) (or the complex reflection amplitude).
    """
    N = len(layers) - 1

    k = [ _kz(Q, L['rho']) for L in layers ]
    Gamma = np.zeros_like(Q, dtype=np.complex128)  # start in substrate
    
    for j in range(N-1, -1, -1):
        rj = (k[j] - k[j+1]) / (k[j] + k[j+1])
        sigma = sigmas[j] if j < len(sigmas) else 0.0
        rj *= np.exp(-2.0 * k[j] * k[j+1] * (sigma**2))  # Nevot–Croce
        phase = np.exp(2j * k[j+1] * layers[j+1].get('d', 0.0))
        Gamma = (rj + Gamma * phase) / (1.0 + rj * Gamma * phase)
    
    return Gamma

def reflectivity(Q, layers, sigmas, bkg=0.0):
    return np.abs(parratt_amplitude(Q, layers, sigmas))**2 + bkg

def spin_sld(rho_n, rho_m, spin='up'):
    return rho_n + (rho_m if spin == 'up' else -rho_m)
