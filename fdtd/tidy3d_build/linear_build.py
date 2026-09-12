"""Local-only construction of a **real** ``tidy3d.Simulation`` from a validated
:class:`~fdtd.mrr.linear_sim.LinearSimulationPlan`.

``tidy3d`` is imported *lazily* -- only when a caller actually asks to build the
object -- so importing this module (or :mod:`fdtd.tidy3d_build`) still pulls in
no solver / network / cloud code. The module answers exactly one question:
*given a plan document that already passed
:func:`fdtd.mrr.linear_dryrun.dry_run`, what is the concrete ``tidy3d.Simulation``
it maps onto, and what is the SHA-256 of that object's canonical serialisation?*

Hard boundaries (mirrored by ``tests/fdtd/test_linear_build.py``):

* **No cloud, ever.** Nothing here touches ``tidy3d.web``: no ``upload``,
  ``estimate_cost``, ``run`` / ``start`` / ``monitor`` / ``download``, no task id,
  no FlexCredit call, no socket. :func:`build_simulation` asserts
  ``tidy3d.web`` was not imported as a side effect.
* **Linear only.** A plan whose ``linearity`` is not ``"linear"``, whose
  ``provenance.linear_only`` is not ``True``, or that carries any nonlinear
  marker (Kerr / TPA / chi(3) / free-carrier / ``n2``) is rejected before any
  Tidy3D object is built.
* **No invented physics or geometry.** Every permittivity, conductivity, length,
  radius, wavelength, layer count, run time and shutoff is read verbatim from
  the plan. The only computed quantities are mechanical: wavelength -> frequency
  via Tidy3D's own ``C_0`` (the plan explicitly defers this), a slab's centre
  from the domain centre and its ``z`` bounds, and a linear frequency sweep
  across the plan's excitation band. No material constant, no speed of light, no
  mesh / time / PML choice originates here.
* **Fail closed.** The plan is re-run through :func:`fdtd.mrr.linear_dryrun.dry_run`
  by default; any failing check raises :class:`LinearBuildError` and nothing is
  built.

The build itself is pure translation:

===============================  ===================================================
plan token                       Tidy3D object
===============================  ===================================================
``background_medium`` / structure ``medium`` (``model="non_dispersive"``)
                                 ``td.Medium(permittivity=eps_r, conductivity=sigma)``
structure ``kind="ring"``        ``td.Structure`` over a ``td.ClipOperation`` difference
                                 of two coaxial ``td.Cylinder`` (outer minus inner)
structure ``kind="waveguide"``   ``td.Structure`` over a ``td.Box``
structure ``kind="slab"``        ``td.Structure`` over a domain-wide ``td.Box`` in ``z``
``boundary_spec`` (``PML`` ...)   ``td.BoundarySpec`` of ``td.Boundary.pml`` /
                                 ``.absorber`` / ``.periodic`` / ``.pec`` / ``.pmc``
``sources`` (``ModeSource``)     ``td.ModeSource`` + ``td.GaussianPulse``
``monitors`` (``flux`` / ``field``) ``td.FluxMonitor`` / ``td.FieldMonitor``
``grid_spec`` (``AutoGrid``)     ``td.GridSpec.auto(min_steps_per_wvl=, wavelength=)``
===============================  ===================================================
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from fdtd.mrr.linear_dryrun import _as_document, _find_nonlinear_markers, dry_run
from fdtd.mrr.linear_sim import BOUNDARY_PLAN_KIND, LINEAR_MEDIUM_MODELS, LINEAR_SIM_SCHEMA_ID
from fdtd.provenance.schema import sha256_text

# Structure precedence for the emitted ``structures`` list. Tidy3D resolves
# overlapping structures last-wins, and the plan's planar stack (substrate /
# buried oxide / cladding) spans the same ``z`` band as the waveguide cores, so
# the slabs must be listed *before* the ring / bus structures or the device
# would be buried in the cladding medium. This is an ordering of the same
# structures, not a change to any geometry value.
_STRUCTURE_ORDER = {"slab": 0, "ring": 1, "waveguide": 1}


class LinearBuildError(RuntimeError):
    """Raised when a plan document cannot be turned into a linear ``tidy3d.Simulation``."""


@dataclass
class BuiltLinearSimulation:
    """A concrete ``tidy3d.Simulation`` plus its canonical serialisation + digest."""

    simulation: object          # tidy3d.Simulation (untyped here to keep the import lazy)
    canonical_json: str         # sorted-key, compact JSON of the Simulation
    digest: str                 # SHA-256 hex of ``canonical_json``
    tidy3d_version: str          # the tidy3d that produced the serialisation


# --------------------------------------------------------------------------- #
# lazy tidy3d handle
# --------------------------------------------------------------------------- #
def _td():
    """Import :mod:`tidy3d` on demand. Never imports :mod:`tidy3d.web`."""
    import tidy3d as td  # noqa: PLC0415  (intentionally lazy: keeps module import cloud-free)

    return td


# --------------------------------------------------------------------------- #
# fail-closed gate (pure: no tidy3d import)
# --------------------------------------------------------------------------- #
def _guard(doc: dict, *, run_dry_run: bool) -> None:
    if not isinstance(doc, dict):
        raise LinearBuildError(f"plan document must be an object, got {type(doc).__name__}")

    problems: list[str] = []

    if doc.get("schema") != LINEAR_SIM_SCHEMA_ID:
        problems.append(f"schema {doc.get('schema')!r} != {LINEAR_SIM_SCHEMA_ID!r}")
    if doc.get("tidy3d_target") != "tidy3d.Simulation":
        problems.append(f"tidy3d_target {doc.get('tidy3d_target')!r} != 'tidy3d.Simulation'")
    if doc.get("linearity") != "linear":
        problems.append(f"linearity {doc.get('linearity')!r} != 'linear'")

    prov = doc.get("provenance") or {}
    if prov.get("linear_only") is not True:
        problems.append("provenance.linear_only is not True")
    if prov.get("nonlinear") is not None:
        problems.append(f"provenance.nonlinear is set ({prov.get('nonlinear')!r})")

    scan = {k: v for k, v in doc.items() if k != "provenance"}
    hits = _find_nonlinear_markers(scan)
    if hits:
        problems.append(f"nonlinear content found at: {hits}")

    cloud = prov.get("cloud") or {}
    for flag in ("uploaded", "estimated", "started", "monitored", "downloaded"):
        if cloud.get(flag):
            problems.append(f"provenance.cloud.{flag} is truthy")
    if cloud.get("task_ids"):
        problems.append(f"provenance.cloud.task_ids is non-empty: {cloud.get('task_ids')!r}")
    if cloud.get("flex_credit") is not None:
        problems.append(f"provenance.cloud.flex_credit is set ({cloud.get('flex_credit')!r})")

    if run_dry_run:
        report = dry_run(doc)
        if not report.ok:
            problems.append("dry run failed: " + ", ".join(c.name for c in report.failed))

    if problems:
        raise LinearBuildError("; ".join(problems))


# --------------------------------------------------------------------------- #
# token -> tidy3d object helpers
# --------------------------------------------------------------------------- #
def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _medium(td, med_doc: object, where: str):
    if not isinstance(med_doc, dict):
        raise LinearBuildError(f"{where}: medium is missing")
    if med_doc.get("model") not in LINEAR_MEDIUM_MODELS:
        raise LinearBuildError(
            f"{where}: medium model {med_doc.get('model')!r} not in {list(LINEAR_MEDIUM_MODELS)}"
        )
    eps = med_doc.get("permittivity")
    sigma = med_doc.get("conductivity")
    if not (_is_number(eps) and eps > 0):
        raise LinearBuildError(f"{where}: permittivity must be a number > 0, got {eps!r}")
    if not (_is_number(sigma) and sigma >= 0):
        raise LinearBuildError(f"{where}: conductivity must be a number >= 0, got {sigma!r}")
    return td.Medium(permittivity=float(eps), conductivity=float(sigma))


def _structure(td, s: dict, domain_center):
    kind = s.get("kind")
    medium = _medium(td, s.get("medium"), f"structure {s.get('name')!r}")

    if kind == "ring":
        center = tuple(float(v) for v in s["center_um"])
        outer = float(s["outer_radius_um"])
        inner = float(s["inner_radius_um"])
        thickness = float(s["thickness_um"])
        outer_cyl = td.Cylinder(center=center, radius=outer, length=thickness, axis=2)
        inner_cyl = td.Cylinder(center=center, radius=inner, length=thickness, axis=2)
        geom = td.ClipOperation(operation="difference", geometry_a=outer_cyl, geometry_b=inner_cyl)
        return td.Structure(geometry=geom, medium=medium, name=s.get("name"))

    if kind == "waveguide":
        center = tuple(float(v) for v in s["center_um"])
        width = float(s["width_um"])
        length = float(s["length_um"])
        thickness = float(s["thickness_um"])
        axis = s.get("axis", "x")
        if axis == "x":
            size = (length, width, thickness)
        elif axis == "y":
            size = (width, length, thickness)
        else:
            raise LinearBuildError(f"structure {s.get('name')!r}: unsupported waveguide axis {axis!r}")
        return td.Structure(geometry=td.Box(center=center, size=size), medium=medium, name=s.get("name"))

    if kind == "slab":
        z_min = float(s["z_min_um"])
        z_max = float(s["z_max_um"])
        if not z_max > z_min:
            raise LinearBuildError(f"structure {s.get('name')!r}: slab needs z_max > z_min")
        center = (float(domain_center[0]), float(domain_center[1]), (z_min + z_max) / 2.0)
        size = (td.inf, td.inf, z_max - z_min)
        return td.Structure(geometry=td.Box(center=center, size=size), medium=medium, name=s.get("name"))

    raise LinearBuildError(f"structure {s.get('name')!r}: unknown kind {kind!r}")


def _structures(td, doc: dict):
    domain_center = (doc.get("domain") or {}).get("center_um") or [0.0, 0.0, 0.0]
    raw = list(doc.get("structures") or [])
    if not raw:
        raise LinearBuildError("plan has no structures")
    ordered = sorted(raw, key=lambda s: _STRUCTURE_ORDER.get(s.get("kind"), 1))
    return [_structure(td, s, domain_center) for s in ordered]


def _band_frequencies(td, doc: dict):
    """(freq0, fwidth, [monitor freqs]) from the plan's excitation band via Tidy3D's C_0."""
    exc = (doc.get("inputs") or {}).get("excitation") or {}
    center = exc.get("center_wavelength_um")
    bandwidth = exc.get("bandwidth_wavelength_um")
    num_freqs = exc.get("num_freqs")
    for name, value in (("center_wavelength_um", center), ("bandwidth_wavelength_um", bandwidth)):
        if not (_is_number(value) and value > 0):
            raise LinearBuildError(f"excitation.{name} must be a number > 0, got {value!r}")
    if not (isinstance(num_freqs, int) and not isinstance(num_freqs, bool) and num_freqs >= 1):
        raise LinearBuildError(f"excitation.num_freqs must be an integer >= 1, got {num_freqs!r}")

    lo_wl = center - bandwidth / 2.0
    hi_wl = center + bandwidth / 2.0
    if lo_wl <= 0:
        raise LinearBuildError(f"excitation band [{lo_wl}, {hi_wl}] um reaches non-positive wavelength")

    c0 = td.C_0
    freq0 = c0 / center
    f_lo = c0 / hi_wl
    f_hi = c0 / lo_wl
    fwidth = f_hi - f_lo
    if num_freqs == 1:
        freqs = [freq0]
    else:
        step = (f_hi - f_lo) / (num_freqs - 1)
        freqs = [f_lo + i * step for i in range(num_freqs)]
    return freq0, fwidth, freqs


def _sources(td, doc: dict, pulse):
    out = []
    for src in doc.get("sources") or []:
        if src.get("type") != "ModeSource":
            raise LinearBuildError(f"source {src.get('token')!r}: unsupported type {src.get('type')!r}")
        out.append(
            td.ModeSource(
                center=tuple(float(v) for v in src["plane_center_um"]),
                size=tuple(float(v) for v in src["plane_size_um"]),
                source_time=pulse,
                direction=src["direction"],
                mode_spec=td.ModeSpec(),
                name=src.get("token"),
            )
        )
    if not out:
        raise LinearBuildError("plan lists no sources")
    return out


def _sampling_frequencies(td, sampling: dict, where: str):
    """Monitor-local frequency list from a ``sampling`` block.

    A monitor's spectral sampling is a *measurement* choice and is independent of
    the source pulse: resolving a high-Q line needs a fine frequency comb, while
    narrowing the excitation itself would only lengthen the pulse in time. The
    plan already carries a per-monitor ``sampling`` block; this reads it.
    """
    center = sampling.get("center_wavelength_um")
    bandwidth = sampling.get("bandwidth_wavelength_um")
    num_freqs = sampling.get("num_freqs")
    for name, value in (("center_wavelength_um", center), ("bandwidth_wavelength_um", bandwidth)):
        if not (_is_number(value) and value > 0):
            raise LinearBuildError(f"{where}.sampling.{name} must be a number > 0, got {value!r}")
    if not (isinstance(num_freqs, int) and not isinstance(num_freqs, bool) and num_freqs >= 1):
        raise LinearBuildError(
            f"{where}.sampling.num_freqs must be an integer >= 1, got {num_freqs!r}"
        )
    lo_wl = center - bandwidth / 2.0
    hi_wl = center + bandwidth / 2.0
    if lo_wl <= 0:
        raise LinearBuildError(
            f"{where}.sampling band [{lo_wl}, {hi_wl}] um reaches non-positive wavelength"
        )
    c0 = td.C_0
    if num_freqs == 1:
        return [c0 / center]
    f_lo = c0 / hi_wl
    f_hi = c0 / lo_wl
    step = (f_hi - f_lo) / (num_freqs - 1)
    return [f_lo + i * step for i in range(num_freqs)]


def _monitors(td, doc: dict, freqs):
    out = []
    for mon in doc.get("monitors") or []:
        mtype = mon.get("type")
        center = tuple(float(v) for v in mon["plane_center_um"])
        size = tuple(float(v) for v in mon["plane_size_um"])
        sampling = mon.get("sampling")
        if isinstance(sampling, dict):
            mon_freqs = _sampling_frequencies(td, sampling, f"monitor {mon.get('token')!r}")
        else:
            mon_freqs = list(freqs)
        if mtype == "FluxMonitor":
            out.append(td.FluxMonitor(center=center, size=size, freqs=mon_freqs, name=mon["token"]))
        elif mtype == "FieldMonitor":
            out.append(td.FieldMonitor(center=center, size=size, freqs=mon_freqs, name=mon["token"]))
        else:
            raise LinearBuildError(f"monitor {mon.get('token')!r}: unsupported type {mtype!r}")
    if not out:
        raise LinearBuildError("plan lists no monitors")
    return out


def _boundary_spec(td, doc: dict):
    bspec = doc.get("boundary_spec") or {}
    if set(bspec) != {"x", "y", "z"}:
        raise LinearBuildError(f"boundary_spec must have keys x, y, z; got {sorted(bspec)}")

    def _one(axis: str):
        entry = bspec[axis]
        ctype = entry.get("config_type")
        kind = entry.get("kind")
        if kind != BOUNDARY_PLAN_KIND.get(ctype):
            raise LinearBuildError(
                f"boundary_spec[{axis!r}] kind {kind!r} does not match config_type {ctype!r}"
            )
        num_layers = entry.get("num_layers")
        if ctype == "pml":
            return td.Boundary.pml(num_layers=int(num_layers))
        if ctype == "absorber":
            return td.Boundary.absorber(num_layers=int(num_layers))
        if ctype == "periodic":
            return td.Boundary.periodic()
        if ctype == "pec":
            return td.Boundary.pec()
        if ctype == "pmc":
            return td.Boundary.pmc()
        raise LinearBuildError(f"boundary_spec[{axis!r}]: unknown config_type {ctype!r}")

    return td.BoundarySpec(x=_one("x"), y=_one("y"), z=_one("z"))


def _grid_spec(td, doc: dict):
    grid = doc.get("grid_spec") or {}
    if grid.get("type") != "AutoGrid":
        raise LinearBuildError(f"grid_spec.type {grid.get('type')!r} != 'AutoGrid'")
    return td.GridSpec.auto(
        min_steps_per_wvl=float(grid["min_steps_per_wavelength"]),
        wavelength=float(grid["wavelength_um"]),
    )


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def build_simulation(plan_or_doc, *, run_dry_run: bool = True):
    """Build a concrete ``tidy3d.Simulation`` from a validated linear plan.

    ``plan_or_doc`` is a :class:`~fdtd.mrr.linear_sim.LinearSimulationPlan`, its
    ``.document`` dict, or any object exposing ``to_document()``. Raises
    :class:`LinearBuildError` if the plan is not a complete, linear, cloud-free
    document (the :func:`fdtd.mrr.linear_dryrun.dry_run` gate runs unless
    ``run_dry_run=False``).
    """
    try:
        doc = _as_document(plan_or_doc)
    except TypeError as exc:
        raise LinearBuildError(str(exc)) from exc
    _guard(doc, run_dry_run=run_dry_run)

    web_was_imported = "tidy3d.web" in sys.modules
    td = _td()

    background = _medium(td, doc.get("background_medium"), "background_medium")
    structures = _structures(td, doc)
    freq0, fwidth, freqs = _band_frequencies(td, doc)
    pulse = td.GaussianPulse(freq0=freq0, fwidth=fwidth)
    sources = _sources(td, doc, pulse)
    monitors = _monitors(td, doc, freqs)
    boundary_spec = _boundary_spec(td, doc)
    grid_spec = _grid_spec(td, doc)

    domain = doc.get("domain") or {}
    symmetry = tuple(int(v) for v in doc.get("symmetry") or (0, 0, 0))

    sim = td.Simulation(
        center=tuple(float(v) for v in domain["center_um"]),
        size=tuple(float(v) for v in domain["size_um"]),
        grid_spec=grid_spec,
        structures=structures,
        sources=sources,
        monitors=monitors,
        run_time=float(doc["run_time_s"]),
        shutoff=float(doc["field_decay_shutoff"]),
        boundary_spec=boundary_spec,
        symmetry=symmetry,
        medium=background,
    )

    if not web_was_imported and "tidy3d.web" in sys.modules:
        raise LinearBuildError(
            "tidy3d.web was imported while building the Simulation; this layer is local-only"
        )

    return sim


def serialize_simulation(sim) -> str:
    """Canonical (sorted-key, compact) JSON of a ``tidy3d.Simulation``.

    Uses Tidy3D's own serialisation, then re-dumps it with sorted keys and
    compact separators so the string -- and its SHA-256 -- is insensitive to
    field ordering but sensitive to any value change.
    """
    import json  # noqa: PLC0415

    dump = getattr(sim, "model_dump_json", None)
    text = dump() if callable(dump) else sim.json()
    return json.dumps(json.loads(text), sort_keys=True, separators=(",", ":"))


def simulation_digest(sim) -> str:
    """SHA-256 hex digest of :func:`serialize_simulation`."""
    return sha256_text(serialize_simulation(sim))


def build(plan_or_doc, *, run_dry_run: bool = True) -> BuiltLinearSimulation:
    """Build the Simulation and return it with its canonical JSON, digest and tidy3d version."""
    sim = build_simulation(plan_or_doc, run_dry_run=run_dry_run)
    canonical = serialize_simulation(sim)
    return BuiltLinearSimulation(
        simulation=sim,
        canonical_json=canonical,
        digest=sha256_text(canonical),
        tidy3d_version=getattr(_td(), "__version__", "unknown"),
    )
