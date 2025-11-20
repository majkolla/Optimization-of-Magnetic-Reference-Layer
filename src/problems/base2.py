from dataclasses import dataclass
import numpy as np
from ..physics.reflectometry import reflectivity, spin_sld
from ..physics.fom import sensitivity, sfm, mcf, tsf


@dataclass
class Bounds:
    lo: float
    hi: float



class Base2OptimizationProblem:
    """
    Base2 problem [See base2 problem in report/main.tex for more information]:
    x = [x_Co, d_MRL, sigma_MRL/sub, sigma_MRL/cap, d_cap,
        sigma_cap/SOI, cap_material_id, B, lambda, bkg]
    """
    def __init__(self, materials, soi_scenarios, q_grid, bounds, weights): #add functionality for weights later
        """
        materials: represented in a multilevel disctionary,     
        with nuclear SLDs and magnetic model hooks. 
    
        
        Consider materials['MRL'] has a callable rho_n(x_Co), rho_m(x_Co, B).

        soi_scenarios: list of dicts, where each {'rho_n':..., 'd':..., 'sigma_SOI':...}
        q_grid: np.array of Q
        bounds: dict name->Bounds

        May implement a weight dict to optimize a weighted sum instead. 
        """
        self.materials = materials
        self.T = soi_scenarios          
        self.Q = q_grid
        self.bounds = bounds
        
        # self.weights = weights (currently not implemented)



    def _layers(self, x, soi_rho_n, soi_d, spin):
        # unpack decision vector
        
        xCo, dMRL, sig_MS, sig_MC, dcap, sig_CS, cap_id, B, lam, bkg = x
        # ambient
        
        layers = [{'rho': self.materials['Air']['rho_n'], 'd': 0.0}]
        
        
        # MRL 
        rn = self.materials['MRL']['rho_n'](xCo)
        rm = self.materials['MRL']['rho_m'](xCo, B)
        layers.append({'rho': spin_sld(rn, rm, spin), 'd': dMRL})
        
        
        # cap
        cap_mat = self.materials['Cap'][int(cap_id)]
        layers.append({'rho': cap_mat['rho_n'], 'd': dcap})
        
        # SOI
        layers.append({'rho': soi_rho_n, 'd': soi_d})
        
        # substrate
        layers.append({'rho': self.materials['Sub']['rho_n'], 'd': 0.0})
        
        
        # interface roughness sequence: Air|MRL, MRL|Cap, Cap|SOI, SOI|Sub
        sig_SOI_sub = self.materials['SOI']['sigma_SOI_sub']
        sigmas = [sig_MS, sig_MC, sig_CS, sig_SOI_sub]
        return layers, sigmas, bkg

    
    def evaluate_objectives(self, x):
        """Returns a dict with SFM_up, SFM_down, MCF, TSF"""
        
        foms = []
        for t in self.T:
            
            Lu, Su, bkg = self._layers(x, t['rho_n'], t['d'], 'up')
            Ld, Sd, _ = self._layers(x, t['rho_n'], t['d'], 'down')
            R_up_full = reflectivity(self.Q, Lu, Su, bkg=bkg)
            R_down_full = reflectivity(self.Q, Ld, Sd, bkg=bkg)
            
            # references (without SOI layer)
            Lu_ref = [Lu[i] for i in [0,1,2,4]]; Su_ref = [Su[i] for i in [0,1,3]]
            Ld_ref = [Ld[i] for i in [0,1,2,4]]; Sd_ref = [Sd[i] for i in [0,1,3]]
            R_up_ref = reflectivity(self.Q, Lu_ref, Su_ref, bkg=bkg)
            R_down_ref = reflectivity(self.Q, Ld_ref, Sd_ref, bkg=bkg)
            
            # compute sensitivities & FOMs
            S_up = sensitivity(self.Q, R_up_ref, R_up_full)
            S_dn = sensitivity(self.Q, R_down_ref, R_down_full)
            foms.append((
                sfm(self.Q, S_up),
                sfm(self.Q, S_dn),
                mcf(self.Q, S_up, S_dn),
            ))


        return {
            'SFM_up': sum(x[0] for x in foms),
            'SFM_down': sum(x[1] for x in foms),
            'MCF': sum(x[2] for x in foms),
            'TSF': tsf(foms),
            }

    def constraints(self, x):
        """
        Return dict of bound violations
        May further expand this as I learn about the physics. 
        """
        viol = {}
        names = ['xCo','dMRL','sig_MS','sig_MC','dcap','sig_CS','cap_id','B','lam','bkg']
        for name, val in zip(names, x):
            b = self.bounds[name]
            viol[name] = max(b.lo - val, 0.0) + max(val - b.hi, 0.0)
        return viol
