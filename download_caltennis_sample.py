"""Download one CalTennis video sample from Hugging Face.

Usage:
    conda activate pose_estimation
    python download_caltennis_sample.py --index 0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


DATASET = "demalenk/caltennis"
BASE_URL = f"https://huggingface.co/datasets/{DATASET}/resolve/main"


def hf_url(path: str) -> str:
    return f"{BASE_URL}/{'/'.join(quote(part) for part in path.split('/'))}"


def download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=120) as response, out_path.open("wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if total:
                pct = done / total * 100
                print(f"\r{done / 1024 / 1024:.1f}/{total / 1024 / 1024:.1f} MB ({pct:.1f}%)", end="")
        if total:
            print()


def load_metadata(split: str, output_dir: Path) -> list[dict]:
    metadata_name = f"metadata_{split}.jsonl"
    metadata_path = output_dir / metadata_name
    if not metadata_path.exists():
        print(f"Downloading {metadata_name}...")
        download(hf_url(metadata_name), metadata_path)

    rows = []
    with metadata_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="mini", choices=["mini", "mid"])
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--output-dir", default="datasets/caltennis")
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    rows = load_metadata(args.split, output_dir)
    if not rows:
        raise RuntimeError(f"No rows found in split: {args.split}")
    if args.index < 0 or args.index >= len(rows):
        raise IndexError(f"--index must be between 0 and {len(rows) - 1}")

    row = rows[args.index]
    video_rel = row["video"]
    video_id = row.get("video_id") or Path(video_rel).stem
    video_path = output_dir / video_rel

    print(f"Selected row: {args.index}/{len(rows) - 1}")
    print(f"Video: {video_rel}")
    print(f"Video id: {video_id}")

    if not args.metadata_only and not video_path.exists():
        print("Downloading video...")
        download(hf_url(video_rel), video_path)

    print()
    print("Use these config.py values:")
    print(f'VIDEO = r"{video_path}"')
    print(f'POSES_NAME = "caltennis_{video_id}"')
    print("FORCE_REEXTRACT = False")


if __name__ == "__main__":
    main()
