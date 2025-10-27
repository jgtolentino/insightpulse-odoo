# OCA Vendoring Pattern

## repos.yaml Format

```yaml
server-tools:
  url: https://github.com/OCA/server-tools
  branch: "19.0"
  commit: abc123def456
  modules: [base_technical_user, sentry]
```

## Commands

```bash
# Clone with sparse checkout
git clone --filter=blob:none --sparse https://github.com/OCA/server-tools
cd server-tools
git sparse-checkout set module1 module2
```
