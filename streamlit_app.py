"""Interactive biomass gasification to syngas conceptual sizing tool.

Run with: streamlit run streamlit_app.py
"""
from __future__ import annotations

import streamlit as st

from biomass_to_syngas.biomass_feedstock import TYPICAL_RICE_STRAW, TYPICAL_WOOD_CHIPS, BiomassAnalysis
from biomass_to_syngas.gas_cleanup import clean_syngas
from biomass_to_syngas.gasifier import TYPICAL_TAR_YIELD_G_NM3, gasify_biomass
from biomass_to_syngas.syngas_quality import evaluate_syngas_quality

st.set_page_config(page_title="Biomass-to-Syngas Conceptual Sizing", layout="wide")
st.title("Biomass Gasification to Syngas (open-source)")
st.caption(
    "Independent open-source conceptual sizing using public-domain correlations "
    "(Higman & van der Burgt, Channiwala & Parikh 2002, NREL tar report) and CoolProp "
    "thermodynamics. Not derived from any proprietary vendor/client data. Motivated by "
    "India's ~230 Mt/year unutilized agricultural biomass surplus and the stubble-"
    "burning crisis it drives - see README.md and docs/VALIDATION.md."
)

tab_feedstock, tab_gasifier, tab_cleanup, tab_quality, tab_chain = st.tabs([
    "Feedstock", "Gasifier", "Gas Cleanup", "Syngas Quality", "Full Chain",
])

with tab_feedstock:
    st.header("Biomass feedstock characterization")
    preset = st.radio("Preset", ["Rice/paddy straw (India, ash ~14%)", "Wood chips (ash ~1.6%)"])
    biomass = TYPICAL_RICE_STRAW if "straw" in preset else TYPICAL_WOOD_CHIPS
    colA, colB = st.columns(2)
    colA.metric("HHV", f"{biomass.hhv_MJ_kg():.1f} MJ/kg")
    colB.metric("LHV", f"{biomass.lhv_MJ_kg():.1f} MJ/kg")
    st.write({"C": biomass.carbon, "H": biomass.hydrogen, "O": biomass.oxygen,
              "N": biomass.nitrogen, "S": biomass.sulfur, "ash": biomass.ash, "moisture": biomass.moisture})
    st.session_state["biomass"] = biomass

with tab_gasifier:
    st.header("Gasifier")
    st.caption("Elemental balance + water-gas-shift equilibrium quench (Higman & van der Burgt).")
    biomass = st.session_state.get("biomass", TYPICAL_RICE_STRAW)
    c1, c2, c3 = st.columns(3)
    with c1:
        feed_flow = st.number_input("Biomass mass flow (kg/s)", min_value=0.01, value=1.16)
    with c2:
        o2_ratio = st.number_input("O2:biomass mass ratio", min_value=0.05, value=0.22)
    with c3:
        steam_ratio = st.number_input("Steam:biomass mass ratio", min_value=0.0, value=0.40)
    c1, c2, c3 = st.columns(3)
    with c1:
        gasifier_T_C = st.number_input("Gasifier temperature (°C)", value=850.0)
    with c2:
        carbon_conv = st.slider("Carbon conversion", 0.70, 0.99, 0.85)
    with c3:
        gasifier_type = st.selectbox("Gasifier type (sets tar yield)", list(TYPICAL_TAR_YIELD_G_NM3.keys()), index=2)

    if st.button("Run gasifier", type="primary"):
        try:
            g = gasify_biomass(biomass, feed_flow, o2_ratio, steam_ratio, gasifier_T_C + 273.15, carbon_conv, gasifier_type)
            st.session_state["gasifier_result"] = g
            colA, colB, colC = st.columns(3)
            colA.metric("Syngas flow", f"{g.syngas_molar_flow_mol_s:.2f} mol/s")
            colB.metric("Cold gas efficiency", f"{g.cold_gas_efficiency*100:.1f}%")
            colC.metric("Tar yield", f"{g.tar_mass_flow_kg_s*1000:.2f} g/s")
            st.write({k: f"{v*100:.2f}%" for k, v in g.syngas_composition_mole_frac.items()})
        except ValueError as e:
            st.error(str(e))

with tab_cleanup:
    st.header("Gas cleanup (tar + particulate)")
    if "gasifier_result" not in st.session_state:
        st.info("Run the Gasifier tab first.")
    else:
        g = st.session_state["gasifier_result"]
        c1, c2 = st.columns(2)
        with c1:
            particulate_frac = st.number_input("Illustrative particulate loading (fraction of syngas mass)", min_value=0.0, value=0.02)
        with c2:
            st.metric("Tar in (from gasifier)", f"{g.tar_mass_flow_kg_s*1000:.2f} g/s")
        c1, c2 = st.columns(2)
        with c1:
            tar_removal = st.slider("Tar removal fraction", 0.80, 0.999, 0.97)
        with c2:
            particulate_removal = st.slider("Particulate removal fraction", 0.80, 0.999, 0.98)
        if st.button("Run cleanup", type="primary"):
            cleanup = clean_syngas(g.tar_mass_flow_kg_s, g.syngas_mass_flow_kg_s * particulate_frac, tar_removal, particulate_removal)
            colA, colB = st.columns(2)
            colA.metric("Tar remaining", f"{cleanup.cleaned_tar_mass_flow_kg_s*1000:.3f} g/s")
            colB.metric("Particulate remaining", f"{cleanup.cleaned_particulate_mass_flow_kg_s*1000:.3f} g/s")

with tab_quality:
    st.header("Syngas quality & downstream-use screening")
    if "gasifier_result" not in st.session_state:
        st.info("Run the Gasifier tab first.")
    else:
        g = st.session_state["gasifier_result"]
        quality = evaluate_syngas_quality(g.syngas_composition_mole_frac)
        colA, colB, colC = st.columns(3)
        colA.metric("H2:CO ratio", f"{quality.h2_to_co_molar_ratio:.2f}:1")
        colB.metric("LHV", f"{quality.lhv_MJ_per_Nm3:.2f} MJ/Nm3")
        colC.metric("Inert fraction", f"{quality.inert_mole_fraction*100:.1f}%")
        st.success(f"**Recommended: {quality.recommended_use}**")
        st.write(quality.rationale)

with tab_chain:
    st.header("Full chain: biomass → syngas")
    st.caption(
        "Mirrors examples/full_chain_worked_example.py - rice straw → gasifier → cleanup → "
        "quality screening, with a scale-up comparison against India's real ~230 Mt/year "
        "surplus-biomass estimate. Use the tabs above interactively, or run the example "
        "script from a terminal for the full printed trace."
    )

st.divider()
st.caption(
    "**Disclaimer**: this tool implements textbook/public-domain conceptual sizing "
    "methods for early-stage screening only. It is not a substitute for a rigorous "
    "process simulator or vendor-certified equipment data for detailed design."
)
