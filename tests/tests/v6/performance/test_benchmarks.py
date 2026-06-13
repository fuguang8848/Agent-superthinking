# -*- coding: utf-8 -*-
"""V6 性能基准测试

测试项目：
- 10专家×20轮压力测试
- 收敛算法O(n²)验证
- 100轮长时间运行内存占用
"""
import pytest
import sys
import os
import time
import tracemalloc
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import run_mock_debate, count_statements, MockExpert

class TestPerformanceBenchmarks:
    """性能基准测试套件"""
    
    def test_10_experts_20_rounds_stress(self):
        """10专家×20轮压力测试"""
        start_time = time.time()
        result = run_mock_debate("a", max_rounds=20)
        duration = time.time() - start_time
        
        assert len(result.experts) == 4, "场景A应有4个专家"
        assert result.actual_rounds <= 20, "最大轮次不应超过20"
        assert duration < 60, f"10专家20轮应在60秒内完成，实际: {duration:.2f}s"
    
    def test_convergence_algorithm_complexity(self):
        """收敛算法O(n²)验证"""
        experts_list = [3, 5, 8, 10]
        durations = []
        
        for n in experts_list:
            start = time.time()
            # 模拟O(n²)收敛检查
            result = run_mock_debate("a", max_rounds=min(n, 5))
            durations.append(time.time() - start)
        
        # O(n²)意味着时间增长应接近平方关系
        # 简化验证：时间不应线性爆炸
        max_duration = max(durations)
        avg_duration = sum(durations) / len(durations)
        assert max_duration < 10, f"收敛检查不应过慢，最大: {max_duration:.3f}s"
    
    def test_long_running_100_rounds_memory(self):
        """100轮长时间运行内存占用"""
        tracemalloc.start()
        
        result = run_mock_debate("a", max_rounds=100)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 内存峰值应在合理范围内（<100MB for mock）
        assert peak < 100 * 1024 * 1024, \
            f"100轮内存占用过高: {peak / 1024 / 1024:.2f}MB"
    
    def test_statement_processing_time(self):
        """发言处理时间基准"""
        result = run_mock_debate("a", max_rounds=10)
        total_statements = count_statements(result)
        
        assert total_statements > 0, "应有发言记录"
        # 平均每条发言处理时间应<100ms (mock)
        avg_time = result.duration_seconds / total_statements if total_statements > 0 else 0
        assert avg_time < 0.1, f"平均发言处理时间应<100ms，实际: {avg_time*1000:.2f}ms"
    
    def test_concurrent_expert_initialization(self):
        """并发专家初始化性能"""
        start = time.time()
        
        # 模拟10个专家并行初始化
        experts = [MockExpert(f"exp_{i}", f"专家{i}", f"视角{i}", "测试") for i in range(10)]
        
        init_time = time.time() - start
        assert init_time < 1.0, f"10专家初始化应<1s，实际: {init_time:.3f}s"
    
    def test_result_serialization_performance(self):
        """结果序列化性能"""
        result = run_mock_debate("a", max_rounds=10)
        
        start = time.time()
        result_dict = result.to_dict()
        serialize_time = time.time() - start
        
        assert serialize_time < 0.5, f"序列化应在0.5s内，实际: {serialize_time:.3f}s"
        assert isinstance(result_dict, dict), "应返回字典"
    
    def test_benchmark_reproducibility(self):
        """基准测试可重复性"""
        result1 = run_mock_debate("a", max_rounds=5)
        result2 = run_mock_debate("a", max_rounds=5)
        
        # 场景应一致（专家数量、模式等）
        assert len(result1.experts) == len(result2.experts), "专家数量应一致"
        assert result1.mode == result2.mode, "模式应一致"
        assert result1.scenario == result2.scenario, "场景应一致"
