# Recommended architecture

## Product boundary

The system coordinates evidence gathering and human-reviewed follow-up. It does not autonomously diagnose a disease, select an agrochemical, calculate a dose, or dispatch machinery.

```text
Voice/text note
     |
     v
Browser capture -> FastAPI orchestration -> Nemotron structured extractor
                         |                         |
Weather + lot history --+                         v
                         |                 Evidence schema
                         v                         |
                 Deterministic gates <------------+
                         |
          +--------------+--------------+
          |                             |
   Missing evidence                Review-ready
   targeted questions             proposed tasks
          |                             |
          +----------> Human approval <-+
                              |
                         SQLite audit log

Optional Tavily -> allowlisted official alerts -> priority signal only
```

## Components

| Component | Responsibility | Trust rule |
|---|---|---|
| Browser | Voice-to-text convenience, lot selection, review UI | Never receives provider keys. Typed fallback always available. |
| FastAPI API | Request validation, orchestration, audit event creation | Reject malformed model output. |
| Nemotron provider | Extract explicit observations and draft concise rationales | Must return schema-constrained tool arguments; cannot approve actions. |
| Local provider | Deterministic zero-cost development/evaluation | Same output schema as Nemotron. |
| Evidence policy | Completeness, critical omissions, readiness, priority | Pure deterministic code with tests. |
| Tavily provider | Retrieve recent allowlisted official alerts | No diagnosis; source/date retained; no result means no extra signal. |
| SQLite | Fields, history, observations, proposals, approvals, audit | Append-only audit events; secrets are never stored. |

## Model routing

- Default production candidate: `nvidia/nemotron-3-super-120b-a12b` for one structured extraction/synthesis call per note.
- Cost candidate: benchmark `Nemotron-3-Nano-30B-A3B` for extraction. Promote only if it passes the same critical-omission gate.
- Ultra is not justified in the MVP; use only if an evaluation shows material benefit on complex cases.
- Browser speech recognition is an input convenience, not the evaluated NVIDIA component.

## Data contract

The guarded Nebius wire contract selects request-local source IDs in
`evidence_sources` and `note_sources`. Application code resolves those IDs to exact
original note excerpts before constructing the shared observation schema. Invalid
references fail closed. This guarantees literal provenance, not semantic support
for every model-extracted value; see `submission/nebius-source-anchors-2026-09-14.md`.

The shared `ObservationDraft` contains typed observation fields, an `evidence_quotes` mapping, `notes` and `uncertainties`; it does not contain per-field confidence scores. Units are defined by field names and wire-schema descriptions. The v2 candidate explicitly distinguishes event age from water duration, total affected area from water area, and event type from crop condition. Unknown values remain `null`/`unknown`. Client-side quantity checks reject negative or nonfinite measurements even where the shared model lacks a bound. These checks do not prove semantic support. See `submission/nebius-semantic-candidate-2026-09-15.md`; v2 is locally tested only.

Critical fields for the post-event slice:

- confirmed lot and crop stage;
- event type and approximate timing;
- safety/access status;
- number of representative sample points;
- affected area estimate;
- standing-water duration for flooding;
- stand/regrowth and stem injury for hail/wind;
- proposed re-scout window and responsible person.

## Failure behavior

- Provider unavailable: preserve the raw note, show a retryable error, and allow local demo mode.
- Invalid JSON/tool arguments: reject; never silently coerce a decision.
- Missing critical evidence: mark `blocked`, generate targeted questions, and do not propose treatment.
- Tavily unavailable or no authoritative source: continue without external-alert enrichment.
- Conflicting evidence: show both facts, reduce confidence, and require adviser resolution.
- Stale lot metadata: display age and request confirmation.

## Deployment path (not authorized yet)

1. Containerize the single FastAPI process.
2. Deploy to a low-cost public host or Nebius compute only after a written cost cap is approved.
3. Make a runtime Nemotron call for every analyzed demo note.
4. Use a persistent managed volume/database or preloaded demo tenant.
5. Add health/readiness endpoints and synthetic uptime checks through the judging period.

Public deployment, DNS, repository publication, and billing remain explicit approval gates.
