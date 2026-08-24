##description, title and items

bl_info = {
    "name": "Armature Bone Optimizer",
    "author": UsagiEnjoyer,
    "version": (0, 1),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > Chain Optimizer",
    "description": "Shorten and compress any bone chain (e.g. hair) while preserving root name.
    "category": "Rigging",
}

import bpy
from . import properties
from . import operators
from . import analysis


# The Panel stays here in __init__.py, incase for quick changes
# (as of Blender 5.0, panel wasn't its own file — it lived alongside bl_info/register)
class BONEOPT_PT_panel(bpy.types.Panel):
    bl_label = "Bone Optimizer"
    bl_idname = "BoneOPT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bone Optimizer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        armature = scene.chain_opt_armature
        root_bone = scene.chain_opt_root_bone
        segments = scene.chain_opt_segments

        layout.label(text="Armature Bone Optimizer", icon='ARMATURE_DATA')
        layout.separator()

        layout.label(text="Select your Armature:")
        layout.prop(scene, "chain_opt_armature", text="")

        layout.separator()
        layout.label(text="Select Root:")
        row = layout.row(align=True)
        row.prop(scene, "chain_opt_root_bone", text="")
        row.operator("chainopt.pick_root", text="", icon='EYEDROPPER')

        layout.separator()
        layout.label(text="Bone Length:")
        layout.prop(scene, "chain_opt_segments", text="")

        # Live preview: recomputes on every redraw, so it updates the
        # instant you change any field - no button needed to "see" it.
        if armature is not None and root_bone and root_bone != 'NONE':
            box = layout.box()
            try:
                chain = analysis.get_bone_chain(armature, root_bone)
                chain_length = len(chain)
                max_segments = chain_length - 1

                if segments > max_segments:
                    box.label(
                        text=f"Chain has {chain_length} bones — max is {max_segments}",
                        icon='ERROR',
                    )
                else:
                    result_count = segments + 1
                    box.label(
                        text=f"Chain: {chain_length} bones → {result_count} bones",
                        icon='INFO',
                    )
            except ValueError as e:
                box.label(text=str(e), icon='ERROR')

        layout.separator()
        layout.operator("chainopt.compress")


classes = (
    operators.BONEOPT_OT_pick_root,
    operators.BONEOPT_OT_compress,
    BONEOPT_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    properties.register()


def unregister():
    properties.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
