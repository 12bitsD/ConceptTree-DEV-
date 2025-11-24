import os
import json
from typing import List, Dict, Any
import httpx


async def generate_refine_options(concept: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("KIMI_API_KEY")
    api_url = os.getenv("KIMI_API_URL", "https://api.moonshot.cn/v1/chat/completions")
    model = os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview")
    if not api_key:
        raise RuntimeError("missing_api_key")
    try:
        system = (
            "你是一个产品助理，负责为用户输入的任务生成结构化的补充细节选项。"
            "严格只返回 JSON，不要任何额外文本。"
        )
        user = (
            "请基于下述任务，生成 3-6 个可勾选的细化选项。"
            "每项包含字段：id、title、description、type、defaultChecked、suggested(可选)。"
            "要求：紧贴任务语境、覆盖预算/偏好/限制等常见维度、避免重复与含糊。"
            f"任务：{concept}"
        )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            resp = await client.post(api_url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"bad_status:{resp.status_code}")
        data = resp.json()
        content = None
        try:
            choices = data.get("choices") or []
            if choices:
                content = choices[0].get("message", {}).get("content")
        except Exception:
            content = None
        if not content:
            raise RuntimeError("empty_content")
        try:
            parsed = json.loads(content)
        except Exception:
            raise RuntimeError("json_parse_error")
        if isinstance(parsed, dict) and "options" in parsed:
            parsed = parsed["options"]
        if not isinstance(parsed, list):
            raise RuntimeError("invalid_structure")
        result: List[Dict[str, Any]] = []
        for o in parsed:
            try:
                raw_type = str(o.get("type", "single-line")).lower()
                if raw_type in {"checkbox", "multi", "multi_select", "multi-select", "chips", "tags"}:
                    norm_type = "multi-select"
                elif raw_type in {"textarea", "long_text", "multiline", "multi-line"}:
                    norm_type = "multi-line"
                else:
                    norm_type = "single-line"
                result.append(
                    {
                        "id": str(o.get("id")),
                        "title": str(o.get("title")),
                        "description": o.get("description"),
                        "type": norm_type,
                        "defaultChecked": bool(o.get("defaultChecked", False)),
                        "suggested": o.get("suggested") or None,
                    }
                )
            except Exception:
                continue
        return result
    except Exception as e:
        raise e

async def check_kimi_status() -> Dict[str, Any]:
    api_key = os.getenv("KIMI_API_KEY")
    api_url = os.getenv("KIMI_API_URL", "https://api.moonshot.cn/v1/chat/completions")
    model = os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview")
    env_present = bool(api_key)
    can_call = False
    if env_present:
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "ping"},
                    {"role": "user", "content": "ping"},
                ],
                "temperature": 0,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                resp = await client.post(api_url, headers=headers, json=payload)
            if resp.status_code == 200:
                can_call = True
        except Exception:
            can_call = False
    return {"env_present": env_present, "can_call": can_call, "model": model, "api_url": api_url}