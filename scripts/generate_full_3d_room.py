"""Deprecated legacy entry point redirected to scripts/generate_mega_room.py.

Historically this script emitted a monolithic single-file prototype to
examples/room-3d.html. The Room 3D diorama is now modularized under
src/examples/room-3d/ and built via scripts/generate_mega_room.py.
"""

import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from generate_mega_room import build_mega_room  # noqa: E402


def main():
    print(
        '[DEPRECATED] scripts/generate_full_3d_room.py now redirects to '
        'scripts/generate_mega_room.py to preserve the modular architecture.'
    )
    return build_mega_room()


if __name__ == '__main__':
    main()
