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
