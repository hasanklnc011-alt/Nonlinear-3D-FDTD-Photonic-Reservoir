"""Local configuration / provenance validation scaffold for Tidy3D candidate studies.

Purpose
-------
Before any paid 3D nonlinear FDTD solve, ``const.md`` and the project charter
require recorded, verifiable evidence:

* material dispersion model **source and version**,
* a **geometry hash**,
* the **nonlinear model parameters and their source**,
* a **mesh / time-step / PML convergence ladder**,
* **estimated and actual FlexCredit** cost,
* the Tidy3D **task IDs** backing every number above.

This package provides a typed schema for that record
(:mod:`fdtd.provenance.schema`) and a *fail-closed* validator
(:mod:`fdtd.provenance.validate`): if a required field or its backing evidence
is absent, validation fails and the study is not cleared.

Boundaries (enforced by omission, not by code):

* it does not choose a candidate family,
* it does not contain any physical material / nonlinear parameter values —
  those live in external artifacts that are referenced only by SHA-256 digest,
* it never calls Tidy3D, submits or downloads a task, or runs a solve.
"""

from __future__ import annotations

from .schema import (
    CandidateStudyManifest,
    ConvergenceLadder,
    ConvergenceRung,
    FlexCreditBudget,
    GeometryProvenance,
    MaterialSource,
    NonlinearModel,
    SCHEMA_ID,
    SOURCE_KINDS,
    blank_manifest,
    looks_like_sha256,
    sha256_bytes,
    sha256_text,
)
from .validate import (
    Check,
    STATUS_FAIL,
    STATUS_INFO,
    STATUS_PASS,
    StudyProvenanceIncomplete,
    ValidationReport,
    validate_study,
)

__all__ = [
    "CandidateStudyManifest",
    "ConvergenceLadder",
    "ConvergenceRung",
    "FlexCreditBudget",
    "GeometryProvenance",
    "MaterialSource",
    "NonlinearModel",
    "SCHEMA_ID",
    "SOURCE_KINDS",
    "blank_manifest",
    "looks_like_sha256",
    "sha256_bytes",
    "sha256_text",
    "Check",
    "STATUS_FAIL",
    "STATUS_INFO",
    "STATUS_PASS",
    "StudyProvenanceIncomplete",
    "ValidationReport",
    "validate_study",
]
