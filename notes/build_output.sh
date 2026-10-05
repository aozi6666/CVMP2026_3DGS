#!/usr/bin/env bash
# Build SynGS paper and overwrite output/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> [1/4] pdflatex (pass 1)"
pdflatex -interaction=nonstopmode main

echo "==> [2/4] bibtex"
bibtex main

echo "==> [3/4] pdflatex (pass 2)"
pdflatex -interaction=nonstopmode main

echo "==> [4/4] pdflatex (pass 3)"
pdflatex -interaction=nonstopmode main

mkdir -p output
cp -f main.pdf main.log main.aux main.bbl main.blg main.out output/

echo "DONE. PDF -> $ROOT/output/main.pdf"
