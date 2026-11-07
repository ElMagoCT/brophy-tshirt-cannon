"""Feed the parts list into the Glacis air & wiring artifact from bom/glacis_bom.py.

    python docs/glacis/parts_section.py            # rewrites the JSON between the BOM markers in air_wiring_artifact.html
    python docs/glacis/parts_section.py --base REF # compare against bom/glacis_bom.py at git REF (default HEAD)

Each BOM section header becomes a system. Every item carries its change against the base revision (new, changed
price or quantity, or unchanged), and items dropped since the base are listed as removed, so the page can show what
this round changed and what it costs.
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
    ref = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "HEAD"
    new, old = sections(ROWS), sections(base_rows(ref))
    old_items = {i["name"]: (s["name"], i) for s in old for i in s["items"]}
    new_names = {i["name"] for s in new for i in s["items"]}
    for s in new:
        for i in s["items"]:
            o = old_items.get(i["name"])
            if o is None:
                i["change"] = "new"
            elif (o[1]["qty"], o[1]["unit"]) != (i["qty"], i["unit"]):
                i["change"] = "changed"
                i["was"] = dict(qty=o[1]["qty"], unit=o[1]["unit"])
            else:
                i["change"] = ""
        s["removed"] = [dict(name=i["name"], seller=i["seller"], qty=i["qty"], unit=i["unit"], link=i["link"])
                        for (sec, i) in old_items.values() if sec == s["name"] and i["name"] not in new_names]
    total = sum((i["qty"] or 0) * (i["unit"] or 0) for s in new for i in s["items"])
    base_total = sum((i["qty"] or 0) * (i["unit"] or 0) for s in old for i in s["items"])
    data = dict(base=ref, total=round(total, 2), base_total=round(base_total, 2), sections=new)
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = open(PAGE).read()
    a, b = page.index(START) + len(START), page.index(END)
    open(PAGE, "w").write(page[:a] + blob + page[b:])
    print(f"parts: ${total:,.2f} (base {ref}: ${base_total:,.2f}, {total - base_total:+.2f})")


if __name__ == "__main__":
    main()
