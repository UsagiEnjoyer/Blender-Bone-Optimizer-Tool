import bpy




def build_reassignment_map(chain, kept_names):
    kept_indices = [chain.index(name) for name in kept_names]
    reassignment_map = {}

    for i, bone_name in enumerate(chain):
        if bone_name in kept_names:
            continue  # survives on its own, nothing to reassign

        nearest_kept_index = min(kept_indices, key=lambda k: abs(k - i))
        reassignment_map[bone_name] = chain[nearest_kept_index]

    return reassignment_map


def find_associated_meshes(armature_object):
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for modifier in obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object == armature_object:
                meshes.append(obj)
                break
    return meshes


def apply_weight_reassignment(armature_object, chain, kept_names):
    
    # Auto-detects every mesh deformed by armature_object, and applies the
    # same weight reassignment map to each one that actually has vertex
    # groups matching bones in this chain — meshes unrelated to this chain
    # (e.g. a body mesh sharing the same armature) are skipped automatically.

    # If the chain's hair is split across multiple mesh objects, all of
    # them are updated together as a single combined operation.

    # Returns (reassignment_map, list of affected mesh names) so the
    # caller can report what happened.
    
    reassignment_map = build_reassignment_map(chain, kept_names)
    chain_names = set(chain)
    affected_mesh_names = []

    for mesh_object in find_associated_meshes(armature_object):
        group_names = {vg.name for vg in mesh_object.vertex_groups}
        if not group_names & chain_names:
            continue  # this mesh has nothing to do with this hiearchy of bones

        vertex_groups = mesh_object.vertex_groups
        for deleted_name, target_name in reassignment_map.items():
            deleted_group = vertex_groups.get(deleted_name)
            target_group = vertex_groups.get(target_name)

            if deleted_group is None or target_group is None:
                continue

            for vertex in mesh_object.data.vertices:
                weight = None
                for g in vertex.groups:
                    if g.group == deleted_group.index:
                        weight = g.weight
                        break

                if weight is not None and weight > 0:
                    target_group.add([vertex.index], weight, 'ADD')

        affected_mesh_names.append(mesh_object.name)

    return reassignment_map, affected_mesh_names
