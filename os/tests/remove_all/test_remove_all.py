"""Run recursive deletion with a low file-descriptor limit on POSIX."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

compiler = Path(sys.argv[1]).resolve()
fixture = Path(__file__).resolve().parent
stdlib = fixture.parents[2]

with tempfile.TemporaryDirectory(prefix="ocean-remove-all-") as temp:
    root = Path(temp)
    binary = root / "remove-all"
    subprocess.run(
        [str(compiler), "build", str(fixture), "-o", str(binary)],
        env=dict(os.environ, OCEAN_SRC=str(stdlib)),
        check=True,
    )
    tree = root / "tree"
    tree.mkdir()
    (tree / "early").touch()
    current = tree
    for _ in range(80):
        current /= "nested"
        current.mkdir()
    (current / "leaf").touch()
    subprocess.run(
        ["/bin/sh", "-c", 'ulimit -n 64 && exec "$@"', "remove-all", str(binary), str(tree)],
        check=True,
        timeout=15,
    )
    assert not tree.exists()
