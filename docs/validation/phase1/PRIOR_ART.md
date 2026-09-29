# PRIOR_ART.md — Novelty / Prior-Art Audit (Phase 2)

Scope: audits only the *mathematical/terminological novelty* of the paper's core
quantities. Does not touch Phase 1 (theorem correctness) or Phases 3–8.

All citations below were retrieved via live web search on 2026-09-28. Where a
claim could not be verified against a primary source, that is stated explicitly.
Per the paper's own discipline rule: **absence of a search hit is evidence of
"not found," never evidence of novelty.**

## Summary table

| Quantity / idea in the paper | Classification | Grounds / citation |
|---|---|---|
| ε̂(A,I) = sup_x∈S_I min_y∈A(I) d_H(x,y) | **A** — standard math, new label | Exactly the directed/one-sided Hausdorff distance $\vec{d}_H(S_I,A(I))$; since $A(I)\subseteq S_I$ it also equals the full symmetric Hausdorff distance $d_H(S_I,A(I))$. Directed Hausdorff distance is a textbook construct (see below). |
| ε̂ as "covering radius" | **A/C boundary** | Classical covering radius $\rho(C)=\max_{v\in\mathbb F_2^n}\min_{c\in C}d(v,c)$ is defined over the *whole ambient space* (Cohen–Honkala–Litsyn–Lobstein, *Covering Codes*, North-Holland Math. Library vol. 54, 1997, ISBN 0-444-82511-8). The paper's version restricts the outer max to $S_I\subsetneq\{0,1\}^n$ rather than the full cube. This "covering radius relative to a subset" is not the object coding theorists call "covering radius" (nor the recently studied *generalized* covering radii of Elimelech–Firer–Schwartz, which generalize in a different, information-theoretic direction). It is, however, exactly directed Hausdorff distance restricted to point sets — a basic, well-known construction in computational geometry, so the "subset-relative covering radius" framing adds no new mathematics; it's a restatement in coding-theory language of an already-standard geometric quantity. |
| Cov(A,I) = \|A(I)∩S_I\|/\|S_I\| | **A** | Ordinary recall / coverage fraction; standard in sampling and information retrieval. |
| Cluster spectrum $C_S(r)$ | **A** | Standard single-linkage / connectivity-threshold clustering (Vietoris–Rips 1-skeleton connected components) applied to Hamming space. |
| "Blind zone is structured, not random" (empirical claim) | **C**, with strong adjacent **B** prior art | Not a new *quantity*, but the *finding* sits inside an active, well-developed literature (see §5 below) that already establishes solver-specific sampling bias in SAT solution spaces. |
| Persistent-homology stability under Hausdorff perturbation (the tool needed for Phase 4) | **B — known result, directly reusable** | Cohen-Steiner, Edelsbrunner, Harer, *Stability of Persistence Diagrams*, Discrete Comput. Geom. 37(1), 103–120 (2007), DOI 10.1007/s00454-006-1276-5; Chazal, de Silva, Oudot, *Persistence Stability for Geometric Complexes*, Geometriae Dedicata 173, 193–214 (2014), arXiv:1207.3885. |
| "Algorithmic resolution" as a term of art | **D (as a label), not as a quantity** | No independent (non-self-authored) use of this exact phrase for this exact quantity was found. The underlying quantity itself is (A). |

---

## 1. Covering radius (coding theory)

Canonical reference: G. Cohen, I. Honkala, S. Litsyn, A. Lobstein, *Covering
Codes*, North-Holland Mathematical Library vol. 54, Elsevier, 1997 (ISBN
0-444-82511-8). Standard definition: for a code $C\subseteq \mathbb F_2^n$,
$\rho(C) = \max_{v\in \mathbb F_2^n}\min_{c\in C} d_H(v,c)$ — the max is over
the *entire ambient space*, not a subset.

A genuine, recent generalization exists — **generalized covering radii**
(Elimelech, Firer, Schwartz), studied further in several 2024–2025 arXiv
papers (e.g. arXiv:2608.30961, arXiv:2606.16669, arXiv:2510.25295) — but this
generalizes along a different axis (multiple query vectors / private
information retrieval), not "restrict the outer max to a subset of the
ambient space." No paper was found that studies "covering radius of $A$
relative to a subset $S\subsetneq \mathbb F_2^n$" under that name.

**Verdict:** the paper's ε̂ is *not* the standard covering radius (wrong
ambient set) but *is* exactly a subset-restricted directed Hausdorff
distance — see §2. Classification: **A**, existing math, with a
non-standard but harmless relabeling as "covering radius."

## 2. Directed / asymmetric Hausdorff distance

Standard definition confirmed via multiple sources (survey material,
Discrete & Comput. Geom. treatments of Hausdorff-distance complexity, e.g.
Springer DOI 10.1007/s00454-023-00562-5): for point sets $A,B$,
$\vec{d}_H(A,B) = \max_{a\in A}\min_{b\in B} d(a,b)$, called the "one-sided"
or "directed" Hausdorff distance; the symmetric version is
$d_H(A,B)=\max(\vec d_H(A,B),\vec d_H(B,A))$. This is decades-old,
textbook computational geometry (used pervasively in shape matching, image
segmentation quality (e.g. medical-image segmentation metrics), point-cloud
quality assessment — e.g. arXiv:2003.13669 "generalized Hausdorff distance
based quality metric for point cloud geometry").

**Direct algebraic identity** (verified independently, not something I
searched for — a derivation, stated here for the record): because
$A(I)\subseteq S_I$,
$$\vec d_H(A(I), S_I) = \max_{y\in A(I)}\min_{x\in S_I} d(y,x) = 0$$
(every $y\in A(I)$ is itself in $S_I$, distance 0 to itself), so
$$d_H(S_I, A(I)) = \max\big(\vec d_H(S_I,A(I)),\ \vec d_H(A(I),S_I)\big) = \vec d_H(S_I,A(I)) = \hat\varepsilon(A,I).$$
**$\hat\varepsilon(A,I)$ is, exactly, the Hausdorff distance between the two
sets $S_I$ and $A(I)$** — no new quantity is being introduced; it's a
100%-standard object under a domain-specific name.

**Verdict: A.**

## 3. Epsilon-nets and metric entropy

Standard: $\varepsilon$-covering number $M(\mathcal F,\varepsilon)$ = min
balls of radius $\varepsilon$ needed to cover $\mathcal F$; $\log M$ is the
Kolmogorov $\varepsilon$-entropy (Encyclopedia of Mathematics; standard in
empirical process theory / statistical learning theory, e.g. binghamton.edu
lecture notes "Covering numbers (Metric Entropy)"). $A(I)$ is an
$\hat\varepsilon$-net of $S_I$ by construction — i.e., ε̂ is literally the
smallest $r$ such that $A(I)$ is an $r$-net of $S_I$.

No paper was found giving a **deterministic inequality directly linking**
$|A(I)|/|S_I|$ (a *cardinality* ratio) **to a covering radius** for
*arbitrary* finite subsets of a discrete metric space; the classical
covering-number/entropy machinery bounds *cardinality needed to achieve a
given radius* for well-behaved (often continuous, doubling, or convex)
spaces, not the reverse direction for an arbitrary given subset $A(I)\subseteq S_I$
of unconstrained geometry. This gap is real, but it is a gap in a
*direction* of the epsilon-net literature that would need $S_I$'s specific
combinatorial structure (packing numbers of the true solution set) to close
— see Phase 7 in `V2_THEOREMS.md`. Classify the framework here as: standard
tools (A) with a **potentially genuine small gap (D)** in the specific
question "what deterministic inequality holds between coverage fraction and
covering radius for an *arbitrary* subset of an *arbitrary* finite metric
space," which is likely unprovable without extra structure — see the
counterexamples constructed in `V2_THEOREMS.md` Phase 7.

## 4. Persistent-homology stability (the tool needed for Phase 4)

Two canonical, load-bearing theorems, both confirmed against primary/
secondary sources:

- **Cohen-Steiner, D., Edelsbrunner, H., Harer, J. (2007).** *Stability of
  Persistence Diagrams.* Discrete & Computational Geometry 37(1), 103–120.
  DOI: 10.1007/s00454-006-1276-5. States: for tame functions $f,g$ on a
  common space, $d_B(\mathrm{Dgm}(f),\mathrm{Dgm}(g)) \le \|f-g\|_\infty$.

- **Chazal, F., de Silva, V., Oudot, S. (2014).** *Persistence Stability
  for Geometric Complexes.* Geometriae Dedicata 173, 193–214.
  arXiv:1207.3885. Proves stability of persistent homology of Vietoris–
  Rips / Čech / witness complexes built on precompact metric spaces **with
  respect to Gromov–Hausdorff distance**. Related: Chazal, Cohen-Steiner,
  Guibas, Mémoli, Oudot, *Gromov–Hausdorff Stable Signatures for Shapes
  using Persistence*, gives the specialization to two point sets sitting
  inside a **common ambient metric space**, where Gromov–Hausdorff distance
  is bounded above by ordinary Hausdorff distance, giving
  $d_B(\mathrm{Dgm}(\mathrm{Rips}(X)),\mathrm{Dgm}(\mathrm{Rips}(Y))) \le 2\, d_H(X,Y)$.

**Applicability check to the discrete Hamming cube (this was the key risk
flagged in the task):** the search results indicate the *stability*
framework (bottleneck bound via interleaving distance) holds for **general
metric spaces** — it does *not* require geodesicity or a length-space
structure. Geodesicity/convexity-radius conditions appear only in a
*different* family of theorems (manifold-*reconstruction*/homotopy-type
recovery results, e.g. Niyogi–Smale–Weinberger-style theorems, and
$\delta$-hyperbolic contractibility results), not in the bottleneck-
stability theorem itself. This is an important distinction for the paper:
**the stability bound imports cleanly into the discrete Hamming cube with no
extra hypotheses**, but a *reconstruction* theorem (recovering the true
homotopy type of $S_I$ from $A(I)$, not just bounding diagram distance)
would need geometric regularity of $S_I$ that the Hamming cube does not
generically provide. This distinction should be made explicit and not
blurred in V2 — see `V2_THEOREMS.md`.

Since $d_H(S_I,A(I)) = \hat\varepsilon(A,I)$ exactly (§2), the schematic
"small covering radius ⇒ reliable topology above some scale" **is already a
theorem**, by direct substitution:
$$d_B\big(\mathrm{Dgm}(\mathrm{Rips}(A(I))),\ \mathrm{Dgm}(\mathrm{Rips}(S_I))\big) \le 2\,\hat\varepsilon(A,I).$$
This should be reported as **KNOWN RESULT, directly applicable** — not
reproved from scratch, and not claimed as new. See `V2_THEOREMS.md` for the
precise statement and translation caveats (in particular: this bounds
diagram *distance*, and only gives "features live/die at the correct scale
up to $2\hat\varepsilon$," not "clusters are identical" — the cluster-count
gap $\Delta_A(r)$ in the original paper is a cruder, non-stable quantity
that the bottleneck-distance version should likely replace).

## 5. SAT solution-space geometry and sampling bias

This is the area with the most direct, load-bearing prior art against the
paper's *empirical* claims (not its formal quantity).

- **Mézard, Parisi, Zecchina (2002)**, *Analytic and algorithmic solution
  of random satisfiability problems*, Science 297(5582), 812–815 — already
  cited by the paper itself.
- **Achlioptas, Ricci-Tersenghi (2006)**, *On the solution-space geometry
  of random constraint satisfaction problems*, STOC 2006 (arXiv:cs/0611052)
  — already cited by the paper. Confirmed: proves solutions organize into
  exponentially many well-separated clusters with frozen ("backbone")
  variables well before the SAT/UNSAT threshold. This is *the* canonical
  result that the paper's Example 5.1 "apparent clustering" observation
  must be read against: some clustering in random 3-SAT solution spaces is
  a **geometric fact about $S_I$ itself**, not only an observer artifact.
  The paper needs to be careful to distinguish intrinsic (Achlioptas–
  Ricci-Tersenghi) clustering from observer-induced fragmentation — the
  January draft's Example 5.1 (49 solutions, 1 true component) is at
  $\alpha=3.0$, plausibly below typical clustering thresholds for small
  $n$, but this should be checked explicitly against known threshold
  estimates rather than asserted.
- **Backbone / frozen-variable literature**: Monasson, Zecchina, Kirkpatrick,
  Selman, Troyansky (Nature/Science-era work on phase transitions);
  Slaney & Walsh, *Backbones in Optimization and Approximation* (IJCAI
  2001); "Frozen variables in random boolean CSPs" (arXiv:1209.4829);
  "Backbone Fragility and the Local Search Cost Peak" (arXiv:1106.0240).
  Backbone fraction as a hardness confound is **already established**
  machinery — directly relevant since a stronger V2 predictive-accessibility
  study (Phase 5) proposes backbone structure as one candidate predictor;
  that candidate is well-motivated by this literature, not invented from
  nothing.
- **Sampling bias of local search / WalkSAT**: search results confirm an
  active, recent literature (2023-2026 preprints found: "Numerical
  Solution-Space Analysis of Satisfiability Problems," "Solution space
  heterogeneity of the random K-satisfiability problem," "Self-averaging of
  digital memcomputing machines," "Communities of solutions in single
  solution clusters") establishing that local-search / random-walk
  samplers are **known** to be non-uniform and biased toward specific
  regions (e.g. large basins of attraction), and that lowering restart
  cutoffs improves uniformity. This directly anticipates (as prior art,
  classification **B**) the paper's central empirical claim in §5–6 that
  "blind zones are structured, not random" — the *qualitative* phenomenon
  (solver sampling bias distorts observed solution geometry) is established
  literature. What the January draft adds beyond this literature is (i)
  formalizing the distortion via a Hausdorff/covering-radius quantity and
  (ii) the connectivity/cluster-count framing — i.e., classification **C**
  (useful recombination), not **D** (novel phenomenon).
- **Near-uniform SAT sampling** (UniGen family): Chakraborty, Meel, Vardi
  et al., *Constrained Sampling and Counting: Universal Hashing Meets SAT
  Solving* (arXiv:1512.06633); *On Parallel Scalable Uniform SAT Witness
  Generation* (TACAS 2015, Springer 10.1007/978-3-662-46681-0_25); GitHub
  `meelgroup/unigen`. This entire line of work exists *specifically because*
  naive samplers (local search, DPLL enumeration order, biased random
  generation) are known to be non-uniform — i.e., the SAT community has
  already built an entire toolchain around exactly the phenomenon the
  paper demonstrates qualitatively. A V2 revision should cite this and, if
  feasible, benchmark $\hat\varepsilon$/coverage against a UniGen-style
  near-uniform sampler as a near-ground-truth-unbiased baseline. This is
  the single highest-value addition Phase 2 surfaced for Phase 5's
  experiment design.

## 6. Algorithm portfolios / search-space coverage & diversity metrics

- **SATzilla** (Xu, Hutter, Hoos, Leyton-Brown) and general algorithm-
  portfolio literature (Huberman–Lukose–Hogg 1997 coined "algorithm
  portfolio") — concerned with *selecting* among solvers per-instance
  based on runtime features, not with measuring geometric coverage of the
  solution space. Only tangential relevance.
- **Diverse-solution SAT literature** — this is the closest adjacent active
  research area and should be cited prominently in V2:
  - Nadel, *Generating Diverse Solutions in SAT*, SAT 2011 (Springer
    10.1007/978-3-642-21581-0_23) — explicitly raised the problem of
    generating multiple far-apart satisfying assignments.
  - Crescenzi & Rossi, MAX HAMMING DISTANCE SAT (classical) — maximize
    Hamming distance between two satisfying assignments.
  - **Fomin et al. and others, *Algorithms for the Diverse-k-SAT Problem:
    The Geometry of Satisfying Assignments*, ICALP 2025
    (arXiv:2408.03465, DOLIPIcs.ICALP.2025.14)** — very recent (2024-2025),
    explicitly studies "the geometry of satisfying assignments" and
    algorithms (including PPZ/Schöning-style) for finding maximally
    dispersed solution sets. This is the single closest title/theme match
    found in the entire search. It is about a *different question*
    (constructively finding a diverse/dispersed solution set, a
    combinatorial-optimization/complexity problem) rather than *measuring,
    after the fact, how far a given found set is from the true solution
    set* — but any V2 revision **must** cite and distinguish itself from
    this line of work explicitly, since a referee will find it immediately.
    Classification of the overlap: **C** (adjacent, distinguishable, but
    close enough that failing to cite it would be a real omission).
  - "Computing diverse pair of solutions for tractable SAT" (arXiv:2412.04016),
    "On the Parameterized Complexity of Diverse SAT" (ISAAC 2024),
    "Diversity of Solutions... Fixed-Parameter Tractability" (arXiv:1903.07410)
    — same cluster of recent work, all about *constructing* diverse
    solutions rather than measuring blind-zone geometry of a given
    algorithm's output.

## 7. Does "algorithmic resolution" name a new quantity?

**No.** $\hat\varepsilon(A,I)$ is, exactly and without approximation, the
Hausdorff distance between the found-solution set $A(I)$ and the true
solution set $S_I$ under the Hamming metric — equivalently, the radius of
the smallest $\varepsilon$-net of $S_I$ that $A(I)$ constitutes. Both
"Hausdorff distance" and "covering radius / $\varepsilon$-net radius" are
decades-old, textbook objects (computational geometry and coding theory
respectively), and the paper's own Definition 3.3 is a direct, unmodified
instance of the standard directed-Hausdorff-distance formula applied to a
subset relationship ($A(I)\subseteq S_I$) that collapses the usual
two-sided max into the one-sided term. "Algorithmic resolution" is new
**terminology** for this existing, standard mathematical quantity —
classification **A** for the object itself. No independent (non-self-
authored) usage of the phrase "algorithmic resolution" for this or any
closely related meaning was found in the searches performed; this should be
read as "no term-of-art collision was found," not as a novelty claim for
the underlying math, which is not new.

The place where the paper's contribution is least reducible to existing
terminology is not the *definition* of $\hat\varepsilon$ but the specific
**framing and empirical demonstration** that different SAT search
paradigms (DPLL / local search / biased vs. unbiased sampling) exhibit
systematically different, structured values of this Hausdorff-type quantity
on identical instances, connected explicitly to apparent connectivity/
cluster-count distortion. That framing is a **recombination (C)** of
(a) standard Hausdorff/covering-radius geometry, (b) already-known SAT
sampling-bias phenomena (§5), and (c) the cluster-spectrum construction —
worth developing further (per Phases 3–4, e.g. via the persistence-
stability route in §4, which is genuinely underused in the current SAT-
sampling literature as far as this search could determine), but should not
be marketed as introducing a new geometric invariant.
