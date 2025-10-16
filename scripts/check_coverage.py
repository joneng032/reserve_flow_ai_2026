#!/usr/bin/env python3
"""Check coverage XML and enforce minimum threshold.

Usage: python scripts/check_coverage.py path/to/coverage.xml [threshold]
"""
import sys
from pathlib import Path
import xmltodict


def compute_coverage(xml_path: Path):
    if not xml_path.exists():
        print(f'Coverage file not found: {xml_path}')
        return 0.0
    try:
        data = xmltodict.parse(xml_path.read_text())
    except Exception as e:
        print(f'Error parsing coverage XML file: {xml_path}\n{e}')
        return 0.0
    # Navigate to classes -> class -> lines -> line
    cov = data.get('coverage', {})
    packages = cov.get('packages', {}).get('package', [])
    if isinstance(packages, dict):
        packages = [packages]

    lines_total = 0
    lines_covered = 0
    for pkg in packages:
        classes = pkg.get('classes', {}).get('class', [])
        if isinstance(classes, dict):
            classes = [classes]
        for cl in classes:
            lines = cl.get('lines', {}).get('line', [])
            if isinstance(lines, dict):
                lines = [lines]
            for ln in lines:
                lines_total += 1
                if ln.get('@hits') and int(ln.get('@hits')) > 0:
                    lines_covered += 1

    if lines_total == 0:
        return 0.0
    return (lines_covered / lines_total) * 100.0


def main():
    if len(sys.argv) < 2:
        print('Usage: check_coverage.py path/to/coverage.xml [threshold]')
        sys.exit(2)
    xml_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        try:
            threshold = float(sys.argv[2])
        except ValueError:
            print(f'Error: threshold "{sys.argv[2]}" is not a valid number.')
            sys.exit(2)
    else:
        threshold = 80.0
    cov = compute_coverage(xml_path)
    print(f'Backend coverage: {cov:.2f}%')
    if cov < threshold:
        print(f'Coverage {cov:.2f}% is below threshold {threshold}%')
        sys.exit(1)
    print('Coverage threshold met')


if __name__ == '__main__':
    main()
