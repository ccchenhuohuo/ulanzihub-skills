#!/usr/bin/env python3
"""
分批导入 JSON 文件到 Doris

用法:
    python3 import_batches.py --path <数据目录>

环境变量:
    DORIS_HOST     - Doris服务器地址 (必需)
    DORIS_USER     - Doris用户名 (必需)
    DORIS_PASSWORD - Doris密码 (必需)
"""

import subprocess
import glob
import os
import argparse

# 从环境变量读取Doris连接配置（无默认值，必须设置）
DORIS_HOST = os.environ.get("DORIS_HOST")
DORIS_USER = os.environ.get("DORIS_USER")
DORIS_PASSWORD = os.environ.get("DORIS_PASSWORD")

# 验证必需的环境变量
if not DORIS_HOST or not DORIS_USER or not DORIS_PASSWORD:
    raise ValueError("缺少必需的环境变量: DORIS_HOST, DORIS_USER, DORIS_PASSWORD")
DATABASE = "flywheel"
TABLE_NAME = "product_category_dimension"

# StreamLoad URL
URL = f"http://{DORIS_HOST}:33060/api/{DATABASE}/{TABLE_NAME}/_stream_load"

def import_batch(json_file):
    """导入单个 JSON 文件"""
    cmd = [
        "curl", "-s", "-w", "\\n%{http_code}",
        "--location-trusted",
        "-u", f"{DORIS_USER}:{DORIS_PASSWORD}",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "Expect: 100-continue",
        "-H", "column_separator: ,",
        "-H", "format: json",
        "-H", "strip_outer_array: true",
        "-H", "ignore_json_size: true",
        "-d", f"@{json_file}",
        URL
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    if '"Status": "Success"' in output:
        return True, output
    else:
        return False, output

def main():
    parser = argparse.ArgumentParser(description='批量导入JSON到Doris')
    parser.add_argument('--path', required=True, help='数据目录（JSON文件所在目录）')
    args = parser.parse_args()

    BATCH_DIR = args.path

    print(f"Doris服务器: {DORIS_HOST}")
    print(f"目标表: {DATABASE}.{TABLE_NAME}")
    print("=" * 50)

    # 获取所有 batch 文件
    batch_files = sorted(glob.glob(f"{BATCH_DIR}/batch_*.json"))
    total = len(batch_files)

    print(f"总共 {total} 个文件待导入")
    print("=" * 50)

    success = 0
    fail = 0

    for i, file in enumerate(batch_files, 1):
        filename = os.path.basename(file)
        ok, result = import_batch(file)

        if ok:
            print(f"[{i}/{total}] {filename}: 成功")
            success += 1
        else:
            print(f"[{i}/{total}] {filename}: 失败")
            print(f"  错误: {result[:200]}")
            fail += 1

        # 每 50 批显示进度
        if i % 50 == 0:
            print(f"--- 进度: {i}/{total} (成功: {success}, 失败: {fail}) ---")

    print("=" * 50)
    print(f"导入完成！")
    print(f"总批数: {total}")
    print(f"成功: {success}")
    print(f"失败: {fail}")

if __name__ == "__main__":
    main()
