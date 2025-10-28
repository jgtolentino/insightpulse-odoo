import logging
import time

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MicroservicesHealthController(http.Controller):

    @http.route("/microservices/health", type="json", auth="public", methods=["POST"])
    def health_check(self):
        """Health check endpoint for microservices components"""
        start_time = time.time()

        # Get microservices configuration
        config = (
            request.env["microservices.config"]
            .sudo()
            .search([("is_active", "=", True)], limit=1)
        )

        if not config:
            return {
                "status": "error",
                "message": "No active microservices configuration found",
                "timestamp": time.time(),
                "components": {},
            }

        components = {
            "ocr": {"status": "unknown", "response_time": 0, "error": None},
            "llm": {"status": "unknown", "response_time": 0, "error": None},
            "agent": {"status": "unknown", "response_time": 0, "error": None},
        }

        # Check OCR service
        if config.ocr_endpoint:
            try:
                ocr_start = time.time()
                response = requests.get(
                    f"{config.ocr_endpoint}/health",
                    timeout=5,
                    headers=(
                        {"Authorization": f"Bearer {config.ocr_token}"}
                        if config.ocr_token
                        else {}
                    ),
                )
                components["ocr"]["response_time"] = time.time() - ocr_start
                components["ocr"]["status"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
                components["ocr"]["status_code"] = response.status_code
            except Exception as e:
                components["ocr"]["status"] = "error"
                components["ocr"]["error"] = str(e)
                _logger.error(f"OCR health check failed: {e}")

        # Check LLM service
        if config.llm_endpoint:
            try:
                llm_start = time.time()
                response = requests.get(
                    f"{config.llm_endpoint}/health",
                    timeout=5,
                    headers=(
                        {"Authorization": f"Bearer {config.llm_token}"}
                        if config.llm_token
                        else {}
                    ),
                )
                components["llm"]["response_time"] = time.time() - llm_start
                components["llm"]["status"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
                components["llm"]["status_code"] = response.status_code
            except Exception as e:
                components["llm"]["status"] = "error"
                components["llm"]["error"] = str(e)
                _logger.error(f"LLM health check failed: {e}")

        # Check Agent service
        if config.agent_endpoint:
            try:
                agent_start = time.time()
                response = requests.get(
                    f"{config.agent_endpoint}/health",
                    timeout=5,
                    headers=(
                        {"Authorization": f"Bearer {config.agent_token}"}
                        if config.agent_token
                        else {}
                    ),
                )
                components["agent"]["response_time"] = time.time() - agent_start
                components["agent"]["status"] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
                components["agent"]["status_code"] = response.status_code
            except Exception as e:
                components["agent"]["status"] = "error"
                components["agent"]["error"] = str(e)
                _logger.error(f"Agent health check failed: {e}")

        # Log health check results
        total_time = time.time() - start_time
        _logger.info(
            f"Microservices health check completed in {total_time:.2f}s: {components}"
        )

        # Log failures to audit table
        self._log_health_check_results(config, components, total_time)

        # Determine overall status
        overall_status = "healthy"
        for component in components.values():
            if component["status"] in ["unhealthy", "error"]:
                overall_status = "unhealthy"
                break

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "response_time": total_time,
            "components": components,
        }

    def _log_health_check_results(self, config, components, total_time):
        """Log health check results to audit table"""
        try:
            # Create health check log entry
            health_log_model = request.env["microservices.health.log"].sudo()

            for component_name, component_data in components.items():
                health_log_model.create(
                    {
                        "config_id": config.id,
                        "component": component_name,
                        "status": component_data["status"],
                        "response_time": component_data.get("response_time", 0),
                        "error_message": component_data.get("error"),
                        "total_check_time": total_time,
                    }
                )
        except Exception as e:
            _logger.error(f"Failed to log health check results: {e}")
