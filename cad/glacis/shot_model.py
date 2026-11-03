"""Glacis chamber sizing. Lumped shot model: isentropic chamber -> valve (Cv 12, area ramps open over t_open) -> barrel gas behind
the shirt (energy balance) -> shirt (mass, friction). Prints exit speed and air used per shot vs chamber size."""
import math
g, R = 1.4, 287.0
cv_air, cp_air = R / (g - 1), g * R / (g - 1)
PATM, T0 = 101325.0, 300.0
IN = 0.0254
A_B = math.pi / 4 * (2.75 * IN) ** 2          # barrel bore
L_T = 0.5715 - 0.15                           # travel: 22.5 in barrel minus a 150 mm shirt
V_DEAD = 0.08e-3                              # nipple + breech adapter bore + gap behind the shirt
A_V = 12 / 38.0 * IN ** 2                     # valve effective area from Cv 12
PSI_CH = g ** 0.5 * (2 / (g + 1)) ** ((g + 1) / (2 * (g - 1)))


def flow(p1, T1, p2):
    r = max(p2 / p1, 1e-9)
    if r <= (2 / (g + 1)) ** (g / (g - 1)):
        psi = PSI_CH
    elif r >= 1:
        return 0.0
    else:
        psi = math.sqrt(2 * g / (g - 1) * (r ** (2 / g) - r ** ((g + 1) / g)))
    return p1 / math.sqrt(R * T1) * psi


def shot(vc_l, psig=110, t_open=0.05, m_s=0.25, f_fric=15.0):
    V1 = vc_l * 1e-3
    p10 = psig * 6894.76 + PATM
    m10 = p10 * V1 / (R * T0)
    m1, T1 = m10, T0
    V2 = V_DEAD
    m2 = PATM * V2 / (R * T0)
    U2 = m2 * cv_air * T0
    x = v = t = 0.0
    dt = 2e-6
    while x < L_T and t < 0.5:
        p1 = p10 * (m1 / m10) ** g
        T1 = T0 * (p1 / p10) ** ((g - 1) / g)
        T2 = U2 / (m2 * cv_air)
        p2 = m2 * R * T2 / V2
        a = min(1.0, t / t_open) * A_V
        dm = a * flow(p1, T1, p2) * dt
        F = (p2 - PATM) * A_B
        acc = (F - f_fric) / m_s if (v > 0 or F > f_fric) else 0.0
        v_new = max(0.0, v + acc * dt)
        dx = 0.5 * (v + v_new) * dt
        dV = A_B * dx
        m1 -= dm
        m2 += dm
        U2 += dm * cp_air * T1 - p2 * dV
        V2 += dV
        x += dx
        v = v_new
        t += dt
    return v, t, (m10 - m1), m10


def shots_per_charge(vc_l, psig=110, tanks_l=12.0, tank_psig=200.0):
    n, pt = 0, tank_psig
    while pt >= psig:
        pt -= vc_l * psig / tanks_l
        n += 1
    return 2 + n - 1                                # two chambers start loaded


if __name__ == "__main__":
    print("chamber L | exit m/s (valve 10 ms / 50 ms / 80 ms) | J at 50 ms | shots per charge")
    for vc in (0.5, 0.53, 0.64, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.8):
        vs = [shot(vc, t_open=to)[0] for to in (0.01, 0.05, 0.08)]
        print(f"{vc:5.2f}     | {vs[0]:5.1f} / {vs[1]:5.1f} / {vs[2]:5.1f}            | {0.5 * 0.25 * vs[1] ** 2:6.0f}     | "
              f"{shots_per_charge(vc)}")
