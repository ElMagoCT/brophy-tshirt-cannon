"""Speakers (rev C.2): a slim 100 W siren speaker high in each front-side corner, aimed 45 deg out and 30 deg
up (a bottom pair at 22.5 out / 15 up doesn't fit: the notches pinch the side panels in two, the cups hit the
front wheels, and the grilles push the robot past the 28 in door). Each sits in a square pocket cut into the
corner (the body polyhedron is notched, so the panels, frame, LED rails and loops all follow it), lined by a
printed cup, with a printed grille over its face (print it 3 walls, no top or bottom layers, 12% gyroid, so
it's an open mesh)."""
import math
import cadquery as cq
from cadquery import Vector as V
import params as P


def _corner(sgn, end):
    """End of the front-side corner edge on one side, and the unit direction along the edge away from it."""
    top = V(P.X_TOP_FRONT, sgn * P.wall_y(P.Z_TOP), P.Z_TOP)
    bot = V(P.FRAME_X, sgn * P.Y_S, P.Z_WALL_BOT)
    return (top, (bot - top).normalized()) if end == "top" else (bot, (top - bot).normalized())


def _prism(q, a, b1, b2, h1, h2, back, out):
    """Box centred on the line through q along a: +-h1 along b1, +-h2 along b2, from q - a*back to q + a*out."""
    pl = cq.Plane(origin=(q - a * back).toTuple(), xDir=b1.toTuple(), normal=a.toTuple())
    return cq.Workplane(pl).rect(2 * h1, 2 * h2).extrude(back + out).val()


def pods():
    """One dict per speaker: aim, axes, seat centre and the solids that place it."""
    w, h, d = P.SPEAKER
    clr, wall = P.SPK_CLEAR, P.SPK_WALL
    out = []
    for sgn, side in ((1, "left"), (-1, "right")):
        for tag, end, along, az, el, sink, inboard in P.SPEAKERS:
            c0, e = _corner(sgn, end)
            c = c0 + e * along - V(0, sgn * inboard, 0)     # slid inboard keeps the grille inside the bumpers
            az, el = math.radians(az), math.radians(el)
            a = V(math.cos(el) * math.cos(az), sgn * math.cos(el) * math.sin(az), math.sin(el))
            b1 = (e - a * e.dot(a)).normalized()          # speaker height runs along the corner edge
            b2 = a.cross(b1).normalized()
            q = c - a * sink                              # seat: the cup floor the speaker's back sits on
            h1, h2 = h / 2 + clr, w / 2 + clr
            out.append(dict(
                name=f"{tag} {side}", sgn=sgn, a=a, b1=b1, b2=b2, q=q,
                cut=_prism(q, a, b1, b2, h1 + wall, h2 + wall, wall, 400.0),        # notch in the body
                pocket=_prism(q, a, b1, b2, h1, h2, 0.0, 400.0),
                speaker=_prism(q + a * (d / 2), a, b1, b2, h / 2, w / 2, d / 2, d / 2),
                grille=_prism(q + a * (d + 0.5), a, b1, b2, h1 - 0.3, h2 - 0.3, 0.0, P.SPK_GRILLE),
                wire=cq.Solid.makeCylinder(6.0, wall + 2.0, (q - a * (wall + 1.0) + b1 * (h / 2 - 20.0)), a)))
    return out


def cuts():
    return [p["cut"] for p in pods()]
