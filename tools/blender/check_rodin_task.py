#!/usr/bin/env python3
"""Poll a Rodin task once and download its deliverables when complete."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import requests

from submit_rodin_direct import read_free_trial_key


BASE_URL = "https://hyperhuman.deemos.com/api/v2"


def safe_name(value: str, fallback: str) -> str:
    name = Path(value).name or fallback
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file")
    parser.add_argument("--download-dir")
    args = parser.parse_args()

    task_file = Path(args.task_file).resolve()
    task = json.loads(task_file.read_text(encoding="utf-8"))
    headers = {"Authorization": f"Bearer {read_free_trial_key()}"}
    response = requests.post(
        f"{BASE_URL}/status",
        headers=headers,
        json={"subscription_key": task["jobs"]["subscription_key"]},
        timeout=(20, 60),
    )
    response.raise_for_status()
    status_payload = response.json()
    statuses = [job.get("status") for job in status_payload.get("jobs", [])]
    print(json.dumps({"statuses": statuses}, ensure_ascii=False))

    if not statuses or any(status in {"Failed", "Canceled"} for status in statuses):
        return 2
    if not all(status == "Done" for status in statuses):
        return 3
    if not args.download_dir:
        return 0

    download_response = requests.post(
        f"{BASE_URL}/download",
        headers=headers,
        json={"task_uuid": task["uuid"]},
        timeout=(20, 60),
    )
    download_response.raise_for_status()
    download_payload = download_response.json()
    output_dir = Path(args.download_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for index, item in enumerate(download_payload.get("list", [])):
        url = item["url"]
        filename = safe_name(item.get("name") or url, f"rodin_asset_{index}")
        destination = output_dir / filename
        with requests.get(url, stream=True, timeout=(20, 180)) as asset_response:
            asset_response.raise_for_status()
            with destination.open("wb") as output:
                for chunk in asset_response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
        written.append(str(destination))
    print(json.dumps({"downloaded": written}, ensure_ascii=False, indent=2))
    return 0 if written else 4


if __name__ == "__main__":
    raise SystemExit(main())
