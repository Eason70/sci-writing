# Manuscript drafting and revision

## Match the task
For a paragraph edit, revise directly, preserve technical meaning and list substantive unresolved issues separately. Do not initialize a project or search for novelty unless needed for the requested change.

For an existing paper, inspect structure, macros, notation, bibliography and target venue. Preserve the template. For a new paper, choose a structure that fits the contribution and venue; IEEE is one option. Check current author instructions when preparing for a specified venue.

## Section readiness
| Section | Evidence needed |
| --- | --- |
| Title and contributions | Bounded contribution relative to closest work |
| Abstract | Actual outcome and scope; distinguish planned from completed work |
| Introduction/related work | Verified source claims, nearest competitors, concrete unresolved question |
| Problem formulation | Model, information pattern, notation, assumptions, domains, units and objective |
| Theory | Precise quantifiers, guarantees and conditions; proof or clearly identified gap |
| Method/algorithm | Implementable steps, inputs, outputs, costs and parameter rules matching analysis |
| Experiments | Fair protocol, real run artifacts, baselines, failures and limitations |
| Conclusion | Established results and bounded future work |

Theory, engineering, algorithm and dataset/tool papers need different section emphasis. Do not insert a vacuous theorem into an empirical paper or turn a simulation trend into a stability claim.

Draft the technical core first when developing a project. A clearly labeled plan may precede results; use prospective language and placeholders, never a fabricated completed abstract.

## Technical and citation audit
Trace each substantive contribution to a derivation, source or completed run. Check:
- variables have consistent dimensions/domains; CT derivatives and DT differences are not mixed;
- theorem statements and captions respect actual assumptions and validity regions;
- optimality, robustness, convergence and safety are named at demonstrated strength;
- comparisons distinguish performance from statistical significance and measured runtime from complexity;
- citations support adjacent statements at the cited version and location;
- equations, algorithm and implementation share parameter definitions;
- figures derive from identified artifacts and include units and conditions.

Use `evidence.json` and `notes/claim-evidence.md` for ongoing projects. Mark unverified claims visibly and offer an evidence request, narrower wording or removal. Never create plausible-looking bibliography fillers.

## Revision deliverables
Return the requested clean revision and concise notes for changes affecting meaning. Preserve numbers, theorem strength and scope unless a change is requested and supported. Separate language edits from proposed technical corrections.

For reviewer responses, map comments to specific changes and locations or evidence-backed explanations. Never claim an experiment was added, proof completed, or request met unless the artifact exists.

For Word inputs, use the available document workflow and preserve formatting. Track changes only if the tool supports it; explain the actual delivered format.

## Mechanical and visual review
For scaffolded projects:
```bash
python "<skill-dir>/scripts/check_project.py" "<project-dir>" --mode submission
python "<skill-dir>/scripts/build_paper.py" "<project-dir>" --mode submission
```
The checker detects common issues in declared artifacts and text. Unconventional TeX macros and bibliography systems may need manual review; static checking is not a complete TeX parser. For an existing custom toolchain, use its build and interpret logs instead of replacing it.

Inspect rendered PDFs when tools are available: equation overflow, column widths, tiny fonts, figure legibility, broken references and layout. Compilation alone is not visual review. State if rendered inspection was not performed.

Submission checking aids the generated workflow; it does not certify correctness, novelty, citation entailment or acceptance.
