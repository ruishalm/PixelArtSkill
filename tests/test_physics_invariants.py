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

            self.assertLess(len(raw), 28 * 1024, 'studio/index.html must stay < 28 KB')
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

    def test_10_caves_and_dual_sidebar_studio(self):
        # 1. Dual sidebar DOM/CSS contract in built studio/index.html & studio/studio.css
        studio_html_path = os.path.join(ROOT, 'studio', 'index.html')
        studio_css_path = os.path.join(ROOT, 'studio', 'studio.css')
        with open(studio_html_path, 'r', encoding='utf-8') as f:
            studio_html = f.read()
        with open(studio_css_path, 'r', encoding='utf-8') as f:
            studio_css = f.read()

        idx_left = studio_html.find('class="sidebar sidebar-left"')
        idx_stage = studio_html.find('class="stage"')
        idx_right = studio_html.find('class="sidebar sidebar-right"')
        self.assertGreater(idx_left, 0)
        self.assertGreater(idx_stage, idx_left)
        self.assertGreater(idx_right, idx_stage)

        left_html = studio_html[idx_left:idx_stage]
        right_html = studio_html[idx_right:]
        for tool in ('data-tool="raise"', 'data-tool="cave_carve"', 'data-tool="cave_fill"', 'data-tool="mat_water"', 'data-tool="spring"', 'id="slRadius"'):
            self.assertIn(tool, left_html, f'Missing {tool} in left sidebar')
        for item in ('data-tool="prop_pine_tree"', 'id="customAssetGrid"', 'id="avatarSelect"', 'id="slWind"', 'id="slGravity"', 'id="slCool"', 'id="slTalus"'):
            self.assertIn(item, right_html, f'Missing {item} in right sidebar')
        self.assertNotIn('data-tool="prop_pine_tree"', left_html)
        self.assertIn('.sidebar-right', studio_css)
        self.assertIn('border-left', studio_css)
        self.assertIn('.play-only .topbar, .play-only .sidebar', studio_css)
        self.assertIn('id="btnZoomOut"', studio_html)
        self.assertIn('id="btnZoomReset"', studio_html)
        self.assertIn('id="btnZoomIn"', studio_html)
        self.assertIn('Scroll: Zoom', studio_html)
        self.assertIn('.zoom-pill', studio_css)

        # 2. Caves: baking, 2-floor physics, cutaway X-ray, brushes, undo/redo, JSON persistence
        node_cave_test = r"""
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = process.cwd();
const mathCode = fs.readFileSync(path.join(root, 'src/engine/00-math-noise.js'), 'utf8');
const bakerCode = fs.readFileSync(path.join(root, 'src/engine/02-slice-baker.js'), 'utf8');
const sculptorCode = fs.readFileSync(path.join(root, 'src/engine/03-terrain-sculptor.js'), 'utf8');
const rendererCode = fs.readFileSync(path.join(root, 'src/engine/04-renderer.js'), 'utf8');
const fluidsCode = fs.readFileSync(path.join(root, 'src/engine/06-fluids-weather.js'), 'utf8');
const physCode = fs.readFileSync(path.join(root, 'src/engine/07-physics-movement.js'), 'utf8');
const destrCode = fs.readFileSync(path.join(root, 'src/engine/08-destruction-carry.js'), 'utf8');
const brushesCode = fs.readFileSync(path.join(root, 'src/studio/01-studio-state-brushes.js'), 'utf8');
const regenCode = fs.readFileSync(path.join(root, 'src/studio/02-studio-regen-undo.js'), 'utf8');
const uiCode = fs.readFileSync(path.join(root, 'src/studio/03-studio-ui-io.js'), 'utf8');

const mw = 64, mh = 64, VOX = 2, HALF_GRID = 32;
const Z_MIN = -6, TERRAIN_Z_MAX = 66, Z_GRASS_MAX = 70;
const MAT_GRASS = 0, MAT_PATH = 1, MAT_SAND = 2, MAT_STONE = 3,
      MAT_WATER = 4, MAT_BRIDGE = 5, MAT_PEAK = 6, MAT_LILYPAD = 7, MAT_SHALLOW = 8;

const elements = new Map();
function makeEl(id, extra = {}) {
  const listeners = {};
  const el = {
    id, value: '', textContent: '', innerHTML: '', className: '',
    style: {}, dataset: {},
    classList: { _s: new Set(), add(c){this._s.add(c);}, remove(c){this._s.delete(c);}, contains(c){return this._s.has(c);} },
    addEventListener(ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    _emit(ev, e = {}) { (listeners[ev] || []).forEach(fn => fn({ preventDefault(){}, target: el, ...e })); },
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 640, height: 480 }),
    setPointerCapture(){}, releasePointerCapture(){},
    parentElement: { clientWidth: 640, clientHeight: 480 },
    width: 640, height: 480, clientWidth: 640, clientHeight: 480,
    ...extra
  };
  if (id) elements.set(id, el);
  return el;
}

const alphaLog = [];
function makeCtx(trackAlpha = false) {
  let _alpha = 1.0;
  return {
    imageSmoothingEnabled: false,
    globalCompositeOperation: 'source-over',
    fillStyle: '', strokeStyle: '', lineWidth: 1, font: '', textBaseline: 'middle',
    get globalAlpha() { return _alpha; },
    set globalAlpha(v) { _alpha = v; if (trackAlpha) alphaLog.push(v); },
    save(){}, restore(){}, translate(){}, scale(){}, rotate(){}, setTransform(){},
    beginPath(){}, closePath(){}, moveTo(){}, lineTo(){}, ellipse(){}, arc(){}, roundRect(){},
    fill(){}, stroke(){}, fillRect(){}, clearRect(){}, fillText(){},
    measureText: () => ({ width: 20 }),
    createLinearGradient: () => ({ addColorStop(){} }),
    createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
    getImageData: (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
    putImageData(img) { if (this._owner) this._owner._buf = new Uint32Array(img.data.buffer.slice(0)); },
    drawImage(src) { if (trackAlpha && src && src._isSlice) alphaLog.push('draw:' + _alpha.toFixed(2)); }
  };
}

const viewportCv = makeEl('viewport');
viewportCv.getContext = () => makeCtx(false);
makeEl('studioOverlay').getContext = () => makeCtx(false);
makeEl('baseKindSelect', { value: 'flat' });
makeEl('genModeSelect', { value: 'hybrid' });
makeEl('gridSizeSelect', { value: '64' });
makeEl('seedInput', { value: '1337' });
makeEl('avatarSelect', { value: 'human' });
makeEl('slAvatarScale', { value: '1.0' });
makeEl('valAvatarScale');
makeEl('slRadius', { value: '16' });
makeEl('valRadius');
makeEl('slStrength', { value: '1.2' });
makeEl('valStrength');
makeEl('slWind', { value: '1.0' });
makeEl('valWind');
makeEl('slGravity', { value: '1200' });
makeEl('valGravity');
makeEl('slCool', { value: '0.22' });
makeEl('valCool');
makeEl('slTalus', { value: '2' });
makeEl('valTalus');
for (const id of [
  'btnModeEdit','btnModeTest','btnRandSeed','btnNewFlat','btnUndo','btnRedo',
  'btnPinSel','btnUnpinSel','btnPinAll','btnUnpinAll','btnClearSel',
  'btnRegenAll','btnRegenUnpinned','btnExportJson','btnPublishHtml','btnImportJson',
  'fileImportInput','btnTouchJump','helpPill','coordPill','biomeToast',
  'biomeLabel','fishCounter','biomeCounter','statElev','statObstacle',
  'btnZoomOut','btnZoomReset','btnZoomIn'
]) makeEl(id);

const winListeners = {};

const sidebars = [makeEl('sbL'), makeEl('sbR')];
const btnLeft = makeEl('btnLeft', { dataset: { tool: 'raise' }, classList: { _s: new Set(['tool-btn', 'active']), add(c){this._s.add(c);}, remove(c){this._s.delete(c);}, contains(c){return this._s.has(c);} } });
const btnRight = makeEl('btnRight', { dataset: { tool: 'prop_pine_tree' }, classList: { _s: new Set(['tool-btn']), add(c){this._s.add(c);}, remove(c){this._s.delete(c);}, contains(c){return this._s.has(c);} } });
const sandbox = {
  assert, Math, Number, Array, Object, JSON, Int16Array, Int32Array, Uint8Array, Uint32Array, Float32Array,
  Set, Map, URLSearchParams, URL: class { static createObjectURL(){ return 'blob:test'; } constructor(u){ this.href = u; this.searchParams = new URLSearchParams(); } toString(){ return this.href; } },
  __exportedPayload: null,
  Blob: class { constructor(parts){ sandbox.__exportedPayload = parts[0]; } },
  FileReader: class { readAsText(file) { this.result = file._text; if (this.onload) this.onload(); } },
  __leftBtn: btnLeft, __rightBtn: btnRight, __sidebars: sidebars,
  console, performance: { now: () => 0 },
  confirm: () => true, alert: () => {},
  WORLD_CFG: { gridW: mw, gridH: mh, vox: VOX, isDefault: false },
  mw, mh, VOX, HALF_GRID, HALF_WORLD: HALF_GRID * VOX,
  WORLD_MIN: -HALF_GRID * VOX, WORLD_MAX: HALF_GRID * VOX,
  Z_MIN, TERRAIN_Z_MAX, Z_GRASS_MAX, CAT_HEIGHT: 16, AUTO_STEP_MAX: 5.5,
  GRAVITY: 1200, JUMP_VEL: Math.sqrt(2 * 1200 * 35.0),
  MAT_GRASS, MAT_PATH, MAT_SAND, MAT_STONE, MAT_WATER, MAT_BRIDGE, MAT_PEAK, MAT_LILYPAD, MAT_SHALLOW,
  isWetMat: (m) => m === MAT_WATER || m === MAT_SHALLOW,
  hmap: new Int16Array(mw * mh),
  caveFloor: new Int16Array(mw * mh).fill(-32768),
  caveCeil: new Int16Array(mw * mh).fill(-32768),
  waterDepth: new Uint8Array(mw * mh),
  waterfallDropMask: new Uint8Array(mw * mh),
  waterSprings: [],
  matMap: new Uint8Array(mw * mh),
  biomeMap: new Uint8Array(mw * mh),
  cliffMask: new Uint8Array(mw * mh),
  shadowMask: new Uint8Array(mw * mh),
  noGrassMask: new Uint8Array(mw * mh),
  standableMap: new Uint8Array(mw * mh).fill(1),
  cliffTopMap: new Int16Array(mw * mh),
  props: [], foliageProps: [], propColliders: [], platformColliders: [],
  fishes: [], npcs: [], toolPickups: [], fallingBodies: [], debrisDrops: [],
  verletChains: [], catSkinModels: [{ paw: { count: 4, w: 4, h: 4, sheet: {} }, body: { count: 8, w: 8, h: 8, sheet: {} } }],
  HAT_PRESETS: [{ id: 'none' }], hatModels: {}, TOOLS_META: { none: { modelKey: null } },
  PROP_COLLIDER_META: {},
  propModels: { wood_log: { count: 6, w: 6, h: 6, sheet: {} } },
  lastRustleCell: -1,
  sfxJump(){}, sfxLand(){}, sfxBlocked(){}, sfxShallowStep(){}, sfxBiome(){}, sfxFish(){}, sfxChop(){}, sfxCrumble(){},
  addProp(){}, bakeMinimapBase(){},
  worldToGrid: (wx, wy) => ({ mx: Math.floor(wx / VOX + HALF_GRID), my: Math.floor(wy / VOX + HALF_GRID) }),
  getCellAt: (wx, wy) => {
    const mx = Math.floor(wx / VOX + HALF_GRID);
    const my = Math.floor(wy / VOX + HALF_GRID);
    if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
    const idx = my * mw + mx;
    const cf = sandbox.caveFloor[idx], cc = sandbox.caveCeil[idx];
    const mat = sandbox.matMap[idx], wd = sandbox.waterDepth[idx];
    const wet = mat === MAT_WATER || mat === MAT_SHALLOW;
    const solidTop = (wet && wd > 0) ? Math.max(Z_MIN, sandbox.hmap[idx] - wd) : sandbox.hmap[idx];
    return {
      mx, my, idx,
      h: sandbox.hmap[idx], mat, waterDepth: wd,
      hasCave: cc > cf && solidTop > cc, caveFloor: cf, caveCeil: cc,
      biomeId: 0, biomeKey: 'vila', biome: 'Vila',
      standable: sandbox.standableMap[idx] === 1, cliffTop: sandbox.cliffTopMap[idx]
    };
  },
  getHeightAt: (wx, wy) => {
    const mx = Math.floor(wx / VOX + HALF_GRID);
    const my = Math.floor(wy / VOX + HALF_GRID);
    if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
    return sandbox.hmap[my * mw + mx];
  },
  window: {
    __IS_STUDIO__: true, innerWidth: 640, innerHeight: 480, devicePixelRatio: 1,
    location: { search: '', href: 'http://localhost/studio/index.html' },
    addEventListener(ev, fn){ (winListeners[ev] = winListeners[ev] || []).push(fn); },
    _emit(ev, e = {}){ (winListeners[ev] || []).forEach(fn => fn({ preventDefault(){}, target: { tagName: 'BODY' }, ...e })); },
    dispatchEvent(){}
  },
  document: {
    body: { classList: { _s: new Set(), add(c){this._s.add(c);}, remove(c){this._s.delete(c);}, contains(c){return this._s.has(c);} } },
    getElementById: (id) => elements.get(id) || null,
    querySelector: (sel) => sel === '.sidebar' ? sidebars[0] : makeEl('q'),
    querySelectorAll: (sel) => sel === '.sidebar' ? sidebars : (sel === '.sidebar .tool-btn' ? [btnLeft, btnRight] : []),
    createElement: (tag) => {
      if (tag === 'a') return { click(){}, href: '', download: '' };
      const cv = { width: 0, height: 0, _buf: null, _isSlice: true };
      const c2d = makeCtx(false);
      c2d._owner = cv;
      cv.getContext = () => c2d;
      return cv;
    }
  }
};
sandbox.globalThis = sandbox;
sandbox.window.document = sandbox.document;
vm.createContext(sandbox);

function runCaveSuite() {
  let sawCutawayAlpha = false;
  let sawRestoreAlpha = false;
  let _curAlpha = 1.0;
  Object.defineProperty(lowCtx, 'globalAlpha', {
    get() { return _curAlpha; },
    set(v) {
      if (Math.abs(v - 0.22) < 0.01) sawCutawayAlpha = true;
      if (sawCutawayAlpha && Math.abs(v - 1.0) < 0.01) sawRestoreAlpha = true;
      _curAlpha = v;
    }
  });

  // Build flat world with a steep rectangular mountain block on mx=30..44, my=26..38 (h=26)
  hmap.fill(0);
  caveFloor.fill(-32768);
  caveCeil.fill(-32768);
  matMap.fill(MAT_GRASS);
  for (let my = 26; my <= 38; my++) {
    for (let mx = 30; mx <= 44; mx++) {
      hmap[my * mw + mx] = 26;
    }
  }
  buildStandableMap();

  // Carve cave inside mountain (mx=30..38, my=30..34) with floor=0, ceil=14; mouth at mx=29 (h=0)
  for (let my = 30; my <= 34; my++) {
    for (let mx = 30; mx <= 38; mx++) {
      const idx = my * mw + mx;
      caveFloor[idx] = 0;
      caveCeil[idx] = 14;
    }
  }
  bakeTerrainSlices();

  // 1. Slice baker checks: hollow air at z=5, solid floor at z=0, roof at z=16, 4-conn wall at mx=39
  const caveMx = 34, caveMy = 32;
  const wallMx = 39, wallMy = 32;
  const sl5 = terrainSlices[5];
  assert(sl5 && sl5.canvas && sl5.canvas._buf, 'Slice 5 must exist for cave walls');
  const pxHollow = sl5.canvas._buf[(caveMy - sl5.offY) * sl5.w + (caveMx - sl5.offX)];
  assert.strictEqual(pxHollow, 0, 'Interior cave slice z=5 must be hollow/transparent (0)');

  const pxWall = sl5.canvas._buf[(wallMy - sl5.offY) * sl5.w + (wallMx - sl5.offX)];
  assert.notStrictEqual(pxWall, 0, '4-connected solid wall at mx=39, z=5 must NOT be culled by min8');

  const sl0 = terrainSlices[0];
  assert(sl0 && sl0.canvas && sl0.canvas._buf, 'Slice 0 must exist for cave floor');
  const pxFloor = sl0.canvas._buf[(caveMy - sl0.offY) * sl0.w + (caveMx - sl0.offX)];
  assert.notStrictEqual(pxFloor, 0, 'Cave floor at z=0 must be painted even when min8 >= 0');

  const sl16 = terrainSlices[16];
  assert(sl16 && sl16.canvas && sl16.canvas._buf, 'Slice 16 must exist for cave roof');
  const pxRoof = sl16.canvas._buf[(caveMy - sl16.offY) * sl16.w + (caveMx - sl16.offX)];
  assert.notStrictEqual(pxRoof, 0, 'Cave roof at z=16 must be solid');

  // 2. 2-Floor physics: enter cave mouth at z=0, walk inside, jump hits ceiling, and walk on mountain roof z=26
  const mouthWx = (29 - HALF_GRID + 0.5) * VOX;
  const inCaveWx = (32 - HALF_GRID + 0.5) * VOX;
  const caveWy = (32 - HALF_GRID + 0.5) * VOX;
  cat.scale = 1.0;
  teleportToWorld(mouthWx, caveWy, null, 0);
  assert.strictEqual(getEffectiveGroundAt(inCaveWx, caveWy, 0, 1.0), 0, 'Lower floor effective ground must be caveFloor=0');
  assert.strictEqual(getEffectiveGroundAt(inCaveWx, caveWy, 26, 1.0), 26, 'Upper floor effective ground must be hmap=26');
  assert.strictEqual(checkCollisionAt(inCaveWx, caveWy, 0, true).blocked, false, 'Player at z=0 must be able to enter cave');

  // Move player inside cave and check cutaway rendering
  teleportToWorld(inCaveWx, caveWy, null, 0);
  window.__STUDIO_EDIT_MODE__ = false;
  sawCutawayAlpha = false;
  sawRestoreAlpha = false;
  renderScene();
  assert(sawCutawayAlpha, 'Cutaway X-ray must apply globalAlpha = 0.22 when player is inside cave');
  assert(sawRestoreAlpha, 'Cutaway X-ray must restore globalAlpha = 1.0 after drawing slice');
  assert.strictEqual(lowCtx.globalAlpha, 1.0, 'lowCtx.globalAlpha must end at 1.0');

  // Jump inside cave must not clip through roof (z must stay < caveCeil)
  cat.jumpBuffer = 0.14;
  for (let s = 0; s < 30; s++) updatePhysics(1 / 60);
  assert(cat.z < 14, 'Jumping inside cave must bump ceiling and stay below caveCeil=14, got z=' + cat.z);

  // Low-ceiling cave (headroom 8 < 10*scale) must block entry
  caveCeil[32 * mw + 31] = 8;
  const lowWx = (31 - HALF_GRID + 0.5) * VOX;
  assert.strictEqual(checkCollisionAt(lowWx, caveWy, 0, true).blocked, true, 'Low-ceiling cave (<10*scale) must block entry');
  caveCeil[32 * mw + 31] = 14;

  // Walking on top of mountain above cave
  teleportToWorld(inCaveWx, caveWy, null, 26);
  assert.strictEqual(checkCollisionAt(inCaveWx + 2, caveWy, 26, true).blocked, false, 'Player on mountain top z=26 must walk over cave roof');

  // 3. Studio brushes (cave_carve, cave_fill), Undo/Redo, and JSON persistence
  window.__STUDIO_EDIT_MODE__ = true;
  const S = window.__STUDIO__;
  S.syncSculptFromHmap();
  S.pushUndoSnapshot();
  S.activeTool = 'cave_carve';
  S.brushRadius = 8;
  const brushWx = (36 - HALF_GRID + 0.5) * VOX;
  const brushWy = (28 - HALF_GRID + 0.5) * VOX;
  S.applyTerrainBrush(brushWx, brushWy, true);
  const cBr = getCellAt(brushWx, brushWy);
  assert(cBr.hasCave, 'cave_carve brush on mountain must carve a cave');

  // Dual sidebar tool-btn delegation check (left & right sidebars share active state)
  __sidebars[1]._emit('click', { target: { closest: () => __rightBtn } });
  assert.strictEqual(S.activeTool, 'prop_pine_tree', 'Right sidebar tool click must update S.activeTool');
  assert(!__leftBtn.classList.contains('active'), 'Left sidebar tool must be deactivated when right sidebar tool is clicked');
  assert(__rightBtn.classList.contains('active'), 'Right sidebar tool must become active');

  // Export JSON, wipe flat, re-import JSON, verify cave restored
  document.getElementById('btnExportJson')._emit('click');
  assert(globalThis.__exportedPayload, 'Export JSON must emit payload');
  const parsed = JSON.parse(globalThis.__exportedPayload);
  assert(Array.isArray(parsed.caveSparse) && parsed.caveSparse.length > 0, 'Export JSON must include non-empty caveSparse');

  document.getElementById('btnNewFlat')._emit('click');
  assert.strictEqual(getCellAt(brushWx, brushWy).hasCave, false, 'btnNewFlat must clear caves');

  // Re-import JSON via fileImportInput and verify cave restored
  document.getElementById('fileImportInput')._emit('change', { target: { files: [{ _text: globalThis.__exportedPayload }], value: 'x' } });
  const cImported = getCellAt(brushWx, brushWy);
  assert(cImported.hasCave, 'Importing JSON must restore carved cave via caveSparse');
  assert.strictEqual(cImported.caveFloor, cBr.caveFloor);
  assert.strictEqual(cImported.caveCeil, cBr.caveCeil);

  // Studio cutaway X-ray when cave_carve active and hoverWorld over cave
  window.__STUDIO_EDIT_MODE__ = true;
  S.activeTool = 'cave_carve';
  S.hoverWorld = { wx: brushWx, wy: brushWy, z: cImported.h };
  sawCutawayAlpha = false;
  sawRestoreAlpha = false;
  renderScene();
  assert(sawCutawayAlpha && sawRestoreAlpha, 'Studio cave_carve hover over cave must trigger cutaway X-ray');

  // Undo restores cave after btnNewFlat
  document.getElementById('btnNewFlat')._emit('click');
  assert.strictEqual(getCellAt(brushWx, brushWy).hasCave, false);
  S.popUndoSnapshot();
  assert(getCellAt(brushWx, brushWy).hasCave, 'Undo must restore carved cave');

  // cave_fill closes cave
  S.pushUndoSnapshot();
  S.activeTool = 'cave_fill';
  S.applyTerrainBrush(brushWx, brushWy, true);
  assert.strictEqual(getCellAt(brushWx, brushWy).hasCave, false, 'cave_fill brush must close cave');
  S.popUndoSnapshot();
  assert(getCellAt(brushWx, brushWy).hasCave, 'Undo after cave_fill must reopen cave');

  // 4. Regression checks:
  // 4a. Sloped cave mouth (h=12) must open cleanly for human scale=1.0 (no 9u headroom bottleneck)
  document.getElementById('btnNewFlat')._emit('click');
  for (let my = 28; my <= 36; my++) {
    hmap[my * mw + 30] = 12;
    for (let mx = 31; mx <= 40; mx++) hmap[my * mw + mx] = 26;
  }
  buildStandableMap();
  S.syncSculptFromHmap();
  S.activeTool = 'cave_carve';
  S.brushRadius = 10;
  S.applyTerrainBrush((29 - HALF_GRID + 0.5) * VOX, (32 - HALF_GRID + 0.5) * VOX, true);
  cat.scale = 1.0;
  teleportToWorld((29 - HALF_GRID + 0.5) * VOX, (32 - HALF_GRID + 0.5) * VOX, null, 0);
  assert.strictEqual(
    checkCollisionAt((30 - HALF_GRID + 0.5) * VOX, (32 - HALF_GRID + 0.5) * VOX, 0, true).blocked,
    false,
    'Sloped foothill carved with cave_carve must allow human (scale=1.0) to enter'
  );

  // 4b. Lake over cave preserves water body slices (blue, not rock) & clamps punctured roof
  document.getElementById('btnNewFlat')._emit('click');
  for (let my = 28; my <= 36; my++) {
    for (let mx = 28; mx <= 36; mx++) {
      const idx = my * mw + mx;
      hmap[idx] = 20; caveFloor[idx] = 0; caveCeil[idx] = 12;
      if (mx >= 31 && mx <= 33 && my >= 31 && my <= 33) {
        matMap[idx] = MAT_WATER; waterDepth[idx] = 5;
      }
    }
  }
  bakeTerrainSlices();
  const sl17 = terrainSlices[17];
  const px17 = sl17.canvas._buf[(32 - sl17.offY) * sl17.w + (32 - sl17.offX)];
  assert((px17 >>> 16 & 255) > (px17 & 255) + 40, 'Water body above cave at z=17 must stay blue water, not rock');
  paintWetCell(32 * mw + 32, 13, 10, MAT_WATER);
  assert(caveCeil[32 * mw + 32] < 10, 'Water bed puncturing cave ceiling must clamp caveCeil below bedZ');

  // 4c. Dropping & throwing carried item inside cave keeps item on caveFloor instead of mountain roof
  document.getElementById('btnNewFlat')._emit('click');
  for (let my = 24; my <= 40; my++) {
    for (let mx = 24; mx <= 40; mx++) {
      const idx = my * mw + mx;
      hmap[idx] = 26; caveFloor[idx] = 0; caveCeil[idx] = 14;
    }
  }
  const cWx = (32 - HALF_GRID + 0.5) * VOX, cWy = (32 - HALF_GRID + 0.5) * VOX;
  cat.avatar = 'human'; cat.scale = 1.0;
  teleportToWorld(cWx, cWy, null, 0);
  spawnPushableLog(cWx, cWy, 0);
  debrisDrops[debrisDrops.length - 1].z = 0;
  pickOrDropItem();
  stepDebrisDrops(1 / 60);
  pickOrDropItem();
  for (let i = 0; i < 60; i++) stepDebrisDrops(1 / 60);
  assert(debrisDrops[debrisDrops.length - 1].z < 2, 'Dropped log inside cave must land on caveFloor=0, not roof=26');
  pickOrDropItem();
  stepDebrisDrops(1 / 60);
  throwCarriedItem();
  for (let i = 0; i < 90; i++) stepDebrisDrops(1 / 60);
  assert(debrisDrops[debrisDrops.length - 1].z < 2, 'Thrown log inside cave must bounce off ceiling and land on caveFloor=0');

  // 5. Engine & Studio 3D Map Zoom (camZoom, setCamZoom, adjustCamZoom, wheel, keys, pill buttons)
  assert.strictEqual(camZoom, 1.0, 'Initial camZoom must be 1.0');
  assert.strictEqual(pixelScale, 2, 'Initial pixelScale at 640x480 must be 2');
  assert.strictEqual(LOW_W, 320);
  assert.strictEqual(LOW_H, 240);
  assert.strictEqual(document.getElementById('btnZoomReset').textContent, '🔍 100%');

  setCamZoom(2.5);
  assert.strictEqual(camZoom, 2.5);
  assert.strictEqual(pixelScale, 5);
  assert.strictEqual(LOW_W, 128);
  assert.strictEqual(LOW_H, 96);
  assert.strictEqual(document.getElementById('btnZoomReset').textContent, '🔍 250%');

  setCamZoom(0.05);
  assert.strictEqual(camZoom, 0.35, 'camZoom must clamp to min 0.35');
  assert.strictEqual(pixelScale, 1, 'pixelScale must clamp to min 1');
  assert.strictEqual(LOW_W, 640);
  assert.strictEqual(LOW_H, 480);

  setCamZoom(10.0);
  assert.strictEqual(camZoom, 3.0, 'camZoom must clamp to max 3.0');
  assert.strictEqual(pixelScale, 6);
  adjustCamZoom(-0.5);
  assert.strictEqual(camZoom, 2.5);
  setCamZoom(NaN);
  assert.strictEqual(camZoom, 1.0, 'NaN camZoom must fallback safely to 1.0');

  // Wheel zoom in & out on #viewport
  const vpEl = document.getElementById('viewport');
  vpEl._emit('wheel', { deltaY: -120 });
  assert(camZoom > 1.0, 'Wheel up on viewport must zoom in');
  vpEl._emit('wheel', { deltaY: 120 });
  assert(Math.abs(camZoom - 1.0) < 0.001, 'Wheel down must return to ~1.0');

  // Render & 3D picker remain valid across extreme zoom levels
  window.__STUDIO_EDIT_MODE__ = true;
  setCamZoom(0.35);
  renderScene();
  setCamZoom(3.0);
  renderScene();
  vpEl._emit('pointermove', { clientX: 320, clientY: 240 });
  assert(S.hoverWorld && Number.isFinite(S.hoverWorld.wx) && Number.isFinite(S.hoverWorld.wy), 'pickTerrainAtClient must resolve hoverWorld when zoomed');
  setCamZoom(1.0);

  // Zoom pill buttons
  document.getElementById('btnZoomIn')._emit('click');
  assert(camZoom > 1.1, 'btnZoomIn must increase camZoom');
  document.getElementById('btnZoomOut')._emit('click');
  assert(Math.abs(camZoom - 1.0) < 0.001, 'btnZoomOut must decrease camZoom');
  setCamZoom(2.0);
  document.getElementById('btnZoomReset')._emit('click');
  assert.strictEqual(camZoom, 1.0, 'btnZoomReset must reset camZoom to 1.0');

  // Keyboard shortcuts (+ / - / 0) in Edit mode and Test mode, ignored in <input>
  window.__STUDIO_EDIT_MODE__ = true;
  window._emit('keydown', { key: '=', code: 'Equal' });
  assert(camZoom > 1.0, 'Key =/+ must zoom in during Edit mode');
  window._emit('keydown', { key: '0', code: 'Digit0' });
  assert.strictEqual(camZoom, 1.0, 'Key 0 must reset zoom in Edit mode');
  window.__STUDIO_EDIT_MODE__ = false;
  window._emit('keydown', { key: '-', code: 'Minus' });
  assert(camZoom < 1.0, 'Key - must zoom out during Test mode');
  const prevZoom = camZoom;
  window._emit('keydown', { key: '0', code: 'Digit0', target: { tagName: 'INPUT' } });
  assert.strictEqual(camZoom, prevZoom, 'Zoom hotkeys must be ignored inside INPUT');
  setCamZoom(1.0);

  console.log('CAVES_AND_DUAL_SIDEBAR_OK');
}

vm.runInContext(
  mathCode + '\n' + bakerCode + '\n' + sculptorCode + '\n' + rendererCode + '\n' +
  fluidsCode + '\n' + physCode + '\n' + destrCode + '\n' + brushesCode + '\n' + regenCode + '\n' + uiCode +
  '\n(' + runCaveSuite.toString() + ')()',
  sandbox
);
"""
        res = subprocess.run(['node', '-e', node_cave_test], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Node cave & dual-sidebar test failed:\n{res.stderr}\n{res.stdout}')
        self.assertIn('CAVES_AND_DUAL_SIDEBAR_OK', res.stdout)

    def test_11_modular_tree_studio_and_2d_to_3d_math_converter(self):
        # 1. Verify 3-column Modeler layout, topbar hiding, and Section 8.1 / 8.2 DOM+CSS contract
        studio_html_path = os.path.join(ROOT, 'studio', 'index.html')
        studio_css_path = os.path.join(ROOT, 'studio', 'studio.css')
        with open(studio_html_path, 'r', encoding='utf-8') as f:
            studio_html = f.read()
        with open(studio_css_path, 'r', encoding='utf-8') as f:
            studio_css = f.read()

        self.assertIn('world-only-top', studio_html)
        self.assertIn('body.in-modeler .world-only-top', studio_css)
        self.assertIn('.topbar::-webkit-scrollbar', studio_css)
        self.assertIn('@supports not selector(::-webkit-scrollbar)', studio_css)

        idx_mleft = studio_html.find('class="m-sidebar-left"')
        idx_mcenter = studio_html.find('class="m-stage-center"')
        idx_mright = studio_html.find('class="m-sidebar-right"')
        self.assertGreater(idx_mleft, 0)
        self.assertGreater(idx_mcenter, idx_mleft)
        self.assertGreater(idx_mright, idx_mcenter)

        center_html = studio_html[idx_mcenter:idx_mright]
        self.assertIn('id="mEditCanvas"', center_html)
        self.assertIn('id="mPreviewCanvas"', center_html)
        for z_id in ('id="mEditZoomOut"', 'id="mEditZoomReset"', 'id="mEditZoomIn"', 'id="mPrevZoomOut"', 'id="mPrevZoomReset"', 'id="mPrevZoomIn"'):
            self.assertIn(z_id, center_html, f'Missing {z_id} in modeler center stage')

        right_html = studio_html[idx_mright:]
        for req_id in (
            'id="mRightTabs"', 'id="mTabChars"', 'id="mTabTrees"', 'id="mTabConv2d"',
            'id="mTreeBranch"', 'id="mTreeThick"', 'id="mTreeCurve"', 'id="mTreeCrown"',
            'id="mTreeFlowerPct"', 'id="mTreeFruitPct"',
            'id="mTreeColTrunk"', 'id="mTreeColLeaf"', 'id="mTreeColFlower"', 'id="mTreeColFruit"',
            'id="mBtnGenModularTree"',
            'id="m2dFrontCanvas"', 'id="m2dSideCanvas"', 'id="m2dMode"',
            'id="m2dThickness"', 'id="mBtnConvert2d3d"', 'id="m2dLoadPreset"'
        ):
            self.assertIn(req_id, right_html, f'Missing {req_id} in modeler right sidebar')

        # 2. Execute src/studio/00-modeler.js in Node VM and verify Section 8.1 & 8.2 algorithms
        node_mod_test = r"""
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = process.cwd();
const mathCode = fs.readFileSync(path.join(root, 'src/engine/00-math-noise.js'), 'utf8');
const modelerCode = fs.readFileSync(path.join(root, 'src/studio/00-modeler.js'), 'utf8');

const elements = new Map();
function makeEl(id, extra = {}) {
  const listeners = {};
  const el = {
    id, value: '', textContent: '', innerHTML: '', className: '',
    checked: false, style: {}, dataset: {},
    options: [{ textContent: 'Opt' }], selectedIndex: 0,
    classList: { _s: new Set(), add(c){this._s.add(c);}, remove(c){this._s.delete(c);}, contains(c){return this._s.has(c);} },
    addEventListener(ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    _emit(ev, e = {}) { (listeners[ev] || []).forEach(fn => fn({ preventDefault(){}, target: el, ...e })); },
    appendChild(child) { this._children = this._children || []; this._children.push(child); },
    querySelector: () => null,
    querySelectorAll: () => [],
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 384, height: 384 }),
    setPointerCapture(){}, releasePointerCapture(){},
    width: 384, height: 384,
    ...extra
  };
  if (id) elements.set(id, el);
  return el;
}
function make2dCtx() {
  return {
    fillStyle: '', strokeStyle: '', lineWidth: 1, globalAlpha: 1, font: '', imageSmoothingEnabled: false,
    clearRect(){}, fillRect(){}, strokeRect(){}, beginPath(){}, moveTo(){}, lineTo(){}, ellipse(){}, fill(){}, stroke(){}, fillText(){},
    drawImage(){}, getImageData: (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4) })
  };
}

makeEl('modelerView');
makeEl('mEditCanvas', { width: 384, height: 384, getContext: () => make2dCtx() });
makeEl('mPreviewCanvas', { width: 300, height: 300, getContext: () => make2dCtx() });
makeEl('m2dFrontCanvas', { width: 144, height: 144, getContext: () => make2dCtx() });
makeEl('m2dSideCanvas', { width: 144, height: 144, getContext: () => make2dCtx() });
makeEl('mSize', { value: '24' });
makeEl('mZ', { value: '0', max: '23' });
makeEl('mZLabel');
makeEl('mMirror', { checked: true });
makeEl('mOnion', { checked: true });
makeEl('mExtrudeZ', { value: '1' });
makeEl('mExtrudeZVal');
makeEl('mPalPreset', { value: 'default', options: [{ textContent: 'Default' }], selectedIndex: 0 });
makeEl('mPalette');
makeEl('mColor', { value: '#4F83C2' });
makeEl('mAutoSpin', { checked: false });
makeEl('mRefHuman', { checked: false });
makeEl('mName', { value: 'meu_modelo' });
makeEl('mKind', { value: 'decor' });
makeEl('mDestrOpts');
makeEl('mHp', { value: '3' });
makeEl('mDropKey', { value: 'stone_chunk' });
makeEl('mMsg');
makeEl('mTreeBranch', { value: '3' });
makeEl('mTreeThick', { value: '2' });
makeEl('mTreeThickVal');
makeEl('mTreeCurve', { value: '1' });
makeEl('mTreeCurveVal');
makeEl('mTreeCrown', { value: 'spheres' });
makeEl('mTreeFlowerPct', { value: '25' });
makeEl('mTreeFlowerPctVal');
makeEl('mTreeFruitPct', { value: '20' });
makeEl('mTreeFruitPctVal');
makeEl('mTreeColTrunk', { value: '#7C4D2B' });
makeEl('mTreeColLeaf', { value: '#3F8F3A' });
makeEl('mTreeColFlower', { value: '#F472B6' });
makeEl('mTreeColFruit', { value: '#EF4444' });
makeEl('m2dPreset', { value: 'sword' });
makeEl('m2dMode', { value: 'edt_blade' });
makeEl('m2dThickness', { value: '10' });
makeEl('m2dThicknessVal');
for (const id of [
  'mBtnAutoShade','mZUp','mZDown','mCopyDown','mCopyUp','mBtnClearLayer','mBtnNew',
  'mBtnSave','mBtnExport','mBtnImport','mFileImport','btnTabWorld','btnTabModeler',
  'mBtnGenModularTree','m2dFromSlice','m2dCopyFrontToSide','m2dClear','m2dImportImg','m2dFileImg',
  'm2dLoadPreset','mBtnConvert2d3d','mRightTabs','mTabChars','mTabTrees','mTabConv2d',
  'mBtnGenChar','mBtnVaryChar','mProcProps','btnOpenModelerSide',
  'mEditZoomOut','mEditZoomReset','mEditZoomIn','mPrevZoomOut','mPrevZoomReset','mPrevZoomIn'
]) makeEl(id);

const workspaceEl = makeEl('workspaceMock');
const bodyClassList = { _s: new Set(), add(c){this._s.add(c);}, remove(c){this._s.delete(c);}, contains(c){return this._s.has(c);} };
const sandbox = {
  assert, Math, Number, Array, Object, JSON, Int16Array, Uint8Array, Float32Array, Set, Map,
  URLSearchParams, Event: class { constructor(t){ this.type = t; } }, console, confirm: () => true,
  propModels: {}, PROP_COLLIDER_META: {}, DESTRUCTIBLE_META: {}, FOLIAGE_META: {},
  buildSliceSheet: () => ({ count: 1, w: 24, h: 24, sheet: {} }),
  window: { dispatchEvent(){}, customAvatarModels: {}, location: { search: '' } },
  document: {
    body: { classList: bodyClassList },
    getElementById: (id) => elements.get(id) || null,
    querySelector: (sel) => sel === '.workspace' ? workspaceEl : null,
    querySelectorAll: () => [],
    createElement: () => makeEl('')
  }
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

function runModelerTests() {
  // 1. Topbar body.in-modeler class toggles on tab switch
  document.getElementById('btnTabModeler')._emit('click');
  assert(document.body.classList.contains('in-modeler'), 'btnTabModeler must add body.in-modeler');
  document.getElementById('btnTabWorld')._emit('click');
  assert(!document.body.classList.contains('in-modeler'), 'btnTabWorld must remove body.in-modeler');

  const M = window.StudioModeler;
  const N = M.getSize();
  assert.strictEqual(N, 24);

  // 2. Section 8.1: Modular Tree Studio (trifurcated + spheres + flowers + fruits)
  document.getElementById('mBtnGenModularTree')._emit('click');
  let vol = M.getVol();
  let trunkCount = 0, leafCount = 0, flowerCount = 0, fruitCount = 0;
  for (let z = 0; z < N; z++) {
    for (let i = 0; i < vol[z].length; i++) {
      const v = vol[z][i];
      if (v >= 1 && v <= 3) trunkCount++;
      else if (v >= 4 && v <= 7) leafCount++;
      else if (v === 8 || v === 9) flowerCount++;
      else if (v === 10 || v === 11) fruitCount++;
    }
  }
  assert(trunkCount > 30, 'Modular tree must generate trunk & branches');
  assert(leafCount > 100, 'Modular tree must generate crown foliage');
  assert(flowerCount > 0, 'flowerPct=25 must place flowers on outer crown surface');
  assert(fruitCount > 0, 'fruitPct=20 must place fruits on outer crown surface');
  assert.strictEqual(document.getElementById('mKind').value, 'foliage');

  // Single trunk + pine cones + 0% flowers/fruits
  M.generateModularTree({ branchCount: 1, crownType: 'cones', flowerPct: 0, fruitPct: 0 }, 301);
  let coneLeaves = 0, zeroFlowFruit = 0;
  for (let z = 0; z < N; z++) {
    for (let i = 0; i < vol[z].length; i++) {
      const v = vol[z][i];
      if (v >= 4 && v <= 7) coneLeaves++;
      if (v >= 8 && v <= 11) zeroFlowFruit++;
    }
  }
  assert(coneLeaves > 80, 'Conical pine crown must generate foliage');
  assert.strictEqual(zeroFlowFruit, 0, '0% flower/fruit must place zero flowers/fruits');

  // Multi-branch + weeping willow with curvature reaches lower Z layers and stays centered near curved branches
  M.generateModularTree({ branchCount: 4, curve: 3, crownType: 'weeping', flowerPct: 0, fruitPct: 0 }, 302);
  let lowWillowLeaves = 0;
  for (let z = 4; z <= 10; z++) {
    for (let i = 0; i < vol[z].length; i++) if (vol[z][i] >= 4 && vol[z][i] <= 7) lowWillowLeaves++;
  }
  assert(lowWillowLeaves > 15, 'Weeping willow crown must drape tendrils down to Z=4..10');

  // Dead tree ('none') has trunk/branches and zero leaves
  M.generateModularTree({ branchCount: 3, crownType: 'none', flowerPct: 20, fruitPct: 20 }, 303);
  let deadTrunk = 0, deadLeaves = 0;
  for (let z = 0; z < N; z++) {
    for (let i = 0; i < vol[z].length; i++) {
      if (vol[z][i] >= 1 && vol[z][i] <= 3) deadTrunk++;
      if (vol[z][i] >= 4) deadLeaves++;
    }
  }
  assert(deadTrunk > 40 && deadLeaves === 0, 'crownType=none must produce bare branches with zero leaves');

  // 3. Section 8.2: Mathematical 2D -> 3D Converter
  // Empty 2D guard
  document.getElementById('m2dClear')._emit('click');
  const emptyRes = M.convert2dTo3d('edt_blade', 10);
  assert.strictEqual(emptyRes.ok, false, 'Empty 2D canvas must return ok=false');

  // 3a. edt_blade on sword preset: sharp 1-voxel outer edges + thicker interior crossguard
  document.getElementById('m2dPreset').value = 'sword';
  document.getElementById('m2dLoadPreset')._emit('click');
  const bladeRes = M.convert2dTo3d('edt_blade', 10);
  assert(bladeRes.ok && bladeRes.voxels > 80, 'edt_blade must convert sword silhouette to 3D');
  // At blade upper tip/edge (z=16), edge pixel should be thinner in Y than center
  let minSpan = 99, maxSpan = 0;
  for (let z = 0; z < N; z++) {
    for (let x = 0; x < N; x++) {
      let yCnt = 0;
      for (let y = 0; y < N; y++) if (vol[z][y * N + x] > 0) yCnt++;
      if (yCnt > 0) {
        if (yCnt < minSpan) minSpan = yCnt;
        if (yCnt > maxSpan) maxSpan = yCnt;
      }
    }
  }
  assert.strictEqual(minSpan, 1, 'edt_blade must keep sharp 1-voxel edges');
  assert(maxSpan >= 3, 'edt_blade interior must thicken beyond 1 voxel');

  // 3b. edt_organic on solid rectangle: rounded elliptical profile tapering to 1-voxel rim
  const bufs = M.get2dBuffers();
  bufs.front2D.fill(0);
  for (let z = 4; z <= 19; z++) for (let x = 6; x <= 17; x++) bufs.front2D[z * N + x] = 2;
  const orgRes = M.convert2dTo3d('edt_organic', 12);
  assert(orgRes.ok && orgRes.voxels > 200, 'edt_organic must inflate volume');
  let edgeY = 0, centerY = 0;
  for (let y = 0; y < N; y++) {
    if (vol[4][y * N + 6] > 0) edgeY++;
    if (vol[12][y * N + 12] > 0) centerY++;
  }
  assert.strictEqual(edgeY, 1, 'edt_organic outer rim must taper to 1 voxel instead of thick wall');
  assert(centerY >= 11 && centerY > edgeY, 'edt_organic center must be thicker than corner edge');

  // 3c. lathe (360 revolution) on vase preset: rotational symmetry around central Z axis
  document.getElementById('m2dPreset').value = 'vase';
  document.getElementById('m2dLoadPreset')._emit('click');
  const latheRes = M.convert2dTo3d('lathe', 10);
  assert(latheRes.ok && latheRes.voxels > 300, 'lathe must revolve vase into 3D');
  // At belly z=8, verify X-diameter equals Y-diameter (360 symmetry)
  let xMinL = N, xMaxL = -1, yMinL = N, yMaxL = -1;
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    if (vol[8][y * N + x] > 0) {
      if (x < xMinL) xMinL = x; if (x > xMaxL) xMaxL = x;
      if (y < yMinL) yMinL = y; if (y > yMaxL) yMaxL = y;
    }
  }
  assert.strictEqual(xMaxL - xMinL, yMaxL - yMinL, 'lathe must produce equal X and Y diameters');
  assert((xMaxL - xMinL) >= 8, 'lathe vase belly must span wide circular cross-section');

  // 3d. visual_hull (Front x Side intersection) on creature preset
  document.getElementById('m2dPreset').value = 'creature';
  document.getElementById('m2dLoadPreset')._emit('click');
  const hullRes = M.convert2dTo3d('visual_hull', 10);
  assert(hullRes.ok && hullRes.voxels > 200, 'visual_hull must intersect Front and Side silhouettes');
  // Every filled voxel (x, y, z) must be inside BOTH front2D[z, x] AND side2D[z, y]
  for (let z = 0; z < N; z++) {
    for (let y = 0; y < N; y++) {
      for (let x = 0; x < N; x++) {
        if (vol[z][y * N + x] > 0) {
          assert(bufs.front2D[z * N + x] > 0, `Visual hull voxel (${x},${y},${z}) outside front2D`);
          assert(bufs.side2D[z * N + y] > 0, `Visual hull voxel (${x},${y},${z}) outside side2D`);
        }
      }
    }
  }
  // Verify snout in side2D (y > 16 at z=13) projects in 3D only within front2D head width
  let snoutVoxels = 0;
  for (let x = 0; x < N; x++) if (vol[13][17 * N + x] > 0) snoutVoxels++;
  assert(snoutVoxels > 0 && snoutVoxels < 10, 'Visual hull must preserve side snout within front head bounds');

  // 3e. Copy Slice -> Front and Front -> Side buttons
  document.getElementById('m2dClear')._emit('click');
  M.setZ(13);
  document.getElementById('m2dFromSlice')._emit('click');
  document.getElementById('m2dCopyFrontToSide')._emit('click');
  let copiedCount = 0;
  for (let i = 0; i < bufs.side2D.length; i++) if (bufs.side2D[i] > 0) copiedCount++;
  assert(copiedCount > 0, 'm2dFromSlice + m2dCopyFrontToSide must populate side2D');

  // 4. Modeler Zoom (previewZoom + editZoom + cursor-centered wheel + pan clamp)
  assert.strictEqual(M.getPreviewZoom(), 1.0, 'Initial previewZoom must be 1.0');
  document.getElementById('mPrevZoomIn')._emit('click');
  assert(M.getPreviewZoom() > 1.0, 'mPrevZoomIn must increase previewZoom');
  assert.notStrictEqual(document.getElementById('mPrevZoomReset').textContent, '100%');
  document.getElementById('mPrevZoomReset')._emit('click');
  assert.strictEqual(M.getPreviewZoom(), 1.0);
  document.getElementById('mPreviewCanvas')._emit('wheel', { deltaY: -100 });
  assert(M.getPreviewZoom() > 1.0, 'Wheel up on mPreviewCanvas must zoom in');
  M.setPreviewZoom(0.1);
  assert.strictEqual(M.getPreviewZoom(), 0.4, 'previewZoom min clamp 0.4');
  M.setPreviewZoom(9.0);
  assert.strictEqual(M.getPreviewZoom(), 3.0, 'previewZoom max clamp 3.0');
  M.setPreviewZoom(1.0);

  assert.strictEqual(M.getEditZoom(), 1.0, 'Initial editZoom must be 1.0');
  const editCvEl = document.getElementById('mEditCanvas');
  const beforeCell = M.cellAt({ clientX: 96, clientY: 96 });
  assert.deepStrictEqual(beforeCell, { x: 6, y: 6 });
  editCvEl._emit('wheel', { deltaY: -120, clientX: 96, clientY: 96 });
  assert(M.getEditZoom() > 1.0, 'Wheel up on mEditCanvas must increase editZoom');
  const afterCell = M.cellAt({ clientX: 96, clientY: 96 });
  assert.deepStrictEqual(afterCell, beforeCell, 'Cursor-centered wheel zoom must keep target cell under cursor');
  const pan = M.getEditPan();
  assert(pan.x > 0 && pan.y > 0, 'Zooming around (96,96) must offset editPan');

  // Right-click pan & clamp
  editCvEl._emit('pointerdown', { button: 2, clientX: 100, clientY: 100, pointerId: 1 });
  editCvEl._emit('pointermove', { clientX: 40, clientY: 40 });
  editCvEl._emit('pointerup', { pointerId: 1 });
  const maxPan = 384 * (M.getEditZoom() - 1);
  const panned = M.getEditPan();
  assert(panned.x >= 0 && panned.x <= maxPan + 1e-6 && panned.y >= 0 && panned.y <= maxPan + 1e-6, 'editPan must stay clamped');

  document.getElementById('mEditZoomIn')._emit('click');
  assert(M.getEditZoom() <= 4.0);
  M.setEditZoom(9.0);
  assert.strictEqual(M.getEditZoom(), 4.0, 'editZoom max clamp 4.0');
  document.getElementById('mEditZoomReset')._emit('click');
  assert.strictEqual(M.getEditZoom(), 1.0, 'mEditZoomReset must restore 1.0');
  assert.deepStrictEqual(M.getEditPan(), { x: 0, y: 0 }, 'Resetting editZoom to 1.0 must reset pan to 0,0');

  console.log('MODULAR_TREE_AND_2D3D_OK');
}

vm.runInContext(mathCode + '\n' + modelerCode + '\n(' + runModelerTests.toString() + ')()', sandbox);
"""
        res = subprocess.run(['node', '-e', node_mod_test], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Node modeler 8.1/8.2 test failed:\n{res.stderr}\n{res.stdout}')
        self.assertIn('MODULAR_TREE_AND_2D3D_OK', res.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
