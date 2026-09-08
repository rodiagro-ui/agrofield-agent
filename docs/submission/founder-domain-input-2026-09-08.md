# Sanitized founder domain input — 2026-09-08

> Status: product-discovery input only. Non-independent, self-reported, not part of the blind benchmark, and not authorized for public use.

## Provenance and limitations

- Evidence ID: `FDI-001`.
- Source type: first-party written workflow account supplied by the project owner.
- Self-reported role: agronomy adviser involved in field observation and visit prioritization.
- Experience band: not reported.
- Independence from the project: no.
- External verification: none.
- Publication authorization: none.
- Raw account retained in the repository: no.

This record can support design choices and an honest founder story. It cannot establish market prevalence, agronomic accuracy, independent validation, or measured impact.

## Sanitized workflow summary

After an intense rain event with a localized hail report, measurements and informal alerts arrived through field messaging and weather tools. The first decision was not a treatment or planting action. The team first assessed access safety, suspended planned field operations, and reprioritized the morning around inspection of vulnerable crops.

Event detection, field observation, and visit ordering involved different operational roles. Before departure, the team had rainfall and regional weather context but lacked reliable field-level information about hail intensity, event duration, and plant damage. A measurement from one point did not establish conditions across a distant part of the property.

The field check deliberately avoided judging the crop from the entrance. The team followed a representative route across contrasting terrain and inspected several points. At each point, it assessed stand, visible damage, and plant tissue indicators. An irreversible replanting decision was deferred for roughly two to three days so that regrowth could be checked during a return visit.

The resulting record included sampled points, images, stand-loss estimates, and technical recommendations for review by operational and insurance roles. The source described this workflow as recurring during the crop season and identified premature decisions as the main consequence of missing information.

## Product requirements supported by this account

1. **Access safety precedes agronomic triage.** Unsafe or unknown access must block entry recommendations.
2. **One observation is not a field.** The product should request a representative route and multiple sampling points.
3. **External context changes inspection priority, not field truth.** Rain gauges, radar, satellite anomalies, and neighboring reports may guide where to inspect but cannot prove crop condition.
4. **Some decisions require elapsed time.** Hail or flooding damage may require a scheduled return visit before an irreversible action.
5. **Evidence must remain auditable.** The original note, sampled observations, missing checks, proposed task, reviewer, and decision should be retained.
6. **A useful system must sometimes stay quiet.** A routine, spatially uniform rain event with safe access and no mechanical-damage signal may not justify a detailed digital workflow.

## Trust-destroying failure inferred from the account

The product would lose credibility if it inferred plant death, field-wide damage, or a replanting decision from a drive-by observation, a remote signal, or a single sampling point.

This is a design inference from the first-party account, not a measured user-research result.

## Scope note

The source used another crop as a comparative example when explaining stage-dependent vulnerability. AgroField's submitted vertical remains post-event soybean scouting; the comparison is not treated as soybean evidence and is excluded from product claims.
