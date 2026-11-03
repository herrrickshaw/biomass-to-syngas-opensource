# Biomass gasification to syngas - conceptual sizing tools

Open-source, literature-grounded conceptual sizing tools for biomass gasification to syngas, for
process engineers and students doing early-stage screening. The chain is feedstock characterisation
-> gasifier (elemental balance + water-gas-shift equilibrium + tar yield) -> gas cleanup
(tar/particulate) -> syngas quality and downstream-use screening. Outputs are Python result
dataclasses, a printed worked example, and a Streamlit app.

> Status: maintained. **Conceptual sizing only, not for detailed design.** Public-domain/textbook
> correlations only; nothing derives from proprietary vendor or client engineering data. It is not a
> substitute for a rigorous process simulator or vendor-certified equipment data.

Sibling project to [lng-design-opensource](https://github.com/herrrickshaw/lng-design-opensource) and
[coal-to-urea-design-opensource](https://github.com/herrrickshaw/coal-to-urea-design-opensource),
with the same discipline: every method cited, every module tested, every worked example actually run.

**Real-world motivation**: India generates an estimated 990 million tonnes/year of agricultural
biomass, with ~230 million tonnes/year currently unutilised - a surplus that, especially where
storage is limited (northern India), drives open-field stubble burning, a major seasonal air-quality
crisis. Gasification of that surplus (rice/paddy straw in particular) is a genuine, often-proposed
alternative. See `docs/VALIDATION.md` for the public source and the worked example's scale-up context.

## What it does
- Computes HHV and LHV of a biomass from its ultimate analysis (Channiwala & Parikh 2002), with rice-straw and wood-chip presets.
- Solves an elemental mass balance with a water-gas-shift equilibrium quench (Higman & van der Burgt) for syngas composition, flow and cold-gas efficiency.
- Estimates tar yield by gasifier type (downdraft / updraft / fluidised bed; Milne, Evans & Abatzoglou, NREL/TP-570-25357).
- Applies mass-balance tar and particulate removal fractions.
- Screens syngas by H2:CO ratio, LHV and inert content to suggest power vs. FT/methanol feed vs. shift-first.
- Provides CoolProp-based mixture properties (`properties.py`) and an interactive Streamlit app.

## Quick start
```bash
git clone https://github.com/herrrickshaw/biomass-to-syngas-opensource.git
cd biomass-to-syngas-opensource
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python examples/full_chain_worked_example.py     # rice straw -> syngas, end to end
streamlit run streamlit_app.py                   # interactive app
```
New to this? See [How to use this repo with AI](HOW_TO_USE_WITH_AI.md).

## How it works
| Stage | Module | Method | Key outputs |
|---|---|---|---|
| Feedstock | `biomass_to_syngas/biomass_feedstock.py` | Channiwala & Parikh (2002) unified HHV correlation | HHV, LHV (MJ/kg) |
| Gasifier | `biomass_to_syngas/gasifier.py` | Elemental balance + WGS-equilibrium quench + tar yield | Syngas composition/flow, cold-gas efficiency, tar |
| Cleanup | `biomass_to_syngas/gas_cleanup.py` | Mass-balance tar/particulate removal | Cleaned syngas, captured tar/particulate |
| Quality | `biomass_to_syngas/syngas_quality.py` | H2:CO + LHV + inert screening | Recommended downstream use |

Sizing functions are pure: dataclass inputs in, result dataclasses out (units in docstrings and
field names, e.g. `_kg_s`, `_K`). Correlation coefficients, physical constants and screening
thresholds are named constants with citations in `biomass_to_syngas/constants.py` and at the top of
each module. The CLI/UI (`examples/`, `streamlit_app.py`) sit at the edge.

### Cross-checked against real gasifier vendors
`docs/VENDOR_REFERENCE.md` checks the gasifier-type categories against real, named providers:
Ankur Scientific (India, downdraft, verified installed-project figures), Powermax (explicitly
rice-straw-rated fixed-bed, circulating-fluidised-bed and updraft gasifiers - one vendor spanning all
three of `gasifier.py`'s categories) and Chanderpur Works (a second India-based downdraft+updraft
manufacturer, rice husk named as feedstock). Powermax's published **>=1,200 kcal/Nm3** minimum syngas
energy spec is cleared by the 100 t/day rice-straw worked example (1,364 kcal/Nm3), and its updraft
product's published tar range brackets `TYPICAL_TAR_YIELD_G_NM3["updraft"]`. Separately, a literature
figure for water-scrub + venturi-scrubber tar removal (97%) lands exactly on `gas_cleanup.py`'s
`tar_removal_fraction` default - a corroboration, not a correction.

## Repository layout
| Path | Purpose |
|---|---|
| `biomass_to_syngas/` | Sizing modules and `constants.py` |
| `examples/full_chain_worked_example.py` | End-to-end rice-straw worked example |
| `streamlit_app.py` | Interactive UI |
| `tests/` | pytest suite incl. characterisation tests pinning example outputs |
| `docs/` | `METHODOLOGY.md`, `VALIDATION.md`, `VENDOR_REFERENCE.md` |

## Configuration
No environment variables, secrets or config files. All inputs are function arguments or Streamlit widgets.

## Testing
```bash
pytest -q        # 27 tests
ruff check .
```

## Limitations and known issues
- Conceptual screening only: the gasifier module assumes a pure O2 feed (air-blown cases are not modelled) and is CH4-free, a larger simplification at 700-900 C than for high-temperature coal gasification.
- Tar yield is a per-gasifier-type input (illustrative midpoints of literature ranges), not predicted from first principles.
- Heating-value correlation is applied on an as-received basis although defined on a dry basis.
- Particulate loading is not estimated; supply it separately.

## Related repositories
[lng-design-opensource](https://github.com/herrrickshaw/lng-design-opensource),
[coal-to-urea-design-opensource](https://github.com/herrrickshaw/coal-to-urea-design-opensource).
Related open-source work: [DWSIM](https://github.com/DanWBR/dwsim5),
[IDAES](https://github.com/IDAES/idaes-pse), and
[BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam) (a Python biorefinery TEA toolkit
with published lignocellulosic-ethanol flowsheets, useful for downstream biomass-to-fuel routes).

## Licence
`pyproject.toml` declares MIT; there is no `LICENSE` file in the repository yet.
