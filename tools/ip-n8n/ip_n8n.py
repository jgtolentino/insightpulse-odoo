#!/usr/bin/env python3
"""
InsightPulse n8n CLI
Manage n8n workflows from command line
"""
import os, json, sys, argparse, pathlib, time
import requests

CFG_PATH = pathlib.Path(os.getenv("IP_N8N_CONFIG", "~/.config/ip-n8n/config.json")).expanduser()

def load_cfg():
    if CFG_PATH.exists():
        return json.loads(CFG_PATH.read_text())
    return {"base_url": "http://127.0.0.1:5678", "api_key": ""}

def save_cfg(cfg):
    CFG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CFG_PATH.write_text(json.dumps(cfg, indent=2))

def auth_headers(cfg):
    return {"X-N8N-API-KEY": cfg["api_key"]} if cfg.get("api_key") else {}

def api(cfg, method, path, **kw):
    url = cfg["base_url"].rstrip("/") + "/api/v1" + path
    r = requests.request(method, url, headers=auth_headers(cfg) | {"Content-Type": "application/json"}, **kw)
    if r.status_code >= 400:
        raise SystemExit(f"[n8n] {r.status_code} {r.text}")
    return r.json() if r.text else {}

def cmd_login(args):
    cfg = load_cfg()
    if args.base:
        cfg["base_url"] = args.base
    if args.key:
        cfg["api_key"] = args.key
    save_cfg(cfg)

    # smoke test
    try:
        ver = requests.get(cfg["base_url"].rstrip("/") + "/rest/version").json()
        print("✅ Connected to n8n", ver)
    except Exception as e:
        print("⚠️  Saved config, but health check failed:", e)

def cmd_list(args):
    cfg = load_cfg()
    data = api(cfg, "GET", "/workflows")
    for w in data.get("data", []):
        s = "on" if w.get("active") else "off"
        print(f"{w['id']:>4}  {s:3}  {w['name']}")

def cmd_get(args):
    cfg = load_cfg()
    w = api(cfg, "GET", f"/workflows/{args.id}")
    print(json.dumps(w, indent=2))

def cmd_run(args):
    cfg = load_cfg()
    payload = {"workflowId": args.id, "runData": {}, "startNodes": [], "pinData": {}}
    r = api(cfg, "POST", "/workflows/run", json=payload)
    print(json.dumps(r, indent=2))

def cmd_toggle(args, active: bool):
    cfg = load_cfg()
    w = api(cfg, "PATCH", f"/workflows/{args.id}", json={"active": active})
    print(("✅ Activated" if active else "✅ Deactivated"), w.get("name"))

def cmd_activate(args):
    cmd_toggle(args, True)

def cmd_deactivate(args):
    cmd_toggle(args, False)

def cmd_import(args):
    cfg = load_cfg()
    wf = json.loads(pathlib.Path(args.file).read_text())
    r = api(cfg, "POST", "/workflows", json=wf)
    print("✅ Imported:", r.get("name"), r.get("id"))

def cmd_export(args):
    cfg = load_cfg()
    w = api(cfg, "GET", f"/workflows/{args.id}")
    out = args.out or f"workflow-{args.id}.json"
    pathlib.Path(out).write_text(json.dumps(w, indent=2))
    print("💾 Saved to", out)

def cmd_exec_webhook(args):
    # convenience: call a webhook-triggered workflow
    url = args.url
    if args.data:
        try:
            body = json.loads(args.data)
        except:
            body = {"text": args.data}
    else:
        body = {}

    r = requests.post(url, json=body)
    print(r.status_code, r.text[:800])

def main():
    p = argparse.ArgumentParser(prog="ip-n8n", description="InsightPulse n8n CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("login")
    s.add_argument("--base")
    s.add_argument("--key")
    s.set_defaults(func=cmd_login)

    s = sub.add_parser("list")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("get")
    s.add_argument("id")
    s.set_defaults(func=cmd_get)

    s = sub.add_parser("run")
    s.add_argument("id")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("activate")
    s.add_argument("id")
    s.set_defaults(func=cmd_activate)

    s = sub.add_parser("deactivate")
    s.add_argument("id")
    s.set_defaults(func=cmd_deactivate)

    s = sub.add_parser("import")
    s.add_argument("file")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("export")
    s.add_argument("id")
    s.add_argument("--out")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("exec-webhook")
    s.add_argument("url")
    s.add_argument("--data")
    s.set_defaults(func=cmd_exec_webhook)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
