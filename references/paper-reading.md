# Read and explain research papers

Use this workflow for a single paper, a related set, or a literature review. Answer in the user's language while preserving technical notation and unambiguous terminology. Scale the depth to the request: a paragraph explanation does not require a full paper report.

## Establish the source and coverage

- Record the title, authors, year, DOI or stable URL, version/date, and available supplementary material. Distinguish a preprint from its published revision.
- Inspect the actual supplied text or full paper before explaining its specific results. Metadata or an abstract alone cannot support claims about proofs, algorithms, or experiments.
- Record coverage explicitly: full text inspected; selected sections inspected; abstract only; supplements/code unavailable. For a long paper, read the requested material and its prerequisites first; do not silently call partial reading complete.
- Use precise locators: printed page plus PDF page if different, section, equation, theorem, figure, table, or code file/function. If a scanned equation is unclear, flag transcription uncertainty rather than repair it from imagination.
- Separate the paper's statements from cited predecessors. Open the predecessor when its content is necessary to the explanation; otherwise attribute it as the paper's description.

## Reconstruct the research argument

1. **Problem:** Identify the system, decision variables, available measurements, uncertainty, constraints, time domain, and success criterion. State what the paper excludes.
2. **Starting point:** Explain the closest method or conventional formulation and the precise limitation being addressed. Identify whether the limitation is established, asserted by the authors, or your interpretation.
3. **Mechanism:** Trace information and computation through the model, estimator, controller, optimizer, or learning procedure. Explain why each major component is present and what breaks if it is removed.
4. **Mathematics:** Define symbols with dimensions and domains; separate assumptions, definitions, lemmas, main results, and corollaries. Reconstruct only as much derivation as needed for the user's goal.
5. **Guarantee:** State the exact conclusion, its quantifiers, and all material conditions. Distinguish local/global, asymptotic/exponential/practical, deterministic/probabilistic, and continuous/discrete guarantees.
6. **Evidence:** Connect each claim to its derivation, experiment, or citation. Distinguish a proved result, a numerical observation, and an untested interpretation.
7. **Limits:** Identify the boundary of applicability and whether an apparent gap is a demonstrated defect, an omitted detail, or a question requiring verification.

For theory-heavy papers, use `control-theory-review.md` for targeted proof obligations. An explanation or internal consistency check is not a formal proof certificate.

## Explain at the requested depth

For a **compact paper card**, include:

| Field | Required content |
|---|---|
| Source and coverage | Version, stable locator, inspected material, unavailable parts |
| Problem and assumptions | System class, information, constraints, domain of validity |
| Contribution and mechanism | What changes, why it should matter, closest comparison |
| Main result | Exact guarantee or empirical finding, with source locator |
| Evidence and limitations | Proof/experiment support, material restrictions, unresolved issues |
| Reuse conditions | Which components transfer and what must be re-established |

For a **full learning report**, additionally provide:

- A plain-language overview followed by prerequisite concepts and a symbol table.
- A section-by-section account of the logical dependencies, not a sentence-by-sentence paraphrase.
- Stepwise explanations of the key equations; name the inequality, modeling assumption, or theorem used at each nontrivial transition.
- A map from assumptions to results. Identify assumptions introduced only in proofs or experiments.
- The algorithm's inputs, outputs, update order, tuning parameters, computational burden, and execution conditions.
- An experiment analysis covering baselines, shared conditions, metrics, ablations, uncertainty, and whether the evidence supports the scope of the conclusions.
- A reusable-method assessment and a short list of questions the reader should resolve next.

Do not infer missing intermediate steps as if they appeared in the paper. Label a reconstructed derivation and show where it relies on additional conditions.

## Separate evidence from new ideas

Use explicit labels where ambiguity matters:

- **Source statement:** What the inspected source actually states, with a locator.
- **Interpretation:** Your explanation of its meaning or implication, with reasoning.
- **Proposed extension:** A new hypothesis, with changed assumptions and a validation plan.

For transfer to another control setting, list what changes in dynamics, sampling, observations, disturbances, topology, constraints, and computation. Then identify which proof or experiment must be repeated. Similar notation does not establish transferability.

Never describe an extension as novel solely because it is absent from the supplied papers. Pass potential directions to `direction-selection.md` for closest-work verification.

## Persist only useful records

In an existing project, append or update compact cards in `notes/paper-cards.md` and record unresolved questions in `PROJECT_STATE.md`. Store a full report separately only when requested or helpful for continued work.

Follow `project-contract.md` when updating `evidence.json`: metadata verification and content inspection are different statuses. Use source IDs and precise claim-level locators; do not mark an interpretation supported merely because the cited paper exists. Keep access restrictions and unread sections visible in the report and state.
