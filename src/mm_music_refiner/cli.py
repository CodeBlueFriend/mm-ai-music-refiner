from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .audio import AnalysisError, analyze_audio
from .issues import build_issues
from .report import html_report, markdown_report


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="mm-music-refiner", description="Local-first, non-destructive music diagnostics")
    root.add_argument("--version", action="version", version=__version__)
    sub = root.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Create a quick-scan project and reports")
    analyze.add_argument("audio", type=Path)
    analyze.add_argument("--output", type=Path, required=True)
    analyze.add_argument("--name")
    analyze.add_argument("--snapshot", action="store_true", help="Copy the source into a read-only originals directory")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "analyze":
        try:
            return analyze_command(args)
        except AnalysisError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
    return 1


def analyze_command(args: argparse.Namespace) -> int:
    source = args.audio.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise AnalysisError(f"Output path must be an empty directory: {output.name}")
    output.mkdir(parents=True, exist_ok=True)
    analysis = analyze_audio(source)
    issues = build_issues(analysis)
    project = {
        "schema_version": "1.0.0",
        "project_id": "prj_" + analysis["source"]["sha256"][:12],
        "name": args.name or source.stem,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "quick_scan",
        "source": analysis["source"],
        "source_snapshot": None,
        "provenance": {"c2pa_status": "not_checked", "unknown_watermark_status": "unknown"},
        "engine_version": __version__,
    }
    if args.snapshot:
        original_dir = output / "originals"
        original_dir.mkdir()
        snapshot = original_dir / source.name
        shutil.copy2(source, snapshot)
        snapshot.chmod(0o444)
        project["source_snapshot"] = str(Path("originals") / source.name)
    _json(output / "project.json", project)
    _json(output / "analysis.json", analysis)
    _json(output / "issues.json", {"schema_version": "1.0.0", "issues": issues})
    report = markdown_report(project, analysis, issues)
    (output / "report.md").write_text(report, encoding="utf-8")
    (output / "report.html").write_text(html_report(report), encoding="utf-8")
    print(json.dumps({"project": str(output), "issues": len(issues), "source_modified": False}, ensure_ascii=False))
    return 0


def _json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
