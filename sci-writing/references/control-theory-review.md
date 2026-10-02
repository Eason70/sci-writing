# Review control-theoretic claims

Use this reference for a targeted theory audit, explanation, or derivation. Select obligations from the actual system features and claimed conclusion; do not impose every row on every paper. Report in the user's language. This workflow identifies reasoning and evidence gaps; it does not certify a mathematical proof.

## Fix the statement before reviewing the proof

Record the dynamics and solution concept; state/input/output dimensions; time domain; admissible initial conditions; uncertainty; information pattern; and operating constraints. Define every design parameter and its allowed range. Separate a nominal model from its implementation, approximation, or sampled version.

Rewrite the target as a precise statement: under which assumptions, for all or some trajectories/policies/disturbances, on which domain, over which time horizon, with what conclusion? Distinguish local/global and uniform/nonuniform results. Keep deterministic, almost-sure, in-probability, mean-square, and high-probability claims separate.

Check existence and continuation of the relevant solutions before relying on behavior for all time. Uniqueness is required only where the argument needs it; if solutions are nonunique, clarify whether the claim concerns all solutions or the existence of one.

## Route by system features

| Feature | Review the relevant obligations |
|---|---|
| Continuous time | Regularity and solution concept; derivative conditions on the claimed domain; invariance and forward completeness where needed; finite escape and discontinuous feedback |
| Discrete time / sampled implementation | One-step difference conditions; actual sampling/hold and discretization errors; admissible step-size range; intersample behavior if a continuous-state guarantee is claimed |
| Stochastic | Probability space, filtration and adapted decisions; disturbance law and independence assumptions; integrability; generator or conditional drift; exact probabilistic conclusion and finite/infinite horizon |
| Delay | Retarded/neutral and constant/time-varying setting; admissible history functions; delay/rate bounds used in the proof; functional terms and delayed information availability |
| Hybrid / switched | Flow and jump domains/maps; behavior at both flows and jumps; switching/dwell conditions; solution completeness and Zeno behavior when relevant |
| Distributed / networked | Graph direction and connectivity over time; local versus global information; synchronization of updates; communication delays/losses; agent heterogeneity and topology changes |
| Learning / data-driven | Training versus validation data; model/error assumptions and where they hold; policy adaptation in the proof; extrapolation; uncertainty calibration; computational and actuation implementation limits |

Features compose. For example, a sampled distributed learner must meet the relevant information, timing, and model-error conditions together. Check that these conditions are jointly satisfiable.

## Route by claimed conclusion

| Claim | Questions that the argument must resolve |
|---|---|
| Stability / convergence | What equilibrium, set, or trajectory? What notion of stability/attractivity? Is the candidate function positive definite relative to the target and suitably bounded on the claimed domain? What does its derivative/difference actually imply? |
| Robustness / disturbance attenuation | Which input class and norm? Uniform over which uncertainties? Are internal stability, initial-state terms, gain bounds, and residual sets handled as required by the claimed notion? |
| Constraint satisfaction / safety | What is the safe set and admissible initial set? Does a feasible input exist throughout the relevant region? Are invariance conditions compatible with the solution concept, disturbances, sampling, and input limits? |
| Optimization / MPC feasibility | Does the optimization admit a feasible solution and, where claimed, an optimizer? Does the next actual state admit a feasible candidate? Are terminal, horizon, tightening, model-error, and solver assumptions sufficient for the chosen argument? |
| Optimality / performance | Is the claim global, local, stationary, approximate, regret-based, or relative to a restricted comparator? Are existence, convexity/duality, differentiability, and numerical accuracy assumptions used correctly? |
| Estimation / identification | Which states or parameters are observable/identifiable under the available signals? What excitation and noise conditions are needed? Is the conclusion bounded error, consistency, convergence, or a finite-sample guarantee? |
| Finite-/fixed-time behavior | Does the settling-time argument match the definition and initial-condition dependence? Are singularities, saturation, disturbances, and the post-settling solution handled? |

An MPC proof need not use terminal ingredients if a different valid argument is supplied. Persistent excitation is not a universal requirement for every estimation objective. Request the conditions demanded by the actual conclusion, not a memorized checklist.

## Trace the proof and look for counterexamples

1. Build a dependency chain from assumptions through lemmas and inequalities to the exact conclusion. Identify circular arguments and assumptions introduced after they are needed.
2. Check dimensions, signs, index/time alignment, matrix definiteness, domains, inverses, rank conditions, and constant dependencies. Distinguish a computable design condition from one requiring unknown quantities.
3. Re-derive the key transition. Name the inequality or theorem, check its hypotheses, and identify any change from equality to bound.
4. Test boundary cases analytically where possible: zero disturbance, saturation, singular matrices, disconnected graphs, inactive/active constraints, equilibrium, and zero excitation. Select cases tied to the specific claim.
5. If numerical checks help, state their finite scope. A solver success or many simulated trajectories cannot establish a universal theorem; a valid counterexample can disprove a universal claim.

Common failure patterns:

- A negative-semidefinite Lyapunov derivative is promoted to asymptotic convergence without an applicable invariance, detectability, or other convergence argument.
- A local inequality or model-error bound is used globally; boundedness of trajectories is assumed while trying to prove it.
- Continuous-time safety or stability is transferred to sampled, delayed, approximate, or saturated implementation without accounting for the change.
- A barrier inequality is treated as a feasible controller despite conflicting constraints or unavailable state information.
- Initial optimization feasibility is treated as recursive feasibility; a shifted candidate relies on an unproved terminal or robustness condition.
- Expected performance is reported as an almost-sure guarantee, or a fixed-time probability bound is used over an unbounded horizon without justification.
- Negative consensus error is mistaken for stability of the common trajectory; learning success on training data is promoted to an out-of-distribution guarantee.

## Report actionable findings

For each finding, give its source locator, the claimed step, required condition, observed gap, consequence, and smallest useful correction or verification. Label its confidence and severity:

- **Demonstrated error:** A concrete contradiction, invalid algebraic step, or valid counterexample.
- **Missing justification:** A necessary step or condition is not supplied in the inspected material.
- **Scope limitation:** The result may hold under narrower conditions than the wording suggests.
- **Open question:** Available evidence is insufficient to decide.

Do not call a missing proof an established falsehood. Do not silently add assumptions while preserving the original strength of the claim. If proposing a repair, state how it changes the theorem and what remains unproved.

Save an audit in `notes/theory-audit.md` when a project exists. Link exact derivation/source locations in `evidence.json` under `project-contract.md`; record unresolved obligations in `PROJECT_STATE.md`. Numerical diagnostics remain empirical evidence. Mark repaired claims supported only after the relevant derivation has actually been completed and reviewed; the structural checker cannot make that judgment.
