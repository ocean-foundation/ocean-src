#!/usr/bin/env python3
"""Deliver real signals to a blocked Ocean process; set OCEAN to the compiler."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def main():
    if not (sys.platform.startswith("linux") or sys.platform == "darwin"):
        print("skipped: POSIX signals only")
        return
    compiler = os.environ.get("OCEAN", shutil.which("ocean"))
    assert compiler, "set OCEAN to the matching compiler"
    with tempfile.TemporaryDirectory(prefix="ocean-signal-") as directory:
        executable = str(Path(directory) / "signals")
        env = dict(os.environ, OCEAN_SRC=str(ROOT))
        subprocess.run([compiler, "build", str(Path(__file__).parent), "-o", executable], env=env, check=True)
        child = subprocess.Popen([executable], stdout=subprocess.PIPE, text=True)
        assert child.stdout.readline().strip() == "ready"
        child.send_signal(signal.SIGTERM)
        assert child.stdout.readline().strip() == "SIGTERM"
        child.send_signal(signal.SIGINT)
        assert child.stdout.readline().strip() == "SIGINT"
        assert child.wait(timeout=10) == 0, "blocked signals should not end the process"
    print("ok")


main()
