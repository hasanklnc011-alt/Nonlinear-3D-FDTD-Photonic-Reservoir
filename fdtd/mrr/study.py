"""Assemble an intentionally incomplete ``CandidateStudyManifest`` for an MRR study.

:class:`MicroringStudyBuilder` takes:

* a validated :class:`~fdtd.mrr.geometry.RingResonatorGeometry`,
* a validated :class:`~fdtd.mrr.config.SimulationConfig`,
* a **caller-supplied** :class:`~fdtd.provenance.schema.MaterialSource` and
  :class:`~fdtd.provenance.schema.NonlinearModel` — these must already carry a
  reference, version, source kind, and a SHA-256 ``parameter_digest`` of an
  external artifact. The builder never fills in physical values; if the evidence
  is missing it **fails closed** (:class:`MissingEvidenceError`).

It emits a manifest that:

* records the deterministic geometry digest under ``geometry.geometry_hash``,
* carries the supplied material / nonlinear evidence verbatim,
* leaves ``candidate_family`` ``None`` (Astra's architecture call),
* leaves every convergence ladder **empty** and ``flex_credit`` **blank**
  (Astra's mesh / time / PML / cost decisions),
* lists no Tidy3D task ids (nothing has been submitted).

Running :func:`fdtd.provenance.validate.validate_study` on the result therefore
returns ``ok = False`` by design: it is a form pre-filled with the parts Claude
is allowed to prepare, handed to Astra for the evidence / maturity gate.
"""

from __future__ import annotations

from dataclasses import dataclass

from fdtd.provenance.schema import (
    CandidateStudyManifest,
    ConvergenceLadder,
    FlexCreditBudget,
    GeometryProvenance,
    LADDER_DIMENSIONS,
    MaterialSource,
    NonlinearModel,
    SOURCE_KINDS,
    looks_like_sha256,
)
from fdtd.provenance.schema import _blank as _is_blank

from .config import SimulationConfig
from .geometry import RingResonatorGeometry

REQUIRED_MATERIAL_FIELDS = (
    "name",
    "dispersion_model",
    "source_kind",
    "reference",
    "version",
    "retrieved_utc",
    "parameter_digest",
    "wavelength_range_um",
)

REQUIRED_NONLINEAR_FIELDS = (
    "model_type",
    "source_kind",
    "reference",
    "version",
    "parameter_digest",
    "applies_to_medium",
)


class MissingEvidenceError(RuntimeError):
    """Raised by the builder when required external evidence is absent/malformed."""

    def __init__(self, problems: list[str]):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


@dataclass
class StudyIdentity:
    """The non-physical identity of a study."""

    study_id: str
    created_utc: str
    tidy3d_version: str | None = None   # often unknown before Astra runs anything
    notes: str | None = None


class MicroringStudyBuilder:
    """Turn caller inputs into a partially-filled candidate-study manifest."""

    def __init__(
        self,
        *,
        identity: StudyIdentity,
        geometry: RingResonatorGeometry,
        config: SimulationConfig,
        material: MaterialSource,
        nonlinear: NonlinearModel,
        evidence_paths: list[str] | None = None,
        geometry_artifact: str | None = None,
    ) -> None:
        self.identity = identity
        self.geometry = geometry
        self.config = config
        self.material = material
        self.nonlinear = nonlinear
        self.evidence_paths = list(evidence_paths or [])
        self.geometry_artifact = geometry_artifact

    # -- deterministic digests --------------------------------------- #
    def geometry_digest(self) -> str:
        return self.geometry.digest()

    def config_digest(self) -> str:
        return self.config.digest()

    # -- evidence gate (fail closed) -------------------------------- #
    def evidence_problems(self) -> list[str]:
        """Everything the builder needs from outside and does not have."""
        problems: list[str] = []

        if not isinstance(self.material, MaterialSource):
            problems.append("material must be a MaterialSource record")
        else:
            for name in REQUIRED_MATERIAL_FIELDS:
                if _is_blank(getattr(self.material, name, None)):
                    problems.append(f"material.{name} is missing (must be supplied externally)")
            if not _is_blank(self.material.source_kind) and self.material.source_kind not in SOURCE_KINDS:
                problems.append(
                    f"material.source_kind {self.material.source_kind!r} not in {list(SOURCE_KINDS)}"
                )
            if not _is_blank(self.material.parameter_digest) and not looks_like_sha256(
                self.material.parameter_digest
            ):
                problems.append("material.parameter_digest is not a sha256 hex digest of an external file")

        if not isinstance(self.nonlinear, NonlinearModel):
            problems.append("nonlinear must be a NonlinearModel record")
        else:
            for name in REQUIRED_NONLINEAR_FIELDS:
                if _is_blank(getattr(self.nonlinear, name, None)):
                    problems.append(f"nonlinear.{name} is missing (must be supplied externally)")
            if not _is_blank(self.nonlinear.source_kind) and self.nonlinear.source_kind not in SOURCE_KINDS:
                problems.append(
                    f"nonlinear.source_kind {self.nonlinear.source_kind!r} not in {list(SOURCE_KINDS)}"
                )
            if not _is_blank(self.nonlinear.parameter_digest) and not looks_like_sha256(
                self.nonlinear.parameter_digest
            ):
                problems.append("nonlinear.parameter_digest is not a sha256 hex digest of an external file")

        # Cross-checks between the supplied evidence and the geometry labels.
        mat_name = getattr(self.material, "name", None)
        if not _is_blank(mat_name):
            if not _is_blank(self.nonlinear.applies_to_medium) and self.nonlinear.applies_to_medium != mat_name:
                problems.append(
                    f"nonlinear.applies_to_medium {self.nonlinear.applies_to_medium!r} "
                    f"!= material.name {mat_name!r}"
                )
            if self.geometry.core_medium != mat_name:
                problems.append(
                    f"geometry.core_medium {self.geometry.core_medium!r} != material.name {mat_name!r}"
                )

        problems.extend(f"geometry: {q}" for q in self.geometry.problems())
        problems.extend(f"config: {q}" for q in self.config.problems())
        return problems

    def require_evidence(self) -> None:
        problems = self.evidence_problems()
        if problems:
            raise MissingEvidenceError(problems)

    # -- manifest assembly ----------------------------------------- #
    def geometry_provenance(self) -> GeometryProvenance:
        return GeometryProvenance(
            geometry_hash=self.geometry_digest(),
            hash_algorithm="sha256",
            source_artifact=self.geometry_artifact,
            units="um",
            description=(
                "silicon microring add/drop resonator; canonical geometry document "
                f"digested by fdtd.mrr.geometry ({self.geometry.__class__.__name__})"
            ),
        )

    def _notes(self) -> str:
        head = f"{self.identity.notes.strip()} " if self.identity.notes else ""
        return (
            f"{head}MRR candidate-study inputs prepared by fdtd.mrr.MicroringStudyBuilder. "
            f"geometry_digest={self.geometry_digest()} config_digest={self.config_digest()}. "
            "INCOMPLETE BY DESIGN - Astra must still set: candidate_family; the mesh/time/pml "
            "convergence ladders (rungs + tolerance_rel); flex_credit (estimate + approved_ceiling); "
            "tidy3d_version; and submit Tidy3D tasks. Material and nonlinear parameter values are "
            "external and referenced here only by source + sha256 digest."
        )

    def build_manifest(self) -> CandidateStudyManifest:
        """Assemble the manifest. Fails closed if required evidence is absent."""
        self.require_evidence()
        return CandidateStudyManifest(
            study_id=self.identity.study_id,
            created_utc=self.identity.created_utc,
            candidate_family=None,               # Astra's architecture decision
            tidy3d_version=self.identity.tidy3d_version,
            notes=self._notes(),
            material=self.material,
            nonlinear=self.nonlinear,
            geometry=self.geometry_provenance(),
            ladders=[ConvergenceLadder(dimension=d) for d in LADDER_DIMENSIONS],  # empty: Astra fills
            flex_credit=FlexCreditBudget(),      # blank: Astra sets estimate + ceiling
            task_ids=[],                          # nothing submitted
            evidence_paths=list(self.evidence_paths),
        )
