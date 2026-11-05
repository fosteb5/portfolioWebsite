# Rebuilds the whole drone from the module files. exec() this from Blender's Python.
import bpy, os
R = r"C:\Users\foste\OneDrive\Resume\portfolioWebsite\Projects\TetheredDrone\Blender"
G = {}
for _f in ('td_lib.py', 'td_build.py', 'td_motor.py', 'td_electronics.py', 'td_systems.py', 'td_studio.py',
           'td_facade.py', 'td_spray.py', 'td_scene.py', 'td_anim.py'):
    _p = os.path.join(R, _f)
    if os.path.exists(_p):
        exec(compile(open(_p, encoding='utf-8').read(), _p, 'exec'), G)


def build_all():
    m = G['materials']()
    root, body, arms = G['build_frame'](m)
    motors, props = G['build_propulsion'](m, arms)
    if 'build_electronics' in G:
        G['build_electronics'](m, root)
    if 'build_systems' in G:
        G['build_systems'](m, root)
    G['studio']()
    G['studio_world']()
    G['sky_world']()
    G['build_facade'](m)
    G['build_spray'](m)
    # clear out meshes left behind by earlier builds
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    for cu in list(bpy.data.curves):
        if cu.users == 0:
            bpy.data.curves.remove(cu)
    return m


def preview(name, cam_loc, target=(0, 0, 0), lens=50, w=1280, h=720, samples=24):
    sc = bpy.context.scene
    cam = bpy.data.objects['TD_StudioCam']
    cam.location = cam_loc
    cam.data.lens = lens
    bpy.data.objects['TD_StudioTarget'].location = target
    sc.camera = cam
    G['render_settings'](sc, w, h, samples)
    sc.render.filepath = os.path.join(R, 'renders', 'preview', name + '.png')
    bpy.ops.render.render(write_still=True)
    return sc.render.filepath
