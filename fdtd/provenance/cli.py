"""Command-line entry point for the candidate-study provenance scaffold.

    python -m fdtd.provenance template  [--out PATH]
    python -m fdtd.provenance validate  --manifest PATH [--json]
    python -m fdtd.provenance digest    PATH

``validate`` exits 0 only when every required provenance check passes
(fail-closed). ``template`` emits a blank manifest for Astra to fill; it
deliberately does not validate. ``digest`` prints the SHA-256 of a local file
so a parameter / geometry artifact can be referenced by hash.

Nothing here talks to Tidy3D or the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .schema import CandidateStudyManifest, blank_manifest, sha256_file
from .validate import validate_study


def cmd_template(args: argparse.Namespace) -> int:
    text = blank_manifest().to_json()
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.manifest)
    if not path.exists():
        print(f"manifest not found: {path}")
        return 2
    try:
        manifest = CandidateStudyManifest.from_json(path.read_text(encoding="utf-8"))
    except (ValueError, TypeError) as exc:
        print(f"manifest is not readable: {exc}")
        return 2

    report = validate_study(manifest)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(report.format_text())
    return 0 if report.ok else 1


def cmd_digest(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"file not found: {path}")
        return 2
    print(f"{sha256_file(path)}  {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fdtd.provenance")
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("template", help="emit a blank study manifest to fill in")
    t.add_argument("--out", help="write to this path instead of stdout")
    t.set_defaults(func=cmd_template)

    v = sub.add_parser("validate", help="fail-closed validation of a study manifest")
    v.add_argument("--manifest", required=True, help="path to the manifest JSON")
    v.add_argument("--json", action="store_true", help="emit the report as JSON")
    v.set_defaults(func=cmd_validate)

    d = sub.add_parser("digest", help="print the SHA-256 of a local evidence file")
    d.add_argument("path")
    d.set_defaults(func=cmd_digest)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
