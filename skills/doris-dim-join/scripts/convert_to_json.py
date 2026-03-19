#!/usr/bin/env python3
"""
将合并后的CSV转换为JSON格式（分批）

用法:
    python3 convert_to_json.py --path <数据目录>

示例:
    python3 convert_to_json.py --path <数据路径>
"""

import csv
import json
import os
import argparse

# ==================== 主程序 ====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV转JSON工具')
    parser.add_argument('--path', required=True, help='数据目录（merged_data.csv和JSON输出都在此目录）')
    parser.add_argument('--batch-size', type=int, default=5000, help='每批次行数（默认5000）')
    args = parser.parse_args()

    data_dir = args.path
    input_file = os.path.join(data_dir, 'merged_data.csv')
    batch_size = args.batch_size

    # 创建输出目录
    os.makedirs(data_dir, exist_ok=True)

    # 清理已存在的JSON文件
    for f in os.listdir(data_dir):
        if f.endswith('.json'):
            os.remove(os.path.join(data_dir, f))

    # 读取合并后的CSV文件
    print(f"读取文件: {input_file}")
    all_rows = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)

    total_rows = len(all_rows)
    print(f"总行数: {total_rows}")

# 转换为目标格式并分批写入JSON
# 注意：CSV列名已经是目标表字段格式，直接取值即可
batch_num = 1
for i in range(0, total_rows, batch_size):
    batch_rows = all_rows[i:i+batch_size]
    converted_batch = []

    for row in batch_rows:
        # CSV列名已经是正确格式，不需要额外映射
        converted_row = {
            'device_type': row.get('device_type', ''),
            'product_id': row.get('product_id', ''),
            'row_num': row.get('row_num', ''),
            'site': row.get('site', ''),
            'sku_id': row.get('sku_id', ''),
            'stdcategory1': row.get('stdcategory1', ''),
            'stdcategory2': row.get('stdcategory2', ''),
            'stdcategory3': row.get('stdcategory3', ''),
            'year_num': row.get('year_num', '')
        }
        converted_batch.append(converted_row)

    # 写入JSON文件
    output_file = os.path.join(data_dir, f'batch_{batch_num:04d}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_batch, f, ensure_ascii=False, indent=2)

    print(f"已写入: {output_file} ({len(converted_batch)} 行)")
    batch_num += 1

print(f"\n=== 完成 ===")
print(f"生成 JSON 文件数: {batch_num - 1}")
print(f"总行数: {total_rows}")
