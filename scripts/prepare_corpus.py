"""Build corpus/ from one or more docs folders with UNIQUE flat file names.

    python scripts/prepare_corpus.py <docs_root> corpus/ <subfolder> [<subfolder> ...]

Example (Kubernetes website repo):
    python scripts/prepare_corpus.py kubernetes-docs/content/en/docs corpus/ tasks concepts/workloads

What it does to every Markdown file:
  1. Flattens the path:  tasks/debug/index.md -> tasks__debug__index.md
  2. Removes the YAML front matter (--- ... --- block at the top), but keeps
     the page title as a "# Title" heading so the parser finds a title.
  3. Turns {{% heading "prerequisites" %}} into a real heading, drops HTML comments, and
     removes other Hugo shortcodes such as {{< note >}} ... {{< /note >}} and
     {{% code_sample file="x.yaml" %}}. The text inside note/caution blocks stays.
  4. Skips stub pages (fewer than MIN_WORDS words of body text), e.g. empty _index.md.
"""
import pathlib
import re
import sys

MIN_WORDS = 50
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
TITLE = re.compile(r"^title:\s*[\"']?(.*?)[\"']?\s*$", re.M)
HEADING_SC = re.compile(r"\{\{[<%]\s*heading\s+[\"']?(\w+)[\"']?\s*[>%]\}\}")
HEADING_NAMES = {
    "prerequisites": "Before you begin",
    "whatsnext": "What's next",
    "cleanup": "Cleaning up",
    "objectives": "Objectives",
    "body": "Overview",
}
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
EMPTY_HEADING = re.compile(r"^#{1,6}[ \t]*$", re.M)
SHORTCODE = re.compile(r"\{\{[<%].*?[>%]\}\}", re.S)
BLANKS = re.compile(r"\n{3,}")


def clean(raw: str) -> str:
    title = None
    m = FRONT_MATTER.match(raw)
    if m:
        t = TITLE.search(m.group(1))
        title = t.group(1).strip() if t else None
        raw = raw[m.end():]
    raw = HEADING_SC.sub(lambda m: HEADING_NAMES.get(m.group(1), m.group(1).capitalize()), raw)
    raw = HTML_COMMENT.sub("", raw)
    body = SHORTCODE.sub("", raw)
    body = EMPTY_HEADING.sub("", body)
    body = BLANKS.sub("\n\n", body).strip()
    if title and not re.match(r"^#\s", body):
        body = f"# {title}\n\n{body}"
    return body + "\n"


def main(root: str, dst: str, subfolders: list[str]) -> None:
    base, target = pathlib.Path(root), pathlib.Path(dst)
    target.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    for sub in subfolders:
        source = base / sub
        for path in sorted(source.rglob("*.md")):
            text = clean(path.read_text(encoding="utf-8", errors="ignore"))
            body_words = len(re.sub(r"^#.*$", "", text, flags=re.M).split())
            if body_words < MIN_WORDS:
                skipped += 1
                continue
            flat = "__".join(path.relative_to(base).parts)
            (target / flat).write_text(text, encoding="utf-8")
            copied += 1
    print(f"copied {copied} files, skipped {skipped} stubs -> {target}/")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
