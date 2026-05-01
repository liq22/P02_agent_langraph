const PATHS = {
  graph: '../../backend/graph/graph.json',
  graphStatus: '../../backend/graph/graph_status.json',
  hierarchy: '../../backend/graph/hierarchy.json',
  nodeDetails: '../../backend/graph/node_details.json',
  scopeRollup: '../../backend/graph/scope_rollup.json',
  boardState: '../../backend/graph/board_state.json',
};

const PHASES = ['P0', 'P1', 'P2', 'P3', 'P4'];
const I18N = {
  zh: {
    brandEyebrow: 'Research OS',
    brandTitle: '研究状态看板',
    brandSubtitle: '用于层级监控、节点切换与多节点并行研究的前端工作台。',
    language: '语言',
    centerView: '中央视图',
    scopeFilter: '范围过滤',
    search: '搜索',
    showDependencies: '显示依赖',
    refresh: '刷新',
    overviewMode: '层级总览',
    boardMode: '研究看板',
    filterAll: '全部范围',
    filterCurrentPhase: '当前阶段',
    filterFocusScope: '当前焦点范围',
    scheduler: '调度器',
    scopeRail: '范围轨道',
    phaseRange: 'P0 → P4',
    focusScope: '当前焦点范围',
    directChildrenOnly: '仅显示直接子项',
    hotQueue: '热队列',
    humanFlow: '用于人类心流',
    centerPanel: '工作区',
    backToParent: '返回上一级',
    focusNextNode: '聚焦 next node',
    graphUnavailable: '层级图不可用。',
    dashboardStaticHint: '请从仓库根目录启动静态服务：python -m http.server 8000，然后打开 http://127.0.0.1:8000/web/dashboard/。',
    dashboardWrongRoot: '如果不是从仓库根目录启动，../../backend/graph/*.json 会加载失败。',
    nodeInspector: '节点检视器',
    selectNode: '选择一个节点',
    selectScopeTitle: '请选择范围或节点',
    selectScopeBody: '使用左侧 scope rail 或中央层级图查看状态、review gate、进度、心跳、文件和局部关系。',
    schedulerMeta: '同步调度摘要',
    active: '活跃',
    currentPhase: '当前阶段',
    nextNode: '调度下一节点',
    unfinishedCount: '未完成',
    readyCount: '调度就绪',
    blockedCount: '调度阻塞',
    truthReadyCount: '真值就绪',
    truthBlockedCount: '真值阻塞',
    truthState: '真值状态',
    handoffReadiness: '交接就绪',
    reviewGateState: '评审门状态',
    executionGateState: '执行门状态',
    blockingReasons: '阻断原因',
    placeholderRisk: '占位符风险',
    overviewTitle: '层级总览',
    boardTitle: '研究看板',
    boardSchedulerNow: '调度当前',
    boardTruthReady: '真值就绪',
    boardReviewBlocked: '评审阻塞',
    boardExecutionBlocked: '执行阻塞',
    boardTruthBlocked: '真值阻塞',
    boardActiveWork: '活跃工作',
    boardParked: '停放',
    laneSchedulerNowHint: '调度器当前选择的节点，不代表已经通过真值门',
    laneTruthReadyHint: '已满足真值与交接条件的节点',
    laneReviewBlockedHint: '真值成立但被外部评审门卡住',
    laneExecutionBlockedHint: '执行 contract 或执行产物仍阻塞',
    laneTruthBlockedHint: '研究真值、父节点汇总或未知阻断仍未解除',
    laneActiveWorkHint: '当前处于 active / review / fix 的工作节点',
    laneParkedHint: '暂时停放的节点',
    files: '文件',
    relations: '关系',
    state: '状态',
    review: '评审',
    links: '链接',
    progress: '进度',
    nodeMode: '节点模式',
    nodeProfile: '节点语义',
    status: '状态',
    aiReviews: 'AI 评审',
    humanReviews: '人工评审',
    responded: '评论已响应',
    canEnterFix: '可进入 fix',
    heartbeat: '心跳',
    lastActor: '最后操作者',
    incoming: '入边',
    outgoing: '出边',
    readme: 'README',
    statusFile: '状态文件',
    noFiles: '没有文件投影',
    noRelations: '没有局部关系',
    yes: '是',
    no: '否',
    unknown: '未知',
    root: '根范围',
    topScopes: '顶层范围',
    directChildren: '直接子项',
    leafDescendants: '叶子后代',
    hoverHint: '悬停查看摘要，点击聚焦',
    dependencyOverlay: '依赖覆盖',
    noData: '暂无数据',
    allScopes: '全部范围',
    currentPhaseFilterLabel: '当前阶段',
    focusedScopeFilterLabel: '焦点范围',
    fallbackOnly: '仅 fallback',
    missingLocalEntry: '缺少 local_entry',
    missingNodeSkill: '缺少 node skill',
    missingSop: '缺少 SOP',
    unexpectedNodeSkill: '多余 node skill',
    unexpectedSop: '多余 SOP',
    unexpectedLocalExecution: '多余 local_execution',
    missingExecutionBinder: '缺少 execution binder',
    thinLocalEntry: 'local_entry 过薄',
    diagnostics: '诊断',
    missingNodeSkillCount: '缺少 node skill',
    missingSopCount: '缺少 SOP',
    unexpectedNodeSkillCount: '多余 node skill',
    unexpectedSopCount: '多余 SOP',
    unexpectedLocalExecutionCount: '多余 local_execution',
    missingExecutionBinderCount: '缺少 execution binder',
    thinLocalEntryCount: 'local_entry 过薄',
    zeroProgressActive: 'active 但进度为 0',
    reviewNotStarted: 'review 尚未开始',
    stale: '可能陈旧',
    requiredLocalReads: '必需本地读取',
    optionalLocalReads: '按需本地读取',
    kindScope: '范围',
    kindParent: '父节点',
    kindLeaf: '叶子',
    schedulerNext: '调度下一节点',
    truthReady: '真值就绪',
    truthBlocked: '真值阻塞',
    reviewBlocked: '评审阻塞',
    executionBlocked: '执行阻塞',
    blockedParentRollup: '父节点汇总阻塞',
    blockedUnknown: '未知阻塞',
    gateNotRequired: '不需要',
    gateMissingVerdict: '缺少 verdict',
    gateIncomplete: '未完成',
    gateFailed: '失败',
    gatePassed: '通过',
    executionNotApplicable: '不适用',
    executionMissingContract: '缺少 contract',
    executionReviewOnly: '仅 review_only',
    executionContractIncomplete: 'contract 不完整',
    executionMissingOutputs: '缺少执行产物',
    executionFailed: '执行失败',
    executionReady: '执行就绪',
    placeholderNone: '无',
    placeholderSuspected: '疑似',
    placeholderConfirmed: '确认',
    statusSeed: 'seed',
    statusActive: 'active',
    statusReview: 'review',
    statusFix: 'fix',
    statusTerminal: 'done/archive',
    statusBlocked: 'blocked',
    statusNext: 'next',
    stateSummary: '状态摘要',
    activeScope: '活跃范围',
    viewNode: '查看节点',
    level: '层级',
    count: '数量',
    refreshIdle: '空闲',
    refreshLoading: '刷新中…',
    refreshOk: '已刷新',
    refreshFailed: '刷新失败',
  },
  en: {
    brandEyebrow: 'Research OS',
    brandTitle: 'Research Status Board',
    brandSubtitle: 'A hierarchy-first workspace for monitoring, switching, and parallel research across multiple nodes.',
    language: 'Language',
    centerView: 'Center view',
    scopeFilter: 'Scope filter',
    search: 'Search',
    showDependencies: 'Show dependencies',
    refresh: 'Refresh',
    overviewMode: 'Overview map',
    boardMode: 'Research board',
    filterAll: 'All scopes',
    filterCurrentPhase: 'Current phase',
    filterFocusScope: 'Focused scope',
    scheduler: 'Scheduler',
    scopeRail: 'Scope rail',
    phaseRange: 'P0 → P4',
    focusScope: 'Focused scope',
    directChildrenOnly: 'Direct children only',
    hotQueue: 'Hot queue',
    humanFlow: 'For human flow',
    centerPanel: 'Workspace',
    backToParent: 'Back to parent',
    focusNextNode: 'Focus next node',
    graphUnavailable: 'Hierarchy graph unavailable.',
    dashboardStaticHint: 'Start the static server from the repository root: python -m http.server 8000, then open http://127.0.0.1:8000/web/dashboard/.',
    dashboardWrongRoot: 'If the server is not started from the repository root, ../../backend/graph/*.json will fail to load.',
    nodeInspector: 'Node inspector',
    selectNode: 'Select a node',
    selectScopeTitle: 'Select a scope or node',
    selectScopeBody: 'Use the scope rail or hierarchy map to inspect status, review gate, progress, heartbeat, files, and local relations.',
    schedulerMeta: 'Synced scheduler summary',
    active: 'Active',
    currentPhase: 'Current phase',
    nextNode: 'Scheduler next',
    unfinishedCount: 'Unfinished',
    readyCount: 'Scheduler ready',
    blockedCount: 'Scheduler blocked',
    truthReadyCount: 'Truth ready',
    truthBlockedCount: 'Truth blocked',
    truthState: 'Truth state',
    handoffReadiness: 'Handoff readiness',
    reviewGateState: 'Review gate state',
    executionGateState: 'Execution gate state',
    blockingReasons: 'Blocking reasons',
    placeholderRisk: 'Placeholder risk',
    overviewTitle: 'Overview map',
    boardTitle: 'Research board',
    boardSchedulerNow: 'Scheduler now',
    boardTruthReady: 'Truth ready',
    boardReviewBlocked: 'Review blocked',
    boardExecutionBlocked: 'Execution blocked',
    boardTruthBlocked: 'Truth blocked',
    boardActiveWork: 'Active work',
    boardParked: 'Parked',
    laneSchedulerNowHint: 'The scheduler-selected node; not proof of truth readiness',
    laneTruthReadyHint: 'Nodes that satisfy truth and handoff conditions',
    laneReviewBlockedHint: 'Truth is satisfied but external review still blocks handoff',
    laneExecutionBlockedHint: 'Execution contract or outputs still block progress',
    laneTruthBlockedHint: 'Research truth, parent rollup, or unknown blockers remain',
    laneActiveWorkHint: 'Nodes currently in active / review / fix work',
    laneParkedHint: 'Intentionally parked nodes',
    files: 'Files',
    relations: 'Relations',
    state: 'State',
    review: 'Review',
    links: 'Links',
    progress: 'Progress',
    nodeMode: 'Node mode',
    nodeProfile: 'Node profile',
    status: 'Status',
    aiReviews: 'AI reviews',
    humanReviews: 'Human reviews',
    responded: 'Comments responded',
    canEnterFix: 'Can enter fix',
    heartbeat: 'Heartbeat',
    lastActor: 'Last actor',
    incoming: 'Incoming',
    outgoing: 'Outgoing',
    readme: 'README',
    statusFile: 'Status file',
    noFiles: 'No projected files',
    noRelations: 'No local relations',
    yes: 'Yes',
    no: 'No',
    unknown: 'Unknown',
    root: 'Root scope',
    topScopes: 'Top scopes',
    directChildren: 'Direct children',
    leafDescendants: 'Leaf descendants',
    hoverHint: 'Hover for summary, click to focus',
    dependencyOverlay: 'Dependency overlay',
    noData: 'No data',
    allScopes: 'All scopes',
    currentPhaseFilterLabel: 'Current phase',
    focusedScopeFilterLabel: 'Focused scope',
    fallbackOnly: 'Fallback only',
    missingLocalEntry: 'Missing local_entry',
    missingNodeSkill: 'Missing node skill',
    missingSop: 'Missing SOP',
    unexpectedNodeSkill: 'Unexpected node skill',
    unexpectedSop: 'Unexpected SOP',
    unexpectedLocalExecution: 'Unexpected local_execution',
    missingExecutionBinder: 'Missing execution binder',
    thinLocalEntry: 'Thin local_entry',
    diagnostics: 'Diagnostics',
    missingNodeSkillCount: 'Missing node skill',
    missingSopCount: 'Missing SOP',
    unexpectedNodeSkillCount: 'Unexpected node skill',
    unexpectedSopCount: 'Unexpected SOP',
    unexpectedLocalExecutionCount: 'Unexpected local_execution',
    missingExecutionBinderCount: 'Missing execution binder',
    thinLocalEntryCount: 'Thin local_entry',
    zeroProgressActive: 'Active but zero progress',
    reviewNotStarted: 'Review not started',
    stale: 'Possibly stale',
    requiredLocalReads: 'Required local reads',
    optionalLocalReads: 'Optional local reads',
    kindScope: 'Scope',
    kindParent: 'Parent',
    kindLeaf: 'Leaf',
    schedulerNext: 'Scheduler next',
    truthReady: 'Truth ready',
    truthBlocked: 'Truth blocked',
    reviewBlocked: 'Review blocked',
    executionBlocked: 'Execution blocked',
    blockedParentRollup: 'Parent rollup blocked',
    blockedUnknown: 'Unknown blocked',
    gateNotRequired: 'Not required',
    gateMissingVerdict: 'Missing verdict',
    gateIncomplete: 'Incomplete',
    gateFailed: 'Failed',
    gatePassed: 'Passed',
    executionNotApplicable: 'Not applicable',
    executionMissingContract: 'Missing contract',
    executionReviewOnly: 'Review only',
    executionContractIncomplete: 'Contract incomplete',
    executionMissingOutputs: 'Missing outputs',
    executionFailed: 'Failed',
    executionReady: 'Ready',
    placeholderNone: 'None',
    placeholderSuspected: 'Suspected',
    placeholderConfirmed: 'Confirmed',
    statusSeed: 'seed',
    statusActive: 'active',
    statusReview: 'review',
    statusFix: 'fix',
    statusTerminal: 'done/archive',
    statusBlocked: 'blocked',
    statusNext: 'next',
    stateSummary: 'State summary',
    activeScope: 'Active scope',
    viewNode: 'Inspect node',
    level: 'Depth',
    count: 'Count',
    refreshIdle: 'Idle',
    refreshLoading: 'Refreshing…',
    refreshOk: 'Refreshed',
    refreshFailed: 'Refresh failed',
  }
};

const STATUS_LABELS = {
  seed: { zh: 'seed', en: 'seed' },
  active: { zh: 'active', en: 'active' },
  review: { zh: 'review', en: 'review' },
  fix: { zh: 'fix', en: 'fix' },
  done: { zh: 'done', en: 'done' },
  archive: { zh: 'archive', en: 'archive' },
  blocked: { zh: 'blocked', en: 'blocked' },
  next: { zh: 'next', en: 'next' },
};

const state = {
  language: localStorage.getItem('research-dashboard-lang') || 'zh',
  centerView: localStorage.getItem('research-dashboard-view') || 'overview',
  scopeFilter: localStorage.getItem('research-dashboard-scope-filter') || 'all',
  search: '',
  showDependencies: false,
  data: null,
  selectedId: null,
  activeScopeId: 'research',
  graphSvg: null,
  hierarchyIndex: new Map(),
  visibleHierarchyRoot: null,
};

const el = {};

document.addEventListener('DOMContentLoaded', () => {
  bindElements();
  bindEvents();
  loadAll();
});

function bindElements() {
  el.languageToggle = document.getElementById('language-toggle');
  el.centerViewToggle = document.getElementById('center-view-toggle');
  el.scopeFilter = document.getElementById('scope-filter');
  el.searchInput = document.getElementById('search-input');
  el.dependencyToggle = document.getElementById('dependency-toggle');
  el.refreshButton = document.getElementById('refresh-button');
  el.heartbeat = document.getElementById('heartbeat');
  el.schedulerMeta = document.getElementById('scheduler-meta');
  el.schedulerCards = document.getElementById('scheduler-cards');
  el.scopeRail = document.getElementById('scope-rail');
  el.breadcrumb = document.getElementById('breadcrumb');
  el.scopeChildren = document.getElementById('scope-children');
  el.hotQueue = document.getElementById('hot-queue');
  el.centerTitle = document.getElementById('center-title');
  el.backScopeButton = document.getElementById('back-scope-button');
  el.focusNextButton = document.getElementById('focus-next-button');
  el.overviewView = document.getElementById('overview-view');
  el.boardView = document.getElementById('board-view');
  el.graphCanvas = document.getElementById('graph-canvas');
  el.graphEmpty = document.getElementById('graph-empty');
  el.graphTooltip = document.getElementById('graph-tooltip');
  el.boardLanes = document.getElementById('board-lanes');
  el.inspectorMeta = document.getElementById('inspector-meta');
  el.inspectorContent = document.getElementById('inspector-content');
}

function bindEvents() {
  el.languageToggle.value = state.language;
  el.centerViewToggle.value = state.centerView;
  el.scopeFilter.value = state.scopeFilter;

  el.languageToggle.addEventListener('change', (event) => {
    state.language = event.target.value;
    localStorage.setItem('research-dashboard-lang', state.language);
    renderAll();
  });

  el.centerViewToggle.addEventListener('change', (event) => {
    state.centerView = event.target.value;
    localStorage.setItem('research-dashboard-view', state.centerView);
    renderAll();
  });

  el.scopeFilter.addEventListener('change', (event) => {
    state.scopeFilter = event.target.value;
    localStorage.setItem('research-dashboard-scope-filter', state.scopeFilter);
    renderAll();
  });

  el.searchInput.addEventListener('input', (event) => {
    state.search = event.target.value.trim().toLowerCase();
    renderAll();
  });

  el.dependencyToggle.addEventListener('change', (event) => {
    state.showDependencies = event.target.checked;
    if (state.centerView === 'overview') renderOverview();
  });

  el.refreshButton.addEventListener('click', loadAll);
  el.backScopeButton.addEventListener('click', () => {
    const current = state.hierarchyIndex.get(state.activeScopeId);
    if (!current || !current.parentId) return;
    setActiveScope(current.parentId, { preserveSelection: true });
  });
  el.focusNextButton.addEventListener('click', focusNextNode);
}

function t(key) {
  return I18N[state.language]?.[key] ?? key;
}

function setHeartbeat(mode, extra = '') {
  const map = {
    idle: t('refreshIdle'),
    loading: t('refreshLoading'),
    ok: t('refreshOk'),
    failed: t('refreshFailed'),
  };
  el.heartbeat.textContent = extra ? `${map[mode]} · ${extra}` : map[mode];
}

async function loadAll() {
  setHeartbeat('loading');
  try {
    const [graph, graphStatus, hierarchy, nodeDetails, scopeRollup, boardState] = await Promise.all([
      fetchJson(PATHS.graph),
      fetchJson(PATHS.graphStatus),
      fetchJson(PATHS.hierarchy),
      fetchJson(PATHS.nodeDetails),
      fetchJson(PATHS.scopeRollup),
      fetchJson(PATHS.boardState),
    ]);

    state.data = normalizeData({ graph, graphStatus, hierarchy, nodeDetails, scopeRollup, boardState });

    if (!state.selectedId || !state.data.nodeIndex[state.selectedId]) {
      state.selectedId = state.data.graphStatus.next_node || state.data.hierarchy.id;
    }

    if (!state.activeScopeId || !state.data.hierarchyMap.has(state.activeScopeId)) {
      state.activeScopeId = state.data.activeScopeOf(state.selectedId);
    }

    setHeartbeat('ok', state.data.graphStatus.current_phase || '—');
    renderAll();
  } catch (error) {
    console.error(error);
    const message = error.message || 'load error';
    setHeartbeat('failed', message);
    el.graphEmpty.classList.remove('hidden');
    el.graphEmpty.innerHTML = `
      <div class="empty-state load-failure">
        <h3>${t('graphUnavailable')}</h3>
        <p>${html(message)}</p>
        <p>${t('dashboardStaticHint')}</p>
        <p class="section-meta">${t('dashboardWrongRoot')}</p>
      </div>
    `;
  }
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`${path} → ${response.status}`);
  }
  return response.json();
}

function normalizeData(raw) {
  const graph = raw.graph || {};
  const graphStatus = raw.graphStatus || {};
  const hierarchy = raw.hierarchy || { id: 'research', name: 'research', path: 'research', children: [] };
  const nodeDetailsPayload = raw.nodeDetails || { nodes: {} };
  const scopeRollupPayload = raw.scopeRollup || { scopes: {} };
  const boardStatePayload = raw.boardState || { lanes: {} };

  const nodeIndex = graph.nodes || {};
  const edges = Array.isArray(graph.edges) ? graph.edges : [];
  const nodeDetails = nodeDetailsPayload.nodes || {};
  const scopeRollup = scopeRollupPayload.scopes || {};
  const boardState = boardStatePayload.lanes || {};
  const hierarchyMap = new Map();

  walkHierarchy(hierarchy, null, hierarchyMap);

  const edgeIndex = buildEdgeIndex(edges);
  const activeScopeOf = (nodeId) => {
    if (!nodeId) return 'research';
    const nodeMeta = nodeIndex[nodeId];
    if (!nodeMeta) return 'research';
    const parts = nodeMeta.path.split('/');
    if (parts.length <= 2) return nodeId;
    return parts.slice(0, 2).join('::').replace('/', '::');
  };

  return {
    graph,
    graphStatus,
    hierarchy,
    nodeIndex,
    edges,
    nodeDetails,
    scopeRollup,
    boardState,
    hierarchyMap,
    edgeIndex,
    activeScopeOf,
  };
}

function walkHierarchy(node, parentId, map) {
  map.set(node.id, { ...node, parentId, children: node.children || [] });
  (node.children || []).forEach((child) => walkHierarchy(child, node.id, map));
}

function buildEdgeIndex(edges) {
  const incoming = new Map();
  const outgoing = new Map();
  edges.forEach((edge) => {
    if (!outgoing.has(edge.src)) outgoing.set(edge.src, []);
    if (!incoming.has(edge.dst)) incoming.set(edge.dst, []);
    outgoing.get(edge.src).push(edge);
    incoming.get(edge.dst).push(edge);
  });
  return { incoming, outgoing };
}

function renderAll() {
  if (!state.data) return;
  updateStaticCopy();
  renderScheduler();
  renderScopeRail();
  renderScopeChildren();
  renderHotQueue();
  renderCenter();
  renderInspector();
}

function updateStaticCopy() {
  document.documentElement.lang = state.language === 'zh' ? 'zh-CN' : 'en';
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-option]').forEach((option) => {
    option.textContent = t(option.dataset.i18nOption);
  });
  el.searchInput.placeholder = state.language === 'zh' ? 'P1_04 / 方法 / 路径' : 'P1_04 / method / path';
  el.centerTitle.textContent = state.centerView === 'overview' ? t('overviewTitle') : t('boardTitle');
  el.overviewView.classList.toggle('hidden', state.centerView !== 'overview');
  el.boardView.classList.toggle('hidden', state.centerView !== 'board');
  el.overviewView.classList.toggle('active', state.centerView === 'overview');
  el.boardView.classList.toggle('active', state.centerView === 'board');
}

function renderScheduler() {
  const gs = state.data.graphStatus;
  const truth = truthCounts();
  el.schedulerMeta.textContent = `${t('schedulerMeta')} · ${gs.current_phase || '—'}`;
  const cards = [
    [t('currentPhase'), gs.current_phase || '—'],
    [t('schedulerNext'), nodeLabel(gs.next_node)],
    [t('unfinishedCount'), gs.unfinished_count ?? 0],
    [t('readyCount'), (gs.ready_nodes || []).length],
    [t('blockedCount'), (gs.blocked_nodes || []).length],
    [t('truthReadyCount'), truth.ready],
    [t('truthBlockedCount'), truth.blocked],
    [t('activeScope'), nodeLabel(state.activeScopeId)],
  ];
  el.schedulerCards.innerHTML = cards.map(([label, value]) => `
    <article class="stat-card">
      <div class="stat-label">${escapeHtml(String(label))}</div>
      <div class="stat-value">${escapeHtml(String(value ?? '—'))}</div>
    </article>
  `).join('');
}

function renderScopeRail() {
  const container = el.scopeRail;
  container.innerHTML = '';
  PHASES.forEach((phase) => {
    const scopeNode = findPhaseScope(phase);
    const scopeMeta = scopeNode ? state.data.scopeRollup[scopeNode.id] : null;
    const node = document.createElement('button');
    node.type = 'button';
    node.className = `scope-chip ${scopeNode && state.activeScopeId === scopeNode.id ? 'active' : ''}`;
    node.innerHTML = `
      <div class="scope-chip-top">
        <span class="scope-title">${escapeHtml(scopeNode ? scopeNode.name : phase)}</span>
        <span class="scope-badges">
          ${(scopeMeta?.scheduler_next_descendants || 0) > 0 ? `<span class="badge scheduler-next">${t('schedulerNext')}</span>` : ''}
          ${(scopeMeta?.truth_blocked_count || 0) > 0 ? `<span class="badge truth-blocked">${t('truthBlockedCount')}: ${scopeMeta.truth_blocked_count}</span>` : ''}
          ${(scopeMeta?.truth_ready_count || 0) > 0 ? `<span class="badge truth-ready">${t('truthReadyCount')}: ${scopeMeta.truth_ready_count}</span>` : ''}
        </span>
      </div>
      <div class="scope-item-meta">${escapeHtml(summaryTextForScope(scopeMeta))}</div>
    `;
    node.addEventListener('click', () => {
      if (scopeNode) setActiveScope(scopeNode.id, { preserveSelection: false });
    });
    container.appendChild(node);
  });
}

function findPhaseScope(phase) {
  const rootChildren = state.data.hierarchy.children || [];
  return rootChildren.find((child) => child.name.startsWith(phase)) || null;
}

function summaryTextForScope(scopeMeta) {
  if (!scopeMeta) return t('noData');
  return `${t('readyCount')}: ${scopeMeta.scheduler_ready_count || 0} · ${t('blockedCount')}: ${scopeMeta.scheduler_blocked_count || 0} · ${t('truthReadyCount')}: ${scopeMeta.truth_ready_count || 0} · ${t('truthBlockedCount')}: ${scopeMeta.truth_blocked_count || 0}`;
}

function renderScopeChildren() {
  const container = el.scopeChildren;
  const crumb = el.breadcrumb;
  container.innerHTML = '';
  crumb.innerHTML = '';
  const scope = state.data.hierarchyMap.get(state.activeScopeId) || state.data.hierarchyMap.get('research');
  if (!scope) return;

  const breadcrumbNodes = [];
  let cursor = scope;
  while (cursor) {
    breadcrumbNodes.unshift(cursor);
    cursor = cursor.parentId ? state.data.hierarchyMap.get(cursor.parentId) : null;
  }
  breadcrumbNodes.forEach((item, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = item.name || t('root');
    button.addEventListener('click', () => setActiveScope(item.id, { preserveSelection: true }));
    crumb.appendChild(button);
    if (index < breadcrumbNodes.length - 1) {
      const sep = document.createElement('span');
      sep.textContent = '›';
      crumb.appendChild(sep);
    }
  });

  const children = filterScopeChildren(scope.children || []);
  children.forEach((child) => {
    const details = state.data.nodeDetails[child.id] || {};
    const node = document.createElement('button');
    node.type = 'button';
    node.className = `scope-item ${state.selectedId === child.id ? 'active' : ''}`;
    const flags = (details.flags || []).map(flagToLabel).map((label) => `<span class="badge flag">${escapeHtml(label)}</span>`).join('');
    node.innerHTML = `
      <div class="scope-item-title">${escapeHtml(child.name)}</div>
      <div class="scope-item-meta">${escapeHtml(child.path || '')}</div>
      <div class="scope-badges">
        <span class="badge ${badgeClassForNode(child.id)}">${escapeHtml(statusLabel(child.id))}</span>
        ${flags}
      </div>
    `;
    node.addEventListener('click', () => selectNode(child.id));
    container.appendChild(node);
  });
}

function filterScopeChildren(children) {
  if (!state.search) return children;
  return children.filter((child) => {
    const haystack = [child.name, child.path, (state.data.nodeDetails[child.id]?.title || '')].join(' ').toLowerCase();
    return haystack.includes(state.search);
  });
}

function renderHotQueue() {
  const container = el.hotQueue;
  container.innerHTML = '';
  const lanes = state.data.boardState;
  const hotIds = [
    ...(lanes.scheduler_now || []),
    ...(lanes.truth_ready || []),
    ...(lanes.active_work || []),
  ].slice(0, 8);

  hotIds.forEach((nodeId) => {
    const details = state.data.nodeDetails[nodeId] || {};
    const card = document.createElement('button');
    card.type = 'button';
    card.className = `queue-item ${state.selectedId === nodeId ? 'active' : ''}`;
    card.innerHTML = `
      <div class="queue-item-title">${escapeHtml(details.title || nodeLabel(nodeId))}</div>
      <div class="queue-item-meta">${escapeHtml(nodeLabel(nodeId))}</div>
      <div class="scope-badges">
        <span class="badge ${badgeClassForNode(nodeId)}">${escapeHtml(statusLabel(nodeId))}</span>
        ${nodeId === state.data.graphStatus.next_node ? `<span class="badge scheduler-next">${escapeHtml(t('schedulerNext'))}</span>` : ''}
      </div>
    `;
    card.addEventListener('click', () => selectNode(nodeId));
    container.appendChild(card);
  });
}

function renderCenter() {
  if (state.centerView === 'overview') {
    renderOverview();
  } else {
    renderBoard();
  }
}

function renderOverview() {
  const root = getVisibleHierarchyRoot();
  if (!root) {
    el.graphEmpty.classList.remove('hidden');
    return;
  }

  const container = el.graphCanvas;
  const width = container.clientWidth || 960;
  const height = container.clientHeight || 720;
  const tooltip = el.graphTooltip;
  container.innerHTML = '';
  el.graphEmpty.classList.add('hidden');

  const hierarchy = d3.hierarchy(root).sum((d) => (d.children?.length ? 0 : 1)).sort((a, b) => b.height - a.height || b.value - a.value);
  d3.pack().size([width, height]).padding(10)(hierarchy);

  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${width} ${height}`);
  const layer = svg.append('g');

  const nodes = hierarchy.descendants();
  const circles = layer.selectAll('g.node').data(nodes).join('g').attr('class', 'node').attr('transform', (d) => `translate(${d.x},${d.y})`);

  circles.append('circle')
    .attr('r', (d) => d.r)
    .attr('fill', (d) => fillForNode(d.data.id, !!(d.children && d.depth > 0)))
    .attr('fill-opacity', (d) => d.children ? 0.22 : 0.9)
    .attr('stroke', (d) => strokeForNode(d.data.id, !!d.children))
    .attr('stroke-width', (d) => d.data.id === state.selectedId ? 3.2 : (d.children ? 1.4 : 1.1))
    .attr('stroke-dasharray', (d) => state.showDependencies && isDependencyEndpoint(d.data.id) ? '5 4' : null)
    .on('mouseenter', function(event, d) {
      d3.select(this).attr('stroke-width', 3.2);
      showTooltip(event, d.data.id);
      d3.select(this.parentNode).raise();
    })
    .on('mousemove', moveTooltip)
    .on('mouseleave', function(event, d) {
      d3.select(this).attr('stroke-width', d.data.id === state.selectedId ? 3.2 : (d.children ? 1.4 : 1.1));
      hideTooltip();
    })
    .on('click', (event, d) => {
      event.stopPropagation();
      if (d.children && d.depth >= 0) {
        setActiveScope(d.data.id, { preserveSelection: false });
      }
      selectNode(d.data.id);
    });

  circles.filter((d) => d.r > 30).append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '0.34em')
    .attr('font-size', (d) => Math.max(11, Math.min(18, d.r / 3)))
    .attr('fill', '#181612')
    .style('pointer-events', 'none')
    .text((d) => ellipsis(d.data.name, d.r > 110 ? 28 : 16));

  if (state.showDependencies && state.selectedId) {
    drawDependencyOverlay(layer, hierarchy);
  }

  svg.on('click', () => hideTooltip());
  tooltip.classList.add('hidden');
}

function drawDependencyOverlay(layer, hierarchy) {
  const visible = new Map();
  hierarchy.descendants().forEach((node) => visible.set(node.data.id, node));
  const selectedId = state.selectedId;
  const relevant = [
    ...(state.data.edgeIndex.outgoing.get(selectedId) || []),
    ...(state.data.edgeIndex.incoming.get(selectedId) || []),
  ].filter((edge) => visible.has(edge.src) && visible.has(edge.dst));

  relevant.forEach((edge) => {
    const src = visible.get(edge.src);
    const dst = visible.get(edge.dst);
    if (!src || !dst) return;
    layer.append('line')
      .attr('x1', src.x)
      .attr('y1', src.y)
      .attr('x2', dst.x)
      .attr('y2', dst.y)
      .attr('stroke', edge.rel === 'depends_on' ? '#7a6658' : '#1c6277')
      .attr('stroke-width', 1.8)
      .attr('stroke-dasharray', edge.rel === 'depends_on' ? '6 6' : '2 6')
      .attr('opacity', 0.78);
  });
}

function renderBoard() {
  el.boardLanes.innerHTML = '';
  const lanes = [
    ['scheduler_now', t('boardSchedulerNow'), t('laneSchedulerNowHint')],
    ['truth_ready', t('boardTruthReady'), t('laneTruthReadyHint')],
    ['review_blocked', t('boardReviewBlocked'), t('laneReviewBlockedHint')],
    ['execution_blocked', t('boardExecutionBlocked'), t('laneExecutionBlockedHint')],
    ['truth_blocked', t('boardTruthBlocked'), t('laneTruthBlockedHint')],
    ['active_work', t('boardActiveWork'), t('laneActiveWorkHint')],
    ['parked', t('boardParked'), t('laneParkedHint')],
  ];

  lanes.forEach(([key, title, hint]) => {
    const lane = document.createElement('section');
    lane.className = 'board-lane';
    const list = (state.data.boardState[key] || []).filter(matchesCurrentFilter);
    lane.innerHTML = `
      <div>
        <h3>${escapeHtml(title)}</h3>
        <div class="board-lane-meta">${escapeHtml(hint)} · ${list.length}</div>
      </div>
      <div class="board-lane-list"></div>
    `;
    const listNode = lane.querySelector('.board-lane-list');
    list.forEach((nodeId) => {
      const detail = state.data.nodeDetails[nodeId] || {};
      const card = document.createElement('button');
      card.type = 'button';
      card.className = `board-card ${state.selectedId === nodeId ? 'active' : ''}`;
      card.innerHTML = `
        <div class="board-card-title">${escapeHtml(detail.title || nodeLabel(nodeId))}</div>
        <div class="board-card-meta">${escapeHtml(detail.path || nodeLabel(nodeId))}</div>
        <div class="scope-badges">
          <span class="badge ${badgeClassForNode(nodeId)}">${escapeHtml(statusLabel(nodeId))}</span>
          ${(detail.flags || []).slice(0, 2).map((flag) => `<span class="badge flag">${escapeHtml(flagToLabel(flag))}</span>`).join('')}
        </div>
      `;
      card.addEventListener('click', () => selectNode(nodeId));
      listNode.appendChild(card);
    });
    el.boardLanes.appendChild(lane);
  });
}

function renderInspector() {
  const nodeId = state.selectedId;
  if (!nodeId) return;
  const detail = state.data.nodeDetails[nodeId] || fallbackDetail(nodeId);
  const scopeMeta = state.data.scopeRollup[nodeId] || null;
  const incoming = state.data.edgeIndex.incoming.get(nodeId) || [];
  const outgoing = state.data.edgeIndex.outgoing.get(nodeId) || [];
  const files = detail.files || defaultFiles(detail);
  const localSkills = detail.local_skill_files || [];

  el.inspectorMeta.textContent = detail.title || nodeLabel(nodeId);
  el.inspectorContent.innerHTML = `
    <div>
      <h3 class="inspector-title">${escapeHtml(detail.title || nodeLabel(nodeId))}</h3>
      <p class="inspector-path">${escapeHtml(detail.path || nodeLabel(nodeId))}</p>
      <div class="scope-badges" style="margin-top:10px;">
        <span class="badge ${badgeClassForNode(nodeId)}">${escapeHtml(statusLabel(nodeId))}</span>
        <span class="badge flag">${escapeHtml(detail.kind ? (detail.kind === 'parent' ? t('kindParent') : t('kindLeaf')) : inferKind(nodeId))}</span>
        ${(detail.flags || []).map((flag) => `<span class="badge flag">${escapeHtml(flagToLabel(flag))}</span>`).join('')}
      </div>
    </div>

    <div class="inspector-grid">
      ${infoTile(t('status'), detail.status || '—')}
      ${infoTile(t('truthState'), detailTruthLabel(detail))}
      ${infoTile(t('handoffReadiness'), detail.handoff_readiness || '—')}
      ${infoTile(t('reviewGateState'), reviewGateLabel(detail.review_gate_state))}
      ${infoTile(t('executionGateState'), executionGateLabel(detail.execution_gate_state))}
      ${infoTile(t('placeholderRisk'), placeholderRiskLabel(detail.placeholder_risk))}
      ${infoTile(t('nodeMode'), detail.node_mode || '—')}
      ${infoTile(t('nodeProfile'), detail.node_profile || '—')}
      ${infoTile(t('progress'), detail.progress_pct ?? '—')}
      ${infoTile(t('aiReviews'), detail.review_gate?.ai_review_count ?? 0)}
      ${infoTile(t('humanReviews'), detail.review_gate?.human_review_count ?? 0)}
      ${infoTile(t('responded'), booleanLabel(detail.review_gate?.all_comments_responded))}
      ${infoTile(t('canEnterFix'), booleanLabel(detail.can_enter_fix))}
      ${infoTile(t('heartbeat'), detail.heartbeat_at || t('unknown'))}
      ${infoTile(t('lastActor'), detail.last_actor || t('unknown'))}
    </div>

    ${infoSection(t('files'), files.map((file) => `
      <div class="file-row">
        ${escapeHtml(file.label || file.path || t('unknown'))}
        <small>${escapeHtml(file.path || '')}${file.state ? ` · ${escapeHtml(file.state)}` : ''}</small>
      </div>
    `).join('') || `<div class="file-row">${escapeHtml(t('noFiles'))}</div>`)}

    ${infoSection(t('relations'), relationListHtml(incoming, outgoing))}

    ${infoSection(t('requiredLocalReads'), readListHtml(detail.required_local_reads))}

    ${infoSection(t('optionalLocalReads'), readListHtml(detail.optional_local_reads))}

    ${infoSection(t('blockingReasons'), blockingReasonsHtml(detail))}

    ${scopeMeta && scopeMeta.leaf_count !== undefined ? infoSection(t('diagnostics'), scopeDiagnosticsHtml(scopeMeta)) : ''}

    ${infoSection(t('links'), `
      <div class="link-list">
        ${detail.readme_path ? `<a href="../../${escapeHtml(detail.readme_path)}" target="_blank" rel="noreferrer">${escapeHtml(t('readme'))}</a>` : ''}
        ${detail.status_path ? `<a href="../../${escapeHtml(detail.status_path)}" target="_blank" rel="noreferrer">${escapeHtml(t('statusFile'))}</a>` : ''}
        ${localSkills.map((skillPath) => `<a href="../../${escapeHtml(skillPath)}" target="_blank" rel="noreferrer">${escapeHtml(skillPath)}</a>`).join('')}
      </div>
    `)}
  `;
}

function relationListHtml(incoming, outgoing) {
  const incomingHtml = incoming.length ? incoming.map((edge) => `
      <div class="relation-row">
        ${escapeHtml(t('incoming'))}: ${escapeHtml(edge.rel)}
        <small>${escapeHtml(nodeLabel(edge.src))}</small>
      </div>`).join('') : `<div class="relation-row">${escapeHtml(t('noRelations'))}</div>`;
  const outgoingHtml = outgoing.length ? outgoing.map((edge) => `
      <div class="relation-row">
        ${escapeHtml(t('outgoing'))}: ${escapeHtml(edge.rel)}
        <small>${escapeHtml(nodeLabel(edge.dst))}</small>
      </div>`).join('') : '';
  return `<div class="relation-list">${incomingHtml}${outgoingHtml}</div>`;
}

function infoTile(label, value) {
  return `
    <div class="info-tile">
      <div class="info-label">${escapeHtml(String(label))}</div>
      <div class="info-value">${escapeHtml(String(value ?? '—'))}</div>
    </div>
  `;
}

function infoSection(title, body) {
  return `
    <section class="info-section">
      <h4>${escapeHtml(title)}</h4>
      ${body}
    </section>
  `;
}

function readListHtml(items) {
  if (!items || !items.length) {
    return `<div class="file-row">${escapeHtml(t('noData'))}</div>`;
  }
  return items.map((item) => `
      <div class="file-row">
        ${escapeHtml(item)}
      </div>
    `).join('');
}

function scopeDiagnosticsHtml(roll) {
  const items = [
    [t('missingNodeSkillCount'), roll.missing_node_skill_count || 0],
    [t('missingSopCount'), roll.missing_sop_count || 0],
    [t('unexpectedNodeSkillCount'), roll.unexpected_node_skill_count || 0],
    [t('unexpectedSopCount'), roll.unexpected_sop_count || 0],
    [t('unexpectedLocalExecutionCount'), roll.unexpected_local_execution_count || 0],
    [t('missingExecutionBinderCount'), roll.missing_execution_binder_count || 0],
    [t('thinLocalEntryCount'), roll.thin_local_entry_count || 0],
    [t('truthReadyCount'), roll.truth_ready_count || 0],
    [t('truthBlockedCount'), roll.truth_blocked_count || 0],
    [t('placeholderRisk'), roll.placeholder_confirmed_count || 0],
  ];
  return `<div class="inspector-grid">${items.map(([label, value]) => infoTile(label, value)).join('')}</div>`;
}

function defaultFiles(detail) {
  return [
    detail.readme_path ? { label: t('readme'), path: detail.readme_path, state: 'entry' } : null,
    detail.status_path ? { label: t('statusFile'), path: detail.status_path, state: detail.status || 'seed' } : null,
  ].filter(Boolean);
}

function fallbackDetail(nodeId) {
  const meta = state.data.nodeIndex[nodeId] || {};
  return {
    title: nodeLabel(nodeId),
    path: meta.path,
    status: meta.status,
    kind: inferKind(nodeId),
    review_gate: {},
    flags: [],
    readme_path: meta.path ? `${meta.path}/README.md` : null,
    status_path: meta.path ? `${meta.path}/status.yaml` : null,
  };
}

function getVisibleHierarchyRoot() {
  let root = state.data.hierarchyMap.get('research');
  if (state.scopeFilter === 'focus-scope') {
    root = state.data.hierarchyMap.get(state.activeScopeId) || root;
  } else if (state.scopeFilter === 'current-phase') {
    const phase = state.data.graphStatus.current_phase;
    const phaseScope = findPhaseScope(phase);
    root = phaseScope ? state.data.hierarchyMap.get(phaseScope.id) : root;
  }
  state.visibleHierarchyRoot = root;
  return root;
}

function setActiveScope(scopeId, { preserveSelection = true } = {}) {
  if (!scopeId || !state.data.hierarchyMap.has(scopeId)) return;
  state.activeScopeId = scopeId;
  state.scopeFilter = 'focus-scope';
  el.scopeFilter.value = 'focus-scope';
  localStorage.setItem('research-dashboard-scope-filter', state.scopeFilter);
  if (!preserveSelection) {
    state.selectedId = scopeId;
  }
  renderAll();
}

function selectNode(nodeId) {
  state.selectedId = nodeId;
  const activeScope = state.data.activeScopeOf(nodeId);
  if (state.scopeFilter === 'focus-scope' && activeScope) {
    state.activeScopeId = activeScope;
  }
  renderAll();
}

function focusNextNode() {
  const nextNode = state.data.graphStatus.next_node;
  if (!nextNode) return;
  state.selectedId = nextNode;
  setActiveScope(state.data.activeScopeOf(nextNode), { preserveSelection: true });
}

function nodeLabel(nodeId) {
  if (!nodeId) return '—';
  const detail = state.data?.nodeDetails?.[nodeId];
  if (detail?.title) return detail.title;
  const meta = state.data?.nodeIndex?.[nodeId];
  if (meta?.path) return meta.path.split('/').pop();
  return String(nodeId).split('::').pop();
}

function statusLabel(nodeId) {
  const detail = state.data.nodeDetails[nodeId] || state.data.nodeIndex[nodeId] || {};
  if (nodeId === state.data.graphStatus.next_node) return t('schedulerNext');
  return detailTruthLabel(detail);
}

function badgeClassForNode(nodeId) {
  const detail = state.data.nodeDetails[nodeId] || state.data.nodeIndex[nodeId] || {};
  if (nodeId === state.data.graphStatus.next_node) return 'status-scheduler-next';
  return `status-${detailTruthClass(detail)}`;
}

function inferKind(nodeId) {
  const scope = state.data.hierarchyMap.get(nodeId);
  return scope && scope.children && scope.children.length ? t('kindParent') : t('kindLeaf');
}

function flagToLabel(flag) {
  return {
    'fallback-only': t('fallbackOnly'),
    'missing-local-entry': t('missingLocalEntry'),
    'missing-node-skill': t('missingNodeSkill'),
    'missing-sop': t('missingSop'),
    'unexpected-node-skill': t('unexpectedNodeSkill'),
    'unexpected-sop': t('unexpectedSop'),
    'unexpected-local-execution': t('unexpectedLocalExecution'),
    'missing-execution-binder': t('missingExecutionBinder'),
    'thin-local-entry': t('thinLocalEntry'),
    'zero-progress-active': t('zeroProgressActive'),
    'review-not-started': t('reviewNotStarted'),
    'stale': t('stale'),
  }[flag] || flag;
}

function booleanLabel(value) {
  if (value === true) return t('yes');
  if (value === false) return t('no');
  return t('unknown');
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

function truthCounts() {
  const details = state.data?.nodeDetails || {};
  let ready = 0;
  let blocked = 0;
  Object.values(details).forEach((detail) => {
    if (!detail || typeof detail !== 'object') return;
    if (detail.handoff_readiness === 'ready') ready += 1;
    else if (detail.handoff_readiness) blocked += 1;
  });
  return { ready, blocked };
}

function matchesCurrentFilter(nodeId) {
  const meta = state.data.nodeIndex[nodeId] || {};
  if (state.scopeFilter === 'current-phase') {
    return (meta.path || '').split('/')[1]?.startsWith(state.data.graphStatus.current_phase || '');
  }
  if (state.scopeFilter === 'focus-scope') {
    const scope = state.data.hierarchyMap.get(state.activeScopeId);
    return scope ? (meta.path || '').startsWith(scope.path || '') : true;
  }
  return true;
}

function fillForNode(nodeId, isScope) {
  const status = statusColorKey(nodeId, isScope);
  const map = {
    scope: 'rgba(216, 207, 191, 0.35)',
    seed: 'rgba(201, 188, 166, 0.86)',
    active: 'rgba(28, 98, 119, 0.82)',
    review: 'rgba(187, 124, 45, 0.84)',
    fix: 'rgba(150, 75, 57, 0.84)',
    terminal: 'rgba(112, 131, 106, 0.84)',
    blocked: 'rgba(122, 102, 88, 0.88)',
    next: 'rgba(16, 16, 16, 0.92)',
  };
  return map[status] || map.seed;
}

function strokeForNode(nodeId, isScope) {
  const status = statusColorKey(nodeId, isScope);
  const map = {
    scope: 'rgba(24,22,18,0.16)',
    seed: 'rgba(24,22,18,0.24)',
    active: 'rgba(28, 98, 119, 0.9)',
    review: 'rgba(187,124,45,0.9)',
    fix: 'rgba(150,75,57,0.9)',
    terminal: 'rgba(112,131,106,0.9)',
    blocked: 'rgba(122,102,88,0.92)',
    next: 'rgba(16,16,16,1)',
  };
  return map[status] || map.seed;
}

function statusColorKey(nodeId, isScope) {
  const detail = state.data.nodeDetails[nodeId] || state.data.nodeIndex[nodeId] || {};
  if (nodeId === state.data.graphStatus.next_node) return 'next';
  if (detailTruthClass(detail) === 'truth-ready') return 'ready';
  if (detailTruthClass(detail) === 'review-blocked') return 'review';
  if (detailTruthClass(detail) === 'execution-blocked' || detailTruthClass(detail) === 'truth-blocked') return 'blocked';
  if (['done', 'archive'].includes(detail.status)) return 'terminal';
  if (isScope && !(detail.status && detail.status !== 'seed')) return 'scope';
  return detail.status || 'seed';
}

function isDependencyEndpoint(nodeId) {
  const selected = state.selectedId;
  if (!selected) return false;
  return nodeId === selected || (state.data.edgeIndex.incoming.get(selected) || []).some((e) => e.src === nodeId) || (state.data.edgeIndex.outgoing.get(selected) || []).some((e) => e.dst === nodeId);
}

function showTooltip(event, nodeId) {
  const detail = state.data.nodeDetails[nodeId] || fallbackDetail(nodeId);
  const scopeMeta = state.data.scopeRollup[nodeId] || {};
  el.graphTooltip.innerHTML = `
    <strong>${escapeHtml(detail.title || nodeLabel(nodeId))}</strong>
    <div>${escapeHtml(detail.path || nodeLabel(nodeId))}</div>
    <div style="margin-top:6px;">${escapeHtml(t('truthState'))}: ${escapeHtml(detailTruthLabel(detail))}</div>
    <div>${escapeHtml(t('reviewGateState'))}: ${escapeHtml(reviewGateLabel(detail.review_gate_state))}</div>
    <div>${escapeHtml(t('executionGateState'))}: ${escapeHtml(executionGateLabel(detail.execution_gate_state))}</div>
    <div>${escapeHtml(t('placeholderRisk'))}: ${escapeHtml(placeholderRiskLabel(detail.placeholder_risk))}</div>
    <div>${escapeHtml(t('progress'))}: ${escapeHtml(String(detail.progress_pct ?? '—'))}</div>
    ${scopeMeta.leaf_count !== undefined ? `<div>${escapeHtml(t('leafDescendants'))}: ${escapeHtml(String(scopeMeta.leaf_count))}</div>` : ''}
    <div style="margin-top:6px; color: rgba(244,239,231,0.72);">${escapeHtml(t('hoverHint'))}</div>
  `;
  el.graphTooltip.classList.remove('hidden');
  moveTooltip(event);
}

function moveTooltip(event) {
  const rect = el.graphCanvas.getBoundingClientRect();
  const x = event.clientX - rect.left + 18;
  const y = event.clientY - rect.top + 18;
  el.graphTooltip.style.left = `${x}px`;
  el.graphTooltip.style.top = `${y}px`;
}

function hideTooltip() {
  el.graphTooltip.classList.add('hidden');
}

function blockingReasonsHtml(detail) {
  const reasons = Array.isArray(detail.blocking_reasons) ? detail.blocking_reasons : [];
  if (!reasons.length) {
    return `<div class="file-row">${escapeHtml(t('noData'))}</div>`;
  }
  return reasons.map((reason) => `
      <div class="file-row">
        ${escapeHtml(reason)}
      </div>
    `).join('');
}

function ellipsis(text, max) {
  if (!text) return '';
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
