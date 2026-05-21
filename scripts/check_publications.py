#!/usr/bin/env python3
"""
check_publications.py — keep publications.qmd and collaborators.qmd in sync.

Scans both files and reports:
  - anchors in publications.qmd with no matching key in PUBLICATIONS  (new papers)
  - PUBLICATIONS keys with no anchor in publications.qmd               (orphan map entries)
  - COAUTHORS .papers references pointing to unknown PUBLICATIONS keys (typos)
  - for each new paper: the URL Claude needs to fetch, or a warning that
    the link is a PDF / Drive / files/ entry that will not parse cleanly

Workflow when this script reports a missing entry:
  1. WebFetch the URL to pull authors and affiliations.
  2. For each author, match against existing COAUTHORS by last name + first
     initial. If matched, append the new pubid to that person's .papers.
     If not matched, flag for human input — the affiliation must be mapped
     to an INSTITUTIONS key (or a new institution added) before insertion.
  3. Add a new PUBLICATIONS entry with year + short label.

Exit code is 0 when everything is consistent and 1 when anything is missing,
so this can also be wired in as a pre-commit or pre-render hook.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB_FILE   = ROOT / "publications.qmd"
COLL_FILE  = ROOT / "collaborators.qmd"

## URL hosts where WebFetch will return clean HTML metadata
FETCHABLE = (
    "doi.org", "academic.oup.com", "library.seg.org", "onlinelibrary.wiley.com",
    "sciencedirect.com", "mdpi.com", "seismica.library.mcgill.ca",
    "eartharxiv.org", "agu.confex.com", "earthdoc.org",
    "research-repository.uwa.edu.au",
)
## URL patterns that will NOT parse cleanly (PDF / Drive / local file)
UNFETCHABLE = ("files/", "drive.google.com", ".pdf", "osti.gov")


def parse_publications_qmd(text):
    """Return list of dicts: {pubid, url, line, in_review}."""
    entries = []
    ## match [ id ]{ #pubid } followed by the rest of the list-item line
    anchor_re = re.compile(r"\[\]\{#([a-zA-Z0-9_]+)\}(.+)")
    ## first markdown link `[Title](URL)` after the anchor; URL is group 1
    link_re   = re.compile(r"\[[^\]]+\]\((https?://[^\)\s]+|files/[^\)\s]+)\)")
    for raw in text.splitlines():
        m = anchor_re.search(raw)
        if not m:
            continue
        pubid, rest = m.group(1), m.group(2)
        link = link_re.search(rest)
        url  = link.group(1) if link else None
        in_review = "in review" in rest.lower()
        entries.append({
            "pubid"     : pubid,
            "url"       : url,
            "in_review" : in_review,
            "line"      : raw.strip(),
        })
    return entries


def parse_collaborators_qmd(text):
    """Return (publication_keys, coauthor_paper_refs)."""
    ## PUBLICATIONS dict entries:  <key>: { year: <n>, label: "..."
    pub_re = re.compile(r"^\s*([a-zA-Z0-9_]+)\s*:\s*\{\s*year:\s*\d+\s*,\s*label:", re.M)
    pub_keys = set(pub_re.findall(text))

    ## COAUTHORS .papers lists: papers: [ "id1","id2", ... ]
    paper_re = re.compile(r"papers:\s*\[([^\]]*)\]", re.S)
    refs = set()
    for block in paper_re.findall(text):
        for tok in re.findall(r'"([a-zA-Z0-9_]+)"', block):
            refs.add(tok)
    return pub_keys, refs


def fetchability(url):
    if url is None:
        return "no link"
    if any(p in url for p in UNFETCHABLE):
        return "PDF / Drive  -  WebFetch will not return clean HTML; affiliations must be entered manually"
    if any(h in url for h in FETCHABLE):
        return "fetchable"
    return "unknown host  -  try WebFetch but verify output"


def main():
    pub_text  = PUB_FILE.read_text()
    coll_text = COLL_FILE.read_text()

    pub_entries = parse_publications_qmd(pub_text)
    pub_anchor_ids = {e["pubid"] for e in pub_entries}
    pub_keys, paper_refs = parse_collaborators_qmd(coll_text)

    missing_in_map      = sorted(pub_anchor_ids - pub_keys)   # new papers, need map entry
    orphan_in_map       = sorted(pub_keys - pub_anchor_ids)   # map entry with no anchor
    unknown_paper_refs  = sorted(paper_refs - pub_keys)       # typo in someone's .papers

    print("=" * 70)
    print(f"  publications.qmd     : {len(pub_anchor_ids)} anchored entries")
    print(f"  collaborators.qmd    : {len(pub_keys)} PUBLICATIONS keys, {len(paper_refs)} unique .papers refs")
    print("=" * 70)

    problems = 0

    if missing_in_map:
        problems += len(missing_in_map)
        print(f"\nNEW PAPERS  -  add to PUBLICATIONS dict in collaborators.qmd ({len(missing_in_map)}):")
        for pid in missing_in_map:
            e = next(x for x in pub_entries if x["pubid"] == pid)
            print(f"  - {pid}")
            print(f"      url    : {e['url'] or '(none)'}")
            print(f"      status : {fetchability(e['url'])}")
            if e["in_review"]:
                print(f"      note   : flagged 'in review' in the bibliography line")

    if orphan_in_map:
        problems += len(orphan_in_map)
        print(f"\nORPHAN MAP ENTRIES  -  PUBLICATIONS key has no anchor in publications.qmd ({len(orphan_in_map)}):")
        for pid in orphan_in_map:
            print(f"  - {pid}")

    if unknown_paper_refs:
        problems += len(unknown_paper_refs)
        print(f"\nBROKEN REFS  -  COAUTHORS .papers points to unknown id ({len(unknown_paper_refs)}):")
        for pid in unknown_paper_refs:
            print(f"  - {pid}")

    if problems == 0:
        print("\nall good. publications and collaborators map are consistent.")
        return 0

    print(f"\n{problems} issue(s) found.")
    print("Workflow: hand the URLs above to Claude with 'fetch and propose additions'.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
