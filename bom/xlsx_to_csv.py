"""Mirror every sheet of the BOM workbook to CSV (computed values, not formulas).

Usage: python3 bom/xlsx_to_csv.py   (needs openpyxl: pip install openpyxl)

Formulas are written by openpyxl without cached values, so the Line $ and subtotal
columns are recomputed here for the BOM sheet. Run after every xlsx edit and
commit the xlsx and the CSVs together.
"""
import csv
import re
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
XLSX = HERE / "Brophy_TShirt_Cannon_Mark5_Parts_List.xlsx"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def evaluate(ws, cell, cache):
    """Tiny evaluator for the formula shapes this workbook uses."""
    if cell in cache:
        return cache[cell]
    v = ws[cell].value
    if isinstance(v, str) and v.startswith("="):
        f = v[1:].replace("$", "")
        m = re.fullmatch(r"([A-Z]+\d+)\*([A-Z]+\d+)", f)
        if m:
            a, b = (evaluate(ws, c, cache) for c in m.groups())
            v = (a or 0) * (b or 0)
        elif (m := re.fullmatch(r"SUMIFS\(([A-Z]+)(\d+):[A-Z]+(\d+),([A-Z]+)\d+:[A-Z]+\d+,\"(\w+)\"\)", f)):
            col, r0, r1, keycol, key = m.groups()
            v = sum(
                evaluate(ws, f"{col}{r}", cache) or 0
                for r in range(int(r0), int(r1) + 1)
                if ws[f"{keycol}{r}"].value == key
            )
        elif (m := re.fullmatch(r"([A-Z]+\d+)([+-])([A-Z]+\d+)(?:\+([A-Z]+\d+))?", f)):
            a, op, b, c = m.groups()
            v = evaluate(ws, a, cache) + (1 if op == "+" else -1) * evaluate(ws, b, cache)
            if c:
                v += evaluate(ws, c, cache)
        else:
            raise ValueError(f"unhandled formula in {ws.title}!{cell}: {v}")
    cache[cell] = v
    return v


def main():
    wb = openpyxl.load_workbook(XLSX)
    for ws in wb.worksheets:
        cache = {}
        out = HERE / f"{slug(ws.title)}.csv"
        with out.open("w", newline="") as fh:
            w = csv.writer(fh)
            for row in ws.iter_rows():
                vals = [evaluate(ws, c.coordinate, cache) for c in row]
                vals = [round(v, 2) if isinstance(v, float) else v for v in vals]
                while vals and vals[-1] is None:
                    vals.pop()
                w.writerow(["" if v is None else v for v in vals])
        print(f"wrote {out.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
