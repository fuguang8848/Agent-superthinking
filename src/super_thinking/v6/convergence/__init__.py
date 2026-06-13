"""
v6 Convergence 模块

提供收敛检测功能，用于判断辩论是否已经收敛。
"""

from .detector import (
    DefaultConvergenceDetector,
    ConvergenceDetector,
    ConvergenceSignal,
    ConvergenceCalculator,
    JaccardCalculator,
    calculate_overlap_rate,
    calculate_new_arg_density,
    calculate_confidence_drift,
)


__all__ = [
    "ConvergenceDetector",
    "ConvergenceSignal",
    "ConvergenceCalculator",
    "JaccardCalculator",
    "DefaultConvergenceDetector",
    "calculate_overlap_rate",
    "calculate_new_arg_density",
    "calculate_confidence_drift",
]
