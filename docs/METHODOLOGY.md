# Methodology

## Feedstock characterization (`biomass_feedstock.py`)

Channiwala, S.A. & Parikh, P.P., "A unified correlation for estimating
HHV of solid, liquid and gaseous fuels", Fuel 81(8), 2002, 1051-1063 -
the most widely cited generic HHV correlation validated across a large
published fuel dataset including biomass. LHV correction for fuel
hydrogen and free moisture: standard method (e.g. Basu, "Biomass
Gasification and Pyrolysis"). Presets: wood chips per Jenkins, B.M. et
al., "Combustion properties of biomass", Fuel Processing Technology 54,
1998; rice/paddy straw per commonly reported published ranges for
Indian agricultural residue (see docs/VALIDATION.md).

## Gasifier (`gasifier.py`)

Same elemental-balance + water-gas-shift-equilibrium-quench method as
the sibling coal-to-urea repo's gasifier.py (Higman & van der Burgt,
"Gasification", 2nd ed., Elsevier, 2008 - covers both coal and biomass
gasification with this same conceptual-level approach). Tar yield by
gasifier type: Milne, T.A., Evans, R.J., Abatzoglou, N., "Biomass
Gasifier 'Tars': Their Nature, Formation, and Conversion", NREL/
TP-570-25357, National Renewable Energy Laboratory, 1998 (a freely
available US government technical report).

## Gas cleanup (`gas_cleanup.py`)

Mass-balance removal-fraction model; typical achievable tar/
particulate removal efficiencies per the same NREL tar report and
subsequent DOE/NREL syngas cleanup literature.

## Syngas quality (`syngas_quality.py`)

H2:CO ratio screening against the 2:1 stoichiometric target both
Fischer-Tropsch and methanol synthesis consume - standard syngas
utilization knowledge, structured the same way as the sibling LNG
project's process_selection.py screening heuristic.
