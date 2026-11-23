# runtime

Identifies the compilation target: `OS()` is `linux`, `macos`, `windows`, or
`js`; `Arch()` is `x86_64`, `aarch64`, `riscv64`, or `wasm`. `Linux()`,
`MacOS()`, `Windows()`, `Wasm()`, `ExeSuffix()`, `PathSeparator()` and
`PathListSeparator()` are derived from them. Native values come from target-
selected assembly blocks (`runtime_native.oc`), so they cost a constant store and
cannot be changed by the environment; `runtime_wasm.oc` serves Wasm.

Other standard-library packages use this instead of private detection code.
Run `ocean test runtime`.
