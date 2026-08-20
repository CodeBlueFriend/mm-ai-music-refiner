# 指标词典（v0.1）

| Metric ID | 单位 | 用途 | 主要误区 |
|---|---:|---|---|
| `file.codec.lossy_source` | bool | 标记有损来源与重复转码风险 | 有损不等于质量一定不可用 |
| `level.integrated_lufs` | LUFS | 全曲节目响度 | 不同用途没有一个全球统一目标 |
| `level.true_peak_dbfs` | dBFS | 编码间峰值与导出余量 | Sample Peak 不能代替 True Peak |
| `level.sample_peak_dbfs` | dBFS | 代理 PCM 峰值 | 有损解码可能产生新峰值 |
| `level.clipped_sample_ratio` | ratio | 满幅/近满幅样本比例 | 强限制不一定等于可听削波 |
| `signal.dc_offset` | linear | 波形中心偏移 | 极小值通常不可听 |
| `rhythm.bpm` | BPM | 快速速度估算 | 半倍、双倍、自由速度会歧义 |
| `tonality.key` | label | 快速调性候选 | 单音、调式和转调会低置信 |
| `pitch.global_tuning_offset_cents` | cent | 相对 A4=440 定音偏移 | 定音偏移不是调性错误 |

v0.1 只启用经过单元测试的垂直切片指标；不以数量冒充生产可靠性。
