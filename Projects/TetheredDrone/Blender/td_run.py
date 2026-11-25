# Loads the tethered drone's build and render code into G. exec() this from Blender's Python, then:
#   G['build_all']('proto')   the demo prototype, for the breakdown in the studio
#   G['build_all']('full')    the full-size drone, for the washing scene
# td_quad.py loads last and replaces the older hexacopter airframe from td_build.py.
import bpy, os
R = r"C:\Users\foste\OneDrive\Resume\portfolioWebsite\Projects\TetheredDrone\Blender"
G = {}
for _f in ('td_lib.py', 'td_build.py', 'td_motor.py', 'td_electronics.py', 'td_systems.py', 'td_studio.py',
           'td_facade.py', 'td_spray.py', 'td_scene.py', 'td_anim.py', 'td_quad.py'):
    _p = os.path.join(R, _f)
    exec(compile(open(_p, encoding='utf-8').read(), _p, 'exec'), G)
build_all = G['build_all']


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
