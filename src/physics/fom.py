import numpy as np

def sensitivity(Q, R_sub, R_full):
    return (R_full - R_sub) / (R_sub + R_full)

def sfm(Q, S, w=None):
    y = np.abs(S) if w is None else np.abs(S) * w 
    return np.trapezoid(y, Q) 

def mcf(Q, S_up, S_down, w=None):
    y = np.abs(S_up - S_down) if w is None else np.abs(S_up - S_down) * w
    return np.trapezoid(y, Q)

def tsf(foms_over_types):
    # foms_over_types: iterable of (SFM_up, SFM_down, MCF) per SOI type
    # from matlab but we may change them 0.5 * |Area_up - Area_down| + 0.5 * MCF
    return sum(0.5 * abs(Su - Sd) + 0.5 * Mcf for (Su, Sd, Mcf) in foms_over_types)
