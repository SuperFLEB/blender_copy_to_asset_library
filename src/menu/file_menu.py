import bpy
from bpy.types import Menu
from ..operator import copy_to_asset_library
from ..lib import addon

if "_LOADED" in locals():
    import importlib

    for mod in (copy_to_asset_library,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class DestinationMenu(Menu):
    bl_idname = 'copy_to_asset_library_MT_destination_menu'
    bl_label = 'Copy to Asset Library...'

    def draw(self, context):
        layout = self.layout
        libraries = context.preferences.filepaths.asset_libraries
        if bpy.data.is_dirty or not bpy.data.is_saved:
            layout.alert = True
            layout.label(text="File must be saved before copying", icon='ERROR')

        for lib in libraries:
            oper = layout.operator(copy_to_asset_library.CopyToAssetLibrary.bl_idname, text=lib.name)
            oper.path = lib.path

REGISTER_CLASSES = [DestinationMenu]
