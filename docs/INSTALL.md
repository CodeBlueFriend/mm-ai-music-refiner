# 安装

## macOS Apple Silicon

安装 Python 3.10+ 与 FFmpeg（Homebrew：`brew install ffmpeg`），建立虚拟环境后运行 `python -m pip install -e .`。基础扫描使用 CPU，无需 PyTorch 或 MPS。

## Windows

安装 Python 3.10+，将可信 FFmpeg 构建的 `ffmpeg.exe` 与 `ffprobe.exe` 加入 PATH，再在 PowerShell 虚拟环境运行 `python -m pip install -e .`。

## 离线与卸载

当前版本没有模型下载和网络调用。离线可完成全部扫描。卸载 Python 包并删除用户自行创建的项目目录即可；原始音频不会被修改或自动删除。

安装 Skill 时，把 `skills/mm-ai-music-refiner` 复制到 `~/.codex/skills/`。仓库引擎与 Skill 可分别安装；执行分析需要本仓库或已安装的命令行包。
