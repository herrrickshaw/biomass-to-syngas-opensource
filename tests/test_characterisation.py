"""Characterisation tests: pin the exact numeric outputs of every sizing
module on its documented example inputs, captured from the pre-refactor
code (2026-11). Any change here is a behaviour change and must be
deliberate."""
from __future__ import annotations

import pytest

from biomass_to_syngas.biomass_feedstock import TYPICAL_RICE_STRAW, TYPICAL_WOOD_CHIPS
from biomass_to_syngas.gas_cleanup import clean_syngas
from biomass_to_syngas.gasifier import gasify_biomass
from biomass_to_syngas.syngas_quality import evaluate_syngas_quality

REL = 1e-9


def test_feedstock_presets_heating_values():
    assert TYPICAL_RICE_STRAW.hhv_MJ_kg() == pytest.approx(14.13912, rel=REL)
    assert TYPICAL_RICE_STRAW.lhv_MJ_kg() == pytest.approx(12.9259344, rel=REL)
    assert TYPICAL_WOOD_CHIPS.hhv_MJ_kg() == pytest.approx(19.45556, rel=REL)
    assert TYPICAL_WOOD_CHIPS.lhv_MJ_kg() == pytest.approx(18.09741728, rel=REL)


def test_gasifier_rice_straw_fluidized_bed_reference_case():
    g = gasify_biomass(TYPICAL_RICE_STRAW, 10.0, 0.22, 0.40, 1123.15,
                       carbon_conversion=0.85, gasifier_type="fluidized_bed")
    comp = g.syngas_composition_mole_frac
    assert comp["CarbonMonoxide"] == pytest.approx(0.18276657256707182, rel=REL)
    assert comp["CarbonDioxide"] == pytest.approx(0.15448042638975346, rel=REL)
    assert comp["Hydrogen"] == pytest.approx(0.31532726171752107, rel=REL)
    assert comp["Water"] == pytest.approx(0.34364548780391635, rel=REL)
    assert comp["Nitrogen"] == pytest.approx(0.003780251521737198, rel=REL)
    assert g.syngas_molar_flow_mol_s == pytest.approx(755.4298922233367, rel=REL)
    assert g.syngas_mass_flow_kg_s == pytest.approx(14.240116699131857, rel=REL)
    assert g.unconverted_carbon_kg_s == pytest.approx(0.54, rel=REL)
    assert g.cold_gas_efficiency == pytest.approx(0.757846304006116, rel=REL)
    assert g.tar_mass_flow_kg_s == pytest.approx(0.253983084064408, rel=REL)
    assert g.o2_mass_flow_kg_s == pytest.approx(2.2, rel=REL)
    assert g.steam_mass_flow_kg_s == pytest.approx(4.0, rel=REL)


def test_gasifier_wood_chips_downdraft_reference_case():
    g = gasify_biomass(TYPICAL_WOOD_CHIPS, 10.0, 0.25, 0.40, 1123.15, gasifier_type="downdraft")
    comp = g.syngas_composition_mole_frac
    assert comp["CarbonMonoxide"] == pytest.approx(0.2843680587147826, rel=REL)
    assert comp["Hydrogen"] == pytest.approx(0.38661786661628633, rel=REL)
    assert g.syngas_molar_flow_mol_s == pytest.approx(891.4992937578835, rel=REL)
    assert g.cold_gas_efficiency == pytest.approx(0.8750763236058869, rel=REL)
    assert g.tar_mass_flow_kg_s == pytest.approx(0.0399641303405784, rel=REL)
    assert g.carbon_conversion == 0.9


def test_cleanup_reference_case():
    c = clean_syngas(0.25, 0.10, 0.97, 0.98)
    assert c.cleaned_tar_mass_flow_kg_s == pytest.approx(0.0075, rel=REL)
    assert c.captured_tar_mass_flow_kg_s == pytest.approx(0.2425, rel=REL)
    assert c.cleaned_particulate_mass_flow_kg_s == pytest.approx(0.002, rel=REL)
    assert c.captured_particulate_mass_flow_kg_s == pytest.approx(0.098, rel=REL)


def test_syngas_quality_reference_case():
    g = gasify_biomass(TYPICAL_RICE_STRAW, 10.0, 0.22, 0.40, 1123.15,
                       carbon_conversion=0.85, gasifier_type="fluidized_bed")
    q = evaluate_syngas_quality(g.syngas_composition_mole_frac)
    assert q.h2_to_co_molar_ratio == pytest.approx(1.725300514686853, rel=REL)
    assert q.lhv_MJ_per_Nm3 == pytest.approx(5.709336661005528, rel=REL)
    assert q.inert_mole_fraction == pytest.approx(0.501906165715407, rel=REL)
    assert q.recommended_use == "Direct combustion / gas engine power generation only"
