import bpy

# 1. DEFINE YOUR OPERATOR (The Logic)
class MESH_OT_generic_operator(bpy.types.Operator):
    """Tooltip text that appears when hovering over the button"""
    bl_idname = "generic.my_operator"
    bl_label = "Delete and Compress Bone Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Place your actual functional code here
        self.report({'INFO'}, "The generic operator ran successfully!")
        return {'FINISHED'}


# 2. DEFINE YOUR UI PANEL (The Visuals)
class VIEW3D_PT_generic_panel(bpy.types.Panel):
    bl_label = "My Custom Tool"
    bl_idname = "VIEW3D_PT_generic_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Addon Tab"  # This names the tab in the N-Panel sidebar

    def draw(self, context):
        layout = self.layout
        
        # Add the operator button to the panel
        row = layout.row()
        row.operator("generic.my_operator", text="Click Me", icon='PLAY')


# 3. REGISTRATION PIPELINE (The Setup)
classes = (
    MESH_OT_generic_operator,
    VIEW3D_PT_generic_panel,
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