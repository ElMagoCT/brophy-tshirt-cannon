"""NPT pipe fittings and valves as simple solids, placed along a run like real make-up.

A Chain walks along a direction from a start point. Its state is either an open female port
('F', s) or a bare male end ('M', s), with s the distance along the run. Male threads go
ENG deep into the female before them, so parts overlap only inside threads (bores are hollow).
Dimensions are nominal (catalog-typical) and good to a few mm; see JUDGMENTS for which.
"""
import math
import cadquery as cq
from cadquery import Vector as V
from lib import cyl, tube, hex_prism, union

IN = 25.4
OD = {"1/8": 10.29, "1/4": 13.72, "3/4": 26.67, "4": 114.3}
ENG = {"1/8": 6.7, "1/4": 10.2, "3/4": 13.9, "4": 33.0}
BORE = {"1/8": 6.0, "1/4": 9.2, "3/4": 20.9, "4": 97.2}      # Sch 80 small sizes, Sch 40 for 4"
CLOSE_NIPPLE = {"1/4": 22.2, "3/4": 34.9, "4": 73.0}


def _along(shape, base, d):
    """Shape built along +Z from the origin -> placed at `base` pointing along `d`."""
    z = V(0, 0, 1)
    d = d.normalized()
    k = z.cross(d)
    s = shape
    if k.Length > 1e-9:
        s = s.rotate(V(0, 0, 0), k, math.degrees(math.acos(max(-1.0, min(1.0, z.dot(d))))))
    elif d.z < 0:
        s = s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    return s.translate(base)


class Chain:
    def __init__(self, start, direction, state="F", add=None, prefix="", group="pneu", moving=False):
        self.p0 = V(*start)
        self.d = V(*direction).normalized()
        self.state, self.s = state, 0.0
        self.add, self.prefix, self.group, self.moving = add, prefix, group, moving
        self.items = []

    def at(self, s):
        return self.p0 + self.d * s

    def _put(self, name, shape_z, s0, color, bom, kind="cots"):
        sh = _along(shape_z, self.at(s0), self.d)
        if self.add:
            self.add(f"{self.prefix}{name}", sh, color, self.group, bom=bom, kind=kind, moving=self.moving)
        self.items.append(sh)
        return sh

    # --- male parts into an open female port
    def nipple(self, size, length=None, color="steel", bom=None):
        assert self.state == "F", "nipple needs a female port"
        L = length or CLOSE_NIPPLE[size]
        s0 = self.s - ENG[size]
        self._put(f"nipple {size}x{L / IN:.2f}", tube(OD[size] / 2, BORE[size] / 2, L), s0, color,
                  bom or f"{size} NPT nipple x {L / IN:.2f} in ({'brass' if color == 'brass' else 'steel'})")
        self.state, self.s = "M", s0 + L
        return self

    def bushing(self, male, female, hex_af, hex_t, color="steel", bom=None):
        assert self.state == "F"
        e = ENG[male]
        body = tube(OD[male] / 2, OD[female] / 2, e).translate(V(0, 0, -e))
        hx = hex_prism(hex_af, hex_t).cut(cyl(OD[female] / 2, hex_t + 1, (0, 0, -0.5)))
        self._put(f"bushing {male}x{female}", body.fuse(hx), self.s, color,
                  bom or f"{male} x {female} NPT hex bushing")
        self.state, self.s = "F", self.s + hex_t
        return self

    def bushing_rev(self, male, female, hex_af, hex_t, color="steel", bom=None):
        """Bushing turned the other way: its female port takes the male end, its male thread leads on."""
        assert self.state == "M"
        ef, em = ENG[female], ENG[male]
        s0 = self.s - ef
        # cast bushing: hex flange with the small port, then a thin-walled male thread ring
        hx = hex_prism(hex_af, hex_t).cut(cyl(OD[female] / 2, hex_t + 1, (0, 0, -0.5)))
        boss = tube(OD[female] / 2 + 6, OD[female] / 2, ef, (0, 0, 0))
        th = tube(OD[male] / 2, OD[male] / 2 - 7.0, em + 2, (0, 0, hex_t))
        hx = hx.fuse(boss)
        self._put(f"bushing {male}x{female}", hx.fuse(th), s0, color, bom or f"{male} x {female} NPT hex bushing")
        self.state, self.s = "M", s0 + hex_t + em + 2
        return self

    def block(self, size="1/4", side=25.4, sides=((0, 1, 0), (0, -1, 0)), color="brass", bom=None, rear=True):
        """Brass port block on a male end: rear port continues the run (unless rear=False), returns chains
        for the side ports."""
        assert self.state == "M"
        e = ENG[size]
        s0 = self.s - e
        body = cq.Solid.makeBox(side, side, side, V(-side / 2, -side / 2, 0))
        sh = _along(body, self.at(s0), self.d)
        c = self.at(s0 + side / 2)
        sh = sh.cut(_along(cyl(OD[size] / 2, e), self.at(s0), self.d))
        if rear:
            sh = sh.cut(_along(cyl(OD[size] / 2, e), self.at(s0 + side - e), self.d))
        sh = sh.cut(cq.Solid.makeSphere(7.5, c, angleDegrees1=-90, angleDegrees2=90))   # drilled ports meet
        out = []
        for sd in sides:
            b = V(*sd).normalized()
            sh = sh.cut(cyl(OD[size] / 2, e, (c + b * (side / 2 - e)).toTuple(), b.toTuple()))
            out.append(Chain((c + b * (side / 2)).toTuple(), b.toTuple(), "F", self.add, self.prefix, self.group,
                             self.moving))
        if self.add:
            self.add(f"{self.prefix}port block {size}", sh, color, self.group,
                     bom=bom or f"{size} NPT brass port block (4-port)", moving=self.moving)
        self.items.append(sh)
        self.state, self.s = ("F" if rear else "end"), s0 + side
        return out

    # --- female parts onto a male end
    def coupling(self, size, length, od, color="steel", bom=None):
        assert self.state == "M"
        e = ENG[size]
        s0 = self.s - e
        self._put(f"coupling {size}", tube(od / 2, OD[size] / 2, length), s0, color, bom or f"{size} NPT coupling")
        self.state, self.s = "F", s0 + length
        return self

    def cap(self, size, length, od, color="steel", bom=None):
        assert self.state == "M"
        e = ENG[size]
        s0 = self.s - e
        body = cyl(od / 2, length).cut(cyl(OD[size] / 2, e))
        self._put(f"cap {size}", body, s0, color, bom or f"{size} NPT cap")
        self.state, self.s = "end", s0 + length
        return self

    def ff(self, name, length, od, size="1/4", color="brass", bom=None, extra=None):
        """Generic female-female body (check valve, solenoid body, ball valve) on a male end."""
        assert self.state == "M"
        e = ENG[size]
        s0 = self.s - e
        body = cyl(od / 2, length).cut(cyl(OD[size] / 2, e)).cut(cyl(OD[size] / 2, e + 1, (0, 0, length - e)))
        if extra is not None:
            body = body.fuse(extra(length))
        self._put(name, body, s0, color, bom or name)
        self.state, self.s = "F", s0 + length
        return self

    def male_end(self, name, length, od, size="1/4", color="brass", bom=None, extra=None):
        """Male-threaded terminal part (relief valve, push-to-connect, gauge stem, muffler)."""
        assert self.state == "F"
        e = ENG[size]
        s0 = self.s - e
        body = cyl(OD[size] / 2, e).fuse(cyl(od / 2, length - e, (0, 0, e)))
        if extra is not None:
            body = body.fuse(extra(length))
        self._put(name, body, s0, color, bom or name)
        self.state, self.s = "end", s0 + length
        return self

    def tee(self, size, run, od, branch_dir, color="brass", bom=None):
        """Tee on a male end; the run continues, returns a Chain for the branch."""
        assert self.state == "M"
        e = ENG[size]
        s0 = self.s - e
        b = V(*branch_dir).normalized()
        run_body = cyl(od / 2, run)
        sh = _along(run_body, self.at(s0), self.d)
        bc = self.at(s0 + run / 2)
        br = cyl(od / 2, run / 2, bc.toTuple(), b.toTuple())
        body = sh.fuse(br)
        body = body.cut(_along(cyl(OD[size] / 2, e), self.at(s0), self.d))
        body = body.cut(_along(cyl(OD[size] / 2, e), self.at(s0 + run - e), self.d))
        body = body.cut(cyl(OD[size] / 2, e, (bc + b * (run / 2 - e)).toTuple(), b.toTuple()))
        if self.add:
            self.add(f"{self.prefix}tee {size}", body, color, self.group, bom=bom or f"{size} NPT tee (brass)",
                     moving=self.moving)
        self.items.append(body)
        self.state, self.s = "F", s0 + run
        return Chain((bc + b * (run / 2)).toTuple(), b.toTuple(), "F", self.add, self.prefix, self.group, self.moving)

    def cross(self, size, run, od, branch_dir, color="brass", bom=None):
        """Cross on a male end; the run continues, returns Chains for the two opposite branches."""
        assert self.state == "M"
        e = ENG[size]
        s0 = self.s - e
        b = V(*branch_dir).normalized()
        sh = _along(cyl(od / 2, run), self.at(s0), self.d)
        bc = self.at(s0 + run / 2)
        body = sh.fuse(cyl(od / 2, run, (bc - b * (run / 2)).toTuple(), b.toTuple()))
        body = body.cut(_along(cyl(OD[size] / 2, e), self.at(s0), self.d))
        body = body.cut(_along(cyl(OD[size] / 2, e), self.at(s0 + run - e), self.d))
        for bb in (b, b * -1):
            body = body.cut(cyl(OD[size] / 2, e, (bc + bb * (run / 2 - e)).toTuple(), bb.toTuple()))
        if self.add:
            self.add(f"{self.prefix}cross {size}", body, color, self.group, bom=bom or f"{size} NPT cross (brass)",
                     moving=self.moving)
        self.items.append(body)
        self.state, self.s = "F", s0 + run
        return [Chain((bc + bb * (run / 2)).toTuple(), bb.toTuple(), "F", self.add, self.prefix, self.group, self.moving)
                for bb in (b, b * -1)]


# ------------------------------------------------------------------ valve bodies (along +Z)
def va4_coil(length):
    """HornBlasters VA-4: brass body with the 12 V coil standing off one side (along +X)."""
    return cyl(18.0, 50.0, (11.0, 0, length / 2), (1, 0, 0))


def relief_cap(length):
    return cyl(9.0, 8.0, (0, 0, length - 8.0)).fuse(cyl(13.0, 2.0, (0, 0, length - 14.0)))


def ball_lever(length):
    return cq.Solid.makeBox(4.0, 55.0, 8.0, V(-2.0, 0.0, length / 2 - 4.0))


def gauge_face(length, d=52.0, depth=26.0, back=True):
    if back:
        return cyl(d / 2, depth, (0, 0, length))
    return cyl(d / 2, depth, (0, -depth / 2, length + d / 2), (0, 1, 0))
