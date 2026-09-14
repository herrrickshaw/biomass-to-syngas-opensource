# External validation

## Real-world motivation and public source

Datta, A.K., Bharodia, C., Bani, R.J., Vedanti, P., Meet, N., Jensi, N.,
"Indian Scenario of Biomass Availability and its Bioenergy Conversion",
Plant Archives 25, Special Issue (ICTPAIRS-JAU, Junagadh), Jan. 2025,
pp. 121-126, DOI 10.51470/PLANTARCHIVES.2025.SP.ICTPAIRS-021 - a
publicly published, peer-reviewed paper. Key figures used in this
repo's worked example and defaults:

- India produces ~990 million tonnes/year of agricultural biomass;
  ~230 million tonnes/year (roughly a third) goes unutilized.
- Gasification "performs best with 10-15% moisture content" (Gao et
  al. 2023, cited within) - consistent with this repo's rice-straw
  preset's 5% as-received moisture (well within the favorable range;
  higher-moisture feedstock would need pre-drying, not modeled here).
- The paper explicitly flags limited biomass storage - especially in
  northern India - as a driver of open-field stubble burning, and
  names "exploring new bioenergy markets, like sustainable aviation
  fuels" as a stated strategy for the sector. Directly connects this
  repo to the planned `sustainable-aviation-fuel-opensource` sibling
  project - syngas quality-screened here as FT-feed-suitable is exactly
  the SAF route's expected feedstock.

## Feedstock HHV — matches published ranges

`biomass_feedstock.py`'s Channiwala & Parikh (2002) correlation gives
19.5 MJ/kg for the wood-chip preset (published range: ~18-20 MJ/kg) and
14.1 MJ/kg for the rice-straw preset (published range: ~12-15 MJ/kg,
lower than wood due to higher ash/oxygen content) - both land
comfortably inside commonly reported literature ranges, cross-checked
after the correlation was implemented, not tuned to match in advance.

## Full-chain worked example — a real scale-up finding, and a units bug caught before shipping

`examples/full_chain_worked_example.py` sizes a representative
100 t/day rice-straw gasification plant and asks how many such plants
would be needed to process India's entire ~230 Mt/year surplus: ~6,300
plants. This is reported explicitly as "illustrating the scale of the
opportunity and the logistics challenge" (the source paper's own
identified primary barrier - collection, storage, transport - not a
claim about optimal plant count or technology).

While writing this comparison, the first version of the script's own
summary print statement divided by the wrong power of ten and reported
"36.5 million tonnes/year" for a 100 t/day plant - an order-of-magnitude
error that would have been embarrassing to ship (100 t/day is
physically ~36,500 t/year, not 36.5 million). Caught by a plain sanity
check (does one plant's number make sense against the national total)
before this file was committed, not left in the repo.

## What was deliberately not modeled in this first pass

- Air-blown gasification (smaller-scale, more common in practice than
  the pure-O2 feed this module assumes) - would need an ASU sizing
  step (see the sibling coal-to-urea repo's air_separation.py, directly
  reusable) or a simpler direct-air-mixing model.
- Rate-based tar/particulate removal equipment sizing (cyclone
  diameter, scrubber packing) - gas_cleanup.py is mass-balance only.
- Downstream syngas-to-fuel conversion itself (Fischer-Tropsch,
  methanol, or biogas/ethanol routes) - reserved for sibling repos per
  the project's own scope separation.
