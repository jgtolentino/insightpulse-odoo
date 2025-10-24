{
  "name": "Knowledge Notion Clone",
  "summary": "Notion-like pages & databases built with OWL",
  "version": "1.0.0",
  "category": "Productivity",
  "depends": ["base","web"],
  "data": [
    "security/security.xml",
    "security/ir.model.access.csv",
    "views/menu.xml",
    "views/actions.xml",
    "static/src/xml/app.xml"
  ],
  "assets": {
    "web.assets_backend": [
      "knowledge_notion_clone/static/src/js/app.js",
      "knowledge_notion_clone/static/src/xml/app.xml"
    ]
  },
  "license": "LGPL-3"
}
