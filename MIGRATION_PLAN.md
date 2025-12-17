# Migration Plan: google.generativeai to google.genai

## Overview

The `google-generativeai` package has been deprecated and support ended on November 30, 2025. This document outlines the complete migration plan to the new `google-genai` SDK.

## Key API Differences

### 1. Package & Import Changes

| Old SDK | New SDK |
|---------|---------|
| `pip install google-generativeai` | `pip install google-genai` |
| `import google.generativeai as genai` | `from google import genai` |
| `from google.generativeai.types import GenerationConfig` | `from google.genai import types` |

### 2. Client Initialization Pattern

**Old SDK (implicit client):**
```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')
```

**New SDK (explicit client):**
```python
from google import genai
client = genai.Client(api_key="YOUR_API_KEY")
# Or with env var GEMINI_API_KEY / GOOGLE_API_KEY:
client = genai.Client()
```

### 3. Generate Content Changes

**Old SDK:**
```python
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello")
print(response.text)
```

**New SDK:**
```python
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Hello'
)
print(response.text)
```

### 4. Configuration Changes

**Old SDK:**
```python
from google.generativeai.types import GenerationConfig
config = GenerationConfig(
    temperature=0.7,
    max_output_tokens=1000,
    top_p=0.95,
    top_k=40
)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config=config)
```

**New SDK:**
```python
from google.genai import types
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Hello',
    config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=1000,
        top_p=0.95,
        top_k=40
    )
)
```

### 5. Async API Changes

**Old SDK:**
```python
response = await model.generate_content_async(contents)
```

**New SDK:**
```python
response = await client.aio.models.generate_content(
    model='gemini-2.0-flash',
    contents='Hello'
)
```

---

## Files to Modify

### 1. `pyproject.toml`

**Change:**
```diff
- "google-generativeai>=0.3.0",
+ "google-genai>=1.0.0",
```

### 2. `src/claude_codex_proxy/gemini_router.py`

This file requires the most significant changes:

#### 2.1 Import Changes

**Before (lines 6-7):**
```python
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
```

**After:**
```python
from google import genai
from google.genai import types
```

#### 2.2 Global Client Storage

**Before:**
```python
_configured_api_key: Optional[str] = None
```

**After:**
```python
_client: Optional[genai.Client] = None
_configured_api_key: Optional[str] = None
```

#### 2.3 Configure Function

**Before (lines 23-35):**
```python
def configure(api_key: Optional[str] = None, **kwargs):
    global _configured_api_key
    _configured_api_key = api_key or os.environ.get("GOOGLE_API_KEY")

    if not _is_all_nines(_configured_api_key):
        genai.configure(api_key=_configured_api_key, **kwargs)
```

**After:**
```python
def configure(api_key: Optional[str] = None, **kwargs):
    global _configured_api_key, _client
    _configured_api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not _is_all_nines(_configured_api_key):
        _client = genai.Client(api_key=_configured_api_key)
```

#### 2.4 GenerativeModel Class

The class needs to be refactored to use the new client-based approach:

**Before:**
```python
class GenerativeModel:
    def __init__(self, model_name: str, generation_config: Optional[GenerationConfig] = None, ...):
        self._real_model = genai.GenerativeModel(model_name=model_name, ...)

    def generate_content(self, contents, generation_config=None, ...):
        return self._real_model.generate_content(contents, ...)
```

**After:**
```python
class GenerativeModel:
    def __init__(self, model_name: str, generation_config: Optional[types.GenerateContentConfig] = None, ...):
        self.model_name = model_name
        self._generation_config = generation_config
        self._system_instruction = system_instruction
        # No longer create a model object - use client directly

    def generate_content(self, contents, generation_config=None, ...):
        config = generation_config or self._generation_config
        return _client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )

    async def generate_content_async(self, contents, generation_config=None, ...):
        config = generation_config or self._generation_config
        return await _client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )
```

### 3. `src/claude_codex_proxy/gemini_client.py`

Update the `GenerationConfig` dataclass and response structure to align with new SDK:

#### 3.1 GenerationConfig

**Before (lines 8-15):**
```python
@dataclass
class GenerationConfig:
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    candidate_count: Optional[int] = None
    max_output_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
```

**After:**
```python
# Remove local dataclass - use types.GenerateContentConfig from google.genai
# OR keep it for CLI routing compatibility, but document it's local-only
```

#### 3.2 Response Object Structure

The response object in `_create_response_object()` should mimic the new SDK structure:

**Before (lines 169-183):**
```python
def _create_response_object(self, text: str) -> Any:
    class Candidate:
        def __init__(self, text):
            self.content = type('Content', (), {'parts': [type('Part', (), {'text': text})()]})()
            self.finish_reason = 1

    class Response:
        def __init__(self, text):
            self.text = text
            self.candidates = [Candidate(text)]
            self.parts = [type('Part', (), {'text': text})()]

    return Response(text)
```

**After:** (enhanced to match new SDK response structure)
```python
def _create_response_object(self, text: str) -> Any:
    class Part:
        def __init__(self, text):
            self.text = text

    class Content:
        def __init__(self, text):
            self.parts = [Part(text)]
            self.role = "model"

    class Candidate:
        def __init__(self, text):
            self.content = Content(text)
            self.finish_reason = "STOP"

    class Response:
        def __init__(self, text):
            self.text = text
            self.candidates = [Candidate(text)]
            self.parts = [Part(text)]
            # New SDK uses pydantic models with these methods
            def model_dump_json(self, **kwargs):
                import json
                return json.dumps({"text": self.text})

        model_dump_json = model_dump_json

    return Response(text)
```

---

## Complete Refactored `gemini_router.py`

```python
"""
Gemini API Router that routes to Gemini CLI when API key is all 9s
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
    return all(c == '9' for c in api_key)


def configure(api_key: Optional[str] = None, **kwargs):
    """
    Configure the Gemini API.
    """
    global _configured_api_key, _client
    _configured_api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

    # Create client only if not using local mode (all 9s)
    if not _is_all_nines(_configured_api_key):
        _client = genai.Client(api_key=_configured_api_key)


class GenerativeModel:
    """
    A wrapper that provides google.generativeai-compatible interface
    using the new google.genai SDK, and routes to Gemini CLI when
    the configured API key is all 9s.
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

            # Build config with system instruction if provided
            if self.system_instruction and config is None:
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )
            elif self.system_instruction and config:
                # Merge system instruction into config
                pass  # types.GenerateContentConfig handles this

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


# Expose types for backward compatibility
GenerationConfig = types.GenerateContentConfig
```

---

## Migration Steps

1. **Update dependency in `pyproject.toml`**
   - Replace `google-generativeai>=0.3.0` with `google-genai>=1.0.0`

2. **Update `gemini_router.py`**
   - Change imports
   - Add global `_client` variable
   - Update `configure()` to create Client instead of calling `genai.configure()`
   - Update `GenerativeModel` class to use `_client.models.generate_content()`
   - Update async method to use `_client.aio.models.generate_content()`
   - Expose `types.GenerateContentConfig` as `GenerationConfig` for compatibility

3. **Update `gemini_client.py`**
   - Keep local `GenerationConfig` dataclass for CLI routing (optional)
   - Update response structure in `_create_response_object()` if needed

4. **Run tests**
   - `uv run pytest`
   - Verify all tests pass

5. **Test manually**
   - Test with real API key
   - Test with all-9s key (local CLI mode)

---

## Potential Breaking Changes

1. **Response Structure**: The new SDK returns pydantic models with methods like `model_dump_json()`. Code relying on specific response attributes may need updates.

2. **Configuration**: `GenerationConfig` is now `types.GenerateContentConfig` with slightly different parameter handling.

3. **Streaming**: The streaming API now uses `generate_content_stream()` instead of a `stream=True` parameter.

4. **Async**: Async methods are now accessed via `client.aio.models.*` namespace.

---

## References

- [Official Migration Guide](https://ai.google.dev/gemini-api/docs/migrate)
- [New SDK GitHub](https://github.com/googleapis/python-genai)
- [New SDK Documentation](https://googleapis.github.io/python-genai/)
- [Deprecated SDK Repository](https://github.com/google-gemini/deprecated-generative-ai-python)
