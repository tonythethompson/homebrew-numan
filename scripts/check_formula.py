#!/usr/bin/env python3
"""Static + release-archive checks for Formula/numan.rb.

Catches the class of bug where the formula looks for a nested numan-* directory
after Homebrew has already staged into that directory (install must use ./numan).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FORMULA_PATH = REPO_ROOT / "Formula" / "numan.rb"
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render_homebrew_formula.py"
NUMAN_REPO = "tonythethompson/numan"
LINUX_TRIPLE = "x86_64-unknown-linux-gnu"


def fail(message: str) -> None:
    print(f"::error::{message}", file=sys.stderr)
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load_render_mod():
    spec = importlib.util.spec_from_file_location("render_homebrew_formula", RENDER_SCRIPT)
    if spec is None or spec.loader is None:
        fail(f"failed to load {RENDER_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_formula(text: str) -> tuple[str, str]:
    version_match = re.search(r'(?m)^  version "([^"]+)"$', text)
    if not version_match:
        fail('Formula/numan.rb missing version "X.Y.Z" line')
    version = version_match.group(1)

    linux_block = re.search(
        rf'numan-#\{{version\}}-{re.escape(LINUX_TRIPLE)}\.tar\.gz"\s*\n\s*sha256 "([0-9a-f]{{64}})"',
        text,
    )
    if not linux_block:
        fail(f"Formula/numan.rb missing sha256 for {LINUX_TRIPLE}")
    return version, linux_block.group(1).lower()


def check_static_invariants(text: str) -> None:
    required = [
        ('bin.install "numan"', 'must install staged binary with bin.install "numan"'),
        ("no longer ships Intel Mac", "must odie on Intel Mac"),
        ("x86_64-unknown-linux-gnu.tar.gz", "must ship Linux x86_64 URL"),
        ("aarch64-apple-darwin.tar.gz", "must ship macOS arm64 URL"),
    ]
    for needle, reason in required:
        if needle not in text:
            fail(f"Formula/numan.rb {reason}")

    forbidden = [
        ("arch_dir", "must not look for a nested numan-* directory (Homebrew stages into it)"),
        ("expected numan-* directory", "must not look for a nested numan-* directory"),
        ("x86_64-apple-darwin.tar.gz", "must not ship Intel Mac archive URL"),
        ('Dir["numan-*"]', "must not glob nested numan-* dirs after staging"),
    ]
    for needle, reason in forbidden:
        if needle in text:
            fail(f"Formula/numan.rb {reason}: found {needle!r}")


def check_render_roundtrip(version: str) -> None:
    sums_url = f"https://github.com/{NUMAN_REPO}/releases/download/v{version}/SHA256SUMS"
    with urllib.request.urlopen(sums_url, timeout=60) as response:
        sums_text = response.read().decode("utf-8")

    mod = load_render_mod()
    digests = mod.parse_sha256sums(sums_text, version)
    expected = mod.render_formula(version, digests)
    actual = FORMULA_PATH.read_text(encoding="utf-8")
    if actual != expected:
        fail(
            "Formula/numan.rb does not match scripts/render_homebrew_formula.py "
            f"output for v{version} (re-render from SHA256SUMS)"
        )


def check_linux_archive_layout(version: str, expected_sha256: str) -> None:
    asset = f"numan-{version}-{LINUX_TRIPLE}.tar.gz"
    url = f"https://github.com/{NUMAN_REPO}/releases/download/v{version}/{asset}"
    with urllib.request.urlopen(url, timeout=120) as response:
        blob = response.read()

    digest = hashlib.sha256(blob).hexdigest()
    if digest != expected_sha256:
        fail(f"{asset} sha256 mismatch: got {digest}, formula expects {expected_sha256}")

    with tempfile.TemporaryDirectory() as tmp:
        archive_path = Path(tmp) / asset
        archive_path.write_bytes(blob)
        extract_root = Path(tmp) / "extract"
        extract_root.mkdir()
        with tarfile.open(archive_path, "r:gz") as tar:
            # Release archives are trusted first-party assets; still avoid absolute paths.
            members = [m for m in tar.getmembers() if not m.name.startswith("/")]
            try:
                tar.extractall(extract_root, members=members, filter="data")
            except TypeError:
                tar.extractall(extract_root, members=members)

        top = sorted(extract_root.iterdir(), key=lambda p: p.name)
        if len(top) != 1 or not top[0].is_dir():
            fail(
                f"{asset} must contain exactly one top-level directory "
                f"(Homebrew staging contract); found {[p.name for p in top]!r}"
            )

        stage_dir = top[0]
        expected_name = f"numan-{version}-{LINUX_TRIPLE}"
        if stage_dir.name != expected_name:
            fail(f"{asset} top-level dir is {stage_dir.name!r}, expected {expected_name!r}")

        # After Homebrew stages into the sole top-level dir, install sees ./numan.
        staged_binary = stage_dir / "numan"
        if not staged_binary.is_file():
            fail(f"{asset} missing {expected_name}/numan (staged path ./numan would be absent)")
        if not staged_binary.stat().st_mode & 0o111:
            fail(f"{asset} staged binary is not executable: {staged_binary}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Only run static formula checks (no SHA256SUMS / archive download)",
    )
    args = parser.parse_args(argv)

    if not FORMULA_PATH.is_file():
        fail(f"missing {FORMULA_PATH}")

    text = FORMULA_PATH.read_text(encoding="utf-8")
    check_static_invariants(text)
    version, linux_sha = parse_formula(text)
    print(f"Formula version={version} linux_sha256={linux_sha[:12]}…")
    if not args.skip_network:
        check_render_roundtrip(version)
        print("Render roundtrip: ok")
        check_linux_archive_layout(version, linux_sha)
        print("Linux archive staging layout: ok")
    print("check_formula: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
