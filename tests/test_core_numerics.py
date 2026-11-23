"""Hand-computed values, invariants and error paths for the biomass-to-syngas modules.

Expected numbers are derived on paper from the formulas in each module
docstring. CoolProp mixture state calls are replaced by a fake wherever a
number depends on them (no real high-pressure mixture output is asserted).
"""
import math

import pytest

from biomass_to_syngas import biomass_feedstock as BF
from biomass_to_syngas import gas_cleanup as GC
from biomass_to_syngas import gasifier as G
from biomass_to_syngas import properties as P
from biomass_to_syngas import syngas_quality as SQ

# ----------------------------------------------------------------- properties


def test_gas_mixture_requires_mole_fractions_summing_to_one():
    P.GasMixture({"Hydrogen": 0.75, "Nitrogen": 0.25})
    P.GasMixture({"Hydrogen": 0.75, "Nitrogen": 0.2500005})  # within 1e-6
    with pytest.raises(ValueError, match="sum to 1.0"):
        P.GasMixture({"Hydrogen": 0.75, "Nitrogen": 0.26})
    with pytest.raises(ValueError):
        P.GasMixture({"Hydrogen": 0.74, "Nitrogen": 0.25})


def test_heos_string_format_and_order():
    m = P.GasMixture({"Hydrogen": 0.75, "Nitrogen": 0.25})
    assert m._heos_string() == "Hydrogen[0.75]&Nitrogen[0.25]"


def test_molecular_weight_is_the_mole_weighted_mean():
    m = P.GasMixture({"Hydrogen": 0.75, "Nitrogen": 0.25})
    assert m.molecular_weight() == pytest.approx(0.75 * 2.016 + 0.25 * 28.014, rel=1e-3)


@pytest.mark.parametrize("method,output", [
    ("cp_over_cv", None), ("compressibility", "Z"), ("density", "Dmass"), ("enthalpy", "Hmass"),
    ("viscosity", "V"), ("thermal_conductivity", "L"), ("specific_heat", "Cpmass"),
])
def test_state_accessors_request_the_right_coolprop_output(monkeypatch, method, output):
    calls = []

    def fake(out, k1, v1, k2, v2, fluid):
        calls.append((out, k1, v1, k2, v2, fluid))
        return {"Cpmass": 14.0, "Cvmass": 10.0}.get(out, 7.0)

    monkeypatch.setattr(P.CP, "PropsSI", fake)
    m = P.GasMixture({"Hydrogen": 0.75, "Nitrogen": 0.25})
    result = getattr(m, method)(300.0, 2.0e5)
    if method == "cp_over_cv":
        assert result == pytest.approx(1.4)
        assert [c[0] for c in calls] == ["Cpmass", "Cvmass"]
    else:
        assert result == 7.0 if output not in ("Cpmass",) else result == 14.0
        assert calls[0][0] == output
    assert calls[0][1:] == ("T", 300.0, "P", 2.0e5, "Hydrogen[0.75]&Nitrogen[0.25]")


def test_pure_fluid_prop_passes_state_pairs_through():
    # nitrogen normal boiling point, 77.355 K (NIST)
    assert P.pure_fluid_prop("Nitrogen", "T", P=101325.0, Q=0) == pytest.approx(77.355, abs=0.05)


# ------------------------------------------------------------------ feedstock


def test_biomass_analysis_must_sum_to_one_with_a_tight_tolerance():
    BF.BiomassAnalysis(0.48, 0.06, 0.42, 0.003, 0.001, 0.016, 0.0199995)    # off by 5e-7: accepted
    with pytest.raises(ValueError, match="sum to 1.0"):
        BF.BiomassAnalysis(0.48, 0.06, 0.42, 0.003, 0.001, 0.016, 0.021)    # off by 1e-3
    with pytest.raises(ValueError):
        BF.BiomassAnalysis(0.48, 0.06, 0.42, 0.003, 0.001, 0.016, 0.019)


def test_presets_have_their_documented_composition():
    w, s = BF.TYPICAL_WOOD_CHIPS, BF.TYPICAL_RICE_STRAW
    assert (w.carbon, w.hydrogen, w.oxygen, w.ash, w.moisture) == (0.480, 0.060, 0.420, 0.016, 0.020)
    assert (s.carbon, s.hydrogen, s.oxygen, s.ash, s.moisture) == (0.360, 0.050, 0.390, 0.140, 0.050)
    assert s.ash > w.ash and s.carbon < w.carbon          # straw: ashy and carbon-poor


def test_channiwala_parikh_hhv_hand_computed():
    w = BF.TYPICAL_WOOD_CHIPS
    # 0.3491*48 + 1.1783*6 + 0.1005*0.1 - 0.1034*42 - 0.0151*0.3 - 0.0211*1.6
    expected = 16.7568 + 7.0698 + 0.01005 - 4.3428 - 0.00453 - 0.03376
    assert w.hhv_MJ_kg() == pytest.approx(expected)
    assert w.hhv_MJ_kg() == pytest.approx(19.4555, abs=1e-3)
    s = BF.TYPICAL_RICE_STRAW
    assert s.hhv_MJ_kg() == pytest.approx(0.3491 * 36 + 1.1783 * 5 + 0.1005 * 0.2 - 0.1034 * 39
                                          - 0.0151 * 0.8 - 0.0211 * 14)
    assert s.hhv_MJ_kg() < w.hhv_MJ_kg()


def test_lhv_subtracts_latent_heat_of_formed_and_free_water():
    w = BF.TYPICAL_WOOD_CHIPS
    assert w.lhv_MJ_kg() == pytest.approx(w.hhv_MJ_kg() - 2.442 * (8.936 * 0.06 + 0.02))
    assert w.lhv_MJ_kg() < w.hhv_MJ_kg()
    dry = BF.BiomassAnalysis(0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0)
    assert dry.lhv_MJ_kg() == pytest.approx(dry.hhv_MJ_kg())            # no hydrogen, no moisture -> no correction


# ----------------------------------------------------------------- gas cleanup


def test_cleanup_hand_computed_defaults():
    r = GC.clean_syngas(1.0, 2.0)
    assert r.captured_tar_mass_flow_kg_s == pytest.approx(0.97)
    assert r.cleaned_tar_mass_flow_kg_s == pytest.approx(0.03)
    assert r.captured_particulate_mass_flow_kg_s == pytest.approx(1.96)
    assert r.cleaned_particulate_mass_flow_kg_s == pytest.approx(0.04)
    assert (r.tar_removal_fraction, r.particulate_removal_fraction) == (0.97, 0.98)


def test_cleanup_removal_fractions_are_independent_and_inclusive():
    none = GC.clean_syngas(1.0, 1.0, tar_removal_fraction=0.0, particulate_removal_fraction=0.0)
    assert none.cleaned_tar_mass_flow_kg_s == 1.0 and none.cleaned_particulate_mass_flow_kg_s == 1.0
    full = GC.clean_syngas(1.0, 1.0, tar_removal_fraction=1.0, particulate_removal_fraction=1.0)
    assert full.cleaned_tar_mass_flow_kg_s == 0.0 and full.cleaned_particulate_mass_flow_kg_s == 0.0
    mixed = GC.clean_syngas(2.0, 3.0, tar_removal_fraction=0.5, particulate_removal_fraction=0.9)
    assert mixed.captured_tar_mass_flow_kg_s == pytest.approx(1.0)
    assert mixed.captured_particulate_mass_flow_kg_s == pytest.approx(2.7)


@pytest.mark.parametrize("kw,name", [
    ({"tar_removal_fraction": -0.01}, "tar_removal_fraction"), ({"tar_removal_fraction": 1.01}, "tar_removal_fraction"),
    ({"particulate_removal_fraction": -0.01}, "particulate_removal_fraction"),
    ({"particulate_removal_fraction": 1.01}, "particulate_removal_fraction"),
])
def test_cleanup_rejects_fractions_outside_zero_one(kw, name):
    with pytest.raises(ValueError, match=name):
        GC.clean_syngas(1.0, 1.0, **kw)


def test_cleanup_conserves_mass():
    r = GC.clean_syngas(1.7, 4.2, 0.83, 0.61)
    assert r.captured_tar_mass_flow_kg_s + r.cleaned_tar_mass_flow_kg_s == pytest.approx(1.7)
    assert r.captured_particulate_mass_flow_kg_s + r.cleaned_particulate_mass_flow_kg_s == pytest.approx(4.2)


# -------------------------------------------------------------------- gasifier


def _gasify(**kw):
    args = {"biomass": BF.TYPICAL_RICE_STRAW, "biomass_mass_flow_kg_s": 10.0, "o2_to_biomass_mass_ratio": 0.22,
            "steam_to_biomass_mass_ratio": 0.40, "gasifier_T_K": 1123.15}
    args.update(kw)
    return G.gasify_biomass(**args)


def test_wgs_equilibrium_constant_matches_moe_correlation():
    assert G._wgs_equilibrium_K(1000.0) == pytest.approx(math.exp(4.5778 - 4.33))
    assert G._wgs_equilibrium_K(800.0) > G._wgs_equilibrium_K(1200.0)


def test_tar_yield_table_values():
    assert G.TYPICAL_TAR_YIELD_G_NM3 == {"downdraft": 2.0, "updraft": 50.0, "fluidized_bed": 15.0}


@pytest.mark.parametrize("bad", [0.0, -0.1, 1.0001])
def test_carbon_conversion_range(bad):
    with pytest.raises(ValueError, match="carbon_conversion"):
        _gasify(carbon_conversion=bad)


def test_gasifier_type_error_lists_the_options():
    with pytest.raises(ValueError, match="downdraft"):
        _gasify(gasifier_type="rotary_kiln")


def test_feed_flows_unconverted_carbon_and_defaults():
    r = _gasify()
    assert r.o2_mass_flow_kg_s == pytest.approx(2.2)
    assert r.steam_mass_flow_kg_s == pytest.approx(4.0)
    assert r.carbon_conversion == 0.90                                          # default
    assert r.unconverted_carbon_kg_s == pytest.approx(10.0 * 0.36 * 0.10)       # (1 - 0.90) of biomass carbon
    assert _gasify(carbon_conversion=1.0).unconverted_carbon_kg_s == 0.0


def test_default_gasifier_type_is_fluidized_bed():
    d = _gasify()
    explicit = _gasify(gasifier_type="fluidized_bed")
    assert d.tar_mass_flow_kg_s == pytest.approx(explicit.tar_mass_flow_kg_s)


def test_tar_mass_flow_is_yield_times_normal_gas_volume():
    for typ, y in G.TYPICAL_TAR_YIELD_G_NM3.items():
        r = _gasify(gasifier_type=typ)
        assert r.tar_mass_flow_kg_s == pytest.approx(r.syngas_molar_flow_mol_s * 0.022414 * y / 1000.0)
    down, fb, up = (_gasify(gasifier_type=t).tar_mass_flow_kg_s for t in ("downdraft", "fluidized_bed", "updraft"))
    assert down < fb < up
    assert up / down == pytest.approx(25.0)


def test_gasifier_conserves_carbon_hydrogen_oxygen_nitrogen():
    b, m = BF.TYPICAL_RICE_STRAW, 10.0
    r = _gasify()
    comp, n = r.syngas_composition_mole_frac, r.syngas_molar_flow_mol_s
    mol = {k: v * n for k, v in comp.items()}
    assert set(comp) == {"CarbonMonoxide", "CarbonDioxide", "Hydrogen", "Water", "Nitrogen"}
    assert sum(comp.values()) == pytest.approx(1.0)
    n_c = m * b.carbon * 1000 / 12.011 * 0.90
    assert mol["CarbonMonoxide"] + mol["CarbonDioxide"] == pytest.approx(n_c, rel=1e-9)
    water_in = m * b.moisture * 1000 / 18.015 + 4.0 * 1000 / 18.015
    assert 2 * mol["Hydrogen"] + 2 * mol["Water"] == pytest.approx(m * b.hydrogen * 1000 / 1.008 + 2 * water_in, rel=1e-9)
    o_in = m * b.oxygen * 1000 / 15.999 + water_in + 2 * 2.2 * 1000 / 31.998
    assert mol["CarbonMonoxide"] + 2 * mol["CarbonDioxide"] + mol["Water"] == pytest.approx(o_in, rel=1e-9)
    assert mol["Nitrogen"] == pytest.approx(m * b.nitrogen * 1000 / 14.007 / 2)


def test_gasifier_outlet_sits_on_the_water_gas_shift_equilibrium():
    for T in (1000.0, 1123.15, 1300.0):
        c = _gasify(gasifier_T_K=T).syngas_composition_mole_frac
        q = (c["CarbonDioxide"] * c["Hydrogen"]) / (c["CarbonMonoxide"] * c["Water"])
        assert q == pytest.approx(G._wgs_equilibrium_K(T), rel=1e-6)


def test_cold_gas_efficiency_matches_its_definition():
    r = _gasify()
    c, n = r.syngas_composition_mole_frac, r.syngas_molar_flow_mol_s
    hhv_gas = n * (c["CarbonMonoxide"] * 283.0 + c["Hydrogen"] * 285.8)
    assert r.cold_gas_efficiency == pytest.approx(hhv_gas / (10.0 * BF.TYPICAL_RICE_STRAW.hhv_MJ_kg() * 1000.0))


def test_zero_heating_value_feed_reports_zero_cold_gas_efficiency(monkeypatch):
    monkeypatch.setattr(BF.BiomassAnalysis, "hhv_MJ_kg", lambda self: 0.0)
    assert _gasify().cold_gas_efficiency == 0.0


def test_syngas_mass_flow_is_the_mole_weighted_molar_mass_times_moles():
    r = _gasify()
    mw = sum(f * G._species_mw(k) for k, f in r.syngas_composition_mole_frac.items())
    assert r.syngas_mass_flow_kg_s == pytest.approx(r.syngas_molar_flow_mol_s * mw / 1000.0)
    assert G._species_mw("Hydrogen") == 2.016 and G._species_mw("Nitrogen") == 28.014


def test_more_oxygen_burns_more_carbon_to_co2():
    lean = _gasify(o2_to_biomass_mass_ratio=0.15).syngas_composition_mole_frac
    rich = _gasify(o2_to_biomass_mass_ratio=0.30).syngas_composition_mole_frac
    assert rich["CarbonDioxide"] > lean["CarbonDioxide"]
    assert rich["CarbonMonoxide"] < lean["CarbonMonoxide"]


def test_over_oxidised_feed_has_no_physical_composition():
    pure_c = BF.BiomassAnalysis(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="No physically valid"):
        G.gasify_biomass(pure_c, 1.0, 20.0, 0.0, 1123.15)


# --------------------------------------------------------------- syngas quality


def _quality(h2, co, **others):
    return SQ.evaluate_syngas_quality({"Hydrogen": h2, "CarbonMonoxide": co, **others})


def test_quality_hand_computed_lhv_and_ratio():
    r = _quality(0.35, 0.20, CarbonDioxide=0.25, Water=0.20)
    assert r.h2_to_co_molar_ratio == pytest.approx(1.75)
    # (0.20 * 283.0 + 0.35 * 241.8) kJ/mol / 0.022414 / 1000 = 6.30 MJ/Nm3 (H2 on an LHV basis)
    assert r.lhv_MJ_per_Nm3 == pytest.approx((0.20 * 283.0 + 0.35 * 241.8) / 0.022414 / 1000.0)
    assert r.lhv_MJ_per_Nm3 == pytest.approx(6.30, abs=0.01)
    assert r.inert_mole_fraction == pytest.approx(0.45)
    assert r.recommended_use == "Fischer-Tropsch / methanol synthesis feed"
    assert "1.75" in r.rationale


def test_quality_counts_all_inert_species_but_not_fuel_gases():
    r = _quality(0.3, 0.3, Nitrogen=0.1, CarbonDioxide=0.1, Water=0.1, HydrogenSulfide=0.05, Methane=0.05)
    assert r.inert_mole_fraction == pytest.approx(0.35)


def test_quality_ratio_window_is_inclusive_at_both_ends():
    assert _quality(0.34, 0.20).recommended_use.startswith("Fischer-Tropsch")     # exactly 1.7
    assert _quality(0.46, 0.20).recommended_use.startswith("Fischer-Tropsch")     # exactly 2.3
    assert _quality(0.33, 0.20).recommended_use.startswith("Water-gas-shift")     # 1.65
    assert _quality(0.47, 0.20).recommended_use.startswith("H2-rich")             # 2.35
    assert "CO-rich" in _quality(0.33, 0.20).rationale
    assert "H2-rich" in _quality(0.47, 0.20).rationale


def test_quality_high_inerts_override_the_ratio_but_only_above_half():
    diluted = _quality(0.17, 0.10, Nitrogen=0.5000001)
    assert diluted.recommended_use.startswith("Direct combustion")
    assert "too high for chemical" in diluted.rationale
    assert not _quality(0.17, 0.10, Nitrogen=0.5).recommended_use.startswith("Direct combustion")  # exactly 0.50


def test_quality_requires_positive_co():
    for co in (0.0, -0.1):
        with pytest.raises(ValueError, match="must be positive"):
            _quality(0.5, co)
    with pytest.raises(ValueError):
        SQ.evaluate_syngas_quality({"Hydrogen": 0.5})        # CO missing entirely


def test_quality_tables_and_lhv_vs_hhv_basis():
    assert SQ._LHV_KJ_MOL["Hydrogen"] < SQ._HHV_KJ_MOL["Hydrogen"]
    assert SQ._LHV_KJ_MOL["CarbonMonoxide"] == SQ._HHV_KJ_MOL["CarbonMonoxide"] == 283.0


def test_gasifier_output_feeds_the_quality_screen():
    r = _gasify()
    q = SQ.evaluate_syngas_quality(r.syngas_composition_mole_frac)
    c = r.syngas_composition_mole_frac
    assert q.h2_to_co_molar_ratio == pytest.approx(c["Hydrogen"] / c["CarbonMonoxide"])
    assert q.inert_mole_fraction == pytest.approx(c["Water"] + c["CarbonDioxide"] + c["Nitrogen"])


