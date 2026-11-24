# strings

Byte-oriented helpers for UTF-8 text. Every index and length is a byte offset;
searches return -1 when nothing matches. Case helpers (`ToLower`, `ToUpper`,
`EqualFold`) and whitespace helpers (`TrimSpace`, `Fields`, `IsSpace`) are
ASCII-only; use `unicode` for other characters.

- Searching: `Contains`, `ContainsAny`, `ContainsByte`, `HasPrefix`, `HasSuffix`,
  `Index`, `LastIndex`, `IndexByte`, `LastIndexByte`, `IndexAny`, `Count`.
- Splitting and joining: `Split`, `SplitN`, `Fields`, `Lines`, `Cut`, `Join`.
  An empty separator splits into UTF-8 characters; `Split("", sep)` is `[""]`.
- Trimming: `TrimSpace`, `Trim`, `TrimLeft`, `TrimRight`, `TrimPrefix`, `TrimSuffix`.
- Changing: `Replace(text, old, new, limit)` (negative limit replaces all),
  `ReplaceAll`, `Repeat` (panics on a negative count), `ToLower`, `ToUpper`.
- Comparing: `EqualFold`, `Compare`.

`Builder` accumulates text without repeated copying: `WriteString`, `WriteByte`,
`WriteRune` (invalid code points write U+FFFD), `WriteLine`, `Len`, `String`,
`Reset`, `Truncate`. The zero value is ready to use; pass it by pointer.

Run `ocean test strings`.
