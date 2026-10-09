# AgroField Agent — demo runbook

> Target: 2:42. English narration or complete English subtitles. Do not record a final public video until separately authorized.

## Single judge takeaway

AgroField does not guess its way from a field note to a recommendation. It shows what the note proves, blocks what it does not prove, and makes a human accountable for the next task.

## Preflight gates

- Record with `?lang=en` so the interface, questions and task templates are in English; the field notes stay in Spanish on purpose and the narration says so.
- Public build uses a real Nemotron runtime call and the header says `Nemotron · Token Factory`; `/api/runtime` shows the model and demo budget.
- The run records model, latency, tokens, request ID, retries, and measured cost.
- No API key, personal data, browser bookmark, email, or private tab is visible.
- Demo database contains only synthetic fields and a fresh audit trail.
- Tavily is off unless its authorized ablation passed and the shown source is current and allowlisted.
- Metric overlay uses real Nemotron results; otherwise it visibly says `ENSAYO LOCAL · SINTÉTICO`.

## Shot list and narration

### 0:00–0:14 — The operational failure

**Screen:** Four synthetic soybean fields after a storm. Highlight the priority list and weather/history context.

**Narration:**

> After a storm, a field message can sound complete while omitting the measurement that makes a decision safe. AgroField turns that message into accountable evidence before anyone acts.

### 0:14–0:29 — Product boundary

**Screen:** Provider badge, selected field, and the line “No diagnostica ni autoriza tratamientos.”

**Narration:**

> Nemotron extracts explicit observations. Deterministic policy owns the safety gates. The system never prescribes, never invents a missing value, and never executes a task without a named human.

### 0:29–1:01 — Incomplete note

**Action:** Select **Lote Bajo**, choose **Incomplete note**, and click **Analyze evidence**.

**Screen:** Pause on literal evidence quotes, the red blocked banner, and the two missing checks.

**Narration:**

> This note reports soybean stage, event timing, safe access, standing water, and a low stand. But it never says whether the observation represents the field or how long the water has remained. AgroField preserves the facts, exposes those omissions, and blocks closure instead of filling the gaps.

### 1:01–1:31 — Complete evidence

**Action:** Choose **Complete note** and analyze again.

**Screen:** Show the W-route quote, six sampling points, water duration, review-ready state, priority score, and proposed follow-up task.

**Narration:**

> The second note adds a representative W route, six points, affected area, and water duration. The packet is now ready for review. Weather and field history explain priority, but they do not prove field condition.

### 1:31–1:52 — Human approval and audit

**Action:** Enter a synthetic reviewer label, approve one follow-up task, and open **Audit trail**.

**Screen:** Show the pending-to-approved transition and the audit events.

**Narration:**

> The task still does nothing by itself. A named adviser approves or rejects it, and AgroField records the observation, policy outcome, proposal, reviewer, and decision.

### 1:52–2:12 — Technical proof

**Screen:** Architecture graphic or concise overlay: Nemotron → schema → deterministic gate → approval → audit.

**Narration:**

> The browser holds no provider key. Nemotron runs through Nebius Token Factory with constrained output. Invalid output is rejected, SQLite retains field memory, and the deterministic gate cannot be overridden by the model.

### 2:12–2:33 — Measured evidence

**Screen:** Real Nemotron result card only after the authorized evaluation.

**Narration template:**

> On our frozen synthetic suite, `[MODEL]` reached `[F1]` extraction F1 and `[OMISSION_RECALL]` critical-omission recall at `[P95]` p95 latency and `[COST]` per visit. Full independent agronomy validation remains future work.

### 2:33–2:42 — Close

**Screen:** Return to the blocked-versus-ready comparison and logo.

**Narration:**

> AgroField Agent: evidence before action after the storm.

## Optional Tavily insert

Use at most ten seconds and remove equivalent material elsewhere. Show one dated official alert, its source URL, and the small change in inspection priority. State explicitly that it does not prove presence in the field. If the ablation is not measured, omit this insert and the bonus claim.

## Retake criteria

Retake the recording if any of the following occurs:

- the provider badge says local during a claimed Nemotron run;
- a metric is shown without its provider and dataset;
- the note or alert produces an unsupported field fact;
- a sensitive action appears executed without approval;
- the video exceeds 2:55 before upload;
- a key, email, real location, real establishment, or personal name appears;
- the narration implies independent human validation;
- Tavily is described as diagnosing field conditions.

## Local rehearsal command

```powershell
.\.venv\Scripts\python.exe -m agrofield_agent --recording
```

Open `http://127.0.0.1:8000`. Restart this command before each take to obtain a fresh temporary database and audit trail. Recording mode forces the local deterministic provider, disables external-provider credentials for the process, and shows `ENSAYO LOCAL · SINTÉTICO`. It is for timing and UI verification only; it does not satisfy the hackathon's Nebius runtime requirement.

For this local timing rehearsal, replace the product-boundary narration with: “This rehearsal uses the deterministic local extractor. In the final eligible build, Nemotron will extract explicit observations while the same deterministic policy owns the safety gates.” Do not narrate a live Nemotron claim until the provider badge and measured evidence prove it.
