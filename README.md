# Plans Generator

Convert Markdown design docs to professional PDFs with LaTeX typesetting, TikZ diagrams, and syntax highlighting.

## Quick Start

```bash
./build-pdf.sh path/to/design-doc.md
```

Output: `path/to/design-doc.pdf`

## Features

- **Computer Modern fonts** — Standard academic typography
- **TikZ diagrams** — Architecture diagrams, flowcharts, UML sequence diagrams
- **Syntax highlighting** — All major languages
- **Title page** — Professional cover with customizable colors
- **Table of contents** — Auto-generated
- **Internal links** — Clickable cross-references

## Document Setup

Add minimal frontmatter to your Markdown:

```yaml
---
title: "Your Design Doc Title"
subtitle: "Optional Subtitle"
author: "Your Name"
date: 2025-01-01
---
```

All styling (fonts, colors, TikZ styles) is inherited from `_templates/pdf-defaults.yaml`.

## Prerequisites

The build script auto-installs dependencies on first run:

- **Homebrew** (macOS package manager)
- **Pandoc** (document converter)
- **BasicTeX** (LaTeX distribution)
- **Eisvogel template** (PDF styling)

Interactive password input required for `tlmgr install` (LaTeX packages).

## Documentation

See the [full guide (Markdown)](00-pdf-generation.md) or [example PDF output](00-pdf-generation.pdf).

The guide covers:

- TikZ diagram examples and available styles
- Table formatting tips
- Troubleshooting common issues
- Unicode character handling

## File Structure

```
plans-generator/
  _templates/
    Eisvogel-3.3.0/
      eisvogel.latex      # LaTeX template
    build-pdf.sh          # Build script
    pdf-defaults.yaml     # Shared styling
  00-pdf-generation.md    # Full documentation
  README.md               # This file
```

## License

MIT

