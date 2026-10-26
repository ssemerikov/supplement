#!/usr/bin/env python3
"""Enforce the reference rule: nothing is cited that has not been DOI-verified.

    python3 code/11_check_references.py

WHY THIS EXISTS. The project rule is that no entry enters
`build/sn-bibliography.bib` before it appears in `docs/reference-ledger.md` as
verified, and that every reference is DOI-verified rather than plausible-looking.
Until now that rule was enforced by remembering it, which is the same way the
wrong publisher for the citation edition of *OSE* survived in eleven files: a
fabricated or unchecked reference looks exactly like a checked one.

Four invariants are checked, in the order in which violating them does damage:

  1. Every key CITED in main.tex resolves to an entry in the .bib.
     (BibTeX reports this too, but only after a completed five-pass run, and
     only as a warning buried in a log.)
  2. Every key in the .bib appears in the ledger. An entry that reached the
     bibliography without passing through the ledger has bypassed verification.
  3. Every ledger row for a cited key carries a verification mark and either a
     DOI or an explicit statement of why it has none.
  4. No Cyrillic anywhere in the .bib -- `inputenc` throws on every Cyrillic
     codepoint, and the failure surfaces as an unrelated-looking build error.

It also reports .bib entries that nothing cites. Those are not errors: BibTeX
omits them from the rendered bibliography. They are reported because an
uncited entry is usually either a citation that got dropped in editing or a
reference someone meant to use.

Exit status 0 = every invariant holds. Non-zero = at least one violation.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "build/main.tex"
BIB = ROOT / "build/sn-bibliography.bib"
LEDGER = ROOT / "docs/reference-ledger.md"

# A row counts as verified if it carries the tick. The ledger's own preamble
# defines the tick as "the DOI was resolved and its metadata compared against
# the citation on the date shown", so the tick is the claim being checked.
VERIFIED = "\u2705"


def cited_keys(tex: str) -> set[str]:
    """Keys inside \\cite, \\citet, \\citep, \\citealt ... including starred and
    optional-argument forms. Comment lines are stripped first: a citation inside
    a commented-out draft paragraph is not a citation."""
    live = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in tex.splitlines())
    keys: set[str] = set()
    for m in re.finditer(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}", live):
        keys.update(k.strip() for k in m.group(1).split(",") if k.strip())
    return keys


def main() -> int:
    for p in (TEX, BIB, LEDGER):
        if not p.exists():
            print(f"FAIL  missing input: {p}")
            return 2

    tex, bib, ledger = TEX.read_text(), BIB.read_text(), LEDGER.read_text()

    cited = cited_keys(tex)
    bib_keys = set(re.findall(r"^@\w+\s*\{\s*([^,\s]+)\s*,", bib, re.M))
    # Ledger keys are written in backticks in the first column of each table row.
    ledger_keys = set(re.findall(r"^\|\s*`([^`]+)`\s*\|", ledger, re.M))

    problems: list[str] = []

    # 1. cited but not in the bibliography ------------------------------------------------
    for k in sorted(cited - bib_keys):
        problems.append(f"cited in main.tex but absent from the .bib: {k}")

    # 2. in the bibliography but never verified in the ledger ------------------------------
    for k in sorted(bib_keys - ledger_keys):
        problems.append(f"in the .bib but not in the reference ledger (unverified): {k}")

    # 3. cited, in the ledger, but the row does not claim verification ---------------------
    for k in sorted(cited & ledger_keys):
        row = next((ln for ln in ledger.splitlines()
                    if re.match(rf"^\|\s*`{re.escape(k)}`\s*\|", ln)), "")
        if VERIFIED not in row:
            problems.append(f"ledger row carries no verification mark: {k}")
        # A row must state a DOI or say explicitly that there is none. "—" alone is
        # ambiguous; the ledger's convention is to write "(book; no DOI)" or similar.
        cells = [c.strip() for c in row.split("|")]
        doi_cell = cells[3] if len(cells) > 4 else ""
        if not re.search(r"10\.\d{4,9}/", doi_cell) and "no doi" not in doi_cell.lower():
            problems.append(
                f"ledger row has neither a DOI nor an explicit 'no DOI' note: {k} "
                f"(DOI cell reads {doi_cell!r})")

    # 4. Cyrillic in the .bib --------------------------------------------------------------
    for i, line in enumerate(bib.splitlines(), 1):
        for ch in line:
            if "CYRILLIC" in unicodedata.name(ch, ""):
                problems.append(
                    f"Cyrillic codepoint in the .bib at line {i} ({ch!r}) -- inputenc will "
                    f"throw; use Library of Congress transliteration with a bracketed gloss")
                break

    uncited = sorted(bib_keys - cited)

    print(f"  {len(cited)} keys cited in main.tex")
    print(f"  {len(bib_keys)} entries in sn-bibliography.bib")
    print(f"  {len(ledger_keys)} keys in the reference ledger")
    if uncited:
        print(f"\n  {len(uncited)} .bib entr{'y' if len(uncited) == 1 else 'ies'} "
              f"nothing cites (not an error; BibTeX omits them):")
        for k in uncited:
            print(f"      {k}")

    if problems:
        print(f"\n{len(problems)} violation(s):")
        for p in problems:
            print(f"  FAIL  {p}")
        return 1

    print("\nAll reference invariants hold: every cited key is in the .bib, every .bib entry "
          "is in the ledger,\nevery cited ledger row is marked verified with a DOI or an "
          "explicit reason it has none, and\nthe .bib is free of Cyrillic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
