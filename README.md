# biomass-to-syngas-opensource

<!-- how-to-use-with-ai -->
> **New here?** See [How to use this repo with AI (Claude, Gemini, ChatGPT)](HOW_TO_USE_WITH_AI.md) — clone it, paste it into an AI tool, and ask in plain English.


Open-source, literature-grounded conceptual sizing tools for biomass
gasification to syngas: feedstock characterization &rarr; gasifier
&rarr; gas cleanup (tar/particulate) &rarr; syngas quality &
downstream-use screening. Sibling project to
[lng-design-opensource](https://github.com/herrrickshaw/lng-design-opensource)
and [coal-to-urea-design-opensource](https://github.com/herrrickshaw/coal-to-urea-design-opensource),
same discipline: public-domain/textbook correlations only, every
method cited, every module tested, every worked example actually run.

**Real-world motivation**: India generates an estimated 990 million
tonnes/year of agricultural biomass, with ~230 million tonnes/year
currently unutilized - a surplus that, especially where storage is
limited (northern India), drives open-field stubble burning, a major
seasonal air-quality crisis. Gasification of that surplus (rice/paddy
straw in particular) is a genuine, often-proposed alternative. See
`docs/VALIDATION.md` for the public source and the worked example's
scale-up context.

**Scope**: fully generic and literature-only - nothing here derives
from proprietary vendor/client engineering data.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                                        # 18 tests
python examples/full_chain_worked_example.py     # rice straw -> syngas, end to end
streamlit run streamlit_app.py                   # interactive app
```

## Modules

| Module | Method | Key outputs |
|---|---|---|
| `biomass_to_syngas/biomass_feedstock.py` | Channiwala & Parikh (2002) unified HHV correlation | HHV, LHV; rice-straw and wood-chip presets |
| `biomass_to_syngas/gasifier.py` | Elemental balance + WGS-equilibrium quench (Higman & van der Burgt) + tar yield (NREL/TP-570-25357) | Syngas composition/flow, cold gas efficiency, tar yield |
| `biomass_to_syngas/gas_cleanup.py` | Mass-balance tar/particulate removal | Cleaned syngas, captured tar/particulate |
| `biomass_to_syngas/syngas_quality.py` | H2:CO ratio + LHV + downstream-use screening | Recommended use (power vs. FT/methanol feed vs. shift-first) |

## Cross-checked against real gasifier vendors — all three technology categories

`docs/VENDOR_REFERENCE.md` checks this repo's gasifier-type categories
against real, named equipment providers: Ankur Scientific (India,
downdraft, verified installed-project figures), Powermax (explicitly
rice-straw-rated fixed-bed, circulating-fluidized-bed AND updraft
gasifiers — a single real vendor spanning all three of `gasifier.py`'s
technology categories), and Chanderpur Works (a second India-based
downdraft+updraft manufacturer, rice husk explicitly named as
feedstock). Powermax's own published **>=1,200 kcal/Nm3** minimum
syngas energy spec is cleared by this repo's own 100 t/day rice-straw
worked example (1,364 kcal/Nm3), and its updraft product's real
published tar-content range independently brackets `gasifier.py`'s own
`TYPICAL_TAR_YIELD_G_NM3["updraft"]` default. Separately, an
independent literature figure for water-scrub + venturi-scrubber tar
removal (97%) lands exactly on `gas_cleanup.py`'s own existing
`tar_removal_fraction` default — a genuine corroboration, not a
correction, found by checking rather than assumed.

## Related open-source work

Same related-project list as the sibling repos:
[DWSIM](https://github.com/DanWBR/dwsim5),
[IDAES](https://github.com/IDAES/idaes-pse),
[BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam) (the
most directly relevant - a Python biorefinery TEA toolkit with real
published lignocellulosic-ethanol flowsheets, worth consulting
alongside this repo for downstream biomass-to-fuel routes).

## Disclaimer

This tool implements textbook/public-domain conceptual sizing methods
for early-stage screening only. It is not a substitute for a rigorous
process simulator or vendor-certified equipment data for detailed
design.
