"""Build the robot once: test-fit two 2.5 gal tanks, then write robot.glb (one mesh per look) + meta.json for the
three.js render."""
import os, sys, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
import numpy as np, trimesh
import cadquery as cq
import robot, params as P
from lib import PARTS
parts = robot.build()
# the new light bar and its brackets against everything else, then the Onshape STEPs and the parts rollup
lb = [p for p in PARTS if p['name'].startswith('LED light bar')]
hits = []
for a in lb:
    ba = a['shape'].BoundingBox()
    for b in PARTS:
        if b is a or b['name'].startswith('LED light bar'): continue
        bb = b['shape'].BoundingBox()
        if bb.xmax < ba.xmin or ba.xmax < bb.xmin or bb.ymax < ba.ymin or ba.ymax < bb.ymin or bb.zmax < ba.zmin or ba.zmax < bb.zmin:
            continue
        v = a['shape'].intersect(b['shape']).Volume()
        if v > 30: hits.append((round(v), a['name'], b['name']))
print('light bar clashes', hits)
robot.export(parts)
robot.bom_rollup(parts)

# ---------------------------------------------------------------- tank test-fit (EVIL ENERGY 2.5 gal: 498 x 200 x 160)
skip = ('Air tank', 'Tank strap', 'Tank saddle', 'Tank arm', 'Tank post', 'Tank plug', 'Tank elbow', 'Tube tank')
fixed = [p for p in PARTS if not p['name'].startswith(skip) and not p.get('moving')]
plain = robot.misc.B.body_solid(notched=False)
def tank(c, axis, w=200.0, h=160.0, L=498.0):
    if axis == 'x':
        wp = cq.Workplane('YZ', origin=(c[0] - L / 2, 0, 0)).center(c[1], c[2])
    else:
        wp = cq.Workplane('XZ', origin=(0, c[1] + L / 2, 0)).center(c[0], c[2])
    return wp.ellipse(w / 2, h / 2).extrude(L).val()
def clash(s):
    out, bb = [], s.BoundingBox()
    for p in fixed:
        q = p['shape'].BoundingBox()
        if q.xmax < bb.xmin or bb.xmax < q.xmin or q.ymax < bb.ymin or bb.ymax < q.ymin or q.zmax < bb.zmin or bb.zmax < q.zmin:
            continue
        v = s.intersect(p['shape']).Volume()
        if v > 30: out.append((round(v), p['name']))
    o = s.Volume() - s.intersect(plain).Volume()
    if o > 30: out.append((round(o), 'OUTSIDE THE BODY'))
    floor = min(z for x, z in robot.misc.B.SLOT_PTS if -400 < x < 400)
    return sorted(out, reverse=True)
res = {}
for xc in (-60.0, 0.0, 60.0):
    res[f'side x{xc:.0f}'] = clash(tank((xc, 163.0, 360.0), 'x'))[:5]
for xc in (60.0, 100.0, 220.0):
    for zc in (330.0, 370.0):
        res[f'front-across x{xc:.0f} z{zc:.0f}'] = clash(tank((xc, 0.0, zc), 'y', 160.0, 200.0))[:5]
json.dump(res, open(OUT + 'tankfit.json', 'w'), indent=1)
print('tank fit done')

# ---------------------------------------------------------------- meshes by look
def role(p):
    n, g = p['name'], p['group']
    if n.startswith('Panel clip') or n.startswith('Battery door latch'): return 'frame'
    if n.startswith('Panel '): return 'panel'
    if n.startswith('LED loop'): return 'loop'
    if n.startswith('LED strip underglow'): return 'underglow'
    if n.startswith('LED strip frame'): return None                 # inside the frame: shown by the frame's glow
    if n.startswith('LED light bar front'): return 'lightbar'
    if n.startswith(('Body frame', 'LED light bar bracket', 'Underglow bracket', 'Speaker cup')): return 'frame'
    if n.startswith('Speaker grille') or n.startswith('Speaker '): return 'grille'
    if g == 'bumper': return 'bumper'
    if g == 'gun':
        if n.startswith('Barrel'): return 'barrel'
        if p['kind'] == 'print': return 'gunprint'
        return 'metal'
    if g == 'drive':
        if 'tread' in n.lower(): return 'tire'
        if p['kind'] == 'print' or 'hub' in n.lower() or 'core' in n.lower(): return 'darkprint'
        return 'metal'
    if g == 'frame': return 'metal'
    return None                                                     # tanks, electronics, plumbing: inside the body
meshes = {}
for p in PARTS:
    r = role(p)
    if r is None: continue
    tol = 0.6 if r in ('loop', 'underglow') else 1.2
    v, f = p['shape'].tessellate(tol, 0.5)
    if not f: continue
    m = trimesh.Trimesh(np.array([(q.x, q.y, q.z) for q in v]) / 1000.0, np.array(f), process=False)
    meshes.setdefault(r, []).append(m)
scene = trimesh.Scene()
for r, ms in meshes.items():
    scene.add_geometry(trimesh.util.concatenate(ms), node_name=r, geom_name=r)
scene.export(OUT + 'robot.glb')
# muzzles: far end of each barrel (posed), direction from the barrel's axis
meta = {}
for p in PARTS:
    if p['name'] in ('Barrel top', 'Barrel bottom'):
        v, _ = p['shape'].tessellate(2.0, 0.5)
        pts = np.array([(q.x, q.y, q.z) for q in v])
        a = math.radians(P.ELEV_SHOW)
        d = np.array([math.cos(a), 0.0, math.sin(a)])
        s = pts @ d
        tip = pts[s > s.max() - 3.0].mean(axis=0)
        meta[p['name']] = dict(tip=(tip / 1000).tolist(), dir=d.tolist())
meta['vents'] = dict(front=[0.368, 0.08, 0.09], rear=[-0.14, 0.0, 0.09])
meta['bbox'] = [list(map(float, scene.bounds[0])), list(map(float, scene.bounds[1]))]
json.dump(meta, open(OUT + 'meta.json', 'w'), indent=1)
print('glb', {r: sum(len(m.faces) for m in ms) for r, ms in meshes.items()})
