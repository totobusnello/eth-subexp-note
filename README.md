# Independent replication of both ETH proofs, and a finite range where the openAI bound's exponential factor sits above 2^n

Two Lean proofs were published against the Exponential Time Hypothesis: the `SubexponentialSAT`
challenge of [`openai/math`](https://github.com/openai/math), and a different proof of a similar
result by [`anthropics/formal-math`](https://github.com/anthropics/formal-math). **Both were rerun
here, locally, under the official comparator, and both are accepted.** Receipts and raw logs for
each are in this repository, together with a recomputation of the openAI time bound.

| run | verdict | kernels | receipt |
|---|---|---|---|
| openAI, `SubexponentialSAT` | accepted, 2026-10-28 | Lean's default kernel only (their `.json` sets `enable_nanoda: false`) | [`RECEIPT_2026-10-28.md`](RECEIPT_2026-10-28.md) |
| Anthropic, `eth/` | accepted, 2026-10-30 | **two** — `nanoda` and Lean's default (their `.json` sets `enable_nanoda: true`) | [`RECEIPT_ANTHROPIC_2026-10-30.md`](RECEIPT_ANTHROPIC_2026-10-30.md) |

The second run closes the first of the three limits stated for the first one: it is a check by two
independently written kernel implementations, which the openAI challenge's configuration does not
allow. Section 7 covers it, and the sections numbered 1 to 6 are about the openAI run, unchanged.

The three objects differ in what checking them costs. The arithmetic reproduces in seconds with
nothing but a Python interpreter. The openAI comparator run took 3 h 47 min over 12,014 build jobs;
the Anthropic one took 42 min 28 s on five cores. Both need a Linux host with Lean, elan and
landrun, because `landrun` exists only on Linux, so for most readers the receipts and the raw logs
are the practical object, not a rerun of my reruns.

**What this is not.** Accepting a proof is not endorsing a claim, and nothing here says the ETH is
false or true. It is not a refutation of anything either, and it does not claim the algorithm is
slow: the finite range below has no asymptotic consequence, and the two reasons why are stated in
section 5.

For the **openAI** statement, two conditions are left unestablished and are claimed nowhere here:
that the formal statement is a faithful rendering of k-SAT, and that the unary encoding keeps the
input size polynomial. For the **Anthropic** statement, the second of those is settled by reading
the definitions, and section 7 shows where; what remains outside Lean there is a bridge their own
file declares as such, and that too is in section 7 rather than left for a reader to notice.

## What is in this repository

| | |
|---|---|
| [`paper/eth-subexp-note.pdf`](paper/eth-subexp-note.pdf) | the note itself, three pages, readable on its own; same content as this README with an abstract. Source in [`paper/eth-subexp-note.md`](paper/eth-subexp-note.md), built by [`paper/build.sh`](paper/build.sh) in the same format as this project's other deposit notes |
| [`RECEIPT_2026-10-28.md`](RECEIPT_2026-10-28.md) | the openAI comparator receipt in full, with its limits, the reading of the statement, and a retraction of two earlier errors of mine |
| [`RECEIPT_ANTHROPIC_2026-10-30.md`](RECEIPT_ANTHROPIC_2026-10-30.md) | the Anthropic receipt: two kernels, the full provenance, a reading of the statement as six checks, and the one limit their own file declares to be outside Lean |
| [`logs/comparator_runs_2026-10-27_28.log`](logs/comparator_runs_2026-10-27_28.log) | raw log of all three openAI runs, 3,862 lines, including the two failures that preceded the success. Verbatim, so the progress lines my own script printed are in Portuguese; everything the toolchain and the comparator emitted is in English, as are the lines that carry the verdict |
| [`logs/anthropic_comparator_run_2026-10-30.log`](logs/anthropic_comparator_run_2026-10-30.log) | raw log of the Anthropic run, 1,296 lines, two dry runs and the real one. Same convention: my progress lines are in Portuguese, everything the toolchain emitted is in English. sha256 `89482f8a9f23c4591435950d07f36a36c741019b5c879ecc5a4fec40ec664824` |
| [`scripts/prep_eth_exam.sh`](scripts/prep_eth_exam.sh) | the script that prepared and ran the openAI comparator |
| [`scripts/prep_eth_anthropic.sh`](scripts/prep_eth_anthropic.sh) | the script for the Anthropic run: their procedure, their pinned commits, with the PATH gate proved against a planted offender on every run |
| [`scripts/runtime_scale_crossover.py`](scripts/runtime_scale_crossover.py) | reproduces the crossings, the maximum and the threshold on A; eight self-tests, plus `--plant` |
| [`scripts/runtime_scale_crossover.csv`](scripts/runtime_scale_crossover.csv) | the ratio tabulated in `L = ln(n+16)` |

To reproduce the arithmetic, which needs nothing but a Python interpreter:

```
python3 scripts/runtime_scale_crossover.py
python3 scripts/runtime_scale_crossover.py --plant   # the self-tests must reject a corrupted formula
```

---

## 1. The comparator accepts the openAI solution

On 2026-10-28 the comparator from `leanprover/comparator`, run under a real sandbox, reported that
the Lean kernel accepts the solution for the challenge's own declaration,
`OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat`. Of the solution's declarations
that print their own axiom dependencies, 19 in total, every one declares exactly
`[propext, Classical.choice, Quot.sound]`, the three the challenge permits. That is a statement
about those 19 outputs and not about the whole development: whether the final declaration is among
them needs the log, which I did not check and which is included here.

Three limits of that run, stated so nobody has to find them:

1. It used Lean's default kernel, so it did not provide an independent check from a second kernel
   implementation. The challenge sets `enable_nanoda` to false and the log reads
   `Running Lean default kernel`.
2. The binary is the comparator from `leanprover/comparator` at the commit recorded below, and that
   commit identifies the source rather than the binary I executed.
3. A comparator result says nothing about whether the formal statement means what the informal
   claim says.

## 2. Reading the openAI statement by hand

What follows is four checks rather than a verdict. Three of them found no mismatch; the fourth I
could not complete, and I say where it stops.

- **Quantifier order.** One fixed deterministic machine and fixed constants come before the
  universal quantifier over n and over formulas.
- **Locality of the transition function.** It reads only the tape symbol designated by the current
  state.
- **Strength and reach.** Within the formal definitions, the statement counts satisfying assignments
  exactly, which is at least as strong as deciding satisfiability, and it covers every k at least 2,
  so k = 3 is included.
- **Input encoding (not completed).** The encoding is unary. I did not establish what that costs in
  encoding length. Unary encoding of an integer is in general exponential in its binary length, and
  whether it stays polynomial here depends on the bounds on the encoded integers and on the formula
  size, which I did not check.

## 3. The bound, and the ratio

The stated bound is

    T <= C * (bits+1)^d * 2^(A * runtimeScale(n))
    runtimeScale(n) = n * ln(ln(n+16))^2 / sqrt(ln(n+16))

with C, A and d existential. Everything below concerns the exponential factor alone, taking A = 1.
The polynomial factor and the actual value of A are not determined by the statement, and nothing
here claims either.

Dividing runtimeScale(n) by n leaves

    ratio(n) = ln(L)^2 / sqrt(L),    L = ln(n + 16)

which tends to zero. For any fixed A, that makes the exponent o(n) in the number of variables.
Whether an o(n) exponent contradicts the ETH needs the two conditions named at the top, neither
established nor claimed here.

## 4. The ratio is not monotone, and both crossings are closed-form

What the asymptotics do not show is that ratio(n) starts below 1, rises to a maximum, and falls
back. At A = 1 it crosses 1 twice. Writing u = ln L, the equation ratio = 1 becomes

    u^2 = e^(u/2),   hence   (-u/4) e^(-u/4) = -1/4,   so   L = exp(-4 W(-1/4))

on the two real branches of the Lambert W function:

    ascending crossing    principal branch   n = 49.175096
    descending crossing   branch -1          n ~ 10^2390.2112

At those exact roots the ratio is exactly 1; the printed values are rounded and do not satisfy the
equation exactly. Between the crossings the ratio rises to a maximum of 16/e^2 at L = e^4:

    n ~ 10^23.7117    ratio 2.165    (the maximum)

The maximum needs no numerical search either. Differentiating gives

    d/dL [ ln(L)^2 / sqrt(L) ] = ln(L) * (4 - ln(L)) / (2 * L^(3/2))

which is positive for 1 < L < e^4 and negative beyond, so the only interior maximum is at L = e^4,
where the ratio is 4^2 / e^2 = 16/e^2.

The ascending crossing is written as 49.175096 rather than as a power of ten for readability at
that scale. The `+16` inside the logarithms still matters there: the same equation without it has
its root at n = 65.175096, which is 16 higher, and the original ratio evaluated at that point is
about 1.0458 rather than 1.

So, for A = 1 and for the exponential factor alone, there is a finite range of n in which that
factor sits above 2^n. Since n counts variables and is therefore an integer, the range is n = 50 up
to 10^2390: the crossing falls at 49.175096, so at n = 49 the ratio is still 0.999421 and at n = 50
it is 1.002702.

## 5. Two things that do not follow

- **It does not show the algorithm is slower than exhaustive search.** An upper bound above 2^n says
  nothing about the running time, which may sit far below its own bound. The comparison here is
  between bounds, not between running times.
- **It does not change the asymptotics.** The exponent is o(n) for any fixed A, so a finite range
  cannot bear on an asymptotic statement.

The value of A decides how much of this is visible at all. With A below about e^2/16, roughly 0.46,
the exponential factor stays under 2^n for every n at least 1. With A above 1 the range is wider.
Without A, the effective range is undetermined. The bound on n is not pedantry: at n = 0 the
exponent is A * runtimeScale(0) = 0, so both sides equal 1 and neither is below the other.

## 6. Provenance of the openAI run

    examined clone  openai/math at 7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a
    challenge json  sha256 debbfdc9c01104d2369be80da5180978275106df8b685f693fba7ce7da7c5b19
    challenge lean  sha256 4183b2057cff350d66848215ff7167196dfc20e1891b598fdddea59077a76685
    toolchain       leanprover/lean4:v4.34.1, declared in that repository's lean-toolchain
    comparator      leanprover/comparator @ 865edc14486c3388e9225daa971da8e157488c3e
    lean4export     5a9a355dc6c5fd82b69058d433e2ae2e8dfbf8fe
    sandbox         landrun 0.1.18
    cost            3 h 47 min for the verdict step, 12,014 build jobs

The two challenge hashes can be reproduced from the two files at that commit; I did that on
2026-10-29 and both match byte for byte.

## 7. The Anthropic proof, and two kernels

On 2026-10-30 the same official tooling was run on the other proof: the `eth/` directory of
`anthropics/formal-math`, at commit `16a5ce41304fcdaea4e0be7c132e1c361dc26da5`, the one the blog
links. Verdict `ANTHROPIC_COMPARATOR_OK` in 42 min 28 s on five cores. The full receipt is
[`RECEIPT_ANTHROPIC_2026-10-30.md`](RECEIPT_ANTHROPIC_2026-10-30.md); what follows is what a reader
of this page should not have to open a second file to learn.

**Two kernels, not one.** Their `comparator.json` sets `enable_nanoda: true`, so the comparator
checks the exported proof twice, in two independently written implementations. Lines 1288 to 1294 of
the raw log, verbatim:

```
Running nanoda kernel on solution
nanoda kernel accepts the solution
Running Lean default kernel on solution.
Lean default kernel accepts the solution
Your solution is okay!
PASS comparator.json
All 1 comparator configuration(s) accepted.
```

That is the first of the three limits of section 1 closed. The other two still hold here: the
recorded commits identify sources rather than the binaries executed, and no comparator result speaks
to whether a formal statement means what an informal claim says.

**Both declarations use only the permitted axioms**, and here they are the two the challenge names,
so there is no gap of the kind section 1 had to leave open:

```
'MainResults.ethIsFalse' depends on axioms: [propext, Classical.choice, Quot.sound]
'MainResults.mainTheorem' depends on axioms: [propext, Classical.choice, Quot.sound]
```

**The statement was read by hand, and here that is cheap.** `Challenge.lean` is 17 lines and imports
`MainResults.lean` alone; that file has definitions only, no theorem and no proof, and imports
Mathlib alone. So the entire meaning of both claims fits in 182 readable lines, which is a design
choice of theirs and their README says so: "no machine checks that this file says what the paper
says; the file is kept short so that a reader can check this." Six checks are in the receipt. Two
are worth lifting to this page:

- **The encoding question that section 2 could not close, closes here.** For the openAI statement the
  input encoding is unary and I could not establish what that costs in length. Here `encClauses`
  writes the variable count n in unary but each clause as k positions of `Nat.log2 (2n) + 1` bits,
  which is binary — about `n + 1 + m·k·(⌊log₂ 2n⌋ + 1)` bits in all, polynomial in n and m. The
  unary part is linear, not exponential.
- **The alphabets are finite by a hypothesis stronger than the library's.** Both statements carry
  `∀ i, Finite (M.tm.Γ i)`, and the file notes that Mathlib requires only the input stack's alphabet
  to be finite. The extra condition makes the claim harder to prove, not easier.

**What is outside Lean there, by their own declaration.** The head comment of `MainResults.lean`
argues that a random-access machine simulates their `Turing.FinTM2` with bounded overhead, and that
rewriting a formula between two variable namings is polynomial, so that s₃ = 0 in their sense gives
s₃ = 0 in the usual sense. It then states: "The simulation and the rewriting are standard facts;
they are not part of the Lean statements or proofs." So the kernels certify a theorem about
Mathlib's machine type, and the step to the hypothesis as complexity theory states it is prose.
Naming which step is extra-Lean is more than the other challenge did, and it is the place where a
further reader is most useful.

**I did not read the proof** — `Solution.lean` draws both theorems from three other developments,
and none of that was read here. That is what the two kernels checked. Kernels for the proof, a human
for the statement.

### Provenance of the Anthropic run

    examined clone    anthropics/formal-math at 16a5ce41304fcdaea4e0be7c132e1c361dc26da5
    comparator.json   sha256 757e5537ccf47d1946521b0b5fb91a230cdcfd8933dc9ab047710709c15ffa7e
    Challenge.lean    sha256 63f54edafad0b4d1a4184c6279dc2fea4d8b3a6ef39fa04ab7fa72e86bfbb39e
    Solution.lean     sha256 27d304798a6ec294db7fdeee301227b70d72044cb31c85615901a8d728b0b98f
    MainResults.lean  sha256 47f78a9550d95b37d8718dd1ee16ae824da893a5e17c319f737e6d0a5ed24944
    project toolchain leanprover/lean4:v4.33.1, theirs, read from lean-toolchain
    comparator        575674928e239f5bc452aab72d1dd7b0f1326494, the commit their CI pins
    lean4export       15f6055e299ad5b89345e533cc2192f4cc00f659, at revision b18d673bd29b476466a51a3be1012df2ed322b10
    second kernel     nanoda_lib @ 68d5ca9db226849b41a6fff59d796ff19d0a8840
    sandbox           landrun @ 811cfff51ceaf3d9843708aa6d22e9b84ccac8b4
    build size        8,708 jobs for Challenge, 9,516 for Solution
    cost              42 min 28 s of wall clock on 5 of 8 cores

All four hashes were recomputed from the files at that commit on 2026-10-31 and match byte for byte.
Three of the four are printed by the run itself; the one for `Solution.lean` is not, which is why it
was checked against the source.

## How to cite, and license

Cite the archived Zenodo record rather than this repository URL:

**https://doi.org/10.5281/zenodo.23820111**

That is the concept DOI, which resolves to the latest version. Each release also has its own version
DOI: [10.5281/zenodo.23821421](https://doi.org/10.5281/zenodo.23821421) for v1.0.2,
[10.5281/zenodo.23821317](https://doi.org/10.5281/zenodo.23821317) for v1.0.1, which added the PDF,
and [10.5281/zenodo.23820112](https://doi.org/10.5281/zenodo.23820112) for v1.0.0. Fields for a
bibliography are in [`CITATION.cff`](CITATION.cff). MIT licence, see [`LICENSE`](LICENSE).

**Which version holds what.** Everything up to v1.0.2 covers the openAI run and the arithmetic
alone. The Anthropic replication lands in the next release, so a reader who follows the concept DOI
before that release is archived will find sections 1 to 6 and not section 7; until then, this
repository is ahead of the archive, and this paragraph says so rather than leaving the gap to be
discovered.

The PDF is also attached to each release, so it can be fetched without unpacking the archive:
`https://github.com/totobusnello/eth-subexp-note/releases/download/v1.0.2/eth-subexp-note.pdf`
