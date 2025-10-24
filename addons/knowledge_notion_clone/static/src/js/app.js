/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";

class App extends Component {
  setup() {
    this.state = useState({ pages: [], page: {}, blocks: [] });
    onWillStart(async () => { await this.searchPages(); });
  }
  async searchPages(q=null){ const r = await jsonrpc("/knowledge/api/pages", {search:q}); this.state.pages = r.pages; if(r.pages[0]){ await this.loadPage(r.pages[0].id); } }
  async loadPage(id){ const r = await jsonrpc(`/knowledge/api/page/${id}`, {}); this.state.page = r.page; this.state.blocks = r.blocks; }
  onSearch(ev){ this.searchPages(ev.target.value); }
  async addBlock(type){ const vals = { page_id:this.state.page.id, type, text:type.toUpperCase() }; const r = await jsonrpc("/knowledge/api/block/save",{vals}); this.state.blocks.push({id:r.id, sequence:999, type, text:vals.text}); }
  async toggleTodo(b, ev){ await jsonrpc("/knowledge/api/block/save",{id:b.id, vals:{checked:ev.target.checked}}); b.checked = ev.target.checked; }
  async newPage(){ /* TODO: implement create page via RPC */ }
}
App.template = "knowledge_notion_clone.App";
registry.category("actions").add("knowledge_notion_clone.app", App);
