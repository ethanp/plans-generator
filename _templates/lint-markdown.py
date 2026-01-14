#!/usr/bin/env python3
"""
Linter for Markdown files to enforce PDF generation rules.

Checks:
- Blank lines before lists
- Proper headers (not bold text)
- Blank lines before tables
- No Unicode characters in code blocks
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class MarkdownLinter:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.errors: List[Tuple[int, str]] = []
        self.lines = file_path.read_text().splitlines()

    def check_blank_line_before_lists(self):
        """Check that lists have a blank line before them."""
        for i, line in enumerate(self.lines, start=1):
            # Check if this line starts a list (bullet or numbered)
            if re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+[.)]\s', line):
                # Check previous line (if exists and not first line)
                if i > 1:
                    prev_line = self.lines[i - 2]  # i is 1-indexed, array is 0-indexed
                    # Allow if previous line is blank or is a list continuation
                    if prev_line.strip() and not re.match(r'^\s*[-*+\d]', prev_line):
                        # Check if it's not a code block continuation
                        if not prev_line.rstrip().endswith('\\'):
                            self.errors.append((
                                i,
                                f"Missing blank line before list (line {i}). "
                                f"Add a blank line before: {line[:50]}"
                            ))

    def check_blank_line_before_tables(self):
        """Check that tables have a blank line before them."""
        for i, line in enumerate(self.lines, start=1):
            # Check if this line is a table row (starts with |)
            if re.match(r'^\s*\|', line):
                # Check previous line (if exists and not first line)
                if i > 1:
                    prev_line = self.lines[i - 2]
                    # Allow if previous line is blank, is a table row, or is a code block
                    if prev_line.strip() and not re.match(r'^\s*\|', prev_line):
                        # Check if it's not a code block continuation
                        if not prev_line.rstrip().endswith('\\'):
                            # Check if previous line is not a code fence
                            if not prev_line.strip().startswith('```'):
                                self.errors.append((
                                    i,
                                    f"Missing blank line before table (line {i}). "
                                    f"Add a blank line before: {line[:50]}"
                                ))

    def check_proper_headers(self):
        """Check that bold text isn't used as headers."""
        for i, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            # Check for bold text patterns that look like headers
            if re.match(r'^\*\*[^*]+\*\*:?\s*$', stripped):
                # Check if it's followed by content (list, paragraph, etc.)
                if i < len(self.lines):
                    next_line = self.lines[i].strip()
                    # If next line is a list or starts content, it should be a header
                    if next_line and (
                        re.match(r'^[-*+\d]', next_line) or
                        (not next_line.startswith('```') and not next_line.startswith('|'))
                    ):
                        self.errors.append((
                            i,
                            f"Bold text used as header (line {i}). "
                            f"Convert to proper header (e.g. ###, depending on the level of the header): {stripped}"
                        ))

    def check_unicode_in_code_blocks(self):
        """Check for Unicode characters in code blocks."""
        in_code_block = False
        code_block_lang = None
        
        for i, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            
            # Track code block state
            if stripped.startswith('```'):
                if in_code_block:
                    in_code_block = False
                    code_block_lang = None
                else:
                    in_code_block = True
                    # Extract language if present
                    lang_match = re.match(r'^```(\w+)', stripped)
                    code_block_lang = lang_match.group(1) if lang_match else None
                continue
            
            # Check for Unicode in code blocks
            if in_code_block:
                # Check for common Unicode characters that cause LaTeX issues
                unicode_patterns = [
                    (r'[✅✓]', 'checkmark'),
                    (r'[├│└]', 'box-drawing'),
                    (r'[→←]', 'arrow'),
                    (r'[^\x00-\x7F]', 'Unicode character'),  # Any non-ASCII
                ]
                
                for pattern, desc in unicode_patterns:
                    if re.search(pattern, line):
                        # Allow in comments or strings that might legitimately have Unicode
                        # But flag it for review
                        self.errors.append((
                            i,
                            f"Unicode character in code block (line {i}): {desc}. "
                            f"Use ASCII alternative. Found in: {line[:50]}"
                        ))
                        break

    def lint(self) -> bool:
        """Run all lint checks. Returns True if no errors."""
        self.check_blank_line_before_lists()
        self.check_blank_line_before_tables()
        self.check_proper_headers()
        self.check_unicode_in_code_blocks()
        return len(self.errors) == 0

    def print_errors(self):
        """Print all errors found."""
        if self.errors:
            print(f"\n❌ Markdown linting errors in {self.file_path}:", file=sys.stderr)
            for line_num, message in self.errors:
                print(f"  Line {line_num}: {message}", file=sys.stderr)
            print(f"\nFound {len(self.errors)} error(s).", file=sys.stderr)
        else:
            print(f"✔️ {self.file_path}: No linting errors", file=sys.stdout)


def main():
    if len(sys.argv) < 2:
        print("Usage: lint-markdown.py <markdown-file> [<markdown-file> ...]", file=sys.stderr)
        sys.exit(1)
    
    files = [Path(f) for f in sys.argv[1:]]
    all_passed = True
    
    for file_path in files:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            all_passed = False
            continue
        
        linter = MarkdownLinter(file_path)
        if not linter.lint():
            all_passed = False
        linter.print_errors()
    
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()

