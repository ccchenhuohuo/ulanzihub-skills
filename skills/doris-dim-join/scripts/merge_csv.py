#!/usr/bin/env python3
"""
合并CSV文件并映射到Doris表结构

用法:
    python3 merge_csv.py --path <数据路径> --merge    # 仅合并CSV
    python3 merge_csv.py --path <数据路径>             # 合并并导入Doris

环境变量:
    DORIS_HOST     - Doris服务器地址 (必需)
    DORIS_PORT     - Doris HTTP端口 (必需)
    DORIS_USER     - Doris用户名 (必需)
    DORIS_PASSWORD - Doris密码 (必需)
"""

import csv
import os
import subprocess
import argparse

# ==================== 配置 ====================
# 从环境变量读取Doris连接配置（无默认值，必须设置）
DORIS_HOST = os.environ.get("DORIS_HOST")
DORIS_PORT = os.environ.get("DORIS_PORT")
DORIS_USER = os.environ.get("DORIS_USER")
DORIS_PASSWORD = os.environ.get("DORIS_PASSWORD")
DATABASE = "flywheel"
TABLE_NAME = "product_category_dimension"

# 验证必需的环境变量
if not DORIS_HOST or not DORIS_PORT or not DORIS_USER or not DORIS_PASSWORD:
    raise ValueError("缺少必需的环境变量: DORIS_HOST, DORIS_PORT, DORIS_USER, DORIS_PASSWORD")

# ==================== 目标表列定义 ====================
# 目标表 product_category_dimension 的实际字段
target_columns = [
    "device_type", "product_id", "row_num", "site", "sku_id",
    "stdcategory1", "stdcategory2", "stdcategory3", "year_num"
]

# ==================== CSV处理函数 ====================
def map_csv_to_target(row, columns):
    """将CSV行映射到目标表结构"""
    result = {col: '' for col in target_columns}

    # CSV 源字段 -> 目标表字段的映射
    col_map = {
        'devicetype': 'device_type',
        'productid': 'product_id',
        'site': 'site',           # 重要：必须有！
        'skuid': 'sku_id',
        'stdcategory1': 'stdcategory1',
        'stdcategory2': 'stdcategory2',
        'stdcategory3': 'stdcategory3',
        'yearnum': 'year_num',
        'rownum': 'row_num',
    }

    for csv_col, target_col in col_map.items():
        # 查找匹配的 CSV 列（忽略大小写）
        for col in columns:
            if col.lower().strip() == csv_col:
                result[target_col] = row.get(col, '')
                break

    return result

def merge_csv_files(csv_dir, output_file):
    """合并CSV文件（支持通配符模式：桶*.csv）"""
    import glob

    # 使用通配符匹配所有桶文件
    csv_pattern = os.path.join(csv_dir, "桶*.csv")
    csv_files = sorted(glob.glob(csv_pattern))

    if not csv_files:
        print(f"警告: 未找到匹配的CSV文件 (模式: {csv_pattern})")
        print(f"目录内容: {os.listdir(csv_dir)}")
        csv_files = []

    total_rows = 0

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=target_columns)
        writer.writeheader()

        for csv_file in csv_files:
            print(f"Processing: {csv_file}")
            with open(csv_file, 'r', encoding='utf-8-sig') as infile:
                reader = csv.DictReader(infile)
                columns = reader.fieldnames
                print(f"  Columns: {columns}")

                for row in reader:
                    mapped_row = map_csv_to_target(row, columns)
                    writer.writerow(mapped_row)
                    total_rows += 1

            print(f"  Done: {csv_file}")

    print(f"\nTotal rows written: {total_rows}")
    print(f"Output file: {output_file}")
    return total_rows

# ==================== StreamLoad 导入函数 ====================
def stream_load(output_file):
    """使用 StreamLoad 导入数据到 Doris"""
    print("\n使用 StreamLoad 方式导入...")
    print(f"Doris服务器: {DORIS_HOST}:{DORIS_PORT}")

    # 使用 Nginx 端口 33060
    url = f"http://{DORIS_HOST}:33060/api/{DATABASE}/{TABLE_NAME}/_stream_load"

    cmd = [
        "curl",
        "--location-trusted",
        "-u", f"{DORIS_USER}:{DORIS_PASSWORD}",
        "-X", "POST",
        "-H", "Content-Type: application/octet-stream",
        "-H", "Expect: 100-continue",
        "-H", "column_separator: ,",
        "-H", "format: csv",
        "-T", output_file,
        url
    ]

    print(f"URL: {url}")
    print(f"文件: {output_file}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\n返回状态码: {result.returncode}")
    print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")

    return result.returncode == 0

# ==================== 主程序 ====================
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description='合并CSV文件')
    parser.add_argument('--path', required=True, help='数据路径（CSV源文件及输出目录）')
    parser.add_argument('--merge', action='store_true', help='仅合并CSV，不导入Doris')
    args = parser.parse_args()

    csv_dir = args.path
    output_file = os.path.join(args.path, "merged_data.csv")

    # 确保输出目录存在
    os.makedirs(args.path, exist_ok=True)

    if args.merge:
        # 步骤1: 合并CSV
        print("=" * 50)
        print("步骤1: 合并CSV文件")
        print("=" * 50)
        merge_csv_files(csv_dir, output_file)
    else:
        # 步骤1: 合并CSV
        print("=" * 50)
        print("步骤1: 合并CSV文件")
        print("=" * 50)
        merge_csv_files(csv_dir, output_file)

        # 步骤2: StreamLoad导入
        print("\n" + "=" * 50)
        print("步骤2: 执行StreamLoad导入")
        print("=" * 50)
        success = stream_load(output_file)

        if success:
            print("\n导入成功!")
        else:
            print("\n导入失败，请检查错误信息")
