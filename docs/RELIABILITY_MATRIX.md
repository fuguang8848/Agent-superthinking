# V6 系统可靠性测试矩阵

> 版本: 0.1.0
> 状态: 草案
> 日期: 2026-06-05

本文档定义了 V6 Multi-Agent 圆桌辩论系统的可靠性测试场景，涵盖异常处理、恢复机制和降级策略。

---

## 1. LLM 调用故障

### 1.1 超时场景

| 场景 ID | 场景描述 | 触发条件 | 期望行为 | 严重程度 |
|---------|----------|----------|----------|----------|
| LLM-T01 | 单次调用超时 | LLM 响应 > 超时阈值 | 重试 3 次，失败则使用缓存或降级 | 高 |
| LLM-T02 | 连续超时 | 3 次调用连续超时 | 降级到 v5 模式 | 严重 |
| LLM-T03 | 慢响应 | 响应时间 > 5s | 记录警告，继续等待 | 中 |
| LLM-T04 | 超时后成功 | 超时后 LLM 返回 | 使用返回结果，标记警告 | 低 |

### 1.2 超时测试实现
```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

class TestLLMTimeout:
    """LLM 超时测试"""
    
    @pytest.mark.asyncio
    async def test_single_timeout_retry(self):
        """测试单次超时重试"""
        call_count = 0
        
        async def slow_mock(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise asyncio.TimeoutError("LLM 调用超时")
            return "成功响应"
        
        with patch('v6.llm.call', slow_mock):
            result = await call_with_retry(
                llm_func=slow_mock,
                max_retries=3,
                timeout=1.0
            )
            
            assert call_count == 3
            assert result == "成功响应"
    
    @pytest.mark.asyncio
    async def test_continuous_timeout_fallback(self):
        """测试连续超时降级"""
        async def always_timeout(*args, **kwargs):
            raise asyncio.TimeoutError("LLM 调用超时")
        
        with patch('v6.llm.call', always_timeout):
            result = await call_with_fallback(
                llm_func=always_timeout,
                fallback_func=mock_v5_response
            )
            
            assert result.mode == "v5_fallback"
```

### 1.3 超时配置
```python
# 超时配置
LLM_TIMEOUT_CONFIG = {
    "single_call_timeout": 30.0,      # 单次调用超时（秒）
    "retry_count": 3,                  # 重试次数
    "retry_delay": 1.0,                # 重试延迟（秒）
    "circuit_breaker_threshold": 3,    # 断路器阈值
    "fallback_timeout": 60.0,          # 降级模式超时
}
```

---

## 2. 网络中断

### 2.1 网络故障场景

| 场景 ID | 场景描述 | 触发条件 | 期望行为 | 严重程度 |
|---------|----------|----------|----------|----------|
| NET-T01 | 连接被拒绝 | API 服务不可用 | 切换到备用 API 或降级 | 高 |
| NET-T02 | DNS 解析失败 | 网络配置错误 | 使用缓存配置，报告错误 | 高 |
| NET-T03 | SSL 证书错误 | 证书过期/无效 | 记录警告，跳过 HTTPS 验证（仅测试） | 中 |
| NET-T04 | 间歇性断网 | 网络不稳定 | 实现重试机制 | 中 |
| NET-T05 | 完全断网 | 网络完全断开 | 降级到离线模式 | 严重 |

### 2.2 网络故障测试
```python
import socket
from unittest.mock import patch

class TestNetworkFailure:
    """网络故障测试"""
    
    def test_connection_refused_fallback(self):
        """测试连接被拒绝时的降级"""
        def mock_api_call(*args, **kwargs):
            raise ConnectionRefusedError("连接被拒绝")
        
        with patch('v6.llm.http_post', mock_api_call):
            result = call_with_fallback(
                primary=mock_api_call,
                fallback=mock_cache_response
            )
            
            # 应该使用缓存或降级响应
            assert result is not None
    
    def test_dns_failure_handling(self):
        """测试 DNS 解析失败处理"""
        def mock_dns_failure(*args, **kwargs):
            raise socket.gaierror("DNS 解析失败")
        
        with patch('socket.getaddrinfo', mock_dns_failure):
            result = call_with_fallback(
                primary=mock_dns_failure,
                fallback=mock_local_response
            )
            
            assert result is not None
            assert "缓存" in result.metadata.get("source", "")
```

### 2.3 网络重试策略
```python
import time
import functools

def retry_with_exponential_backoff(max_retries=3, base_delay=1.0):
    """指数退避重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    logging.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
            
            raise last_exception
        return wrapper
    return decorator
```

---

## 3. 专家模块故障

### 3.1 专家崩溃场景

| 场景 ID | 场景描述 | 触发条件 | 期望行为 | 严重程度 |
|---------|----------|----------|----------|----------|
| EXP-T01 | 单个专家崩溃 | 专家进程异常退出 | 移除该专家，继续辩论 | 中 |
| EXP-T02 | 多个专家崩溃 | ≥2 个专家同时崩溃 | 降级到 v5 模式 | 高 |
| EXP-T03 | 专家响应无效 | 专家返回格式错误 | 使用默认值，记录警告 | 中 |
| EXP-T04 | 专家死锁 | 专家无限等待 | 超时后移除该专家 | 高 |
| EXP-T05 | 专家行为异常 | 返回内容包含安全风险 | 过滤危险内容，继续 | 中 |

### 3.2 专家故障测试
```python
class TestExpertFailure:
    """专家故障测试"""
    
    def test_single_expert_crash_continues(self):
        """测试单个专家崩溃时继续辩论"""
        experts = [
            MockExpert("e1"),  # 正常
            MockExpert("e2"),  # 会崩溃
            MockExpert("e3"),  # 正常
        ]
        
        def crash_mock(*args, **kwargs):
            raise RuntimeError("专家进程崩溃")
        
        debate = DebateSession(experts=experts)
        
        # e2 崩溃
        with patch.object(experts[1], 'think', crash_mock):
            result = debate.run()
            
            # 辩论应该继续
            assert result is not None
            assert result.completed_experts == ["e1", "e3"]
            assert result.failed_experts == ["e2"]
    
    def test_expert_timeout_removal(self):
        """测试专家超时移除"""
        async def slow_expert(*args, **kwargs):
            await asyncio.sleep(60)  # 超过超时阈值
        
        with patch('v6.experts.Expert.think', slow_expert):
            with pytest.raises(ExpertTimeoutError):
                call_with_timeout(
                    expert.think,
                    timeout=10.0
                )
```

### 3.3 专家健康检查
```python
import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExpertHealthStatus:
    """专家健康状态"""
    expert_id: str
    is_alive: bool
    last_response_time: Optional[float] = None
    error_count: int = 0
    is_responsive: bool = True

class ExpertHealthMonitor:
    """专家健康监控"""
    
    def __init__(self):
        self.experts: dict[str, ExpertHealthStatus] = {}
    
    async def check_expert(self, expert_id: str) -> ExpertHealthStatus:
        """检查专家健康状态"""
        try:
            start = time.time()
            await asyncio.wait_for(
                self.experts[expert_id].ping(),
                timeout=5.0
            )
            return ExpertHealthStatus(
                expert_id=expert_id,
                is_alive=True,
                last_response_time=time.time() - start
            )
        except asyncio.TimeoutError:
            return ExpertHealthStatus(
                expert_id=expert_id,
                is_alive=False,
                is_responsive=False,
                error_count=self.experts[expert_id].error_count + 1
            )
```

---

## 4. 主持人崩溃恢复

### 4.1 主持人故障场景

| 场景 ID | 场景描述 | 触发条件 | 期望行为 | 严重程度 |
|---------|----------|----------|----------|----------|
| MOD-T01 | 主持人异常退出 | 进程崩溃/被杀死 | 自动重启，从检查点恢复 | 严重 |
| MOD-T02 | 主持人死锁 | 无限等待某个条件 | 超时重启 | 高 |
| MOD-T03 | 主持人状态损坏 | 内存数据损坏 | 加载最新检查点 | 高 |
| MOD-T04 | 主持人资源耗尽 | 内存/CPU 耗尽 | 清理资源后重启 | 中 |

### 4.2 主持人恢复测试
```python
import pickle
from pathlib import Path

class TestModeratorRecovery:
    """主持人恢复测试"""
    
    def test_moderator_checkpoint_recovery(self):
        """测试主持人从检查点恢复"""
        # 创建检查点
        checkpoint_path = Path("checkpoint.pkl")
        session = DebateSession(...)
        
        # 保存检查点
        with open(checkpoint_path, 'wb') as f:
            pickle.dump({
                'session_state': session.get_state(),
                'round_number': 3,
                'experts': session.experts,
            }, f)
        
        # 模拟主持人崩溃
        moderator = Moderator()
        moderator.crash()
        
        # 重新启动并恢复
        new_moderator = Moderator()
        new_moderator.restore_from_ch
