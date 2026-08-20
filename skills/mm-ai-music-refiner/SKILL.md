---
name: mm-ai-music-refiner
description: Diagnose finished or stemmed music locally, build an explainable time-aware issue list, plan non-destructive repairs, render reports, and guide conservative, balanced, deep, or DAW-only workflows. Use for WAV, FLAC, MP3, M4A/AAC audio inspection; loudness, peak, tempo, key, tuning, clipping, encoding, vocal, spectral, structure, mix, stem, repair, preview, export, or edit-manifest tasks. Do not use to evade AI detectors, remove watermarks, forge provenance, or claim binary AI authorship.
---

# MM AI Music Refiner

Treat the original as read-only. Diagnose quality and production evidence; do not infer authorship from one feature.

## Route the task

- Use **quick scan** for a non-modifying technical and musical report.
- Use **conservative optimization** only for high-confidence, low-risk repairs with previews and an edit manifest.
- Use **workbench guidance** for issue-by-issue accept, reject, strength, A/B, and export decisions.
- Use **DAW-only plan** when the user wants timecodes, plugin types, parameter ranges, reasons, and listening checks without audio processing.

## Workflow

1. Confirm inputs, goal, target format, prohibited changes, and whether stems or lyrics exist.
2. Validate the file and preserve its hash, metadata, and readable provenance state.
3. Run the local engine for deterministic metrics. Use `python scripts/run_diagnosis.py <audio> --output <project-dir>` when the repository engine is available.
4. Separate measured facts, algorithm estimates, and listening hypotheses.
5. Create issues with category, range, severity, confidence, audibility, possible causes, risk level, and recommended actions.
6. Rank with severity × confidence × audibility × goal relevance × fixability; explain high/medium/low rather than a mysterious total score.
7. Prefer local, reversible edits. Require confirmation for pitch, timing, formant, width, structure, or other style-changing work.
8. Re-measure after repair, loudness-match A/B previews, retain rejected suggestions, and never overwrite the source.

## Safety and provenance

Do not optimize against detector scores, add random noise or timing jitter as “humanization,” attack unknown watermarks, copy invalid credentials, or produce a human-authorship certificate. Report undetectable or proprietary provenance as unknown.

## Resources

- Read [references/metrics-and-issues.md](references/metrics-and-issues.md) when interpreting metrics or writing issues.
- Read [references/repair-policy.md](references/repair-policy.md) before proposing or executing edits.
- Read [references/provenance-and-privacy.md](references/provenance-and-privacy.md) for local-file and credential handling.

If a required engine, model, or stem is unavailable, degrade explicitly and still provide the safe portion of the report.
