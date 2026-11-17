from __future__ import annotations

import pytest

from biomass_to_syngas.properties import GasMixture, pure_fluid_prop

SYNGAS = {"Hydrogen": 0.35, "CarbonMonoxide": 0.30, "CarbonDioxide": 0.15, "Water": 0.15, "Nitrogen": 0.05}


def test_gas_mixture_rejects_fractions_not_summing_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        GasMixture({"Hydrogen": 0.5, "CarbonMonoxide": 0.4})


def test_gas_mixture_reference_properties():
    m = GasMixture(SYNGAS)
    assert m.molecular_weight() == pytest.approx(19.8130222, rel=1e-6)
    assert m.density(400.0, 101325.0) == pytest.approx(0.6036928833167349, rel=1e-6)
    assert m.compressibility(400.0, 101325.0) == pytest.approx(0.9999012378110673, rel=1e-6)


def test_pure_fluid_prop_nitrogen_boiling_point():
    assert pure_fluid_prop("Nitrogen", "T", P=101325, Q=0) == pytest.approx(77.355, abs=0.01)
