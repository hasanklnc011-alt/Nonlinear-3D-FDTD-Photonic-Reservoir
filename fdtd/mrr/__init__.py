"""Local study-builder scaffold for a 3D silicon microring-resonator (MRR) candidate.

This package turns caller-supplied **geometry** and **simulation configuration**
into a deterministic, hashable description and assembles an *intentionally
incomplete* :class:`~fdtd.provenance.schema.CandidateStudyManifest` for the Astra
evidence / maturity gate.

What it does **not** do (enforced by omission, mirrored by tests):

* it does not hold or invent any physical material / nonlinear parameter value
  (refractive index, absorption, ``n2``, TPA, ``chi(3)`` ...); those must be
  supplied from outside as :class:`~fdtd.provenance.schema.MaterialSource` /
  :class:`~fdtd.provenance.schema.NonlinearModel` records that carry only a
  reference + SHA-256 digest of an external artifact;
* it does not choose the candidate family — ``candidate_family`` is left ``None``
  for Astra;
* it does not choose a mesh, time-step, PML ladder, tolerance, run time, or
  FlexCredit ceiling — the manifest's ``ladders`` are emitted empty and
  ``flex_credit`` is left blank for Astra to fill;
* it never imports Tidy3D, opens a socket, submits or downloads a cloud task, or
  runs an FDTD solve.

The manifest it produces is designed to **fail**
:func:`fdtd.provenance.validate.validate_study` until Astra completes it.
"""

from __future__ import annotations

from .config import ConfigError, SimulationConfig
from .geometry import GeometryError, RingResonatorGeometry
from .study import (
    MicroringStudyBuilder,
    MissingEvidenceError,
    REQUIRED_MATERIAL_FIELDS,
    REQUIRED_NONLINEAR_FIELDS,
    StudyIdentity,
)
from .linear_sim import (
    DiscretizationSpec,
    ExcitationSpec,
    LINEAR_INPUT_SCHEMA_ID,
    LINEAR_SIM_SCHEMA_ID,
    LinearMaterialTable,
    LinearMediumValue,
    LinearSimulationPlan,
    LinearSimulationTranslator,
    MissingLinearEvidenceError,
    TranslationError,
)
from .linear_dryrun import DryRunReport, LinearPlanIncomplete, dry_run

__all__ = [
    "ConfigError",
    "SimulationConfig",
    "GeometryError",
    "RingResonatorGeometry",
    "MicroringStudyBuilder",
    "MissingEvidenceError",
    "REQUIRED_MATERIAL_FIELDS",
    "REQUIRED_NONLINEAR_FIELDS",
    "StudyIdentity",
    "DiscretizationSpec",
    "ExcitationSpec",
    "LINEAR_INPUT_SCHEMA_ID",
    "LINEAR_SIM_SCHEMA_ID",
    "LinearMaterialTable",
    "LinearMediumValue",
    "LinearSimulationPlan",
    "LinearSimulationTranslator",
    "MissingLinearEvidenceError",
    "TranslationError",
    "DryRunReport",
    "LinearPlanIncomplete",
    "dry_run",
]
