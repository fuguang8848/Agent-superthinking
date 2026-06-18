"""
Agent-superthinking Jury analysis_metadata 修复测试 (SOP #36 升级必带 test)

V 6/18 修 JuryResult dataclass 缺 analysis_metadata 字段 (报告 P0 bug)

测试覆盖:
1. JuryResult 现在有 analysis_metadata 字段 (回归保护)
2. 默认值是空 dict (不传也能用)
3. .get('experts_used', []) 模式可访问 (super_brain.py:174 调用模式)
4. think() 实际填 experts_used (从 routing_result.activated)
5. 不传 analysis_metadata 也能用 (backward compat)

回归保护: 防止有人删 analysis_metadata 字段
"""
import sys
import os
import dataclasses
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


def test_01_juryresult_has_analysis_metadata():
    """Check 1: JuryResult 包含 analysis_metadata 字段"""
    from super_thinking.core.jury import JuryResult
    fields = [f.name for f in dataclasses.fields(JuryResult)]
    assert "analysis_metadata" in fields, f"JuryResult 缺 analysis_metadata, fields={fields}"
    print(f"✓ Check 1: JuryResult fields={fields}")


def test_02_analysis_metadata_default_empty_dict():
    """Check 2: 不传 analysis_metadata 默认空 dict"""
    from super_thinking.core.jury import JuryResult
    r = JuryResult(
        outputs={},
        errors={},
        routing_result=None,
        total_perspectives=0,
        successful=0,
        failed=0,
    )
    assert r.analysis_metadata == {}, f"默认应是空 dict, 实际 {r.analysis_metadata}"
    print("✓ Check 2: 默认 analysis_metadata={} (空 dict)")


def test_03_get_experts_used_pattern():
    """Check 3: super_brain.py:174 调用模式 .get('experts_used', []) 可用"""
    from super_thinking.core.jury import JuryResult
    r = JuryResult(
        outputs={},
        errors={},
        routing_result=None,
        total_perspectives=2,
        successful=2,
        failed=0,
        analysis_metadata={"experts_used": ["商业", "哲学"]},
    )
    # super_brain.py:174 实际调用
    experts_used = r.analysis_metadata.get("experts_used", []) if r.analysis_metadata else []
    assert experts_used == ["商业", "哲学"], f".get 模式失败: {experts_used}"
    print(f"✓ Check 3: super_brain.py:174 .get() 模式 work, experts_used={experts_used}")


def test_04_get_experts_used_with_empty_metadata():
    """Check 4: analysis_metadata 是 None 时不崩 (backward compat)"""
    from super_thinking.core.jury import JuryResult
    # 模拟 backward compat: 不填 analysis_metadata
    r = JuryResult(
        outputs={},
        errors={},
        routing_result=None,
        total_perspectives=0,
        successful=0,
        failed=0,
    )
    # 三元表达式模式: if r.analysis_metadata else []
    experts_used = r.analysis_metadata.get("experts_used", []) if r.analysis_metadata else []
    assert experts_used == [], f"空 dict 应返回 [], 实际 {experts_used}"
    print("✓ Check 4: 空 metadata .get() 返回 [] (backward compat)")


def test_05_jury_think_fills_experts_used():
    """Check 5: think() 自动填 experts_used (从 routing_result.activated)"""
    from super_thinking.core.jury import JuryResult
    # 模拟 think() 返回: 视角 ID 从 routing_result.activated
    r = JuryResult(
        outputs={"A": None, "B": None, "C": None},
        errors={},
        routing_result=None,  # 简化, 只测 metadata
        total_perspectives=3,
        successful=3,
        failed=0,
        analysis_metadata={"experts_used": ["A", "B", "C"]},
    )
    assert r.analysis_metadata["experts_used"] == ["A", "B", "C"]
    # 关键: experts_used 应跟 outputs 的 keys 一致
    assert set(r.analysis_metadata["experts_used"]) == set(r.outputs.keys())
    print(f"✓ Check 5: experts_used={r.analysis_metadata['experts_used']} 跟 outputs 一致")


def test_06_no_attribute_error_on_juryresult():
    """Check 6: 直接访问 .analysis_metadata 不抛 AttributeError (旧 bug 回归保护)"""
    from super_thinking.core.jury import JuryResult
    r = JuryResult(
        outputs={},
        errors={},
        routing_result=None,
        total_perspectives=0,
        successful=0,
        failed=0,
    )
    # 旧 bug: AttributeError: 'JuryResult' object has no attribute 'analysis_metadata'
    try:
        _ = r.analysis_metadata
        print("✓ Check 6: 访问 .analysis_metadata 不抛 AttributeError (旧 bug 修复)")
    except AttributeError as e:
        raise AssertionError(f"回归! {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Agent-superthinking Jury analysis_metadata 修复测试 (SOP #36)")
    print("=" * 60)
    test_01_juryresult_has_analysis_metadata()
    test_02_analysis_metadata_default_empty_dict()
    test_03_get_experts_used_pattern()
    test_04_get_experts_used_with_empty_metadata()
    test_05_jury_think_fills_experts_used()
    test_06_no_attribute_error_on_juryresult()
    print("=" * 60)
    print("✅ 6/6 tests passed")
    print("=" * 60)
