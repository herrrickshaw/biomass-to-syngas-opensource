"""Smoke test for the CLI entry point: the worked example must run and
print the pinned headline figures."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "examples" / "full_chain_worked_example.py"


def test_worked_example_runs_and_prints_reference_figures():
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=REPO, check=True).stdout
    assert "Feed: rice/paddy straw, 100 t/day (1.157 kg/s), HHV 14.1 MJ/kg" in out
    assert "87.43 mol/s syngas, CGE 75.8%, tar yield 29.40 g/s" in out
    assert "tar reduced to 0.882 g/s (from 29.40 g/s), particulate reduced to 0.66 g/s" in out
    assert "H2:CO = 1.73:1, LHV = 5.71 MJ/Nm3, inert fraction 50.2%" in out
    assert "would need ~6,297 plants of this scale" in out
