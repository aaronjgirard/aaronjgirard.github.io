#!/usr/bin/env python3
"""
hide_unlisted.py — keep unlisted pages out of the rendered sitemap and search.

A page is unlisted when its front matter has `unlisted: true`. Such pages are
reachable only by their URL (e.g. a poster QR code): this post-render hook drops
them from docs/sitemap.xml and docs/search.json. Pair it with `search: false`
and a robots noindex meta tag in the page itself.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "docs"


def unlisted_pages():
    pages = []
    for qmd in ROOT.glob("*.qmd"):
        head = re.match(r"^---\n(.*?)\n---", qmd.read_text(), re.S)
        if head and re.search(r"^unlisted:\s*true\s*$", head.group(1), re.M):
            pages.append(qmd.stem + ".html")
    return pages


def main():
    pages = unlisted_pages()
    if not pages:
        return 0
    smap = OUT / "sitemap.xml"
    if smap.exists():
        xml = smap.read_text()
        for p in pages:
            xml = re.sub(r"\s*<url>\s*<loc>[^<]*/%s</loc>.*?</url>" % re.escape(p), "", xml, flags=re.S)
        smap.write_text(xml)
    srch = OUT / "search.json"
    if srch.exists():
        rec = json.loads(srch.read_text())
        rec = [r for r in rec if r.get("href", "").split("#")[0] not in pages]
        srch.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    print("hide_unlisted: kept out of sitemap and search: %s" % ", ".join(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
