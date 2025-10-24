odoo.define('rag_panel.panel', function (require) {
  'use strict';
  const { jsonRpc } = require('web.ajax');
  function mount(){
    const el = document.getElementById('rag-panel'); if(!el) return;
    el.innerHTML = `
      <textarea id="rag-q" rows="4" style="width:100%;" placeholder="Ask..."></textarea>
      <button id="rag-send" class="btn btn-primary" style="margin-top:8px;">Ask</button>
      <div id="rag-ans" style="margin-top:12px;white-space:pre-wrap;"></div>
      <div id="rag-cites" style="margin-top:8px;font-size:12px;"></div>`;
    document.getElementById('rag-send').onclick = async () => {
      const q = document.getElementById('rag-q').value.trim(); if(!q) return;
      const ans = document.getElementById('rag-ans'); ans.textContent='Thinking...';
      try {
        const res = await jsonRpc('/rag/ask','call',{question:q,top_k:5});
        ans.textContent = res.answer || '(no answer)';
        document.getElementById('rag-cites').innerHTML =
          (res.citations||[]).map(c=>`<div>• <b>${c.title||c.id}</b> [${c.source}] (${c.score.toFixed(3)})</div>`).join('');
      } catch { ans.textContent='Error querying RAG API.'; }
    };
  }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', mount); else mount();
});
