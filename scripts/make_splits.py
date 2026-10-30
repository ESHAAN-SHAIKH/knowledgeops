"""Split the corpus into train / val / test BY DOCUMENT (never by chunk).

    python scripts/make_splits.py corpus/

Writes evals/datasets/doc_splits.json. The split depends only on the file name
(a hash), so adding new files later never moves existing files to another split.
Run it ONCE, commit the result, and never change it.
"""
import hashlib
import json
import pathlib
import sys

KEEP = {".md", ".html", ".pdf", ".txt"}
OUT = pathlib.Path("evals/datasets/doc_splits.json")


def bucket(name: str) -> str:
    n = int(hashlib.sha256(name.encode()).hexdigest(), 16) % 100
    if n < 60:
        return "train"
    if n < 80:
        return "val"
    return "test"


def main(corpus: str) -> None:
    root = pathlib.Path(corpus)
    names = sorted(p.name for p in root.iterdir() if p.suffix.lower() in KEEP)
    if len(names) != len(set(names)):
        raise SystemExit("File names are not unique. Run prepare_corpus.py first.")
    splits: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    for name in names:
        splits[bucket(name)].append(name)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(splits, indent=2))
    words = sum(len(p.read_text(errors="ignore").split()) for p in root.iterdir()
                if p.suffix.lower() in {".md", ".html", ".txt"})
    print(f"{len(names)} files, about {words:,} words (text files only)")
    for key, files in splits.items():
        print(f"  {key}: {len(files)} files")
    print(f"saved {OUT}")


if __name__ == "__main__":
    main(sys.argv[1])
