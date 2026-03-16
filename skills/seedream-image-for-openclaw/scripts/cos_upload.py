#!/usr/bin/env python3
"""
腾讯云 COS 图床上传脚本
功能：
1. 上传图片到 COS
2. 生成预签名 URL（默认 10 分钟过期）
3. 返回可用于图生图的 URL
"""

import argparse
import os
import sys
from datetime import timedelta
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def upload_to_cos(
    file_path: str,
    secret_id: str = None,
    secret_key: str = None,
    region: str = None,
    bucket: str = None,
    expire_minutes: int = 10
) -> str:
    """上传文件到 COS 并返回预签名 URL"""
    
    # 从环境变量读取配置（如果参数未提供）
    secret_id = secret_id or os.environ.get('TENCENT_COS_SECRET_ID')
    secret_key = secret_key or os.environ.get('TENCENT_COS_SECRET_KEY')
    region = region or os.environ.get('TENCENT_COS_REGION')
    bucket = bucket or os.environ.get('TENCENT_COS_BUCKET')
    
    if not all([secret_id, secret_key, region, bucket]):
        raise ValueError("请配置环境变量: TENCENT_COS_SECRET_ID, TENCENT_COS_SECRET_KEY, TENCENT_COS_REGION, TENCENT_COS_BUCKET")
    
    # 初始化 COS 客户端
    config = CosConfig(
        SecretId=secret_id,
        SecretKey=secret_key,
        Region=region
    )
    client = CosS3Client(config)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 生成唯一文件名
    filename = os.path.basename(file_path)
    import uuid
    key = f"artemis/{uuid.uuid4().hex}_{filename}"
    
    # 上传文件
    with open(file_path, 'rb') as f:
        client.put_object(
            Bucket=bucket,
            Body=f,
            Key=key,
            StorageClass='STANDARD'
        )
    
    # 生成预签名 URL（GET 方法，expire_minutes 转换为秒）
    presigned_url = client.get_presigned_url(
        Bucket=bucket,
        Key=key,
        Method='GET',
        Expired=expire_minutes * 60
    )
    
    return presigned_url


def main():
    parser = argparse.ArgumentParser(description='腾讯云 COS 图床上传工具')
    parser.add_argument('--file', '-f', required=True, help='要上传的图片文件路径')
    parser.add_argument('--secret-id', help='腾讯云 SecretId（也可通过环境变量 TENCENT_COS_SECRET_ID 设置）')
    parser.add_argument('--secret-key', help='腾讯云 SecretKey（也可通过环境变量 TENCENT_COS_SECRET_KEY 设置）')
    parser.add_argument('--region', help='COS 区域，如 ap-guangzhou（也可通过环境变量 TENCENT_COS_REGION 设置）')
    parser.add_argument('--bucket', help='COS Bucket 名称（也可通过环境变量 TENCENT_COS_BUCKET 设置）')
    parser.add_argument('--expire', '-e', type=int, default=10, help='预签名URL过期分钟数（默认10分钟）')
    
    args = parser.parse_args()
    
    try:
        url = upload_to_cos(
            file_path=args.file,
            secret_id=args.secret_id,
            secret_key=args.secret_key,
            region=args.region,
            bucket=args.bucket,
            expire_minutes=args.expire
        )
        print(url)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
