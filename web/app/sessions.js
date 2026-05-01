import {
  API,
  CONTEXT_MENTIONS,
  DOM,
  VALID_SESSION_TYPES,
  appRuntime,
  displayNodeTitle,
  fetchJson,
  findNodeInHierarchy,
  html,
  nodeDetails,
  parentScopeId,
  setCurrentSessionId,
  setWorkspaceTab,
  shortName,
  state,
  statusBadge,
  t,
  unique,
} from './ui_core.js';
import { manuscriptHasDirtyChanges } from './manuscript.js';

function selectedSessionType() {
  const el = document.getElementById('session-type-select');
  const value = el?.value || state.sessionType;
  return VALID_SESSION_TYPES.has(value) ? value : 'node';
}

function currentSession() {
  const session = state.sessions.find((item) => item.id === state.currentSessionId) || null;
  return session && sessionMatchesContext(session) ? session : null;
}

function sessionTypeLabel(type) {
  return ({ general: t('sessionGeneral'), scope: t('sessionScope'), node: t('sessionNode') })[type] || type;
}

function sessionDraftContext() {
  const type = selectedSessionType();
  const inputNode = document.getElementById('target-node-input')?.value.trim() || '';
  const targetNode = type === 'node' ? (inputNode || state.selectedNodeId || null) : null;
  const targetScope = type === 'node' && targetNode
    ? (parentScopeId(targetNode) || state.activeScopeId || null)
    : (type === 'scope' ? (state.activeScopeId || null) : null);
  if (type === 'node') {
    return {
      session_type: 'node',
      target_node: targetNode,
      target_scope: targetScope,
      label: targetNode ? shortName(targetNode) : t('targetMissing'),
      path: nodeDetails(targetNode)?.path || targetNode || '',
    };
  }
  if (type === 'scope') {
    const scope = findNodeInHierarchy(targetScope);
    return {
      session_type: 'scope',
      target_node: null,
      target_scope: targetScope,
      label: scope ? displayNodeTitle(scope.name) : t('scopeMissing'),
      path: scope?.path || targetScope || '',
    };
  }
  return {
    session_type: 'general',
    target_node: null,
    target_scope: null,
    label: t('repoRoot'),
    path: '',
  };
}

function contextKey(context = sessionDraftContext()) {
  if (context.session_type === 'node' && context.target_node) return `node::${context.target_node}`;
  if (context.session_type === 'scope' && context.target_scope) return `scope::${context.target_scope}`;
  return context.session_type === 'general' ? 'general' : '';
}

function sessionMatchesContext(session, context = sessionDraftContext()) {
  const key = contextKey(context);
  if (key && session.context_key) return session.context_key === key;
  if (context.session_type === 'node') return session.session_type === 'node' && session.target_node === context.target_node;
  if (context.session_type === 'scope') return session.session_type === 'scope' && session.target_scope === context.target_scope;
  return session.session_type === 'general' && !session.target_node && !session.target_scope;
}

function visibleSessions(context = sessionDraftContext()) {
  return state.sessions.filter((session) => sessionMatchesContext(session, context));
}

function syncCurrentSessionToContext() {
  const sessions = visibleSessions();
  if (sessions.some((session) => session.id === state.currentSessionId)) return;
  setCurrentSessionId(sessions[0]?.id || null);
}

function actionPrompt(action, context = sessionDraftContext()) {
  const header = [
    `Session type: ${context.session_type}`,
    context.target_node ? `Target node: ${context.target_node}` : '',
    context.target_scope ? `Target scope: ${context.target_scope}` : '',
    context.path ? `Path: ${context.path}` : '',
  ].filter(Boolean).join('\n');
  const prompts = {
    analyze: `Read the selected graph context only. Summarize status, local skill route, blockers, and the smallest next bounded action. Do not modify files.\n\n${header}`,
    blockers: `Explain why this graph context is not flowing smoothly. Return blocking gaps, missing local contracts, missing artifacts, and the smallest next fixes. Do not modify files.\n\n${header}`,
    experiment: `Suggest the next bounded experiment for this graph context. Use baseline -> experiment -> keep/discard -> state update discipline. Do not leave the selected context.\n\n${header}`,
    run_bounded: `Run one bounded worker step for this graph context. Read graph status first, then local README/status/skills. Execute at most one bounded control unit and report exact files changed or proposed.\n\n${header}`,
    draft: `Draft a concise proposal for this graph context. Put emphasis on objective, acceptance criteria, risks, and the next bounded action. Do not modify canonical graph files.\n\n${header}`,
  };
  return prompts[action] || prompts.analyze;
}

function renderPromptActionChip(action, label, disabled) {
  return `<button class="action-chip" data-action="${action}" type="button" ${disabled ? 'disabled' : ''}>${t(label)}</button>`;
}

function renderPromptActions() {
  const root = document.getElementById('prompt-actions');
  if (!root) return;
  const context = sessionDraftContext();
  const disabled = context.session_type === 'node' && !context.target_node;
  const actions = [
    ['analyze', 'actionAnalyze'],
    ['blockers', 'actionBlockers'],
    ['experiment', 'actionExperiment'],
    ['run_bounded', 'actionRunBounded'],
    ['draft', 'actionDraft'],
  ];
  root.innerHTML = actions.map(([action, label]) => renderPromptActionChip(action, label, disabled)).join('');
  root.querySelectorAll('[data-action]').forEach((button) => {
    button.addEventListener('click', () => {
      document.getElementById('agent-prompt').value = actionPrompt(button.dataset.action);
      renderAgentControls();
    });
  });
}

function renderNodeOptions() {
  const list = document.getElementById('node-options');
  if (!list) return;
  const nodes = state.data?.details?.nodes || {};
  list.innerHTML = Object.entries(nodes).map(([id, detail]) => `<option value="${html(id)}">${html(displayNodeTitle(detail.title || id))}</option>`).join('');
}

function mentionCandidates(query) {
  const q = query.toLowerCase();
  const contextItems = CONTEXT_MENTIONS
    .filter((token) => token.slice(1).toLowerCase().includes(q))
    .map((token) => ({
      value: token,
      title: token,
      detail: {
        '@current': t('currentSession'),
        '@scope': t('boundScope'),
        '@node': t('boundNode'),
        '@readme': t('readme'),
        '@status': t('statusFile'),
        '@manuscript': t('manuscriptMode'),
      }[token],
    }));
  const nodes = Object.entries(state.data?.details?.nodes || {});
  const nodeItems = nodes
    .filter(([id, detail]) => {
      const title = detail.title || id;
      return id.toLowerCase().includes(q)
        || title.toLowerCase().includes(q)
        || displayNodeTitle(title).toLowerCase().includes(q);
    })
    .map(([id, detail]) => ({
      value: `@${id}`,
      title: displayNodeTitle(detail.title || shortName(id)),
      detail: id,
    }));
  return [...contextItems, ...nodeItems].slice(0, 8);
}

function renderMentionSuggestions(query) {
  const root = document.getElementById('mention-suggestions');
  if (!root) return;
  const items = mentionCandidates(query);
  if (!items.length) {
    root.classList.add('hidden');
    root.innerHTML = '';
    return;
  }
  root.classList.remove('hidden');
  root.innerHTML = items.map((item, index) => `
    <div class="mention-item ${index === 0 ? 'active' : ''}" data-mention-value="${html(item.value)}">
      <strong>${html(item.title)}</strong><br/>
      <small>${html(item.detail)}</small>
    </div>
  `).join('');
  root.querySelectorAll('[data-mention-value]').forEach((el) => {
    el.addEventListener('click', () => applyMention(el.dataset.mentionValue));
  });
}

function applyMention(valueToInsert) {
  const textarea = document.getElementById('agent-prompt');
  const root = document.getElementById('mention-suggestions');
  if (!textarea) return;
  const value = textarea.value;
  const cursor = textarea.selectionStart;
  const prefix = value.slice(0, cursor).replace(/@([^\s@]*)$/, `${valueToInsert} `);
  textarea.value = prefix + value.slice(cursor);
  if (root) {
    root.classList.add('hidden');
    root.innerHTML = '';
  }
  textarea.focus();
  renderAgentControls();
}

function handleMentionInput() {
  const textarea = document.getElementById('agent-prompt');
  if (!textarea) return;
  const value = textarea.value.slice(0, textarea.selectionStart);
  const match = value.match(/@([^\s@]*)$/);
  if (!match) {
    document.getElementById('mention-suggestions')?.classList.add('hidden');
    return;
  }
  renderMentionSuggestions(match[1] || '');
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function promptContainsToken(prompt, token) {
  return new RegExp(`(^|\\s)${escapeRegExp(token)}(?=\\s|$|[.,;:!?])`).test(prompt);
}

function targetNodeDetail(context) {
  return context.target_node ? nodeDetails(context.target_node) : null;
}

function nodeContextLine(nodeId) {
  const detail = nodeDetails(nodeId);
  if (!detail) return `node ${nodeId}: unknown`;
  return `node ${nodeId}: title=${displayNodeTitle(detail.title || nodeId)}; status=${detail.status || 'unknown'}; path=${detail.path || nodeId}`;
}

function resolvedContextExcerpt(session) {
  const prompt = session?.prompt || '';
  const markers = [`[${t('resolvedMentions')}]`, '[已解析上下文]', '[Resolved context]'];
  const match = markers
    .map((marker) => ({ marker, index: prompt.indexOf(marker) }))
    .filter((item) => item.index >= 0)
    .sort((a, b) => a.index - b.index)[0];
  if (!match) return '';
  const index = match.index;
  return prompt.slice(index + match.marker.length).trim();
}

function draftMentionPreviewLines(prompt, context = sessionDraftContext()) {
  const lines = [];
  const detail = targetNodeDetail(context);
  if (promptContainsToken(prompt, '@current')) {
    lines.push(`@current -> session_type=${context.session_type}; target_node=${context.target_node || 'none'}; target_scope=${context.target_scope || 'none'}`);
  }
  if (promptContainsToken(prompt, '@scope')) {
    lines.push(`@scope -> ${context.target_scope || 'none'}`);
  }
  if (promptContainsToken(prompt, '@node')) {
    lines.push(`@node -> ${context.target_node ? nodeContextLine(context.target_node) : 'node: none'}`);
  }
  if (promptContainsToken(prompt, '@readme')) {
    lines.push(`@readme -> ${detail?.readme_path || 'none'}`);
  }
  if (promptContainsToken(prompt, '@status')) {
    lines.push(`@status -> status=${detail?.status || 'unknown'}; status_file=${detail?.status_path || 'none'}`);
  }
  if (promptContainsToken(prompt, '@manuscript')) {
    const manuscriptPath = state.manuscript.nodeId === context.target_node ? state.manuscript.path : 'node-local manuscript';
    lines.push(`@manuscript -> ${manuscriptPath || 'none'}${manuscriptHasDirtyChanges() ? '; save required first' : ''}`);
  }
  for (const nodeMention of unique(prompt.match(/@research::[^\s,.;)]+/g) || [])) {
    lines.push(`${nodeMention} -> ${nodeContextLine(nodeMention.slice(1))}`);
  }
  return lines;
}

async function resolveManuscriptContext(context) {
  if (!context.target_node) return 'manuscript_path: none\n\n';
  if (state.manuscript.nodeId === context.target_node && state.manuscript.path) {
    return `manuscript_path: ${state.manuscript.path}\n\n${state.manuscript.current || ''}`;
  }
  try {
    const payload = await fetchJson(`/api/node/${encodeURIComponent(context.target_node)}/manuscript`);
    return `manuscript_path: ${payload.path}\n\n${payload.content || ''}`;
  } catch (err) {
    throw new Error(`${t('manuscriptContextLoadFailed')}: ${err.message}`);
  }
}

async function resolvedMentionLines(prompt, context = sessionDraftContext()) {
  const lines = [];
  const detail = targetNodeDetail(context);
  if (promptContainsToken(prompt, '@current')) {
    lines.push(`current: session_type=${context.session_type}; target_node=${context.target_node || 'none'}; target_scope=${context.target_scope || 'none'}; path=${context.path || 'repo'}`);
  }
  if (promptContainsToken(prompt, '@scope')) {
    const scope = context.target_scope ? findNodeInHierarchy(context.target_scope) : null;
    lines.push(`scope: ${context.target_scope || 'none'}${scope ? `; title=${displayNodeTitle(scope.name)}; path=${scope.path || ''}` : ''}`);
  }
  if (promptContainsToken(prompt, '@node')) {
    lines.push(context.target_node ? nodeContextLine(context.target_node) : 'node: none');
  }
  if (promptContainsToken(prompt, '@readme')) {
    lines.push(`readme: ${detail?.readme_path || 'none'}`);
  }
  if (promptContainsToken(prompt, '@status')) {
    lines.push(`status: ${detail?.status || 'unknown'}; status_file=${detail?.status_path || 'none'}; lifecycle=${detail?.lifecycle_stage || 'unknown'}; progress=${detail?.progress_pct ?? 'unknown'}`);
  }
  if (promptContainsToken(prompt, '@manuscript')) {
    if (manuscriptHasDirtyChanges()) throw new Error(t('manuscriptSaveFirst'));
    lines.push(await resolveManuscriptContext(context));
  }
  for (const nodeMention of unique(prompt.match(/@research::[^\s,.;)]+/g) || [])) {
    lines.push(nodeContextLine(nodeMention.slice(1)));
  }
  return lines;
}

async function promptWithResolvedMentions(prompt) {
  const lines = await resolvedMentionLines(prompt);
  if (!lines.length) return prompt;
  return `${prompt}\n\n[${t('resolvedMentions')}]\n${lines.map((line) => `- ${line}`).join('\n')}`;
}

function agentRunBlockReason({ requirePrompt = true } = {}) {
  const boot = state.bootstrap || {};
  const agent = document.getElementById('agent-select')?.value;
  const prompt = document.getElementById('agent-prompt')?.value.trim();
  const context = sessionDraftContext();
  if (!boot.graph_ready) return 'python scripts/refresh_views.py --mode full';
  if (!boot.can_run_agents) return boot.using_example_config ? t('exampleConfig') : t('cannotRun');
  if (!agent) return t('agent');
  if (context.session_type === 'node') {
    if (!context.target_node) return t('targetMissing');
    if (!nodeDetails(context.target_node)) return `${t('unknown')}: ${context.target_node}`;
  }
  if (context.session_type === 'scope' && !context.target_scope) return t('scopeMissing');
  if (requirePrompt && !prompt) return t('prompt');
  if (requirePrompt && promptContainsToken(prompt, '@manuscript') && manuscriptHasDirtyChanges()) return t('manuscriptSaveFirst');
  return '';
}

function renderAgentControls(message = '') {
  const runReason = agentRunBlockReason({ requirePrompt: true });
  const createReason = agentRunBlockReason({ requirePrompt: false });
  const runButton = document.getElementById('run-session-button');
  const createButton = document.getElementById('create-session-button');
  const status = document.getElementById('agent-run-status');
  if (runButton) runButton.disabled = Boolean(runReason);
  if (createButton) createButton.disabled = Boolean(createReason);
  if (status) status.textContent = message || (runReason ? `${t('runBlocked')}: ${runReason}` : t('canRun'));
  renderSessionHeader();
  renderSessionContext();
}

function renderAgentCatalog() {
  const select = document.getElementById('agent-select');
  if (!select) return;
  const previous = select.value;
  const agents = state.data?.catalog?.agents || {};
  const defaultAgent = state.data?.catalog?.default_agent || state.bootstrap?.default_agent || '';
  const options = Object.entries(agents).map(([key, value]) => `<option value="${html(key)}">${html(value.label)}</option>`).join('');
  select.innerHTML = options || `<option value="">${t('noData')}</option>`;
  if (previous && agents[previous]) select.value = previous;
  else if (defaultAgent && agents[defaultAgent]) select.value = defaultAgent;
}

function sessionPayload() {
  const context = sessionDraftContext();
  return {
    agent: document.getElementById('agent-select')?.value || '',
    session_type: context.session_type,
    target_node: context.target_node,
    target_scope: context.target_scope,
  };
}

async function createSession() {
  const reason = agentRunBlockReason({ requirePrompt: false });
  if (reason) {
    renderAgentControls(`${t('runBlocked')}: ${reason}`);
    return;
  }
  const session = await createSessionRecord();
  setCurrentSessionId(session.id);
  setWorkspaceTab('session');
  appRuntime.renderAll();
}

async function createSessionRecord() {
  const response = await fetch(API.sessions, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(sessionPayload())
  });
  const data = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(data));
  state.sessions = [data.session, ...state.sessions.filter((item) => item.id !== data.session.id)];
  setCurrentSessionId(data.session.id);
  return data.session;
}

async function runSession() {
  const reason = agentRunBlockReason({ requirePrompt: true });
  if (reason) {
    renderAgentControls(`${t('runBlocked')}: ${reason}`);
    return;
  }
  const session = currentSession() || await createSessionRecord();
  const prompt = await promptWithResolvedMentions(document.getElementById('agent-prompt').value.trim());
  const data = await fetchJson(`${API.sessions}/${encodeURIComponent(session.id)}/run`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ prompt })
  });
  state.sessions = [data.session, ...state.sessions.filter((item) => item.id !== data.session.id)];
  setCurrentSessionId(data.session.id);
  setWorkspaceTab('session');
  await refreshSessions();
  appRuntime.renderAll();
  renderAgentControls(t('refreshOk'));
}

async function stopSession() {
  const session = currentSession();
  if (!session) return;
  try {
    await fetchJson(`${API.sessions}/${encodeURIComponent(session.id)}/stop`, { method: 'POST' });
    await refreshSessions();
  } catch (err) {
    renderAgentControls(err.message);
  }
}

async function refreshSessions() {
  const response = await fetch(API.sessions, { cache: 'no-store' });
  const data = await response.json();
  state.sessions = data.sessions || [];
  syncCurrentSessionToContext();
  renderSessions();
  renderSessionHeader();
  renderSessionContext();
}

function renderSessionHeaderCard(context, sessionLabel, agent, detail, runnable) {
  return `
    <div class="session-header-top">
      <div>
        <p class="section-label">${t('sessionDraft')}</p>
        <h3>${sessionTypeLabel(context.session_type)} · ${html(context.label)}</h3>
      </div>
      <div class="badges">
        <span class="badge">${t('boundedNotice')}</span>
      </div>
    </div>
    <div class="session-context-grid">
      <div class="kv"><div class="kv-label">${t('currentSession')}</div><div class="kv-value">${html(sessionLabel)}</div></div>
      <div class="kv"><div class="kv-label">${t('agent')}</div><div class="kv-value">${html(agent)}</div></div>
      <div class="kv"><div class="kv-label">${t('status')}</div><div class="kv-value">${html(detail?.status || runnable)}</div></div>
      <div class="kv"><div class="kv-label">${context.session_type === 'node' ? t('boundNode') : (context.session_type === 'scope' ? t('boundScope') : t('repoRoot'))}</div><div class="kv-value">${html(context.path || context.label)}</div></div>
    </div>
  `;
}

function renderSessionHeader() {
  const root = document.getElementById('session-header');
  if (!root) return;
  const context = sessionDraftContext();
  const session = currentSession();
  const sessionLabel = session ? `${session.agent} · ${session.status}` : t('noSession');
  const agent = document.getElementById('agent-select')?.value || session?.agent || '—';
  const detail = context.target_node ? nodeDetails(context.target_node) : null;
  const runnable = agentRunBlockReason({ requirePrompt: false }) ? t('cannotRun') : t('canRun');
  root.innerHTML = renderSessionHeaderCard(context, sessionLabel, agent, detail, runnable);
}

function renderSessionContextCard(context, session) {
  const prompt = document.getElementById('agent-prompt')?.value.trim() || '';
  const resolved = resolvedContextExcerpt(session);
  const previewLines = resolved ? resolved.split('\n') : draftMentionPreviewLines(prompt, context);
  return `
    <div class="session-context-card">
      <div class="kv"><div class="kv-label">${t('sessionType')}</div><div class="kv-value">${sessionTypeLabel(context.session_type)}</div></div>
      <div class="kv"><div class="kv-label">${t('sessionDraft')}</div><div class="kv-value">${html(context.label)}</div></div>
      <div class="kv"><div class="kv-label">${t('currentSession')}</div><div class="kv-value">${session ? html(session.id) : t('noSession')}</div></div>
      <div class="section-meta">${t('boundedNotice')}</div>
      <div class="resolved-context-preview">
        <div class="kv-label">${t('resolvedMentions')}</div>
        <pre>${previewLines.length ? html(previewLines.join('\n')) : t('noData')}</pre>
      </div>
    </div>
  `;
}

function renderSessionContext() {
  const root = document.getElementById('session-context-content');
  if (!root) return;
  const context = sessionDraftContext();
  const session = currentSession();
  root.innerHTML = renderSessionContextCard(context, session);
}

function renderSessionListItem(session) {
  const sessionScope = session.context_label
    ? displayNodeTitle(session.context_label)
    : (session.target_node ? shortName(session.target_node) : t('repoRoot'));
  return `
    <div class="session-item ${state.currentSessionId === session.id ? 'active' : ''}" data-id="${html(session.id)}">
      <div class="session-top">
        <div class="session-title">${html(session.agent)}</div>
        <div class="badges">${statusBadge(session.status)}<span class="badge">${html(session.session_type || (session.target_node ? 'node' : 'general'))}</span></div>
      </div>
      <div class="section-meta">${html(sessionScope)}</div>
      <div class="section-meta">${html(session.id)}</div>
    </div>
  `;
}

function renderSessions() {
  const list = DOM.sessionList();
  if (!list) return;
  const sessions = visibleSessions();
  document.getElementById('agent-meta').textContent = String(sessions.length);
  list.innerHTML = sessions.map(renderSessionListItem).join('') || `<div class="section-meta">${t('noSession')}</div>`;
  list.querySelectorAll('[data-id]').forEach((el) => {
    el.addEventListener('click', () => {
      setCurrentSessionId(el.dataset.id);
      setWorkspaceTab('session');
      appRuntime.renderAll();
    });
  });
  renderSessionLog();
}

function renderSessionLog() {
  const pre = DOM.sessionLog();
  if (!pre) return;
  const session = currentSession();
  if (!session) {
    pre.textContent = '';
    return;
  }
  pre.textContent = (session.log_lines || []).join('\n');
}

export {
  syncCurrentSessionToContext,
  renderPromptActions,
  renderNodeOptions,
  handleMentionInput,
  renderAgentControls,
  renderAgentCatalog,
  createSession,
  runSession,
  stopSession,
  refreshSessions,
  renderSessionHeader,
  renderSessionContext,
  renderSessions,
  sessionDraftContext,
};
