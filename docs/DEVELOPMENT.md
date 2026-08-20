# 架构与开发

`src/mm_music_refiner` 分为音频探测/测量、Issue 规则、报告和 CLI。运行时只依赖 Python 标准库和外部 FFmpeg。代理音频写入受控临时目录，完成后自动清理。

分析器接口目标为 `analyze(context) -> metrics + issues`；后续修复器遵循 `propose`、`preview`、`render`，所有操作写 Edit Manifest。每个新指标必须先定义 ID、单位、窗口、适用条件、误报、修复映射与测试。每个依赖同时更新第三方许可证。

运行测试：`PYTHONPATH=src python3 -m unittest discover -s tests -v`。对 3–5 分钟合法音频建立黄金结果时，应使用容差而非逐字节比较浮点值。

后续顺序：时间码异常与 HTML 可视化 → 高置信 Click/Peak 修复与 A/B → 4-stem 可选后端 → 本地 API → React/Tauri 工作台。不得在验证前一次性引入全部模型。
