"""
LLM Client
Wrapper for Claude API (Anthropic)
"""
import os
import logging
from typing import Optional, Dict, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Claude API client

    Environment variables:
    - ANTHROPIC_API_KEY: Anthropic API key
    """

    # Pricing per model (USD per 1M tokens)
    PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "output": 15.00
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = Anthropic(api_key=self.api_key)
        logger.info("✅ Claude API client initialized")

    async def generate(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate completion using Claude

        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Max output tokens
            temperature: Sampling temperature (0-1)
            system: System prompt
            metadata: Additional metadata for logging

        Returns:
            dict: {
                'content': str,
                'usage': {...},
                'cost_cents': int,
                'model': str
            }
        """
        try:
            # Call Claude API
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "You are a helpful AI assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            content = message.content[0].text

            # Calculate cost
            cost_cents = self._calculate_cost(
                model=model,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens
            )

            logger.info(
                f"✅ LLM call: {message.usage.input_tokens} in + "
                f"{message.usage.output_tokens} out = ${cost_cents/100:.4f}"
            )

            return {
                'content': content,
                'usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens,
                    'total_tokens': message.usage.input_tokens + message.usage.output_tokens
                },
                'cost_cents': cost_cents,
                'model': model,
                'metadata': metadata or {}
            }

        except Exception as e:
            logger.error(f"❌ LLM API error: {str(e)}")
            raise

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> int:
        """Calculate cost in cents"""
        pricing = self.PRICING.get(model, self.PRICING["claude-3-5-sonnet-20241022"])

        cost_usd = (
            (input_tokens / 1_000_000) * pricing['input'] +
            (output_tokens / 1_000_000) * pricing['output']
        )

        return int(cost_usd * 100)  # Convert to cents

    async def generate_json(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON output

        Appends instruction to return valid JSON to the prompt
        """
        json_prompt = f"""{prompt}

IMPORTANT: Return your response as valid JSON only. Do not include any text before or after the JSON object."""

        response = await self.generate(
            prompt=json_prompt,
            model=model,
            **kwargs
        )

        # Parse JSON
        import json
        try:
            response['json'] = json.loads(response['content'])
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON: {e}")
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response['content'], re.DOTALL)
            if json_match:
                response['json'] = json.loads(json_match.group(0))
            else:
                raise ValueError("No valid JSON found in response")

        return response
