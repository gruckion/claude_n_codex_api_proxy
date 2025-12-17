"""
Gemini API Router that routes to Gemini CLI when API key is all 9s

Migrated from deprecated google-generativeai to google-genai SDK.
"""
import os
from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types

from .gemini_client import GeminiClient

# Global storage for the client and configured API key
_client: Optional[genai.Client] = None
_configured_api_key: Optional[str] = None


def _is_all_nines(api_key: Optional[str]) -> bool:
    """Check if the API key is all 9s."""
    if not api_key:
        return False
    # Remove prefixes or query params if present (though typically just the key string)
    return all(c == '9' for c in api_key)


def configure(api_key: Optional[str] = None, **kwargs):
    """
    Configure the Gemini API.

    Creates a Client instance for the new google-genai SDK.
    """
    global _configured_api_key, _client
    _configured_api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

    # Create client only if not using local mode (all 9s)
    if not _is_all_nines(_configured_api_key):
        _client = genai.Client(api_key=_configured_api_key)


class GenerativeModel:
    """
    A wrapper that provides backward-compatible interface using the new
    google-genai SDK, and routes to Gemini CLI when the configured API
    key is all 9s.
    """

    def __init__(
        self,
        model_name: str,
        generation_config: Optional[types.GenerateContentConfig] = None,
        safety_settings: Optional[Any] = None,
        tools: Optional[Any] = None,
        tool_config: Optional[Any] = None,
        system_instruction: Optional[Any] = None
    ):
        self.model_name = model_name
        self._generation_config = generation_config
        self.safety_settings = safety_settings
        self.tools = tools
        self.tool_config = tool_config
        self.system_instruction = system_instruction

        # Determine mode based on globally configured key
        self._is_local_mode = _is_all_nines(_configured_api_key)

        if self._is_local_mode:
            self.client = GeminiClient()
        else:
            self.client = None

    def generate_content(
        self,
        contents: Union[str, List[Dict[str, Any]]],
        generation_config: Optional[types.GenerateContentConfig] = None,
        safety_settings: Optional[Any] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate content, routing to local CLI if in local mode.
        """
        if self._is_local_mode:
            # Use local Gemini Client
            config = generation_config or self._generation_config

            if stream:
                raise NotImplementedError("Streaming not supported in local mode")

            return self.client.generate_content(
                model=self.model_name,
                contents=contents,
                generation_config=config,
                stream=stream
            )
        else:
            # Use new SDK client
            config = generation_config or self._generation_config

            # Build config with system instruction if not already set
            if self.system_instruction and config is None:
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )

            if stream:
                return _client.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
            return _client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

    async def generate_content_async(
        self,
        contents: Union[str, List[Dict[str, Any]]],
        generation_config: Optional[types.GenerateContentConfig] = None,
        safety_settings: Optional[Any] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Async version of generate_content.
        """
        if self._is_local_mode:
            config = generation_config or self._generation_config
            if stream:
                raise NotImplementedError("Streaming not supported in local mode")

            return await self.client.generate_content_async(
                model=self.model_name,
                contents=contents,
                generation_config=config,
                stream=stream
            )
        else:
            config = generation_config or self._generation_config

            if self.system_instruction and config is None:
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )

            if stream:
                return await _client.aio.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
            return await _client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )


# Expose GenerateContentConfig as GenerationConfig for backward compatibility
GenerationConfig = types.GenerateContentConfig
