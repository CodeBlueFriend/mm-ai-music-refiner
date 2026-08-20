# mm-ai-music-refiner

本地优先、可解释、非破坏的 AI 音乐质量诊断与优化项目。当前仓库交付设计基线的第一个完整垂直切片：导入音频，读取技术参数，计算响度/峰值与基础音乐估算，生成统一 Issue JSON、Markdown/HTML 报告，并保证不修改源文件。

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

## 产品边界

本项目诊断听感和制作质量，不输出二元 AI 鉴定，不优化检测器分数，不移除水印，不伪造来源。当前版本不包含分轨、自动音频修复、多轨 UI 或 C2PA 验证；这些能力已有 Schema 与安全接口边界，但会在通过黄金音频测试后逐步实现。

## 文档

- [安装](docs/INSTALL.md)
- [使用指南](docs/USER_GUIDE.md)
- [架构与开发](docs/DEVELOPMENT.md)
- [指标词典](docs/METRICS.md)
- [隐私与来源](docs/PRIVACY_AND_PROVENANCE.md)
- [第三方许可证](docs/THIRD_PARTY_LICENSES.md)
- [故障排除](docs/TROUBLESHOOTING.md)

Copyright © 2026 CodeBlueFriend. All rights reserved.
