"""Quick matplotlib renders of CadQuery shapes (flat shaded, painter's sort)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

LIGHT = np.array([0.35, -0.45, 0.82]); LIGHT /= np.linalg.norm(LIGHT)


def mesh(shape, tol=0.8):
    v, f = shape.tessellate(tol, 0.4)
    if not f:
        return None, None
    return np.array([(p.x, p.y, p.z) for p in v]), np.array(f)


def draw(items, path, views=((22, -58),), size=(9, 7), dpi=110, titles=None, xlim=None):
    """items: list of (shape, rgba). One subplot per view."""
    tris, cols = [], []
    for shape, rgba in items:
        v, f = mesh(shape)
        if v is None:
            continue
        t = v[f]
        nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        ln = np.linalg.norm(nrm, axis=1); ln[ln == 0] = 1
        shade = 0.38 + 0.62 * np.abs((nrm / ln[:, None]) @ LIGHT)
        c = np.clip(np.outer(shade, rgba[:3]), 0, 1)
        a = np.full((len(t), 1), rgba[3] if len(rgba) > 3 else 1.0)
        tris.append(t); cols.append(np.hstack([c, a]))
    T = np.concatenate(tris); Cc = np.concatenate(cols)
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    ctr, r = (lo + hi) / 2, (hi - lo).max() / 2 * 0.92
    fig = plt.figure(figsize=(size[0] * len(views), size[1]), dpi=dpi)
    for i, (el, az) in enumerate(views):
        ax = fig.add_subplot(1, len(views), i + 1, projection="3d")
        # painter's sort along the view direction
        e, a = np.radians(el), np.radians(az)
        d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        depth = (T.mean(1) - ctr) @ d
        o = np.argsort(depth)
        ax.add_collection3d(Poly3DCollection(T[o], facecolors=Cc[o], edgecolors="none", linewidths=0))
        ax.set_xlim(ctr[0] - r, ctr[0] + r); ax.set_ylim(ctr[1] - r, ctr[1] + r); ax.set_zlim(ctr[2] - r, ctr[2] + r)
        ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.set_axis_off()
        if titles:
            ax.set_title(titles[i])
    plt.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path
