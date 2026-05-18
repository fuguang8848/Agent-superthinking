"""
Test LLMRouter - list available perspectives
"""
import sys, logging
sys.path.insert(0, 'src')
from super_thinking.core.extended_registry import ExtendedRegistry
from super_thinking.core.llm_router import LLMRouter

logging.basicConfig(level=logging.INFO)

registry = ExtendedRegistry()
registry.discover()

print("Available perspectives:")
for p in registry.list_all():
    print(f"  {p.id}: {p.name}")

print(f"\nTotal: {len(registry.list_all())} perspectives")

print("\nTesting router...")
router = LLMRouter(registry)
result = router.route("build a chrome extension that translates web pages", mode="llm")
print(f"Activated: {result.activated}")
