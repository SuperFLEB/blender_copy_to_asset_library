import bpy
from typing import Callable, Type
from types import ModuleType

from hashlib import md5

"""
This library contains helper functions useful in setup and management of Blender addons.
It is required by the __init__.py, so don't remove it unless you fix dependencies.
"""


def m(string):
    return md5(str(string).encode('utf-8')).hexdigest()


def menuitem(cls: bpy.types.Operator | bpy.types.Menu, operator_context: str = "EXEC_DEFAULT") -> Callable:
    if issubclass(cls, bpy.types.Operator):
        def operator_fn(self, context):
            self.layout.operator_context = operator_context
            if (not hasattr(cls, 'can_show')) or cls.can_show(context):
                self.layout.operator(cls.bl_idname)
        return operator_fn
    if issubclass(cls, bpy.types.Menu):
        def submenu_fn(self, context):
            self.layout.menu(cls.bl_idname)

        return submenu_fn
    raise Exception(f"Copy to Asset Library: Unknown menu type for menu {cls}. The developer screwed up.")


def get_registerable_classes(registerable_modules: list[ModuleType]) -> list[Type]:
    module_classes = [m.REGISTER_CLASSES for m in registerable_modules if hasattr(m, "REGISTER_CLASSES")]
    flat_classes = [c for mc in module_classes for c in mc]
    # Deduplicate and preserve order using the Python 3.7+ fact that dicts keep insertion order
    dedupe_classes = list(dict.fromkeys(flat_classes))
    return dedupe_classes


def register_menus(menus: list[tuple[str, Callable]]):
    for m in menus:
        getattr(bpy.types, m[0]).append(m[1])


def unregister_menus(menus: list[tuple[str, Callable]]):
    for m in menus[::-1]:
        getattr(bpy.types, m[0]).remove(m[1])
