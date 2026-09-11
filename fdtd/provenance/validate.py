"""Fail-closed validation of a :class:`~fdtd.provenance.schema.CandidateStudyManifest`.

The validator never reaches the network and never runs a solve. It answers one
question: *does this study carry every piece of evidence the project requires
before a paid 3D nonlinear FDTD solve can be approved?* If anything required is
missing, blank, malformed, or internally inconsistent, the corresponding check
is a ``FAIL`` and :attr:`ValidationReport.ok` is ``False``.

Check order is fixed and the report is deterministic (no timestamps, identical
across runs) so it can be diffed and pasted into a decision record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from . import schema
from .schema import (
    CandidateStudyManifest,
    LADDER_DIMENSIONS,
    SCHEMA_ID,
    SOURCE_KINDS,
    is_finite_number,
    looks_like_sha256,
)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_INFO = "INFO"


class StudyProvenanceIncomplete(RuntimeError):
    """Raised by :meth:`ValidationReport.require_complete` when validation fails."""


@dataclass
class Check:
    name: str
    status: str
    summary: str
    details: list[str] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return self.status == STATUS_FAIL

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "summary": self.summary,
            "details": list(self.details),
        }


@dataclass
class ValidationReport:
    checks: list[Check]

    @property
    def failed(self) -> list[Check]:
        return [c for c in self.checks if c.failed]

    @property
    def ok(self) -> bool:
        return not self.failed

    def require_complete(self) -> None:
        if not self.ok:
            names = ", ".join(c.name for c in self.failed)
            raise StudyProvenanceIncomplete(
                f"candidate-study provenance incomplete: {names}"
            )

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "n_checks": len(self.checks),
            "n_failed": len(self.failed),
            "checks": [c.to_dict() for c in self.checks],
        }

    def format_text(self) -> str:
        lines: list[str] = []
        for c in self.checks:
            lines.append(f"[{c.status}] {c.name}: {c.summary}")
            lines.extend(f"       {d}" for d in c.details)
        lines.append("")
        if self.ok:
            lines.append(f"STUDY PROVENANCE OK ({len(self.checks)} checks)")
        else:
            names = ", ".join(c.name for c in self.failed)
            lines.append(
                f"STUDY PROVENANCE INCOMPLETE ({len(self.failed)} failing: {names})"
            )
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _blank(value) -> bool:
    return schema._blank(value)


def _require_fields(obj, names: Iterable[str], prefix: str) -> list[str]:
    return [f"{prefix}.{n} is missing" for n in names if _blank(getattr(obj, n, None))]


# --------------------------------------------------------------------------- #
# individual checks
# --------------------------------------------------------------------------- #
def _check_schema(m: CandidateStudyManifest) -> Check:
    name = "schema"
    if m.schema != SCHEMA_ID:
        return Check(name, STATUS_FAIL, f"schema {m.schema!r} != {SCHEMA_ID!r}")
    return Check(name, STATUS_PASS, f"schema is {SCHEMA_ID}")


def _check_identity(m: CandidateStudyManifest) -> Check:
    name = "identity"
    missing = _require_fields(m, ("study_id", "created_utc", "tidy3d_version"), "manifest")
    details = [
        f"study_id = {m.study_id!r}",
        f"created_utc = {m.created_utc!r}",
        f"tidy3d_version = {m.tidy3d_version!r}",
    ]
    if missing:
        return Check(name, STATUS_FAIL, "; ".join(missing), details)
    return Check(name, STATUS_PASS, "study id, timestamp and Tidy3D version recorded", details)


def _check_candidate_family(m: CandidateStudyManifest) -> Check:
    name = "candidate_family"
    note = "the candidate family is an Astra architecture decision, not Claude's"
    if _blank(m.candidate_family):
        return Check(name, STATUS_FAIL, "candidate_family is not set", [note])
    return Check(name, STATUS_PASS, f"candidate_family = {m.candidate_family!r}", [note])


def _check_source_kind(value, prefix: str, out: list[str]) -> bool:
    if _blank(value):
        out.append(f"{prefix}.source_kind is missing")
        return False
    if value not in SOURCE_KINDS:
        out.append(f"{prefix}.source_kind {value!r} not in {list(SOURCE_KINDS)}")
        return False
    return True


def _check_material(m: CandidateStudyManifest) -> Check:
    name = "material.source"
    mat = m.material
    if mat is None:
        return Check(name, STATUS_FAIL, "material block is absent")

    problems = _require_fields(
        mat,
        ("name", "dispersion_model", "reference", "version",
         "retrieved_utc", "parameter_digest", "wavelength_range_um"),
        "material",
    )
    _check_source_kind(mat.source_kind, "material", problems)

    if not _blank(mat.parameter_digest) and not looks_like_sha256(mat.parameter_digest):
        problems.append(f"material.parameter_digest {mat.parameter_digest!r} is not a sha256 hex digest")

    wr = mat.wavelength_range_um
    if not _blank(wr):
        if (not isinstance(wr, (list, tuple)) or len(wr) != 2
                or not all(is_finite_number(x) and x > 0 for x in wr) or wr[0] >= wr[1]):
            problems.append(f"material.wavelength_range_um {wr!r} must be [lo, hi] with 0 < lo < hi")

    details = [
        f"name = {mat.name!r}", f"dispersion_model = {mat.dispersion_model!r}",
        f"source_kind = {mat.source_kind!r}", f"version = {mat.version!r}",
        f"parameter_digest = {mat.parameter_digest!r}",
    ]
    if problems:
        return Check(name, STATUS_FAIL, "; ".join(problems), details)
    return Check(name, STATUS_PASS, f"{mat.name} / {mat.dispersion_model} from {mat.source_kind}", details)


def _check_nonlinear(m: CandidateStudyManifest) -> Check:
    name = "nonlinear.model"
    nl = m.nonlinear
    if nl is None:
        return Check(name, STATUS_FAIL, "nonlinear block is absent")

    problems = _require_fields(
        nl, ("model_type", "reference", "version", "parameter_digest", "applies_to_medium"), "nonlinear"
    )
    _check_source_kind(nl.source_kind, "nonlinear", problems)

    if not _blank(nl.parameter_digest) and not looks_like_sha256(nl.parameter_digest):
        problems.append(f"nonlinear.parameter_digest {nl.parameter_digest!r} is not a sha256 hex digest")

    mat_name = getattr(m.material, "name", None)
    if not _blank(nl.applies_to_medium) and not _blank(mat_name) and nl.applies_to_medium != mat_name:
        problems.append(
            f"nonlinear.applies_to_medium {nl.applies_to_medium!r} != material.name {mat_name!r}"
        )

    details = [
        f"model_type = {nl.model_type!r}", f"source_kind = {nl.source_kind!r}",
        f"applies_to_medium = {nl.applies_to_medium!r}", f"parameter_digest = {nl.parameter_digest!r}",
    ]
    if problems:
        return Check(name, STATUS_FAIL, "; ".join(problems), details)
    return Check(name, STATUS_PASS, f"{nl.model_type} on {nl.applies_to_medium} from {nl.source_kind}", details)


def _check_geometry(m: CandidateStudyManifest) -> Check:
    name = "geometry.hash"
    geo = m.geometry
    if geo is None:
        return Check(name, STATUS_FAIL, "geometry block is absent")

    problems = _require_fields(geo, ("geometry_hash", "source_artifact", "units"), "geometry")
    if geo.hash_algorithm != "sha256":
        problems.append(f"geometry.hash_algorithm {geo.hash_algorithm!r} != 'sha256'")
    if not _blank(geo.geometry_hash) and not looks_like_sha256(geo.geometry_hash):
        problems.append(f"geometry.geometry_hash {geo.geometry_hash!r} is not a sha256 hex digest")

    details = [
        f"geometry_hash = {geo.geometry_hash!r}",
        f"source_artifact = {geo.source_artifact!r}",
        f"units = {geo.units!r}",
    ]
    if problems:
        return Check(name, STATUS_FAIL, "; ".join(problems), details)
    return Check(name, STATUS_PASS, f"geometry hashed ({geo.geometry_hash[:16]}...)", details)


def _check_ladder(ladder, dimension: str) -> Check:
    name = f"convergence.{dimension}"
    if ladder is None:
        return Check(name, STATUS_FAIL, f"no ladder for the {dimension!r} axis")

    problems: list[str] = []
    if not is_finite_number(ladder.tolerance_rel) or ladder.tolerance_rel <= 0:
        problems.append(f"tolerance_rel {ladder.tolerance_rel!r} must be a positive number")

    rungs = ladder.rungs or []
    if len(rungs) < 2:
        problems.append(f"needs >= 2 rungs, has {len(rungs)}")

    for i, r in enumerate(rungs):
        if _blank(r.observable) or not is_finite_number(r.observable_value):
            problems.append(f"rung {i}: observable / observable_value missing")
        if r.refinement_parameter(dimension) is None or not is_finite_number(r.refinement_parameter(dimension)):
            problems.append(f"rung {i}: {dimension} refinement parameter missing")
        if r.flex_credit_actual is not None and _blank(r.task_id):
            problems.append(f"rung {i}: has flex_credit_actual but no task_id")

    details = [
        f"rungs = {len(rungs)}",
        f"tolerance_rel = {ladder.tolerance_rel!r}",
        f"monotonic_refinement = {ladder.refinement_is_monotonic()}",
        f"last_relative_change = {ladder.last_relative_change()!r}",
    ]

    if problems:
        return Check(name, STATUS_FAIL, "; ".join(problems), details)

    if not ladder.refinement_is_monotonic():
        return Check(name, STATUS_FAIL, "refinement parameter is not strictly increasing", details)

    if not ladder.converged():
        return Check(
            name, STATUS_FAIL,
            f"not converged: last change {ladder.last_relative_change():.3g} > tolerance {ladder.tolerance_rel:.3g}",
            details,
        )

    return Check(
        name, STATUS_PASS,
        f"converged: last change {ladder.last_relative_change():.3g} <= tolerance {ladder.tolerance_rel:.3g}",
        details,
    )


def _check_flex_credit(m: CandidateStudyManifest) -> Check:
    name = "flex_credit"
    fc = m.flex_credit
    if fc is None:
        return Check(name, STATUS_FAIL, "flex_credit block is absent")

    problems: list[str] = []
    if not is_finite_number(fc.estimated_total) or fc.estimated_total <= 0:
        problems.append(f"estimated_total {fc.estimated_total!r} must be a positive number")
    if _blank(fc.estimate_source):
        problems.append("estimate_source is missing")
    if not is_finite_number(fc.approved_ceiling) or fc.approved_ceiling <= 0:
        problems.append(f"approved_ceiling {fc.approved_ceiling!r} must be a positive number (Astra sets it)")
    if fc.actual_total is not None and not (is_finite_number(fc.actual_total) and fc.actual_total >= 0):
        problems.append(f"actual_total {fc.actual_total!r} must be a non-negative number when present")

    details = [
        f"estimated_total = {fc.estimated_total!r}",
        f"actual_total = {fc.actual_total!r}",
        f"approved_ceiling = {fc.approved_ceiling!r}",
        f"estimate_source = {fc.estimate_source!r}",
        f"within_ceiling = {fc.within_ceiling()!r}",
    ]

    if problems:
        return Check(name, STATUS_FAIL, "; ".join(problems), details)

    if fc.within_ceiling() is False:
        cost = fc.actual_total if is_finite_number(fc.actual_total) else fc.estimated_total
        return Check(name, STATUS_FAIL,
                     f"cost {cost} exceeds approved ceiling {fc.approved_ceiling}", details)

    if fc.actual_total is None:
        return Check(name, STATUS_INFO,
                     f"estimate {fc.estimated_total} within ceiling {fc.approved_ceiling}; "
                     "actual not yet recorded", details)
    return Check(name, STATUS_PASS,
                 f"actual {fc.actual_total} within ceiling {fc.approved_ceiling}", details)


def _collect_task_ids(m: CandidateStudyManifest) -> tuple[set[str], set[str]]:
    """Return (task ids referenced by sub-records, task ids in manifest.task_ids)."""
    referenced: set[str] = set()
    for ladder in m.ladders or []:
        for r in ladder.rungs or []:
            if not _blank(r.task_id):
                referenced.add(r.task_id)
    if m.flex_credit is not None:
        referenced.update(t for t in (m.flex_credit.estimate_task_ids or []) if not _blank(t))
    declared = {t for t in (m.task_ids or []) if not _blank(t)}
    return referenced, declared


def _check_task_ids(m: CandidateStudyManifest) -> Check:
    name = "task_ids"
    referenced, declared = _collect_task_ids(m)
    details = [
        f"declared = {sorted(declared)}",
        f"referenced_by_rungs_and_estimates = {sorted(referenced)}",
    ]

    bad_type = [t for t in (m.task_ids or []) if not isinstance(t, str) or _blank(t)]
    if bad_type:
        return Check(name, STATUS_FAIL, f"manifest.task_ids has blank / non-string entries: {bad_type!r}", details)

    orphan = referenced - declared
    if orphan:
        return Check(name, STATUS_FAIL,
                     f"task id(s) used but not listed in manifest.task_ids: {sorted(orphan)}", details)

    has_actual = any(
        r.flex_credit_actual is not None
        for ladder in (m.ladders or []) for r in (ladder.rungs or [])
    ) or (m.flex_credit is not None and m.flex_credit.actual_total is not None)

    if not declared:
        status = STATUS_FAIL if has_actual else STATUS_INFO
        msg = ("actual results are recorded but no task ids are listed"
               if has_actual else "no task ids yet (nothing submitted) - expected pre-solve")
        return Check(name, status, msg, details)

    return Check(name, STATUS_PASS, f"{len(declared)} task id(s), all references resolved", details)


def _check_evidence(m: CandidateStudyManifest) -> Check:
    name = "evidence"
    paths = [p for p in (m.evidence_paths or []) if not _blank(p)]
    digests = {
        "material.parameter_digest": getattr(m.material, "parameter_digest", None),
        "nonlinear.parameter_digest": getattr(m.nonlinear, "parameter_digest", None),
        "geometry.geometry_hash": getattr(m.geometry, "geometry_hash", None),
    }
    present_digests = [k for k, v in digests.items() if not _blank(v)]
    details = [
        f"evidence_paths = {paths}",
        f"digests_present = {present_digests}",
    ]

    if present_digests and not paths:
        return Check(name, STATUS_FAIL,
                     "digests are recorded but evidence_paths is empty - "
                     "the artifacts backing the digests are not identified", details)

    missing_on_disk = [p for p in paths if not Path(p).exists()]
    if missing_on_disk:
        details.append(f"not_found_locally = {missing_on_disk}")
        return Check(name, STATUS_FAIL, f"evidence file(s) not found: {missing_on_disk}", details)

    if not paths:
        return Check(name, STATUS_INFO, "no evidence paths (nothing to back yet)", details)
    return Check(name, STATUS_PASS, f"{len(paths)} evidence file(s) present", details)


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def validate_study(m: CandidateStudyManifest) -> ValidationReport:
    """Run every provenance check in fixed order and collect the report."""
    ladders_by_dim = {}
    for ladder in m.ladders or []:
        if ladder.dimension not in ladders_by_dim:  # first wins, extras flagged below
            ladders_by_dim[ladder.dimension] = ladder

    checks = [
        _check_schema(m),
        _check_identity(m),
        _check_candidate_family(m),
        _check_material(m),
        _check_nonlinear(m),
        _check_geometry(m),
    ]
    for dim in LADDER_DIMENSIONS:
        checks.append(_check_ladder(ladders_by_dim.get(dim), dim))
    checks.append(_check_flex_credit(m))
    checks.append(_check_task_ids(m))
    checks.append(_check_evidence(m))

    extra_dims = [d for d in (l.dimension for l in (m.ladders or [])) if d not in LADDER_DIMENSIONS]
    if extra_dims:
        checks.append(Check("convergence.extra", STATUS_FAIL,
                            f"unexpected ladder dimension(s): {sorted(set(extra_dims))}"))

    return ValidationReport(checks)
