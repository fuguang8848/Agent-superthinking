# V6 系统可移植性检查清单

> 版本: 0.1.0
> 状态: 草案
> 日期: 2026-06-05

本文档定义了确保 V6 Multi-Agent 圆桌辩论系统跨平台运行的可移植性要求。

---

## 1. Python 版本要求

### 最低版本验证
```bash
# 检查当前 Python 版本
python --version

# 验证版本要求
python -c "import sys; assert sys.version_info >= (3, 10)"
```

| 组件 | 最低版本 | 推荐版本 | 理由 |
|------|----------|----------|------|
| Python | 3.10 | 3.11+ | `dataclasses.field` default 改进 |
| typing | 3.10 内置 | 3.10 内置 | 完全向后兼容 |

### 版本兼容性检查
```python
import sys
from packaging import version

MIN_VERSION = "3.10"
current = f"{sys.version_info.major}.{sys.version_info.minor}"

if version.parse(current) < version.parse(MIN_VERSION):
    raise SystemExit(f"需要 Python >= {MIN_VERSION}, 当前版本: {current}")
```

---

## 2. 第三方依赖

### 必须依赖 (Required)
| 依赖 | 版本 | 用途 | 备选方案 |
|------|------|------|----------|
| `pyyaml` | ≥6.0 | YAML 配置加载 | 内置 JSON 替代 |
| `pytest` | ≥7.0 | 测试框架 | unittest 内置 |

### 可选依赖 (Optional)
| 依赖 | 版本 | 用途 | 缺失时行为 |
|------|------|------|-----------|
| `openai` | ≥1.0 | LLM 调用 | 使用 mock |
| `anthropic` | ≥0.18 | Claude 调用 | 使用 mock |
| `langchain` | ≥0.1 | Agent 框架 | 使用原生 API |
| `rich` | ≥13.0 | 彩色输出 | 回退到纯文本 |

### 依赖安装
```bash
# 仅安装必须依赖
pip install -e ".[core]"

# 安装所有依赖
pip install -e ".[all]"
```

---

## 3. 路径处理

### 跨平台路径原则
```python
from pathlib import Path
import os

# ❌ 错误：硬编码路径分隔符
config_path = "C:\Users\config\settings.yaml"  # Windows only
config_path = "/home/user/config/settings.yaml"   # Unix only

# ✅ 正确：使用 pathlib
config_dir = Path(__file__).parent.parent / "config"
config_path = config_dir / "settings.yaml"

# ✅ 正确：使用 os.path
config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
```

### 路径验证检查清单
| 检查项 | Windows | Linux | macOS | 验证命令 |
|--------|---------|-------|-------|----------|
| 目录存在 | ✓ | ✓ | ✓ | `Path.is_dir()` |
| 文件可写 | ✓ | ✓ | ✓ | `Path.stat().st_mode` |
| 路径编码 | UTF-8 | UTF-8 | UTF-8 | 文件打开测试 |
| 权限正确 | N/A | ✓ | ✓ | `os.access(path, os.W_OK)` |

### 临时文件处理
```python
import tempfile
import os

# ✅ 使用系统临时目录
temp_dir = Path(tempfile.gettempdir()) / "v6_debate"
temp_dir.mkdir(parents=True, exist_ok=True)

# ✅ 使用 tempfile 创建文件
with tempfile.NamedTemporaryFile(
    mode='w',
    encoding='utf-8',
    suffix='.json',
    delete=False
) as f:
    temp_path = Path(f.name)
```

---

## 4. 文件编码

### 编码要求
- **所有源文件**: UTF-8 (无 BOM)
- **配置文件**: UTF-8
- **输入/输出**: UTF-8
- **日志文件**: UTF-8

### 编码检查脚本
```python
import chardet
from pathlib import Path

def verify_file_encoding(file_path: Path) -> bool:
    """验证文件编码"""
    with open(file_path, 'rb') as f:
        raw = f.read()
        result = chardet.detect(raw)
        return result['encoding'] == 'utf-8' and result['confidence'] > 0.9

# 检查所有 Python 文件
for py_file in Path(".").rglob("*.py"):
    assert verify_file_encoding(py_file), f"文件编码错误: {py_file}"
```

### BOM 处理
```python
# ❌ 错误：写入 BOM
with open(file_path, 'w', encoding='utf-8') as f:
    f.write('\ufeff')  # 不要这样做

# ✅ 正确：不写入 BOM
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)  # 纯 UTF-8

# ✅ 正确：如果必须读取带 BOM 的文件
with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()
```

---

## 5. 环境变量

### 环境变量分类

#### 必需环境变量 (Required)
| 变量名 | 示例值 | 用途 | 默认值 |
|--------|--------|------|--------|
| `V6_DATA_DIR` | `./data` | 数据目录 | `./data` |
| `V6_CONFIG_DIR` | `./config` | 配置目录 | `./config` |
| `V6_LOG_LEVEL` | `INFO` | 日志级别 | `INFO` |

#### 可选环境变量 (Optional)
| 变量名 | 示例值 | 用途 | 默认行为 |
|--------|--------|------|----------|
| `OPENAI_API_KEY` | `sk-xxx` | OpenAI API | 使用 mock |
| `ANTHROPIC_API_KEY` | `sk-ant-xxx` | Anthropic API | 使用 mock |
| `V6_LLM_PROVIDER` | `openai` | LLM 提供商 | 自动检测 |
| `V6_MAX_TOKENS` | `4096` | 最大 token | `8192` |

#### 环境变量验证
```python
import os
from dataclasses import dataclass, field

@dataclass
class EnvConfig:
    """环境变量配置"""
    data_dir: Path = field(default_factory=lambda: Path("./data"))
    config_dir: Path = field(default_factory=lambda: Path("./config"))
    log_level: str = field(default_factory=lambda: os.getenv("V6_LOG_LEVEL", "INFO"))
    llm_provider: str = field(default_factory=lambda: os.getenv("V6_LLM_PROVIDER", "mock"))
    
    @classmethod
    def from_env(cls) -> "EnvConfig":
        """从环境变量加载配置"""
        return cls(
            data_dir=Path(os.getenv("V6_DATA_DIR", "./data")),
            config_dir=Path(os.getenv("V6_CONFIG_DIR", "./config")),
            log_level=os.getenv("V6_LOG_LEVEL", "INFO"),
            llm_provider=os.getenv("V6_LLM_PROVIDER", "mock"),
        )
    
    def validate(self) -> list[str]:
        """验证配置，返回错误列表"""
        errors = []
        if not self.data_dir.exists():
            errors.append(f"数据目录不存在: {self.data_dir}")
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            errors.append(f"无效日志级别: {self.log_level}")
        return errors
```

---

## 6. 配置加载

### 支持的配置格式
| 格式 | 扩展名 | 库依赖 | 优先级 |
|------|--------|--------|--------|
| YAML | `.yaml`, `.yml` | pyyaml | 高 |
| JSON | `.json` | 内置 | 中 |
| TOML | `.toml` | tomli/tomli-w | 低 |

### 配置加载器
```python
import json
import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigLoader:
    """跨平台配置加载器"""
    
    @staticmethod
    def load_yaml(path: Path) -> Dict[str, Any]:
        """加载 YAML 配置"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    @staticmethod
    def load_json(path: Path) -> Dict[str, Any]:
        """加载 JSON 配置"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def load(cls, path: Path) -> Dict[str, Any]:
        """自动检测格式并加载"""
        suffix = path.suffix.lower()
        
        if suffix in ('.yaml', '.yml'):
            return cls.load_yaml(path)
        elif suffix == '.json':
            return cls.load_json(path)
        else:
            raise ValueError(f"不支持的配置文件格式: {suffix}")
```

---

## 7. 日志系统

### 日志配置
```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path = None):
    """配置日志系统"""
    
    # 日志格式
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    
    # 处理器列表
    handlers = []
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter(fmt, date_fmt))
    handlers.append(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(fmt, date_fmt))
        handlers.append(file_handler)
    
    # 根日志器
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True  # 重新配置已存在的日志器
    )

# 使用示例
logger = logging.getLogger(__name__)
logger.info("辩论会话开始")
logger.debug("专家选择: %s", expert_list)
```

### 日志级别检查
| 级别 | 用途 | 生产环境 |
|------|------|----------|
| DEBUG | 详细调试信息 | ❌ 关闭 |
| INFO | 一般信息 | ✅ INFO |
| WARNING | 警告 | ✅ WARNING |
| ERROR | 错误 | ✅ ERROR |

---

## 8. 完整检查清单

### 部署前检查
```bash
# 1. Python 版本检查
python -c "import sys; assert sys.version_info >= (3, 10)"

# 2. 依赖检查
pip install -e ".[core]"
python -c "import yaml, pytest"

# 3. 目录权限检查
python -c "
from pathlib import Path
for d in ['data', 'config', 'logs']:
    p = Path(d)
    p.mkdir(exist_ok=True)
    assert p.exists() and p.is_dir(), f'目录不可用: {d}'
"

# 4. 编码检查
find . -name "*.py" -exec python -c "
import sys
with open(sys.argv[1], 'rb') as f:
    assert f.read().decode('utf-8'), sys.argv[1]
" {} \;

# 5. 配置文件检查
python -c "
from scripts.e2e_runner import load_config
config = load_config()
assert not config.validate(), '配置验证失败'
"
```

### CI/CD 集成
```yaml
# .github/workflows/test.yml
name: Cross-Platform Tests
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python: ["3.10", "3.11", "3.12"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions
