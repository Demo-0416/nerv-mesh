"""Local sandbox for restricted shell execution."""

import asyncio
from pathlib import Path


class LocalSandbox:
    """Execute shell commands in an isolated working directory."""

    def __init__(self, workdir: Path, timeout: int = 30):
        self.workdir = workdir
        self.timeout = timeout
        self.workdir.mkdir(parents=True, exist_ok=True)

    async def execute(self, command: str) -> str:
        """Run a command and return combined stdout + stderr."""
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=self.workdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            return f"[timeout] Command exceeded {self.timeout}s limit"

        output = stdout.decode()
        if stderr:
            output += f"\n[stderr]\n{stderr.decode()}"
        return output.strip()
