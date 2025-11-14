import os
import json
import re
from datetime import datetime, timezone
import httpx
from app.models.concept import ConceptTree, ConceptNode, TreeStats

_progress_store: dict[str, dict] = {}

def _set_progress(key: str, stage: int, message: str, percent: int):
    k = key.lower()
    _progress_store[k] = {
        "stage": stage,
        "message": message,
        "percent": max(0, min(100, percent)),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }

def get_progress(concept: str) -> dict:
    return _progress_store.get(concept.lower(), {
        "stage": 0,
        "message": "idle",
        "percent": 0,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    })

def _normalize_json_text(s: str) -> str:
    t = s.strip()
    t = re.sub(r"^[`\s]*```(?:json)?", "", t)
    t = re.sub(r"```[`\s]*$", "", t)
    t = re.sub(r"//.*", "", t)
    t = re.sub(r"/\*[\s\S]*?\*/", "", t)
    t = re.sub(r"\,(\s*[}\]])", r"\1", t)
    t = re.sub(r"'", '"', t)
    t = t.strip()
    return t

def _parse_message_json(msg: dict) -> dict:
    tool_calls = msg.get("tool_calls") or []
    content = msg.get("content")
    if tool_calls:
        args = tool_calls[0].get("function", {}).get("arguments", "")
        if not args:
            raise ValueError("ai tool_calls empty arguments")
        try:
            return json.loads(args)
        except Exception:
            return json.loads(_normalize_json_text(args))
    if not content:
        raise ValueError("ai empty content")
    content = re.sub(r"<think>[\s\S]*?</think>", "", content)
    try:
        return json.loads(content)
    except Exception:
        return json.loads(_normalize_json_text(content))

def _get_provider_config() -> tuple[str, dict, str]:
    provider = os.getenv("AI_PROVIDER", "minimax").strip().lower()
    model = os.getenv("AI_MODEL", "").strip()
    headers = {"Content-Type": "application/json"}
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("AI service unavailable: missing DEEPSEEK_API_KEY")
        headers["Authorization"] = f"Bearer {api_key}"
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        if not model:
            model = "deepseek-chat"
        return base_url, headers, model
    if provider == "kimi":
        api_key = os.getenv("KIMI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("AI service unavailable: missing KIMI_API_KEY")
        headers["Authorization"] = f"Bearer {api_key}"
        base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn").rstrip("/")
        if not model:
            model = "moonshot-v1-8k"
        return base_url, headers, model
    # default minimax
    api_key = os.getenv("MINIMAX_API_KEY", "").strip()
    if not api_key:
        raise ValueError("AI service unavailable: missing MINIMAX_API_KEY")
    headers["Authorization"] = f"Bearer {api_key}"
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1").rstrip("/")
    if not model:
        model = "MiniMax-M2"
    return base_url, headers, model

def _count_nodes(n: ConceptNode) -> int:
    return 1 + sum(_count_nodes(c) for c in (n.children or []))

def _calc_depth(n: ConceptNode) -> int:
    if not n.children:
        return 0
    return 1 + max(_calc_depth(c) for c in n.children)

def _collect_ids(n: ConceptNode, acc: set):
    acc.add(n.id)
    for c in (n.children or []):
        _collect_ids(c, acc)

def _ensure_unique_id(base: str, ids: set) -> str:
    bid = base
    i = 1
    while bid in ids:
        bid = f"{base}-{i}"
        i += 1
    ids.add(bid)
    return bid

def _expand_known_topics(root: ConceptNode, max_width: int):
    ids = set()
    _collect_ids(root, ids)

    def match_sorting(name: str) -> bool:
        s = (name or "").lower()
        return ("排序" in name) or ("sorting" in s) or ("sort" in s)

    def expand_sorting(node: ConceptNode):
        if node.children is None:
            node.children = []
        if len(node.children) >= max_width:
            return
        templates = [
            ("bubble_sort", "冒泡排序", "稳定的对比交换排序，适合小规模数据"),
            ("selection_sort", "选择排序", "每轮选择最小/最大元素，简单但效率较低"),
            ("insertion_sort", "插入排序", "通过逐步插入构建有序序列，适合近乎有序数据"),
            ("merge_sort", "归并排序", "分治合并，稳定且时间复杂度O(n log n)"),
            ("quick_sort", "快速排序", "分治与划分，平均O(n log n)，工程中常用"),
            ("heap_sort", "堆排序", "利用堆结构选择性输出，时间复杂度O(n log n)"),
        ]
        for base_id, nm, desc in templates:
            if len(node.children) >= max_width:
                break
            cid = _ensure_unique_id(base_id, ids)
            node.children.append(ConceptNode(id=cid, name=nm, description=desc, level=max(node.level - 1, 0), children=[]))

    def dfs(n: ConceptNode):
        if match_sorting(n.name):
            expand_sorting(n)
        for ch in (n.children or []):
            dfs(ch)

    dfs(root)
    return root

async def generate_concept_tree(concept: str, req_max_depth: int | None = None, req_max_width: int | None = None, branch_focus_ids: list[str] | None = None, branch_min_widths: dict[str, int] | None = None, branch_priorities: dict[str, int] | None = None, refine_enabled: bool = True) -> ConceptTree:
    name = concept.strip()
    if not name:
        raise ValueError("empty concept")

    base_url, headers, model_name = _get_provider_config()

    _set_progress(name, 1, "准备生成依赖树", 5)

    _set_progress(name, 2, "Building dependency tree...", 25)

    prompt = (
        "你是一个知识图谱构建专家。根据用户给出的目标概念，生成其学习依赖树。"
        "严格按以下JSON格式输出，不要包含其他说明或markdown：\n"
        "{\n"
        "  \"root\": {\n"
        "    \"id\": \"string\",\n"
        "    \"name\": \"string\",\n"
        "    \"description\": \"string\",\n"
        "    \"level\": number,\n"
        "    \"children\": [ { ... 子节点，字段同root ... } ]\n"
        "  }\n"
        "}\n"
        "规则：\n"
        "1. 使用嵌套children表示树；\n"
        "2. id必须唯一且稳定，可用短字母或语义化；\n"
        "3. level为难度等级0-10，前置概念的level应低于或接近父节点；\n"
        "4. 每个节点的description简要说明其与目标的关系；\n"
        "5. 至少生成4层结构（或直到基础概念不可再细分），根节点下建议3-6个分支；\n"
        "6. 细化到初高中知识层级，例如数学/物理/编程的基础概念。\n"
    )

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是严谨的知识图谱构建专家。请通过函数调用返回树数据，并严格遵守参数要求。"},
            {"role": "user", "content": f"目标概念：{name}\n期望深度≥4，直到基础概念（初高中知识）为止；每层建议3-6个分支；最大深度={req_max_depth or os.getenv('TREE_MAX_DEPTH', '8')}，最大宽度={req_max_width or os.getenv('TREE_MAX_WIDTH', '8')}。\n{prompt}"},
        ],
        "temperature": 1.0,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "build_concept_tree",
                    "description": "返回嵌套的概念树",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "root": {
                                "$ref": "#/$defs/ConceptNode"
                            }
                        },
                        "required": ["root"],
                        "$defs": {
                            "ConceptNode": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "level": {"type": "integer"},
                                    "children": {
                                        "type": "array",
                                        "items": {"$ref": "#/$defs/ConceptNode"}
                                    }
                                },
                                "required": ["id", "name", "description", "level"],
                                "additionalProperties": False
                            }
                        }
                    }
                }
            }
        ],
        "tool_choice": "required",
    }

    
    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    _set_progress(name, 3, "接收AI响应", 60)

    msg = data.get("choices", [{}])[0].get("message", {})
    _set_progress(name, 4, "解析JSON", 70)
    parsed = _parse_message_json(msg)
    # parsed 已在上面分支解析得到

    def ensure_root(p):
        if isinstance(p, dict):
            if "root" in p and isinstance(p["root"], (dict, list, str)):
                return p["root"]
            # 有可能直接就是节点对象
            if {"id", "name"}.issubset(set(p.keys())):
                return p
        if isinstance(p, list) and p and isinstance(p[0], dict):
            return p[0]
        if isinstance(p, str):
            try:
                j = json.loads(p)
                return ensure_root(j)
            except Exception:
                return None
        return None

    root_obj = ensure_root(parsed)
    if not isinstance(root_obj, dict):
        # 兜底：构造最小根节点，保证前端可渲染
        root_obj = {
            "id": "root",
            "name": name,
            "description": name,
            "level": 0,
            "children": [],
        }

    max_depth = int(req_max_depth or os.getenv("TREE_MAX_DEPTH", "8"))
    max_width = int(req_max_width or os.getenv("TREE_MAX_WIDTH", "8"))

    def _clamp_level(v):
        try:
            i = int(v)
        except Exception:
            i = 0
        if i < 0:
            i = 0
        if i > 10:
            i = 10
        return i

    def normalize_node(obj, depth, parent_id, seen_ids):
        if not isinstance(obj, dict):
            obj = {"id": str(obj), "name": str(obj), "description": str(obj), "level": 0, "children": []}
        raw_id = str(obj.get("id")) if obj.get("id") is not None else None
        if not raw_id or raw_id in seen_ids:
            base = (raw_id or "node")
            idx = 1
            nid = f"{base}-{idx}"
            while nid in seen_ids:
                idx += 1
                nid = f"{base}-{idx}"
            node_id = nid
        else:
            node_id = raw_id
        seen_ids.add(node_id)

        name = str(obj.get("name")) if obj.get("name") not in (None, "") else node_id
        desc = obj.get("description")
        if desc is None or (isinstance(desc, str) and desc.strip() == ""):
            desc = name
        level = _clamp_level(obj.get("level", 0))

        raw_children = obj.get("children") or []
        # 规范化子节点输入，避免循环引用与非法类型
        children_in = []
        for c in raw_children:
            if isinstance(c, dict):
                cid = c.get("id")
                if cid is not None and str(cid) == node_id:
                    continue
                children_in.append(c)
            else:
                children_in.append({"id": str(c), "name": str(c), "description": str(c), "level": 0, "children": []})
        children_fix = []
        for c in children_in:
            cid = str(c.get("id")) if isinstance(c, dict) and c.get("id") is not None else None
            if cid and cid in seen_ids:
                continue
            children_fix.append(normalize_node(c, depth + 1, node_id, seen_ids))

        node = ConceptNode(
            id=node_id,
            name=name,
            description=str(desc),
            level=level,
            children=children_fix,
            parent=parent_id,
        )
        return node

    root = normalize_node(root_obj, 0, None, set())

    _set_progress(name, 4, "Optimizing learning path", 80)

    def _index_nodes_by_id(n: ConceptNode, acc: dict[str, ConceptNode]):
        acc[n.id] = n
        for c in (n.children or []):
            _index_nodes_by_id(c, acc)

    def _node_depths(n: ConceptNode, depth: int, acc: dict[str, int]):
        acc[n.id] = depth
        for c in (n.children or []):
            _node_depths(c, depth + 1, acc)

    def _merge_expansions(cur_root: ConceptNode, expansions: list, max_width_cap: int) -> ConceptNode:
        id_map: dict[str, ConceptNode] = {}
        _index_nodes_by_id(cur_root, id_map)
        depths: dict[str, int] = {}
        _node_depths(cur_root, 0, depths)
        seen_ids: set[str] = set()
        _collect_ids(cur_root, seen_ids)

        for exp in (expansions or []):
            if not isinstance(exp, dict):
                continue
            parent_id = str(exp.get("parentId")) if exp.get("parentId") is not None else None
            if not parent_id or parent_id not in id_map:
                continue
            parent = id_map[parent_id]
            recommended_width = exp.get("recommendedWidth")
            target_width = max_width_cap
            try:
                if recommended_width is not None:
                    target_width = max(1, min(int(recommended_width), max_width_cap))
            except Exception:
                target_width = max_width_cap

            children = exp.get("children") or []
            for child in children:
                if len(parent.children or []) >= target_width:
                    break
                norm = normalize_node(child, depths.get(parent_id, 0) + 1, parent_id, seen_ids)
                if any((ch.id == norm.id) for ch in (parent.children or [])):
                    continue
                if parent.children is None:
                    parent.children = []
                parent.children.append(norm)
        return cur_root

    async def _refine_with_ai(cur_root: ConceptNode) -> ConceptNode:
        base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1").rstrip("/")
        headers = {"Content-Type": "application/json"}
        try:
            # 使用统一的提供者配置
            base_url, headers, model2 = _get_provider_config()
        except Exception:
            return cur_root
        payload = {
            "model": model2,
            "messages": [
                {"role": "system", "content": "你是知识图谱细化助手。请分析每个子树的成熟度，并仅返回需要扩展的分支列表。不要替换已有节点结构，只追加。每个分支可有不同的推荐宽度和目标深度，整体仍需遵守全局上限。"},
                {"role": "user", "content": f"目标概念：{name}\n全局最大深度：{max_depth}；每层全局最大宽度：{max_width}。分支焦点：{json.dumps(branch_focus_ids or [], ensure_ascii=False)}；分支最小宽度：{json.dumps(branch_min_widths or {}, ensure_ascii=False)}；分支优先级：{json.dumps(branch_priorities or {}, ensure_ascii=False)}。请针对当前树进行第二次分析，优先扩展焦点分支，并给出扩展建议（仅返回 expansions 数组）：\n{json.dumps({'root': cur_root.model_dump()}, ensure_ascii=False)}"},
            ],
            "temperature": 1.0,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.RequestError:
            return cur_root
        msg = data.get("choices", [{}])[0].get("message", {})
        try:
            proposal = _parse_message_json(msg)
        except Exception:
            return cur_root
        expansions = proposal.get("expansions") if isinstance(proposal, dict) else []
        if not expansions:
            root_obj2 = proposal.get("root") if isinstance(proposal, dict) else None
            if isinstance(root_obj2, dict):
                new_root = normalize_node(root_obj2, 0, None, set())
                if _count_nodes(new_root) > _count_nodes(cur_root) or _calc_depth(new_root) > _calc_depth(cur_root):
                    return new_root
            return cur_root
        if branch_min_widths:
            for e in expansions:
                pid = str(e.get("parentId")) if e.get("parentId") is not None else None
                if pid and pid in branch_min_widths:
                    mw = branch_min_widths.get(pid, 1)
                    recw = e.get("recommendedWidth")
                    try:
                        e["recommendedWidth"] = max(int(mw), int(recw) if recw is not None else 1)
                    except Exception:
                        e["recommendedWidth"] = max(int(mw), 1)
        merged_root = _merge_expansions(cur_root, expansions, max_width)
        if _count_nodes(merged_root) <= _count_nodes(cur_root) and _calc_depth(merged_root) <= _calc_depth(cur_root):
            return cur_root
        return merged_root

    rounds = 0
    try:
        while refine_enabled and rounds < 2:
            new_root = await _refine_with_ai(root)
            if _count_nodes(new_root) <= _count_nodes(root):
                break
            root = new_root
            rounds += 1
    except Exception:
        _set_progress(name, 4, "Optimize step skipped (error)", 80)
    _set_progress(name, 5, "校验并计算统计", 85)

    tree = ConceptTree(
        target=name,
        root=root,
        total_nodes=_count_nodes(root),
        max_depth=_calc_depth(root),
        stats=TreeStats(),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    _set_progress(name, 6, "完成", 100)

    return tree
