# Seedance 型号参考

## 型号对比表

| 型号 | Model ID | 文生视频 | 图生视频 | 首帧 | 首尾帧 | 参考图 | 音频 | 草稿模式 |
|------|----------|:--------:|:--------:|:----:|:------:|:------:|:----:|:--------:|
| Seedance 1.5 Pro | `doubao-seedance-1-5-pro-251215` | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| Seedance 1.0 Pro | `doubao-seedance-1-0-pro-250428` | ✅ | ✅ | ✅ | ✅ | - | - | - |
| Seedance 1.0 Pro Fast | `doubao-seedance-1-0-pro-fast-250528` | ✅ | ✅ | ✅ | - | - | - | - |
| Seedance 1.0 Lite T2V | `doubao-seedance-1-0-lite-t2v-250219` | ✅ | - | - | - | - | - | - |
| Seedance 1.0 Lite I2V | `doubao-seedance-1-0-lite-i2v-250219` | - | ✅ | ✅ | ✅ | ✅ (1-4张) | - | - |

## 视频参数限制

| 型号 | 时长范围 | 分辨率支持 | 宽高比支持 |
|------|----------|------------|------------|
| Seedance 1.5 Pro | 4-12 秒（可设 -1 自动） | 480p, 720p, 1080p | 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive |
| Seedance 1.0 Pro | 2-12 秒 | 480p, 720p, 1080p | 16:9, 4:3, 1:1, 3:4, 9:16, adaptive |
| Seedance 1.0 Pro Fast | 2-12 秒 | 480p, 720p, 1080p | 16:9, 4:3, 1:1, 3:4, 9:16, adaptive |
| Seedance 1.0 Lite | 2-12 秒 | 480p, 720p | 16:9, 4:3, 1:1, 3:4, 9:16 |

## 型号选择建议

### 推荐：Seedance 1.5 Pro
- **默认选择**，最新版本，功能最全
- 支持音频生成（AI 配乐与音效）
- 支持草稿模式（低成本预览）
- 支持最长 12 秒视频
- 支持自动时长（`duration: -1`）

### 场景选择

| 场景 | 推荐型号 |
|------|----------|
| 快速预览/低成本测试 | Seedance 1.5 Pro + 草稿模式 |
| 追求性价比 | Seedance 1.0 Pro Fast |
| 预算有限，仅文生视频 | Seedance 1.0 Lite T2V |
| 预算有限，需要图生视频 | Seedance 1.0 Lite I2V |
| 需要多张参考图 | Seedance 1.0 Lite I2V |
| 需要生成配乐 | Seedance 1.5 Pro |

## 默认值

| 参数 | 文生视频默认值 | 图生视频默认值 |
|------|----------------|----------------|
| 型号 | `doubao-seedance-1-5-pro-251215` | `doubao-seedance-1-5-pro-251215` |
| 分辨率 | 720p | 720p |
| 宽高比 | 16:9 | adaptive |
| 时长 | 5 秒 | 5 秒 |
| 生成音频 | true | true |

## 相关文档

- [API 参考](./api.md) - 详细的 API 调用示例
- [参数参考](./parameters.md) - 完整参数说明
- [高级用法](./advanced.md) - 连续视频、草稿模式等
