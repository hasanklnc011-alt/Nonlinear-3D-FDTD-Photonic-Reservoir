"""Child-process driver for ``tests/fdtd/test_linear_build.py``.

The linear translation / dry-run modules are asserted elsewhere to never pull in
``tidy3d``. To keep the test *process* that checks that assertion clean, every
test that actually builds a ``tidy3d.Simulation`` runs this driver in a fresh
subprocess instead of importing ``tidy3d`` inline.

Usage::

    echo '<plan document json>' | python tests/fdtd/_linear_build_driver.py [--no-dry-run]

It prints a single JSON object describing the built Simulation to stdout.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Running this file as a script puts its own directory on sys.path, not the repo
# root; add the root so ``fdtd`` / ``tests`` import the same way as under the
# unittest runner.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> int:
    no_dry_run = "--no-dry-run" in sys.argv[1:]
    doc = json.load(sys.stdin)

    module_had_tidy3d = "tidy3d" in sys.modules
    import fdtd.tidy3d_build.linear_build as lb

    import_pulled_tidy3d = (not module_had_tidy3d) and ("tidy3d" in sys.modules)

    from tidy3d import C_0

    built = lb.build(doc, run_dry_run=not no_dry_run)
    built_again = lb.build(doc, run_dry_run=not no_dry_run)
    sim = built.simulation

    def boundary(entry):
        return [type(entry.plus).__name__, getattr(entry.plus, "num_layers", None)]

    reparsed = type(sim).model_validate_json(built.canonical_json)

    out = {
        "sim_type": type(sim).__name__,
        "sim_module": type(sim).__module__.split(".")[0],
        "digest": built.digest,
        "digest_again": built_again.digest,
        "digest_method": lb.simulation_digest(sim),
        "reparse_digest": lb.simulation_digest(reparsed),
        "canonical_len": len(built.canonical_json),
        "tidy3d_version": built.tidy3d_version,
        "web_imported": "tidy3d.web" in sys.modules,
        "import_pulled_tidy3d": import_pulled_tidy3d,
        "n_structures": len(sim.structures),
        "structure_names": [s.name for s in sim.structures],
        "structure_permittivity": [s.medium.permittivity for s in sim.structures],
        "structure_geom": [type(s.geometry).__name__ for s in sim.structures],
        "background_permittivity": sim.medium.permittivity,
        "background_conductivity": sim.medium.conductivity,
        "size": [float(v) for v in sim.size],
        "center": [float(v) for v in sim.center],
        "run_time": sim.run_time,
        "shutoff": sim.shutoff,
        "symmetry": [int(v) for v in sim.symmetry],
        "boundary": {
            "x": boundary(sim.boundary_spec.x),
            "y": boundary(sim.boundary_spec.y),
            "z": boundary(sim.boundary_spec.z),
        },
        "sources": [[type(s).__name__, s.direction, s.name] for s in sim.sources],
        "source_freq0": [s.source_time.freq0 for s in sim.sources],
        "source_fwidth": [s.source_time.fwidth for s in sim.sources],
        "monitors": [[type(m).__name__, m.name, len(m.freqs)] for m in sim.monitors],
        "monitor_lambda_bounds_um": [
            [min(C_0 / f for f in m.freqs) if len(m.freqs) else None,
             max(C_0 / f for f in m.freqs) if len(m.freqs) else None]
            for m in sim.monitors
        ],
        "grid_type": type(sim.grid_spec.grid_x).__name__,
    }
    json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
