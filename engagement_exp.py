__author__ = 'nickdg'

import os
import random
import interactions
import numpy as np
import ratcave.graphics as graphics
from ratcave.utils import timers, rotate_to_var

import ratcave.graphics.resources as resources


from psychopy import event

# Note: Collect Metadata (subject, mainly, and Session Parameters) for the log
nPhases = 2
total_phase_secs = 5 * 60.  # 5 minutes
corner_idx = 1 #random.randint(1, 4)  # Select which corner everything appears in.
interaction_level = 0 #random.randint(0, 2)  # Three different levels
interaction_distance = .05  # In meters (I think)

metadata = {'Total Phases: ': nPhases,
            'Phase Time (secs)': total_phase_secs,
            'Corner ID where Objects Appear:': corner_idx,
            'Interactivity Amount (0-2)': interaction_level,
            'Rat-Object Distance Where Interaction Activates (meters)': interaction_distance,
            'Experimenter': 'Nicholas A. Del Grosso'}


# Note: Connect to Motive, and get rigid bodies to track
# FIXME: Plan to use the NatNetClient, not MotivePy, for this experiment.
import motive
motive.load_project(os.path.join('..', 'vr_demo', 'vr_demo.ttp'))
motive.update()
arena_rb = motive.get_rigid_bodies()['Arena']
rat_rb = motive.get_rigid_bodies()['Rat']

# Calculate Arena's orientation
for attempt in range(3):
        arena_rb.reset_orientation()
        motive.update()
arena_markers = np.array(arena_rb.point_cloud_markers)
additional_rotation = rotate_to_var(arena_markers)


# Note: Get Arena and locations for meshes to appear in the arena
reader = graphics.WavefrontReader(graphics.resources.obj_arena)
arena = reader.get_mesh('Arena', lighting=True, centered=False)
del reader

# Generate list of dict of position-triples (4 corners, paired with 4 sides, each with a center)
reader =graphics.WavefrontReader(os.path.join('obj', 'VR_Playground.obj'))
mesh_pos = {'Center': None, 'Side': None, 'Corner': None}
for coord in mesh_pos:
    mesh_name = 'Pos' + coord + str(corner_idx) if coord is not 'Center' else 'Pos' + coord
    mesh = reader.get_mesh(mesh_name)
    mesh_pos[coord] = mesh.local.position


# Note: Only for interaction levels 1 and 2 (No Virtual Meshes in interaction level 0)
mesh_groups = [[]] * nPhases
if interaction_level > 0:

    # Note: Import Mesh Objects (randomly chosen) and put in groups of three, one group for each phase
    vir_reader = graphics.WavefrontReader(os.path.join('obj', 'NOP_Primitives.obj'))
    for group in mesh_groups:
        mesh_list = []
        for pos_coords in mesh_pos.values():
            mesh_list.append(vir_reader.get_mesh(random.choice(vir_reader.mesh_names), position=pos_coords, centered=True))
    # Note: Interaction Level 2: Assign Object Properties (based on Interaction Level)
    if interaction_level == 2:
        interact_opts = [interactions.Jumper, interactions.Scaler, interactions.Spinner]
        for group in mesh_groups:
           for mesh, new_local in zip(mesh_list, [random.choice(interact_opts) for mesh in mesh_list]):
                mesh.local = new_local(position=mesh.local.position)
# Note: Build Scenes (1st half, 2nd half) and window
vir_scenes = [graphics.Scene(meshes) for meshes in mesh_groups]
active_scene = graphics.Scene([arena])
active_scene.camera = graphics.projector
active_scene.camera.fov_y = 27.8
active_scene.light.position = active_scene.camera.position
active_scene.bgColor.b = .5


window = graphics.Window(active_scene, fullscr=True, screen=1)
window.virtual_scene = vir_scenes[0]

while 'escape' not in event.getKeys():
        motive.update()
        for mesh in window.virtual_scene.meshes + [arena]:
            mesh.world.position = arena_rb.location
            mesh.world.rotation = arena_rb.rotation_global
            mesh.world.rot_y += additional_rotation
        window.draw()
        window.flip()
#
# # Note: Main Experiment Logic
# with graphics.Logger(scenes=vir_scenes+[active_scene], exp_name='VR_Engagement', log_directory=os.path.join('.', 'logs'),
#                      metadata_dict=metadata) as logger:

    # for phase in xrange(nPhases):
    #
    #     window.virtual_scene = vir_scenes[phase]
    #     arena.cubemap = True
    #     logger.write('Start of Phase {}'.format(phase))
    #
    #     for _ in timers.countdown_timer(total_phase_secs, stop_iteration=True):
    #
    #         # Update Data
    #         motive.update()
    #
    #         for mesh in window.virtual_scene.meshes:
    #
    #             # Update the Rat's position on the virtual scene's camera
    #             window.virtual_scene.camera.position = rat_rb.location  # FIXME: Fix when adding in tracking!
    #             window.virtual_scene.camera.rotation = rat_rb.rotation_global
    #             mesh.world.rot_y += additional_rotation
    #
    #             # Update the positions of everything, based on the Optitrack data
    #             mesh.world.position = arena.local.position
    #             mesh.world.rotation = arena.local.rotation
    #
    #             # Activate the mesh's custom physics if the rat gets close
    #             if np.linalg.norm(np.subtract(window.virtual_scene.camera.position, mesh)) < interaction_distance:
    #                 mesh.local.start()
    #
    #             # Update all mesh's physics
    #             mesh.local.update()
    #
    #         # Draw and Flip
    #         window.draw()
    #         logger.write()
    #         window.flip()
    #
    #
    #         # Give keyboard option to cleanly break out of the nested for-loop
    #         if 'escape' in event.getKeys():
    #             break
    #     else:
    #         continue
    #     break




# Note: Clean-Up Section
window.close()