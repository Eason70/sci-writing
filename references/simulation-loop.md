# Reproduction and experiments

## Establish the question
State the exact empirical claim, operating domain, primary metric and meaningful tolerance before tuning. Separate reproducing a result, testing a new method, and developing an implementation. A replication mismatch is useful evidence.

Read the original equations, implementation details and supplementary code. Record source version, figure/table target, parameters, discretization, solver tolerances, horizon, initial conditions, seeds and recoverability gaps. Classify reconstructed settings as inferred rather than reported.

## Fair comparisons
Create a protocol table with a row per method and columns for:
- available measurements, model information, uncertainty and training data;
- input/state constraints, disturbances, sampling and communication budget;
- solver, hardware, stopping tolerances, implementation language and tuning budget;
- parameters chosen on development cases and held-out validation cases.

Equal settings are not always appropriate: methods may have different required assumptions. Explain which comparison is matched and which is outside a method's admissible scope. Include a credible closest baseline when available. Do not silently disable baseline constraints, give one method extra information, or tune only the proposed method.

Select metrics from the claim: tracking/regulation error, constraint-violation magnitude and duration, effort, robustness range, communication, estimation quality, compute time and failures. Specify normalization, units, aggregation, infeasible-run treatment and trade-offs. Avoid unexplained aggregate scores.

## Implement and execute
1. Start from a small checkable reference problem with known behavior.
2. Verify signs, dimensions, units, integrator/solver convergence and controller timing. State sampled implementation separately from continuous-time theory.
3. Implement baseline and candidate from the declared protocol. Add focused checks for concrete risks.
4. Freeze development choices before evaluating held-out cases. Where repeated stochastic runs matter, report seeds, variation and uncertainty; never invent statistical confidence.
5. Save configurations, raw data, metrics and environment before plotting.
6. Inspect numerical failures, infeasibility, saturation, missing values and misleading axes. Diagnose theoretical, numerical and implementation explanations separately.
7. Update claims to match evidence and repeat only to answer a concrete unresolved question.

No hardcoded “baseline” and “proposed” trajectories standing in for experiments. If a pedagogical demonstration is requested, isolate it, label it synthetic and exclude it from research evidence.

## Records and provenance
For scaffolded projects follow [project-contract](project-contract.md). Each run has a stable ID and status. A completed run needs:
- saved configuration including solver settings and data/model versions;
- code revision or reproducible content hash, plus environment/runtime record;
- explicit RNG seed (document deterministic computations as such too);
- raw outputs and any figures derived from them.

Record commands, elapsed time, warnings and deviations in `notes/experiment-log.md`. Keep failed and inconclusive runs; a plot does not make a failed run completed. Claim evidence must identify the run and metric/table/figure.

If the runtime or licensed software is unavailable, deliver implementation and an execution command with status **not run**. Do not substitute invented data or a different solver and imply equivalence. Before executing external code, inspect its file/network operations and dependencies.

## Stop and report
Stop when planned evidence is collected or a defined resource limit/failure condition is reached. Outcomes may be a supported bounded advantage, a trade-off, no measurable difference, failure, or insufficient evidence. Never tune indefinitely until the candidate wins.

Report protocol, reproduction fidelity, completed and failed cases, metrics with units and supported uncertainty, interpretation within the tested domain, and remaining gaps. Simulation success is empirical evidence for those cases, not a general theoretical guarantee.
