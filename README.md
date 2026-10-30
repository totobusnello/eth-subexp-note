# A finite range where the stated bound's exponential factor sits above 2^n, taking A = 1

Two checkable things about the `SubexponentialSAT` challenge of
[`openai/math`](https://github.com/openai/math): the receipt of a rerun of the official comparator
on the solution, and a recomputation of the stated time bound.

The two differ in what checking them costs. The arithmetic reproduces in seconds with nothing but a
Python interpreter. The comparator run took 3 h 47 min over 12,014 build jobs and needs a Linux host
with Lean, elan and landrun installed, so for most readers the receipt and the raw log are the
practical object, not a rerun of my rerun.

**What this is not.** It is not a refutation of anything, and it does not claim the algorithm is
slow. The finite range below has no asymptotic consequence, and the two reasons why are stated in
section 5. Two conditions are left unestablished and are claimed nowhere here: that the formal
statement is a faithful rendering of k-SAT, and that the unary encoding keeps the input size
polynomial.

## What is in this repository

| | |
|---|---|
| [`paper/eth-subexp-note.pdf`](paper/eth-subexp-note.pdf) | the note itself, three pages, readable on its own; same content as this README with an abstract. Source in [`paper/eth-subexp-note.md`](paper/eth-subexp-note.md), built by [`paper/build.sh`](paper/build.sh) in the same format as this project's other deposit notes |
| [`RECEIPT_2026-10-28.md`](RECEIPT_2026-10-28.md) | the comparator receipt in full, with its limits, the reading of the statement, and a retraction of two earlier errors of mine |
| [`logs/comparator_runs_2026-10-27_28.log`](logs/comparator_runs_2026-10-27_28.log) | raw log of all three runs, 3,862 lines, including the two failures that preceded the success. Verbatim, so the progress lines my own script printed are in Portuguese; everything the toolchain and the comparator emitted is in English, as are the lines that carry the verdict |
| [`scripts/prep_eth_exam.sh`](scripts/prep_eth_exam.sh) | the script that prepared and ran the comparator |
| [`scripts/runtime_scale_crossover.py`](scripts/runtime_scale_crossover.py) | reproduces the crossings, the maximum and the threshold on A; eight self-tests, plus `--plant` |
| [`scripts/runtime_scale_crossover.csv`](scripts/runtime_scale_crossover.csv) | the ratio tabulated in `L = ln(n+16)` |

To reproduce the arithmetic, which needs nothing but a Python interpreter:

```
python3 scripts/runtime_scale_crossover.py
python3 scripts/runtime_scale_crossover.py --plant   # the self-tests must reject a corrupted formula
```

---

## 1. The comparator accepts the solution

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

## 2. Reading the formal statement by hand

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

## 6. Provenance

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

## How to cite, and license

Cite the archived Zenodo record rather than this repository URL:

**https://doi.org/10.5281/zenodo.23820111**

That is the concept DOI, which resolves to the latest version. Each release also has its own version
DOI: [10.5281/zenodo.23821317](https://doi.org/10.5281/zenodo.23821317) for v1.0.1, which added the
PDF, and [10.5281/zenodo.23820112](https://doi.org/10.5281/zenodo.23820112) for v1.0.0. Fields for a
bibliography are in [`CITATION.cff`](CITATION.cff). MIT licence, see [`LICENSE`](LICENSE).

The PDF is also attached to the release, so it can be fetched without unpacking the archive:
`https://github.com/totobusnello/eth-subexp-note/releases/download/v1.0.1/eth-subexp-note.pdf`
