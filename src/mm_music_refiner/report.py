from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def markdown_report(project: dict[str, Any], analysis: dict[str, Any], issues: list[dict[str, Any]]) -> str:
    meta = analysis["metadata"]
    metrics = analysis["metrics"]
    rows = [
        ("文件", analysis["source"]["filename"]),
        ("SHA-256", analysis["source"]["sha256"]),
        ("格式/编码", f"{meta.get('container')} / {meta.get('codec')}"),
        ("采样率/声道", f"{meta.get('sample_rate_hz')} Hz / {meta.get('channels')}"),
        ("时长", _fmt(meta.get("duration_sec"), "s")),
        ("Integrated loudness", _fmt(metrics.get("integrated_lufs"), "LUFS")),
        ("True Peak", _fmt(metrics.get("true_peak_dbfs"), "dBFS")),
        ("BPM", _estimate(metrics.get("bpm"), metrics.get("bpm_confidence"))),
        ("Key", _estimate(metrics.get("key"), metrics.get("key_confidence"))),
        ("Tuning", _estimate(_fmt(metrics.get("tuning_offset_cents"), "cent"), metrics.get("tuning_confidence"))),
    ]
    lines = [
        f"# {project['name']} — 快速体检报告",
        "",
        "> 本报告描述音频质量与处理证据，不证明作品由真人或 AI 创作。快速体检没有修改输入文件。",
        "",
        "## 摘要",
        "",
        f"发现 {len(issues)} 个需关注项目；输入源为{'有损' if meta.get('lossy') else '无损或 PCM'}编码。",
        "",
        "## 技术与音乐估算",
        "",
        "| 项目 | 结果 |",
        "|---|---|",
        *[f"| {name} | {value} |" for name, value in rows],
        "",
        "## 问题清单",
        "",
    ]
    if not issues:
        lines.append("当前快速扫描未发现达到规则阈值的问题；这不等于音频没有听感问题。")
    for item in issues:
        lines.extend([
            f"### {item['issue_id']} · {item['title_zh']}",
            "",
            f"- 分类/优先级：{item['category']} / {item['severity']}",
            f"- 置信度/可听性：{item['confidence']} / {item['audibility']}",
            f"- 风险等级：{item['auto_fix_level']}",
            f"- 证据：`{json.dumps(item['evidence'], ensure_ascii=False)}`",
            "- 建议：" + "；".join(item["recommended_actions"]),
            "",
        ])
    lines.extend(["## 已知局限", "", *[f"- {item}" for item in analysis["limitations"]], "", f"引擎版本：{analysis['engine_version']}；Schema：{analysis['schema_version']}。", ""])
    return "\n".join(lines)


def html_report(markdown: str) -> str:
    escaped = html.escape(markdown)
    return "<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>MM Music Refiner Report</title><style>body{max-width:900px;margin:40px auto;padding:0 24px;font:16px/1.65 system-ui;color:#17202a;background:#f7f8fa}pre{white-space:pre-wrap;background:white;padding:28px;border-radius:14px;box-shadow:0 5px 24px #0001}</style><pre>" + escaped + "</pre></html>"


def _fmt(value: Any, unit: str) -> str:
    if value is None:
        return "不可用"
    if isinstance(value, float):
        return f"{value:.2f} {unit}"
    return f"{value} {unit}"


def _estimate(value: Any, confidence: Any) -> str:
    return f"{value if value is not None else '不可用'}（置信度 {float(confidence or 0):.2f}）"
