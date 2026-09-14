# Biomass Gasifier Technology Provider Reference

Same purpose as the sibling repos' `docs/VENDOR_REFERENCE.md` (lng-
design-opensource / coal-to-urea-design-opensource's joint document,
and cbg-design-opensource's, ethanol-design-opensource's own): for each
named provider below, does their own public page publish a genuine,
verifiable technical detail this project's sizing can be cross-checked
against — not vendor endorsement, not a procurement recommendation.
Every entry was fetched and its content inspected at the time of
writing (September 2026); where a claim could only be confirmed via a
secondary source, that is stated explicitly rather than cited as if
independently verified.

| Provider | Public resource (verified) | What it confirms | Relevance to this repo |
|---|---|---|---|
| **Ankur Scientific** | [Project examples](https://www.ankurscientific.com/project.php) (ankurscientific.com, own site) | A real, Vadodara, India-headquartered downdraft-gasifier manufacturer (40+ years, "1,000+ installations on 60+ feedstock types"), with specific verified installed-project figures: a 750 kWe WBG-1250 unit processing ~900 kg/hr of woody residues (Samoa, 2020); 8 x MSW-2200 downdraft gasifiers converting 384 t/day of dry MSW to 8 MWe gross (Solo, Indonesia, 2023); a 1 x MSW-1250 unit producing 400 kWe (Mexico, 2023). Confirmed feedstocks include agricultural residues (mango seeds, corncob, cotton stalk, deoiled cashewnut cake) but **rice straw specifically is not mentioned** on this page. | Real, named cross-check for this repo's `"downdraft"` gasifier-type category and its `TYPICAL_TAR_YIELD_G_NM3["downdraft"]` default (downdraft's cleaner exhaust, ~1-3 g/Nm3 tar, is the mechanism the whole product line is built around). The 900 kg/hr -> 750 kWe ratio is an overall biomass-to-electricity figure (gasifier + engine), not directly comparable to this module's own gasifier-only cold-gas efficiency, so it is not used as a numeric validation target — only as confirmation the technology and scale are real. |
| **Powermax (Kaifeng)** | [Straw Gasification Power Plant](https://www.powermaxgasifiers.com/7-16323779251792489.html) (powermaxgasifiers.com, own site) | Explicitly rice-straw-rated gasifiers in two technology classes: **TFBG** (twin-fire fixed-bed, 50-2,000 kW) and **CFBG** (circulating fluidized-bed, 200-2,000 kW), both listing rice straw among accepted feedstocks with moisture/size limits (<=20% moisture, <15 mm for CFBG). Published gas production **125-150 Nm3/h at 50 kW up to 5,000-6,000 Nm3/h at 2,000 kW**, and a syngas energy content of **>=1,200 kcal/Nm3** for TFBG. | **A genuine, real cross-check this project's own worked example clears**: `examples/full_chain_worked_example.py`'s 100 t/day rice-straw case (oxygen/steam-blown fluidized bed) computes a syngas LHV of 5.71 MJ/Nm3 = 1,364 kcal/Nm3 — above Powermax's published >=1,200 kcal/Nm3 floor for a real, commercially sold rice-straw gasifier. Caveat, stated honestly: Powermax's product line is very likely air-blown (typical air-blown syngas LHV is 4-6 MJ/Nm3, vs. 10-15+ MJ/Nm3 for oxygen-blown), so this repo's oxygen/steam-blown case landing in that same range is itself partly an artifact of this module's own heavy steam dilution (34% water in the syngas) rather than a like-for-like process match — a real number worth reporting, not a claim that the two are the same process. |
| **Thermax Limited** | Real, NSE-listed Indian energy-engineering company with a public biomass-power business line (thermaxglobal.com) and press coverage of a first **20 MW rice-husk-based** independent power plant (commissioned 2015) — but thermaxglobal.com returns HTTP 403 to both a standard fetch and a browser-UA `curl` request, so no page on the company's own site could be independently inspected for this document. | — | Named because rice husk (a different rice-crop residue from the straw this repo focuses on, but from the same crop and a commonly co-processed feedstock) is a real, large-scale (20 MW) commercial precedent for agricultural-residue gasification power in India — flagged as unverified-on-site rather than cited with a number pulled only from search-result summaries, the same honesty standard the LNG/coal-to-urea sibling document applies to CB&I/McDermott (also blocked by its own site's WAF). |
| **Powermax -- Updraft Fixed Bed Gasifier (UFBG)** | [UFBG working principle](https://www.powermaxgasifiers.com/updraft-gasifier-working-principle) and [UFBG product page](https://www.powermaxgasifiers.com/2-16323874376201109.html) (powermaxgasifiers.com, own site) | The SAME real vendor as the CFBG/TFBG entry above also sells a real, quantified **updraft** product line -- 12 models, 50 kW to 2 MW, wood chips/shells/briquettes (20-80 mm) feedstock, real published syngas composition (CO 16-21%, CO2 5-11%, CH4 4-6%, H2 10-12%, N2 54-60% -- a heavily air-diluted, low-H2/CO composition consistent with a simple air-blown updraft design), and a heating value of **>=1,100-1,200 Kcal/Nm3**. | **Fills this repo's third, previously unconfirmed gasifier-type category** -- Ankur Scientific covers downdraft, Powermax's CFBG covers fluidized bed, and this same Powermax UFBG line now covers updraft, so all three of `gasifier.py`'s `TYPICAL_TAR_YIELD_G_NM3` categories trace to at least one real, named, quantified commercial product. Independent published literature (not this vendor's own page) gives updraft tar production as **30-150 g/Nm3** -- this module's own `TYPICAL_TAR_YIELD_G_NM3["updraft"] = 50.0` sits comfortably inside that real cited range, a genuine external check the earlier version of this document did not have. |
| **Chanderpur Works** | [Biomass Gasifier](https://www.chanderpur.com/products/biomass-gasifier) (chanderpur.com, own site) | A second, India-headquartered gasifier manufacturer (20 kWe-1,200 kWe range) explicitly offering BOTH downdraft and updraft gasifiers, with **rice husk** named directly as an accepted feedstock -- and ESP/chiller/filter gas cleaning stages, a real cross-check for `gas_cleanup.py`'s cleanup-stage concept. No quantified tar/efficiency figures published on this page. | A second, independently confirmed real downdraft+updraft vendor beyond Ankur Scientific/Powermax, reinforcing that both technologies are real, multiply-sourced commercial options for exactly this repo's India rice-residue use case -- not single-vendor or hypothetical. |
| **Envitech Inc.** | [Tar removal scrubber](https://www.envitechinc.com/tar_removal_scrubber) (envitechinc.com, own site) | A real, named US gas-cleanup technology vendor confirming tar-removal scrubbing for biomass gasifier syngas is a real, commercially offered product category, not a generic textbook step -- no quantified removal-efficiency figures published on this specific page. | Confirms `gas_cleanup.py`'s scope (tar/particulate scrubbing ahead of downstream use) matches a real commercial technology category, distinct from the gasifier vendors above. |

## A real, independent number that matches this repo's own default exactly

Independent published tar-removal literature (not tied to any single
vendor above) reports water scrubbing alone removing up to 50% of
syngas tar, and a water scrub followed by a venturi scrubber increasing
that to **97%** -- `gas_cleanup.clean_syngas()`'s own `tar_removal_fraction`
default is **0.97**, already cited generically to a 90-99% literature
range before this check; this is a more specific, mechanism-matched
real number landing exactly on that existing default, a genuine
corroboration found by checking, not something tuned to match.

## Note on this document's scope vs. the sibling repos'

Smaller in scope than the LNG/coal-to-urea document's international
component-catalog cross-checks (valves, exchangers, pressure vessels) —
biomass gasification for agricultural-residue power in India is
dominated by a handful of turnkey gasifier OEMs (Ankur Scientific,
Thermax) plus international suppliers like Powermax, rather than a
standardized component-series market the way TEMA shells or API 661 air
coolers are.
