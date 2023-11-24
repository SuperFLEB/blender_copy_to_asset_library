# Copy to Asset Library

https://github.com/SuperFLEB/blender_copy_to_asset_library

Adds a menu to the File menu allowing you to copy or symlink the currently-open file to an Asset Library directory. This
is for people who don't want to go through the hassle of moving files around every time they update an asset, or want to
verify that an asset they're making works as expected.

## Features

* The option to save or to symlink the file into the Asset Library directory.
* Removes numeric suffixes and replaces them with "_latest", so `file_101.blend` becomes `file_latest.blend` and
  `file101.blend` becomes `file_latest.blend`. This means you can work in the iterative, "Save Incremental" style,
  but not have to file-manage your Asset Library and clean out old iterations.
* Optionally save compressed, or just do like in the file.
* If there's a `blender_assets.cats.txt` in a Textblock in your .blend file, or alongside your .blend file in the
  filesystem, it'll add any missing Catalogs into the asset library you copy it to.
* The option to back up prior existing files or just live dangerously.
* A preflight feature checks out some common gotchas before proceeding.

All these features are optional and can be set in the addon's Preferences panel. 

## To install

Either install the ZIP file from the release or clone this repository and use the
build_release.py script to build a ZIP file that you can install into Blender.

## To use

Before using this for the first time, you might want to check out the settings in the Add-on Preferences Panel.

After that, just go to the File menu (on the top bar), to the "Copy to Asset Library..." menu, and select
an Asset Library to copy to.

## Caveats

* This uses the Blender Save As Copy feature to "copy" files, even if they haven't been modified since opening. This
  will cause the file to be saved in the version of Blender you are using, with any extra data that might be added by
  that particular installation. (This is done so features like compression can be done.) This probably won't be any
  issue for most practical workflows (since you'll probably be working on the file in the copy of Blender you're
  using this with anyway), but if this tweaks your edge case, be aware of it.
