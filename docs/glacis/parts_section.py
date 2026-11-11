"""Feed the parts list into the Glacis air & wiring artifact from bom/glacis_bom.py.

    python docs/glacis/parts_section.py            # rewrites the JSON between the BOM markers in air_wiring_artifact.html
    python docs/glacis/parts_section.py --base REF # compare against bom/glacis_bom.py at git REF (default: rev D.2.1)

Each BOM section header becomes a system. Every item carries its change against the base revision (new, changed
price or quantity, or unchanged), and items dropped since the base are listed as removed, so the page can show what
this round changed and what it costs. Rows are matched by name, one for one (a name used twice pairs with the base's
rows in order), and a section the base had but the list no longer has keeps its dropped rows, so new + changed -
removed always adds up to the change in the total: the page's Money table is built from exactly that.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "bom"))
from glacis_bom import ROWS  # noqa: E402

PAGE = os.path.join(HERE, "air_wiring_artifact.html")
START, END = "/*BOM:START*/", "/*BOM:END*/"
BASE = "5a76180"   # rev D.2.1 (origin/main on 2026-11-10): what the page's "vs rev D.2.1" labels compare against


def key(name):
    """Section name without a trailing note: "GUN (rev D.2)" and "GUN" are the same section."""
    return re.sub(r"\s*\(.*?\)\s*$", "", name).strip()


def sections(rows):
    out = []
    for r in rows:
        if r[1] is None:
            name, _, about = r[0].partition(" - ")
            out.append(dict(name=name.strip(), about=about.strip(), items=[]))
        elif out:
            name, seller, qty, unit, link, typ, purpose, notes = r
            out[-1]["items"].append(dict(name=name, seller=seller, qty=qty, unit=unit, link=link, type=typ,
                                         purpose=purpose, notes=notes))
    return out


def base_rows(ref):
    src = subprocess.check_output(["git", "-C", ROOT, "show", f"{ref}:bom/glacis_bom.py"]).decode()
    ns = {}
    exec(compile(src, "base", "exec"), ns)
    return ns["ROWS"]


def main():
    ref = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else BASE
    new, old = sections(ROWS), sections(base_rows(ref))
    left = {}                                             # base rows not yet paired with a current row, by name
    for s in old:
        for i in s["items"]:
            left.setdefault(i["name"], []).append((key(s["name"]), i))
    for s in new:
        for i in s["items"]:
            o = left[i["name"]].pop(0)[1] if left.get(i["name"]) else None
            if o is None:
                i["change"] = "new"
            elif (o["qty"], o["unit"]) != (i["qty"], i["unit"]):
                i["change"] = "changed"
                i["was"] = dict(qty=o["qty"], unit=o["unit"])
            else:
                i["change"] = ""

    def gone(sec):
        return [dict(name=i["name"], seller=i["seller"], qty=i["qty"], unit=i["unit"], link=i["link"])
                for rows in left.values() for (k, i) in rows if k == sec]

    for s in new:
        s["removed"] = gone(key(s["name"]))
    have = {key(s["name"]) for s in new}
    for s in old:                                         # sections dropped since the base: only their removed rows
        if key(s["name"]) not in have and gone(key(s["name"])):
            have.add(key(s["name"]))
            new.append(dict(name=s["name"], about=s["about"], items=[], removed=gone(key(s["name"]))))
    total = sum((i["qty"] or 0) * (i["unit"] or 0) for s in new for i in s["items"])
    base_total = sum((i["qty"] or 0) * (i["unit"] or 0) for s in old for i in s["items"])
    data = dict(base=ref, total=round(total, 2), base_total=round(base_total, 2), sections=new)
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = open(PAGE, encoding="utf-8", newline="").read()   # UTF-8 and LF kept as they are (Windows defaults break both)
    a, b = page.index(START) + len(START), page.index(END)
    open(PAGE, "w", encoding="utf-8", newline="").write(page[:a] + blob + page[b:])
    print(f"parts: ${total:,.2f} (base {ref}: ${base_total:,.2f}, {total - base_total:+.2f})")


if __name__ == "__main__":
    main()
