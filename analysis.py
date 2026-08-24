# import bpy
# no need for import bpy
def _walk_chain(root_bone):

    chain = [root_bone.name]
    current = root_bone

    while current.children:
        if len(current.children) > 1:
            # Branching chain (e.g. hand splitting into fingers).
            # Not supported yet by design — raise clearly rather than
            # silently guessing which branch is "the" chain.
            raise ValueError(
                f"Bone '{current.name}' has {len(current.children)} children — "
                "branching chains aren't supported yet"
            )
        current = current.children[0]
        chain.append(current.name)

    return chain


def get_bone_chain(armature_object, root_bone_name):
    
    # The bpy-facing entry point. Looks up the real bone by name on the
    # given armature, then hands off to _walk_chain for the actual work.
    
    root_bone = armature_object.data.bones.get(root_bone_name)
    if root_bone is None:
        raise ValueError(
            f"Bone '{root_bone_name}' not found in armature '{armature_object.name}'"
        )
    return _walk_chain(root_bone)