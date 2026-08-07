# homebrew-numan

Homebrew tap for [Numan](https://github.com/tonythethompson/numan).

```bash
brew tap tonythethompson/numan
brew install numan
```

## Platforms

| Platform | Status |
|----------|--------|
| macOS Apple Silicon (`aarch64-apple-darwin`) | shipped |
| Linux x86_64 (`x86_64-unknown-linux-gnu`) | shipped |
| Linux ARM64 (`aarch64-unknown-linux-gnu`) | formula support ready; bottle URLs appear on the next numan release that publishes that archive |
| macOS Intel | not shipped (`odie` with cargo install hint) |

Formula digests are updated automatically by the Numan `Publish to Homebrew tap`
workflow (and this repo's `Update numan formula` workflow) after each `v*.*.*`
GitHub Release. Pre-Linux-ARM tags re-render with `--legacy-pre-linux-arm`.

## CI

Pull requests and pushes to `master` run:

1. Renderer unit tests (`scripts/test_render_homebrew_formula.py`)
2. Formula static checks + Linux release-archive staging contract (`scripts/check_formula.py`)
3. `brew install tonythethompson/numan/numan` + `brew test` on Linux

Local:

```bash
python3 -m unittest scripts.test_render_homebrew_formula -v
python3 scripts/check_formula.py
```
