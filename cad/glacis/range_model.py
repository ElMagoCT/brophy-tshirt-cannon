"""Glacis range and air budget (rev C.3 electronics/air review, 2026-11-03). Micah's targets: one shot at 200 ft and six at
75 ft before the tanks need refilling.

Interior: shot_model.py's lumped shot with the valve Cv, opening time and barrel length as parameters.
Exterior: point mass with quadratic drag, 250 g rolled shirt, launched 1.2 m up, Phoenix air (1.12 kg/m^3), best angle.
CdA of a tumbling rolled shirt is the big unknown: 0.004 (flies end-on) to 0.008 m^2 (tumbles broadside); 0.006 nominal.
Tanks: isothermal, each refill takes chamber_L * chamber_psi / tank_L out of the tanks; chambers empty to ~0 psig on a shot.

    python range_model.py
"""
import math
from shot_model import PATM, R, T0, V_DEAD, A_B, IN, cv_air, cp_air, flow, g

FT = 0.3048


def shot(vc_l, psig, t_open=0.05, cv=12.0, barrel_in=22.5, m_s=0.25, f_fric=15.0):
    """shot_model.shot with the valve and barrel as parameters. Returns exit speed, m/s."""
    a_v = cv / 38.0 * IN ** 2
    l_t = barrel_in * IN - 0.15
    p10 = psig * 6894.76 + PATM
    m10 = p10 * vc_l * 1e-3 / (R * T0)
    m1, V2 = m10, V_DEAD
    m2 = PATM * V2 / (R * T0)
    U2 = m2 * cv_air * T0
    x = v = t = 0.0
    dt = 2e-6
    while x < l_t and t < 0.5:
        p1 = p10 * (m1 / m10) ** g
        T1 = T0 * (p1 / p10) ** ((g - 1) / g)
        p2 = m2 * R * (U2 / (m2 * cv_air)) / V2
        dm = min(1.0, t / t_open) * a_v * flow(p1, T1, p2) * dt
        F = (p2 - PATM) * A_B
        acc = (F - f_fric) / m_s if (v > 0 or F > f_fric) else 0.0
        vn = max(0.0, v + acc * dt)
        dx = 0.5 * (v + vn) * dt
        m1 -= dm
        m2 += dm
        U2 += dm * cp_air * T1 - p2 * A_B * dx
        V2 += A_B * dx
        x += dx
        v = vn
        t += dt
    return v


def range_ft(v0, cda, m=0.25, h0=1.2, rho=1.12):
    best = 0.0
    k = 0.5 * rho * cda / m
    for deg in range(20, 56):
        th = math.radians(deg)
        vx, vy, x, y, dt = v0 * math.cos(th), v0 * math.sin(th), 0.0, h0, 1e-3
        while y >= 0:
            sp = math.hypot(vx, vy)
            vx -= k * sp * vx * dt
            vy -= (9.81 + k * sp * vy) * dt
            x += vx * dt
            y += vy * dt
        best = max(best, x)
    return best / FT


def speed_for(ft, cda):
    lo, hi = 5.0, 120.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if range_ft(mid, cda) < ft else (lo, mid)
    return hi


def psi_for(v_target, vc, cv, t_open, barrel, hi=150.0):
    lo = 10.0
    if shot(vc, hi, t_open, cv, barrel) < v_target:
        return None
    for _ in range(25):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if shot(vc, mid, t_open, cv, barrel) < v_target else (lo, mid)
    return hi


def tank_l_needed(vc, p_big, p_small, p_start, n_small=6):
    """Smallest tank (L) that fills the 200 ft shot first, then six 75 ft shots, keeping 5 psi over each setpoint."""
    lo, hi = 0.5, 400.0
    for _ in range(40):
        vt = 0.5 * (lo + hi)
        pt = p_start
        ok = pt >= p_big + 5
        pt -= vc * p_big / vt
        for _ in range(n_small):
            ok = ok and pt >= p_small + 5
            pt -= vc * p_small / vt
        lo, hi = (lo, vt) if ok else (vt, hi)
    return hi


if __name__ == "__main__":
    print("Muzzle speed for 75 ft / 200 ft (m/s) by shirt CdA:")
    for cda in (0.004, 0.006, 0.008):
        print(f"  CdA {cda:.3f}: {speed_for(75, cda):4.1f} / {speed_for(200, cda):4.1f}")
    v200, v75 = speed_for(200, 0.006), speed_for(75, 0.008)       # nominal long shot, pessimistic short one
    cfgs = [("rev C.2: SZW-25, 0.53 L, 22.5 in barrel", 0.53, 12, 0.05, 22.5),
            ("SZW-25, 2.0 L, 36 in", 2.0, 12, 0.05, 36), ("SZW-25, 2.0 L, 48 in", 2.0, 12, 0.05, 48),
            ("SZW-25, 3.8 L (old 1 gal tank), 36 in", 3.8, 12, 0.05, 36),
            ("QE5 QEV (Cv 6.6, 10 ms), 1.0 L, 30 in", 1.0, 6.6, 0.01, 30),
            ("QE5 QEV (Cv 6.6, 20 ms), 2.0 L, 30 in", 2.0, 6.6, 0.02, 30)]
    print(f"\nconfig | m/s at 110 psi | range ft (CdA .004/.006/.008) | psi for 200 ft | psi for 75 ft | "
          f"tank L for 1x200 + 6x75 (shop air at 150 / 190 psi)")
    for name, vc, cv, to, b in cfgs:
        v = shot(vc, 110, to, cv, b)
        rs = "/".join(f"{range_ft(v, c):.0f}" for c in (0.004, 0.006, 0.008))
        p2, p7 = psi_for(v200, vc, cv, to, b), psi_for(v75, vc, cv, to, b)
        tanks = " / ".join(f"{tank_l_needed(vc, p2, p7, p0):.1f}" for p0 in (150, 190)) if p2 else "-"
        print(f"{name:40s} | {v:4.1f} | {rs:11s} | {('%3.0f' % p2) if p2 else 'n/a'} | {p7:3.0f} | {tanks}")

    # Rev D.1 proposal (Micah, 2026-11-03): both chambers are 3 in Sch 40 between 3 x 1 reducing couplings. Top cannon:
    # 12 in nipple (~1.59 L) on a U.S. Solid HSV04 (1 in, Cv 11.67, pilot, 725 psi), so it can run to 190 psi; bottom:
    # 10 in nipple (~1.35 L) on the old SZW-25 (110 psi cap). Both barrels the same length. (Rev D had the old 1 gal
    # tank on top; Micah found it too big.)
    # Targets: 200 ft from the top cannon; 120 ft shots, 6 per cannon (12) per tank charge, 10 each (20) ideally.
    # The HSV04's opening time isn't published, so 50 and 80 ms bracket it.
    v120 = speed_for(120, 0.008)                                   # pessimistic drag for the everyday shot
    top, bot = 1.59, 1.35
    print(f"\nRev D: 120 ft needs {v120:.1f} m/s (CdA .008), 200 ft {v200:.1f} (CdA .006)")
    for b in (30, 36, 42, 48):
        for to in (0.05, 0.08):
            vt = shot(top, 200, to, 11.67, b)
            p2 = psi_for(v200, top, 11.67, to, b, hi=200.0)
            print(f"  barrel {b} in, HSV04 {to * 1000:.0f} ms: top {vt:4.1f} m/s at 200 psi = "
                  f"{range_ft(vt, 0.006):3.0f} ft; 200 ft at {('%3.0f psi' % p2) if p2 else 'n/a'}; "
                  f"120 ft at {psi_for(v120, top, 11.67, to, b, hi=200.0):3.0f} psi")
        p_b = psi_for(v120, bot, 12, 0.05, b)
        print(f"  barrel {b} in, bottom: {shot(bot, 110, 0.05, 12, b):4.1f} m/s at 110 psi; 120 ft at {p_b:3.0f} psi")

    def tank_for(n_each, p0, p_top, p_bot, k=1.15):
        """Tank (L) for n_each 120 ft shots per cannon, alternating, k = penalty for tanks cooling as they empty."""
        lo, hi = 1.0, 300.0
        for _ in range(40):
            vt = 0.5 * (lo + hi)
            pt, ok = p0, True
            for _ in range(n_each):
                for vc, ps in ((top, p_top), (bot, p_bot)):
                    ok = ok and pt >= ps + 5
                    pt -= k * vc * ps / vt
            lo, hi = (lo, vt) if ok else (vt, hi)
        return hi

    b = 36
    p_bot = psi_for(v120, bot, 12, 0.05, b)
    print(f"\nTank volume for 120 ft shots, {b} in barrels (6+6 / 10+10):")
    for to in (0.05, 0.08):
        p_top = psi_for(v120, top, 11.67, to, b)
        row = "  ".join(f"{p0} psi: {tank_for(6, p0, p_top, p_bot):4.1f} / {tank_for(10, p0, p_top, p_bot):4.1f} L"
                        for p0 in (150, 175, 200))
        print(f"  HSV04 {to * 1000:.0f} ms (top at {p_top:.0f} psi, bottom at {p_bot:.0f}):  {row}")

    def shots_per_charge(vt, p0, p_top, p_bot, k=1.15):
        pt, n = p0, 0
        while True:
            for vc, ps in ((top, p_top), (bot, p_bot)):
                if pt < ps + 5:
                    return n
                pt -= k * vc * ps / vt
                n += 1

    print("\n120 ft shots per charge, both cannons alternating (charged to 150 / 175 / 200 psi):")
    for vt, name in ((12, "two side 6 L tanks"), (18, "+ a third 6 L"), (21.5, "+ Viair 2.5 gal"), (23.4, "+ 3 gal")):
        row = "   ".join(f"HSV04 {to * 1000:.0f} ms: " + " / ".join(
            str(shots_per_charge(vt, p0, psi_for(v120, top, 11.67, to, b, hi=200.0), p_bot)) for p0 in (150, 175, 200))
            for to in (0.05, 0.08))
        print(f"  {name:20s} {vt:4.1f} L   {row}")
