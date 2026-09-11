from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "build_edc_corpus_index.py"
SPEC = importlib.util.spec_from_file_location("build_edc_corpus_index", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
edc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(edc)


def write_note(
    root: Path,
    date: str,
    name: str,
    *,
    note_id: str,
    source: str,
    url: str,
    body: str,
    author: str = "Fixture Author",
) -> Path:
    directory = root / date
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        "\n".join(
            [
                "---",
                f"author: {author}",
                f"source: {source}",
                f"url: {url}",
                f"saved: {date} 12:34:56",
                f"id: {note_id}",
                "---",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def fixture_expectations() -> dict:
    return {
        "sourceCount": 2,
        "platformCounts": {"xiaohongshu": 1, "douyin": 1},
        "readableUniqueImageCount": 3,
        "missingImageReferenceCount": 1,
    }


class EdcCorpusIndexTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[Path, Path]:
        images = root / "images"
        images.mkdir(parents=True)
        Image.new("RGB", (48, 32), (210, 20, 30)).save(images / "a.png")
        Image.new("RGB", (32, 48), (20, 210, 30)).save(images / "b.png")
        Image.new("RGB", (40, 40), (20, 30, 210)).save(images / "c space.png")

        xhs = write_note(
            root,
            "2026-09-01",
            "fixture-xhs.md",
            note_id="11111111-1111-4111-8111-111111111111",
            source="AI整理 - 小红书",
            url=(
                "https://www.xiaohongshu.com/discovery/item/abc123"
                "?xsec_token=tracking&share_id=also-tracking&type=video"
            ),
            body=(
                "# EDC fixture spinner\n"
                "![[笔记同步助手/images/a.png|frame]]\n"
                "[[龙鳞（NOVO EDC）分镜与3D生成规范]]"
            ),
        )
        write_note(
            root,
            "2026-09-01",
            "fixture-douyin.md",
            note_id="22222222-2222-4222-8222-222222222222",
            source="AI整理 - 抖音",
            url="https://v.douyin.com/ShortToken/?share=tracking",
            body=(
                "# 解压玩具 fixture\n"
                "![frame](<../images/b.png>)\n"
                '<img src="../images/c%20space.png">\n'
                "![[笔记同步助手/images/missing.png|missing]]"
            ),
        )
        derived = root / "2026-09-01" / "龙鳞（NOVO EDC）分镜与3D生成规范.md"
        derived.write_text("# assistant-derived only\n", encoding="utf-8")

        # These paths must never be traversed by the date-only scanner.
        secret = root / ".obsidian" / "plugins" / "fixture" / "secrets.md"
        secret.parent.mkdir(parents=True)
        secret.write_text("DO_NOT_INDEX_API_KEY=fixture-secret", encoding="utf-8")
        nested = root / "2026-09-01" / "nested" / "ignored.md"
        nested.parent.mkdir()
        nested.write_text("DO_NOT_INDEX_NESTED", encoding="utf-8")
        return xhs, secret

    def test_true_dct_phash_has_stable_known_vectors(self) -> None:
        constant = Image.new("L", (64, 64), 128)
        self.assertEqual(edc.phash_dct64(constant), "8000000000000000")

        yy, xx = np.mgrid[0:32, 0:32]
        pattern = ((xx * 7 + yy * 13 + (xx * yy) % 17) % 256).astype(np.uint8)
        patterned = Image.fromarray(pattern)
        self.assertEqual(edc.phash_dct64(patterned), "88b38c376ce12d5b")
        self.assertEqual(edc.phash_dct64(patterned.copy()), edc.phash_dct64(patterned))

    def test_builds_deterministic_index_without_reading_private_trees(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "笔记同步助手"
            _, secret = self.make_fixture(root)
            first = edc.build_index(
                root,
                expectations=fixture_expectations(),
                baseline_policies={},
            )
            second = edc.build_index(
                root,
                previous=first,
                expectations=fixture_expectations(),
                baseline_policies={},
            )

            self.assertEqual(edc.serialize_index(first), edc.serialize_index(second))
            self.assertEqual(first["acceptance"]["status"], "pass")
            self.assertEqual(first["summary"]["sourceCount"], 2)
            self.assertEqual(first["summary"]["readableUniqueImageCount"], 3)
            self.assertEqual(first["summary"]["missingImageReferenceCount"], 1)
            self.assertEqual(first["selectionAudit"]["markdownFilesScanned"], 3)
            self.assertTrue(secret.is_file())
            self.assertNotIn("fixture-secret", edc.serialize_index(first))
            self.assertNotIn("DO_NOT_INDEX_NESTED", edc.serialize_index(first))

            by_platform = {source["platform"]: source for source in first["sources"]}
            self.assertEqual(
                by_platform["xiaohongshu"]["canonicalUrl"],
                "https://www.xiaohongshu.com/discovery/item/abc123",
            )
            self.assertEqual(
                by_platform["douyin"]["canonicalUrl"],
                "https://v.douyin.com/ShortToken/",
            )
            self.assertEqual(
                by_platform["douyin"]["resumeCheckpoint"]["state"],
                "blocked-missing-local-image",
            )
            self.assertEqual(
                by_platform["xiaohongshu"]["relatedDerivedNotes"][0]["classification"],
                "ai-target",
            )
            for source in first["sources"]:
                for image in source["images"]:
                    if image["status"] == "readable":
                        self.assertRegex(image["pHashDct64"], r"^[0-9a-f]{16}$")
                        self.assertEqual(
                            image["pHashAlgorithm"],
                            "dct-ii-32x32-low8x8-median64-v1",
                        )

    def test_check_mode_detects_note_drift_and_never_writes_the_vault(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "笔记同步助手"
            xhs, _ = self.make_fixture(root)
            output = Path(temporary) / "out" / "corpus-index.json"
            common = [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--vault-root",
                str(root),
                "--output",
                str(output),
                "--expected-source-count",
                "2",
                "--expected-xhs-count",
                "1",
                "--expected-douyin-count",
                "1",
                "--expected-readable-images",
                "3",
                "--expected-missing-images",
                "1",
                "--strict-acceptance",
            ]
            built = subprocess.run(common, capture_output=True, text=True, check=False)
            self.assertEqual(built.returncode, 0, built.stderr)
            current = subprocess.run(
                common + ["--check"], capture_output=True, text=True, check=False
            )
            self.assertEqual(current.returncode, 0, current.stderr)

            xhs.write_text(xhs.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
            stale = subprocess.run(
                common + ["--check"], capture_output=True, text=True, check=False
            )
            self.assertEqual(stale.returncode, 1)
            self.assertIn("index is stale", stale.stderr)

            refused = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--vault-root",
                    str(root),
                    "--output",
                    str(root / "must-not-write.json"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(refused.returncode, 2)
            self.assertFalse((root / "must-not-write.json").exists())


if __name__ == "__main__":
    unittest.main()
