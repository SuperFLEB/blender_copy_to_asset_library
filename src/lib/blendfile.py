import bpy


def is_compressed(filepath: str = None):
    filepath = filepath if filepath else bpy.data.filepath
    # This may be a new, unsaved file
    if not filepath:
        return False
    with open(filepath, "rb") as fh:
        head = fh.read(4)
        return head[0:2] == b"\x1f\x8b" or head[0:4] == b"\x28\xb5\x2f\xfd"
