#!/usr/bin/env python3
"""toml_parse: Minimal TOML parser."""
import re, sys

def parse(text):
    result = {}
    current = result
    path = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        # Table header
        m = re.match(r"^\[\[(.+?)\]\]$", line)
        if m:
            keys = [k.strip() for k in m.group(1).split(".")]
            current = result
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            if keys[-1] not in current:
                current[keys[-1]] = []
            current[keys[-1]].append({})
            current = current[keys[-1]][-1]
            continue
        m = re.match(r"^\[(.+?)\]$", line)
        if m:
            keys = [k.strip() for k in m.group(1).split(".")]
            current = result
            for k in keys:
                current = current.setdefault(k, {})
            continue
        # Key = Value
        m = re.match(r'^([\w.\-]+)\s*=\s*(.+)$', line)
        if m:
            key, val = m.group(1).strip(), m.group(2).strip()
            current[key] = _parse_value(val)
    return result

def _parse_value(val):
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1].replace('\\n', '\n').replace('\\t', '\t')
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    if val.lower() == "true": return True
    if val.lower() == "false": return False
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner: return []
        return [_parse_value(v.strip()) for v in _split_array(inner)]
    try: return int(val)
    except ValueError: pass
    try: return float(val)
    except ValueError: pass
    return val

def _split_array(s):
    result, depth, current = [], 0, ""
    for c in s:
        if c == "[": depth += 1
        elif c == "]": depth -= 1
        if c == "," and depth == 0:
            result.append(current); current = ""
        else:
            current += c
    if current.strip(): result.append(current)
    return result

def test():
    doc = """
[server]
host = "localhost"
port = 8080
debug = true

[database]
name = "mydb"
max_connections = 100
ratio = 0.75

[[users]]
name = "alice"
role = "admin"

[[users]]
name = "bob"
role = "user"

[nested.deep]
key = "value"
"""
    r = parse(doc)
    assert r["server"]["host"] == "localhost"
    assert r["server"]["port"] == 8080
    assert r["server"]["debug"] is True
    assert r["database"]["name"] == "mydb"
    assert r["database"]["ratio"] == 0.75
    assert len(r["users"]) == 2
    assert r["users"][0]["name"] == "alice"
    assert r["users"][1]["role"] == "user"
    assert r["nested"]["deep"]["key"] == "value"
    # Arrays
    r2 = parse('tags = [1, 2, 3]')
    assert r2["tags"] == [1, 2, 3]
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: toml_parse.py test")
