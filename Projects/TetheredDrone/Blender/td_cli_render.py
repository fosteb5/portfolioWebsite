# Renders frames in a background Blender, so the open Blender window stays free:
#   blender -b tethered-drone.blend --python td_cli_render.py -- wash 1 120
#   blender -b tethered-drone.blend --python td_cli_render.py -- break 1 132
#   blender -b tethered-drone.blend --python td_cli_render.py -- hero
import bpy, os, sys
R = os.path.dirname(os.path.abspath(bpy.data.filepath))
ns = {}
exec(open(os.path.join(R, 'td_run.py'), encoding='utf-8').read(), ns)
G = ns['G']
args = sys.argv[sys.argv.index('--') + 1:]
kind = args[0]
if kind == 'wash':
    G['render_wash'](frames=range(int(args[1]), int(args[2]) + 1))
elif kind == 'break':
    G['render_breakdown'](frames=range(int(args[1]), int(args[2]) + 1))
elif kind == 'hero':
    G['render_hero']()
