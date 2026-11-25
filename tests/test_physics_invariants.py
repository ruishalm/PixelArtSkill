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

            # Zero unresolved placeholders
            for token in (
                '__TERRAIN_JS_BUNDLE__',
                '__CAT_SLICES__',
                '__HATS_PACK__',
                '__CHICKEN_DATA__',
                '__PROPS_PACK__',
            ):
                self.assertNotIn(token, html)

            # Extract <script> block and validate full bundle syntax with Node
            m = re.search(r'<script>\n(.*?)\n  </script>', html, re.S)
            self.assertIsNotNone(m, 'Missing <script> block in bundled HTML')
            js_path = os.path.join(tmpdir, 'bundle.js')
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(m.group(1))

            res = subprocess.run(['node', '--check', js_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Bundled JS syntax error:\n{res.stderr}')

        # Also check every individual module in src/terrain-world/*.js
        modules = sorted(glob.glob(os.path.join(ROOT, 'src', 'terrain-world', '*.js')))
        self.assertEqual(len(modules), 6)
        for mod in modules:
            res = subprocess.run(['node', '--check', mod], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Syntax error in {mod}:\n{res.stderr}')

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

console.log('ALL_NODE_PHYSICS_INVARIANTS_OK');
"""
        res = subprocess.run(['node', '-e', node_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Node physics test failed:\n{res.stderr}')
        self.assertIn('ALL_NODE_PHYSICS_INVARIANTS_OK', res.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
