# Develop and select research directions

Use this workflow when the user asks for research gaps, extensions, a project plan, or comparison of candidate topics. Use the user's language. Do not promise novelty, publication, or a positive experimental outcome.

## Start from the actual research setting

Record the problem, available models/data/platforms, research stage, skills, computational budget, and important deadlines when known. Infer routine choices from context; ask only questions that materially change the proposed work. Do not assume a particular application, controller family, publisher, or need for a new theorem.

Describe the setting by features: continuous/discrete time; linear/nonlinear; deterministic/stochastic; delay/hybrid/distributed; objectives; measurement, actuation, safety, and computation constraints. A direction may combine several features.

Classify the intended contribution:

- **Theory:** A new result, weaker assumptions, stronger conclusion, sharper bound, or counterexample, with a defensible proof strategy.
- **Algorithm:** A changed computational or control mechanism with demonstrated benefit and a clear tradeoff.
- **Engineering:** A validated capability under meaningful implementation or operating constraints, with reproducible evidence of what enables it.
- **Data/tool:** A dataset, benchmark, evaluation protocol, or software capability whose reliability and usefulness are demonstrated.

These categories may overlap. Judge the contribution by its claim and evidence, not by whether every project contains a new theorem.

## Generate provisional candidates, then check closest work

1. Read relevant seed sources at the depth needed to identify assumptions, mechanisms, limits, and evidence. Record actual gaps separately from unexplored possibilities.
2. Produce as many distinct candidates as useful. One focused plan or a small comparison is often better than a forced list of five.
3. Formulate each candidate as a testable difference from the closest known work: what changes, under which conditions, with what measurable or provable consequence?
4. Search for the closest work **before ranking or committing**. Use synonyms, equivalent formulations, foundational work, and recent primary sources. Follow `reference-expansion.md`.
5. Update or reject candidates whose central idea is already established. A negative search result is scoped evidence, not proof of novelty. Record search date, queries, inspected sources, and remaining uncertainty.
6. Identify the minimal result that would make a surviving candidate informative, including a useful negative result.

A combination of existing methods is not itself a demonstrated contribution. Explain the interaction, incompatibility, missing guarantee, implementation bottleneck, or new evidence that makes the combination research-worthy.

## Use one shared evaluation rubric

Apply these same criteria in reports and `notes/directions.md`. Prefer qualitative judgments with supporting evidence; numerical scores are optional and must not conceal uncertainty.

| Criterion | Question | Evidence to record |
|---|---|---|
| Problem value | Who benefits, and why does the limitation matter? | Operating need or scientifically meaningful unresolved question |
| Distinctness | What remains different after inspecting the closest work? | Closest sources and the precise remaining delta |
| Technical plausibility | Is there a credible mechanism or proof route? | Key derivation, preliminary reasoning, and likely obstacle |
| Validation quality | Can the central claim be falsified and evaluated fairly? | Baselines, metrics, counterexamples, or proof obligations |
| Feasibility | Can the available resources support the work? | Data/platform access, tools, skills, time, compute |
| Scope and cost | Is the minimal contribution bounded and achievable? | Milestones, dependency order, effort and failure risks |
| Robustness of contribution | What remains useful if the strongest claim fails? | Reduced claim, negative finding, benchmark, or reusable artifact |

Use `unknown` when evidence is missing. If using a weighted score, state the weights and why they match the user's goals; present critical blockers separately. A high total must not override an unavailable dataset or an invalid central assumption.

## Candidate record

For each serious candidate, provide:

1. A descriptive title and contribution type.
2. The research question and bounded target claim.
3. The closest work, its assumptions/results, and the proposed difference.
4. The mechanism or proof idea, including the hardest unresolved step.
5. A minimal validation plan: a small analytical case, counterexample search, reproducible baseline, or initial experiment.
6. A falsification or stop condition: what observation or derivation would undermine the proposed benefit?
7. Required resources, principal risks, and a fallback that does not disguise failure.
8. Current evidence, uncertainty, and the next decision needed.

Do not substitute an invented improvement percentage, benchmark result, or “easy acceptance” estimate for evidence. If resource estimates are rough, label assumptions and ranges.

## Select and stage the work

Recommend a direction only after explaining the strongest alternative and the relevant tradeoff. If the evidence is too weak to choose, recommend the smallest discriminating investigation instead of a confident ranking.

Set short milestones with observable outputs: reproduce one baseline; resolve a proof obstacle; demonstrate feasibility on a small instance; run a fair stress test; reassess the target claim. Use development cases for tuning and reserve validation cases for the eventual evaluation.

When new literature or a failed experiment removes the claimed difference, revise the scope or stop. Do not keep changing metrics, baselines, or assumptions simply to obtain a favorable comparison.

Update `notes/directions.md` and `PROJECT_STATE.md` with the selected/provisional/rejected status, decision rationale, open evidence gaps, and next action. In `evidence.json`, new claims remain hypotheses until the appropriate evidence has actually been obtained and reviewed. A plan is not a completed result.
