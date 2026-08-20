#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description="Run the MM AI Music Refiner local engine")
parser.add_argument("audio", type=Path)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--snapshot", action="store_true")
args = parser.parse_args()

skill_dir = Path(__file__).resolve().parents[1]
repo_root = skill_dir.parents[1]
source_dir = repo_root / "src"
if source_dir.exists():
    command = [sys.executable, "-m", "mm_music_refiner", "analyze", str(args.audio), "--output", str(args.output)]
    if args.snapshot:
        command.append("--snapshot")
    env = __import__("os").environ.copy()
    env["PYTHONPATH"] = str(source_dir) + __import__("os").pathsep + env.get("PYTHONPATH", "")
    raise SystemExit(subprocess.call(command, env=env))

print("Local engine not found beside the installed Skill. Install the mm-ai-music-refiner repository, then run `mm-music-refiner analyze ...`.", file=sys.stderr)
raise SystemExit(2)
