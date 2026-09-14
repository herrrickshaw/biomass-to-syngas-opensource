"""End-to-end worked example: rice/paddy straw -> syngas -> cleanup ->
quality screening, chaining every module in this repo on one basis.

Real-world motivation: India's Ministry of New and Renewable Energy
estimates ~230 million tonnes/year of agricultural biomass goes
unutilized nationally, and a well-documented consequence - especially
where storage is limited, as in northern India - is open-field stubble
burning, a major seasonal air-quality crisis (Datta, A.K. et al.,
"Indian Scenario of Biomass Availability and its Bioenergy Conversion",
Plant Archives 25, Special Issue, 2025 - see docs/VALIDATION.md).
Gasification is a genuine, often-proposed alternative use for this
surplus. This example sizes a representative district-scale plant and
asks: what fraction of India's surplus biomass would a fleet of such
plants need to process to make a dent in the stubble-burning problem?

Run: python examples/full_chain_worked_example.py
"""
from __future__ import annotations

from biomass_to_syngas.biomass_feedstock import TYPICAL_RICE_STRAW
from biomass_to_syngas.gas_cleanup import clean_syngas
from biomass_to_syngas.gasifier import gasify_biomass
from biomass_to_syngas.syngas_quality import evaluate_syngas_quality

SECONDS_PER_YEAR = 365.25 * 24 * 3600
INDIA_SURPLUS_BIOMASS_MTPA = 230.0  # Datta et al. 2025 - see docs/VALIDATION.md

# A representative district-scale plant: 100 tonnes/day rice straw -
# a realistic scale for a distributed biomass gasification project
# (well within the range of real reported small-to-medium biomass
# gasification plants).
STRAW_FEED_TPD = 100.0
STRAW_FEED_KG_S = STRAW_FEED_TPD * 1000.0 / (24 * 3600)

print("=" * 78)
print("BIOMASS-TO-SYNGAS FULL CHAIN WORKED EXAMPLE")
print("=" * 78)
print(f"Feed: rice/paddy straw, {STRAW_FEED_TPD:.0f} t/day ({STRAW_FEED_KG_S:.3f} kg/s), "
      f"HHV {TYPICAL_RICE_STRAW.hhv_MJ_kg():.1f} MJ/kg")

# ---------------------------------------------------------------------
# Gasifier - fluidized bed, oxygen-blown
# ---------------------------------------------------------------------
g = gasify_biomass(
    TYPICAL_RICE_STRAW, STRAW_FEED_KG_S,
    o2_to_biomass_mass_ratio=0.22, steam_to_biomass_mass_ratio=0.40,
    gasifier_T_K=1123.15, carbon_conversion=0.85, gasifier_type="fluidized_bed",
)
print(f"\nGasifier (850 C, fluidized bed): {g.syngas_molar_flow_mol_s:.2f} mol/s syngas, "
      f"CGE {g.cold_gas_efficiency*100:.1f}%, tar yield {g.tar_mass_flow_kg_s*1000:.2f} g/s")
print("  Composition:", {k: f"{v*100:.1f}%" for k, v in g.syngas_composition_mole_frac.items()})

# ---------------------------------------------------------------------
# Gas cleanup
# ---------------------------------------------------------------------
particulate_estimate_kg_s = g.syngas_mass_flow_kg_s * 0.02  # illustrative loading, not predicted by gasifier.py
cleanup = clean_syngas(g.tar_mass_flow_kg_s, particulate_estimate_kg_s,
                         tar_removal_fraction=0.97, particulate_removal_fraction=0.98)
print(f"\nGas cleanup: tar reduced to {cleanup.cleaned_tar_mass_flow_kg_s*1000:.3f} g/s "
      f"(from {g.tar_mass_flow_kg_s*1000:.2f} g/s), "
      f"particulate reduced to {cleanup.cleaned_particulate_mass_flow_kg_s*1000:.2f} g/s")

# ---------------------------------------------------------------------
# Syngas quality screening
# ---------------------------------------------------------------------
quality = evaluate_syngas_quality(g.syngas_composition_mole_frac)
print(f"\nSyngas quality: H2:CO = {quality.h2_to_co_molar_ratio:.2f}:1, "
      f"LHV = {quality.lhv_MJ_per_Nm3:.2f} MJ/Nm3, inert fraction {quality.inert_mole_fraction*100:.1f}%")
print(f"  Recommended use: {quality.recommended_use}")
print(f"  {quality.rationale}")

# ---------------------------------------------------------------------
# Scale-up context: this repo's real motivation
# ---------------------------------------------------------------------
n_plants_for_full_surplus = (INDIA_SURPLUS_BIOMASS_MTPA * 1.0e9) / (STRAW_FEED_KG_S * SECONDS_PER_YEAR)
print("\n" + "=" * 78)
print("Scale-up context")
print("=" * 78)
print(f"  A single {STRAW_FEED_TPD:.0f} t/day plant processes "
      f"{STRAW_FEED_KG_S*SECONDS_PER_YEAR/1.0e9:.4f} million tonnes/year "
      f"({STRAW_FEED_KG_S*SECONDS_PER_YEAR/1.0e3:,.0f} tonnes/year).")
print(f"  Processing India's ENTIRE estimated {INDIA_SURPLUS_BIOMASS_MTPA:.0f} Mt/year surplus "
      f"biomass this way would need ~{n_plants_for_full_surplus:,.0f} plants of this scale - "
      "illustrating the scale of the opportunity (and the logistics challenge: collection, "
      "storage and transport, which the Datta et al. 2025 source flags as the primary real-world "
      "barrier, not the gasification technology itself). Not a proposal that a single "
      "technology choice or plant count is optimal - a scale sanity check, nothing more.")
print(
    "\nNote: this is a conceptual, module-chained estimate (fixed conversions, an illustrative "
    "tar-yield lookup, no rate-based cleanup equipment sizing) - useful for screening, not a "
    "substitute for a site-specific feasibility study. See docs/VALIDATION.md."
)
