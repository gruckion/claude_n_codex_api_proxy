#!/usr/bin/env python3
"""Cross-platform launcher for Anthropic API proxy server."""
import argparse
import asyncio
import logging
import shutil
import sys
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def command_exists(cmd: str) -> bool:
    """Check if a command exists on PATH."""
    return shutil.which(cmd) is not None


def ensure_dependencies() -> None:
    """Verify required dependencies are available."""
    if not command_exists("claude"):
        print("⚠️  Warning: Claude Code CLI not found; local routing will fail.")
    if not command_exists("codex"):
        print("⚠️  Warning: Codex CLI not found; codex routing will fail.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Anthropic API Proxy Server Launcher")
    parser.add_argument("--host", default=os.environ.get("PROXY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PROXY_PORT", "8080")))
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--allowed-paths",
        help="Comma-separated regex patterns to replace default allowed paths",
    )
    parser.add_argument(
        "--allowed-path",
        action="append",
        default=[],
        help="Additional regex pattern to allow",
    )
    args = parser.parse_args()

    ensure_dependencies()

    from . import proxy_server

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    override = args.allowed_paths or os.environ.get("ALLOWED_PATHS")
    if override:
        patterns = [p.strip() for p in override.split(",") if p.strip()]
    else:
        patterns = list(proxy_server.DEFAULT_ALLOWED_PATH_PATTERNS)
    if args.allowed_path:
        patterns.extend(args.allowed_path)
    allowed_paths_regex = proxy_server.build_allowed_paths_regex(patterns)

    try:
        asyncio.run(
            proxy_server.start_proxy(
                args.host,
                args.port,
                allowed_paths_regex=allowed_paths_regex,
            )
        )
    except KeyboardInterrupt:
        print("\nProxy server stopped.")
        sys.exit(0)
    except Exception as exc:
        print(f"Proxy server error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
