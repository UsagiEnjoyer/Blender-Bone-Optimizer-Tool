import bpy


def on_armature_changed(self, context):
    # this runs automatically the instant chain_opt_armature
    # changes (that's what `update=` does — Blender calls this function
    # for you, no manual triggering needed).
    #
    # Task: reset context.scene.chain_opt_root_bone back to empty here,
    # so a leftover bone name from the PREVIOUS armature can't linger
    # and silently point at a bone that doesn't exist on the new one.
    #
    # Hint: this is a one-line function body.




    pass






def register():
    bpy.types.Scene.chain_opt_armature = bpy.props.PointerProperty(
        name="Armature",
        type=bpy.types.Object,
        description="The armature containing the bone chain to optimize",
        update=on_armature_changed,
    )

    # StringProperty instead of EnumProperty now — the search box
    # (prop_search, wired up in the Panel) filters bone names as you
    # type, rather than needing a fixed dropdown list.
    bpy.types.Scene.chain_opt_root_bone = bpy.props.StringProperty(
        name="Root Bone",
        description="The bone where the chain to optimize begins",
    )

    bpy.types.Scene.chain_opt_segments = bpy.props.IntProperty(
        name="Bone Length",
        description="Number of segments the optimized chain should have",
        default=4,
        min=1,
    )


def unregister():
    del bpy.types.Scene.chain_opt_armature
    del bpy.types.Scene.chain_opt_root_bone
    del bpy.types.Scene.chain_opt_segments
