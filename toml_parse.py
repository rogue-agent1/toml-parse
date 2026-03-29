#!/usr/bin/env python3
"""toml_parse - TOML parser for configuration files."""
import sys, re

def parse_toml(text):
    result = {}
    current = result
    current_path = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            if line.startswith("[["):
                key = line.strip("[] ")
                parts = key.split(".")
                target = result
                for p in parts[:-1]:
                    target = target.setdefault(p, {})
                if parts[-1] not in target:
                    target[parts[-1]] = []
                target[parts[-1]].append({})
                current = target[parts[-1]][-1]
            else:
                key = line.strip("[] ")
                parts = key.split(".")
                current = result
                for p in parts:
                    current = current.setdefault(p, {})
        elif "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            current[key] = _parse_value(val)
    return result

def _parse_value(val):
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    if val.lower() == "true": return True
    if val.lower() == "false": return False
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner: return []
        items = []
        for item in _split_array(inner):
            items.append(_parse_value(item.strip()))
        return items
    try: return int(val)
    except ValueError:
        try: return float(val)
        except ValueError: return val

def _split_array(s):
    items = []
    depth = 0
    current = []
    in_str = False
    quote_char = None
    for ch in s:
        if not in_str and ch in ('"', "'"):
            in_str = True
            quote_char = ch
            current.append(ch)
        elif in_str and ch == quote_char:
            in_str = False
            current.append(ch)
        elif not in_str and ch == "[":
            depth += 1
            current.append(ch)
        elif not in_str and ch == "]":
            depth -= 1
            current.append(ch)
        elif not in_str and ch == "," and depth == 0:
            items.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        items.append("".join(current))
    return items

def test():
    toml = """
# Config
title = "My App"
debug = true
port = 8080
rate = 3.14

[database]
host = "localhost"
port = 5432
enabled = true

[database.pool]
size = 10
timeout = 30

[[servers]]
name = "alpha"
ip = "10.0.0.1"

[[servers]]
name = "beta"
ip = "10.0.0.2"
"""
    d = parse_toml(toml)
    assert d["title"] == "My App"
    assert d["debug"] == True
    assert d["port"] == 8080
    assert abs(d["rate"] - 3.14) < 0.01
    assert d["database"]["host"] == "localhost"
    assert d["database"]["port"] == 5432
    assert d["database"]["pool"]["size"] == 10
    assert len(d["servers"]) == 2
    assert d["servers"][0]["name"] == "alpha"
    assert d["servers"][1]["ip"] == "10.0.0.2"
    arr = parse_toml('tags = [1, 2, 3]')
    assert arr["tags"] == [1, 2, 3]
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("toml_parse: TOML parser. Use --test")
