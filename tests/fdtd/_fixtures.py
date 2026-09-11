"""Synthetic fixtures for the fdtd.provenance tests.

None of the values here are physical. Digests are hashes of literal placeholder
bytes, ``candidate_family`` is an obvious test string, and the "observable"
numbers are made up to exercise the convergence logic. The point is only to
drive the *shape* of a complete, self-consistent manifest so the pass path and
each fail path can be tested.
"""

from __future__ import annotations

from pathlib import Path

from fdtd.provenance import schema
from fdtd.provenance.schema import (
    CandidateStudyManifest,
    ConvergenceLadder,
    ConvergenceRung,
    FlexCreditBudget,
    GeometryProvenance,
    MaterialSource,
    NonlinearModel,
)

MAT_DIGEST = schema.sha256_text("PLACEHOLDER-material-parameters")
NL_DIGEST = schema.sha256_text("PLACEHOLDER-nonlinear-parameters")
GEO_HASH = schema.canonical_geometry_digest([{"type": "placeholder-box", "size": [1, 1, 1]}])


def write_evidence(tmp_path: Path) -> list[str]:
    """Create the three local artifacts a complete manifest references."""
    paths = []
    for stem, content in (
        ("material_params.json", "PLACEHOLDER-material-parameters"),
        ("nonlinear_params.json", "PLACEHOLDER-nonlinear-parameters"),
        ("geometry.json", '[{"type": "placeholder-box"}]'),
    ):
        p = tmp_path / stem
        p.write_text(content, encoding="utf-8")
        paths.append(str(p))
    return paths


def _ladder(dimension: str, refine, observable_values, tol: float) -> ConvergenceLadder:
    field_name = {
        "mesh": "grid_cells_per_wavelength",
        "time": "steps_per_period",
        "pml": "pml_layers",
    }[dimension]
    rungs = []
    for i, (rp, ov) in enumerate(zip(refine, observable_values)):
        kw = {field_name: rp, "label": f"{dimension}-{i}",
              "observable": "T@drop", "observable_value": ov}
        if i == len(refine) - 1:  # finest rung is "run"
            kw["task_id"] = f"task-{dimension}-{i}"
            kw["flex_credit_estimated"] = 1.0
            kw["flex_credit_actual"] = 1.1
        rungs.append(ConvergenceRung(**kw))
    return ConvergenceLadder(dimension=dimension, tolerance_rel=tol, rungs=rungs)


def complete_manifest(tmp_path: Path) -> CandidateStudyManifest:
    """A manifest that passes validate_study (evidence written under tmp_path)."""
    evidence = write_evidence(tmp_path)
    ladders = [
        _ladder("mesh", [10.0, 20.0, 30.0], [1.000, 1.020, 1.0210], 0.01),
        _ladder("time", [20.0, 40.0, 80.0], [0.500, 0.510, 0.5110], 0.01),
        _ladder("pml", [8, 12, 16], [0.300, 0.305, 0.30520], 0.01),
    ]
    rung_task_ids = [r.task_id for l in ladders for r in l.rungs if r.task_id]
    return CandidateStudyManifest(
        study_id="synthetic-study-001",
        created_utc="2026-09-10T00:00:00Z",
        candidate_family="synthetic-test-family",
        tidy3d_version="0.0.0-test",
        material=MaterialSource(
            name="SYN_MAT",
            dispersion_model="PoleResidue",
            source_kind="tidy3d_material_library",
            reference="synthetic/library#SYN_MAT",
            version="test-1",
            retrieved_utc="2026-09-10",
            parameter_digest=MAT_DIGEST,
            wavelength_range_um=[1.4, 1.7],
        ),
        nonlinear=NonlinearModel(
            model_type="KerrNonlinearity",
            source_kind="literature",
            reference="synthetic/doi",
            version="test-1",
            parameter_digest=NL_DIGEST,
            applies_to_medium="SYN_MAT",
        ),
        geometry=GeometryProvenance(
            geometry_hash=GEO_HASH,
            source_artifact=evidence[2],
            units="um",
            description="synthetic placeholder geometry",
        ),
        ladders=ladders,
        flex_credit=FlexCreditBudget(
            estimated_total=3.0,
            actual_total=3.3,
            estimate_source="synthetic",
            estimate_task_ids=["task-estimate-0"],
            approved_ceiling=10.0,
        ),
        task_ids=sorted(set(rung_task_ids + ["task-estimate-0"])),
        evidence_paths=evidence,
    )
