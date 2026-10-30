#!/usr/bin/env bash
# prep_eth_exam.sh - prepares and runs leanprover's `comparator` on the open SubexponentialSAT
# challenge of openai/math, under a real sandbox.
#
# WHY ON A LINUX HOST. The solution is third-party code, so the sandbox has to be real. `landrun`
# exists only on Linux; on macOS the comparator falls back to a stub that isolates nothing.
#
# WHY A SECOND BUILD OF THE COMPARATOR. openai/math pins `leanprover/lean4:v4.34.1`, and
# `lean4export` has to match the Lean version exactly, so a comparator built against another
# toolchain does not serve here. One build per version.
#
# THE PROCEDURE IS THEIRS, not invented. The README of `lean/ComparatorChallenges` says: "Install
# comparator, landrun, and lean4export, and make them available on PATH. Then, from lean/:
# lake update && lake exe cache get && lake env comparator ComparatorChallenges/<X>.json".
#
# THIRD-PARTY DATA. The clone lives in its own directory ($BASE/math), this script lives elsewhere,
# and nothing of mine is imported by it.
set -uo pipefail

BASE=/root/eth_exam
LOG="$BASE/prep.log"
CHALLENGE=ComparatorChallenges/SubexponentialSAT.json

mkdir -p "$BASE"
exec >> "$LOG" 2>&1
echo "=============== $(date -Is) step 0: start"

step() { echo "=============== $(date -Is) step $*"; }
die() { echo "STEP FAILED: $*"; echo "RESULT=FAILED_$1"; exit 1; }

export PATH="$HOME/.elan/bin:$PATH"

step 1 "clone of openai/math (~918 MB, third-party data, own directory)"
if [ ! -d "$BASE/math/.git" ]; then
  git clone --depth 1 https://github.com/openai/math.git "$BASE/math" || die 1_clone
else
  echo "  already cloned; sha: $(git -C "$BASE/math" rev-parse --short HEAD)"
fi
echo "  clone sha: $(git -C "$BASE/math" rev-parse HEAD)"
echo "  their toolchain: $(cat "$BASE/math/lean/lean-toolchain")"

step 2 "toolchain via elan (reads their lean-toolchain)"
cd "$BASE/math/lean" || die 2_cd
elan show || die 2_elan
lean --version || die 2_lean

step 3 "lake update (resolves the dependencies of their manifest)"
lake update || die 3_update

step 4 "lake exe cache get (precompiled mathlib; several GB)"
lake exe cache get || die 4_cache

step 5 "build lean4export and comparator AT THEIR VERSION (v4.34.1)"
TC="$(cat "$BASE/math/lean/lean-toolchain")"
CMP="$BASE/comparator-$(echo "$TC" | tr '/:' '__')"
if [ ! -x "$CMP/.lake/build/bin/comparator" ]; then
  [ -d "$CMP/.git" ] || git clone https://github.com/leanprover/comparator.git "$CMP" || die 5_clone
  echo "$TC" > "$CMP/lean-toolchain"
  (cd "$CMP" && lake build lean4export comparator) || die 5_build
fi
# `comparator` lands in `.lake/build/bin`, but `lean4export` is a PACKAGE of it and its binary lands
# in `.lake/packages/lean4export/.lake/build/bin`: two directories, not one. The build reported
# "Built lean4export:exe" and the binary existed; it simply was not where the PATH was looking.
export PATH="$CMP/.lake/build/bin:$CMP/.lake/packages/lean4export/.lake/build/bin:$PATH"

# `command -v a b c` returns success if ONE of the three exists, not if all three do: it is not a
# conjunction. On 2026-10-27 that gate approved a run with `lean4export` OUTSIDE the PATH. The log
# printed two paths where three were expected, the guard did not fire, and the failure resurfaced
# six minutes later inside landrun as "Failed to find binary: lean4export: executable file not
# found in $PATH", without saying which PATH or that the binary existed on disk. Cost: a whole run,
# 34 minutes of clone, dependencies and build, for a verdict that was never a verdict.
require_on_path() {
  local missing=0 b p
  for b in "$@"; do
    if p="$(command -v "$b" 2>/dev/null)"; then
      echo "  $b -> $p"
    else
      echo "  $b -> MISSING FROM PATH"
      missing=$((missing + 1))
    fi
  done
  [ "$missing" -eq 0 ]
}

# The planted offender: a name that exists on no machine. If require_on_path approves it, the gate
# is worthless and the run stops HERE, before spending the comparator, rather than six minutes
# later. This runs on every invocation, before the real check.
if require_on_path comparator no_such_binary_exists_here landrun; then
  echo "GATE FAILURE: require_on_path approved a nonexistent binary"
  die 5_require_on_path_broken
fi
echo "  [gate proof] the planted offender failed, as it should"

require_on_path comparator lean4export landrun || die 5_path

step 6 "the challenge, before running: what is being checked"
cat "$BASE/math/lean/$CHALLENGE"

step 7 "comparator on the challenge (the verdict)"
cd "$BASE/math/lean" || die 7_cd

# THIS STEP RUNS IN A systemd SCOPE WITH AN EXPLICIT CPU QUOTA, and the quota is not optional.
# Earlier runs put this step inside a cgroup capped at `cpu.max 20000 100000`, one fifth of a single
# core, while `lake build` spawns one `lean` process per core and all eight then contend for that
# fifth. Measured: 6 jobs in 30 minutes against a target of 12,014, which projected to roughly ten
# days for a build that takes hours on five cores. Conversely, `systemd-run --scope` with no
# `-p CPUQuota` hands over the whole machine. Verified inside the scope before relying on it:
# `-p CPUQuota=500%` yields `cpu.max 500000 100000` and `nproc` = 5, so `lake` sizes itself to five
# parallel jobs on its own.
QUOTA="${ETH_CPUQUOTA:-500%}"
echo "  CPU quota: $QUOTA, in a systemd scope"
if systemd-run --scope -q -p CPUQuota="$QUOTA" --unit="eth-comparator-$$" \
     lake env comparator "$CHALLENGE"; then
  echo "RESULT=COMPARATOR_OK"
else
  rc=$?
  echo "RESULT=COMPARATOR_RC_$rc"
fi
echo "=============== $(date -Is) step 8: end"
