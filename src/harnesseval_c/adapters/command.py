"""Run an explicitly configured coding-agent command without a shell."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any


class CommandAgentAdapter:
    def __init__(self, argv_template: list[str], timeout: float = 3600):
        if not argv_template:
            raise ValueError("argv_template cannot be empty")
        self.argv_template = list(argv_template)
        self.timeout = timeout

    def run(self, workspace: Path, prompt_file: Path) -> dict[str, Any]:
        substitutions = {"workspace": str(workspace), "prompt_file": str(prompt_file)}
        argv = [part.format_map(substitutions) for part in self.argv_template]
        started = time.monotonic()
        completed = subprocess.run(argv, cwd=workspace, text=True, capture_output=True,
                                   timeout=self.timeout, check=False)
        return {"exit_code": completed.returncode, "passed": completed.returncode == 0,
                "elapsed_seconds": round(time.monotonic() - started, 6),
                "stdout": completed.stdout[-8000:], "stderr": completed.stderr[-8000:]}

