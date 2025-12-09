from dataclasses import dataclass
import numpy as np
from physics.reflectometry import reflectivity, spin_sld
from physics.fom import sensitivity, sfm, mcf, tsf
from typing import Optional, Callable, List, Tuple, Dict, Any
from solvers.search_space import SearchSpace, ContinuousParam, CategoricalParam, IntegerParam



@dataclass
class Bounds:
    lo: float
    hi: float

@dataclass
class SOISpec: 
    name: str                    
    rho_n: float     
    thickness: float 
    sigma: float 

@dataclass
class CapSpec: 
    name: str 
    nom_thickness: float # NOT ACTUALLY USED IN THE PROBLEM ONLY FOR PLOTITNG 
    rho_n: float # nuclear SLD 
    sigma: float 

@dataclass 
class SubstrateSpec: 
    """ ALWAYS SI"""
    name: str
    rho_n: float # = check it later 
    sigma: float 

@dataclass 
class MRL: 
    """
    Ingredients for a CoTi MRL
    """
    rho_n_Co: float
    rho_n_Ti: float

    m_sld_from_x: Callable[[float], float] 
    # either a functions takes a float returns a float  
    # i think Anton said that it's basically scale with amount and 
    # mult with SLD for the mateiral 


    # Interface width between substrate and MRL & MRL and cap
    sigma_sub_mrl : float = 5.0
    sigma_mrl_cap: float = 5.0

@dataclass 
class Materials: 
    """ help class to construct the stacks"""
    substrate: SubstrateSpec
    caps: dict[str: CapSpec]
    mrl: MRL

class Base1OptimizationProblem:
    """
    Base1 problem [See base1 problem in report/main.tex for more information]:
    x = [x_co-ti, d_MRL,cap_material]

    TSF(x)
        s.t.
        # x_coti \in [0,1]
        
        d_MRL > 0 
        c \in {Al_2O_3, SiO_2, Au} (for example)
        d_cap > 0


    ----------------------------------------------
    Parameters: 
    materials: Materials 
        Substrate, Co/Ti data for MRL and avaible caps 
    soi_list: list[SOISpecs]
        we can create random numbers or just look at the most relevant reserach
    q_grid: np.ndarry
        just a interval 
    bounds_x: 
        bounds for example for x_coti between 0-1
    bounds_d: 
        for thickness 
    weights_fn: 
        a weight for Q, potentially to optimze for particular Q vals
    
    """ 
    def __init__(
                self, 
                 materials: Materials, 
                 soi_list: list[SOISpec], 
                 q_grid: np.ndarray, 
                 bounds_x: Bounds, 
                 bounds_d: Bounds, 
                 bounds_cap: Bounds,
                 weight_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
                ):
        
        self.materials = materials 
        self.soi_list = list(soi_list)
        self.Q = np.asarray(q_grid, dtype=float)
        self.bounds_x = bounds_x
        self.bounds_d = bounds_d
        self.bounds_cap = bounds_cap
        self.validate()
        self.weight_fn = weight_fn

    @property
    def cap_choices(self) -> list[str]: 
        return list(self.materials.caps.keys())

    @property
    def name(self) -> str:
        return "Base1"
    
    @property
    def search_space(self) -> SearchSpace:
        """
        Search space for Base1:

        - x_coti \in [bounds_x.lo, bounds_x.hi]
        - d_mrl \in [bounds_d.lo, bounds_d.hi]
        - cap \in available cap names (e.g. ["Al2O3", "SiO2", "Au"])
        """

        return SearchSpace(
            [
                ContinuousParam("x_coti", self.bounds_x.lo, self.bounds_x.hi),
                ContinuousParam("d_mrl", self.bounds_d.lo, self.bounds_d.hi),
                ContinuousParam("d_cap", self.bounds_cap.lo, self.bounds_cap.hi),
                CategoricalParam("cap", self.cap_choices),
            ]
            )
    
    def validate(self) -> None: 
        """ 
        Assert all constraints
        """
        assert self.Q.ndim == 1 and np.all(self.Q > 0), "Q must be 1d and positive."
        assert 0.0 <= self.bounds_x.lo < self.bounds_x.hi <= 1.0, "x bounds must be within [0,1]."
        assert self.bounds_d.hi > max(0.0, self.bounds_d.lo), "thickness bounds invalid."
        assert len(self.materials.caps) > 0, "No caps available."
        assert len(self.soi_list) > 0, "Provide at least one SOI."
        assert self.materials.mrl.m_sld_from_x is not None, "Provide MRL.m_sld_from_x(x)."
    
    
    def evaluate_objective(self,
                           x_coti: float,
                           d_mrl: float, 
                           d_cap: float,
                           cap: str,
                           objective: str = "TSF", 
                           return_breakdown: bool = False
                           ) -> float: 
        """ Returns TSF val as default """

        #in case cap dont exist: 
        if cap not in self.materials.caps: 
            raise ValueError(f"unknown cap mateiral")
        
        w = None if self.weight_fn is None else self.weight_fn(self.Q)

        triplets: List[Tuple[float, float, float]] = []  # (SFM_up, SFM_down, MCF)
        parts: List[Dict[str, Any]] = []                 # optional breakdown

        for soi in self.soi_list:
            # build stacks without and with SOI (spin up and down)
            layers_sub_up, layers_sub_down = self._layers(x_coti, d_mrl, d_cap, cap, soi=None)
            layers_full_up, layers_full_down = self._layers(x_coti, d_mrl, d_cap, cap, soi=soi)

            # reflectivities
            Rsub_up = self._reflect(self.Q, layers_sub_up)
            Rsub_dn = self._reflect(self.Q, layers_sub_down)
            Rfull_up = self._reflect(self.Q, layers_full_up)
            Rfull_dn = self._reflect(self.Q, layers_full_down)

            # sensitivities S(Q) and FOMs
            S_up = sensitivity(self.Q, Rsub_up, Rfull_up)
            S_dn = sensitivity(self.Q, Rsub_dn, Rfull_dn)
            SFM_up = sfm(self.Q, S_up, w=w)
            SFM_dn = sfm(self.Q, S_dn, w=w)
            MCF = mcf(self.Q, S_up, S_dn, w=w)

            triplets.append((SFM_up, SFM_dn, MCF))
            if return_breakdown:
                parts.append({
                    "soi": soi.name,
                    "SFM_up": float(SFM_up),
                    "SFM_down": float(SFM_dn),
                    "MCF": float(MCF)
                })

        value = float(tsf(triplets)) if objective.upper() == "TSF" else float(tsf(triplets))

        if return_breakdown:
            return {"value": value, "per_soi": parts}
        return value

    def analyze_single_soi(
        self,
        soi: SOISpec,
        x_coti: float,
        d_mrl: float,
        d_cap: float,
        cap: str,
        bkg: float = 0.0,
    ) -> Dict[str, Any]:
        if cap not in self.materials.caps:
            raise ValueError(f"unknown cap material {cap!r}")

        Q = self.Q
        w = None if self.weight_fn is None else self.weight_fn(Q)

        # substrate-only (no SOI)
        layers_sub_up, layers_sub_dn = self._layers(
            x_coti=x_coti, d_mrl=d_mrl, d_cap=d_cap, cap=cap, soi=None
        )
        # full (with SOI)
        layers_full_up, layers_full_dn = self._layers(
            x_coti=x_coti, d_mrl=d_mrl, d_cap=d_cap, cap=cap, soi=soi
        )

        Rsub_up  = self._reflect(Q, layers_sub_up,  bkg=bkg)
        Rsub_dn  = self._reflect(Q, layers_sub_dn,  bkg=bkg)
        Rfull_up = self._reflect(Q, layers_full_up, bkg=bkg)
        Rfull_dn = self._reflect(Q, layers_full_dn, bkg=bkg)

        S_up = sensitivity(Q, Rsub_up, Rfull_up)
        S_dn = sensitivity(Q, Rsub_dn, Rfull_dn)

        SFM_up = sfm(Q, S_up, w=w)
        SFM_dn = sfm(Q, S_dn, w=w)
        MCF    = mcf(Q, S_up, S_dn, w=w)

        return {
            "Q": Q,
            "Rsub_up":  Rsub_up,
            "Rsub_dn":  Rsub_dn,
            "Rfull_up": Rfull_up,
            "Rfull_dn": Rfull_dn,
            "S_up":     S_up,
            "S_dn":     S_dn,
            "SFM_up":   float(SFM_up),
            "SFM_dn":   float(SFM_dn),
            "MCF":      float(MCF),
        }

    # ----------------- stack builder part -------------------

    def _layers(
        self,
        x_coti: float,
        d_mrl: float,
        d_cap: float,
        cap: str,
        soi: Optional[SOISpec],
    ) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
        """
        Build spin up and down stacks.

        We store layer dicts as:
            {'rho', 'thickness', 'sigma'}
        which is exactly what physics.reflectometry expects.
        """
        sub = self.materials.substrate
        cap_spec = self.materials.caps[cap]
        mrl = self.materials.mrl

        # nuclear SLD of alloy; magnetic SLD from user function
        rho_n_mrl = x_coti * mrl.rho_n_Co + (1.0 - x_coti) * mrl.rho_n_Ti
        rho_m_mrl = float(mrl.m_sld_from_x(x_coti))
        rho_up_mrl = rho_n_mrl + rho_m_mrl
        rho_dn_mrl = rho_n_mrl - rho_m_mrl

        def L(rho, thickness, sigma) -> Dict[str, float]:
            return {
                "rho": float(rho),
                "thickness": float(thickness),
                "sigma": float(sigma),
            }

        up_stack: List[Dict[str, float]] = []
        dn_stack: List[Dict[str, float]] = []

        # optional SOI on top
        if soi is not None:
            up_stack.append(L(soi.rho_n, soi.thickness, soi.sigma))
            dn_stack.append(L(soi.rho_n, soi.thickness, soi.sigma))

        # cap (non-magnetic)
        up_stack.append(L(cap_spec.rho_n, d_cap, cap_spec.sigma))
        dn_stack.append(L(cap_spec.rho_n, d_cap, cap_spec.sigma))

        # MRL (spin split)
        up_stack.append(L(rho_up_mrl, d_mrl, mrl.sigma_mrl_cap))
        dn_stack.append(L(rho_dn_mrl, d_mrl, mrl.sigma_mrl_cap))

        # substrate (semi-infinite: thickness=0)
        up_stack.append(L(sub.rho_n, 0.0, mrl.sigma_sub_mrl))
        dn_stack.append(L(sub.rho_n, 0.0, mrl.sigma_sub_mrl))

        return up_stack, dn_stack

        
    
    def _reflect(
        self,
        Q: np.ndarray,
        layers: List[Dict[str, float]],
        bkg: float = 0.0,
    ) -> np.ndarray:
        # layers already have 'rho', 'thickness', 'sigma'
        return reflectivity(Q, layers, bkg=bkg)
