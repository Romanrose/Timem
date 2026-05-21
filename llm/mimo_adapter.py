"""
TiMem Mimo LLM Adapter
OpenAI-compatible adapter for Xiaomi Mimo gateway.
"""

from __future__ import annotations

from typing import Optional

from llm.base_llm import ModelConfig
from llm.openai_adapter import OpenAIAdapter


class MimoAdapter(OpenAIAdapter):
    """Mimo adapter backed by the OpenAI-compatible request path."""

    def __init__(self, config: Optional[ModelConfig] = None):
        from timem.utils.config_manager import get_llm_config

        llm_config = get_llm_config()
        mimo_config = llm_config.get("providers", {}).get("mimo", {})

        if config is None:
            config = ModelConfig(
                model_name=mimo_config.get("model", "mimo-v2-omni"),
                temperature=mimo_config.get("temperature", 0.7),
                max_tokens=mimo_config.get("max_tokens", 2048),
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=None,
                stream=False,
            )

        super().__init__(config)

        self.provider_name = "mimo"
        self.base_url = mimo_config.get("base_url", "https://token-plan-cn.xiaomimimo.com/v1")
        self.api_key = mimo_config.get("api_key", "")
        self.timeout = mimo_config.get("timeout", 90)
        self.api_keys = []
        self._current_key_index = 0
        self._init_multi_api_keys(mimo_config)

        # Override supported models to include Mimo models
        self.supported_models = [
            "mimo-v2-omni",
            "mimo-v2-flash",
            "mimo-v2-pro",
        ]

        self.logger.info(
            "Initializing Mimo adapter: base_url=%s, model=%s",
            self.base_url,
            self.config.model_name,
        )

    def _allow_custom_model_on_compatible_gateway(self) -> bool:
        """Mimo adapter always allows custom model names."""
        return True
