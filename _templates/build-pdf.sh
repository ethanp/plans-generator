#!/bin/bash
#
# PDF Generator for Markdown Documents
# =====================================
# Usage: ./build-pdf.sh document.md
# Output: document.pdf in same directory as input
#
# Prerequisites (one-time setup):
#   brew install pandoc basictex
#   sudo tlmgr update --self
#   sudo tlmgr install collection-fontsrecommended pgf-umlsd lm fontspec \
#     fvextra footnotebackref mdframed needspace zref pagecolor \
#     sourcesanspro sourcecodepro titling ly1 mweights csquotes float \
#     booktabs longtable array
#
# Template: Eisvogel (https://github.com/Wandmalfarbe/pandoc-latex-template)
#   Download and extract to: _templates/Eisvogel-X.X.X/eisvogel.latex
#
# Documents only need minimal frontmatter:
#   ---
#   title: "Your Title"
#   subtitle: "Optional Subtitle"
#   author: "Author Name"
#   date: 2025-12-30
#   ---
#
# All styling (fonts, TikZ, colors) comes from pdf-defaults.yaml
#

set -e

# ============================================================================
# Configuration
# ============================================================================

INPUT="$1"
OUTPUT="${INPUT%.md}.pdf"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Find Eisvogel template (supports versioned folder names)
TEMPLATE=$(find "$SCRIPT_DIR" -name "eisvogel.latex" -type f 2>/dev/null | head -1)

# Shared defaults file with all styling
DEFAULTS="$SCRIPT_DIR/pdf-defaults.yaml"

# ============================================================================
# Validation
# ============================================================================

if [ -z "$INPUT" ]; then
  cat <<-EOF
	Usage: $0 <document.md>

	Example:
	  $0 path/to/design-doc.md
	EOF
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "Error: File not found: $INPUT"
  exit 1
fi

# Lint markdown before building
LINT_SCRIPT="$SCRIPT_DIR/lint-markdown.py"
if [ -f "$LINT_SCRIPT" ]; then
  python3 "$LINT_SCRIPT" "$INPUT" || {
    echo "❌ Markdown linting failed. Fix errors before building PDF."
    exit 1
  }
else
  echo "⚠️  Warning: lint-markdown.py not found, skipping lint check"
fi

if [ -z "$TEMPLATE" ]; then
  echo "Eisvogel template not found. Installing..."
  curl -sL https://github.com/Wandmalfarbe/pandoc-latex-template/releases/latest/download/Eisvogel.tar.gz | tar xz -C "$SCRIPT_DIR"
  TEMPLATE=$(find "$SCRIPT_DIR" -name "eisvogel.latex" -type f 2>/dev/null | head -1)
  if [ -z "$TEMPLATE" ]; then
    echo "Error: Failed to install Eisvogel template"
    exit 1
  fi
  echo "Installed: $TEMPLATE"
fi

if [ ! -f "$DEFAULTS" ]; then
  echo "Error: Defaults file not found: $DEFAULTS"
  exit 1
fi

# Check for pdflatex (required for Computer Modern fonts)
if ! command -v pdflatex &> /dev/null; then
  echo "pdflatex not found. Installing BasicTeX..."
  
  if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [ -f "/opt/homebrew/bin/brew" ]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
  fi
  
  brew install basictex
  
  # Add TeX to PATH for this session
  eval "$(/usr/libexec/path_helper)"
  export PATH="/Library/TeX/texbin:$PATH"
  
  if ! command -v pdflatex &> /dev/null; then
    echo "Error: pdflatex still not found after install. Try restarting your terminal."
    exit 1
  fi
  
  echo "Installing required LaTeX packages..."
  sudo tlmgr update --self
  sudo tlmgr install \
    collection-fontsrecommended pgf-umlsd lm fontspec \
    fvextra footnotebackref mdframed needspace zref pagecolor \
    sourcesanspro sourcecodepro titling ly1 mweights csquotes float \
    booktabs longtable array
  
  echo "LaTeX installation complete."
fi

# ============================================================================
# Build
# ============================================================================

PDF_ENGINE="pdflatex"

echo "Building: $INPUT → $OUTPUT"
echo "Using PDF engine: $PDF_ENGINE"

pandoc "$INPUT" \
  -o "$OUTPUT" \
  --from markdown \
  --template "$TEMPLATE" \
  --metadata-file="$DEFAULTS" \
  --pdf-engine="$PDF_ENGINE"

if [ $? -eq 0 ]; then
  echo "Done: $OUTPUT"
else
  echo "Error producing PDF."
  exit 1
fi
