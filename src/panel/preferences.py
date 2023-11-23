import bpy

from ..lib import pkginfo

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()

class ThePreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = package_name
    create_symlinks: bpy.props.BoolProperty(
        name="Create symlinks instead of copying",
        description="Create symbolic links to the file instead of copying the file",
        default=False
    )
    normalize_numeric_suffix: bpy.props.BoolProperty(
        name="Replace numeric suffixes with \"_latest\"",
        description="Replace numeric suffixes with \"latest\" (e.g., MyFile01.blend -> MyFile_latest.blend)",
        default=True
    )
    create_backup: bpy.props.BoolProperty(
        name="Move existing files to a .blend1 backup file",
        description="If the file already exists, move it to a \".blend1\" file",
        default=True
    )
    append_catalog: bpy.props.BoolProperty(
        name="Append catalogs (blender_assets.cats.txt) from Textblock or file to the library",
        description='Append catalogs from the file or directory to the destination library. If a '
                    '"blender_assets.cats.txt" Textblock exists in the file, it will be used. Otherwise, '
                    'if a "blender_assets.cats.txt" file exists in the source file\'s directory, it will be used.',
        default=False
    )

    def draw(self, context) -> None:
        layout = self.layout
        layout.prop(self, 'create_symlinks')
        layout.prop(self, 'normalize_numeric_suffix')
        layout.prop(self, 'create_backup')
        layout.prop(self, 'append_catalog')

REGISTER_CLASSES = [ThePreferencesPanel]
