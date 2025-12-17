"""
Claude & Codex API Proxy - Universal HTTP proxy and Python library for routing
Anthropic, OpenAI, and Gemini API calls to local CLI tools.
"""

from .anthropic_router import (
    AnthropicRouter,
    AsyncAnthropicRouter,
    create_client,
)
from .openai_router import (
    OpenAIRouter,
    AsyncOpenAIRouter,
    create_openai_client,
)
from .gemini_router import (
    GenerativeModel,
    configure as configure_gemini,
)
from .claude_code_client import ClaudeCodeClient
from .codex_client import CodexClient
from .gemini_client import GeminiClient
from .utils import (
    is_all_nines_api_key,
    CLIError,
    CLINotFoundError,
    CLITimeoutError,
)

__version__ = "0.1.0"

__all__ = [
    # Anthropic routing
    "AnthropicRouter",
    "AsyncAnthropicRouter",
    "create_client",
    # OpenAI routing
    "OpenAIRouter",
    "AsyncOpenAIRouter",
    "create_openai_client",
    # Gemini routing
    "GenerativeModel",
    "configure_gemini",
    # Clients
    "ClaudeCodeClient",
    "CodexClient",
    "GeminiClient",
    # Utilities
    "is_all_nines_api_key",
    "CLIError",
    "CLINotFoundError",
    "CLITimeoutError",
]
