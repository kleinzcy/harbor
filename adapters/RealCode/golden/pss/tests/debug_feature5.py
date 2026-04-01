#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from test_runner import load_test_cases
from pathlib import Path

cases = load_test_cases(Path('test_cases/feature5_cross_platform.json'))
print('Loaded', len(cases), 'cases')
for i, case in enumerate(cases):
    print(f'Case {i}:')
    print('  input:', case['input'])
    print('  expected:', case['expected_output'])