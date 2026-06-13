"""
v6 Moderator 模块

提供主持人功能，包括：
- Moderator 主类：负责决策、论点提取、菜单构建
- ArgumentExtractor：结构化论点解析器
"""

from .moderator import (
    Moderator,
    ModeratorImpl,
    DefaultModerator,
    ModeratorConfig,
)
from .argument_extractor import (
    ArgumentExtractor,
    extract_arguments_from_statement,
)
from .menu_builder import (
    MenuBuilder,
    build_argument_menu,
)

__all__ = [
    "Moderator",
    "DefaultModerator",
    "ModeratorConfig",
    "ArgumentExtractor",
    "extract_arguments_from_statement",
    "MenuBuilder",
    "build_argument_menu",
]
