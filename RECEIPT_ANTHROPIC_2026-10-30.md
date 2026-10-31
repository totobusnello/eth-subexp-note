# Receipt: two kernels accept the Anthropic ETH solution

**Verdict: `ANTHROPIC_COMPARATOR_OK`, on 2026-10-30 21:26:27 -03.** Raw log in
[`logs/anthropic_comparator_run_2026-10-30.log`](logs/anthropic_comparator_run_2026-10-30.log),
1,296 lines, sha256 `89482f8a9f23c4591435950d07f36a36c741019b5c879ecc5a4fec40ec664824`.

This is the companion of [`RECEIPT_2026-10-28.md`](RECEIPT_2026-10-28.md), which covered the
`SubexponentialSAT` challenge of `openai/math`. The blog's own Background page records that
Anthropic released a different proof and Lean formalization of a similar result, so a replication
that stops at one of the two is half a replication.

**This run closes the first of the three limits stated in that earlier receipt.** Their
`comparator.json` sets `enable_nanoda: true`, where the `SubexponentialSAT` challenge sets it to
false. So here two independently written kernel implementations check the same proof, which is
precisely what the earlier run could not provide.

> **Notice, at the top on purpose.** The log contains three runs: two dry runs at 20:38 and the
> real run at 20:43:59. The first dry run shows a `jq` syntax error, visible at lines 41–44. That
> was a defect in my own preparation script, fixed before the real run, and it printed nothing that
> fed the verdict. The run that produced the verdict starts at line 97 and shows the theorem names
> listed correctly. An error in the same file as a `PASS` deserves to be pointed at rather than left
> to be found.

## What was measured

| | |
|---|---|
| challenge | the `eth/` directory of [`anthropics/formal-math`](https://github.com/anthropics/formal-math) |
| examined clone | `16a5ce41304fcdaea4e0be7c132e1c361dc26da5`, the commit the blog links |
| sha256 of `comparator.json` | `757e5537ccf47d1946521b0b5fb91a230cdcfd8933dc9ab047710709c15ffa7e` |
| sha256 of `Challenge.lean` | `63f54edafad0b4d1a4184c6279dc2fea4d8b3a6ef39fa04ab7fa72e86bfbb39e` |
| sha256 of `Solution.lean` | `27d304798a6ec294db7fdeee301227b70d72044cb31c85615901a8d728b0b98f` |
| sha256 of `MainResults.lean` | `47f78a9550d95b37d8718dd1ee16ae824da893a5e17c319f737e6d0a5ed24944` |
| project toolchain | `leanprover/lean4:v4.33.1`, theirs, read from `lean-toolchain` |
| comparator | `575674928e239f5bc452aab72d1dd7b0f1326494`, the commit **their** CI pins |
| lean4export | `15f6055e299ad5b89345e533cc2192f4cc00f659`, which checked out revision `b18d673bd29b476466a51a3be1012df2ed322b10` |
| second kernel | `nanoda_lib` @ `68d5ca9db226849b41a6fff59d796ff19d0a8840` |
| sandbox | `landrun` @ `811cfff51ceaf3d9843708aa6d22e9b84ccac8b4` (v0.1.18 pre-release) |
| host | 5 of 8 cores (`systemd-run`, `CPUQuota=500%`), quota verified inside the scope |
| build size | 8,708 jobs for `Challenge`, 9,516 for `Solution` |
| cost | 42 min 28 s of wall clock, end to end |

All four hashes were **recomputed from the files at that commit** on 2026-10-31 and match byte for
byte. Three of the four are also printed by the run itself, at lines 115–117 of the log; the one
for `Solution.lean` is not, so for that one the check against the source is the only anchor, and
that is why it was made.

Note the comparator commit: `575674928e…` is not the `865edc14…` of the earlier receipt. Their CI
pins its own version, and I ran their script rather than substituting mine. The comparator also
downloads and installs `lean-4.34.0-rc1` for its own build, which is a different toolchain from the
`v4.33.1` the project is pinned to; both facts are in the log, at lines 1249 and 1250, with `lean4export` at 1268 and the two
kernels' own commits at 1275.

## The two kernels, verbatim

Lines 1288–1294 of the log, in the order they appear:

```
Running nanoda kernel on solution
nanoda kernel accepts the solution
Running Lean default kernel on solution.
Lean default kernel accepts the solution
Your solution is okay!
PASS comparator.json
All 1 comparator configuration(s) accepted.
```

**The axioms match the permitted set.** The `.json` permits `propext`, `Quot.sound` and
`Classical.choice`. Their `PrintAxioms` script, run before the comparator, gives both declarations:

```
'MainResults.ethIsFalse' depends on axioms: [propext, Classical.choice, Quot.sound]
'MainResults.mainTheorem' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Here, unlike in the earlier receipt, the two declarations that print their axioms **are** the two
the challenge names, so there is no gap between "19 declarations printed this" and "the final
declaration is among them".

## The two `sorry` warnings are not a reservation

The log shows two `declaration uses sorry` warnings, both from `Challenge.lean`, at `12:8` and
`16:8`. That file is the **reference statement**: it states the two theorems without proofs, so the
comparator has something trusted to compare the solution's types against. `Solution.lean` is what
proves them. Their README predicts exactly these two.

A caution about counting them: the warnings appear **four** times in the log, because the build runs
twice, once at step 6 and again inside the comparator at step 8. Four occurrences, two distinct
declarations. I made that mistake first and record it so a reader does not repeat it.

## What this receipt claims

That at the commit and hashes above, the `comparator` of `leanprover/comparator` pinned by their own
CI, under a real sandbox, reported that **both** the `nanoda` kernel and Lean's default kernel accept
the solution for the two declarations the challenge states, `MainResults.ethIsFalse` and
`MainResults.mainTheorem`, and that both use no axiom outside the three permitted. Reproducible by
the procedure in their own README.

**No code of mine did the judging.** The binary is theirs; the sandbox is theirs; the pinned commits
are theirs. I operated their script and recorded what it said.

## Reading the statement, as six checks

A comparator result says nothing about whether the formal statement means what the informal claim
says. For the `SubexponentialSAT` challenge I reported four checks of that kind, one of which I
could not complete. Here the reading is cheaper than there, and the reason is theirs: `Challenge.lean`
is **17 lines** and imports `MainResults.lean` alone, which has **definitions only, no theorem and
no proof**, and imports Mathlib alone. So the whole meaning of both claims fits in 182 readable
lines. Their README puts the same point about their own file: "no machine checks that this file says
what the paper says; the file is kept short so that a reader can check this."

What follows is six checks rather than a verdict. Line numbers are in `MainResults.lean` at the
commit above.

- **Quantifier order.** `MainTheorem` (177–180) is `∃ M, ∃ C, (finite alphabets) ∧ ∀ k n φ, …`. One
  machine and one constant come **before** k, n and the formula, which is what the claim needs. The
  same order appears in `InTime` (100–102) for the ETH side, where the machine and the constant may
  depend on k and δ but not on n.
- **Finiteness of the alphabets.** Both statements carry `∀ i, Finite (M.tm.Γ i)` (101, 178). The
  file states, at 32–34, that Mathlib requires only the *input* stack's alphabet to be finite, and
  that this condition requires every stack alphabet to be finite, "as for a textbook machine". That
  is a hypothesis **stronger** than the library's, in the direction that makes the claim harder, and
  it is the first place I looked for a gap.
- **Input encoding, and this is where the earlier receipt stopped.** In the `SubexponentialSAT`
  statement the encoding is unary and I could not establish what that costs in encoding length. Here
  it is settled by reading `encClauses` (85–87): n is written in unary (`List.replicate n true`),
  and then each clause takes k positions of `Nat.log2 (2 * n) + 1` bits each, which is **binary**.
  So the input is about `n + 1 + m·k·(⌊log₂ 2n⌋ + 1)` bits, polynomial in n and m. The unary part is
  the variable count alone, which is linear, not exponential. The file also states the reason for
  the no-repeated-clause condition in those terms, at 64–68: without it "no time bound in n alone
  could hold", since a machine must pop nearly all of its input. The question I left open there is
  closed here, and not by argument: it is read off the definition.
- **Strength and reach.** `numSat` (130–131) counts the satisfying assignments exactly, and the
  output is that number in n + 1 bits, lowest bit first (`binary`, 135). Counting exactly is at
  least as strong as deciding satisfiability. The Main Theorem covers every k ≥ 1, and the ETH side
  fixes k = 3.
- **Is `ETH` the hypothesis it names?** `ETH := 0 < s 3` (117), with `s k` the infimum over δ of
  those δ admitting a machine (107), `InTime` spelling out "one machine, finite alphabets, one
  constant c, within ⌊c·2^{δn}⌋ steps for every n" (100–102), and `DecidesKSat` requiring a one-bit
  output that is 1 exactly when the formula is satisfiable (92–95). That is the Impagliazzo–Paturi
  form, s₃ > 0, and the file cites it as such. `ETHIsFalse := ¬ ETH` (122), which for a quantity in
  [0, ∞] says s₃ = 0.
- **What the thresholds exclude.** `MainTheorem` requires `1 ≤ k`, `2 ≤ φ.length` and `4 ≤ n`, and
  the file says at 174–176 that nothing is claimed about any other input word, giving the reason for
  each threshold: at n = 2 the factor log log n is 0 and at m = 1 the divisor √(log m) is 0, so in
  both cases the bound would degenerate to one step. Stating one C that serves every m ≥ 2 and
  n ≥ 4, rather than "for all large enough", is the stronger reading of a 2^{O(·)} bound.

## What this reading does not cover, and one limit is theirs by declaration

**I did not read the proof.** `Solution.lean` draws both theorems from `CountedRoute.Main`,
`NamesInOrder.Main` and `Wrap.Main`, and I read none of that development. That is the part the two
kernels checked, and it is the division of labour this whole exercise rests on: kernels for the
proof, a human for the statement.

**The bridge to "algorithm in the usual sense" is outside Lean, and they say so.** The head comment
of `MainResults.lean`, at 36–48, argues that a random-access machine simulates a `Turing.FinTM2`
with a bounded number of operations per step, and that rewriting a formula from the paper's
x₁ … xₙ into the x₀ … x_{n−1} used here is polynomial; from which s₃ = 0 here gives s₃ = 0 in the
usual sense. It then states, at 48: "The simulation and the rewriting are standard facts; **they are
not part of the Lean statements or proofs**." So the kernels certify a theorem about
`TM2ComputableAux`, and the step from there to the hypothesis as complexity theory states it is
prose. That is not a defect hidden in the file; it is a limit written into it, and naming which step
is extra-Lean is more than the earlier challenge did.

**Cost conventions inside the proof.** `Solution.lean` (29–35) states that inside the proof one
operation may cost time polynomial in the bound on the operations, so that in Turing-machine steps
the exponent holds only up to a constant factor, absorbed by the O in their Theorem D (a). Their
argument that this cannot weaken the claim is that the **types** of the two theorems count steps of
a Mathlib Turing machine, and the kernel checks the proofs against those types. I record the
argument; I did not verify the chain it summarises.

## Times, step by step

| step | wall clock |
|---|---|
| `lake exe cache get` (precompiled Mathlib) | 4 min 21 s |
| `lake build` | 28 min 02 s |
| `PrintAxioms` | 10 s |
| comparator + nanoda + landrun, built from pinned commits | 9 min 54 s |
| **total** | **42 min 28 s** |

For comparison, the `SubexponentialSAT` run took 3 h 47 min over 12,014 build jobs. Their README
reports ~8 min for `lake build` on 24 vCPUs; on 5 cores it took 28, which is the ratio one would
expect. Neither run needs special hardware, but both need a Linux host, because `landrun` does.

The gate that runs before anything is built is in the script: it requires the seven tools their CI
needs and, on every run, asks for one deliberately non-existent binary and checks that the
requirement **fails**. `command -v a b c` returns success if *one* of them exists, not if all do,
and that defect once cost a whole run. The proof of the gate is at line 102 of the log.

## What this receipt does not say

It does not say the ETH is false. It says that at the commit and hashes above, two independently
written kernels accept the proof, both declarations use only the three permitted axioms, and a
reading of the 182 lines that define the statements found no mismatch in six respects. The
statement-to-paper question is answered only as far as a reading of those lines can answer it, the
proof development itself I did not read, and the bridge to the usual notion of algorithm is, by
their own statement, outside what Lean checked.
