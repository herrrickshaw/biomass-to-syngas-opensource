import pytest

from biomass_to_syngas.gas_cleanup import clean_syngas


def test_clean_syngas_mass_balance_closes():
    result = clean_syngas(tar_mass_flow_kg_s=0.25, particulate_mass_flow_kg_s=0.10,
                            tar_removal_fraction=0.97, particulate_removal_fraction=0.98)
    assert result.cleaned_tar_mass_flow_kg_s + result.captured_tar_mass_flow_kg_s == pytest.approx(0.25)
    assert result.cleaned_particulate_mass_flow_kg_s + result.captured_particulate_mass_flow_kg_s == pytest.approx(0.10)


def test_clean_syngas_higher_removal_fraction_leaves_less_behind():
    low = clean_syngas(0.25, 0.10, tar_removal_fraction=0.80, particulate_removal_fraction=0.80)
    high = clean_syngas(0.25, 0.10, tar_removal_fraction=0.99, particulate_removal_fraction=0.99)
    assert high.cleaned_tar_mass_flow_kg_s < low.cleaned_tar_mass_flow_kg_s
    assert high.cleaned_particulate_mass_flow_kg_s < low.cleaned_particulate_mass_flow_kg_s


def test_clean_syngas_rejects_invalid_fraction():
    with pytest.raises(ValueError):
        clean_syngas(0.25, 0.10, tar_removal_fraction=1.5)
    with pytest.raises(ValueError):
        clean_syngas(0.25, 0.10, particulate_removal_fraction=-0.1)
