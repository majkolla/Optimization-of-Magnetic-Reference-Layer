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

from problems.interfaces import OptimizationProblemProtocol

class Base1OptimizationProblem(OptimizationProblemProtocol):
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
    SLD_SCALE = 1e-6  # convert (10^-6 Å^-2) -> (Å^-2)
    def __init__(
                self, 
                 materials: Materials, 
                 soi_list: list[SOISpec], 
                 q_grid: np.ndarray, 
                 bounds_x: Bounds, 
                 bounds_d: Bounds, 
                 bounds_cap: Bounds,
                 weight_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
                 SLD_SCALE = 1e-6
                ):
        
        self.materials = materials 
        self.soi_list = list(soi_list)
        self.Q = np.asarray(q_grid, dtype=float)
        self.bounds_x = bounds_x
        self.bounds_d = bounds_d
        self.bounds_cap = bounds_cap
        self.validate()
        self.weight_fn = weight_fn
        self.sld_scale = float(SLD_SCALE) # convert 10^-6 Å^-2 -> Å

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
            layers_sub_up, layers_sub_down = self._layers(
                        x_coti=x_coti, d_mrl=d_mrl, d_cap=d_cap, cap=cap, soi=None
                        )
            layers_full_up, layers_full_down = self._layers(
                        x_coti=x_coti, d_mrl=d_mrl, d_cap=d_cap, cap=cap, soi=soi
                        )

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
    def _rho(self, rho_in_1e6: float) -> float:
        """Convert SLD given in 10^-6 Å^-2 into Å^-2 (what Parratt expects)."""
        return float(rho_in_1e6) * self.SLD_SCALE

    def _air(self) -> Dict[str, float]:
        return {"rho": 0.0, "thickness": 0.0, "sigma": 0.0}

    def _maybe_add_cap(
        self,
        up_stack: List[Dict[str, float]],
        dn_stack: List[Dict[str, float]],
        cap: str,
        d_cap: float,
    ) -> None:
        if cap == "none" or d_cap <= 0.0:
            return

        cap_spec = self.materials.caps[cap]

        # sigma on the cap layer => roughness at (cap | next layer below) = (cap | MRL)
        up_stack.append({
            "rho": self._rho(cap_spec.rho_n),
            "thickness": float(d_cap),
            "sigma": float(cap_spec.sigma),
        })
        dn_stack.append({
            "rho": self._rho(cap_spec.rho_n),
            "thickness": float(d_cap),
            "sigma": float(cap_spec.sigma),
        })

    def layers_no_mrl(self, soi: Optional[SOISpec]) -> List[Dict[str, float]]:
        sub = self.materials.substrate
        stack: List[Dict[str, float]] = [self._air()]
        if soi is not None:
            stack.append({
                "rho": self._rho(soi.rho_n),
                "thickness": float(soi.thickness),
                "sigma": float(soi.sigma),  # (SOI | substrate) here
            })
        stack.append({
            "rho": self._rho(sub.rho_n),
            "thickness": 0.0,
            "sigma": 0.0,  # substrate sigma is not used by your Parratt loop anyway
        })
        return stack

    def layers_with_mrl(
        self,
        x_coti: float,
        d_mrl: float,
        d_cap: float,
        cap: str,
        soi: Optional[SOISpec] = None,
    ) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:

        sub = self.materials.substrate
        mrl = self.materials.mrl

        # --- build MRL SLDs (inputs are in 10^-6 Å^-2, convert with _rho) ---
        rho_n_mrl_1e6 = x_coti * mrl.rho_n_Co + (1.0 - x_coti) * mrl.rho_n_Ti
        rho_m_mrl_1e6 = float(mrl.m_sld_from_x(x_coti))  # must be in same 10^-6 units

        rho_n_mrl = self._rho(rho_n_mrl_1e6)
        rho_m_mrl = self._rho(rho_m_mrl_1e6)

        rho_up_mrl = rho_n_mrl + rho_m_mrl
        rho_dn_mrl = rho_n_mrl - rho_m_mrl

        up_stack: List[Dict[str, float]] = [self._air()]
        dn_stack: List[Dict[str, float]] = [self._air()]

        if soi is not None:
            # sigma on SOI => roughness at (SOI | next layer below) = (SOI | cap) or (SOI | MRL)
            up_stack.append({
                "rho": self._rho(soi.rho_n),
                "thickness": float(soi.thickness),
                "sigma": float(soi.sigma),
            })
            dn_stack.append({
                "rho": self._rho(soi.rho_n),
                "thickness": float(soi.thickness),
                "sigma": float(soi.sigma),
            })

        self._maybe_add_cap(up_stack, dn_stack, cap=cap, d_cap=d_cap)

        # MRL: sigma on MRL => roughness at (MRL | substrate)
        up_stack.append({
            "rho": float(rho_up_mrl),
            "thickness": float(d_mrl),
            "sigma": float(mrl.sigma_sub_mrl),
        })
        dn_stack.append({
            "rho": float(rho_dn_mrl),
            "thickness": float(d_mrl),
            "sigma": float(mrl.sigma_sub_mrl),
        })

        # substrate (semi-infinite)
        up_stack.append({
            "rho": self._rho(sub.rho_n),
            "thickness": 0.0,
            "sigma": 0.0,
        })
        dn_stack.append({
            "rho": self._rho(sub.rho_n),
            "thickness": 0.0,
            "sigma": 0.0,
        })

        return up_stack, dn_stack

    def _layers(
        self,
        x_coti: float,
        d_mrl: float,
        d_cap: float,
        cap: str,
        soi: Optional[SOISpec] = None,
    ) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
        # optional safety clip (doesn't hurt optimization)
        x_coti = float(np.clip(x_coti, self.bounds_x.lo, self.bounds_x.hi))
        d_mrl  = float(np.clip(d_mrl,  self.bounds_d.lo, self.bounds_d.hi))
        d_cap  = float(np.clip(d_cap,  self.bounds_cap.lo, self.bounds_cap.hi))
        return self.layers_with_mrl(x_coti, d_mrl, d_cap, cap, soi=soi)

    def _reflect(self, Q, layers, bkg: float = 1e-3) -> np.ndarray:
        return reflectivity(Q, layers, bkg=bkg)