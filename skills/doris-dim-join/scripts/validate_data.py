#!/usr/bin/env python3
"""
Doris维度表JOIN结果验证脚本

用于自动化验证 JOIN 执行结果，包括：
- 总行数检查
- 站点分布检查
- 数据抽样检查

用法:
    python3 validate_data.py
"""

import sys

# 验证SQL模板
VALIDATION_QUERIES = {
    # 检查总行数
    "total_count": """
SELECT COUNT(*) as total FROM flywheel.monthly_sales_with_dim
""",
    # 检查各站点分布
    "site_distribution": """
SELECT site, COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim
GROUP BY site
ORDER BY cnt DESC
""",
    # 抽样查看数据
    "sample_data": """
SELECT site, product_id, sku_id, month_dt, stdcategory1, stdcategory2, stdcategory3, device_type
FROM flywheel.monthly_sales_with_dim
LIMIT 10
""",
    # 检查空值情况
    "null_check": """
SELECT
    SUM(CASE WHEN stdcategory1 IS NULL OR stdcategory1 = '' THEN 1 ELSE 0 END) as null_stdcategory1,
    SUM(CASE WHEN stdcategory2 IS NULL OR stdcategory2 = '' THEN 1 ELSE 0 END) as null_stdcategory2,
    SUM(CASE WHEN stdcategory3 IS NULL OR stdcategory3 = '' THEN 1 ELSE 0 END) as null_stdcategory3,
    SUM(CASE WHEN device_type IS NULL OR device_type = '' THEN 1 ELSE 0 END) as null_device_type,
    COUNT(*) as total
FROM flywheel.monthly_sales_with_dim
""",
    # 检查JOIN匹配率
    "join_match_rate": """
SELECT
    'Dimension Table' as source,
    COUNT(*) as cnt
FROM flywheel.product_category_dimension
UNION ALL
SELECT
    'Target Table (with dim)' as source,
    COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim
"""
}


def print_header(title):
    """打印带分隔线的标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result(query_name, result):
    """打印查询结果"""
    print(f"\n--- {query_name} ---")
    if result is None:
        print("  [跳过 - 需要手动执行]")
        return

    try:
        if isinstance(result, dict):
            if 'results' in result:
                data = result.get('results', [])
                if data and isinstance(data[0], dict):
                    # 打印表头
                    headers = list(data[0].keys())
                    print("  " + " | ".join(headers))
                    print("  " + "-" * (len(" | ".join(headers))))
                    # 打印数据行
                    for row in data[:10]:  # 限制显示行数
                        values = [str(row.get(h, '')) for h in headers]
                        print("  " + " | ".join(values))
                else:
                    print(f"  {data}")
            elif 'error' in result:
                print(f"  [错误] {result['error']}")
            else:
                print(f"  {result}")
        else:
            print(f"  {result}")
    except Exception as e:
        print(f"  [解析错误] {str(e)}")


def main():
    """主函数"""
    print_header("Doris 维度表JOIN结果验证")

    print("""
    本脚本提供以下验证SQL:

    1. total_count       - 检查总行数
    2. site_distribution - 检查各站点分布
    3. sample_data       - 抽样查看数据
    4. null_check        - 检查空值情况
    5. join_match_rate   - 检查JOIN匹配率

    使用方法:
    - 使用 MCP 工具 mcp__doris__exec_query 执行各验证SQL
    - 或在 Doris 客户端中执行 config/validation_queries.sql
    """)

    # 打印所有验证SQL供用户参考
    print_header("验证SQL清单")

    for name, sql in VALIDATION_QUERIES.items():
        print(f"\n### {name}")
        print(sql.strip())

    print("\n")
    print_header("快速验证命令")

    print("""
    # 在 Doris 客户端中执行:

    -- 1. 总行数
    SELECT COUNT(*) as total FROM flywheel.monthly_sales_with_dim;

    -- 2. 站点分布
    SELECT site, COUNT(*) as cnt
    FROM flywheel.monthly_sales_with_dim
    GROUP BY site
    ORDER BY cnt DESC;

    -- 3. 抽样数据
    SELECT site, product_id, sku_id, month_dt,
           stdcategory1, stdcategory2, stdcategory3, device_type
    FROM flywheel.monthly_sales_with_dim
    LIMIT 10;

    -- 4. 空值检查
    SELECT
        SUM(CASE WHEN stdcategory1 IS NULL OR stdcategory1 = '' THEN 1 ELSE 0 END) as null_stdcategory1,
        SUM(CASE WHEN stdcategory2 IS NULL OR stdcategory2 = '' THEN 1 ELSE 0 END) as null_stdcategory2,
        SUM(CASE WHEN stdcategory3 IS NULL OR stdcategory3 = '' THEN 1 ELSE 0 END) as null_stdcategory3,
        SUM(CASE WHEN device_type IS NULL OR device_type = '' THEN 1 ELSE 0 END) as null_device_type,
        COUNT(*) as total
    FROM flywheel.monthly_sales_with_dim;
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
