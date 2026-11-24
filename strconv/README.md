# strconv

Integer and boolean conversions, and Ocean string quoting.

- `Itoa(n)`, `FormatInt(n, base)`, `FormatUint(n, base)` format in bases 2–36
  (lower-case digits). An invalid base panics.
- `Atoi(text)`, `ParseInt(text, base)`, `ParseUint(text, base)` return `Result`s.
  They accept an optional sign (not for `ParseUint`) and digits of either case,
  and reject empty text, prefixes such as `0x`, separators, spaces, and values
  outside 64 bits.
- `ParseBool` accepts exactly `true`/`false`; `FormatBool` produces them.
- `Quote(text)` returns a double-quoted Ocean literal, escaping `"`, `\`, `\n`,
  `\t`, `\r` and other control bytes as `\xHH`; UTF-8 is kept as is.
  `Unquote(literal)` accepts every Ocean string escape (`\a \b \e \f \n \r \t \v`,
  octal, `\xHH`, `\uHHHH`, `\UHHHHHHHH`).

`io.ParseInt` and `io.ParseFloat` remain the base-10 and float parsers.
Run `ocean test strconv`.
