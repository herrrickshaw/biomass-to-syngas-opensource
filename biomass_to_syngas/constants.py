"""Physical constants shared by the sizing modules.

Every value is a textbook/public-domain number; the citation sits next
to it so a reviewer can check the figure without opening another file.
Changing any of these changes every module's output - the
characterisation tests in tests/test_characterisation.py will fail.
"""
from __future__ import annotations

# Atomic weights, g/mol (IUPAC 2013 conventional values, 4-5 significant
# figures - sufficient for a conceptual elemental balance).
ATOMIC_WEIGHT_G_MOL: dict[str, float] = {
    "C": 12.011,
    "H": 1.008,
    "O": 15.999,
    "N": 14.007,
    "S": 32.06,
}

# Molecular weights, g/mol, keyed by CoolProp fluid name so the same
# keys work for properties.GasMixture.
MOLECULAR_WEIGHT_G_MOL: dict[str, float] = {
    "CarbonMonoxide": 28.01,
    "CarbonDioxide": 44.01,
    "Hydrogen": 2.016,
    "Water": 18.015,
    "Nitrogen": 28.014,
}
MW_H2O_G_MOL = MOLECULAR_WEIGHT_G_MOL["Water"]
MW_O2_G_MOL = 31.998

# Standard heats of combustion, kJ/mol (Perry's Chemical Engineers'
# Handbook / NIST WebBook, 25 C). CO has no H2O product so LHV == HHV.
HHV_KJ_MOL: dict[str, float] = {"CarbonMonoxide": 283.0, "Hydrogen": 285.8}
LHV_KJ_MOL: dict[str, float] = {"CarbonMonoxide": 283.0, "Hydrogen": 241.8}

# Molar volume of an ideal gas at normal conditions (0 C, 1 atm), m3/mol
# - the "Nm3" basis used for tar yields (g/Nm3) and syngas LHV (MJ/Nm3).
NM3_PER_MOL_STP = 0.022414

# Latent heat of vaporisation of water at standard conditions, MJ/kg
# (Basu, "Biomass Gasification and Pyrolysis", HHV -> LHV correction).
LATENT_HEAT_WATER_MJ_KG = 2.442
# kg of H2O formed per kg of fuel hydrogen burnt (stoichiometric
# H2 + 1/2 O2 -> H2O, 18.015 / 2.016).
KG_H2O_PER_KG_H2 = 8.936
