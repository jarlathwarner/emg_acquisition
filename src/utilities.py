import struct

def pack(fmt, *args):
    """
    Convert non-byte values (e.g., integers, strings, etc.) and convert them to bytes.

    Available format characters: https://docs.python.org/3/library/struct.html

    :param fmt: String format to pack the values to
    :param args: values to pack
    :return: packed bytes object
    """
    # < means little endian
    return struct.pack('<' + fmt, *args)
