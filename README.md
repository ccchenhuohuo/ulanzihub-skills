# ulanzihub-skills

<p align="center">
  <img src="https://img.shields.io/npm/v/ulanzihub-skills?style=flat&color=00D8FF" alt="npm version">
  <img src="https://img.shields.io/github/license/ccchenhuohuo/ulanzihub-skills" alt="license">
  <img src="https://img.shields.io/github/stars/ccchenhuohuo/ulanzihub-skills" alt="stars">
  <img src="https://img.shields.io/github/forks/ccchenhuohuo/ulanzihub-skills" alt="forks">
</p>

> 优篮子内部技能市场 - 让团队复用 Claude Code & OpenClaw 技能

## 简介

ulanzihub-skills 是优篮子公司的内部技能市场，基于 **Agent Skills** 开放标准，支持 **Claude Code** 和 **OpenClaw** 双平台。让团队成员可以共享和复用 AI 助手技能，提升工作效率。

## 特性

- 🎯 **双平台兼容** - 同时支持 Claude Code 和 OpenClaw
- 🔄 **一键安装** - 通过 npm 自动安装，无需配置
- 👥 **团队协作** - 统一管理，按需更新
- 📦 **开箱即用** - 技能开箱即用，无需额外配置
- 🔒 **安全可靠** - 代码审查通过，安全无风险

## 快速开始

### 前置要求

- Node.js 18.0.0+
- npm 9.0.0+ 或 yarn 1.22.0+

### 安装 CLI

```bash
# 官方镜像（推荐）
npm install -g ulanzihub

# 国内镜像（如果无法访问 npm 官方）
npm config set registry https://registry.npmmirror.com
npm install -g ulanzihub
```

### 验证安装

```bash
ulanzihub --version
```

---

## 用户指南

### 安装技能

```bash
# 交互式安装（推荐）
ulanzihub install ulanzihub-skills

# 安装到指定平台
ulanzihub install ulanzihub-skills --platform openclaw   # OpenClaw
ulanzihub install ulanzihub-skills --platform claude-code # Claude Code
ulanzihub install ulanzihub-skills --platform all         # 两个平台

# 安装全部技能
ulanzihub install ulanzihub-skills --yes

# 只安装指定技能
ulanzihub install ulanzihub-skills --skills seedream
```

### 查看已安装

```bash
# 查看所有已安装技能
ulanzihub list

# 查看特定平台
ulanzihub list --platform openclaw
```

### 更新技能

```bash
# 检查更新
ulanzihub update --check

# 更新所有技能
ulanzihub update

# 更新指定技能
ulanzihub update seedream
```

### 查看技能详情

```bash
ulanzihub info <技能名称>
```

### 卸载技能

```bash
ulanzihub uninstall <技能名称>
```

---

## 技能列表

当前版本包含 **5 个技能**：

| 技能名称 | 说明 | 平台 | 版本 |
|----------|------|------|------|
| [doris-dim-join](#doris-dim-join) | Doris维度表与事实表JOIN | Claude Code | 1.0.0 |
| [skill-creator](#skill-creator) | Claude Code Skill 创建与优化工具 | Claude Code | 1.0.0 |
| [seedream-image-for-openclaw](#seedream-image-for-openclaw) | 火山引擎 Seedream 图片生成 | Claude Code | 1.0.2 |
| [seedance-video-generation](#seedance-video-generation) | 字节跳动 Seedance 视频生成 | Claude Code | 1.0.2 |
| [humanizer-zh](#humanizer-zh) | 去除 AI 写作痕迹 | Claude Code | - |
| [marketing-skills](#marketing-skills) | 23 个营销模块技能合集 | Claude Code | - |
| [n8n-workflow-automation](#n8n-workflow-automation) | n8n 工作流自动化 | Claude Code | - |

---

### 技能详细介绍

#### 🗄️ doris-dim-join

Doris 维度表与事实表 JOIN 技能，为销售数据挂载标准化分类维度。

**功能：**
- CSV 数据合并与处理
- StreamLoad 批量导入 Doris
- 维度表与事实表 JOIN（CN/US/JP/DE 站点）
- 结果验证与报告

**触发词：** dim表JOIN、维度表挂载、stdcategory、product_category_dimension

**注意：** 必须使用此 skill 完成维度表 JOIN，不要自行编写 SQL。

---

#### 🛠️ skill-creator

Claude Code Skill 创建与优化工具。

**功能：**
- 从零创建新 Skill
- 迭代优化现有 Skill
- 运行测试用例评估 Skill 效果
- 优化 Skill 描述以提高触发准确性

**触发词：** 创建 skill、优化 skill、skill 评估

---

#### 🌄 seedream-image-for-openclaw

火山引擎 Seedream-4.5 AI 图片生成技能。

**功能：**
- 文生图：输入文本提示词生成图片
- 图生图：上传参考图，生成风格化图片
- 组图生成：最多生成 15 张关联图片

**触发词：** 文生图、图生图、AI绘图、Seedream、AI图片

**使用示例：**

```bash
# 文生图
uv run scripts/generate_image.py --prompt "一只赛博朋克风格的猫"

# 指定分辨率
uv run scripts/generate_image.py --prompt "壮丽的山川日出" --size "2K"

# 生成组图
uv run scripts/generate_image.py --prompt "宇航员探险" --sequential --max-images 4
```

**环境变量：**
| 变量名 | 说明 | 必填 |
|--------|------|------|
| `VOLC_API_KEY` | 火山引擎 API Key | 是 |
| `SEEDREAM_OUTPUT_DIR` | 图片输出目录（默认 ~/Downloads/seedream） | 否 |
| `TENCENT_COS_*` | 腾讯云 COS（图生图用） | 仅图生图 |

**输出位置：** `~/Downloads/seedream/`

---

#### 🎬 seedance-video-generation

字节跳动 Seedance AI 视频生成技能。

**支持的型号：**
- Seedance 1.5 Pro（默认）：支持音频、草稿模式
- Seedance 1.0 Pro：文生视频、图生视频
- Seedance 1.0 Pro Fast：快速生成
- Seedance 1.0 Lite：低成本选项

**功能：**
- 文生视频：输入文本生成视频
- 图生视频：首帧/首尾帧/参考图模式
- 音频生成：AI 配乐 + 音效（1.5 Pro）
- 草稿模式：低成本预览

**触发词：** 视频生成、AI视频、Seedance、文生视频、图生视频

**使用示例：**

```bash
# 文生视频
python3 scripts/seedance.py create --prompt "小猫打哈欠" --wait --download

# 图生视频
python3 scripts/seedance.py create --prompt "人物转身" --image photo.jpg --wait --download

# 首尾帧视频
python3 scripts/seedance.py create --prompt "花朵绽放" --image first.jpg --last-frame last.jpg --wait --download

# 草稿模式（预览）
python3 scripts/seedance.py create --prompt "海浪" --draft true --wait --download
```

**环境变量：**
| 变量名 | 说明 | 必填 |
|--------|------|------|
| `ARK_API_KEY` | 火山引擎 Ark API Key | 是 |
| `SEEDANCE_OUTPUT_DIR` | 视频输出目录（默认 ~/Downloads/seedance） | 否 |

**输出位置：** `~/Downloads/seedance/`

---

#### ✍️ humanizer-zh

去除 AI 写作痕迹，让文本更自然。

**功能：**
- 检测 AI 写作特征
- 改写为人类风格
- 支持多种场景

---

#### 📢 marketing-skills

23 个营销模块技能合集。

**包含模块：**
- SEO 优化
- 内容营销
- 社交媒体运营
- 广告投放
- 数据分析
- 等等...

---

#### 🔗 n8n-workflow-automation

n8n 工作流自动化技能。

**功能：**
- 工作流设计
- 自动化编排
- 集成第三方服务

---

## 技能开发指南

### 目录结构

```
skills/
├── skill-name/
│   ├── SKILL.md          # 技能定义（必需）
│   ├── _meta.json        # 元数据
│   ├── scripts/           # 可执行脚本
│   ├── references/        # 参考文档
│   └── assets/           # 静态资源
```

### 创建新技能

1. 在 `skills/` 目录下创建新文件夹
2. 编写 `SKILL.md` 文件
3. 添加 `_meta.json` 元数据
4. 提交 PR

### SKILL.md 规范

```yaml
---
name: skill-name
description: 技能描述（触发词+功能说明）
version: 1.0.0
author: 作者名
tags: [tag1, tag2]
platforms:
  - claude-code
  - openclaw
---
```

---

## 常见问题

### Q: 安装失败怎么办？

```bash
# 检查网络
ulanzihub doctor

# 清除缓存
npm cache clean --force
```

### Q: 如何更新到最新版本？

```bash
npm update ulanzihub -g
```

### Q: 支持哪些平台？

- Claude Code (macOS/Linux/Windows)
- OpenClaw (飞书)

### Q: 技能安装在哪里？

- Claude Code: `~/.claude/skills/`
- OpenClaw: `~/.openclaw/workspace/skills/`

---

## 相关链接

- 📖 [完整文档](./docs)
- 💬 [Issues 反馈](https://github.com/ccchenhuohuo/ulanzihub-skills/issues)
- 📦 [npm 包](https://www.npmjs.com/package/ulanzihub-skills)
- 🐙 [GitHub 仓库](https://github.com/ccchenhuohuo/ulanzihub-skills)

---

## 贡献者

<p align="center">
  <img src="https://contrib.rocks/image?repo=ccchenhuohuo/ulanzihub-skills" alt="contributors">
</p>

欢迎提交 Issue 和 PR！

---

## License

MIT © 2024 Ulanzi Team
