# Builds the tethered hexacopter. Run inside Blender with td_lib.py loaded first.
# Units are metres. The drone faces +Y, the spray lance points forward, and arm 0 points along +X.
# Sizes are a concept for the capstone airframe, not measurements of the real build.

ARM_ANGLES = [math.radians(a) for a in (0, 60, 120, 180, 240, 300)]
MOTOR_R = 0.55          # centre to motor, so 1.1 m motor to motor across
PROP_R = 0.2286         # 18 inch propellers
TUBE_R = 0.0125         # 25 mm carbon arm tubes
PLATE_T = 0.003
ARM_Z = PLATE_T / 2 + TUBE_R + 0.0003
TOP_Z = ARM_Z + TUBE_R + 0.0003 + PLATE_T / 2
GOLD = (0.78, 0.50, 0.12)


def materials():
    mats = {}
    mats['carbon'] = carbon('TD_Carbon', coat=1.0, coat_rough=0.05, rough=(0.4, 0.65), spec=0.25)
    mats['carbon_tube'] = carbon('TD_CarbonTube', scale=330.0, coat=1.0, coat_rough=0.04, rough=(0.35, 0.6), spec=0.25)
    mats['gunmetal'] = brushed('TD_Gunmetal', (0.075, 0.08, 0.088), rough=0.32)
    mats['alu'] = brushed('TD_Aluminium', (0.62, 0.63, 0.65), rough=0.22)
    mats['gold'] = brushed('TD_GoldAnodised', GOLD, rough=0.24, aniso=0.15)
    mats['bell'] = brushed('TD_MotorBell', (0.04, 0.042, 0.047), rough=0.3, aniso=0.25, scale=1400)
    mats['steel'] = principled('TD_Steel', (0.55, 0.56, 0.58), 1.0, 0.18)
    mats['black_steel'] = principled('TD_BlackOxide', (0.03, 0.03, 0.032), 1.0, 0.35)
    mats['copper'] = principled('TD_Copper', (0.93, 0.48, 0.28), 1.0, 0.25, coat=0.6, coat_rough=0.1)
    mats['magnet'] = principled('TD_Magnet', (0.2, 0.2, 0.21), 1.0, 0.35)
    mats['brass'] = principled('TD_Brass', (0.85, 0.62, 0.28), 1.0, 0.26)
    mats['rubber'] = principled('TD_Rubber', (0.025, 0.025, 0.027), 0.0, 0.62)
    mats['plastic'] = principled('TD_BlackPlastic', (0.03, 0.031, 0.034), 0.0, 0.42)
    mats['plastic_white'] = principled('TD_WhitePlastic', (0.75, 0.74, 0.7), 0.0, 0.4)
    mats['shrink'] = principled('TD_HeatShrink', (0.02, 0.022, 0.026), 0.0, 0.5, coat=0.3, coat_rough=0.3)
    mats['foam'] = principled('TD_Foam', (0.04, 0.04, 0.042), 0.0, 0.85)
    mats['wire_red'] = principled('TD_WireRed', (0.55, 0.04, 0.03), 0.0, 0.35, coat=0.4)
    mats['wire_black'] = principled('TD_WireBlack', (0.02, 0.02, 0.022), 0.0, 0.35, coat=0.4)
    mats['wire_yellow'] = principled('TD_WireYellow', (0.75, 0.55, 0.05), 0.0, 0.35, coat=0.4)
    mats['wire_blue'] = principled('TD_WireBlue', (0.03, 0.12, 0.55), 0.0, 0.35, coat=0.4)
    mats['xt'] = principled('TD_XTYellow', (0.85, 0.62, 0.04), 0.0, 0.35)
    mats['jst'] = principled('TD_JST', (0.82, 0.78, 0.66), 0.0, 0.45)
    mats['pcb_black'] = principled('TD_PCBBlack', (0.012, 0.014, 0.016), 0.0, 0.28, coat=0.5, coat_rough=0.2)
    mats['pcb_green'] = principled('TD_PCBGreen', (0.02, 0.14, 0.05), 0.0, 0.3, coat=0.5, coat_rough=0.2)
    mats['enig'] = principled('TD_ENIG', (0.95, 0.72, 0.38), 1.0, 0.2)
    mats['silk'] = principled('TD_Silk', (0.85, 0.85, 0.82), 0.0, 0.6)
    mats['chip'] = principled('TD_ChipEpoxy', (0.025, 0.025, 0.027), 0.0, 0.45)
    mats['shield'] = brushed('TD_ShieldCan', (0.7, 0.71, 0.72), rough=0.18, aniso=0.3, scale=2000)
    mats['cap_tan'] = principled('TD_CapTan', (0.55, 0.42, 0.25), 0.0, 0.5)
    mats['cap_alu'] = principled('TD_CapCan', (0.55, 0.56, 0.6), 1.0, 0.25)
    mats['lens'] = principled('TD_Lens', (0.0, 0.0, 0.0), 0.0, 0.02, spec=1.0, coat=1.0)
    mats['led_red'] = principled('TD_LEDRed', (0.5, 0.02, 0.02), 0.0, 0.2, emit=(1.0, 0.05, 0.03), emit_strength=40)
    mats['led_green'] = principled('TD_LEDGreen', (0.02, 0.5, 0.1), 0.0, 0.2, emit=(0.1, 1.0, 0.25), emit_strength=40)
    mats['led_white'] = principled('TD_LEDWhite', (0.9, 0.9, 0.9), 0.0, 0.2, emit=(1.0, 0.95, 0.85), emit_strength=60)
    mats['led_status'] = principled('TD_LEDStatus', (0.1, 0.4, 0.9), 0.0, 0.2, emit=(0.2, 0.55, 1.0), emit_strength=12)
    mats['hose'] = principled('TD_Hose', (0.12, 0.42, 0.75), 0.0, 0.18, transmission=0.55, ior=1.5, coat=0.5)
    mats['cable'] = principled('TD_TetherCable', (0.018, 0.018, 0.02), 0.0, 0.48, coat=0.2, coat_rough=0.3)
    mats['canopy'] = principled('TD_Canopy', (0.05, 0.055, 0.06), 0.0, 0.04, alpha=0.24, spec=0.6, coat=0.6, coat_rough=0.02)
    mats['ffc'] = principled('TD_FFC', (0.85, 0.82, 0.74), 0.0, 0.35)
    mats['fan'] = principled('TD_FanBlack', (0.02, 0.02, 0.022), 0.0, 0.5)
    return mats


def plate_outline(r, flat=0.034):
    """A hexagon with its corners squared off where the arm clamps sit, then rounded."""
    pts = []
    for a in ARM_ANGLES:
        c, s = math.cos(a), math.sin(a)
        tx, ty = -s, c
        for side in (-1, 1):
            pts.append((r * c + side * flat * tx, r * s + side * flat * ty))
    return rounded_poly(pts, 0.012, 5)


def build_plates(m, col, body):
    # bottom plate, with lightening holes and the slot the lance and hoses pass through
    bm = bmesh.new()
    prism(bm, plate_outline(0.148), -PLATE_T / 2, PLATE_T / 2)
    bottom = part('TD_PlateBottom', bm, col, m['carbon'], body, angle=30)
    cuts = []
    for i, a in enumerate(ARM_ANGLES):
        bm = bmesh.new()
        ang = a + math.radians(30)
        outline = rounded_poly([(0.052, -0.022), (0.098, -0.032), (0.098, 0.032), (0.052, 0.022)], 0.008, 4)
        rot = [(x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)) for x, y in outline]
        prism(bm, rot, -0.02, 0.02)
        cuts.append(cutter(f'cut_b{i}', bm, col))
    bm = bmesh.new()
    cyl(bm, 0.016, 0.04, segs=40)
    cuts.append(cutter('cut_bc', bm, col))
    cut(bottom, cuts)
    bev(bottom, 0.0006, 2)

    # top plate, a little smaller, with a pattern of round holes
    bm = bmesh.new()
    prism(bm, plate_outline(0.142), TOP_Z - PLATE_T / 2, TOP_Z + PLATE_T / 2)
    top = part('TD_PlateTop', bm, col, m['carbon'], body, angle=30)
    cuts = []
    for i, a in enumerate(ARM_ANGLES):
        ang = a + math.radians(30)
        for k, (rr, rad) in enumerate(((0.108, 0.011), (0.082, 0.007))):
            bm = bmesh.new()
            cyl(bm, rad, 0.05, loc=(rr * math.cos(ang), rr * math.sin(ang), TOP_Z), segs=28)
            cuts.append(cutter(f'cut_t{i}{k}', bm, col))
    cut(top, cuts)
    bev(top, 0.0006, 2)

    # standoffs between the plates, and their screw heads
    bm = bmesh.new()
    heads = bmesh.new()
    for a in ARM_ANGLES:
        ang = a + math.radians(30)
        x, y = 0.125 * math.cos(ang), 0.125 * math.sin(ang)
        cyl(bm, 0.0045, TOP_Z - PLATE_T, loc=(x, y, TOP_Z / 2), segs=6)
        for z, sgn in ((TOP_Z + PLATE_T / 2, 1), (-PLATE_T / 2, -1)):
            cyl(heads, 0.0042, 0.0025, loc=(x, y, z + sgn * 0.00125), segs=24)
    part('TD_Standoffs', bm, col, m['gold'], body, angle=40, bevel=0.0004)
    part('TD_PlateScrews', heads, col, m['black_steel'], body, bevel=0.0005)


def build_arm(m, col, root, i):
    a = ARM_ANGLES[i]
    arm = empty(f'TD_Arm{i}', col, root, rot=(0, 0, a))
    # carbon tube from inside the plates out to the motor
    bm = bmesh.new()
    tube(bm, TUBE_R, TUBE_R - 0.0015, MOTOR_R - 0.045, loc=((MOTOR_R + 0.045) / 2, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=40)
    part(f'TD_ArmTube{i}', bm, col, m['carbon_tube'], arm, angle=20)

    # clamp block where the arm leaves the plates
    bm = bmesh.new()
    box(bm, (0.03, 0.04, TOP_Z - PLATE_T - 0.0006), loc=(0.125, 0, TOP_Z / 2))
    clamp = part(f'TD_ArmClamp{i}', bm, col, m['gunmetal'], arm, bevel=0.0015, segs=3)
    bm = bmesh.new()
    cyl(bm, TUBE_R + 0.0003, 0.05, loc=(0.125, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=40)
    cut(clamp, [cutter(f'cut_c{i}', bm, col)])

    # folding hinge: two blocks on a vertical pin, with a locking sleeve
    hinge = bmesh.new()
    box(hinge, (0.026, 0.034, 0.034), loc=(0.19, 0, ARM_Z))
    box(hinge, (0.026, 0.034, 0.034), loc=(0.218, 0, ARM_Z))
    h = part(f'TD_Hinge{i}', hinge, col, m['gunmetal'], arm, bevel=0.002, segs=3)
    bm = bmesh.new()
    cyl(bm, TUBE_R + 0.0003, 0.08, loc=(0.204, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=40)
    cut(h, [cutter(f'cut_h{i}', bm, col)])
    bm = bmesh.new()
    cyl(bm, 0.0035, 0.042, loc=(0.204, 0.012, ARM_Z), segs=20)
    cyl(bm, 0.0055, 0.003, loc=(0.204, 0.012, ARM_Z + 0.0215), segs=24)
    part(f'TD_HingePin{i}', bm, col, m['steel'], arm, bevel=0.0004)
    bm = bmesh.new()
    tube(bm, 0.0215, 0.0185, 0.01, loc=(0.204, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=40)
    part(f'TD_HingeLock{i}', bm, col, m['gold'], arm, bevel=0.0005)
    # quick-release lever on the hinge
    bm = bmesh.new()
    box(bm, (0.034, 0.006, 0.004), loc=(0.204, -0.02, ARM_Z + 0.008), rot=(0, 0, 0.12))
    cyl(bm, 0.004, 0.008, loc=(0.204, -0.0185, ARM_Z), rot=(math.pi / 2, 0, 0), segs=16)
    part(f'TD_HingeLever{i}', bm, col, m['black_steel'], arm, bevel=0.0008)

    # motor mount at the tip: a clamp around the tube and a flat seat for the motor
    bm = bmesh.new()
    cyl(bm, 0.022, 0.04, loc=(MOTOR_R - 0.004, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=40)
    box(bm, (0.072, 0.064, 0.004), loc=(MOTOR_R, 0, ARM_Z + TUBE_R + 0.004))
    mount = part(f'TD_MotorMount{i}', bm, col, m['gunmetal'], arm, bevel=0.0012, segs=3)
    bm = bmesh.new()
    cyl(bm, TUBE_R + 0.0003, 0.06, loc=(MOTOR_R - 0.03, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=40)
    cyl(bm, 0.009, 0.03, loc=(MOTOR_R + 0.024, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=24)
    cut(mount, [cutter(f'cut_m{i}', bm, col)])
    # clamp screws on the mount and the inner clamp
    bm = bmesh.new()
    for x in (MOTOR_R - 0.016, MOTOR_R + 0.008):
        cyl(bm, 0.0026, 0.004, loc=(x, 0.0225, ARM_Z), rot=(math.pi / 2, 0, 0), segs=20)
    for x in (0.116, 0.134):
        cyl(bm, 0.0026, 0.003, loc=(x, 0, TOP_Z + PLATE_T / 2 + 0.0015), segs=20)
    part(f'TD_MountScrews{i}', bm, col, m['black_steel'], arm, bevel=0.0004)

    # navigation light under the motor mount: red on the left, green on the right, white at the back
    led = ('led_green', 'led_green', 'led_red', 'led_red', 'led_white', 'led_white')[i]
    bm = bmesh.new()
    box(bm, (0.018, 0.012, 0.004), loc=(MOTOR_R + 0.03, 0, ARM_Z - TUBE_R - 0.003), mat=0)
    part(f'TD_LEDHousing{i}', bm, col, m['plastic'], arm, bevel=0.001)
    bm = bmesh.new()
    sphere(bm, 0.0042, loc=(MOTOR_R + 0.03, 0, ARM_Z - TUBE_R - 0.005), scale=(1.6, 1, 0.6), segs=16, rings=8)
    part(f'TD_LED{i}', bm, col, m[led], arm)

    # ESC under the arm, with a finned heatsink and wires to the motor and back to the body
    esc = bmesh.new()
    box(esc, (0.074, 0.036, 0.014), loc=(0.34, 0, ARM_Z - TUBE_R - 0.0075))
    part(f'TD_ESC{i}', esc, col, m['shrink'], arm, bevel=0.003, segs=3)
    fins = bmesh.new()
    box(fins, (0.06, 0.032, 0.002), loc=(0.34, 0, ARM_Z - TUBE_R - 0.0155))
    for k in range(7):
        box(fins, (0.06, 0.0016, 0.006), loc=(0.34, -0.0135 + k * 0.0045, ARM_Z - TUBE_R - 0.0195))
    part(f'TD_ESCFins{i}', fins, col, m['alu'], arm, bevel=0.0003)
    # cable ties holding the wiring to the arm
    bm = bmesh.new()
    for x in (0.27, 0.41, 0.47):
        tube(bm, TUBE_R + 0.0012, TUBE_R + 0.0002, 0.0035, loc=(x, 0, ARM_Z), rot=(0, math.pi / 2, 0), segs=32)
        box(bm, (0.005, 0.006, 0.005), loc=(x, 0, ARM_Z + TUBE_R + 0.002))
    part(f'TD_Ties{i}', bm, col, m['plastic'], arm, bevel=0.0003)
    wires(m, col, arm, i)
    return arm


def wire(name, pts, radius, mat, col, parent, res=8):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.materials.append(mat)
    return obj(name, cu, col, parent)


def wires(m, col, arm, i):
    under = ARM_Z - TUBE_R - 0.0018
    # three motor phase wires from the ESC out to the motor
    for k, mat in enumerate(('wire_black', 'wire_black', 'wire_black')):
        dy = (k - 1) * 0.0034
        wire(f'TD_Phase{i}{k}', [(0.377, dy, under - 0.006), (0.43, dy, under + 0.0005), (0.5, dy, under + 0.0005),
                                  (MOTOR_R - 0.02, dy, ARM_Z), (MOTOR_R - 0.006, dy * 1.4, ARM_Z + TUBE_R + 0.012)],
             0.0014, m[mat], col, arm)
    # power pair back to the plates
    for k, mat in enumerate(('wire_red', 'wire_black')):
        dy = (k - 0.5) * 0.005
        wire(f'TD_Power{i}{k}', [(0.303, dy, under - 0.006), (0.27, dy, under + 0.0006), (0.17, dy, under - 0.011),
                                  (0.125, dy, -0.0085), (0.104, dy, -0.0064)], 0.0022, m[mat], col, arm)


def build_frame(m):
    col = coll('TD Drone')
    root = empty('TD_Drone', col, size=0.2)
    body = empty('TD_Body', col, root)
    build_plates(m, col, body)
    arms = [build_arm(m, col, root, i) for i in range(6)]
    return root, body, arms
