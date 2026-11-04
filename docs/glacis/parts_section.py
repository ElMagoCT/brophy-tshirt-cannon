"""Write the "Parts by system" section of the Glacis air & wiring artifact from bom/glacis_bom.py.

    python docs/glacis/parts_section.py     # rewrites the block between the PARTS markers in air_wiring_artifact.html

Each BOM section header becomes a system: a cost table up top (what each system costs to buy), then the items
of every system in a collapsible list. Owned, stash and unused lines show at $0.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "bom"))
from glacis_bom import ROWS  # noqa: E402

PAGE = os.path.join(HERE, "air_wiring_artifact.html")
START, END = "<!-- PARTS:START -->", "<!-- PARTS:END -->"


def systems():
    out = []
    for r in ROWS:
        if r[1] is None:
            name, _, about = r[0].partition(" - ")
            out.append(dict(name=name.strip().capitalize(), about=about.strip(), items=[]))
        elif out:
            name, seller, qty, unit, link = r[0], r[1], r[2], r[3], r[4]
            purpose = r[6] if len(r) > 6 else ""
            out[-1]["items"].append(dict(name=name, seller=seller, qty=qty, unit=unit, link=link, purpose=purpose,
                                         cost=(qty or 0) * (unit or 0.0)))
    for s in out:
        s["cost"] = sum(i["cost"] for i in s["items"])
    return out


def money(v):
    return f"${v:,.2f}"


def render():
    sy = systems()
    total = sum(s["cost"] for s in sy)
    rows = []
    for s in sorted(sy, key=lambda s: -s["cost"]):
        share = s["cost"] / total * 100 if total else 0
        rows.append(f'<tr><th scope="row">{html.escape(s["name"])}</th><td class="num">{money(s["cost"])}</td>'
                    f'<td class="num">{share:.0f}%</td><td class="num">{sum(1 for i in s["items"] if i["cost"] > 0)}</td></tr>')
    blocks = []
    for s in sy:
        items = []
        for i in s["items"]:
            nm = html.escape(i["name"])
            if i["link"]:
                nm = f'<a href="{html.escape(i["link"])}" target="_blank" rel="noopener">{nm}</a>'
            muted = ' class="zero"' if i["cost"] == 0 else ""
            items.append(f'<tr{muted}><td>{nm}<span class="why">{html.escape(i["purpose"])}</span></td>'
                         f'<td>{html.escape(i["seller"])}</td><td class="num">{i["qty"]}</td>'
                         f'<td class="num">{money(i["unit"] or 0)}</td><td class="num">{money(i["cost"])}</td></tr>')
        blocks.append(
            f'<details class="sys"><summary><span>{html.escape(s["name"])}</span><span class="num">{money(s["cost"])}</span></summary>'
            f'<p class="about">{html.escape(s["about"])}</p><div class="tscroll"><table class="bom">'
            f'<thead><tr><th>Part</th><th>From</th><th class="num">Qty</th><th class="num">Each</th><th class="num">Line</th></tr></thead>'
            f'<tbody>{"".join(items)}</tbody></table></div></details>')
    return f"""{START}
  <section class="sheet" id="parts" aria-labelledby="parts-h">
    <div class="head">
      <h2 id="parts-h">Parts by system</h2>
      <div class="legend"><span>{money(total)} to buy</span><span>owned and stash parts at $0</span></div>
    </div>
    <div class="tscroll"><table class="cost">
      <thead><tr><th>System</th><th class="num">Cost</th><th class="num">Share</th><th class="num">Lines to buy</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
      <tfoot><tr><th scope="row">Total</th><td class="num">{money(total)}</td><td class="num">100%</td><td></td></tr></tfoot>
    </table></div>
    {"".join(blocks)}
  </section>
  {END}"""


CSS = """
/* parts list */
.tscroll { overflow-x: auto; -webkit-overflow-scrolling: touch }
#parts table { border-collapse: collapse; width: 100%; font-size: 13px }
#parts th, #parts td { text-align: left; padding: 6px 8px; border-bottom: 1px solid color-mix(in srgb, var(--line) 18%, transparent); vertical-align: top }
#parts thead th { font-family: var(--mono); font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .05em }
#parts .num { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap }
#parts table.cost { max-width: 560px }
#parts table.cost tbody th { font-weight: 600 }
#parts tfoot th, #parts tfoot td { font-weight: 800; border-bottom: none }
#parts details.sys { border-top: 1px solid color-mix(in srgb, var(--line) 25%, transparent) }
#parts details.sys summary { display: flex; justify-content: space-between; gap: 12px; padding: 10px 2px; cursor: pointer; font-weight: 600 }
#parts details.sys summary:focus-visible { outline: 3px solid var(--on); outline-offset: 2px }
#parts .about { margin: 0 0 8px; font-size: 13px; color: var(--muted) }
#parts table.bom { min-width: 640px }
#parts .why { display: block; font-size: 12px; color: var(--muted) }
#parts tr.zero td { color: var(--muted) }
#parts a { color: var(--ink) }
"""


def main():
    src = open(PAGE).read()
    if START in src:
        a, b = src.index(START), src.index(END) + len(END)
        src = src[:a] + render() + src[b:]
    else:                                          # first run: before the closing wrapper div, plus the styles
        at = src.rindex("</div>\n\n<script>")
        src = src[:at] + "  " + render() + "\n" + src[at:]
        src = src.replace("@media (prefers-reduced-motion: reduce)", CSS.strip() + "\n@media (prefers-reduced-motion: reduce)", 1)
    open(PAGE, "w").write(src)
    sy = systems()
    print(f"{len(sy)} systems, {money(sum(s['cost'] for s in sy))}")


if __name__ == "__main__":
    main()
