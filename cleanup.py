import bpy
from . import weights


def apply_cleanup(armature_object, chain, kept_names):
    
    # Final step: deletes bones that didn't survive, renames surviving
    # bones (except the root — per the compatibility requirement) with an
    # "opt_" prefix, and mirrors both changes onto every associated mesh's
    # vertex groups so they keep matching the armature's actual bone names.

    # Must be called with armature_object able to become the active
    # object; this temporarily switches into Edit Mode and restores the
    # original mode afterward.
    
    root_name = chain[0]
    deleted_names = [n for n in chain if n not in kept_names]
    rename_targets = [n for n in kept_names if n != root_name]

    # --- Step 1: edit the armature itself ---
    previous_mode = armature_object.mode
    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    edit_bones = armature_object.data.edit_bones

    # Before deleting anything, grab live references to the bones that
    # WILL survive, plus a snapshot of each kept bone's original head
    # position. We need the ORIGINAL head positions (before any bone
    # gets deleted) so we know exactly where each surviving bone's tail
    # needs to stretch to, to close the gap left by its deleted
    # neighbors.
    kept_edit_bones = [edit_bones[name] for name in kept_names]
    kept_original_heads = [eb.head.copy() for eb in kept_edit_bones]

    for name in deleted_names:
        eb = edit_bones.get(name)
        if eb is not None:
            edit_bones.remove(eb)

    # Now stretch + re-parent the survivors so the chain is one
    # continuous, connected line again instead of having gaps where
    # bones used to be.
    for i, eb in enumerate(kept_edit_bones):
        if i < len(kept_edit_bones) - 1:
            # Stretch this bone's tail to reach the NEXT surviving
            # bone's original head position - this is what closes the
            # gap left by whatever got deleted in between.
            eb.tail = kept_original_heads[i + 1]
        # else: this is the tip - its own tail was already correct,
        # nothing follows it, leave it as-is.

        if i > 0:
            # Re-parent to the PREVIOUS surviving bone (not whatever
            # its original parent was, which may have just been
            # deleted). use_connect=True locks this bone's head to
            # match its new parent's tail automatically - which is
            # exactly the position we just set above, so this is
            # consistent rather than fighting itself.
            eb.parent = kept_edit_bones[i - 1]
            eb.use_connect = True
        # else: this is the root - its own parent (outside this chain,
        # e.g. a hip/spine bone) is left untouched.

    new_names = {}  # old_name -> new_name, needed below for vertex groups
    for name in rename_targets:
        eb = edit_bones.get(name)
        if eb is not None:
            new_name = f"Opt_{name}"
            eb.name = new_name
            new_names[name] = new_name

    bpy.ops.object.mode_set(mode=previous_mode if previous_mode != 'EDIT' else 'OBJECT')

    # --- Step 2: mirror the same changes onto every associated mesh ---
    affected_meshes = []
    for mesh_object in weights.find_associated_meshes(armature_object):
        vertex_groups = mesh_object.vertex_groups
        touched = False

        for name in deleted_names:
            vg = vertex_groups.get(name)
            if vg is not None:
                vertex_groups.remove(vg)
                touched = True

        for old_name, new_name in new_names.items():
            vg = vertex_groups.get(old_name)
            if vg is not None:
                vg.name = new_name
                touched = True

        if touched:
            affected_meshes.append(mesh_object.name)

    return {
        "deleted_bones": deleted_names,
        "renamed_bones": new_names,
        "affected_meshes": affected_meshes,
    }
