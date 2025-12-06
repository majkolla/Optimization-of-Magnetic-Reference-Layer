"""
Helper for loading material specifcation from the json file into the 
Base1 mateirals dataclasses. 
"""

import json 
from pathlib import Path 
from typing import Any, Callable, Dict 

from problems.base1 import SubstrateSpec, CapSpec, MRL, Materials
DATA_DIR = Path(__file__).resolve().parent

def load_base1_materials(
        filename: str, 
        m_sld_from_x: Callable[[float], float] | None, 
        ) -> Materials: 
    """
    Here we load base1 mateirals instance from a json file in the data folder 

    filename: str 
    """  
    path = DATA_DIR / filename 
    with path.open("r", encoding="utf-8") as f: 
        data: Dict[str, Any] = json.load(f)

    # Substate 
    sub = data["substrate"]
    substrate = SubstrateSpec(
        name = str(sub["name"]), 
        rho_n=float(sub["rho_n"]), 
        sigma=float(sub["sigma"]),
    )
    # ---- caps ---
    caps_dict: Dict[str, CapSpec] = {}
    for name, cap in data["caps"].items():
        caps_dict[name] = CapSpec(
            name=name,
            rho_n=float(cap["rho_n"]),
            nom_thickness=float(cap["thickness"]),
            sigma=float(cap["sigma"]),
        )

    # ----- MRL -----
    mrl_data = data["mrl"]
    mrl = MRL(
        rho_n_Co=float(mrl_data["rho_n_Co"]),
        rho_n_Ti=float(mrl_data["rho_n_Ti"]),
        m_sld_from_x=m_sld_from_x,
        sigma_sub_mrl=float(mrl_data.get("sigma_sub_mrl", 5.0)),
        sigma_mrl_cap=float(mrl_data.get("sigma_mrl_cap", 5.0)),
    )
    return Materials(substrate=substrate, caps=caps_dict, mrl=mrl)
