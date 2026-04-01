"""
Command-line interface for PSS.
"""
import argparse
import sys
from typing import List, Optional

from .utils import get_file_extensions


def parse_args(args: Optional[List[str]] = None) -> dict:
    """
    Parse command-line arguments.

    Args:
        args: Argument list (defaults to sys.argv[1:])

    Returns:
        Dictionary of parsed parameters matching test expectations
    """
    parser = argparse.ArgumentParser(
        description="Python Source Search - Intelligent source code search tool",
        add_help=False,  # We'll add help manually to control formatting
    )

    # Pattern and search options
    parser.add_argument(
        'pattern',
        nargs='?',
        help="Search pattern (regex unless --literal is used)",
    )
    parser.add_argument(
        'roots',
        nargs='*',
        default=['.'],
        help="Directories to search (default: current directory)",
    )

    # Case sensitivity
    case_group = parser.add_mutually_exclusive_group()
    case_group.add_argument(
        '-i', '--ignore-case',
        action='store_true',
        help="Case-insensitive search",
    )
    case_group.add_argument(
        '-s', '--smart-case',
        action='store_true',
        help="Smart case: case-sensitive if pattern contains uppercase",
    )

    # Matching modes
    parser.add_argument(
        '-w', '--whole-words',
        action='store_true',
        help="Match whole words only",
    )
    parser.add_argument(
        '-v', '--invert-match',
        action='store_true',
        help="Invert match: select non-matching lines",
    )
    parser.add_argument(
        '--literal',
        action='store_true',
        help="Treat pattern as literal string, not regex",
    )
    parser.add_argument(
        '-m', '--max-match-count',
        type=int,
        help="Stop after N matches per file",
    )

    # Context
    parser.add_argument(
        '-C', '--context',
        type=int,
        default=0,
        help="Show N lines of context before and after matches",
    )

    # File discovery
    parser.add_argument(
        '-f', '--only-find-files',
        action='store_true',
        help="Only find files, don't search content",
    )
    parser.add_argument(
        '-r', '--recurse',
        action='store_true',
        default=True,
        help="Recursively search directories (default: true)",
    )
    parser.add_argument(
        '--no-recurse',
        action='store_false',
        dest='recurse',
        help="Do not recursively search directories",
    )
    parser.add_argument(
        '--textonly',
        action='store_true',
        help="Search only text files",
    )

    # File type filters (language-specific)
    language_extensions = {
        'python': get_file_extensions('python'),
        'cpp': get_file_extensions('cpp'),
        'c': get_file_extensions('c'),
        'java': get_file_extensions('java'),
        'javascript': get_file_extensions('javascript'),
        'typescript': get_file_extensions('typescript'),
        'go': get_file_extensions('go'),
        'rust': get_file_extensions('rust'),
        'ruby': get_file_extensions('ruby'),
        'php': get_file_extensions('php'),
        'swift': get_file_extensions('swift'),
        'kotlin': get_file_extensions('kotlin'),
        'scala': get_file_extensions('scala'),
        'html': get_file_extensions('html'),
        'css': get_file_extensions('css'),
        'markdown': get_file_extensions('markdown'),
        'json': get_file_extensions('json'),
        'yaml': get_file_extensions('yaml'),
        'xml': get_file_extensions('xml'),
        'shell': get_file_extensions('shell'),
        'perl': get_file_extensions('perl'),
        'lua': get_file_extensions('lua'),
        'sql': get_file_extensions('sql'),
        'r': get_file_extensions('r'),
        'matlab': get_file_extensions('matlab'),
        'fortran': get_file_extensions('fortran'),
        'haskell': get_file_extensions('haskell'),
        'elixir': get_file_extensions('elixir'),
        'erlang': get_file_extensions('erlang'),
        'clojure': get_file_extensions('clojure'),
        'groovy': get_file_extensions('groovy'),
        'dart': get_file_extensions('dart'),
        'objective-c': get_file_extensions('objective-c'),
        'pascal': get_file_extensions('pascal'),
        'vb': get_file_extensions('vb'),
        'fsharp': get_file_extensions('fsharp'),
        'ocaml': get_file_extensions('ocaml'),
        'racket': get_file_extensions('racket'),
        'scheme': get_file_extensions('scheme'),
        'prolog': get_file_extensions('prolog'),
        'ada': get_file_extensions('ada'),
        'coffeescript': get_file_extensions('coffeescript'),
        'vimscript': get_file_extensions('vimscript'),
        'tex': get_file_extensions('tex'),
        'latex': get_file_extensions('latex'),
        'plaintext': get_file_extensions('plaintext'),
    }

    # Reserved option strings that cannot be used as language flags
    reserved = {
        'help', 'color', 'no-color', 'json', 'context', 'ignore-case', 'smart-case',
        'whole-words', 'invert-match', 'literal', 'max-match-count', 'only-find-files',
        'recurse', 'no-recurse', 'textonly', 'include-type', 'exclude-type',
        # Short options that might conflict with language names
        'c', 'h', 'i', 'm', 'r', 'v', 'w',
    }

    # Add language flags for non-conflicting languages
    for lang in language_extensions.keys():
        if lang in reserved:
            continue
        parser.add_argument(
            f'--{lang}',
            action='append_const',
            const=lang,
            dest='include_types',
            help=f"Include {lang} files",
        )

    # Special handling for JSON files (conflicts with --json output format)
    parser.add_argument(
        '--json-files',
        action='append_const',
        const='json',
        dest='include_types',
        help="Include JSON files",
    )

    # Include/exclude types (generic)
    parser.add_argument(
        '--include-type',
        action='append',
        dest='include_types',
        help="Include files of specified type",
    )
    parser.add_argument(
        '--exclude-type',
        action='append',
        dest='exclude_types',
        help="Exclude files of specified type",
    )

    # Output formatting
    parser.add_argument(
        '--color',
        action='store_true',
        default=sys.stdout.isatty(),
        help="Force colored output",
    )
    parser.add_argument(
        '--no-color',
        action='store_false',
        dest='color',
        help="Disable colored output",
    )
    parser.add_argument(
        '--json',
        action='store_true',
        dest='json_output',
        help="Output results in JSON format",
    )

    # Help
    parser.add_argument(
        '-h', '--help',
        action='help',
        help="Show this help message and exit",
    )

    # Parse arguments
    parsed = parser.parse_args(args)

    # Convert to dictionary matching test expectations
    result = {
        'pattern': parsed.pattern,
        'roots': parsed.roots,
        'ignore_case': parsed.ignore_case,
        'smart_case': parsed.smart_case,
        'whole_words': parsed.whole_words,
        'invert_match': parsed.invert_match,
        'literal_pattern': parsed.literal,
        'max_match_count': parsed.max_match_count,
        'only_find_files': parsed.only_find_files,
        'include_types': parsed.include_types or [],
        'exclude_types': parsed.exclude_types or [],
        'recurse': parsed.recurse,
        'textonly': parsed.textonly,
        'ncontext_before': parsed.context,
        'ncontext_after': parsed.context,
        'color': parsed.color,
        'json': parsed.json_output,
    }

    # Normalize include_types: remove duplicates, handle language flags
    # Language flags already added via append_const
    # include_type arguments may add duplicates
    if result['include_types']:
        result['include_types'] = list(set(result['include_types']))

    return result


def pss_run(args_dict: dict) -> int:
    """
    Main search function.

    Args:
        args_dict: Dictionary of arguments from parse_args

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # TODO: Implement full search workflow
    # For now, just print a message
    print(f"Searching with args: {args_dict}")
    return 0


if __name__ == '__main__':
    args = parse_args()
    print(args)
    sys.exit(pss_run(args))