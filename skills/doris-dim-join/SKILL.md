---
name: doris-dim-join
description: 执行Doris维度表与事实表JOIN，为销售数据挂载标准化分类维度（stdcategory1/2/3, device_type）。**必须使用此skill完成维度表JOIN**，不要自行编写SQL。支持CN站点（product_id匹配）和US/JP/DE站点（sku_id+site匹配），MX/BR自动剔除。包含CSV处理、StreamLoad导入、字段映射、JOIN执行、结果验证全流程。当用户提到dim表JOIN、维度表挂载、stdcategory、product_category_dimension时，**立即使用此skill**。
---

# Doris 维度表与事实表 JOIN 执行器

## 任务概览

将 `monthly_sales_wide_new` 事实表与 `product_category_dimension` 维度表 JOIN，为销售数据挂载分类维度。

### 用户决策

| 决策项 | 选择 |
|--------|------|
| **字段策略** | dim表的category_1/2/3改名为stdcategory1/2/3后JOIN |
| **存储表名** | monthly_sales_with_dim |
| **匹配策略** | 只保留能匹配的记录 (INNER JOIN) |


> **重要**: 以下路径变量由用户在调用时指定：
> - `{数据路径}` - CSV源文件及中间产物目录（如 `/Users/chenyu/script-dev/dim表_3.18/`）
> - 脚本目录: `~/.claude/skills/doris-dim-join/scripts/`
> - 参考文档: `~/.claude/skills/doris-dim-join/references/`

---

## 执行确认

触发此Skill后，**按以下步骤依次确认，全部通过后方可执行**：

### 步骤1：配置检查（智能感知）

**同时检查以下配置项**：

| 检查项 | 检查方式 | 缺失时处理 |
|--------|----------|------------|
| 环境变量 | `echo $DORIS_HOST $DORIS_PORT $DORIS_USER $DORIS_PASSWORD $MYSQL_HOST $MYSQL_PORT` | 一次性询问所有缺失项 |
| MCP连接 | 询问用户确认 | 如未配置则终止 |
| 数据路径 | 询问用户 | 未提供则终止 |

**如果环境变量已全部设置**，跳过询问，直接进入步骤2。

**如果有任何缺失**，一次性询问：
```
请提供以下配置信息（如已设置请填"已配置"）：
- Doris服务器地址 (DORIS_HOST):
- Doris HTTP端口 (DORIS_PORT):
- Doris用户名 (DORIS_USER):
- Doris密码 (DORIS_PASSWORD):
- MySQL服务器地址 (MYSQL_HOST):
- MySQL端口 (MYSQL_PORT):
- CSV源文件目录路径（如 /path/to/data）:
```

### 步骤2：MCP与权限确认

使用 `AskUserQuestion` 向用户确认：
```
请确认以下MCP配置已就绪：
1. Doris MCP 已配置并可用
2. MySQL MCP 已配置并可用（如使用remote MCP）
3. MCP 已开启DDL权限（ALLOW_DDL_OPERATION=true）

如尚未配置，请先完成MCP配置后再继续。
- 确认请回复"yes"或"继续"
- 其他回复：取消本次操作
```

### 步骤3：执行确认（风险提示+最终确认合并）

向用户展示风险并请求最终确认：
```
【执行风险确认】

将执行以下DDL操作：
| 操作 | 目标表 | 影响 |
|------|--------|------|
| TRUNCATE | flywheel.product_category_dimension | 清空维度表 |
| ALTER COLUMN | flywheel.product_category_dimension | category_1/2/3 → stdcategory1/2/3 |
| TRUNCATE | flywheel.monthly_sales_with_dim | 清空目标表（如存在） |
| INSERT SELECT | flywheel.monthly_sales_with_dim | 写入JOIN数据 |

CN站点：用product_id+year_num匹配
US/JP/DE站点：用sku_id+site+year_num匹配
MX/BR站点：**不参与JOIN**（直接剔除）

确认开始执行？
- 输入"继续"或"yes"：开始执行
- 输入其他：取消本次操作
```

> **注意**: 任何步骤缺失或用户取消，**不得执行任何阶段**。

---

## 执行流程

### 阶段1: 前置检查

| 步骤 | 操作 | 命令 |
|------|------|------|
| 1.1 | 检查数据文件 | `ls {数据路径}` |
| 1.2 | 确认CSV文件 | 验证 `桶 *.csv` 存在（Python glob跨平台匹配，支持桶1-N任意数量） |
| 1.3 | 统计行数 | `wc -l {数据路径}/桶*.csv`（记录合并后期望行数）|
| 1.4 | 检查脚本 | `ls ~/.claude/skills/doris-dim-join/scripts/` |

> **配置检查已在步骤1完成**：环境变量、MCP连接、数据路径已通过执行确认步骤验证。

### 阶段2: 数据处理

**脚本**: `scripts/merge_csv.py`, `scripts/convert_to_json.py`
**参考**：`references/field_mapping.md` - 字段映射详情

| 步骤 | 操作 | 命令 |
|------|------|------|
| 3.1 | 合并CSV | `python3 ~/.claude/skills/doris-dim-join/scripts/merge_csv.py --path {数据路径} --merge` |
| 3.2 | 验证合并 | `head -3 {数据路径}/merged_data.csv` |
| 3.3 | 转换为JSON | `python3 ~/.claude/skills/doris-dim-join/scripts/convert_to_json.py --path {数据路径}` |
| 3.4 | 验证JSON | `head -c 500 {数据路径}/batch_0001.json` |

**验证点**：
- 合并后检查site字段分布
  ```bash
  awk -F',' 'NR>1 {print $4}' {数据路径}/merged_data.csv | sort | uniq -c
  ```
- 字段映射自动化：先用Python打印源文件列名，再编写映射
  ```python
  import csv
  with open('{数据路径}/桶1.csv', 'r') as f:
      reader = csv.DictReader(f)
      print(reader.fieldnames)  # 先看源文件有什么列
  ```

### 阶段3: 数据导入

**脚本**: `scripts/import_batches.py`

| 步骤 | 操作 | 命令 |
|------|------|------|
| 4.1 | 清空维度表 | `TRUNCATE TABLE flywheel.product_category_dimension` |
| 4.2 | 执行导入(Python) | `python3 ~/.claude/skills/doris-dim-join/scripts/import_batches.py --path {数据路径}` |
| 4.2 | 执行导入(Bash) | `bash ~/.claude/skills/doris-dim-join/scripts/import_batches.sh` (需先设置 `BATCH_DIR={数据路径}`) |
| 4.3 | 验证行数 | `SELECT COUNT(*) FROM flywheel.product_category_dimension` |

**分批监控**：大数据量导入时，定期检查进度
```sql
-- 每分钟执行一次，检查导入进度
SELECT COUNT(*) FROM flywheel.product_category_dimension;
```
**期望**: 与阶段1统计的合并后行数一致

### 阶段4: JOIN准备

**参考**: `references/join_rules.md` - 完整SQL模板

| 步骤 | 操作 | SQL/命令 |
|------|------|----------|
| 5.0 | 修改dim表字段名 | `ALTER TABLE flywheel.product_category_dimension CHANGE COLUMN category_1 stdcategory1 VARCHAR(100)` (category_2/3同理) |
| 5.1 | 创建目标表(如不存在) | 使用 `references/join_rules.md` 中的 CREATE TABLE 语句 |
| 5.2 | 查询目标表结构 | `DESC flywheel.monthly_sales_with_dim` (INSERT前必须先查!) |

### 阶段5: JOIN执行

| 步骤 | 操作 | SQL |
|------|------|-----|
| 6.1 | 清空目标表 | `TRUNCATE TABLE flywheel.monthly_sales_with_dim` |
| 6.2 | CN站点JOIN | `INSERT ... SELECT` (product_id + year_num) |
| 6.3 | US/JP/DE站点JOIN | `INSERT ... SELECT` (sku_id + site + year_num) |

> **MX/BR站点数据直接剔除，不参与JOIN**
> **INSERT前必须先执行 `DESC` 查询目标表结构，使用显式列名，不要用 `SELECT *`**

### 阶段6: 结果验证

**脚本**: `scripts/validate_data.py`
**参考**: `references/validation_queries.sql` - 验证SQL模板

运行验证脚本查看所有验证SQL：
```bash
python3 ~/.claude/skills/doris-dim-join/scripts/validate_data.py
```

---

### 阶段7: 执行报告

任务完成后，向用户输出本次运行的详细报告：

#### 7.1 运行时间统计

| 阶段 | 开始时间 | 结束时间 | 耗时 |
|------|----------|----------|------|
| 阶段1-前置检查 | HH:MM | HH:MM | X分钟 |
| 阶段2-数据处理 | HH:MM | HH:MM | X分钟 |
| 阶段3-数据导入 | HH:MM | HH:MM | X分钟 |
| 阶段4-JOIN准备 | HH:MM | HH:MM | X分钟 |
| 阶段5-JOIN执行 | HH:MM | HH:MM | X分钟 |
| 阶段6-结果验证 | HH:MM | HH:MM | X分钟 |
| **总计** | - | - | **X分钟** |

#### 7.2 执行结果摘要

```sql
-- 维度表导入结果
SELECT COUNT(*) AS dim_total FROM flywheel.product_category_dimension;

-- 目标表JOIN结果
SELECT COUNT(*) AS join_total FROM flywheel.monthly_sales_with_dim;

-- 各站点数据分布
SELECT site, COUNT(*) FROM flywheel.monthly_sales_with_dim GROUP BY site;
```

#### 7.3 数据覆盖率

```sql
-- JOIN匹配率 = 匹配数 / 源数据总数
SELECT
    (SELECT COUNT(*) FROM flywheel.monthly_sales_with_dim) AS matched,
    (SELECT COUNT(*) FROM flywheel.monthly_sales_wide_new WHERE site IN ('CN','US','JP','DE')) AS total,
    ROUND((SELECT COUNT(*) FROM flywheel.monthly_sales_with_dim) * 100.0 / NULLIF((SELECT COUNT(*) FROM flywheel.monthly_sales_wide_new WHERE site IN ('CN','US','JP','DE')), 0), 2) AS match_rate;
```

#### 7.4 异常记录（如有）

| 阶段 | 异常描述 | 原因分析 | 处理方式 |
|------|----------|----------|----------|
| - | 无 | - | - |

#### 7.5 报告模板

任务完成后，向用户输出以下格式的报告：

```
========================================
Doris维度表JOIN - 执行报告
========================================
执行时间: YYYY-MM-DD HH:MM:SS
总耗时: XX分钟

【数据统计】
- 维度表导入: XX条
- JOIN后总数: XX条
- 匹配率: XX%

【站点分布】
CN: XX条
US: XX条
JP: XX条
DE: XX条

【异常记录】
（无 / 详见上方异常记录表）

【结论】
- 执行状态: 成功/部分成功/失败
- 数据质量: 符合预期/存在偏差
========================================
```

---

## 文件结构

```
doris-dim-join/
├── SKILL.md                    # 流程编排层
├── scripts/                    # 可执行脚本
│   ├── merge_csv.py           # CSV合并（--path参数化）
│   ├── convert_to_json.py     # JSON转换（--path参数化）
│   ├── import_batches.py      # 批量导入Python版（--path参数化）
│   ├── import_batches.sh      # 批量导入Bash版（先清空表再导入）
│   └── validate_data.py       # 结果验证
└── references/                 # 参考文档（按需加载）
    ├── field_mapping.md       # 字段映射
    ├── join_rules.md          # JOIN规则与SQL
    ├── validation_queries.sql # 验证SQL
    └── troubleshooting.md      # 常见错误排查（随使用积累更新）
```

> **遇到错误时**: 参考 `references/troubleshooting.md` 排查，该文档随每次运行不断更新
