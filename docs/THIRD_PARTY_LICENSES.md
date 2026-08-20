# 第三方许可证

运行时不包含或再分发第三方 Python 包。

项目调用用户系统中的 FFmpeg/ffprobe。FFmpeg 的许可取决于具体构建配置，可能是 LGPL 或在启用相关组件时为 GPL；发布安装包前必须固定构建、保存 `ffmpeg -buildconf`、附上对应许可证和源码提供方式。

当前版本不捆绑 Essentia、Demucs、Basic Pitch、Rubber Band、模型权重或 VST/AU 插件。引入任何组件前必须分别核验代码、模型和商业分发权利。
