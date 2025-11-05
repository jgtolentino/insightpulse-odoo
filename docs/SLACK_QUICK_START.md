# 🚀 Slack Enterprise → Odoo: 5-Minute Quick Start

## Prerequisites

- Odoo 19 CE running
- PostgreSQL with pgvector
- Access to Slack workspace (admin)

## Step 1: Install Core Module (2 minutes)

```bash
cd /home/user/insightpulse-odoo

# Install ipai_chat_core (foundation)
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf -d odoo19 \
  -i ipai_chat_core --stop-after-init
```

## Step 2: Test Chat (1 minute)

1. Login to Odoo
2. Go to Discuss app
3. Create a channel: "Finance SSC General"
4. Try features:
   - Send message
   - Add reaction (👍)
   - Reply in thread
   - Pin message

## Step 3: Install Slack Bridge (2 minutes)

```bash
# Install Slack integration
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf -d odoo19 \
  -i ipai_slack_bridge --stop-after-init
```

## Step 4: Connect Slack App

1. Create Slack App: https://api.slack.com/apps
2. Add OAuth redirect: `https://erp.insightpulseai.net/slack/oauth/callback`
3. Add events URL: `https://erp.insightpulseai.net/slack/events`
4. Install app to workspace
5. Copy bot token to Odoo

## Done! 🎉

You now have:
- ✅ Enterprise chat in Odoo
- ✅ Slack integration
- ✅ Message sync
- ✅ Threaded conversations
- ✅ Reactions
- ✅ File sharing

## Next Steps

- Install remaining modules (SCIM, Audit, DLP, etc.)
- Configure policies
- Set up analytics
- Train users
- Migrate Slack data

**Full Guide:** [SLACK_ENTERPRISE_MIGRATION.md](./SLACK_ENTERPRISE_MIGRATION.md)
