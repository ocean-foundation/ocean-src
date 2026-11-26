"""Compile the standard library's monotonic clock for every native target."""
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

compiler, clang = (Path(path).resolve() for path in sys.argv[1:])
stdlib = Path(__file__).resolve().parents[3]
targets = (
    ("linux", "x86_64"), ("linux", "aarch64"), ("linux", "riscv64"),
    ("macos", "x86_64"), ("macos", "aarch64"),
    ("windows", "x86_64"), ("windows", "aarch64"),
)
with tempfile.TemporaryDirectory(prefix="ocean-clock-asm-") as tmp:
    root = Path(tmp)
    for system, arch in targets:
        env = dict(os.environ, OCEAN_SRC=str(stdlib), OCEAN_BUILD_CACHE="off",
                   OCOS=system, OCARCH=arch)
        ir = root / "clock.ll"
        subprocess.run([compiler, "build", "--emit-llvm", "-o", ir, stdlib / "time"],
                       env=env, check=True, timeout=60)
        triple = re.search(r'^target triple = "([^"]+)"', ir.read_text(), re.MULTILINE)
        assert triple, (system, arch)
        for optimization in ("-O0", "-O2"):
            subprocess.run([clang, "--target=" + triple[1], optimization,
                            "-Wno-override-module", "-x", "ir", str(ir), "-c",
                            "-o", root / "clock.o"], check=True, timeout=60)
print("All seven monotonic-clock variants assembled at -O0 and -O2")
