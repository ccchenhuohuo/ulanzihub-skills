---
name: feishu-bot
description: 开发飞书机器人和集成应用，支持消息卡片、交互组件等。当用户要求开发飞书机器人、集成飞书 API、实现消息推送时使用此技能。
version: 1.0.0
author: ulanzi
tags: [feishu, bot, internal]
platforms:
  - claude-code
  - openclaw
---

# 飞书机器人开发

开发优篮子内部的飞书机器人和集成应用。

## 适用场景

- 开发飞书自定义机器人
- 实现消息卡片推送
- 集成飞书 Open API
- 构建飞书应用
- 自动化流程集成

## 开发规范

### 1. 机器人类型

- 自定义机器人：用于群消息推送
- 应用机器人：用于更复杂的交互

### 2. 消息类型

- 文本消息
- 富文本消息
- 消息卡片 (Card)
- 交互组件

### 3. 常见功能

- 定时提醒
- 审批通知
- 数据推送
- 人工交互

## 代码示例

### 发送文本消息

```javascript
const webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx';

const message = {
  msg_type: 'text',
  content: {
    text: 'Hello from飞书机器人!'
  }
};

fetch(webhook, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(message)
});
```

### 发送卡片消息

```javascript
const message = {
  msg_type: 'interactive',
  card: {
    header: {
      title: { tag: 'plain_text', content: '标题' },
      color: 'blue'
    },
    elements: [
      {
        tag: 'div',
        text: { tag: 'plain_text', content: '内容' }
      },
      {
        tag: 'action',
        actions: [
          {
            tag: 'button',
            text: { tag: 'plain_text', content: '点击' },
            type: 'primary',
            url: 'https://example.com'
          }
        ]
      }
    ]
  }
};
```

## 注意事项

- 机器人 Webhook 地址保密
- 合理使用 API 频率限制
- 注意消息内容合规
- 测试环境先验证
