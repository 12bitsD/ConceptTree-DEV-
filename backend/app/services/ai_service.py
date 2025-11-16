import os
import json
import re
import logging
from datetime import datetime, timezone
import httpx
from app.models.concept import ConceptTree, ConceptNode, TreeStats

# 配置日志
logger = logging.getLogger(__name__)

# 安全限制常量
MAX_CONCEPT_LENGTH = 200  # 最大概念名称长度
MAX_TREE_NODES = 500  # 最大树节点数，防止无限扩展
MAX_TREE_DEPTH = 15  # 最大树深度，防止递归溢出
MAX_RECURSION_DEPTH = 100  # 最大递归深度
MAX_ID_GENERATION_ATTEMPTS = 1000  # ID生成最大尝试次数

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

def _fix_json_syntax(s: str) -> str:
    """
    修复常见的JSON语法错误
    """
    t = s
    original_len = len(t)
    
    # 0. 先处理缺少冒号的问题（在规范化空白之前）
    # 匹配: "key" "value" -> "key": "value"
    # 匹配: "key" { -> "key": {
    # 匹配: "key" [ -> "key": [
    # 匹配: "key" null/true/false/number -> "key": value
    before_len = len(t)
    # 这个正则需要在空白规范化之前执行，因为它依赖空白来判断
    t = re.sub(r'"([^"]+)"\s+("(?:[^"]*)"|\{|\[|null|true|false|\d+)', r'"\1": \2', t)
    # 还要处理没有空格的情况（紧挨着）
    t = re.sub(r'"([^"]+)"(\{|\[)', r'"\1": \2', t)
    if len(t) != before_len:
        logger.debug(f"修复了缺少冒号的情况")
    
    # 1. 预处理：修复换行符问题
    # 移除字符串值中不该有的换行符（除非被转义）
    # 这里只是简单地将多余的空白规范化
    t = re.sub(r'\s+', ' ', t)  # 将多个空白字符压缩为单个空格
    t = re.sub(r'\s*([{}\[\],:])\s*', r'\1', t)  # 移除特殊字符周围的空格
    # 在冒号和逗号后添加空格以提高可读性
    t = re.sub(r'([{,])', r'\1 ', t)
    t = re.sub(r':', ': ', t)
    if len(t) != original_len:
        logger.debug(f"规范化了空白字符")
    if len(t) != before_len:
        logger.debug(f"修复了缺少冒号的情况")
    
    # 2. 修复对象/数组开始后立即跟逗号的情况
    # 匹配: {, -> {  或 [, -> [
    before_len = len(t)
    t = re.sub(r'(\{|\[)\s*,', r'\1', t)
    if len(t) != before_len:
        logger.debug(f"修复了对象/数组开始后的逗号")
    
    # 3. 修复逗号后紧跟逗号的情况（双逗号）
    # 匹配: ,, -> ,
    before_len = len(t)
    t = re.sub(r',\s*,+', ',', t)
    if len(t) != before_len:
        logger.debug(f"移除了双逗号")
    
    # 4. 修复冒号后紧跟逗号的情况（缺少值）
    # 匹配: ":," -> ": null,"
    before_len = len(t)
    t = re.sub(r':\s*,', ': null,', t)
    if len(t) != before_len:
        logger.debug(f"修复了冒号后缺少值的情况")
    
    # 5. 修复冒号后紧跟闭合括号的情况（缺少值）
    # 匹配: ": }" -> ": null }"  或 ": ]" -> ": null ]"
    before_len = len(t)
    t = re.sub(r':\s*([\}\]])', r': null\1', t)
    if len(t) != before_len:
        logger.debug(f"修复了冒号后紧跟闭合括号的情况")
    
    # 6. 修复双冒号
    # 匹配: :: -> :
    before_len = len(t)
    t = re.sub(r':\s*:+', ':', t)
    if len(t) != before_len:
        logger.debug(f"移除了双冒号")
    
    # 7. 修复对象属性之间缺少逗号的情况
    # 匹配: "value" "key" -> "value", "key"
    before_len = len(t)
    t = re.sub(r'("\s*:\s*(?:"[^"]*"|(?![\{\[])[^",\s}\]]+))\s*(")', r'\1, \2', t)
    if len(t) != before_len:
        logger.debug(f"修复了对象属性之间缺少的逗号")
    
    # 8. 修复数组元素之间缺少逗号的情况（闭合括号后跟新对象）
    # 匹配: }{ -> },{
    before_len = len(t)
    t = re.sub(r'(\})(\{)', r'\1, \2', t)
    if len(t) != before_len:
        logger.debug(f"修复了数组元素之间缺少的逗号")
    
    # 9. 修复 ]{ 和 }[
    before_len = len(t)
    t = re.sub(r'(\])(\{)', r'\1, \2', t)
    t = re.sub(r'(\})(\[)', r'\1, \2', t)
    if len(t) != before_len:
        logger.debug(f"修复了数组和对象之间缺少的逗号")
    
    # 10. 修复逗号后紧跟闭合括号的情况（冗余逗号）
    # 匹配: ,} -> }  或 ,] -> ]
    before_len = len(t)
    t = re.sub(r',\s*([\}\]])', r'\1', t)
    if len(t) != before_len:
        logger.debug(f"移除了尾随逗号")
    
    return t

def _normalize_json_text(s: str) -> str:
    t = s.strip()
    original_start = t[:100] if len(t) > 100 else t
    logger.debug(f"_normalize_json_text 输入前100字符: {original_start}")
    
    # 去除markdown代码块标记（包括多行情况）
    t = re.sub(r"```+\s*json\s*\n?", "", t, flags=re.IGNORECASE)
    t = re.sub(r"```+\s*", "", t)
    # 去除注释
    t = re.sub(r"//.*", "", t)
    t = re.sub(r"/\*[\s\S]*?\*/", "", t)
    # 统一引号
    t = re.sub(r"'", '"', t)
    t = t.strip()
    
    # 先修复常见的JSON语法错误，再移除尾随逗号
    logger.debug(f"调用 _fix_json_syntax 前: {t[:100]}")
    t = _fix_json_syntax(t)
    logger.debug(f"调用 _fix_json_syntax 后: {t[:100]}")
    
    # 再次移除尾随逗号（以防修复过程中产生新的尾随逗号）
    for _ in range(2):
        t = re.sub(r",(\s*[}\]])", r"\1", t)
    
    # 在字符串字面量内替换换行符为\n，避免未终止字符串
    out = []
    in_string = False
    escape = False
    for ch in t:
        if in_string:
            if escape:
                out.append(ch)
                escape = False
                continue
            if ch == "\\":
                out.append(ch)
                escape = True
                continue
            if ch == '"':
                out.append(ch)
                in_string = False
                continue
            if ch == '\n' or ch == '\r':
                out.append('\\n')
                continue
            out.append(ch)
        else:
            if ch == '"':
                out.append(ch)
                in_string = True
                continue
            out.append(ch)
    t = ''.join(out)
    
    return t

def _extract_json_segment(s: str) -> str:
    t = _normalize_json_text(s)
    logger.debug(f"_extract_json_segment规范化后前150字符: {t[:150]}")
    start = None
    stack = []
    in_string = False
    escape = False
    for i, ch in enumerate(t):
        if start is None:
            if ch == '{' or ch == '[':
                start = i
                stack.append('}' if ch == '{' else ']')
                continue
        else:
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == '{':
                    stack.append('}')
                elif ch == '[':
                    stack.append(']')
                elif stack and ch == stack[-1]:
                    stack.pop()
                    if not stack:
                        seg = t[start:i+1]
                        logger.debug(f"提取到的平衡JSON段前150字符: {seg[:150]}")
                        return seg
    return t

def _extract_json_segment_with_key(s: str, key: str) -> str:
    t = _normalize_json_text(s)
    i = 0
    while i < len(t):
        ch = t[i]
        if ch == '{' or ch == '[':
            start = i
            stack = ['}' if ch == '{' else ']']
            in_string = False
            escape = False
            i += 1
            while i < len(t):
                c = t[i]
                if in_string:
                    if escape:
                        escape = False
                    elif c == '\\':
                        escape = True
                    elif c == '"':
                        in_string = False
                else:
                    if c == '"':
                        in_string = True
                    elif c == '{':
                        stack.append('}')
                    elif c == '[':
                        stack.append(']')
                    elif stack and c == stack[-1]:
                        stack.pop()
                        if not stack:
                            seg = t[start:i+1]
                            if re.search(rf'"{key}"\s*:', seg):
                                return seg
                            break
                i += 1
        else:
            i += 1
    return _extract_json_segment(s)

def _parse_message_json(msg: dict) -> dict:
    tool_calls = msg.get("tool_calls") or []
    content = msg.get("content")
    if tool_calls:
        args = tool_calls[0].get("function", {}).get("arguments", "")
        if not args:
            raise ValueError("ai tool_calls empty arguments")
        try:
            return json.loads(args)
        except Exception as e:
            logger.debug(f"解析tool_calls参数失败，尝试提取JSON段: {e}")
            return json.loads(_extract_json_segment(args))
    if not content:
        raise ValueError("ai empty content")
    
    # 处理思考标签（MiniMax特有）
    # 先检查<think>标签外是否有内容
    content_outside_think = re.sub(r"<think>[\s\S]*?</think>", "", content)
    logger.debug(f"去除<think>标签后的内容长度: {len(content_outside_think)}, 前200字符: {content_outside_think[:200]}")
    
    # 如果标签外没有有效内容，尝试从标签内提取JSON
    if len(content_outside_think.strip()) < 50:
        logger.warning("去除<think>标签后内容太少，尝试从标签内提取JSON...")
        think_match = re.search(r"<think>([\s\S]*?)</think>", content)
        if think_match:
            think_content = think_match.group(1)
            logger.debug(f"<think>标签内容长度: {len(think_content)}")
            # 尝试从think标签内提取JSON
            json_in_think = re.search(r"\{[\s\S]*\"root\"[\s\S]*\}", think_content)
            if json_in_think:
                content = json_in_think.group(0)
                logger.info("成功从<think>标签内提取到JSON内容")
            else:
                logger.warning("在<think>标签内未找到JSON内容")
                content = content_outside_think
        else:
            content = content_outside_think
    else:
        content = content_outside_think
    
    # 先规范化内容
    logger.debug("开始规范化JSON文本...")
    content_normalized = _normalize_json_text(content)
    logger.debug(f"规范化后长度: {len(content_normalized)}, 前200字符: {content_normalized[:200]}")
    
    # 第一次尝试：直接解析规范化后的内容
    try:
        result = json.loads(content_normalized)
        logger.debug("直接JSON解析成功")
        return result
    except json.JSONDecodeError as e1:
        logger.debug(f"直接JSON解析失败: {e1}, 尝试提取JSON段")
        # 第二次尝试：从规范化后的内容中提取JSON段
        try:
            # 重要：使用规范化后的内容，而不是原始content
            extracted = _extract_json_segment(content_normalized)
            logger.debug(f"提取的JSON段长度: {len(extracted)}")
            if not extracted or len(extracted) < 10:
                raise ValueError(f"提取的JSON段太短或为空: {extracted[:100]}")
            logger.debug(f"提取的JSON段前200字符: {extracted[:200]}")
            result = json.loads(extracted)
            logger.debug("从提取的JSON段解析成功")
            return result
        except Exception as e2:
            logger.error(f"提取JSON段后解析失败: {e2}")
            
            # 尝试找出并修复问题位置
            if "line" in str(e2) and "column" in str(e2):
                try:
                    import re as re2
                    match = re2.search(r"line (\d+) column (\d+) \(char (\d+)\)", str(e2))
                    if match:
                        line_num = int(match.group(1))
                        col_num = int(match.group(2))
                        char_pos = int(match.group(3))
                        lines = extracted.split('\n')
                        
                        logger.error(f"JSON错误位置: line {line_num}, column {col_num}, char {char_pos}")
                        
                        if line_num <= len(lines):
                            logger.error(f"错误位置附近的内容:")
                            start_line = max(0, line_num - 3)
                            end_line = min(len(lines), line_num + 2)
                            for i in range(start_line, end_line):
                                prefix = ">>>" if i == line_num - 1 else "   "
                                logger.error(f"{prefix} {i+1}: {lines[i]}")
                        
                        # 尝试更激进的修复
                        logger.info("尝试更激进的JSON修复...")
                        try:
                            # 在错误字符位置前后尝试添加逗号
                            if char_pos > 0 and char_pos < len(extracted):
                                # 检查是否是缺少逗号的情况
                                before_char = extracted[char_pos-1] if char_pos > 0 else ''
                                at_char = extracted[char_pos] if char_pos < len(extracted) else ''
                                
                                # 向前看更多字符以确定上下文
                                context_before = extracted[max(0, char_pos-20):char_pos]
                                context_after = extracted[char_pos:min(len(extracted), char_pos+20)]
                                
                                logger.debug(f"错误位置字符: 前='{before_char}', 当前='{at_char}'")
                                logger.debug(f"前20字符: {context_before}")
                                logger.debug(f"后20字符: {context_after}")
                                
                                comma_needed = False
                                if before_char in ('}', ']') and at_char == '"':
                                    comma_needed = True
                                elif before_char == '"' and at_char == '"':
                                    if context_before.count('"') % 2 == 0:
                                        comma_needed = True
                                elif before_char == '}' and at_char == '{':
                                    comma_needed = True
                                elif before_char.isdigit() and at_char in ('"', '{', '['):
                                    comma_needed = True
                                elif before_char == '"' and (at_char.isalpha() or at_char == '{'):
                                    comma_needed = True
                                elif at_char in (' ', '\n', '\r', '\t'):
                                    nxt_idx = char_pos
                                    while nxt_idx < len(extracted) and extracted[nxt_idx] in (' ', '\n', '\r', '\t'):
                                        nxt_idx += 1
                                    if nxt_idx < len(extracted):
                                        nxt_ch = extracted[nxt_idx]
                                        if before_char in ('}', ']', '"', '0','1','2','3','4','5','6','7','8','9') and (nxt_ch == '"' or nxt_ch.isalpha() or nxt_ch in ('{','[')):
                                            comma_needed = True
                                
                                if comma_needed:
                                    # 尝试在这里添加逗号
                                    fixed = extracted[:char_pos] + ',' + extracted[char_pos:]
                                    logger.info("尝试在错误位置添加逗号...")
                                    try:
                                        result = json.loads(fixed)
                                        logger.info("修复成功！")
                                        return result
                                    except json.JSONDecodeError as e_retry:
                                        logger.debug(f"第一次修复失败: {e_retry}")
                                        # 尝试添加逗号和换行
                                        fixed2 = extracted[:char_pos] + ',\n        ' + extracted[char_pos:]
                                        try:
                                            result = json.loads(fixed2)
                                            logger.info("添加逗号+换行修复成功！")
                                            return result
                                        except Exception as e_retry2:
                                            logger.debug(f"第二次修复失败: {e_retry2}")
                        except Exception as e3:
                            logger.debug(f"修复尝试失败: {e3}")
                except Exception as e_fix:
                    logger.debug(f"错误位置分析失败: {e_fix}")
            
            # 最后的尝试：截断到最后一个完整的对象
            logger.info("尝试最后的修复策略：截断到最后一个完整对象...")
            try:
                # 找到最后一个 } 的位置
                last_brace = extracted.rfind('}')
                if last_brace > 0:
                    # 检查从开始到这个位置的括号是否平衡
                    truncated = extracted[:last_brace + 1]
                    open_braces = truncated.count('{')
                    close_braces = truncated.count('}')
                    
                    if open_braces == close_braces:
                        logger.info(f"尝试使用截断的JSON（截断位置: {last_brace + 1}/{len(extracted)}）")
                        result = json.loads(truncated)
                        logger.info("截断修复成功！")
                        return result
                    elif open_braces > close_braces:
                        # 缺少闭合括号，尝试添加
                        missing = open_braces - close_braces
                        fixed_truncated = truncated + ('}' * missing)
                        logger.info(f"尝试添加 {missing} 个闭合括号")
                        result = json.loads(fixed_truncated)
                        logger.info("添加闭合括号修复成功！")
                        return result
            except Exception as e_truncate:
                logger.debug(f"截断修复失败: {e_truncate}")
            
            logger.error(f"原始content长度: {len(content)}")
            logger.error(f"提取的JSON段长度: {len(extracted)}")
            # 只记录前后各500字符，避免日志太长
            logger.error(f"提取的JSON段(开头500字符): {extracted[:500]}")
            logger.error(f"提取的JSON段(结尾500字符): {extracted[-500:]}")
            
            raise ValueError(f"无法解析AI响应的JSON内容: {e2}")

def _get_provider_config() -> tuple[str, dict, str, str]:
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
        return base_url, headers, model, provider
    if provider == "kimi":
        api_key = os.getenv("KIMI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("AI service unavailable: missing KIMI_API_KEY")
        headers["Authorization"] = f"Bearer {api_key}"
        base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn").rstrip("/")
        if not model:
            model = "moonshot-v1-8k"
        return base_url, headers, model, provider
    # default minimax
    api_key = os.getenv("MINIMAX_API_KEY", "").strip()
    if not api_key:
        raise ValueError("AI service unavailable: missing MINIMAX_API_KEY")
    headers["Authorization"] = f"Bearer {api_key}"
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat").rstrip("/")
    if not model:
        model = "MiniMax-M2"
    return base_url, headers, model, provider

def _completions_url(base_url: str) -> str:
    path = os.getenv("AI_COMPLETIONS_PATH", "/v1/chat/completions").strip()
    bu = base_url.rstrip("/")
    # 如果 base_url 已包含版本号，如 /v1，则避免重复
    if bu.endswith("/v1"):
        endpoint = "/chat/completions"
    else:
        endpoint = "/v1/chat/completions" if not path else (path if path.startswith("/") else f"/{path}")
    return f"{bu}{endpoint}"

def _count_nodes(n: ConceptNode, depth: int = 0) -> int:
    """递归计算节点数，带递归深度保护"""
    if depth > MAX_RECURSION_DEPTH:
        logger.warning(f"递归深度超过限制 {MAX_RECURSION_DEPTH}，停止计数")
        return 1
    return 1 + sum(_count_nodes(c, depth + 1) for c in (n.children or []))

def _calc_depth(n: ConceptNode, current_depth: int = 0) -> int:
    """递归计算树深度，带递归深度保护"""
    if current_depth > MAX_RECURSION_DEPTH:
        logger.warning(f"递归深度超过限制 {MAX_RECURSION_DEPTH}，停止深度计算")
        return current_depth
    if not n.children:
        return 0
    return 1 + max(_calc_depth(c, current_depth + 1) for c in n.children)

def _collect_ids(n: ConceptNode, acc: set, depth: int = 0):
    """递归收集所有节点ID，带递归深度保护"""
    if depth > MAX_RECURSION_DEPTH:
        logger.warning(f"递归深度超过限制 {MAX_RECURSION_DEPTH}，停止ID收集")
        return
    acc.add(n.id)
    for c in (n.children or []):
        _collect_ids(c, acc, depth + 1)

def _ensure_unique_id(base: str, ids: set) -> str:
    """生成唯一ID，带循环次数保护"""
    bid = base
    i = 1
    attempts = 0
    while bid in ids:
        if attempts >= MAX_ID_GENERATION_ATTEMPTS:
            # 如果尝试次数过多，使用时间戳确保唯一性
            import time
            bid = f"{base}-{int(time.time() * 1000000) % 1000000}"
            logger.warning(f"ID生成尝试次数过多，使用时间戳: {bid}")
            break
        bid = f"{base}-{i}"
        i += 1
        attempts += 1
    ids.add(bid)
    return bid

 

async def generate_concept_tree(concept: str, req_max_depth: int | None = None, req_max_width: int | None = None, branch_focus_ids: list[str] | None = None, branch_min_widths: dict[str, int] | None = None, branch_priorities: dict[str, int] | None = None, refine_enabled: bool = True) -> ConceptTree:
    """
    生成概念依赖树

    Args:
        concept: 目标概念名称
        req_max_depth: 请求的最大深度
        req_max_width: 请求的最大宽度
        branch_focus_ids: 分支焦点ID列表
        branch_min_widths: 分支最小宽度字典
        branch_priorities: 分支优先级字典
        refine_enabled: 是否启用AI优化

    Returns:
        ConceptTree: 生成的概念树

    Raises:
        ValueError: 输入验证失败
    """
    # 输入验证
    name = concept.strip()
    if not name:
        raise ValueError("empty concept")
    if len(name) > MAX_CONCEPT_LENGTH:
        raise ValueError(f"concept name too long (max {MAX_CONCEPT_LENGTH} characters)")

    logger.info(f"开始生成概念树: {name}")

    base_url, headers, model_name, provider = _get_provider_config()

    # Stage 1: Initializing (对应前端第1阶段)
    _set_progress(name, 1, "Initializing CodeMonkey...", 5)

    # Stage 2: Analyzing (对应前端第2阶段)
    _set_progress(name, 2, "Analyzing concept structure...", 20)

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
    "1. 使用嵌套children表示树结构；\n"
    "2. id必须唯一且稳定，使用语义化命名；\n"
    "3. level为难度等级0-10，前置概念的level应低于或接近父节点；\n"
    "4. 每个节点的description简要说明其核心内容和学习目标；\n"
    "5. 【自适应深度】根据概念复杂度动态调整深度：\n"
    "   - 基础概念（如基本数学运算）：2-3层即可\n"
    "   - 中等概念（如数据结构）：3-5层\n"
    "   - 复杂概念（如机器学习、系统设计）：4-7层\n"
    "   - 继续细分直到达到初高中基础知识或不可再分的原子概念\n"
    "6. 【自适应广度】根据概念特性动态调整每层宽度：\n"
    "   - 分类型概念（如编程语言类型、算法分类）：需要更大广度(5-10个分支)展示所有重要类别\n"
    "   - 层次型概念（如数学定理推导）：适中广度(3-5个分支)逐步深入\n"
    "   - 线性概念（如历史发展、流程步骤）：较小广度(2-4个分支)突出主线\n"
    "7. 【完整性原则】：\n"
    "   - 当某个节点代表一个类别或集合时，其子节点应该完整列举该类别的主要成员\n"
    "   - 例如：'排序算法'节点应包含所有主流排序算法作为独立子节点\n"
    "   - 例如：'数据类型'节点应包含所有基本数据类型\n"
    "8. 【独立性原则】：每个重要概念、方法、算法都应作为独立节点，不要合并\n"
    "9. 严格输出JSON对象，不要输出额外解释。\n"
    )

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是严谨的知识图谱构建专家。你必须直接输出纯JSON格式的树数据，不要使用markdown代码块，不要添加任何解释性文字。"},
            {"role": "user", "content": f"目标概念：{name}\n期望深度≥4，直到基础概念（初高中知识）为止；每层建议3-6个分支；最大深度={req_max_depth or os.getenv('TREE_MAX_DEPTH', '8')}，最大宽度={req_max_width or os.getenv('TREE_MAX_WIDTH', '8')}。\n{prompt}\n\n重要：你必须直接输出JSON，不要在<think>标签内输出，不要用代码块包裹，直接以{{开头输出JSON对象。"},
        ],
        "temperature": 0.5,  # 进一步降低温度以获得更确定的输出
        "max_tokens": 8192,
    }

    payload["response_format"] = {"type": "json_object"}

    logger.info(f"发送AI请求 - Provider: {provider}, Model: {model_name}, Concept: {name}")


    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=15.0, read=180.0, write=60.0, pool=10.0)) as client:
        try:
            resp = await client.post(_completions_url(base_url), headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            # 详细日志：记录响应结构
            logger.info(f"AI响应成功 - Status: {resp.status_code}, Concept: {name}")
            logger.debug(f"AI响应数据结构: choices数量={len(data.get('choices', []))}")

            # 检查响应是否有内容
            if not data.get("choices") or len(data.get("choices", [])) == 0:
                logger.error(f"AI响应中没有choices字段或为空: {data}")
                raise ValueError("AI response missing choices")

            msg = data["choices"][0].get("message", {})
            content = msg.get("content", "")
            logger.debug(f"AI返回内容长度: {len(content)} 字符")
            logger.debug(f"AI返回内容前500字符: {content[:500]}")

        except httpx.TimeoutException as e:
            error_msg = f"AI API请求超时: {type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.error(f"请求URL: {_completions_url(base_url)}")
            logger.error(f"Provider: {provider}, Model: {model_name}")
            logger.error(f"超时配置: connect=15s, read=180s")
            raise ValueError(f"AI请求超时，请检查网络连接和API配置。如果使用MiniMax，请确认API key有效且账户有足够额度。错误详情: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"AI API返回错误状态码 {e.response.status_code}")
            logger.error(f"错误响应内容: {e.response.text[:500]}")
            logger.error(f"请求URL: {_completions_url(base_url)}")
            raise ValueError(f"AI API返回错误 (状态码 {e.response.status_code}): {e.response.text[:200]}")
        except httpx.RequestError as e:
            error_msg = f"AI API请求失败: {type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.error(f"请求URL: {_completions_url(base_url)}")
            raise ValueError(f"AI请求失败: {str(e)}")
        except ValueError as e:
            logger.error(f"响应JSON解析失败: {e}")
            raise

    # Stage 3: Building dependency tree (对应前端第3阶段)
    _set_progress(name, 3, "Building dependency tree...", 50)

    msg = data.get("choices", [{}])[0].get("message", {})
    logger.debug(f"开始解析AI消息，message keys: {list(msg.keys())}")

    try:
        parsed = _parse_message_json(msg)
        logger.info(f"AI消息解析成功，parsed keys: {list(parsed.keys()) if isinstance(parsed, dict) else type(parsed)}")
    except Exception as e:
        logger.error(f"AI消息解析失败: {type(e).__name__}: {e}")
        logger.error(f"原始message内容: {str(msg)[:500]}")
        # 尝试使用AI进行一次JSON修复
        try:
            repair_payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "你是JSON修复器。你必须只返回严格的JSON对象，不允许任何解释或标记。"},
                    {"role": "user", "content": f"请将下面的内容修复为严格的JSON对象，并只返回JSON：\n\n{msg.get('content','')}"},
                ],
                "temperature": 0,
                "max_tokens": 4096,
                "response_format": {"type": "json_object"},
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=15.0, read=60.0, write=30.0, pool=10.0)) as client:
                resp2 = await client.post(_completions_url(base_url), headers=headers, json=repair_payload)
                resp2.raise_for_status()
                data2 = resp2.json()
                msg2 = data2.get("choices", [{}])[0].get("message", {})
                parsed = _parse_message_json(msg2)
                logger.info("使用AI修复JSON成功")
        except Exception as e2:
            raise ValueError(f"无法解析AI返回的消息: {str(e)}")

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
    logger.debug(f"第一次ensure_root结果: {type(root_obj)}, is_dict={isinstance(root_obj, dict)}")

    if not isinstance(root_obj, dict):
        logger.warning("第一次ensure_root未找到有效根节点，尝试从content提取")
        content_raw = msg.get("content") or ""
        logger.debug(f"content_raw长度: {len(content_raw)}")
        try:
            parsed2 = json.loads(_extract_json_segment_with_key(content_raw, "root"))
            root_obj = ensure_root(parsed2)
            logger.info(f"从content提取成功: {type(root_obj)}")
        except Exception as e:
            logger.error(f"从content提取失败: {type(e).__name__}: {e}")

    if not isinstance(root_obj, dict):
        # 所有提取方法都失败了，抛出错误而不是返回空树
        error_msg = f"无法从AI响应中提取有效的概念树结构。parsed类型: {type(parsed)}, parsed内容: {str(parsed)[:200]}"
        logger.error(error_msg)
        logger.error(f"完整parsed内容: {parsed}")
        raise ValueError(error_msg)
    
    logger.info(f"成功提取root节点，children数量: {len(root_obj.get('children', []))}")

    # 强制限制深度和宽度在安全范围内
    max_depth = min(int(req_max_depth or os.getenv("TREE_MAX_DEPTH", "8")), MAX_TREE_DEPTH)
    max_width = int(req_max_width or os.getenv("TREE_MAX_WIDTH", "8"))

    logger.info(f"树生成限制 - 最大深度: {max_depth}, 最大宽度: {max_width}")

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

    def normalize_node(obj, depth, parent_id, seen_ids, node_count_ref=None):
        """
        规范化节点，带深度和节点数限制

        Args:
            obj: 原始节点对象
            depth: 当前深度
            parent_id: 父节点ID
            seen_ids: 已见ID集合
            node_count_ref: 节点计数引用（字典）
        """
        # 深度保护：超过最大深度则不再创建子节点
        if depth >= MAX_TREE_DEPTH:
            logger.warning(f"达到最大树深度 {MAX_TREE_DEPTH}，停止扩展")
            if not isinstance(obj, dict):
                obj = {"id": str(obj), "name": str(obj), "description": str(obj), "level": 0, "children": []}
            # 返回叶子节点
            node_id = _ensure_unique_id(str(obj.get("id", "node")), seen_ids)
            return ConceptNode(
                id=node_id,
                name=str(obj.get("name", node_id)),
                description=str(obj.get("description", obj.get("name", node_id))),
                level=_clamp_level(obj.get("level", 0)),
                children=[],
                parent=parent_id,
            )

        # 节点数保护
        if node_count_ref is not None:
            if node_count_ref.get('count', 0) >= MAX_TREE_NODES:
                logger.warning(f"达到最大节点数 {MAX_TREE_NODES}，停止扩展")
                if not isinstance(obj, dict):
                    obj = {"id": str(obj), "name": str(obj), "description": str(obj), "level": 0, "children": []}
                node_id = _ensure_unique_id(str(obj.get("id", "node")), seen_ids)
                return ConceptNode(
                    id=node_id,
                    name=str(obj.get("name", node_id)),
                    description=str(obj.get("description", obj.get("name", node_id))),
                    level=_clamp_level(obj.get("level", 0)),
                    children=[],
                    parent=parent_id,
                )
            node_count_ref['count'] = node_count_ref.get('count', 0) + 1

        if not isinstance(obj, dict):
            obj = {"id": str(obj), "name": str(obj), "description": str(obj), "level": 0, "children": []}
        raw_id = str(obj.get("id")) if obj.get("id") is not None else None
        node_id = _ensure_unique_id(raw_id or "node", seen_ids)
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
            # 检查节点数限制
            if node_count_ref and node_count_ref.get('count', 0) >= MAX_TREE_NODES:
                logger.warning(f"子节点处理时达到最大节点数限制，停止添加子节点")
                break
            cid = str(c.get("id")) if isinstance(c, dict) and c.get("id") is not None else None
            if cid and cid in seen_ids:
                continue
            children_fix.append(normalize_node(c, depth + 1, node_id, seen_ids, node_count_ref))

        node = ConceptNode(
            id=node_id,
            name=name,
            description=str(desc),
            level=level,
            children=children_fix,
            parent=parent_id,
        )
        return node

    # 使用节点计数器防止树无限扩展
    node_count_ref = {'count': 0}
    root = normalize_node(root_obj, 0, None, set(), node_count_ref)
    logger.info(f"初始树生成完成，节点数: {node_count_ref['count']}, 深度: {_calc_depth(root)}")

    def _index_nodes_by_id(n: ConceptNode, acc: dict[str, ConceptNode]):
        acc[n.id] = n
        for c in (n.children or []):
            _index_nodes_by_id(c, acc)

    def _node_depths(n: ConceptNode, depth: int, acc: dict[str, int]):
        acc[n.id] = depth
        for c in (n.children or []):
            _node_depths(c, depth + 1, acc)

    def _merge_expansions(cur_root: ConceptNode, expansions: list, max_width_cap: int, current_node_count: int) -> ConceptNode:
        """
        合并AI建议的扩展到当前树

        Args:
            cur_root: 当前根节点
            expansions: 扩展列表
            max_width_cap: 最大宽度限制
            current_node_count: 当前节点总数
        """
        # 检查当前节点数是否已经接近限制
        if current_node_count >= MAX_TREE_NODES * 0.9:
            logger.warning(f"当前节点数 {current_node_count} 接近最大限制，跳过扩展")
            return cur_root

        id_map: dict[str, ConceptNode] = {}
        _index_nodes_by_id(cur_root, id_map)
        depths: dict[str, int] = {}
        _node_depths(cur_root, 0, depths)
        seen_ids: set[str] = set()
        _collect_ids(cur_root, seen_ids)

        node_count_ref = {'count': current_node_count}
        total_added = 0

        for exp in (expansions or []):
            if not isinstance(exp, dict):
                continue
            parent_id = str(exp.get("parentId")) if exp.get("parentId") is not None else None
            if not parent_id or parent_id not in id_map:
                continue
            parent = id_map[parent_id]

            # 检查父节点深度
            parent_depth = depths.get(parent_id, 0)
            if parent_depth >= MAX_TREE_DEPTH - 1:
                logger.warning(f"父节点 {parent_id} 深度 {parent_depth} 接近最大限制，跳过扩展")
                continue

            # 使用AI建议的宽度，但不超过全局最大值
            recommended_width = exp.get("recommendedWidth")
            if recommended_width is not None:
                try:
                    # 允许AI根据节点特性推荐不同的宽度
                    target_width = max(1, min(int(recommended_width), max_width_cap))
                except Exception:
                    target_width = max_width_cap
            else:
                # 如果没有推荐值，使用默认策略
                current_children = len(parent.children or [])
                if current_children < 3:
                    target_width = 5  # 子节点较少时允许更多扩展
                else:
                    target_width = max_width_cap

            children = exp.get("children") or []
            added_count = 0
            for child in children:
                # 检查全局节点数限制
                if node_count_ref['count'] >= MAX_TREE_NODES:
                    logger.warning(f"达到最大节点数限制 {MAX_TREE_NODES}，停止扩展")
                    return cur_root

                # 使用推荐宽度作为软限制，允许适度超出以保证完整性
                if len(parent.children or []) >= target_width and added_count > 0:
                    # 如果已经添加了至少一个节点且达到推荐宽度，可以停止
                    # 但如果是第一个节点，即使超出宽度也要添加（保证至少有扩展）
                    break
                norm = normalize_node(child, depths.get(parent_id, 0) + 1, parent_id, seen_ids, node_count_ref)
                if any((ch.id == norm.id) for ch in (parent.children or [])):
                    continue
                if parent.children is None:
                    parent.children = []
                parent.children.append(norm)
                added_count += 1
                total_added += 1

        logger.info(f"扩展完成，添加了 {total_added} 个新节点")
        return cur_root

    async def _refine_with_ai(cur_root: ConceptNode) -> ConceptNode:
        base_url2, headers2, model2, provider2 = _get_provider_config()

        # 增强的细化prompt
        refine_prompt = f"""目标概念：{name}
    全局最大深度：{max_depth}；全局最大宽度：{max_width}

    当前树结构：
    {json.dumps({'root': cur_root.model_dump()}, ensure_ascii=False)}

    请执行以下分析和优化：

    1. 【完整性检查】
    - 识别每个"类别型"节点（如XX算法、XX方法、XX类型等）
    - 检查这些节点是否包含了该类别的所有重要成员
    - 如果缺失重要成员，在expansions中补充

    2. 【深度自适应】
    - 评估每个分支的概念复杂度
    - 简单概念分支无需强制深化
    - 复杂概念分支应继续细分至基础知识
    - 不同分支可以有不同深度

    3. 【广度自适应】
    - 识别需要并列展示多个要素的节点（如技术栈、工具集、方法论）
    - 这些节点应有更大广度(recommendedWidth: 6-10)
    - 线性递进的节点保持较小广度(recommendedWidth: 2-4)

    4. 【知识密度优化】
    - 避免过于宽泛的节点（如"基础知识"、"高级内容"）
    - 每个节点应代表具体的、可学习的知识点
    - 如发现模糊节点，将其细化为具体概念

    5. 【学习路径优化】
    - 确保前置知识出现在依赖它的知识之前
    - 调整节点的level值以反映真实难度梯度

    返回格式：
    {{
    "expansions": [
        {{
        "parentId": "需要扩展的父节点ID",
        "recommendedWidth": 该节点建议的子节点数量（根据概念特性自适应）,
        "rationale": "扩展理由（如：该类别缺少重要成员XX）",
        "children": [
            {{
            "id": "新节点ID",
            "name": "具体概念名称",
            "description": "概念说明",
            "level": 难度等级,
            "children": []
            }}
        ]
        }}
    ],
    "analysis": {{
        "currentDepth": 当前实际深度,
        "currentTotalNodes": 当前节点总数,
        "coverageScore": 知识覆盖度评分(0-100),
        "suggestions": ["改进建议1", "改进建议2"]
    }}
    }}

    注意事项：
    - 不要替换已有节点，只在expansions中添加缺失的内容
    - recommendedWidth是建议值，根据节点特性动态调整
    - 优先扩展知识覆盖不完整的分支
    - 保持整体结构的平衡性，但允许不同分支有不同的深度和广度"""

        payload = {
            "model": model2,
            "messages": [
                {"role": "system", "content": "你是知识图谱优化专家。分析现有知识树的完整性和结构合理性，通过智能扩展补充缺失的重要知识点。"},
                {"role": "user", "content": refine_prompt}
            ],
            "temperature": 0.8,  # 适中的温度保证创造性和稳定性的平衡
            "max_tokens": 8192,
            "response_format": {"type": "json_object"},
        }
        if provider2 not in ("openai", "minimax-openai"):
            payload.pop("tool_choice", None)
            payload.pop("tools", None)
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=15.0, read=180.0, write=60.0, pool=10.0)) as client:
                resp = await client.post(_completions_url(base_url2), headers=headers2, json=payload)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception as e:
                    logger.error(f"AI优化响应JSON解析失败: {e}")
                    data = {"choices": [{"message": {"content": json.dumps({"expansions": []}, ensure_ascii=False)}}]}
        except httpx.HTTPStatusError as e:
            logger.error(f"AI优化API返回错误状态码 {e.response.status_code}: {e}")
            return cur_root
        except httpx.RequestError as e:
            logger.error(f"AI优化API请求失败: {e}")
            return cur_root
        msg = data.get("choices", [{}])[0].get("message", {})
        try:
            proposal = _parse_message_json(msg)
        except Exception as e:
            logger.error(f"解析AI优化建议失败: {e}")
            return cur_root
        expansions = proposal.get("expansions") if isinstance(proposal, dict) else []
        if not expansions:
            root_obj2 = proposal.get("root") if isinstance(proposal, dict) else None
            if isinstance(root_obj2, dict):
                node_count_ref2 = {'count': 0}
                new_root = normalize_node(root_obj2, 0, None, set(), node_count_ref2)
                new_count = _count_nodes(new_root)
                cur_count = _count_nodes(cur_root)
                if new_count > cur_count or _calc_depth(new_root) > _calc_depth(cur_root):
                    logger.info(f"使用AI完全重构的树，节点数: {new_count}")
                    return new_root
            logger.info("AI没有建议扩展，保持当前树")
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

        current_node_count = _count_nodes(cur_root)
        merged_root = _merge_expansions(cur_root, expansions, max_width, current_node_count)
        new_node_count = _count_nodes(merged_root)
        new_depth = _calc_depth(merged_root)

        if new_node_count <= current_node_count and new_depth <= _calc_depth(cur_root):
            logger.info("扩展后树未增长，保持原树")
            return cur_root

        logger.info(f"树优化成功，节点数: {current_node_count} -> {new_node_count}, 深度: {_calc_depth(cur_root)} -> {new_depth}")
        return merged_root

    rounds = 0
    max_refine_rounds = 3  # 最大优化轮数

    if refine_enabled:
        logger.info(f"开始AI优化迭代，最多 {max_refine_rounds} 轮")
        # Stage 4: Optimizing learning path (对应前端第4阶段)
        _set_progress(name, 4, "Optimizing learning path...", 60)

    try:
        while refine_enabled and rounds < max_refine_rounds:
            prev_node_count = _count_nodes(root)
            prev_depth = _calc_depth(root)

            # 安全检查：如果已经达到节点数限制的80%，停止优化
            if prev_node_count >= MAX_TREE_NODES * 0.8:
                logger.warning(f"节点数 {prev_node_count} 已达到限制的80%，停止优化")
                break

            logger.info(f"开始第 {rounds + 1} 轮优化，当前节点数: {prev_node_count}, 深度: {prev_depth}")
            new_root = await _refine_with_ai(root)
            new_node_count = _count_nodes(new_root)
            new_depth = _calc_depth(new_root)

            # 如果节点数没有明显增加（增加少于5%），说明已经足够完善
            if new_node_count <= prev_node_count * 1.05:
                logger.info(f"节点数增长不足5%，优化收敛，停止迭代")
                break

            root = new_root
            rounds += 1

            # 更新优化进度：保持在stage 4，但更新百分比和消息
            # 第1轮: 65%, 第2轮: 75%, 第3轮: 85%
            progress_percent = 60 + (rounds * 10)
            _set_progress(name, 4, f"Optimizing round {rounds}/{max_refine_rounds}...", min(progress_percent, 90))

        if refine_enabled:
            logger.info(f"AI优化完成，共 {rounds} 轮，最终节点数: {_count_nodes(root)}, 深度: {_calc_depth(root)}")

    except Exception as e:
        logger.error(f"优化过程出错: {e}", exc_info=True)
        _set_progress(name, 4, f"Optimization skipped (error: {str(e)})", 75)

    # 计算最终统计信息
    final_node_count = _count_nodes(root)
    final_depth = _calc_depth(root)

    logger.info(f"概念树生成完成 - 概念: {name}, 节点数: {final_node_count}, 深度: {final_depth}")

    # Stage 5: Ready to learn! (对应前端第5阶段)
    _set_progress(name, 5, "Ready to learn!", 100)

    tree = ConceptTree(
        target=name,
        root=root,
        total_nodes=final_node_count,
        max_depth=final_depth,
        stats=TreeStats(),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    return tree
