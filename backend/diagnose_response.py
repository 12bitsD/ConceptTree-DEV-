#!/usr/bin/env python3
"""
诊断AI响应格式
"""

import asyncio
import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv
import httpx

# 加载环境变量
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

async def diagnose():
    provider = os.getenv("AI_PROVIDER", "minimax").strip().lower()
    model = os.getenv("AI_MODEL", "MiniMax-M2").strip()
    api_key = os.getenv("MINIMAX_API_KEY", "").strip()
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat").rstrip("/")
    
    print("=" * 80)
    print("AI响应格式诊断")
    print("=" * 80)
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    url = f"{base_url}/v1/chat/completions"
    
    # 简化的prompt
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是知识图谱专家。请严格按JSON格式返回。"},
            {"role": "user", "content": '生成"Python"的概念树，包含2层，每层2个子节点。严格JSON格式：{"root": {"id": "root", "name": "Python", "description": "描述", "level": 0, "children": [...]}}'}
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
    }
    
    print(f"发送请求到: {url}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=15.0, read=180.0, write=60.0, pool=10.0)) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"[OK] 响应成功 (状态码: {resp.status_code})")
            print()
            
            # 分析响应结构
            if "choices" in data and data["choices"]:
                msg = data["choices"][0].get("message", {})
                content = msg.get("content", "")
                
                print(f"Content长度: {len(content)} 字符")
                print()
                print("=" * 80)
                print("原始Content:")
                print("=" * 80)
                print(content)
                print()
                print("=" * 80)
                
                # 尝试去除<think>标签
                content_no_think = re.sub(r"<think>[\s\S]*?</think>", "", content)
                print(f"\n去除<think>后长度: {len(content_no_think)} 字符")
                print("=" * 80)
                print("去除<think>后的Content:")
                print("=" * 80)
                print(content_no_think)
                print()
                
                # 尝试规范化
                normalized = content_no_think.strip()
                normalized = re.sub(r"```+\s*json\s*\n?", "", normalized, flags=re.IGNORECASE)
                normalized = re.sub(r"```+\s*", "", normalized)
                
                print(f"\n规范化后长度: {len(normalized)} 字符")
                print("=" * 80)
                print("规范化后的Content:")
                print("=" * 80)
                print(normalized)
                print()
                
                # 尝试解析
                print("=" * 80)
                print("解析测试:")
                print("=" * 80)
                try:
                    parsed = json.loads(normalized)
                    print("[OK] 直接解析成功！")
                    print(f"Keys: {list(parsed.keys())}")
                    if "root" in parsed:
                        print("[OK] 包含 'root' 字段")
                        root = parsed["root"]
                        print(f"  Root name: {root.get('name')}")
                        print(f"  Root children: {len(root.get('children', []))}")
                except json.JSONDecodeError as e:
                    print(f"[FAIL] 直接解析失败: {e}")
                    
                    # 尝试提取JSON
                    print("\n尝试提取JSON段...")
                    m = re.search(r"\{[\s\S]*\}", normalized)
                    if m:
                        extracted = m.group(0)
                        print(f"[OK] 提取到JSON段 (长度: {len(extracted)})")
                        try:
                            parsed = json.loads(extracted)
                            print("[OK] 提取的JSON解析成功！")
                            print(f"Keys: {list(parsed.keys())}")
                        except json.JSONDecodeError as e2:
                            print(f"[FAIL] 提取的JSON解析失败: {e2}")
                    else:
                        print("[FAIL] 未找到JSON段")
                        
            else:
                print("[FAIL] 响应中没有choices或为空")
                print(f"响应数据: {data}")
                
    except Exception as e:
        print(f"[FAIL] 请求失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose())
