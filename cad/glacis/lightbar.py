"""Brophy Borealis light bar pocket (2026-11-10): the Zmoon bar sits recessed in a pocket cut straight back into the
front slant, with a 3 in band left blank above it for crowd sensors later.

The pocket has a level floor and roof and an upright back wall, so the bar still points straight ahead and a sensor
screwed to the band's back wall does too. Its faces carry no panel; a printed liner (two halves, split at y = 0 to fit
the 250 mm bed) lines it, sits on the frame round the opening, and carries the bar on its two end bolts.
"""
import params as P
from lib import box

BP = P.BAR_POCKET


def dims():
    """Every station of the pocket, in robot coordinates."""
    L, hb, db, _, _ = P.LIGHT_BAR
    c, w = BP["clear"], BP["wall"]
    zf = BP["floor_z"]                                  # liner floor, top face
    zb0, zb1 = zf + c, zf + c + hb                      # the bar
    zr = zb1 + c + BP["sensor"]                         # liner roof, underside (top of the sensor band)
    xb1 = P.front_x(zf) - BP["recess"]                  # bar's front face
    xb0 = xb1 - db                                      # bar's back
    xi = xb0 - c                                        # liner back wall, inside face
    yi = L / 2 + c                                      # liner side walls, inside faces
    return dict(L=L, hb=hb, db=db, zf=zf, zb=(zb0, zb1), zr=zr, xb=(xb0, xb1), xi=xi, yi=yi,
                cut=dict(x0=xi - w, y=yi + w, z0=zf - w, z1=zr + w))


def cut():
    """The notch in the body polyhedron (runs out past the front)."""
    d = dims()["cut"]
    return box(d["x0"], P.FRAME_X + 50.0, -d["y"], d["y"], d["z0"], d["z1"])


def cuts():
    return [cut()]


def pocket():
    """The open space inside the liner."""
    d = dims()
    return box(d["xi"], P.FRAME_X + 60.0, -d["yi"], d["yi"], d["zf"], d["zr"])


def bar():
    d = dims()
    s = box(d["xb"][0], d["xb"][1], -d["L"] / 2, d["L"] / 2, d["zb"][0], d["zb"][1])
    return s.cut(box(d["xb"][1] - 2.0, d["xb"][1] + 1.0, -d["L"] / 2 + 14.0, d["L"] / 2 - 14.0,
                     d["zb"][0] + 5.0, d["zb"][1] - 5.0))   # one lens strip


def sensor_band():
    """The blank band above the bar (for the drawing and the log; nothing is fitted yet)."""
    d = dims()
    return box(d["xi"], d["xi"] + 2.0, -d["yi"], d["yi"], d["zb"][1] + BP["clear"], d["zr"])
