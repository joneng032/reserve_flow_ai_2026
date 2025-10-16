import xml.etree.ElementTree as ET
import re
from collections import defaultdict

import os
ROOT = os.path.dirname(os.path.dirname(__file__))
COV_PATH = os.path.join(ROOT, "backend", "coverage.xml")
DB_PATH = os.path.join(ROOT, "backend", "database.py")

# Parse coverage.xml
if not os.path.exists(COV_PATH):
    raise SystemExit(f"coverage.xml not found at {COV_PATH}")
root = ET.parse(COV_PATH).getroot()
missing_lines = set()
# Find class element with filename 'database.py'
for cls in root.findall('.//class'):
    if cls.get('filename') == 'database.py':
        for line in cls.findall('.//line'):
            num = int(line.get('number'))
            hits = int(line.get('hits'))
            if hits == 0:
                missing_lines.add(num)
        break

# Read database.py and find function defs
funcs = []
if not os.path.exists(DB_PATH):
    raise SystemExit(f"database.py not found at {DB_PATH}")
with open(DB_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, raw in enumerate(lines, start=1):
    m = re.match(r"^\s*def\s+(\w+)\s*\(|^\s*class\s+(\w+)\s*:\s*", raw)
    if m:
        if m.group(1):
            funcs.append((m.group(1), i))
# Add end sentinel
file_end = len(lines)
# Build ranges
func_ranges = []
for idx, (name, start) in enumerate(funcs):
    end = funcs[idx+1][1]-1 if idx+1 < len(funcs) else file_end
    func_ranges.append((name, start, end))

# Count missing lines per function
counts = []
for name, start, end in func_ranges:
    missing = [n for n in missing_lines if start <= n <= end]
    counts.append((name, start, end, len(missing), sorted(missing)))

# Sort by missing count desc
counts.sort(key=lambda x: x[3], reverse=True)

print("Top functions in backend/database.py by number of uncovered lines:\n")
for name, start, end, cnt, misses in counts[:12]:
    print(f"{name}: lines {start}-{end}, missing {cnt} lines")
    if cnt > 0:
        print(f"  sample missing lines: {misses[:6]}")
    print()

print("Total functions analyzed:", len(counts))

# Also print coverage summary for database.py
lines_total = sum(1 for cls in root.findall('.//class') if cls.get('filename') == 'database.py' for _ in cls.findall('.//line'))
lines_covered = lines_total - len(missing_lines)
print(f"database.py total lines reported in coverage.xml: {lines_total}")
print(f"database.py covered lines: {lines_covered}")
print(f"database.py missing lines: {len(missing_lines)}")
