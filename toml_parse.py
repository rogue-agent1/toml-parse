#!/usr/bin/env python3
"""toml_parse - Minimal TOML parser for config files."""
import sys, re

def parse(text):
    result = {}
    current = result
    path = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        # Table header
        m = re.match(r"^\[([^\]]+)\]$", line)
        if m:
            path = m.group(1).split(".")
            current = result
            for p in path:
                if p not in current: current[p] = {}
                current = current[p]
            continue
        # Key = value
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            current[key] = _parse_value(val)
    return result

def _parse_value(val):
    if val.startswith('"') and val.endswith('"'): return val[1:-1]
    if val.startswith("'") and val.endswith("'"): return val[1:-1]
    if val == "true": return True
    if val == "false": return False
    if val.startswith("["): return _parse_array(val)
    try: return int(val)
    except ValueError:
        try: return float(val)
        except ValueError: return val

def _parse_array(val):
    inner = val[1:-1].strip()
    if not inner: return []
    items = []
    for item in re.split(r",\s*", inner):
        items.append(_parse_value(item.strip()))
    return items

def test():
    text = """
[database]
host = "localhost"
port = 5432
enabled = true

[server]
name = "myapp"
workers = 4
ratio = 3.14
tags = ["web", "api"]
"""
    cfg = parse(text)
    assert cfg["database"]["host"] == "localhost"
    assert cfg["database"]["port"] == 5432
    assert cfg["database"]["enabled"] is True
    assert cfg["server"]["workers"] == 4
    assert cfg["server"]["ratio"] == 3.14
    assert cfg["server"]["tags"] == ["web", "api"]
    print("toml_parse: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: toml_parse.py --test")
