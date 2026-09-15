# Semantic extraction candidate v2 — local only

> Status: LOCAL_CANDIDATE_FROZEN_NOT_LIVE_EVALUATED. No provider call, key,
> personal data, human annotation, publication or expense in this increment.

## Starting evidence

At bb91cd1, 88 tests passed, both local baselines reproduced, and the human
benchmark candidate freeze matched 34/34 hashes. The saved real Nano response
still got only 4/8 expected observed fields right on one synthetic development
note, with three omissions, a wrong event and an unsupported condition.

Inspection found that most numeric and categorical wire fields had no semantic
description. Source IDs made quotes literal but did not teach the distinctions
between event age/water duration, affected area/water area or event/crop condition.
That is a plausible contributor to the observed errors, not a proven model cause.

## What changed

Runtime candidate commit: 6d7a5a8.
Development references/checker/freeze commit: ab339dc.
Profile: source-anchors-es-v2-semantic-candidate.

1. Every observation field now has an explicit Spanish definition in the wire
   schema. No wire key, enum, numeric limit or mandatory field was removed.
2. Instructions distinguish explicit negation, zero and unknown; prohibit
   transferring other-lot facts or forecasts; preserve unresolved contradictions;
   and require binding numbers to the right variable, unit and scope.
3. Client-side validation now rejects negative and nonfinite quantities. The
   shared model previously lacked some wire-schema minima, allowing e.g. a
   negative event age/count through its type validation. Six mocked adverse
   cases verify rejection, safe diagnostics, no retry and no local fallback.
4. The CLI result/preflight identifies the extraction profile. App telemetry
   retains its existing schema; a future route-run record must separately retain
   the tested commit/profile and request fingerprint.
5. Twenty new AI-authored synthetic development cases are explicitly separated
   from the 12/30-case evaluation sets. They contain all 12 expected observation
   fields, source IDs, uncertainty labels and visible developer rationales.
6. A network-free checker validates reference shape, literal sources, hashes and
   request budget. It does not create simulated model outputs or quality scores.

No changes to policy.py, shared ObservationDraft, source resolution, local
extractor, frozen benchmark data/rubric/evaluator or historical live evidence.
No extra model call, model judge, silent correction or deterministic filling of
Nemotron values was added. Numeric validation is not semantic entailment checking.

## Verification

- 124 tests passing, including 37 mocked guarded-Nebius tests and 30 development
  reference/profile checks. Test counts are engineering checks, not model scores.
- Old 12-case local baseline: F1 0.9551; omission recall 1.0000; unsupported 0;
  safety 1.0000; nDCG 1.0000; eight adverse failures.
- Old 30-case local candidate: F1 0.9188; omission recall 0.9714; unsupported 0.0050;
  safety 1.0000; nDCG 0.9877; 53 adverse failures; 7/17 gates; validated false.
- Original benchmark candidate freeze: 34/34 hashes unchanged.
- Separate development profile freeze: 8/8 hashes, 20 synthetic cases, zero live
  candidate calls and zero human reviews. Valid hashes do not mean valid agronomy.
- Saved real-response audit unchanged: 4/8 observed fields correct for historical
  Nemotron, 8/8 for local, plus the documented adverse errors.

The checker reports observed/unknown reference coverage separately. Most fields
are intentionally unknown in many cases; counting those as successes could make
an abstaining model look artificially strong. No accuracy or F1 is reported here.

## Budget and risks

At historical 2026-09-14 Nano prices, the smoke request grew from 5,885 to 9,776
serialized bytes; the largest development request is 9,999 bytes. All fit the
unchanged 16,384 prompt / 1,024 completion ceilings and the conservative
US$0.00122880 per-request ceiling. No price, current credit or paid authorization
is inferred from this offline calculation. The CLI without live confirmation
still stops with exit code 2 before network access.

A longer prompt may increase latency/input cost and may still fail extraction.
The v2 descriptions may also be too conservative on unfamiliar wording. The
references are AI-authored, exposed development material, not independent
agronomic ground truth. Mock/reference tests cannot establish improvement over v1.

## Reproduction and next decision

From the repository root:

```powershell
python -m pytest -q
python -m agrofield_agent.semantic_preflight
python -m agrofield_agent.freeze fixtures/development/semantic_v2/manifest.json --root .
python -m agrofield_agent.smoke_audit
```

See [development package](../../fixtures/development/semantic_v2/README.md) for
the case map, request fingerprints and freeze. The existing full benchmark and
its gates remain separate.

The next useful external action is a separately authorized single request on the
same historical development note. Compare all 12 fields, not just HTTP success:
look for the missing 18-hour event age, 35% standing water and 14-hour duration,
the correct event, and an unknown general condition. Keep all adverse outcomes.
Even a perfect repeat would only justify broader controlled testing, not a claim
of model superiority or independent validation. Before that request, verify
current prices, credit and Stop usage; use/revoke a temporary key and do not retry.
No such new authorization is granted by this report.
