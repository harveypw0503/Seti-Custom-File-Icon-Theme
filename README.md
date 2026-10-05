# harveypw0503-&-Seti-Custom-File-Icon-Theme

VS Code doesn't support "layering" one icon theme on top of another —
only one icon theme is active at a time, and there's no plugin API to
say "use Seti, but add these." So this extension takes the actual
approach that works: it **forks Seti's real theme file and font**,
then extends the mappings. Most every icon you're used to from Seti still
looks exactly the same (with a few niche exceptions); you're only adding what's missing.

Use Ctrl+Shift+P → 'Preferences: File Icon Theme' → harveypw0503+Seti Custom File Icon Theme to enable

## What's in here

- `icons/seti.woff` — Seti's actual icon font, copied byte-for-byte
  from the VS Code repo (MIT licensed — see `THIRD-PARTY-LICENSE-vscode.txt`).
- `icons/my-file-icons-theme.json` — Seti's full theme definition
  (all 380+ of its original icon mappings, untouched), plus:

## Keeping this in sync with upstream Seti

Since this is a fork/snapshot rather than a live layer, if Microsoft
updates Seti's icon set later, your copy won't pick that up
automatically. To refresh the base periodically, re-download
`vs-seti-icon-theme.json` and `seti.woff` from
[microsoft/vscode](https://github.com/microsoft/vscode/tree/main/extensions/theme-seti/icons)
and re-apply your custom `iconDefinitions`/`fileExtensions` additions
on top (keep a note of exactly which keys you added — the list above
is your whole diff).

## Publishing

1. Update `publisher`/`name`/`displayName` in `package.json` to your
   own values.
2. `npm install -g @vscode/vsce`
3. `vsce package` from this folder → produces a `.vsix`.

Since this bundles Seti's font and JSON, keep
`THIRD-PARTY-LICENSE-vscode.txt` in the repo for attribution — Seti
and the rest of VS Code are MIT licensed, so redistribution like this
is fine as long as the license notice travels with it.

## Other Licensing/Notice

Non Seti icons were either found online, modified, or created.