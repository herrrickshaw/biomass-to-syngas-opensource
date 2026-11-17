import pytest

from biomass_to_syngas.biomass_feedstock import TYPICAL_RICE_STRAW, TYPICAL_WOOD_CHIPS
from biomass_to_syngas.gasifier import gasify_biomass


def test_gasify_biomass_mass_and_mole_balance_closes():
    result = gasify_biomass(TYPICAL_RICE_STRAW, 10.0, 0.22, 0.40, 1123.15,
                              carbon_conversion=0.85, gasifier_type="fluidized_bed")
    total_frac = sum(result.syngas_composition_mole_frac.values())
    assert total_frac == pytest.approx(1.0, abs=1e-9)
    for frac in result.syngas_composition_mole_frac.values():
        assert frac >= 0.0
    assert result.syngas_molar_flow_mol_s > 0


def test_gasify_biomass_cold_gas_efficiency_in_published_range():
    # Commonly reported biomass gasification CGE range, e.g. Gao et al.
    # (2023), ACS Omega 8(35) - roughly 60-85% depending on design.
    result = gasify_biomass(TYPICAL_RICE_STRAW, 10.0, 0.22, 0.40, 1123.15,
                              carbon_conversion=0.85, gasifier_type="fluidized_bed")
    assert 0.55 < result.cold_gas_efficiency < 0.90


def test_gasify_biomass_rejects_unknown_gasifier_type():
    with pytest.raises(ValueError, match="gasifier_type"):
        gasify_biomass(TYPICAL_WOOD_CHIPS, 10.0, 0.25, 0.40, 1123.15, gasifier_type="rotary_kiln")


def test_gasify_biomass_tar_yield_matches_gasifier_type_ordering():
    # Updraft produces far more tar than downdraft (no hot throat the
    # tar must crack through) - a basic ordering check on the module's
    # gasifier-type tar yield table.
    down = gasify_biomass(TYPICAL_WOOD_CHIPS, 10.0, 0.25, 0.40, 1123.15, gasifier_type="downdraft")
    up = gasify_biomass(TYPICAL_WOOD_CHIPS, 10.0, 0.25, 0.40, 1123.15, gasifier_type="updraft")
    assert up.tar_mass_flow_kg_s > down.tar_mass_flow_kg_s


def test_gasify_biomass_rejects_invalid_carbon_conversion():
    with pytest.raises(ValueError, match="carbon_conversion"):
        gasify_biomass(TYPICAL_WOOD_CHIPS, 10.0, 0.25, 0.40, 1123.15, carbon_conversion=1.2)


def test_gasify_biomass_higher_o2_ratio_lowers_cold_gas_efficiency():
    # More O2 per unit biomass pushes toward complete combustion
    # (more CO2/H2O, less CO/H2 heating value retained).
    low_o2 = gasify_biomass(TYPICAL_RICE_STRAW, 10.0, 0.15, 0.40, 1123.15, carbon_conversion=0.85)
    high_o2 = gasify_biomass(TYPICAL_RICE_STRAW, 10.0, 0.30, 0.40, 1123.15, carbon_conversion=0.85)
    assert high_o2.cold_gas_efficiency < low_o2.cold_gas_efficiency


# --- Element balances and equilibrium, from first principles (not from the module).
import math  # noqa: E402

_AW = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007}
_CASE = dict(biomass_mass_flow_kg_s=10.0, o2_to_biomass_mass_ratio=0.30,
             steam_to_biomass_mass_ratio=0.40, gasifier_T_K=1123.15, carbon_conversion=0.90)


def _species_mol(r):
    return {k: v * r.syngas_molar_flow_mol_s for k, v in r.syngas_composition_mole_frac.items()}


def test_carbon_hydrogen_oxygen_atoms_are_conserved():
    b, m = TYPICAL_WOOD_CHIPS, 10.0
    r = gasify_biomass(b, **_CASE, gasifier_type="fluidized_bed")
    n = _species_mol(r)
    h2o_in = m * b.moisture * 1000 / 18.015 + m * 0.40 * 1000 / 18.015
    c_in = m * b.carbon * 1000 / _AW["C"] * 0.90
    h_in = m * b.hydrogen * 1000 / _AW["H"] + 2 * h2o_in
    o_in = m * b.oxygen * 1000 / _AW["O"] + h2o_in + 2 * (m * 0.30 * 1000 / 31.998)
    assert n["CarbonMonoxide"] + n["CarbonDioxide"] == pytest.approx(c_in, rel=1e-9)
    assert 2 * n["Hydrogen"] + 2 * n["Water"] == pytest.approx(h_in, rel=1e-9)
    assert n["CarbonMonoxide"] + 2 * n["CarbonDioxide"] + n["Water"] == pytest.approx(o_in, rel=1e-9)
    assert r.unconverted_carbon_kg_s == pytest.approx(m * b.carbon * 0.10, rel=1e-9)


def test_outlet_satisfies_water_gas_shift_equilibrium_moe_1962():
    r = gasify_biomass(TYPICAL_WOOD_CHIPS, **_CASE, gasifier_type="fluidized_bed")
    y = r.syngas_composition_mole_frac
    K = math.exp(4577.8 / 1123.15 - 4.33)          # exp(4.07586 - 4.33) = 0.7756 at 850 C
    assert K == pytest.approx(0.7756, abs=1e-4)
    assert y["CarbonDioxide"] * y["Hydrogen"] / (y["CarbonMonoxide"] * y["Water"]) == pytest.approx(K, rel=1e-6)


def test_tar_yield_is_per_dry_nm3():
    """Milne et al. tar yields are g per Nm3 of DRY product gas; the water in
    the raw syngas must not inflate the tar flow (prove-it)."""
    r = gasify_biomass(TYPICAL_WOOD_CHIPS, **_CASE, gasifier_type="fluidized_bed")
    dry_mol = r.syngas_molar_flow_mol_s * (1 - r.syngas_composition_mole_frac["Water"])
    assert r.tar_mass_flow_kg_s == pytest.approx(dry_mol * 0.022414 * 15.0 / 1000.0, rel=1e-9)


def test_tar_yield_override_documented_in_docstring_is_accepted():
    r = gasify_biomass(TYPICAL_WOOD_CHIPS, **_CASE, gasifier_type="downdraft", tar_yield_g_per_Nm3=0.5)
    dry_mol = r.syngas_molar_flow_mol_s * (1 - r.syngas_composition_mole_frac["Water"])
    assert r.tar_mass_flow_kg_s == pytest.approx(dry_mol * 0.022414 * 0.5 / 1000.0, rel=1e-9)


def test_no_physical_solution_raises():
    # Far too much O2: everything burns to CO2/H2O, no CO root to bracket
    with pytest.raises(ValueError):
        gasify_biomass(TYPICAL_WOOD_CHIPS, 10.0, 3.0, 0.4, 1123.15)
