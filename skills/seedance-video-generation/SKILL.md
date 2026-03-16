---
name: seedance-video
description: "使用字节跳动 Seedance 生成 AI 视频。当用户想要：(1) 通过文本提示词生成视频，(2) 通过图片生成视频（首帧、首尾帧、参考图），或 (3) 查询/管理视频生成任务时使用。支持 Seedance 1.5 Pro（带音频）、1.0 Pro、1.0 Pro Fast 和 1.0 Lite 型号。"
---

# Seedance 视频生成

使用字节跳动 Seedance 模型通过火山引擎 Ark API 生成 AI 视频。

## 前置条件

用户必须设置 `ARK_API_KEY` 环境变量。可以通过以下方式设置：

```bash
export ARK_API_KEY="你的-api-key"
```

**基础 URL**: `https://ark.cn-beijing.volces.com/api/v3`

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `ARK_API_KEY` | 火山引擎 API Key（必填） |
| `SEEDANCE_OUTPUT_DIR` | 视频输出目录（可选，默认 `~/Downloads/seedance`） |

## 支持的型号

| 型号 | Model ID | 能力 |
|------|----------|------|
| Seedance 1.5 Pro | `doubao-seedance-1-5-pro-251215` | 文生视频、图生视频（首帧、首尾帧）、音频支持、草稿模式 |
| Seedance 1.0 Pro | `doubao-seedance-1-0-pro-250428` | 文生视频、图生视频（首帧、首尾帧） |
| Seedance 1.0 Pro Fast | `doubao-seedance-1-0-pro-fast-250528` | 文生视频、图生视频（仅首帧） |
| Seedance 1.0 Lite T2V | `doubao-seedance-1-0-lite-t2v-250219` | 仅文生视频 |
| Seedance 1.0 Lite I2V | `doubao-seedance-1-0-lite-i2v-250219` | 图生视频（首帧、首尾帧、参考图1-4张） |

**默认型号**: `doubao-seedance-1-5-pro-251215`（最新，支持音频）

详细型号对比和参数限制见 [references/models.md](references/models.md)。

## 使用方法（推荐：Python CLI 工具）

提供了一个 Python CLI 工具 `seedance.py`，具有完善的错误处理、自动重试和本地图片 base64 转换功能。**建议使用此工具而非原始 curl 命令。**

> 脚本会自动获取自身位置，无论 skill 安装在哪个目录都能正常运行。

### 快速示例

```bash
# 文生视频（创建 + 等待 + 下载）- 保存到 ~/Downloads/seedance
python3 scripts/seedance.py create --prompt "小猫对着镜头打哈欠" --wait --download

# 本地图生视频
python3 scripts/seedance.py create --prompt "人物缓缓转头微笑" --image /path/to/photo.jpg --wait --download

# URL 图生视频
python3 scripts/seedance.py create --prompt "风景画面缓缓推进" --image "https://example.com/image.jpg" --wait --download

# 首帧 + 尾帧
python3 scripts/seedance.py create --prompt "花朵从含苞到盛开" --image first.jpg --last-frame last.jpg --wait --download

# 参考图（Lite I2V）
python3 scripts/seedance.py create --prompt "[图1]的人物在跳舞" --ref-images ref1.jpg ref2.jpg --model doubao-seedance-1-0-lite-i2v-250219 --wait --download

# 自定义参数
python3 scripts/seedance.py create --prompt "城市夜景延时摄影" --ratio 21:9 --duration 8 --resolution 1080p --generate-audio false --wait --download

# 草稿模式（便宜预览）
python3 scripts/seedance.py create --prompt "海浪拍打沙滩" --draft true --wait --download

# 从草稿生成正式视频
python3 scripts/seedance.py create --draft-task-id <DRAFT_TASK_ID> --resolution 720p --wait --download

# 查询任务状态
python3 scripts/seedance.py status <TASK_ID>

# 等待已有任务
python3 scripts/seedance.py wait <TASK_ID> --download

# 列出任务
python3 scripts/seedance.py list --status succeeded

# 删除/取消任务
python3 scripts/seedance.py delete <TASK_ID>
```

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 文本提示词 | **必填** |
| `--image` | 首帧图片（本地路径或 URL） | 可选 |
| `--last-frame` | 尾帧图片（用于首尾帧模式） | 可选 |
| `--ref-images` | 参考图（1-4张，Lite I2V 专用） | 可选 |
| `--model` | 型号 ID | `doubao-seedance-1-5-pro-251215` |
| `--ratio` | 宽高比 | `16:9` (文生) / `adaptive` (图生) |
| `--duration` | 时长（秒） | `5` |
| `--resolution` | 分辨率 | `720p` |
| `--generate-audio` | 是否生成音频 | `true` (仅 1.5 Pro) |
| `--draft` | 草稿模式 | `false` |
| `--wait` | 等待生成完成 | - |
| `--download` | 下载保存路径（默认 `~/Downloads/seedance`） | - |

完整参数说明见 [references/parameters.md](references/parameters.md)。

## 其他操作

### 通过 curl 调用 API

详细 curl 命令示例见 [references/api.md](references/api.md)。

### 高级用法

连续视频生成、草稿模式、从草稿生成正式视频等高级用法见 [references/advanced.md](references/advanced.md)。

### 通过飞书发送视频

视频生成后必须保存到 `video_generate` 文件夹。飞书发送方式见 [references/feishu.md](references/feishu.md)。

## 规则

1. **始终检查** `ARK_API_KEY` 是否已设置：`[ -z "$ARK_API_KEY" ] && echo "Error: ARK_API_KEY not set" && exit 1`
2. **默认使用 Seedance 1.5 Pro** (`doubao-seedance-1-5-pro-251215`)，除非用户指定其他型号。
3. 文生视频**默认 720p、16:9、5 秒、带音频**。
4. 图生视频**默认自适应比例**（根据输入图片自动调整）。
5. **轮询间隔**：状态检查间隔 15 秒。
6. **视频 URL 24 小时过期** - 生成后立即下载。
7. **任务历史仅保留 7 天**。
8. 本地图片文件需转换为 base64 data URL 格式后再发送。
9. 始终向用户显示任务 ID，以便他们稍后检查状态。
10. 生成失败时，清晰显示错误信息并建议可能的修复方法。

## 图片要求

- 格式：jpeg、png、webp、bmp、tiff、gif（1.5 Pro 还支持 heic、heif）
- 宽高比（宽/高）：0.4 到 2.5 之间
- 尺寸：每边 300-6000 像素
- 最大文件大小：30 MB
