# Corpus

| Item | Value |
|---|---|
| Source project | Kubernetes documentation |
| Source repo | https://github.com/kubernetes/website |
| Folders used | `content/en/docs/tasks` and `content/en/docs/concepts/workloads` |
| Commit used | `43374c571c6f1c7b0f23daffb16e401232ea7bf3` |
| License | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| License link | https://github.com/kubernetes/website/blob/43374c571c6f1c7b0f23daffb16e401232ea7bf3/LICENSE |
| Credit / attribution | Kubernetes documentation, copyright The Kubernetes Authors, CC BY 4.0. Files were modified: front matter and Hugo shortcodes removed, paths flattened, six pages converted to HTML/PDF. |
| Files | 235 (md: 229, html: 3, pdf: 3) |
| Approx. words | about 271,000 in text files (PDFs add roughly 10,000) |
| Split | train 144 / val 54 / test 37 (by document, hash of file name) |
| Converted files | HTML: `tasks__configure-pod-container__assign-memory-resource`, `tasks__debug__debug-application__debug-pods`, `tasks__run-application__scale-stateful-set`. PDF: `tasks__configure-pod-container__configure-liveness-readiness-startup-probes`, `tasks__administer-cluster__reserve-compute-resources`, `concepts__workloads__controllers__deployment` |

## Why this corpus
Scanned every section of `content/en/docs` at this commit. `reference` (1,198 files) was rejected: 719 files under 150 words, 442 auto-generated, duplicate API pages. `tasks` is procedural prose with many code blocks and few stubs. `concepts/workloads` adds explanatory prose for multi-chunk and paraphrase questions.

## How it was prepared
1. `git clone --depth 1 https://github.com/kubernetes/website.git` (commit above).
2. `python scripts/prepare_corpus.py kubernetes-docs/content/en/docs corpus/ tasks concepts/workloads`
   - flat unique names (`tasks__debug__debug-pods.md`)
   - front matter removed, page title kept as `# Title`
   - `{{% heading "prerequisites" %}}` turned into real headings; other Hugo shortcodes and HTML comments removed
   - 24 stub pages (under 50 words, mostly empty `_index.md`) skipped
3. Six pages converted with pandoc (HTML) and pandoc + wkhtmltopdf (PDF); their Markdown originals removed so no page exists twice.
4. `python scripts/make_splits.py corpus/` (run once, never changed).

## Known limitations
- Some pages had `{{< include >}}` shortcodes (shared snippets); that text is absent, so a few "Before you begin" sections are empty.
- Code samples loaded via `code_sample` shortcodes (external YAML files) are not in the pages.
- Go templates inside code blocks (`{{range .items}}`) are real content and were kept.

## Rules
- The split is **frozen**. Never move a file between splits.
- Golden questions use **val** and **test** documents only.
- Fine-tuning uses **train** documents only.
- The test split is used **once**, for the final honest score.
