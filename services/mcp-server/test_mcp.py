"""
Test script for MCP GitHub server.

Tests all 11 GitHub operation tools through the MCP protocol.
"""

import json
import httpx
import asyncio
from typing import Dict, Any

# MCP server URL (update for production)
MCP_URL = "http://localhost:8000/mcp/github"


async def mcp_request(method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send MCP request and return response."""
    request_body = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": method,
        "params": params or {}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(MCP_URL, json=request_body, timeout=30.0)
        return response.json()


async def test_tools_list():
    """Test listing available tools."""
    print("\n=== Test: tools/list ===")
    response = await mcp_request("tools/list")

    if "result" in response and "tools" in response["result"]:
        print(f"✅ Found {len(response['result']['tools'])} tools:")
        for tool in response["result"]["tools"]:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
        return True
    else:
        print(f"❌ Failed: {response}")
        return False


async def test_list_branches():
    """Test listing repository branches."""
    print("\n=== Test: github_list_branches ===")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_list_branches",
            "arguments": {}
        }
    )

    if "result" in response and "branches" in response["result"]:
        branches = response["result"]["branches"]
        print(f"✅ Found {len(branches)} branches:")
        for branch in branches[:5]:  # Show first 5
            print(f"  - {branch['name']} (protected: {branch['protected']})")
        return True
    else:
        print(f"❌ Failed: {response}")
        return False


async def test_list_prs():
    """Test listing pull requests."""
    print("\n=== Test: github_list_prs ===")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_list_prs",
            "arguments": {"state": "open"}
        }
    )

    if "result" in response and "pull_requests" in response["result"]:
        prs = response["result"]["pull_requests"]
        print(f"✅ Found {len(prs)} open PRs:")
        for pr in prs[:3]:  # Show first 3
            print(f"  - #{pr['number']}: {pr['title']} ({pr['head']} → {pr['base']})")
        return True
    else:
        print(f"❌ Failed: {response}")
        return False


async def test_list_issues():
    """Test listing GitHub issues."""
    print("\n=== Test: github_list_issues ===")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_list_issues",
            "arguments": {"state": "open"}
        }
    )

    if "result" in response and "issues" in response["result"]:
        issues = response["result"]["issues"]
        print(f"✅ Found {len(issues)} open issues:")
        for issue in issues[:3]:  # Show first 3
            print(f"  - #{issue['number']}: {issue['title']}")
            if issue['labels']:
                print(f"    Labels: {', '.join(issue['labels'])}")
        return True
    else:
        print(f"❌ Failed: {response}")
        return False


async def test_read_file():
    """Test reading file contents."""
    print("\n=== Test: github_read_file ===")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_read_file",
            "arguments": {
                "path": "README.md",
                "ref": "main"
            }
        }
    )

    if "result" in response and "content" in response["result"]:
        content_preview = response["result"]["content"][:100]
        print(f"✅ Read file successfully:")
        print(f"  Path: {response['result']['path']}")
        print(f"  Size: {response['result']['size']} bytes")
        print(f"  Preview: {content_preview}...")
        return True
    else:
        print(f"❌ Failed: {response}")
        return False


async def test_search_code():
    """Test searching code in repository."""
    print("\n=== Test: github_search_code ===")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_search_code",
            "arguments": {"query": "FastAPI"}
        }
    )

    if "result" in response and "items" in response["result"]:
        print(f"✅ Search found {response['result']['total_count']} results:")
        for item in response["result"]["items"][:3]:  # Show first 3
            print(f"  - {item['path']}")
        return True
    else:
        print(f"❌ Failed: {response}")
        return False


async def test_create_branch_and_commit():
    """Test creating branch and committing files (integration test)."""
    print("\n=== Integration Test: Create Branch + Commit ===")

    # Generate unique branch name
    import time
    branch_name = f"test/mcp-{int(time.time())}"

    # Step 1: Create branch
    print(f"Step 1: Creating branch '{branch_name}'...")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_create_branch",
            "arguments": {
                "branch": branch_name,
                "from_branch": "main"
            }
        }
    )

    if "error" in response:
        print(f"❌ Branch creation failed: {response['error']}")
        return False

    print(f"✅ Branch created: {response['result']['branch']}")

    # Step 2: Commit test file
    print("Step 2: Committing test file...")
    response = await mcp_request(
        "tools/call",
        {
            "name": "github_commit_files",
            "arguments": {
                "branch": branch_name,
                "message": "test: MCP server integration test",
                "files": [
                    {
                        "path": "test-mcp.txt",
                        "content": f"MCP test file created at {time.time()}"
                    }
                ]
            }
        }
    )

    if "error" in response:
        print(f"❌ Commit failed: {response['error']}")
        return False

    print(f"✅ Committed {response['result']['files_committed']} file(s)")
    print(f"   Commit SHA: {response['result']['commit_sha']}")

    print(f"\n⚠️  Test branch '{branch_name}' created - cleanup manually if needed")
    return True


async def run_all_tests():
    """Run all MCP server tests."""
    print("=" * 60)
    print("MCP GitHub Server Test Suite")
    print("=" * 60)

    results = []

    # Read-only tests (safe to run anytime)
    results.append(("tools/list", await test_tools_list()))
    results.append(("github_list_branches", await test_list_branches()))
    results.append(("github_list_prs", await test_list_prs()))
    results.append(("github_list_issues", await test_list_issues()))
    results.append(("github_read_file", await test_read_file()))
    results.append(("github_search_code", await test_search_code()))

    # Write tests (creates test branch - run with caution)
    # Uncomment to run integration tests
    # results.append(("create_branch_and_commit", await test_create_branch_and_commit()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
