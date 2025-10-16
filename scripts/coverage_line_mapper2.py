#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
import re
from pathlib import Path


def parse_missing_lines(covxml_path, cov_filename_match):
    tree = ET.parse(covxml_path)
    root = tree.getroot()
    missing = set()
    for cls in root.findall('.//class'):
        filename = cls.get('filename')
        if not filename:
            continue
        if filename.endswith(cov_filename_match) or filename.replace('\\','/').endswith(cov_filename_match):
            for line in cls.findall('.//line'):
                if line.get('hits') == '0':
                    missing.add(int(line.get('number')))
    return sorted(missing)


def find_func_range(source_path, func_name):
    src = Path(source_path).read_text(encoding='utf-8')
    lines = src.splitlines()
    pattern = re.compile(r'^(\s*)def\s+' + re.escape(func_name) + r'\s*\(')
    start = None
    indent = None
    for i, ln in enumerate(lines, start=1):
        m = pattern.match(ln)
        if m:
            start = i
            indent = len(m.group(1))
            break
    if start is None:
        raise SystemExit(f'Function {func_name} not found in {source_path}')

    end = len(lines)
    for j in range(start+1, len(lines)+1):
        ln = lines[j-1]
        m = re.match(r'^(\s*)def\s+', ln)
        if m:
            cand_indent = len(m.group(1))
            if cand_indent <= indent:
                end = j-1
                break
    return start, end


def main():
    if len(sys.argv) != 4:
        print('Usage: coverage_line_mapper2.py <function_name> <coverage_xml> <source_file>')
        raise SystemExit(2)
    func, covxml, source = sys.argv[1], sys.argv[2], sys.argv[3]
    covxml = Path(covxml)
    if not covxml.exists():
        raise SystemExit(f'coverage xml {covxml} not found')
    missing = parse_missing_lines(str(covxml), Path(source).name)
    start, end = find_func_range(source, func)
    in_range = [l for l in missing if start <= l <= end]
    print(f'Function {func} in {source}: lines {start}-{end}')
    print(f'Missing lines inside function: {len(in_range)}')
    if in_range:
        print('Missing lines:', in_range)


if __name__ == '__main__':
    main()
