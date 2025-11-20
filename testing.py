import numpy as np
import matplotlib.pyplot as plt

# Units 
# Q in Å^{-1}
# thickness d 
# roughness sigma in Å
# SLDs rho in Å^{-2}

"""
Thoughts: 
we can for example define spin as a "binary" string, with up and down parameters. 
we can also have 1, 0. For the simple script ill just do up and down

"""

def kz(Q, rho):
    return np.sqrt((Q**2)/4.0 - 4.0*np.pi*rho + 0j)  # 0j to allow complex

def reflectivity(Q, layers, roughness, spin='up', F=None, bkg=0.0):
    sgn = +1 if spin == 'up' else -1
    N = len(layers) - 1  # last is substrate

    rho_s = [L['rho_n'] + sgn * L.get('rho_m', 0.0) for L in layers]
    k = [kz(Q, r) for r in rho_s]

    Gamma = np.zeros_like(Q, dtype=np.complex128)

    for j in range(N-1, -1, -1):
        rj = (k[j] - k[j+1]) / (k[j] + k[j+1])
        sigma = roughness[j] if j < len(roughness) else 0.0
        rj *= np.exp(-2.0 * k[j] * k[j+1] * (sigma**2))

        dj1 = layers[j+1].get('d', 0.0)
        phase = np.exp(2j * k[j+1] * dj1)

        Gamma = (rj + Gamma * phase) / (1.0 + rj * Gamma * phase)

    R = np.abs(Gamma)**2
    if F is not None:
        R = F(Q) * R
    return R + bkg

air = {'rho_n': 0.0, 'rho_m': 0.0, 'd': 0.0}
mrl = {'rho_n': 1.0e-6, 'rho_m': 2.0e-6, 'd': 100.0}  # 100 Å
cap = {'rho_n': 3.5e-6, 'rho_m': 0.0,'d': 16.0}
soi = {'rho_n': 2.0e-6, 'rho_m': 0.0,'d': 500.0}
sub = {'rho_n': 2.07e-6,'rho_m': 0.0, 'd': 0.0}   

layers = [air, mrl, cap, soi, sub]
rough = [3.0, 5.0, 8.6, 3.0]  # sigma_air/MRL, sigma_MRL/cap, sigma_cap/SOI, sigma_SOI/sub  (Å)

Q = np.linspace(0.005, 0.25, 1000)  # Å^-1
R_up = reflectivity(Q, layers, rough, spin='up',   bkg=1e-5)
R_down = reflectivity(Q, layers, rough, spin='down', bkg=1e-5)

