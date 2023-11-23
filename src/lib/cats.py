import os.path
import bpy
import re
import shutil

# If version 2 or whatever comes around and it's compatible, just bump this number to make the script work
MAX_CATSFILE_VERSION = 1


class CatalogVersionException(BaseException):
    pass


def _text_to_catalogs_by_uuid(cats_text: str) -> dict[str, str]:
    lines = cats_text.split('\n')
    uuids = {}
    for line in lines:
        match = re.search('([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}):.+', line)
        if not match:
            continue
        uuid = match.group(1)
        uuids[uuid] = line
    return uuids


def _get_text_from_textblock() -> str | None:
    return bpy.data.texts[
        'blender_assets.cats.txt'].as_string() if 'blender_assets.cats.txt' in bpy.data.texts else None


def _get_text_from_file() -> str | None:
    source_path = bpy.path.abspath('//blender_assets.cats.txt')
    if not os.path.isfile(source_path):
        return None
    fh = open(source_path, 'r')
    contents = fh.read()
    fh.close()
    return contents


def _copy_cats_file(dest_file: str) -> None:
    # Use the textblock if one exists
    if contents := _get_text_from_textblock():
        fh = open(dest_file, 'x')
        fh.write(contents)
        fh.close()
        return

    # Copy the file if one exists
    source_path = bpy.path.abspath('//blender_assets.cats.txt')
    if os.path.isfile(source_path):
        shutil.copy(source_path, dest_file)
        return

    # No source existed. Nothing done.
    return


def append_catalogs_from_current_file(dest_path: str) -> None:
    """Attempt to export any blender_assets.cats.txt lines from either a textblock (preferred) or a file, to the
    given destination. Appends the file's data onto any existing data if it exists. If no blender_assets.cats.txt
    data exists with the current file (no Textblock or file), nothing is done and the operation returns."""

    dest_file = os.path.join(dest_path, 'blender_assets.cats.txt')

    # If no file exists at the destination, just copy the one we have
    if not os.path.isfile(dest_file):
        print(f"No catalog file existed at {dest_file}, so creating/copying a new one.")
        _copy_cats_file(dest_file)
        return

    dest_fh = open(dest_file, 'r')
    dest_cats_text = dest_fh.read()
    dest_fh.close()

    source_cats_text = _get_text_from_textblock() or _get_text_from_file()
    if not source_cats_text:
        print(f"No existing catalog data. Nothing to export.")
        return

    version_lines = [line for line in dest_cats_text.split('\n') if re.match('^VERSION \d+$', line)]
    if not version_lines:
        raise CatalogVersionException(f"Cannot find VERSION in {dest_file}. It may be a newer version, or invalid.")

    version = int(version_lines[0][8:])

    print(f"Catalog file is version {version}, max supported is version {MAX_CATSFILE_VERSION}")

    if version > MAX_CATSFILE_VERSION:
        raise CatalogVersionException(
            f"VERSION in blender_assets.cats.txt file is version {version} and may not be compatible with version "
            f"{MAX_CATSFILE_VERSION}. Change MAX_CATSFILE_VERSION in the script if you want to try it.")

    source_cats_data = _text_to_catalogs_by_uuid(source_cats_text)
    dest_cats_data = _text_to_catalogs_by_uuid(dest_cats_text)

    new_cats = {uuid: spec for (uuid, spec) in source_cats_data.items() if uuid not in dest_cats_data}
    new_lines = [line for line in new_cats.values()]

    if not new_lines:
        print(f"All new catalogs already existed in {dest_file}")
        return

    # Make a backup
    shutil.copyfile(dest_file, f"{dest_file}.backup")
    print(f"Backed up {dest_file} -> {dest_file}.backup")

    # Write the new lines
    fh = open(dest_file, 'a')
    fh.write('\n'.join(new_lines))
    fh.close()

    print(f"Added {len(new_lines)} catalog(s) to {dest_file}")
