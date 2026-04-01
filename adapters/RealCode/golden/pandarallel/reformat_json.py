#!/usr/bin/env python3
"""
Reformat JSON test case files to match start.md formatting (4-space indentation,
single-line objects for test cases).
"""
import json
import os
import re

def compact_json_dump(obj, indent=4):
    """
    Dump JSON with indent, but keep each element of the 'cases' array on a single line.
    """
    # First, dump with indentation
    raw = json.dumps(obj, indent=indent, ensure_ascii=False)
    lines = raw.split('\n')
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # If line starts with indent and '{' (start of a case object)
        # We'll look ahead to find the closing brace at same indent level
        if line.strip().startswith('{'):
            # Find the matching closing brace
            start_indent = len(line) - len(line.lstrip())
            j = i
            brace_count = 0
            while j < len(lines):
                brace_count += lines[j].count('{')
                brace_count -= lines[j].count('}')
                if brace_count == 0:
                    break
                j += 1
            # From i to j inclusive is the whole object
            if j > i:
                # Compact lines i..j into a single line
                compact = ''.join(lines[i:j+1]).replace('\n', ' ').replace('  ', ' ')
                # Normalize spaces after colons
                compact = re.sub(r':\s+', ': ', compact)
                output.append(compact)
                i = j + 1
                continue
        output.append(line)
        i += 1
    return '\n'.join(output)

def reformat_file(filepath):
    """Reformat a single JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Use custom compact dump
    # Actually we can use json.dumps with indent=4 and custom separators for cases
    # Let's try to dump the whole structure with indent=4, then post-process cases array
    raw = json.dumps(data, indent=4, ensure_ascii=False)
    # Now we need to make each element of "cases" array compact
    # Find the "cases": [ ... ] section
    lines = raw.split('\n')
    in_cases = False
    case_depth = 0
    result_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('"cases":'):
            in_cases = True
            result_lines.append(line)
            continue
        if in_cases:
            if stripped == '[':
                case_depth += 1
                result_lines.append(line)
                continue
            if stripped == ']':
                case_depth -= 1
                if case_depth == 0:
                    in_cases = False
                result_lines.append(line)
                continue
            if case_depth == 1 and stripped.startswith('{'):
                # This is a case object, we need to compact it
                # Collect all lines until matching '}'
                # But easier: we can just keep the line as is if it's already single line
                # Actually the dumped JSON may have split the case across multiple lines
                # We'll use a different approach: rebuild the whole JSON with custom encoder
                pass

    # Simpler: just dump with indent=4, then use regex to replace newlines within cases array
    # We'll implement a custom encoder that treats dicts inside cases array as compact
    # Let's implement recursively
    def encode_compact(obj, level=0, in_case=False):
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                # Key always string
                items.append(f'{json.dumps(k, ensure_ascii=False)}: {encode_compact(v, level+1, in_case)}')
            inner = ', '.join(items)
            return '{' + inner + '}'
        elif isinstance(obj, list):
            if in_case:
                # compact list
                inner = ', '.join([encode_compact(item, level+1, True) for item in obj])
                return '[' + inner + ']'
            else:
                # multi-line list with indentation
                if not obj:
                    return '[]'
                indent = ' ' * (4 * (level + 1))
                items = []
                for item in obj:
                    items.append(f'{indent}{encode_compact(item, level+1, True)}')
                inner = ',\n'.join(items)
                outer_indent = ' ' * (4 * level)
                return f'[\n{inner}\n{outer_indent}]'
        else:
            return json.dumps(obj, ensure_ascii=False)

    # Determine if we're in a case context
    def encode_full(obj, level=0, in_cases_array=False, in_case=False):
        if isinstance(obj, dict):
            indent = ' ' * (4 * level)
            next_indent = ' ' * (4 * (level + 1))
            items = []
            for k, v in obj.items():
                key_str = json.dumps(k, ensure_ascii=False)
                # Determine if we're now inside a case object
                new_in_case = in_case or (in_cases_array and level == 2)  # heuristic
                val_str = encode_full(v, level + 1, in_cases_array, new_in_case)
                items.append(f'{next_indent}{key_str}: {val_str}')
            inner = ',\n'.join(items)
            return f'{{\n{inner}\n{indent}}}'
        elif isinstance(obj, list):
            if not obj:
                return '[]'
            indent = ' ' * (4 * level)
            next_indent = ' ' * (4 * (level + 1))
            items = []
            for i, item in enumerate(obj):
                # Determine if we're in the cases array
                new_in_cases_array = (in_cases_array or (level == 1 and i == 0))  # hack
                new_in_case = in_case or (new_in_cases_array and level == 2)
                item_str = encode_full(item, level + 1, new_in_cases_array, new_in_case)
                items.append(f'{next_indent}{item_str}')
            inner = ',\n'.join(items)
            return f'[\n{inner}\n{indent}]'
        else:
            return json.dumps(obj, ensure_ascii=False)

    # Let's use a simpler approach: dump with indent=4, then reprocess cases array
    # We'll write a custom encoder that knows the structure
    # Since we know the exact structure, we can manually format
    description = data['description']
    cases = data['cases']

    # Format each case as a single line
    case_lines = []
    for case in cases:
        # Convert case dict to single-line JSON
        case_line = json.dumps(case, ensure_ascii=False, separators=(', ', ': '))
        case_lines.append(case_line)

    # Build final JSON
    lines = [
        '{',
        '    "description": ' + json.dumps(description, ensure_ascii=False) + ',',
        '    "cases": ['
    ]
    for i, case_line in enumerate(case_lines):
        prefix = '        '  # 8 spaces
        lines.append(prefix + case_line + (',' if i < len(case_lines) - 1 else ''))
    lines.append('    ]')
    lines.append('}')

    formatted = '\n'.join(lines)

    # Verify it's valid JSON
    parsed = json.loads(formatted)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted)

    print(f"Reformatted {filepath}")

def main():
    test_cases_dir = os.path.join(os.path.dirname(__file__), 'tests', 'test_cases')
    for filename in os.listdir(test_cases_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(test_cases_dir, filename)
            reformat_file(filepath)

if __name__ == '__main__':
    main()