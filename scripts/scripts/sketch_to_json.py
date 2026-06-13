#!/usr/bin/env python3
"""
SKILL.md → JSON Schema Converter

Usage:
    python scripts/sketch_to_json.py

Outputs:
    experts/<domain>/<name>-perspective/schema.json
"""

import json
import re
from pathlib import Path

def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter

def extract_models(content: str) -> list:
    """Extract core mental models."""
    models = []
    model_section = re.search(r'## 核心心智模型(.*?)(?=##|\Z)', content, re.DOTALL)
    if not model_section:
        return models
    
    # Simple extraction - look for numbered or bulleted items
    text = model_section.group(1)
    items = re.findall(r'(?:^|\n)(?:[-*]|\d+\.) (.*?)(?=\n(?:[-*]|\d+\.)|\Z)', text, re.DOTALL)
    
    for item in items[:7]:  # Max 7 models
        # Extract model name (before first colon or dash)
        name_match = re.match(r'**(.+?)**', item.strip())
        if name_match:
            models.append({
                "name": name_match.group(1),
                "summary": item.strip()[:200],
                "evidence": "",
                "application": "",
                "limitation": ""
            })
    return models

def extract_heuristics(content: str) -> list:
    """Extract decision heuristics."""
    heuristics = []
    heur_section = re.search(r'## 决策启发式(.*?)(?=##|\Z)', content, re.DOTALL)
    if not heur_section:
        return heuristics
    
    text = heur_section.group(1)
    items = re.findall(r'(?:^|\n)(?:[-*]|\d+\.) (.*?)(?=\n(?:[-*]|\d+\.)|\Z)', text, re.DOTALL)
    
    for item in items[:10]:
        heuristics.append({
            "name": item.strip().split('\n')[0][:50],
            "description": item.strip()[:200],
            "scenario": "",
            "example": ""
        })
    return heuristics

def extract_dna(content: str) -> dict:
    """Extract expression DNA."""
    dna = {"style": "", "sentencePattern": "", "attitude": "", "certainty": ""}
    dna_section = re.search(r'## 表达DNA(.*?)(?=##|\Z)', content, re.DOTALL)
    if not dna_section:
        return dna
    
    text = dna_section.group(1)
    # Simple key-value extraction
    for line in text.split('\n'):
        if '风格' in line or 'style' in line.lower():
            dna["style"] = line.split(':')[-1].strip()
        elif '句式' in line or 'sentence' in line.lower():
            dna["sentencePattern"] = line.split(':')[-1].strip()
        elif '态度' in line or 'attitude' in line.lower():
            dna["attitude"] = line.split(':')[-1].strip()
        elif '确定性' in line or 'certainty' in line.lower():
            dna["certainty"] = line.split(':')[-1].strip()
    
    return dna

def extract_limits(content: str) -> list:
    """Extract honest boundaries."""
    limits = []
    limits_section = re.search(r'## 诚实边界(.*?)(?=##|\Z)', content, re.DOTALL)
    if not limits_section:
        return limits
    
    text = limits_section.group(1)
    items = re.findall(r'(?:^|\n)(?:[-*]|\d+\.) (.*?)(?=\n(?:[-*]|\d+\.)|\Z)', text, re.DOTALL)
    limits = [item.strip() for item in items[:5]]
    return limits

def sketch_to_json(sketch_path: Path, output_dir: Path) -> dict:
    """Convert SKILL.md to JSON schema."""
    content = sketch_path.read_text(encoding='utf-8')
    
    frontmatter = extract_frontmatter(content)
    
    # Determine type
    name = frontmatter.get('name', sketch_path.parent.name)
    domain = sketch_path.parent.parent.name  # people or methods
    is_people = domain == 'people'
    
    # Build schema
    schema = {
        "name": name,
        "type": "people" if is_people else "methods",
        "domain": sketch_path.parent.name.replace('-perspective', ''),
        "displayName": frontmatter.get('name', name).replace('-perspective', '').replace('-', ' '),
        "keywords": [],  # Fill from INDEX
        "tags": [],
        "models": extract_models(content),
        "heuristics": extract_heuristics(content),
        "dna": extract_dna(content),
        "limits": extract_limits(content),
        "source": {
            "type": "people" if is_people else "framework",
            "origin": "local",
            "reference": frontmatter.get('name', name)
        },
        "version": "1.0.0"
    }
    
    # Write JSON
    output_path = output_dir / "schema.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return schema

def main():
    base = Path(__file__).parent.parent
    experts_dir = base / "experts"
    
    count = 0
    for sketch_path in experts_dir.rglob("SKILL.md"):
        try:
            output_dir = sketch_path.parent
            sketch_to_json(sketch_path, output_dir)
            count += 1
            print(f"OK {sketch_path.parent.name}")
        except Exception as e:
            print(f"FAIL {sketch_path.parent.name}: {e}")
    
    print(f"\nGenerated {count} JSON schemas")

if __name__ == "__main__":
    main()
