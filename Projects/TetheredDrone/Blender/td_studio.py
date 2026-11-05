# Studio for the breakdown: soft key, strong rim lights so black carbon reads against the site's dark board,
# and a gradient world for reflections. The background renders transparent.

def area(name, col, loc, target, size, energy, color=(1, 1, 1), shape='RECTANGLE', size_y=None):
    li = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'AREA')
    li.shape = shape
    li.size = size
    li.size_y = size_y or size
    li.energy = energy
    li.color = color
    ob = obj(name, li, col, loc=loc)
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def studio_world():
    w = bpy.data.worlds.get('TD_StudioWorld') or bpy.data.worlds.new('TD_StudioWorld')
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = add(nt, 'ShaderNodeOutputWorld', (600, 0))
    bg = add(nt, 'ShaderNodeBackground', (400, 0))
    tc = add(nt, 'ShaderNodeTexCoord', (-400, 0))
    sep = add(nt, 'ShaderNodeSeparateXYZ', (-200, 0))
    link(nt, tc.outputs['Generated'], sep.inputs[0])
    ramp = add(nt, 'ShaderNodeValToRGB', (0, 0))
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = (0.01, 0.011, 0.013, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.05, 0.052, 0.056, 1)
    link(nt, sep.outputs['Z'], ramp.inputs['Fac'])
    link(nt, ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 0.6
    link(nt, bg.outputs[0], out.inputs[0])
    w.use_fake_user = True
    return w


def studio():
    col = coll('TD Studio')
    tgt = empty('TD_StudioTarget', col, loc=(0, 0, 0))
    cam_data = bpy.data.cameras.get('TD_StudioCam') or bpy.data.cameras.new('TD_StudioCam')
    cam_data.lens = 50
    cam_data.clip_start = 0.01
    cam_data.clip_end = 100
    cam = obj('TD_StudioCam', cam_data, col, loc=(1.6, -2.2, 1.2))
    c = cam.constraints.new('TRACK_TO')
    c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    area('TD_Key', col, (-1.8, -1.9, 2.4), (0, 0, 0), 1.6, 150, (1.0, 0.97, 0.93))
    area('TD_Fill', col, (2.6, -1.2, 0.3), (0, 0, 0), 2.5, 40, (0.85, 0.9, 1.0))
    area('TD_RimL', col, (-2.2, 2.4, 1.0), (0, 0, 0.05), 0.5, 260, (0.9, 0.95, 1.0), size_y=2.4)
    area('TD_RimR', col, (2.4, 2.2, 1.4), (0, 0, 0.05), 0.5, 300, (1.0, 0.92, 0.8), size_y=2.4)
    area('TD_Top', col, (0, 0, 3.0), (0, 0, 0), 1.6, 10, (1, 1, 1), shape='DISK')
    return cam


def render_settings(scene, w=1600, h=900, samples=64):
    r = scene.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.film_transparent = True
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGBA'
    e = scene.eevee
    e.taa_render_samples = samples
    e.use_raytracing = True
    e.ray_tracing_method = 'SCREEN'
    e.use_shadows = True
    e.shadow_ray_count = 2
    e.shadow_step_count = 8
    e.use_fast_gi = True
    e.fast_gi_method = 'GLOBAL_ILLUMINATION'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
