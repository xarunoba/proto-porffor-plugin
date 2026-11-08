#!/usr/bin/env python3
"""Refresh the declarative plugin from published Porffor alpha releases."""

import json
import os
import re
import tomllib
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

RELEASES = "https://api.github.com/repos/CanadaHonk/porffor/releases"
PLUGIN = Path(__file__).resolve().parents[1] / "porffor.toml"
ASSETS = {
    f"porffor-{target}.tar.gz"
    for target in (
        "linux-x64",
        "linux-arm64",
        "linux-x64-musl",
        "linux-arm64-musl",
        "darwin-x64",
        "darwin-arm64",
    )
}


def load_versions():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "proto-porffor-plugin",
    }
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    numbers = set()
    latest_alpha = None
    latest_other = None
    page = 1
    while True:
        request = Request(f"{RELEASES}?per_page=100&page={page}", headers=headers)
        with urlopen(request, timeout=30) as response:
            releases = json.load(response)
        if not isinstance(releases, list):
            raise TypeError("Expected a GitHub releases array")
        if not releases:
            break
        for release in releases:
            if release["draft"]:
                continue
            tag = release["tag_name"]
            published = datetime.fromisoformat(release["published_at"])
            match = re.fullmatch(r"alpha-([1-9][0-9]*)", tag)
            if not match:
                if latest_other is None or published > latest_other[0]:
                    latest_other = (published, tag)
                continue
            if latest_alpha is None or published > latest_alpha:
                latest_alpha = published
            assets = {
                asset["name"]
                for asset in release["assets"]
                if asset["state"] == "uploaded"
            }
            if ASSETS <= assets:
                numbers.add(int(match[1]))
        page += 1
    if latest_other is not None and (
        latest_alpha is None or latest_other[0] >= latest_alpha
    ):
        raise ValueError(
            f"Release {latest_other[1]!r} is newer than the alpha release series. "
            "Automatic updates are paused. Review upstream versioning and assets, "
            "then update version mapping and download URLs before resuming."
        )
    if not numbers:
        raise ValueError("No published alpha releases with all supported assets found")
    return [f"0.{number}.0" for number in sorted(numbers)]


def update_plugin(path, versions):
    text = path.read_text()
    current = tomllib.loads(text)["source"]["versions"]
    # Preserve previously published versions if upstream deletes a release.
    versions = sorted(
        set(current) | set(versions),
        key=lambda version: tuple(map(int, version.split("."))),
    )
    replacement = (
        "versions = [\n" + "".join(f'    "{version}",\n' for version in versions) + "]"
    )
    updated, count = re.subn(r"(?m)^versions = \[[^\]]*\]", replacement, text)
    if count != 1:
        raise ValueError("Expected exactly one versions array")
    assert tomllib.loads(updated)["source"]["versions"] == versions
    if updated != text:
        temporary = path.with_suffix(".toml.tmp")
        temporary.write_text(updated)
        temporary.replace(path)
        print(f"Updated {path.name}; latest is {versions[-1]}")
    else:
        print(f"No changes; latest is {versions[-1]}")


if __name__ == "__main__":
    update_plugin(PLUGIN, load_versions())
