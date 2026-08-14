##description, title and items

bl_info = {
    "name": "Bome Optimizer",
    "author": "UsagiEnjoyer",
    "version": (0, 1),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > Bone Opti",
    "description": "Shorten bone groups (e.g. hair, tails, chains, etc) within armatures, preserving root name for external compatibility",
    "category": "Rigging",
}






import bpy
from . import properties
from . import operators


# 1. DEFINE YOUR OPERATOR (The Logic)
class BoneOpti_operator(bpy.types.Operator):
    """Tooltip text that appears when hovering over the button"""
    bl_idname = "generic.my_operator"
    bl_label = "Run Bone Optimization"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Place your actual functional code here
        self.report({'INFO'}, "The generic operator ran successfully!")
        return {'FINISHED'}


# 2. DEFINE YOUR UI PANEL (The Visuals)
class BoneOptipanel(bpy.types.Panel):
    bl_label = "Bone Optimize Tool"
    bl_idname = "Bone Optimizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bone Optimizer"  # This names the tab in the N-Panel sidebar

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Armature Chain Optimizer", icon='ARMATURE_DATA')
        layout.separator()

        layout.label(text="Select your Armature:")
        layout.prop(scene, "chain_opt_armature", text="")

        layout.separator()
        layout.label(text="Select Root:")
        layout.prop(scene, "chain_opt_root_bone", text="")

        layout.separator()
        layout.label(text="Bone Length:")
        layout.prop(scene, "chain_opt_segments", text="")

        layout.separator()
        layout.operator("chainopt.compress")


classes = (
    operators.CHAINOPT_OT_compress,
    CHAINOPT_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

# Allows running the script directly from Blender's Text Editor for testing
if __name__ == "__main__":
    register()