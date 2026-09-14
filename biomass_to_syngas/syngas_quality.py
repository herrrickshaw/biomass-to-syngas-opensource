"""Syngas quality metrics and downstream-use screening.

H2:CO molar ratio is the single most important syngas quality metric
for choosing a downstream route: Fischer-Tropsch and methanol synthesis
both want H2:CO close to 2:1 (the stoichiometric ratio their own
synthesis reactions consume - see the companion `sustainable-aviation-
fuel-opensource` repo's Fischer-Tropsch module for where this leads),
while gas engines/turbines for direct power generation are far more
tolerant of ratio and of N2 dilution (relevant for air-blown
gasification, not the pure-O2 case this repo's gasifier.py models).
This screening logic mirrors the structure of the sibling LNG project's
process_selection.py (a coarse, citation-grounded heuristic, not a
techno-economic optimization).
"""
from __future__ import annotations

from dataclasses import dataclass

_HHV_KJ_MOL = {"CarbonMonoxide": 283.0, "Hydrogen": 285.8}
_LHV_KJ_MOL = {"CarbonMonoxide": 283.0, "Hydrogen": 241.8}  # CO's LHV=HHV (no H2O product)


@dataclass
class SyngasQualityResult:
    h2_to_co_molar_ratio: float
    lhv_MJ_per_Nm3: float
    inert_mole_fraction: float
    recommended_use: str
    rationale: str


def evaluate_syngas_quality(composition_mole_frac: dict[str, float]) -> SyngasQualityResult:
    """composition_mole_frac must include at least "Hydrogen" and
    "CarbonMonoxide" keys; "Nitrogen"/"CarbonDioxide"/"Water" are
    treated as inerts for the LHV and dilution calculations if present.
    """
    h2 = composition_mole_frac.get("Hydrogen", 0.0)
    co = composition_mole_frac.get("CarbonMonoxide", 0.0)
    if co <= 0:
        raise ValueError("CarbonMonoxide mole fraction must be positive to evaluate H2:CO ratio")
    h2_to_co = h2 / co

    lhv_kJ_mol = sum(composition_mole_frac.get(name, 0.0) * _LHV_KJ_MOL[name] for name in _LHV_KJ_MOL)
    lhv_MJ_Nm3 = lhv_kJ_mol / 0.022414 / 1000.0  # kJ/mol -> kJ/Nm3 -> MJ/Nm3

    inert_names = {"Nitrogen", "CarbonDioxide", "Water", "HydrogenSulfide"}
    inert_frac = sum(v for k, v in composition_mole_frac.items() if k in inert_names)

    if inert_frac > 0.50:
        recommended = "Direct combustion / gas engine power generation only"
        rationale = (
            f"Inert (N2/CO2/H2O) content {inert_frac*100:.0f}% is too high for chemical "
            "synthesis feed quality - typical of air-blown or heavily steam-diluted gasification. "
            "Power generation via gas engine/turbine is far more tolerant of dilution."
        )
    elif 1.7 <= h2_to_co <= 2.3:
        recommended = "Fischer-Tropsch / methanol synthesis feed"
        rationale = (
            f"H2:CO ratio {h2_to_co:.2f}:1 sits close to the 2:1 stoichiometric ratio both "
            "Fischer-Tropsch and methanol synthesis consume - a good match without a large "
            "additional water-gas-shift adjustment step."
        )
    elif h2_to_co < 1.7:
        recommended = "Water-gas-shift adjustment needed before FT/methanol synthesis"
        rationale = (
            f"H2:CO ratio {h2_to_co:.2f}:1 is CO-rich relative to the 2:1 target - a WGS stage "
            "(see the sibling coal-to-urea repo's shift_reactor.py, directly reusable here) "
            "would need to convert some CO to H2 first."
        )
    else:
        recommended = "H2-rich - suitable for hydrogen recovery or ammonia-style synthesis"
        rationale = (
            f"H2:CO ratio {h2_to_co:.2f}:1 is H2-rich relative to FT/methanol's 2:1 target - "
            "consider PSA hydrogen recovery, or routing toward an ammonia-style synthesis loop "
            "(see the sibling coal-to-urea repo) instead of FT/methanol."
        )

    return SyngasQualityResult(
        h2_to_co_molar_ratio=h2_to_co,
        lhv_MJ_per_Nm3=lhv_MJ_Nm3,
        inert_mole_fraction=inert_frac,
        recommended_use=recommended,
        rationale=rationale,
    )
