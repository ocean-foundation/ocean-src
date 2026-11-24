#!/usr/bin/env python3
"""Generate internal/native/native.oc: C-ABI bridges written as Ocean assembly.

Run from the repository root: python3 internal/native/generate.py

Each bridge calls one C library or Win32 function on the targets that provide
it. Blocks for other targets are omitted at compile time, so a symbol that
exists only on some platforms is never referenced elsewhere; on targets with
no block (including Wasm) a value-returning bridge returns -1. Every argument and result is a
64-bit integer slot; callers pass pointers as addresses. The calling sequences
match the compiler's own bridges (compiler/util/native.oc).
"""
import os

# name: (argument count, result kind, {platform: symbol}).
# Platforms: linux, macos, windows; "posix" means linux and macos.
# Result kinds: i32 sign-extends a C int, u32 zero-extends a DWORD, i64 keeps
# a full 64-bit value (pointers, handles, ssize_t).
# On x86-64 macOS, stat/lstat/opendir/readdir use the $INODE64 symbols that
# the SDK headers select, so structures use the 64-bit inode layout everywhere.
BRIDGES = {
    # errno and messages
    "ErrnoLocation": (0, "i64", {"linux": "__errno_location", "macos": "__error", "windows": "_errno"}),
    "Strerror": (1, "i64", {"posix": "strerror", "windows": "strerror"}),
    # environment and process
    "Getenv": (1, "i64", {"posix": "getenv"}),
    "Setenv": (3, "i32", {"posix": "setenv"}),
    "Unsetenv": (1, "i32", {"posix": "unsetenv"}),
    "Getpid": (0, "i32", {"posix": "getpid"}),
    "Getcwd": (2, "i64", {"posix": "getcwd"}),
    "Chdir": (1, "i32", {"posix": "chdir"}),
    # files and directories
    "Stat": (2, "i32", {"linux": "stat", "macos": "stat", "macos-x86_64": "stat$INODE64"}),
    "Fstat": (2, "i32", {"posix": "fstat", "macos-x86_64": "fstat$INODE64"}),
    "Lstat": (2, "i32", {"linux": "lstat", "macos": "lstat", "macos-x86_64": "lstat$INODE64"}),
    "Mkdir": (2, "i32", {"posix": "mkdir"}),
    "Openat": (3, "i32", {"posix": "openat"}),
    "Unlinkat": (3, "i32", {"posix": "unlinkat"}),
    "Fdopendir": (1, "i64", {"posix": "fdopendir", "macos-x86_64": "fdopendir$INODE64"}),
    "Rmdir": (1, "i32", {"posix": "rmdir"}),
    "Unlink": (1, "i32", {"posix": "unlink"}),
    "Rename": (2, "i32", {"posix": "rename"}),
    "Chmod": (2, "i32", {"posix": "chmod"}),
    "Opendir": (1, "i64", {"linux": "opendir", "macos": "opendir", "macos-x86_64": "opendir$INODE64"}),
    "Readdir": (1, "i64", {"linux": "readdir", "macos": "readdir", "macos-x86_64": "readdir$INODE64"}),
    "Closedir": (1, "i32", {"posix": "closedir"}),
    "Realpath": (2, "i64", {"linux": "realpath", "macos": "realpath", "macos-x86_64": "realpath$DARWIN_EXTSN"}),
    "Readlink": (3, "i64", {"posix": "readlink"}),
    "Mkdtemp": (1, "i64", {"posix": "mkdtemp"}),
    "Mkstemp": (1, "i32", {"posix": "mkstemp"}),
    "Close": (1, "i32", {"posix": "close"}),
    "MacExecutablePath": (2, "i32", {"macos": "_NSGetExecutablePath"}),
    "Dlsym": (2, "i64", {"macos": "dlsym"}),
    # clocks
    "ClockGettime": (2, "i32", {"posix": "clock_gettime"}),
    # signals
    "Sigemptyset": (1, "i32", {"posix": "sigemptyset"}),
    "Sigaddset": (2, "i32", {"posix": "sigaddset"}),
    "Sigismember": (2, "i32", {"posix": "sigismember"}),
    "PthreadSigmask": (3, "i32", {"posix": "pthread_sigmask"}),
    "Sigtimedwait": (3, "i32", {"linux": "sigtimedwait"}),
    "Sigpending": (1, "i32", {"posix": "sigpending"}),
    "Sigwait": (2, "i32", {"posix": "sigwait"}),
    "MacSignalTryLock": (1, "i32", {"macos": "os_unfair_lock_trylock"}),
    "MacSignalUnlock": (1, "void", {"macos": "os_unfair_lock_unlock"}),
    # Windows (UTF-16 paths and strings)
    "WinGetLastError": (0, "u32", {"windows": "GetLastError"}),
    "WinSetLastError": (1, "void", {"windows": "SetLastError"}),
    "WinGetEnvironmentVariable": (3, "u32", {"windows": "GetEnvironmentVariableW"}),
    "WinSetEnvironmentVariable": (2, "i32", {"windows": "SetEnvironmentVariableW"}),
    "WinGetCurrentProcessId": (0, "u32", {"windows": "GetCurrentProcessId"}),
    "WinGetCurrentDirectory": (2, "u32", {"windows": "GetCurrentDirectoryW"}),
    "WinSetCurrentDirectory": (1, "i32", {"windows": "SetCurrentDirectoryW"}),
    "WinGetModuleFileName": (3, "u32", {"windows": "GetModuleFileNameW"}),
    "WinFullPath": (3, "i64", {"windows": "_wfullpath"}),
    "WinGetTempPath": (2, "u32", {"windows": "GetTempPathW"}),
    "WinGetFileAttributes": (1, "u32", {"windows": "GetFileAttributesW"}),
    "WinCreateDirectory": (2, "i32", {"windows": "CreateDirectoryW"}),
    "WinRemoveDirectory": (1, "i32", {"windows": "RemoveDirectoryW"}),
    "WinDeleteFile": (1, "i32", {"windows": "DeleteFileW"}),
    "WinMoveFileEx": (3, "i32", {"windows": "MoveFileExW"}),
    "WinStat": (2, "i32", {"windows": "_wstat64"}),
    "WinChmod": (2, "i32", {"windows": "_wchmod"}),
    "WinCloseHandle": (1, "i32", {"windows": "CloseHandle"}),
    "WinLocalFree": (1, "i64", {"windows": "LocalFree"}),
    "WinSystemTime": (1, "void", {"windows": "GetSystemTimePreciseAsFileTime"}),
}

X86_SYSV = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
X86_WIN = ["rcx", "rdx", "r8", "r9"]
RISCV = ["a0", "a1", "a2", "a3", "a4", "a5"]

AARCH64_SAVE = """        sub sp, sp, #80
        stp x9, x10, [sp, #16]
        stp x11, x12, [sp, #32]
        stp x13, x14, [sp, #48]
        stp x15, x30, [sp, #64]"""
AARCH64_RESTORE = """        ldp x9, x10, [sp, #16]
        ldp x11, x12, [sp, #32]
        ldp x13, x14, [sp, #48]
        ldp x15, x30, [sp, #64]
        add sp, sp, #80"""
RISCV_SAVE = """        addi sp, sp, -48
        sd ra, 0(sp)
        sd t3, 8(sp)
        sd t4, 16(sp)
        sd t5, 24(sp)
        sd t6, 32(sp)"""
RISCV_RESTORE = """        ld ra, 0(sp)
        ld t3, 8(sp)
        ld t4, 16(sp)
        ld t5, 24(sp)
        ld t6, 32(sp)
        addi sp, sp, 48"""


def quote(symbol):
    return f'"{symbol}"' if "$" in symbol else symbol


def x86_sysv(n, symbol, kind):
    lines = [f"        mov {X86_SYSV[i]}, ${{a{i}}}" for i in range(n)]
    # LLVM's Intel-dialect inline assembly drops '$' from symbol names, so such
    # functions are resolved once with dlsym and called through a pointer.
    target = "qword ptr ${function}" if "$" in symbol else symbol
    lines += ["        xor eax, eax", f"        call {target}"]
    if kind != "void":
        lines.append("        mov ${result}, rax")
    return "\n".join(lines)


def x86_win(n, symbol, kind):
    lines = [f"        mov {X86_WIN[i]}, ${{a{i}}}" for i in range(n)]
    lines += ["        sub rsp, 32", f"        call {symbol}", "        add rsp, 32"]
    if kind == "u32":
        lines.append("        mov eax, eax")
    if kind != "void":
        lines.append("        mov ${result}, rax")
    return "\n".join(lines)


def aarch64(n, symbol, kind):
    lines = [f"        ldr x{i}, ${{a{i}}}" for i in range(n)]
    lines += [AARCH64_SAVE, f"        bl {quote(symbol)}", AARCH64_RESTORE]
    if kind == "u32":
        lines.append("        mov w0, w0")
    if kind != "void":
        lines.append("        str x0, ${result}")
    return "\n".join(lines)


def riscv(n, symbol, kind):
    lines = [f"        ld {RISCV[i]}, ${{a{i}}}" for i in range(n)]
    lines += [RISCV_SAVE, f"        call {symbol}", RISCV_RESTORE]
    if kind != "void":
        lines.append("        sd a0, ${result}")
    return "\n".join(lines)


def symbol_for(symbols, platform, arch):
    key = f"{platform}-{arch}"
    if key in symbols:
        return symbols[key]
    if platform in symbols:
        return symbols[platform]
    if platform in ("linux", "macos") and "posix" in symbols:
        return symbols["posix"]
    return None


def bridge(name, n, kind, symbols):
    params = ", ".join(f"a{i} int" for i in range(n))
    out = []
    indirect = [s for s in symbols.values() if "$" in s]
    scan_local = name == "Readdir"
    if scan_local:
        out += ["func ReaddirFunction() int {", f'    return lookupDarwinX86("{indirect[0]}");', "}", ""]
        params += ", function int"
    result_type = "" if kind == "void" else " int"
    out.append(f"func {name}({params}){result_type} {{")
    if kind != "void":
        out.append("    result := -1;")
    if indirect and not scan_local:
        out += [f'    function := lookupDarwinX86("{indirect[0]}");',
                "    if (function == 0) { SetErrno(78); return -1; }"]  # ENOSYS on Darwin
    targets = [("x86_64", "linux", x86_sysv), ("aarch64", "linux", aarch64), ("riscv64", "linux", riscv),
               ("x86_64", "macos", x86_sysv), ("aarch64", "macos", aarch64),
               ("x86_64", "windows", x86_win), ("aarch64", "windows", aarch64)]
    for arch, platform, emit in targets:
        symbol = symbol_for(symbols, platform, arch)
        if symbol is None:
            continue
        if platform == "macos":
            symbol = "_" + symbol
        if n > 3:
            raise SystemExit(f"{name}: asm blocks allow four operands, so bridges take at most three arguments")
        out.append(f"    asm {arch}/{platform} {{")
        out.append(emit(n, symbol, kind))
        out.append("    }")
    if kind == "i32":
        out.append("    return (result -> i32) -> int;")
    elif kind != "void":
        out.append("    return result;")
    out.append("}")
    return "\n".join(out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parts = [
        "package native;",
        "",
        "// Generated by generate.py; do not edit. C-ABI bridges for the standard",
        "// library: value-returning bridges return -1 when the target lacks the function.",
        "// Arguments and results are 64-bit slots; pass pointers as addresses.",
        "",
    ]
    for name, (n, kind, symbols) in BRIDGES.items():
        parts.append(bridge(name, n, kind, symbols))
        parts.append("")
    with open(os.path.join(here, "native.oc"), "w") as f:
        f.write("\n".join(parts))


main()
