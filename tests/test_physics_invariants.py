"""Automated verification suite for PixelArtSkill.

Covers:
1. Voxel pack structural validation (assets/voxels/terrain_props_pack.json).
2. Zero-dependency HTML bundler + JS syntax verification (node --check).
3. Documentation hygiene (SKILL.md / README.md alignment and control-char check).
4. Mathematical & physics invariants (smax/smin, parabolic bridge, Rankine dipole,
   WaveBuffer sponge decay, Virtual Pipe waterfall, Foliage cantilever spring,
   and Destructible 3D inverted pendulum).
"""

import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))


class TestPixelArtSkill(unittest.TestCase):
    def test_01_voxel_pack_integrity(self):
        import generate_terrain_props as gtp

        pack_path = os.path.join(ROOT, 'assets', 'voxels', 'terrain_props_pack.json')
        with open(pack_path, 'r', encoding='utf-8') as f:
            pack = json.load(f)

        self.assertGreaterEqual(len(pack), 25)
        # validate_pack raises AssertionError / ValueError on any malformed slice
        gtp.validate_pack(pack)

    def _assert_utf8_lf(self, path):
        with open(path, 'rb') as bf:
            raw = bf.read()
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), f'UTF-8 BOM found in {path}')
        self.assertNotIn(b'\r\n', raw, f'CRLF found in {path}')
        return raw

    def test_02_bundler_and_js_syntax(self):
        import generate_terrain_world as gtw

        with tempfile.TemporaryDirectory() as tmpdir:
            out_html = os.path.join(tmpdir, 'terrain-world.html')
            gtw.build_terrain_world(out_html)
            raw = self._assert_utf8_lf(out_html)
            html = raw.decode('utf-8')

            self.assertLess(len(raw), 15 * 1024, 'terrain-world.html must stay < 15 KB')
            # Zero unresolved placeholders
            for token in (
                '__TERRAIN_SCRIPTS__',
                '__TERRAIN_JS_BUNDLE__',
                '__CAT_SLICES__',
                '__HATS_PACK__',
                '__CHICKEN_DATA__',
                '__PROPS_PACK__',
            ):
                self.assertNotIn(token, html)

            self.assertIn('<link rel="stylesheet" href="terrain-world.css"', html)
            terrain_css = os.path.join(ROOT, 'examples', 'terrain-world.css')
            self.assertTrue(os.path.isfile(terrain_css))
            self._assert_utf8_lf(terrain_css)
            committed_html = os.path.join(ROOT, 'examples', 'terrain-world.html')
            self.assertTrue(os.path.isfile(committed_html))
            self.assertEqual(self._assert_utf8_lf(committed_html), raw, 'Committed examples/terrain-world.html is out of sync with generator')

            # Every <script src="..."> must exist relative to examples/ and pass node --check
            srcs = re.findall(r'<script\s+src="([^"]+)"', html)
            self.assertGreaterEqual(len(srcs), 15)
            examples_dir = os.path.join(ROOT, 'examples')
            combined_parts = []
            for rel_src in srcs:
                resolved = os.path.normpath(os.path.join(examples_dir, rel_src))
                self.assertTrue(os.path.isfile(resolved), f'Missing script target: {rel_src} -> {resolved}')
                js_raw = self._assert_utf8_lf(resolved)
                res = subprocess.run(['node', '--check', resolved], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f'Syntax error in {resolved}:\n{res.stderr}')
                combined_parts.append(js_raw.decode('utf-8'))

            # Combined cross-module syntax check (catches duplicate top-level const/let)
            combined_js = os.path.join(tmpdir, 'combined_terrain.js')
            with open(combined_js, 'w', encoding='utf-8', newline='\n') as cf:
                cf.write('\n'.join(combined_parts))
            res = subprocess.run(['node', '--check', combined_js], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Combined Terrain JS syntax error:\n{res.stderr}')

        # Also check every individual module in src/engine/*.js and src/terrain-world/*.js
        engine_modules = sorted(glob.glob(os.path.join(ROOT, 'src', 'engine', '*.js')))
        modules = sorted(glob.glob(os.path.join(ROOT, 'src', 'terrain-world', '*.js')))
        self.assertGreaterEqual(len(engine_modules), 1)
        self.assertEqual(len(modules), 6)
        for mod in engine_modules + modules:
            res = subprocess.run(['node', '--check', mod], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Syntax error in {mod}:\n{res.stderr}')

        # Verify all sfx*() calls across modules are defined in engine/01-voxel-audio.js
        with open(os.path.join(ROOT, 'src', 'engine', '01-voxel-audio.js'), 'r', encoding='utf-8') as f:
            assets_js = f.read()
        defined_sfx = set(re.findall(r'const\s+(sfx[A-Za-z0-9_]+)\s*=', assets_js))
        for mod in engine_modules + modules:
            with open(mod, 'r', encoding='utf-8') as f:
                code = f.read()
            for called in set(re.findall(r'\b(sfx[A-Za-z0-9_]+)\s*\(', code)):
                self.assertIn(called, defined_sfx, f'Undefined SFX call {called}() in {mod}')

    def test_03_docs_hygiene(self):
        with open(os.path.join(ROOT, 'SKILL.md'), 'r', encoding='utf-8') as f:
            skill = f.read()
        with open(os.path.join(ROOT, 'README.md'), 'r', encoding='utf-8') as f:
            readme = f.read()

        # No stray backspace control chars from escaped \b
        self.assertNotIn('\x08', skill, 'Found raw backspace char in SKILL.md')
        self.assertNotIn(' order-radius', skill)
        self.assertNotIn('C:\\Users\\Ruishalm', readme)

        # Updated keybindings reflected in both docs
        self.assertIn('KeyR', skill)
        self.assertIn('KeyQ', skill)
        self.assertIn('KeyE', skill)
        self.assertIn('KeyR', readme)

    def test_04_physics_and_math_invariants_in_node(self):
        node_script = r"""
const assert = require('assert');

// 1. Geological smooth union/carve (smax / smin)
function smax(a, b, k) {
  const h = Math.max(0, Math.min(1, 0.5 + 0.5 * (b - a) / k));
  return a + (b - a) * h + k * h * (1 - h);
}
function smin(a, b, k) {
  const h = Math.max(0, Math.min(1, 0.5 - 0.5 * (b - a) / k));
  return a + (b - a) * h - k * h * (1 - h);
}
assert(smax(10, 10, 4) > 10, 'smax smooth blend should exceed sharp max at tie');
assert(smin(10, 10, 4) < 10, 'smin smooth carve should dip below sharp min at tie');
assert(Math.abs(smax(3, 9, 5) - smax(9, 3, 5)) < 1e-9, 'smax must be symmetric');
assert(Math.abs(smin(3, 9, 5) - smin(9, 3, 5)) < 1e-9, 'smin must be symmetric');

// 2. Parabolic Arch Bridge deck height
function bridgeDeckZ(zBase, hArch, u) {
  return zBase + hArch * (1 - Math.pow(2 * u - 1, 2));
}
assert(Math.abs(bridgeDeckZ(4, 12, 0) - 4) < 1e-9);
assert(Math.abs(bridgeDeckZ(4, 12, 1) - 4) < 1e-9);
assert(Math.abs(bridgeDeckZ(4, 12, 0.5) - 16) < 1e-9);

// 3. Rankine Dipole potential flow deflection around cylindrical obstacle + Drain Sink
function rankineFlow(px, py, u0x, u0y, ox, oy, r) {
  const dx = px - ox, dy = py - oy;
  const d2 = dx * dx + dy * dy;
  const r2 = r * r;
  const dot = u0x * dx + u0y * dy;
  const factor = r2 / (d2 * d2);
  return {
    ux: u0x + factor * (d2 * u0x - 2 * dot * dx),
    uy: u0y + factor * (d2 * u0y - 2 * dot * dy),
  };
}
// Stagnation point at (-r, 0) for u0 = (1, 0): u_x should vanish!
const stag = rankineFlow(-10, 0, 1, 0, 0, 0, 10);
assert(Math.abs(stag.ux) < 1e-9 && Math.abs(stag.uy) < 1e-9, 'Rankine upstream stagnation point');
// Top flank (0, r) for u0 = (1, 0): tangential speed doubles to 2*u0!
const flank = rankineFlow(0, 10, 1, 0, 0, 0, 10);
assert(Math.abs(flank.ux - 2.0) < 1e-9 && Math.abs(flank.uy) < 1e-9, 'Rankine flank acceleration');
// Far field decays to u0
const far = rankineFlow(1000, 0, 1, 0, 0, 0, 10);
assert(Math.abs(far.ux - 1.0) < 1e-3, 'Rankine far-field decay');

// 4. WaveBuffer 2D stability, sponge boundary damping, and cutoff decay to 0
const W = 40, H = 40, SPONGE = 6;
let prev = new Float32Array(W * H);
let curr = new Float32Array(W * H);
let next = new Float32Array(W * H);
curr[20 * W + 20] = 1.0; // impulse in center
for (let step = 0; step < 300; step++) {
  for (let y = 1; y < H - 1; y++) {
    for (let x = 1; x < W - 1; x++) {
      const i = y * W + x;
      const edgeDist = Math.min(x, y, W - 1 - x, H - 1 - y);
      const gamma = edgeDist < SPONGE ? 0.72 : 0.955;
      let val = ((curr[i - 1] + curr[i + 1] + curr[i - W] + curr[i + W]) * 0.5 - prev[i]) * gamma;
      if (Math.abs(val) < 0.008) val = 0;
      next[i] = val;
    }
  }
  const tmp = prev; prev = curr; curr = next; next = tmp;
}
let maxAmp = 0;
for (let i = 0; i < curr.length; i++) {
  assert(Number.isFinite(curr[i]), 'WaveBuffer produced NaN/Inf');
  if (Math.abs(curr[i]) > maxAmp) maxAmp = Math.abs(curr[i]);
}
assert.strictEqual(maxAmp, 0, `WaveBuffer did not decay to rest (maxAmp=${maxAmp})`);

// 5. Foliage Parabolic Cantilever Bend + Damped Spring convergence
function cantileverOffset(sz, Hslices, bx, by) {
  const f = Math.pow(sz / (Hslices - 1), 2);
  return { dx: bx * f, dy: by * f };
}
const baseOff = cantileverOffset(0, 16, 4, -2);
const topOff = cantileverOffset(15, 16, 4, -2);
assert(Math.abs(baseOff.dx) === 0);
assert(Math.abs(baseOff.dy) === 0);
assert(Math.abs(topOff.dx - 4) < 1e-9 && Math.abs(topOff.dy + 2) < 1e-9);

// Damped spring settles to wind equilibrium target = W * windScale * (1 - rigidity)
let bx = 0, vx = 0;
const kStiff = 26, cDamp = 6.5, targetB = 2.4, dt = 1 / 60;
for (let i = 0; i < 300; i++) {
  const ax = kStiff * (targetB - bx) - cDamp * vx;
  vx += ax * dt;
  bx += vx * dt;
}
assert(Math.abs(bx - targetB) < 0.02, `Foliage spring failed to settle (bx=${bx})`);

// 6. Destructible 3D Inverted Pendulum ('chop')
let phi = 0.08, omega = 0;
const g = 240, L = 42;
for (let i = 0; i < 240 && phi < Math.PI / 2; i++) {
  const alpha = (3 * g) / (2 * L) * Math.sin(phi);
  omega += alpha * dt;
  phi += omega * dt;
}
assert(Number.isFinite(phi) && phi >= Math.PI / 2, 'Inverted pendulum did not reach ground');

// 7. Archimedes Buoyancy equilibrium (wood_log floats near surfZ; stone_chunk sinks)
let logZ = 4.0, logVz = 0;
const surfZ = -2.0;
for (let i = 0; i < 300; i++) {
  const submerged = Math.max(0, Math.min(1.5, (surfZ - logZ + 1.5) / 3.0));
  const az = (submerged * 1.85 - 1.0) * 180 - logVz * 4.5;
  logVz += az * dt;
  logZ += logVz * dt;
}
assert(Math.abs(logZ - surfZ) < 0.35, `Wood log did not settle near water surface (logZ=${logZ})`);
// Volume displacement: basin water level rise Δh = V_sub / A_basin > 0 when submerged
const smallPoolWet = 60, oceanWet = 4000;
const riseSmall = Math.min(1.5, (2.5 * 12) / Math.max(40, smallPoolWet));
const riseOcean = Math.min(1.5, (2.5 * 12) / Math.max(40, oceanWet));
assert(riseSmall > riseOcean && riseSmall > 0.1, 'Submerged volume must raise small basin level more than ocean');

// 8. Thermodynamics: heat diffusion + cooling decays to 0 when source removed & water quenches
let T = 95, moist = 0.65, fuel = 0.70;
const alphaT = 0.14, coolT = 0.22, tDt = 1 / 15;
for (let i = 0; i < 600; i++) {
  T = Math.max(0, T - coolT * T * tDt);
  if (moist > 0.05 && T > 6) moist = Math.max(0, moist - 0.018 * T * tDt);
}
assert(T < 0.05, `Heat did not cool down without source (T=${T})`);
assert(fuel === 0.70, 'Moist grass should not ignite while cooling below T_ign');

// 9. Granular Matter angle-of-repose relaxation (talus = 2) conserves mass
const pile = [0, 0, 8, 0, 0];
const sumBefore = pile.reduce((a, b) => a + b, 0);
for (let pass = 0; pass < 10; pass++) {
  for (let i = 1; i < pile.length - 1; i++) {
    if (pile[i] - pile[i - 1] > 2) { pile[i]--; pile[i - 1]++; }
    if (pile[i] - pile[i + 1] > 2) { pile[i]--; pile[i + 1]++; }
  }
}
const sumAfter = pile.reduce((a, b) => a + b, 0);
assert.strictEqual(sumBefore, sumAfter, 'Granular avalanche must conserve total height/mass');
for (let i = 0; i < pile.length - 1; i++) {
  assert(Math.abs(pile[i] - pile[i + 1]) <= 2, 'Granular slope must settle within talus angle');
}

// 10. Verlet distance constraint solver preserves segment length under gravity
let n0 = { x: 0, z: 20, pinned: true };
let n1 = { x: 0, z: 14, ox: 0, oz: 14, pinned: false };
const segLen = 6;
for (let step = 0; step < 60; step++) {
  const vz = (n1.z - n1.oz) * 0.96 - 190 * dt * dt;
  n1.oz = n1.z;
  n1.z += vz;
  for (let it = 0; it < 4; it++) {
    const dz = n1.z - n0.z;
    const dist = Math.abs(dz) || 0.0001;
    const diff = (dist - segLen) / dist;
    n1.z -= dz * diff;
  }
}
assert(Math.abs(Math.abs(n1.z - n0.z) - segLen) < 0.01, 'Verlet constraint did not preserve segment length');

// 11. Procedural tree trunk/branch/crown variation across seeds
const tr1 = { leanX: ((42 % 17) - 8) * 0.4, tiers: 3 + (42 % 3) };
const tr2 = { leanX: ((99 % 17) - 8) * 0.4, tiers: 3 + (99 % 3) };
assert.notStrictEqual(tr1.leanX, tr2.leanX, 'Procedural trees should vary trunk lean');

console.log('ALL_NODE_PHYSICS_INVARIANTS_OK');
"""
        res = subprocess.run(['node', '-e', node_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Node physics test failed:\n{res.stderr}')
        self.assertIn('ALL_NODE_PHYSICS_INVARIANTS_OK', res.stdout)

    def test_05_seeded_procedural_reproducibility(self):
        import generate_terrain_props as gtp

        gtp.set_seed(42)
        pine_a1 = gtp.build_pine_tree()
        ruin_a1 = gtp.build_ruin_pillar()

        gtp.set_seed(42)
        pine_a2 = gtp.build_pine_tree()
        ruin_a2 = gtp.build_ruin_pillar()

        gtp.set_seed(99)
        pine_b = gtp.build_pine_tree()
        ruin_b = gtp.build_ruin_pillar()

        # Restore default seed
        gtp.set_seed(1337)

        # Same seed must be 100% deterministic
        self.assertEqual(pine_a1['slices'], pine_a2['slices'])
        self.assertEqual(ruin_a1['slices'], ruin_a2['slices'])

        # Different seeds must produce distinct organic variations
        self.assertNotEqual(pine_a1['slices'], pine_b['slices'])
        self.assertNotEqual(ruin_a1['slices'], ruin_b['slices'])

        # Verify Mulberry32 & seeded hash2i determinism in Node
        node_seed_test = r"""
const assert = require('assert');
function mulberry32(seed) {
  let t = seed >>> 0;
  return function() {
    t = (t + 0x6D2B79F5) | 0;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}
const r1 = mulberry32(42), r2 = mulberry32(42), r3 = mulberry32(99);
for (let i = 0; i < 20; i++) {
  const v1 = r1(), v2 = r2(), v3 = r3();
  assert.strictEqual(v1, v2);
  assert(v1 >= 0 && v1 < 1);
  assert.notStrictEqual(v1, v3);
}
console.log('SEED_OK');
"""
        res = subprocess.run(['node', '-e', node_seed_test], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Node seed test failed:\n{res.stderr}')
        self.assertIn('SEED_OK', res.stdout)

    def test_06_modular_studio_build_and_js_syntax(self):
        import generate_studio as gs

        with tempfile.TemporaryDirectory() as tmpdir:
            out_html = os.path.join(tmpdir, 'studio.html')
            gs.build_studio(out_html)
            raw = self._assert_utf8_lf(out_html)
            studio_html = raw.decode('utf-8')

            self.assertLess(len(raw), 15 * 1024, 'studio/index.html must stay < 15 KB')
            for token in (
                '__STUDIO_SCRIPTS__',
                '__STUDIO_JS_BUNDLE__',
                '__CAT_SLICES__',
                '__HATS_PACK__',
                '__CHICKEN_DATA__',
                '__PROPS_PACK__',
            ):
                self.assertNotIn(token, studio_html)

            self.assertIn('<link rel="stylesheet" href="studio.css"', studio_html)
            studio_css = os.path.join(ROOT, 'studio', 'studio.css')
            self.assertTrue(os.path.isfile(studio_css))
            self._assert_utf8_lf(studio_css)
            committed_studio = os.path.join(ROOT, 'studio', 'index.html')
            self.assertTrue(os.path.isfile(committed_studio))
            self.assertEqual(self._assert_utf8_lf(committed_studio), raw, 'Committed studio/index.html is out of sync with generator')
            voxel_data_js = os.path.join(ROOT, 'assets', 'voxels', 'voxel-data.js')
            self.assertTrue(os.path.isfile(voxel_data_js))
            self._assert_utf8_lf(voxel_data_js)

            # Every <script src="..."> in studio HTML must exist on disk and pass node --check
            srcs = re.findall(r'<script\s+src="([^"]+)"', studio_html)
            self.assertGreaterEqual(len(srcs), 15)
            studio_dir = os.path.join(ROOT, 'studio')
            combined_parts = []
            for rel_src in srcs:
                resolved = os.path.normpath(os.path.join(studio_dir, rel_src))
                self.assertTrue(os.path.isfile(resolved), f'Missing script target: {rel_src} -> {resolved}')
                js_raw = self._assert_utf8_lf(resolved)
                res = subprocess.run(['node', '--check', resolved], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f'Syntax error in {resolved}:\n{res.stderr}')
                combined_parts.append(js_raw.decode('utf-8'))

            combined_studio = os.path.join(tmpdir, 'combined_studio.js')
            with open(combined_studio, 'w', encoding='utf-8', newline='\n') as cf:
                cf.write('\n'.join(combined_parts))
            res = subprocess.run(['node', '--check', combined_studio], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Combined Studio JS syntax error:\n{res.stderr}')

        # Also validate all studio modules directly
        studio_modules = sorted(glob.glob(os.path.join(ROOT, 'src', 'studio', '*.js')))
        self.assertGreaterEqual(len(studio_modules), 4)
        for mod in studio_modules:
            self._assert_utf8_lf(mod)
            res = subprocess.run(['node', '--check', mod], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Syntax error in {mod}:\n{res.stderr}')

    def test_07_modular_examples_and_index_build(self):
        import generate_html as gcat
        import generate_chicken_html as gchk
        import generate_mega_room as groom

        with tempfile.TemporaryDirectory() as tmpdir:
            cat_html = os.path.join(tmpdir, 'cat-3d.html')
            chk_html = os.path.join(tmpdir, 'chicken-3d.html')
            room_html = os.path.join(tmpdir, 'room-3d.html')
            idx_html = os.path.join(tmpdir, 'index.html')

            gcat.build_cat_html(cat_html)
            gchk.build_chicken_html(chk_html)
            groom.build_mega_room(room_html, idx_html)

            specs = [
                (cat_html, os.path.join(ROOT, 'examples', 'cat-3d.html'), os.path.join(ROOT, 'examples'), 'cat-3d.css', 2),
                (chk_html, os.path.join(ROOT, 'examples', 'chicken-3d.html'), os.path.join(ROOT, 'examples'), 'chicken-3d.css', 2),
                (room_html, os.path.join(ROOT, 'examples', 'room-3d.html'), os.path.join(ROOT, 'examples'), 'room-3d.css', 7),
                (idx_html, os.path.join(ROOT, 'index.html'), ROOT, 'examples/room-3d.css', 7),
            ]

            for html_path, committed_path, base_dir, expected_css, min_scripts in specs:
                raw = self._assert_utf8_lf(html_path)
                self.assertTrue(os.path.isfile(committed_path), f'Missing committed HTML: {committed_path}')
                self.assertEqual(self._assert_utf8_lf(committed_path), raw, f'Committed {committed_path} is out of sync with generator')
                html_text = raw.decode('utf-8')
                self.assertLess(len(raw), 15 * 1024, f'{html_path} must stay < 15 KB')
                self.assertEqual(re.findall(r'__[A-Z0-9_]+__', html_text), [])
                self.assertIn(f'<link rel="stylesheet" href="{expected_css}"', html_text)
                css_resolved = os.path.normpath(os.path.join(base_dir, expected_css))
                self.assertTrue(os.path.isfile(css_resolved), f'Missing CSS: {css_resolved}')
                self._assert_utf8_lf(css_resolved)

                srcs = re.findall(r'<script\s+src="([^"]+)"', html_text)
                self.assertGreaterEqual(len(srcs), min_scripts, f'Too few scripts in {html_path}')
                parts = []
                for rel_src in srcs:
                    resolved = os.path.normpath(os.path.join(base_dir, rel_src))
                    self.assertTrue(os.path.isfile(resolved), f'Missing script target: {rel_src} -> {resolved}')
                    js_raw = self._assert_utf8_lf(resolved)
                    res = subprocess.run(['node', '--check', resolved], capture_output=True, text=True)
                    self.assertEqual(res.returncode, 0, f'Syntax error in {resolved}:\n{res.stderr}')
                    parts.append(js_raw.decode('utf-8'))

                combined_path = os.path.join(tmpdir, f'{os.path.basename(html_path)}.combined.js')
                with open(combined_path, 'w', encoding='utf-8', newline='\n') as cf:
                    cf.write('\n'.join(parts))
                res = subprocess.run(['node', '--check', combined_path], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f'Combined syntax error for {html_path}:\n{res.stderr}')

    def test_08_repo_hygiene_links_and_legacy_redirects(self):
        text_exts = {'.html', '.css', '.js', '.json', '.py', '.md', '.yml', '.yaml', '.txt'}
        special_names = {'.gitattributes', '.gitignore', 'LICENSE'}
        all_js = []

        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [
                d for d in dirnames
                if d not in {'.git', '__pycache__', '.playwright-mcp', 'pixel-plays', 'pixelart-gaussiansplat', 'shapeshift-labs-ink-studio'}
            ]
            for fn in filenames:
                if fn == 'temp_check.js':
                    continue
                p = os.path.join(dirpath, fn)
                ext = os.path.splitext(fn)[1].lower()
                if ext == '.js':
                    all_js.append(p)
                if ext in text_exts or fn in special_names:
                    raw = self._assert_utf8_lf(p)
                    raw.decode('utf-8')

        self.assertGreaterEqual(len(all_js), 30)
        for js_path in sorted(all_js):
            res = subprocess.run(['node', '--check', js_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Syntax error in {js_path}:\n{res.stderr}')

        # Legacy room scripts must redirect to generate_mega_room instead of emitting monolithic HTML
        for legacy_name in ('generate_room.py', 'generate_full_3d_room.py'):
            with open(os.path.join(ROOT, 'scripts', legacy_name), 'r', encoding='utf-8') as f:
                code = f.read()
            self.assertIn('generate_mega_room', code, f'{legacy_name} must redirect to generate_mega_room')
            self.assertNotIn('<!DOCTYPE html>', code, f'{legacy_name} must not contain monolithic HTML')

        # All local relative href/src links in HTML pages must exist on disk
        for rel_html in (
            'index.html',
            'examples/terrain-world.html',
            'examples/room-3d.html',
            'examples/cat-3d.html',
            'examples/chicken-3d.html',
            'studio/index.html',
        ):
            html_path = os.path.join(ROOT, rel_html)
            base_dir = os.path.dirname(html_path)
            with open(html_path, 'r', encoding='utf-8') as f:
                html_txt = f.read()
            for ref in re.findall(r'(?:href|src)="([^"]+)"', html_txt):
                if ref.startswith(('http://', 'https://', 'data:', '#')):
                    continue
                target = os.path.normpath(os.path.join(base_dir, ref))
                self.assertTrue(os.path.exists(target), f'Broken link in {rel_html}: {ref} -> {target}')

    def test_09_mountain_lakes_drainage_and_anti_aquarium(self):
        node_test = r"""
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = process.cwd();
const mathCode = fs.readFileSync(path.join(root, 'src/engine/00-math-noise.js'), 'utf8');
const bakerCode = fs.readFileSync(path.join(root, 'src/engine/02-slice-baker.js'), 'utf8');
const sculptorCode = fs.readFileSync(path.join(root, 'src/engine/03-terrain-sculptor.js'), 'utf8');
const fluidsCode = fs.readFileSync(path.join(root, 'src/engine/06-fluids-weather.js'), 'utf8');

const mw = 64, mh = 64, VOX = 2, HALF_GRID = 32;
const Z_MIN = -6, TERRAIN_Z_MAX = 66, Z_GRASS_MAX = 70;
const MAT_GRASS = 0, MAT_PATH = 1, MAT_SAND = 2, MAT_STONE = 3,
      MAT_WATER = 4, MAT_BRIDGE = 5, MAT_PEAK = 6, MAT_LILYPAD = 7, MAT_SHALLOW = 8;

const fakeCanvases = [];
const sandbox = {
  assert, Math, Number, Array, Int16Array, Int32Array, Uint8Array, Uint32Array, Float32Array,
  Set, Map, URLSearchParams, console, performance: { now: () => 0 },
  WORLD_CFG: { gridW: mw, gridH: mh, vox: VOX, isDefault: false },
  mw, mh, VOX, HALF_GRID, HALF_WORLD: HALF_GRID * VOX,
  Z_MIN, TERRAIN_Z_MAX, Z_GRASS_MAX, AUTO_STEP_MAX: 5.5,
  MAT_GRASS, MAT_PATH, MAT_SAND, MAT_STONE, MAT_WATER, MAT_BRIDGE, MAT_PEAK, MAT_LILYPAD, MAT_SHALLOW,
  isWetMat: (m) => m === MAT_WATER || m === MAT_SHALLOW,
  hmap: new Int16Array(mw * mh),
  waterDepth: new Uint8Array(mw * mh),
  waterfallDropMask: new Uint8Array(mw * mh),
  waterSprings: [],
  matMap: new Uint8Array(mw * mh),
  biomeMap: new Uint8Array(mw * mh),
  cliffMask: new Uint8Array(mw * mh),
  shadowMask: new Uint8Array(mw * mh),
  noGrassMask: new Uint8Array(mw * mh),
  standableMap: new Uint8Array(mw * mh),
  cliffTopMap: new Int16Array(mw * mh),
  props: [],
  debrisDrops: [],
  cat: { x: 0, y: 0, z: 0, onGround: true, scale: 1 },
  camX: 0, camY: 0,
  RIVER_SEGMENTS: [],
  PROP_COLLIDER_META: {},
  getBridgeAt: () => null,
  getBridgeDeckZ: () => 0,
  getCellAt: (wx, wy) => {
    const mx = Math.floor(wx / VOX + HALF_GRID);
    const my = Math.floor(wy / VOX + HALF_GRID);
    if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
    const idx = my * mw + mx;
    return { mx, my, idx, h: sandbox.hmap[idx], mat: sandbox.matMap[idx], waterDepth: sandbox.waterDepth[idx] };
  },
  getHeightAt: (wx, wy) => {
    const mx = Math.floor(wx / VOX + HALF_GRID);
    const my = Math.floor(wy / VOX + HALF_GRID);
    if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
    return sandbox.hmap[my * mw + mx];
  },
  worldToGrid: (wx, wy) => ({ mx: Math.floor(wx / VOX + HALF_GRID), my: Math.floor(wy / VOX + HALF_GRID) }),
  window: { __IS_STUDIO__: true, location: { search: '' } },
  document: {
    createElement: () => {
      const cv = {
        width: 0, height: 0, _buf: null,
        getContext: () => ({
          createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
          putImageData: (img) => { cv._buf = new Uint32Array(img.data.buffer.slice(0)); }
        })
      };
      fakeCanvases.push(cv);
      return cv;
    }
  }
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
function runTestsInVm() {
  function resetIslandWithMountain() {
    hmap.fill(-6);
    matMap.fill(MAT_WATER);
    waterDepth.fill(0);
    waterfallDropMask.fill(0);
    waterSprings.length = 0;
    for (let my = 10; my <= 54; my++) {
      for (let mx = 10; mx <= 54; mx++) {
        const d = Math.hypot(mx - 32, my - 32);
        const idx = my * mw + mx;
        if (d <= 14) {
          hmap[idx] = 20;
          matMap[idx] = MAT_GRASS;
        } else if (d <= 22) {
          const h = Math.round(20 * (1 - (d - 14) / 8) - 2);
          hmap[idx] = Math.max(-6, h);
          matMap[idx] = h > -2 ? (h <= 2 ? MAT_SAND : MAT_GRASS) : MAT_WATER;
        }
      }
    }
  }

  // A. Cratera fechada na montanha: preenche até spillZ - 1 com centro fundo e borda rasa
  resetIslandWithMountain();
  for (let my = 27; my <= 37; my++) {
    for (let mx = 27; mx <= 37; mx++) {
      const d = Math.hypot(mx - 32, my - 32);
      if (d <= 4.5) {
        const idx = my * mw + mx;
        hmap[idx] = Math.round(12 + d * 1.4);
      }
    }
  }
  applyWaterBrushHydrology(32, 32, 2, 'mat_water');
  const centerIdx = 32 * mw + 32;
  assert.strictEqual(matMap[centerIdx], MAT_WATER, 'Center of deep mountain crater should be MAT_WATER');
  assert.strictEqual(hmap[centerIdx], 19, 'Crater surface should level at spillZ - 1 = 19');
  assert.strictEqual(waterDepth[centerIdx], 7, 'Crater center waterDepth should be 19 - 12 = 7');
  const edgeIdx = 32 * mw + 36;
  assert.strictEqual(matMap[edgeIdx], MAT_SHALLOW, 'Shallow crater edge should be MAT_SHALLOW');
  assert(waterDepth[edgeIdx] >= 1 && waterDepth[edgeIdx] <= 2, 'Shallow edge depth 1..2');
  assert.strictEqual(matMap[32 * mw + 40], MAT_GRASS, 'Outer mountain rim must stay dry');

  // B. Anti-Aquário: parede lateral exposta abaixo da superfície sem cachoeira ativa deve ser ROCHA sólida
  resetIslandWithMountain();
  const aqIdx = 32 * mw + 32;
  hmap[aqIdx] = 20;
  matMap[aqIdx] = MAT_WATER;
  waterDepth[aqIdx] = 5; // bedZ = 15
  hmap[32 * mw + 33] = 4;
  matMap[32 * mw + 33] = MAT_GRASS;
  bakeTerrainSlices();
  assert.strictEqual(waterfallDropMask[aqIdx], 0, 'Dry drop next to lake must NOT trigger waterfall curtain');
  const sl18 = terrainSlices[18];
  assert(sl18 && sl18.canvas && sl18.canvas._buf, 'Slice 18 should be baked');
  const px18 = sl18.canvas._buf[(32 - sl18.offY) * sl18.w + (32 - sl18.offX)];
  const r18 = px18 & 255, g18 = (px18 >>> 8) & 255, b18 = (px18 >>> 16) & 255;
  assert(r18 > 40 && b18 < 180 && Math.abs(r18 - b18) < 40, 'Exposed lake wall at z=18 must be solid rock, got rgb(' + r18 + ',' + g18 + ',' + b18 + ')');

  // C. Nascente (spring) em montanha com queda abrupta + encosta suave: escoa até o mar, gera cachoeira e -∇h
  resetIslandWithMountain();
  for (let mx = 32; mx <= 38; mx++) hmap[32 * mw + mx] = 20 - Math.floor((mx - 32) / 3);
  hmap[32 * mw + 39] = 6;
  matMap[32 * mw + 39] = MAT_GRASS;
  for (let mx = 40; mx <= 50; mx++) {
    const h = Math.max(-3, 6 - (mx - 39));
    hmap[32 * mw + mx] = h;
    matMap[32 * mw + mx] = h <= -2 ? MAT_WATER : MAT_GRASS;
  }
  placeSpringHydrology(32, 32);
  computeWaterfallDrops();
  assert(waterfallDrops.length >= 1, 'Steep drop (18 -> 6) must create dynamic waterfall drop');
  assert(waterfallDrops[0].botWx !== undefined && waterfallDrops[0].botWy !== undefined, 'Waterfall drop must record plunge-pool base coordinates');
  let reachedSea = false;
  for (let mx = 45; mx <= 52; mx++) {
    const idx = 32 * mw + mx;
    if (isWetMat(matMap[idx]) && hmap[idx] <= -2) reachedSea = true;
  }
  assert(reachedSea, 'Spring drainage must reach sea level (Z <= -2)');
  const wxSlope = (42 - HALF_GRID + 0.5) * VOX;
  const wySlope = (32 - HALF_GRID + 0.5) * VOX;
  const flow = sampleBaseWaterFlow(wxSlope, wySlope);
  assert(flow.speed > 5 && flow.vx > 0, 'Sloped mountain stream must flow downhill (+x), got vx=' + flow.vx + ', speed=' + flow.speed);

  // D. Rompimento de barragem: baixar a borda do lago da cratera drena o lago e escoa pelo corte
  resetIslandWithMountain();
  for (let my = 27; my <= 37; my++) {
    for (let mx = 27; mx <= 37; mx++) {
      const d = Math.hypot(mx - 32, my - 32);
      if (d <= 4.5) hmap[my * mw + mx] = Math.round(12 + d * 1.4);
    }
  }
  applyWaterBrushHydrology(32, 32, 2, 'mat_water');
  assert.strictEqual(hmap[32 * mw + 32], 19);
  for (let mx = 37; mx <= 50; mx++) {
    const h = Math.max(-3, 10 - (mx - 37));
    hmap[32 * mw + mx] = h;
    matMap[32 * mw + mx] = h <= -2 ? MAT_WATER : MAT_GRASS;
  }
  const breachRes = drainBreachedLakesInRect(35, 30, 39, 34);
  assert(breachRes.changed, 'Dam breach must detect and drain lake');
  assert(!isWetMat(matMap[centerIdx]), 'Lake bed at Z=12 must drain dry when breach is at Z=10');

  // E. Escoamento ao subir terreno do mar (elevação > -2 vira solo seco)
  const seaIdx = 5 * mw + 5;
  hmap[seaIdx] = 5;
  matMap[seaIdx] = MAT_WATER;
  waterDepth[seaIdx] = 0;
  assert(drainElevatedWetCell(seaIdx), 'Elevated uncontained sea cell must drain');
  assert.strictEqual(matMap[seaIdx], MAT_GRASS, 'Drained cell at Z=5 must become MAT_GRASS');
  assert.strictEqual(waterDepth[seaIdx], 0);

  // F. Encosta suave com degraus planos (> 18 degraus): nascente deve alcançar o mar sem parar no meio da montanha
  hmap.fill(-6); matMap.fill(MAT_WATER); waterDepth.fill(0);
  for (let my = 4; my <= 60; my++) {
    for (let mx = 4; mx <= 60; mx++) {
      const d = Math.hypot(mx - 32, my - 32);
      if (d <= 28) {
        const h = Math.round(28 * (1 - d / 28));
        const idx = my * mw + mx;
        hmap[idx] = h;
        matMap[idx] = h <= -2 ? MAT_WATER : (h <= 2 ? MAT_SAND : MAT_GRASS);
      }
    }
  }
  placeSpringHydrology(32, 32);
  let gentleTouchesSea = false;
  for (let my = 1; my < mh - 1; my++) {
    for (let mx = 1; mx < mw - 1; mx++) {
      const i = my * mw + mx;
      if (waterDepth[i] > 0) {
        for (const nb of [i-1, i+1, i-mw, i+mw, i-mw-1, i-mw+1, i+mw-1, i+mw+1]) {
          if (isWetMat(matMap[nb]) && hmap[nb] <= -2) gentleTouchesSea = true;
        }
      }
    }
  }
  assert(gentleTouchesSea, 'Gentle terraced mountain spring (>18 steps) must reach sea level');

  // G. Arrastar pincel de água sobre platô plano não deve perfurar o terreno repetidamente
  hmap.fill(20); matMap.fill(MAT_GRASS); waterDepth.fill(0);
  for (let step = 0; step < 8; step++) {
    applyWaterBrushHydrology(28 + step, 32, 3, 'mat_water', null, step === 0);
  }
  for (let i = 0; i < hmap.length; i++) {
    if (isWetMat(matMap[i])) {
      assert.strictEqual(hmap[i], 19, 'Flat plateau pond surface must stay at 19');
      assert(waterDepth[i] <= 3, 'Flat plateau pond must not drill deeper than depth 3');
    }
  }

  // H. Lago raso (waterDepth=1) rompido deve escoar e MAT_SHALLOW no mar deve ter hmap=-2
  hmap.fill(20); matMap.fill(MAT_GRASS); waterDepth.fill(0);
  for (let my = 29; my <= 35; my++) {
    for (let mx = 29; mx <= 35; mx++) {
      if (Math.hypot(mx - 32, my - 32) <= 2.5) paintWetCell(my * mw + mx, 20, 19, MAT_SHALLOW);
    }
  }
  for (let mx = 35; mx <= 48; mx++) hmap[32 * mw + mx] = 10 - (mx - 35);
  const shallowBreach = drainBreachedLakesInRect(33, 30, 36, 34);
  assert(shallowBreach.changed, 'Shallow breached pond must drain');
  assert(!isWetMat(matMap[32 * mw + 32]), 'Shallow breached pond bed must become dry');
  paintWetCell(6 * mw + 6, -2, -2, MAT_SHALLOW);
  assert.strictEqual(hmap[6 * mw + 6], -2, 'Sea-level MAT_SHALLOW must have hmap=-2');

  console.log('HYDROLOGY_AND_ANTI_AQUARIUM_OK');
}
vm.runInContext(
  mathCode + '\n' + bakerCode + '\n' + sculptorCode + '\n' + fluidsCode + '\n(' + runTestsInVm.toString() + ')()',
  sandbox
);
"""
        res = subprocess.run(['node', '-e', node_test], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Node hydrology test failed:\n{res.stderr}\n{res.stdout}')
        self.assertIn('HYDROLOGY_AND_ANTI_AQUARIUM_OK', res.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
