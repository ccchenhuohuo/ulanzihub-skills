# 高级用法

## 生成连续视频（使用尾帧）

通过 `return_last_frame` 参数获取尾帧，然后将其作为下一个视频的首帧，可以生成长时间的连续视频。

### 步骤 1：从第一个任务获取尾帧 URL

创建任务时设置 `return_last_frame: true`：

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
    "return_last_frame": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

任务完成后获取尾帧 URL：

```bash
LAST_FRAME_URL=$(curl -s -X GET "${BASE_URL}/contents/generations/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -c "import sys,json; print(json.load(sys.stdin)['content']['last_frame_url'])")

echo "尾帧 URL: $LAST_FRAME_URL"
```

### 步骤 2：用尾帧作为下一个视频的首帧

```bash
# 等待第一个任务完成
# ... (轮询逻辑)

# 创建第二个视频，使用尾帧作为首帧
SECOND_TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "视频继续..." },
      {
        "type": "image_url",
        "image_url": { "url": "'"$LAST_FRAME_URL"'" },
        "role": "first_frame"
      }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p"
  }')

SECOND_TASK_ID=$(echo "$SECOND_TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

## 草稿模式（Seedance 1.5 Pro）

草稿模式生成低分辨率（480p）预览视频，成本更低，适合快速验证效果。满意后再生成正式视频。

### 步骤 1：创建草稿任务

```bash
DRAFT_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      { "type": "text", "text": "你的提示词" }
    ],
    "draft": true,
    "resolution": "480p"
  }')

DRAFT_TASK_ID=$(echo "$DRAFT_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "草稿任务创建成功: $DRAFT_TASK_ID"

# 等待草稿生成完成
# ... (轮询逻辑)
```

### 步骤 2：从草稿生成正式视频

草稿生成成功后，使用草稿任务 ID 创建正式视频：

```bash
FINAL_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "draft_task",
        "draft_task": { "id": "'"$DRAFT_TASK_ID"'" }
      }
    ],
    "resolution": "720p"
  }')

FINAL_TASK_ID=$(echo "$FINAL_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "正式任务创建成功: $FINAL_TASK_ID"

# 等待正式视频生成完成
# ... (轮询逻辑)
```

**注意：**
- 草稿模式强制使用 480p 分辨率
- 草稿视频不能直接用于生产，需要从草稿生成正式视频
- 从草稿生成正式视频时可以指定更高分辨率（720p 或 1080p）

## 使用自定义随机种子

使用 `seed` 参数可以复现相同结果：

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
    "seed": 12345
  }')

# 使用相同 seed 可以复现相同结果
```

| seed 值 | 说明 |
|---------|------|
| `-1` | 随机生成（默认） |
| 正整数 | 复现相同结果 |

## 离线服务（Flex Tier）

使用 `service_tier: flex` 可以使用离线服务，价格便宜约 50%，但生成速度更慢：

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "你的提示词" }
    ],
    "service_tier": "flex",
    "execution_expires_after": 259200
  }')
```

| service_tier | 说明 | 价格 |
|--------------|------|------|
| `default` | 在线服务 | 标准 |
| `flex` | 离线服务 | 便宜约 50% |

## 固定相机位置

使用 `camera_fixed: true` 固定相机位置：

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "'"$MODEL"'",
    "content": [
      { "type": "text", "text": "你的提示词" }
    ],
    "camera_fixed": true
  }')
```

## 自动时长（Seedance 1.5 Pro）

设置 `duration: -1` 让模型自动决定视频时长（4-12 秒）：

```bash
TASK_RESULT=$(curl -s -X POST "${BASE_URL}/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      { "type": "text", "text": "你的提示词" }
    ],
    "duration": -1,
    "ratio": "16:9",
    "resolution": "720p"
  }')
```

## 相关文档

- [参数参考](./parameters.md) - 完整参数说明
- [型号参考](./models.md) - 型号对比
- [API 参考](./api.md) - 详细的 API 调用示例
