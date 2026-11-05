# Scene modes and animation states for the tethered drone renders.
#   wash:   the drone climbs to a window on its tether and sprays it clean (opaque background)
#   studio: the breakdown, on a transparent background

def show(col_name, on):
    c = bpy.data.collections.get(col_name)
    if c:
        c.hide_render = not on
        c.hide_viewport = not on


def set_mode(mode):
    sc = bpy.context.scene
    wash = mode == 'wash'
    show('TD Facade', wash)
    show('TD Spray', wash)
    show('TD Studio', not wash)
    sc.world = bpy.data.worlds['TD_SkyWorld' if wash else 'TD_StudioWorld']
    sc.camera = bpy.data.objects['TD_WashCam' if wash else 'TD_StudioCam']
    sc.render.film_transparent = not wash
    set_spinning(wash)


def set_spinning(on, angle=0.0):
    """Spinning props are drawn as blurred discs; stopped ones as blades."""
    for i in range(6):
        bpy.data.objects[f'TD_PropBlur{i}'].hide_render = not on
        bpy.data.objects[f'TD_PropBlur{i}'].hide_viewport = not on
        for n in (f'TD_Blades{i}', f'TD_PropHub{i}'):
            ob = bpy.data.objects[n]
            ob.hide_render = on
            ob.hide_viewport = on
        bpy.data.objects[f'TD_PropSpin{i}'].rotation_euler = (0, 0, angle * (1 if i % 2 == 0 else -1) + i * 0.7)


# ---------------------------------------------------------------- helpers

def hermite(keys, p):
    ps = [k[0] for k in keys]
    n = len(keys)
    i = max(0, min(n - 2, next((j for j in range(n - 1) if ps[j + 1] >= p), n - 2)))
    t = 0.0 if ps[i + 1] == ps[i] else (p - ps[i]) / (ps[i + 1] - ps[i])
    t = max(0.0, min(1.0, t))
    out = []
    for c in range(1, len(keys[0])):
        v = [k[c] for k in keys]

        def tan(j):
            a, b = max(0, j - 1), min(n - 1, j + 1)
            return (v[b] - v[a]) / (ps[b] - ps[a]) * (ps[i + 1] - ps[i])
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1
        h10 = t ** 3 - 2 * t ** 2 + t
        h01 = -2 * t ** 3 + 3 * t ** 2
        h11 = t ** 3 - t ** 2
        out.append(h00 * v[i] + h10 * tan(i) + h01 * v[i + 1] + h11 * tan(i + 1))
    return out


def ease(p, a, b):
    u = min(1.0, max(0.0, (p - a) / (b - a)))
    return u * u * (3 - 2 * u)


def window(p, a, b, c, d):
    return ease(p, a, b) * (1 - ease(p, c, d))
