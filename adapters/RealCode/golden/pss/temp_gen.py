#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from pss.filefinder import FileFinder

def test_case(description, **kwargs):
    finder = FileFinder(**kwargs)
    return list(finder.files())

# Case 3: empty roots
print('Empty roots:')
print(test_case('empty roots', roots=[], recurse=True))

# Case 4: nonexistent root
print('Nonexistent root:')
print(test_case('nonexistent', roots=['/nonexistent_xyz'], recurse=True))

# Case 5: search_extensions empty list vs None (should behave same)
print('search_extensions empty list:')
print(test_case('empty ext', roots=['./test_data'], recurse=False, search_extensions=[]))

# Case 6: ignore_extensions with dot prefix (already covered)
# Case 7: search_patterns with wildcard
print('search_patterns *.py:')
print(test_case('pattern *.py', roots=['./test_data'], recurse=True, search_patterns=['*.py']))

# Case 8: filter_include_patterns with ** glob
print('include pattern src/** :')
print(test_case('include src/**', roots=['./test_data'], recurse=True, filter_include_patterns=['src/**']))

# Case 9: overlapping include/exclude
print('include src/** exclude src/vendor/** :')
print(test_case('include exclude', roots=['./test_data'], recurse=True, filter_include_patterns=['src/**'], filter_exclude_patterns=['src/vendor/**']))

# Case 10: find_only_text_files true (already covered)
# Case 11: ignore_dirs with non-existent dir (should still work)
print('ignore_dirs dummy:')
print(test_case('ignore dummy', roots=['./test_data'], recurse=True, ignore_dirs=['dummy']))

# Case 12: recurse false with subdirectories (already covered)
# Case 13: multiple roots with one empty
print('multiple roots with empty:')
print(test_case('multi roots', roots=['./test_data', './nonexistent_abc'], recurse=False))

# Case 14: search_extensions case sensitivity? (OS dependent)
# Case 15: filter_include_patterns with absolute path (should not match)