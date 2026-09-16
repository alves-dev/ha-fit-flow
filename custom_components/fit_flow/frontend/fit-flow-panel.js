const esc = (value) => String(value ?? "").replace(/[&<>\"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[char]));

class FitFlowPanel extends HTMLElement {
  set hass(value) { this._hass = value; if (!this._booted) this.boot(); }

  async boot() {
    this._booted = true; this._view = "today"; this.renderShell(); await this.load();
  }

  async load() {
    try {
      this._data = await this._hass.callWS({type: "fit_flow/config/get"});
      this.renderContent();
    } catch (error) {
      const content = this.querySelector("#content");
      if (content) content.innerHTML = `<div class="card"><h2>FitFlow não conseguiu carregar</h2><p>${esc(error?.message || "Erro de comunicação com o Home Assistant")}</p><button data-retry>Tentar novamente</button></div>`;
    }
  }

  renderShell() {
    this.innerHTML = `<style>
      :host { display:block; padding:32px; color:var(--primary-text-color); background:var(--primary-background-color); min-height:100vh; box-sizing:border-box; }
      .app { max-width:1180px; margin:auto; } .top { display:flex; align-items:center; justify-content:space-between; gap:24px; margin-bottom:28px; }
      h1,h2,h3 { margin:0 0 8px; } p { color:var(--secondary-text-color); } .tabs { display:flex; gap:8px; flex-wrap:wrap; }
      button { border:0; border-radius:var(--ha-control-button-border-radius,20px); padding:10px 16px; background:var(--primary-color); color:var(--text-primary-color,var(--primary-text-color)); cursor:pointer; font:inherit; transition:filter .15s, transform .15s; }
      button:hover { filter:brightness(1.08); transform:translateY(-1px); } button.secondary { background:var(--secondary-background-color); color:var(--primary-text-color); } .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:18px; }
      .card { background:var(--card-background-color); border-radius:var(--ha-card-border-radius,12px); padding:22px; box-shadow:var(--ha-card-box-shadow,none); }
      .hero { border-left:5px solid var(--primary-color); } .muted { color:var(--secondary-text-color); } .row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px 0; border-bottom:1px solid var(--divider-color); }
      .row:last-child { border:0; } .actions { display:flex; gap:8px; flex-wrap:wrap; } label { display:block; margin:10px 0 5px; color:var(--secondary-text-color); }
      input,select { width:100%; box-sizing:border-box; padding:10px; border:1px solid var(--divider-color); border-radius:8px; background:var(--input-fill-color,var(--secondary-background-color)); color:var(--primary-text-color); font:inherit; } select { cursor:pointer; }
      form { max-width:600px; } .section-title { margin-top:28px; } .check { display:flex; align-items:center; gap:8px; padding:8px 0; } .check input { width:auto; } .blocked { color:var(--error-color); } .hint { font-size:.9em; } .req { display:grid; grid-template-columns:1fr 90px auto; gap:8px; align-items:end; margin:8px 0; }
      .config-sections { display:flex; flex-direction:column; gap:18px; } .config-section { width:100%; box-sizing:border-box; } .section-header { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; } .section-header h2 { margin-bottom:4px; } .section-count { color:var(--secondary-text-color); font-size:.9em; white-space:nowrap; } .section-toolbar { display:grid; grid-template-columns:minmax(0,2fr) minmax(180px,1fr); gap:10px; margin:18px 0 8px; } .exercise-row > span { min-width:0; } .exercise-row .exercise-link + span { min-width:0; } .exercise-name { font-weight:500; } .empty-filter { padding:16px 0 8px; color:var(--secondary-text-color); } .exercise-list { max-height:620px; overflow:auto; padding-right:4px; }
      .workout-count { display:flex; align-items:baseline; gap:6px; margin:14px 0 6px; } .workout-count strong { font-size:1.5em; } .workout-count span { color:var(--secondary-text-color); font-size:.9em; } .workout-chart { block-size:6px; margin:0 0 16px; overflow:hidden; border-radius:999px; background:var(--divider-color); } .workout-chart span { display:block; block-size:100%; border-radius:inherit; background:var(--primary-color); }
      .exercise-frequency { color:var(--secondary-text-color); font-weight:400; }
      .date-heading { margin:28px 0 10px; font-size:1.05em; color:var(--primary-text-color); } .history-item { display:block; padding:16px 0; border-bottom:1px solid var(--divider-color); } .history-item:last-child { border:0; } .history-top { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; } .history-name { font-size:1.05em; font-weight:600; } .history-meta { margin-top:5px; color:var(--secondary-text-color); font-size:.9em; } .badge { display:inline-block; padding:4px 9px; border-radius:12px; background:var(--secondary-background-color); color:var(--secondary-text-color); font-size:.78em; white-space:nowrap; } .history-details { margin-top:10px; color:var(--secondary-text-color); } .history-details summary { cursor:pointer; color:var(--primary-color); } .exercise-link { display:inline-flex; align-items:center; gap:8px; color:var(--primary-text-color); } .exercise-image { width:54px; height:54px; border-radius:8px; object-fit:cover; vertical-align:middle; background:var(--secondary-background-color); }
      @media(max-width:600px){ :host{padding:12px;} .top{align-items:flex-start; flex-direction:column;} .section-toolbar{grid-template-columns:1fr;} .section-header{display:block;} .section-count{display:block; margin-top:6px;} .req{grid-template-columns:1fr 80px;} }
      button:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible, a:focus-visible { outline:2px solid var(--primary-color); outline-offset:2px; }
    </style><div class="app"><div class="top"><div><h1>FitFlow</h1><p>Treinos flexíveis, escolhidos pelo seu histórico.</p></div><div class="tabs"><button data-view="today">Hoje</button><button data-view="history">Histórico</button><button data-view="config">Configuração</button></div></div><main id="content" aria-live="polite"><div class="card"><p>Carregando FitFlow...</p></div></main></div>`;
    this.addEventListener("click", (event) => this.handleClick(event)); this.addEventListener("input", (event) => this.handleInput(event)); this.addEventListener("submit", (event) => this.handleSubmit(event));
  }

  renderContent() { const content = this.querySelector("#content"); if (content) content.innerHTML = this._view === "history" ? this.historyView() : this._view === "config" ? this.configView() : this.todayView(); }

  todayView() {
    const data = this._data, rec = data.recommendation || {}, active = data.active_session;
    if (active) {
      const workout = data.workouts.find((item) => item.id === active.workout_id) || {name: active.workout_id, requirements: []}; const selected = active.selected_exercise_ids || [];
      const groups = workout.requirements.map((req) => { const options = data.exercises.filter((item) => item.muscle_group_id === req.muscle_group_id).sort((left, right) => this.exerciseCount(left.id) - this.exerciseCount(right.id) || left.name.localeCompare(right.name, "pt-BR")); const planned = Number(req.exercise_count || 0); return `<section class="card"><h3>${esc(this.groupName(req.muscle_group_id))} <span class="muted">${selected.filter((id) => options.some((x) => x.id === id)).length}/${planned}</span></h3>${options.map((item) => { const count = this.exerciseCount(item.id); return `<label class="check"><input type="checkbox" data-exercise="${esc(item.id)}" ${selected.includes(item.id) ? "checked" : ""}> ${this.imageMarkup(item)} <span>${esc(item.name)} <small class="exercise-frequency">(${count} vez${count === 1 ? "" : "es"})</small></span></label>`; }).join("")}</section>`; }).join("");
      return `<div class="card hero"><h2>${esc(workout.name)}</h2><p>Treino em andamento desde ${esc(this.compactDate(active.started_at))}</p><div class="actions"><button data-action="finish">Finalizar treino</button><button class="secondary" data-action="cancel">Cancelar</button></div></div><div class="grid section-title">${groups || '<div class="card"><p>Adicione requisitos ao treino na Configuração.</p></div>'}</div>`;
    }
    const workout = data.workouts.find((item) => item.id === rec.workout_id);
    const alternate = data.workouts.find((item) => item.id === rec.alternate_workout_id);
    return `<div class="card hero"><h2>${workout ? esc(workout.name) : "Nenhum treino disponível"}</h2><p>${workout ? "Este é o próximo treino recomendado com base no seu histórico." : (rec.next_available_at ? `Próxima disponibilidade: ${this.dateMarkup(rec.next_available_at)}` : "Configure treinos e regras para começar.")}</p><div class="actions"><button data-action="check">Verificar recomendação agora</button>${workout ? `<button class="secondary" data-start="${esc(workout.id)}">Começar treino</button>` : ""}</div>${alternate ? `<p class="hint">Alternativa se o primeiro treino não puder ser feito: <strong>${esc(alternate.name)}</strong> <button class="secondary" data-start="${esc(alternate.id)}">Escolher alternativa</button></p>` : ""}</div><h2 class="section-title">Treinos configurados</h2><div class="grid">${data.workouts.map((item) => { const count = this.workoutCount(item.id); return `<div class="card"><h3>${esc(item.name)}</h3><p>${this.totalPlanned(item)} exercícios planejados</p><div class="workout-count"><strong>${count}</strong><span>vez${count === 1 ? "" : "es"} feito${count === 1 ? "" : "s"}</span></div>${this.workoutChart(count)}<button class="secondary" data-start="${esc(item.id)}">Escolher</button>${rec.blocked_workouts?.[item.id] ? `<p class="blocked">${this.blockedMarkup(rec.blocked_workouts[item.id].until)}</p>` : ""}</div>`; }).join("") || '<div class="card"><p>Nenhum treino cadastrado.</p></div>'}</div>`;
  }

  historyView() {
    const sorted = [...this._data.history].sort((left, right) => this.historyTimestamp(right) - this.historyTimestamp(left));
    const groups = sorted.reduce((result, item) => { const day = this.formatDate(item.finished_at || item.performed_at, false); (result[day] ||= []).push(item); return result; }, {});
    const content = Object.entries(groups).map(([day, items]) => `<section><h3 class="date-heading">${esc(day)}</h3>${items.map((item) => this.historyItem(item)).join("")}</section>`).join("");
    return `<div class="card"><h2>Histórico</h2><p class="hint">Atividades mais recentes aparecem primeiro.</p>${content || "<p>Nenhuma atividade registrada ainda.</p>"}</div>`;
  }

  historyItem(item) {
    const isWorkout = item.kind === "workout";
    const name = item.workout_name || item.activity_name || "Atividade";
    const duration = isWorkout ? this.workoutDuration(item) : (item.duration_minutes ? `${item.duration_minutes} min` : "Duração não informada");
    const exercises = isWorkout && item.exercises?.length ? `<details class="history-details"><summary>Ver exercícios (${item.exercises.length})</summary><ul>${item.exercises.map((exercise) => `<li>${this.imageMarkup({name: exercise.exercise_name, image_url: exercise.image_url})} ${esc(exercise.exercise_name || exercise.exercise_id)}</li>`).join("")}</ul></details>` : "";
    return `<article class="history-item"><div class="history-top"><div><div class="history-name">${esc(name)}</div><div class="history-meta">${esc(this.formatDate(item.finished_at || item.performed_at, true))} · ${esc(duration)}</div></div><div class="actions"><span class="badge">${isWorkout ? "Treino" : "Atividade"}</span><button class="secondary" data-delete="history" data-id="${esc(item.id)}">Excluir</button></div></div>${exercises}</article>`;
  }

  historyTimestamp(item) { const timestamp = Date.parse(item.finished_at || item.performed_at || ""); return Number.isNaN(timestamp) ? 0 : timestamp; }
  formatDate(value, includeTime = true) { const date = new Date(value); if (Number.isNaN(date.getTime())) return "Data não informada"; return new Intl.DateTimeFormat("pt-BR", {dateStyle:"long", ...(includeTime ? {timeStyle:"short"} : {})}).format(date); }
  dateMarkup(value) { const formatted = this.formatDate(value); return `<time datetime="${esc(value)}" title="${esc(value)}">${esc(formatted)}</time>`; }
  compactDate(value) { const date = new Date(value); if (Number.isNaN(date.getTime())) return "Data não informada"; const pad = (part) => String(part).padStart(2, "0"); return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`; }
  blockedMarkup(value) { return `Bloqueado até ${this.dateMarkup(value)}`; }
  exerciseCount(exerciseId) { return this._data.history.reduce((count, item) => count + (item.kind === "workout" ? (item.exercises || []).filter((exercise) => exercise.exercise_id === exerciseId).length : 0), 0); }
  workoutCount(workoutId) { return this._data.history.filter((item) => item.kind === "workout" && item.workout_id === workoutId).length; }
  workoutChart(count) { const max = Math.max(1, ...this._data.workouts.map((item) => this.workoutCount(item.id))); const width = Math.round((count / max) * 100); return `<div class="workout-chart" role="img" aria-label="${count} treino(s) concluído(s)"><span style="inline-size:${width}%"></span></div>`; }
  workoutDuration(item) { const start = Date.parse(item.started_at || ""), end = Date.parse(item.finished_at || ""); if (Number.isNaN(start) || Number.isNaN(end)) return "Duração não informada"; const minutes = Math.max(0, Math.round((end - start) / 60000)); return minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)}h ${minutes % 60}min`; }

  configView() {
    return `<div class="config-sections">
      ${this.simpleConfigCard("muscle_groups", "1. Grupos musculares", "Cadastre as regiões do corpo usadas para organizar exercícios e treinos.")}
      <section class="card config-section"><div class="section-header"><div><h2>2. Exercícios</h2><p class="hint">Use a busca ou filtre por grupo para encontrar rapidamente um exercício.</p></div><span class="section-count" data-exercise-count>${this._data.exercises.length} exercício(s)</span></div><div class="section-toolbar"><input data-exercise-search type="search" placeholder="Buscar exercício..." aria-label="Buscar exercício"><select data-exercise-filter aria-label="Filtrar por grupo muscular"><option value="">Todos os grupos</option>${this._data.muscle_groups.map((item) => `<option value="${esc(item.id)}">${esc(item.name)}</option>`).join("")}</select></div><div class="exercise-list" data-exercise-list>${this.exerciseRows()}</div><details><summary>Adicionar exercício</summary><form data-collection="exercises"><label>Nome<input name="name" required></label><label>Grupo muscular<select name="muscle_group_id" required>${this.groupOptions()}</select></label><label>Link da imagem (opcional)<input name="image_url" type="url" placeholder="https://exemplo.com/aparelho.jpg"><span class="hint">Use um link público direto para uma imagem.</span></label><button>Salvar exercício</button></form></details></section>
      <section class="card config-section"><div class="section-header"><div><h2>3. Treinos</h2><p class="hint">Cada treino é formado por grupos musculares e uma quantidade de exercícios.</p></div><span class="section-count">${this._data.workouts.length} treino(s)</span></div>${this._data.workouts.map((item) => this._editingWorkoutId === item.id ? this.workoutEditForm(item) : `<div class="row"><div><strong>${esc(item.name)}</strong><div class="muted">${this.workoutRequirements(item)} · ${this.totalPlanned(item)} no total</div></div><div class="actions"><button class="secondary" data-edit-workout="${esc(item.id)}">Editar</button><button class="secondary" data-delete="workouts" data-id="${esc(item.id)}">Excluir</button></div></div>`).join("") || "<p>Nenhum treino.</p>"}<details><summary>Adicionar treino</summary><form data-collection="workouts"><label>Nome<input name="name" required></label><div data-requirements><div class="req"><select name="requirement_group" required>${this.groupOptions()}</select><input name="requirement_count" type="number" min="1" value="1" required></div></div><button type="button" class="secondary" data-add-requirement>+ Adicionar grupo</button> <button>Salvar treino</button></form></details></section>
      ${this.simpleConfigCard("activities", "4. Atividades externas", "Registre corrida, vôlei e outras atividades fora da academia.")}
      <section class="card config-section"><div class="section-header"><div><h2>5. Regras de recuperação</h2><p class="hint">As regras são direcionais: a origem bloqueia o treino de destino.</p></div><span class="section-count">${this._data.conflict_rules.length} regra(s)</span></div>${this._data.conflict_rules.map((item) => `<div class="row"><span>${esc(this.sourceName(item))} → ${esc(this.workoutName(item.target_workout_id))}<small class="muted"> · ${item.recovery_hours} h</small></span><button class="secondary" data-delete="conflict_rules" data-id="${esc(item.id)}">Excluir</button></div>`).join("") || "<p>Nenhuma regra.</p>"}<details><summary>Adicionar regra</summary><form data-collection="conflict_rules"><label>Origem<select name="source_id" required>${this.sourceOptions()}</select></label><label>Treino bloqueado<select name="target_workout_id" required>${this.workoutOptions()}</select></label><label>Recuperação (horas)<input name="recovery_hours" type="number" min="1" value="24" required></label><button>Salvar regra</button></form></details></section>
    </div>`;
  }

  simpleConfigCard(collection, title, hint) { return `<section class="card config-section"><div class="section-header"><div><h2>${title}</h2><p class="hint">${hint}</p></div><span class="section-count">${this._data[collection].length} registro(s)</span></div>${this._data[collection].map((item) => `<div class="row"><span>${esc(item.name)}</span><button class="secondary" data-delete="${collection}" data-id="${esc(item.id)}">Excluir</button></div>`).join("") || "<p>Nenhum registro.</p>"}<details><summary>Adicionar</summary><form data-collection="${collection}"><label>Nome<input name="name" required></label><button>Salvar</button></form></details></section>`; }
  exerciseRows() { return this._data.exercises.map((item) => this._editingExerciseId === item.id ? `<div class="exercise-row">${this.exerciseEditForm(item)}</div>` : `<div class="row exercise-row" data-exercise-row data-search="${esc(`${item.name} ${this.groupName(item.muscle_group_id)}`.toLocaleLowerCase())}" data-group="${esc(item.muscle_group_id)}"><span>${this.imageMarkup(item)} <span class="exercise-name">${esc(item.name)}</span><small class="muted"> · ${esc(this.groupName(item.muscle_group_id))}</small></span><div class="actions"><button class="secondary" data-edit-exercise="${esc(item.id)}">Editar</button><button class="secondary" data-delete="exercises" data-id="${esc(item.id)}">Excluir</button></div></div>`).join("") || "<p>Nenhum exercício.</p>"; }
  groupOptions(selectedId = "") { return this._data.muscle_groups.map((item) => `<option value="${esc(item.id)}" ${item.id === selectedId ? "selected" : ""}>${esc(item.name)}</option>`).join("") || '<option value="">Cadastre um grupo primeiro</option>'; }
  workoutOptions() { return this._data.workouts.map((item) => `<option value="${esc(item.id)}">${esc(item.name)}</option>`).join("") || '<option value="">Cadastre um treino primeiro</option>'; }
  sourceOptions() { return [...this._data.workouts.map((item) => `<option value="${esc(item.id)}">Treino · ${esc(item.name)}</option>`), ...this._data.activities.map((item) => `<option value="${esc(item.id)}">Atividade · ${esc(item.name)}</option>`)].join(""); }
  sourceName(item) { const source = item.source_type === "activity" ? this._data.activities.find((x) => x.id === item.source_id) : this._data.workouts.find((x) => x.id === item.source_id); return `${item.source_type === "activity" ? "Atividade" : "Treino"} · ${source?.name || item.source_id}`; }
  totalPlanned(item) { return (item.requirements || []).reduce((sum, req) => sum + Number(req.exercise_count || 0), 0); }
  imageMarkup(item) { const url = String(item.image_url || ""); if (!/^https?:\/\//i.test(url)) return ""; return `<a class="exercise-link" href="${esc(url)}" target="_blank" rel="noreferrer" title="Abrir imagem"><img class="exercise-image" src="${esc(url)}" alt="Imagem de ${esc(item.name || "exercício")}" loading="lazy"></a>`; }
  workoutRequirements(item) { return (item.requirements || []).map((req) => `${esc(this.groupName(req.muscle_group_id))} × ${Number(req.exercise_count || 0)}`).join(", ") || "Sem grupos configurados"; }
  workoutEditForm(item) { return `<form class="edit-workout" data-collection="workouts" data-item-id="${esc(item.id)}"><label>Nome<input name="name" value="${esc(item.name)}" required></label><div data-requirements>${(item.requirements || []).map((req) => `<div class="req"><select name="requirement_group" required>${this.groupOptions(req.muscle_group_id)}</select><input name="requirement_count" type="number" min="1" value="${Number(req.exercise_count || 1)}" required></div>`).join("") || `<div class="req"><select name="requirement_group" required>${this.groupOptions()}</select><input name="requirement_count" type="number" min="1" value="1" required></div>`}</div><div class="actions"><button type="button" class="secondary" data-add-requirement>+ Adicionar grupo</button><button>Salvar alterações</button><button type="button" class="secondary" data-cancel-edit>Cancelar</button></div></form>`; }
  exerciseEditForm(item) { return `<form data-collection="exercises" data-item-id="${esc(item.id)}"><label>Nome<input name="name" value="${esc(item.name)}" required></label><label>Grupo muscular<select name="muscle_group_id" required>${this.groupOptions(item.muscle_group_id)}</select></label><label>Link da imagem (opcional)<input name="image_url" type="url" value="${esc(item.image_url || "")}" placeholder="https://exemplo.com/aparelho.jpg"></label><div class="actions"><button>Salvar alterações</button><button type="button" class="secondary" data-cancel-exercise>Cancelar</button></div></form>`; }

  groupName(id) { return this._data.muscle_groups.find((x) => x.id === id)?.name || id; }
  workoutName(id) { return this._data.workouts.find((x) => x.id === id)?.name || id; }
  handleInput(event) {
    if (!event.target.matches("[data-exercise-search], [data-exercise-filter]")) return;
    const section = event.target.closest(".config-section");
    const search = section.querySelector("[data-exercise-search]").value.trim().toLocaleLowerCase();
    const group = section.querySelector("[data-exercise-filter]").value;
    const rows = [...section.querySelectorAll("[data-exercise-row]")];
    let visible = 0;
    rows.forEach((row) => {
      const matches = (!search || row.dataset.search.includes(search)) && (!group || row.dataset.group === group);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    let empty = section.querySelector("[data-filter-empty]");
    if (visible === 0 && rows.length) {
      if (!empty) {
        empty = document.createElement("p");
        empty.className = "empty-filter";
        empty.dataset.filterEmpty = "";
        empty.textContent = "Nenhum exercício corresponde ao filtro.";
        section.querySelector("[data-exercise-list]").append(empty);
      }
    } else if (empty) {
      empty.remove();
    }
    const count = section.querySelector("[data-exercise-count]");
    if (count) count.textContent = `${visible} de ${rows.length} exercício(s)`;
  }
  async handleClick(event) {
    if (event.target.closest("[data-retry]")) { await this.load(); return; }
    const checkbox = event.target.closest("[data-exercise]");
    if (checkbox) {
      const selected = [...this.querySelectorAll("[data-exercise]:checked")].map((x) => x.dataset.exercise);
      await this.callSession("update", {selected_exercise_ids: selected});
      return;
    }
    const view = event.target.closest("[data-view]"); if (view) { this._view = view.dataset.view; this.renderContent(); return; }
    const editWorkout = event.target.closest("[data-edit-workout]");
    if (editWorkout) { this._editingWorkoutId = editWorkout.dataset.editWorkout; this.renderContent(); return; }
    const editExercise = event.target.closest("[data-edit-exercise]");
    if (editExercise) { this._editingExerciseId = editExercise.dataset.editExercise; this.renderContent(); return; }
    if (event.target.closest("[data-cancel-edit]")) { this._editingWorkoutId = null; this.renderContent(); return; }
    if (event.target.closest("[data-cancel-exercise]")) { this._editingExerciseId = null; this.renderContent(); return; }
    const addRequirement = event.target.closest("[data-add-requirement]");
    if (addRequirement) {
      const form = addRequirement.closest("form");
      form.querySelector("[data-requirements]").insertAdjacentHTML("beforeend", `<div class="req"><select name="requirement_group" required>${this.groupOptions()}</select><input name="requirement_count" type="number" min="1" value="1" required></div>`);
      return;
    }
    const start = event.target.closest("[data-start]"); if (start) { await this.callSession("start", {workout_id:start.dataset.start}); return; }
    const action = event.target.closest("[data-action]"); if (action) { if (action.dataset.action === "check") { await this._hass.callWS({type:"fit_flow/recommendation/check"}); await this.load(); return; } const selected = [...this.querySelectorAll("[data-exercise]:checked")].map((x) => x.dataset.exercise); await this.callSession(action.dataset.action, action.dataset.action === "finish" ? {} : {selected_exercise_ids:selected}); return; }
    const del = event.target.closest("[data-delete]"); if (del && confirm("Excluir este item?")) { await this._hass.callWS({type:"fit_flow/mutate", collection:del.dataset.delete, item_id:del.dataset.id, delete:true}); await this.load(); }
  }
  async handleSubmit(event) {
    const form = event.target.closest("form[data-collection]"); if (!form) return; event.preventDefault();
    const collection = form.dataset.collection; const item = Object.fromEntries(new FormData(form));
    if (collection === "workouts") {
      const groups = [...form.querySelectorAll('[name="requirement_group"]')]; const counts = [...form.querySelectorAll('[name="requirement_count"]')];
      item.requirements = groups.map((select, index) => ({muscle_group_id: select.value, exercise_count: Number(counts[index].value)}));
      delete item.requirement_group; delete item.requirement_count;
    }
    if (collection === "conflict_rules") item.source_type = this._data.activities.some((x) => x.id === item.source_id) ? "activity" : "workout";
    const message = {type:"fit_flow/mutate", collection, item};
    if (form.dataset.itemId) message.item_id = form.dataset.itemId;
    await this._hass.callWS(message); this._editingWorkoutId = null; this._editingExerciseId = null; form.reset(); await this.load();
  }
  async callSession(operation, extra = {}) { await this._hass.callWS({type:"fit_flow/session", operation, ...extra}); await this.load(); }
}
customElements.define("fit-flow-panel", FitFlowPanel);
