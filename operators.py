import bpy
import os
from . import analysis
from . import optimizer
from . import weights
from . import cleanup


def _save_backup(context):
    """
    Saves a COPY of the current file (not overwriting the working file)
    before a destructive operation runs. Returns (backup_path, error) —
    error is None on success, or a message if there's nothing to back up.
    """
    filepath = bpy.data.filepath
    if not filepath:
        return None, "File has never been saved — please save your .blend file first"

    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    backup_path = os.path.join(directory, f"{name}_before_compress{ext}")

    # copy=True saves a copy WITHOUT making it the active file — your
    # current session keeps working on the original path
    bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=True)
    return backup_path, None


class CHAINOPT_OT_pick_root(bpy.types.Operator):
    bl_idname = "chainopt.pick_root"
    bl_label = "Pick Root From Selection"
    bl_description = "Use the bone currently selected in the viewport (Edit or Pose mode) as the root"

    def execute(self, context):
        armature = context.scene.chain_opt_armature
        if armature is None:
            self.report({'ERROR'}, "Select an armature first")
            return {'CANCELLED'}

        # Pose Mode and Edit Mode track "the active bone" in DIFFERENT
        # places in Blender's API — this was the actual bug. Pose Mode
        # selection lives on context.active_pose_bone; Edit Mode
        # selection lives on context.active_bone. Checking only one
        # meant the other mode silently never worked.
        bone_name = None
        if context.mode == 'POSE' and context.active_pose_bone:
            bone_name = context.active_pose_bone.name
        elif context.mode == 'EDIT_ARMATURE' and context.active_bone:
            bone_name = context.active_bone.name

        if bone_name is None:
            self.report(
                {'ERROR'},
                "No bone selected — click a bone on the armature in "
                "Edit Mode or Pose Mode first, then try again"
            )
            return {'CANCELLED'}

        context.scene.chain_opt_root_bone = bone_name
        self.report({'INFO'}, f"Root bone set to '{bone_name}'")
        return {'FINISHED'}


class CHAINOPT_OT_compress(bpy.types.Operator):
    bl_idname = "chainopt.compress"
    bl_label = "Compress Chain"
    bl_description = "Shorten the selected bone chain to the target segment count"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # Blender's built-in confirmation popup — shows an OK/Cancel
        # dialog and only calls execute() if the user confirms. One
        # line covers the whole "are you sure?" step.
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene
        armature = scene.chain_opt_armature
        root_bone = scene.chain_opt_root_bone
        segments = scene.chain_opt_segments

        if armature is None:
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}
        if not root_bone or root_bone == 'NONE':
            self.report({'ERROR'}, "No root bone specified")
            return {'CANCELLED'}

        try:
            chain = analysis.get_bone_chain(armature, root_bone)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        # Guard against segment counts the compression math can't
        # actually support - requesting more segments than the chain
        # has bones for would make the formula produce duplicate/
        # colliding bone indices instead of a clean result.
        max_segments = len(chain) - 1
        if segments > max_segments:
            self.report(
                {'ERROR'},
                f"Target segments ({segments}) exceeds this chain's length "
                f"— max is {max_segments} for a {len(chain)}-bone chain"
            )
            return {'CANCELLED'}

        # All validation passed - now it's safe to actually save a
        # backup, since we know this run isn't about to fail immediately.
        backup_path, backup_error = _save_backup(context)
        if backup_error:
            self.report({'ERROR'}, backup_error)
            return {'CANCELLED'}

        kept = optimizer.shorten_chain(chain, segments)

        reassignment_map, affected_meshes = weights.apply_weight_reassignment(
            armature, chain, kept
        )

        cleanup_result = cleanup.apply_cleanup(armature, chain, kept)

        print(f"Full chain ({len(chain)} bones): {chain}")
        print(f"Kept after compression ({len(kept)} bones): {kept}")
        print(f"Reassignment map: {reassignment_map}")
        print(f"Deleted bones: {cleanup_result['deleted_bones']}")
        print(f"Renamed bones: {cleanup_result['renamed_bones']}")
        print(f"Meshes touched: {cleanup_result['affected_meshes']}")

        self.report(
            {'INFO'},
            f"Backup saved to {os.path.basename(backup_path)}. "
            f"Compressed to {len(kept)} bones. "
            f"Deleted {len(cleanup_result['deleted_bones'])}, "
            f"renamed {len(cleanup_result['renamed_bones'])}."
        )
        return {'FINISHED'}
