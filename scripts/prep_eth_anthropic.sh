#!/usr/bin/env bash
# prep_eth_anthropic.sh - runs the full verification that the CI of `anthropics/formal-math` runs
# on the second ETH proof: the comparator, the nanoda kernel and a real sandbox.
#
# WHY THIS RUN AND NOT ONLY THE OTHER ONE. The blog's Background page records that "Anthropic also
# subsequently released a DIFFERENT proof and Lean formalization (also AI generated) of a similar
# result". There are therefore two proofs to replicate, and the receipt of 2026-10-28 covered one.
# Repository: anthropics/formal-math, directory eth/, at the commit the blog links.
#
# WHAT THIS RUN GIVES THAT THE OTHER COULD NOT. Their `comparator.json` sets
# `enable_nanoda: true`. The SubexponentialSAT challenge of openai/math sets it to false, which is
# why limit number 1 of the earlier receipt reads, verbatim, "It used Lean's default kernel, so it
# did not provide an independent check from a second kernel implementation". Here the comparator
# re-checks the proof in `nanoda`, an independently written kernel. So this run closes that limit
# rather than repeating it.
#
# THE PROCEDURE IS THEIRS, read from the README of eth/ and from their CI script, not invented:
#   cd eth && lake exe cache get && lake build && lake env lean scripts/PrintAxioms.lean
#   and the full check: bash ../.github/scripts/comparator-check.sh   (Linux only)
# Their CI script requires `git go cargo jq lean lake` on the PATH and builds comparator, nanoda
# and landrun at PINNED commits. A Linux host is not optional: `landrun` exists only on Linux, and
# on macOS the comparator falls back to a stub that isolates nothing.
#
# COST THEY REPORT in the README: `lake build` took ~8 min on 24 vCPUs, largest process ~7 GB.
#
# USAGE:  bash prep_eth_anthropic.sh                      # the full run
#         ETH_CHECK_ONLY=1 bash prep_eth_anthropic.sh      # dry run: checks everything, builds nothing
#         ETH_SIMPLE_ONLY=1 bash prep_eth_anthropic.sh     # only the simple route (build + PrintAxioms),
#                                                          # without the comparator and nanoda
# THIRD-PARTY DATA. The clone lives in its own directory ($BASE/formal-math); this script lives
# elsewhere, and nothing of mine is imported by it.
set -uo pipefail

BASE="${ETH_BASE:-$HOME/eth_anthropic}"
COMMIT=16a5ce41304fcdaea4e0be7c132e1c361dc26da5
LOG="$BASE/anthropic.log"
CHECK_ONLY="${ETH_CHECK_ONLY:-0}"
SIMPLE_ONLY="${ETH_SIMPLE_ONLY:-0}"
QUOTA="${ETH_CPUQUOTA:-500%}"

mkdir -p "$BASE"
exec >> "$LOG" 2>&1
echo "=============== $(date -Is) step 0: start (Anthropic proof)"
step() { echo "=============== $(date -Is) step $*"; }
die() { echo "STEP FAILED: $*"; echo "RESULT=FAILED_$1"; exit 1; }

export PATH="$HOME/.elan/bin:$HOME/.cargo/bin:/usr/local/go/bin:$PATH"

step 1 "the seven tools their CI requires, with a planted offender"
require_on_path() {
  local missing=0 b p
  for b in "$@"; do
    if p="$(command -v "$b" 2>/dev/null)"; then echo "  $b -> $p"
    else echo "  $b -> ABSENT FROM PATH"; missing=$((missing + 1)); fi
  done
  [ "$missing" -eq 0 ]
}
# `command -v a b c` returns success if ONE of them exists, not if all do. That defect once passed
# a run with lean4export off the PATH and cost 34 min of clone and build for a non-verdict. So the
# requirement is proved against a deliberately non-existent binary on every run, before anything
# is built: if the offender passes, the script stops.
if require_on_path git no_such_binary_here jq; then
  echo "GATE FAILED: require_on_path accepted a non-existent binary"
  die 1_gate_broken
fi
echo "  [gate proof] the offender failed, as it must"
require_on_path git go cargo jq lean lake landrun || die 1_missing_tool

step 2 "clone of anthropics/formal-math at the commit the blog links"
if [ ! -d "$BASE/formal-math/.git" ]; then
  git clone --filter=blob:none https://github.com/anthropics/formal-math.git "$BASE/formal-math" || die 2_clone
fi
git -C "$BASE/formal-math" fetch -q origin "$COMMIT" 2>/dev/null || true
git -C "$BASE/formal-math" checkout -q "$COMMIT" || die 2_checkout
echo "  requested sha: $COMMIT"
echo "  sha on disk:   $(git -C "$BASE/formal-math" rev-parse HEAD)"
[ "$(git -C "$BASE/formal-math" rev-parse HEAD)" = "$COMMIT" ] || die 2_sha_mismatch

step 3 "what is going to be checked, verbatim"
cd "$BASE/formal-math/eth" || die 3_cd
echo "  their toolchain: $(cat lean-toolchain)"
echo "  sha256 of comparator.json:  $(sha256sum comparator.json | cut -d' ' -f1)"
echo "  sha256 of MainResults.lean: $(sha256sum MainResults.lean | cut -d' ' -f1)"
echo "  sha256 of Challenge.lean:   $(sha256sum Challenge.lean | cut -d' ' -f1)"
echo "  sha256 of Solution.lean:    $(sha256sum Solution.lean | cut -d' ' -f1)"
echo "--- comparator.json ---"
cat comparator.json
echo "  nanoda enabled? $(jq -r '.enable_nanoda' comparator.json)  <<< this is what the openai/math run did not have"
echo "  theorems:"; jq -r '.theorem_names[]' comparator.json | sed 's/^/    /'

step 4 "the CPU quota, verified INSIDE the scope rather than assumed"
echo "  nproc on host: $(nproc)   quota: $QUOTA   nproc in scope: $(systemd-run --scope -q -p CPUQuota="$QUOTA" nproc 2>/dev/null || echo error)"

if [ "$CHECK_ONLY" = "1" ]; then
  echo "ETH_CHECK_ONLY=1: everything checked and NOTHING was built."
  echo "RESULT=DRY_RUN_OK"
  step 9 "end (dry run)"; exit 0
fi

step 5 "lake exe cache get (precompiled Mathlib for v4.33.1)"
systemd-run --scope -q -p CPUQuota="$QUOTA" lake exe cache get || die 5_cache
step 6 "lake build (they measured ~8 min on 24 vCPUs, largest process ~7 GB)"
systemd-run --scope -q -p CPUQuota="$QUOTA" lake build || die 6_build
step 7 "PrintAxioms: both declarations must list the three permitted axioms"
systemd-run --scope -q -p CPUQuota="$QUOTA" lake env lean scripts/PrintAxioms.lean || die 7_axioms

if [ "$SIMPLE_ONLY" = "1" ]; then
  echo "ETH_SIMPLE_ONLY=1: the simple route passed; the comparator and nanoda were NOT run."
  echo "RESULT=SIMPLE_ROUTE_OK"
  step 9 "end (simple route)"; exit 0
fi

step 8 "their FULL check: comparator + nanoda + landrun (the second kernel)"
if systemd-run --scope -q -p CPUQuota="$QUOTA" --unit="eth-anthropic-$$" \
     bash ../.github/scripts/comparator-check.sh; then
  echo "RESULT=ANTHROPIC_COMPARATOR_OK"
else
  rc=$?
  echo "RESULT=ANTHROPIC_COMPARATOR_RC_$rc"
fi
step 9 "end"
