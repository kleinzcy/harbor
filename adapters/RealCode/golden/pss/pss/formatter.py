"""
Output formatting module for search results.
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .utils import decode_colorama_color


class OutputFormatter(ABC):
    """
    Abstract base class for output formatters.
    """

    @abstractmethod
    def start_matches_in_file(self, filename: str) -> None:
        """Called when starting to process matches in a file."""
        pass

    @abstractmethod
    def matching_line(self, matchresult: Dict[str, Any], filename: str) -> None:
        """
        Called for each matching line.

        Args:
            matchresult: Dict with keys 'matching_line', 'matching_lineno',
                         'matching_column_ranges'
            filename: Name of the file
        """
        pass

    @abstractmethod
    def context_line(self, line: str, lineno: int, filename: str) -> None:
        """Called for each context line."""
        pass

    @abstractmethod
    def end_matches_in_file(self, filename: str) -> None:
        """Called when finished processing matches in a file."""
        pass

    @abstractmethod
    def found_filename(self, filename: str) -> None:
        """
        Called when a file is found (for -f/--only-find-files mode).
        """
        pass

    @abstractmethod
    def get_output(self) -> Any:
        """
        Return the formatted output.

        Returns:
            String, dict, or other serializable output
        """
        pass


class DefaultPssOutputFormatter(OutputFormatter):
    """
    Default colored terminal output formatter.
    """

    def __init__(self, colors: bool = True):
        """
        Initialize formatter.

        Args:
            colors: Whether to use ANSI color codes
        """
        self.colors = colors
        self.output_lines: List[str] = []
        self.current_file: Optional[str] = None
        self._setup_colors()

    def _setup_colors(self) -> None:
        """Initialize color codes."""
        if self.colors:
            try:
                import colorama
                # Initialize colorama for Windows support
                colorama.init()
                self.color_filename = decode_colorama_color("CYAN")
                self.color_lineno = decode_colorama_color("GREEN")
                self.color_match = decode_colorama_color("RED")
                self.color_reset = decode_colorama_color("RESET_ALL")
            except ImportError:
                # Fallback to basic ANSI codes
                self.color_filename = "\033[36m"
                self.color_lineno = "\033[32m"
                self.color_match = "\033[31m"
                self.color_reset = "\033[0m"
        else:
            self.color_filename = ""
            self.color_lineno = ""
            self.color_match = ""
            self.color_reset = ""

    def start_matches_in_file(self, filename: str) -> None:
        """Start processing a file."""
        self.current_file = filename
        # Print filename (colored)
        if self.colors:
            self.output_lines.append(
                f"{self.color_filename}{filename}{self.color_reset}"
            )
        else:
            self.output_lines.append(filename)

    def matching_line(self, matchresult: Dict[str, Any], filename: str) -> None:
        """Process a matching line."""
        line = matchresult['matching_line']
        lineno = matchresult['matching_lineno']
        column_ranges = matchresult['matching_column_ranges']

        # Format line with optional match highlighting
        formatted_line = self._format_line(line, lineno, column_ranges, is_match=True)
        self.output_lines.append(formatted_line)

    def context_line(self, line: str, lineno: int, filename: str) -> None:
        """Process a context line."""
        formatted_line = self._format_line(line, lineno, [], is_match=False)
        self.output_lines.append(formatted_line)

    def _format_line(
        self,
        line: str,
        lineno: int,
        column_ranges: List[List[int]],
        is_match: bool,
    ) -> str:
        """
        Format a line for output.

        Args:
            line: Line content
            lineno: Line number (1-based)
            column_ranges: List of [start, end) ranges to highlight
            is_match: Whether this is a matching line (affects prefix)

        Returns:
            Formatted line string
        """
        # Line number prefix
        if self.colors:
            prefix = f"{self.color_lineno}{lineno}:{self.color_reset}"
        else:
            prefix = f"{lineno}:"

        # Apply match highlighting if any column ranges
        if column_ranges and self.colors:
            # Highlight matches within the line
            highlighted = []
            last_pos = 0
            for start, end in sorted(column_ranges):
                if start > last_pos:
                    highlighted.append(line[last_pos:start])
                highlighted.append(f"{self.color_match}{line[start:end]}{self.color_reset}")
                last_pos = end
            if last_pos < len(line):
                highlighted.append(line[last_pos:])
            line_content = ''.join(highlighted)
        else:
            line_content = line

        return prefix + line_content

    def end_matches_in_file(self, filename: str) -> None:
        """End processing a file."""
        self.current_file = None
        # No additional output for default formatter

    def found_filename(self, filename: str) -> None:
        """Output just the filename (for -f mode)."""
        if self.colors:
            self.output_lines.append(
                f"{self.color_filename}{filename}{self.color_reset}"
            )
        else:
            self.output_lines.append(filename)

    def get_output(self) -> str:
        """Return the accumulated output as a string."""
        return '\n'.join(self.output_lines)


class JsonOutputFormatter(OutputFormatter):
    """
    JSON output formatter.
    """

    def __init__(self):
        self.result: Dict[str, Any] = {}
        self.current_file: Optional[str] = None
        self.current_matches: List[Dict[str, Any]] = []

    def start_matches_in_file(self, filename: str) -> None:
        """Start processing a file."""
        self.current_file = filename
        self.current_matches = []

    def matching_line(self, matchresult: Dict[str, Any], filename: str) -> None:
        """Process a matching line."""
        match_data = {
            'line': matchresult['matching_lineno'],
            'content': matchresult['matching_line'],
            'columns': matchresult['matching_column_ranges'],
        }
        self.current_matches.append(match_data)

    def context_line(self, line: str, lineno: int, filename: str) -> None:
        """Context lines are not included in JSON output."""
        pass

    def end_matches_in_file(self, filename: str) -> None:
        """End processing a file."""
        if self.current_file:
            if 'files' not in self.result:
                self.result['files'] = []
            self.result['files'].append({
                'file': self.current_file,
                'matches': self.current_matches.copy(),
            })
        self.current_file = None
        self.current_matches = []

    def found_filename(self, filename: str) -> None:
        """Output just the filename (for -f mode)."""
        if 'files' not in self.result:
            self.result['files'] = []
        self.result['files'].append({
            'file': filename,
            'matches': [],
        })

    def get_output(self) -> str:
        """Return JSON string."""
        if 'files' not in self.result:
            self.result['files'] = []
        return json.dumps(self.result, indent=2)


def format_output(
    formatter_name: str,
    actions: List[Dict[str, Any]],
    colors: bool = False,
) -> Any:
    """
    Convenience function for test runner.

    Args:
        formatter_name: 'default' or 'json'
        actions: List of action dicts with 'type' and other fields
        colors: Whether to use colors (for default formatter)

    Returns:
        Formatted output (string for default, dict for json)
    """
    if formatter_name == 'default':
        formatter = DefaultPssOutputFormatter(colors=colors)
    elif formatter_name == 'json':
        formatter = JsonOutputFormatter()
    else:
        raise ValueError(f"Unknown formatter: {formatter_name}")

    for action in actions:
        action_type = action['type']
        if action_type == 'start_matches_in_file':
            formatter.start_matches_in_file(action['filename'])
        elif action_type == 'matching_line':
            formatter.matching_line(action['matchresult'], action['filename'])
        elif action_type == 'context_line':
            formatter.context_line(
                action['line'],
                action['lineno'],
                action['filename'],
            )
        elif action_type == 'end_matches_in_file':
            formatter.end_matches_in_file(action['filename'])
        elif action_type == 'found_filename':
            formatter.found_filename(action['filename'])
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    output = formatter.get_output()
    if formatter_name == 'json':
        # Parse JSON to match expected output (dict)
        return json.loads(output)
    return output


if __name__ == '__main__':
    # Simple test
    actions = [
        {'type': 'start_matches_in_file', 'filename': 'test.py'},
        {'type': 'matching_line', 'matchresult': {
            'matching_line': 'def test():',
            'matching_lineno': 1,
            'matching_column_ranges': [[0, 3]]
        }, 'filename': 'test.py'},
        {'type': 'end_matches_in_file', 'filename': 'test.py'},
    ]
    print(format_output('default', actions, colors=False))
    print(format_output('json', actions))