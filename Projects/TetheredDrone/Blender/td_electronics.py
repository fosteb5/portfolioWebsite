# Electronics: the custom ESP32 flight controller, the Raspberry Pi with its camera, the GPS,
# the power distribution board and tether DC-DC converter, and the splash canopy.
import numpy as np

MM = 0.001
TOP_FACE = TOP_Z + PLATE_T / 2        # upper face of the top plate
UNDER = -PLATE_T / 2                  # lower face of the bottom plate


# ---------------------------------------------------------------- PCB artwork

def pcb_image(name, w_mm, h_mm, seed, ppm=14, traces=140, outlines=()):
    """Copper traces (red channel) and silkscreen outlines (green) drawn into an image, so the board
    surface shows routing under the solder mask. Outlines are (x, y, w, h) in board millimetres."""
    w, h = int(w_mm * ppm), int(h_mm * ppm)
    a = np.zeros((h, w, 4), np.float32)
    a[..., 3] = 1
    rng = random.Random(seed)
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def stamp(x, y, r, ch):
        x0, x1 = max(0, int(x - r)), min(w, int(x + r) + 1)
        y0, y1 = max(0, int(y - r)), min(h, int(y + r) + 1)
        if x0 < x1 and y0 < y1:
            a[y0:y1, x0:x1, ch] = 1.0

    for _ in range(traces):
        x, y = rng.uniform(0.05, 0.95) * w, rng.uniform(0.05, 0.95) * h
        d = rng.randrange(0, 8, 2)
        r = rng.choice((1, 1, 1.5, 2, 3))
        for _seg in range(rng.randint(2, 5)):
            dx, dy = dirs[d]
            for _s in range(rng.randint(int(1.5 * ppm), int(12 * ppm))):
                x += dx
                y += dy
                if not (2 < x < w - 3 and 2 < y < h - 3):
                    break
                stamp(x, y, r, 0)
            d = (d + rng.choice((-1, 1))) % 8
        # a via at the end of most traces
        if rng.random() < 0.7:
            for yy in range(-3, 4):
                for xx in range(-3, 4):
                    if 4 <= xx * xx + yy * yy <= 10:
                        stamp(x + xx, y + yy, 0, 0)
    # a copper pour band around the edge
    a[3:6, 3:w - 3, 0] = 1
    a[h - 6:h - 3, 3:w - 3, 0] = 1
    a[3:h - 3, 3:6, 0] = 1
    a[3:h - 3, w - 6:w - 3, 0] = 1
    for (cx, cy, ow, oh) in outlines:
        x0, x1 = int((cx - ow / 2 + w_mm / 2) * ppm), int((cx + ow / 2 + w_mm / 2) * ppm)
        y0, y1 = int((cy - oh / 2 + h_mm / 2) * ppm), int((cy + oh / 2 + h_mm / 2) * ppm)
        x0, x1, y0, y1 = max(0, x0), min(w - 1, x1), max(0, y0), min(h - 1, y1)
        a[y0:y0 + 2, x0:x1, 1] = 1
        a[y1 - 1:y1 + 1, x0:x1, 1] = 1
        a[y0:y1, x0:x0 + 2, 1] = 1
        a[y0:y1, x1 - 1:x1 + 1, 1] = 1
        a[max(0, y1 - 5):y1 - 2, x0 + 3:x0 + 6, 1] = 1   # pin 1 marker
    img = bpy.data.images.get(name)
    if img is not None:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.colorspace_settings.name = 'Non-Color'
    img.pixels.foreach_set(a.ravel())
    img.pack()
    return img


def pcb_material(name, mask, img, w, h, edge=(0.0, 0.0, 0.0)):
    """Solder mask over copper: traces show as slightly raised, lighter lines; silkscreen in white."""
    m, nt, out = node_mat(name)
    p = add(nt, 'ShaderNodeBsdfPrincipled', (300, 0))
    p.inputs['Roughness'].default_value = 0.3
    p.inputs['Coat Weight'].default_value = 0.5
    p.inputs['Coat Roughness'].default_value = 0.18
    tc = add(nt, 'ShaderNodeTexCoord', (-1100, 0))
    mp = add(nt, 'ShaderNodeMapping', (-900, 0))
    mp.inputs['Scale'].default_value = (1 / w, 1 / h, 1)
    mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    tex = add(nt, 'ShaderNodeTexImage', (-700, 0))
    tex.image = img
    tex.interpolation = 'Linear'
    tex.extension = 'CLIP'
    link(nt, mp.outputs[0], tex.inputs['Vector'])
    sep = add(nt, 'ShaderNodeSeparateColor', (-450, 0))
    link(nt, tex.outputs['Color'], sep.inputs[0])
    lift = add(nt, 'ShaderNodeMix', (-200, 150), data_type='RGBA')
    sock(lift.inputs, 'A_Color').default_value = (*mask, 1)
    sock(lift.inputs, 'B_Color').default_value = (mask[0] * 1.9 + 0.006, mask[1] * 1.9 + 0.006, mask[2] * 1.9 + 0.006, 1)
    link(nt, sep.outputs['Red'], sock(lift.inputs, 'Factor_Float'))
    silk = add(nt, 'ShaderNodeMix', (50, 150), data_type='RGBA')
    sock(silk.inputs, 'B_Color').default_value = (0.82, 0.82, 0.78, 1)
    link(nt, sock(lift.outputs, 'Result_Color'), sock(silk.inputs, 'A_Color'))
    link(nt, sep.outputs['Green'], sock(silk.inputs, 'Factor_Float'))
    link(nt, sock(silk.outputs, 'Result_Color'), p.inputs['Base Color'])
    bump = add(nt, 'ShaderNodeBump', (50, -200))
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.00004
    hsum = math_node(nt, 'ADD', sep.outputs['Red'], sep.outputs['Green'], (-200, -200))
    link(nt, hsum, bump.inputs['Height'])
    link(nt, bump.outputs['Normal'], p.inputs['Normal'])
    link(nt, p.outputs[0], out.inputs[0])
    return m


def label(name, text, col, parent, loc, size, mat, rot=(0, 0, 0), align='CENTER'):
    cu = bpy.data.curves.get(name) or bpy.data.curves.new(name, 'FONT')
    cu.body = text
    cu.size = size
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.materials.clear()
    cu.materials.append(mat)
    return obj(name, cu, col, parent, loc, rot)


def board_bm(bm, w, h, t, r=0.003, z=0.0):
    pts = rounded_poly([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], r, 4)
    prism(bm, pts, z - t / 2, z + t / 2)


def smd(bm, x, y, w, h, t, top, rot=0.0):
    """A small surface-mount part sitting on the board top, coordinates in millimetres."""
    box(bm, (w * MM, h * MM, t * MM), loc=(x * MM, y * MM, top + t * MM / 2), rot=(0, 0, rot))


def scatter_passives(rng, n, clusters, keepouts, top, bm_body, bm_ends, bm_res):
    """Rows of 0402 and 0603 capacitors and resistors around each IC, skipping anything already placed."""
    placed = list(keepouts)
    count = 0
    tries = 0
    while count < n and tries < n * 30:
        tries += 1
        cx, cy, spread = rng.choice(clusters)
        x, y = cx + rng.uniform(-spread, spread), cy + rng.uniform(-spread, spread)
        big = rng.random() < 0.35
        w, h = (1.6, 0.8) if big else (1.0, 0.5)
        vert = rng.random() < 0.5
        if vert:
            w, h = h, w
        if any(abs(x - kx) < (w + kw) / 2 + 0.35 and abs(y - ky) < (h + kh) / 2 + 0.35 for kx, ky, kw, kh in placed):
            continue
        placed.append((x, y, w, h))
        t = 0.5 if big else 0.35
        res = rng.random() < 0.35
        body_w, body_h = (w * 0.62, h) if not vert else (w, h * 0.62)
        smd(bm_res if res else bm_body, x, y, body_w, body_h, t, top)
        # tinned ends
        for s in (-1, 1):
            if not vert:
                smd(bm_ends, x + s * (w / 2 - w * 0.17), y, w * 0.34, h * 1.02, t * 1.02, top)
            else:
                smd(bm_ends, x, y + s * (h / 2 - h * 0.17), w * 1.02, h * 0.34, t * 1.02, top)
        count += 1


# ---------------------------------------------------------------- flight controller

FC_W, FC_H, FC_T = 70.0, 50.0, 1.6


def build_fc(m, col, root):
    grp = empty('TD_GrpFC', col, root, loc=(0, 0.045, TOP_FACE + 0.0085))
    top = FC_T * MM / 2
    parts = {
        'esp': (-20, 8.5, 18, 25.5), 'imu': (6, 2, 3, 2.5), 'baro': (12, 6, 2, 2), 'buck': (-2, -16, 2.9, 1.6),
        'ind': (5, -16, 5, 5), 'xt30': (-24, -20, 10.2, 5.2), 'cap1': (-24, -10.5, 6.6, 6.6), 'cap2': (-15.5, -12, 6.6, 6.6),
        'usb': (0, -21.5, 9, 7.3), 'hdr': (27.5, 2, 7.6, 15.3), 'gh1': (6, 21.6, 6, 4.3), 'gh2': (14.5, 21.6, 6, 4.3),
        'gh3': (14.5, -21.6, 6, 4.3), 'gh4': (23, -21.6, 6, 4.3), 'btn1': (-5.5, 18, 3, 4), 'btn2': (-5.5, 12, 3, 4),
        'xtal': (-5.5, 4, 3.2, 2.5), 'leds': (4, 12, 6, 1),
    }
    img = pcb_image('TD_FC_Art', FC_W, FC_H, seed=7, outlines=[v for k, v in parts.items() if k not in ('esp',)])
    mat = pcb_material('TD_FC_Board', (0.012, 0.014, 0.016), img, FC_W * MM, FC_H * MM)
    bm = bmesh.new()
    board_bm(bm, FC_W * MM, FC_H * MM, FC_T * MM, r=0.0025)
    brd = part('TD_FCBoard', bm, col, mat, grp, angle=40)
    holes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            bm = bmesh.new()
            cyl(bm, 0.0016, 0.01, loc=(sx * 31.5 * MM, sy * 21.5 * MM, 0), segs=24)
            holes.append(cutter(f'cut_fch{sx}{sy}', bm, col))
    cut(brd, holes)

    # ESP32-S3 module: its own substrate, a shield can, castellated pads and a meandered antenna
    ex, ey = parts['esp'][0], parts['esp'][1]
    bm = bmesh.new()
    smd(bm, ex, ey, 18, 25.5, 0.8, top)
    part('TD_ESPSubstrate', bm, col, m['pcb_black'], grp, bevel=0.0002)
    bm = bmesh.new()
    smd(bm, ex, ey - 3.0, 16.0, 17.8, 2.4, top + 0.8 * MM)
    part('TD_ESPShield', bm, col, m['shield'], grp, bevel=0.0003)
    pads = bmesh.new()
    for k in range(14):
        yy = ey - 11.5 + k * 1.27
        for sx in (-1, 1):
            smd(pads, ex + sx * 9.0, yy, 0.9, 0.85, 0.82, top)
    for k in range(10):
        smd(pads, ex - 5.7 + k * 1.27, ey - 12.75, 0.85, 0.9, 0.82, top)
    # antenna meander
    for k in range(6):
        smd(pads, ex - 6 + k * 2.4, ey + 9.6, 0.5, 3.2, 0.84, top)
        if k < 5:
            smd(pads, ex - 4.8 + k * 2.4, ey + (11.0 if k % 2 == 0 else 8.2), 2.9, 0.5, 0.84, top)
    for k in range(3):
        sx = -1.8 + k * 1.8
        smd(pads, sx, 23.4, 1.2, 1.2, 0.05, top)
    part('TD_FCPadsGold', pads, col, m['enig'], grp, smooth=False)
    label('TD_ESPText', 'ESP32-S3-WROOM-1', col, grp, ((ex) * MM, (ey - 1.5) * MM, top + 3.21 * MM), 1.25 * MM, m['silk_dark'], rot=(0, 0, math.pi / 2))
    label('TD_ESPText2', 'N16R8', col, grp, ((ex - 3.0) * MM, (ey - 3.0) * MM, top + 3.21 * MM), 1.0 * MM, m['silk_dark'], rot=(0, 0, math.pi / 2))

    chips = bmesh.new()
    smd(chips, *parts['imu'][:2], 3, 2.5, 0.9, top)
    smd(chips, *parts['buck'][:2], 2.9, 1.6, 1.1, top)
    smd(chips, 14.5, -8.5, 4, 4, 0.9, top)     # USB to UART bridge
    smd(chips, -5.5, -6, 3, 3, 0.9, top)       # flash
    smd(chips, 20, 14, 5, 4, 1.2, top)         # dual buffer for the ESC lines
    smd(chips, 6, -10, 2.9, 1.6, 1.1, top)     # LDO
    part('TD_FCChips', chips, col, m['chip'], grp, bevel=0.00012)
    bm = bmesh.new()
    smd(bm, *parts['ind'][:2], 5, 5, 3, top)
    part('TD_FCInductor', bm, col, m['chip'], grp, bevel=0.0006)
    label('TD_IndText', '4R7', col, grp, (5 * MM, -16 * MM, top + 3.01 * MM), 1.5 * MM, m['silk_dark'])
    met = bmesh.new()
    smd(met, *parts['baro'][:2], 2, 2, 0.75, top)
    smd(met, *parts['xtal'][:2], 3.2, 2.5, 0.8, top)
    part('TD_FCMetal', met, col, m['shield'], grp, bevel=0.0002)

    # electrolytic capacitors with their dark sleeves and scored tops
    for k, key in enumerate(('cap1', 'cap2')):
        x, y = parts[key][:2]
        bm = bmesh.new()
        cyl(bm, 3.15 * MM, 7.7 * MM, loc=(x * MM, y * MM, top + 3.85 * MM), segs=40)
        part(f'TD_FCCapSleeve{k}', bm, col, m['cap_sleeve'], grp, bevel=0.0005)
        bm = bmesh.new()
        cyl(bm, 2.9 * MM, 0.12 * MM, loc=(x * MM, y * MM, top + 7.72 * MM), segs=40)
        part(f'TD_FCCapTop{k}', bm, col, m['cap_alu'], grp)
        bm = bmesh.new()
        box(bm, (6.7 * MM, 6.7 * MM, 0.8 * MM), loc=(x * MM, y * MM, top + 0.4 * MM))
        part(f'TD_FCCapBase{k}', bm, col, m['plastic'], grp, bevel=0.0002)

    # XT30 power input
    x, y = parts['xt30'][:2]
    bm = bmesh.new()
    box(bm, (10.2 * MM, 5.2 * MM, 6.0 * MM), loc=(x * MM, y * MM, top + 3.0 * MM))
    box(bm, (3.0 * MM, 5.2 * MM, 1.6 * MM), loc=((x - 3.6) * MM, y * MM, top + 6.6 * MM))
    part('TD_FCXT30', bm, col, m['xt'], grp, bevel=0.0005)
    bm = bmesh.new()
    for sx in (-2.5, 2.5):
        cyl(bm, 1.0 * MM, 4 * MM, loc=((x + sx) * MM, (y - 3.8) * MM, top + 3.0 * MM), rot=(math.pi / 2, 0, 0), segs=16)
    part('TD_FCXT30Pins', bm, col, m['enig'], grp)

    # USB-C, ESC header, JST-GH connectors, buttons and LEDs
    bm = bmesh.new()
    x, y = parts['usb'][:2]
    smd(bm, x, y, 9, 7.3, 3.2, top)
    part('TD_FCUSB', bm, col, m['steel'], grp, bevel=0.0012, segs=4)
    bm = bmesh.new()
    smd(bm, 0, -25.0, 8.0, 0.3, 2.3, top + 0.45 * MM)
    part('TD_FCUSBHole', bm, col, m['plastic'], grp)
    x, y = parts['hdr'][:2]
    bm = bmesh.new()
    smd(bm, x, y, 7.6, 15.3, 2.5, top)
    part('TD_FCHeader', bm, col, m['plastic'], grp, bevel=0.0002)
    pins = bmesh.new()
    for r in range(3):
        for c in range(6):
            smd(pins, x - 2.54 + r * 2.54, y - 6.35 + c * 2.54, 0.64, 0.64, 8.5, top)
    part('TD_FCPins', pins, col, m['enig'], grp, bevel=0.0001)
    gh = bmesh.new()
    for key in ('gh1', 'gh2', 'gh3', 'gh4'):
        x, y = parts[key][:2]
        smd(gh, x, y, 6, 4.3, 4.25, top)
    part('TD_FCJST', gh, col, m['jst'], grp, bevel=0.0003)
    bm = bmesh.new()
    for key in ('btn1', 'btn2'):
        x, y = parts[key][:2]
        smd(bm, x, y, 3, 4, 1.5, top)
    part('TD_FCButtons', bm, col, m['steel'], grp, bevel=0.0003)
    bm = bmesh.new()
    for key in ('btn1', 'btn2'):
        x, y = parts[key][:2]
        cyl(bm, 0.8 * MM, 0.6 * MM, loc=(x * MM, y * MM, top + 1.8 * MM), segs=16)
    part('TD_FCButtonCaps', bm, col, m['plastic'], grp)
    for k, led in enumerate(('led_red', 'led_green', 'led_status')):
        bm = bmesh.new()
        smd(bm, 2 + k * 2.2, 12, 1.6, 0.8, 0.55, top)
        part(f'TD_FCLED{k}', bm, col, m[led], grp, bevel=0.0001)

    body, ends, res = bmesh.new(), bmesh.new(), bmesh.new()
    rng = random.Random(3)
    keep = [v for v in parts.values()]
    keep += [(sx * 31.5, sy * 21.5, 6.5, 6.5) for sx in (-1, 1) for sy in (-1, 1)]
    scatter_passives(rng, 80, [(6, 2, 7), (-2, -14, 7), (-6, 5, 6), (14, -8, 6), (18, 13, 6), (-7, -7, 5)], keep, top, body, ends, res)
    part('TD_FCCaps', body, col, m['cap_tan'], grp, smooth=False)
    part('TD_FCCapEnds', ends, col, m['tin'], grp, smooth=False)
    part('TD_FCResistors', res, col, m['chip'], grp, smooth=False)

    # mounting holes: gold rings, soft-mount grommets and screws
    ring = bmesh.new()
    gr = bmesh.new()
    sc = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 31.5 * MM, sy * 21.5 * MM
            tube(ring, 3.0 * MM, 1.6 * MM, FC_T * MM + 0.06 * MM, loc=(x, y, 0), segs=32)
            tube(gr, 3.4 * MM, 1.6 * MM, 3.2 * MM, loc=(x, y, top + 1.6 * MM), segs=32)
            tube(gr, 3.4 * MM, 1.6 * MM, 6.0 * MM, loc=(x, y, -top - 3.0 * MM), segs=32)
            cyl(sc, 2.7 * MM, 1.8 * MM, loc=(x, y, top + 4.1 * MM), segs=28)
            cyl(sc, 1.5 * MM, 13 * MM, loc=(x, y, -2.0 * MM), segs=16)
    part('TD_FCHoleRings', ring, col, m['enig'], grp)
    part('TD_FCGrommets', gr, col, m['grommet'], grp, bevel=0.0006)
    part('TD_FCScrews', sc, col, m['black_steel'], grp, bevel=0.0004)

    label('TD_FCName', 'TD-FC  REV A', col, grp, (6 * MM, -3.5 * MM, top + 0.03 * MM), 1.7 * MM, m['silk'])
    label('TD_FCName2', 'TETHERED DRONE 2026', col, grp, (6 * MM, -6.3 * MM, top + 0.03 * MM), 1.15 * MM, m['silk'])
    label('TD_FCEsc', 'ESC 1-6', col, grp, (27.5 * MM, 11.4 * MM, top + 0.03 * MM), 1.2 * MM, m['silk'])
    for k, (key, txt) in enumerate((('gh1', 'PI'), ('gh2', 'GPS'), ('gh3', 'TLM'), ('gh4', 'PWR'))):
        x, y = parts[key][:2]
        label(f'TD_FCJ{k}', txt, col, grp, (x * MM, (y - 3.6 * (1 if y > 0 else -1)) * MM, top + 0.03 * MM), 1.0 * MM, m['silk'])
    return grp


# ---------------------------------------------------------------- Raspberry Pi and camera

PI_W, PI_H = 85.0, 56.0


def build_pi(m, col, root):
    grp = empty('TD_GrpPi', col, root, loc=(0, -0.058, TOP_FACE + 0.0115))
    top = 0.7 * MM
    parts = {'eth': (34, 10, 21, 16), 'usb1': (34, -6.5, 17.5, 13.1), 'usb2': (34, -20.5, 17.5, 13.1),
             'gpio': (-10, 23.5, 51, 5), 'cool': (-10, -2, 40, 36), 'hdmi1': (-17, -25.5, 7.5, 6),
             'hdmi2': (-4, -25.5, 7.5, 6), 'pwr': (-31, -25, 9, 7.3), 'ffc': (14, 13.5, 15, 3), 'rp1': (14, -9, 7, 7)}
    img = pcb_image('TD_Pi_Art', PI_W, PI_H, seed=11, traces=120, outlines=[parts[k] for k in ('rp1', 'ffc', 'hdmi1', 'hdmi2')])
    mat = pcb_material('TD_Pi_Board', (0.02, 0.13, 0.045), img, PI_W * MM, PI_H * MM)
    bm = bmesh.new()
    board_bm(bm, PI_W * MM, PI_H * MM, 1.4 * MM, r=0.003)
    brd = part('TD_PiBoard', bm, col, mat, grp, angle=40)
    cuts = []
    for hx in (-39, 19):
        for hy in (-24.5, 24.5):
            bm = bmesh.new()
            cyl(bm, 1.35 * MM, 0.01, loc=(hx * MM, hy * MM, 0), segs=24)
            cuts.append(cutter(f'cut_pi{hx}{hy}', bm, col))
    cut(brd, cuts)
    ring = bmesh.new()
    so = bmesh.new()
    for hx in (-39, 19):
        for hy in (-24.5, 24.5):
            tube(ring, 3.0 * MM, 1.35 * MM, 1.46 * MM, loc=(hx * MM, hy * MM, 0), segs=28)
            cyl(so, 2.75 * MM, 10.5 * MM, loc=(hx * MM, hy * MM, -5.95 * MM), segs=6)
            cyl(so, 2.6 * MM, 1.6 * MM, loc=(hx * MM, hy * MM, top + 0.8 * MM), segs=24)
    part('TD_PiRings', ring, col, m['enig'], grp)
    part('TD_PiStandoffs', so, col, m['gold'], grp, bevel=0.0003)

    # USB and Ethernet: folded steel shells with dark openings
    shells = bmesh.new()
    for key, hgt in (('eth', 13.5), ('usb1', 15.6), ('usb2', 15.6)):
        x, y, w, h = parts[key]
        smd(shells, x, y, w, h, hgt, top)
    part('TD_PiPorts', shells, col, m['steel'], grp, bevel=0.0005)
    holes = bmesh.new()
    x, y, w, h = parts['eth']
    smd(holes, x + w / 2 + 0.05, y, 0.2, 12, 9, top + 2 * MM)
    for key in ('usb1', 'usb2'):
        x, y, w, h = parts[key]
        for z in (2.2, 9.6):
            smd(holes, x + w / 2 + 0.05, y, 0.2, 11, 4.6, top + z * MM)
    part('TD_PiPortHoles', holes, col, m['plastic'], grp)
    tongues = bmesh.new()
    for key in ('usb1', 'usb2'):
        x, y, w, h = parts[key]
        for z in (3.6, 11.0):
            smd(tongues, x + w / 2 - 2.2, y, 4.5, 9, 1.6, top + z * MM)
    part('TD_PiTongues', tongues, col, m['wire_blue'], grp)

    # GPIO header
    x, y, w, h = parts['gpio']
    bm = bmesh.new()
    smd(bm, x, y, w, h, 2.5, top)
    part('TD_PiGPIO', bm, col, m['plastic'], grp, bevel=0.0002)
    pins = bmesh.new()
    for c in range(20):
        for r in range(2):
            smd(pins, x - 24.13 + c * 2.54, y - 1.27 + r * 2.54, 0.64, 0.64, 8.5, top)
    part('TD_PiPins', pins, col, m['enig'], grp)

    # small parts: HDMI, USB-C, camera connector, RP1, RAM, PMIC
    met = bmesh.new()
    for key in ('hdmi1', 'hdmi2', 'pwr'):
        x, y, w, h = parts[key]
        smd(met, x, y, w, h, 3.2, top)
    part('TD_PiSmallPorts', met, col, m['steel'], grp, bevel=0.0006, segs=3)
    chips = bmesh.new()
    smd(chips, *parts['rp1'][:2], 7, 7, 1.0, top)
    smd(chips, 22, 18, 5, 5, 0.9, top)
    smd(chips, -33, 6, 4, 4, 0.9, top)
    part('TD_PiChips', chips, col, m['chip'], grp, bevel=0.0001)
    bm = bmesh.new()
    x, y, w, h = parts['ffc']
    smd(bm, x, y, w, h, 2.4, top)
    part('TD_PiFFCConn', bm, col, m['plastic'], grp, bevel=0.0002)
    bm = bmesh.new()
    smd(bm, x, y - 0.6, w * 0.92, 1.0, 0.8, top + 2.4 * MM)
    part('TD_PiFFCLatch', bm, col, m['plastic_white'], grp)

    # active cooler: finned heatsink with a fan
    x, y, w, h = parts['cool']
    bm = bmesh.new()
    smd(bm, x, y, w, h, 2.0, top + 1.2 * MM)
    for k in range(13):
        smd(bm, x - w / 2 + 1.5 + k * 3.08, y, 1.0, h, 7.5, top + 3.2 * MM)
    part('TD_PiHeatsink', bm, col, m['fan'], grp, bevel=0.00025)
    bm = bmesh.new()
    tube(bm, 15.5 * MM, 14.2 * MM, 8.6 * MM, loc=((x - 3) * MM, y * MM, top + 7.5 * MM), segs=48)
    box(bm, (31 * MM, 31 * MM, 1.2 * MM), loc=((x - 3) * MM, y * MM, top + 11.2 * MM))
    fan = part('TD_PiFanFrame', bm, col, m['fan'], grp, bevel=0.0003)
    bm = bmesh.new()
    cyl(bm, 15.0 * MM, 2 * MM, loc=((x - 3) * MM, y * MM, top + 11.2 * MM), segs=48)
    cut(fan, [cutter('cut_fan', bm, col)])
    blades = bmesh.new()
    cyl(blades, 5.5 * MM, 6.5 * MM, loc=((x - 3) * MM, y * MM, top + 8.2 * MM), segs=32)
    for k in range(7):
        a = TAU * k / 7
        box(blades, (8.5 * MM, 3.2 * MM, 0.5 * MM), loc=((x - 3) * MM + 9.6 * MM * math.cos(a), y * MM + 9.6 * MM * math.sin(a), top + 8.4 * MM),
            rot=(0.45, 0, a + math.pi / 2))
    part('TD_PiFanBlades', blades, col, m['fan'], grp, bevel=0.0002)

    passives(m, col, grp, 13, 60, [(14, -9, 7), (22, 18, 6), (-33, 6, 6), (0, -18, 8), (12, 3, 5)],
             list(parts.values()) + [(hx, hy, 6, 6) for hx in (-39, 19) for hy in (-24.5, 24.5)], top, 'TD_Pi')
    return grp


def passives(m, col, grp, seed, n, clusters, keep, top, prefix):
    body, ends, res = bmesh.new(), bmesh.new(), bmesh.new()
    scatter_passives(random.Random(seed), n, clusters, keep, top, body, ends, res)
    part(prefix + 'Caps', body, col, m['cap_tan'], grp, smooth=False)
    part(prefix + 'CapEnds', ends, col, m['tin'], grp, smooth=False)
    part(prefix + 'Resistors', res, col, m['chip'], grp, smooth=False)


def build_camera(m, col, root):
    """Pi camera module on an L-bracket at the front of the top plate, lens to the glass and tilted up a touch."""
    grp = empty('TD_GrpCam', col, root, loc=(0, 0.121, TOP_FACE))
    br = bmesh.new()
    box(br, (0.032, 0.02, 0.0025), loc=(0, -0.006, 0.00125))       # foot, screwed to the top plate
    box(br, (0.032, 0.0025, 0.034), loc=(0, 0.0028, 0.017))        # upright the module mounts to
    part('TD_CamBracket', br, col, m['carbon'], grp, bevel=0.0005)
    bm = bmesh.new()
    for x in (-0.011, 0.011):
        cyl(bm, 0.0022, 0.0015, loc=(x, -0.01, 0.0032), segs=16)
    part('TD_CamBracketScrews', bm, col, m['black_steel'], grp)
    tilt = empty('TD_CamTilt', col, grp, loc=(0, 0.0058, 0.02), rot=(-math.radians(82), 0, 0))
    bm = bmesh.new()
    board_bm(bm, 25 * MM, 24 * MM, 1.0 * MM, r=0.002)
    img = pcb_image('TD_Cam_Art', 25, 24, seed=21, traces=40)
    part('TD_CamBoard', bm, col, pcb_material('TD_Cam_Board', (0.02, 0.13, 0.045), img, 0.025, 0.024), tilt)
    bm = bmesh.new()
    smd(bm, 0, 1.5, 8.5, 8.5, 2.6, 0.5 * MM)
    part('TD_CamLensBase', bm, col, m['plastic'], tilt, bevel=0.0004)
    bm = bmesh.new()
    cyl(bm, 3.6 * MM, 3.2 * MM, loc=(0, 1.5 * MM, 4.6 * MM), segs=40)
    part('TD_CamBarrel', bm, col, m['plastic'], tilt, bevel=0.0003)
    bm = bmesh.new()
    sphere(bm, 2.4 * MM, loc=(0, 1.5 * MM, 6.1 * MM), scale=(1, 1, 0.35), segs=32, rings=12)
    part('TD_CamGlass', bm, col, m['lens'], tilt)
    bm = bmesh.new()
    smd(bm, 0, -9.5, 21, 5.5, 2.7, 0.5 * MM)
    part('TD_CamConn', bm, col, m['plastic'], tilt, bevel=0.0002)
    ring = bmesh.new()
    for sx in (-10.5, 10.5):
        for sy in (-10, 2.5):
            tube(ring, 2.0 * MM, 1.1 * MM, 1.06 * MM, loc=(sx * MM, sy * MM, 0), segs=24)
    part('TD_CamRings', ring, col, m['enig'], tilt)
    passives(m, col, tilt, 22, 18, [(-7, -4, 4), (7, -4, 4)], [(0, 1.5, 9, 9), (0, -9.5, 21, 5.5)], 0.5 * MM, 'TD_Cam')
    return grp


def ffc_ribbon(m, col, root, a, b, ctrl, width=0.016, name='TD_CamRibbon'):
    """A flat flex cable as a mesh strip along a bezier from a to b, its width kept along X."""
    pts = []
    n = 40
    P = [Vector(a), Vector(ctrl[0]), Vector(ctrl[1]), Vector(b)]
    for k in range(n + 1):
        t = k / n
        p = (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]
        pts.append(p)
    bm = bmesh.new()
    left, right = [], []
    for p in pts:
        left.append(bm.verts.new(p + Vector((-width / 2, 0, 0))))
        right.append(bm.verts.new(p + Vector((width / 2, 0, 0))))
    for k in range(n):
        bm.faces.new((left[k], right[k], right[k + 1], left[k + 1]))
    me = to_mesh(name, bm, mats=[m['ffc']])
    ob = obj(name, me, col, root)
    s = ob.modifiers.new('thick', 'SOLIDIFY')
    s.thickness = 0.0003
    return ob


def build_gps(m, col, root):
    grp = empty('TD_GrpGPS', col, root, loc=(0, -0.112, TOP_FACE))
    bm = bmesh.new()
    box(bm, (0.018, 0.018, 0.008), loc=(0, 0, 0.004))
    part('TD_GPSBase', bm, col, m['gunmetal'], grp, bevel=0.0012)
    bm = bmesh.new()
    tube(bm, 0.004, 0.003, 0.11, loc=(0, 0, 0.062), segs=24)
    part('TD_GPSMast', bm, col, m['carbon_tube'], grp)
    bm = bmesh.new()
    cyl(bm, 0.028, 0.006, loc=(0, 0, 0.12), segs=64)
    part('TD_GPSPuckBase', bm, col, m['plastic'], grp, bevel=0.002, segs=3)
    bm = bmesh.new()
    sphere(bm, 0.0275, loc=(0, 0, 0.123), scale=(1, 1, 0.3), segs=64, rings=16)
    part('TD_GPSDome', bm, col, m['gps_dome'], grp)
    bm = bmesh.new()
    prism(bm, [(0, 0.012), (-0.006, 0.0), (-0.002, 0.0), (-0.002, -0.01), (0.002, -0.01), (0.002, 0.0), (0.006, 0.0)], 0.1311, 0.1313)
    part('TD_GPSArrow', bm, col, m['plastic'], grp, smooth=False)
    return grp


# ---------------------------------------------------------------- power

def build_power(m, col, root):
    pdb = empty('TD_GrpPDB', col, root, loc=(0, 0, UNDER - 0.0035))
    img = pcb_image('TD_PDB_Art', 236, 236, seed=31, ppm=5, traces=60)
    mat = pcb_material('TD_PDB_Board', (0.012, 0.014, 0.016), img, 0.236, 0.236)
    bm = bmesh.new()
    prism(bm, plate_outline(0.118, 0.026), -0.0008, 0.0008)
    part('TD_PDBBoard', bm, col, mat, pdb, angle=40, bevel=0.0003)
    # bare copper bus pads under each arm, with solder joints
    pads, blobs = bmesh.new(), bmesh.new()
    for a in ARM_ANGLES:
        for k in range(2):
            dy = (k - 0.5) * 0.005
            r = 0.104
            x, y = r * math.cos(a) - dy * math.sin(a), r * math.sin(a) + dy * math.cos(a)
            box(pads, (0.011, 0.0042, 0.0002), loc=(x, y, -0.0009), rot=(0, 0, a))
            sphere(blobs, 0.0028, loc=(x, y, -0.0011), scale=(1.4, 0.8, 0.45), segs=16, rings=8, rot=(0, 0, a))
    part('TD_PDBPads', pads, col, m['tin'], pdb, smooth=False)
    part('TD_PDBSolder', blobs, col, m['tin'], pdb)
    # bulk capacitors on the bus
    for k, (x, y) in enumerate(((0.05, 0.055), (-0.05, 0.055))):
        bm = bmesh.new()
        cyl(bm, 0.008, 0.026, loc=(x, y, -0.0008 - 0.013), segs=40)
        part(f'TD_BusCap{k}', bm, col, m['cap_sleeve'], pdb, bevel=0.001)
        bm = bmesh.new()
        cyl(bm, 0.0076, 0.0003, loc=(x, y, -0.0008 - 0.0262), segs=40)
        part(f'TD_BusCapEnd{k}', bm, col, m['cap_alu'], pdb)

    dc = empty('TD_GrpDCDC', col, root, loc=(0, -0.076, UNDER - 0.0045 - 0.0145))
    bm = bmesh.new()
    box(bm, (0.1, 0.07, 0.022), loc=(0, 0, 0.0015))
    part('TD_DCDCCase', bm, col, m['alu_dark'], dc, bevel=0.0025, segs=3)
    fins = bmesh.new()
    for k in range(11):
        box(fins, (0.094, 0.0022, 0.009), loc=(0, -0.031 + k * 0.0062, -0.0135))
    part('TD_DCDCFins', fins, col, m['alu_dark'], dc, bevel=0.0006)
    bm = bmesh.new()
    box(bm, (0.06, 0.004, 0.0003), loc=(0, -0.0352, 0.003), rot=(math.pi / 2, 0, 0))
    part('TD_DCDCLabel', bm, col, m['plastic_white'], dc, smooth=False)
    label('TD_DCDCText', 'TETHER POWER', col, dc, (0, -0.0355, 0.0055), 0.0032, m['silk_dark'], rot=(math.pi / 2, 0, 0))
    label('TD_DCDCText2', 'DC-DC CONVERTER', col, dc, (0, -0.0355, 0.0005), 0.0032, m['silk_dark'], rot=(math.pi / 2, 0, 0))
    glands = bmesh.new()
    for x in (-0.025, 0.025):
        cyl(glands, 0.0065, 0.01, loc=(x, 0.039, 0.0), rot=(math.pi / 2, 0, 0), segs=6)
    part('TD_DCDCGlands', glands, col, m['plastic'], dc, bevel=0.0008)
    # output leads up to the distribution board
    for k, (x, mat) in enumerate(((-0.012, 'wire_red'), (0.012, 'wire_black'))):
        wire(f'TD_DCOut{k}', [(x, -0.036, 0.004), (x, -0.045, 0.012), (x * 1.3, -0.04, 0.0145)], 0.0032, m[mat], col, dc)
    return pdb, dc


# ---------------------------------------------------------------- canopy

def build_canopy(m, col, root):
    grp = empty('TD_GrpCanopy', col, root, loc=(0, 0.018, TOP_FACE))
    bm = bmesh.new()
    sphere(bm, 1.0, scale=(0.104, 0.122, 0.082), segs=72, rings=36)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-5], context='VERTS')
    sh = part('TD_Canopy', bm, col, m['canopy'], grp)
    s = sh.modifiers.new('thick', 'SOLIDIFY')
    s.thickness = 0.0016
    s.offset = -1
    bm = bmesh.new()
    vs = tube(bm, 1.0, 0.955, 0.004, loc=(0, 0, 0.002), segs=96)
    bmesh.ops.scale(bm, vec=(0.1062, 0.1242, 1.0), verts=vs)
    part('TD_CanopyRim', bm, col, m['gold'], grp, angle=50)
    return grp


def extra_materials(m):
    m['silk_dark'] = principled('TD_Laser', (0.16, 0.16, 0.17), 0.3, 0.5)
    m['tin'] = principled('TD_Tin', (0.72, 0.73, 0.75), 1.0, 0.25)
    m['cap_sleeve'] = principled('TD_CapSleeve', (0.02, 0.03, 0.08), 0.0, 0.3, coat=0.6, coat_rough=0.1)
    m['grommet'] = principled('TD_Grommet', (0.75, 0.32, 0.04), 0.0, 0.55, sss=0.1)
    m['alu_dark'] = brushed('TD_AluDark', (0.11, 0.115, 0.125), rough=0.36)
    m['gps_dome'] = principled('TD_GPSDome', (0.6, 0.6, 0.6), 0.0, 0.3, coat=0.5)


def build_electronics(m, root):
    col = coll('TD Drone')
    extra_materials(m)
    fc = build_fc(m, col, root)
    pi = build_pi(m, col, root)
    cam = build_camera(m, col, root)
    gps = build_gps(m, col, root)
    pdb, dc = build_power(m, col, root)
    can = build_canopy(m, col, root)
    return {'fc': fc, 'pi': pi, 'cam': cam, 'gps': gps, 'pdb': pdb, 'dc': dc, 'canopy': can}
