"""
super_thinking + VCP V7.1 协议块 胶水层 (V 6/15 P1-7 升级)

解决问题: vcp_perspective 输出 V7.1 协议块 (<<<[TOOL_REQUEST]>>>...<<<[END_TOOL_REQUEST]>>>)
是文本, 不会被 VCP 真接. 本模块:
  1. parse 协议块成结构化 (tool_name, query, tagmemo_tags, metathinking_type, magi_verdict, protocol_version, confidence)
  2. 用 /v1/chat/completions 真发到 VCPToolBox 触发 plugin 调
  3. 支持 Bearer token (VCP 全局 auth)

V7.1 协议格式 (从 vcp_perspective 输出实测):
<<<[TOOL_REQUEST]>>>
tool_name:「始」X「末」,
query:「始」Y「末」,
tagmemo_tags:「始」Z「末」,
metathinking_type:「始」W「末」,
magi_verdict:「始」...「末」,
protocol_version:「始」V7.1「末」,
confidence:「始」0.82「末」
<<<[END_TOOL_REQUEST]>>>
"""
import re
import json
import urllib.request
import urllib.error
from typing import Optional


PROTOCOL_VERSION = "V7.1"

# 「始」...「末」 字段提取
KV_PATTERN = re.compile(r"(\w+):「始」([^「]*)「末」")
# 协议块边界
BLOCK_PATTERN = re.compile(r"<<<\[TOOL_REQUEST\]>>>(.*?)<<<\[END_TOOL_REQUEST\]>>>", re.DOTALL)


def parse_v7_blocks(text: str) -> list[dict]:
    """从 vcp_perspective 输出 parse 所有 V7.1 TOOL_REQUEST 块

    Returns:
      list[dict]: 每个块一个 dict, 字段: tool_name, query, tagmemo_tags,
                  metathinking_type, magi_verdict, protocol_version, confidence
    """
    results = []
    for match in BLOCK_PATTERN.finditer(text):
        block = match.group(1)
        d = {}
        for kv in KV_PATTERN.finditer(block):
            d[kv.group(1)] = kv.group(2).strip()
        # 数值字段
        if "confidence" in d:
            try:
                d["confidence"] = float(d["confidence"])
            except ValueError:
                pass
        d["_raw"] = block.strip()
        d["_protocol"] = d.get("protocol_version", PROTOCOL_VERSION)
        results.append(d)
    return results


def call_vcp_chat(
    messages: list[dict],
    vcp_url: str = "http://127.0.0.1:6005",
    bearer_token: Optional[str] = None,
    model: str = "llama3.2:1b",
    timeout: float = 15.0,
    max_tokens: int = 50,
) -> dict:
    """真发 chat 请求到 VCPToolBox /v1/chat/completions

    Args:
      messages: OpenAI 风格 [{"role":..., "content":...}, ...]
      vcp_url: VCPToolBox base URL
      bearer_token: 6005 的 Bearer token (从 VCP_CONFIG_TOKEN 读)
      model: 模型名 (默认 llama3.2:1b — 1.3GB 响应快, 适合 ql 路由)
      timeout: 超时秒数
      max_tokens: 限制输出长度 (V 6/15 21:30 发现: 不加 max_tokens 时 VCP 内部转 ollama
                会持续到 context 满, 30s+ timeout. max_tokens=50 是甜点)
    """
    if not bearer_token:
        import os
        bearer_token = os.environ.get("VCP_BEARER_TOKEN", "vcp_local_2026")
    url = f"{vcp_url}/v1/chat/completions"
    payload = {"model": model, "messages": messages, "stream": False, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers=headers, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read().decode("utf-8", errors="ignore")[:500]}
    except Exception as e:
        return {"status": 0, "error": f"{type(e).__name__}: {e}"}


def execute_v7_block(
    block: dict,
    vcp_url: str = "http://127.0.0.1:6005",
    bearer_token: Optional[str] = None,
    model: str = "deepseek",
) -> dict:
    """执行一个 V7.1 块: 用 tool_name/query 构造 messages 发到 VCP

    Returns:
      dict: {status, tool_name, query, response, error?}
    """
    tool_name = block.get("tool_name", "")
    query = block.get("query", "")
    if not query:
        return {"status": 0, "error": "empty query", "block": block}
    # 构造 messages: 用 system 提示 tool_name, user 给 query
    messages = [
        {"role": "system", "content": f"Use VCP tool: {tool_name}"},
        {"role": "user", "content": query},
    ]
    resp = call_vcp_chat(messages, vcp_url=vcp_url, bearer_token=bearer_token, model=model)
    return {
        "status": resp.get("status", 0),
        "tool_name": tool_name,
        "query": query[:100],
        "confidence": block.get("confidence"),
        "protocol": block.get("_protocol", PROTOCOL_VERSION),
        "response": resp,
    }


def demo():
    """P1-7 端到端 demo: parse vcp_perspective 输出, 真发 VCPToolBox"""
    import sys
    sys.path.insert(0, "/home/fuguang/Agent-superthinking/src")
    from super_thinking.core.jury import Jury

    j = Jury()
    print("=== 1) 触发 vcp_perspective 输出 V7.1 协议块 ===")
    r = j.think("vcp_perspective 测试: 帮我查一下今天日期", {})

    vcp_output = ""
    for pid, out in r.outputs.items():
        if pid == "vcp_perspective":
            vcp_output = out.analysis
            break

    print(f"  vcp_perspective 输出: {len(vcp_output)} chars")
    print(f"  含 TOOL_REQUEST 块: {bool(BLOCK_PATTERN.search(vcp_output))}")

    print()
    print("=== 2) Parse V7.1 协议块 ===")
    blocks = parse_v7_blocks(vcp_output)
    print(f"  解析到 {len(blocks)} 个 V7.1 块:")
    for i, b in enumerate(blocks):
        print(f"    块 {i}: tool={b.get('tool_name', '?')[:30]} conf={b.get('confidence')} proto={b.get('_protocol')}")

    if not blocks:
        print("  ⚠️ 没解析到块, 检查协议格式")
        return

    print()
    print("=== 3) 真发到 VCPToolBox 6005 ===")
    b = blocks[0]
    result = execute_v7_block(b, vcp_url="http://127.0.0.1:6005", model="deepseek")
    print(f"  status: {result['status']}")
    print(f"  tool_name: {result['tool_name']}")
    print(f"  query preview: {result['query']}")
    if result['status'] == 200:
        print(f"  ✅ VCP 真接了, response 前 200 chars: {str(result['response'].get('body', ''))[:200]}")
    else:
        print(f"  ⚠️ VCP 返错: {result['response'].get('error', '')[:200]}")


if __name__ == "__main__":
    demo()
