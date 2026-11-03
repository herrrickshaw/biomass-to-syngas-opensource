"""Syngas cleanup: tar and particulate removal ahead of any downstream
use (engine/turbine power generation, or further syngas-to-fuels/
chemicals upgrading - see syngas_quality.py for that screening).

Method: mass-balance removal-fraction model, not a rate-based
scrubber/cyclone design (out of scope for conceptual screening).
Typical achievable tar removal efficiencies for wet scrubbing (venturi/
water spray) are widely reported in the 90-99% range for a well-
designed system (see e.g. the same NREL tar report cited in
gasifier.py's docstring, and subsequent DOE/NREL syngas cleanup
literature); particulate removal via a cyclone (coarse) followed by a
scrubber or filter (fine) commonly achieves >95-99% overall removal.

This module's own `tar_removal_fraction` default (0.97) is independently
corroborated by a specific, mechanism-matched literature figure found
via vendor research (docs/VENDOR_REFERENCE.md): water scrubbing alone
removes up to ~50% of tar, and a water scrub followed by a venturi
scrubber raises that to ~97% - landing exactly on this module's existing
default rather than just inside the generic 90-99% range already cited.
"""
from __future__ import annotations

from dataclasses import dataclass

# Defaults: see module docstring for the literature support.
DEFAULT_TAR_REMOVAL_FRACTION = 0.97
DEFAULT_PARTICULATE_REMOVAL_FRACTION = 0.98


@dataclass
class CleanupResult:
    """Mass flows in kg/s; removal fractions dimensionless (0-1)."""

    cleaned_tar_mass_flow_kg_s: float
    captured_tar_mass_flow_kg_s: float
    tar_removal_fraction: float
    cleaned_particulate_mass_flow_kg_s: float
    captured_particulate_mass_flow_kg_s: float
    particulate_removal_fraction: float


def clean_syngas(
    tar_mass_flow_kg_s: float,
    particulate_mass_flow_kg_s: float,
    tar_removal_fraction: float = DEFAULT_TAR_REMOVAL_FRACTION,
    particulate_removal_fraction: float = DEFAULT_PARTICULATE_REMOVAL_FRACTION,
) -> CleanupResult:
    """Mass-balance tar/particulate removal. tar_mass_flow_kg_s and
    particulate_mass_flow_kg_s are typically taken from
    gasifier.gasify_biomass's tar output and a separate particulate
    loading estimate (this module does not estimate particulate
    loading itself - that depends heavily on gasifier internals/
    freeboard design, not modeled here).
    """
    if not (0.0 <= tar_removal_fraction <= 1.0):
        raise ValueError("tar_removal_fraction must be in [0, 1]")
    if not (0.0 <= particulate_removal_fraction <= 1.0):
        raise ValueError("particulate_removal_fraction must be in [0, 1]")

    captured_tar = tar_mass_flow_kg_s * tar_removal_fraction
    captured_particulate = particulate_mass_flow_kg_s * particulate_removal_fraction

    return CleanupResult(
        cleaned_tar_mass_flow_kg_s=tar_mass_flow_kg_s - captured_tar,
        captured_tar_mass_flow_kg_s=captured_tar,
        tar_removal_fraction=tar_removal_fraction,
        cleaned_particulate_mass_flow_kg_s=particulate_mass_flow_kg_s - captured_particulate,
        captured_particulate_mass_flow_kg_s=captured_particulate,
        particulate_removal_fraction=particulate_removal_fraction,
    )
