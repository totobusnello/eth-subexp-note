#!/bin/sh
# eth-subexp-note: eth-subexp-note.md -> eth-subexp-note.pdf, in the same format as the other
# deposit notes of this project (STIX Two, 10pt, 1in margins, xurl, numbered sections, ORCID in
# the author line, version and DOI in the date line).
set -eu
cd "$(dirname "$0")"
DOI="10.5281/zenodo.23820111"
VERSION="1.1.0"
pandoc eth-subexp-note.md -o eth-subexp-note.pdf --pdf-engine=xelatex \
  -V title="Independent replication of both ETH proofs, and a finite range where the SubexponentialSAT bound's exponential factor sits above \$2^n\$ with \$A = 1\$" \
  -V author="Luiz Antonio Busnello (Independent Researcher, ORCID 0009-0007-5911-8141)" \
  -V date="Version ${VERSION} · 30 October 2026 · doi:${DOI}" \
  -V geometry:margin=1in -V fontsize=10pt -V mainfont="STIX Two Text" -V mathfont="STIX Two Math" \
  -V colorlinks=true -H header.tex \
  2> build.log || { cat build.log; exit 1; }
# the house gate: a missing glyph is silent in the PDF and loud in the log
grep -i "missing character" build.log && { echo "ABORT: glifo faltando"; exit 1; } || true
printf 'eth-subexp-note.pdf  %s pages\n' "$(pdfinfo eth-subexp-note.pdf | awk '/^Pages/{print $2}')"
