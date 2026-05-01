import {
  API,
  DOM,
  assertDomContract,
  collapseAll,
  configureAppRuntime,
  fetchJson,
  fetchOptionalJson,
  gatewayFailureHtml,
  parentScopeId,
  setDrawerOpen,
  setHeartbeat,
  setNavOpen,
  setWorkspaceTab,
  state,
  t,
} from './ui_core.js';
import {
  confirmDiscardManuscriptChanges,
  loadManuscript,
  manuscriptHasDirtyChanges,
  revertManuscript,
  saveManuscript,
} from './manuscript.js';
import {
  createSession,
  handleMentionInput,
  refreshSessions,
  renderAgentControls,
  syncCurrentSessionToContext,
  runSession,
  stopSession,
} from './sessions.js';
import {
  expandActivePath,
  handleWorkspaceTabKeydown,
  openSessionForSelection,
  renderGlobalChrome,
  renderNavigation,
  renderSetupStatus,
  renderTopbar,
  renderWorkspace,
  renderWorkspacePanels,
  selectNode,
  selectScope,
  togglePinnedSelectedNode,
} from './workspace.js';

function renderLoadFailure(error) {
  setWorkspaceTab('overview');
  renderTopbar();
  renderSetupStatus();
  renderAgentControls();
  setHeartbeat('heartbeatGateway', 'gateway');

  const title = DOM.centerTitle();
  if (title) title.textContent = t('gatewayUnavailableTitle');
  const empty = DOM.graphEmpty();
  if (empty) empty.classList.add('hidden');
  const canvas = DOM.graphCanvas();
  if (canvas) canvas.innerHTML = gatewayFailureHtml(error);
}

async function loadAll({ preserveDirtyManuscript = false } = {}) {
  setHeartbeat('refreshLoading');
  state.loadError = null;
  try {
    const bootstrap = await fetchJson(API.bootstrap);
    state.bootstrap = bootstrap;
    const [catalog, sessions] = await Promise.all([
      fetchOptionalJson(API.catalog, { agents: {} }),
      fetchOptionalJson(API.sessions, { sessions: [] }),
    ]);

    if (!bootstrap.graph_ready) {
      state.data = {
        health: bootstrap,
        status: {
          current_phase: bootstrap.current_phase,
          next_node: bootstrap.next_node,
          unfinished_count: 0,
          ready_nodes: [],
          blocked_nodes: [],
        },
        graph: { nodes: {}, edges: [] },
        hierarchy: null,
        details: { nodes: {} },
        rollup: { scopes: {} },
        board: { lanes: {} },
        catalog,
      };
      state.sessions = sessions.sessions || [];
      renderAll();
      setHeartbeat('refreshFailed');
      return;
    }

    const [status, graph, hierarchy, details, rollup, board] = await Promise.all([
      fetchJson(API.status),
      fetchJson(API.structure),
      fetchJson(API.hierarchy),
      fetchJson(API.details),
      fetchJson(API.rollup),
      fetchJson(API.board),
    ]);

    state.data = { health: bootstrap, status, graph, hierarchy, details, rollup, board, catalog };
    state.sessions = sessions.sessions || [];
    if (!state.selectedNodeId) state.selectedNodeId = status.next_node || null;
    if (!state.activeScopeId) {
      const firstScope = hierarchy.children?.[0]?.id || hierarchy.id;
      state.activeScopeId = firstScope;
    }
    syncCurrentSessionToContext();
    expandActivePath();
    if (state.selectedNodeId && !(preserveDirtyManuscript && manuscriptHasDirtyChanges())) {
      await loadManuscript(state.selectedNodeId).catch((err) => {
        state.loadError = err.message || String(err);
      });
    }
    renderAll();
    setHeartbeat('refreshOk');
  } catch (err) {
    state.loadError = err.message || String(err);
    console.error(err);
    renderLoadFailure(err);
    if (state.bootstrap) setHeartbeat('refreshFailed');
  }
}

function renderAll() {
  renderGlobalChrome();
  renderNavigation();
  renderWorkspace();
  renderWorkspacePanels();
}

function bindEvent(id, eventName, handler) {
  const el = DOM.byId(id);
  if (el) el.addEventListener(eventName, handler);
}

function closeSecondaryActions() {
  document.querySelector('.secondary-actions')?.removeAttribute('open');
}

function setupEvents() {
  bindEvent('language-toggle', 'change', (event) => {
    state.lang = event.target.value;
    localStorage.setItem('research_app_lang', state.lang);
    renderAll();
  });
  document.querySelectorAll('.workspace-tab').forEach((el) => {
    el.addEventListener('click', () => {
      setWorkspaceTab(el.dataset.tab);
      renderAll();
    });
    el.addEventListener('keydown', handleWorkspaceTabKeydown);
  });
  bindEvent('global-search-input', 'input', (event) => {
    state.searchQuery = event.target.value;
    renderNavigation();
  });
  bindEvent('collapse-all-button', 'click', () => {
    collapseAll();
    renderNavigation();
  });
  bindEvent('expand-active-path-button', 'click', () => {
    expandActivePath();
    renderNavigation();
  });
  bindEvent('refresh-button', 'click', () => {
    if (confirmDiscardManuscriptChanges()) loadAll();
  });
  bindEvent('sidebar-toggle-button', 'click', () => {
    closeSecondaryActions();
    setNavOpen(!state.navOpen);
  });
  bindEvent('drawer-toggle-button', 'click', () => {
    setDrawerOpen(!state.drawerOpen);
  });
  bindEvent('back-scope-button', 'click', () => {
    closeSecondaryActions();
    const parent = parentScopeId(state.activeScopeId);
    if (parent) selectScope(parent);
  });
  bindEvent('focus-next-button', 'click', () => {
    closeSecondaryActions();
    const next = state.data?.status?.next_node;
    if (next) selectNode(next);
  });
  bindEvent('dependency-toggle-button', 'click', () => {
    closeSecondaryActions();
    state.dependencyOverlayEnabled = !state.dependencyOverlayEnabled;
    localStorage.setItem('research_app_dependency_overlay', state.dependencyOverlayEnabled ? '1' : '0');
    renderAll();
  });
  bindEvent('pin-node-button', 'click', () => {
    closeSecondaryActions();
    togglePinnedSelectedNode();
  });
  bindEvent('open-session-button', 'click', openSessionForSelection);
  bindEvent('session-type-select', 'change', (event) => {
    state.sessionType = event.target.value;
    localStorage.setItem('research_app_session_type', state.sessionType);
    const input = document.getElementById('target-node-input');
    if (input && state.sessionType !== 'node') input.value = '';
    if (input && state.sessionType === 'node' && !input.value && state.selectedNodeId) input.value = state.selectedNodeId;
    syncCurrentSessionToContext();
    renderWorkspacePanels();
  });
  bindEvent('target-node-input', 'input', () => {
    syncCurrentSessionToContext();
    renderWorkspacePanels();
  });
  bindEvent('agent-prompt', 'input', () => {
    renderAgentControls();
    handleMentionInput();
  });
  bindEvent('agent-select', 'change', () => renderAgentControls());
  bindEvent('manuscript-editor', 'input', (event) => {
    state.manuscript.current = event.target.value;
    state.manuscript.dirty = state.manuscript.current !== state.manuscript.original;
    state.manuscript.status = state.manuscript.dirty ? 'dirty' : 'saved';
    state.manuscript.error = '';
    renderWorkspace();
  });
  bindEvent('reload-manuscript-button', 'click', () => {
    if (confirmDiscardManuscriptChanges()) {
      loadManuscript().catch((err) => renderAgentControls(err.message));
    }
  });
  bindEvent('revert-manuscript-button', 'click', revertManuscript);
  bindEvent('save-manuscript-button', 'click', () => {
    saveManuscript().catch((err) => renderAgentControls(err.message));
  });
  bindEvent('create-session-button', 'click', () => createSession().then(() => renderAgentControls(t('refreshOk'))).catch((err) => renderAgentControls(err.message)));
  bindEvent('run-session-button', 'click', () => runSession().catch((err) => renderAgentControls(err.message)));
  bindEvent('stop-session-button', 'click', () => stopSession());
  window.addEventListener('beforeunload', (event) => {
    if (!manuscriptHasDirtyChanges()) return;
    event.preventDefault();
    event.returnValue = '';
  });
  document.addEventListener('keydown', (event) => {
    if (!(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== 's') return;
    if (!state.manuscript.nodeId) return;
    event.preventDefault();
    saveManuscript().catch((err) => renderAgentControls(err.message));
  });
}

async function bootstrap() {
  assertDomContract();
  configureAppRuntime({ renderAll, loadAll });
  setupEvents();
  await loadAll();
  if (state.pollHandle) clearInterval(state.pollHandle);
  state.pollHandle = setInterval(async () => {
    await refreshSessions();
  }, 3000);
}

bootstrap().catch(console.error);
