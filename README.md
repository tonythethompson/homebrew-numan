# homebrew-numan

Homebrew tap for [Numan](https://github.com/tonythethompson/numan).

Prefer the explicit HTTPS remote so `brew update` does not depend on SSH
host keys or GitHub SSH auth:

```bash
brew tap tonythethompson/numan https://github.com/tonythethompson/homebrew-numan
brew install numan
```

`brew tap tonythethompson/numan` alone also works when Homebrew clones over
HTTPS (the usual default for public taps).

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

## Troubleshooting

### `Host key verification failed` while updating this tap

`brew update` fetches each tapped repo with git. If this tap was cloned (or
rewritten) to an SSH remote (`git@github.com:...`) and SSH host-key checks
fail, the tap stays stale and installs can keep an old formula.

Recover by switching the tap to HTTPS, then reinstalling:

```bash
brew untap tonythethompson/numan
brew tap tonythethompson/numan https://github.com/tonythethompson/homebrew-numan
brew install tonythethompson/numan/numan
```

Or keep the tap and only fix the remote:

```bash
git -C "$(brew --repo tonythethompson/numan)" remote set-url origin https://github.com/tonythethompson/homebrew-numan.git
brew update
brew reinstall tonythethompson/numan/numan
```

You should see the current formula version (not an older tag such as 0.1.4).
If git still rewrites HTTPS to SSH, check for `url.*.insteadOf` rules:

```bash
git config --global --get-regexp '^url\..*\.insteadof$'
```
