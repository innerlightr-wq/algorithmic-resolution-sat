# Algorithmic Resolution and Solver-Dependent Observational Geometry in SAT Solution Spaces

Elias De Jesus
Independent Researcher
ORCID: 0009-0007-0190-9143

*Draft V2 — built from the frozen four-phase validation record at `sat-algorithmic-resolution-v2-audit-2026-09-28/`. Supersedes and corrects the January 2026 preprint "Algorithmic Resolution and Geometric Distinguishability in SAT Solution Spaces."*

---

## Abstract

The solution space of a satisfiability instance is usually characterized not directly but through the subset of solutions an algorithm happens to find. We formalize this distinction by separating the intrinsic solution space $S_I$ from an algorithm's observed subset $A(I) \subseteq S_I$, and define the empirical resolution $\hat\varepsilon(A,I) = \max_{x \in S_I} \min_{y \in A(I)} d_H(x,y)$, which for nonempty $A(I)$ is exactly the Hausdorff distance $d_{\mathrm{Haus}}(A(I), S_I)$ — a standard quantity, not a new one. Standard Rips-complex persistence stability, specialized here to zero-dimensional homology, bounds how far observed connectivity can drift from true connectivity as a function of $\hat\varepsilon$; we further show this bound's constant is sharp, including in the discrete Hamming cube. We prove coverage and resolution are logically independent via explicit constructions. Empirically, two structurally different SAT solvers — WalkSAT and a CDCL solver (Glucose3) — each show statistically significant, held-out, non-circular prediction of their own eventual blind zones from pre-reveal search dynamics (AUROC $0.658$ and $0.667$ respectively). Our central result: on $349$ paired held-out instances, at matched coverage on the identical solution space, WalkSAT achieves significantly better resolution ($\hat\varepsilon$; paired $p=5.1\times10^{-38}$) while showing $11.6\times$ (95% CI $[9.6,13.3]$) greater apparent fragmentation than CDCL. Neither solver dominates; each preserves a different aspect of the true geometry. We report this as a direct empirical instance of the coverage/resolution independence we prove abstractly, and explicitly retract an initially promising but ultimately confounded cross-solver predictive-transfer finding.

*(228 words)*

---

## 1. Introduction

A satisfiability solver is typically asked one question — is $I$ satisfiable? — and, if the answer is yes, may return one, several, or many satisfying assignments. When a research question concerns the *structure* of the solution space itself (how solutions cluster, how many distinct regions exist, how far apart they sit), that structure is almost never observed directly. It is inferred from whatever subset of solutions the solver happened to produce, under whatever budget it was given, using whatever search strategy it uses internally.

This creates an identification problem that is easy to state and easy to overlook: a structural claim about "the solution space of $I$" is, in practice, a claim about $A(I)$, the specific finite subset an algorithm $A$ returned — not about $S_I \subseteq \{0,1\}^n$, the full set of satisfying assignments. The two can diverge in ways that are not obvious from summary statistics alone. Knowing that an algorithm found, say, 30% of all solutions does not by itself say whether the missing 70% is scattered evenly through the space or concentrated in one geometrically remote region; it does not say whether the found solutions form a single connected structure or several apparently disconnected ones, and if the latter, whether that fragmentation reflects the true geometry of $S_I$ or is an artifact of which solutions happened to be found.

This paper develops a framework for making that identification problem precise, and reports what happens when the framework is applied to two structurally different SAT-solving paradigms — stochastic local search (WalkSAT) and conflict-driven clause learning (CDCL, via Glucose3) — on the same random 3-SAT instances.

**Three distinct quantities.** For an algorithm $A$ observing instance $I$, we distinguish:

1. **Coverage**: $\mathrm{Cov}(A,I) = |A(I)| / |S_I|$ — what fraction of the true solution set was found.
2. **Geometric resolution**: $\hat\varepsilon(A,I)$ — how far, in Hamming distance, the *worst-represented* true solution sits from the nearest found solution. This is the covering radius of $A(I)$ relative to $S_I$, and (Section 3) is exactly the Hausdorff distance between the two sets.
3. **Connectivity fidelity**: whether the connected-component structure of $A(I)$, at any given Hamming-distance threshold, matches that of $S_I$ at the same threshold — or whether it appears more fragmented, or less, than the truth.

The central question this paper answers empirically: **can two algorithms, observing comparable fractions of the same solution space, nevertheless reveal systematically different geometry?** The answer is yes, and the way in which it is yes is itself informative: on $349$ paired held-out instances, at matched coverage, WalkSAT and a CDCL solver trade off in *opposite directions* on resolution and connectivity fidelity. Neither diagnostic alone characterizes "how faithfully" a solver represents $S_I$; both are necessary, and they are not redundant.

This paper is a substantial revision of a January 2026 preprint under the same general topic. That preprint's central mathematical claim — a universal distinguishability threshold at $\varepsilon = d/2$ in arbitrary metric spaces — is false as stated (Section 4 corrects it) and its main quantity, "algorithmic resolution," is a standard Hausdorff-distance construction under new terminology, not a new mathematical object (Section 3). Its empirical evidence for predictable solver blind zones relied on a sampler deliberately biased toward the feature used to predict it, which we show is close to circular (Section 6). We do not repair the January preprint; we replace its architecture with one built from correctly attributed mathematics and non-circular, freeze-before-reveal experiments, validated across two solver paradigms and audited for the confounds that undermined an initially promising cross-solver finding (Section 8).

### 1.1 Contributions

1. A clean separation between the intrinsic geometry of a SAT solution space and the algorithm-dependent geometry of what is actually observed, formalized via $S_I$, $A(I)$, and three logically independent diagnostics (coverage, resolution, connectivity fidelity).
2. Correct attribution of the covering-radius/Hausdorff-distance identity and the connectivity-recovery stability bound this framework relies on — both standard, neither claimed as new — together with one independently verified original result: the recovery bound's constant is sharp, including a construction realized directly in the Hamming cube.
3. A rigorous demonstration, via explicit constructions, that coverage and geometric resolution are logically independent: neither bounds the other without further assumptions on the solution space's geometry.
4. Non-circular, freeze-before-reveal, anti-leakage-verified evidence that both WalkSAT and CDCL search dynamics carry statistically significant held-out information about their own eventual blind zones (AUROC $0.658$ and $0.667$).
5. The paper's central empirical result: at matched coverage, on the same solution space, WalkSAT and CDCL trade off oppositely on resolution and connectivity fidelity — a direct, real-solver realization of the logical independence proved in contribution 3.
6. A fully reported, audited negative result: an initially observed cross-solver predictive-transfer asymmetry does not survive confound control and is retracted rather than presented as a finding.

---

## 2. Related Work

Random-3-SAT solution-space geometry — clustering, freezing, the appearance of well-separated regions before the satisfiability threshold — is established territory (Mézard, Parisi & Zecchina 2002; Achlioptas & Ricci-Tersenghi, STOC 2006). Non-uniformity of local-search and DPLL/CDCL-derived samples relative to the true solution distribution is also well documented, motivating an entire line of work on near-uniform SAT sampling via universal hashing (Chakraborty, Meel & Vardi 2015 and the UniGen family). This paper does not contest that solver sampling bias exists; it asks a different, geometric question — not *whether* a sampler is biased, but *how the specific geometric shape of that bias, measured via covering radius and connectivity, differs between solver paradigms observing the same instance.*

The mathematical machinery — Hausdorff-distance stability of Vietoris–Rips persistent homology — is due to Chazal, de Silva & Oudot (*Persistence Stability for Geometric Complexes*, Geometriae Dedicata, 2014) at the level of bottleneck distance between full persistence diagrams. The sharper, asymmetric, zero-dimensional specialization this paper uses — exploiting that our observed set is literally a subset of the true set, not merely a nearby unrelated point cloud — is a direct corollary of Harker, Kramár, Levanger & Mischaikow's interleaving-based comparison framework (*A Comparison Framework for Interleaved Persistence Modules*, J. Appl. Comput. Topol. 3(1–2):85–118, 2019; arXiv:1801.06725), Proposition 5.6(i). We state this attribution explicitly in Section 5 rather than presenting the bound as original.

---

## 3. Preliminaries

**Definition 1 (SAT instance and solution space).** A Boolean satisfiability instance $I$ over $n$ variables is a formula in conjunctive normal form; its solution space is $S_I = \{x \in \{0,1\}^n : I(x) = \mathrm{true}\}$.

**Definition 2 (Hamming metric).** $d_H(x,y) = |\{i : x_i \neq y_i\}|$; $(\{0,1\}^n, d_H)$ is a metric space.

**Definition 3 (observed set and blind zone).** For algorithm $A$ run on $I$, $A(I) \subseteq S_I$ is the set of solutions returned within its budget; $M_A(I) = S_I \setminus A(I)$ is the blind zone.

**Definition 4 (coverage).** $\mathrm{Cov}(A,I) = |A(I)| / |S_I|$.

**Definition 5 (empirical resolution).**
$$\hat\varepsilon(A,I) = \max_{x \in S_I} \min_{y \in A(I)} d_H(x,y), \qquad A(I) \neq \emptyset.$$

**Proposition 1 (standard metric fact, not new).** For nonempty $A(I) \subseteq S_I$,
$$\hat\varepsilon(A,I) = d_{\mathrm{Haus}}(A(I), S_I).$$
*Proof.* $\hat\varepsilon(A,I)$ is by definition the directed Hausdorff distance $\vec d(S_I, A(I))$. The reverse direction $\vec d(A(I), S_I) = \max_{y \in A(I)} \min_{x \in S_I} d_H(y,x) = 0$, since every $y \in A(I)$ is itself in $S_I$ at distance $0$ (using $A(I) \subseteq S_I$). The symmetric Hausdorff distance is the max of the two directed distances, hence equals $\hat\varepsilon(A,I)$. $\blacksquare$

We retain the domain-facing name "empirical resolution" for $\hat\varepsilon$ — it usefully signals the interpretation (a solver's effective measurement precision) to a SAT audience — but state Proposition 1 first and explicitly: the underlying object is textbook computational geometry, not a contribution of this paper.

**The $A(I) = \emptyset$ case** is handled as a categorical failure flag, not folded into the numeric scale of $\hat\varepsilon$: the directed Hausdorff distance is $+\infty$ under the standard convention when $A(I)$ is empty, and reporting it as a bounded sentinel (as the January preprint did) creates a false unconditional inequality, addressed in Appendix A.

---

## 4. A Corrected Discrete-Space Result

The January preprint's central geometric claim was: in an arbitrary metric space, points at distance $D$ are distinguishable by a measurement of resolution $\varepsilon$ if and only if $\varepsilon < D/2$. This is false in general and specifically false in the Hamming cube. Take $x,y \in \{0,1\}^n$ with $d_H(x,y)=1$ and $\varepsilon=1$: the open ball $B_1(x) = \{z : d_H(x,z)<1\} = \{x\}$ and likewise $B_1(y)=\{y\}$, so the balls are disjoint (the points *are* distinguishable) — yet $\varepsilon=1 \not< D/2 = 0.5$, contradicting the claimed threshold.

The error traces to an implicit midpoint assumption: the proof's forward direction requires a point exactly at distance $D/2$ from both $x$ and $y$, which exists in continuous, geodesic metric spaces but not in the integer-valued, discrete Hamming cube whenever $D$ is odd.

**Theorem 1 (corrected, proved and exhaustively verified).** For $x,y \in \{0,1\}^n$ with $d_H(x,y)=D>0$ and real $\varepsilon>0$:
$$B_\varepsilon(x) \cap B_\varepsilon(y) = \emptyset \iff \varepsilon \le \lceil D/2 \rceil \quad \text{(open balls)},$$
$$\bar B_\varepsilon(x) \cap \bar B_\varepsilon(y) = \emptyset \iff \varepsilon < \lceil D/2 \rceil \quad \text{(closed balls)}.$$

*Proof idea.* The minimum, over $z \in \{0,1\}^n$, of $\max(d_H(x,z), d_H(y,z))$ equals $\lceil D/2 \rceil$ exactly, achieved by splitting the $D$ differing coordinates as evenly as possible; the result follows directly. Full proof and exhaustive verification (45,393 cases, $n=1$–$10$, zero mismatches, including exhaustive coverage for $n\le6$) in Appendix A.

This section is brief by design; the theorem is elementary once correctly stated, and this paper's central contribution lies elsewhere (Sections 5–8).

---

## 5. Coverage and Resolution Are Logically Independent

Neither coverage nor $\hat\varepsilon$ determines the other without further assumptions on $S_I$'s geometry. We exhibit two explicit, verified, parameterized families.

**Family A (high coverage, poor resolution).** For each $n$, let $S_n = \{0^n\} \cup \{\text{weight-1 vectors}\} \cup \{1^n\}$ ($|S_n|=n+2$) and $A_n = S_n \setminus \{1^n\}$. Then $\mathrm{Cov}(A_n,S_n) = (n+1)/(n+2) \to 1$ while $\hat\varepsilon(A_n,S_n) = n-1$, so $\hat\varepsilon/\mathrm{diam} \to 1$ simultaneously — coverage approaching $1$ and resolution approaching the worst possible value at once. A single omitted point, however rare in relative terms, can be arbitrarily geometrically catastrophic.

**Family B (low coverage, good resolution).** For $n=2^m-1$, let $S_n = \{0,1\}^n$ (the full cube) and $A_n$ a perfect binary Hamming code (covering radius exactly $1$, $|A_n| = 2^n/(n+1)$). Then $\mathrm{Cov}(A_n,S_n) = 1/(n+1) \to 0$ while $\hat\varepsilon(A_n,S_n) = 1$, constant. Verified exactly (via syndrome decoding, not brute force) up to $n=63$ ($|A_n| = 2^{57}$).

These are standard coding-theoretic ingredients (perfect codes, covering radius) recombined into an explicit demonstration; the underlying facts are not new, and we attribute them as such (Cohen, Honkala, Litsyn & Lobstein, *Covering Codes*). What the two families jointly establish — that no deterministic inequality can relate $\mathrm{Cov}(A,I)$ and $\hat\varepsilon(A,I)$ without further structural assumptions on $S_I$ — is the theoretical basis for why raw coverage cannot substitute for $\hat\varepsilon$, or vice versa, as a diagnostic of solver fidelity. Section 8 shows this abstract, worst-case divergence is realized concretely by real solvers on real instances.

---

## 6. Connectivity Fidelity and Its Stability Bound

For $S \subseteq \{0,1\}^n$ and threshold $r \ge 0$, let $C_S(r)$ denote the number of connected components of the graph on $S$ with an edge between $p,q$ whenever $d_H(p,q) \le r$ — the zero-dimensional persistence / cluster spectrum of $S$. This function is exactly the connected-component count of the Vietoris–Rips complex of $S$ at scale $r$.

**Known result (Harker, Kramár, Levanger & Mischaikow, 2019, Proposition 5.6(i)), specialized to $H_0$.** For $A \subseteq S$ with $\hat\varepsilon(A,S) = \varepsilon$:

(a) *No false merge, zero slack.* If $x,y \in A$ are connected in $A$'s $r$-cluster graph, they are connected in $S$'s $r$-cluster graph — immediate from $A \subseteq S$ (any chain of points in $A$ is a valid chain in $S$).

(b) *Guaranteed recovery, $+2\varepsilon$.* If $x,y \in S$ are connected in $S$'s $r$-cluster graph, their nearest-$A$ images are connected in $A$'s $(r+2\varepsilon)$-cluster graph.

We state this attribution carefully because the original derivation of this project mistakenly treated it as a new theorem. Harker et al.'s Proposition 5.6(i) — stated for general persistence modules under their $\delta$-approximation hypothesis (word-for-word our $A \subseteq S$, $\delta = \varepsilon$), with their Rips parameter $t$ related to our radius by $r=2t$ — is, once this convention is tracked, exactly claims (a) and (b) above, generalized to all homological dimensions. Restricting to $H_0$ recovers our statement verbatim, including the exact constant $+2\varepsilon$ (Appendix B gives the full translation). We present it here as a citation-grounded application, not a contribution.

**Consequence.** $C_A(r+2\varepsilon) \le C_S(r)$ for all $r$: any apparent fragmentation in the observed set is guaranteed to resolve once the radius is loosened by $2\varepsilon$. We verified this bound directly against $349$ real SAT solution spaces: zero violations across approximately $7{,}000$ (instance, $r$) checks.

**Sharpness (independently verified, narrow-scope original contribution).** The constant $2$ cannot be improved. For any $r,\varepsilon \ge 1$, an explicit four-point construction in $\{0,1\}^{r+2\varepsilon}$ — using three disjoint coordinate blocks to independently realize the worst case on each side of the triangle inequality — achieves $d(a,b) = r+2\varepsilon$ exactly, where $a,b$ are the nearest-$A$ images of two directly $r$-connected points of $S$. Verified across seven $(r,\varepsilon)$ combinations. We did not locate an explicit statement of this sharpness result, in the general metric-space case or the Hamming-cube-specific case, anywhere in the literature searched; we report this as an absence, not as a novelty claim, following our own discipline against inferring novelty from a failed search.

**Exact conditions for naive monotonicity.** The informal claim "$C_A(r) \ge C_S(r)$" (deleting points can only fragment, never merge, connectivity) requires care: an entire $S$-component with no representative in $A$ at all pulls $C_A(r)$ *below* $C_S(r)$, a distinct failure mode (under-representation) from fragmentation. We prove: $C_A(r) \ge C_S(r)$ is guaranteed exactly once $r \ge \varepsilon$ (every $x \in S$ then has a directly-connected nearest neighbor in $A$, ruling out under-representation), and give an explicit counterexample showing this can fail for $r<\varepsilon$. Verified: $877/877$ random-instance checks confirm the $r \ge \varepsilon$ guarantee; zero counterexamples to the failure mode below it.

---

## 7. Experimental Design

**Instances.** $720$ random 3-SAT instances ($360$ train / $360$ test, split by instance), $n \in \{16,18,20\}$, $\alpha \in \{2.5 \text{ (solution-rich)}, 3.5 \text{ (intermediate)}, 4.2 \text{ (near-threshold)}\}$, $40$ instances per $(n,\alpha)$ cell per split, all satisfiable, **no solution cap** (the January preprint's fixed 500-solution cap was found, in an earlier audit phase, to truncate the true solution set itself at low $\alpha$ for $64$–$100\%$ of instances at $n \ge 18$ — a confound removed entirely here by exhaustive enumeration).

**WalkSAT.** Standard random-walk/greedy local search: $K=150$ independent restarts, $\mathrm{max\_flips}=3000$, noise parameter $p=0.5$.

**CDCL.** Glucose3 (Audemard & Simon), accessed via PySAT — a genuine, unmodified, competition-grade CDCL solver (VSIDS branching, first-UIP clause learning, LBD-based aggressive restarts), not a homemade DPLL implementation. Solution enumeration via native blocking-clause iteration. Since Glucose3 exposes no direct RNG seed, independent runs are obtained via a mathematically exact symmetry of the CNF (uniformly random variable relabeling and clause-order shuffling) combined with randomized initial-phase hints — confirmed empirically to produce genuinely different search trajectories and discovery orders across seeds. Primary budget: $R=5$ independent permuted runs, $T=8$ solutions enumerated per run, calibrated (on coverage statistics alone, before any predictive result was examined) to give CDCL a coverage level comparable in order of magnitude to WalkSAT's on the same instances.

**Freeze-before-reveal protocol.** For every predictive experiment, a Stage-A process sees only the CNF formula and the solver's own trajectory (flips/restarts for WalkSAT; permutation seeds, conflicts/decisions/restarts counters for CDCL) and writes its predictions to disk with a SHA-256 hash and UTC timestamp before any ground-truth enumeration occurs; a separate Stage-B process verifies that hash before revealing $S_I$. For the CDCL pipeline, this isolation is additionally enforced by a programmatic runtime guard that raises an error if Stage-A code attempts to open any ground-truth-bearing file path — tested directly to confirm it trips correctly.

**Statistical unit.** The SAT instance, never an individual solution (solutions within one instance are highly dependent). All reported metrics are computed per instance first, then aggregated via median and instance-level bootstrap (5,000 resamples) for confidence intervals, with instance-level permutation tests (1,000 permutations, label-shuffling within each instance) for significance.

---

## 8. Prospective Blind-Zone Prediction

For each solver, a risk score computed *only* from pre-reveal search dynamics is tested against the retrospective blind zone after reveal.

**WalkSAT: `risk_basin`.** For each found solution $y$, $\mathrm{basin}(y)$ counts how many of the $K=150$ restarts converge to $y$; low basin count is hypothesized to predict higher local miss risk.

**CDCL: `risk_cdcl_recurrence`.** No restart concept exists for blocking-clause enumeration; the structural analogue is $\mathrm{recurrence}(y)$, the number of independent permuted search orderings (out of $R=5$) that rediscover $y$.

**Table 1. Held-out blind-zone prediction, test split, touched once.**

| Solver | Predictor | Median AUROC [95% CI] | Median Spearman | Permutation $p$ |
|---|---|---|---|---|
| WalkSAT | `risk_basin` | **0.658** [0.636, 0.685] | 0.252 | 0.000999 |
| WalkSAT | `risk_disc_flips` (failed) | 0.407 | −0.160 | — |
| WalkSAT | Hamming-weight | 0.519 | 0.025 | — |
| WalkSAT | random (sanity) | 0.504 | 0.016 | 0.347 |
| CDCL | `risk_cdcl_recurrence` | **0.667** [0.647, 0.700] | 0.346 | 0.000999 |
| CDCL | `conflicts_to_discovery` (failed) | 0.471 | −0.043 | — |
| CDCL | Hamming-weight | 0.492 | −0.011 | — |
| CDCL | random (sanity) | 0.481 | −0.001 | 0.934 |

Both solvers show a genuine, comparably sized effect (overlapping confidence intervals), robust to stratification by SAT regime, $n$, and $|S_I|$ tercile in both cases (Appendix C). We report the failed predictors — flip/conflict-count-based "harder discovery predicts higher risk" did not hold for either solver — as informative negative sub-results, not as post-hoc-rescued findings. **We claim only that each solver's own dynamics predict its own blind zone**; cross-solver transfer is addressed, and rejected, in Section 9.

---

## 9. A Retracted Cross-Solver Finding

A natural follow-up question is whether one solver's risk score predicts the *other* solver's blind zone — evidence, if it held up, of a shared underlying accessibility structure. Raw cross-prediction showed an asymmetry: `risk_basin` (WalkSAT) predicted CDCL's blind zone at AUROC $0.625$; `risk_cdcl_recurrence` (CDCL) predicted WalkSAT's blind zone at only $0.526$.

This did not survive confound analysis, and we report it as retracted rather than as a finding. Three independent methods converge: (i) a joint model using only generic confounds (Hamming weight, local density, distance to the other solver's set, instance size, coverage, $\hat\varepsilon$, regime) already reaches AUROC $0.946$ (or $0.756$ excluding the single strongest, most tautology-adjacent confound), and adding the solver-specific risk score improves discrimination by approximately zero in both directions; (ii) residualizing each risk score against the same confounds leaves a residual with no reliable within-instance predictive power ($0.441$ and $0.589$ median per-instance AUROC, both statistically indistinguishable from noise); (iii) restricting to instances where the two solvers' coverage levels are matched shrinks the WalkSAT$\to$CDCL figure from $0.625$ to $0.556$. The dominant confound is a coverage-calibration mismatch: CDCL's tested budget gave it systematically lower mean coverage than WalkSAT on the same instances, mechanically inflating the apparent transfer.

A specific alternative hypothesis — that a risk score identifies solutions that are difficult to find by *any* method (a solver-agnostic rarity signal) — was tested directly and also not supported: while pooled correlations between a risk score and joint-discoverability-by-both-solvers are large, the within-instance ranking ability is at or near chance ($0.533$, $0.500$), indicating the pooled correlation is a between-instance artifact of shared confounds rather than a genuine solution-level sensing capability.

We explicitly do not use, and found no evidence supporting, dynamical-systems language ("conjugacy," "semiconjugacy") for any relationship between the two solvers: no state-space map between their respective search dynamics was ever constructed, and the predictive relationship the terminology would have decorated is itself the confounded finding just retracted.

---

## 10. The Paired Observer Effect

This is the paper's central empirical result. For all $349$ held-out test instances with both solvers' observed sets nonempty, we compare $A_W(I)$ and $A_C(I)$ against the identical, freshly re-enumerated $S_I$, at each solver's standard experimental budget (Section 7) — no post-hoc budget tuning to produce this result.

**Fragmentation.** At fixed radius $r=1$, WalkSAT's excess-component count ($C_{A_W}(1) - C_S(1)$) is a median $11.6\times$ (95% CI $[9.6, 13.3]$) larger than CDCL's, paired Wilcoxon $p=5.2\times10^{-31}$. The effect holds in every regime, every $n$, every coverage band tested, and — critically — survives restricting to the $160$ instances where the two solvers' coverage levels are matched within $10$ percentage points (paired $p=2.4\times10^{-7}$; Figure 4).

**Resolution.** On the same $349$ paired instances, WalkSAT achieves significantly *better* $\hat\varepsilon$ than CDCL: mean $1.413$ versus $3.516$, paired Wilcoxon $p=5.1\times10^{-38}$, surviving the same coverage-matched restriction ($p=2.5\times10^{-8}$; Figure 5).

**The trade-off is the finding.** WalkSAT wins on resolution and loses badly on connectivity fidelity; CDCL does the reverse. Neither solver is geometrically superior in an unqualified sense — each better preserves a different, logically independent aspect of $S_I$'s true geometry (Section 5), and this is not a contradiction of the stability bound in Section 6: that bound is a one-directional worst-case guarantee (small $\hat\varepsilon$ bounds *how much* distortion is possible, not that distortion must be small), and CDCL's larger $\hat\varepsilon$ does not violate it — it simply operates further from the bound's tightest regime while still, empirically, showing far less realized distortion in practice.

This result is, to our knowledge, the first demonstration that the abstract coverage/resolution independence proved in Section 5 — established there via hand-built extremal point-set constructions — is realized "in the wild" by two real, unmodified, off-the-shelf SAT solvers on real random-3-SAT instances, rather than only as a worst-case existence proof.

---

## 11. Discussion and Limitations

**What this paper establishes.** A corrected, exact discrete distinguishability theorem; a correctly attributed (not novel) connectivity-stability bound with one independently verified sharpness result; a proof that coverage and resolution are logically independent; non-circular held-out evidence that two solver paradigms each predict their own blind zones; and — the central contribution — direct empirical evidence that solver identity materially and *oppositely* shapes two geometric diagnostics of the same solution space at matched coverage.

**What this paper does not establish.** No claim is made about computational complexity, hardness characterization, or which solver paradigm is preferable for any practical purpose. No portfolio-performance claim is made beyond the narrow observation that the union of the two solvers' found sets improves $\hat\varepsilon$ on a real but modest ($15.6\%$) minority of instances (Appendix D) — this is reported as a geometric observation, not an engineering recommendation. No dynamical or causal relationship between the two solvers is claimed.

**Scope.** The paired observer effect (Section 10) is established for two specific, carefully audited implementations — this WalkSAT configuration and Glucose3 specifically — on random 3-SAT with $n \le 20$ (the ceiling imposed by exhaustive ground-truth enumeration). Whether the resolution/connectivity trade-off generalizes across local-search implementations, across CDCL solvers, to structured or larger instances, or to other constraint-satisfaction domains, is an open question this paper does not address.

**Coverage/resolution near-redundancy, and why it is not the whole story.** For WalkSAT alone, coverage and $\hat\varepsilon$ are empirically almost perfectly anti-correlated across our instance ensemble ($\rho=-0.975$) — in that narrow sense $\hat\varepsilon$ adds little practical information beyond coverage *for a single solver*. Section 10's cross-solver result shows this near-redundancy is not fundamental: introducing a second solver paradigm on the identical instances reveals the two diagnostics diverging sharply and reproducibly.

---

## Appendix A — Hamming-Ball Theorem: Full Proof and Verification

*(Full statement, proof, and exhaustive verification detail from Section 4; brute-force results across 45,393 $(n,D,\varepsilon)$ cases, $n=1$–$10$: exhaustive for $n\le6$, representative-plus-transitivity-spot-checked for $n=7$–$10$; zero mismatches.)*

## Appendix B — Convention Translation for the Harker et al. Correspondence

*(Full $t \leftrightarrow r/2$ translation table and triangle-inequality computation matching Harker et al.'s Lemma 5.7 term-for-term with our $\varepsilon+r+\varepsilon$ derivation.)*

## Appendix C — Stratification Tables

*(Regime, $n$, and $|S_I|$-tercile breakdowns for both solvers' held-out AUROC, Table 1's full companion.)*

## Appendix D — Portfolio Geometry (Framed Strictly as an Observation)

*(Union coverage/$\hat\varepsilon$ improvement statistics, $15.6\%$ of instances, no performance claim.)*

## Data and Code Availability

All instance generation, solver, and analysis code, together with raw and processed results supporting every number in this paper, are available in the frozen four-phase audit record accompanying this manuscript.

## References

1. Mézard, M., Parisi, G., Zecchina, R. (2002). Analytic and algorithmic solution of random satisfiability problems. *Science*, 297(5582), 812–815.
2. Achlioptas, D., Ricci-Tersenghi, F. (2006). On the solution-space geometry of random constraint satisfaction problems. *Proceedings of STOC*, 130–139.
3. Chazal, F., de Silva, V., Oudot, S. (2014). Persistence stability for geometric complexes. *Geometriae Dedicata*, 173, 193–214.
4. Harker, S., Kramár, M., Levanger, R., Mischaikow, K. (2019). A comparison framework for interleaved persistence modules. *Journal of Applied and Computational Topology*, 3(1–2), 85–118. arXiv:1801.06725.
5. Cohen, G., Honkala, I., Litsyn, S., Lobstein, A. (1997). *Covering Codes*. North-Holland Mathematical Library, vol. 54.
6. Chakraborty, S., Meel, K. S., Vardi, M. Y. (2015). Constrained sampling and counting: universal hashing meets SAT solving. *arXiv:1512.06633*.
7. Audemard, G., Simon, L. (2009). Predicting learnt clauses quality in modern SAT solvers. *Proceedings of IJCAI*.
