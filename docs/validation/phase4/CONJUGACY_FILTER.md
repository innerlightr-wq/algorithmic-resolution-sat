# CONJUGACY_FILTER.md — Phase 4, Part 11

## The strict requirement

A dynamical **conjugacy** between two solvers' search dynamics `T_W` (WalkSAT's Markov-chain state transition) and `T_C` (CDCL's search-tree transition) would require an explicit, well-defined state-space map `h` (invertible, for conjugacy; not necessarily invertible, for semiconjugacy) satisfying `h∘T_W = T_C∘h`. Establishing this would require: (i) formal state spaces for both dynamics, (ii) an explicit candidate `h`, and (iii) evidence that `h` actually intertwines the two transition maps (not just that some downstream summary statistic of each dynamics happens to correlate).

## What this project actually has

None of the above. What exists is: two scalar summary statistics (`basin(y)`, `recurrence(y)`) derived from each solver's *outcome* (which points get found how often across repeated runs), and a cross-prediction AUROC between them and the *other* solver's blind-zone membership. This is several levels of abstraction removed from anything resembling a state-space map between dynamical systems.

## Applying the filter to what was actually found in this phase

The evidentiary situation is now **weaker** than when this question was first raised (Phase 3), not stronger:
- The raw cross-prediction asymmetry (`0.625` vs. `0.526`) — already, on its own, "nowhere near sufficient" per the task's own framing — has been shown in Parts 6–10 to be **substantially explained by generic geometric/instance-level confounds** (coverage mismatch, `|S_I|`, distance-to-other-solver-set, `ε̂`), not by any demonstrated relationship between the two solvers' internal dynamics.
- The one test that could have supported a genuine dynamics-linking claim — whether a risk score retains predictive power after confound adjustment — **failed** (`CONDITIONAL_PREDICTION.md`, `RESIDUALIZATION.md`: paired improvement `≈0` in both directions).
- The "rare solution" alternative (a solver-agnostic accessibility structure both solvers partially sense) — the *closest* of the available interpretations to anything conjugacy-adjacent — is **also not supported** at the within-instance level (`RARE_SOLUTION_TEST.md`).

## Answers to the three questions

1. **Do the current data justify any use of "conjugacy"? No.** Not close. No state-space map was constructed or tested, and the underlying predictive relationship the terminology would have decorated has itself been substantially explained away.
2. **Do they justify "semiconjugacy"? No,** for the same reason — semiconjugacy still requires an explicit map between defined dynamical systems, which was never attempted, and even the weaker aspiration (a documented, robust directional information flow) is not supported after confound control.
3. **The correct language is the weakest defensible option**: **"directional predictive asymmetry, largely explained by shared geometric confounds; no robust evidence of solver-specific dynamical transfer after adjustment."** Where any residual, unadjusted correlation is mentioned at all (e.g. in a limitations section), it should be called exactly that — a raw, confounded correlation — never "shared accessibility structure" or "factor-like relationship" as a settled finding, since Parts 6–10 found those framings not supported either. The single honest positive statement available is much narrower: *"WalkSAT and CDCL blind zones show a modest raw predictive asymmetry that appears to be mostly attributable to a coverage-calibration mismatch between the two solvers' tested budgets, not to an established dynamical relationship."*

## Purpose served

This filter accomplishes exactly what it was commissioned to do: it prevents V2 from reaching for an attractive but unearned dynamical-systems analogy. The honest empirical finding of this phase is a **negative-leaning, confound-explained result**, not a positive discovery of cross-solver structure — `CONJUGACY_FILTER.md` and the Parts 6–10 documents it summarizes should be read together as the reason V2 must not describe the WalkSAT/CDCL relationship in any dynamical-systems-flavored language at all.
