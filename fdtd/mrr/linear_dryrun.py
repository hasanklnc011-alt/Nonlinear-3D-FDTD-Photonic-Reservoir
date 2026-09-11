"""Local dry-run validator for a :mod:`fdtd.mrr.linear_sim` plan document.

The dry run never touches the network and never instantiates ``tidy3d``. It
answers one question about a serialised
:class:`~fdtd.mrr.linear_sim.LinearSimulationPlan` document: *is this a complete,
internally consistent, evidence-backed **linear** simulation that Tidy3D could be
asked to build?* Any missing value, malformed digest, wavelength-band mismatch,
structure that does not fit the domain, or trace of nonlinear / cloud content is
a ``FAIL`` and :attr:`DryRunReport.ok` is ``False``.

The report is deterministic (no timestamps, fixed check order) so it can be
diffed and pasted into a coordination note.

Pure stdlib.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fdtd.provenance.schema import looks_like_sha256

from .linear_sim import (
    BOUNDARY_PLAN_KIND,
    LAYERED_BOUNDARIES,
    LINEAR_MEDIUM_MODELS,
    LINEAR_SIM_SCHEMA_ID,
    MONITOR_TOKEN_KINDS,
    SOURCE_TOKEN_KINDS,
    _finite_non_negative,
    _finite_positive,
    _is_wavelength_range,
    _parse_token,
    _covers,
)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_INFO = "INFO"

_NONLINEAR_MARKERS = (
    "nonlinear",
    "kerr",
    "kerrnonlinearity",
    "chi3",
    "chi(3)",
    "twophotonabsorption",
    "two_photon",
    "tpa",
    "free_carrier",
    "freecarrier",
    "n2",
)


class LinearPlanIncomplete(RuntimeError):
    """Raised by :meth:`DryRunReport.require_ok` when the dry run fails."""


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
        return {"name": self.name, "status": self.status, "summary": self.summary, "details": list(self.details)}


@dataclass
class DryRunReport:
    checks: list[Check]

    @property
    def failed(self) -> list[Check]:
        return [c for c in self.checks if c.failed]

    @property
    def ok(self) -> bool:
        return not self.failed

    def require_ok(self) -> None:
        if not self.ok:
            names = ", ".join(c.name for c in self.failed)
            raise LinearPlanIncomplete(f"linear simulation plan dry run failed: {names}")

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
            lines.append(f"LINEAR PLAN DRY RUN OK ({len(self.checks)} checks)")
        else:
            names = ", ".join(c.name for c in self.failed)
            lines.append(f"LINEAR PLAN DRY RUN FAILED ({len(self.failed)} failing: {names})")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _as_document(plan_or_doc) -> dict:
    if isinstance(plan_or_doc, dict):
        return plan_or_doc
    to_document = getattr(plan_or_doc, "to_document", None)
    if callable(to_document):
        return to_document()
    raise TypeError("dry_run expects a plan document dict or a LinearSimulationPlan")


def _excitation_band(doc: dict) -> list[float] | None:
    exc = (doc.get("inputs") or {}).get("excitation") or {}
    c, bw = exc.get("center_wavelength_um"), exc.get("bandwidth_wavelength_um")
    if not (_finite_positive(c) and _finite_positive(bw)):
        return None
    return [c - bw / 2.0, c + bw / 2.0]


def _find_nonlinear_markers(obj, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k).lower()
            here = f"{path}.{k}" if path else str(k)
            if any(m in key for m in _NONLINEAR_MARKERS) and v is not None:
                hits.append(here)
            hits.extend(_find_nonlinear_markers(v, here))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            hits.extend(_find_nonlinear_markers(v, f"{path}[{i}]"))
    elif isinstance(obj, str):
        low = obj.lower()
        for m in ("kerrnonlinearity", "twophotonabsorption", "chi(3)"):
            if m in low:
                hits.append(f"{path}={obj!r}")
    return hits


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def _check_schema(doc: dict) -> Check:
    got = doc.get("schema")
    if got != LINEAR_SIM_SCHEMA_ID:
        return Check("schema", STATUS_FAIL, f"schema {got!r} != {LINEAR_SIM_SCHEMA_ID!r}")
    if doc.get("tidy3d_target") != "tidy3d.Simulation":
        return Check("schema", STATUS_FAIL, f"tidy3d_target {doc.get('tidy3d_target')!r} != 'tidy3d.Simulation'")
    return Check("schema", STATUS_PASS, f"schema is {LINEAR_SIM_SCHEMA_ID}")


def _check_linear_only(doc: dict) -> Check:
    prov = doc.get("provenance") or {}
    problems: list[str] = []
    if doc.get("linearity") != "linear":
        problems.append(f"linearity {doc.get('linearity')!r} != 'linear'")
    if prov.get("linear_only") is not True:
        problems.append("provenance.linear_only is not True")
    if prov.get("nonlinear") is not None:
        problems.append(f"provenance.nonlinear is set ({prov.get('nonlinear')!r})")
    # scan everything except the provenance bookkeeping keys that legitimately
    # spell 'nonlinear' to assert its own absence.
    scan = {k: v for k, v in doc.items() if k != "provenance"}
    hits = _find_nonlinear_markers(scan)
    if hits:
        problems.append(f"nonlinear content found at: {hits}")
    if problems:
        return Check("linear_only", STATUS_FAIL, "; ".join(problems))
    return Check("linear_only", STATUS_PASS, "no nonlinear medium / term / marker present")


def _check_no_cloud(doc: dict) -> Check:
    prov = doc.get("provenance") or {}
    cloud = prov.get("cloud") or {}
    problems: list[str] = []
    for flag in ("uploaded", "estimated", "started", "monitored", "downloaded"):
        if cloud.get(flag):
            problems.append(f"provenance.cloud.{flag} is truthy")
    if cloud.get("task_ids"):
        problems.append(f"provenance.cloud.task_ids is non-empty: {cloud.get('task_ids')!r}")
    if cloud.get("flex_credit") is not None:
        problems.append(f"provenance.cloud.flex_credit is set ({cloud.get('flex_credit')!r})")
    if problems:
        return Check("no_cloud", STATUS_FAIL, "; ".join(problems))
    return Check("no_cloud", STATUS_PASS, "no task id, cost, or cloud action recorded")


def _check_domain(doc: dict) -> Check:
    dom = doc.get("domain") or {}
    size = dom.get("size_um")
    center = dom.get("center_um")
    problems: list[str] = []
    if not (isinstance(size, (list, tuple)) and len(size) == 3 and all(_finite_positive(x) for x in size)):
        problems.append(f"domain.size_um must be three positive numbers, got {size!r}")
    if not (isinstance(center, (list, tuple)) and len(center) == 3 and all(isinstance(x, (int, float)) for x in center)):
        problems.append(f"domain.center_um must be three numbers, got {center!r}")
    details = [f"size_um = {size!r}", f"center_um = {center!r}"]
    if problems:
        return Check("domain", STATUS_FAIL, "; ".join(problems), details)
    return Check("domain", STATUS_PASS, "domain size and center are well formed", details)


def _check_structures_fit(doc: dict) -> Check:
    dom = doc.get("domain") or {}
    size = dom.get("size_um")
    geo = ((doc.get("inputs") or {}).get("geometry_document") or {}).get("parameters") or {}
    if not (isinstance(size, (list, tuple)) and len(size) == 3 and all(_finite_positive(x) for x in size)):
        return Check("structures_fit", STATUS_FAIL, "cannot check fit: domain.size_um is invalid")
    problems: list[str] = []

    bus_length = geo.get("bus_length_um")
    if _finite_positive(bus_length) and bus_length > size[0] + 1e-9:
        problems.append(f"bus_length_um {bus_length} exceeds domain x-size {size[0]}")

    try:
        y_needed = (
            2.0
            * (geo["ring_outer_radius_um"] + geo["coupling_gap_um"] + geo["bus_waveguide_width_um"] / 2.0)
            + geo["bus_waveguide_width_um"]
        )
        if y_needed > size[1] + 1e-9:
            problems.append(f"transverse extent {y_needed:g} exceeds domain y-size {size[1]}")
    except (KeyError, TypeError):
        problems.append("geometry parameters missing; cannot check y-extent")

    try:
        z_stack = (
            geo["substrate_thickness_um"]
            + geo["box_thickness_um"]
            + geo["waveguide_thickness_um"]
            + geo["cladding_thickness_um"]
        )
        if z_stack > size[2] + 1e-9:
            problems.append(f"vertical stack {z_stack:g} exceeds domain z-size {size[2]}")
    except (KeyError, TypeError):
        problems.append("geometry parameters missing; cannot check z-stack")

    n_struct = len(doc.get("structures") or [])
    details = [f"structures = {n_struct}", f"domain size_um = {size!r}"]
    if n_struct == 0:
        problems.append("plan has no structures")
    if problems:
        return Check("structures_fit", STATUS_FAIL, "; ".join(problems), details)
    return Check("structures_fit", STATUS_PASS, f"{n_struct} structures fit inside the domain", details)


def _check_media(doc: dict) -> Check:
    problems: list[str] = []
    n_checked = 0

    def _check_medium(med, where: str) -> None:
        nonlocal n_checked
        n_checked += 1
        if not isinstance(med, dict):
            problems.append(f"{where}: medium is not an object")
            return
        if med.get("model") not in LINEAR_MEDIUM_MODELS:
            problems.append(f"{where}: model {med.get('model')!r} not in {list(LINEAR_MEDIUM_MODELS)}")
        if not _finite_positive(med.get("permittivity")):
            problems.append(f"{where}: permittivity must be > 0, got {med.get('permittivity')!r}")
        if not _finite_non_negative(med.get("conductivity")):
            problems.append(f"{where}: conductivity must be >= 0, got {med.get('conductivity')!r}")
        ev = med.get("evidence") or {}
        if not looks_like_sha256(ev.get("digest")):
            problems.append(f"{where}: evidence.digest is not a sha256 hex digest")
        if not (isinstance(ev.get("reference"), str) and ev.get("reference").strip()):
            problems.append(f"{where}: evidence.reference is missing")
        if not _is_wavelength_range(ev.get("wavelength_range_um")):
            problems.append(f"{where}: evidence.wavelength_range_um is malformed")

    bg = doc.get("background_medium")
    if bg is None:
        problems.append("background_medium is absent")
    else:
        _check_medium(bg, "background_medium")

    for i, s in enumerate(doc.get("structures") or []):
        med = s.get("medium") if isinstance(s, dict) else None
        if med is None:
            problems.append(f"structures[{i}] ({s.get('name') if isinstance(s, dict) else '?'}): medium is missing")
        else:
            _check_medium(med, f"structures[{i}] {s.get('name')!r}")

    details = [f"media checked = {n_checked}"]
    if problems:
        return Check("media", STATUS_FAIL, "; ".join(problems), details)
    return Check("media", STATUS_PASS, f"{n_checked} linear media fully specified and evidenced", details)


def _check_wavelength_consistency(doc: dict) -> Check:
    band = _excitation_band(doc)
    details = [f"excitation_band_um = {band!r}"]
    if band is None:
        return Check("wavelength_consistency", STATUS_FAIL, "excitation band is undefined", details)
    if band[0] <= 0:
        return Check("wavelength_consistency", STATUS_FAIL, f"excitation band {band!r} reaches non-positive wavelength", details)

    problems: list[str] = []
    cfg = (doc.get("inputs") or {}).get("config") or {}
    cfg_range = cfg.get("wavelength_range_um")
    details.append(f"config.wavelength_range_um = {cfg_range!r}")
    if not _covers(cfg_range, band):
        problems.append(f"excitation band not inside config.wavelength_range_um {cfg_range!r}")

    for label, ev in ((doc.get("provenance") or {}).get("material_evidence") or {}).items():
        wr = ev.get("wavelength_range_um")
        if not _covers(wr, band):
            problems.append(f"excitation band outside medium {label!r} validity window {wr!r}")

    if problems:
        return Check("wavelength_consistency", STATUS_FAIL, "; ".join(problems), details)
    return Check("wavelength_consistency", STATUS_PASS, "excitation band inside config and every medium window", details)


def _check_grid_and_time(doc: dict) -> Check:
    problems: list[str] = []
    grid = doc.get("grid_spec") or {}
    if grid.get("type") != "AutoGrid":
        problems.append(f"grid_spec.type {grid.get('type')!r} != 'AutoGrid'")
    if not _finite_positive(grid.get("min_steps_per_wavelength")):
        problems.append(f"grid_spec.min_steps_per_wavelength must be > 0, got {grid.get('min_steps_per_wavelength')!r}")
    if not _finite_positive(grid.get("wavelength_um")):
        problems.append(f"grid_spec.wavelength_um must be > 0, got {grid.get('wavelength_um')!r}")
    if not _finite_positive(doc.get("run_time_s")):
        problems.append(f"run_time_s must be > 0, got {doc.get('run_time_s')!r}")
    if not _finite_non_negative(doc.get("field_decay_shutoff")):
        problems.append(f"field_decay_shutoff must be >= 0, got {doc.get('field_decay_shutoff')!r}")
    details = [
        f"grid_spec = {grid!r}",
        f"run_time_s = {doc.get('run_time_s')!r}",
        f"field_decay_shutoff = {doc.get('field_decay_shutoff')!r}",
    ]
    if problems:
        return Check("grid_and_time", STATUS_FAIL, "; ".join(problems), details)
    return Check("grid_and_time", STATUS_PASS, "grid, run time and shutoff are set", details)


def _check_boundaries(doc: dict) -> Check:
    bspec = doc.get("boundary_spec") or {}
    problems: list[str] = []
    if set(bspec) != {"x", "y", "z"}:
        problems.append(f"boundary_spec must have keys x, y, z; got {sorted(bspec)}")
    for axis, entry in bspec.items():
        if not isinstance(entry, dict):
            problems.append(f"boundary_spec[{axis!r}] is not an object")
            continue
        ctype = entry.get("config_type")
        if entry.get("kind") != BOUNDARY_PLAN_KIND.get(ctype):
            problems.append(f"boundary_spec[{axis!r}] kind {entry.get('kind')!r} does not match config_type {ctype!r}")
        if ctype in LAYERED_BOUNDARIES:
            if not (isinstance(entry.get("num_layers"), int) and entry.get("num_layers") >= 1):
                problems.append(f"boundary_spec[{axis!r}] {ctype} needs num_layers >= 1, got {entry.get('num_layers')!r}")
    details = [f"boundary_spec = {bspec!r}"]
    if problems:
        return Check("boundaries", STATUS_FAIL, "; ".join(problems), details)
    return Check("boundaries", STATUS_PASS, "all three axes carry a known boundary kind", details)


def _check_symmetry(doc: dict) -> Check:
    sym = doc.get("symmetry")
    if not (isinstance(sym, (list, tuple)) and len(sym) == 3 and all(s in (-1, 0, 1) for s in sym)):
        return Check("symmetry", STATUS_FAIL, f"symmetry must be three values in (-1, 0, 1), got {sym!r}")
    return Check("symmetry", STATUS_PASS, f"symmetry = {list(sym)}")


def _structure_names(doc: dict) -> set[str]:
    return {s.get("name") for s in (doc.get("structures") or []) if isinstance(s, dict)}


def _check_ports(doc: dict, key: str, allowed_kinds) -> Check:
    items = doc.get(key) or []
    names = _structure_names(doc)
    problems: list[str] = []
    if not items:
        problems.append(f"{key} is empty")
    for i, item in enumerate(items):
        tok = item.get("token") if isinstance(item, dict) else None
        parsed = _parse_token(tok)
        if parsed is None:
            problems.append(f"{key}[{i}]: token {tok!r} is malformed")
            continue
        kind, structure, _port = parsed
        if kind not in allowed_kinds:
            problems.append(f"{key}[{i}]: kind {kind!r} not in {list(allowed_kinds)}")
        if names and structure not in names:
            problems.append(f"{key}[{i}]: structure {structure!r} not among {sorted(names)}")
        plane = item.get("plane_size_um") if isinstance(item, dict) else None
        if not (isinstance(plane, (list, tuple)) and len(plane) == 3 and sum(1 for v in plane if v == 0) == 1):
            problems.append(f"{key}[{i}]: plane_size_um {plane!r} must be a plane (exactly one zero extent)")
    details = [f"{key} = {len(items)}"]
    if problems:
        return Check(key, STATUS_FAIL, "; ".join(problems), details)
    return Check(key, STATUS_PASS, f"{len(items)} {key} well formed", details)


def _check_provenance(doc: dict) -> Check:
    prov = doc.get("provenance") or {}
    problems: list[str] = []
    for name in ("study_id", "created_utc"):
        if not (isinstance(prov.get(name), str) and prov.get(name).strip()):
            problems.append(f"provenance.{name} is missing")
    for name in ("geometry_hash", "config_hash"):
        if not looks_like_sha256(prov.get(name)):
            problems.append(f"provenance.{name} is not a sha256 hex digest")
    if not ((doc.get("inputs") or {}).get("materials")):
        problems.append("inputs.materials is empty")
    details = [
        f"geometry_hash = {prov.get('geometry_hash')!r}",
        f"config_hash = {prov.get('config_hash')!r}",
        f"material_evidence labels = {sorted((prov.get('material_evidence') or {}))}",
    ]
    if problems:
        return Check("provenance", STATUS_FAIL, "; ".join(problems), details)
    return Check("provenance", STATUS_PASS, "study id, geometry hash and config hash recorded", details)


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def dry_run(plan_or_doc) -> DryRunReport:
    """Run every dry-run check in fixed order over a linear-simulation plan."""
    doc = _as_document(plan_or_doc)
    checks = [
        _check_schema(doc),
        _check_linear_only(doc),
        _check_no_cloud(doc),
        _check_domain(doc),
        _check_structures_fit(doc),
        _check_media(doc),
        _check_wavelength_consistency(doc),
        _check_grid_and_time(doc),
        _check_boundaries(doc),
        _check_symmetry(doc),
        _check_ports(doc, "sources", SOURCE_TOKEN_KINDS),
        _check_ports(doc, "monitors", MONITOR_TOKEN_KINDS),
        _check_provenance(doc),
    ]
    return DryRunReport(checks)
