"""Zero-dependency bundler for Vale Felino 3D (examples/terrain-world.html).

Reads the HTML shell and modular JS files from src/terrain-world/, injects the
embedded Base-36 / RLE voxel packs from assets/voxels/, and emits a single
100% self-contained HTML5 Canvas 2D file with zero runtime dependencies.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOXELS_DIR = os.path.join(ROOT, 'assets', 'voxels')
SRC_DIR = os.path.join(ROOT, 'src', 'terrain-world')
EXAMPLES_DIR = os.path.join(ROOT, 'examples')
_RLE_RE = re.compile(r'(.)\1{2,}')


def rle_compress_props(pack):
    compressed = {}
    for key, entry in pack.items():
        compressed[key] = {
            'palette': entry['palette'],
            'slices': [
                [_RLE_RE.sub(lambda m: f'*{m.group(1)}{len(m.group(0))};', row) for row in sl]
                for sl in entry['slices']
            ],
        }
    return compressed


def build_terrain_world(out_path=None):
    with open(os.path.join(VOXELS_DIR, 'slices_v5.json'), 'r', encoding='utf-8') as f:
        cat_slices = json.load(f)
    with open(os.path.join(VOXELS_DIR, 'hats_pack.json'), 'r', encoding='utf-8') as f:
        hats_pack = json.load(f)
    with open(os.path.join(VOXELS_DIR, 'chicken_slices.json'), 'r', encoding='utf-8') as f:
        chicken_data = json.load(f)
    with open(os.path.join(VOXELS_DIR, 'terrain_props_pack.json'), 'r', encoding='utf-8') as f:
        props_pack = json.load(f)

    shell_path = os.path.join(SRC_DIR, 'shell.html')
    with open(shell_path, 'r', encoding='utf-8') as f:
        shell_html = f.read()

    module_paths = sorted(glob.glob(os.path.join(SRC_DIR, '*.js')))
    if not module_paths:
        raise RuntimeError(f'No JS modules found in {SRC_DIR}')

    js_parts = []
    for mod_path in module_paths:
        with open(mod_path, 'r', encoding='utf-8') as f:
            js_parts.append(f.read())
    js_bundle = ''.join(js_parts)

    html_out = shell_html.replace('__TERRAIN_JS_BUNDLE__', js_bundle)
    html_out = (
        html_out
        .replace('__CAT_SLICES__', json.dumps(cat_slices, separators=(',', ':')))
        .replace('__HATS_PACK__', json.dumps(hats_pack, separators=(',', ':')))
        .replace('__CHICKEN_DATA__', json.dumps(chicken_data, separators=(',', ':')))
        .replace('__PROPS_PACK__', json.dumps(rle_compress_props(props_pack), separators=(',', ':')))
    )

    unresolved = re.findall(r'__(?:TERRAIN_JS_BUNDLE|CAT_SLICES|HATS_PACK|CHICKEN_DATA|PROPS_PACK)__', html_out)
    if unresolved:
        raise RuntimeError(f'Unresolved template placeholders: {unresolved}')

    if out_path is None:
        out_path = os.path.join(EXAMPLES_DIR, 'terrain-world.html')
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html_out)

    print(
        f'SUCCESS: Bundled {len(module_paths)} modules -> {out_path} '
        f'({os.path.getsize(out_path) / 1024:.1f} KB)'
    )
    return out_path


if __name__ == '__main__':
    build_terrain_world()
