# 使用指南

## 快速体检

运行 `mm-music-refiner analyze INPUT --output PROJECT`。输出目录必须为空，以避免覆盖已有工程。加 `--snapshot` 会把源文件复制到 `originals/` 并设为只读。

先看 `report.html` 或 `report.md`，再用 `issues.json` 对接工具。BPM、Key 和 Tuning 都带置信度；低置信时应人工核听，不把估算当事实。

## 模式边界

当前版本只实现快速体检，不修改音频。保守、均衡、深度与 DAW 方案的风险规则已经在 Skill 中定义，但自动修复必须等 A/B、Edit Manifest 和回归测试闭环完成后才开放。

有损输入会保留诊断，但应尽量回到 WAV/FLAC。复杂人声、错词、和声内容和结构问题不应使用 EQ 伪修复，应重唱、局部再生成或人工编辑。
