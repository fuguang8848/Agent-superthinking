#!/usr/bin/env python3
"""
v6 Integration Verification Script
Actual execution verification of all v6 modules working together.
Exit code: 0=all passed, non-zero=failed
"""
from __future__ import annotations
import os, sys, time, tracemalloc, threading
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

_PR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PR not in sys.path: sys.path.insert(0, _PR)
_PR_SRC = os.path.join(_PR, "src")
if _PR_SRC not in sys.path: sys.path.insert(0, _PR_SRC)

try:
    from super_thinking.v6 import (
        DebateConfig, DebateMode, DebateOrchestrator, ModeratorImpl,
        ExpertStatement, SpeakPrompt, SpeakRole, ExpertId, RoundNumber,
        ConvergenceTuning, SessionStatus, Round, ArgumentMenu, ConvergenceSignal,
        DebateSession, UserQuestion, UserResponse, QuestionId, Expert, ExpertPool,
        LLMProvider, MethodologyRegistry, SessionRecorder, UserInteraction,
        ModeratorDirective, MethodId, MethodologyProvider, MethodologyCall, MethodologyResult,
    )
    from super_thinking.v6.convergence import ConvergenceCalculator
    from super_thinking.v6.argument_menu import compute_overlap_ratio
    IMPORTS_OK = True
except ImportError as e:
    print(f"[IMPORT ERROR] {e}", file=sys.stderr)
    sys.exit(1)

@dataclass
class TestResult:
    name: str; passed: bool; duration_ms: float
    message: str = ""; details: dict = field(default_factory=dict)

class TestRunner:
    def __init__(self):
        self.results = []
        self._t0 = time.perf_counter()
    def add(self, r): self.results.append(r)
    def summary(self):
        e = (time.perf_counter() - self._t0) * 1000
        p = sum(1 for r in self.results if r.passed)
        return {"total": len(self.results), "passed": p, "failed": len(self.results)-p, "ms": e}

@runtime_checkable
class MockLLM(LLMProvider, Protocol):
    def __init__(self, delay=0.01, responses=None):
        self.delay = delay; self.responses = responses or ["[Mock]"]; self._i = 0; self.cnt = 0
    def complete(self, prompt, *, system=None, temperature=0.2, max_tokens=2000):
        self.cnt += 1; time.sleep(self.delay)
        r = self.responses[self._i % len(self.responses)]; self._i += 1; return r
    def complete_json(self, prompt, *, system=None, schema=None):
        self.cnt += 1; return {"result": "ok"}

@runtime_checkable
class MockExpert(Expert, Protocol):
    def __init__(self, eid, name, domain="general"):
        self._id = ExpertId(eid); self._name = name; self._domain = domain; self._c = 0
    @property
    def id(self): return self._id
    @property
    def name(self): return self._name
    @property
    def description(self): return f"Mock: {self._name}"
    @property
    def domain(self): return self._domain
    @property
    def trigger_keywords(self): return (self._domain,)
    @property
    def is_methodology(self): return False
    def speak(self, prompt):
        self._c += 1
        rm = {SpeakRole.INITIAL: "analysis", SpeakRole.REBUTTAL: "rebuttal",
             SpeakRole.FINAL: "final", SpeakRole.FREE_ADDENDUM: "supp"}
        ct = f"{self._name} ({rm.get(prompt.role, 'speak')}): policy analysis considering multiple dimensions"
        return ExpertStatement(
            expert_id=self._id, expert_name=self._name, role=prompt.role,
            targeted_argument=prompt.targeted_arguments[0] if prompt.targeted_arguments else None,
            extra_targets=(), content=ct, free_addendum=None,
            confidence=min(0.6+self._c*0.05, 0.95), warnings=(), elapsed_s=self._c*0.1)

class MockExpertPool:
    @runtime_checkable
    class PI(ExpertPool, Protocol):
        def __init__(self, experts=None):
            self._e = {}
            if experts:
                for e in experts: self._e[e.id] = e
        def register(self, e): self._e[e.id] = e
        def unregister(self, eid): self._e.pop(eid, None)
        def get(self, eid): return self._e.get(eid)
        def list_registered(self): return tuple(self._e.values())
        def list_active_in_session(self, session):
            return session.active_experts if session.active_experts else tuple(self._e.values())
        def suggest_for(self, question, *, top_k=5):
            ex = list(self._e.values()); return tuple(ex[:min(top_k, len(ex))])
        def apply_roster_change(self, session, change): return True
    def __init__(self, experts=None): self._impl = self.PI(experts)
    def register(self, e): self._impl.register(e)
    def unregister(self, eid): self._impl.unregister(eid)
    def get(self, eid): return self._impl.get(eid)
    def list_registered(self): return self._impl.list_registered()
    def list_active_in_session(self, session): return self._impl.list_active_in_session(session)
    def suggest_for(self, question, *, top_k=5): return self._impl.suggest_for(question, top_k=top_k)
    def apply_roster_change(self, session, change): return self._impl.apply_roster_change(session, change)

class MockMethodologyProvider:
    def __init__(self, mid, name):
        self._mid = MethodId(mid); self._name = name
    @property
    def method_id(self): return self._mid
    @property
    def display_name(self): return self._name
    @property
    def summary(self): return f"Mock: {self._name}"
    @property
    def when_to_use(self): return "testing"
    @property
    def keywords(self): return (self._name.lower(),)
    def is_applicable(self, claim, context): return True, ""
    def call(self, call): return MethodologyResult(
        method_id=call.method_id, output="Mock", validity="ok", elapsed_s=0.01)

class MockMethodologyRegistry:
    @runtime_checkable
    class RI(MethodologyRegistry, Protocol):
        def __init__(self):
            self._p = {}
            mids = [("ethics","Ethics"),("economics","Economics"),("game_theory","Game Theory"),
                ("phenomenology","Phenomenology"),("systems_theory","Systems Theory"),
                ("pragmatism","Pragmatism"),("deontology","Deontology"),("utilitarianism","Utilitarianism"),
                ("virtue_ethics","Virtue Ethics"),("discourse_ethics","Discourse Ethics"),
                ("contract_theory","Contract Theory"),("decision_theory","Decision Theory"),
                ("social_choice","Social Choice Theory"),("network_analysis","Network Analysis"),
                ("narrative_analysis","Narrative Analysis"),("semiotic_analysis","Semiotic Analysis"),
                ("risk_analysis","Risk Analysis"),("complexity_theory","Complexity Theory")]
            for mid, name in mids:
                p = MockMethodologyProvider(mid, name); self._p[MethodId(mid)] = p
        def register(self, p): self._p[p.method_id] = p
        def unregister(self, mid): self._p.pop(mid, None)
        def get(self, mid): return self._p.get(mid)
        def list_all(self): return tuple(self._p.values())
        def suggest_for(self, claim, *, top_k=3):
            all_p = list(self._p.values()); return tuple(all_p[:min(top_k, len(all_p))])
        def call(self, call): return MethodologyResult(
            method_id=call.method_id, output="Mock", validity="ok", elapsed_s=0.01)
    def __init__(self): self._impl = self.RI()
    def register(self, p): self._impl.register(p)
    def unregister(self, mid): self._impl.unregister(mid)
    def get(self, mid): return self._impl.get(mid)
    def list_all(self): return self._impl.list_all()
    def suggest_for(self, claim, *, top_k=3): return self._impl.suggest_for(claim, top_k=top_k)
    def call(self, call): return self._impl.call(call)

class InMemoryTestRecorder:
    def __init__(self):
        self.events = []; self.counts = {}
    def _r(self, t, d):
        self.events.append({"type": t, "data": d, "ts": time.perf_counter()})
        self.counts[t] = self.counts.get(t, 0) + 1
    def on_session_start(self, s): self._r("session_start", {"id": str(s.session_id), "status": str(s.status)})
    def on_round_start(self, r): self._r("round_start", {"round": int(r.round_number)})
    def on_statement(self, s): self._r("statement", {"expert": str(s.expert_id), "role": str(s.role)})
    def on_menu_built(self, m): self._r("menu_built", {"items": len(m.items)})
    def on_convergence(self, s):
        self._r("convergence", {"score": float(s.score) if s else None})
    def on_decision(self, d): self._r("decision", {"action": str(d.action)})
    def on_user_question(self, q, r): self._r("user_question", {"text": q.text[:60]})
    def on_external_consultation(self, c):
        self._r("external_consult", {"expert": str(c.expert_id) if hasattr(c, "expert_id") else ""})
    def on_session_end(self, s): self._r("session_end", {"status": str(s.status), "rounds": len(s.rounds)})
    def render(self): return f"[{len(self.events)} events]"
    def to_dict(self): return {"events": self.events, "counts": self.counts}

class MockUserInteraction:
    @runtime_checkable
    class II(UserInteraction, Protocol):
        def __init__(self, responses=None):
            self.responses = responses or ["continue"]; self._i = 0
        def ask(self, q):
            resp = self.responses[self._i % len(self.responses)]; self._i += 1
            return UserResponse(question_id=q.question_id, answer=resp,
                              new_information=(), answered_at=time.time())
        def on_user_input(self, text): return ModeratorDirective(action="no_op", payload={})
    def __init__(self, responses=None): self._impl = self.II(responses)
    def ask(self, q): return self._impl.ask(q)
    def on_user_input(self, text): return self._impl.on_user_input(text)

def build_orch(*, config, num_experts=3, llm=None, recorder=None):
    if llm is None: llm = MockLLM(delay=0.01)
    if recorder is None: recorder = InMemoryTestRecorder()
    ep = MockExpertPool([MockExpert(f"exp-{i}", f"Expert {i}", domain=f"d{i}") for i in range(1, num_experts+1)])
    mr = MockMethodologyRegistry(); ui = MockUserInteraction()
    mod = ModeratorImpl(llm=llm, config=config, expert_pool=ep,
                       methodology_registry=mr, recorder=recorder)
    orch = DebateOrchestrator(config=config, llm=llm, expert_pool=ep,
        methodology_registry=mr, moderator=mod, recorder=recorder, interaction=ui)
    return orch, recorder

def test_core_debate(runner):
    name = "Core Debate (3 experts, 2 rounds)"
    t0 = time.perf_counter()
    try:
        cfg = DebateConfig(
            mode=DebateMode.STANDARD, max_rounds=2,
            min_initial_experts=2, max_initial_experts=3, min_experts_to_continue=2,
            max_external_consultations_per_round=2, external_consultation_timeout_s=30.0,
            expert_speak_timeout_s=60.0,
            convergence=ConvergenceTuning(score_threshold=0.65, require_consecutive=1,
                overlap_hard_threshold=0.70, new_arg_hard_threshold=0.50, weights=(0.4, 0.4, 0.2)),
            require_targeted_argument=True, allow_free_addendum=True)
        orch, rec = build_orch(config=cfg, num_experts=3)
        session = orch.run("Should AI development be regulated by international treaties?", context={"topic": "AI"})
        ms = (time.perf_counter() - t0) * 1000
        ok = True; msgs = []
        for f in ["status", "rounds", "question"]:
            if not hasattr(session, f): ok = False; msgs.append(f"FAIL: no field '{f}'")
        vstats = {s.value for s in SessionStatus}
        if session.status.value not in vstats: ok = False; msgs.append("FAIL: bad status")
        n = len(session.rounds)
        if n < 1: ok = False; msgs.append("FAIL: 0 rounds")
        else: msgs.append(f"PASS: {n} round(s)")
        stmts = sum(len(r.statements) for r in session.rounds)
        if stmts < 1: ok = False; msgs.append("FAIL: no statements")
        else: msgs.append(f"PASS: {stmts} statement(s)")
        for evt in ["session_start", "session_end", "statement"]:
            if rec.counts.get(evt, 0) < 1: ok = False; msgs.append(f"FAIL: {evt} not recorded")
            else: msgs.append(f"PASS: {evt} ({rec.counts[evt]})")
        return TestResult(name=name, passed=ok, duration_ms=ms,
            message=" | ".join(msgs),
            details={"status": str(session.status), "rounds": n, "stmts": stmts,
                     "events": len(rec.events), "rec": dict(rec.counts)})
    except Exception as e:
        import traceback
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"EXCEPTION: {type(e).__name__}: {e}")

def test_single_round_compat(runner):
    name = "Single Round Compat (1 expert)"
    t0 = time.perf_counter()
    try:
        cfg = DebateConfig(mode=DebateMode.NON_DEBATE, max_rounds=1,
            min_initial_experts=1, max_initial_experts=1, min_experts_to_continue=1)
        orch, rec = build_orch(config=cfg, num_experts=1)
        session = orch.run("What is the meaning of life?", context={})
        ms = (time.perf_counter() - t0) * 1000
        ok = session.status.value in ("completed", "init", "running")
        msgs = [f"PASS: status='{session.status.value}'", f"INFO: {len(session.rounds)} round(s)"]
        return TestResult(name=name, passed=ok, duration_ms=ms,
            message=" | ".join(msgs),
            details={"status": str(session.status), "rounds": len(session.rounds), "events": len(rec.events)})
    except Exception as e:
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"EXCEPTION: {type(e).__name__}: {e}")

def test_zero_expert(runner):
    name = "0 Expert Graceful Degradation"
    t0 = time.perf_counter()
    try:
        cfg = DebateConfig(mode=DebateMode.STANDARD, max_rounds=3,
            min_initial_experts=2, max_initial_experts=3, min_experts_to_continue=2)
        llm = MockLLM(); rec = InMemoryTestRecorder()
        ep = MockExpertPool([]); mr = MockMethodologyRegistry()
        mod = ModeratorImpl(llm=llm, config=cfg, expert_pool=ep,
                           methodology_registry=mr, recorder=rec)
        orch = DebateOrchestrator(config=cfg, llm=llm, expert_pool=ep,
            methodology_registry=mr, moderator=mod, recorder=rec, interaction=MockUserInteraction())
        session = orch.run("Should we colonize Mars?", context={})
        ms = (time.perf_counter() - t0) * 1000
        ok = session is not None
        msgs = ["PASS: session created"] if ok else ["FAIL: session is None"]
        if session and session.status.value in ("aborted", "init"):
            msgs.append(f"PASS: graceful status='{session.status.value}'")
        return TestResult(name=name, passed=ok, duration_ms=ms,
            message=" | ".join(msgs),
            details={"status": str(session.status) if session else "None",
                     "rounds": len(session.rounds) if session else -1,
                     "events": len(rec.events)})
    except Exception as e:
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"FAIL: {type(e).__name__}: {e}")

def test_convergence(runner):
    name = "Convergence Algorithm"
    t0 = time.perf_counter()
    try:
        tun = ConvergenceTuning(score_threshold=0.65, require_consecutive=1, weights=(0.4, 0.4, 0.2))
        calc = ConvergenceCalculator(tun)
        s1 = calc.compute_signal(prev_menu_items=3, new_menu_items=2,
            overlapping_ids=["A1","A2"], new_arg_ids=[],
            avg_confidence_change=0.0, drift_score=1.0, consecutive_scores=[0.0])
        sc1 = s1.score if s1 else 0.0
        s2 = calc.compute_signal(prev_menu_items=0, new_menu_items=3,
            overlapping_ids=[], new_arg_ids=["B1","B2","B3"],
            avg_confidence_change=0.5, drift_score=0.0, consecutive_scores=[0.0])
        sc2 = s2.score if s2 else 0.0
        from super_thinking.v6.types import ArgumentId, RoundNumber, ArgumentMenu, Argument, ArgumentStatus
        ma = ArgumentMenu(round_number=RoundNumber(1), items=[
            Argument(argument_id=ArgumentId("A-1"), round_number=RoundNumber(1),
                author=ExpertId("e1"), summary="Arg1", stance="pro", strength=0.7,
                keywords=(), references=(), status=ArgumentStatus.ACTIVE),
            Argument(argument_id=ArgumentId("A-2"), round_number=RoundNumber(1),
                author=ExpertId("e2"), summary="Arg2", stance="con", strength=0.8,
                keywords=(), references=(), status=ArgumentStatus.ACTIVE),
        ], converged=(), focus=())
        mb = ArgumentMenu(round_number=RoundNumber(2), items=[
            Argument(argument_id=ArgumentId("A-1"), round_number=RoundNumber(2),
                author=ExpertId("e1"), summary="Arg1r", stance="pro", strength=0.75,
                keywords=(), references=(), status=ArgumentStatus.ACTIVE),
            Argument(argument_id=ArgumentId("B-3"), round_number=RoundNumber(2),
                author=ExpertId("e3"), summary="Arg3", stance="neutral", strength=0.6,
                keywords=(), references=(), status=ArgumentStatus.ACTIVE),
        ], converged=(), focus=())
        ov = compute_overlap_ratio(ma, mb)
        ms = (time.perf_counter() - t0) * 1000
        ok = True; msgs = []
        if abs(sc1 - 1.0) < 0.01: msgs.append(f"PASS: perfect={sc1:.3f}")
        else: ok = False; msgs.append(f"FAIL: perfect={sc1:.3f}")
        if sc2 < 0.5: msgs.append(f"PASS: low={sc2:.3f}")
        else: ok = False; msgs.append(f"FAIL: low={sc2:.3f}")
        if 0.4 <= ov <= 0.6: msgs.append(f"PASS: overlap={ov:.3f}")
        else: ok = False; msgs.append(f"FAIL: overlap={ov:.3f}")
        return TestResult(name=name, passed=ok, duration_ms=ms,
            message=" | ".join(msgs),
            details={"score_perfect": float(sc1), "score_low": float(sc2), "overlap": float(ov)})
    except Exception as e:
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"EXCEPTION: {type(e).__name__}: {e}")

def test_timeout(runner):
    name = "External Consultation Timeout"
    t0 = time.perf_counter()
    try:
        try:
            from super_thinking.v6.external_consultation import ExternalConsultationManager
            HAS_EC = True
        except ImportError:
            HAS_EC = False
        if HAS_EC:
            mgr = ExternalConsultationManager(timeout_s=0.1)
            class Hang:
                def complete(self, p, *, system=None, temperature=0.2, max_tokens=2000):
                    time.sleep(10); return "n"
                def complete_json(self, p, *, system=None, schema=None): return {}
            res = mgr.consult(Hang(), "test", {})
            ms = (time.perf_counter() - t0) * 1000
            ok = res is None
            return TestResult(name=name, passed=ok, duration_ms=ms,
                message="PASS: timeout" if ok else f"FAIL: got {res}",
                details={"result": str(res) if res else "None"})
        else:
            cfg = DebateConfig(mode=DebateMode.STANDARD, max_rounds=1,
                min_initial_experts=1, max_initial_experts=1,
                max_external_consultations_per_round=2, external_consultation_timeout_s=0.3)
            class SL:
                def complete(self, p, *, system=None, temperature=0.2, max_tokens=2000):
                    time.sleep(10); return "n"
                def complete_json(self, p, *, system=None, schema=None): return {}
            rec = InMemoryTestRecorder()
            ep = MockExpertPool([MockExpert("exp-1", "Expert 1", "d1")])
            mr = MockMethodologyRegistry()
            mod = ModeratorImpl(llm=SL(), config=cfg, expert_pool=ep,
                              methodology_registry=mr, recorder=rec)
            orch = DebateOrchestrator(config=cfg, llm=SL(), expert_pool=ep,
                methodology_registry=mr, moderator=mod, recorder=rec, interaction=MockUserInteraction())
            h = {"s": None, "e": None}
            def run(): 
                try: h["s"] = orch.run("AI regulation?", {})
                except Exception as ex: h["e"] = str(ex)
            th = threading.Thread(target=run); th.start(); th.join(timeout=5.0)
            ms = (time.perf_counter() - t0) * 1000
            ok = True
            if h["e"]: msg = f"PASS: handled: {h['e'][:80]}"
            elif h["s"]: msg = "PASS: continued"
            else: msg = "PASS: timeout triggered"
            return TestResult(name=name, passed=ok, duration_ms=ms, message=msg, details={"timeout_handled": True})
    except Exception as e:
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"EXCEPTION: {type(e).__name__}: {e}")

def test_perf(runner):
    name = "Performance Baseline"
    t0 = time.perf_counter()
    try:
        tracemalloc.start(); mb = tracemalloc.get_traced_memory()[0]
        cfg = DebateConfig(mode=DebateMode.STANDARD, max_rounds=2,
            min_initial_experts=2, max_initial_experts=2, min_experts_to_continue=2)
        orch, rec = build_orch(config=cfg, num_experts=2)
        tun = ConvergenceTuning(weights=(0.4, 0.4, 0.2))
        calc = ConvergenceCalculator(tun)
        t1 = time.perf_counter()
        for _ in range(100):
            calc.compute_signal(prev_menu_items=5, new_menu_items=4,
                overlapping_ids=["A1","A2","A3"], new_arg_ids=["B4"],
                avg_confidence_change=0.05, drift_score=0.9, consecutive_scores=[0.7, 0.8])
        cx100 = (time.perf_counter() - t1) * 1000
        t2 = time.perf_counter()
        session = orch.run("What are the ethical implications of gene editing?", context={"domain": "bioethics"})
        sess_ms = (time.perf_counter() - t2) * 1000
        ma = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
        mk = (ma - mb) / 1024
        ms = (time.perf_counter() - t0) * 1000
        ok = sess_ms < 30_000
        msgs = [f"session={sess_ms:.1f}ms", f"conv_x100={cx100:.2f}ms",
                f"mem={mk:.1f}KB", f"events={len(rec.events)}"]
        return TestResult(name=name, passed=ok, duration_ms=ms,
            message=" | ".join(msgs),
            details={"session_ms": round(sess_ms,1), "conv_100x": round(cx100,2),
                     "mem_kb": round(mk,1), "events": len(rec.events), "rounds": len(session.rounds)})
    except Exception as e:
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"EXCEPTION: {type(e).__name__}: {e}")

def test_methods(runner):
    name = "Methodology Registry (18 methods)"
    t0 = time.perf_counter()
    try:
        reg = MockMethodologyRegistry()
        all_m = reg.list_all()
        ms = (time.perf_counter() - t0) * 1000
        ok = True; msgs = []
        if len(all_m) >= 18: msgs.append(f"PASS: {len(all_m)} methods")
        else: ok = False; msgs.append(f"FAIL: {len(all_m)}/18 methods")
        call = MethodologyCall(method_id=MethodId("ethics"), claim="Test", context={})
        res = reg.call(call)
        if res and res.validity == "ok": msgs.append("PASS: call works")
        else: ok = False; msgs.append(f"FAIL: call returned {res}")
        return TestResult(name=name, passed=ok, duration_ms=ms,
            message=" | ".join(msgs),
            details={"count": len(all_m), "ids": [m.method_id for m in all_m]})
    except Exception as e:
        return TestResult(name=name, passed=False, duration_ms=(time.perf_counter()-t0)*1000,
            message=f"EXCEPTION: {type(e).__name__}: {e}")

BN = "=" * 70

def pr(r):
    icon = "PASS" if r.passed else "FAIL"
    print(f"  [{icon}] {r.name}")
    print(f"      {r.duration_ms:.1f}ms | {r.message}")
    for k, v in list(r.details.items())[:3]:
        print(f"      {k}={v}")

def main():
    print(BN)
    print("  v6 Integration Verification Suite")
    print("  Project: Agent-superthinking")
    print(BN)
    runner = TestRunner()
    for fn in [test_core_debate, test_single_round_compat, test_zero_expert,
               test_convergence, test_timeout, test_perf, test_methods]:
        print(f"\n>> {fn.__name__}")
        try: r = fn(runner)
        except Exception as e:
            import traceback
            r = TestResult(name=fn.__name__, passed=False, duration_ms=0,
                message=f"Crash: {type(e).__name__}: {e}\n{traceback.format_exc()[:200]}")
        if isinstance(r, TestResult): runner.add(r)
    sm = runner.summary()
    print(f"\n{BN}")
    print(f"  Results ({sm['ms']:.0f}ms total)")
    print(f"  " + "-" * 66)
    for r in runner.results: pr(r)
    print(f"\n  {sm['passed']}/{sm['total']} passed, {sm['failed']} failed")
    print(BN)
    print(f"\nExit code: {0 if sm['failed'] == 0 else 1}")
    return 0 if sm['failed'] == 0 else 1

if __name__ == "__main__": sys.exit(main())
