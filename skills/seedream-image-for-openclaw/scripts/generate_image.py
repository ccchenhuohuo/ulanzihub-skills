#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

import argparse
import json
import os
import sys
import requests
import tempfile
import uuid

# 获取脚本自身所在目录（兼容 uv run 和直接运行）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
SKILL_DIR = os.path.dirname(SCRIPT_DIR)  # skill 根目录

# 默认输出目录（兼容不同部署环境）
DEFAULT_OUTPUT_DIR = os.environ.get("SEEDREAM_OUTPUT_DIR", os.path.expanduser("~/Downloads/seedream"))


def generate_image(prompt, model, size, api_key, image_input=None, sequential=False, max_images=1):
    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
    }
    
    if image_input:
        payload["image"] = image_input
        
    if sequential:
        payload["sequential_image_generation"] = "auto"
        payload["sequential_image_generation_options"] = {"max_images": max_images}
    else:
        payload["sequential_image_generation"] = "disabled"

    try:
        # 添加超时设置，防止请求无限等待
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        if "data" in result and len(result["data"]) > 0:
            for item in result["data"]:
                if "url" in item:
                    image_url = item['url']
                    # 自动下载图片到本地
                    print(f"正在下载图片...", file=sys.stderr)
                    img_response = requests.get(image_url, timeout=60)
                    img_response.raise_for_status()

                    # 确保输出目录存在
                    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

                    # 保存到本地文件
                    local_path = f"{DEFAULT_OUTPUT_DIR}/seedream_{uuid.uuid4().hex[:8]}.jpg"
                    with open(local_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"LOCAL_PATH: {local_path}", file=sys.stderr)
                    print(f"MEDIA_URL: {image_url}")
                elif "b64_json" in item:
                    print("ERROR: Received base64 data but expected URL.")
        else:
            print(f"ERROR: No image data in response. Full response: {json.dumps(result)}")
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images using Volcengine Seedream API.")
    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--model", default="doubao-seedream-4-5-251128", help="Model ID or Endpoint ID")
    parser.add_argument("--size", default="2048x2048", help="Image size (e.g., 2K, 4K, 2048x2048)")
    parser.add_argument("--api-key", help="Volcengine API Key")
    parser.add_argument("--image", help="Input image URL or base64 (optional)")
    parser.add_argument("--sequential", action="store_true", help="Enable sequential image generation (group)")
    parser.add_argument("--max-images", type=int, default=1, help="Max images for sequential generation (1-15)")

    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("VOLC_API_KEY")
    if not api_key:
        print("ERROR: API key is required. Provide via --api-key or VOLC_API_KEY environment variable.")
        sys.exit(1)
        
    generate_image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        api_key=api_key,
        image_input=args.image,
        sequential=args.sequential,
        max_images=args.max_images
    )


if __name__ == "__main__":
    main()
