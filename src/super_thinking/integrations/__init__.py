"""
super_thinking integrations — V 6/15

对外集成的胶水层集合:
  - agentmemory_adapter: JuryWithMemory (tagmemo/msa 注入 context['memory'])
  - vcp_v7_client: VCP V7.1 协议块 parse + 真发 /v1/chat/completions

设计原则: 不修改 super_thinking 核心包, 在 integrations/ 下加胶水层, 向后兼容.
"""
