import { fetchJson, html, state, t } from './ui_core.js';

function manuscriptHasDirtyChanges() {
  return Boolean(state.manuscript.nodeId && state.manuscript.dirty);
}

function confirmDiscardManuscriptChanges() {
  return !manuscriptHasDirtyChanges() || window.confirm(t('manuscriptDiscardConfirm'));
}

async function loadManuscript(nodeId = state.selectedNodeId) {
  if (!nodeId) return;
  const payload = await fetchJson(`/api/node/${encodeURIComponent(nodeId)}/manuscript`);
  state.manuscript = {
    nodeId,
    path: payload.path,
    original: payload.content || '',
    current: payload.content || '',
    dirty: false,
    status: 'saved',
    error: '',
    lastSavedAt: payload.updated_at || null,
  };
  renderManuscript();
}

async function saveManuscript() {
  if (!state.manuscript.nodeId) return;
  if (!state.manuscript.dirty && state.manuscript.status !== 'error') return;
  state.manuscript.status = 'saving';
  state.manuscript.error = '';
  renderManuscript();
  try {
    const payload = await fetchJson(`/api/node/${encodeURIComponent(state.manuscript.nodeId)}/manuscript`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ content: state.manuscript.current })
    });
    state.manuscript.original = payload.content || state.manuscript.current;
    state.manuscript.current = payload.content || state.manuscript.current;
    state.manuscript.dirty = false;
    state.manuscript.status = 'saved';
    state.manuscript.error = '';
    state.manuscript.lastSavedAt = payload.updated_at || null;
    renderManuscript();
  } catch (err) {
    state.manuscript.status = 'error';
    state.manuscript.error = err.message || String(err);
    renderManuscript();
    throw err;
  }
}

function revertManuscript() {
  if (!confirmDiscardManuscriptChanges()) return;
  state.manuscript.current = state.manuscript.original;
  state.manuscript.dirty = false;
  state.manuscript.status = 'saved';
  state.manuscript.error = '';
  renderManuscript();
}

function safeLinkHref(value) {
  const href = String(value || '').trim();
  return /^(https?:\/\/|\/|#)/.test(href) ? href : '#';
}

function inlineMarkdown(value) {
  return html(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/~~([^~]+)~~/g, '<del>$1</del>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => (
      `<a href="${html(safeLinkHref(href))}" target="_blank" rel="noreferrer">${label}</a>`
    ));
}

function parseTableCells(line) {
  const trimmed = String(line || '').trim();
  if (!trimmed.includes('|')) return null;
  const normalized = trimmed.replace(/^\|/, '').replace(/\|$/, '');
  const cells = normalized.split('|').map((cell) => cell.trim());
  return cells.length >= 2 ? cells : null;
}

function isTableSeparator(line, expectedLength) {
  const cells = parseTableCells(line);
  return Boolean(cells && cells.length === expectedLength && cells.every((cell) => /^:?-{3,}:?$/.test(cell)));
}

function renderMarkdownPreview(source) {
  const lines = String(source || '').split('\n');
  const out = [];
  let paragraph = [];
  let listType = '';
  let listItems = [];
  let quoteLines = [];
  let inCode = false;
  let codeLines = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    out.push(`<p>${paragraph.map(inlineMarkdown).join('<br/>')}</p>`);
    paragraph = [];
  }

  function flushList() {
    if (!listType) return;
    out.push(`<${listType}>${listItems.map((item) => `<li>${inlineMarkdown(item)}</li>`).join('')}</${listType}>`);
    listType = '';
    listItems = [];
  }

  function flushQuote() {
    if (!quoteLines.length) return;
    out.push(`<blockquote>${quoteLines.map(inlineMarkdown).join('<br/>')}</blockquote>`);
    quoteLines = [];
  }

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line.trim().startsWith('```')) {
      flushParagraph();
      flushList();
      flushQuote();
      if (inCode) {
        out.push(`<pre><code>${html(codeLines.join('\n'))}</code></pre>`);
        codeLines = [];
      }
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    const unordered = line.match(/^\s*[-*]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+\.\s+(.+)$/);
    const quote = line.match(/^\s*>\s?(.*)$/);
    const thematicBreak = line.match(/^\s{0,3}([-*_])(?:\s*\1){2,}\s*$/);
    const tableHeader = parseTableCells(line);

    if (!line.trim()) {
      flushParagraph();
      flushList();
      flushQuote();
    } else if (thematicBreak) {
      flushParagraph();
      flushList();
      flushQuote();
      out.push('<hr/>');
    } else if (heading) {
      flushParagraph();
      flushList();
      flushQuote();
      out.push(`<h${heading[1].length}>${inlineMarkdown(heading[2])}</h${heading[1].length}>`);
    } else if (tableHeader && isTableSeparator(lines[index + 1], tableHeader.length)) {
      flushParagraph();
      flushList();
      flushQuote();
      const bodyRows = [];
      index += 2;
      while (index < lines.length) {
        const cells = parseTableCells(lines[index]);
        if (!cells || cells.length !== tableHeader.length) break;
        bodyRows.push(cells);
        index += 1;
      }
      index -= 1;
      out.push(`
        <table class="manuscript-table">
          <thead><tr>${tableHeader.map((cell) => `<th>${inlineMarkdown(cell)}</th>`).join('')}</tr></thead>
          <tbody>${bodyRows.map((cells) => `<tr>${cells.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join('')}</tr>`).join('')}</tbody>
        </table>
      `);
    } else if (quote) {
      flushParagraph();
      flushList();
      quoteLines.push(quote[1]);
    } else if (unordered || ordered) {
      flushParagraph();
      flushQuote();
      const nextType = unordered ? 'ul' : 'ol';
      if (listType && listType !== nextType) flushList();
      listType = nextType;
      listItems.push((unordered || ordered)[1]);
    } else {
      flushList();
      flushQuote();
      paragraph.push(line);
    }
  }

  flushParagraph();
  flushList();
  flushQuote();
  if (inCode) out.push(`<pre><code>${html(codeLines.join('\n'))}</code></pre>`);
  return out.join('\n') || `<p class="section-meta">${t('manuscriptNoFile')}</p>`;
}

function renderManuscript() {
  const pathEl = document.getElementById('manuscript-path');
  const statusEl = document.getElementById('manuscript-status');
  const editor = document.getElementById('manuscript-editor');
  const preview = document.getElementById('manuscript-preview');
  const saveButton = document.getElementById('save-manuscript-button');
  const reloadButton = document.getElementById('reload-manuscript-button');
  const revertButton = document.getElementById('revert-manuscript-button');
  if (!pathEl || !statusEl || !editor || !preview) return;

  pathEl.textContent = state.manuscript.path || 'docs/manuscript.md';
  const statusLabel = {
    dirty: t('manuscriptDirty'),
    saving: t('manuscriptSaving'),
    error: t('manuscriptSaveFailed'),
    saved: t('manuscriptSaved'),
  }[state.manuscript.status || (state.manuscript.dirty ? 'dirty' : 'saved')];
  statusEl.textContent = state.manuscript.nodeId
    ? `${statusLabel}${state.manuscript.error ? ': ' + state.manuscript.error : ''}${state.manuscript.lastSavedAt ? ' · ' + state.manuscript.lastSavedAt : ''}`
    : t('manuscriptNoFile');

  if (editor.value !== state.manuscript.current) editor.value = state.manuscript.current || '';
  editor.disabled = state.manuscript.status === 'saving';
  if (saveButton) saveButton.disabled = !state.manuscript.nodeId || state.manuscript.status === 'saving' || (!state.manuscript.dirty && state.manuscript.status !== 'error');
  if (reloadButton) reloadButton.disabled = state.manuscript.status === 'saving';
  if (revertButton) revertButton.disabled = state.manuscript.status === 'saving' || !state.manuscript.dirty;
  preview.innerHTML = renderMarkdownPreview(state.manuscript.current);
}

export {
  manuscriptHasDirtyChanges,
  confirmDiscardManuscriptChanges,
  loadManuscript,
  saveManuscript,
  revertManuscript,
  renderMarkdownPreview,
  renderManuscript,
};
