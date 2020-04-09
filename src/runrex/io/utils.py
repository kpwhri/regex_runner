import sys
import contextlib
from typing import Optional


@contextlib.contextmanager
def open_all(filename: Optional[str] = None, mode: str = 'r', *args, **kwargs):
    """Open files and i/o streams transparently."""
    if filename is None or filename == '-':
        stream = sys.stdin if 'r' in mode else sys.stdout
        fh = stream.buffer if 'b' in mode else stream
        closeable = False
    else:
        fh = open(filename, mode, *args, **kwargs)
        closeable = True
    try:
        yield fh
    finally:
        if closeable:
            try:
                fh.close()
            except AttributeError:
                pass
