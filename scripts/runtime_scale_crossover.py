#!/usr/bin/env python3
"""Where the SubexponentialSAT time bound's exponential factor sits above 2^n.

THE OBJECT. The challenge states the time bound

    T <= C * (bits+1)^d * 2^(A * runtimeScale(n))
    runtimeScale(n) = n * ln(ln(n+16))^2 / sqrt(ln(n+16))

transcribed verbatim from `ComparatorChallenges/SubexponentialSAT.lean`, namespace
`OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement`, where `Real.log` is the natural logarithm.
Dividing runtimeScale(n) by n leaves ln(L)^2 / sqrt(L) with L = ln(n+16), which tends to zero, so
the exponent is o(n). What the asymptotics do not say is WHEN: the ratio rises before it falls, and
the point where it crosses 1 is the difference between "the bound is subexponential" and "the bound
is subexponential and that changes something at any scale anyone will ever run".

WHICH VARIABLE THE WORK IS DONE IN. Everything is computed in L = ln(n+16), never in n: the
descending crossing lands near n ~ 10^2390 and no float represents it. The ratio depends on n only
through L, so the whole computation is a one-variable function, and n returns at the end as
log10(n) = L / ln(10), which is the number of decimal digits.

WHAT CANNOT BE CLAIMED, AND WHY. In the statement A is existential (`exists (C A S : R)`) with no
value given, and the time is 2^(A * runtimeScale(n)). Exceeding 2^n requires
A * runtimeScale(n) > n, that is ratio > 1/A. The crossings printed here are for A = 1. Any A > 1
pushes the descending crossing much further out and A < 1 brings it closer; below A = e^2/16, about
0.46, the exponential factor stays under 2^n for every n. Nothing here asserts a value for A.

WHAT A HIGH UPPER BOUND DOES NOT MEAN. An upper bound above 2^n does not say the algorithm runs
slower than exhaustive search. The algorithm may run far below its own bound; the comparison here
is between bounds, not between running times.

Implementation note: no dependency beyond the standard library, on purpose, so that re-running this
needs nothing but a Python interpreter. Run `--plant` to see the self-tests reject a corrupted
transcription of the formula.
"""
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "runtime_scale_crossover.csv")
LN10 = math.log(10.0)
# Module-level on purpose: leg 4 requires the crossing to fall INSIDE this table, so the table the
# self-test checks has to be the same table `main` publishes.
L_TABLE = [10, 20, 55, 100, 200, 500, 1000, 2000, 5000, 5504, 1e4, 1e5, 1e6, 1e9, 1e12]
TARGETS = (1.0, 0.5, 0.1)
# Two decimals on purpose, and leg 5 enforces it. The descending crossing is at 10^2390.21; printed
# as an integer exponent it reads 10^2390, and at exactly 10^2390 the ratio is 1.00002, which is
# still above 1. Rounding a threshold in the wrong direction moves the claim to a point where it is
# false, and the error leaves no visible trace.
FMT_EXPO = ",.2f"
PREC_EXPO = 2


def lambert_W(x, guess):
    """W(x) by Newton's method, on whichever branch `guess` selects.

    The crossing equation has a closed form. With u = ln L, the equation (ln L)^2 = sqrt(L) becomes
    u^2 = e^(u/2), that is 2 ln u = u/2, that is ln u = u/4, whose solution is u = -4 W(-1/4).
    Hence L = exp(-4 W(-1/4)).

    And the part that matters: -1/4 lies in (-1/e, 0), where the Lambert W function has TWO real
    branches. So the equation has TWO crossings:

        W0   (principal branch) -> L = 4.177077  -> n = e^L - 16 = 49.175096   (ASCENDING)
        W-1  (lower branch)     -> L = 5503.6647 -> log10(n) = 2390.2112       (DESCENDING)

    At both the ratio is exactly 1.000000000000000.
    """
    w = guess
    for _ in range(300):
        e = math.exp(w)
        w -= (w * e - x) / (e * (1 + w))
    return w


def closed_form_crossings():
    """Both crossings of the ratio through 1, in closed form."""
    L_asc = math.exp(-4 * lambert_W(-0.25, -0.3))
    L_desc = math.exp(-4 * lambert_W(-0.25, -2.0))
    return L_asc, L_desc


def publishable_exponent(L):
    """log10 of a crossing, rounded UP at the precision being published.

    Up, not to nearest, and the difference is not cosmetic. The claim is "from this n on the ratio
    stays below the target", so the printed label has to fall on the side where that is true. The
    descending crossing is at 10^2390.2112; to nearest at two decimals that is 10^2390.21, which is
    below the crossing, where the ratio is still 1.0000001 and the claim is still false. Rounded up
    it reads 10^2390.22 and the claim holds. Any threshold published at finite precision has this
    problem, and the rounding direction is the cure.
    """
    f = 10.0 ** PREC_EXPO
    return math.ceil((L / LN10) * f) / f


def runtime_scale(n, shift=16.0):
    """The Lean definition, pointwise, for n that fits in a float.

    `shift` is the constant 16 of the statement. It is a parameter only so that `--plant` can
    corrupt it without rebinding the function name.
    """
    L = math.log(n + shift)
    return n * (math.log(L)) ** 2 / math.sqrt(L)


def ratio_of_L(L):
    """runtimeScale(n)/n as a function of L = ln(n+16), where the arithmetic is numerically sane."""
    return (math.log(L)) ** 2 / math.sqrt(L)


def crossing(target, L_start, L_end=1e12, iters=300):
    """The least L from which the ratio stays below `target`, by bisection.

    Requires a bracket: ratio(L_start) > target > ratio(L_end). Returns None when the bracket does
    not hold, because bisection on an invalid bracket still returns a number, and a silent wrong
    number is worse than no number.
    """
    if not (ratio_of_L(L_start) > target > ratio_of_L(L_end)):
        return None
    a, b = L_start, L_end
    for _ in range(iters):
        m = (a + b) / 2.0
        if ratio_of_L(m) > target:
            a = m
        else:
            b = m
    return b


def maximum():
    """The L at which the ratio peaks, by log-uniform sweep plus local refinement."""
    grid = [10.0 ** (i / 200.0) for i in range(200, 1400)]
    L_best = max(grid, key=ratio_of_L)
    a, b = L_best / 2, L_best * 2
    for _ in range(200):
        m1, m2 = a + (b - a) / 3, b - (b - a) / 3
        if ratio_of_L(m1) < ratio_of_L(m2):
            a = m1
        else:
            b = m2
    return (a + b) / 2


def selftests(plant=False):
    """Eight legs, before any number is printed. Each one can fail on its own."""
    f = []

    # Leg 0: the transcription matches the Lean definition, checked by hand at two points.
    # n=0: runtimeScale = 0 * ... = 0, whatever the rest evaluates to.
    if abs(runtime_scale(0) - 0.0) > 1e-12:
        f.append(f"leg 0: runtimeScale(0) = {runtime_scale(0)}, expected exactly 0")
    # n=100 by hand: L=ln(116)=4.753590, ln(L)=1.558899, squared=2.430166, sqrt(L)=2.180273,
    #                100 * 2.430166 / 2.180273 = 111.4621...
    expected = 100 * (math.log(math.log(116.0))) ** 2 / math.sqrt(math.log(116.0))
    if abs(runtime_scale(100) - expected) > 1e-9 or not (111.0 < expected < 112.0):
        f.append(f"leg 0: runtimeScale(100) = {runtime_scale(100)}, by hand it is ~111.46")

    # Leg 1: runtimeScale(n)/n and the ratio in L are the same function, so the two routes have to
    # agree wherever both are computable.
    for n in (10, 1000, 10 ** 6, 10 ** 15):
        via_n = runtime_scale(n) / n
        via_L = ratio_of_L(math.log(n + 16.0))
        if abs(via_n - via_L) > 1e-12 * max(1.0, abs(via_n)):
            f.append(f"leg 1: at n={n} the two routes disagree: {via_n} vs {via_L}")

    # Leg 2: the ratio TENDS TO ZERO, which is what makes the bound subexponential. Without this
    # the statement would not bear on the ETH at all, and the rest of this measurement would have
    # no subject.
    if not ratio_of_L(1e12) < 1e-3:
        f.append(f"leg 2: ratio at L=1e12 is {ratio_of_L(1e12)}, expected ~0 (o(n) requires it)")
    if not (ratio_of_L(1e6) < ratio_of_L(1e5) < ratio_of_L(1e4)):
        f.append("leg 2: the ratio is not decreasing in the tail, where the analysis assumes it is")

    # Leg 3: the ratio RISES before it falls. Were it monotonically decreasing, the crossing would
    # be trivial and this file would have no subject. This leg checks the fact that motivates it.
    L_max = maximum()
    if not (ratio_of_L(L_max) > ratio_of_L(10.0) and ratio_of_L(L_max) > ratio_of_L(1e4)):
        f.append(f"leg 3: L={L_max:.4g} is not a local maximum of the ratio")
    if not ratio_of_L(L_max) > 2.0:
        f.append(f"leg 3: the maximum of the ratio is {ratio_of_L(L_max):.4f}, expected > 2")
    # Leg 3b: the CLOSED FORM of the maximum, which needs no numerical search and can be checked by
    # hand. Differentiating (ln L)^2 / sqrt(L) and setting it to zero gives ln L = 4, so L* = e^4
    # and the maximum is 4^2 / e^2 = 16/e^2 = 2.1653645... The numerical search is thus checked
    # against a DERIVED value rather than against itself, so a bug in maximum() can no longer pass
    # by agreeing with itself. The tolerance is loose on purpose: what is checked is that the search
    # landed at the right point, not the precision of the refinement.
    L_closed = math.e ** 4
    max_closed = 16.0 / math.e ** 2
    # Leg 3c: BOTH crossings against the closed form in Lambert W. This leg exists because of an
    # error none of the others could catch. crossing() starts its search AT THE MAXIMUM, so by
    # construction it only ever finds the descending branch, and a claim of the form "above 2^n for
    # every n" would survive every other leg while being false from n=1 to n=49. The blind spot is
    # structural, not careless: the two crossings are the two real branches of the SAME function,
    # and a one-sided search sees one of them.
    L_asc, L_desc = closed_form_crossings()
    for name, L_f in (("ascending", L_asc), ("descending", L_desc)):
        if abs(ratio_of_L(L_f) - 1.0) > 1e-12:
            f.append(f"leg 3c: at the closed-form {name} crossing (L={L_f:.6f}) the ratio is "
                     f"{ratio_of_L(L_f):.15f}, expected 1")
    if not (ratio_of_L(L_asc * 0.99) < 1.0 < ratio_of_L(L_asc * 1.01)):
        f.append("leg 3c: the ascending crossing is not a crossing of 1 (the ratio should be BELOW "
                 "1 before it and above 1 after)")
    L_bisection = crossing(1.0, L_start=maximum())
    if L_bisection is None or abs(L_bisection - L_desc) > 1e-3:
        f.append(f"leg 3c: bisection gives L={L_bisection}, the closed form gives L={L_desc:.6f}")
    if abs(L_max - L_closed) > 1e-3:
        f.append(f"leg 3b: the search gives L*={L_max:.6f}, the closed form gives "
                 f"e^4={L_closed:.6f}")
    if abs(ratio_of_L(L_max) - max_closed) > 1e-9:
        f.append(f"leg 3b: the measured maximum is {ratio_of_L(L_max):.10f}, the closed form gives "
                 f"16/e^2={max_closed:.10f}")

    # Leg 4 (negative): the crossing has to fall INSIDE the range the published table covers.
    # Without this leg the script would approve a table that, by accident, did not contain the
    # crossing, and the note would publish "crosses at 10^N" from a table in which no row shows the
    # transition. Checked in both directions: some row has ratio > 1 and some row has ratio < 1.
    above = [L for L in L_TABLE if ratio_of_L(L) > 1.0]
    below = [L for L in L_TABLE if ratio_of_L(L) < 1.0]
    if not above or not below:
        f.append(f"leg 4: the table does not contain the crossing of the ratio through 1 "
                 f"({len(above)} row(s) above, {len(below)} below) - the published crossing would "
                 f"not be visible in the artefact that grounds it")

    # Leg 5: the label `main` PRINTS has to satisfy the target AT THE POINT IT NAMES. This leg
    # formats the exponent exactly as main does, reads back what came out, and requires the target
    # to hold there. Legs 0 to 4 check the ARITHMETIC and none of them checks the LABEL, which is
    # the gap a wrong published number came through once.
    L_max_p5 = maximum()
    for target in TARGETS:
        L_cross = crossing(target, L_start=L_max_p5)
        if L_cross is None:
            continue
        expo = publishable_exponent(L_cross)
        r = ratio_of_L(expo * LN10)
        if r >= target:
            f.append(f"leg 5: the published label 10^{expo} does NOT satisfy ratio < {target}; "
                     f"there the ratio is {r:.7f}. Formatting {FMT_EXPO!r} lost the claim while "
                     f"rounding")

    if plant:
        # The planted offender replaces the statement's constant 16 by 1.5. The ratio changes and
        # leg 0 has to catch it, because leg 0 is the only one comparing against a value computed
        # by hand.
        print("  [--plant] the line(s) below are from the PLANTED OFFENDER (constant 16 -> 1.5), "
              "not from the real run", file=sys.stderr)
        bad = runtime_scale(100, shift=1.5)
        if abs(bad - expected) <= 1e-9:
            print("  [--plant] GATE FAILURE: the offender passed leg 0", file=sys.stderr)
            return ["the offender passed"]
        print(f"  [--plant] the offender failed leg 0 ({bad:.4f} against {expected:.4f} expected), "
              f"as it should", file=sys.stderr)
        return []
    return f


def main():
    plant = "--plant" in sys.argv
    f = selftests(plant=plant)
    if f:
        print("FAILURE (runtime_scale_crossover): the self-tests failed, no number is printed:")
        for x in f:
            print(f"  - {x}")
        return 1
    if plant:
        return 0

    L_max = maximum()
    rows = []
    for L in L_TABLE:
        rows.append({"L_ln_n": f"{L:.6g}", "log10_n": f"{L / LN10:.6g}",
                     "ratio_runtimeScale_over_n": f"{ratio_of_L(L):.6f}",
                     "below_2^n_when_A_is_1": "yes" if ratio_of_L(L) < 1 else "no"})
    cross = {}
    for target in TARGETS:
        cross[target] = crossing(target, L_start=L_max)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["L_ln_n", "log10_n", "ratio_runtimeScale_over_n",
                                           "below_2^n_when_A_is_1"])
        w.writeheader()
        w.writerows(rows)

    print("  self-tests: 8 legs OK (transcription, two routes, ratio->0, unimodality, maximum = "
          "16/e^2 at L=e^4, BOTH crossings in Lambert W, crossing inside the table, published "
          "label satisfies the target)")
    L_asc, L_desc = closed_form_crossings()
    print("  TWO CROSSINGS, the two real branches of L = exp(-4 W(-1/4)), ratio exactly 1:")
    print(f"    ascending   (W0):  L={L_asc:.6f}  ->  n = {math.exp(L_asc) - 16:.6f}  "
          f"-- below 1 from n=1 to n=49, so the bound is already under 2^n there")
    print(f"    descending  (W-1): L={L_desc:.4f}  ->  n ~ 10^{L_desc / LN10:{FMT_EXPO}}")
    print("  CARE WHEN QUOTING: between the two the ratio is > 1, outside them it is < 1. No "
          "statement about 'every n' is true, and a high upper bound does NOT make the algorithm "
          "slow.")
    print(f"  MAXIMUM of the ratio: {ratio_of_L(L_max):.4f} at L={L_max:.4g}, that is "
          f"n ~ 10^{L_max / LN10:.0f}")
    for target, L in cross.items():
        if L is None:
            print(f"  ratio < {target}: NO VALID BRACKET - no number is published")
            continue
        expo = publishable_exponent(L)
        # The digit count of 10^e is floor(e)+1, never round(e): with e=2390.22 it is 2391.
        print(f"  ratio < {target:<4}: from L={L:.5g} on, that is n ~ 10^{expo:{FMT_EXPO}} "
              f"({math.floor(expo) + 1:,} decimal digits)")
    print(f"  artefact: {OUTPUT}")
    print("  REMINDER: A is existential in the statement. These crossings are for A = 1; A > 1 "
          "pushes them further out, and nothing here asserts the value of A.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
