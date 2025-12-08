import numpy as np

def sensitivity(Q, R_sub, R_full, eps=1e-30):
    return (R_sub - R_full) / (R_sub + R_full + eps)

def sfm(Q, S, w=None):
    y = np.abs(S) if w is None else np.abs(S) * w 
    return np.trapezoid(y, Q) 

def mcf(Q, S_up, S_down, w=None):
    y = np.abs(S_up - S_down) if w is None else np.abs(S_up - S_down) * w
    return np.trapezoid(y, Q)

def tsf(foms_over_types):
    # foms_over_types: iterable of (SFM_up, SFM_down, MCF) per SOI type
    return sum(Su + Sd + Mcf for (Su, Sd, Mcf) in foms_over_types)
