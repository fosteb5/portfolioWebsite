# The tethered quadcopter. Loaded last by td_run.py, so what it defines here replaces the older hexacopter
# airframe, its explode animation and its washing pose. Motors, props, the flight controller, camera, GPS,
# tether hub, facade, spray and studio still come from the other td_*.py modules.
#
# One design, two sizes:
#   proto  the scaled-down demo build: a 3D-printed body with four carbon fibre tubes through it as the arms,
#          wiring inside the tubes, and the flight controller, camera and step-down converter in the body
#   full   the full-size drone for the washing scene, the same layout scaled up
# The airframe is still being designed, so every size here is an estimate.
#
# Units are metres. The drone faces +Y (the glass), arm 0 points front-right, and body parts are modelled
# at prototype size inside TD_Body, which is scaled up for the full-size drone.

VARIANTS = {
    'proto': dict(S=1.0, MOTOR_R=0.35, PROP_R=0.1905, MOTOR_S=1.0),    # 700 mm motor to motor, 15 inch props
    'full': dict(S=1.35, MOTOR_R=0.55, PROP_R=0.254, MOTOR_S=1.25),    # 1.1 m, 20 inch props
}
T = 0.011                     # arm tube radius in body units (22 mm tubes on the prototype)
W = 0.095                     # half-width of the square body
C = 0.042                     # corner chamfers, where the tubes pass through
CORNER = 0.006                # rounding on the vertical edges
Z0, Z1 = -0.036, 0.018        # bottom of the tub and top of its walls
WALL = 0.0024
LID_T = 0.0036
R_SOCK = 0.06                 # inner end of each arm tube, from the centre
R_FACE = (2 * W - C) / math.sqrt(2)   # centre to a chamfer face along the diagonal
NOZZLE_BODY = (0.0, 0.112, -0.05)     # spray apex in body space
PRINT_COLOUR = (0.8, 0.36, 0.012)     # high-visibility gold PLA


def configure(variant='proto'):
    g = globals()
    c = VARIANTS[variant]
    g['VARIANT'] = variant
    g['BODY_S'] = c['S']
    g['MOTOR_R'] = c['MOTOR_R']
    g['PROP_R'] = c['PROP_R']
    g['MOTOR_S'] = c['MOTOR_S']
    g['TUBE_R'] = T * c['S']
    g['ARM_ANGLES'] = [math.radians(a) for a in (45, 135, 225, 315)]
    g['ARM_Z'] = 0.0
    g['SEAT_Z'] = g['TUBE_R'] + 0.0095
    g['NOZZLE_LOCAL'] = [tuple(v * c['S'] for v in NOZZLE_BODY)]
    g['FAN'] = math.radians(19)
    # props stay about 0.36 m off the glass
    g['STANDOFF'] = -(c['MOTOR_R'] * math.sqrt(0.5) + c['PROP_R'] + 0.36)


# ---------------------------------------------------------------- materials and shapes

def print_material(name, color):
    """Matte PLA with fine horizontal layer lines, 0.28 mm apart in the part's own space."""
    m, nt, out = node_mat(name)
    p = add(nt, 'ShaderNodeBsdfPrincipled', (300, 0))
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = 0.5
    p.inputs['Specular IOR Level'].default_value = 0.42
    p.inputs['Coat Weight'].default_value = 0.08
    p.inputs['Coat Roughness'].default_value = 0.35
    tc = add(nt, 'ShaderNodeTexCoord', (-900, 0))
    sep = add(nt, 'ShaderNodeSeparateXYZ', (-700, 0))
    link(nt, tc.outputs['Object'], sep.inputs[0])
    mul = add(nt, 'ShaderNodeMath', (-500, 0), operation='MULTIPLY')
    link(nt, sep.outputs['Z'], mul.inputs[0])
    mul.inputs[1].default_value = TAU / 0.00028
    sin = add(nt, 'ShaderNodeMath', (-300, 0), operation='SINE')
    link(nt, mul.outputs[0], sin.inputs[0])
    bump = add(nt, 'ShaderNodeBump', (0, -200))
    bump.name = 'Layers'
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.00006
    link(nt, sin.outputs[0], bump.inputs['Height'])
    link(nt, bump.outputs['Normal'], p.inputs['Normal'])
    link(nt, p.outputs[0], out.inputs[0])
    return m


def quad_materials(m):
    m['print'] = print_material('TD_Print', PRINT_COLOUR)
    m['print_dark'] = print_material('TD_PrintDark', (0.03, 0.031, 0.034))
    m['pcb_blue'] = principled('TD_PCBBlue', (0.01, 0.06, 0.32), 0.0, 0.3, coat=0.5, coat_rough=0.2)
    m['sonar_can'] = brushed('TD_SonarCan', (0.66, 0.67, 0.69), rough=0.25, aniso=0.2, scale=1800)
    m['sonar_mesh'] = principled('TD_SonarMesh', (0.02, 0.02, 0.022), 0.0, 0.7)
    m['rj45'] = principled('TD_RJ45Shield', (0.72, 0.72, 0.7), 1.0, 0.3)
    m['terminal'] = principled('TD_Terminal', (0.05, 0.32, 0.12), 0.0, 0.45)
    m['ethernet'] = principled('TD_EthernetCable', (0.08, 0.2, 0.42), 0.0, 0.4, coat=0.3)
    m['nozzle_tip'] = principled('TD_NozzleTip', (0.75, 0.08, 0.04), 0.0, 0.38)


def octagon(w, c, r, segs=4):
    pts = [(-w + c, -w), (w - c, -w), (w, -w + c), (w, w - c), (w - c, w), (-w + c, w), (-w, w - c), (-w, -w + c)]
    return rounded_poly(pts, r, segs)


def inner_octagon(t, r=CORNER):
    return octagon(W - t, C - t * (2 - math.sqrt(2)), max(0.0008, r - t))


def along(angle, r, z=0.0):
    return Vector((r * math.cos(angle), r * math.sin(angle), z))


def diag_rot(angle):
    """Turns local Z to point along the arm at `angle`."""
    return (0, math.pi / 2, angle)


def cylinder_cutter(name, col, r, p0, p1, segs=40):
    bm = bmesh.new()
    rod(bm, p0, p1, r, segs=segs)
    return cutter(name, bm, col)


if '_cut_world' not in globals():
    _cut_world = cut


def cut(ob, cutters, solver='EXACT'):
    """As td_lib's cut(), but each cutter is placed in its target's parent space, where both were modelled."""
    for c in cutters:
        c.parent = ob.parent
        c.matrix_parent_inverse = ob.matrix_parent_inverse.copy()
        c.location, c.rotation_euler, c.scale = ob.location, ob.rotation_euler, ob.scale
    return _cut_world(ob, cutters, solver)


# ---------------------------------------------------------------- the printed body

def build_tub(m, col, body):
    grp = empty('TD_GrpTub', col, body)
    bm = bmesh.new()
    prism(bm, octagon(W, C, CORNER), Z0, Z1)
    tub = part('TD_Tub', bm, col, m['print'], grp, angle=40)
    cuts = []
    bm = bmesh.new()
    prism(bm, inner_octagon(WALL), Z0 + WALL, Z1 + 0.02)
    cuts.append(cutter('cut_tub_in', bm, col))
    for i, a in enumerate(ARM_ANGLES):
        cuts.append(cylinder_cutter(f'cut_tub_arm{i}', col, T + 0.0004, along(a, R_FACE - 0.02), along(a, R_FACE + 0.05)))
    # front: a window for the camera lens and two holes for the ultrasonic transducers
    cuts.append(cylinder_cutter('cut_lens', col, 0.0048, (0, W - 0.01, 0.006), (0, W + 0.01, 0.006)))
    for x in (-0.013, 0.013):
        cuts.append(cylinder_cutter(f'cut_can{x}', col, 0.0084, (x, W - 0.01, -0.019), (x, W + 0.01, -0.019)))
    # floor: the converter's heatsink drops through, and the tether's leads come up beside the hub
    bm = bmesh.new()
    box(bm, (0.062, 0.04, 0.02), loc=(0, -0.03, Z0))
    cuts.append(cutter('cut_fins', bm, col))
    cuts.append(cylinder_cutter('cut_leads', col, 0.009, (0, 0.012, Z0 - 0.01), (0, 0.012, Z0 + 0.01)))
    cut(tub, cuts)
    bev(tub, 0.0011, 2)

    # bosses on the chamfers where the tubes pass through, each with a clamp screw
    bm = bmesh.new()
    screws = bmesh.new()
    for a in ARM_ANGLES:
        tube(bm, T + 0.0068, T + 0.0004, 0.024, loc=along(a, R_FACE + 0.009), rot=diag_rot(a), segs=48)
        p = along(a, R_FACE + 0.012, T + 0.0068)
        box(bm, (0.012, 0.012, 0.004), loc=p - Vector((0, 0, 0.001)), rot=(0, 0, a))
        cyl(screws, 0.0026, 0.0022, loc=p + Vector((0, 0, 0.0021)), segs=24)
    part('TD_Bosses', bm, col, m['print'], grp, angle=40, bevel=0.0007)
    part('TD_BossScrews', screws, col, m['black_steel'], grp, bevel=0.0004)

    # clamp blocks inside: each tube sits in a printed saddle with a cap screwed over it
    bm = bmesh.new()
    for a in ARM_ANGLES:
        c = along(a, 0.081, (Z0 + WALL + T + 0.006) / 2)
        box(bm, (0.032, 0.028, T + 0.006 - (Z0 + WALL)), loc=c, rot=(0, 0, a))
    blocks = part('TD_Sockets', bm, col, m['print'], grp, angle=40)
    cut(blocks, [cylinder_cutter(f'cut_sock{i}', col, T + 0.0003, along(a, 0.05), along(a, 0.12)) for i, a in enumerate(ARM_ANGLES)])
    bev(blocks, 0.0008, 2)
    bm = bmesh.new()
    for a in ARM_ANGLES:
        for r in (0.072, 0.09):
            for s in (-1, 1):
                p = along(a, r) + Vector((-math.sin(a), math.cos(a), 0)) * s * 0.0095
                cyl(bm, 0.0024, 0.002, loc=p + Vector((0, 0, T + 0.007)), segs=20)
    part('TD_SocketScrews', bm, col, m['black_steel'], grp, bevel=0.0003)
    return grp


def build_lid(m, col, body):
    grp = empty('TD_GrpLid', col, body, loc=(0, 0, Z1))
    bm = bmesh.new()
    prism(bm, octagon(W, C, CORNER), 0, LID_T)
    prism(bm, inner_octagon(WALL + 0.0004), -0.004, 0.0002)
    prism(bm, octagon(0.056, 0.024, 0.004), LID_T - 0.0002, LID_T + 0.0016)
    lid = part('TD_Lid', bm, col, m['print'], grp, angle=40)
    cuts = []
    bm = bmesh.new()
    prism(bm, inner_octagon(WALL * 2 + 0.0004), -0.006, -0.0008)
    cuts.append(cutter('cut_lid_lip', bm, col))
    for s in (-1, 1):
        for k in range(6):
            bm = bmesh.new()
            box(bm, (0.014, 0.0026, 0.02), loc=(s * 0.074, -0.0275 + k * 0.011, 0))
            cuts.append(cutter(f'cut_vent{s}{k}', bm, col))
    cut(lid, cuts)
    bev(lid, 0.001, 2)
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(bm, 0.0032, 0.0018, loc=(sx * 0.064, sy * 0.064, LID_T + 0.0009), segs=24)
    part('TD_LidScrews', bm, col, m['black_steel'], grp, bevel=0.0004)
    # status light behind a small window
    bm = bmesh.new()
    cyl(bm, 0.0026, 0.0012, loc=(0.036, 0.062, LID_T + 0.0004), segs=24)
    part('TD_LidLED', bm, col, m['led_status'], grp)
    return grp


# ---------------------------------------------------------------- electronics inside the body

def build_esc(m, col, body):
    """A four-in-one ESC under the flight controller, with the motor leads running off into the tubes."""
    grp = empty('TD_GrpESC', col, body, loc=(0, 0, -0.008))
    img = pcb_image('TD_ESC_Art', 66, 46, seed=51, traces=90)
    mat = pcb_material('TD_ESC_Board', (0.012, 0.014, 0.016), img, 0.066, 0.046)
    bm = bmesh.new()
    board_bm(bm, 0.066, 0.046, 0.0016, r=0.003)
    part('TD_ESCBoard', bm, col, mat, grp, angle=40)
    top = 0.0008
    fets, drivers = bmesh.new(), bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            for k in range(3):
                for j in range(2):
                    box(fets, (0.005, 0.006, 0.001), loc=(sx * (0.012 + k * 0.0062), sy * (0.009 + j * 0.0072), top + 0.0005))
            box(drivers, (0.004, 0.004, 0.0009), loc=(sx * 0.006, sy * 0.017, top + 0.00045))
    part('TD_ESCFETs', fets, col, m['chip'], grp, bevel=0.0002)
    part('TD_ESCDrivers', drivers, col, m['chip'], grp, bevel=0.0002)
    for k, x in enumerate((-0.006, 0.006)):
        bm = bmesh.new()
        cyl(bm, 0.0042, 0.006, loc=(x, 0, top + 0.003), segs=32)
        part(f'TD_ESCCap{k}', bm, col, m['cap_sleeve'], grp, bevel=0.0006)
    # motor leads: three from each corner, out to the inner end of each tube
    for i, a in enumerate(ARM_ANGLES):
        c = Vector((math.copysign(0.03, math.cos(a)), math.copysign(0.02, math.sin(a)), top + 0.001))
        end = along(a, R_SOCK + 0.012, 0.008) - Vector((0, 0, -0.0))
        side = Vector((-math.sin(a), math.cos(a), 0))
        for k in range(3):
            d = side * (k - 1) * 0.0028
            mid = c.lerp(end, 0.5) + Vector((0, 0, 0.006))
            wire(f'TD_MotorLead{i}{k}', [c + d * 0.6, mid + d, end + d], 0.0011, m['wire_black'], col, grp)
    # power in from the converter
    for k, (x, mat) in enumerate(((-0.004, 'wire_red'), (0.004, 'wire_black'))):
        wire(f'TD_ESCPower{k}', [(x, -0.022, top + 0.001), (x * 1.5, -0.03, -0.002), (x * 2, -0.034, -0.0075)], 0.0018, m[mat], col, grp)
    # standoffs up to the flight controller
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(bm, 0.0026, 0.012, loc=(sx * 0.0315, sy * 0.0215, 0.0068), segs=6)
    part('TD_FCStandoffs', bm, col, m['gold'], grp, bevel=0.0003)
    return grp


def build_converter(m, col, body):
    """The step-down converter that brings the tether's high-voltage feed down for the motors."""
    grp = empty('TD_GrpDCDC', col, body, loc=(0, -0.03, Z0 + WALL))
    bm = bmesh.new()
    box(bm, (0.068, 0.048, 0.017), loc=(0, 0, 0.0085))
    part('TD_DCDCCase', bm, col, m['alu_dark'], grp, bevel=0.0018, segs=3)
    fins = bmesh.new()
    for k in range(8):
        box(fins, (0.0022, 0.036, 0.013), loc=(-0.028 + k * 0.008, 0, -0.0065 - WALL / 2))
    part('TD_DCDCFins', fins, col, m['alu_dark'], grp, bevel=0.0005)
    bm = bmesh.new()
    box(bm, (0.056, 0.026, 0.0003), loc=(0, -0.003, 0.0171))
    part('TD_DCDCLabel', bm, col, m['plastic_white'], grp, smooth=False)
    label('TD_DCDCText', 'STEP-DOWN', col, grp, (0, -0.009, 0.0174), 0.0052, m['silk_dark'], rot=(0, 0, math.pi))
    label('TD_DCDCText2', 'CONVERTER', col, grp, (0, 0.0005, 0.0174), 0.0038, m['silk_dark'], rot=(0, 0, math.pi))
    label('TD_DCDCText3', 'HV IN  /  MOTOR BUS OUT', col, grp, (0, 0.0065, 0.0174), 0.002, m['silk_dark'], rot=(0, 0, math.pi))
    # terminal block on the front, with its screws
    bm = bmesh.new()
    box(bm, (0.04, 0.009, 0.01), loc=(0, 0.0285, 0.006))
    part('TD_DCDCTerminal', bm, col, m['terminal'], grp, bevel=0.0007)
    bm = bmesh.new()
    for k in range(4):
        cyl(bm, 0.0022, 0.002, loc=(-0.015 + k * 0.01, 0.0285, 0.0115), segs=20)
    part('TD_DCDCTerminalScrews', bm, col, m['steel'], grp, bevel=0.0003)
    # high-voltage feed up through the floor from the tether
    for k, (x, mat) in enumerate(((-0.005, 'wire_red'), (0.005, 'wire_black'))):
        wire(f'TD_HVIn{k}', [(x, 0.042, -0.002), (x, 0.042, 0.004), (x * 2, 0.0325, 0.008)], 0.0022, m[mat], col, grp)
    return grp


def build_poe(m, col, body):
    """The low-voltage Power-over-Ethernet supply: it powers the flight controller and camera and carries their data."""
    grp = empty('TD_GrpPoE', col, body, loc=(0, -0.077, -0.012))
    img = pcb_image('TD_PoE_Art', 42, 24, seed=61, traces=40)
    mat = pcb_material('TD_PoE_Board', (0.02, 0.13, 0.045), img, 0.042, 0.024)
    bm = bmesh.new()
    board_bm(bm, 0.042, 0.024, 0.0016, r=0.002)
    part('TD_PoEBoard', bm, col, mat, grp, angle=40)
    top = 0.0008
    bm = bmesh.new()
    box(bm, (0.016, 0.021, 0.013), loc=(-0.01, 0.0005, top + 0.0065))
    jack = part('TD_PoEJack', bm, col, m['rj45'], grp, bevel=0.0004)
    bm = bmesh.new()
    box(bm, (0.012, 0.01, 0.009), loc=(-0.01, 0.011, top + 0.0055))
    cut(jack, [cutter('cut_rj45', bm, col)])
    bm = bmesh.new()
    box(bm, (0.009, 0.009, 0.006), loc=(0.009, 0.004, top + 0.003))
    box(bm, (0.006, 0.005, 0.0012), loc=(0.009, -0.007, top + 0.0006))
    part('TD_PoEParts', bm, col, m['chip'], grp, bevel=0.0003)
    bm = bmesh.new()
    cyl(bm, 0.0035, 0.0055, loc=(0.017, -0.004, top + 0.00275), segs=28)
    part('TD_PoECap', bm, col, m['cap_sleeve'], grp, bevel=0.0005)
    # the Ethernet lead from the jack down to the tether, and power up to the flight controller
    wire('TD_EthernetLead', [(-0.01, 0.009, top + 0.0055), (-0.014, 0.022, 0.0), (-0.01, 0.06, -0.0005), (-0.004, 0.078, -0.006), (0, 0.089, -0.028)],
         0.0022, m['ethernet'], col, grp)
    for k, (x, mat) in enumerate(((0.004, 'wire_red'), (0.008, 'wire_black'))):
        wire(f'TD_PoEOut{k}', [(x + 0.008, 0.012, top + 0.001), (x + 0.008, 0.03, 0.014), (x + 0.006, 0.056, 0.02)], 0.0009, m[mat], col, grp)
    return grp


def build_sonar(m, col, body):
    """The ultrasonic rangefinder that holds the drone's distance from the glass."""
    grp = empty('TD_GrpSonar', col, body, loc=(0, W - WALL - 0.0042, -0.019))
    bm = bmesh.new()
    box(bm, (0.045, 0.0016, 0.02), loc=(0, 0, 0))
    part('TD_SonarBoard', bm, col, m['pcb_blue'], grp, bevel=0.0003)
    cans, meshes = bmesh.new(), bmesh.new()
    for x in (-0.013, 0.013):
        cyl(cans, 0.0081, 0.012, loc=(x, 0.0068, 0), rot=(math.pi / 2, 0, 0), segs=48)
        cyl(meshes, 0.0068, 0.0004, loc=(x, 0.0129, 0), rot=(math.pi / 2, 0, 0), segs=48)
    part('TD_SonarCans', cans, col, m['sonar_can'], grp, bevel=0.0006)
    part('TD_SonarMesh', meshes, col, m['sonar_mesh'], grp)
    bm = bmesh.new()
    box(bm, (0.006, 0.0016, 0.004), loc=(0, -0.0016, 0.004))
    box(bm, (0.004, 0.0012, 0.003), loc=(0.006, -0.0014, -0.005))
    box(bm, (0.004, 0.0012, 0.003), loc=(-0.006, -0.0014, -0.005))
    part('TD_SonarChips', bm, col, m['chip'], grp, bevel=0.0002)
    bm = bmesh.new()
    for k in range(4):
        box(bm, (0.0006, 0.0006, 0.008), loc=(-0.0038 + k * 0.00254, -0.0018, 0.012))
    part('TD_SonarPins', bm, col, m['enig'], grp)
    return grp


def build_nozzle(m, col, body):
    """Spray only: one flat-fan nozzle under the front of the body, fed from the tether's hose."""
    grp = empty('TD_GrpWater', col, body)
    zc = NOZZLE_BODY[2]
    bm = bmesh.new()
    box(bm, (0.026, 0.03, 0.008), loc=(0, 0.08, Z0 - 0.004))
    box(bm, (0.012, 0.014, 0.008), loc=(0, 0.084, Z0 - 0.011))
    part('TD_NozzleBracket', bm, col, m['print'], grp, angle=40, bevel=0.0008)
    bm = bmesh.new()
    box(bm, (0.014, 0.014, 0.014), loc=(0, 0.084, zc))
    rod(bm, (0, 0.066, zc), (0, 0.077, zc), 0.005, segs=6)
    part('TD_NozzleElbow', bm, col, m['brass'], grp, bevel=0.0008)
    bm = bmesh.new()
    rod(bm, (0, 0.091, zc), (0, 0.1, zc), 0.0068, segs=6)
    rod(bm, (0, 0.1, zc), (0, 0.106, zc), 0.0052, segs=32)
    part('TD_Nozzle', bm, col, m['steel'], grp, bevel=0.0005)
    bm = bmesh.new()
    rod(bm, (0, 0.106, zc), (0, 0.111, zc), 0.0048, segs=32)
    tip = part('TD_NozzleTip', bm, col, m['nozzle_tip'], grp, bevel=0.0006)
    bm = bmesh.new()
    box(bm, (0.0016, 0.004, 0.012), loc=(0, 0.112, zc))
    cut(tip, [cutter('cut_slot', bm, col)])
    # water from the hub's port to the nozzle
    wire('TD_NozzleHose', [(0, 0.046, Z0 - 0.02), (0, 0.052, Z0 - 0.019), (0, 0.06, zc), (0, 0.067, zc)], 0.0045, m['hose'], col, grp)
    return grp


def build_legs(m, col, body):
    grp = empty('TD_GrpGear', col, body)
    rods, sockets, feet = bmesh.new(), bmesh.new(), bmesh.new()
    for a in ARM_ANGLES:
        p0 = along(a, R_FACE + 0.008, -T - 0.012)
        p1 = along(a, 0.165, -0.168)
        rod(rods, p0, p1, 0.0055, segs=28, hollow=0.0045)
        box(sockets, (0.024, 0.02, 0.014), loc=p0 + Vector((0, 0, 0.002)), rot=(0, 0, a))
        sphere(feet, 0.011, loc=p1 + Vector((0, 0, -0.004)), scale=(1, 1, 0.8), segs=32, rings=16)
    part('TD_LegTubes', rods, col, m['carbon_tube'], grp, angle=20)
    part('TD_LegSockets', sockets, col, m['print'], grp, angle=40, bevel=0.0012)
    part('TD_LegFeet', feet, col, m['rubber'], grp)
    return grp


# ---------------------------------------------------------------- arms

def build_quad_arm(m, col, root, i):
    a = ARM_ANGLES[i]
    arm = empty(f'TD_Arm{i}', col, root, rot=(0, 0, a))
    r0 = R_SOCK * BODY_S
    r1 = MOTOR_R + 0.03
    bm = bmesh.new()
    tube(bm, TUBE_R, TUBE_R - 0.0015, r1 - r0, loc=((r0 + r1) / 2, 0, 0), rot=(0, math.pi / 2, 0), segs=48)
    part(f'TD_ArmTube{i}', bm, col, m['carbon_tube'], arm, angle=20)
    # rubber plug in the outer end; the motor leads leave through the top of the tube under the motor
    bm = bmesh.new()
    cyl(bm, TUBE_R - 0.0012, 0.006, loc=(r1 - 0.001, 0, 0), rot=(0, math.pi / 2, 0), segs=32)
    cyl(bm, TUBE_R + 0.0004, 0.002, loc=(r1 + 0.002, 0, 0), rot=(0, math.pi / 2, 0), segs=32)
    part(f'TD_ArmPlug{i}', bm, col, m['rubber'], arm, bevel=0.0005)

    # printed motor mount: a split collar round the tube with a seat for the motor on top
    rc = TUBE_R + 0.0055
    bm = bmesh.new()
    cyl(bm, rc, 0.054, loc=(MOTOR_R, 0, 0), rot=(0, math.pi / 2, 0), segs=48)
    cyl(bm, 0.036 * MOTOR_S, SEAT_Z - TUBE_R, loc=(MOTOR_R, 0, (SEAT_Z + TUBE_R) / 2), segs=64)
    box(bm, (0.012, 0.006, rc * 2 + 0.002), loc=(MOTOR_R + 0.017, -rc - 0.002, 0))
    box(bm, (0.012, 0.006, rc * 2 + 0.002), loc=(MOTOR_R - 0.017, -rc - 0.002, 0))
    mount = part(f'TD_MotorMount{i}', bm, col, m['print'], arm, angle=40)
    cut(mount, [cylinder_cutter(f'cut_mm{i}', col, TUBE_R + 0.0003, (MOTOR_R - 0.05, 0, 0), (MOTOR_R + 0.05, 0, 0))])
    bev(mount, 0.0009, 2)
    bm = bmesh.new()
    for x in (MOTOR_R - 0.017, MOTOR_R + 0.017):
        cyl(bm, 0.0026, 0.003, loc=(x, -rc - 0.0065, 0), rot=(math.pi / 2, 0, 0), segs=20)
    part(f'TD_MountScrews{i}', bm, col, m['black_steel'], arm, bevel=0.0004)

    # navigation light under the mount: green on the right, red on the left, white at the back
    led = ('led_green', 'led_red', 'led_white', 'led_white')[i]
    bm = bmesh.new()
    box(bm, (0.018, 0.012, 0.004), loc=(MOTOR_R, 0, -rc - 0.002))
    part(f'TD_LEDHousing{i}', bm, col, m['print_dark'], arm, bevel=0.001)
    bm = bmesh.new()
    sphere(bm, 0.0042, loc=(MOTOR_R, 0, -rc - 0.004), scale=(1.6, 1, 0.6), segs=16, rings=8)
    part(f'TD_LED{i}', bm, col, m[led], arm)
    return arm


def build_quad_propulsion(m, arms):
    col = coll('TD Drone')
    m['prop_blur'] = prop_blur_material()
    for i, arm in enumerate(arms):
        mot = build_motor(m, col, arm, i)
        mot.scale = (MOTOR_S,) * 3
        prop = build_prop(m, col, mot, i)
        prop.scale = (1 / MOTOR_S,) * 3


# ---------------------------------------------------------------- assembly

def clear_drone():
    for name in ('TD Drone', 'TD Tether'):
        c = bpy.data.collections.get(name)
        if c:
            for ob in list(c.objects):
                bpy.data.objects.remove(ob, do_unlink=True)


def build_quad(m):
    col = coll('TD Drone')
    root = empty('TD_Drone', col, size=0.2)
    body = empty('TD_Body', col, root)
    body.scale = (BODY_S,) * 3
    build_tub(m, col, body)
    lid = build_lid(m, col, body)
    fc = build_fc(m, col, body)
    fc.location = (0, 0, 0.0056)
    build_esc(m, col, body)
    build_converter(m, col, body)
    build_poe(m, col, body)
    cam = build_camera(m, col, body)
    cam.location = (0, 0.082, -0.0134)
    build_sonar(m, col, body)
    gps = build_gps(m, col, body)
    gps.location = (0, -0.072, Z1 + LID_T)
    hub = build_hub(m, col, body)
    hub.location = (0, 0.016, Z0)
    build_nozzle(m, col, body)
    build_legs(m, col, body)
    arms = [build_quad_arm(m, col, root, i) for i in range(4)]
    build_quad_propulsion(m, arms)
    return root


def build_all(variant='proto'):
    configure(variant)
    clear_drone()
    m = materials()
    extra_materials(m)
    quad_materials(m)
    root = build_quad(m)
    build_tether(m)
    G_studio = bpy.data.objects.get('TD_StudioCam')
    if G_studio is None:
        studio()
        studio_world()
    if bpy.data.objects.get('TD_WashCam') is None:
        sky_world()
        build_facade(m)
        build_spray(m)
    bpy.data.cameras['TD_WashCam'].dof.focus_object = root
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    for cu in list(bpy.data.curves):
        if cu.users == 0:
            bpy.data.curves.remove(cu)
    capture_bases()
    set_mode('studio' if variant == 'proto' else 'wash')
    return m


# ---------------------------------------------------------------- poses

def set_spinning(on, angle=0.0):
    """Spinning props are drawn as blurred discs; stopped ones as blades."""
    for i in range(4):
        blur = bpy.data.objects[f'TD_PropBlur{i}']
        blur.hide_render = blur.hide_viewport = not on
        for n in (f'TD_Blades{i}', f'TD_PropHub{i}'):
            ob = bpy.data.objects[n]
            ob.hide_render = ob.hide_viewport = on
        bpy.data.objects[f'TD_PropSpin{i}'].rotation_euler = (0, 0, angle * (1 if i % 2 == 0 else -1) + i * 0.7)


# Each part group moves through one or more stages: (offset in body units, start, end).
EXPLODE = {
    'TD_GrpLid': [((0, 0, 0.24), 0.40, 0.48)],
    'TD_GrpGPS': [((0, 0, 0.3), 0.40, 0.49)],
    'TD_GrpFC': [((0, 0, 0.16), 0.44, 0.52)],
    'TD_GrpESC': [((0, 0, 0.1), 0.48, 0.56)],
    'TD_GrpCam': [((0, 0, 0.095), 0.52, 0.58), ((0, 0.12, 0), 0.56, 0.63)],
    'TD_GrpSonar': [((0, 0, 0.052), 0.53, 0.59), ((0, 0.12, 0), 0.57, 0.64)],
    'TD_GrpPoE': [((0, 0, 0.07), 0.55, 0.61), ((0, -0.08, 0), 0.59, 0.66)],
    'TD_GrpDCDC': [((0, 0, 0.055), 0.68, 0.76)],
    'TD_GrpHub': [((0, 0, -0.12), 0.70, 0.78)],
    'TD_GrpWater': [((0, 0.06, -0.075), 0.72, 0.80)],
    'TD_GrpGear': [((0, 0, -0.06), 0.74, 0.82)],
}
PROP_UP = (0.2, 0.04, 0.16)       # props lift off
MOTOR_UP = (0.12, 0.09, 0.21)      # then the motors
ARM_OUT = (0.17, 0.24, 0.37)       # the tubes slide out of the body


def _base(ob):
    if 'base' not in ob:
        ob['base'] = tuple(ob.location)
    return Vector(ob['base'])


def capture_bases():
    ob = bpy.data.objects
    for name in EXPLODE:
        if 'base' in ob[name]:
            del ob[name]['base']
        _base(ob[name])
    for i in range(4):
        for n in (f'TD_Motor{i}', f'TD_Prop{i}'):
            if 'base' in ob[n]:
                del ob[n]['base']
            _base(ob[n])


def reset_explode():
    ob = bpy.data.objects
    for name in EXPLODE:
        ob[name].location = _base(ob[name])
    for i in range(4):
        ob[f'TD_Arm{i}'].location = (0, 0, 0)
        for n in (f'TD_Motor{i}', f'TD_Prop{i}'):
            ob[n].location = _base(ob[n])


def set_breakdown_state(p):
    ob = bpy.data.objects
    root = ob['TD_Drone']
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    set_spinning(False)
    for name, stages in EXPLODE.items():
        loc = _base(ob[name])
        for off, a, b in stages:
            loc = loc + Vector(off) * smoother((p - a) / (b - a))
        ob[name].location = loc
    e_arm = smoother((p - ARM_OUT[1]) / (ARM_OUT[2] - ARM_OUT[1])) * ARM_OUT[0]
    e_mot = smoother((p - MOTOR_UP[1]) / (MOTOR_UP[2] - MOTOR_UP[1])) * MOTOR_UP[0]
    u_prop = smoother((p - PROP_UP[1]) / (PROP_UP[2] - PROP_UP[1]))
    for i in range(4):
        a = ARM_ANGLES[i]
        ob[f'TD_Arm{i}'].location = (math.cos(a) * e_arm, math.sin(a) * e_arm, 0)
        mo = ob[f'TD_Motor{i}']
        mo.location = _base(mo) + Vector((0, 0, e_mot))
        pr = ob[f'TD_Prop{i}']
        pr.location = _base(pr) + Vector((0, 0, PROP_UP[0] * u_prop / MOTOR_S))
        ob[f'TD_PropSpin{i}'].rotation_euler = (0, 0, (1 if i % 2 == 0 else -1) * u_prop * math.radians(70) + i * 0.7)
    az, el, dist, tx, ty, tz = hermite(BREAK_CAM, p)
    tgt = ob['TD_StudioTarget']
    tgt.location = (tx, ty, tz)
    a, e = math.radians(az), math.radians(el)
    ob['TD_StudioCam'].location = tgt.location + Vector((dist * math.cos(e) * math.cos(a), dist * math.cos(e) * math.sin(a), dist * math.sin(e)))
    bpy.context.view_layer.update()
    hub = ob['TD_GrpHub'].matrix_world @ Vector((0, 0, -0.09))
    set_tether(hub, hub + Vector((0, 0, -0.35)), hub + Vector((0.02, 0.06, -0.8)), hub + Vector((0.05, 0.12, -1.6)), phase=0.0)


# Camera keys: progress, azimuth (deg, 0 is +X, 90 is the front), elevation (deg), distance (m), target x y z
BREAK_CAM = [
    (0.00, 62, 24, 1.9, 0.0, 0.0, 0.0),
    (0.12, 70, 28, 2.0, 0.0, 0.0, 0.1),
    (0.24, 80, 50, 1.9, 0.0, 0.0, 0.06),
    (0.37, 92, 42, 1.6, 0.0, 0.0, 0.06),
    (0.46, 90, 26, 1.1, 0.0, 0.02, 0.11),
    (0.56, 84, 20, 0.95, 0.0, 0.04, 0.12),
    (0.64, 70, 12, 0.95, 0.0, 0.08, 0.08),
    (0.74, 110, -12, 1.2, 0.0, 0.03, -0.06),
    (0.84, 96, -4, 1.5, 0.0, 0.02, 0.0),
    (1.00, 74, 16, 2.05, 0.0, 0.02, 0.11),
]


def set_wash_state(p, frame_seed=0):
    W_ = WORK_Z
    reset_explode()
    root = bpy.data.objects['TD_Drone']
    pos, (pitch, roll, yaw) = drone_pose(p)
    root.location = pos
    root.rotation_euler = (pitch, roll, yaw)
    set_spinning(True, angle=p * 400.0)
    cx, cy, cz, tx, ty, tz = hermite(WASH_CAM, p)
    bpy.data.objects['TD_WashCam'].location = (cx, cy, W_ + cz)
    bpy.data.objects['TD_WashTarget'].location = (tx, ty, W_ + tz)
    bpy.context.view_layer.update()

    amount = ease(p, 0.33, 0.4) * (1 - ease(p, 0.92, 0.955))
    nozzle = root.matrix_world @ Vector(NOZZLE_LOCAL[0])
    spraying = p >= 0.33
    x_now = min(nozzle.x, X1 + 0.02) if spraying else X0 - 2.0
    set_clean(X0 - 0.02, x_now, W_ + NOZZLE_LOCAL[0][2], 0.3 * ease(p, 0.34, 0.4), 1.0, amount)
    set_spray(amount, 1000 + frame_seed)
    bpy.data.materials['TD_Mist'].node_tree.nodes['Amount'].outputs[0].default_value = amount

    # the tether trails a little behind the drone's moves on its way down to the base station
    hub = bpy.data.objects['TD_GrpHub'].matrix_world @ Vector((0, 0, -0.09))
    vx = (drone_pose(min(1, p + 0.01))[0].x - drone_pose(max(0, p - 0.01))[0].x) / 0.02
    lag = Vector((-vx * 0.06, 0.0, 0.0))
    set_tether(hub, hub + Vector((0, 0, -1.4)) + lag, Vector((pos.x - 0.8, -2.0, W_ - 9.0)) + lag * 2,
               Vector((-1.5, -4.5, 0.0)), phase=p * 2.0)


def render_hero(p=0.74, samples=128):
    """A full-size still of the drone mid-sweep, for the home page card and the case study's lead image."""
    wash_settings(1920, 1080, samples)
    set_wash_state(p, 7)
    _render(os.path.join(R_DIR, 'renders', 'tethered-drone-hero.png'))


def render_exploded(samples=128):
    studio_settings(1920, 1080, samples)
    set_breakdown_state(1.0)
    _render(os.path.join(R_DIR, 'renders', 'tethered-drone-exploded.png'))


configure('proto')
