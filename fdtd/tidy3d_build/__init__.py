"""The one place in :mod:`fdtd` that is allowed to build real Tidy3D objects.

:mod:`fdtd.mrr` stays a pure, stdlib-only *planning* layer: it turns a
fully-evidenced study input into a deterministic
:class:`~fdtd.mrr.linear_sim.LinearSimulationPlan` document and validates it
locally, and every module under ``fdtd/mrr`` is asserted to never import
``tidy3d`` or any network code.

This sibling package is the realisation step: :mod:`fdtd.tidy3d_build.linear_build`
takes a plan document that already passed
:func:`fdtd.mrr.linear_dryrun.dry_run` and constructs the concrete
``tidy3d.Simulation`` it maps onto, then serialises and SHA-256-hashes it.

It is still **local-only**: ``tidy3d`` is imported lazily (so importing this
package pulls in no solver / cloud code), and nothing here ever touches
``tidy3d.web`` -- no upload, cost estimate, task submission, monitoring or
download. It builds the object and hashes it; running it is somebody else's job.
"""

from __future__ import annotations

from .linear_build import (
    BuiltLinearSimulation,
    LinearBuildError,
    build,
    build_simulation,
    serialize_simulation,
    simulation_digest,
)

__all__ = [
    "BuiltLinearSimulation",
    "LinearBuildError",
    "build",
    "build_simulation",
    "serialize_simulation",
    "simulation_digest",
]
