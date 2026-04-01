#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from pss.cli import parse_args

# Test case 1
args = ['-i', '-w', 'hello', './src']
print('Input:', args)
try:
    result = parse_args(args)
    print('Result:', result)
except SystemExit as e:
    print('SystemExit:', e)
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()