import bpy
import os
import re
import shutil
from typing import Set
from bpy.types import Operator
from bpy.props import StringProperty
from ..lib import pkginfo
from ..lib import cats

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo, cats,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class CopyToAssetLibrary(Operator):
    """Copy or symlink the open file into an Asset Library directory"""
    bl_idname = "copy_to_asset_library.copy"
    bl_label = "Copy to Asset Library"
    bl_options = {'REGISTER'}

    path: StringProperty(name="path", description="Path")

    @classmethod
    def poll(cls, context) -> bool:
        if bpy.data.is_dirty or not bpy.data.is_saved:
            cls.poll_message_set('File must be saved before copying')
            return False
        return True

    def execute(self, context) -> Set[str]:
        prefs = context.preferences.addons[package_name].preferences
        self_path = bpy.data.filepath
        filename = bpy.path.basename(self_path)
        new_filename = filename

        if prefs.normalize_numeric_suffix:
            new_filename = re.sub(r'[_ ]?\d+(\.[^\.]+)$', '_latest\\1', new_filename)

        if not self.path:
            self.report({'ERROR'}, 'Internal error: Path not provided to operator')
            return {'FAILED'}

        if not (filename and new_filename):
            self.report({'ERROR'}, 'Internal error: File name could not be determined')
            return {'FAILED'}

        destination = os.path.join(self.path, new_filename)
        backup_file = f"{destination}1"

        if prefs.create_backup and os.path.isfile(destination):
            if os.path.isfile(backup_file):
                print(f"Removing backup file {backup_file} to make room for the new one")
                os.remove(backup_file)
            print(f"Moving existing {destination} to {backup_file}")
            os.rename(destination, backup_file)
            made_backup = True

        if prefs.create_symlinks:
            print(f"Creating symlink from {self_path} -> {destination}")
            os.symlink(self_path, destination)
        else:
            print(f"Copying file {self_path} to {destination}")
            shutil.copy2(self_path, destination)

        warning = None
        if prefs.append_catalog:
            try:
                cats.append_catalogs_from_current_file(self.path)
            except cats.CatalogVersionException as e:
                print("Catalog version exception", e)
                warning = "Catalog version was invalid or too new. Copied asset but did not update the catalog file."

        if warning:
            self.report({'WARNING'}, warning)
        else:
            self.report({'INFO'}, f"{'Symlinked' if prefs.create_symlinks else 'Copied'} {new_filename}")
        return {'FINISHED'}


REGISTER_CLASSES = [CopyToAssetLibrary]
