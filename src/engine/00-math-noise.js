    // =========================================================================
    // ENGINE: PRNG DETERMINÍSTICO, RUÍDO 2D & PRIMITIVAS MATEMÁTICAS
    // =========================================================================
    const DEFAULT_WORLD_SEED = 1337;
    const _rawSeedParam = new URLSearchParams(window.location.search).get('seed');
    const _parsedSeed = _rawSeedParam !== null ? parseInt(_rawSeedParam, 10) : NaN;
    const WORLD_SEED = Number.isFinite(_parsedSeed) ? (_parsedSeed >>> 0) : DEFAULT_WORLD_SEED;
    const SEED_HASH_MIX = WORLD_SEED === DEFAULT_WORLD_SEED
      ? 0
      : (Math.imul(WORLD_SEED ^ (WORLD_SEED >>> 16), 2246822519) | 0);

    function mulberry32(seed) {
      let t = seed >>> 0;
      return function() {
        t = (t + 0x6D2B79F5) | 0;
        let r = Math.imul(t ^ (t >>> 15), 1 | t);
        r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
        return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
      };
    }
    const worldRand = mulberry32(WORLD_SEED);

    function hash2i(ix, iy) {
      let n = (Math.imul(ix, 374761393) + Math.imul(iy, 668265263) + SEED_HASH_MIX) | 0;
      n = Math.imul(n ^ (n >>> 13), 1274126177);
      return ((n ^ (n >>> 16)) >>> 0) * 2.3283064365386963e-10;
    }

    function valueNoise2d(x, y) {
      const ix = Math.floor(x);
      const iy = Math.floor(y);
      const fx = x - ix;
      const fy = y - iy;
      const u = fx * fx * (3 - 2 * fx);
      const v = fy * fy * (3 - 2 * fy);
      const a = hash2i(ix, iy);
      const b = hash2i(ix + 1, iy);
      const c = hash2i(ix, iy + 1);
      const d = hash2i(ix + 1, iy + 1);
      return (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v) * 2 - 1;
    }

    function fbm2d(x, y) {
      let sum = 0;
      let amp = 0.55;
      let freq = 1.0;
      for (let i = 0; i < 3; i++) {
        sum += amp * valueNoise2d(x * freq, y * freq);
        freq *= 2.05;
        amp *= 0.45;
      }
      return sum;
    }

    function fbm2dFast(x, y) {
      return 0.60 * valueNoise2d(x, y) + 0.30 * valueNoise2d(x * 2.05, y * 2.05);
    }

    const _wp = { x: 0, y: 0 };
    function warp2d(wx, wy, freq = 0.012, amp = 24) {
      const qx = fbm2dFast(wx * freq + 5.2, wy * freq + 1.3);
      const qy = fbm2dFast(wx * freq + 1.7, wy * freq + 9.2);
      const f2 = freq * 1.35;
      const rx = valueNoise2d((wx + qx * amp) * f2 + 8.3, (wy + qy * amp) * f2 + 2.8);
      const ry = valueNoise2d((wx + qx * amp) * f2 + 1.2, (wy + qy * amp) * f2 + 6.4);
      _wp.x = wx + rx * amp;
      _wp.y = wy + ry * amp;
      return _wp;
    }

    function smax(a, b, k) {
      if (k <= 0.001) return Math.max(a, b);
      const h = Math.max(0, Math.min(1, 0.5 + 0.5 * (b - a) / k));
      return a + (b - a) * h + k * h * (1 - h);
    }

    function smin(a, b, k) {
      return -smax(-a, -b, k);
    }

    function ridgedFbm(x, y, octaves = 3) {
      let sum = 0, amp = 0.55, freq = 1.0, norm = 0;
      for (let i = 0; i < octaves; i++) {
        const n = 1.0 - Math.abs(valueNoise2d(x * freq, y * freq));
        sum += n * n * amp;
        norm += amp;
        freq *= 2.05;
        amp *= 0.48;
      }
      return sum / norm;
    }

    function rockTerrace(h, step = 12, strength = 0.5, wx = 0, wy = 0) {
      if (h <= 2 || step <= 0 || strength <= 0) return h;
      const s = step * (1 + fbm2dFast(wx * 0.014 + 3.1, wy * 0.014 - 4.7) * 0.22);
      const u = h / s;
      const base = Math.floor(u);
      const frac = u - base;
      const smooth = frac * frac * (3 - 2 * frac);
      const terraced = (base + smooth * smooth) * s;
      return h + (terraced - h) * strength;
    }

    function segDistAndT(px, py, ax, ay, bx, by) {
      const vx = bx - ax, vy = by - ay;
      const wx = px - ax, wy = py - ay;
      const lenSq = vx * vx + vy * vy;
      const t = lenSq > 0 ? Math.max(0, Math.min(1, (wx * vx + wy * vy) / lenSq)) : 0;
      const cx = ax + vx * t, cy = ay + vy * t;
      return { d: Math.hypot(px - cx, py - cy), t };
    }

