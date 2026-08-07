# homebrew-numan

Homebrew tap for [Numan](https://github.com/tonythethompson/numan).

```bash
brew tap tonythethompson/numan
brew install numan
```

Formula digests are updated automatically by the Numan `Publish to Homebrew tap` workflow after each `v*.*.*` GitHub Release.

## CI

Pull requests and pushes to `master` run:

1. Renderer unit tests (`scripts/test_render_homebrew_formula.py`)
2. Formula static checks + Linux release-archive staging contract (`scripts/check_formula.py`)
3. `brew install` + `brew test` of `Formula/numan.rb` on Linux

Local:

```bash
python3 -m unittest scripts.test_render_homebrew_formula -v
python3 scripts/check_formula.py
```
