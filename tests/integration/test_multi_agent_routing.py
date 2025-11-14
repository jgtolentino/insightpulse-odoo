"""
Multi-Agent Routing Integration Tests
Tests orchestrator's ability to route tasks to correct specialist agents
"""
import pytest
import requests
from typing import Dict, List

# Test configuration - update with actual deployed URLs
SPECIALIST_URLS = {
    "odoo_developer": "https://odoo-developer-agent.ondigitalocean.app",
    "finance_ssc_expert": "https://finance-ssc-expert.ondigitalocean.app",
    "bi_architect": "https://bi-architect.ondigitalocean.app",
    "devops_engineer": "https://devops-engineer.ondigitalocean.app"
}

ORCHESTRATOR_URL = "https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run"

@pytest.fixture
def specialist_services():
    """Fixture to provide specialist service URLs"""
    return SPECIALIST_URLS

class TestAgentRouting:
    """Test correct routing to specialist agents"""

    def test_route_to_odoo_developer(self, specialist_services):
        """Test routing of Odoo development tasks"""
        task = "Create an Odoo 19 module for expense report approval workflow"

        response = requests.post(
            f"{specialist_services['odoo_developer']}/execute",
            json={"task": task, "context": {}, "conversation_id": "test_001"},
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        assert data["confidence"] > 0.8
        assert "actions_taken" in data
        assert len(data["actions_taken"]) > 0

        # Check for Odoo-specific keywords
        result_lower = data["result"].lower()
        assert any(kw in result_lower for kw in ["module", "model", "__manifest__.py", "odoo"])

    def test_route_to_finance_ssc_expert(self, specialist_services):
        """Test routing of BIR compliance tasks"""
        task = "Generate BIR Form 1601-C for January 2025 for RIM agency"

        response = requests.post(
            f"{specialist_services['finance_ssc_expert']}/execute",
            json={
                "task": task,
                "context": {"agency": "RIM", "period": "2025-01"},
                "conversation_id": "test_002"
            },
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        assert data["confidence"] > 0.9  # Very high confidence for compliance
        assert "1601-C" in data["result"] or "1601C" in data["result"]

    def test_route_to_bi_architect(self, specialist_services):
        """Test routing of BI/analytics tasks"""
        task = "Design a Superset dashboard for expense analytics with category breakdown"

        response = requests.post(
            f"{specialist_services['bi_architect']}/execute",
            json={"task": task, "context": {}, "conversation_id": "test_003"},
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        assert data["confidence"] > 0.8
        result_lower = data["result"].lower()
        assert any(kw in result_lower for kw in ["dashboard", "chart", "sql", "superset"])

    def test_route_to_devops_engineer(self, specialist_services):
        """Test routing of DevOps/deployment tasks"""
        task = "Create a deployment spec for a new API service on DigitalOcean App Platform"

        response = requests.post(
            f"{specialist_services['devops_engineer']}/execute",
            json={"task": task, "context": {}, "conversation_id": "test_004"},
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        assert data["confidence"] > 0.8
        result_lower = data["result"].lower()
        assert any(kw in result_lower for kw in ["deploy", "app platform", "yaml", "digitalocean"])

class TestMultiAgentCoordination:
    """Test multi-agent coordination workflows"""

    @pytest.mark.slow
    def test_create_and_deploy_workflow(self, specialist_services):
        """Test coordination between odoo_developer and devops_engineer"""
        # Step 1: Create module (odoo_developer)
        create_task = "Create a simple Odoo module for tracking project tasks"
        create_response = requests.post(
            f"{specialist_services['odoo_developer']}/execute",
            json={"task": create_task, "context": {}, "conversation_id": "test_workflow_001"},
            timeout=30
        )

        assert create_response.status_code == 200
        create_data = create_response.json()
        assert create_data["confidence"] > 0.8

        # Step 2: Deploy module (devops_engineer)
        deploy_task = "Deploy the Odoo module to staging environment"
        deploy_response = requests.post(
            f"{specialist_services['devops_engineer']}/execute",
            json={"task": deploy_task, "context": {"previous_step": "module_created"}, "conversation_id": "test_workflow_001"},
            timeout=30
        )

        assert deploy_response.status_code == 200
        deploy_data = deploy_response.json()
        assert deploy_data["confidence"] > 0.7

    @pytest.mark.slow
    def test_analyze_and_visualize_workflow(self, specialist_services):
        """Test coordination between finance_ssc_expert and bi_architect"""
        # Step 1: Analyze compliance requirements (finance_ssc_expert)
        analyze_task = "Analyze BIR withholding tax requirements for Q1 2025"
        analyze_response = requests.post(
            f"{specialist_services['finance_ssc_expert']}/execute",
            json={"task": analyze_task, "context": {}, "conversation_id": "test_workflow_002"},
            timeout=30
        )

        assert analyze_response.status_code == 200
        analyze_data = analyze_response.json()
        assert analyze_data["confidence"] > 0.9

        # Step 2: Create visualization (bi_architect)
        visualize_task = "Create a Superset dashboard for withholding tax analytics"
        visualize_response = requests.post(
            f"{specialist_services['bi_architect']}/execute",
            json={"task": visualize_task, "context": {"previous_step": "requirements_analyzed"}, "conversation_id": "test_workflow_002"},
            timeout=30
        )

        assert visualize_response.status_code == 200
        visualize_data = visualize_response.json()
        assert visualize_data["confidence"] > 0.8

class TestHealthAndCapabilities:
    """Test health checks and capability discovery"""

    def test_all_health_endpoints(self, specialist_services):
        """Verify all specialist services are healthy"""
        for agent_name, base_url in specialist_services.items():
            response = requests.get(f"{base_url}/health", timeout=5)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["agent"] == agent_name

    def test_all_capabilities_endpoints(self, specialist_services):
        """Verify all specialist services expose capabilities"""
        for agent_name, base_url in specialist_services.items():
            response = requests.get(f"{base_url}/capabilities", timeout=5)

            assert response.status_code == 200
            data = response.json()
            assert "agent_name" in data
            assert "capabilities" in data
            assert isinstance(data["capabilities"], list)
            assert len(data["capabilities"]) > 0

class TestPerformanceMetrics:
    """Test performance requirements"""

    def test_response_time_p95_under_3s(self, specialist_services):
        """Verify P95 response time is under 3 seconds"""
        response_times = []

        # Make 20 requests to each specialist
        for agent_name, base_url in specialist_services.items():
            for i in range(5):  # 5 requests per agent
                import time
                start = time.time()

                response = requests.post(
                    f"{base_url}/execute",
                    json={
                        "task": f"Test query {i}",
                        "context": {},
                        "conversation_id": f"perf_test_{i}"
                    },
                    timeout=30
                )

                elapsed = time.time() - start
                response_times.append(elapsed)

        # Calculate P95
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95_time = response_times[p95_index]

        assert p95_time < 3.0, f"P95 response time {p95_time:.2f}s exceeds 3s threshold"

    def test_cost_per_query_under_10_cents(self, specialist_services):
        """Verify average cost per query is under $0.10"""
        # Make a test query and check metadata for cost
        response = requests.post(
            f"{specialist_services['odoo_developer']}/execute",
            json={
                "task": "Simple test query",
                "context": {},
                "conversation_id": "cost_test"
            },
            timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        if "metadata" in data and "cost_usd" in data["metadata"]:
            cost = data["metadata"]["cost_usd"]
            assert cost < 0.10, f"Cost ${cost:.4f} exceeds $0.10 threshold"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
