# RESIDUALIZATION.md — Phase 4, Part 9

Independent confirmation of `CONDITIONAL_PREDICTION.md`'s conclusion via a different method: regress the own-solver risk score on the same confound set (linear regression, not logistic — the risk score itself, not the binary label, is the regression target here), take the residual `R = \text{risk} - \hat{\text{risk}}(\text{confounds})`, and test whether this residual — the part of the risk score confounds *cannot* explain — still predicts the cross-solver blindness target.

## Results

| Direction | `R²` of risk `~` confounds | Spearman(`R`, label), pooled | Per-instance AUROC of `R→`label, median (`n` instances) |
|---|---|---|---|
| `R_W = \text{basin} - \widehat{\text{basin}}` `→` CDCL blindness | `0.425` | `+0.087` (`p=3.3×10⁻³⁵`) | **`0.441`** (`n=177`) |
| `R_C = \text{recurrence} - \widehat{\text{recurrence}}` `→` WalkSAT blindness | `0.609` | `−0.022` (`p=0.045`) | **`0.589`** (`n=161`) |

## Interpretation

- **`42.5%`/`60.9%` of the variance in each risk score is already explained by generic confounds alone** — confirming the risk scores are themselves substantially *redundant with* geometric confounds, not independent of them.
- **The residual (confound-independent) component's predictive power is inconsistent and weak**: pooled Spearman correlations are tiny (`0.09`, `−0.02`) — and in one case have the *wrong sign* relative to the hypothesized direction — and neither residual achieves a meaningfully-above-`0.5` per-instance AUROC (`0.441`, `0.589` — the first is actually *below* chance on the median instance, the second only modestly above). **This is not a clean confirmatory signal in either direction.**
- The pooled-vs-per-instance inconsistency for `R_W` (weak positive pooled correlation, `0.089`, vs. below-chance median per-instance AUROC, `0.441`) is itself informative: it suggests whatever pooled correlation exists is driven by **between-instance** variation (the residual happens to be systematically higher or lower across different instances in a way that correlates with instance-level target base rates) rather than genuine **within-instance** ranking ability — exactly the kind of confound Phase 2/3's "instance is the independent unit" discipline was designed to catch, and exactly why this project insists on per-instance metrics rather than pooled ones (`phase2/EXPERIMENT_PROTOCOL.md` §7, reused here).

## Conclusion

**Residualization independently confirms `CONDITIONAL_PREDICTION.md`**: once the risk scores' confound-explainable component is removed, no reliable, properly-scoped (per-instance) predictive signal remains. Two independent methods (a joint conditional model, and a two-stage residualize-then-test procedure) converge on the same answer.
