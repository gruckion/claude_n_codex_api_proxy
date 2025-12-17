import asyncio
import os
import sys
from pathlib import Path
import contextlib

import pytest

from claude_codex_proxy.claude_code_client import ClaudeCodeClient
from claude_codex_proxy.codex_client import CodexClient
from claude_codex_proxy.claude_code_proxy_handler import ClaudeCodeProxyHandler
from claude_codex_proxy.codex_proxy_handler import CodexProxyHandler
from claude_codex_proxy.utils import CLITimeoutError

SCRIPT = str(Path(__file__).with_name("hanging_cli.py"))
# Use Python interpreter to run the script
SCRIPT_CMD = [sys.executable, SCRIPT]


async def _fast_timeout(awaitable, timeout, *args, **kwargs):
    task = asyncio.create_task(awaitable)
    await asyncio.sleep(0.05)
    task.cancel()
    with contextlib.suppress(BaseException):
        await task
    raise asyncio.TimeoutError


@pytest.mark.asyncio
@pytest.mark.skip(reason="Test requires running hanging_cli.py as CLI command")
@pytest.mark.parametrize("client_cls", [ClaudeCodeClient, CodexClient])
async def test_client_process_killed_on_timeout(client_cls, monkeypatch, tmp_path):
    pid_file = tmp_path / "pid"
    os.environ["PID_FILE"] = str(pid_file)
    client = client_cls()
    client.claude_command = SCRIPT

    monkeypatch.setattr(asyncio, "wait_for", _fast_timeout)

    with pytest.raises(CLITimeoutError):
        await client.acreate_message(
            messages=[{"role": "user", "content": "hi"}],
            model="test",
            max_tokens=1,
        )

    pid = int(pid_file.read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    os.environ.pop("PID_FILE", None)


@pytest.mark.asyncio
@pytest.mark.skip(reason="Test requires running hanging_cli.py as CLI command")
@pytest.mark.parametrize("handler_cls", [ClaudeCodeProxyHandler, CodexProxyHandler])
async def test_handler_process_killed_on_timeout(handler_cls, monkeypatch, tmp_path):
    pid_file = tmp_path / "pid"
    os.environ["PID_FILE"] = str(pid_file)
    handler = handler_cls()
    handler.claude_command = SCRIPT

    monkeypatch.setattr(asyncio, "wait_for", _fast_timeout)

    with pytest.raises(CLITimeoutError):
        await handler._call_claude_cli_async("prompt")

    pid = int(pid_file.read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    os.environ.pop("PID_FILE", None)
