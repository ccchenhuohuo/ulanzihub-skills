---
name: seedream
description: 使用火山引擎 Seedream-4.5 API 生成高质量图片。适用于文生图、图生图以及生成关联组图的场景。
---

# Seedream

本 Skill 封装了火山引擎（Volcengine）的 Seedream-4.5 图片生成能力，支持通过文本提示词或参考图生成高质量 AI 图像。

## 使用方法

### 文生图
生成单张图片：
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "一只赛博朋克风格的猫"
```

指定分辨率：
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "壮丽的山川日出" --size "2K"
```

### 图生图
提供参考图片 URL（需先上传到腾讯 COS）：
```bash
# 先上传参考图到 COS
uv run {baseDir}/scripts/cos_upload.py --file /path/to/image.jpg
# 返回 COS 预签名 URL

# 再调用图生图
uv run {baseDir}/scripts/generate_image.py --prompt "将其风格变为印象派" --image "COS_URL"
```

### 生成组图
生成一组内容关联的图片（最多 15 张）：
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "一个宇航员在不同行星上的探险经历" --sequential --max-images 4
```

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `VOLC_API_KEY` | 火山引擎 API Key（必填） |
| `TENCENT_COS_SECRET_ID` | 腾讯云 SecretId（图生图上传参考图用） |
| `TENCENT_COS_SECRET_KEY` | 腾讯云 SecretKey |
| `TENCENT_COS_REGION` | COS 区域（如 ap-guangzhou） |
| `TENCENT_COS_BUCKET` | COS Bucket 名称 |

## 工作流

### 统一流程

**前置步骤（图生图才有）**
- 用户提供参考图片时，先上传到腾讯 COS：
  - 执行 `cos_upload.py --file /root/.openclaw/media/inbound/xxx.jpg`
  - 获取 COS 预签名 URL

**核心步骤（文生图和图生图共有）**

1. **调用生成脚本**
   - 执行 `generate_image.py --prompt "提示词" [--image "参考图URL"]`
   - 图生图需要传入 `--image` 参数带上参考图 URL

2. **获取 API 返回**
   - API 返回带签名的图片 URL
   - 格式：`https://ark-content-generation-v2-cn-beijing.tos-cn-beijing.volces.com/xxx.jpeg?X-Tos-Algorithm=...`

3. **自动下载图片**
   - 脚本使用完整的签名 URL（包含所有参数）通过 curl 下载
   - 保存到本地：`/root/.openclaw/workspace-artemis/seedream_{uuid}.jpg`

4. **输出本地路径**
   - 脚本输出 `LOCAL_PATH: /root/.openclaw/workspace-artemis/seedream_xxx.jpg`

5. **发送图片给用户**
   - 使用 message 工具，path 参数指定本地文件路径
   - 示例：`message(action="send", path="/root/.openclaw/workspace-artemis/seedream_xxx.jpg")`

---

### 决策分支

```
用户请求
    │
    ├─ 纯文字提示词（文生图）─────┐
    │                            │
    └─ 提供参考图片（图生图）─────┤
                                   │
                                   ▼
                     1. 上传参考图到 COS（仅图生图）
                        cos_upload.py
                                   │
                                   ▼
                     2. 调用生成脚本
                        generate_image.py
                        [--image "参考图URL"]
                                   │
                                   ▼
                     3. API 返回签名 URL
                                   │
                                   ▼
                     4. curl 下载到本地
                                   │
                                   ▼
                     5. 输出 LOCAL_PATH
                                   │
                                   ▼
                     6. 发送本地文件给用户
```

---

### 关键要点

- **不要发送 URL 给用户**：飞书无法直接显示火山引擎 TOS 签名 URL
- **必须下载到本地**：使用完整的签名 URL（带所有参数）curl 下载
- **使用 LOCAL_PATH**：脚本输出的本地路径，用于飞书发送
- **图生图必须先上传 COS**：Seedream 仅接受 URL 格式的参考图
