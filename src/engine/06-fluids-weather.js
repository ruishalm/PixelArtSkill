    // =========================================================================
    // ENGINE: FLUIDOS 2.5D, GRANULAR, VERLET & TERMODINÂMICA
    // =========================================================================
    // =========================================================================
    // 8B. FLUIDOS 2.5D: WINDFIELD + WATERFLOW (DRAIN SINK) + WAVEBUFFER
    // =========================================================================
    const ENGINE_TUNING = {
      windMul: 1.0,
      fireCool: 0.22,
      sandTalus: 2,
      rockTalus: 3
    };
    const FLOW_GRID_STEP = 8;
    const FLOW_GRID_W = Math.ceil(WORLD_CFG.gridW / FLOW_GRID_STEP); // 135x135 sobre 1080x1080
    const customWindVx = new Float32Array(FLOW_GRID_W * FLOW_GRID_W);
    const customWindVy = new Float32Array(FLOW_GRID_W * FLOW_GRID_W);
    const customFlowVx = new Float32Array(FLOW_GRID_W * FLOW_GRID_W);
    const customFlowVy = new Float32Array(FLOW_GRID_W * FLOW_GRID_W);

    function samplePaintedVector(arrVx, arrVy, wx, wy) {
      const gx = (wx / VOX + HALF_GRID) / FLOW_GRID_STEP;
      const gy = (wy / VOX + HALF_GRID) / FLOW_GRID_STEP;
      if (gx < 0 || gy < 0 || gx >= FLOW_GRID_W - 1 || gy >= FLOW_GRID_W - 1) return null;
      const ix = gx | 0;
      const iy = gy | 0;
      const fx = gx - ix;
      const fy = gy - iy;
      const i00 = iy * FLOW_GRID_W + ix;
      const i10 = i00 + 1;
      const i01 = i00 + FLOW_GRID_W;
      const i11 = i01 + 1;
      const vx = (arrVx[i00] * (1 - fx) + arrVx[i10] * fx) * (1 - fy) + (arrVx[i01] * (1 - fx) + arrVx[i11] * fx) * fy;
      const vy = (arrVy[i00] * (1 - fx) + arrVy[i10] * fx) * (1 - fy) + (arrVy[i01] * (1 - fx) + arrVy[i11] * fx) * fy;
      return { vx, vy };
    }

    let fluidTime = 0;
    const windImpulses = [];
    function injectWindImpulse(wx, wy, vx, vy, r = 42, life = 0.75) {
      if (windImpulses.length >= 16) windImpulses.shift();
      windImpulses.push({ wx, wy, vx, vy, r, life, maxLife: life });
    }

    function sampleWind(wx, wy, t = fluidTime) {
      const gust = Math.sin((wx * 0.009 + wy * 0.006) - t * 2.1) * 0.55 + 0.55;
      const turb = fbm2dFast(wx * 0.008 - t * 0.25, wy * 0.008 + t * 0.14) * 0.45;
      let vx = 0.72 + gust * 0.52 + turb * 0.35;
      let vy = 0.34 + gust * 0.24 - turb * 0.25;

      const h = getHeightAt(wx, wy) || 0;
      const hL = getHeightAt(wx - 4, wy) ?? h;
      const hR = getHeightAt(wx + 4, wy) ?? h;
      const hU = getHeightAt(wx, wy - 4) ?? h;
      const hD = getHeightAt(wx, wy + 4) ?? h;
      const altBoost = 1 + Math.max(0, h) / 75;
      const windDotGrad = (hR - hL) * vx + (hD - hU) * vy;
      const shelter = windDotGrad < -6 ? 0.38 : 1.0;
      vx *= altBoost * shelter;
      vy *= altBoost * shelter;

      for (let i = 0; i < windImpulses.length; i++) {
        const imp = windImpulses[i];
        const dx = wx - imp.wx;
        const dy = wy - imp.wy;
        const d2 = dx * dx + dy * dy;
        const r2 = imp.r * imp.r;
        if (d2 < r2 * 6) {
          const w = Math.exp(-d2 / r2) * (imp.life / imp.maxLife);
          vx += imp.vx * w;
          vy += imp.vy * w;
        }
      }
      const paintedWind = samplePaintedVector(customWindVx, customWindVy, wx, wy);
      if (paintedWind) {
        vx += paintedWind.vx;
        vy += paintedWind.vy;
      }
      vx *= ENGINE_TUNING.windMul;
      vy *= ENGINE_TUNING.windMul;
      return { wx: vx, wy: vy, mag: Math.hypot(vx, vy) };
    }

    let cachedWaterObstacles = [];
    let cachedWaterObstaclesNoCat = [];

    function getActiveWaterObstacles(includeCat = true) {
      const obs = [];
      for (let i = 0; i < props.length; i++) {
        const p = props[i];
        if (p.destroyed || (p.destr && p.destr.chopped) || p.isDamBoulder) continue;
        const meta = PROP_COLLIDER_META[p.modelKey];
        const sr = Math.min(7, ((meta && meta.r) || 6) * 0.7);
        let inWet = false;
        const c0 = getCellAt(p.wx, p.wy);
        if (c0 && isWetMat(c0.mat)) {
          inWet = true;
        } else {
          const c1 = getCellAt(p.wx + sr, p.wy);
          const c2 = getCellAt(p.wx - sr, p.wy);
          const c3 = getCellAt(p.wx, p.wy + sr);
          const c4 = getCellAt(p.wx, p.wy - sr);
          if ((c1 && isWetMat(c1.mat)) || (c2 && isWetMat(c2.mat)) || (c3 && isWetMat(c3.mat)) || (c4 && isWetMat(c4.mat))) {
            inWet = true;
          }
        }
        if (!inWet) continue;
        let r = meta ? ((meta.r || Math.max(meta.halfW || 6, meta.halfD || 6)) * (p.scale || 1)) : 6.0;
        if (p.modelKey === 'ruin_pillar') r = Math.max(11.5, r);
        obs.push({ wx: p.wx, wy: p.wy, r });
      }
      for (let i = 0; i < debrisDrops.length; i++) {
        const dr = debrisDrops[i];
        if (dr.inWater) obs.push({ wx: dr.x, wy: dr.y, r: 5.2 });
      }
      if (includeCat) {
        const cc = getCellAt(cat.x, cat.y);
        const br = getBridgeAt(cat.x, cat.y);
        const onBr = br && cat.z >= getBridgeDeckZ(br, cat.x, cat.y) - AUTO_STEP_MAX - 1;
        if (cc && cc.mat === MAT_SHALLOW && !onBr && cat.onGround) {
          obs.push({ wx: cat.x, wy: cat.y, r: 8.2, isCat: true });
        }
      }
      return obs;
    }

    function refreshWaterObstaclesCache() {
      cachedWaterObstaclesNoCat = getActiveWaterObstacles(false);
      cachedWaterObstacles = cachedWaterObstaclesNoCat.slice();
      const cc = getCellAt(cat.x, cat.y);
      const br = getBridgeAt(cat.x, cat.y);
      const onBr = br && cat.z >= getBridgeDeckZ(br, cat.x, cat.y) - AUTO_STEP_MAX - 1;
      if (cc && cc.mat === MAT_SHALLOW && !onBr && cat.onGround) {
        cachedWaterObstacles.push({ wx: cat.x, wy: cat.y, r: 8.2, isCat: true });
      }
    }

    function applyRankineDipole(wx, wy, ux0, uy0) {
      const U0 = Math.hypot(ux0, uy0);
      if (U0 < 0.001) return { vx: ux0, vy: uy0, speed: 0 };
      const hx = ux0 / U0;
      const hy = uy0 / U0;
      const px = -hy;
      const py = hx;
      let vx = ux0;
      let vy = uy0;

      const obs = cachedWaterObstacles;
      for (let i = 0; i < obs.length; i++) {
        const o = obs[i];
        const dx = wx - o.wx;
        const dy = wy - o.wy;
        const r2Raw = dx * dx + dy * dy;
        const a = o.r * 1.18;
        const cutR = a * 4.0;
        if (r2Raw >= cutR * cutR) continue;
        const rRaw = Math.sqrt(r2Raw);
        const r = Math.max(rRaw, a * 1.04);
        const r2 = r * r;
        const r4 = r2 * r2;
        const xPar = dx * hx + dy * hy;
        const yPerp = dx * px + dy * py;
        const a2 = a * a;
        const falloff = rRaw > a * 3.0 ? Math.max(0, 1 - (rRaw - a * 3.0) / a) : 1.0;
        const dvPar = -U0 * (a2 * (xPar * xPar - yPerp * yPerp) / r4) * falloff;
        const dvPerp = -U0 * (2 * a2 * xPar * yPerp / r4) * falloff;
        vx += (hx * dvPar + px * dvPerp);
        vy += (hy * dvPar + py * dvPerp);
        if (rRaw < a && rRaw > 0.001) {
          const push = U0 * 0.55 * (1 - rRaw / a);
          vx += (dx / rRaw) * push;
          vy += (dy / rRaw) * push;
        }
      }
      return { vx, vy, speed: Math.hypot(vx, vy) };
    }

    function sampleBaseWaterFlow(wx, wy) {
      const c = getCellAt(wx, wy);
      if (!c || !isWetMat(c.mat)) return { vx: 0, vy: 0, speed: 0 };

      const shallowScale = c.mat === MAT_SHALLOW ? 0.55 : 1.0;

      const paintedFlow = samplePaintedVector(customFlowVx, customFlowVy, wx, wy);
      if (paintedFlow && (paintedFlow.vx * paintedFlow.vx + paintedFlow.vy * paintedFlow.vy) > 0.04) {
        const pvx = paintedFlow.vx * shallowScale;
        const pvy = paintedFlow.vy * shallowScale;
        return { vx: pvx, vy: pvy, speed: Math.hypot(pvx, pvy) };
      }

      // Correnteza automática por gravidade (-∇h) em riachos/cachoeiras acima do nível do mar
      if (c.h >= 0) {
        const mx = c.mx, my = c.my;
        const h0 = c.h;
        let gx = 0, gy = 0;
        for (let dy = -2; dy <= 2; dy++) {
          const ny = my + dy;
          if (ny < 0 || ny >= mh) continue;
          const row = ny * mw;
          for (let dx = -2; dx <= 2; dx++) {
            if (dx === 0 && dy === 0) continue;
            const nx = mx + dx;
            if (nx < 0 || nx >= mw) continue;
            const nIdx = row + nx;
            if (!isWetMat(matMap[nIdx])) continue;
            const nh = hmap[nIdx] < 0 ? (matMap[nIdx] === MAT_SHALLOW ? -1 : -2) : hmap[nIdx];
            const w = 1 / (dx * dx + dy * dy);
            gx += dx * (nh - h0) * w;
            gy += dy * (nh - h0) * w;
          }
        }
        const gMag = Math.hypot(gx, gy);
        if (gMag > 0.12) {
          const slopeSpeed = Math.min(54, 22 + gMag * 14) * (c.mat === MAT_SHALLOW ? 0.85 : 1.0);
          return { vx: (-gx / gMag) * slopeSpeed, vy: (-gy / gMag) * slopeSpeed, speed: slopeSpeed };
        }
      }

      if (window.__IS_STUDIO__) {
        return { vx: 0, vy: 0, speed: 0 };
      }

      let drainFactor = 1.0;
      if (wy >= 740) {
        const t = Math.max(0, Math.min(1, (wy - 740) / 220));
        drainFactor = 1 - t * t * (3 - 2 * t);
        if (drainFactor <= 0.001) return { vx: 0, vy: 0, speed: 0 };
      }

      if (wx >= 130 && wx <= 280 && wy >= -540 && wy <= -450) {
        const vx = -34 * drainFactor * shallowScale;
        const vy = 4 * drainFactor * shallowScale;
        return { vx, vy, speed: Math.hypot(vx, vy) };
      }

      let bestD2 = Infinity;
      let bestTx = 0, bestTy = 1;
      for (let i = 0; i < RIVER_SEGMENTS.length; i++) {
        const seg = RIVER_SEGMENTS[i];
        const t = seg.len2 > 0
          ? Math.max(0, Math.min(1, ((wx - seg.ax) * seg.dx + (wy - seg.ay) * seg.dy) / seg.len2))
          : 0;
        const px = seg.ax + seg.dx * t;
        const py = seg.ay + seg.dy * t;
        const d2 = (wx - px) * (wx - px) + (wy - py) * (wy - py);
        if (d2 < bestD2) {
          bestD2 = d2;
          bestTx = seg.tx;
          bestTy = seg.ty;
        }
      }
      if (bestD2 > 64 * 64) {
        return { vx: 0, vy: 0, speed: 0 };
      }
      const speed = 26 * drainFactor * shallowScale;
      return { vx: bestTx * speed, vy: bestTy * speed, speed };
    }

    function sampleWaterFlow(wx, wy) {
      const base = sampleBaseWaterFlow(wx, wy);
      if (base.speed <= 0.001) return base;
      return applyRankineDipole(wx, wy, base.vx, base.vy);
    }

    const floatingItems = [];
    const PETAL_COLORS = ['#FBCFE8', '#E0F2FE', '#FEF08A'];
    let floatingSpawnAccum = 0;

    function spawnFloatingPetal(wx, wy, color = null, z = -2) {
      if (floatingItems.length >= 64) return;
      floatingItems.push({
        x: wx,
        y: wy,
        z,
        life: 1.0,
        phase: Math.random() * Math.PI * 2,
        color: color || PETAL_COLORS[Math.floor(Math.random() * PETAL_COLORS.length)]
      });
    }

    const FLOW_STREAK_COUNT = 180;
    const flowStreaks = [];

    function seedFlowStreak(s, randomAge = false) {
      let sx = 0, sy = 0, fc = null, found = false;
      const visObs = [];
      for (let i = 0; i < cachedWaterObstacles.length; i++) {
        const o = cachedWaterObstacles[i];
        if (Math.hypot(o.wx - camX, o.wy - camY) < 420) visObs.push(o);
      }

      if (visObs.length > 0 && Math.random() < 0.40) {
        const o = visObs[Math.floor(Math.random() * visObs.length)];
        const base = sampleBaseWaterFlow(o.wx, o.wy);
        if (base.speed > 1.5) {
          const ux = base.vx / base.speed;
          const uy = base.vy / base.speed;
          const px = -uy;
          const py = ux;
          for (let attempt = 0; attempt < 4; attempt++) {
            const distUp = 14 + Math.random() * 24;
            const lat = (Math.random() * 2 - 1) * 1.6 * o.r;
            const tx = o.wx - ux * distUp + px * lat;
            const ty = o.wy - uy * distUp + py * lat;
            const c = getCellAt(tx, ty);
            if (c && isWetMat(c.mat) && sampleBaseWaterFlow(tx, ty).speed >= 1.2) {
              sx = tx; sy = ty; fc = c; found = true;
              break;
            }
          }
        }
      }

      if (!found) {
        for (let attempt = 0; attempt < 16; attempt++) {
          const tx = camX + (Math.random() * 2 - 1) * 340;
          const ty = camY + (Math.random() * 2 - 1) * 240;
          const c = getCellAt(tx, ty);
          if (c && isWetMat(c.mat) && sampleBaseWaterFlow(tx, ty).speed >= 1.2) {
            sx = tx; sy = ty; fc = c; found = true;
            break;
          }
        }
      }

      if (!found && !window.__IS_STUDIO__) {
        const tx = 128 + (Math.random() * 2 - 1) * 44;
        const ty = 200 + (Math.random() * 2 - 1) * 140;
        const c = getCellAt(tx, ty);
        if (c && isWetMat(c.mat)) {
          sx = tx; sy = ty; fc = c; found = true;
        }
      }

      if (!found) {
        s.hLen = 0;
        s.age = 0;
        s.maxAge = 0.5;
        s.deflect = 0;
        return;
      }

      s.x = sx;
      s.y = sy;
      s.z = waterSurfZ(fc);
      s.hist[0] = sx;
      s.hist[1] = sy;
      s.hLen = 1;
      s.histAccum = 0;
      s.maxAge = 1.3 + Math.random() * 1.3;
      s.age = randomAge ? Math.random() * s.maxAge * 0.5 : 0;
      s.deflect = 0;
    }

    function stepFlowStreaks(dt) {
      for (let i = 0; i < flowStreaks.length; i++) {
        const s = flowStreaks[i];
        if (s.hLen === 0 || s.age >= s.maxAge || Math.hypot(s.x - camX, s.y - camY) > 480) {
          seedFlowStreak(s, false);
          if (s.hLen === 0) continue;
        }
        const v1 = sampleWaterFlow(s.x, s.y);
        if (v1.speed < 1.2) {
          seedFlowStreak(s, false);
          continue;
        }
        const v2 = sampleWaterFlow(s.x + 0.5 * v1.vx * dt, s.y + 0.5 * v1.vy * dt);
        if (v2.speed < 1.2) {
          seedFlowStreak(s, false);
          continue;
        }
        s.x += v2.vx * dt;
        s.y += v2.vy * dt;
        s.age += dt;

        const fc = getCellAt(s.x, s.y);
        if (!fc || !isWetMat(fc.mat)) {
          seedFlowStreak(s, false);
          continue;
        }
        s.z = waterSurfZ(fc);

        const base = sampleBaseWaterFlow(s.x, s.y);
        s.deflect = base.speed > 0.5
          ? Math.hypot(v2.vx - base.vx, v2.vy - base.vy) / Math.max(2, base.speed)
          : 0;

        s.histAccum += dt;
        if (s.histAccum >= 0.045) {
          s.histAccum -= 0.045;
          if (s.hLen < 6) {
            s.hist[s.hLen * 2] = s.x;
            s.hist[s.hLen * 2 + 1] = s.y;
            s.hLen++;
          } else {
            for (let k = 0; k < 10; k++) s.hist[k] = s.hist[k + 2];
            s.hist[10] = s.x;
            s.hist[11] = s.y;
          }
        }
      }
    }

    function initFlowStreaks() {
      refreshWaterObstaclesCache();
      flowStreaks.length = 0;
      for (let i = 0; i < FLOW_STREAK_COUNT; i++) {
        const s = {
          x: 0, y: 0, z: -2,
          hist: new Float32Array(12),
          hLen: 0, histAccum: 0,
          age: 0, maxAge: 1.8, deflect: 0
        };
        seedFlowStreak(s, true);
        flowStreaks.push(s);
      }
      for (let tick = 0; tick < 25; tick++) {
        stepFlowStreaks(1 / 30);
      }
    }

    const WAVE_W = 120, WAVE_H = 80, WAVE_CELL = 6;
    let waveCurr = new Float32Array(WAVE_W * WAVE_H);
    let wavePrev = new Float32Array(WAVE_W * WAVE_H);
    let waveTmp = new Float32Array(WAVE_W * WAVE_H);
    let waveOriginX = 0;
    let waveOriginY = 0;
    let waveAccum = 0;

    function isWaterFast(wx, wy) {
      const mx = Math.floor(wx / VOX + HALF_GRID);
      const my = Math.floor(wy / VOX + HALF_GRID);
      if (mx < 0 || my < 0 || mx >= mw || my >= mh) return false;
      return isWetMat(matMap[my * mw + mx]);
    }

    function syncWaveOrigin() {
      const targetOX = Math.floor(camX / WAVE_CELL) * WAVE_CELL - (WAVE_W * WAVE_CELL) * 0.5;
      const targetOY = Math.floor(camY / WAVE_CELL) * WAVE_CELL - (WAVE_H * WAVE_CELL) * 0.5;
      const shiftX = Math.round((targetOX - waveOriginX) / WAVE_CELL);
      const shiftY = Math.round((targetOY - waveOriginY) / WAVE_CELL);
      if (shiftX === 0 && shiftY === 0) return;

      if (Math.abs(shiftX) >= WAVE_W || Math.abs(shiftY) >= WAVE_H) {
        waveCurr.fill(0);
        wavePrev.fill(0);
        waveOriginX = targetOX;
        waveOriginY = targetOY;
        return;
      }

      const xStart = Math.max(0, -shiftX);
      const xEnd = Math.min(WAVE_W, WAVE_W - shiftX);
      const yStart = Math.max(0, -shiftY);
      const yEnd = Math.min(WAVE_H, WAVE_H - shiftY);

      waveTmp.fill(0);
      for (let dy = yStart; dy < yEnd; dy++) {
        const srcRow = (dy + shiftY) * WAVE_W;
        const dstRow = dy * WAVE_W;
        for (let dx = xStart; dx < xEnd; dx++) {
          waveTmp[dstRow + dx] = waveCurr[srcRow + dx + shiftX];
        }
      }
      waveCurr.set(waveTmp);

      waveTmp.fill(0);
      for (let dy = yStart; dy < yEnd; dy++) {
        const srcRow = (dy + shiftY) * WAVE_W;
        const dstRow = dy * WAVE_W;
        for (let dx = xStart; dx < xEnd; dx++) {
          waveTmp[dstRow + dx] = wavePrev[srcRow + dx + shiftX];
        }
      }
      wavePrev.set(waveTmp);

      waveOriginX = targetOX;
      waveOriginY = targetOY;
    }

    function injectWaterRipple(wx, wy, strength = 1.0, radiusCells = 2) {
      const cx = Math.floor((wx - waveOriginX) / WAVE_CELL);
      const cy = Math.floor((wy - waveOriginY) / WAVE_CELL);
      if (cx < -radiusCells || cx >= WAVE_W + radiusCells || cy < -radiusCells || cy >= WAVE_H + radiusCells) return;
      const r2 = radiusCells * radiusCells + 0.25;
      const y0 = Math.max(1, cy - radiusCells);
      const y1 = Math.min(WAVE_H - 2, cy + radiusCells);
      const x0 = Math.max(1, cx - radiusCells);
      const x1 = Math.min(WAVE_W - 2, cx + radiusCells);
      for (let dy = y0; dy <= y1; dy++) {
        const cwy = waveOriginY + (dy + 0.5) * WAVE_CELL;
        for (let dx = x0; dx <= x1; dx++) {
          const d2 = (dx - cx) * (dx - cx) + (dy - cy) * (dy - cy);
          if (d2 > r2) continue;
          const cwx = waveOriginX + (dx + 0.5) * WAVE_CELL;
          if (!isWaterFast(cwx, cwy)) continue;
          const falloff = 1 - Math.sqrt(d2) / (radiusCells + 0.8);
          const idx = dy * WAVE_W + dx;
          waveCurr[idx] = Math.max(-4.0, Math.min(4.0, waveCurr[idx] + strength * falloff));
        }
      }
    }

    function sampleWaveBilerp(buf, fx, fy) {
      const x0 = Math.max(0, Math.min(WAVE_W - 2, Math.floor(fx)));
      const y0 = Math.max(0, Math.min(WAVE_H - 2, Math.floor(fy)));
      const tx = Math.max(0, Math.min(1, fx - x0));
      const ty = Math.max(0, Math.min(1, fy - y0));
      const i00 = y0 * WAVE_W + x0;
      return (buf[i00] * (1 - tx) + buf[i00 + 1] * tx) * (1 - ty) +
             (buf[i00 + WAVE_W] * (1 - tx) + buf[i00 + WAVE_W + 1] * tx) * ty;
    }

    // Amostragem de altura u(x,y) e gradiente ∇u do WaveBuffer para Empuxo de Arquimedes
    function sampleWaveHeightAndGrad(wx, wy) {
      const fx = (wx - waveOriginX) / WAVE_CELL - 0.5;
      const fy = (wy - waveOriginY) / WAVE_CELL - 0.5;
      if (fx < 1 || fx >= WAVE_W - 2 || fy < 1 || fy >= WAVE_H - 2) {
        return { u: 0, gx: 0, gy: 0 };
      }
      const u = sampleWaveBilerp(waveCurr, fx, fy);
      const uR = sampleWaveBilerp(waveCurr, fx + 1, fy);
      const uL = sampleWaveBilerp(waveCurr, fx - 1, fy);
      const uD = sampleWaveBilerp(waveCurr, fx, fy + 1);
      const uU = sampleWaveBilerp(waveCurr, fx, fy - 1);
      return {
        u,
        gx: (uR - uL) / (2 * WAVE_CELL),
        gy: (uD - uU) / (2 * WAVE_CELL),
      };
    }

    function isInsideWaterObstacle(wx, wy, obs) {
      for (let i = 0; i < obs.length; i++) {
        const o = obs[i];
        const dx = wx - o.wx;
        const dy = wy - o.wy;
        if (dx * dx + dy * dy < o.r * o.r) return true;
      }
      return false;
    }

    function stepWaveBuffer() {
      const obs = cachedWaterObstacles;
      waveTmp.fill(0);
      for (let dy = 1; dy < WAVE_H - 1; dy++) {
        const wy = waveOriginY + (dy + 0.5) * WAVE_CELL;
        const my = Math.floor(wy / VOX + HALF_GRID);
        if (my < 0 || my >= mh) continue;
        const row = dy * WAVE_W;
        const isSpongeY = dy < 6 || dy >= WAVE_H - 6;
        let rowWind = null;
        for (let dx = 1; dx < WAVE_W - 1; dx++) {
          const idx = row + dx;
          const wx = waveOriginX + (dx + 0.5) * WAVE_CELL;
          const mx = Math.floor(wx / VOX + HALF_GRID);
          if (mx < 0 || mx >= mw || !isWetMat(matMap[my * mw + mx]) || isInsideWaterObstacle(wx, wy, obs)) {
            waveTmp[idx] = 0;
            continue;
          }
          if ((dx & 3) === 1 || !rowWind) {
            rowWind = sampleWind(wx, wy, fluidTime);
          }
          const isSponge = isSpongeY || dx < 6 || dx >= WAVE_W - 6;
          const damp = isSponge ? 0.72 : 0.955;

          const base = sampleBaseWaterFlow(wx, wy);
          let sx = dx;
          let sy = dy;
          if (base.speed > 0.1) {
            const advX = Math.max(-0.45, Math.min(0.45, -base.vx * 0.012));
            const advY = Math.max(-0.45, Math.min(0.45, -base.vy * 0.012));
            const candX = Math.max(1, Math.min(WAVE_W - 2, dx + advX));
            const candY = Math.max(1, Math.min(WAVE_H - 2, dy + advY));
            const upWx = waveOriginX + (candX + 0.5) * WAVE_CELL;
            const upWy = waveOriginY + (candY + 0.5) * WAVE_CELL;
            if (isWaterFast(upWx, upWy) && !isInsideWaterObstacle(upWx, upWy, obs)) {
              sx = candX;
              sy = candY;
            }
          }

          let next;
          if (sx === dx && sy === dy) {
            next = ((waveCurr[idx - 1] + waveCurr[idx + 1] + waveCurr[idx - WAVE_W] + waveCurr[idx + WAVE_W]) * 0.5 - wavePrev[idx]) * damp;
          } else {
            const cAvg = (
              sampleWaveBilerp(waveCurr, sx - 1, sy) +
              sampleWaveBilerp(waveCurr, sx + 1, sy) +
              sampleWaveBilerp(waveCurr, sx, sy - 1) +
              sampleWaveBilerp(waveCurr, sx, sy + 1)
            ) * 0.5;
            const pVal = sampleWaveBilerp(wavePrev, sx, sy);
            next = (cAvg - pVal) * damp;
          }

          // Marolas capilares geradas pelo WindField na superfície da água (com sombra topográfica)
          if (!isSponge && rowWind && rowWind.mag > 0.42) {
            const wForce = Math.min(0.08, (rowWind.mag - 0.42) * 0.055);
            const phase = (wx * rowWind.wx + wy * rowWind.wy) * 0.16 - fluidTime * 5.2;
            next += Math.sin(phase) * wForce;
          }

          if (Math.abs(next) < 0.008) next = 0;
          else if (next > 4.0) next = 4.0;
          else if (next < -4.0) next = -4.0;
          waveTmp[idx] = next;
        }
      }
      const oldPrev = wavePrev;
      wavePrev = waveCurr;
      waveCurr = waveTmp;
      waveTmp = oldPrev;
    }

    // Deslocamento local de Arquimedes (apenas corpos submersos num raio de 64u na mesma cota d'água)
    function getLocalArchimedesRise(wx, wy, refSurfZ) {
      let localVol = 0;
      if ((cat._prevSubVol || 0) > 0 && Math.hypot(cat.x - wx, cat.y - wy) <= 64) {
        localVol += cat._prevSubVol;
      }
      for (let i = 0; i < debrisDrops.length; i++) {
        const d = debrisDrops[i];
        if (!d.inWater || !(d._prevSubVol > 0)) continue;
        if (Math.abs(d.z - refSurfZ) <= 3.5 && Math.hypot(d.x - wx, d.y - wy) <= 64) {
          localVol += d._prevSubVol;
        }
      }
      return Math.min(1.5, localVol * 0.14);
    }

    // =========================================================================
    // 8C. VIRTUAL PIPE SHALLOW WATER (waterfallSim 40×26, WF_CELL=4)
    // =========================================================================
    const WF_W = 40, WF_H = 26, WF_CELL = 4;
    const WF_X0 = 208, WF_Y0 = -545;
    const wfH = new Float32Array(WF_W * WF_H);
    const wfBedZ = new Float32Array(WF_W * WF_H);
    const wfBlockH = new Float32Array(WF_W * WF_H);
    const wfFL = new Float32Array(WF_W * WF_H);
    const wfFR = new Float32Array(WF_W * WF_H);
    const wfFT = new Float32Array(WF_W * WF_H);
    const wfFB = new Float32Array(WF_W * WF_H);

    function rebuildWaterfallBlocks() {
      wfBlockH.fill(0);
      for (let iy = 0; iy < WF_H; iy++) {
        const wy = WF_Y0 + (iy + 0.5) * WF_CELL;
        for (let ix = 0; ix < WF_W; ix++) {
          const wx = WF_X0 + (ix + 0.5) * WF_CELL;
          const idx = iy * WF_W + ix;
          const h = getHeightAt(wx, wy);
          wfBedZ[idx] = h !== null ? Math.max(-2, h) : 0;
          if (wx >= 250 && Math.abs(wy + 495) > 17.5) {
            wfBlockH[idx] = 48;
          }
        }
      }
      for (let i = 0; i < props.length; i++) {
        const p = props[i];
        if (p.destroyed || (p.destr && p.destr.chopped)) continue;
        if (p.wx < WF_X0 - 16 || p.wx > WF_X0 + WF_W * WF_CELL + 16) continue;
        if (p.wy < WF_Y0 - 16 || p.wy > WF_Y0 + WF_H * WF_CELL + 16) continue;
        const meta = PROP_COLLIDER_META[p.modelKey] || { r: 6 };
        const obsR = p.isDamBoulder ? 10.8 : ((meta.r || 6) * (p.scale || 1) + 0.4);
        for (let iy = 0; iy < WF_H; iy++) {
          const wy = WF_Y0 + (iy + 0.5) * WF_CELL;
          for (let ix = 0; ix < WF_W; ix++) {
            const wx = WF_X0 + (ix + 0.5) * WF_CELL;
            if (Math.hypot(wx - p.wx, wy - p.wy) <= obsR) {
              const idx = iy * WF_W + ix;
              wfBlockH[idx] = Math.max(wfBlockH[idx], 24);
              wfH[idx] = 0;
              wfFL[idx] = wfFR[idx] = wfFT[idx] = wfFB[idx] = 0;
            }
          }
        }
      }
    }

    function stepWaterfallSim(dtSim = 1 / 30, emitEffects = true) {
      const substeps = 3;
      const dtSub = dtSim / substeps;
      const pipeAccel = 160.0 / WF_CELL;
      const damp = 0.92;

      for (let sub = 0; sub < substeps; sub++) {
        // 1. Inflow source upstream of (278, -495)
        for (let iy = 8; iy <= 16; iy++) {
          const row = iy * WF_W;
          for (let ix = 22; ix <= 28; ix++) {
            const idx = row + ix;
            if (wfBlockH[idx] === 0) {
              wfH[idx] = Math.min(7.5, wfH[idx] + 72.0 * dtSub);
            }
          }
        }

        // 2. Virtual Pipe accelerations + depth-proportional Chézy cap + mass-preserving scaling
        for (let iy = 0; iy < WF_H; iy++) {
          const row = iy * WF_W;
          for (let ix = 0; ix < WF_W; ix++) {
            const idx = row + ix;
            const hCell = wfH[idx];
            if (wfBlockH[idx] > 0 || hCell <= 1e-5) {
              wfFL[idx] = wfFR[idx] = wfFT[idx] = wfFB[idx] = 0;
              continue;
            }
            const Hc = wfBedZ[idx] + hCell;
            const cap = Math.min(32.0, hCell * 7.2);
            const wxCell = WF_X0 + (ix + 0.5) * WF_CELL;
            const steepDrop = (ix > 0 && (wfBedZ[idx] - wfBedZ[idx - 1]) >= 1.5) || (wxCell < 273);
            const latGain = steepDrop ? 0.025 : 1.0;
            const latDamp = steepDrop ? 0.45 : damp;
            let fL = 0, fR = 0, fT = 0, fB = 0;
            if (ix > 0 && wfBlockH[idx - 1] === 0) {
              fL = Math.min(cap, Math.max(0, wfFL[idx] * damp + dtSub * pipeAccel * (Hc - (wfBedZ[idx - 1] + wfH[idx - 1]))));
            }
            if (ix < WF_W - 1 && wfBlockH[idx + 1] === 0) {
              fR = Math.min(cap, Math.max(0, wfFR[idx] * damp + dtSub * pipeAccel * (Hc - (wfBedZ[idx + 1] + wfH[idx + 1]))));
            }
            if (iy > 0 && wfBlockH[idx - WF_W] === 0) {
              fT = Math.min(cap, Math.max(0, wfFT[idx] * latDamp + dtSub * pipeAccel * latGain * (Hc - (wfBedZ[idx - WF_W] + wfH[idx - WF_W]))));
            }
            if (iy < WF_H - 1 && wfBlockH[idx + WF_W] === 0) {
              fB = Math.min(cap, Math.max(0, wfFB[idx] * latDamp + dtSub * pipeAccel * latGain * (Hc - (wfBedZ[idx + WF_W] + wfH[idx + WF_W]))));
            }

            const sumOut = fL + fR + fT + fB;
            if (sumOut * dtSub > hCell && sumOut > 1e-6) {
              const K = hCell / (sumOut * dtSub);
              fL *= K; fR *= K; fT *= K; fB *= K;
            }
            wfFL[idx] = fL;
            wfFR[idx] = fR;
            wfFT[idx] = fT;
            wfFB[idx] = fB;
          }
        }

        // 3. Conservative depth update + plunge pool drain (wx < 245) & live impact foam
        for (let iy = 0; iy < WF_H; iy++) {
          const wy = WF_Y0 + (iy + 0.5) * WF_CELL;
          const row = iy * WF_W;
          for (let ix = 0; ix < WF_W; ix++) {
            const idx = row + ix;
            if (wfBlockH[idx] > 0) {
              wfH[idx] = 0;
              continue;
            }
            const inL = ix > 0 ? wfFR[idx - 1] : 0;
            const inR = ix < WF_W - 1 ? wfFL[idx + 1] : 0;
            const inT = iy > 0 ? wfFB[idx - WF_W] : 0;
            const inB = iy < WF_H - 1 ? wfFT[idx + WF_W] : 0;
            let nextH = wfH[idx] + dtSub * ((inL + inR + inT + inB) - (wfFL[idx] + wfFR[idx] + wfFT[idx] + wfFB[idx]));
            if (nextH < 1e-5) nextH = 0;

            const wx = WF_X0 + (ix + 0.5) * WF_CELL;
            if (emitEffects && sub === substeps - 1 && wx >= 240 && wx <= 250 && nextH > 0.18) {
              if (Math.hypot(camX - wx, camY - wy) < 460 && particles.length < 220 && Math.random() < 0.22) {
                spawnParticles(
                  wx + (Math.random() - 0.5) * 3,
                  wy + (Math.random() - 0.5) * 3,
                  0.4, 1, ['#E0F2FE', '#FFFFFF', '#7DD3FC'], 16,
                  { grav: 75, vz: 14 + Math.random() * 12, life: 0.48 }
                );
              }
            }
            if (wx < 245 && nextH > 0) {
              const drain = nextH * Math.min(1, 12.0 * dtSub);
              nextH -= drain;
              if (emitEffects && sub === substeps - 1 && drain > 0.015) {
                injectWaterRipple(wx, wy, Math.min(1.3, drain * 2.2), 1);
              }
            }
            wfH[idx] = nextH;
          }
        }
      }
    }

    function getWaterfallSplitStats() {
      let nSum = 0, nCnt = 0;
      let cSum = 0, cCnt = 0;
      let sSum = 0, sCnt = 0;
      let totalVolume = 0;

      for (let iy = 0; iy < WF_H; iy++) {
        const wy = WF_Y0 + (iy + 0.5) * WF_CELL;
        const row = iy * WF_W;
        for (let ix = 0; ix < WF_W; ix++) {
          const idx = row + ix;
          const d = wfH[idx];
          totalVolume += d * WF_CELL * WF_CELL;
          const wx = WF_X0 + (ix + 0.5) * WF_CELL;
          if (wx >= 252 && wx <= 268) {
            if (wy >= -515 && wy < -499) {
              nSum += d; nCnt++;
            } else if (wy >= -499 && wy <= -491) {
              cSum += d; cCnt++;
            } else if (wy > -491 && wy <= -475) {
              sSum += d; sCnt++;
            }
          }
        }
      }

      return {
        damIntact: Boolean(damBoulder && !damBoulder.destroyed && !(damBoulder.destr && damBoulder.destr.chopped)),
        northBranchDepth: nCnt > 0 ? nSum / nCnt : 0,
        southBranchDepth: sCnt > 0 ? sSum / sCnt : 0,
        centerDownstreamDepth: cCnt > 0 ? cSum / cCnt : 0,
        totalVolume
      };
    }

    function stepAutoWaterfallsAndSprings(emitSpray = true) {
      if (typeof waterfallDrops !== 'undefined' && waterfallDrops.length > 0) {
        for (let i = 0; i < waterfallDrops.length; i++) {
          const wd = waterfallDrops[i];
          if (Math.abs(wd.wx - camX) > 380 || Math.abs(wd.wy - camY) > 380) continue;
          if (Math.random() < 0.25) {
            injectWaterRipple(wd.wx, wd.wy, 0.55, 1);
          }
          if (emitSpray && particles.length < 220 && Math.random() < 0.18) {
            spawnParticles(
              wd.wx + (Math.random() - 0.5) * 3,
              wd.wy + (Math.random() - 0.5) * 3,
              wd.botZ + 0.6,
              1,
              ['#E0F2FE', '#FFFFFF', '#7DD3FC'],
              14,
              { grav: 75, vz: 12 + Math.random() * 10, life: 0.45 }
            );
          }
        }
      }
      if (typeof waterSprings !== 'undefined' && waterSprings.length > 0) {
        for (let i = 0; i < waterSprings.length; i++) {
          const sp = waterSprings[i];
          if (Math.abs(sp.wx - camX) > 380 || Math.abs(sp.wy - camY) > 380) continue;
          if (Math.random() < 0.14) {
            injectWaterRipple(sp.wx, sp.wy, 0.45, 1);
          }
          if (emitSpray && particles.length < 220 && Math.random() < 0.08) {
            spawnParticles(
              sp.wx + (Math.random() - 0.5) * 3,
              sp.wy + (Math.random() - 0.5) * 3,
              (getHeightAt(sp.wx, sp.wy) || sp.z) + 0.8,
              1,
              ['#E0F2FE', '#BAE6FD', '#FFFFFF'],
              8,
              { grav: 55, vz: 10 + Math.random() * 6, life: 0.35 }
            );
          }
        }
      }
    }

    // =========================================================================
    // 9C. MATÉRIA GRANULAR (Areia / Neve — Ângulo de Repouso + Dirty-Rect Re-Bake)
    // =========================================================================
    function relaxGranularBox(mx0, my0, mx1, my1, passes = 3) {
      const x0 = Math.max(2, mx0);
      const y0 = Math.max(2, my0);
      const x1 = Math.min(mw - 3, mx1);
      const y1 = Math.min(mh - 3, my1);
      let changed = false;
      for (let pass = 0; pass < passes; pass++) {
        for (let my = y0; my <= y1; my++) {
          const row = my * mw;
          for (let mx = x0; mx <= x1; mx++) {
            const idx = row + mx;
            const mat = matMap[idx];
            if (mat !== MAT_SAND && mat !== MAT_PEAK) continue;
            const talus = mat === MAT_SAND ? ENGINE_TUNING.sandTalus : ENGINE_TUNING.rockTalus;
            const h = hmap[idx];
            let lowestNb = -1;
            let lowestH = h - talus;
            const nbs = [idx - 1, idx + 1, idx - mw, idx + mw];
            for (let k = 0; k < 4; k++) {
              const nb = nbs[k];
              if (isWetMat(matMap[nb])) continue;
              if (hmap[nb] < lowestH) {
                lowestH = hmap[nb];
                lowestNb = nb;
              }
            }
            if (lowestNb >= 0) {
              hmap[idx] = h - 1;
              hmap[lowestNb] = hmap[lowestNb] + 1;
              changed = true;
            }
          }
        }
      }
      if (changed) {
        rebakeTerrainDirtyRect(x0 - 2, y0 - 2, x1 + 2, y1 + 2);
      }
      return changed;
    }

    function disturbGranular(wx, wy, depth = 1) {
      const g = worldToGrid(wx, wy);
      const mx = g.mx, my = g.my;
      if (mx < 3 || mx >= mw - 3 || my < 3 || my >= mh - 3) return;
      const idx = my * mw + mx;
      const mat = matMap[idx];
      if (mat !== MAT_SAND && mat !== MAT_PEAK) return;

      const minFloor = mat === MAT_SAND ? -1 : 10;
      const take = Math.min(depth, Math.max(0, hmap[idx] - minFloor));
      if (take > 0) {
        hmap[idx] -= take;
        // Deposita o material deslocado na borda ao redor
        const rim = [idx - 2, idx + 2, idx - 2 * mw, idx + 2 * mw];
        const target = rim[(Math.abs(mx + my)) & 3];
        if (!isWetMat(matMap[target])) hmap[target] += take;
      }
      relaxGranularBox(mx - 6, my - 6, mx + 6, my + 6, 3);
      rebakeTerrainDirtyRect(mx - 6, my - 6, mx + 6, my + 6);
      const pCol = mat === MAT_SAND ? ['#F2D69A', '#E7C788'] : ['#F5C6E0', '#FFFFFF'];
      spawnParticles(wx, wy, (hmap[idx] || 0) + 1.5, 6, pCol, 22, { grav: 210, vz: 28, life: 0.45 });
      guideSpeak('granular', mat === MAT_SAND ? 'Areia fofa! Ângulo de repouso! ⏳' : 'Neve fofa no pico! ❄️', 130);
    }

    // =========================================================================
    // 9D. TECIDOS, CORDAS & BANDEIRINHAS (Integração de Verlet 3D)
    // =========================================================================
    const verletChains = [];
    function createVerletChain(x0, y0, z0, x1, y1, z1, count, opts = {}) {
      const nodes = [];
      const totalLen = Math.hypot(x1 - x0, y1 - y0, z1 - z0);
      const segLen = opts.segLen || (totalLen / Math.max(1, count - 1));
      for (let i = 0; i < count; i++) {
        const t = i / Math.max(1, count - 1);
        const x = x0 + (x1 - x0) * t;
        const y = y0 + (y1 - y0) * t;
        const z = z0 + (z1 - z0) * t;
        const pinned = (i === 0) || (!!opts.pinEnd && i === count - 1);
        nodes.push({ x, y, z, ox: x, oy: y, oz: z, pinned });
      }
      verletChains.push({
        nodes,
        segLen,
        windScale: opts.windScale !== undefined ? opts.windScale : 1.0,
        kind: opts.kind || 'rope',
        colors: opts.colors || ['#EF4444', '#FACC15', '#38BDF8', '#4ADE80']
      });
    }


    function stepVerletChains(dt) {
      const stepDt = Math.min(0.033, dt);
      const dt2 = stepDt * stepDt;
      const damp = 0.96;
      for (let c = 0; c < verletChains.length; c++) {
        const ch = verletChains[c];
        const nodes = ch.nodes;
        if (Math.hypot(nodes[0].x - camX, nodes[0].y - camY) > 460) continue;

        for (let i = 0; i < nodes.length; i++) {
          const n = nodes[i];
          if (n.pinned) continue;
          const vx = (n.x - n.ox) * damp;
          const vy = (n.y - n.oy) * damp;
          const vz = (n.z - n.oz) * damp;
          n.ox = n.x;
          n.oy = n.y;
          n.oz = n.z;

          const w = sampleWind(n.x, n.y, fluidTime);
          let ax = w.wx * 95 * ch.windScale;
          let ay = w.wy * 95 * ch.windScale;
          let az = -190;

          const dCat = Math.hypot(n.x - cat.x, n.y - cat.y);
          if (dCat < 12 && Math.abs(n.z - (cat.z + 8)) < 10) {
            const inv = 1 / Math.max(0.5, dCat);
            ax += (n.x - cat.x) * inv * 420;
            ay += (n.y - cat.y) * inv * 420;
          }

          n.x += vx + ax * dt2;
          n.y += vy + ay * dt2;
          n.z += vz + az * dt2;
        }

        // Restrições de distância (4 iterações de Gauss-Seidel)
        for (let iter = 0; iter < 4; iter++) {
          for (let i = 0; i < nodes.length - 1; i++) {
            const a = nodes[i];
            const b = nodes[i + 1];
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const dz = b.z - a.z;
            const dist = Math.hypot(dx, dy, dz) || 0.0001;
            const diff = (dist - ch.segLen) / dist;
            if (!a.pinned && !b.pinned) {
              a.x += dx * diff * 0.5;
              a.y += dy * diff * 0.5;
              a.z += dz * diff * 0.5;
              b.x -= dx * diff * 0.5;
              b.y -= dy * diff * 0.5;
              b.z -= dz * diff * 0.5;
            } else if (a.pinned && !b.pinned) {
              b.x -= dx * diff;
              b.y -= dy * diff;
              b.z -= dz * diff;
            } else if (!a.pinned && b.pinned) {
              a.x += dx * diff;
              a.y += dy * diff;
              a.z += dz * diff;
            }
          }
        }
      }
    }

    // =========================================================================
    // 9B. TERMODINÂMICA, DIFUSÃO DE CALOR & COMBUSTÃO (acoplada a WindField & Água)
    // =========================================================================
    const THERM_W = 48;
    const THERM_H = 36;
    const THERM_CELL = 8;
    const tempGrid = new Float32Array(THERM_W * THERM_H);
    const tempNext = new Float32Array(THERM_W * THERM_H);
    const moistGrid = new Float32Array(THERM_W * THERM_H);
    const fuelGrid = new Float32Array(THERM_W * THERM_H);
    let thermInit = false;
    let thermOriginX = 0;
    let thermOriginY = 0;
    let thermAccum = 0;
    let warmthSpeakCd = 0;

    function initThermGridAt(ox, oy) {
      thermOriginX = ox;
      thermOriginY = oy;
      for (let iy = 0; iy < THERM_H; iy++) {
        const wy = oy + (iy + 0.5) * THERM_CELL;
        for (let ix = 0; ix < THERM_W; ix++) {
          const wx = ox + (ix + 0.5) * THERM_CELL;
          const idx = iy * THERM_W + ix;
          const c = getCellAt(wx, wy);
          tempGrid[idx] = 0;
          if (!c || isWetMat(c.mat)) {
            moistGrid[idx] = 1.0;
            fuelGrid[idx] = 0.0;
          } else if (c.mat === MAT_GRASS || c.mat === MAT_LILYPAD) {
            moistGrid[idx] = 0.65;
            fuelGrid[idx] = 0.70;
          } else {
            moistGrid[idx] = 0.20;
            fuelGrid[idx] = 0.0;
          }
        }
      }
      thermInit = true;
    }

    function stepThermodynamics(dt) {
      if (warmthSpeakCd > 0) warmthSpeakCd = Math.max(0, warmthSpeakCd - dt);
      const targetOX = Math.floor((camX - (THERM_W * THERM_CELL) * 0.5) / THERM_CELL) * THERM_CELL;
      const targetOY = Math.floor((camY - (THERM_H * THERM_CELL) * 0.5) / THERM_CELL) * THERM_CELL;
      if (!thermInit || Math.abs(targetOX - thermOriginX) > 96 || Math.abs(targetOY - thermOriginY) > 96) {
        initThermGridAt(targetOX, targetOY);
      }

      // Fontes de calor (campfires e props 'fire') + interação com o gatinho
      for (let i = 0; i < props.length; i++) {
        const p = props[i];
        const pMeta = PROP_COLLIDER_META[p.modelKey];
        if (p.destroyed || (p.modelKey !== 'campfire' && !(pMeta && pMeta.isFire))) continue;
        const S = cat.scale || 1;
        const fireR = ((pMeta && pMeta.r) || 7.2) * (p.scale || 1);
        const fireH = ((pMeta && pMeta.h) || 13) * (p.scale || 1) + 1;
        const dCat = Math.hypot(cat.x - p.wx, cat.y - p.wy);
        if (dCat < fireR + 3.0 * S + 0.3 && cat.z <= p.wz + fireH) {
          // Empurra radialmente para fora do colisor sólido para nunca travar em cima
          const nx = dCat > 0.1 ? (cat.x - p.wx) / dCat : 0;
          const ny = dCat > 0.1 ? (cat.y - p.wy) / dCat : 1;
          const safeDist = fireR + 3.0 * S + 1.8;
          cat.x = p.wx + nx * safeDist;
          cat.y = p.wy + ny * safeDist;
          if (cat.hurtTimer <= 0) {
            cat.hurtTimer = 1.0;
            cat.vz = 145;
            cat.onGround = false;
            sfxBlocked();
            catSpeak('Ai! Quente! 🔥', 110);
          }
        } else if (dCat >= 10.5 && dCat < 26) {
          if (!guideSpeak('warm_near', 'Quentinho! 🔥', 100) && warmthSpeakCd <= 0 && !cat.speech) {
            warmthSpeakCd = 14;
            catSpeak('Quentinho! 🔥', 90);
          }
        } else if (dCat >= 26 && dCat < 46) {
          guideSpeak('warm_far', 'Já sinto calor daqui! 🌡️', 110);
        }

        // Injeta calor no centro da fogueira e emite brasas no WindField
        const ix = Math.floor((p.wx - thermOriginX) / THERM_CELL);
        const iy = Math.floor((p.wy - thermOriginY) / THERM_CELL);
        if (ix >= 1 && ix < THERM_W - 1 && iy >= 1 && iy < THERM_H - 1) {
          tempGrid[iy * THERM_W + ix] = 95;
        }
        if (Math.hypot(p.wx - camX, p.wy - camY) < 340 && Math.random() < dt * 10) {
          spawnParticles(
            p.wx + (Math.random() - 0.5) * 4,
            p.wy + (Math.random() - 0.5) * 4,
            p.wz + 7,
            1,
            ['#F97316', '#FACC15', '#EF4444'],
            8,
            { grav: -28, vz: 22 + Math.random() * 14, life: 0.55 + Math.random() * 0.35 }
          );
        }
      }

      thermAccum += dt;
      const stepDt = 1 / 15;
      while (thermAccum >= stepDt) {
        thermAccum -= stepDt;
        const alpha = 0.14;
        const cool = ENGINE_TUNING.fireCool;
        const T_IGN = 42;
        for (let iy = 1; iy < THERM_H - 1; iy++) {
          const wy = thermOriginY + (iy + 0.5) * THERM_CELL;
          const row = iy * THERM_W;
          for (let ix = 1; ix < THERM_W - 1; ix++) {
            const wx = thermOriginX + (ix + 0.5) * THERM_CELL;
            const idx = row + ix;
            const c = getCellAt(wx, wy);
            let T = tempGrid[idx];
            if (!c || isWetMat(c.mat)) {
              if (T > 8 && Math.random() < 0.25) {
                spawnParticles(wx, wy, waterSurfZ(c) + 1, 1, ['#E0F2FE', '#FFFFFF'], 6, { grav: -18, vz: 16, life: 0.5 });
              }
              tempNext[idx] = 0;
              moistGrid[idx] = 1.0;
              continue;
            }
            const lap = tempGrid[idx - 1] + tempGrid[idx + 1] + tempGrid[idx - THERM_W] + tempGrid[idx + THERM_W] - 4 * T;
            const w = sampleWind(wx, wy, fluidTime);
            const gradTx = (tempGrid[idx + 1] - tempGrid[idx - 1]) * 0.5;
            const gradTy = (tempGrid[idx + THERM_W] - tempGrid[idx - THERM_W]) * 0.5;
            const adv = -(w.wx * gradTx + w.wy * gradTy) * 0.04;
            T = Math.max(0, T + alpha * lap + adv - cool * T * stepDt);

            if (moistGrid[idx] > 0.05 && T > 6) {
              moistGrid[idx] = Math.max(0, moistGrid[idx] - 0.018 * T * stepDt);
              T = Math.min(T, T_IGN - 2);
            } else if (T >= T_IGN && moistGrid[idx] <= 0.05 && fuelGrid[idx] > 0.05) {
              T = Math.min(120, T + 22 * stepDt);
              fuelGrid[idx] = Math.max(0, fuelGrid[idx] - 0.28 * stepDt);
              if (Math.random() < 0.3) {
                spawnParticles(wx, wy, c.h + 2, 1, ['#F97316', '#FACC15'], 6, { grav: -22, vz: 18, life: 0.45 });
              }
            }
            tempNext[idx] = T < 0.05 ? 0 : T;
          }
        }
        tempGrid.set(tempNext);
      }
    }

