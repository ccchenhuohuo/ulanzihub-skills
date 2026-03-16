# API 参考

使用 curl 命令直接调用 Seedance API。

## 基础配置

```bash
BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MODEL="doubao-seedance-1-5-pro-251215"
```

## 创建视频生成任务

### 模式 A：文生视频

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "你的提示词" }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

### 模式 B：图生视频（首帧）

**使用图片 URL：**

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "你的提示词" },
      {
        "type": "image_url",
        "image_url": { "url": "图片URL" },
        "role": "first_frame"
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

**使用本地图片文件（转为 base64）：**

```bash
IMG_PATH="/path/to/image.png"
IMG_EXT="${IMG_PATH##*.}"
IMG_EXT_LOWER=$(echo "$IMG_EXT" | tr '[:upper:]' '[:lower:]')
IMG_BASE64=$(base64 < "$IMG_PATH" | tr -d '\n')
IMG_DATA_URL="data:image/${IMG_EXT_LOWER};base64,${IMG_BASE64}"

TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "你的提示词" },
      {
        "type": "image_url",
        "image_url": { "url": "'"$IMG_DATA_URL"'" },
        "role": "first_frame"
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

### 模式 C：图生视频（首帧 + 尾帧）

需要两张图片。支持：Seedance 1.5 Pro、1.0 Pro、1.0 Lite I2V。

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "你的提示词" },
      {
        "type": "image_url",
        "image_url": { "url": "首帧图片URL" },
        "role": "first_frame"
      },
      {
        "type": "image_url",
        "image_url": { "url": "尾帧图片URL" },
        "role": "last_frame"
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

### 模式 D：参考图生视频（仅 Seedance 1.0 Lite I2V）

提供 1-4 张参考图。在提示词中使用 `[图1]`、`[图2]` 来引用特定图片。

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-0-lite-i2v-250219",
    "content": [
      { "type": "text", "text": "[图1]的人物在跳舞" },
      {
        "type": "image_url",
        "image_url": { "url": "参考图URL_1" },
        "role": "reference_image"
      }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p"
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

## 轮询任务状态

视频生成是异步的。轮询任务状态直到完成。

```bash
echo "等待视频生成完成..."
while true; do
  STATUS_RESULT=$(curl -s -X GET "${BASE_URL}/contents/generations/tasks/${TASK_ID}" \
    -H "Authorization: Bearer $ARK_API_KEY")

  STATUS=$(echo "$STATUS_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")

  if [ "$STATUS" = "succeeded" ]; then
    echo "视频生成成功！"
    VIDEO_URL=$(echo "$STATUS_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['content']['video_url'])")
    echo "视频 URL: $VIDEO_URL"
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR_MSG=$(echo "$STATUS_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','Unknown error'))" 2>/dev/null || echo "Unknown error")
    echo "视频生成失败: $ERROR_MSG"
    break
  elif [ "$STATUS" = "expired" ]; then
    echo "视频生成任务已过期。"
    break
  else
    echo "状态: $STATUS - 处理中..."
    sleep 15
  fi
done
```

## 下载视频

```bash
OUTPUT_PATH="/root/.openclaw/workspace-artemis/video_generate/seedance_video_$(date +%Y%m%d_%H%M%S).mp4"
curl -s -o "$OUTPUT_PATH" "$VIDEO_URL"
echo "视频保存到: $OUTPUT_PATH"
```

## 查询任务状态

```bash
curl -s -X GET "${BASE_URL}/contents/generations/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -m json.tool
```

## 列出任务

```bash
# 列出所有任务（分页）
curl -s -X GET "${BASE_URL}/contents/generations/tasks?page_num=1&page_size=10" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -m json.tool

# 按状态筛选
curl -s -X GET "${BASE_URL}/contents/generations/tasks?page_num=1&page_size=10&filter.status=succeeded" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -m json.tool
```

## 取消或删除任务

```bash
curl -s -X DELETE "${BASE_URL}/contents/generations/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARK_API_KEY"
```

注意：
- `queued` 任务将被取消
- `succeeded`/`failed`/`expired` 任务将从历史记录中删除

## 相关文档

- [参数参考](./parameters.md) - 完整参数说明
- [型号参考](./models.md) - 型号对比
- [高级用法](./advanced.md) - 连续视频、草稿模式等
