"""Agent-superthinking v6 端到端 smoke test

V 2026-06-04 10:55 写：v6 仓跑通但缺测试覆盖（浮光"多发现"指出的）。
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_01_profile_manager():
    """Check 1: ProfileManager 默认参数"""
    from learning import ProfileManager
    pm = ProfileManager()  # 默认 profiles/
    print(f"✓ Check 1: ProfileManager() default OK, type={type(pm).__name__}")


def test_02_jury_import():
    """Check 2: Jury v6 集成"""
    from super_thinking.core.jury import get_jury
    jury = get_jury()
    assert hasattr(jury, 'think_complex'), "v6 缺 think_complex 方法"
    print(f"✓ Check 2: Jury 有 think_complex (v6 集成)")


def test_03_supervisor_team_learnings():
    """Check 3: v6 三层组件能 import"""
    from super_thinking.orchestrator import SupervisorAdapter
    from super_thinking.team import TeamIntegration
    from super_thinking.learnings import LearningsIntegration
    sup = SupervisorAdapter()
    team = TeamIntegration()
    lea = LearningsIntegration()
    print("✓ Check 3: Supervisor + Team + Learnings 三层 import OK")


def test_04_think_complex_e2e():
    """Check 4: think_complex 端到端 (用 qwen 7B 不用 R1 70B)"""
    os.environ['LLM_MODEL'] = 'qwen2.5-7b-q4'
    os.environ['OLLAMA_URL'] = 'http://127.0.0.1:11434'
    from super_thinking.core.jury import get_jury
    from super_thinking.team import TeamIntegration
    from super_thinking.learnings import LearningsIntegration
    jury = get_jury()
    team = TeamIntegration()
    learnings = LearningsIntegration()
    plan = jury.think_complex(
        question="30岁该跳槽到大模型公司吗？",
        user_id="default",
        team=team,
        learnings=learnings,
    )
    assert isinstance(plan, dict)
    assert 'decomposed_plan' in plan
    dp = plan['decomposed_plan']
    assert 'subtasks' in dp
    print(f"✓ Check 4: think_complex E2E: {len(dp['subtasks'])} 子任务, type={dp.get('question_type','?')}")


if __name__ == "__main__":
    print("=== superthinking v6 smoke test ===")
    test_01_profile_manager()
    test_02_jury_import()
    test_03_supervisor_team_learnings()
    test_04_think_complex_e2e()
    print("\n=== 4/4 check 通过 ===")
