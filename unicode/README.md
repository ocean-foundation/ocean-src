# unicode and unicode/utf8

`unicode` classifies code points (held in an `int`) using Unicode 16.0 general
categories: `IsLetter`, `IsUpper`, `IsLower`, `IsTitle`, `IsDigit` (Nd),
`IsNumber` (N*), `IsPunct`, `IsSymbol`, `IsMark`, `IsControl`, `IsPrint`, and
`IsSpace` (the White_Space property). `IsIdentStart` and `IsIdentContinue`
match Ocean's identifier rules; their tables are copied from the compiler.
`ToUpper` and `ToLower` apply one-to-one (simple) case mappings. Invalid code
points have no properties. `MaxRune` and `ReplacementChar` are exported.

`tables.oc` is generated: run `python3 unicode/generate_tables.py > unicode/tables.oc`
from the repository root with a Python whose `unicodedata` matches the intended
Unicode version and the compiler checkout as a sibling (or pass its
`compiler/scanner/unicode.oc` path as an argument).

`unicode/utf8` encodes and decodes UTF-8: `Decode(text, offset)` and
`DecodeLast(text)` return a code point and its byte width (invalid input gives
`RuneError` with width 1, end of input width 0), `Encode`, `Len`, `Valid`,
`Count`, `Runes`, and `FromRunes`. Overlong forms, surrogates and values above
U+10FFFF are invalid. Ocean copies string arguments, so `Decode` in a loop over
long text copies it once per call; `Runes`, `Count` and `Valid` decode in one pass.

Run `ocean test unicode unicode/utf8`.
