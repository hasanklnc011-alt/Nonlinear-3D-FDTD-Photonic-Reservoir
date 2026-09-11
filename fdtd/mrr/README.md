# `fdtd.mrr` — silicon microring candidate study-builder

Local, dependency-light scaffold that turns caller-supplied **geometry** and
**simulation configuration** into a deterministic, hashable description and
assembles an *intentionally incomplete*
[`CandidateStudyManifest`](../provenance/README.md) for the Astra evidence /
maturity gate.

## Boundaries (mirrored by `tests/fdtd/test_mrr.py`)

- **No physical parameter values.** Silicon `n` / `k` / `n2` / TPA / `chi(3)`
  never appear here. Material and nonlinear evidence is passed in as
  `MaterialSource` / `NonlinearModel` records that carry only a reference,
  version, source kind, and the **SHA-256 digest of an external artifact**. If
  that evidence is missing or malformed the builder raises `MissingEvidenceError`
  (fail closed).
- **No candidate-family choice.** `candidate_family` is left `None` for Astra.
- **No discretisation choice.** `SimulationConfig` holds no grid, steps/period,
  PML layer count, run time, or tolerance. `build_manifest()` emits the
  `mesh` / `time` / `pml` ladders **empty** and `flex_credit` **blank**.
- **No cloud.** Nothing imports Tidy3D, opens a socket, or submits / downloads /
  runs a task. `task_ids` is always empty.

## Modules

| Module | What it holds |
| --- | --- |
| `geometry.py` | `RingResonatorGeometry` — ring radius, waveguide width/thickness, bus width, coupling gap, bus length, cladding / BOX / substrate thickness, domain padding, `add_drop` flag, and four **medium labels** (names, not constants). `.validate()`, `.to_document()`, `.digest()` (canonical SHA-256). |
| `config.py` | `SimulationConfig` — wavelength band, boundary **type names**, symmetry, source / monitor **names**. `.validate()`, `.to_document()`, `.digest()`. `mesh_is_deferred` / `run_time_is_deferred` are always `True`. |
| `study.py` | `MicroringStudyBuilder` — `.geometry_digest()`, `.config_digest()`, `.evidence_problems()`, `.require_evidence()`, `.build_manifest()`. `StudyIdentity`, `MissingEvidenceError`. |
| `linear_sim.py` | `LinearSimulationTranslator` — turns a **fully-evidenced** study input (geometry + config + an explicit `LinearMaterialTable` + `ExcitationSpec` + `DiscretizationSpec` + a background medium label) into a `LinearSimulationPlan`: a canonical, hashable dict that maps 1:1 onto `tidy3d.Simulation(...)` for the **linear** solve. Fails closed (`MissingLinearEvidenceError`) if any linear value or dimension is absent; rejects any `nonlinear` block (`TranslationError`). |
| `linear_dryrun.py` | `dry_run(plan)` — deterministic, fail-closed **local** validator of a linear plan document: schema, linear-only, no-cloud, domain fit, per-medium evidence, wavelength-band consistency, grid / run time, boundaries, symmetry, ports, provenance hashes. |
| `__main__.py` | `python -m fdtd.mrr plan --input bundle.json` / `python -m fdtd.mrr dryrun --plan plan.json`. No Tidy3D, no network. |

### Linear translation layer boundaries (mirrored by `tests/fdtd/test_linear_sim.py`)

- **Linear only.** No `KerrNonlinearity` / `TwoPhotonAbsorption` / `chi(3)` / free-carrier term is emitted or accepted; a bundle with a `nonlinear` (or `kerr` / `tpa` / `chi3` / `free_carrier`) key is rejected.
- **Nothing invented.** Every linear permittivity + conductivity and every geometry dimension must be supplied; each medium value must carry a SHA-256 `evidence_digest`, an `evidence_reference` and a `wavelength_range_um`. The discretisation (grid steps/λ, grid λ, `run_time_seconds`, shutoff, boundary layers) and the excitation band are **caller-supplied** — this layer does not choose a mesh, it only assembles and fails closed when one is absent.
- **No physical constant is hard-coded.** The plan stays in the caller's units (µm, s, relative permittivity, S/m); conversion to Tidy3D `freq0` / `fwidth` uses Tidy3D's own `C_0` and is left to the code that instantiates the real object.
- **No cloud.** No import of `tidy3d` / sockets; the plan lists no task id and no FlexCredit number.

### Linear plan usage sketch

```python
from fdtd.mrr import LinearSimulationTranslator

bundle = {
    "identity": {"study_id": "mrr-lin-001", "created_utc": "..."},
    "geometry": { ...RingResonatorGeometry fields... },
    "config":   { ...SimulationConfig fields... },
    "materials": [
        {"medium_label": "Si", "model": "non_dispersive",
         "relative_permittivity": ..., "conductivity": ...,
         "evidence_digest": "<sha256 of the external value file>",
         "evidence_reference": "...", "wavelength_range_um": [..., ...]},
        # ... one per geometry medium label + the background label
    ],
    "background_medium_label": "SiO2",
    "excitation": {"center_wavelength_um": ..., "bandwidth_wavelength_um": ..., "num_freqs": ...},
    "discretization": {"grid_min_steps_per_wavelength": ..., "grid_wavelength_um": ...,
                       "run_time_seconds": ..., "field_decay_shutoff": ..., "boundary_num_layers": ...},
}

plan = LinearSimulationTranslator.from_bundle(bundle).translate()  # MissingLinearEvidenceError if incomplete
plan.digest()          # deterministic SHA-256 of the canonical plan document
plan.dry_run().ok      # True only when the plan is complete + consistent + linear + cloud-free
```

## Determinism

`RingResonatorGeometry.digest()` and `SimulationConfig.digest()` canonicalise
their document (sorted keys, compact separators) before hashing, so the digest is
independent of field / kwarg ordering and changes iff a value changes.

## Usage sketch

```python
from fdtd.mrr import (
    RingResonatorGeometry, SimulationConfig, MicroringStudyBuilder, StudyIdentity,
)
from fdtd.provenance.schema import MaterialSource, NonlinearModel

geom = RingResonatorGeometry(
    ring_outer_radius_um=..., waveguide_width_um=..., waveguide_thickness_um=...,
    bus_waveguide_width_um=..., coupling_gap_um=..., bus_length_um=...,
    cladding_thickness_um=..., box_thickness_um=..., substrate_thickness_um=...,
    domain_padding_um=..., add_drop=True,
    core_medium="Si", cladding_medium="SiO2", box_medium="SiO2", substrate_medium="Si",
).validate()

cfg = SimulationConfig(
    wavelength_range_um=[..., ...],
    boundary_types={"x": "pml", "y": "pml", "z": "pml"},
    symmetry=[0, 0, 0],
    sources=["mode:bus_through:in"],
    monitors=["flux:bus_through:out", "flux:bus_drop:out"],
).validate()

# material / nonlinear come from OUTSIDE this repo, digest of an external file:
material = MaterialSource(name="Si", dispersion_model="PoleResidue",
                          source_kind="tidy3d_material_library", reference="...",
                          version="...", retrieved_utc="...",
                          parameter_digest="<sha256 of the external params file>",
                          wavelength_range_um=[..., ...])
nonlinear = NonlinearModel(model_type="KerrNonlinearity", source_kind="literature",
                           reference="...", version="...",
                           parameter_digest="<sha256 of the external params file>",
                           applies_to_medium="Si")

builder = MicroringStudyBuilder(
    identity=StudyIdentity(study_id="mrr-001", created_utc="2026-09-10T00:00:00Z"),
    geometry=geom, config=cfg, material=material, nonlinear=nonlinear,
    evidence_paths=["/abs/path/si_params.json", "/abs/path/kerr_params.json"],
)
manifest = builder.build_manifest()          # raises MissingEvidenceError if evidence incomplete
```

`validate_study(manifest)` then returns `ok = False` until Astra fills the
candidate family, ladders, and cost budget — that is the point of the scaffold.

## Tests

```
python -m unittest discover -s tests/fdtd -t .
python -m unittest tests.fdtd.test_mrr -v
python -m unittest tests.fdtd.test_linear_sim -v
```
