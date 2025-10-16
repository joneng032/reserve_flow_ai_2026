#!/usr/bin/env python3
"""
coverage_line_mapper.py

Usage:
  py -3 scripts/coverage_line_mapper.py <function_name> <source_path> [coverage_xml]

Prints the uncovered line numbers from coverage.xml that fall inside the function's range
in the given source file. If coverage_xml is omitted it defaults to coverage.xml in repo root.
"""
import sys
import xml.etree.ElementTree as ET
import re
from pathlib import Path


def parse_coverage_xml(coverage_xml_path, source_relpath):
    tree = ET.parse(coverage_xml_path)
    root = tree.getroot()
    missing_lines = set()
    # coverage.py XML: <packages><package><classes><class filename="..."> with <lines><line number="..." hits="0"/>
    for cls in root.findall('.//class'):
        filename = cls.get('filename')
        if not filename:
            continue
        # Normalize path separators
        if filename.replace('/', '\\').endswith(source_relpath.replace('/', '\\')) or filename.endswith(source_relpath):
            for line in cls.findall('.//line'):
                if line.get('hits') == '0':
                    missing_lines.add(int(line.get('number')))
    return sorted(missing_lines)


def find_function_range(source_path, function_name):
    src = Path(source_path).read_text(encoding='utf-8')
    lines = src.splitlines()
    start = None
    indent = None
    pattern = re.compile(r'^(\s*)def\s+' + re.escape(function_name) + r'\s*\(')
    for i, ln in enumerate(lines, start=1):
        m = pattern.match(ln)
        if m:
            start = i
            indent = len(m.group(1))
            break
    if start is None:
        # try method inside class: look for 'def ' prefixed by 4 spaces
        pattern2 = re.compile(r'^(\s*)def\s+' + re.escape(function_name) + r'\s*\(')
        for i, ln in enumerate(lines, start=1):
            m = pattern2.match(ln)
            if m:
                start = i
                indent = len(m.group(1))
                break
    if start is None:
        raise SystemExit(f"Function {function_name} not found in {source_path}")

    # find end: next line that starts with same or lower indentation and 'def ' (function or method)
    end = len(lines)
    func_def_pattern = re.compile(r'^\s*def\s+')
    for j in range(start + 1, len(lines) + 1):
        ln = lines[j - 1]
        if func_def_pattern.match(ln):
            # top-level def found; stop before it
            end = j - 1
            break
        # also stop at next method with same indent (for methods inside class)
        m = re.match(r'^(\s*)def\s+', ln)
        if m:
            cand_indent = len(m.group(1))
            if cand_indent <= indent:
                end = j - 1
                break
    return start, end


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    func = sys.argv[1]
    source = sys.argv[2]
    covxml = sys.argv[3] if len(sys.argv) > 3 else 'coverage.xml'

    cov_path = Path(covxml)
    if not cov_path.exists():
        raise SystemExit(f"coverage xml not found at {covxml}")

    try:
        missing = parse_coverage_xml(covxml, source)
    except Exception as e:
        raise SystemExit(f"Error parsing coverage.xml: {e}")

    try:
        start, end = find_function_range(source, func)
    except SystemExit as e:
        raise
    except Exception as e:
        raise SystemExit(f"Error parsing source file {source}: {e}")

    in_range = [l for l in missing if start <= l <= end]

    print(f"Function {func} in {source}: lines {start}-{end}")
    print(f"Missing lines in coverage.xml inside this function: {len(in_range)}")
    if in_range:
        print("Sample missing lines:", in_range[:20])
    else:
        print("No missing lines found inside this function.")


if __name__ == '__main__':
    main()
