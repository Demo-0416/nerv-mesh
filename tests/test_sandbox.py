"""Tests for the local sandbox."""

import pytest

from nerv_mesh.sandbox import LocalSandbox


@pytest.fixture
def sandbox(tmp_path):
    return LocalSandbox(workdir=tmp_path, timeout=5)


@pytest.mark.asyncio
async def test_execute_simple_command(sandbox):
    result = await sandbox.execute("echo hello")
    assert "hello" in result


@pytest.mark.asyncio
async def test_execute_captures_stderr(sandbox):
    result = await sandbox.execute("echo err >&2")
    assert "err" in result


@pytest.mark.asyncio
async def test_execute_timeout(tmp_path):
    sandbox = LocalSandbox(workdir=tmp_path, timeout=1)
    result = await sandbox.execute("sleep 10")
    assert "timeout" in result.lower()


@pytest.mark.asyncio
async def test_workdir_is_cwd(sandbox):
    result = await sandbox.execute("pwd")
    assert str(sandbox.workdir) in result
