# InsightPulseAI Chat Widget

A purple-themed, vanilla JavaScript chat widget for InsightPulseAI public-facing pages.

## Features

- **Zero dependencies**: Pure vanilla JavaScript, no external libraries required
- **Purple theme**: Matches InsightPulseAI brand colors (#6B4E71)
- **Rule-based responses**: Smart pattern matching for common queries
- **Optional AI integration**: Ready to connect to AI endpoints
- **Responsive design**: Works on desktop and mobile devices
- **Accessible**: ARIA labels and keyboard navigation support

## Installation

1. Install the module:
   ```bash
   # From Odoo interface
   Apps -> Update Apps List -> Search "InsightPulseAI Chat Widget" -> Install
   ```

2. The widget will automatically appear on all pages that use the `web.layout` template.

## Widget Behavior

### Welcome Messages
When a user opens the chat for the first time, they see:
- "Welcome to InsightPulseAI! 👋"
- "What are you looking for?"

### Built-in Responses

1. **Documentation queries**: Matches keywords like "documentation", "docs", "manual", "guide"
   - Response: Links to product docs and API docs

2. **Support queries**: Matches keywords like "support", "help", "contact"
   - Response: Contact email (business@insightpulseai.com)

3. **Fallback**: For unmatched queries
   - Response: "I'm here to help! Try asking for documentation, support, or integrations."

## LLM Integration

The module integrates with your existing **microservices LLM service** infrastructure:

### How It Works

1. **User sends message** → Chat widget calls `/api/chat`
2. **Widget checks rules** → If pattern matches (docs, support), responds immediately
3. **Falls back to LLM** → If no rule matches, calls LLM service
4. **LLM responds** → Returns intelligent, contextual answer

### Configuration Required

1. **Install microservices_connector module** (dependency)
2. **Configure LLM service**:
   - Go to: Settings → Microservices Configuration
   - Set `LLM Service URL` (default: `http://llm-service:8001`)
   - Set `Auth Token` (encrypted storage)
   - Mark configuration as Active

### API Endpoint Details

**Route**: `POST /api/chat`

**Request Format**:
```json
{
  "message": "user question here",
  "source": "welcome-widget"
}
```

**Response Format**:
```json
{
  "reply": "LLM-generated response or null"
}
```

**LLM Service Call**:
The chat controller calls `{llm_service_url}/chat` with:
```json
{
  "message": "user question",
  "source": "welcome-widget",
  "context": {
    "product": "InsightPulseAI",
    "channel": "website-chat-widget"
  }
}
```

### Behavior

- **LLM available** → Returns intelligent AI-powered responses
- **LLM unavailable** → Falls back to rule-based responses
- **Error handling** → Logs errors, returns null (widget shows fallback message)

## Customization

### Change Colors
Edit `views/chat_widget_templates.xml` and modify the CSS variables:
```css
:root {
  --ipai-purple: #6B4E71;  /* Main purple color */
  --ipai-bg: #f6f8fa;      /* Background color */
}
```

### Add New Rules
Edit the `RULES` array in the JavaScript section:
```javascript
const RULES = [
  {
    test: /your-pattern/i,
    reply: () => `Your response here`
  },
  // ... more rules
];
```

### Auto-Open on Page Load
Uncomment the last line in the JavaScript:
```javascript
// openChat();  // Remove the // to enable
```

## Technical Details

- **Module Path**: `/addons/custom/chat_widget/`
- **Template ID**: `chat_widget.chat_widget_inject`
- **Inherits**: `web.layout`
- **Position**: Injected at end of `<body>` tag
- **z-index**: 9998 (launcher), 9999 (chat window)

## Dependencies

- `base`
- `web`

## License

LGPL-3

## Author

InsightPulseAI - https://insightpulseai.net
