# Find, verify, and use research literature

Use this workflow to expand a reading set, investigate a gap, identify baselines, or support manuscript claims. Choose sources by relevance and evidentiary quality. Do not impose a publisher, venue, language, or reference-count quota.

## Make the search answer a question

- State the claim or decision to be informed: closest method, known theorem, comparable benchmark, implementation constraint, or application need.
- Build queries from system class, objective, constraint, mechanism, and synonyms. Include equivalent mathematical formulations and terms used in neighboring control subfields.
- Search both foundational and recent work when relevant. Record the search date; use version dates when preprints and published papers differ.
- Use review papers to discover terminology and source trails. For technical claims, inspect the primary theorem, experiment, dataset, or official software documentation that supplies the evidence.
- Follow backward references and forward citations when tools allow. Stop when additional searches mainly repeat relevant work and the decision is sufficiently supported; describe material coverage gaps.

Use available scholarly search, DOI registries, publisher pages, institutional repositories, and author pages. If browsing or full-text access is unavailable, work from supplied sources and label the search incomplete. Never present an unperformed search as completed.

## Separate three checks

| Check | What it establishes | What it does not establish |
|---|---|---|
| Existence and metadata | A matching work exists with identifiable title, authors, date, venue/version, and identifier | That the paper contains a particular result |
| Relevant content inspected | The needed section, theorem, experiment, or artifact was read | That every manuscript sentence is entailed or the result is correct |
| Claim support assessed | The source supports a specific, scoped statement under stated conditions | General validity beyond those conditions or formal correctness of its proof |

Verify metadata against an authoritative landing page or the primary document. Resolve title/author/year mismatches instead of silently merging records. Deduplicate preprint and published versions while retaining the exact version used for equation and page locators.

For a quoted or paraphrased result, capture its precise locator and conditions. Distinguish the author's asserted novelty from independently established history. A paper reporting improvement in one experiment does not establish universal superiority.

## Compare the closest work directly

Maintain a comparison table for the sources that determine the research decision:

| Source/version | System and assumptions | Mechanism | Guarantee or measured result | Information and computation | Limitations | Relevance to proposed claim |
|---|---|---|---|---|---|---|

Populate cells only from inspected material. Mark `not reported`, `not inspected`, and `not applicable` distinctly. Do not infer that an absent statement means a method cannot provide that capability.

Check whether apparently different methods become equivalent under a change of notation, a special case, or identical information assumptions. Compare theoretical scope and empirical performance separately. Distinguish a stricter assumption from a worse result; these are different tradeoffs.

Before selecting a baseline, establish whether source code, parameter settings, data, and computational requirements are obtainable. If reproducing a described method rather than using author code, identify that fact and document uncertain implementation choices.

## Add citations responsibly

- Cite the source closest to the claim, including the original result where appropriate. Do not add references solely to increase a count.
- Keep established background, related methods, and direct evidence distinct in the prose.
- Use accurate BibTeX metadata from a verified source; preserve meaningful capitalization. Do not manufacture DOI values, page ranges, venues, or placeholder citations that look real.
- If only an abstract was inspected, limit the supported statement to what it actually establishes and record the access limit.
- If relying on a secondary description of inaccessible work, attribute the secondary description explicitly and keep the original unverified.
- If sources conflict, state the differing settings or conclusions and investigate the cause. Do not average incompatible claims or suppress a negative result.

Follow applicable source quotation limits. Prefer an original explanation with a citation over extensive copied text.

## Record evidence and stopping conditions

Use stable source IDs in `evidence.json`, following `project-contract.md`. `metadata_verified` is appropriate after identity checks; `content_checked` requires inspecting the relevant content. A claim marked supported also needs its own precise evidence locator and an assessment of whether the source supports its wording.

Record useful queries, search date, included/excluded closest sources, access limitations, and unresolved differences in project notes or `PROJECT_STATE.md`. Avoid copying large search result dumps into the project.

Complete the search when it supports the requested decision at the agreed scope. If an important closest source remains inaccessible, report the resulting uncertainty and propose the smallest next action, such as requesting that paper or revising the claim. Do not declare novelty or exhaustive coverage from absence in one search engine.
