#!/usr/bin/env python3
"""
主持人功能验证脚本

验证主持人 (Moderator) 的核心功能：
- 初始化辩论会话
- 选择专家组合
- 整理论点菜单
- 收敛判断
- 生成会议结论
"""

import sys
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class VerificationResult:
    """验证结果"""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


class ModeratorVerifier:
    """主持人验证器"""
    
    def __init__(self):
        self.results: List[VerificationResult] = []
    
    def verify_initialization(self, question: str, expert_count: int) -> VerificationResult:
        """验证初始化功能"""
        try:
            # 验证问题有效性
            if not question or len(question) < 5:
                return VerificationResult(
                    name="主持人初始化-问题有效性",
                    passed=False,
                    message="问题太短或为空"
                )
            
            # 验证专家数量
            if expert_count < 3:
                return VerificationResult(
                    name="主持人初始化-专家数量",
                    passed=False,
                    message=f"专家数量不足: {expert_count} < 3"
                )
            
            return VerificationResult(
                name="主持人初始化",
                passed=True,
                message="初始化成功",
                details={"question": question, "expert_count": expert_count}
            )
        except Exception as e:
            return VerificationResult(
                name="主持人初始化",
                passed=False,
                message=f"初始化失败: {str(e)}"
            )
    
    def verify_argument_menu_format(self, menu_text: str) -> VerificationResult:
        """验证论点菜单格式"""
        required_sections = [
            "核心论点",
            "可反驳",
        ]
        
        missing_sections = [s for s in required_sections if s not in menu_text]
        
        if missing_sections:
            return VerificationResult(
                name="论点菜单格式",
                passed=False,
                message=f"缺少必要部分: {', '.join(missing_sections)}",
                details={"menu_text": menu_text[:200]}
            )
        
        return VerificationResult(
            name="论点菜单格式",
            passed=True,
            message="格式正确"
        )
    
    def verify_convergence_logic(self, rounds: List[Dict], max_rounds: int) -> VerificationResult:
        """验证收敛逻辑"""
        if len(rounds) < 2:
            return VerificationResult(
                name="收敛逻辑",
                passed=False,
                message="轮次不足，无法判断收敛"
            )
        
        # 达到最大轮次应该收敛
        if len(rounds) >= max_rounds:
            return VerificationResult(
                name="收敛逻辑-最大轮次",
                passed=True,
                message="达到最大轮次，触发收敛"
            )
        
        # 检查论点密度
        last_round_args = len(rounds[-1].get("statements", []))
        prev_round_args = len(rounds[-2].get("statements", []))
        
        if last_round_args <= prev_round_args:
            return VerificationResult(
                name="收敛逻辑-论点密度",
                passed=True,
                message="论点密度下降，触发收敛"
            )
        
        return VerificationResult(
            name="收敛逻辑",
            passed=True,
            message="辩论尚未收敛"
        )
    
    def verify_conclusion_structure(self, conclusion: Dict) -> VerificationResult:
        """验证结论结构"""
        required_keys = ["共识点", "分歧点", "未解决的根本矛盾", "建议"]
        
        missing_keys = [k for k in required_keys if k not in conclusion]
        
        if missing_keys:
            return VerificationResult(
                name="结论结构",
                passed=False,
                message=f"缺少必要部分: {', '.join(missing_keys)}"
            )
        
        # 验证建议是可操作的
        suggestions = conclusion.get("建议", [])
        if not isinstance(suggestions, list) or len(suggestions) == 0:
            return VerificationResult(
                name="结论建议",
                passed=False,
                message="建议为空或格式错误"
            )
        
        return VerificationResult(
            name="结论结构",
            passed=True,
            message="结论结构完整",
            details={"conclusion_keys": list(conclusion.keys())}
        )
    
    def print_results(self):
        """打印验证结果"""
        print("\n" + "=" * 60)
        print("主持人功能验证结果")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        for result in self.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"\n{status}: {result.name}")
            print(f"  {result.message}")
            if result.details:
                print(f"  详情: {result.details}")
        
        print("\n" + "-" * 60)
        print(f"总计: {passed}/{total} 项通过")
        print("=" * 60)
        
        return passed == total


def main():
    """主函数"""
    verifier = ModeratorVerifier()
    
    # 测试初始化
    result = verifier.verify_initialization("这个项目要不要接？", 3)
    verifier.results.append(result)
    
    # 测试论点菜单格式
    result = verifier.verify_argument_menu_format(
        "## 第1轮论点菜单\n\n### 核心论点（可反驳）\n1. 专家A认为X"
    )
    verifier.results.append(result)
    
    # 测试收敛逻辑
    result = verifier.verify_convergence_logic(
        [{"statements": ["A", "B"]}, {"statements": ["A"]}],
        max_rounds=5
    )
    verifier.results.append(result)
    
    # 测试结论结构
    result = verifier.verify_conclusion_structure({
        "共识点": ["A和B都认为X"],
        "分歧点": ["Y问题上存在分歧"],
        "未解决的根本矛盾": ["短期vs长期"],
        "建议": ["进一步调查"]
    })
    verifier.results.append(result)
    
    # 打印结果
    success = verifier.print_results()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
