#!/usr/bin/env python3
"""
Minimal Trusted Agent stub for Odoo projects
- Executes all risky actions via a sandbox abstraction (E2B-ready)
- Uses an MCP Gateway placeholder to access curated tools
- Demonstrates a safe GitHub "create PR" flow with a new branch and commit

Environment variables (with CLI fallbacks):
  GITHUB_TOKEN       Personal Access Token (repo scope) or GitHub App token
  GITHUB_REPO        "owner/repo"
  GITHUB_BASE        Base branch (e.g., "main")
  GITHUB_HEAD        New branch name (optional; generated if missing)
  MCP_SERVER_URL     http://mcp-gateway:8080    (placeholder)
  MODEL_RUNNER_URL   http://model-runner:8080   (placeholder)
  E2B_API_KEY        API key for E2B sandbox    (optional in local mode)
  E2B_API_URL        https://api.e2b.dev        (example placeholder)

Usage examples:
  python -m ai.agent.main create-pr \
    --repo owner/repo \
    --base main \
    --branch feat/agent-demo \
    --file README.md \
    --content "\n\n### Added by agent stub" \
    --message "docs: demo change by agent stub" \
    --title "chore(docs): demo PR via agent stub" \
    --body "This PR was created by the trusted agent stub in a sandboxed lane."

Notes:
- E2B/MCP integrations are abstracted; replace TODO sections with real SDK calls when wiring up.
- This stub intentionally avoids direct shell access and only talks to GitHub's REST API over HTTPS.
"""
from __future__ import annotations

import argparse
import base64
import dataclasses
import json
import os
import sys
import time
import typing as t
from dataclasses import dataclass

import requests

GITHUB_API = "https://api.github.com"


# ----------------------------- Utilities ------------------------------------

def _b64(s: t.Union[str, bytes]) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode("ascii")


def _now_ms() -> int:
    return int(time.time() * 1000)


# ----------------------------- Logging --------------------------------------

@dataclass
class Logger:
    correlation_id: str

    def _log(self, level: str, msg: str, **fields: t.Any) -> None:
        payload = {
            "ts": _now_ms(),
            "level": level,
            "cid": self.correlation_id,
            "msg": msg,
        }
        payload.update(fields)
        print(json.dumps(payload), flush=True)

    def info(self, msg: str, **fields: t.Any) -> None:
        self._log("INFO", msg, **fields)

    def warn(self, msg: str, **fields: t.Any) -> None:
        self._log("WARN", msg, **fields)

    def error(self, msg: str, **fields: t.Any) -> None:
        self._log("ERROR", msg, **fields)


# ----------------------------- Sandbox (E2B) --------------------------------

@dataclass
class SandboxConfig:
    api_key: t.Optional[str] = os.getenv("E2B_API_KEY")
    api_url: str = os.getenv("E2B_API_URL", "https://api.e2b.dev")
    local_mode: bool = dataclasses.field(default=False)


class Sandbox:
    """E2B-ready sandbox abstraction.

    In local mode, it simply annotates actions. In cloud mode, replace TODOs with
    real E2B SDK/API calls to create a sandbox run and execute the action.
    """

    def __init__(self, cfg: SandboxConfig, logger: Logger):
        self.cfg = cfg
        self.logger = logger
        self.run_id: t.Optional[str] = None

    def __enter__(self) -> "Sandbox":
        if not self.cfg.api_key:
            self.logger.warn(
                "E2B_API_KEY not set; running in LOCAL_MODE (no remote exec).",
                mode="local",
            )
            self.cfg.local_mode = True
            self.run_id = f"local-{_now_ms()}"
            return self
        # TODO: Create sandbox via E2B API and store run_id
        self.run_id = f"e2b_{_now_ms()}"  # placeholder
        self.logger.info("sandbox.created", run_id=self.run_id)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.cfg.local_mode:
            self.logger.info("sandbox.closed", run_id=self.run_id, mode="local")
            return
        # TODO: Tear down sandbox via E2B API
        self.logger.info("sandbox.closed", run_id=self.run_id)

    # Example wrapper around a safe HTTPS call executed 'within' the sandbox
    def https_call(self, fn: t.Callable[[], requests.Response]) -> requests.Response:
        self.logger.info("sandbox.https_call", run_id=self.run_id)
        # In a real integration, proxy this through the sandbox network policy
        return fn()


# ----------------------------- MCP Gateway ----------------------------------

@dataclass
class MCPConfig:
    server_url: str = os.getenv("MCP_SERVER_URL", "http://mcp-gateway:8080")


class MCPClient:
    """Placeholder MCP client that would route tool invocations through the
    Docker MCP Gateway. Replace 'invoke' with the actual protocol when wiring up.
    """

    def __init__(self, cfg: MCPConfig, logger: Logger):
        self.cfg = cfg
        self.logger = logger

    def invoke(self, tool: str, **kwargs) -> dict:
        # TODO: Implement the real call. For now, log + echo.
        self.logger.info("mcp.invoke", tool=tool, kwargs=kwargs)
        return {"tool": tool, "ok": True, "kwargs": kwargs}


# ----------------------------- GitHub API -----------------------------------

@dataclass
class GitHubConfig:
    token: str = os.getenv("GITHUB_TOKEN", "")
    repo: str = os.getenv("GITHUB_REPO", "")  # owner/repo
    base: str = os.getenv("GITHUB_BASE", "main")


class GitHubClient:
    def __init__(self, cfg: GitHubConfig, sandbox: Sandbox, logger: Logger):
        if not cfg.token:
            raise RuntimeError("GITHUB_TOKEN is required")
        if not cfg.repo or "/" not in cfg.repo:
            raise RuntimeError("GITHUB_REPO must be 'owner/repo'")
        self.cfg = cfg
        self.sandbox = sandbox
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.cfg.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # --- low-level helpers
    def _req(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{GITHUB_API}{path}"
        self.logger.info("github.request", method=method, url=url)

        def do_call():
            return self.session.request(method, url, timeout=30, **kwargs)

        resp = self.sandbox.https_call(do_call)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = {"text": resp.text[:200]}
            self.logger.error("github.error", status=resp.status_code, detail=detail)
            raise RuntimeError(f"GitHub API error {resp.status_code}: {detail}")
        return resp

    def _get(self, path: str, **kwargs) -> dict:
        return self._req("GET", path, **kwargs).json()

    def _post(self, path: str, json: dict) -> dict:
        return self._req("POST", path, json=json).json()

    def _put(self, path: str, json: dict) -> dict:
        return self._req("PUT", path, json=json).json()

    # --- high-level flows
    def get_default_branch(self) -> str:
        owner, repo = self.cfg.repo.split("/", 1)
        data = self._get(f"/repos/{owner}/{repo}")
        return data.get("default_branch", "main")

    def get_branch_sha(self, branch: str) -> str:
        owner, repo = self.cfg.repo.split("/", 1)
        ref = self._get(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
        return ref["object"]["sha"]

    def create_branch(self, new_branch: str, from_branch: t.Optional[str] = None) -> str:
        owner, repo = self.cfg.repo.split("/", 1)
        if not from_branch:
            from_branch = self.cfg.base or self.get_default_branch()
        sha = self.get_branch_sha(from_branch)
        self._post(
            f"/repos/{owner}/{repo}/git/refs",
            json={"ref": f"refs/heads/{new_branch}", "sha": sha},
        )
        self.logger.info("github.branch.created", branch=new_branch, from_branch=from_branch)
        return new_branch

    def put_file(self, path: str, content: str, message: str, branch: str) -> str:
        owner, repo = self.cfg.repo.split("/", 1)
        data = self._put(
            f"/repos/{owner}/{repo}/contents/{path}",
            json={"message": message, "content": _b64(content), "branch": branch},
        )
        sha = data.get("content", {}).get("sha", "")
        self.logger.info("github.file.put", path=path, branch=branch, sha=sha)
        return sha

    def create_pr(self, title: str, body: str, head: str, base: t.Optional[str] = None) -> int:
        owner, repo = self.cfg.repo.split("/", 1)
        if not base:
            base = self.cfg.base or self.get_default_branch()
        pr = self._post(
            f"/repos/{owner}/{repo}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
        )
        number = pr.get("number")
        self.logger.info("github.pr.created", number=number, head=head, base=base)
        return int(number)


# ----------------------------- Agent Logic ----------------------------------

class TrustedAgent:
    def __init__(self, logger: Logger, sandbox: Sandbox, gh: GitHubClient, mcp: MCPClient):
        self.logger = logger
        self.sandbox = sandbox
        self.gh = gh
        self.mcp = mcp

    def create_demo_pr(
        self,
        file_path: str,
        content_append: str,
        commit_message: str,
        pr_title: str,
        pr_body: str,
        base_branch: str,
        new_branch: t.Optional[str] = None,
    ) -> int:
        """Create a PR by adding/appending content to a file on a new branch.
        - Generates a unique branch name if not provided.
        - Uses sandboxed HTTPS calls for GitHub interactions.
        """
        if not new_branch:
            new_branch = f"agent/{int(time.time())}"
        # Example use of MCP tool (placeholder)
        self.mcp.invoke("plan.change", target_file=file_path, rationale="append demo block")

        # Branch
        self.gh.create_branch(new_branch, from_branch=base_branch)

        # File update (naive append: if file exists we could GET and append; for simplicity we create or overwrite)
        # To append safely, consider fetching existing file sha + content first.
        self.gh.put_file(path=file_path, content=content_append, message=commit_message, branch=new_branch)

        # PR
        pr_number = self.gh.create_pr(title=pr_title, body=pr_body, head=new_branch, base=base_branch)
        self.logger.info("agent.demo_pr.complete", pr=pr_number, branch=new_branch)
        return pr_number


# ----------------------------- CLI ------------------------------------------

def parse_args(argv: t.List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="agent", description="Trusted Agent stub")
    sub = p.add_subparsers(dest="cmd", required=True)

    cpr = sub.add_parser("create-pr", help="Create a demo PR with a file change")
    cpr.add_argument("--repo", default=os.getenv("GITHUB_REPO", ""))
    cpr.add_argument("--base", default=os.getenv("GITHUB_BASE", "main"))
    cpr.add_argument("--branch", dest="head", default=os.getenv("GITHUB_HEAD", ""))
    cpr.add_argument("--file", required=True, help="Path to modify/create")
    cpr.add_argument("--content", required=True, help="Content to write (demo appends)")
    cpr.add_argument("--message", required=True, help="Commit message")
    cpr.add_argument("--title", required=True, help="PR title")
    cpr.add_argument("--body", required=True, help="PR body")

    return p.parse_args(argv)


def main(argv: t.List[str]) -> int:
    args = parse_args(argv)

    # Correlation ID: epoch-based for simplicity
    cid = f"cid-{_now_ms()}"
    logger = Logger(correlation_id=cid)

    # Sandbox + clients
    sbox = Sandbox(SandboxConfig(), logger)
    mcp = MCPClient(MCPConfig(), logger)

    with sbox:
        gh = GitHubClient(
            GitHubConfig(
                token=os.getenv("GITHUB_TOKEN", ""),
                repo=args.repo or os.getenv("GITHUB_REPO", ""),
                base=args.base or os.getenv("GITHUB_BASE", "main"),
            ),
            sbox,
            logger,
        )
        agent = TrustedAgent(logger, sbox, gh, mcp)

        if args.cmd == "create-pr":
            pr = agent.create_demo_pr(
                file_path=args.file,
                content_append=args.content,
                commit_message=args.message,
                pr_title=args.title,
                pr_body=args.body,
                base_branch=args.base,
                new_branch=args.head or None,
            )
            logger.info("cli.ok", pr=pr)
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
