# 版本记录

本项目采用语义化版本。`0.x` 表示分析结果、Schema 和命令行接口仍可能在迁移说明下调整。

## v0.1.0 — 2026-08-20

### 已交付

- 首个可安装的 `mm-ai-music-refiner` Codex Skill；
- 本地 `mm-music-refiner analyze` 命令行入口；
- FFprobe 文件/编码探测与 SHA-256；
- EBU R128 Integrated LUFS、LRA 和 True Peak；
- Sample Peak、RMS、Crest Factor、DC Offset 与削波比例；
- 快速 BPM、Key 和相对 A4=440 Tuning Offset 估算及置信度；
- 有损来源、True Peak、Clipping、DC、Tuning 和低置信 BPM 的 Issue 规则；
- `project.json`、`analysis.json`、`issues.json`、Markdown/HTML 报告；
- 可选只读原件快照；
- Project、Issue 与 Edit Manifest JSON Schema；
- 3 项单元/端到端测试、Skill 验证及安装/使用/开发/指标/隐私/许可证文档。

### 已知限制

- BPM、Key 与 Tuning 是快速估算，复杂节奏、转调、弱瞬态或无调性材料会低置信；
- 当前不执行分轨、人声转写、音频修复、A/B 或最终母带导出；
- 当前 C2PA 状态为 `not_checked`，未知水印状态为 `unknown`；
- HTML 报告以可靠离线阅读为目标，尚无交互时间轴；
- FFmpeg 由用户系统提供，发布安装包前必须固定构建和许可证。

### 兼容性

- Python 3.10+；
- FFmpeg/ffprobe；
- macOS Apple Silicon 为一级验证环境；Windows/Linux 具备 CLI 运行路径但尚未形成完整发布矩阵。
