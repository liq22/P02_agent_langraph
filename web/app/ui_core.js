const API = {
  bootstrap: '/api/app/bootstrap',
  status: '/api/graph/status',
  structure: '/api/graph/structure',
  hierarchy: '/api/graph/hierarchy',
  details: '/api/graph/details',
  rollup: '/api/graph/rollup',
  board: '/api/graph/board',
  catalog: '/api/agents/catalog',
  sessions: '/api/agents/sessions',
  health: '/api/health'
};

const VALID_WORKSPACE_TABS = new Set(['overview', 'node', 'manuscript', 'session']);
const VALID_SESSION_TYPES = new Set(['general', 'scope', 'node']);
const CONTEXT_MENTIONS = ['@current', '@scope', '@node', '@readme', '@status', '@manuscript'];
const NODE_STAGES = ['seed', 'active', 'review', 'fix', 'done', 'archive'];
const CURRENT_SESSION_STORAGE_KEY = 'research_app_current_session_id';
const HEARTBEAT_STATES = {
  refreshIdle: 'ready',
  refreshLoading: 'loading',
  refreshOk: 'ready',
  refreshFailed: 'failed',
  heartbeatGateway: 'gateway',
};

const DOM = {
  byId: (id) => document.getElementById(id),
  languageToggle: () => document.getElementById('language-toggle'),
  globalSearchInput: () => document.getElementById('global-search-input'),
  topbarSummary: () => document.getElementById('topbar-summary'),
  centerTitle: () => document.getElementById('center-title'),
  overviewView: () => document.getElementById('overview-view'),
  nodeView: () => document.getElementById('node-view'),
  manuscriptView: () => document.getElementById('manuscript-view'),
  sessionView: () => document.getElementById('session-view'),
  graphCanvas: () => document.getElementById('graph-canvas'),
  graphEmpty: () => document.getElementById('graph-empty'),
  dependencyToggleButton: () => document.getElementById('dependency-toggle-button'),
  pinNodeButton: () => document.getElementById('pin-node-button'),
  openSessionButton: () => document.getElementById('open-session-button'),
  sessionTypeSelect: () => document.getElementById('session-type-select'),
  sessionHeader: () => document.getElementById('session-header'),
  sessionContextContent: () => document.getElementById('session-context-content'),
  sessionList: () => document.getElementById('session-list'),
  sessionLog: () => document.getElementById('session-log'),
  contextDrawer: () => document.getElementById('context-drawer'),
  watchContent: () => document.getElementById('watch-content'),
};

const I18N = {
  zh: {
    brandEyebrow: 'Research OS',
    brandTitle: '研究 Agent 控制台',
    brandSubtitle: '层级监控、研究看板与有界本地 agent 执行的一体化工作台。',
    language: '语言',
    refresh: '刷新',
    search: '搜索',
    treeNavigator: '树状导航',
    collapseAll: '全部折叠',
    expandActivePath: '展开当前路径',
    focusScope: '当前焦点范围',
    directChildrenOnly: '仅显示直接子项',
    humanFlow: '用于人类心流',
    workspace: '工作区',
    backToParent: '返回上一级',
    focusNextNode: '聚焦 next node',
    dependencyOverlay: '依赖诊断',
    dependencyOn: '依赖诊断开启',
    dependencyOff: '依赖诊断关闭',
    pinNode: '加入关注集',
    unpinNode: '移出关注集',
    openSession: '打开会话',
    moreActions: '更多操作',
    graphUnavailable: '层级图不可用。',
    nodeInspector: '节点检视器',
    selectNode: '选择一个节点',
    selectScopeTitle: '请选择范围或节点',
    selectScopeBody: '使用左侧树或中央层级图查看状态、评审、文件与局部关系。',
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
    overviewMode: '层级总览',
    manuscriptMode: 'Manuscript',
    sessionMode: 'Agent 会话',
    topScopes: '顶层范围',
    directChildren: '直接子项',
    leafDescendants: '叶子后代',
    activeScope: '活跃范围',
    hoverHint: '悬停看摘要，点击聚焦',
    state: '状态',
    review: '评审',
    files: '文件',
    localSkills: '本地 skills',
    relations: '关系',
    links: '链接',
    status: '状态',
    lifecycleStage: '生命周期',
    progress: '进度',
    nodeMode: '节点模式',
    nodeProfile: '节点语义',
    requiredLocalReads: '必需本地读取',
    optionalLocalReads: '按需本地读取',
    diagnostics: '诊断',
    missingNodeSkill: '缺少 node skill',
    missingSop: '缺少 SOP',
    unexpectedNodeSkill: '多余 node skill',
    unexpectedSop: '多余 SOP',
    unexpectedLocalExecution: '多余 local_execution',
    missingExecutionBinder: '缺少 execution binder',
    thinLocalEntry: 'local_entry 过薄',
    missingNodeSkillCount: '缺少 node skill',
    missingSopCount: '缺少 SOP',
    unexpectedNodeSkillCount: '多余 node skill',
    unexpectedSopCount: '多余 SOP',
    unexpectedLocalExecutionCount: '多余 local_execution',
    missingExecutionBinderCount: '缺少 execution binder',
    thinLocalEntryCount: 'local_entry 过薄',
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
    laneWatchHint: '本地关注工作集；不会改变 next node、调度队列或节点状态。',
    agent: 'Agent',
    targetNode: '目标节点',
    prompt: '提示词',
    createSession: '新建会话',
    runPrompt: '执行',
    stopSession: '停止',
    sessions: '会话',
    sessionLog: '会话日志',
    sessionType: '会话类型',
    sessionGeneral: 'General',
    sessionScope: 'Scope',
    sessionNode: 'Node',
    boundScope: '绑定范围',
    boundNode: '绑定节点',
    currentSession: '当前会话',
    sessionDraft: '待运行上下文',
    boundedNotice: '有界执行：只围绕当前 graph 上下文行动，不接管全局调度。',
    noSession: '尚无会话',
    pinned: '已关注',
    currentFocus: '当前焦点',
    watchedNodes: '关注工作集',
    updateStatus: '更新状态',
    updatingStatus: '状态更新中…',
    statusUpdateFailed: '状态更新失败',
    refreshIdle: '空闲',
    refreshLoading: '刷新中…',
    refreshOk: '已刷新',
    refreshFailed: '刷新失败',
    heartbeatGateway: 'Gateway 未连接',
    fallbackOnly: '仅 fallback',
    zeroProgressActive: 'active 但进度为 0',
    reviewNotStarted: 'review 尚未开始',
    stale: '可能陈旧',
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
    noData: '暂无数据',
    inspect: '检视',
    sessionTarget: 'Session',
    frontendContractMismatch: '前端 DOM 契约不匹配',
    exampleConfig: '示例配置',
    setupStatus: '启动状态',
    setupReady: '已就绪',
    setupNeedsAttention: '需要处理',
    setupSteps: '下一步',
    canRun: '可执行',
    cannotRun: '不可执行',
    actionAnalyze: '分析当前上下文',
    actionBlockers: '解释阻塞',
    actionExperiment: '建议下一实验',
    actionRunBounded: '运行有界 worker',
    actionDraft: '起草 proposal',
    missingLocalEntry: '缺少 local_entry',
    runBlocked: '执行被阻止',
    targetMissing: '请选择目标节点',
    scopeMissing: '请选择目标范围',
    lastError: '最近错误',
    gatewayUnavailableTitle: 'Agent Cockpit 未连接到 gateway',
    gatewayUnavailableBody: '当前页面需要 FastAPI gateway 提供 /api/*。请从仓库根目录启动 gateway 后再打开页面。',
    gatewayStartCommand: '启动命令',
    gatewayOpenUrl: '打开地址',
    gatewayWrongStaticServer: '不要用 python -m http.server 或 file:// 打开 web/app。静态服务只适合 web/dashboard。',
    gatewayRetryHint: '启动后刷新本页。',
    repoRoot: '仓库根目录',
    reload: 'Reload',
    revert: 'Revert',
    save: 'Save',
    contextDrawer: '上下文抽屉',
    collapseDrawer: '折叠',
    expandDrawer: '展开',
    collapseNavigation: '收起导航',
    expandNavigation: '展开导航',
    manuscriptDirty: '未保存',
    manuscriptSaved: '已保存',
    manuscriptSaving: '保存中',
    manuscriptSaveFailed: '保存失败',
    manuscriptNoFile: '未加载文件',
    manuscriptDiscardConfirm: '当前 manuscript 有未保存修改。放弃这些修改？',
    manuscriptSaveFirst: '请先保存 manuscript，再运行 @manuscript 会话。',
    manuscriptContextLoadFailed: '无法加载 @manuscript 上下文',
    resolvedMentions: '已解析上下文',
    viewNodeStatus: '去节点模式修改',
  },
  en: {
    brandEyebrow: 'Research OS',
    brandTitle: 'Research Agent Cockpit',
    brandSubtitle: 'A hierarchy-first workspace for monitoring, research flow, and bounded local agent execution.',
    language: 'Language',
    refresh: 'Refresh',
    search: 'Search',
    treeNavigator: 'Tree navigator',
    collapseAll: 'Collapse all',
    expandActivePath: 'Expand active path',
    focusScope: 'Focused scope',
    directChildrenOnly: 'Direct children only',
    humanFlow: 'For human flow',
    workspace: 'Workspace',
    backToParent: 'Back to parent',
    focusNextNode: 'Focus next node',
    dependencyOverlay: 'Dependency diagnostics',
    dependencyOn: 'Dependency diagnostics on',
    dependencyOff: 'Dependency diagnostics off',
    pinNode: 'Watch node',
    unpinNode: 'Unwatch node',
    openSession: 'Open session',
    moreActions: 'More actions',
    graphUnavailable: 'Hierarchy graph unavailable.',
    nodeInspector: 'Node inspector',
    selectNode: 'Select a node',
    selectScopeTitle: 'Select a scope or node',
    selectScopeBody: 'Use the left tree or hierarchy map to inspect state, review, files, and local relations.',
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
    overviewMode: 'Overview',
    manuscriptMode: 'Manuscript',
    sessionMode: 'Agent session',
    topScopes: 'Top scopes',
    directChildren: 'Direct children',
    leafDescendants: 'Leaf descendants',
    activeScope: 'Active scope',
    hoverHint: 'Hover for summary, click to focus',
    state: 'State',
    review: 'Review',
    files: 'Files',
    localSkills: 'Local skills',
    relations: 'Relations',
    links: 'Links',
    status: 'Status',
    lifecycleStage: 'Lifecycle',
    progress: 'Progress',
    nodeMode: 'Node mode',
    nodeProfile: 'Node profile',
    requiredLocalReads: 'Required local reads',
    optionalLocalReads: 'Optional local reads',
    diagnostics: 'Diagnostics',
    missingNodeSkill: 'Missing node skill',
    missingSop: 'Missing SOP',
    unexpectedNodeSkill: 'Unexpected node skill',
    unexpectedSop: 'Unexpected SOP',
    unexpectedLocalExecution: 'Unexpected local_execution',
    missingExecutionBinder: 'Missing execution binder',
    thinLocalEntry: 'Thin local_entry',
    missingNodeSkillCount: 'Missing node skill',
    missingSopCount: 'Missing SOP',
    unexpectedNodeSkillCount: 'Unexpected node skill',
    unexpectedSopCount: 'Unexpected SOP',
    unexpectedLocalExecutionCount: 'Unexpected local_execution',
    missingExecutionBinderCount: 'Missing execution binder',
    thinLocalEntryCount: 'Thin local_entry',
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
    laneWatchHint: 'Local watched workset only; it does not change next-node, scheduler queue, or node state.',
    agent: 'Agent',
    targetNode: 'Target node',
    prompt: 'Prompt',
    createSession: 'Create session',
    runPrompt: 'Run',
    stopSession: 'Stop',
    sessions: 'Sessions',
    sessionLog: 'Session log',
    sessionType: 'Session type',
    sessionGeneral: 'General',
    sessionScope: 'Scope',
    sessionNode: 'Node',
    boundScope: 'Bound scope',
    boundNode: 'Bound node',
    currentSession: 'Current session',
    sessionDraft: 'Draft context',
    boundedNotice: 'Bounded execution: act only within the current graph context and do not take over global scheduling.',
    noSession: 'No session yet',
    pinned: 'Watched',
    currentFocus: 'Current focus',
    watchedNodes: 'Watched workset',
    updateStatus: 'Update status',
    updatingStatus: 'Updating status…',
    statusUpdateFailed: 'Status update failed',
    refreshIdle: 'Idle',
    refreshLoading: 'Refreshing…',
    refreshOk: 'Refreshed',
    refreshFailed: 'Refresh failed',
    heartbeatGateway: 'Gateway unavailable',
    fallbackOnly: 'Fallback only',
    zeroProgressActive: 'Active but zero progress',
    reviewNotStarted: 'Review not started',
    stale: 'Possibly stale',
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
    noData: 'No data',
    inspect: 'Inspect',
    sessionTarget: 'Session',
    frontendContractMismatch: 'Frontend DOM contract mismatch',
    exampleConfig: 'example config',
    setupStatus: 'Setup status',
    setupReady: 'Ready',
    setupNeedsAttention: 'Needs attention',
    setupSteps: 'Next steps',
    canRun: 'Runnable',
    cannotRun: 'Not runnable',
    actionAnalyze: 'Analyze context',
    actionBlockers: 'Explain blockers',
    actionExperiment: 'Suggest next experiment',
    actionRunBounded: 'Run bounded worker',
    actionDraft: 'Draft proposal',
    missingLocalEntry: 'Missing local_entry',
    runBlocked: 'Run blocked',
    targetMissing: 'Select target node',
    scopeMissing: 'Select target scope',
    lastError: 'Last error',
    gatewayUnavailableTitle: 'Agent Cockpit is not connected to the gateway',
    gatewayUnavailableBody: 'This page requires the FastAPI gateway for /api/*. Start the gateway from the repository root, then open the app URL.',
    gatewayStartCommand: 'Start command',
    gatewayOpenUrl: 'Open URL',
    gatewayWrongStaticServer: 'Do not open web/app with python -m http.server or file://. Static serving is only for web/dashboard.',
    gatewayRetryHint: 'Refresh this page after the gateway starts.',
    repoRoot: 'Repository root',
    reload: 'Reload',
    revert: 'Revert',
    save: 'Save',
    contextDrawer: 'Context drawer',
    collapseDrawer: 'Collapse',
    expandDrawer: 'Expand',
    collapseNavigation: 'Collapse navigation',
    expandNavigation: 'Expand navigation',
    manuscriptDirty: 'Unsaved',
    manuscriptSaved: 'Saved',
    manuscriptSaving: 'Saving',
    manuscriptSaveFailed: 'Save failed',
    manuscriptNoFile: 'No file loaded',
    manuscriptDiscardConfirm: 'The current manuscript has unsaved changes. Discard them?',
    manuscriptSaveFirst: 'Save the manuscript before running an @manuscript session.',
    manuscriptContextLoadFailed: 'Failed to load @manuscript context',
    resolvedMentions: 'Resolved context',
    viewNodeStatus: 'Edit in Node view',
  }
};

function loadPinnedNodeIds() {
  try {
    const raw = JSON.parse(localStorage.getItem('research_app_pinned_nodes') || '[]');
    return new Set(Array.isArray(raw) ? raw.filter((item) => typeof item === 'string') : []);
  } catch (_) {
    return new Set();
  }
}

function loadExpandedNodeIds() {
  try {
    const raw = JSON.parse(localStorage.getItem('research_app_expanded_nodes') || '[]');
    return new Set(Array.isArray(raw) ? raw.filter((item) => typeof item === 'string') : []);
  } catch (_) {
    return new Set();
  }
}

function loadCurrentSessionId() {
  const raw = localStorage.getItem(CURRENT_SESSION_STORAGE_KEY);
  return raw && raw.trim() ? raw : null;
}

const initialWorkspaceTab = localStorage.getItem('research_app_workspace_tab') || 'overview';
const initialSessionType = localStorage.getItem('research_app_session_type') || 'node';

const state = {
  lang: localStorage.getItem('research_app_lang') || 'zh',
  workspaceTab: VALID_WORKSPACE_TABS.has(initialWorkspaceTab) ? initialWorkspaceTab : 'overview',
  sessionType: VALID_SESSION_TYPES.has(initialSessionType) ? initialSessionType : 'node',
  searchQuery: '',
  dependencyOverlayEnabled: localStorage.getItem('research_app_dependency_overlay') === '1',
  pinnedNodeIds: loadPinnedNodeIds(),
  hoveredNodeId: null,
  data: null,
  bootstrap: null,
  loadError: null,
  selectedNodeId: null,
  activeScopeId: null,
  treeFocusId: null,
  currentSessionId: loadCurrentSessionId(),
  sessions: [],
  pollHandle: null,
  graphClickTimer: null,
  expandedNodeIds: loadExpandedNodeIds(),
  navOpen: localStorage.getItem('research_app_nav_open') !== '0',
  drawerOpen: localStorage.getItem('research_app_drawer_open') === '1',
  manuscript: {
    nodeId: null,
    path: '',
    original: '',
    current: '',
    dirty: false,
    status: 'saved',
    error: '',
    lastSavedAt: null,
  },
};

const appRuntime = {
  renderAll: () => {},
  loadAll: async () => {},
};

function configureAppRuntime(hooks) {
  Object.assign(appRuntime, hooks);
}

function t(key) {
  return I18N[state.lang]?.[key] ?? I18N.zh[key] ?? key;
}

function html(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[char]);
}

function renderDomContractFailure(missing) {
  const shell = document.querySelector('.shell') || document.body;
  shell.innerHTML = `
    <div class="empty-state load-failure contract-failure">
      <h3>${t('frontendContractMismatch')}</h3>
      <p>Missing DOM ids: ${html(missing.join(', '))}</p>
      <p class="section-meta">Update web/app/index.html or web/app/app.js so the frontend contract is consistent.</p>
    </div>
  `;
}

function assertDomContract() {
  const required = [
    'language-toggle',
    'global-search-input',
    'refresh-button',
    'topbar-summary',
    'center-title',
    'sidebar-toggle-button',
    'more-actions-button',
    'tree-root',
    'collapse-all-button',
    'expand-active-path-button',
    'focus-card',
    'graph-canvas',
    'graph-empty',
    'graph-tooltip',
    'overview-view',
    'node-view',
    'manuscript-view',
    'session-view',
    'node-panel',
    'manuscript-path',
    'manuscript-status',
    'manuscript-editor',
    'manuscript-preview',
    'save-manuscript-button',
    'reload-manuscript-button',
    'revert-manuscript-button',
    'inspector-content',
    'agent-select',
    'target-node-input',
    'agent-prompt',
    'mention-suggestions',
    'session-type-select',
    'session-header',
    'session-context-content',
    'session-list',
    'session-log',
    'create-session-button',
    'run-session-button',
    'stop-session-button',
    'dependency-toggle-button',
    'pin-node-button',
    'open-session-button',
    'context-drawer',
    'drawer-toggle-button',
    'watch-content',
  ];
  const missing = required.filter((id) => !DOM.byId(id));
  if (missing.length) {
    renderDomContractFailure(missing);
    throw new Error(`Frontend DOM contract mismatch: missing ${missing.join(', ')}`);
  }
}

function fileHref(path) {
  if (!path) return '#';
  return `/${String(path).replace(/^\/+/, '').split('/').map(encodeURIComponent).join('/')}`;
}

function unique(items) {
  return [...new Set(items.filter(Boolean))];
}

function savePinnedNodes() {
  localStorage.setItem('research_app_pinned_nodes', JSON.stringify([...state.pinnedNodeIds]));
}

function saveExpandedNodes() {
  localStorage.setItem('research_app_expanded_nodes', JSON.stringify([...state.expandedNodeIds]));
}

function saveCurrentSessionId() {
  if (state.currentSessionId) localStorage.setItem(CURRENT_SESSION_STORAGE_KEY, state.currentSessionId);
  else localStorage.removeItem(CURRENT_SESSION_STORAGE_KEY);
}

function setCurrentSessionId(sessionId) {
  state.currentSessionId = sessionId || null;
  saveCurrentSessionId();
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { cache: 'no-store', ...options });
  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    data = null;
  }
  if (!response.ok) {
    const detail = data?.detail?.message || data?.detail || data?.message || `${url}: ${response.status}`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}

async function fetchOptionalJson(url, fallback) {
  try {
    return await fetchJson(url);
  } catch (err) {
    state.loadError = err.message;
    return fallback;
  }
}

function setHeartbeat(key, forcedState = '') {
  const heartbeat = document.getElementById('heartbeat');
  if (!heartbeat) return;
  heartbeat.textContent = t(key);
  heartbeat.dataset.state = forcedState || HEARTBEAT_STATES[key] || 'ready';
}

function gatewayRecoveryUrl() {
  if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
    return `${window.location.origin}/app/`;
  }
  return 'http://127.0.0.1:8765/app/';
}

function gatewayFailureHtml(error) {
  const message = error?.message || String(error || '');
  return `
    <div class="empty-state load-failure">
      <h3>${t('gatewayUnavailableTitle')}</h3>
      <p>${t('gatewayUnavailableBody')}</p>
      <div class="setup-steps">
        <div class="kv-label">${t('gatewayStartCommand')}</div>
        <code>bash scripts/dev_start_agent_app.sh</code>
        <div class="kv-label">${t('gatewayOpenUrl')}</div>
        <code>${html(gatewayRecoveryUrl())}</code>
      </div>
      <p class="section-meta">${t('gatewayWrongStaticServer')}</p>
      <p class="section-meta">${t('gatewayRetryHint')}</p>
      ${message ? `<p class="section-meta">${t('lastError')}: ${html(message)}</p>` : ''}
    </div>
  `;
}

function nodeDetails(nodeId) {
  return state.data?.details?.nodes?.[nodeId] || null;
}

function graphNode(nodeId) {
  return state.data?.graph?.nodes?.[nodeId] || null;
}

function displayNodeTitle(value) {
  const raw = String(value ?? '').trim();
  if (!raw) return '—';
  const segment = raw.split('::').filter(Boolean).slice(-1)[0] || raw;
  const withoutPrefix = segment.replace(/^P\d+_(?:\d+_)?/, '');
  return withoutPrefix.replace(/_/g, '') || segment.replace(/_/g, '') || raw;
}

function shortName(nodeId) {
  if (!nodeId) return '—';
  const detail = nodeDetails(nodeId);
  return displayNodeTitle(detail?.title || nodeId);
}

function flagToKey(flag) {
  return ({
    'fallback-only': 'fallbackOnly',
    'missing-local-entry': 'missingLocalEntry',
    'missing-node-skill': 'missingNodeSkill',
    'missing-sop': 'missingSop',
    'unexpected-node-skill': 'unexpectedNodeSkill',
    'unexpected-sop': 'unexpectedSop',
    'unexpected-local-execution': 'unexpectedLocalExecution',
    'missing-execution-binder': 'missingExecutionBinder',
    'thin-local-entry': 'thinLocalEntry',
    'zero-progress-active': 'zeroProgressActive',
    'review-not-started': 'reviewNotStarted',
    stale: 'stale'
  })[flag] || flag;
}

function statusBadge(status, extra = '') {
  if (!status) return '';
  return `<span class="badge ${html(extra)}">${html(status)}</span>`;
}

function statusClass(status) {
  return NODE_STAGES.includes(status) ? status : 'seed';
}

function boolText(value) {
  if (value === true) return t('yes');
  if (value === false) return t('no');
  return t('unknown');
}

function workspaceTitle() {
  return ({
    overview: t('overviewMode'),
    node: t('nodeMode'),
    manuscript: t('manuscriptMode'),
    session: t('sessionMode'),
  })[state.workspaceTab] || t('overviewMode');
}

function setWorkspaceTab(tab, { persist = true } = {}) {
  state.workspaceTab = VALID_WORKSPACE_TABS.has(tab) ? tab : 'overview';
  if (persist) localStorage.setItem('research_app_workspace_tab', state.workspaceTab);

  const views = {
    overview: DOM.overviewView(),
    node: DOM.nodeView(),
    manuscript: DOM.manuscriptView(),
    session: DOM.sessionView(),
  };
  Object.entries(views).forEach(([key, el]) => {
    el?.classList.toggle('active', key === state.workspaceTab);
    el?.classList.toggle('hidden', key !== state.workspaceTab);
    if (el) el.hidden = key !== state.workspaceTab;
  });

  document.querySelectorAll('.workspace-tab').forEach((el) => {
    const active = el.dataset.tab === state.workspaceTab;
    el.classList.toggle('active', active);
    el.setAttribute('aria-selected', active ? 'true' : 'false');
    el.tabIndex = active ? 0 : -1;
  });

  const title = DOM.centerTitle();
  if (title) title.textContent = workspaceTitle();
}

function setNavOpen(open, { persist = true } = {}) {
  state.navOpen = Boolean(open);
  if (persist) localStorage.setItem('research_app_nav_open', state.navOpen ? '1' : '0');
  document.querySelector('.workspace')?.classList.toggle('nav-collapsed', !state.navOpen);
  const button = document.getElementById('sidebar-toggle-button');
  if (button) button.textContent = state.navOpen ? t('collapseNavigation') : t('expandNavigation');
}

function setDrawerOpen(open, { persist = true } = {}) {
  state.drawerOpen = Boolean(open);
  if (persist) localStorage.setItem('research_app_drawer_open', state.drawerOpen ? '1' : '0');
  document.querySelector('.workspace')?.classList.toggle('drawer-collapsed', !state.drawerOpen);
  DOM.contextDrawer()?.classList.toggle('drawer-collapsed', !state.drawerOpen);
  const button = document.getElementById('drawer-toggle-button');
  if (button) {
    button.textContent = state.drawerOpen ? t('collapseDrawer') : t('expandDrawer');
    button.setAttribute('aria-expanded', state.drawerOpen ? 'true' : 'false');
  }
}

function matchesQuery(nodeId, extra = '') {
  const query = state.searchQuery.trim().toLowerCase();
  if (!query) return true;
  const detail = nodeDetails(nodeId) || {};
  const haystack = [
    nodeId,
    detail.title,
    displayNodeTitle(detail.title || nodeId),
    detail.path,
    detail.status,
    detail.lifecycle_stage,
    extra,
    displayNodeTitle(extra),
  ].filter(Boolean).join(' ').toLowerCase();
  return haystack.includes(query);
}

function topScopes() {
  return state.data?.hierarchy?.children || [];
}

function scopeMetrics(scopeId) {
  return state.data?.rollup?.scopes?.[scopeId] || {};
}

function findNodeInHierarchy(id, root = state.data?.hierarchy) {
  if (!root || !id) return null;
  if (root.id === id) return root;
  for (const child of root.children || []) {
    const found = findNodeInHierarchy(id, child);
    if (found) return found;
  }
  return null;
}

function parentScopeId(targetId, root = state.data?.hierarchy, parent = null) {
  if (!root || !targetId) return null;
  if (root.id === targetId) return parent?.id || null;
  for (const child of root.children || []) {
    const found = parentScopeId(targetId, child, root);
    if (found) return found;
  }
  return null;
}

function breadcrumbFor(id) {
  const path = [];
  if (!state.data?.hierarchy || !id) return path;
  function walk(node, parents = []) {
    if (node.id === id) {
      path.push(...parents, node);
      return true;
    }
    for (const child of node.children || []) {
      if (walk(child, [...parents, node])) return true;
    }
    return false;
  }
  walk(state.data.hierarchy);
  return path;
}

function isExpanded(nodeId) {
  return state.expandedNodeIds.has(nodeId);
}

function expandNode(nodeId) {
  state.expandedNodeIds.add(nodeId);
  saveExpandedNodes();
}

function collapseNode(nodeId) {
  state.expandedNodeIds.delete(nodeId);
  saveExpandedNodes();
}

function toggleExpanded(nodeId) {
  if (isExpanded(nodeId)) collapseNode(nodeId);
  else expandNode(nodeId);
}

function expandActivePath() {
  const chain = breadcrumbFor(state.selectedNodeId || state.activeScopeId);
  chain.forEach((node) => state.expandedNodeIds.add(node.id));
  saveExpandedNodes();
}

function collapseAll() {
  state.expandedNodeIds.clear();
  saveExpandedNodes();
}

function readListRows(items) {
  if (!items || !items.length) {
    return `<div class="section-meta">${t('noData')}</div>`;
  }
  return items.map((item) => `
    <div class="kv">
      <div class="kv-value">${html(item)}</div>
    </div>
  `).join('');
}

function foldSection(title, body) {
  return `
    <details class="fold-section">
      <summary>${html(title)}</summary>
      <div class="fold-body">${body}</div>
    </details>
  `;
}

export {
  API,
  VALID_WORKSPACE_TABS,
  VALID_SESSION_TYPES,
  CONTEXT_MENTIONS,
  NODE_STAGES,
  CURRENT_SESSION_STORAGE_KEY,
  HEARTBEAT_STATES,
  DOM,
  I18N,
  state,
  appRuntime,
  configureAppRuntime,
  t,
  html,
  assertDomContract,
  fileHref,
  unique,
  savePinnedNodes,
  saveExpandedNodes,
  saveCurrentSessionId,
  setCurrentSessionId,
  fetchJson,
  fetchOptionalJson,
  setHeartbeat,
  gatewayFailureHtml,
  nodeDetails,
  graphNode,
  shortName,
  displayNodeTitle,
  flagToKey,
  statusBadge,
  statusClass,
  boolText,
  workspaceTitle,
  setWorkspaceTab,
  setNavOpen,
  setDrawerOpen,
  matchesQuery,
  topScopes,
  scopeMetrics,
  findNodeInHierarchy,
  parentScopeId,
  breadcrumbFor,
  isExpanded,
  expandNode,
  collapseNode,
  toggleExpanded,
  expandActivePath,
  collapseAll,
  readListRows,
  foldSection,
};
