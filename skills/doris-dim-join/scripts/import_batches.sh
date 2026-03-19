#!/bin/bash
# 分批导入 JSON 文件到 Doris
# 使用mysql客户端清空表，然后分批导入JSON

# 从环境变量读取配置（必须设置）
DORIS_HOST="${DORIS_HOST}"
DORIS_PORT="${DORIS_PORT}"
DORIS_USER="${DORIS_USER}"
DORIS_PASSWORD="${DORIS_PASSWORD}"
MYSQL_HOST="${MYSQL_HOST}"
MYSQL_PORT="${MYSQL_PORT}"

# 验证必需的环境变量
if [ -z "$DORIS_HOST" ] || [ -z "$DORIS_PORT" ] || [ -z "$DORIS_USER" ] || [ -z "$DORIS_PASSWORD" ]; then
    echo "错误: 缺少必需的环境变量 DORIS_HOST, DORIS_PORT, DORIS_USER, DORIS_PASSWORD"
    echo "请先设置这些环境变量后重试"
    exit 1
fi

# MySQL配置验证（用于清空表操作）
if [ -z "$MYSQL_HOST" ] || [ -z "$MYSQL_PORT" ]; then
    echo "错误: 缺少MySQL配置 MYSQL_HOST, MYSQL_PORT"
    echo "请先设置这些环境变量后重试"
    exit 1
fi

# BATCH_DIR 需要通过参数传入
if [ -z "$BATCH_DIR" ]; then
    echo "错误: 请设置 BATCH_DIR 环境变量"
    echo "示例: BATCH_DIR=/path/to/data bash import_batches.sh"
    exit 1
fi

# StreamLoad URL
URL="http://${DORIS_HOST}:33060/api/flywheel/product_category_dimension/_stream_load"

echo "========================================"
echo "Doris 批量导入脚本"
echo "========================================"
echo "Doris服务器: ${DORIS_HOST}"
echo "StreamLoad URL: ${URL}"
echo "数据目录: ${BATCH_DIR}"
echo "========================================"

# 先清空表（如果需要）
if [ "$SKIP_TRUNCATE" != "true" ]; then
    echo "清空目标表..."
    mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u "${DORIS_USER}" -p"${DORIS_PASSWORD}" -e "TRUNCATE TABLE flywheel.product_category_dimension;" 2>/dev/null || echo "清空表失败，将继续尝试导入"
    echo ""
fi

total=0
success=0
fail=0

# 遍历所有 batch 文件
for file in $(ls $BATCH_DIR/batch_*.json 2>/dev/null | sort); do
    filename=$(basename $file)
    ((total++))

    echo -n "导入 $filename ... "

    # 执行 curl 导入
    result=$(curl -s -w "\n%{http_code}" --location-trusted -u "${DORIS_USER}:${DORIS_PASSWORD}" -X POST \
        -H "Content-Type: application/json" \
        -H "Expect: 100-continue" \
        -H "column_separator: ," \
        -H "format: json" \
        -H "strip_outer_array: true" \
        -H "ignore_json_size: true" \
        -d @$file \
        "$URL" 2>&1)

    # 检查是否成功 (HTTP 200 且包含 Success)
    if echo "$result" | grep -q '"Status": "Success"'; then
        echo "成功"
        ((success++))
    else
        echo "失败"
        echo "$result" | head -3
        ((fail++))
    fi

    # 每 50 批显示进度
    if [ $((total % 50)) -eq 0 ]; then
        echo "=== 进度: $total (成功: $success, 失败: $fail) ==="
    fi
done

echo ""
echo "========================================"
echo "导入完成！"
echo "总批数: $total"
echo "成功: $success"
echo "失败: $fail"
echo "========================================"
