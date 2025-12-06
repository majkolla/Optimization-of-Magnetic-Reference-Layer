"""
Helper for loading material specifcation from the json file into the 
Base1 mateirals dataclasses. 
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

# Prevent import errors for now, look into better solutions later
PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from problems.base1 import SubstrateSpec, CapSpec, MRL, Materials
DATA_DIR = Path(__file__).resolve().parent


def _resolve_data_path(filename: str) -> Path:
    """
    Resolve a data file path by trying a few sensible locations.
    - exact path as provided (relative to CWD if not absolute)
    - inside this module's data directory (supports callers in notebooks)
    - inside the data directory using only the basename (handles "data/data.json")
    """
    raw_path = Path(filename)
    candidates = [
        raw_path,
        DATA_DIR / raw_path,
        DATA_DIR / raw_path.name,
    ]
    tried: list[str] = []
    for candidate in candidates:
        tried.append(str(candidate))
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"Could not find '{filename}'. Tried: {tried}")

def load_base1_materials(
        filename: str, 
        m_sld_from_x: Callable[[float], float] | None, 
        ) -> Materials: 
    """
    Here we load base1 mateirals instance from a json file in the data folder 

    filename: str 
    """  
    path = _resolve_data_path(filename)
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

if __name__ == "__main__":
    def m_sld_from_x(x: float) -> float:
        return 1.0 * x  # placeholder linear scaling

    materials = load_base1_materials("data.json", m_sld_from_x=m_sld_from_x)
    print(materials)
