from typing import Callable
import bpy
from .lib import addon
from .operator import copy as copy_to_asset_library
from .panel import preferences as preferences_panel
from .menu import file_menu

if "_LOADED" in locals():
    import importlib

    for mod in (addon, copy_to_asset_library, preferences_panel, file_menu):
        importlib.reload(mod)
_LOADED = True

package_name = __package__

bl_info = {
    "name": "Copy to Asset Library",
    "description": "Copy or symlink the open file into an Asset Library directory",
    "author": "FLEB",
    "version": (0, 1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Object",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "https://github.com/SuperFLEB/blender_copy_to_asset_library",
    "tracker_url": "https://github.com/SuperFLEB/blender_copy_to_asset_library/issues",
    "support": "COMMUNITY",
    "category": "System",
}


menus: list[tuple[str, Callable]] = [
    ("TOPBAR_MT_file", addon.menuitem(file_menu.COPYTOASSETLIBRARY_MT_destinations))
]

# Registerable modules have a REGISTER_CLASSES list that lists all registerable classes in the module
registerable_modules = [
    file_menu,
    copy_to_asset_library,
    preferences_panel,
]


def register() -> None:
    for c in addon.get_registerable_classes(registerable_modules):
        # Attempt to clean up if the addon broke during registration.
        try:
            bpy.utils.unregister_class(c)
        except RuntimeError:
            pass
        bpy.utils.register_class(c)
        if hasattr(c, 'post_register') and callable(c.post_register):
            c.post_register()
        print("Copy to Asset Library registered class:", c)
    addon.register_menus(menus)


def unregister() -> None:
    addon.unregister_menus(menus)
    for m in menus[::-1]:
        getattr(bpy.types, m[0]).remove(m[1])
    for c in addon.get_registerable_classes(registerable_modules)[::-1]:
        try:
            bpy.utils.unregister_class(c)
            if hasattr(c, 'post_unregister') and callable(c.post_unregister):
                c.post_unregister()
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
