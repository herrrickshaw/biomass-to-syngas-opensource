"""Biomass feedstock characterization: ultimate analysis + a
solid-fuel-specific HHV correlation (Dulong's formula, used for coal in
the sibling coal-to-urea repo, is calibrated to coal and fits biomass
poorly - biomass has much higher oxygen content and a different H/O
interaction).

HHV method: Channiwala, S.A. & Parikh, P.P., "A unified correlation for
estimating HHV of solid, liquid and gaseous fuels", Fuel 81(8), 2002,
1051-1063 - the most widely cited generic higher-heating-value
correlation for solid fuels including biomass, validated against a
very large published fuel dataset spanning coal, biomass, and other
solid/liquid/gaseous fuels:

    HHV (MJ/kg) = 0.3491 C + 1.1783 H + 0.1005 S - 0.1034 O
                  - 0.0151 N - 0.0211 Ash

(mass percent, dry basis for the elemental terms; ash as received).

Real-world motivation for the rice/paddy straw preset: India generates
an estimated 990 million tonnes/year of agricultural biomass with
~230 million tonnes/year surplus currently unused, and a well-
documented consequence of that surplus going unmanaged - especially
limited storage in northern India - is open-field stubble burning, a
major seasonal air-quality crisis (Datta, A.K. et al., "Indian Scenario
of Biomass Availability and its Bioenergy Conversion", Plant Archives
25, Special Issue, 2025, 121-126, a publicly published peer-reviewed
paper - DOI 10.51470/PLANTARCHIVES.2025.SP.ICTPAIRS-021). Gasification
of paddy/rice straw is a genuine, often-proposed alternative to
burning it, and is the primary motivating use case for this repo -
see docs/VALIDATION.md.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BiomassAnalysis:
    """As-received ultimate analysis, mass fractions summing to 1.0."""
    carbon: float
    hydrogen: float
    oxygen: float
    nitrogen: float
    sulfur: float
    ash: float
    moisture: float

    def __post_init__(self) -> None:
        total = self.carbon + self.hydrogen + self.oxygen + self.nitrogen + self.sulfur + self.ash + self.moisture
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Ultimate analysis mass fractions must sum to 1.0, got {total:.4f}")

    def hhv_MJ_kg(self) -> float:
        """Channiwala & Parikh (2002) unified correlation - see module
        docstring. Mass fractions here are on an as-received (not dry)
        basis, a common simplified application of this correlation for
        conceptual-level work (the original correlation is defined on a
        dry basis); moisture's own effect on usable (lower) heating
        value is captured separately - see lhv_MJ_kg."""
        pct = lambda x: x * 100.0
        return (
            0.3491 * pct(self.carbon) + 1.1783 * pct(self.hydrogen) + 0.1005 * pct(self.sulfur)
            - 0.1034 * pct(self.oxygen) - 0.0151 * pct(self.nitrogen) - 0.0211 * pct(self.ash)
        )

    def lhv_MJ_kg(self) -> float:
        """LHV = HHV minus the latent heat of the water formed from fuel
        hydrogen AND the free moisture already present - standard
        correction (e.g. Basu, "Biomass Gasification and Pyrolysis"),
        using water's latent heat of vaporization at standard conditions,
        2.442 MJ/kg."""
        water_from_h2_combustion = 8.936 * self.hydrogen  # kg H2O per kg fuel, stoichiometric H->H2O
        return self.hhv_MJ_kg() - 2.442 * (water_from_h2_combustion + self.moisture)


# Illustrative presets (not a claim about any specific batch/source).
# Typical wood chip ultimate analysis - widely reported range, e.g.
# Jenkins, B.M. et al., "Combustion properties of biomass", Fuel
# Processing Technology 54, 1998, 17-46 (a classic, widely cited
# biomass characterization reference).
TYPICAL_WOOD_CHIPS = BiomassAnalysis(
    carbon=0.480, hydrogen=0.060, oxygen=0.420, nitrogen=0.003, sulfur=0.001,
    ash=0.016, moisture=0.020,
)
# Rice/paddy straw - the real Indian stubble-burning feedstock this
# repo is motivated by (see module docstring). Higher ash and silica
# content than wood (well-documented - straw's characteristic high
# silica content is why straw-fired grates/gasifiers need different
# ash-handling design than wood), lower carbon, higher oxygen.
TYPICAL_RICE_STRAW = BiomassAnalysis(
    carbon=0.360, hydrogen=0.050, oxygen=0.390, nitrogen=0.008, sulfur=0.002,
    ash=0.140, moisture=0.050,
)
