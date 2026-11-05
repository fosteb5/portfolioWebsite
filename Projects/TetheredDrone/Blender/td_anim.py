# Animation states, one function per sequence, each taking progress p from 0 to 1.
# render_wash() and render_breakdown() write the frames for the site's scroll animations.
import os

X0, X1 = 0.3, 3.0          # where the sweep starts and ends along the glass
STANDOFF = -1.22            # drone centre to glass: puts the nozzles about 0.39 m off it
WASH_FRAMES = 120
BREAK_FRAMES = 132


def smoother(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (u * 6 - 15) + 10)


def smoother_acc(u):
    """Second derivative of smoother(), normalised to peak at 1."""
    if u <= 0 or u >= 1:
        return 0.0
    return (60 * u - 180 * u * u + 120 * u ** 3) / 5.7735


# ---------------------------------------------------------------- washing

WASH_CAM = [  # p, camera x y z, target x y z (z relative to the working height)
    (0.00, -1.9, -2.9, -1.45, 0.4, -0.85, -1.3),
    (0.14, -1.95, -2.85, -0.75, 0.4, -0.8, -0.55),
    (0.28, -2.0, -2.8, -0.25, 0.45, -0.7, -0.05),
    (0.40, -1.85, -2.75, -0.22, 0.55, -0.62, -0.04),
    (0.66, -0.75, -2.8, -0.22, 1.7, -0.6, -0.04),
    (0.90, 0.2, -2.95, -0.2, 2.6, -0.55, -0.03),
    (1.00, -0.2, -3.6, -0.15, 2.1, -0.4, -0.03),
]


def drone_pose(p):
    W = WORK_Z
    rise = smoother(p / 0.25)
    z = W - 1.6 * (1 - rise)
    u = (p - 0.4) / 0.52
    x = X0 + (X1 - X0) * smoother(u)
    y = STANDOFF - 0.45 * (1 - smoother((p - 0.1) / 0.22))
    yaw = math.radians(-24) * (1 - smoother((p - 0.08) / 0.26))
    bob = 0.006 * math.sin(p * 31.0) + 0.004 * math.sin(p * 53.0 + 1.0)
    # it leans into each move: roll with the sweep, pitch with the approach, and a little hover wobble
    roll = math.radians(3.8) * smoother_acc(u) + math.radians(0.35) * math.sin(p * 41.0)
    pitch = math.radians(2.5) * smoother_acc((p - 0.1) / 0.22) - math.radians(1.6) * smoother_acc(p / 0.25) * 0.4 \
        + math.radians(0.3) * math.sin(p * 37.0 + 0.5)
    return Vector((x, y, z + bob)), (pitch, roll, yaw)


def reset_explode():
    ob = bpy.data.objects
    for name in EXPLODE:
        ob[name].location = _base(ob[name])
    for i in range(6):
        ob[f'TD_Arm{i}'].location = (0, 0, 0)
        for n in (f'TD_Motor{i}', f'TD_Prop{i}'):
            ob[n].location = _base(ob[n])


def set_wash_state(p, frame_seed=0):
    W = WORK_Z
    reset_explode()
    root = bpy.data.objects['TD_Drone']
    pos, (pitch, roll, yaw) = drone_pose(p)
    root.location = pos
    root.rotation_euler = (pitch, roll, yaw)
    set_spinning(True, angle=p * 400.0)
    cx, cy, cz, tx, ty, tz = hermite(WASH_CAM, p)
    bpy.data.objects['TD_WashCam'].location = (cx, cy, W + cz)
    bpy.data.objects['TD_WashTarget'].location = (tx, ty, W + tz)
    bpy.context.view_layer.update()

    amount = ease(p, 0.33, 0.4) * (1 - ease(p, 0.92, 0.955))
    nozzle = root.matrix_world @ Vector(NOZZLE_LOCAL[1])
    spraying = p >= 0.33
    x_now = min(nozzle.x, X1 + 0.02) if spraying else X0 - 2.0
    set_clean(X0 - 0.02, x_now, W - 0.036, 0.3 * ease(p, 0.34, 0.4), 1.0, amount)
    set_spray(amount, 1000 + frame_seed)
    bpy.data.materials['TD_Mist'].node_tree.nodes['Amount'].outputs[0].default_value = amount

    # the tether trails a little behind the drone's moves on its way down to the base station
    hub = root.matrix_world @ Vector((0, 0, HUB_TOP - 0.09))
    vx = (drone_pose(min(1, p + 0.01))[0].x - drone_pose(max(0, p - 0.01))[0].x) / 0.02
    lag = Vector((-vx * 0.06, 0.0, 0.0))
    set_tether(hub, hub + Vector((0, 0, -1.4)) + lag, Vector((pos.x - 0.8, -2.0, W - 9.0)) + lag * 2,
               Vector((-1.5, -4.5, 0.0)), phase=p * 2.0)


# ---------------------------------------------------------------- breakdown

# Camera keys: progress, azimuth (deg, 0 is +X, 90 is the front), elevation (deg), distance (m), target x y z
BREAK_CAM = [
    (0.00, -42, 22, 2.55, -0.1, 0.22, -0.06),
    (0.10, -30, 28, 2.45, -0.06, 0.16, 0.04),
    (0.20, 8, 12, 1.3, 0.3, 0.52, 0.27),
    (0.28, 22, 10, 1.2, 0.3, 0.52, 0.28),
    (0.37, -12, 50, 0.34, 0.0, 0.045, 0.335),
    (0.47, -42, 40, 0.3, 0.0, 0.045, 0.34),
    (0.57, -75, 36, 0.42, 0.0, -0.058, 0.19),
    (0.67, 60, 12, 0.24, 0.0, 0.26, 0.14),
    (0.72, 30, 6, 1.45, 0.0, 0.12, -0.02),
    (0.79, -24, -16, 1.45, 0.0, 0.08, -0.17),
    (0.87, -40, -8, 1.6, 0.0, 0.12, -0.22),
    (1.00, -38, 15, 3.3, 0.08, 0.06, 0.08),
]

# Each part group: (offset when fully out, start, end of its move)
EXPLODE = {
    'TD_GrpCanopy': ((0, 0, 0.5), 0.04, 0.14),
    'TD_GrpFC': ((0, 0, 0.3), 0.28, 0.37),
    'TD_GrpPi': ((0, 0, 0.15), 0.49, 0.57),
    'TD_GrpGPS': ((0, -0.05, 0.42), 0.07, 0.17),
    'TD_GrpCam': ((0, 0.13, 0.08), 0.56, 0.64),
    'TD_GrpPDB': ((0, 0, -0.05), 0.69, 0.77),
    'TD_GrpDCDC': ((0, 0, -0.13), 0.7, 0.78),
    'TD_GrpHub': ((0, 0, -0.23), 0.71, 0.79),
    'TD_GrpWater': ((0, 0.13, -0.08), 0.72, 0.8),
    'TD_GrpGear': ((0, 0, -0.27), 0.73, 0.81),
}
ARM_OUT = (0.12, 0.12, 0.22)       # arms slide out
MOTOR_UP = (0.11, 0.13, 0.23)      # motors rise off their mounts
PROP_UP = (0.25, 0.12, 0.22)       # props rise further


def _base(ob):
    if 'base' not in ob:
        ob['base'] = tuple(ob.location)
    return Vector(ob['base'])


def set_breakdown_state(p):
    ob = bpy.data.objects
    root = ob['TD_Drone']
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    set_spinning(False)
    for name, (off, a, b) in EXPLODE.items():
        o = ob[name]
        o.location = _base(o) + Vector(off) * smoother((p - a) / (b - a))
    e_arm = smoother((p - ARM_OUT[1]) / (ARM_OUT[2] - ARM_OUT[1])) * ARM_OUT[0]
    e_mot = smoother((p - MOTOR_UP[1]) / (MOTOR_UP[2] - MOTOR_UP[1])) * MOTOR_UP[0]
    u_prop = smoother((p - PROP_UP[1]) / (PROP_UP[2] - PROP_UP[1]))
    for i in range(6):
        a = ARM_ANGLES[i]
        ob[f'TD_Arm{i}'].location = (math.cos(a) * e_arm, math.sin(a) * e_arm, 0)
        m = ob[f'TD_Motor{i}']
        m.location = _base(m) + Vector((0, 0, e_mot))
        pr = ob[f'TD_Prop{i}']
        pr.location = _base(pr) + Vector((0, 0, PROP_UP[0] * u_prop))
        ob[f'TD_PropSpin{i}'].rotation_euler = (0, 0, (1 if i % 2 == 0 else -1) * u_prop * math.radians(70) + i * 0.7)
    az, el, dist, tx, ty, tz = hermite(BREAK_CAM, p)
    tgt = ob['TD_StudioTarget']
    tgt.location = (tx, ty, tz)
    a, e = math.radians(az), math.radians(el)
    ob['TD_StudioCam'].location = tgt.location + Vector((dist * math.cos(e) * math.cos(a), dist * math.cos(e) * math.sin(a), dist * math.sin(e)))
    bpy.context.view_layer.update()
    # the tether hangs from the hub wherever the hub has gone, and runs out of the bottom of the frame
    hub = root.matrix_world @ (ob['TD_GrpHub'].location + Vector((0, 0, -0.09)))
    set_tether(hub, hub + Vector((0, 0, -0.35)), hub + Vector((0.02, 0.06, -0.8)), hub + Vector((0.05, 0.12, -1.6)), phase=0.0)


def studio_settings(w=1600, h=900, samples=64):
    sc = bpy.context.scene
    set_mode('studio')
    render_settings(sc, w, h, samples)
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = 'RGBA'
    bpy.data.objects['TD_StudioCam'].data.lens = 50


def render_breakdown(frames=None, out=None, w=1600, h=900, samples=64):
    out = out or os.path.join(R_DIR, 'renders', 'breakdown')
    os.makedirs(out, exist_ok=True)
    studio_settings(w, h, samples)
    for f in frames or range(1, BREAK_FRAMES + 1):
        set_breakdown_state((f - 1) / (BREAK_FRAMES - 1))
        _render(os.path.join(out, f'{f:03d}.png'))


# ---------------------------------------------------------------- rendering

def _render(path):
    bpy.context.view_layer.update()
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def wash_settings(w=1600, h=900, samples=64):
    sc = bpy.context.scene
    set_mode('wash')
    render_settings(sc, w, h, samples)
    sc.render.film_transparent = False
    sc.render.image_settings.color_mode = 'RGB'


def render_wash(frames=None, out=None, w=1600, h=900, samples=64):
    out = out or os.path.join(R_DIR, 'renders', 'wash')
    os.makedirs(out, exist_ok=True)
    wash_settings(w, h, samples)
    for f in frames or range(1, WASH_FRAMES + 1):
        set_wash_state((f - 1) / (WASH_FRAMES - 1), f)
        _render(os.path.join(out, f'{f:03d}.png'))


def render_hero(p=0.74, samples=128):
    """Full-size stills: the drone mid-sweep, and the finished exploded view on a transparent background."""
    wash_settings(1920, 1080, samples)
    set_wash_state(p, 7)
    _render(os.path.join(R_DIR, 'renders', 'tethered-drone-hero.png'))
    studio_settings(1920, 1080, samples)
    set_breakdown_state(1.0)
    _render(os.path.join(R_DIR, 'renders', 'tethered-drone-exploded.png'))


R_DIR = r"C:\Users\foste\OneDrive\Resume\portfolioWebsite\Projects\TetheredDrone\Blender"
