# `fdtd.provenance` — candidate-study provenance scaffold

Dependency-light (stdlib only) schema + **fail-closed** validator for the
evidence a 3D nonlinear Tidy3D candidate study must carry *before* a paid solve
is approved. It does **not** choose a candidate family, hold any physical
material / nonlinear parameter value, or call Tidy3D / the network / a solver.

## What a study manifest records

| Block | Fields |
| --- | --- |
| identity | `study_id`, `created_utc`, `tidy3d_version`, `candidate_family` (Astra sets this) |
| `material` | dispersion model **name**, `source_kind`, `reference`, `version`, `retrieved_utc`, `parameter_digest` (sha256 of an external file), `wavelength_range_um` |
| `nonlinear` | model type **name**, `source_kind`, `reference`, `version`, `parameter_digest`, `applies_to_medium` |
| `geometry` | `geometry_hash` (sha256), `hash_algorithm`, `source_artifact`, `units` |
| `ladders` | one per axis — `mesh`, `time`, `pml` — each with `tolerance_rel` and >= 2 ordered `rungs` |
| rung | refinement parameter (`grid_cells_per_wavelength` / `steps_per_period` / `pml_layers`), `observable`, `observable_value`, `task_id`, `flex_credit_estimated`, `flex_credit_actual` |
| `flex_credit` | `estimated_total`, `actual_total`, `estimate_source`, `estimate_task_ids`, `approved_ceiling` |
| top level | `task_ids` (all Tidy3D ids the study relies on), `evidence_paths` (local files backing the digests) |

Physical numbers never enter the manifest: they live in external artifacts
referenced by `*_digest` + an `evidence_paths` entry. Use
`python -m fdtd.provenance digest <file>` to compute a digest.

## Fail-closed rules

`validate_study` returns `ok = False` (and `require_complete()` raises) when any
required field is missing/blank/malformed or a study is internally inconsistent.
Checks, in fixed order:

`schema`, `identity`, `candidate_family`, `material.source`, `nonlinear.model`,
`geometry.hash`, `convergence.mesh`, `convergence.time`, `convergence.pml`,
`flex_credit`, `task_ids`, `evidence`.

Notable inconsistencies caught: a ladder whose refinement parameter is not
strictly increasing or whose last relative change exceeds `tolerance_rel`; a
`source_kind` outside the controlled vocabulary; a digest that is not 64 hex
chars; `nonlinear.applies_to_medium` not matching `material.name`; a rung with
`flex_credit_actual` but no `task_id`; a referenced task id absent from
`manifest.task_ids`; recorded digests with an empty `evidence_paths`; an
`evidence_paths` entry that does not exist on disk; estimated or actual cost
above `approved_ceiling`.

The report is deterministic (no timestamps) so it can be pasted into a decision
record.

## CLI

```
python -m fdtd.provenance template --out study.json     # blank form for Astra
python -m fdtd.provenance validate --manifest study.json # exit 0 iff complete
python -m fdtd.provenance validate --manifest study.json --json
python -m fdtd.provenance digest path/to/material_params.json
```

A freshly generated `template` intentionally **fails** validation — it is an
empty form, not a cleared study.

## Tests

```
python -m unittest discover -s tests/fdtd -t .
python tests/fdtd/run_tests.py
```
