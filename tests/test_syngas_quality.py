import pytest

from biomass_to_syngas.syngas_quality import evaluate_syngas_quality


def test_evaluate_syngas_quality_rejects_zero_co():
    with pytest.raises(ValueError, match="CarbonMonoxide"):
        evaluate_syngas_quality({"Hydrogen": 0.5, "CarbonMonoxide": 0.0})


def test_evaluate_syngas_quality_ft_ratio_recommends_ft_methanol():
    result = evaluate_syngas_quality({"Hydrogen": 0.40, "CarbonMonoxide": 0.20, "CarbonDioxide": 0.10})
    assert result.h2_to_co_molar_ratio == pytest.approx(2.0)
    assert "Fischer-Tropsch" in result.recommended_use


def test_evaluate_syngas_quality_co_rich_recommends_shift():
    result = evaluate_syngas_quality({"Hydrogen": 0.20, "CarbonMonoxide": 0.40, "CarbonDioxide": 0.10})
    assert result.h2_to_co_molar_ratio < 1.0
    assert "shift" in result.recommended_use.lower()


def test_evaluate_syngas_quality_high_inert_content_recommends_power_only():
    result = evaluate_syngas_quality({"Hydrogen": 0.15, "CarbonMonoxide": 0.10, "Nitrogen": 0.60, "CarbonDioxide": 0.15})
    assert result.inert_mole_fraction > 0.5
    assert "power" in result.recommended_use.lower() or "combustion" in result.recommended_use.lower()


def test_evaluate_syngas_quality_lhv_positive():
    result = evaluate_syngas_quality({"Hydrogen": 0.30, "CarbonMonoxide": 0.30, "CarbonDioxide": 0.10, "Water": 0.05})
    assert result.lhv_MJ_per_Nm3 > 0


def test_lhv_of_pure_hydrogen_and_pure_co_per_nm3():
    # H2: 241.8 kJ/mol / 0.022414 m3/mol = 10.79 MJ/Nm3; CO: 283.0/0.022414 = 12.63 MJ/Nm3
    h2_like = evaluate_syngas_quality({"Hydrogen": 1 - 1e-12, "CarbonMonoxide": 1e-12})
    assert h2_like.lhv_MJ_per_Nm3 == pytest.approx(10.788, abs=1e-3)
    assert evaluate_syngas_quality({"CarbonMonoxide": 1.0}).lhv_MJ_per_Nm3 == pytest.approx(12.626, abs=1e-3)


@pytest.mark.parametrize("h2,co,expected", [(0.34, 0.20, "Fischer-Tropsch"),     # 1.70 boundary
                                            (0.46, 0.20, "Fischer-Tropsch"),     # 2.30 boundary
                                            (0.50, 0.20, "H2-rich")])
def test_h2_co_ratio_band_edges(h2, co, expected):
    assert evaluate_syngas_quality({"Hydrogen": h2, "CarbonMonoxide": co}).recommended_use.startswith(expected)
