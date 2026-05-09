(function () {
  'use strict';

  // --- CodeMirror MiniMacro mode ---
  CodeMirror.defineSimpleMode('minimacro', {
    start: [
      { regex: /;.*/, token: 'comment' },
      { regex: /\b(MACRO|MEND|LCL|AIF|AGO|ANOP)\b/i, token: 'keyword' },
      { regex: /&[A-Za-z_][A-Za-z0-9_]*/, token: 'variable-2' },
      { regex: /\b\d+\b/, token: 'number' },
      { regex: /[A-Z][A-Z0-9_]{1,}/, token: 'atom' },
      { regex: /[=,]/, token: 'operator' }
    ]
  });

  // --- Editor setup ---
  const editor = CodeMirror.fromTextArea(document.getElementById('editor'), {
    mode: 'minimacro',
    lineNumbers: true,
    indentUnit: 2,
    tabSize: 2,
    lineWrapping: false,
    autofocus: true,
    extraKeys: {
      'Ctrl-Enter': () => process(),
      'Cmd-Enter':  () => process()
    }
  });

  const sourceMeta = document.getElementById('source-meta');
  function updateMeta() {
    const lines = editor.getValue().split('\n').length;
    sourceMeta.textContent = lines + (lines === 1 ? ' line' : ' lines');
  }
  editor.on('change', updateMeta);
  updateMeta();

  // --- Tab switching ---
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.panel');
  tabs.forEach((t) => {
    t.addEventListener('click', () => {
      tabs.forEach((x) => x.classList.remove('is-active'));
      panels.forEach((p) => p.classList.remove('is-active'));
      t.classList.add('is-active');
      const panel = document.querySelector(`.panel[data-panel="${t.dataset.tab}"]`);
      if (panel) panel.classList.add('is-active');
    });
  });

  // --- Status helpers ---
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  function setStatus(msg, kind) {
    statusText.textContent = msg;
    statusDot.classList.remove('is-busy', 'is-error');
    if (kind === 'busy')  statusDot.classList.add('is-busy');
    if (kind === 'error') statusDot.classList.add('is-error');
  }

  // --- Renderers ---
  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function renderMNT(rows) {
    const body = document.getElementById('mnt-body');
    body.innerHTML = rows.map((r, i) =>
      `<tr>
        <td>${i}</td>
        <td class="keyword">${escapeHTML(r.name)}</td>
        <td class="num">${r.num_pp}</td>
        <td class="num">${r.num_kp}</td>
        <td class="num">${r.mdt_ptr}</td>
        <td class="num">${r.kpdt_ptr}</td>
        <td class="num">${r.ala_ptr}</td>
       </tr>`
    ).join('');
    setEmpty('mnt', rows.length === 0);
  }

  function renderMDT(rows) {
    const body = document.getElementById('mdt-body');
    body.innerHTML = rows.map((r, i) =>
      `<tr>
        <td>${i}</td>
        <td>${highlightMDT(r.text)}</td>
       </tr>`
    ).join('');
    setEmpty('mdt', rows.length === 0);
  }

  function highlightMDT(text) {
    if (text.toUpperCase() === 'MEND') return `<span class="keyword">MEND</span>`;
    return escapeHTML(text).replace(/#(\d+)/g, '<span class="num">#$1</span>');
  }

  function renderKPDTAB(rows) {
    const body = document.getElementById('kpdtab-body');
    body.innerHTML = rows.map((r, i) =>
      `<tr>
        <td>${i}</td>
        <td class="formal">&amp;${escapeHTML(r.name)}</td>
        <td>${escapeHTML(r.default)}</td>
       </tr>`
    ).join('');
    setEmpty('kpdtab', rows.length === 0);
  }

  function renderALA(rows) {
    const body = document.getElementById('ala-body');
    body.innerHTML = rows.map((r, i) => {
      const actual = r.actual === '-'
        ? `<span class="dash">—</span>`
        : escapeHTML(r.actual);
      return `<tr>
        <td>${i}</td>
        <td class="formal">${escapeHTML(r.formal)}</td>
        <td>${actual}</td>
       </tr>`;
    }).join('');
    setEmpty('ala', rows.length === 0);
  }

  function renderLines(targetId, lines, panelKey) {
    const el = document.getElementById(targetId);
    el.innerHTML = lines.map((l) => `<span class="line">${escapeHTML(l) || ' '}</span>`).join('');
    setEmpty(panelKey, lines.length === 0);
  }

  function renderErrors(errors) {
    const body = document.getElementById('errors-body');
    body.innerHTML = errors.map((e) => `<li>${escapeHTML(e)}</li>`).join('');
    setEmpty('errors', errors.length === 0);

    const badge = document.getElementById('errors-badge');
    badge.textContent = errors.length;
    badge.classList.toggle('is-error', errors.length > 0);
  }

  function setEmpty(panelKey, isEmpty) {
    const panel = document.querySelector(`.panel[data-panel="${panelKey}"]`);
    if (panel) panel.classList.toggle('is-empty', isEmpty);
  }

  function renderAll(result) {
    renderMNT(result.mnt || []);
    renderMDT(result.mdt || []);
    renderKPDTAB(result.kpdtab || []);
    renderALA(result.ala || []);
    renderLines('intermediate-body', result.intermediate || [], 'intermediate');
    renderLines('expanded-body',     result.expanded     || [], 'expanded');
    renderErrors(result.errors || []);
  }

  // --- Process ---
  const processBtn = document.getElementById('process-btn');
  async function process() {
    const source = editor.getValue();
    if (!source.trim()) {
      setStatus('Editor is empty', 'error');
      return;
    }
    processBtn.disabled = true;
    setStatus('Processing…', 'busy');
    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source })
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      renderAll(data);
      const errCount = (data.errors || []).length;
      setStatus(
        errCount === 0
          ? `OK · ${(data.mnt || []).length} macros · ${(data.expanded || []).length} expanded lines`
          : `Completed with ${errCount} error${errCount === 1 ? '' : 's'}`,
        errCount === 0 ? null : 'error'
      );
    } catch (err) {
      setStatus('Error: ' + err.message, 'error');
    } finally {
      processBtn.disabled = false;
    }
  }
  processBtn.addEventListener('click', process);

  // --- Sample loaders ---
  document.querySelectorAll('[data-sample]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const name = btn.dataset.sample;
      setStatus('Loading sample…', 'busy');
      try {
        const res = await fetch('/api/sample/' + name);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        editor.setValue(data.source || '');
        setStatus('Sample loaded · click Process or hit Ctrl/Cmd+Enter');
      } catch (err) {
        setStatus('Failed to load sample: ' + err.message, 'error');
      }
    });
  });

  document.getElementById('clear-btn').addEventListener('click', () => {
    editor.setValue('');
    renderAll({ mnt: [], mdt: [], kpdtab: [], ala: [], intermediate: [], expanded: [], errors: [] });
    setStatus('Cleared');
  });

  // --- Initial state ---
  renderAll({ mnt: [], mdt: [], kpdtab: [], ala: [], intermediate: [], expanded: [], errors: [] });
})();
