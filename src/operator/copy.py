import bpy
import os
import re
import shutil
import tempfile
from typing import Set
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ..lib import pkginfo
from ..lib import cats
from ..lib import blendfile

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo, cats,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class COPYTOASSETLIBRARY_OT_copy(Operator):
    """Copy or symlink the open file into an Asset Library directory"""
    bl_idname = "copy_to_asset_library.copy"
    bl_label = "Copy to Asset Library"
    bl_options = {'REGISTER'}

    path: StringProperty(name="path", description="Path")
    skip_preflight: BoolProperty(name="skip_preflight", description="Skip Preflight Checks (confirmed)")

    @classmethod
    def _can_save(cls, prefs) -> bool:
        clean = bpy.data.is_saved and not bpy.data.is_dirty
        return bpy.data.filepath and (clean or (prefs.allow_unsaved and not prefs.create_symlinks))

    @classmethod
    def poll(cls, context) -> bool:
        prefs = context.preferences.addons[package_name].preferences
        if cls._can_save(prefs):
            return True
        cls.poll_message_set('File must be saved before copying')
        return False

    @classmethod
    def _has_assets(cls) -> bool:
        for key in [d[0] for d in bpy.data.bl_rna.properties.items() if isinstance(d[1], bpy.types.CollectionProperty)]:
            for item in getattr(bpy.data, key):
                try:
                    if item.asset_data is not None:
                        return True
                except:
                    pass
        return False

    def _preflight(self, _context) -> list[str]:
        unpacks = [f"Image \"{img.name}\" is not packed" for img in bpy.data.images if
                   img.packed_file is None and img.name != 'Render Result']
        links = [f"{len(lib.users_id)} items are linked from library \"{lib.name}\"" for lib in bpy.data.libraries if
                 len(lib.users_id) > 0]
        if len(unpacks) > 10:
            unpacks = [f"{len(unpacks)} images were not packed"]
        if len(links) > 10:
            unpacks = [f"Linked items from {len(links)} linked libraries were found"]

        no_assets = ["This file contains nothing marked as an Asset"] if not self._has_assets() else []

        return no_assets + unpacks + links

    def _preflight_fail(self, preflight_errors: list[str]):
        def confirm_menu(menu, _) -> None:
            layout = menu.layout.column()

            button_layout = layout.column()
            continue_oper = button_layout.operator(self.bl_idname, text=f"Copy to Asset Library anyway...")
            continue_oper.path = self.path
            continue_oper.skip_preflight = True

            layout.separator()

            err_layout = layout.column()
            for err in preflight_errors:
                err_layout.label(text=f" \u25BA {err}")

        bpy.context.window_manager.popup_menu(confirm_menu, title="There were some problems with this file:",
                                              icon="ERROR")

    def _symlink(self, source, destination):
        print(f"Creating symlink from {source} -> {destination}")
        os.symlink(source, destination)

    def _save_copy(self, destination, prefs):
        compress = prefs.always_compress or blendfile.is_compressed()
        print("Using compression" if compress else "Not using compression")
        if not prefs.save_copy_to_temp:
            print(f"Saving {destination} from current state")
            bpy.ops.wm.save_as_mainfile(filepath=destination, copy=True, compress=compress)
            return

        with tempfile.TemporaryDirectory() as td:
            temp_path = os.path.join(td, 'asset_export_temp.blend')
            print(f"Saving temporary file {temp_path} from current state")
            bpy.ops.wm.save_as_mainfile(filepath=temp_path, copy=True, compress=compress)
            print(f"Copying {temp_path} to {destination}")
            shutil.copy2(temp_path, destination)

    def execute(self, context) -> Set[str]:
        prefs = context.preferences.addons[package_name].preferences
        self_path = bpy.data.filepath
        filename = bpy.path.basename(self_path)
        new_filename = re.sub(r'[_ ]?\d+(\.[^\.]+)$', '_latest\\1',
                              filename) if prefs.normalize_numeric_suffix else filename

        if not self.path:
            self.report({'ERROR'}, 'Internal error: Path not provided to operator')
            return {'CANCELLED'}

        if not (filename and new_filename):
            self.report({'ERROR'}, 'Internal error: File name could not be determined')
            return {'CANCELLED'}

        if not self._can_save(prefs):
            self.report({'ERROR'}, 'File must be saved first')

        if not self.skip_preflight and not prefs.skip_preflight and (preflight_errors := self._preflight(context)):
            print("Preflight failed, so showing a dialog to confirm the copy")
            self._preflight_fail(preflight_errors)
            return {'CANCELLED'}

        destination = os.path.join(self.path, new_filename)
        backup_file = f"{destination}1"

        if prefs.create_backup and os.path.isfile(destination):
            if os.path.isfile(backup_file):
                print(f"Removing backup file {backup_file} to make room for the new one")
                os.remove(backup_file)
            print(f"Moving existing {destination} to {backup_file}")
            os.rename(destination, backup_file)

        if prefs.create_symlinks:
            self._symlink(self_path, destination)
        else:
            self._save_copy(destination, prefs)

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


REGISTER_CLASSES = [COPYTOASSETLIBRARY_OT_copy]
