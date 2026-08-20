# mm-ai-music-refiner

本地优先、可解释、非破坏的 AI 音乐质量诊断与优化项目。当前仓库交付设计基线的第一个完整垂直切片：导入音频，读取技术参数，计算响度/峰值与基础音乐估算，生成统一 Issue JSON、Markdown/HTML 报告，并保证不修改源文件。

> 当前版本：`v0.1.0` · 状态：快速体检 MVP · 首发环境：macOS Apple Silicon

## 产品能力一览

| 用户输入 | 产品能力 | 直接输出 |
|---|---|---|
| WAV、FLAC、MP3、M4A/AAC 等音频 | 读取容器、编码、采样率、声道、时长、码率并计算 SHA-256 | 可审计的项目输入记录 |
| 整首歌曲 | 测量 Integrated LUFS、LRA、True Peak、Sample Peak、RMS、Crest Factor、DC Offset 与削波比例 | 技术质量分析 JSON |
| 有明确节奏与调性的音乐 | 快速估算 BPM、Key、相对 A4=440 的 Tuning Offset | 带置信度的音乐参数 |
| 检测到的异常 | 结合严重度、置信度、可听性、原因与修复风险生成问题对象 | 结构化 Issue 清单 |
| 一次快速体检任务 | 建立项目事实源并渲染结果 | `project.json`、`analysis.json`、`issues.json`、Markdown/HTML 报告 |
| 需要保存原件的项目 | 创建源文件副本并设置只读权限 | 可选 `originals/` 快照 |

当前版本完成的是：**导入 → 测量 → 解释 → Issue → 报告**。源音频不会被覆盖；分轨、自动修复、A/B 和多轨工作台属于后续版本。

## 设计思路

产品不提供一个神秘的“去 AI 总分”，而是建立可复核的工程链路：**定位问题 → 展示证据 → 给出风险等级 → 生成非破坏方案 → A/B → 导出与审计**。

核心原则：

- **原件只读**：任何分析或后续处理都不能覆盖源音频；
- **事实分层**：技术测量、算法估算和听感假设分别展示；
- **问题可解释**：每个 Issue 保留指标、置信度、原因、风险和建议；
- **修复分级**：安全自动、预览后自动、必须确认、人工/重生成四级；
- **本地优先**：默认不上传未发布作品，代理与缓存位于受控目录；
- **来源透明**：不规避检测、不移除水印、不伪造 Content Credentials。

完整架构、数据模型、处理流程和阶段路线见 [设计说明](docs/DESIGN.md)。

## 已实现

- WAV、FLAC、MP3、M4A/AAC 等 FFmpeg 可解码输入；
- SHA-256、容器、编码、采样率、声道、时长和有损来源提示；
- EBU R128 Integrated LUFS、LRA、True Peak；
- Sample Peak、RMS、Crest Factor、DC Offset、削波样本比例；
- 快速 BPM、Key、相对 A4=440 的 Tuning Offset 估算及置信度；
- 统一 `project.json`、`analysis.json`、`issues.json`、Markdown/HTML 报告；
- 可选只读原件快照；
- 可独立安装的 Codex Skill 与 Issue/Edit/Project Schema。

## 快速开始

要求 Python 3.10+ 和 `ffmpeg`/`ffprobe`：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
mm-music-refiner analyze /path/to/song.wav --output /path/to/project --snapshot
```

也可不安装包：

```bash
PYTHONPATH=src python3 -m mm_music_refiner analyze /path/to/song.mp3 --output /path/to/project
```

一次分析会生成：

```text
project/
├── project.json      # 项目、输入哈希、模式和来源状态
├── analysis.json     # 技术测量与音乐估算
├── issues.json       # 结构化问题清单
├── report.md         # Markdown 报告
├── report.html       # 可直接打开的 HTML 报告
└── originals/        # 仅在 --snapshot 时创建的只读原件
```

## 产品边界

本项目诊断听感和制作质量，不输出二元 AI 鉴定，不优化检测器分数，不移除水印，不伪造来源。当前版本不包含分轨、自动音频修复、多轨 UI 或 C2PA 验证；这些能力已有 Schema 与安全接口边界，但会在通过黄金音频测试后逐步实现。

## 文档

- [设计说明](docs/DESIGN.md)
- [安装](docs/INSTALL.md)
- [使用指南](docs/USER_GUIDE.md)
- [架构与开发](docs/DEVELOPMENT.md)
- [指标词典](docs/METRICS.md)
- [隐私与来源](docs/PRIVACY_AND_PROVENANCE.md)
- [第三方许可证](docs/THIRD_PARTY_LICENSES.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [版本记录](CHANGELOG.md)

## 版本范围

`v0.1.0` 完成“导入 → 测量 → Issue → 报告”的第一个可复现闭环。分轨、自动音频修复、局部 A/B、FastAPI、React/Tauri 多轨工作台和 C2PA 验证仍在后续路线中，不属于当前已交付能力。

Copyright © 2026 CodeBlueFriend. All rights reserved.
