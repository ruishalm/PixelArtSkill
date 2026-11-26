"""Zero-dependency modular generator for Vale Felino 3D (examples/terrain-world.html).

Generates:
1. assets/voxels/voxel-data.js — Base-36 / RLE voxel packs on window.__VOXEL_PACKS__
2. examples/terrain-world.css — Viewport & HUD stylesheet copied from src/terrain-world/terrain-world.css
3. examples/terrain-world.html — Lightweight HTML shell referencing terrain-world.css and <script src="..."> modules
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from generate_studio import build_voxel_data_js, rle_compress_props  # noqa: E402, F401

ENGINE_DIR = os.path.join(ROOT, 'src', 'engine')
SRC_DIR = os.path.join(ROOT, 'src', 'terrain-world')
EXAMPLES_DIR = os.path.join(ROOT, 'examples')


def build_terrain_world(out_path=None):
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    voxel_js_path = build_voxel_data_js()

    css_src = os.path.join(SRC_DIR, 'terrain-world.css')
    css_out = os.path.join(EXAMPLES_DIR, 'terrain-world.css')
    with open(css_src, 'r', encoding='utf-8') as f:
        css_text = f.read()
    with open(css_out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(css_text)

    shell_path = os.path.join(SRC_DIR, 'shell.html')
    with open(shell_path, 'r', encoding='utf-8') as f:
        shell_html = f.read()

    engine_paths = sorted(glob.glob(os.path.join(ENGINE_DIR, '*.js'))) if os.path.isdir(ENGINE_DIR) else []
    module_paths = sorted(glob.glob(os.path.join(SRC_DIR, '*.js')))
    if not module_paths:
        raise RuntimeError(f'No JS modules found in {SRC_DIR}')

    all_scripts = [voxel_js_path] + engine_paths + module_paths
    script_tags = []
    for mod_path in all_scripts:
        rel_url = os.path.relpath(mod_path, EXAMPLES_DIR).replace('\\', '/')
        script_tags.append(f'  <script src="{rel_url}"></script>')
    scripts_block = '\n'.join(script_tags)

    html_out = shell_html.replace('__TERRAIN_SCRIPTS__', scripts_block)
    unresolved = re.findall(
        r'__(?:TERRAIN_SCRIPTS|TERRAIN_JS_BUNDLE|CAT_SLICES|HATS_PACK|CHICKEN_DATA|PROPS_PACK)__',
        html_out,
    )
    if unresolved:
        raise RuntimeError(f'Unresolved template placeholders: {unresolved}')

    if out_path is None:
        out_path = os.path.join(EXAMPLES_DIR, 'terrain-world.html')
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html_out)

    print(
        f'SUCCESS: Generated modular Terrain World ({len(engine_paths)} engine + {len(module_paths)} world) -> '
        f'{out_path} ({os.path.getsize(out_path) / 1024:.1f} KB), '
        f'{css_out} ({os.path.getsize(css_out) / 1024:.1f} KB), '
        f'{voxel_js_path} ({os.path.getsize(voxel_js_path) / 1024:.1f} KB)'
    )
    return out_path


if __name__ == '__main__':
    build_terrain_world()
