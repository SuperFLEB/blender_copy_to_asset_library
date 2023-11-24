import bpy

from ..lib import pkginfo

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class COPYTOASSETLIBRARY_PT_preferences(bpy.types.AddonPreferences):
    bl_idname = package_name
    create_symlinks: bpy.props.BoolProperty(
        name="Create symlinks instead of copying",
        description="Create symbolic links to the file instead of copying the file",
        default=False
    )
    allow_unsaved: bpy.props.BoolProperty(
        name="Snapshot unsaved files",
        description="If the file is modified and unsaved, save the current state of the file to the Asset Library. "
                    "If turned off, files must be saved before using the tool. Not applicable when Create Symlinks"
                    "is set.",
        default=True
    )
    always_compress: bpy.props.BoolProperty(
        name="Always save compressed",
        description="Save a compressed .blend file to the Asset Library. (Requires \"Snapshot Unsaved Files\" "
                    "because the \"Save a Copy\" feature is used to compress the file.)",
        default=True
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
    skip_preflight: bpy.props.BoolProperty(
        name="Skip preflight checks",
        description="Skip preflight checks such as making sure resources are packed.",
        default=False
    )

    save_copy_to_temp: bpy.props.BoolProperty(
        name="Save to a temporary file, then copy to the Asset Library (Dropbox bug fix)",
        description="Save the copy in a temporary directory first, then move it to the Asset Library. This works "
                    "around a bug in Dropbox where files are not properly saved in Dropbox-synced directories. "
                    "Not applicable when Create Symlinks is set.",
        default=True
    )
    relative_remap: bpy.props.BoolProperty(
        name="Remap relative paths",
        description="Sets the option to remap relative paths in the saved file.",
        default=True
    )

    def draw(self, context) -> None:
        layout = self.layout
        layout.prop(self, 'create_symlinks')
        au_layout = layout.column()
        au_layout.enabled = not self.create_symlinks
        au_layout.prop(self, 'allow_unsaved')
        ac_layout = layout.column()
        ac_layout.enabled = self.allow_unsaved and not self.create_symlinks
        ac_layout.prop(self, 'always_compress')
        layout.prop(self, 'normalize_numeric_suffix')
        layout.prop(self, 'create_backup')
        layout.prop(self, 'append_catalog')
        layout.prop(self, 'skip_preflight')

        advanced_layout = layout.box()
        advanced_layout.label(text="Advanced Options (you probably don't need to change these)")
        db_layout = advanced_layout.column()
        db_layout.enabled = self.allow_unsaved and not self.create_symlinks
        db_layout.prop(self, 'save_copy_to_temp')


REGISTER_CLASSES = [COPYTOASSETLIBRARY_PT_preferences]
