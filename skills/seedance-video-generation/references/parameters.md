# 参数参考

## 创建任务参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | string | `doubao-seedance-1-5-pro-251215` | 使用的型号 ID |
| `content` | array | **必填** | 内容数组，包含文本和图片 |
| `ratio` | string | `16:9` (T2V) / `adaptive` (I2V) | 宽高比 |
| `duration` | integer | `5` | 视频时长（秒） |
| `resolution` | string | `720p` | 分辨率 |
| `seed` | integer | `-1` | 随机种子 |
| `watermark` | boolean | `false` | 添加水印 |
| `generate_audio` | boolean | `true` | 生成音频（仅 1.5 Pro） |
| `draft` | boolean | `false` | 草稿模式（仅 1.5 Pro） |
| `return_last_frame` | boolean | `false` | 返回尾帧 URL |
| `service_tier` | string | `default` | 服务层级 |
| `execution_expires_after` | integer | `172800` | 任务超时（秒） |

## 参数详解

### ratio（宽高比）

可选值：
- `16:9` - 横向（默认文生视频）
- `4:3` - 横向
- `1:1` - 正方形
- `3:4` - 竖向
- `9:16` - 竖向（短视频）
- `21:9` - 超宽屏
- `adaptive` - 自适应（默认图生视频，根据输入图片自动调整）

### duration（时长）

| 型号 | 范围 | 说明 |
|------|------|------|
| Seedance 1.5 Pro | 4-12 或 -1 | -1 表示自动 |
| 其他型号 | 2-12 | 固定时长 |

### resolution（分辨率）

| 值 | 说明 |
|----|------|
| `480p` | 草稿模式强制使用 |
| `720p` | 默认 |
| `1080p` | 高清 |

### seed（随机种子）

| 值 | 说明 |
|-----|------|
| `-1` | 随机生成（默认） |
| 其他正整数 | 复现相同结果 |

### generate_audio（生成音频）

- `true` - 生成同步音频（AI 配乐 + 音效）
- `false` - 无声视频

**仅 Seedance 1.5 Pro 支持。**

### service_tier（服务层级）

| 值 | 说明 | 价格 |
|----|------|------|
| `default` | 在线服务 | 标准 |
| `flex` | 离线服务 | 便宜约 50%，生成更慢 |

### execution_expires_after（超时时间）

- 范围：3600 - 259200 秒（1 小时 - 3 天）
- 默认：172800 秒（48 小时）

## content 数组结构

### 文本

```json
{
  "type": "text",
  "text": "你的提示词"
}
```

### 图片（首帧）

```json
{
  "type": "image_url",
  "image_url": { "url": "图片URL或base64" },
  "role": "first_frame"
}
```

### 图片（尾帧）

```json
{
  "type": "image_url",
  "image_url": { "url": "尾帧图片URL" },
  "role": "last_frame"
}
```

### 图片（参考图）

```json
{
  "type": "image_url",
  "image_url": { "url": "参考图URL" },
  "role": "reference_image"
}
```

### 草稿任务引用

```json
{
  "type": "draft_task",
  "draft_task": { "id": "草稿任务ID" }
}
```

## 相关文档

- [API 参考](./api.md) - 详细的 API 调用示例
- [型号参考](./models.md) - 型号对比
- [高级用法](./advanced.md) - 连续视频、草稿模式等
