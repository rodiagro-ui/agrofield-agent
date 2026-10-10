const state = { fields: [], selected: null, latest: null, recordingMode: false, runtime: null, lang: "es" };

const incompleteNote = "Soja V3. La tormenta fue hace 18 horas y el acceso es seguro. Hay agua parada en aproximadamente 35% del lote. En los bajos conté 9 plantas por metro. El resto se ve heterogéneo.";
const completeNote = "Soja V3. La tormenta fue hace 18 horas y el acceso es seguro. Recorrí 6 puntos representativos en W. El anegamiento afecta 35% del lote y lleva 14 horas con agua parada. Conté 9 plantas por metro en los bajos. El estado general es heterogéneo.";

// Field notes stay in Spanish: that is the real input. The interface, the
// completeness questions and the task templates are translated client-side so
// the deterministic policy module stays untouched.
const i18n = {
  es: {
    brand_tagline: "evidencia antes de decidir", audit_button: "Trazabilidad",
    panel_eyebrow: "Post-evento · soja", panel_title: "¿Dónde mirar primero?", event_chip: "142 mm máx.",
    panel_copy: "Priorización previa. No diagnostica ni autoriza tratamientos.",
    capture_eyebrow: "1 · Captura de recorrida", capture_title: "Contá lo que viste, sin completar formularios",
    voice_button: "Dictar", voice_title: "Dictar nota", voice_unavailable: "El navegador no ofrece dictado; usá el campo de texto",
    voice_listening: "Escuchando…", example_incomplete: "Nota incompleta", example_complete: "Nota completa",
    note_label: "Nota de campo", note_placeholder: "Ej.: Soja V3, tormenta hace 18 horas…",
    note_hint: "Las notas de campo se escriben en español; la interfaz puede verse en inglés.",
    tavily_label: "Alertas oficiales recientes", tavily_hint: "Tavily, solo fuentes permitidas",
    tavily_disabled: "Configurá TAVILY_API_KEY para activar alertas en runtime",
    analyze_button: "Analizar evidencia", analyzing: "Analizando…",
    evidence_eyebrow: "2 · Hechos extraídos", evidence_title: "Evidencia trazable",
    questions_eyebrow: "3 · Control de completitud", questions_pending: "Preguntas pendientes", questions_complete: "Control completo",
    questions_empty: "No se detectaron omisiones críticas para este tipo de evento. La evidencia sigue requiriendo revisión humana.",
    review_eyebrow: "4 · Revisión humana", review_title: "Tareas propuestas, todavía no ejecutadas",
    reviewer_label: "Revisor", reviewer_placeholder: "Ej.: Asesor demo", reviewer_required: "Indicá quién revisa la tarea.",
    alerts_eyebrow: "Contexto externo · no prueba presencia en el lote", alerts_title: "Alertas oficiales recientes",
    audit_eyebrow: "Registro inmutable", audit_title: "Trazabilidad local", close_button: "Cerrar",
    blocked: n => `Decisión bloqueada · faltan ${n} controles`, blocked_sub: "La nota se conserva, pero el sistema no completa datos ausentes.",
    ready: "Evidencia lista para revisión", ready_sub: "El asesor puede revisar las tareas; nada se ejecuta solo.",
    priority: "prioridad / 100", not_reported: "No informado", due_in: h => `vence en ${h} h`,
    approve: "Aprobar", reject: "Rechazar", approved: "APROBADA", rejected: "RECHAZADA",
    decision_note: "Decisión registrada desde AgroField Agent", decision_note_recording: "Decisión registrada durante ensayo local sintético",
    selected_field: "Lote seleccionado", no_history: "sin alertas históricas", no_critical_history: "sin antecedente crítico",
    rain72: "lluvia · 72 h", gust: "ráfaga máxima", forecast48: "pronóstico · 48 h", ha: "ha", priority_short: "prioridad",
    badge_recording: "ENSAYO LOCAL · SINTÉTICO", badge_local: "modo local · $0", badge_nemotron: "Nemotron · Token Factory",
    badge_local_title: "Extractor determinista local; sin llamada a Nemotron en esta instancia.",
    badge_nemotron_title: m => `Extracción en vivo con ${m} vía Nebius Token Factory. La política de seguridad es determinista.`,
    budget_exhausted: "El presupuesto de la demo con Nemotron se agotó; la instancia sigue disponible con el extractor local.",
    rate_limited: "Demasiadas solicitudes en un minuto; esperá unos segundos.",
    engine_local_note: "Resultado del extractor local determinista, no de Nemotron.",
    verified: (m, ok, cleared) => `Verificación por ${m}: ${ok} respaldados · ${cleared} descartados`,
    unverified: m => `Sin verificar (${m} no respondió; se muestra la extracción sin segunda pasada)`,
    cleared_field: "Descartado por verificación: la cita no respalda el valor",
    labels: { crop_stage: "Estado", event_type: "Evento", event_hours_ago: "Antigüedad", access_safe: "Acceso",
      sample_points: "Puntos", affected_area_pct: "Área afectada", standing_water_pct: "Agua parada",
      water_duration_hours: "Duración agua", lodging_pct: "Vuelco", stem_damage_pct: "Daño de tallos", stand_count_per_m: "Stand" },
    events: { flooding: "Anegamiento", hail: "Granizo", wind: "Viento", mixed: "Mixto", none: "Sin daño", unknown: "Desconocido" },
    access: { true: "Seguro", false: "Inseguro" }, plants_per_m: "plantas/m",
    questions: null, tasks: null
  },
  en: {
    brand_tagline: "evidence before action", audit_button: "Audit trail",
    panel_eyebrow: "Post-storm · soybean", panel_title: "Where to look first?", event_chip: "142 mm max.",
    panel_copy: "Inspection priority only. It does not diagnose or authorize treatments.",
    capture_eyebrow: "1 · Field note", capture_title: "Say what you saw, no forms",
    voice_button: "Dictate", voice_title: "Dictate the note (Spanish)", voice_unavailable: "This browser has no speech recognition; type the note instead",
    voice_listening: "Listening…", example_incomplete: "Incomplete note", example_complete: "Complete note",
    note_label: "Field note", note_placeholder: "E.g.: Soja V3, tormenta hace 18 horas…",
    note_hint: "Field notes are written in Spanish, the scout's language; the interface is translated.",
    tavily_label: "Recent official alerts", tavily_hint: "Tavily, allowlisted sources only",
    tavily_disabled: "Set TAVILY_API_KEY to enable runtime alerts",
    analyze_button: "Analyze evidence", analyzing: "Analyzing…",
    evidence_eyebrow: "2 · Extracted facts", evidence_title: "Traceable evidence",
    questions_eyebrow: "3 · Completeness check", questions_pending: "Open questions", questions_complete: "Check complete",
    questions_empty: "No critical omissions detected for this event type. The evidence still requires human review.",
    review_eyebrow: "4 · Human review", review_title: "Proposed tasks, not executed yet",
    reviewer_label: "Reviewer", reviewer_placeholder: "E.g.: Demo adviser", reviewer_required: "Enter who reviews the task.",
    alerts_eyebrow: "External context · does not prove presence in the field", alerts_title: "Recent official alerts",
    audit_eyebrow: "Append-only record", audit_title: "Local audit trail", close_button: "Close",
    blocked: n => `Decision blocked · ${n} checks missing`, blocked_sub: "The note is preserved, but the system never fills in missing data.",
    ready: "Evidence ready for review", ready_sub: "The adviser can review the tasks; nothing runs on its own.",
    priority: "priority / 100", not_reported: "Not reported", due_in: h => `due in ${h} h`,
    approve: "Approve", reject: "Reject", approved: "APPROVED", rejected: "REJECTED",
    decision_note: "Decision recorded from AgroField Agent", decision_note_recording: "Decision recorded during the local synthetic rehearsal",
    selected_field: "Selected field", no_history: "no historical alerts", no_critical_history: "no critical history",
    rain72: "rain · 72 h", gust: "max gust", forecast48: "forecast · 48 h", ha: "ha", priority_short: "priority",
    badge_recording: "LOCAL REHEARSAL · SYNTHETIC", badge_local: "local mode · $0", badge_nemotron: "Nemotron · Token Factory",
    badge_local_title: "Local deterministic extractor; no Nemotron call on this instance.",
    badge_nemotron_title: m => `Live extraction with ${m} through Nebius Token Factory. The safety policy is deterministic.`,
    budget_exhausted: "The demo's Nemotron budget is exhausted; this instance stays available with the local extractor.",
    rate_limited: "Too many requests within a minute; wait a few seconds.",
    engine_local_note: "Result from the local deterministic extractor, not from Nemotron.",
    verified: (m, ok, cleared) => `Verified by ${m}: ${ok} supported · ${cleared} cleared`,
    unverified: m => `Unverified (${m} did not answer; showing the extraction without the second pass)`,
    cleared_field: "Cleared by the verifier: the quote does not support the value",
    labels: { crop_stage: "Stage", event_type: "Event", event_hours_ago: "Event age", access_safe: "Access",
      sample_points: "Sample points", affected_area_pct: "Affected area", standing_water_pct: "Standing water",
      water_duration_hours: "Water duration", lodging_pct: "Lodging", stem_damage_pct: "Stem damage", stand_count_per_m: "Stand" },
    events: { flooding: "Flooding", hail: "Hail", wind: "Wind", mixed: "Mixed", none: "No damage", unknown: "Unknown" },
    access: { true: "Safe", false: "Unsafe" }, plants_per_m: "plants/m",
    // Keyed by the policy's missing_critical field names.
    questions: {
      crop_stage: "Can you confirm the soybean growth stage (for example V3 or R1)?",
      event_type: "Was the event rain/flooding, hail, wind or a combination?",
      event_hours_ago: "How many hours have passed since the event?",
      access_safe: "Is access to the field safe and passable?",
      sample_points: "How many representative points did you walk, and in what pattern?",
      affected_area_pct: "Roughly what percentage of the field is affected?",
      standing_water_pct: "What percentage still has standing water?",
      water_duration_hours: "How many hours has the crop been under standing water or saturated soil?",
      lodging_pct: "What percentage shows lodging?",
      stem_damage_pct: "What percentage of plants have broken, cut or bruised stems?",
      stand_count_per_m: "What was the stand in plants per meter at several points?"
    },
    // The policy's task templates are fixed Spanish strings; map them by pattern.
    tasks: [
      [/^Escalar acceso inseguro en (.+)$/, (m) => `Escalate unsafe access in ${m[1]}`],
      [/^Completar (\d+) controles críticos en (.+)$/, (m) => `Complete ${m[1]} critical checks in ${m[2]}`],
      [/^Revisar evidencia post-evento de (.+)$/, (m) => `Review post-event evidence for ${m[1]}`],
      [/^Programar control de rebrote en (.+)$/, (m) => `Schedule a regrowth check in ${m[1]}`],
      [/^Revisar persistencia de agua en (.+)$/, (m) => `Re-check standing water in ${m[1]}`],
      [/^No continuar la recorrida hasta que una persona responsable confirme condiciones seguras\.$/, () => "Do not continue the scouting pass until a responsible person confirms safe conditions."],
      [/^La evidencia actual no permite cerrar la revisión sin inventar datos\.$/, () => "The current evidence cannot close the review without inventing data."],
      [/^Paquete completo listo para revisión del asesor; no implica tratamiento automático\.$/, () => "Complete packet ready for the adviser's review; it does not imply automatic treatment."],
      [/^El daño por granizo requiere una evaluación diferida del rebrote antes de decisiones irreversibles\.$/, () => "Hail damage requires a delayed regrowth assessment before irreversible decisions."],
      [/^Actualizar duración y extensión del anegamiento con la misma referencia de muestreo\.$/, () => "Update flooding duration and extent using the same sampling reference."]
    ]
  }
};

const el = id => document.getElementById(id);
const t = key => i18n[state.lang][key];

function translateFixed(text) {
  if (state.lang !== "en") return text;
  for (const [pattern, render] of i18n.en.tasks) {
    const match = text.match(pattern);
    if (match) return render(match);
  }
  return text;
}

function questionFor(fieldName, original) {
  const table = i18n[state.lang].questions;
  return (table && table[fieldName]) || original;
}

function applyLanguage(lang) {
  state.lang = lang;
  document.documentElement.lang = lang;
  try { localStorage.setItem("agrofield.lang", lang); } catch (_) {}
  el("langButton").textContent = lang === "es" ? "EN" : "ES";
  document.querySelectorAll("[data-i18n]").forEach(node => { node.textContent = t(node.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(node => { node.placeholder = t(node.dataset.i18nPlaceholder); });
  document.querySelectorAll("[data-i18n-title]").forEach(node => { node.title = t(node.dataset.i18nTitle); });
  renderBadge();
  if (state.fields.length) { renderFields(); if (state.selected) renderHero(state.selected); }
  if (state.latest) renderAnalysis(state.latest, { keepScroll: true });
}

function initialLanguage() {
  const fromQuery = new URLSearchParams(location.search).get("lang");
  if (fromQuery === "es" || fromQuery === "en") return fromQuery;
  try { const saved = localStorage.getItem("agrofield.lang"); if (saved === "es" || saved === "en") return saved; } catch (_) {}
  return (navigator.language || "es").toLowerCase().startsWith("es") ? "es" : "en";
}

async function api(url, options = {}) {
  const response = await fetch(url, { headers: {"Content-Type":"application/json"}, ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const error = new Error(body.detail || `Error ${response.status}`);
    error.status = response.status; error.body = body;
    throw error;
  }
  return response.json();
}

function fieldRiskScore(field) {
  const w = field.weather || {};
  return Math.min(99, Math.round((w.precipitation_mm_72h || 0) * .42 + (w.max_wind_gust_kmh || 0) * .25 + field.risk_flags.length * 8));
}

function renderFields() {
  const rankedFields = [...state.fields].sort((a, b) => fieldRiskScore(b) - fieldRiskScore(a));
  el("fieldList").innerHTML = rankedFields.map(field => `
    <button class="field-item ${field.id === state.selected?.id ? "active" : ""}" data-field="${field.id}">
      <div class="field-row"><span class="field-name">${field.name}</span><span class="field-stage">${field.stage}</span></div>
      <div class="field-meta"><span>${field.hectares} ${t("ha")}</span><span>${t("priority_short")} ${fieldRiskScore(field)}</span><span>${field.weather.precipitation_mm_72h} mm</span></div>
      <div class="field-risk">${field.risk_flags[0] || t("no_critical_history")}</div>
    </button>`).join("");
  document.querySelectorAll("[data-field]").forEach(button => button.addEventListener("click", () => selectField(button.dataset.field)));
}

function renderHero(field) {
  const w = field.weather;
  el("fieldHero").classList.remove("skeleton");
  el("fieldHero").innerHTML = `
    <div class="hero-main">
      <div><p class="eyebrow">${t("selected_field")} · ${field.crop}</p><h2>${field.name}</h2><p class="hero-sub">${field.hectares} ${t("ha")} · ${field.stage} · ${field.risk_flags.join(" · ") || t("no_history")}</p></div>
      <div class="weather-strip">
        <div class="weather-stat"><strong>${w.precipitation_mm_72h} mm</strong><small>${t("rain72")}</small></div>
        <div class="weather-stat"><strong>${w.max_wind_gust_kmh} km/h</strong><small>${t("gust")}</small></div>
        <div class="weather-stat"><strong>${w.forecast_rain_mm_48h} mm</strong><small>${t("forecast48")}</small></div>
      </div>
    </div>`;
}

function selectField(id) {
  state.selected = state.fields.find(field => field.id === id);
  renderFields(); renderHero(state.selected);
  state.latest = null;
  el("results").classList.add("hidden");
}

function setExample(kind) {
  el("rawNote").value = kind === "complete" ? completeNote : incompleteNote;
  el("completeExample").classList.toggle("active", kind === "complete");
  el("incompleteExample").classList.toggle("active", kind !== "complete");
}

function formatValue(key, value) {
  const lang = i18n[state.lang];
  switch (key) {
    case "event_hours_ago": case "water_duration_hours": return `${value} h`;
    case "access_safe": return lang.access[String(value)];
    case "affected_area_pct": case "standing_water_pct": case "lodging_pct": case "stem_damage_pct": return `${value}%`;
    case "stand_count_per_m": return `${value} ${lang.plants_per_m}`;
    case "event_type": return lang.events[value] || value;
    default: return `${value}`;
  }
}

function renderBadge() {
  const badge = el("providerBadge");
  const runtime = state.runtime || {};
  if (state.recordingMode) { badge.textContent = t("badge_recording"); badge.title = t("badge_local_title"); return; }
  if (!runtime.nemotron_runtime) { badge.textContent = t("badge_local"); badge.title = t("badge_local_title"); return; }
  badge.textContent = t("badge_nemotron");
  badge.title = t("badge_nemotron_title")(runtime.model);
}

function renderAnalysis(result, options = {}) {
  state.latest = result;
  const lang = i18n[state.lang];
  el("results").classList.remove("hidden");
  const ready = result.status === "review_ready";
  el("statusBanner").className = `status-banner ${ready ? "ready" : "blocked"}`;
  el("statusBanner").innerHTML = `
    <div><strong>${ready ? t("ready") : t("blocked")(result.missing_critical.length)}</strong>
    <small>${ready ? t("ready_sub") : t("blocked_sub")}</small></div>
    <div class="score-pill"><strong>${result.priority_score}</strong><small>${t("priority")}</small></div>`;
  const telemetry = result.telemetry;
  const provider = telemetry.provider === "nebius" ? "Nemotron" : telemetry.provider;
  el("latencyBadge").textContent = `${provider} · ${telemetry.model} · ${Math.round(telemetry.latency_ms)} ms`;
  el("latencyBadge").title = telemetry.request_id ? `request ${telemetry.request_id}` : "";

  const verification = result.verification || null;
  const clearedFields = verification ? (verification.cleared || []) : [];
  el("evidenceGrid").innerHTML = Object.keys(lang.labels).map(key => {
    const value = result.observation[key];
    const missing = value === null || value === undefined || value === "unknown";
    const quote = result.observation.evidence_quotes[key];
    const cleared = clearedFields.includes(key);
    return `<div class="evidence-item ${missing ? "missing" : ""} ${cleared ? "cleared" : ""}"><small>${lang.labels[key]}</small><strong>${missing ? t("not_reported") : formatValue(key, value)}</strong>${quote ? `<em>“${quote}”</em>` : ""}${cleared ? `<em class="cleared-note">${t("cleared_field")}</em>` : ""}</div>`;
  }).join("");
  const badge = el("verificationBadge");
  if (verification && verification.status === "verified") {
    badge.textContent = t("verified")(verification.model, verification.supported.length, verification.cleared.length);
    badge.className = "verification-badge ok";
  } else if (verification && verification.status === "unverified") {
    badge.textContent = t("unverified")(verification.model);
    badge.className = "verification-badge warn";
  } else {
    badge.textContent = ""; badge.className = "verification-badge hidden";
  }

  if (result.followup_questions.length) {
    el("questionsTitle").textContent = t("questions_pending");
    el("questionList").innerHTML = result.followup_questions.map((q, i) => {
      const fieldName = result.missing_critical[i];
      return `<div class="question-item"><span class="question-index">${i+1}</span><span>${questionFor(fieldName, q)}</span></div>`;
    }).join("");
  } else {
    el("questionsTitle").textContent = t("questions_complete");
    el("questionList").innerHTML = `<div class="question-empty">${t("questions_empty")}</div>`;
  }

  el("taskList").innerHTML = result.proposed_tasks.map(task => {
    const decided = task.status !== "pending";
    const actions = decided
      ? `<span class="task-status">${t(task.status)}</span>`
      : `<button class="reject" data-reject="${task.id}">${t("reject")}</button><button class="approve" data-approve="${task.id}">${t("approve")}</button>`;
    return `
    <div class="task-item ${decided ? "decided" : ""}" id="task-${task.id}">
      <span class="priority-dot ${task.priority}"></span>
      <div class="task-copy"><strong>${translateFixed(task.title)}</strong><small>${translateFixed(task.rationale)} · ${t("due_in")(task.due_hours)}</small></div>
      <div class="task-actions">${actions}</div>
    </div>`;
  }).join("");
  document.querySelectorAll("[data-approve]").forEach(b => b.addEventListener("click", () => decideTask(b.dataset.approve, "approve")));
  document.querySelectorAll("[data-reject]").forEach(b => b.addEventListener("click", () => decideTask(b.dataset.reject, "reject")));

  const alerts = result.official_alerts || [];
  el("alertsCard").classList.toggle("hidden", !alerts.length);
  el("alertList").innerHTML = alerts.map(alert => `<div class="alert-item"><a href="${alert.url}" target="_blank" rel="noopener">${alert.title}</a><p>${alert.snippet}</p></div>`).join("");
  if (!options.keepScroll) el("results").scrollIntoView({behavior: state.recordingMode ? "auto" : "smooth", block:"start"});
}

async function analyze() {
  const note = el("rawNote").value.trim();
  if (!state.selected || note.length < 5) return;
  const button = el("analyzeButton");
  button.disabled = true; button.textContent = t("analyzing"); el("captureMessage").textContent = "";
  const payload = JSON.stringify({field_id: state.selected.id, raw_text: note, use_tavily: el("tavilyToggle").checked});
  try {
    const result = await api("/api/analyze", {method:"POST", body: payload});
    renderAnalysis(result);
  } catch (error) {
    const code = error.body && error.body.failure_code;
    if (error.status === 429 && error.body && error.body.local_engine_available && code !== "demo_rate_limited") {
      // The shared demo ran out of Nemotron budget: say so, then use the local
      // engine explicitly. The telemetry badge names the engine that answered.
      el("captureMessage").textContent = `${t("budget_exhausted")} ${t("engine_local_note")}`;
      try { renderAnalysis(await api("/api/analyze?engine=local", {method:"POST", body: payload})); } catch (inner) { el("captureMessage").textContent = inner.message; }
    } else if (code === "demo_rate_limited") {
      el("captureMessage").textContent = t("rate_limited");
    } else {
      el("captureMessage").textContent = error.message;
    }
  } finally {
    button.disabled = false; button.innerHTML = `<span data-i18n="analyze_button">${t("analyze_button")}</span> <span>→</span>`;
  }
}

async function decideTask(taskId, action) {
  const reviewer = el("reviewerName").value.trim();
  if (reviewer.length < 2) { el("captureMessage").textContent = t("reviewer_required"); return; }
  const decisionNote = state.recordingMode ? t("decision_note_recording") : t("decision_note");
  const task = await api(`/api/tasks/${taskId}/${action}`, {method:"POST", body: JSON.stringify({reviewer, decision_note: decisionNote})});
  const stored = state.latest.proposed_tasks.find(item => item.id === taskId);
  if (stored) stored.status = task.status;
  const node = el(`task-${taskId}`); node.classList.add("decided");
  node.querySelector(".task-actions").innerHTML = `<span class="task-status">${t(task.status) || task.status}</span>`;
}

function setupVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) { el("voiceButton").title = t("voice_unavailable"); return; }
  const recognition = new SpeechRecognition(); recognition.lang = "es-AR"; recognition.interimResults = false;
  recognition.onstart = () => { el("voiceButton").classList.add("recording"); el("voiceButton").textContent = t("voice_listening"); };
  recognition.onend = () => { el("voiceButton").classList.remove("recording"); el("voiceButton").innerHTML = `<span aria-hidden="true">●</span> <span data-i18n="voice_button">${t("voice_button")}</span>`; };
  recognition.onresult = event => { const text = event.results[0][0].transcript; el("rawNote").value = `${el("rawNote").value.trim()} ${text}`.trim(); };
  el("voiceButton").addEventListener("click", () => recognition.start());
}

async function showAudit() {
  const events = await api("/api/audit?limit=30");
  const locale = state.lang === "es" ? "es-AR" : "en-GB";
  el("auditList").innerHTML = events.map(event => `<div class="audit-event"><strong>${event.event_type}</strong><time>${new Date(event.created_at).toLocaleString(locale)}</time><pre>${JSON.stringify(event.payload, null, 2)}</pre></div>`).join("");
  el("auditDialog").showModal();
}

async function init() {
  const health = await api("/health");
  state.recordingMode = Boolean(health.recording_mode);
  state.runtime = await api("/api/runtime").catch(() => ({ provider: health.provider, nemotron_runtime: health.provider !== "local" }));
  document.body.classList.toggle("recording-mode", state.recordingMode);
  applyLanguage(initialLanguage());
  if (!health.tavily_configured) {
    el("tavilyToggle").disabled = true;
    el("tavilyToggle").closest("label").title = t("tavily_disabled");
  }
  state.fields = await api("/api/fields"); selectField(state.fields[0].id); setExample("incomplete"); setupVoice();
  el("langButton").addEventListener("click", () => applyLanguage(state.lang === "es" ? "en" : "es"));
  el("incompleteExample").addEventListener("click", () => setExample("incomplete"));
  el("completeExample").addEventListener("click", () => setExample("complete"));
  el("analyzeButton").addEventListener("click", analyze);
  el("auditButton").addEventListener("click", showAudit);
  el("closeAudit").addEventListener("click", () => el("auditDialog").close());
}

init().catch(error => { el("captureMessage").textContent = error.message; });
