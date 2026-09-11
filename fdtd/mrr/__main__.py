"""Command-line entry point for the local linear-simulation translation layer.

    python -m fdtd.mrr plan   --input bundle.json [--out plan.json]
    python -m fdtd.mrr dryrun --plan  plan.json  [--json]
    python -m fdtd.mrr dryrun --input bundle.json [--json]

``plan`` translates a fully-evidenced MRR study bundle into a canonical linear
``tidy3d.Simulation`` plan document and prints its SHA-256 digest. ``dryrun``
runs the local dry-run validator and exits 0 only when the plan is complete,
internally consistent, evidence-backed and free of nonlinear / cloud content.

Nothing here imports Tidy3D or touches the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .linear_dryrun import dry_run
from .linear_sim import (
    LinearSimulationPlan,
    LinearSimulationTranslator,
    MissingLinearEvidenceError,
    TranslationError,
)


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _translate(input_path: str) -> LinearSimulationPlan:
    translator = LinearSimulationTranslator.from_bundle(_load_json(input_path))
    return translator.translate()


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        plan = _translate(args.input)
    except (MissingLinearEvidenceError, TranslationError) as exc:
        print(f"cannot translate bundle: {exc}")
        return 2
    text = plan.to_json()
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    print(f"plan_digest {plan.digest()}")
    return 0


def cmd_dryrun(args: argparse.Namespace) -> int:
    if bool(args.plan) == bool(args.input):
        print("pass exactly one of --plan or --input")
        return 2
    try:
        if args.input:
            doc = _translate(args.input).to_document()
        else:
            doc = _load_json(args.plan)
    except (MissingLinearEvidenceError, TranslationError) as exc:
        print(f"cannot build plan: {exc}")
        return 2

    report = dry_run(doc)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(report.format_text())
    return 0 if report.ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fdtd.mrr")
    sub = p.add_subparsers(dest="command", required=True)

    pl = sub.add_parser("plan", help="translate a study bundle into a linear Simulation plan")
    pl.add_argument("--input", required=True, help="path to the study bundle JSON")
    pl.add_argument("--out", help="write the plan JSON here instead of stdout")
    pl.set_defaults(func=cmd_plan)

    dr = sub.add_parser("dryrun", help="fail-closed local dry run of a linear Simulation plan")
    dr.add_argument("--plan", help="path to an existing plan JSON")
    dr.add_argument("--input", help="path to a study bundle JSON (translated then dry-run)")
    dr.add_argument("--json", action="store_true", help="emit the report as JSON")
    dr.set_defaults(func=cmd_dryrun)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
