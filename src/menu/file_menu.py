import bpy
from bpy.types import Menu
from ..operator import copy as copy_to_asset_library
from ..lib import pkginfo

if "_LOADED" in locals():
    import importlib

    for mod in (copy_to_asset_library, pkginfo,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()

class COPYTOASSETLIBRARY_MT_destinations(Menu):
    bl_idname = 'COPYTOASSETLIBRARY_MT_destinations'
    bl_label = 'Copy to Asset Library...'

    def draw(self, context):
        layout = self.layout
        libraries = context.preferences.filepaths.asset_libraries
        prefs = context.preferences.addons[package_name].preferences
        unsaved = bpy.data.is_dirty or not bpy.data.is_saved

        if unsaved and (prefs.create_symlinks or not prefs.allow_unsaved):
            layout.alert = True
            layout.label(text="File must be saved", icon='ERROR')

        for lib in libraries:
            oper = layout.operator(copy_to_asset_library.COPYTOASSETLIBRARY_OT_copy.bl_idname, text=lib.name)
            oper.path = lib.path

REGISTER_CLASSES = [COPYTOASSETLIBRARY_MT_destinations]
