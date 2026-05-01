import {
  appRuntime,
  boolText,
  breadcrumbFor,
  collapseNode,
  displayNodeTitle,
  DOM,
  expandActivePath,
  expandNode,
  fileHref,
  findNodeInHierarchy,
  flagToKey,
  foldSection,
  graphNode,
  html,
  isExpanded,
  matchesQuery,
  nodeDetails,
  NODE_STAGES,
  parentScopeId,
  readListRows,
  savePinnedNodes,
  scopeMetrics,
  setDrawerOpen,
  setNavOpen,
  setWorkspaceTab,
  shortName,
  state,
  statusBadge,
  statusClass,
  t,
  toggleExpanded,
  workspaceTitle,
} from './ui_core.js';
import {
  confirmDiscardManuscriptChanges,
  loadManuscript,
  renderManuscript,
} from './manuscript.js';
import {
  renderAgentCatalog,
  renderAgentControls,
  renderNodeOptions,
  renderPromptActions,
  renderSessionContext,
  renderSessionHeader,
  renderSessions,
  syncCurrentSessionToContext,
} from './sessions.js';

function treeSignalsForNode(nodeId, status) {
  const detail = nodeDetails(nodeId) || {};
  const truthClass = detailTruthClass(detail);
  const isSchedulerNext = nodeId === state.data?.status?.next_node;
  const secondarySignal = isSchedulerNext
    ? `<span class="tree-signal scheduler-next" title="${html(t('schedulerNext'))}"></span>`
    : (truthClass !== 'truth-ready' ? `<span class="tree-signal ${html(truthClass)}" title="${html(detailTruthLabel(detail))}"></span>` : '');
  return `
    <span class="tree-status-dot ${html(statusClass(status))}" title="${html(`${t('status')}: ${status || t('unknown')}`)}"></span>
    ${secondarySignal}
  `;
}

function renderTreeRow(node, {
  depth,
  parentId,
  status,
  hasChildren,
  expanded,
  active,
  focusNodeId,
  childrenHtml,
}) {
  return `
    <div class="tree-item" data-tree-node="${html(node.id)}">
      <div
        class="tree-row ${active ? 'active' : ''}"
        id="tree-row-${html(node.id)}"
        data-node-id="${html(node.id)}"
        data-parent-id="${html(parentId)}"
        data-has-children="${hasChildren ? 'true' : 'false'}"
        data-expanded="${expanded ? 'true' : 'false'}"
        role="treeitem"
        aria-level="${depth + 1}"
        aria-selected="${active ? 'true' : 'false'}"
        ${hasChildren ? `aria-expanded="${expanded ? 'true' : 'false'}"` : ''}
        tabindex="${focusNodeId === node.id ? 0 : -1}"
      >
        <button class="tree-toggle" data-toggle-id="${html(node.id)}" type="button">${hasChildren ? (expanded ? '▾' : '▸') : ''}</button>
        <div class="tree-title" title="${html(`${displayNodeTitle(node.name)} · ${status}`)}">${html(displayNodeTitle(node.name))}</div>
        <div class="tree-meta">${treeSignalsForNode(node.id, status)}</div>
      </div>
      ${childrenHtml}
    </div>
  `;
}

function renderWatchedWorksetRows(watched) {
  return watched.map((nodeId) => {
    const detail = nodeDetails(nodeId) || {};
    return `<button class="watch-row" data-node-id="${html(nodeId)}" type="button">${html(displayNodeTitle(detail.title || shortName(nodeId)))}</button>`;
  }).join('');
}

function renderWatchedWorkset(watched) {
  return `
    <div class="section-meta watch-hint">${t('laneWatchHint')}</div>
    ${watched.length ? renderWatchedWorksetRows(watched) : `<div class="section-meta">${t('noData')}</div>`}
  `;
}

function detailTruthClass(detail = {}) {
  const handoff = detail.handoff_readiness || 'blocked_unknown';
  if (handoff === 'ready') return 'truth-ready';
  if (handoff === 'blocked_review') return 'review-blocked';
  if (handoff === 'blocked_execution') return 'execution-blocked';
  return 'truth-blocked';
}

function detailTruthLabel(detail = {}) {
  return ({
    'truth-ready': t('truthReady'),
    'review-blocked': t('reviewBlocked'),
    'execution-blocked': t('executionBlocked'),
    'truth-blocked': t('truthBlocked'),
  })[detailTruthClass(detail)] || t('unknown');
}

function truthCounts() {
  const details = state.data?.details?.nodes || {};
  let ready = 0;
  let blocked = 0;
  Object.values(details).forEach((detail) => {
    if (!detail || typeof detail !== 'object') return;
    if (detail.handoff_readiness === 'ready') ready += 1;
    else if (detail.handoff_readiness) blocked += 1;
  });
  return { ready, blocked };
}

function reviewGateLabel(value) {
  return ({
    not_required: t('gateNotRequired'),
    missing_verdict: t('gateMissingVerdict'),
    incomplete: t('gateIncomplete'),
    failed: t('gateFailed'),
    passed: t('gatePassed'),
  })[value] || t('unknown');
}

function executionGateLabel(value) {
  return ({
    not_applicable: t('executionNotApplicable'),
    missing_contract: t('executionMissingContract'),
    review_only: t('executionReviewOnly'),
    contract_incomplete: t('executionContractIncomplete'),
    missing_outputs: t('executionMissingOutputs'),
    failed: t('executionFailed'),
    ready: t('executionReady'),
  })[value] || t('unknown');
}

function placeholderRiskLabel(value) {
  return ({
    none: t('placeholderNone'),
    suspected: t('placeholderSuspected'),
    confirmed: t('placeholderConfirmed'),
  })[value] || t('unknown');
}

function detailKindLabel(detail = {}) {
  return detail.kind === 'parent' ? t('kindParent') : t('kindLeaf');
}

function blockingReasonsHtml(detail = {}) {
  const reasons = Array.isArray(detail.blocking_reasons) ? detail.blocking_reasons : [];
  if (!reasons.length) return `<div class="section-meta">${t('noData')}</div>`;
  return reasons.map((reason) => `
    <div class="kv">
      <div class="kv-value">${html(reason)}</div>
    </div>
  `).join('');
}

function renderFocusCardBody(nextDetail, status) {
  const next = status.next_node;
  const truth = truthCounts();
  return `
    <div class="focus-summary">
      <div class="kv">
        <div class="kv-label">${t('schedulerNext')}</div>
        <div class="kv-value">${html(displayNodeTitle(nextDetail.title || shortName(next)))}</div>
      </div>
      <div class="section-meta">${html(nextDetail.path || next || '')} · ${html(detailTruthLabel(nextDetail))}</div>
      <div class="focus-stats">
        <span>${t('readyCount')}: ${(status.ready_nodes || []).length}</span>
        <span>${t('blockedCount')}: ${(status.blocked_nodes || []).length}</span>
        <span>${t('truthReadyCount')}: ${truth.ready}</span>
        <span>${t('truthBlockedCount')}: ${truth.blocked}</span>
        <span>${t('unfinishedCount')}: ${status.unfinished_count ?? '—'}</span>
      </div>
    </div>
  `;
}

function renderTopbar() {
  const languageToggle = DOM.languageToggle();
  if (languageToggle) languageToggle.value = state.lang;
  const globalSearchInput = DOM.globalSearchInput();
  if (globalSearchInput) globalSearchInput.value = state.searchQuery;
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  const centerTitle = DOM.centerTitle();
  if (centerTitle) centerTitle.textContent = workspaceTitle();
  renderTopbarSummary();
  renderActionButtons();
  setNavOpen(state.navOpen, { persist: false });
  setDrawerOpen(state.drawerOpen, { persist: false });
}

function renderTopbarSummary() {
  const root = DOM.topbarSummary();
  if (!root) return;
  const status = state.data?.status || {};
  const boot = state.bootstrap || state.data?.health || {};
  const truth = truthCounts();
  const items = [
    [t('currentPhase'), status.current_phase || '—'],
    [t('schedulerNext'), shortName(status.next_node)],
    [t('setupStatus'), boot.can_run_agents ? t('canRun') : t('cannotRun')],
  ];
  const meta = `${t('readyCount')}: ${(status.ready_nodes || []).length} · ${t('blockedCount')}: ${(status.blocked_nodes || []).length} · ${t('truthReadyCount')}: ${truth.ready} · ${t('truthBlockedCount')}: ${truth.blocked} · ${t('unfinishedCount')}: ${status.unfinished_count ?? '—'}`;
  root.innerHTML = `
    ${items.map(([label, value]) => `
    <div class="topbar-stat primary-stat">
      <span>${html(label)}</span>
      <strong>${html(value)}</strong>
    </div>
    `).join('')}
    <div class="topbar-meta">${html(meta)}</div>
  `;
}

function renderSetupStatus() {
  const root = document.getElementById('setup-content');
  if (!root) return;
  const boot = state.bootstrap || {};
  const missing = boot.missing_projection_files || [];
  const steps = boot.setup_steps || [];
  const ready = boot.graph_ready && boot.can_run_agents;
  const lines = [];
  if (missing.length) lines.push(`${missing.length} missing projections`);
  if (boot.using_example_config) lines.push(t('exampleConfig'));
  if (state.loadError) lines.push(`${t('lastError')}: ${state.loadError}`);
  if (!ready) setDrawerOpen(true, { persist: false });
  root.innerHTML = `
    <div class="setup-card ${ready ? 'ready' : 'blocked'}">
      <div class="setup-top">
        <strong>${ready ? t('setupReady') : t('setupNeedsAttention')}</strong>
        <span class="badge ${ready ? 'ready' : 'blocked'}">${boot.can_run_agents ? t('canRun') : t('cannotRun')}</span>
      </div>
      ${lines.length ? `<div class="section-meta">${html(lines.join(' · '))}</div>` : `<div class="section-meta">${t('setupReady')}</div>`}
      ${steps.length ? `<div class="setup-steps"><div class="kv-label">${t('setupSteps')}</div>${steps.map((step) => `<code>${html(step)}</code>`).join('')}</div>` : ''}
    </div>
  `;
}

function treeRowElements() {
  return [...document.querySelectorAll('.tree-row[data-node-id]')];
}

function setTreeFocus(nodeId, { focus = true } = {}) {
  state.treeFocusId = nodeId || null;
  const treeRoot = document.getElementById('tree-root');
  if (treeRoot && state.treeFocusId) treeRoot.setAttribute('aria-activedescendant', `tree-row-${state.treeFocusId}`);
  treeRowElements().forEach((row) => {
    const active = row.dataset.nodeId === state.treeFocusId;
    row.tabIndex = active ? 0 : -1;
  });
  if (!focus || !nodeId) return;
  const target = treeRowElements().find((row) => row.dataset.nodeId === nodeId);
  target?.focus();
}

function focusTreeRowAt(index) {
  const rows = treeRowElements();
  const target = rows[index];
  if (!target) return;
  setTreeFocus(target.dataset.nodeId);
}

function focusFirstChildRow(nodeId) {
  const child = treeRowElements().find((row) => row.dataset.parentId === nodeId);
  if (child) setTreeFocus(child.dataset.nodeId);
}

function handleTreeRowKeydown(event) {
  const row = event.currentTarget;
  const rows = treeRowElements();
  const index = rows.findIndex((item) => item === row);
  const nodeId = row.dataset.nodeId;
  const hasChildren = row.dataset.hasChildren === 'true';
  const expanded = row.dataset.expanded === 'true';
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      focusTreeRowAt(Math.min(rows.length - 1, index + 1));
      break;
    case 'ArrowUp':
      event.preventDefault();
      focusTreeRowAt(Math.max(0, index - 1));
      break;
    case 'Home':
      event.preventDefault();
      focusTreeRowAt(0);
      break;
    case 'End':
      event.preventDefault();
      focusTreeRowAt(rows.length - 1);
      break;
    case 'ArrowRight':
      event.preventDefault();
      if (!hasChildren) break;
      if (!expanded) {
        expandNode(nodeId);
        renderTreeNavigator();
        setTreeFocus(nodeId);
        break;
      }
      focusFirstChildRow(nodeId);
      break;
    case 'ArrowLeft':
      event.preventDefault();
      if (hasChildren && expanded) {
        collapseNode(nodeId);
        renderTreeNavigator();
        setTreeFocus(nodeId);
        break;
      }
      if (row.dataset.parentId) setTreeFocus(row.dataset.parentId);
      break;
    case 'Enter':
    case ' ':
      event.preventDefault();
      row.click();
      break;
    default:
      break;
  }
}

function handleWorkspaceTabKeydown(event) {
  const tabs = [...document.querySelectorAll('.workspace-tab')];
  const index = tabs.findIndex((tab) => tab === event.currentTarget);
  if (index < 0) return;
  let nextIndex = index;
  switch (event.key) {
    case 'ArrowRight':
      nextIndex = (index + 1) % tabs.length;
      break;
    case 'ArrowLeft':
      nextIndex = (index - 1 + tabs.length) % tabs.length;
      break;
    case 'Home':
      nextIndex = 0;
      break;
    case 'End':
      nextIndex = tabs.length - 1;
      break;
    case 'Enter':
    case ' ':
      event.preventDefault();
      setWorkspaceTab(event.currentTarget.dataset.tab);
      appRuntime.renderAll();
      return;
    default:
      return;
  }
  event.preventDefault();
  const nextTab = tabs[nextIndex];
  if (!nextTab) return;
  setWorkspaceTab(nextTab.dataset.tab);
  appRuntime.renderAll();
  nextTab.focus();
}

function renderTreeNavigator() {
  const root = document.getElementById('tree-root');
  if (!root || !state.data?.hierarchy) return;
  const renderedNodeIds = [];

  function renderNode(node, depth = 0, parentId = '') {
    const childHtml = [];
    for (const child of node.children || []) {
      const rendered = renderNode(child, depth + 1, node.id);
      if (rendered) childHtml.push(rendered);
    }

    const detail = nodeDetails(node.id) || {};
    const status = detail.status || node.status || 'seed';
    const hasChildren = Boolean(node.children?.length);
    const matches = matchesQuery(node.id, node.name) || childHtml.length > 0;
    if (!matches) return '';

    const expanded = isExpanded(node.id);
    const active = state.selectedNodeId === node.id || state.activeScopeId === node.id;
    renderedNodeIds.push(node.id);
    const childrenHtml = hasChildren && expanded
      ? `<div class="tree-children" role="group">${childHtml.join('')}</div>`
      : '';
    const focusNodeId = state.treeFocusId || state.selectedNodeId;

    return renderTreeRow(node, {
      depth,
      parentId,
      status,
      hasChildren,
      expanded,
      active,
      focusNodeId,
      childrenHtml,
    });
  }

  root.innerHTML = (state.data.hierarchy.children || []).map((node) => renderNode(node)).join('') || `<div class="section-meta">${t('noData')}</div>`;

  root.querySelectorAll('[data-toggle-id]').forEach((el) => {
    el.addEventListener('click', (event) => {
      event.stopPropagation();
      toggleExpanded(el.dataset.toggleId);
      renderTreeNavigator();
      setTreeFocus(el.dataset.toggleId);
    });
  });

  root.querySelectorAll('[data-node-id]').forEach((el) => {
    el.addEventListener('keydown', handleTreeRowKeydown);
    el.addEventListener('focus', () => setTreeFocus(el.dataset.nodeId, { focus: false }));
    el.addEventListener('click', () => {
      const nodeId = el.dataset.nodeId;
      const node = findNodeInHierarchy(nodeId);
      state.treeFocusId = nodeId;
      if (node?.children?.length) state.activeScopeId = nodeId;
      if (selectNode(nodeId)) setWorkspaceTab('node');
    });
  });

  if (!renderedNodeIds.length) return;
  if (!state.treeFocusId || !renderedNodeIds.includes(state.treeFocusId)) {
    state.treeFocusId = state.selectedNodeId && renderedNodeIds.includes(state.selectedNodeId)
      ? state.selectedNodeId
      : renderedNodeIds[0];
  }
  root.setAttribute('aria-activedescendant', `tree-row-${state.treeFocusId}`);
  setTreeFocus(state.treeFocusId, { focus: false });
}

function selectScope(scopeId) {
  state.activeScopeId = scopeId;
  state.treeFocusId = scopeId;
  syncCurrentSessionToContext();
  if (state.sessionType === 'scope') renderSessionHeader();
  renderTreeNavigator();
  renderFocusCard();
  renderWatchPanel();
  renderOverviewIfVisible();
  renderInspectorScope(scopeId);
  renderSessionContext();
  renderAgentControls();
}

function renderFocusCard() {
  const root = document.getElementById('focus-card');
  if (!root || !state.data) return;
  const status = state.data.status;
  const nextDetail = nodeDetails(status.next_node) || {};
  root.innerHTML = renderFocusCardBody(nextDetail, status);
}

function renderWatchPanel() {
  const root = DOM.watchContent();
  if (!root || !state.data) return;
  const watched = [...state.pinnedNodeIds].filter((nodeId) => nodeDetails(nodeId));
  root.innerHTML = renderWatchedWorkset(watched);
  root.querySelectorAll('.watch-row[data-node-id]').forEach((el) => {
    el.addEventListener('click', () => selectNode(el.dataset.nodeId));
  });
}

function selectNode(nodeId) {
  if (nodeId !== state.selectedNodeId && !confirmDiscardManuscriptChanges()) return false;
  state.selectedNodeId = nodeId;
  state.treeFocusId = nodeId;
  const parent = parentScopeId(nodeId);
  if (parent) state.activeScopeId = parent;
  syncCurrentSessionToContext();
  expandActivePath();
  const input = document.getElementById('target-node-input');
  if (input) input.value = nodeId;
  renderTreeNavigator();
  renderFocusCard();
  renderWatchPanel();
  renderOverviewIfVisible();
  renderNodePanel();
  renderInspector();
  renderActionButtons();
  renderSessionHeader();
  renderSessionContext();
  renderPromptActions();
  renderAgentControls();
  loadManuscript(nodeId).catch((err) => renderAgentControls(err.message));
  return true;
}

function overviewScopeRoot() {
  if (!state.data?.hierarchy) return null;
  return state.activeScopeId ? findNodeInHierarchy(state.activeScopeId) : state.data.hierarchy;
}

function toOverviewAtlasNode(node) {
  const detail = nodeDetails(node.id) || {};
  const children = (node.children || []).map(toOverviewAtlasNode);
  return {
    id: node.id,
    name: displayNodeTitle(detail.title || node.name),
    path: node.path,
    status: detail.status || node.status || 'seed',
    progress_pct: detail.progress_pct ?? null,
    lifecycle_stage: detail.lifecycle_stage || null,
    review_gate: detail.review_gate || {},
    heartbeat_at: detail.heartbeat_at || null,
    last_actor: detail.last_actor || null,
    truth_ready: detail.truth_ready ?? null,
    handoff_readiness: detail.handoff_readiness || null,
    review_gate_state: detail.review_gate_state || null,
    execution_gate_state: detail.execution_gate_state || null,
    placeholder_risk: detail.placeholder_risk || null,
    blocking_reasons: detail.blocking_reasons || [],
    flags: detail.flags || [],
    children: children.length ? children : undefined,
  };
}

function buildOverviewLayout(rootData, width, height) {
  const root = d3.hierarchy(toOverviewAtlasNode(rootData));
  const rowHeight = 34;
  const columnWidth = 230;
  d3.tree().nodeSize([rowHeight, columnWidth])(root);

  const descendants = root.descendants();
  const minX = Math.min(...descendants.map((d) => d.x));
  const maxX = Math.max(...descendants.map((d) => d.x));
  const maxY = Math.max(...descendants.map((d) => d.y));
  const margin = { top: 34, right: 260, bottom: 34, left: 28 };
  const svgWidth = Math.max(width, maxY + margin.left + margin.right);
  const svgHeight = Math.max(height, maxX - minX + margin.top + margin.bottom);
  return { root, descendants, minX, svgWidth, svgHeight, margin };
}

function renderOverviewNodes(group, descendants) {
  const nodes = group.selectAll('g.atlas-node')
    .data(descendants)
    .enter()
    .append('g')
    .attr('transform', (d) => `translate(${d.y},${d.x})`)
    .attr('class', (d) => [
      'atlas-node',
      d.children ? 'scope-node' : 'leaf-node',
      d.data.id === state.selectedNodeId ? 'selected' : '',
      state.pinnedNodeIds.has(d.data.id) ? 'pinned' : '',
      d.data.id === state.data?.status?.next_node ? 'next' : '',
    ].filter(Boolean).join(' '));

  nodes.append('circle')
    .attr('r', (d) => d.children ? 5.5 : 4.2)
    .attr('fill', (d) => colorForStatus(d.data.status, d.data.id))
    .attr('stroke', (d) => borderColorForStatus(d.data.status, d.data.id))
    .attr('stroke-width', (d) => d.data.id === state.selectedNodeId ? 3 : 1.4)
    .on('mouseenter', (event, d) => {
      state.hoveredNodeId = d.data.id;
      d3.select(event.currentTarget.parentNode).raise();
      showTooltip(event, d);
    })
    .on('mousemove', (event) => moveTooltip(event))
    .on('mouseleave', () => {
      state.hoveredNodeId = null;
      hideTooltip();
    })
    .on('click', (event, d) => {
      const nodeId = d.data.id;
      const isScope = Boolean(d.children);
      const shiftKey = event.shiftKey;
      if (state.graphClickTimer) window.clearTimeout(state.graphClickTimer);
      state.graphClickTimer = window.setTimeout(() => {
        state.graphClickTimer = null;
        if (!isScope && shiftKey) {
          togglePinnedNode(nodeId);
          return;
        }
        if (isScope) selectScope(nodeId);
        else selectNode(nodeId);
      }, 180);
    })
    .on('dblclick', (event, d) => {
      if (d.children) return;
      event.stopPropagation();
      if (state.graphClickTimer) {
        window.clearTimeout(state.graphClickTimer);
        state.graphClickTimer = null;
      }
      openSessionForNode(d.data.id);
    });

  nodes.append('text')
    .attr('class', 'atlas-label')
    .attr('x', 12)
    .attr('dy', '.34em')
    .text((d) => truncate(displayNodeTitle(d.data.name), d.children ? 30 : 36));

  nodes.append('title')
    .text((d) => `${displayNodeTitle(d.data.name)}\n${d.data.path || d.data.id}\n${t('status')}: ${d.data.status || 'seed'}`);
}

function renderOverviewIfVisible() {
  if (state.workspaceTab !== 'overview') return;
  renderOverview();
}

function renderOverview() {
  const svgRoot = document.querySelector('#graph-canvas');
  const canvas = DOM.graphCanvas();
  if (!canvas || !svgRoot) return;
  if (state.workspaceTab !== 'overview') return;
  d3.select(svgRoot).selectAll('*').remove();

  const empty = DOM.graphEmpty();
  if (!state.data?.hierarchy) {
    empty?.classList.remove('hidden');
    return;
  }
  empty?.classList.add('hidden');

  const width = svgRoot.clientWidth || 900;
  const height = svgRoot.clientHeight || 720;

  const rootData = overviewScopeRoot() || state.data.hierarchy;
  const { root, descendants, minX, svgWidth, svgHeight, margin } = buildOverviewLayout(rootData, width, height);
  const svg = d3.select(svgRoot).append('svg').attr('width', svgWidth).attr('height', svgHeight);
  const group = svg.append('g').attr('transform', `translate(${margin.left},${margin.top - minX})`);
  descendants.forEach((d) => {
    d.vx = d.y;
    d.vy = d.x;
  });
  const nodeById = new Map(descendants.map((d) => [d.data.id, d]));
  renderDependencyOverlay(group, nodeById);

  group.selectAll('path.atlas-link')
    .data(root.links())
    .enter()
    .append('path')
    .attr('class', 'atlas-link')
    .attr('d', d3.linkHorizontal().x((d) => d.y).y((d) => d.x));
  renderOverviewNodes(group, descendants);

  if (state.workspaceTab === 'overview') {
    const title = DOM.centerTitle();
    if (title) title.textContent = `${t('overviewMode')} · ${displayNodeTitle(rootData.name)}`;
  }
}

function renderDependencyOverlay(group, nodeById) {
  if (!state.dependencyOverlayEnabled || !state.selectedNodeId) return;
  const edges = (state.data?.graph?.edges || []).filter(
    (edge) => edge.src === state.selectedNodeId || edge.dst === state.selectedNodeId
  ).filter((edge) => nodeById.has(edge.src) && nodeById.has(edge.dst));
  const overlay = group.append('g').attr('class', 'dependency-overlay');
  overlay.selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('class', (d) => `dependency-edge ${d.rel === 'addresses' ? 'addresses' : 'depends-on'}`)
    .attr('x1', (d) => nodeById.get(d.src).vx)
    .attr('y1', (d) => nodeById.get(d.src).vy)
    .attr('x2', (d) => nodeById.get(d.dst).vx)
    .attr('y2', (d) => nodeById.get(d.dst).vy);
}

function showTooltip(event, d) {
  const tooltip = document.getElementById('graph-tooltip');
  tooltip.classList.remove('hidden');
  const reviewGate = d.data.review_gate || {};
  const flags = (d.data.flags || []).map((flag) => t(flagToKey(flag))).join(' · ');
  const isSchedulerNext = d.data.id === state.data?.status?.next_node;
  const isPinned = state.pinnedNodeIds.has(d.data.id);
  const prioritySignals = [
    isSchedulerNext ? t('schedulerNext') : '',
    isPinned ? t('pinned') : '',
    detailTruthLabel(d.data),
  ].filter(Boolean).join(' · ');
  tooltip.innerHTML = `
    <strong>${html(displayNodeTitle(d.data.name))}</strong><br/>
    ${html(d.data.path || '')}<br/>
    ${t('status')}: ${html(d.data.status || 'seed')}<br/>
    ${t('truthState')}: ${html(detailTruthLabel(d.data))}<br/>
    ${prioritySignals ? `${html(prioritySignals)}<br/>` : ''}
    ${t('reviewGateState')}: ${html(reviewGateLabel(d.data.review_gate_state))} · ${t('executionGateState')}: ${html(executionGateLabel(d.data.execution_gate_state))}<br/>
    ${t('placeholderRisk')}: ${html(placeholderRiskLabel(d.data.placeholder_risk))}<br/>
    ${t('progress')}: ${html(d.data.progress_pct ?? '—')}<br/>
    ${t('aiReviews')}: ${html(reviewGate.ai_review_count ?? 0)} · ${t('humanReviews')}: ${html(reviewGate.human_review_count ?? 0)}<br/>
    ${t('lastActor')}: ${html(d.data.last_actor || '—')} · ${t('heartbeat')}: ${html(d.data.heartbeat_at || '—')}<br/>
    ${flags ? html(flags) + '<br/>' : ''}
    <span style="opacity:.78">${t('hoverHint')}</span>
  `;
  moveTooltip(event);
}

function moveTooltip(event) {
  const tooltip = document.getElementById('graph-tooltip');
  tooltip.style.left = `${event.offsetX + 18}px`;
  tooltip.style.top = `${event.offsetY + 18}px`;
}

function hideTooltip() {
  document.getElementById('graph-tooltip').classList.add('hidden');
}

function colorForStatus(status, nodeId) {
  const detail = nodeDetails(nodeId) || {};
  const truthClass = detailTruthClass(detail);
  if (truthClass === 'truth-ready') return '#2f7c60';
  if (truthClass === 'review-blocked') return '#9a641b';
  if (truthClass === 'execution-blocked') return '#675c7a';
  if (truthClass === 'truth-blocked') return '#675c7a';
  return ({
    seed: '#8b929a',
    active: '#0f6f7f',
    review: '#9a641b',
    fix: '#a33d45',
    done: '#47795d',
    archive: '#47795d',
  })[status] || '#aeb9c4';
}

function borderColorForStatus(status, nodeId) {
  return colorForStatus(status, nodeId);
}

function truncate(text, max) {
  if (!text) return '';
  return text.length > max ? `${text.slice(0, Math.max(1, max - 1))}…` : text;
}

function renderInspectorScope(scopeId) {
  const scope = findNodeInHierarchy(scopeId);
  const roll = scopeMetrics(scopeId);
  const root = document.getElementById('inspector-content');
  document.getElementById('inspector-meta').textContent = t('kindParent');
  root.innerHTML = `
    <div class="inspector-section">
      <h3>${html(displayNodeTitle(scope?.name || t('activeScope')))}</h3>
      <div class="kv-grid">
        <div class="kv"><div class="kv-label">${t('directChildren')}</div><div class="kv-value">${roll.children_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('leafDescendants')}</div><div class="kv-value">${roll.leaf_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('readyCount')}</div><div class="kv-value">${roll.scheduler_ready_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('blockedCount')}</div><div class="kv-value">${roll.scheduler_blocked_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('truthReadyCount')}</div><div class="kv-value">${roll.truth_ready_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('truthBlockedCount')}</div><div class="kv-value">${roll.truth_blocked_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('reviewGateState')}</div><div class="kv-value">${roll.review_blocked_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('executionGateState')}</div><div class="kv-value">${roll.execution_blocked_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('handoffReadiness')}</div><div class="kv-value">${roll.handoff_ready_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('placeholderRisk')}</div><div class="kv-value">${roll.placeholder_confirmed_count || 0}</div></div>
      </div>
    </div>
    <div class="inspector-section">
      <h3>${t('diagnostics')}</h3>
      <div class="kv-grid">
        <div class="kv"><div class="kv-label">${t('missingNodeSkillCount')}</div><div class="kv-value">${roll.missing_node_skill_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('missingSopCount')}</div><div class="kv-value">${roll.missing_sop_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('unexpectedNodeSkillCount')}</div><div class="kv-value">${roll.unexpected_node_skill_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('unexpectedSopCount')}</div><div class="kv-value">${roll.unexpected_sop_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('unexpectedLocalExecutionCount')}</div><div class="kv-value">${roll.unexpected_local_execution_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('missingExecutionBinderCount')}</div><div class="kv-value">${roll.missing_execution_binder_count || 0}</div></div>
        <div class="kv"><div class="kv-label">${t('thinLocalEntryCount')}</div><div class="kv-value">${roll.thin_local_entry_count || 0}</div></div>
      </div>
    </div>
  `;
}

function renderInspector() {
  const nodeId = state.selectedNodeId;
  const detail = nodeDetails(nodeId);
  const root = document.getElementById('inspector-content');
  if (!detail) {
    root.innerHTML = `<div class="empty-state"><h3>${t('selectScopeTitle')}</h3><p>${t('selectScopeBody')}</p></div>`;
    document.getElementById('inspector-meta').textContent = t('selectNode');
    return;
  }
  document.getElementById('inspector-meta').textContent = displayNodeTitle(detail.title);
  const skillFiles = detail.local_skill_files || [];
  const graph = state.data.graph || {};
  const outgoing = (graph.edges || []).filter((e) => e.src === nodeId);
  const incoming = (graph.edges || []).filter((e) => e.dst === nodeId);
  root.innerHTML = `
    <div class="inspector-section">
      <h3>${t('nodeProfile')}</h3>
      <div class="kv-grid">
        <div class="kv">
          <div class="kv-label">${t('status')}</div>
          <div class="kv-value">
            <div class="status-readonly">
              ${statusBadge(detail.status || 'seed', `status-${statusClass(detail.status || 'seed')}`)}
              <button class="mini-button status-link-button" type="button" data-open-node-status="true">${t('viewNodeStatus')}</button>
            </div>
          </div>
        </div>
        <div class="kv"><div class="kv-label">${t('truthState')}</div><div class="kv-value"><span class="badge status-${html(detailTruthClass(detail))}">${html(detailTruthLabel(detail))}</span></div></div>
        <div class="kv"><div class="kv-label">${t('handoffReadiness')}</div><div class="kv-value">${html(detail.handoff_readiness ?? '—')}</div></div>
        <div class="kv"><div class="kv-label">${t('reviewGateState')}</div><div class="kv-value">${html(reviewGateLabel(detail.review_gate_state))}</div></div>
        <div class="kv"><div class="kv-label">${t('executionGateState')}</div><div class="kv-value">${html(executionGateLabel(detail.execution_gate_state))}</div></div>
        <div class="kv"><div class="kv-label">${t('placeholderRisk')}</div><div class="kv-value">${html(placeholderRiskLabel(detail.placeholder_risk))}</div></div>
        <div class="kv"><div class="kv-label">${t('nodeMode')}</div><div class="kv-value">${html(detail.node_mode ?? '—')}</div></div>
        <div class="kv"><div class="kv-label">${t('nodeProfile')}</div><div class="kv-value">${html(detail.node_profile ?? '—')}</div></div>
      </div>
    </div>

    ${foldSection(t('files'), (detail.files || []).length ? (detail.files || []).map((file) => `
        <div class="kv">
          <div class="kv-label">${html(file.label)}</div>
          <div class="kv-value">${file.exists ? '✓' : '—'} · ${html(file.state ?? '')} · <a class="file-link" href="${fileHref(file.path)}" target="_blank">${html(file.path)}</a></div>
        </div>
      `).join('') : `<div class="section-meta">${t('noFiles')}</div>`)}

    ${foldSection(t('localSkills'), skillFiles.length ? skillFiles.map((file) => `<div class="kv"><div class="kv-value"><a class="file-link" href="${fileHref(file)}" target="_blank">${html(file)}</a></div></div>`).join('') : `<div class="section-meta">${t('noData')}</div>`)}

    ${foldSection(t('requiredLocalReads'), readListRows(detail.required_local_reads))}

    ${foldSection(t('optionalLocalReads'), readListRows(detail.optional_local_reads))}

    ${foldSection(t('blockingReasons'), blockingReasonsHtml(detail))}

    ${foldSection(t('links'), `
      <div class="kv"><div class="kv-label">${t('readme')}</div><div class="kv-value"><a class="file-link" href="${fileHref(detail.readme_path)}" target="_blank">${html(detail.readme_path)}</a></div></div>
      <div class="kv"><div class="kv-label">${t('statusFile')}</div><div class="kv-value"><a class="file-link" href="${fileHref(detail.status_path)}" target="_blank">${html(detail.status_path)}</a></div></div>
    `)}

    ${foldSection(`${t('relations')} · ${t('outgoing')} ${outgoing.length} / ${t('incoming')} ${incoming.length}`, renderNodeRelationsSection(outgoing, incoming))}
  `;
  const input = document.getElementById('target-node-input');
  if (input) input.value = nodeId;
  root.querySelector('[data-open-node-status="true"]')?.addEventListener('click', () => {
    setWorkspaceTab('node');
    appRuntime.renderAll();
    window.requestAnimationFrame(() => document.getElementById('node-status-select')?.focus());
  });
}

function renderNodeReviewSection(detail) {
  return `
    <div class="info-section">
      <h4>${t('review')}</h4>
      <div class="kv-grid">
        <div class="kv"><div class="kv-label">${t('reviewGateState')}</div><div class="kv-value">${html(reviewGateLabel(detail.review_gate_state))}</div></div>
        <div class="kv"><div class="kv-label">${t('executionGateState')}</div><div class="kv-value">${html(executionGateLabel(detail.execution_gate_state))}</div></div>
        <div class="kv"><div class="kv-label">${t('aiReviews')}</div><div class="kv-value">${detail.review_gate?.ai_review_count ?? 0}</div></div>
        <div class="kv"><div class="kv-label">${t('humanReviews')}</div><div class="kv-value">${detail.review_gate?.human_review_count ?? 0}</div></div>
        <div class="kv"><div class="kv-label">${t('responded')}</div><div class="kv-value">${boolText(detail.review_gate?.all_comments_responded)}</div></div>
        <div class="kv"><div class="kv-label">${t('placeholderRisk')}</div><div class="kv-value">${html(placeholderRiskLabel(detail.placeholder_risk))}</div></div>
      </div>
    </div>
  `;
}

function renderNodeRelationsSection(outgoing, incoming) {
  return `
    <div class="relation-list">
      <div class="relation-row">
        <strong>${t('outgoing')}</strong>
        <small>${outgoing.length ? outgoing.map((edge) => `${html(edge.rel)} → ${html(shortName(edge.dst))}`).join(' · ') : t('noRelations')}</small>
      </div>
      <div class="relation-row">
        <strong>${t('incoming')}</strong>
        <small>${incoming.length ? incoming.map((edge) => `${html(shortName(edge.src))} → ${html(edge.rel)}`).join(' · ') : t('noRelations')}</small>
      </div>
    </div>
  `;
}

function statusSelectHtml(id, currentStatus) {
  return `
    <select id="${html(id)}" class="status-select" aria-label="${html(t('updateStatus'))}">
      ${NODE_STAGES.map((stage) => `<option value="${html(stage)}" ${stage === currentStatus ? 'selected' : ''}>${html(stage)}</option>`).join('')}
    </select>
  `;
}

function bindStatusSelect(id, nodeId) {
  const select = document.getElementById(id);
  if (!select) return;
  select.addEventListener('change', () => {
    updateNodeStatus(nodeId, select.value).catch((err) => {
      renderAgentControls(`${t('statusUpdateFailed')}: ${err.message}`);
      renderNodePanel();
      renderInspector();
    });
  });
}

async function updateNodeStatus(nodeId, stage) {
  if (!nodeId || !NODE_STAGES.includes(stage)) return;
  renderAgentControls(t('updatingStatus'));
  await fetch('/api/node/' + encodeURIComponent(nodeId) + '/status', {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ stage }),
  }).then(async (response) => {
    if (!response.ok) {
      let data = null;
      try {
        data = await response.json();
      } catch (_) {
        data = null;
      }
      const detail = data?.detail?.message || data?.detail || data?.message || `status patch: ${response.status}`;
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
  });
  await appRuntime.loadAll({ preserveDirtyManuscript: true });
  renderAgentControls(t('refreshOk'));
}

function renderNodePanel() {
  const root = document.getElementById('node-panel');
  if (!root) return;

  const nodeId = state.selectedNodeId;
  const detail = nodeDetails(nodeId);
  if (!detail) {
    root.innerHTML = `<div class="empty-state"><h3>${t('selectScopeTitle')}</h3><p>${t('selectScopeBody')}</p></div>`;
    return;
  }

  root.innerHTML = `
    <div class="node-overview-grid">
      <div class="info-section">
        <h3>${html(displayNodeTitle(detail.title))}</h3>
        <div class="kv-grid">
          <div class="kv"><div class="kv-label">${t('status')}</div><div class="kv-value">${statusSelectHtml('node-status-select', detail.status || 'seed')}</div></div>
          <div class="kv"><div class="kv-label">${t('truthState')}</div><div class="kv-value">${html(detailTruthLabel(detail))}</div></div>
          <div class="kv"><div class="kv-label">${t('handoffReadiness')}</div><div class="kv-value">${html(detail.handoff_readiness ?? '—')}</div></div>
          <div class="kv"><div class="kv-label">${t('lifecycleStage')}</div><div class="kv-value">${html(detail.lifecycle_stage ?? '—')}</div></div>
          <div class="kv"><div class="kv-label">${t('progress')}</div><div class="kv-value">${html(detail.progress_pct ?? '—')}</div></div>
          <div class="kv"><div class="kv-label">${t('heartbeat')}</div><div class="kv-value">${html(detail.heartbeat_at ?? '—')}</div></div>
          <div class="kv"><div class="kv-label">${t('lastActor')}</div><div class="kv-value">${html(detail.last_actor ?? '—')}</div></div>
          <div class="kv"><div class="kv-label">${t('canEnterFix')}</div><div class="kv-value">${boolText(detail.can_enter_fix)}</div></div>
        </div>
      </div>
      ${renderNodeReviewSection(detail)}
    </div>
  `;
  bindStatusSelect('node-status-select', nodeId);
}

function renderActionButtons() {
  const selected = state.selectedNodeId;
  const pinButton = document.getElementById('pin-node-button');
  if (pinButton) {
    pinButton.disabled = !selected;
    pinButton.textContent = selected && state.pinnedNodeIds.has(selected) ? t('unpinNode') : t('pinNode');
  }
  const dependencyButton = document.getElementById('dependency-toggle-button');
  if (dependencyButton) {
    dependencyButton.classList.toggle('active', state.dependencyOverlayEnabled);
    dependencyButton.textContent = state.dependencyOverlayEnabled ? t('dependencyOn') : t('dependencyOff');
  }
  const openSessionButton = document.getElementById('open-session-button');
  if (openSessionButton) {
    openSessionButton.disabled = !selected && !state.activeScopeId;
  }
}

function togglePinnedNode(nodeId) {
  if (!nodeId) return;
  state.selectedNodeId = nodeId;
  const parent = parentScopeId(nodeId);
  if (parent) state.activeScopeId = parent;
  if (state.pinnedNodeIds.has(nodeId)) state.pinnedNodeIds.delete(nodeId);
  else state.pinnedNodeIds.add(nodeId);
  savePinnedNodes();
  renderTreeNavigator();
  renderFocusCard();
  renderWatchPanel();
  renderOverviewIfVisible();
  renderNodePanel();
  renderInspector();
  renderActionButtons();
  renderSessionContext();
  renderPromptActions();
  renderAgentControls();
}

function togglePinnedSelectedNode() {
  togglePinnedNode(state.selectedNodeId);
}

function openSessionForNode(nodeId) {
  if (nodeId) {
    if (!selectNode(nodeId)) return;
    const input = document.getElementById('target-node-input');
    if (input) input.value = nodeId;
  }
  openSessionForSelection();
}

function openSessionForSelection() {
  if (state.selectedNodeId) {
    state.sessionType = 'node';
    const input = document.getElementById('target-node-input');
    if (input) input.value = state.selectedNodeId;
  } else if (state.activeScopeId) {
    state.sessionType = 'scope';
  } else {
    state.sessionType = 'general';
  }
  localStorage.setItem('research_app_session_type', state.sessionType);
  syncCurrentSessionToContext();
  setWorkspaceTab('session');
  appRuntime.renderAll();
}

function renderGlobalChrome() {
  renderTopbar();
  if (!state.data) return;
  renderSetupStatus();
}

function renderNavigation() {
  if (!state.data) return;
  renderTreeNavigator();
  renderFocusCard();
  renderWatchPanel();
}

function renderWorkspace() {
  if (!state.data) {
    setWorkspaceTab(state.workspaceTab, { persist: false });
    return;
  }
  setWorkspaceTab(state.workspaceTab, { persist: false });
  renderOverviewIfVisible();
  renderNodePanel();
  renderManuscript();
  renderSessionHeader();
  renderSessionContext();
}

function renderWorkspacePanels() {
  if (!state.data) return;
  renderInspector();
  renderAgentCatalog();
  renderNodeOptions();
  const sessionTypeSelect = DOM.sessionTypeSelect();
  if (sessionTypeSelect) sessionTypeSelect.value = state.sessionType;
  renderPromptActions();
  renderAgentControls();
  renderSessions();
}

export {
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
};
