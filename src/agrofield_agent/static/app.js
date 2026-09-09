const state = { fields: [], selected: null, latest: null, recordingMode: false };

const incompleteNote = "Soja V3. La tormenta fue hace 18 horas y el acceso es seguro. Hay agua parada en aproximadamente 35% del lote. En los bajos conté 9 plantas por metro. El resto se ve heterogéneo.";
const completeNote = "Soja V3. La tormenta fue hace 18 horas y el acceso es seguro. Recorrí 6 puntos representativos en W. El anegamiento afecta 35% del lote y lleva 14 horas con agua parada. Conté 9 plantas por metro en los bajos. El estado general es heterogéneo.";

const labels = {
  crop_stage: "Estado", event_type: "Evento", event_hours_ago: "Antigüedad", access_safe: "Acceso",
  sample_points: "Puntos", affected_area_pct: "Área afectada", standing_water_pct: "Agua parada",
  water_duration_hours: "Duración agua", lodging_pct: "Vuelco", stem_damage_pct: "Daño de tallos",
  stand_count_per_m: "Stand"
};

const formats = {
  event_hours_ago: v => `${v} h`, access_safe: v => v ? "Seguro" : "Inseguro", sample_points: v => `${v}`,
  affected_area_pct: v => `${v}%`, standing_water_pct: v => `${v}%`, water_duration_hours: v => `${v} h`,
  lodging_pct: v => `${v}%`, stem_damage_pct: v => `${v}%`, stand_count_per_m: v => `${v} plantas/m`,
  event_type: v => ({flooding:"Anegamiento", hail:"Granizo", wind:"Viento", mixed:"Mixto", none:"Sin daño", unknown:"Desconocido"}[v] || v)
};

const el = id => document.getElementById(id);

async function api(url, options = {}) {
  const response = await fetch(url, { headers: {"Content-Type":"application/json"}, ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${response.status}`);
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
      <div class="field-meta"><span>${field.hectares} ha</span><span>prioridad ${fieldRiskScore(field)}</span><span>${field.weather.precipitation_mm_72h} mm</span></div>
      <div class="field-risk">${field.risk_flags[0] || "sin antecedente crítico"}</div>
    </button>`).join("");
  document.querySelectorAll("[data-field]").forEach(button => button.addEventListener("click", () => selectField(button.dataset.field)));
}

function renderHero(field) {
  const w = field.weather;
  el("fieldHero").classList.remove("skeleton");
  el("fieldHero").innerHTML = `
    <div class="hero-main">
      <div><p class="eyebrow">Lote seleccionado · ${field.crop}</p><h2>${field.name}</h2><p class="hero-sub">${field.hectares} ha · ${field.stage} · ${field.risk_flags.join(" · ") || "sin alertas históricas"}</p></div>
      <div class="weather-strip">
        <div class="weather-stat"><strong>${w.precipitation_mm_72h} mm</strong><small>lluvia · 72 h</small></div>
        <div class="weather-stat"><strong>${w.max_wind_gust_kmh} km/h</strong><small>ráfaga máxima</small></div>
        <div class="weather-stat"><strong>${w.forecast_rain_mm_48h} mm</strong><small>pronóstico · 48 h</small></div>
      </div>
    </div>`;
}

function selectField(id) {
  state.selected = state.fields.find(field => field.id === id);
  renderFields(); renderHero(state.selected);
  el("results").classList.add("hidden");
}

function setExample(kind) {
  el("rawNote").value = kind === "complete" ? completeNote : incompleteNote;
  el("completeExample").classList.toggle("active", kind === "complete");
  el("incompleteExample").classList.toggle("active", kind !== "complete");
}

function renderAnalysis(result) {
  state.latest = result;
  el("results").classList.remove("hidden");
  const ready = result.status === "review_ready";
  el("statusBanner").className = `status-banner ${ready ? "ready" : "blocked"}`;
  el("statusBanner").innerHTML = `
    <div><strong>${ready ? "Evidencia lista para revisión" : `Decisión bloqueada · faltan ${result.missing_critical.length} controles`}</strong>
    <small>${ready ? "El asesor puede revisar las tareas; nada se ejecuta solo." : "La nota se conserva, pero el sistema no completa datos ausentes."}</small></div>
    <div class="score-pill"><strong>${result.priority_score}</strong><small>prioridad / 100</small></div>`;
  el("latencyBadge").textContent = `${result.telemetry.model} · ${Math.round(result.telemetry.latency_ms)} ms`;

  el("evidenceGrid").innerHTML = Object.keys(labels).map(key => {
    const value = result.observation[key];
    const missing = value === null || value === undefined || value === "unknown";
    const quote = result.observation.evidence_quotes[key];
    return `<div class="evidence-item ${missing ? "missing" : ""}"><small>${labels[key]}</small><strong>${missing ? "No informado" : (formats[key] ? formats[key](value) : value)}</strong>${quote ? `<em>“${quote}”</em>` : ""}</div>`;
  }).join("");

  if (result.followup_questions.length) {
    el("questionsTitle").textContent = "Preguntas pendientes";
    el("questionList").innerHTML = result.followup_questions.map((q, i) => `<div class="question-item"><span class="question-index">${i+1}</span><span>${q}</span></div>`).join("");
  } else {
    el("questionsTitle").textContent = "Control completo";
    el("questionList").innerHTML = `<div class="question-empty">No se detectaron omisiones críticas para este tipo de evento. La evidencia sigue requiriendo revisión humana.</div>`;
  }

  el("taskList").innerHTML = result.proposed_tasks.map(task => `
    <div class="task-item" id="task-${task.id}">
      <span class="priority-dot ${task.priority}"></span>
      <div class="task-copy"><strong>${task.title}</strong><small>${task.rationale} · vence en ${task.due_hours} h</small></div>
      <div class="task-actions"><button class="reject" data-reject="${task.id}">Rechazar</button><button class="approve" data-approve="${task.id}">Aprobar</button></div>
    </div>`).join("");
  document.querySelectorAll("[data-approve]").forEach(b => b.addEventListener("click", () => decideTask(b.dataset.approve, "approve")));
  document.querySelectorAll("[data-reject]").forEach(b => b.addEventListener("click", () => decideTask(b.dataset.reject, "reject")));

  const alerts = result.official_alerts || [];
  el("alertsCard").classList.toggle("hidden", !alerts.length);
  el("alertList").innerHTML = alerts.map(alert => `<div class="alert-item"><a href="${alert.url}" target="_blank" rel="noopener">${alert.title}</a><p>${alert.snippet}</p></div>`).join("");
  el("results").scrollIntoView({behavior: state.recordingMode ? "auto" : "smooth", block:"start"});
}

async function analyze() {
  const note = el("rawNote").value.trim();
  if (!state.selected || note.length < 5) return;
  el("analyzeButton").disabled = true; el("analyzeButton").textContent = "Analizando…"; el("captureMessage").textContent = "";
  try {
    const result = await api("/api/analyze", {method:"POST", body: JSON.stringify({field_id: state.selected.id, raw_text: note, use_tavily: el("tavilyToggle").checked})});
    renderAnalysis(result);
  } catch (error) { el("captureMessage").textContent = error.message; }
  finally { el("analyzeButton").disabled = false; el("analyzeButton").innerHTML = "Analizar evidencia <span>→</span>"; }
}

async function decideTask(taskId, action) {
  const reviewer = el("reviewerName").value.trim();
  if (reviewer.length < 2) { el("captureMessage").textContent = "Indicá quién revisa la tarea."; return; }
  const decisionNote = state.recordingMode ? "Decisión registrada durante ensayo local sintético" : "Decisión registrada desde AgroField Agent";
  const task = await api(`/api/tasks/${taskId}/${action}`, {method:"POST", body: JSON.stringify({reviewer, decision_note: decisionNote})});
  const node = el(`task-${taskId}`); node.classList.add("decided");
  const statusLabel = {approved:"APROBADA", rejected:"RECHAZADA"}[task.status] || task.status;
  node.querySelector(".task-actions").innerHTML = `<span class="task-status">${statusLabel}</span>`;
}

function setupVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) { el("voiceButton").title = "El navegador no ofrece dictado; usá el campo de texto"; return; }
  const recognition = new SpeechRecognition(); recognition.lang = "es-AR"; recognition.interimResults = false;
  recognition.onstart = () => { el("voiceButton").classList.add("recording"); el("voiceButton").textContent = "Escuchando…"; };
  recognition.onend = () => { el("voiceButton").classList.remove("recording"); el("voiceButton").innerHTML = "<span>●</span> Dictar"; };
  recognition.onresult = event => { const text = event.results[0][0].transcript; el("rawNote").value = `${el("rawNote").value.trim()} ${text}`.trim(); };
  el("voiceButton").addEventListener("click", () => recognition.start());
}

async function showAudit() {
  const events = await api("/api/audit?limit=30");
  el("auditList").innerHTML = events.map(event => `<div class="audit-event"><strong>${event.event_type}</strong><time>${new Date(event.created_at).toLocaleString("es-AR")}</time><pre>${JSON.stringify(event.payload, null, 2)}</pre></div>`).join("");
  el("auditDialog").showModal();
}

async function init() {
  const health = await api("/health");
  state.recordingMode = Boolean(health.recording_mode);
  el("providerBadge").textContent = state.recordingMode ? "ENSAYO LOCAL · SINTÉTICO" : (health.provider === "local" ? "modo local · $0" : "Nemotron · Token Factory");
  document.body.classList.toggle("recording-mode", state.recordingMode);
  if (!health.tavily_configured) {
    el("tavilyToggle").disabled = true;
    el("tavilyToggle").closest("label").title = "Configurá TAVILY_API_KEY para activar alertas en runtime";
  }
  state.fields = await api("/api/fields"); selectField(state.fields[0].id); setExample("incomplete"); setupVoice();
  el("incompleteExample").addEventListener("click", () => setExample("incomplete"));
  el("completeExample").addEventListener("click", () => setExample("complete"));
  el("analyzeButton").addEventListener("click", analyze);
  el("auditButton").addEventListener("click", showAudit);
  el("closeAudit").addEventListener("click", () => el("auditDialog").close());
}

init().catch(error => { el("captureMessage").textContent = error.message; });
