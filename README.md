# Claude & Codex API Proxy

A universal HTTP proxy and Python library that automatically routes Anthropic, OpenAI, or Gemini API calls to local CLI tools (Claude Code, Codex, or Gemini) when the API key is set to all 9s, otherwise uses the real cloud APIs.

## Two Solutions Included

### 1. Universal HTTP Proxy (Works with ANY language/tool)
An HTTP/HTTPS proxy server that intercepts Anthropic, OpenAI, or Gemini API calls from any application, regardless of programming language.

### 2. Python Library (Python-specific)
Drop-in replacements for the Anthropic, OpenAI, and Gemini Python clients that handle routing internally.

## Features

- **Universal Compatibility**: HTTP proxy works with ANY programming language or tool
- **Transparent Routing**: No code changes needed for existing projects (with proxy)
- **Claude Code, Codex & Gemini Integration**: Automatically routes to local CLIs when API key is all 9s
- **API Compatibility**: Maintains Anthropic/OpenAI/Gemini API response format
- **Easy Configuration**: Just set your API key to all 9s to enable local routing
- **Python Library**: Drop-in replacement clients for Anthropic, OpenAI, and Gemini Python SDKs
- **Async Support**: Includes both synchronous and asynchronous clients
- **Environment Variables**: Load configuration from `.env` files

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd claude_n_codex_api_proxy

# Install with uv
uv sync

# Or install with dev dependencies
uv sync --all-extras
```

### Using pip

```bash
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

Make sure you have the relevant CLI installed and available in your PATH:
```bash
claude --version   # for Claude Code
codex --version    # for Codex
gemini --version   # for Gemini
```

## Quick Start

### Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your settings
```

### Option 1: Universal HTTP Proxy (Recommended)

1. **Start the proxy:**
```bash
# Using poe (recommended)
uv run poe start

# Or directly
uv run python -m claude_codex_proxy.cli
```

2. **Configure your environment:**

macOS/Linux (bash/zsh):
```bash
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
export ANTHROPIC_API_KEY=999999999999   # All 9s for Claude Code
export OPENAI_API_KEY=999999999999      # All 9s for Codex
export GOOGLE_API_KEY=999999999999      # All 9s for Gemini
```

Windows (PowerShell):
```powershell
$env:HTTP_PROXY="http://localhost:8080"
$env:HTTPS_PROXY="http://localhost:8080"
$env:ANTHROPIC_API_KEY="999999999999"
$env:OPENAI_API_KEY="999999999999"
$env:GOOGLE_API_KEY="999999999999"
```

3. **Use from ANY language/tool:**
```bash
# Python, Node.js, cURL, etc - all work through the proxy!
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: 999999999999" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-sonnet-20240229","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

### Option 2: Python Library

```python
from claude_codex_proxy import create_client

# Use Codex locally
client = create_client(provider="codex", api_key="999999999999")

# Or use Claude Code locally
# client = create_client(provider="claude", api_key="999999999999")

# Or use cloud providers
# client = create_client(provider="anthropic", api_key="sk-ant-real-key")

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

print(message.content[0].text)
```

Valid values for `provider` are `"claude"`, `"anthropic"`, `"codex"`, and `"openai"`. Passing any other value to `create_client` or via the `AI_ROUTER_DEFAULT` environment variable will raise a `ValueError`.

## Commands

```bash
# Start the proxy server
uv run poe start

# Run tests
uv run poe test

# Run tests with verbose output
uv run poe test-verbose

# Run setup (check dependencies, generate certificates)
uv run poe setup
```

## Allowing Additional API Endpoints

By default the proxy only permits a curated set of `/v1` API paths. The default configuration covers common Anthropic and OpenAI endpoints and falls back to allow any path under `/v1/`.

To permit other endpoints you can either override the entire allow-list or extend it:

- **Override** with a comma-separated list via the `ALLOWED_PATHS` environment variable or `--allowed-paths` option:

  ```bash
  ALLOWED_PATHS="^/v1/my/endpoint$" uv run poe start
  # or
  uv run python -m claude_codex_proxy.cli --allowed-paths '^/v1/my/endpoint$'
  ```

- **Extend** the defaults by passing `--allowed-path` one or more times:

  ```bash
  uv run python -m claude_codex_proxy.cli --allowed-path '^/v1/beta$' --allowed-path '^/v1/other$'
  ```

## How It Works

1. When you create a client with an API key that's all 9s (e.g., "999999999999"), the router automatically routes requests to the local CLI
2. The router converts standard API format to the respective local CLI format
3. Responses from the local CLI are converted back to the standard API format
4. Your code doesn't need to change—it behaves like the official client

## Testing

Run the test suite to verify the routing works correctly:
```bash
uv run poe test
```

## API Key Detection

The following API key formats will trigger local routing:
- `"999999999999"` - Pure 9s
- `"sk-ant-999999999999"` or `"sk-openai-999999999999"` - With standard prefix
- Any string where the last segment (after splitting by `-`) is all 9s

## Limitations

- Streaming is not yet supported when routing to local CLIs
- Token counting is approximate when using local CLI tools
- Some advanced API features may not be available through local CLIs

## Project Structure

```
claude_n_codex_api_proxy/
├── src/
│   └── claude_codex_proxy/
│       ├── __init__.py           # Package exports
│       ├── cli.py                # CLI entry point
│       ├── proxy_server.py       # HTTP/HTTPS proxy server
│       ├── anthropic_router.py   # Anthropic/Claude Code routing
│       ├── openai_router.py      # OpenAI/Codex routing
│       ├── gemini_router.py      # Gemini routing
│       ├── claude_code_client.py # Claude Code CLI interface
│       ├── codex_client.py       # Codex CLI interface
│       ├── gemini_client.py      # Gemini CLI interface
│       ├── claude_code_proxy_handler.py  # Proxy handler for Claude
│       ├── codex_proxy_handler.py        # Proxy handler for Codex
│       ├── gemini_proxy_handler.py       # Proxy handler for Gemini
│       ├── setup_proxy.py        # Setup script
│       └── utils.py              # Common utilities
├── tests/                        # Test files
├── pyproject.toml               # Project configuration
├── .env.example                 # Example environment variables
└── README.md                    # This file
```

## Planning a Migration Away From Cloud API Keys?

If you need to adapt an existing application so it can call Claude Code or Codex directly via the locally installed CLIs (e.g., Claude Max or ChatGPT Pro subscriptions), read [`docs/direct_llm_integration.md`](docs/direct_llm_integration.md). The guide explains how the proxy works, what preconditions must hold, and how to translate API payloads into CLI prompts and back without ever storing API keys in your codebase.
