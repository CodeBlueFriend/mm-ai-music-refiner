from __future__ import annotations

from typing import Any


def issue(issue_id: str, metric_id: str, category: str, severity: str, confidence: float, audibility: str, title: str, evidence: dict[str, Any], causes: list[str], risk: str, actions: list[str]) -> dict[str, Any]:
    return {
        "issue_id": issue_id,
        "metric_id": metric_id,
        "category": category,
        "start_sec": 0.0,
        "end_sec": None,
        "stem": "master",
        "severity": severity,
        "confidence": confidence,
        "audibility": audibility,
        "title_zh": title,
        "evidence": evidence,
        "possible_causes": causes,
        "auto_fix_level": risk,
        "recommended_actions": actions,
        "status": "proposed",
    }


def build_issues(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = analysis["metadata"]
    metrics = analysis["metrics"]
    result: list[dict[str, Any]] = []
    counter = 1
    def add(*args, **kwargs):
        nonlocal counter
        result.append(issue(f"iss_{counter:03d}", *args, **kwargs))
        counter += 1
    if metadata.get("lossy"):
        add("file.codec.lossy_source", "file", "low", 1.0, "context", "输入为有损编码源", {"codec": metadata.get("codec"), "bit_rate_bps": metadata.get("bit_rate_bps")}, ["平台下载格式", "重复转码", "分享版而非母带"], "D", ["优先找到 WAV/FLAC 源文件", "若只能使用当前文件，避免再次有损中间导出"])
    clipping = metrics.get("clipped_sample_ratio") or 0.0
    if clipping > 0.00001:
        add("level.clipped_sample_ratio", "loudness", "high" if clipping > 0.001 else "medium", 0.98, "high", "检测到接近数字满幅的样本", {"clipped_sample_ratio": clipping}, ["削波", "硬限制", "有损解码峰值"], "B", ["核听高能量段落", "从上游工程降低电平", "必要时使用保守去削波并生成 A/B"])
    true_peak = metrics.get("true_peak_dbfs")
    if true_peak is not None and true_peak > -1.0:
        add("level.true_peak_dbfs", "loudness", "medium", 0.96, "medium", "True Peak 余量偏低", {"true_peak_dbfs": true_peak}, ["限制器上限过高", "编码间峰值"], "A", ["导出前设置 True Peak 保护", "重新测量编码后峰值"])
    dc = abs(metrics.get("dc_offset") or 0.0)
    if dc > 0.002:
        add("signal.dc_offset", "technical", "low", 0.95, "low", "存在可测 DC Offset", {"dc_offset": metrics.get("dc_offset")}, ["录音链偏置", "处理器偏置"], "A", ["使用 DC blocking filter", "修复后验证低频与波形中心"])
    tuning = metrics.get("tuning_offset_cents")
    tuning_conf = metrics.get("tuning_confidence") or 0.0
    if tuning is not None and abs(tuning) >= 15 and tuning_conf >= 0.25:
        add("pitch.global_tuning_offset_cents", "pitch", "low", tuning_conf, "context", "检测到可能的全局定音偏移", {"tuning_offset_cents": tuning, "confidence": tuning_conf}, ["非 A4=440 定音", "整体移调处理", "估算误差"], "C", ["先确认作品是否有意使用其他定音", "不要把全局定音偏移报告为调性错误"])
    if (metrics.get("bpm_confidence") or 0.0) < 0.15:
        add("rhythm.bpm_confidence", "rhythm", "low", 0.8, "context", "BPM 快速估算置信度较低", {"bpm": metrics.get("bpm"), "confidence": metrics.get("bpm_confidence")}, ["自由速度", "弱瞬态", "半倍/双倍速度歧义"], "D", ["人工 Tap Tempo", "在分轨或高分辨率模式重新分析"])
    return result
