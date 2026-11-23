# path

Lexical path manipulation for the target platform; nothing touches the file
system. Results use `/`. On Windows `\` is also a separator, and drive (`C:/`)
and UNC (`//server/share`) roots are recognized; drive letters and names compare
case-insensitively in `Rel`.

`Join(parts...)`, `Clean`, `Base`, `Dir`, `Ext`, `Split`, `IsAbs`, `ToSlash`,
`FromSlash`, `Rel(base, target) Result<string>` (both absolute or both relative,
on one volume), and `Abs(path) Result<string>` (joins the working directory;
links are not resolved — use `os.Realpath`).

The Windows rules are tested on every host through the package's internal
functions. Run `ocean test path`.
