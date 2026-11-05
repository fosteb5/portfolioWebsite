# Motors and 18 inch propellers. Run after td_lib.py and td_build.py.

SEAT_Z = ARM_Z + TUBE_R + 0.006     # top of the motor mount, in arm space
PROP_Z = 0.046                      # prop hub height above the seat


def build_motor(m, col, arm, i):
    mot = empty(f'TD_Motor{i}', col, arm, loc=(MOTOR_R, 0, SEAT_Z))
    # stator base with mounting ribs
    bm = bmesh.new()
    cyl(bm, 0.029, 0.006, loc=(0, 0, 0.003), segs=48)
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        box(bm, (0.012, 0.064, 0.003), loc=(0, 0, 0.0015), rot=(0, 0, a))
    part(f'TD_MotorBase{i}', bm, col, m['gunmetal'], mot, bevel=0.0008)
    # copper windings on the stator teeth
    bm = bmesh.new()
    for k in range(24):
        a = TAU * k / 24
        box(bm, (0.009, 0.0052, 0.017), loc=(0.0205 * math.cos(a), 0.0205 * math.sin(a), 0.0155), rot=(0, 0, a))
    w = part(f'TD_Windings{i}', bm, col, m['copper'], mot, bevel=0.0018, segs=3)
    bm = bmesh.new()
    cyl(bm, 0.0145, 0.02, loc=(0, 0, 0.016), segs=32)
    part(f'TD_StatorCore{i}', bm, col, m['magnet'], mot, bevel=0.0005)
    # the bell: side wall, magnets on its inside, and a vented top
    bm = bmesh.new()
    tube(bm, 0.0325, 0.0303, 0.024, loc=(0, 0, 0.0195), segs=64)
    part(f'TD_Bell{i}', bm, col, m['bell'], mot, bevel=0.0005)
    bm = bmesh.new()
    tube(bm, 0.0303, 0.0282, 0.02, loc=(0, 0, 0.0195), segs=64)
    part(f'TD_Magnets{i}', bm, col, m['magnet'], mot)
    bm = bmesh.new()
    tube(bm, 0.0325, 0.026, 0.003, loc=(0, 0, 0.033), segs=64)
    cyl(bm, 0.012, 0.004, loc=(0, 0, 0.0335), segs=40)
    for k in range(6):
        a = TAU * k / 6 + (i % 2) * 0.2
        box(bm, (0.017, 0.0055, 0.003), loc=(0.0195 * math.cos(a), 0.0195 * math.sin(a), 0.033), rot=(0, 0, a + 0.35))
    part(f'TD_BellTop{i}', bm, col, m['bell'], mot, bevel=0.0006)
    bm = bmesh.new()
    tube(bm, 0.0331, 0.0322, 0.004, loc=(0, 0, 0.0105), segs=64)
    tube(bm, 0.0125, 0.0105, 0.0042, loc=(0, 0, 0.0362), segs=40)
    part(f'TD_MotorTrim{i}', bm, col, m['gold'], mot, bevel=0.0003)
    # shaft, prop adapter and its screws
    bm = bmesh.new()
    cyl(bm, 0.0105, 0.006, loc=(0, 0, 0.039), segs=40)
    for k in range(4):
        a = TAU * k / 4
        cyl(bm, 0.0018, 0.0016, loc=(0.0072 * math.cos(a), 0.0072 * math.sin(a), 0.0428), segs=12)
    part(f'TD_Adapter{i}', bm, col, m['black_steel'], mot, bevel=0.0004)
    return mot


def _naca(x, tc, camber=0.04, p=0.4):
    yt = 5 * tc * (0.2969 * math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1036 * x ** 4)
    yc = camber / p ** 2 * (2 * p * x - x * x) if x < p else camber / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x * x)
    return yc + yt, yc - yt


def _chord(r):
    u = r / PROP_R
    if u < 0.3:
        c = 0.024 + (0.047 - 0.024) * ((u - 0.1) / 0.2) ** 0.7 if u > 0.1 else 0.024
    else:
        c = 0.047 - (0.047 - 0.024) * (u - 0.3) / 0.62
    if u > 0.9:  # rounded tip
        c *= math.sqrt(max(0.0, 1 - ((u - 0.9) / 0.1) ** 2)) * 0.85 + 0.15 * (1 - (u - 0.9) / 0.1)
    return max(c, 0.0025)


def blade_bm(bm, flip=False, start_angle=0.0, mat_tip=1):
    """One twisted, tapered blade along +X. The leading edge leads in the direction of spin."""
    N, P = 34, 22
    rs = [0.019 + (PROP_R - 0.019) * (1 - math.cos(math.pi / 2 * k / (N - 1))) ** 0.8 for k in range(N)]
    rs[-1] = PROP_R
    xs = [0.5 * (1 - math.cos(math.pi * j / (P - 1))) for j in range(P)]
    rings = []
    for r in rs:
        u = r / PROP_R
        c = _chord(r)
        tc = 0.4 - 0.28 * min(1, (u - 0.083) / 0.12) if u < 0.2 else 0.12 - 0.04 * u
        beta = min(math.radians(30), math.atan(0.152 / (TAU * r)))
        pts = []
        for j in range(P):          # upper surface, leading to trailing
            yu, _ = _naca(xs[j], tc)
            pts.append((xs[j], yu))
        for j in range(P - 2, 0, -1):   # lower surface back to the leading edge
            _, yl = _naca(xs[j], tc)
            pts.append((xs[j], yl))
        ring = []
        for (x, y) in pts:
            cx = (0.3 - x) * c       # +: towards the leading edge
            cz = y * c
            yy = cx * math.cos(beta) - cz * math.sin(beta)
            zz = cx * math.sin(beta) + cz * math.cos(beta)
            if flip:
                yy = -yy
            ca, sa = math.cos(start_angle), math.sin(start_angle)
            ring.append(bm.verts.new((r * ca - yy * sa, r * sa + yy * ca, zz)))
        rings.append(ring)
    n = len(rings[0])
    faces = []
    for a in range(len(rings) - 1):
        for j in range(n):
            k = (j + 1) % n
            q = (rings[a][j], rings[a][k], rings[a + 1][k], rings[a + 1][j])
            f = bm.faces.new(q if not flip else tuple(reversed(q)))
            if 0.9 < rs[a] / PROP_R < 0.94:
                f.material_index = mat_tip
            faces.append(f)
    for ring, rev in ((rings[0], True), (rings[-1], False)):
        f = bm.faces.new(list(reversed(ring)) if rev != flip else ring)
        faces.append(f)
    return faces


def build_prop(m, col, mot, i):
    ccw = i % 2 == 0
    prop = empty(f'TD_Prop{i}', col, mot, loc=(0, 0, PROP_Z))
    spin = empty(f'TD_PropSpin{i}', col, prop)
    bm = bmesh.new()
    blade_bm(bm, flip=not ccw, start_angle=0.0)
    blade_bm(bm, flip=not ccw, start_angle=math.pi)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    part(f'TD_Blades{i}', bm, col, [m['carbon'], m['plastic_white']], spin, angle=50)
    bm = bmesh.new()
    cyl(bm, 0.0175, 0.012, loc=(0, 0, 0), segs=48)
    part(f'TD_PropHub{i}', bm, col, m['carbon'], spin, bevel=0.0015, segs=3)
    bm = bmesh.new()
    sphere(bm, 0.0115, loc=(0, 0, 0.006), scale=(1, 1, 0.75), segs=32, rings=16)
    cyl(bm, 0.0115, 0.002, loc=(0, 0, 0.007), segs=32)
    part(f'TD_Spinner{i}', bm, col, m['gold'], spin)
    # a soft disc that stands in for the blades while they spin
    bm = bmesh.new()
    cyl(bm, PROP_R, 0.0008, loc=(0, 0, 0.001), segs=96)
    blur = part(f'TD_PropBlur{i}', bm, col, m['prop_blur'], prop, smooth=False)
    blur.hide_render = True
    return prop


def prop_blur_material():
    """Coverage falls off with radius like a real blurred prop: dense near the hub, faint at the tip, with the tip stripe as a ring."""
    m, nt, out = node_mat('TD_PropBlur')
    m.surface_render_method = 'BLENDED'
    m.use_transparency_overlap = False
    tc = add(nt, 'ShaderNodeTexCoord', (-1200, 0))
    vl = add(nt, 'ShaderNodeVectorMath', (-1000, 0), operation='LENGTH')
    link(nt, tc.outputs['Object'], vl.inputs[0])
    r = vl.outputs['Value']
    u = math_node(nt, 'DIVIDE', r, PROP_R, (-800, 0))
    # base coverage: 2 blades x chord / circumference, scaled for a slow shutter
    ramp = add(nt, 'ShaderNodeValToRGB', (-600, 0))
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.08, (0.62, 0.62, 0.62, 1)
    els[1].position, els[1].color = 1.0, (0.0, 0.0, 0.0, 1)
    for pos, v in ((0.2, 0.42), (0.45, 0.2), (0.8, 0.1), (0.9, 0.08), (0.905, 0.2), (0.935, 0.2), (0.94, 0.06), (0.995, 0.03)):
        e = els.new(pos)
        e.color = (v, v, v, 1)
    link(nt, u, ramp.inputs['Fac'])
    # fine radial streaks so the disc reads as motion, not a solid plate
    wave = add(nt, 'ShaderNodeTexWave', (-800, -260), wave_type='RINGS')
    wave.inputs['Scale'].default_value = 26
    wave.inputs['Distortion'].default_value = 3
    wave.inputs['Detail'].default_value = 3
    link(nt, tc.outputs['Object'], wave.inputs['Vector'])
    wr = add(nt, 'ShaderNodeMapRange', (-600, -260))
    wr.inputs['To Min'].default_value = 0.75
    wr.inputs['To Max'].default_value = 1.15
    link(nt, wave.outputs['Fac'], wr.inputs['Value'])
    alpha = math_node(nt, 'MULTIPLY', ramp.outputs['Color'], wr.outputs[0], (-350, 0))
    stripe = add(nt, 'ShaderNodeMapRange', (-600, 200))
    stripe.inputs['From Min'].default_value = 0.9
    stripe.inputs['From Max'].default_value = 0.935
    stripe.interpolation_type = 'SMOOTHERSTEP'
    link(nt, u, stripe.inputs['Value'])
    stripe2 = math_node(nt, 'COMPARE', u, 0.9175, (-400, 300))
    nt.nodes[-1].inputs[2].default_value = 0.0175
    col = add(nt, 'ShaderNodeMix', (-200, 200), data_type='RGBA')
    sock(col.inputs, 'A_Color').default_value = (0.02, 0.021, 0.024, 1)
    sock(col.inputs, 'B_Color').default_value = (0.7, 0.7, 0.68, 1)
    link(nt, stripe2, sock(col.inputs, 'Factor_Float'))
    p = add(nt, 'ShaderNodeBsdfPrincipled', (100, 0))
    p.inputs['Roughness'].default_value = 0.35
    p.inputs['Coat Weight'].default_value = 0.4
    link(nt, sock(col.outputs, 'Result_Color'), p.inputs['Base Color'])
    link(nt, alpha, p.inputs['Alpha'])
    link(nt, p.outputs[0], out.inputs[0])
    return m


def build_propulsion(m, arms):
    col = coll('TD Drone')
    m['prop_blur'] = prop_blur_material()
    motors, props = [], []
    for i, arm in enumerate(arms):
        mot = build_motor(m, col, arm, i)
        motors.append(mot)
        props.append(build_prop(m, col, mot, i))
    return motors, props
