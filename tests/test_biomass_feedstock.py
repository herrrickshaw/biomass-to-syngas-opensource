import pytest

from biomass_to_syngas.biomass_feedstock import TYPICAL_RICE_STRAW, TYPICAL_WOOD_CHIPS, BiomassAnalysis


def test_biomass_analysis_rejects_fractions_not_summing_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        BiomassAnalysis(carbon=0.5, hydrogen=0.1, oxygen=0.1, nitrogen=0.1, sulfur=0.1, ash=0.1, moisture=0.1)


def test_hhv_in_plausible_published_range():
    # Wood ~18-20 MJ/kg, rice straw ~12-15 MJ/kg (higher ash/oxygen,
    # lower carbon than wood) are commonly reported ranges.
    assert 16.0 < TYPICAL_WOOD_CHIPS.hhv_MJ_kg() < 22.0
    assert 11.0 < TYPICAL_RICE_STRAW.hhv_MJ_kg() < 17.0
    assert TYPICAL_RICE_STRAW.hhv_MJ_kg() < TYPICAL_WOOD_CHIPS.hhv_MJ_kg()


def test_lhv_less_than_hhv():
    assert TYPICAL_WOOD_CHIPS.lhv_MJ_kg() < TYPICAL_WOOD_CHIPS.hhv_MJ_kg()
    assert TYPICAL_RICE_STRAW.lhv_MJ_kg() < TYPICAL_RICE_STRAW.hhv_MJ_kg()


def test_higher_moisture_widens_hhv_lhv_gap():
    dry = BiomassAnalysis(carbon=0.40, hydrogen=0.05, oxygen=0.40, nitrogen=0.01, sulfur=0.0, ash=0.14, moisture=0.0)
    wet = BiomassAnalysis(carbon=0.36, hydrogen=0.045, oxygen=0.36, nitrogen=0.009, sulfur=0.0, ash=0.126, moisture=0.10)
    assert (dry.hhv_MJ_kg() - dry.lhv_MJ_kg()) < (wet.hhv_MJ_kg() - wet.lhv_MJ_kg())


def test_channiwala_parikh_hhv_and_lhv_hand_computed_for_wood_chips():
    # 0.3491*48 + 1.1783*6 + 0.1005*0.1 - 0.1034*42 - 0.0151*0.3 - 0.0211*1.6 = 19.45556 MJ/kg
    assert TYPICAL_WOOD_CHIPS.hhv_MJ_kg() == pytest.approx(19.45556, abs=1e-5)
    # LHV = HHV - 2.442*(8.936*0.060 + 0.020) = 19.45556 - 1.35814 = 18.09742
    assert TYPICAL_WOOD_CHIPS.lhv_MJ_kg() == pytest.approx(18.09742, abs=1e-5)
