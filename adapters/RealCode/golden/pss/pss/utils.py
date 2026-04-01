"""
Utility functions for cross-platform support and performance optimizations.
"""
import sys
from pathlib import PureWindowsPath, PurePosixPath


def istextfile(bytes_data: bytes, blocksize: int = 512) -> bool:
    """
    Detect if the given bytes represent a text file.

    Examines the first `blocksize` bytes for null characters and control characters
    typical of binary files. Returns True if the data appears to be text.

    Args:
        bytes_data: Bytes to examine
        blocksize: Number of bytes to examine (default 512)

    Returns:
        True if text, False if binary
    """
    # Use a slice to avoid copying if bytes_data is large
    data = bytes_data[:blocksize]
    # Empty data is considered text
    if not data:
        return True

    # Check for null bytes
    if b'\x00' in data:
        return False

    # Count control characters that aren't common in text (tab, newline, carriage return, form feed)
    text_controls = b'\t\n\r\x0c'
    for byte in data:
        # Control characters are bytes < 32 (space)
        if byte < 32 and byte not in text_controls:
            return False

    return True


def tostring(data) -> str:
    """
    Convert data to string, handling both bytes and str inputs.

    Args:
        data: bytes or str

    Returns:
        str decoded with UTF-8 if bytes, otherwise str unchanged
    """
    if isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            # Fall back to system default encoding
            return data.decode(sys.getdefaultencoding(), errors='replace')
    elif isinstance(data, str):
        return data
    else:
        raise TypeError(f"Expected bytes or str, got {type(data).__name__}")


def decode_colorama_color(color_str: str) -> str:
    """
    Parse a comma-separated Colorama color/style string into ANSI escape codes.

    Supported colors: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    Supported styles: DIM, NORMAL, BRIGHT, RESET_ALL
    Backgrounds: prefix with "BACK_" (e.g., BACK_RED)

    Args:
        color_str: Comma-separated string like "RED,WHITE,BOLD"

    Returns:
        ANSI escape sequence string
    """
    # Import colorama locally to avoid dependency if not needed
    try:
        from colorama import Fore, Back, Style
    except ImportError:
        # If colorama not available, return empty string
        return ""

    # Map color strings to colorama constants
    color_map = {
        'BLACK': Fore.BLACK,
        'RED': Fore.RED,
        'GREEN': Fore.GREEN,
        'YELLOW': Fore.YELLOW,
        'BLUE': Fore.BLUE,
        'MAGENTA': Fore.MAGENTA,
        'CYAN': Fore.CYAN,
        'WHITE': Fore.WHITE,
        'BACK_BLACK': Back.BLACK,
        'BACK_RED': Back.RED,
        'BACK_GREEN': Back.GREEN,
        'BACK_YELLOW': Back.YELLOW,
        'BACK_BLUE': Back.BLUE,
        'BACK_MAGENTA': Back.MAGENTA,
        'BACK_CYAN': Back.CYAN,
        'BACK_WHITE': Back.WHITE,
        'DIM': Style.DIM,
        'NORMAL': Style.NORMAL,
        'BRIGHT': Style.BRIGHT,
        'RESET_ALL': Style.RESET_ALL,
    }

    parts = color_str.split(',')
    result = []
    for part in parts:
        part = part.strip()
        if part in color_map:
            result.append(color_map[part])
        elif part == 'BOLD':
            # Alias for BRIGHT
            result.append(Style.BRIGHT)
        else:
            # Unknown color/style, ignore
            continue

    return ''.join(result)


def normalize_path(path: str, platform: str) -> str:
    """
    Normalize a path for the given platform.

    On Windows: converts backslashes to forward slashes and normalizes separators.
    On Linux/Unix: collapses multiple slashes and removes trailing slashes.

    Args:
        path: Path string to normalize
        platform: 'windows' or 'linux' (or 'posix')

    Returns:
        Normalized path string
    """
    if platform.lower() == 'windows':
        # Use pathlib to normalize Windows path
        # PureWindowsPath normalizes backslashes and removes redundant separators
        normalized = str(PureWindowsPath(path))
        # Convert backslashes to forward slashes for consistency
        return normalized.replace('\\', '/')
    else:
        # POSIX path normalization
        # Use pathlib for POSIX
        normalized = str(PurePosixPath(path))
        return normalized


def get_file_extensions(language: str) -> list[str]:
    """
    Get list of file extensions for a programming language.

    Args:
        language: Language name (e.g., 'python', 'cpp', 'javascript')

    Returns:
        List of extensions with leading dots
    """
    # Mapping of language to extensions
    extension_map = {
        'python': ['.py', '.pyw', '.pyx', '.pxd', '.pxi'],
        'cpp': ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hh', '.hxx', '.h++', '.h'],
        'c': ['.c', '.h'],
        'java': ['.java'],
        'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
        'typescript': ['.ts', '.tsx'],
        'go': ['.go'],
        'rust': ['.rs'],
        'ruby': ['.rb'],
        'php': ['.php'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'scala': ['.scala'],
        'html': ['.html', '.htm'],
        'css': ['.css'],
        'markdown': ['.md', '.markdown'],
        'json': ['.json'],
        'yaml': ['.yml', '.yaml'],
        'xml': ['.xml'],
        'shell': ['.sh', '.bash', '.zsh'],
        'perl': ['.pl', '.pm'],
        'lua': ['.lua'],
        'sql': ['.sql'],
        'r': ['.r', '.R'],
        'matlab': ['.m'],
        'fortran': ['.f', '.for', '.f90', '.f95'],
        'haskell': ['.hs'],
        'elixir': ['.ex', '.exs'],
        'erlang': ['.erl'],
        'clojure': ['.clj', '.cljs', '.cljc'],
        'groovy': ['.groovy'],
        'dart': ['.dart'],
        'objective-c': ['.m', '.mm'],
        'pascal': ['.pas', '.p'],
        'vb': ['.vb'],
        'fsharp': ['.fs', '.fsx', '.fsi'],
        'ocaml': ['.ml', '.mli'],
        'racket': ['.rkt'],
        'scheme': ['.scm', '.ss'],
        'prolog': ['.pl', '.pro'],
        'ada': ['.adb', '.ads'],
        'coffeescript': ['.coffee'],
        'vimscript': ['.vim'],
        'tex': ['.tex'],
        'latex': ['.latex'],
        'plaintext': ['.txt', '.text'],
    }
    return extension_map.get(language.lower(), [])


if __name__ == '__main__':
    # Simple test if run directly
    print("Testing istextfile:")
    print(istextfile(b"Hello\nWorld"))
    print(istextfile(b"\x00\x01PNG"))
    print("Testing tostring:")
    print(repr(tostring(b"Hello")))
    print(repr(tostring("World")))
    print("Testing decode_colorama_color:")
    print(repr(decode_colorama_color("RED,WHITE,BOLD")))
    print("Testing normalize_path:")
    print(normalize_path("C:\\Users\\test\\file.py", "windows"))
    print(normalize_path("/home//user/file.py", "linux"))