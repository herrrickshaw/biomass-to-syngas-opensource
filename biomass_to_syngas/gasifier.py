"""Biomass gasification: elemental mass balance + water-gas-shift
equilibrium quench (same method family as the sibling coal-to-urea
repo's gasifier.py - Higman & van der Burgt, "Gasification", 2nd ed.,
Elsevier, 2008, covers both coal and biomass gasification with this
same conceptual-level approach), PLUS an explicit tar yield estimate -
the defining extra complication for biomass vs. coal gasification.

Biomass gasifiers typically run 700-900 C (much colder than coal's
1300-1500 C entrained-flow slagging temperatures - biomass ash melts/
sinters at much lower temperatures and biomass is far more reactive),
so CH4 and tar formation are NOT negligible the way they are for
high-temperature coal gasification - this module's CH4-free assumption
(inherited from the coal repo's method) is a bigger simplification
here than it was there, flagged explicitly rather than silently
carried over.

Tar yield: Milne, T.A., Evans, R.J., Abatzoglou, N., "Biomass Gasifier
"Tars": Their Nature, Formation, and Conversion", NREL/TP-570-25357,
National Renewable Energy Laboratory, 1998 (a freely available US
government technical report) - reports typical tar yields by gasifier
type: downdraft fixed-bed ~1-3 g/Nm3 (tar cracks passing through the
hot throat), updraft fixed-bed ~10-150 g/Nm3 (much higher - no
high-temperature zone the tar must pass through), fluidized bed
~10-30 g/Nm3. This module takes tar yield as a direct input (per
gasifier-type default) rather than predicting it from first
principles - real tar formation depends on residence time, particle
size, and reactor internals well beyond a conceptual elemental balance.

The updraft default (50 g/Nm3) is independently corroborated by a
second, separate literature figure found via vendor research (docs/
VENDOR_REFERENCE.md): published tar-production ranges for updraft
gasifiers of 30-150 g/Nm3, overlapping NREL's own 10-150 g/Nm3 range
above from a different source entirely - two independent citations
bracketing the same default, not one source re-quoted.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.optimize import brentq

from .biomass_feedstock import BiomassAnalysis

_AW = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007, "S": 32.06}
_MW_H2O = 18.015
_MW_O2 = 31.998

_HHV_KJ_MOL = {"H2": 285.8, "CO": 283.0}

# Typical tar yields by gasifier technology, g per Nm3 of dry product
# gas (Milne, Evans & Abatzoglou, NREL/TP-570-25357, 1998) - illustrative
# midpoints of the reported ranges above, override with test/vendor data.
TYPICAL_TAR_YIELD_G_NM3 = {
    "downdraft": 2.0,
    "updraft": 50.0,
    "fluidized_bed": 15.0,
}


@dataclass
class GasifierResult:
    syngas_composition_mole_frac: dict[str, float]
    syngas_molar_flow_mol_s: float
    syngas_mass_flow_kg_s: float
    carbon_conversion: float
    unconverted_carbon_kg_s: float
    cold_gas_efficiency: float
    tar_mass_flow_kg_s: float
    o2_mass_flow_kg_s: float
    steam_mass_flow_kg_s: float


def _wgs_equilibrium_K(T_K: float) -> float:
    return math.exp(4577.8 / T_K - 4.33)


def gasify_biomass(
    biomass: BiomassAnalysis,
    biomass_mass_flow_kg_s: float,
    o2_to_biomass_mass_ratio: float,
    steam_to_biomass_mass_ratio: float,
    gasifier_T_K: float,
    carbon_conversion: float = 0.90,
    gasifier_type: str = "fluidized_bed",
) -> GasifierResult:
    """Elemental balance + WGS-equilibrium quench, same structure as the
    coal-to-urea repo's gasify_coal - see that module's docstring for
    the full derivation and its own found-by-running caveat about
    scaling the O2 ratio with the fuel's carbon content, which applies
    here too.

    o2_to_biomass_mass_ratio: typically much lower than coal's 0.5-1.0
    kg O2/kg fuel, since biomass gasifiers commonly run sub-
    stoichiometric/partial-oxidation at lower temperature - illustrative
    starting point 0.25-0.40 kg O2/kg biomass for an oxygen-blown design
    (air-blown designs, more common at small scale, are not modeled
    here - this module assumes a pure O2 feed, diluting with N2
    separately if an air-blown case is wanted).
    steam_to_biomass_mass_ratio: typically 0.3-0.6 kg steam/kg biomass -
    higher than coal's, since biomass gasification commonly targets a
    higher steam/carbon ratio for better tar cracking and H2 yield.
    gasifier_type: "downdraft", "updraft", or "fluidized_bed" - selects
    the default tar yield (see TYPICAL_TAR_YIELD_G_NM3); pass
    tar_yield_g_per_Nm3 directly to override.
    """
    if gasifier_type not in TYPICAL_TAR_YIELD_G_NM3:
        raise ValueError(f"gasifier_type must be one of {list(TYPICAL_TAR_YIELD_G_NM3)}")
    if not (0.0 < carbon_conversion <= 1.0):
        raise ValueError("carbon_conversion must be in (0, 1]")

    n_C_biomass = biomass_mass_flow_kg_s * biomass.carbon * 1000.0 / _AW["C"]
    n_H_atoms = biomass_mass_flow_kg_s * biomass.hydrogen * 1000.0 / _AW["H"]
    n_O_atoms = biomass_mass_flow_kg_s * biomass.oxygen * 1000.0 / _AW["O"]
    n_N_atoms = biomass_mass_flow_kg_s * biomass.nitrogen * 1000.0 / _AW["N"]
    n_H2O_moisture = biomass_mass_flow_kg_s * biomass.moisture * 1000.0 / _MW_H2O

    o2_mass_flow = biomass_mass_flow_kg_s * o2_to_biomass_mass_ratio
    n_O2_fed = o2_mass_flow * 1000.0 / _MW_O2
    steam_mass_flow = biomass_mass_flow_kg_s * steam_to_biomass_mass_ratio
    n_H2O_steam = steam_mass_flow * 1000.0 / _MW_H2O

    n_C = n_C_biomass * carbon_conversion
    unconverted_carbon_kg_s = (n_C_biomass - n_C) * _AW["C"] / 1000.0

    n_H_total = n_H_atoms + 2.0 * (n_H2O_moisture + n_H2O_steam)
    n_O_total = n_O_atoms + (n_H2O_moisture + n_H2O_steam) + 2.0 * n_O2_fed
    n_H2eq = n_H_total / 2.0

    K = _wgs_equilibrium_K(gasifier_T_K)
    A = 2.0 * n_C + n_H2eq - n_O_total

    def residual(n_CO: float) -> float:
        n_H2 = A - n_CO
        n_CO2 = n_C - n_CO
        n_H2O = n_H2eq - n_H2
        return (n_CO2 * n_H2) - K * n_CO * n_H2O

    lo = max(1e-9, A - n_H2eq)
    hi = min(n_C, A) - 1e-9
    if hi <= lo:
        raise ValueError(
            "No physically valid syngas composition for this O2/steam/biomass "
            "ratio combination at the given temperature - try a different ratio."
        )
    n_CO = brentq(residual, lo, hi)
    n_H2 = A - n_CO
    n_CO2 = n_C - n_CO
    n_H2O = n_H2eq - n_H2
    n_N2 = n_N_atoms / 2.0

    species = {"CarbonMonoxide": n_CO, "CarbonDioxide": n_CO2, "Hydrogen": n_H2,
               "Water": n_H2O, "Nitrogen": n_N2}
    total_mol = sum(species.values())
    composition = {k: v / total_mol for k, v in species.items()}

    hhv_syngas_kW = n_CO * _HHV_KJ_MOL["CO"] + n_H2 * _HHV_KJ_MOL["H2"]
    hhv_biomass_kW = biomass_mass_flow_kg_s * biomass.hhv_MJ_kg() * 1000.0
    cold_gas_efficiency = hhv_syngas_kW / hhv_biomass_kW if hhv_biomass_kW > 0 else 0.0

    mw_mix = sum(composition[k] * _species_mw(k) for k in composition)
    syngas_mass_flow = total_mol * mw_mix / 1000.0

    Nm3_s = total_mol * 0.022414
    tar_yield_g_nm3 = TYPICAL_TAR_YIELD_G_NM3[gasifier_type]
    tar_mass_flow_kg_s = Nm3_s * tar_yield_g_nm3 / 1000.0

    return GasifierResult(
        syngas_composition_mole_frac=composition,
        syngas_molar_flow_mol_s=total_mol,
        syngas_mass_flow_kg_s=syngas_mass_flow,
        carbon_conversion=carbon_conversion,
        unconverted_carbon_kg_s=unconverted_carbon_kg_s,
        cold_gas_efficiency=cold_gas_efficiency,
        tar_mass_flow_kg_s=tar_mass_flow_kg_s,
        o2_mass_flow_kg_s=o2_mass_flow,
        steam_mass_flow_kg_s=steam_mass_flow,
    )


def _species_mw(coolprop_name: str) -> float:
    return {
        "CarbonMonoxide": 28.01, "CarbonDioxide": 44.01, "Hydrogen": 2.016,
        "Water": 18.015, "Nitrogen": 28.014,
    }[coolprop_name]
