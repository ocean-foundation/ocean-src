# internal/native

Private to the standard library; its API can change at any time.

`native.oc` holds C-ABI bridges written as Ocean inline assembly: one function
per C-library or Win32 call, with a block for each target that provides it
(x86-64/AArch64/RISC-V64 Linux, x86-64/AArch64 macOS, x86-64/AArch64 Windows).
Arguments and results are 64-bit slots; pointers are passed as addresses. Where a
target lacks the function, including Wasm, a bridge returns -1. The calling
sequences match the compiler's own bridges.

`native.oc` is generated. Edit the table in `generate.py` and run
`python3 internal/native/generate.py` from the repository root. A bridge takes at
most three arguments (AArch64 and RISC-V asm blocks allow four operands,
including the result). On x86-64 macOS, functions whose symbols contain `$`
(such as `stat$INODE64`) are resolved with `dlsym` and called through a
pointer, because LLVM's Intel-syntax inline assembly drops `$` from symbol
names. Structures therefore use the 64-bit inode layouts on every macOS target.

`helpers.oc` converts strings (C strings and UTF-16 for Win32), reads errno and
its message, and reads native structure fields.

To check a target from a host with Clang, emit and assemble its LLVM IR. For
example, from the directory of a program that imports a native-backed package:

```sh
OCEAN_CROSS_TARGET=aarch64-linux ocean build --emit-llvm -o /tmp/native-aarch64.ll .
clang --target=aarch64-unknown-linux-gnu -c -O1 -x ir /tmp/native-aarch64.ll -o /tmp/native-aarch64.o
```
