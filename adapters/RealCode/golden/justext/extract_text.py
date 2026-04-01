#!/usr/bin/env python3
"""
Command-line script for extracting text from HTML using jusText.
"""

import sys
import argparse

from justext import extract_text, get_available_languages, load_stoplist


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract clean text from HTML using jusText library"
    )
    parser.add_argument(
        "--language",
        "-l",
        default="english",
        help="Language for stopword analysis (default: english)"
    )
    parser.add_argument(
        "--encoding",
        "-e",
        help="Character encoding (auto-detected if not specified)"
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=0,
        help="Minimum paragraph length in characters (default: 0)"
    )
    parser.add_argument(
        "--max-link-density",
        type=float,
        default=0.5,
        help="Maximum link density for content paragraphs (default: 0.5)"
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available languages and exit"
    )
    parser.add_argument(
        "--show-stoplists",
        action="store_true",
        help="Show stopword lists for languages"
    )
    
    args = parser.parse_args()
    
    # Handle list languages option
    if args.list_languages:
        languages = get_available_languages()
        print("Available languages:")
        for lang in sorted(languages):
            print(f"  - {lang}")
        return 0
    
    # Handle show stoplists option
    if args.show_stoplists:
        languages = get_available_languages()
        for lang in sorted(languages):
            try:
                stopwords = load_stoplist(lang)
                print(f"{lang}: {len(stopwords)} stopwords")
                if len(stopwords) > 0:
                    sample = list(stopwords)[:10]
                    print(f"  Sample: {', '.join(sample)}")
            except ValueError as e:
                print(f"{lang}: Error - {e}")
        return 0
    
    # Read HTML from stdin
    html = sys.stdin.read()
    
    # Extract text
    paragraphs = extract_text(
        html=html,
        language=args.language,
        encoding=args.encoding,
        min_paragraph_length=args.min_length,
        max_link_density=args.max_link_density,
    )
    
    # Output only content paragraphs (non-boilerplate)
    content_paragraphs = [p.text for p in paragraphs if not p.is_boilerplate]
    
    # Print paragraphs separated by newlines
    for paragraph in content_paragraphs:
        print(paragraph)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())