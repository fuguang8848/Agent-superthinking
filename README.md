# Super Thinking - 多视角专家团思考系统

> ⚔️ 楚灵出品

一个模拟专家团协作的多维度思考框架。通过并行调用多个专业视角分析问题，自动检测冲突、提炼共识，并生成结构化的综合报告。

**核心理念**：不同领域的思想家看待同一个问题，结论往往不同——这种差异本身就是洞察的来源。

---

## 🎭 18个视角速览

| 视角 | 名称 | 一句话定位 |
|------|------|-----------|
| `magi_debate` | Magi三贤者 | 三方辩论（理性/感性/平衡），重大决策必用 |
| `mao_perspective` | 毛选视角 | 辩证法、矛盾论、实践论、群众路线 |
| `meta_thinking` | 元思考 | 递归反思、五思维簇、思维链自我检查 |
| `msa_perspective` | MSA检索 | 双重路由+记忆交错，L1-L4分层检索 |
| `nuwa_meta` | 女娲元视角 | 动态生成新视角，按需扩展视角库 |
| `tagmemo_perspective` | TagMemo RAG | 浪潮四阶段RAG，语义引力检索 |
| `vcp_perspective` | VCP系统 | TagMemo+元思考+Magi三方整合输出 |
| `verification` | 证伪核查 | 证据优先，声称前必须验证 |
| `elon_perspective` | 马斯克视角 | 第一性原理、渐近极限、垂直整合 |
| `jobs_perspective` | 乔布斯视角 | 聚焦即说不、端到端控制、现实扭曲力场 |
| `zhangxuefeng_perspective` | 张雪峰视角 | 社会筛子论、就业倒推法、阶层现实主义 |
| `naval_perspective` | 纳瓦尔视角 | 杠杆思维、特定知识、幸福算法 |
| `xmentor_perspective` | X导师视角 | Hook公式、1/3/1节奏、4A选题矩阵 |
| `darwin_perspective` | 达尔文视角 | 自主进化、8维Rubric评估、棘轮机制 |
| `risk_detail` | 塔勒布视角 | 非对称风险、反脆弱、黑天鹅、Skin in the Game |
| `doubt` | 费曼视角 | 证伪精神、反自欺、具象化、货物崇拜检测 |
| `stakeholder` | 芒格视角 | 激励诊断、多元思维、逆向、Lollapalooza效应 |
| `past_experience` | 达尔文经验视角 | 进化机制、模式识别、锚定效应、历史类比 |

---

## 🎭 视角详解

### 🔮 分析型视角

#### `magi_debate` - Magi三贤者辩论
**来源**：原创 | **蒸馏对象**：无
**核心心智模型**：
- MELCHIOR（梅尔基奥）：绝对理性，数据驱动，概率计算
- BALTHAZAR（巴尔塔萨）：感性直觉，关注人性、情感、文化因素
- CASPAR（卡斯帕）：综合平衡，识别两者局限，寻求中道

**触发词**：决策、权衡、利弊、三方、分析、理性感性
**适用场景**：重大决策、战略选择、多方利益平衡

---

#### `mao_perspective` - 毛选视角
**来源**：毛泽东思想 | **蒸馏对象**：《毛泽东选集》
**核心心智模型**：
- 矛盾分析法：主要矛盾 vs 次要矛盾，矛盾的主要方面
- 实践论：认识从实践中来，到实践中去
- 持久战：敌强我弱时的战略阶段划分
- 农村包围城市：迂回包抄，边缘突破
- 统一战线：分清敌友，团结一切可团结的力量
- 群众路线：从群众中来，到群众中去

**触发词**：矛盾、实践、斗争、战略、群众、辩证、统一战线
**适用场景**：组织问题、战略分析、政治判断

---

#### `meta_thinking` - 元思考
**来源**：认知科学 | **蒸馏对象**：元认知理论
**核心心智模型**：
- 前思维簇：问题感知、分类、优先级判断
- 逻辑推理簇：演绎/归纳、因果分析、结构化推理
- 反思簇：自我监控、逻辑漏洞检查、预设验证
- 创意簇：发散思维、类比联想、可能性扩展
- 决策簇：权衡方案、风险评估、行动选择

**触发词**：思考、推理、思维、反思、分析过程、深度思考
**适用场景**：复杂问题拆解、推理过程检验、决策前的自我审查

---

#### `msa_perspective` - MSA检索
**来源**：MSA (EverMind) | **蒸馏对象**：MSA架构论文
**核心心智模型**：
- 双重路由检索：主题级粗筛 + 词元级精筛
- 记忆交错：最多3轮迭代检索
- 分层存储：L1缓存/L2图谱/L3向量库/L4文件

**触发词**：记忆、检索、上下文、历史、相关、记得
**适用场景**：需要调用历史记忆的综合性分析

---

#### `nuwa_meta` - 女娲元视角
**来源**：原创 | **蒸馏对象**：女娲造人术 (alchaincyf/nuwa-skill)
**核心心智模型**：
- 需求诊断：评估现有视角覆盖率
- 视角生成：根据问题类型动态生成新视角
- 元视角推荐：推荐最适合的已有视角组合

**触发词**：生成视角、新视角、视角不够、扩展
**适用场景**：现有视角无法覆盖的全新领域问题

---

#### `tagmemo_perspective` - TagMemo RAG
**来源**：VCPToolBox | **蒸馏对象**：TagMemo算法
**核心心智模型**：
- 感应阶段：净化+EPA分析，提取关键实体
- 分段阶段：语义断层检测，识别话题边界
- 扩张阶段：标签生成+关联扩展
- 重塑阶段：向量融合+霰弹枪检索

**触发词**：检索、语义、关联、记忆、TagMemo、浪潮
**适用场景**：需要精确语义检索的深度分析

---

#### `vcp_perspective` - VCP系统集成
**来源**：VCPToolBox | **蒸馏对象**：VCP系统
**核心心智模型**：
- TagMemo浪潮RAG检索
- 元思考递归推理
- Magi三贤者辩论
- VCP协议格式输出

**触发词**：综合、分析、整合、系统性思考
**适用场景**：复杂系统性问题，需要多维度综合分析

---

#### `verification` - 证伪核查
**来源**：原创 | **蒸馏对象**：证伪思维
**核心心智模型**：
- 证据优先原则：声称完成前必须运行验证
- 反面证据搜索：主动寻找可能推翻结论的证据
- 边界条件检验：在极端情况下测试结论是否仍然成立

**触发词**：验证、确认、证明、核查、证伪、完成
**适用场景**：任何需要确认结论可靠性的分析

---

### 💡 人物视角（蒸馏自真实思想家）

#### `elon_perspective` - 马斯克视角
**来源**：alchaincyf/elon-musk-skill | **人物**：Elon Musk
**核心心智模型**：
- 第一性原理：拆解到物理层面，从零开始重新推理
- 渐近极限分析：算理论极限，再分析差距
- 五步算法：提问→排除假设→基础前提→矛盾点→异常
- 垂直整合：控制全链条，不依赖供应商
- 竞争壁垒识别：技术护城河 vs 规模护城河

**触发词**：马斯克、第一性原理、成本拆解、垂直整合、白痴指数、渐近极限

---

#### `jobs_perspective` - 乔布斯视角
**来源**：alchaincyf/steve-jobs-skill | **人物**：Steve Jobs
**核心心智模型**：
- 聚焦即说不：知道不做什么和知道做什么一样重要
- 端到端控制：从体验到供应链全控制
- 连点成线：回头看才能看到机会
- 死亡过滤器：问「这个决定会导致死亡吗？」否就继续
- 现实扭曲力场：打破不可能的信念
- 技术与人文交汇：技术+人文=让人惊喜的产品

**触发词**：乔布斯、聚焦、产品体验、极简、完美主义、端到端

---

#### `zhangxuefeng_perspective` - 张雪峰视角
**来源**：alchaincyf/zhangxuefeng-skill | **人物**：张雪峰
**核心心智模型**：
- 社会筛子论：教育是社会分层的工具，不是阶级跃迁的阶梯
- 选择大于努力：方向错了一切白费
- 就业倒推法：从最终就业目标倒推志愿选择
- 阶层现实主义：认清自己所处的阶层位置
- 争议即传播：有争议的观点往往是传播力最强的

**触发词**：张雪峰、教育、高考、就业、阶层、选择、寒门

---

#### `naval_perspective` - 纳瓦尔视角
**来源**：alchaincyf/naval-skill | **人物**：Naval Ravikant
**核心心智模型**：
- 杠杆思维：代码/资本/媒体三种杠杆
- 特定知识：无法被教授的知识，是真正的护城河
- 欲望即合同：降低欲望是幸福的路径
- 重新定义术：重新定义问题比解决问题更重要
- 痛苦系统化重构：把痛苦当数据而非情绪处理

**触发词**：纳瓦尔、财富、幸福、杠杆、知识、财富观、幸福算法

---

#### `xmentor_perspective` - X导师视角
**来源**：alchaincyf/x-mentor-skill | **人物**：X/Twitter顶级创作者
**核心心智模型**：
- Hook公式：触发→行动→多变量酬赏→投入
- 1/3/1节奏：1个hook+3个要点+1个call to action
- 四段Thread结构：hook/背书/内容/CTA
- 4A选题矩阵：情感/行动/争议/即时性
- 增长阶段策略：启动期→加速期→维持期→重启期

**触发词**：X、Twitter、内容创作、传播、选题、钩子、增长

---

#### `darwin_perspective` - 达尔文视角
**来源**：alchaincyf/darwin-skill | **人物**：Darwin + Karpathy autoresearch
**核心心智模型**：
- 8维Rubric评估：结构60分+效果40分
- 自主优化循环：评估→改进→实测→回滚
- 棘轮机制：只保留改进，自动回滚退步
- 双重评估：结构评分+效果验证

**触发词**：达尔文、优化、进化、评估、测试、迭代

---

### 🔍 蒸馏视角（从真实思想家蒸馏）

#### `risk_detail` - 塔勒布视角
**来源**：alchaincyf/taleb-skill | **人物**：Nassim Nicholas Taleb
**核心心智模型**：
- **非对称风险思维**：永远先看下行风险代价，不问期望值
- **反脆弱偏好**：从混乱中获益，而非抵抗混乱
- **Skin in the Game检验**：没下注的观点可信度打五折
- **林迪效应**：存在越久越可能继续存在
- **Via Negativa减法**：去掉有害的 > 增加更多的
- **领域特异性**：能力和理性都是领域特定的

**触发词**：黑天鹅、尾部风险、反脆弱、skin in the game、杠铃策略、不确定、风险评估、脆弱性、林迪

**输出特色**：风险矩阵、缓解策略、黑天鹅识别、非对称性分析

---

#### `doubt` - 费曼视角
**来源**：alchaincyf/feynman-skill | **人物**：Richard Feynman
**核心心智模型**：
- **命名≠理解**：知道叫什么和真正懂是两回事
- **反自欺原则**：你最容易骗自己
- **不确定性是力量**：承认不知道比假装确定更有力量
- **货物崇拜检测**：空有形式缺内核——飞机不会降落
- **具象化思考**：用具体、可感知的类比替代抽象概念
- **深度游戏**：跟着好奇心走，不预设「有用」或「没用」

**触发词**：怀疑、质疑、怎么证明、什么意思、懂了吗、简化、证据、货物崇拜、自欺、抽象

**输出特色**：列出疑点、证伪检验、货物崇拜识别、具象化建议

---

#### `stakeholder` - 芒格视角
**来源**：alchaincyf/munger-skill | **人物**：Charlie Munger
**核心心智模型**：
- **多元思维模型**：至少3个学科视角——心理学/经济学/博弈论
- **逆向思考**：不问怎么赢，问怎么不输
- **Lollapalooza效应**：多种偏误同时强化时的极端结果
- **激励机制决定一切**：理解任何人的行为先看激励结构
- **葡萄干与粪便法则**：一个致命缺陷污染整体
- **能力圈+意见资格**：知道自己不知道更重要

**触发词**：各方、利益、激励、立场、冲突、博弈、矛盾、联盟、诉求、激励诊断

**输出特色**：激励结构图、各方立场分析、隐性冲突识别、Lollapalooza检测

---

#### `past_experience` - 达尔文经验视角
**来源**：达尔文进化论 + 认知心理学 | **人物**：Charles Darwin
**核心心智模型**：
- **达尔文进化机制**：变异+选择+遗传，环境压力是主驱动力
- **自然选择类比**：好策略像好基因被保留，坏策略被淘汰
- **认知锚定警惕**：过去经验会成为未来判断的锚点（资产或负债）
- **确认偏误回溯**：选择性记忆验证已有观点
- **模式识别**：提取可复用教训而非记住所有细节

**触发词**：以前、过去、经验、教训、成功案例、失败案例、类比、模式、历史

**输出特色**：历史案例映射、经验适用性评估、锚定偏误警告、模式提取

---

## 🚀 快速开始

### Python API

```python
from super_thinking import think, format_result

# 简单使用
result = think("石榴籽项目省赛怎么准备？", mode="auto")

# 格式化输出
output = format_result(result)
print(output.full_report)
```

### 路由模式

| 模式 | 说明 |
|------|------|
| `auto` | 根据问题关键词自动匹配相关视角 |
| `force_all` | 激活所有18个视角，全面分析 |
| `selective` | 仅激活指定的视角 |

### 指定视角

```python
from super_thinking.core.jury import Jury
from super_thinking.core.registry import get_registry

registry = get_registry()
jury = Jury(registry)

# 指定视角组合
result = jury.think(
    input="这个商业决策有什么风险？",
    context={},
    mode="selective",
    selected=["risk_detail", "stakeholder", "doubt"],  # 塔勒布+芒格+费曼
)
```

---

## 🏗️ 添加新视角

```python
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput

class MyPerspective(Perspective):
    @property
    def id(self) -> str:
        return "my_perspective"

    @property
    def name(self) -> str:
        return "我的视角"

    @property
    def description(self) -> str:
        return "一句话描述这个视角的核心能力"

    @property
    def trigger_keywords(self) -> list[str]:
        return ["关键词1", "关键词2"]

    def think(self, input_str: str, context: dict) -> PerspectiveOutput:
        # 分析逻辑
        return PerspectiveOutput(...)
```

---

## 📁 项目结构

```
src/super_thinking/
├── perspectives/          # 所有视角
│   ├── _interface.py    # Perspective 协议
│   ├── magi_debate.py    # Magi三贤者
│   ├── mao_perspective.py # 毛选
│   ├── meta_thinking.py  # 元思考
│   ├── msa_perspective.py # MSA检索
│   ├── nuwa_meta.py      # 女娲元视角
│   ├── tagmemo_perspective.py # TagMemo
│   ├── vcp_perspective.py # VCP系统
│   ├── verification.py    # 证伪核查
│   ├── elon_perspective.py # 马斯克
│   ├── jobs_perspective.py # 乔布斯
│   ├── zhangxuefeng_perspective.py # 张雪峰
│   ├── naval_perspective.py # 纳瓦尔
│   ├── xmentor_perspective.py # X导师
│   ├── darwin_perspective.py # 达尔文
│   ├── risk_detail_perspective.py # 塔勒布
│   ├── doubt_perspective.py # 费曼
│   ├── stakeholder_perspective.py # 芒格
│   └── past_experience_perspective.py # 达尔文经验
├── core/
│   ├── registry.py       # 视角注册表
│   ├── router.py        # 路由引擎
│   └── jury.py          # 陪审团引擎
└── fusion/
    └── formatter.py      # 结果格式化
```

---

## 🔗 相关链接

- GitHub: https://github.com/YintaTriss/Agent-superthinking
- 视角来源：
  - alchaincyf/taleb-skill
  - alchaincyf/feynman-skill
  - alchaincyf/munger-skill
  - alchaincyf/elon-musk-skill
  - alchaincyf/steve-jobs-skill
  - alchaincyf/naval-skill
  - alchaincyf/zhangxuefeng-skill
  - alchaincyf/x-mentor-skill
  - alchaincyf/darwin-skill
  - alchaincyf/nuwa-skill

---

## 许可证

MIT
