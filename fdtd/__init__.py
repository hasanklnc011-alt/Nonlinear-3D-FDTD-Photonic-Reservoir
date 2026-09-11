"""3D nonlinear FDTD candidate-study support code (local, dependency-light).

Currently this package contains only :mod:`fdtd.provenance`, a stdlib-only
configuration / provenance validation scaffold for the *upcoming* Tidy3D
candidate studies (project phases 3-5 in ``AGENTS.md``).

Nothing in this package imports Tidy3D, touches the network, submits or
downloads a cloud task, or runs an FDTD solve. It only describes and validates
the evidence a candidate study must carry before a paid solve can be approved.
"""

from __future__ import annotations

__all__ = ["provenance"]
__version__ = "0.1.0"
