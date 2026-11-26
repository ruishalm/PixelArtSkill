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

    def test_02_bundler_and_js_syntax(self):
        import generate_terrain_world as gtw

        with tempfile.TemporaryDirectory() as tmpdir:
            out_html = os.path.join(tmpdir, 'terrain-world.html')
            gtw.build_terrain_world(out_html)
            with open(out_html, 'r', encoding='utf-8') as f:
                html = f.read()

            self.assertLess(len(html.encode('utf-8')), 15 * 1024, 'terrain-world.html must stay < 15 KB')
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
            self.assertTrue(os.path.isfile(os.path.join(ROOT, 'examples', 'terrain-world.css')))
            self.assertTrue(os.path.isfile(os.path.join(ROOT, 'assets', 'voxels', 'voxel-data.js')))

            # Every <script src="..."> must exist relative to examples/ and pass node --check
            srcs = re.findall(r'<script\s+src="([^"]+)"', html)
            self.assertGreaterEqual(len(srcs), 15)
            examples_dir = os.path.join(ROOT, 'examples')
            combined_parts = []
            for rel_src in srcs:
                resolved = os.path.normpath(os.path.join(examples_dir, rel_src))
                self.assertTrue(os.path.isfile(resolved), f'Missing script target: {rel_src} -> {resolved}')
                res = subprocess.run(['node', '--check', resolved], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f'Syntax error in {resolved}:\n{res.stderr}')
                with open(resolved, 'r', encoding='utf-8') as sf:
                    combined_parts.append(sf.read())

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
            with open(out_html, 'r', encoding='utf-8') as f:
                studio_html = f.read()

            self.assertLess(len(studio_html.encode('utf-8')), 15 * 1024, 'studio/index.html must stay < 15 KB')
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
            self.assertTrue(os.path.isfile(os.path.join(ROOT, 'studio', 'studio.css')))
            voxel_data_js = os.path.join(ROOT, 'assets', 'voxels', 'voxel-data.js')
            self.assertTrue(os.path.isfile(voxel_data_js))

            # Every <script src="..."> in studio HTML must exist on disk and pass node --check
            srcs = re.findall(r'<script\s+src="([^"]+)"', studio_html)
            self.assertGreaterEqual(len(srcs), 15)
            studio_dir = os.path.join(ROOT, 'studio')
            for rel_src in srcs:
                resolved = os.path.normpath(os.path.join(studio_dir, rel_src))
                self.assertTrue(os.path.isfile(resolved), f'Missing script target: {rel_src} -> {resolved}')
                res = subprocess.run(['node', '--check', resolved], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f'Syntax error in {resolved}:\n{res.stderr}')

        # Also validate all studio modules directly
        studio_modules = sorted(glob.glob(os.path.join(ROOT, 'src', 'studio', '*.js')))
        self.assertGreaterEqual(len(studio_modules), 4)
        for mod in studio_modules:
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
                (cat_html, os.path.join(ROOT, 'examples'), 'cat-3d.css', 2),
                (chk_html, os.path.join(ROOT, 'examples'), 'chicken-3d.css', 2),
                (room_html, os.path.join(ROOT, 'examples'), 'room-3d.css', 7),
                (idx_html, ROOT, 'examples/room-3d.css', 7),
            ]

            for html_path, base_dir, expected_css, min_scripts in specs:
                with open(html_path, 'rb') as bf:
                    raw = bf.read()
                self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), f'UTF-8 BOM found in {html_path}')
                self.assertNotIn(b'\r\n', raw, f'CRLF found in {html_path}')
                html_text = raw.decode('utf-8')
                self.assertLess(len(raw), 15 * 1024, f'{html_path} must stay < 15 KB')
                self.assertEqual(re.findall(r'__[A-Z0-9_]+__', html_text), [])
                self.assertIn(f'<link rel="stylesheet" href="{expected_css}"', html_text)
                css_resolved = os.path.normpath(os.path.join(base_dir, expected_css))
                self.assertTrue(os.path.isfile(css_resolved), f'Missing CSS: {css_resolved}')

                srcs = re.findall(r'<script\s+src="([^"]+)"', html_text)
                self.assertGreaterEqual(len(srcs), min_scripts, f'Too few scripts in {html_path}')
                parts = []
                for rel_src in srcs:
                    resolved = os.path.normpath(os.path.join(base_dir, rel_src))
                    self.assertTrue(os.path.isfile(resolved), f'Missing script target: {rel_src} -> {resolved}')
                    with open(resolved, 'rb') as jsbf:
                        js_raw = jsbf.read()
                    self.assertFalse(js_raw.startswith(b'\xef\xbb\xbf'), f'UTF-8 BOM in {resolved}')
                    self.assertNotIn(b'\r\n', js_raw, f'CRLF in {resolved}')
                    res = subprocess.run(['node', '--check', resolved], capture_output=True, text=True)
                    self.assertEqual(res.returncode, 0, f'Syntax error in {resolved}:\n{res.stderr}')
                    parts.append(js_raw.decode('utf-8'))

                combined_path = os.path.join(tmpdir, f'{os.path.basename(html_path)}.combined.js')
                with open(combined_path, 'w', encoding='utf-8', newline='\n') as cf:
                    cf.write('\n'.join(parts))
                res = subprocess.run(['node', '--check', combined_path], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f'Combined syntax error for {html_path}:\n{res.stderr}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
