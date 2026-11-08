import io
import json
import runpy
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

UPDATER = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts" / "update-versions.py")
)
LOAD = UPDATER["load_versions"]
UPDATE = UPDATER["update_plugin"]


def release(tag, day, *, draft=False, complete=True):
    names = sorted(UPDATER["ASSETS"])
    return {
        "tag_name": tag,
        "published_at": f"2026-11-{day:02d}T00:00:00Z" if not draft else None,
        "draft": draft,
        "prerelease": True,
        "assets": [
            {"name": name, "state": "uploaded"}
            for name in (names if complete else names[:-1])
        ],
    }


class ReleaseUpdatesTest(unittest.TestCase):
    def responses(self, pages):
        responses = [io.BytesIO(json.dumps(page).encode()) for page in pages]
        return patch.dict(
            LOAD.__globals__,
            {
                "urlopen": Mock(side_effect=responses),
            },
        )

    def test_loads_complete_alphas_across_pages_despite_older_tag_formats(self):
        with self.responses(
            [
                [release("alpha-22", 8), release("v0.9.0", 1)],
                [
                    release("alpha-9", 2),
                    release("alpha-23", 9, complete=False),
                    release("v1.0.0", 10, draft=True),
                    release("alpha-22", 8),
                ],
                [],
            ]
        ):
            self.assertEqual(LOAD(), ["0.9.0", "0.22.0"])

    def test_new_non_alpha_release_stops_before_writing(self):
        for tag in ("1.0.0", "v1.0.0", "beta-1", "new-release-format"):
            with self.subTest(tag=tag), tempfile.TemporaryDirectory() as directory:
                plugin = Path(directory) / "porffor.toml"
                original = '[source]\nversions = ["0.22.0"]\n'
                plugin.write_text(original)
                with (
                    self.responses(
                        [
                            [release(tag, 9)],
                            [release("alpha-22", 8)],
                            [],
                        ]
                    ),
                    self.assertRaisesRegex(
                        ValueError, "Automatic updates are paused"
                    ),
                ):
                    UPDATE(plugin, LOAD())
                self.assertEqual(plugin.read_text(), original)

    def test_non_alpha_without_alpha_history_stops(self):
        with (
            self.responses([[release("v1.0.0", 9)], []]),
            self.assertRaisesRegex(ValueError, "Automatic updates are paused"),
        ):
            LOAD()

    def test_bad_or_empty_response_fails(self):
        for response, error in (({}, TypeError), ([], ValueError)):
            with (
                self.subTest(response=response),
                self.responses([response]),
                self.assertRaises(error),
            ):
                LOAD()

    def test_update_preserves_versions_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / "porffor.toml"
            plugin.write_text('[source]\nversions = ["0.9.0", "0.22.0"]\n')
            UPDATE(plugin, ["0.10.0", "0.23.0", "0.23.0"])
            self.assertEqual(
                tomllib.loads(plugin.read_text())["source"]["versions"],
                ["0.9.0", "0.10.0", "0.22.0", "0.23.0"],
            )
            before = plugin.read_bytes()
            UPDATE(plugin, ["0.23.0"])
            self.assertEqual(plugin.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
