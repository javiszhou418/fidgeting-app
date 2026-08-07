#!/usr/bin/env python3
"""Submit a compact multiview Rodin job without base64-encoding over Blender MCP.

This is a narrow fallback for Blender MCP's 180-second socket timeout.  It reads
the API key already configured by the installed Blender add-on and never prints
that credential.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import re

import requests


ADDON_PATH = Path(
    "/Users/jiawei.zhou/Library/Application Support/Blender/5.2/scripts/addons/addon.py"
)
ENDPOINT = "https://hyperhuman.deemos.com/api/v2/rodin"


def read_free_trial_key() -> str:
    source = ADDON_PATH.read_text(encoding="utf-8")
    match = re.search(r'^RODIN_FREE_TRIAL_KEY\s*=\s*[\"\']([^\"\']+)[\"\']', source, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find Blender MCP's configured Rodin free-trial key")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    image_paths = [Path(value).resolve() for value in args.images]
    if not all(path.is_file() for path in image_paths):
        raise FileNotFoundError("One or more Rodin reference images do not exist")

    with ExitStack() as stack:
        files: list[tuple[str, tuple[str | None, object]]] = []
        for path in image_paths:
            handle = stack.enter_context(path.open("rb"))
            files.append(("images", (path.name, handle, "image/jpeg")))
        files.extend(
            [
                ("tier", (None, "Sketch")),
                ("mesh_mode", (None, "Raw")),
                ("texture_mode", (None, "high")),
                ("bbox_condition", (None, json.dumps([100, 100, 18]))),
                (
                    "prompt",
                    (
                        None,
                        "Faithful multiview reconstruction of the same compact Dragon Scale EDC "
                        "spinner: curved three-lobed rotor, sculpted triangular recesses, large "
                        "faceted circular finger caps, visible bearing stack, thin tapered profile.",
                    ),
                ),
            ]
        )
        response = requests.post(
            ENDPOINT,
            headers={"Authorization": f"Bearer {read_free_trial_key()}"},
            files=files,
            timeout=(30, 300),
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Rodin returned HTTP {response.status_code} with non-JSON body") from exc

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "http_status": response.status_code,
        "error": payload.get("error"),
        "message": payload.get("message"),
        "task_uuid": payload.get("uuid"),
        "subscription_key": (payload.get("jobs") or {}).get("subscription_key"),
        "response_file": str(output_path),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if response.ok and summary["task_uuid"] and summary["subscription_key"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
