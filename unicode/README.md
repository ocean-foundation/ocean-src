# unicode and unicode/utf8

`unicode` classifies code points (held in an `int`) using Unicode 16.0 general
categories: `IsLetter`, `IsUpper`, `IsLower`, `IsTitle`, `IsDigit` (Nd),
`IsNumber` (N*), `IsPunct`, `IsSymbol`, `IsMark`, `IsControl`, `IsPrint`, and
`IsSpace` (the White_Space property). `IsIdentStart` and `IsIdentContinue`
match Ocean's identifier rules; their tables are copied from the compiler.
`ToUpper` and `ToLower` apply one-to-one (simple) case mappings. Invalid code
points have no properties. `MaxRune` and `ReplacementChar` are exported.

To regenerate `tables.oc`, download the matching `UnicodeData.txt` from the
[Unicode Character Database](https://www.unicode.org/Public/16.0.0/ucd/UnicodeData.txt).
From the repository root, run
`python3 unicode/generate_tables.py 16.0.0 UnicodeData.txt > unicode/tables.oc`.
The generator reads identifier tables from the sibling compiler checkout by
default. Pass its `compiler/scanner/unicode.oc` path as a third argument to
use another checkout.

`unicode/utf8` encodes and decodes UTF-8: `Decode(text, offset)` and
`DecodeLast(text)` return a code point and its byte width (invalid input gives
`RuneError` with width 1, end of input width 0), `Encode`, `Len`, `Valid`,
`Count`, `Runes`, and `FromRunes`. Overlong forms, surrogates and values above
U+10FFFF are invalid. Ocean copies string arguments, so `Decode` in a loop over
long text copies it once per call; `Runes`, `Count` and `Valid` decode in one pass.

Run `ocean test unicode unicode/utf8`.
