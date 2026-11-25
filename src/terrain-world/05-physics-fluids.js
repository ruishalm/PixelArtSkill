    // =========================================================================
    // 7. ESTADO DO GATO, FÍSICA CONTÍNUA EM MICRO-VOXELS & TRAVEL
    // =========================================================================
    const SPAWN_X = -330;
    const SPAWN_Y = 90;
    const spawnH = getHeightAt(SPAWN_X, SPAWN_Y) || 0;

    const cat = {
      x: SPAWN_X,
      y: SPAWN_Y,
      z: spawnH,
      vz: 0,
      groundZ: spawnH,
      onGround: true,
      coyoteTimer: 0,
      jumpBuffer: 0,
      hurtTimer: 0,
      selfAngle: 0,
      walkPhase: 0,
      isWalking: false,
      idleTimer: 0,
      scale: 1.0,
      skinIdx: 0,
      hatIdx: 0,
      speech: null,
      lastSafeX: SPAWN_X,
      lastSafeY: SPAWN_Y,
      lastSafeZ: spawnH,
      maxJumpReached: spawnH,
      obstacleHint: 'ok',
      obstacleLabel: '✅ Caminho Livre'
    };

    const TRAVEL_SPOTS = [
      { wx: -330, wy: 90,   label: '🏡 Vila da Clareira' },
      { wx: -248, wy: 225,  label: '🏠 Cabana 2' },
      { wx: -780, wy: 90,   label: '🌻 Campos de Girassol' },
      { wx: -285, wy: 562,  label: '🏛️ Ruínas Orgânicas' },
      { wx: -180, wy: 684,  label: '🏖️ Praia Dourada' },
      { wx: -615, wy: 795,  label: '🗼 Farol Monumental' },
      { wx: -435, wy: -315, label: '⛩️ Jardim Zen & Torii' },
      { wx: 426,  wy: 228,  label: '🍄 Bosque Cogumelos' },
      { wx: 112,  wy: 232,  label: '💧 Vau Raso do Rio' },
      { wx: 615,  wy: -66,  label: '🥾 Base da Montanha' },
      { wx: 298,  wy: -468, label: '🌊 Topo da Cachoeira (Pedra)' },
      { wx: 480,  wy: -495, label: '🌸 Pico Sakura (Z=64)' }
    ];
    let travelIdx = 0;

    const visitedBiomes = new Set(['vila']);
    let toastTimer = null;
    function showBiomeToast(name) {
      const el = document.getElementById('biomeToast');
      el.textContent = `🗺️ Descoberto: ${name}!`;
      el.classList.add('show');
      if (toastTimer) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
    }

    const particles = [];
    function spawnParticles(wx, wy, wz, count, colors, speed = 28, opts = {}) {
      for (let i = 0; i < count; i++) {
        const a = Math.random() * Math.PI * 2;
        const sp = (0.35 + Math.random() * 0.65) * speed;
        particles.push({
          x: wx, y: wy, z: wz,
          vx: Math.cos(a) * sp,
          vy: Math.sin(a) * sp,
          vz: opts.vz !== undefined ? opts.vz : (20 + Math.random() * 42),
          life: opts.life !== undefined ? opts.life : (0.42 + Math.random() * 0.32),
          grav: opts.grav !== undefined ? opts.grav : 260,
          isLeaf: !!opts.isLeaf,
          color: colors[i % colors.length],
          size: 2
        });
      }
    }

    function catSpeak(text, timer = 140) {
      cat.speech = { text, timer };
    }

    const catGuidedFlags = new Set();
    function guideSpeak(flag, text, timer = 130) {
      if (catGuidedFlags.has(flag)) return false;
      catGuidedFlags.add(flag);
      catSpeak(text, timer);
      return true;
    }

    function waterSurfZ(cell) {
      if (!cell) return -2;
      if (cell.mat === MAT_SHALLOW) return cell.h < 0 ? -1 : cell.h;
      return cell.h < 0 ? -2 : cell.h;
    }

    function evaluateSupport(wx, wy, currentZ, onGround) {
      const r = onGround ? 2.4 : 3.2;
      const samples = [
        [wx, wy],
        [wx - r, wy], [wx + r, wy],
        [wx, wy - r], [wx, wy + r]
      ];
      let bestH = -999;
      const centerCell = getCellAt(wx, wy);
      const climbAllowed = onGround ? AUTO_STEP_MAX + 0.5 : 2.0;

      for (const [sx, sy] of samples) {
        const br = getBridgeAt(sx, sy);
        if (br) {
          const dz = getBridgeDeckZ(br, sx, sy);
          if (dz <= currentZ + climbAllowed && dz > bestH) {
            bestH = dz;
          }
        }
        const c = getCellAt(sx, sy);
        if (!c || c.mat === MAT_WATER || !c.standable) continue;
        if (c.h <= currentZ + climbAllowed) {
          if (c.h > bestH) bestH = c.h;
        }
      }

      for (const pc of platformColliders) {
        if (pc.disabled) continue;
        const d = Math.hypot(wx - pc.wx, wy - pc.wy);
        const pClimb = onGround ? 4.0 : 1.5;
        if (d <= pc.r && pc.topZ <= currentZ + pClimb) {
          if (pc.topZ > bestH) bestH = pc.topZ;
        }
      }

      return { bestH, centerCell };
    }

    function isPointInPropCollider(px, py, sc, pad = 3.0) {
      if (sc.shape === 'box') {
        const dx = px - sc.wx;
        const dy = py - sc.wy;
        const ca = Math.cos(-(sc.angle || 0));
        const sa = Math.sin(-(sc.angle || 0));
        const lx = dx * ca - dy * sa;
        const ly = dx * sa + dy * ca;
        return Math.abs(lx) < sc.halfW + pad && Math.abs(ly) < sc.halfD + pad;
      }
      return Math.hypot(px - sc.wx, py - sc.wy) < sc.r + pad;
    }

    function checkCollisionAt(nx, ny, catZ, onGround) {
      if (nx < WORLD_MIN + 6 || nx > WORLD_MAX - 6 || ny < WORLD_MIN + 6 || ny > WORLD_MAX - 6) {
        return { blocked: true, reason: 'high', maxStepH: 999 };
      }

      const mvX = nx - cat.x, mvY = ny - cat.y;
      const centerBr = getBridgeAt(nx, ny);
      const onCenterBridge = centerBr && catZ >= getBridgeDeckZ(centerBr, nx, ny) - AUTO_STEP_MAX - 1;

      const curBr = getBridgeAt(cat.x, cat.y);
      if (curBr && curBr.hasRailings) {
        const curDeckZ = getBridgeDeckZ(curBr, cat.x, cat.y);
        if (catZ >= curDeckZ - AUTO_STEP_MAX - 1 && catZ < curDeckZ + 6) {
          const margin = 3.2;
          const hitsRailing = curBr.axis === 'x'
            ? (ny < curBr.yMin + margin || ny > curBr.yMax - margin)
            : (nx < curBr.xMin + margin || nx > curBr.xMax - margin);
          if (hitsRailing) {
            return { blocked: true, reason: 'prop', maxStepH: curDeckZ + 6 };
          }
        }
      }

      const centerCell = getCellAt(nx, ny);
      if (!onCenterBridge && centerCell && centerCell.mat === MAT_WATER && (onGround || catZ <= waterSurfZ(centerCell) + 0.3)) {
        return { blocked: true, reason: 'water', maxStepH: waterSurfZ(centerCell) };
      }

      const r = 2.6;
      const offsets = [[0, 0], [-r, -r], [r, -r], [-r, r], [r, r]];

      const allowedClimb = onGround ? AUTO_STEP_MAX : 1.5;
      let blocked = false;
      let maxBlockingH = -999;
      let propBlocked = false;

      for (const [ox, oy] of offsets) {
        if ((ox !== 0 || oy !== 0) && (ox * mvX + oy * mvY < -0.001)) continue;
        const px = nx + ox, py = ny + oy;
        const pBr = getBridgeAt(px, py);
        if (pBr) {
          const deckZ = getBridgeDeckZ(pBr, px, py);
          if (catZ >= deckZ - AUTO_STEP_MAX - 1) {
            if (deckZ > catZ + allowedClimb) {
              blocked = true;
              if (deckZ > maxBlockingH) maxBlockingH = deckZ;
            }
            continue;
          }
        }
        const c = getCellAt(px, py);
        if (!c) {
          blocked = true;
          maxBlockingH = 999;
          continue;
        }
        if (c.mat === MAT_WATER) continue;
        if (!c.standable && c.h > cat.groundZ + AUTO_STEP_MAX) {
          const wallH = Math.max(c.h, c.cliffTop);
          if (wallH > catZ + allowedClimb) {
            blocked = true;
            if (wallH > maxBlockingH) maxBlockingH = wallH;
            continue;
          }
        }
        if (c.h > catZ + allowedClimb) {
          blocked = true;
          if (c.h > maxBlockingH) maxBlockingH = c.h;
        }
      }

      for (const sc of propColliders) {
        if (sc.disabled) continue;
        if (catZ >= sc.baseZ - 2 && catZ < sc.baseZ + sc.colH - 1.5) {
          if (isPointInPropCollider(nx, ny, sc, 3.0)) {
            blocked = true;
            propBlocked = true;
            const topH = sc.baseZ + sc.colH;
            if (topH > maxBlockingH) maxBlockingH = topH;
          }
        }
      }

      for (const pc of platformColliders) {
        if (pc.disabled) continue;
        const d = Math.hypot(nx - pc.wx, ny - pc.wy);
        const curD = Math.hypot(cat.x - pc.wx, cat.y - pc.wy);
        if (d < pc.r + 1.2 && d <= curD + 0.05 && catZ < pc.topZ - 2.0 && catZ >= pc.baseZ - 4.0) {
          blocked = true;
          if (pc.topZ > maxBlockingH) maxBlockingH = pc.topZ;
        }
      }

      if (blocked) {
        if (propBlocked) {
          return { blocked: true, reason: 'prop', maxStepH: maxBlockingH };
        }
        const diff = maxBlockingH - cat.groundZ;
        return {
          blocked: true,
          reason: diff <= CAT_HEIGHT * 2.0 + 0.5 ? 'jump' : 'high',
          maxStepH: maxBlockingH
        };
      }
      return { blocked: false, reason: 'ok', maxStepH: catZ };
    }

    function updateObstacleSensor(dirX, dirY) {
      const fx = dirX !== 0 || dirY !== 0 ? dirX : -Math.sin(cat.selfAngle);
      const fy = dirX !== 0 || dirY !== 0 ? dirY : Math.cos(cat.selfAngle);
      const probeX = cat.x + fx * 11;
      const probeY = cat.y + fy * 11;
      const c = getCellAt(probeX, probeY);
      const curBr = getBridgeAt(cat.x, cat.y);
      const probeBr = getBridgeAt(probeX, probeY);

      if (!c) {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = '⛔ Limite do Vale';
        return;
      }
      if (curBr && curBr.hasRailings) {
        const curDeckZ = getBridgeDeckZ(curBr, cat.x, cat.y);
        if (cat.groundZ >= curDeckZ - AUTO_STEP_MAX - 1 && cat.groundZ < curDeckZ + 6) {
          const hitsRailing = curBr.axis === 'x'
            ? (probeY < curBr.yMin + 3.2 || probeY > curBr.yMax - 3.2)
            : (probeX < curBr.xMin + 3.2 || probeX > curBr.xMax - 3.2);
          if (hitsRailing) {
            cat.obstacleHint = 'jump';
            cat.obstacleLabel = '🪵 Corrimão da Ponte';
            return;
          }
        }
      }

      const onProbeBr = probeBr && cat.groundZ >= getBridgeDeckZ(probeBr, probeX, probeY) - AUTO_STEP_MAX - 1;
      if (!onProbeBr && c.mat === MAT_WATER) {
        cat.obstacleHint = 'water';
        cat.obstacleLabel = '💧 Água Intransponível';
        return;
      }

      for (const sc of propColliders) {
        if (sc.disabled) continue;
        if (cat.groundZ < sc.baseZ + sc.colH - 1.5 && isPointInPropCollider(probeX, probeY, sc, 3.2)) {
          cat.obstacleHint = 'high';
          cat.obstacleLabel = sc.shape === 'box' ? '🏠 Parede / Estrutura' : '🌲 Obstáculo Sólido';
          return;
        }
      }

      let targetH = onProbeBr
        ? getBridgeDeckZ(probeBr, probeX, probeY)
        : ((!c.standable && c.h > cat.groundZ + AUTO_STEP_MAX) ? Math.max(c.h, c.cliffTop) : c.h);
      for (const pc of platformColliders) {
        if (pc.disabled) continue;
        if (Math.hypot(probeX - pc.wx, probeY - pc.wy) <= pc.r + 2.0 && pc.topZ > targetH) {
          targetH = pc.topZ;
        }
      }

      const dz = targetH - cat.groundZ;
      const curCell = getCellAt(cat.x, cat.y);
      const onCurBr = curBr && cat.groundZ >= getBridgeDeckZ(curBr, cat.x, cat.y) - AUTO_STEP_MAX - 1;
      if (curCell && curCell.mat === MAT_SHALLOW && !onCurBr && cat.onGround && dz <= AUTO_STEP_MAX) {
        cat.obstacleHint = 'shallow';
        cat.obstacleLabel = '💧 Água Rasa (Molhando as Patas!)';
      } else if (dz <= AUTO_STEP_MAX) {
        cat.obstacleHint = 'ok';
        cat.obstacleLabel = dz > 0.5 ? '✅ Rampa Suave (≤0.35H)' : '✅ Caminho Livre';
      } else if (dz <= CAT_HEIGHT * 2.0 + 0.5) {
        cat.obstacleHint = 'jump';
        cat.obstacleLabel = `🦘 Degrau ${Math.round(dz)}u — Espaço p/ Pular!`;
      } else {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = `⛔ Paredão ${Math.round(dz)}u (> 2×H)`;
      }
    }

    // =========================================================================
    // 8. CONTROLES, TOUCH & VIEWPORT RESPONSIVO 1:1
    // =========================================================================
    const keys = {};
    let turn = -Math.PI * 0.25;
    let targetTurn = turn;
    let squash = 0.72;
    let camX = cat.x;
    let camY = cat.y;
    let camZ = cat.z;
    let blockedCooldown = 0;

    // =========================================================================
    // 8B. FLUIDOS 2.5D: WINDFIELD + WATERFLOW (DRAIN SINK) + WAVEBUFFER
    // =========================================================================
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

      let drainFactor = 1.0;
      if (wy >= 740) {
        const t = Math.max(0, Math.min(1, (wy - 740) / 220));
        drainFactor = 1 - t * t * (3 - 2 * t);
        if (drainFactor <= 0.001) return { vx: 0, vy: 0, speed: 0 };
      }

      const shallowScale = c.mat === MAT_SHALLOW ? 0.55 : 1.0;

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
      // Lagos isolados e áreas fora do leito do rio (~64u) são água parada (sem correnteza)
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

      if (!found) {
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
    let waveOriginX = Math.floor(camX / WAVE_CELL) * WAVE_CELL - (WAVE_W * WAVE_CELL) * 0.5;
    let waveOriginY = Math.floor(camY / WAVE_CELL) * WAVE_CELL - (WAVE_H * WAVE_CELL) * 0.5;
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

    rebuildWaterfallBlocks();
    for (let i = 0; i < 70; i++) {
      stepWaterfallSim(1 / 30, false);
    }
    initFlowStreaks();

    const canvas = document.getElementById('viewport');
    const ctx = canvas.getContext('2d');
    const lowCanvas = document.createElement('canvas');
    const lowCtx = lowCanvas.getContext('2d');
    const entityCanvas = document.createElement('canvas');
    const entityCtx = entityCanvas.getContext('2d');
    const entitySilCanvas = document.createElement('canvas');
    const entitySilCtx = entitySilCanvas.getContext('2d');

    let LOW_W = 480;
    let LOW_H = 300;
    let pixelScale = 3;
    let viewW = window.innerWidth;
    let viewH = window.innerHeight;
    let dpr = 1;

    function handleResize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      viewW = window.innerWidth;
      viewH = window.innerHeight;
      pixelScale = Math.max(2, Math.min(4, Math.floor(Math.min(viewW, viewH) / 260) || 2));
      LOW_W = Math.ceil(viewW / pixelScale);
      LOW_H = Math.ceil(viewH / pixelScale);

      for (const [cv, cx] of [[lowCanvas, lowCtx], [entityCanvas, entityCtx], [entitySilCanvas, entitySilCtx]]) {
        cv.width = LOW_W;
        cv.height = LOW_H;
        cx.imageSmoothingEnabled = false;
      }

      canvas.width = Math.round(viewW * dpr);
      canvas.height = Math.round(viewH * dpr);
      canvas.style.width = viewW + 'px';
      canvas.style.height = viewH + 'px';
    }
    window.addEventListener('resize', handleResize);
    handleResize();

    let equippedTool = 'none';
    let actionCooldown = 0;
    let swingTimer = 0;
    let shakeTimer = 0;
    let shakeMag = 0;

    function equipTool(toolId, quiet = false) {
      if (!TOOLS_META[toolId]) return;
      equippedTool = toolId;
      const btnTool = document.getElementById('btnTool');
      if (btnTool) btnTool.textContent = TOOLS_META[toolId].label;
      if (!quiet) catSpeak('Equipado: ' + TOOLS_META[toolId].label, 95);
    }

    function spawnDebrisDrops(wx, wy, wz, modelKey, count, biasDx = 0, biasDy = 0, vzMin = 95, vzMax = 145) {
      const model = propModels[modelKey];
      if (!model || count <= 0) return;
      const isLog = modelKey === 'wood_log';
      for (let i = 0; i < count; i++) {
        const ang = Math.atan2(biasDy, biasDx) + (Math.random() - 0.5) * 2.2;
        const hSpd = 24 + Math.random() * 34;
        debrisDrops.push({
          modelKey,
          model,
          x: wx + Math.cos(ang) * 4,
          y: wy + Math.sin(ang) * 4,
          z: wz,
          vx: Math.cos(ang) * hSpd,
          vy: Math.sin(ang) * hSpd,
          vz: vzMin + Math.random() * (vzMax - vzMin),
          scale: 0.75,
          selfAngle: Math.random() * Math.PI * 2,
          spin: (Math.random() - 0.5) * 6,
          bounces: 0,
          inWater: false,
          persistent: isLog,
          life: isLog ? 999999 : 18.0
        });
      }
      if (debrisDrops.length > 96) {
        for (let i = 0; i < debrisDrops.length && debrisDrops.length > 96; i++) {
          if (!debrisDrops[i].persistent) { debrisDrops.splice(i, 1); i--; }
        }
        if (debrisDrops.length > 96) debrisDrops.splice(0, debrisDrops.length - 96);
      }
    }

    function spawnPushableLog(wx, wy, angle = 0.35) {
      const model = propModels.wood_log;
      if (!model) return;
      const c = getCellAt(wx, wy);
      const gz = c ? (isWetMat(c.mat) ? waterSurfZ(c) : c.h) : 0;
      debrisDrops.push({
        modelKey: 'wood_log',
        model,
        x: wx,
        y: wy,
        z: gz,
        vx: 0,
        vy: 0,
        vz: 0,
        scale: 0.85,
        selfAngle: angle,
        spin: 0,
        bounces: 0,
        inWater: !!(c && isWetMat(c.mat)),
        persistent: true,
        life: 999999
      });
    }
    spawnPushableLog(86, 248, 0.4);     // Tronco empurrável na margem do vau do Rio (perto da Vila)
    spawnPushableLog(-618, -585, 0.8);  // Tronco empurrável na borda do Lago Zen

    function triggerAction() {
      if (actionCooldown > 0) return;
      actionCooldown = 0.22;
      swingTimer = 0.22;

      const fx = -Math.sin(cat.selfAngle);
      const fy = Math.cos(cat.selfAngle);
      const hitX = cat.x + fx * 14;
      const hitY = cat.y + fy * 14;

      injectWindImpulse(hitX, hitY, fx * 2.4, fy * 2.4, 38, 0.45);
      spawnParticles(hitX, hitY, cat.z + 6, 4, ['#FFFDF8', '#FDE68A', '#CBD5E1'], 22, { life: 0.25, grav: 80 });

      // Shake nearby non-destructible foliage (e.g. flower_tuft)
      for (let i = 0; i < foliageProps.length; i++) {
        const fp = foliageProps[i];
        if (fp.destroyed || fp.destr) continue;
        if (Math.hypot(fp.wx - cat.x, fp.wy - cat.y) <= 34) {
          fp.vx += fx * 45;
          fp.vy += fy * 45;
          spawnParticles(fp.wx, fp.wy, fp.wz + 6, 5, fp.foliage.leafColors, 24, {
            isLeaf: true, grav: 32, vz: 14, life: 1.6
          });
        }
      }

      // Find nearest intact destructible prop within 34u (or 28u + colliderRadius)
      let bestTarget = null;
      let bestScore = Infinity;
      for (let i = 0; i < props.length; i++) {
        const item = props[i];
        if (item.destroyed || !item.destr || item.destr.chopped) continue;
        if (Math.abs(cat.z - item.wz) > 28) continue;
        const dx = item.wx - cat.x;
        const dy = item.wy - cat.y;
        const dist = Math.hypot(dx, dy);
        const colR = ((PROP_COLLIDER_META[item.modelKey] && PROP_COLLIDER_META[item.modelKey].r) || 5) * (item.scale || 1);
        const maxReach = Math.max(34, 28 + colR);
        if (dist > maxReach) continue;
        const dot = dist > 0.001 ? (dx * fx + dy * fy) / dist : 1;
        const score = (dist - colR) - (dot > 0.1 ? 10 * dot : 0);
        if (score < bestScore) {
          bestScore = score;
          bestTarget = item;
        }
      }

      if (!bestTarget) return;

      const d = bestTarget.destr;
      const dmg = (equippedTool === d.bestTool) ? 2 : 1;
      d.hp -= dmg;
      d.hitFlash = 0.14;
      destructStats.hits++;
      sfxChop();

      const burstZ = bestTarget.wz + Math.min(20, Math.max(4, (bestTarget.topZ - bestTarget.baseZ) * 0.5));
      spawnParticles(bestTarget.wx, bestTarget.wy, burstZ, 8, d.colors, 36);
      if (bestTarget.foliage) {
        bestTarget.vx += fx * 38;
        bestTarget.vy += fy * 38;
      }

      if (d.hp <= 0) {
        d.chopped = true;
        if (bestTarget.solidCollider) bestTarget.solidCollider.disabled = true;
        if (bestTarget.platCollider) bestTarget.platCollider.disabled = true;

        let dirX = bestTarget.wx - cat.x;
        let dirY = bestTarget.wy - cat.y;
        const dLen = Math.hypot(dirX, dirY);
        if (dLen < 0.001) {
          dirX = fx;
          dirY = fy;
        } else {
          dirX /= dLen;
          dirY /= dLen;
        }

        if (d.mode === 'chop') {
          const stumpH = d.zCut * bestTarget.scale;
          bestTarget.renderMaxSlice = d.zCut;
          bestTarget.topZ = bestTarget.baseZ + Math.ceil(stumpH);
          bestTarget.foliage = null;
          bestTarget.bx = 0;
          bestTarget.by = 0;
          bestTarget.vx = 0;
          bestTarget.vy = 0;
          const stumpCol = {
            wx: bestTarget.wx,
            wy: bestTarget.wy,
            r: Math.max(8, ((PROP_COLLIDER_META[bestTarget.modelKey] && PROP_COLLIDER_META[bestTarget.modelKey].r) || 8) * bestTarget.scale),
            baseZ: bestTarget.wz,
            topZ: bestTarget.wz + stumpH,
            modelKey: bestTarget.modelKey + '_stump',
            disabled: false
          };
          platformColliders.push(stumpCol);
          bestTarget.platCollider = stumpCol;
          bestTarget.isPlatform = true;
          bestTarget.platTopZ = stumpCol.topZ;

          fallingBodies.push({
            model: bestTarget.model,
            wx: bestTarget.wx,
            wy: bestTarget.wy,
            baseZ: bestTarget.wz,
            zCut: d.zCut,
            selfAngle: bestTarget.selfAngle,
            scale: bestTarget.scale,
            dx: dirX,
            dy: dirY,
            phi: 0.08,
            omega: 0.45,
            colors: d.colors,
            drops: d.drops,
            dropKey: d.dropKey
          });
          destructStats.choppedCount++;
        } else if (d.mode === 'crumble') {
          if (bestTarget.isDamBoulder) {
            bestTarget.destroyed = true;
            bestTarget.isPlatform = false;
            bestTarget.isFire = false;
            if (bestTarget.platCollider) bestTarget.platCollider.disabled = true;
            shakeTimer = 0.18;
            shakeMag = 3.0;
            sfxCrumble();
            spawnParticles(bestTarget.wx, bestTarget.wy, bestTarget.wz + 6, 28, d.colors, 58, { grav: 240, life: 0.80 });
            spawnParticles(bestTarget.wx, bestTarget.wy, bestTarget.wz + 5, 18, ['#E0F2FE', '#FFFFFF', '#67E8F9'], 46, { grav: 150, vz: 32, life: 0.65 });
            spawnDebrisDrops(bestTarget.wx, bestTarget.wy, bestTarget.wz + 6, d.dropKey || 'stone_chunk', d.drops, dirX, dirY, 95, 145);
            rebuildWaterfallBlocks();
            refreshWaterObstaclesCache();
            destructStats.crumbledCount++;
          } else {
            const baseH = d.zCut * bestTarget.scale;
            bestTarget.renderMaxSlice = d.zCut;
            bestTarget.topZ = bestTarget.baseZ + Math.ceil(baseH);
            bestTarget.isFire = false;
            const ruinPlat = {
              wx: bestTarget.wx,
              wy: bestTarget.wy,
              r: Math.max(6, ((PROP_COLLIDER_META[bestTarget.modelKey] && PROP_COLLIDER_META[bestTarget.modelKey].r) || 8) * bestTarget.scale),
              baseZ: bestTarget.wz,
              topZ: bestTarget.wz + baseH,
              modelKey: bestTarget.modelKey + '_rubble',
              disabled: false
            };
            platformColliders.push(ruinPlat);
            bestTarget.platCollider = ruinPlat;
            bestTarget.isPlatform = true;
            bestTarget.platTopZ = ruinPlat.topZ;

            shakeTimer = 0.16;
            shakeMag = 2.5;
            sfxCrumble();
            spawnParticles(bestTarget.wx, bestTarget.wy, bestTarget.wz + baseH + 4, 22, d.colors, 52, { grav: 240, life: 0.75 });
            spawnDebrisDrops(bestTarget.wx, bestTarget.wy, bestTarget.wz + baseH + 3, d.dropKey || 'stone_chunk', d.drops, dirX, dirY, 95, 145);
            if (bestTarget.modelKey === 'boulder_large') {
              rebuildWaterfallBlocks();
              if (bestTarget.isDamBoulder) guideSpeak('dam_broken', 'Fluxo liberado! 💧', 120);
            }
            refreshWaterObstaclesCache();
            destructStats.crumbledCount++;
          }
        } else if (d.mode === 'trim') {
          bestTarget.destroyed = true;
          bestTarget.foliage = null;
          spawnParticles(bestTarget.wx, bestTarget.wy, bestTarget.wz + 6, 14, d.colors, 36, {
            isLeaf: true, grav: 32, vz: 18 + Math.random() * 14, life: 2.0
          });
          refreshWaterObstaclesCache();
          destructStats.trimmedCount++;
        }
      } else {
        // Sem prop alvo: se estiver sobre areia ou neve, escava matéria granular em tempo real!
        const digX = cat.x - Math.sin(cat.selfAngle) * 8;
        const digY = cat.y + Math.cos(cat.selfAngle) * 8;
        const dc = getCellAt(digX, digY);
        if (dc && (dc.mat === MAT_SAND || dc.mat === MAT_PEAK)) {
          disturbGranular(digX, digY, equippedTool === 'tool_hoe' ? 2 : 1);
        }
      }
    }

    window.addEventListener('keydown', (e) => {
      const code = e.code;
      keys[code] = true;
      if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code)) {
        e.preventDefault();
      }
      if (code === 'Space') {
        cat.jumpBuffer = 0.13;
      } else if (code === 'KeyR') {
        triggerAction();
      } else if (code === 'KeyC') {
        resetCatToSpawn();
      } else if (code === 'KeyM') {
        triggerMeow();
      }
    });
    window.addEventListener('keyup', (e) => {
      keys[e.code] = false;
    });

    document.querySelectorAll('.touch-btn[data-key]').forEach(btn => {
      const k = btn.dataset.key;
      btn.addEventListener('pointerdown', (e) => { e.preventDefault(); keys[k] = true; });
      btn.addEventListener('pointerup',   (e) => { e.preventDefault(); keys[k] = false; });
      btn.addEventListener('pointercancel', () => { keys[k] = false; });
      btn.addEventListener('pointerleave',  () => { keys[k] = false; });
    });
    document.getElementById('btnTouchJump').addEventListener('pointerdown', (e) => {
      e.preventDefault();
      cat.jumpBuffer = 0.14;
    });

    function triggerMeow() {
      sfxMeow();
      catSpeak('Miau! 🐾', 110);
      for (const npc of npcs) {
        if (Math.hypot(npc.x - cat.x, npc.y - cat.y) < 110) {
          npc.speech = { text: npc.kind === 'chicken' ? 'Có có!! 💕' : 'Piu piu! 💛', timer: 110 };
        }
      }
    }

    function teleportToWorld(wx, wy, msg = null, zOverride = null) {
      const br = getBridgeAt(wx, wy);
      const c = getCellAt(wx, wy);
      cat.x = wx;
      cat.y = wy;
      const gz = zOverride !== null ? zOverride : (br ? getBridgeDeckZ(br, wx, wy) : (c ? c.h : 0));
      cat.z = gz;
      cat.vz = 0;
      cat.groundZ = gz;
      cat.onGround = true;
      cat.lastSafeX = wx;
      cat.lastSafeY = wy;
      cat.lastSafeZ = gz;
      cat.maxJumpReached = gz;
      camX = cat.x;
      camY = cat.y;
      camZ = cat.z;
      syncWaveOrigin();
      refreshWaterObstaclesCache();
      if (msg) catSpeak(msg, 125);
    }

    function resetCatToSpawn() {
      teleportToWorld(SPAWN_X, SPAWN_Y, 'De volta à Vila! 🏡');
    }

    let isDraggingCam = false;
    let dragStartX = 0;
    let pointerDownX = 0;
    let pointerDownY = 0;
    canvas.addEventListener('pointerdown', (e) => {
      isDraggingCam = true;
      dragStartX = e.clientX;
      pointerDownX = e.clientX;
      pointerDownY = e.clientY;
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!isDraggingCam) return;
      const dx = e.clientX - dragStartX;
      dragStartX = e.clientX;
      targetTurn -= dx * 0.0085;
      turn = targetTurn;
    });
    canvas.addEventListener('pointerup', (e) => {
      if (isDraggingCam && Math.hypot(e.clientX - pointerDownX, e.clientY - pointerDownY) < 6) {
        triggerAction();
      }
      isDraggingCam = false;
      try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
    });

    const btnSkin = document.getElementById('btnSkin');
    const btnHat = document.getElementById('btnHat');
    btnSkin.addEventListener('click', () => {
      cat.skinIdx = (cat.skinIdx + 1) % CAT_SKINS.length;
      btnSkin.textContent = `🐱 ${CAT_SKINS[cat.skinIdx].name}`;
      sfxMeow();
    });
    btnHat.addEventListener('click', () => {
      cat.hatIdx = (cat.hatIdx + 1) % HAT_PRESETS.length;
      btnHat.textContent = `🎩 ${HAT_PRESETS[cat.hatIdx].name}`;
    });
    document.getElementById('btnTool').addEventListener('click', () => {
      const nextIdx = (TOOL_ORDER.indexOf(equippedTool) + 1) % TOOL_ORDER.length;
      equipTool(TOOL_ORDER[nextIdx]);
    });
    document.getElementById('btnAction').addEventListener('click', () => {
      triggerAction();
    });
    document.getElementById('btnRotL').addEventListener('click', () => { targetTurn += Math.PI / 4; });
    document.getElementById('btnRotR').addEventListener('click', () => { targetTurn -= Math.PI / 4; });
    document.getElementById('btnReset').addEventListener('click', resetCatToSpawn);
    const btnSeedEl = document.getElementById('btnSeed');
    if (btnSeedEl) {
      btnSeedEl.textContent = `🎲 Seed: ${WORLD_SEED}`;
      btnSeedEl.addEventListener('click', () => {
        const nextSeed = 1000 + Math.floor(Math.random() * 90000);
        const url = new URL(window.location.href);
        url.searchParams.set('seed', String(nextSeed));
        window.location.href = url.toString();
      });
    }
    document.getElementById('btnTravel').addEventListener('click', () => {
      travelIdx = (travelIdx + 1) % TRAVEL_SPOTS.length;
      const spot = TRAVEL_SPOTS[travelIdx];
      teleportToWorld(spot.wx, spot.wy, spot.label);
      sfxBiome();
    });

    // =========================================================================
    // 9. UPDATE FÍSICO, DESLIZAMENTO TANGENCIAL (±35°) & NPCS
    // =========================================================================
    function updateNPCs(dt) {
      for (const npc of npcs) {
        npc.timer -= dt;
        if (npc.timer <= 0) {
          npc.moving = !npc.moving;
          npc.timer = npc.moving ? (1.2 + Math.random() * 1.5) : (0.9 + Math.random() * 1.3);
          if (npc.moving) {
            const toHomeX = npc.homeX - npc.x;
            const toHomeY = npc.homeY - npc.y;
            const ang = (Math.hypot(toHomeX, toHomeY) > npc.roamR)
              ? Math.atan2(toHomeY, toHomeX)
              : Math.random() * Math.PI * 2;
            npc.dirX = Math.cos(ang);
            npc.dirY = Math.sin(ang);
          }
        }
        if (npc.moving) {
          const sp = npc.kind === 'chicken' ? 20 : 25;
          const nx = npc.x + npc.dirX * sp * dt;
          const ny = npc.y + npc.dirY * sp * dt;
          const c = getCellAt(nx, ny);
          if (c && !isWetMat(c.mat) && Math.abs(c.h - npc.z) <= 5.5) {
            let hitProp = false;
            for (const sc of propColliders) {
              if (sc.disabled) continue;
              if (isPointInPropCollider(nx, ny, sc, 3.5)) { hitProp = true; break; }
            }
            if (!hitProp) {
              npc.x = nx;
              npc.y = ny;
              npc.z = c.h;
            } else {
              npc.dirX = -npc.dirX;
              npc.dirY = -npc.dirY;
            }
          } else {
            npc.dirX = -npc.dirX;
            npc.dirY = -npc.dirY;
          }
          const desired = npc.kind === 'chicken'
            ? Math.atan2(npc.dirY, npc.dirX)
            : Math.atan2(-npc.dirX, npc.dirY);
          let diff = desired - npc.selfAngle;
          while (diff < -Math.PI) diff += Math.PI * 2;
          while (diff > Math.PI) diff -= Math.PI * 2;
          npc.selfAngle += diff * Math.min(1, dt * 8);
          npc.walkPhase += dt * (npc.kind === 'chicken' ? 9 : 13);
        }
        if (npc.speech && npc.speech.timer > 0) npc.speech.timer--;
      }
    }

    let lastRustleCell = -1;
    function stepFoliageItem(p, h) {
      const f = p.foliage;
      if (p.rustleCd > 0) p.rustleCd = Math.max(0, p.rustleCd - h);

      const kStiff = 44, cDamp = 6.2;
      const w = sampleWind(p.wx, p.wy, fluidTime);
      const tx = w.wx * f.windScale * (1 - f.rigidity);
      const ty = w.wy * f.windScale * (1 - f.rigidity);

      let ax = kStiff * (tx - p.bx) - cDamp * p.vx;
      let ay = kStiff * (ty - p.by) - cDamp * p.vy;

      const modelH = p.model.count * p.scale;
      const maxBrushDz = modelH + 4;

      // Cat brush interference
      const cdx = p.wx - cat.x;
      const cdy = p.wy - cat.y;
      const cd = Math.hypot(cdx, cdy);
      if (cd < f.pushRadius && Math.abs(cat.z - p.wz) <= maxBrushDz) {
        const pushMag = (1 - cd / f.pushRadius) * f.pushStrength;
        const invD = cd > 0.001 ? 1 / cd : 0;
        const dirX = cd > 0.001 ? cdx * invD : -Math.sin(cat.selfAngle);
        const dirY = cd > 0.001 ? cdy * invD : Math.cos(cat.selfAngle);
        ax += dirX * pushMag * kStiff;
        ay += dirY * pushMag * kStiff;

        if ((cat.isWalking || !cat.onGround) && p.rustleCd <= 0) {
          p.rustleCd = 0.28;
          const leafCount = (f.pushStrength >= 6.0 || Math.random() < 0.5) ? 2 : 1;
          spawnParticles(
            p.wx + (Math.random() - 0.5) * 4,
            p.wy + (Math.random() - 0.5) * 4,
            p.wz + Math.min(18, modelH * 0.6),
            leafCount,
            f.leafColors,
            20,
            { isLeaf: true, grav: 32, vz: 6 + Math.random() * 10, life: 2.2 + Math.random() * 1.4 }
          );
        }
      }

      // NPC brush interference
      for (let j = 0; j < npcs.length; j++) {
        const npc = npcs[j];
        const ndx = p.wx - npc.x;
        const ndy = p.wy - npc.y;
        const nd = Math.hypot(ndx, ndy);
        if (nd < f.pushRadius && Math.abs(npc.z - p.wz) <= maxBrushDz) {
          const pushMag = (1 - nd / f.pushRadius) * f.pushStrength * 0.7;
          const invD = nd > 0.001 ? 1 / nd : 0;
          const dirX = nd > 0.001 ? ndx * invD : (npc.dirX || 1);
          const dirY = nd > 0.001 ? ndy * invD : (npc.dirY || 0);
          ax += dirX * pushMag * kStiff;
          ay += dirY * pushMag * kStiff;

          if (npc.moving && p.rustleCd <= 0) {
            p.rustleCd = 0.28;
            spawnParticles(
              p.wx + (Math.random() - 0.5) * 4,
              p.wy + (Math.random() - 0.5) * 4,
              p.wz + Math.min(18, modelH * 0.6),
              1,
              f.leafColors,
              16,
              { isLeaf: true, grav: 32, vz: 4 + Math.random() * 8, life: 2.0 + Math.random() * 1.2 }
            );
          }
        }
      }

      // Gust petal shedding on sakura_oak
      if (p.modelKey === 'sakura_oak' && w.mag > 1.35 && Math.random() < h * 2.5) {
        spawnParticles(
          p.wx + (Math.random() - 0.5) * 18,
          p.wy + (Math.random() - 0.5) * 18,
          p.wz + 72,
          1,
          f.leafColors,
          14,
          { isLeaf: true, grav: 22, vz: -4 - Math.random() * 6, life: 5.0 + Math.random() * 2.0 }
        );
      }

      p.vx += ax * h;
      p.vy += ay * h;
      p.bx += p.vx * h;
      p.by += p.vy * h;

      const maxDeflect = Math.min(7.5, p.model.count * 0.22);
      const bMag = Math.hypot(p.bx, p.by);
      if (bMag > maxDeflect) {
        const s = maxDeflect / bMag;
        p.bx *= s;
        p.by *= s;
        const nx = p.bx / maxDeflect;
        const ny = p.by / maxDeflect;
        const vDotN = p.vx * nx + p.vy * ny;
        if (vDotN > 0) {
          p.vx -= vDotN * nx;
          p.vy -= vDotN * ny;
        }
      }
    }

    function updateFoliage(dt) {
      if (!Number.isFinite(dt) || dt <= 0) return;
      const clampedDt = Math.min(0.066, dt);
      const steps = clampedDt > 0.025 ? 2 : 1;
      const h = Math.min(0.033, clampedDt / steps);
      for (let i = 0; i < foliageProps.length; i++) {
        const p = foliageProps[i];
        if (p.destroyed || !p.foliage) continue;
        if (Math.hypot(p.wx - camX, p.wy - camY) >= 380) continue;
        for (let s = 0; s < steps; s++) {
          stepFoliageItem(p, h);
        }
      }
    }

    let shallowStepTimer = 0;
    let shallowSplashTimer = 0;
    let shallowRippleTimer = 0;

    function updatePhysics(dt) {
      fluidTime += dt;
      if (shallowStepTimer > 0) shallowStepTimer = Math.max(0, shallowStepTimer - dt);
      if (shallowSplashTimer > 0) shallowSplashTimer = Math.max(0, shallowSplashTimer - dt);
      if (shallowRippleTimer > 0) shallowRippleTimer = Math.max(0, shallowRippleTimer - dt);
      for (let i = windImpulses.length - 1; i >= 0; i--) {
        windImpulses[i].life -= dt;
        if (windImpulses[i].life <= 0) windImpulses.splice(i, 1);
      }

      cat.idleTimer += dt;
      if (cat.hurtTimer > 0) cat.hurtTimer = Math.max(0, cat.hurtTimer - dt);
      if (blockedCooldown > 0) blockedCooldown -= dt;
      if (actionCooldown > 0) actionCooldown = Math.max(0, actionCooldown - dt);
      if (swingTimer > 0) swingTimer = Math.max(0, swingTimer - dt);
      if (shakeTimer > 0) shakeTimer = Math.max(0, shakeTimer - dt);

      if (keys['KeyQ']) targetTurn += 2.2 * dt;
      if (keys['KeyE']) targetTurn -= 2.2 * dt;
      turn += (targetTurn - turn) * Math.min(1, dt * 14);

      updateNPCs(dt);

      let ix = 0, iy = 0;
      if (keys['KeyW'] || keys['ArrowUp']) iy -= 1;
      if (keys['KeyS'] || keys['ArrowDown']) iy += 1;
      if (keys['KeyA'] || keys['ArrowLeft']) ix -= 1;
      if (keys['KeyD'] || keys['ArrowRight']) ix += 1;

      const ilen = Math.hypot(ix, iy);
      let moveWorldX = 0, moveWorldY = 0;
      if (ilen > 0) {
        ix /= ilen;
        iy /= ilen;
        const cosA = Math.cos(turn);
        const sinA = Math.sin(turn);
        moveWorldX = ix * cosA + iy * sinA;
        moveWorldY = -ix * sinA + iy * cosA;
        cat.isWalking = true;

        const desiredAngle = Math.atan2(-moveWorldX, moveWorldY);
        let diff = desiredAngle - cat.selfAngle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        cat.selfAngle += diff * Math.min(1, dt * 18);
      } else {
        cat.isWalking = false;
      }

      const isSprinting = !!(keys['ShiftLeft'] || keys['ShiftRight']);
      const baseSpeed = isSprinting ? 205 : 124;
      const preCell = getCellAt(cat.x, cat.y);
      const preBr = getBridgeAt(cat.x, cat.y);
      const onPreBr = preBr && cat.z >= getBridgeDeckZ(preBr, cat.x, cat.y) - AUTO_STEP_MAX - 1;
      const isWadingPre = !onPreBr && cat.onGround && preCell && preCell.mat === MAT_SHALLOW;
      const wadingDrag = isWadingPre ? 0.86 : 1.0;
      const speed = (cat.onGround ? baseSpeed : Math.round(baseSpeed * 0.85)) * wadingDrag;
      if (ilen > 0) {
        const dx = moveWorldX * speed * dt;
        const dy = moveWorldY * speed * dt;
        let moved = false;
        let blockedNow = null;

        const checkX = dx !== 0 ? checkCollisionAt(cat.x + dx, cat.y, cat.z, cat.onGround) : { blocked: false };
        if (dx !== 0 && !checkX.blocked) {
          cat.x += dx;
          moved = true;
        } else if (dx !== 0) {
          blockedNow = checkX;
        }

        const checkY = dy !== 0 ? checkCollisionAt(cat.x, cat.y + dy, cat.z, cat.onGround) : { blocked: false };
        if (dy !== 0 && !checkY.blocked) {
          cat.y += dy;
          moved = true;
        } else if (dy !== 0) {
          blockedNow = checkY;
        }

        // Micro-desvio tangencial (±35°) para deslizar suavemente por rochas e margens curvas
        if (!moved) {
          const deg35 = 35 * Math.PI / 180;
          for (const ang of [deg35, -deg35]) {
            const c = Math.cos(ang), s = Math.sin(ang);
            const sdx = (dx * c - dy * s) * 0.85;
            const sdy = (dx * s + dy * c) * 0.85;
            const checkSlide = checkCollisionAt(cat.x + sdx, cat.y + sdy, cat.z, cat.onGround);
            if (!checkSlide.blocked) {
              cat.x += sdx;
              cat.y += sdy;
              moved = true;
              blockedNow = null;
              break;
            }
          }
        }

        if (!moved && blockedNow && blockedCooldown <= 0) {
          if (blockedNow.reason === 'water') {
            catSpeak('Miau! Água não! 💦', 95);
            sfxBlocked();
            blockedCooldown = 0.85;
          } else if (blockedNow.reason === 'high') {
            catSpeak('Muito alto! (>2×H) 😿', 95);
            sfxBlocked();
            blockedCooldown = 0.95;
          }
        }
      }

      if (cat.onGround) cat.coyoteTimer = 0.11;
      else cat.coyoteTimer = Math.max(0, cat.coyoteTimer - dt);

      if (cat.jumpBuffer > 0) cat.jumpBuffer = Math.max(0, cat.jumpBuffer - dt);

      if (cat.jumpBuffer > 0 && cat.coyoteTimer > 0) {
        cat.vz = JUMP_VEL;
        cat.onGround = false;
        cat.coyoteTimer = 0;
        cat.jumpBuffer = 0;
        cat.maxJumpReached = cat.z;
        sfxJump();
        spawnParticles(cat.x, cat.y, cat.z + 1, 7, ['#FFF8EC', '#E7D8C2'], 22);
        injectWindImpulse(cat.x, cat.y, -Math.sin(cat.selfAngle) * 1.4, Math.cos(cat.selfAngle) * 1.4, 36, 0.5);
        const jc = getCellAt(cat.x, cat.y);
        if (jc && isWetMat(jc.mat)) injectWaterRipple(cat.x, cat.y, 2.2, 2);
      }

      const wasOnGround = cat.onGround;
      const prevZ = cat.z;
      cat.vz -= GRAVITY * dt;
      cat.z += cat.vz * dt;
      if (cat.z > cat.maxJumpReached) cat.maxJumpReached = cat.z;

      const supportQueryZ = (!wasOnGround && cat.vz <= 0) ? Math.max(cat.z, prevZ) : cat.z;
      const sup = evaluateSupport(cat.x, cat.y, supportQueryZ, wasOnGround);
      if (sup.bestH > -900) {
        cat.groundZ = sup.bestH;
        if (cat.z <= sup.bestH + 0.05 && cat.vz <= 0 && (wasOnGround || prevZ >= sup.bestH - 2.0)) {
              if (!wasOnGround && cat.vz < -90) {
            if (sup.centerCell && sup.centerCell.mat === MAT_SHALLOW) {
              sfxShallowStep();
              injectWaterRipple(cat.x, cat.y, 1.8, 2);
              spawnParticles(cat.x, cat.y, waterSurfZ(sup.centerCell) + 0.5, 6, ['#E0F2FE', '#67E8F9', '#FFFFFF'], 24);
            } else {
              sfxLand();
              spawnParticles(cat.x, cat.y, sup.bestH + 1, 6, ['#FDF6E9', '#D6C4AA'], 24);
              if (sup.centerCell && (sup.centerCell.mat === MAT_SAND || sup.centerCell.mat === MAT_PEAK)) {
                disturbGranular(cat.x, cat.y, 1);
              }
            }
          }
          cat.z = sup.bestH;
          cat.vz = 0;
          cat.onGround = true;
          cat.lastSafeX = cat.x;
          cat.lastSafeY = cat.y;
          cat.lastSafeZ = cat.z;
        } else if (wasOnGround && sup.bestH > cat.z && sup.bestH - cat.z <= AUTO_STEP_MAX) {
          cat.z = sup.bestH;
          cat.vz = 0;
          cat.onGround = true;
          cat.lastSafeX = cat.x;
          cat.lastSafeY = cat.y;
          cat.lastSafeZ = cat.z;
        } else if (wasOnGround && sup.bestH < cat.z && cat.z - sup.bestH <= AUTO_STEP_MAX) {
          cat.z = sup.bestH;
          cat.vz = 0;
          cat.onGround = true;
        } else if (cat.z > sup.bestH + 0.5) {
          cat.onGround = false;
        }
      } else {
        cat.groundZ = -6;
        cat.onGround = false;
        if (cat.z < -2.5) {
          const inWater = sup.centerCell && sup.centerCell.mat === MAT_WATER;
          const splashX = cat.x;
          const splashY = cat.y;
          cat.x = cat.lastSafeX;
          cat.y = cat.lastSafeY;
          cat.vz = 0;
          cat.onGround = true;
          if (inWater) {
            cat.z = cat.lastSafeZ + 2;
            cat.hurtTimer = 1.0;
            sfxBlocked();
            catSpeak('Splash! De volta à margem! 💦', 110);
            spawnParticles(cat.x, cat.y, cat.z + 2, 10, ['#93C5FD', '#FFFFFF'], 32);
            injectWaterRipple(splashX, splashY, 2.2, 2);
          } else {
            cat.z = cat.lastSafeZ;
          }
        }
      }

      if (cat.isWalking && cat.onGround) {
        cat.walkPhase += dt * (isSprinting ? 17 : 12);
        if (isSprinting && Math.random() < dt * 16) {
          spawnParticles(cat.x, cat.y, cat.z + 1, 1, ['#FFF8EC', '#E7D8C2'], 16);
        }
        if (isSprinting && Math.random() < dt * 7) {
          injectWindImpulse(cat.x, cat.y, -Math.sin(cat.selfAngle) * 1.4, Math.cos(cat.selfAngle) * 1.4, 36, 0.5);
        }
      }

      // Grama rustle, água rasa wading feedback & descoberta de bioma
      const curCell = sup.centerCell;
      const curBr = getBridgeAt(cat.x, cat.y);
      const onCurBr = curBr && cat.z >= getBridgeDeckZ(curBr, cat.x, cat.y) - AUTO_STEP_MAX - 1;
      const catSubVol = (curCell && isWetMat(curCell.mat) && !onCurBr && cat.z <= waterSurfZ(curCell) + 1.0) ? 1.6 : 0;
      const prevCatSub = cat._prevSubVol || 0;
      if (catSubVol !== prevCatSub) {
        injectWaterRipple(cat.x, cat.y, (catSubVol - prevCatSub) * 1.1, 2);
        cat._prevSubVol = catSubVol;
      }
      if (curCell && curCell.mat === MAT_SHALLOW && !onCurBr && cat.onGround) {
        if (cat.isWalking) {
          guideSpeak('shallow_wade', 'Partindo a correnteza! 🌊', 125);
          if (shallowRippleTimer <= 0) {
            shallowRippleTimer = 0.04;
            injectWaterRipple(cat.x, cat.y, 0.75, 2);
          }
          if (shallowSplashTimer <= 0) {
            shallowSplashTimer = isSprinting ? 0.10 : 0.16;
            spawnParticles(
              cat.x + (Math.random() - 0.5) * 4,
              cat.y + (Math.random() - 0.5) * 4,
              waterSurfZ(curCell) + 0.5,
              2, ['#E0F2FE', '#67E8F9', '#FFFFFF'], 20, { grav: 190, vz: 26, life: 0.35 }
            );
          }
          if (shallowStepTimer <= 0) {
            shallowStepTimer = isSprinting ? 0.22 : 0.30;
            sfxShallowStep();
          }
        }
      }
      if (curCell) {
        if (cat.onGround && (curCell.mat === MAT_GRASS || curCell.mat === MAT_PEAK) && cat.isWalking && curCell.idx !== lastRustleCell) {
          lastRustleCell = curCell.idx;
          if ((curCell.mx * 73 + curCell.my * 37) % 10 < 3 && Math.random() < 0.35) {
            spawnParticles(cat.x, cat.y, cat.z + 2, 2, ['#4DB848', '#8BE064'], 14);
          }
        }
        if (!visitedBiomes.has(curCell.biomeKey)) {
          visitedBiomes.add(curCell.biomeKey);
          sfxBiome();
          showBiomeToast(curCell.biome);
        }
      }

      // Coleta dos 20 Peixes Dourados
      let collectedCount = 0;
      for (const f of fishes) {
        if (f.collected) {
          collectedCount++;
          continue;
        }
        const dx = cat.x - f.wx;
        const dy = cat.y - f.wy;
        const dz = Math.abs(cat.z - f.baseZ);
        if (Math.hypot(dx, dy) < 13 && dz < 14) {
          f.collected = true;
          collectedCount++;
          sfxFish();
          catSpeak(`Peixinho! (${collectedCount}/${fishes.length}) 🐟✨`, 135);
          spawnParticles(f.wx, f.wy, f.baseZ + 6, 16, ['#FBBF24', '#FEF08A', '#F97316', '#FFFFFF'], 44);
        }
      }
      document.getElementById('fishCounter').textContent = `🐟 ${collectedCount} / ${fishes.length}`;
      document.getElementById('biomeCounter').textContent = `🗺️ ${visitedBiomes.size} / 8`;

      updateObstacleSensor(moveWorldX, moveWorldY);
      document.getElementById('biomeLabel').textContent = curCell ? curCell.biome : 'Vale Felino';
      document.getElementById('statElev').textContent = `Chão: Z=${Math.round(cat.groundZ)} | Gato: Z=${Math.round(cat.z)}`;
      const obsEl = document.getElementById('statObstacle');
      obsEl.textContent = cat.obstacleLabel;
      obsEl.className = 'obstacle-chip obs-' + cat.obstacleHint;

      refreshWaterObstaclesCache();

      // Pétalas/itens flutuantes no poço da cachoeira e correnteza do rio até o dreno no mar sul
      floatingSpawnAccum += dt;
      const nearWaterfall = Math.hypot(camX - 232, camY + 495) < 480;
      const spawnInterval = nearWaterfall ? 0.28 : 0.55;
      if (floatingSpawnAccum >= spawnInterval) {
        floatingSpawnAccum = 0;
        if (floatingItems.length < 64) {
          spawnFloatingPetal(
            232 + (Math.random() - 0.5) * 14,
            -495 + (Math.random() - 0.5) * 14,
            null,
            -2
          );
          if (Math.hypot(camX - 118, camY - 220) < 420) {
            spawnFloatingPetal(134 + (Math.random() - 0.5) * 32, 165 + (Math.random() - 0.5) * 14, null, -2);
          }
          if (Math.hypot(camX - 132, camY + 80) < 420) {
            spawnFloatingPetal(126 + (Math.random() - 0.5) * 32, -130 + (Math.random() - 0.5) * 14, null, -2);
          }
        }
      }

      for (let i = floatingItems.length - 1; i >= 0; i--) {
        const f = floatingItems[i];
        const flow = sampleWaterFlow(f.x, f.y);
        const wave = sampleWaveHeightAndGrad(f.x, f.y);
        const fWind = sampleWind(f.x, f.y, fluidTime);
        f.x += (flow.vx + fWind.wx * 3.8 - wave.gx * 18) * dt;
        f.y += (flow.vy + fWind.wy * 3.8 - wave.gy * 18) * dt;
        const fc = getCellAt(f.x, f.y);
        if (fc && isWetMat(fc.mat)) {
          f.z = waterSurfZ(fc) + wave.u * 1.1;
        }
        if (f.y > 820 || flow.speed < 0.8 || !fc || !isWetMat(fc.mat)) {
          f.life -= dt * 1.2;
        }
        if (f.life <= 0) floatingItems.splice(i, 1);
      }

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        const w = sampleWind(p.x, p.y, fluidTime);
        p.vx += w.wx * (p.isLeaf ? 26 : 18) * dt;
        p.vy += w.wy * (p.isLeaf ? 26 : 18) * dt;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vz -= (p.grav !== undefined ? p.grav : 260) * dt;
        if (p.isLeaf && p.vz < -16) p.vz = -16;
        p.z += p.vz * dt;
        p.life -= dt;

        const pc = getCellAt(p.x, p.y);
        if (pc && isWetMat(pc.mat) && p.z <= waterSurfZ(pc) + 0.5) {
          const isSplashDrop = p.color === '#93C5FD' || p.color === '#FFFFFF' || p.color === '#7DD3FC' || p.color === '#67E8F9' || p.color === '#E0F2FE';
          if (!isSplashDrop && floatingItems.length < 64) {
            spawnFloatingPetal(p.x, p.y, p.color, waterSurfZ(pc));
          }
          injectWaterRipple(p.x, p.y, isSplashDrop ? 0.55 : 0.35, 1);
          particles.splice(i, 1);
          continue;
        }
        if (p.isLeaf && pc && !isWetMat(pc.mat) && p.z < pc.h + 0.4) {
          p.z = pc.h + 0.4;
          p.vx *= 0.85;
          p.vy *= 0.85;
          p.vz = 0;
          p.life = Math.min(p.life, 0.35);
        }

        if (p.life <= 0) particles.splice(i, 1);
      }

      // Pickups de Ferramentas (14u)
      for (let i = 0; i < toolPickups.length; i++) {
        const pk = toolPickups[i];
        const dist = Math.hypot(cat.x - pk.wx, cat.y - pk.wy);
        const dz = Math.abs(cat.z - pk.baseZ);
        if (dist < 14 && dz < 16) {
          if (!pk.inside && equippedTool !== pk.toolId) {
            equipTool(pk.toolId);
            sfxBiome();
            spawnParticles(pk.wx, pk.wy, pk.baseZ + 8, 10, ['#FDE68A', '#FFFFFF', '#94A3B8'], 28);
          }
          pk.inside = true;
        } else {
          pk.inside = false;
        }
      }

      // HitFlash decay nos destrutíveis
      for (let i = 0; i < props.length; i++) {
        const d = props[i].destr;
        if (d && d.hitFlash > 0) d.hitFlash = Math.max(0, d.hitFlash - dt);
      }

      // Corpos caindo: pêndulo invertido 3D ('chop')
      for (let i = fallingBodies.length - 1; i >= 0; i--) {
        const fb = fallingBodies[i];
        const L = Math.max(20, (fb.model.count - fb.zCut) * fb.scale);
        const alpha = (3 * GRAVITY / (2 * L * 18)) * Math.sin(fb.phi);
        fb.omega += alpha * dt;
        fb.phi += fb.omega * dt;

        const sinP = Math.sin(fb.phi);
        const cosP = Math.cos(fb.phi);
        const tipX = fb.wx + L * sinP * fb.dx;
        const tipY = fb.wy + L * sinP * fb.dy;
        const tipZ = fb.baseZ + fb.zCut * fb.scale + L * cosP;
        const groundH = getHeightAt(tipX, tipY);
        const effGroundH = groundH !== null ? groundH : fb.baseZ;

        if (fb.phi >= Math.PI * 0.48 || tipZ <= effGroundH) {
          shakeTimer = 0.18;
          shakeMag = 3.2;
          sfxCrumble();
          injectWindImpulse(tipX, tipY, fb.dx * 3.0, fb.dy * 3.0, 56, 0.8);

          for (const frac of [0.35, 0.65, 0.9]) {
            const bx = fb.wx + L * frac * sinP * fb.dx;
            const by = fb.wy + L * frac * sinP * fb.dy;
            const bz = Math.max(fb.baseZ + fb.zCut * fb.scale + L * frac * cosP, (getHeightAt(bx, by) || 0) + 2);
            spawnParticles(bx, by, bz, 8, fb.colors, 42, { isLeaf: true, grav: 48, vz: 24, life: 1.8 });
          }

          for (const frac of [0.5, 0.85]) {
            const ix = fb.wx + L * frac * sinP * fb.dx;
            const iy = fb.wy + L * frac * sinP * fb.dy;
            const ic = getCellAt(ix, iy);
            if (ic && isWetMat(ic.mat)) {
              injectWaterRipple(ix, iy, 2.4, 3);
              spawnParticles(ix, iy, waterSurfZ(ic) + 1, 10, ['#93C5FD', '#FFFFFF', '#E0F2FE'], 36);
            }
          }

          for (let k = 0; k < fb.drops; k++) {
            const frac = 0.25 + ((k + 0.5) / fb.drops) * 0.65;
            const dxPos = fb.wx + L * frac * sinP * fb.dx;
            const dyPos = fb.wy + L * frac * sinP * fb.dy;
            const dzPos = fb.baseZ + fb.zCut * fb.scale + L * frac * cosP;
            const dropZ = Math.max(dzPos, (getHeightAt(dxPos, dyPos) || 0) + 4);
            spawnDebrisDrops(dxPos, dyPos, dropZ, fb.dropKey || 'wood_log', 1, fb.dx, fb.dy, 75, 120);
          }

          fallingBodies.splice(i, 1);
        }
      }

      // Drops balísticos (toras & pedregulhos) + empurrão do gatinho + correnteza + Arquimedes local
      for (let i = debrisDrops.length - 1; i >= 0; i--) {
        const dr = debrisDrops[i];
        if (!dr.persistent) dr.life -= dt;
        if (dr.life <= 0) {
          debrisDrops.splice(i, 1);
          continue;
        }
        if (dr.inWater) {
          const flow = sampleWaterFlow(dr.x, dr.y);
          const wave = sampleWaveHeightAndGrad(dr.x, dr.y);
          const drWind = sampleWind(dr.x, dr.y, fluidTime);
          const isHeavy = dr.modelKey === 'stone_chunk';
          dr.vx = (isHeavy ? flow.vx * 0.25 : flow.vx + drWind.wx * 3.2 - wave.gx * 28);
          dr.vy = (isHeavy ? flow.vy * 0.25 : flow.vy + drWind.wy * 3.2 - wave.gy * 28);
          dr.x += dr.vx * dt;
          dr.y += dr.vy * dt;
          dr.selfAngle += dt * (isHeavy ? 0.1 : 0.6 + wave.gx * 0.8);
          const dc = getCellAt(dr.x, dr.y);
          if (dc && isWetMat(dc.mat)) {
            let subVol = 1.0;
            if (isHeavy) {
              // Pedregulho (densidade > 1): afunda até o leito deslocando seu volume inteiro
              dr.vz -= 180 * dt;
              dr.z = Math.max(dc.h, dr.z + dr.vz * dt);
              if (dr.z <= dc.h + 0.1) { dr.vz = 0; dr.vx *= 0.2; dr.vy *= 0.2; }
            } else {
              // Tora (densidade < 1): Empuxo de Arquimedes acoplado ao WaveBuffer + nível local
              const baseSurfZ = waterSurfZ(dc);
              const surfZ = baseSurfZ + getLocalArchimedesRise(dr.x, dr.y, baseSurfZ) + wave.u * 1.4;
              subVol = Math.max(0, Math.min(1.5, (surfZ - dr.z + 1.5) / 3.0));
              const az = (subVol * 1.85 - 1.0) * 180 - dr.vz * 4.5;
              dr.vz += az * dt;
              dr.z += dr.vz * dt;
            }
            const dVol = subVol - (dr._prevSubVol || 0);
            if (Math.abs(dVol) > 0.06) {
              injectWaterRipple(dr.x, dr.y, Math.max(-0.85, Math.min(0.85, dVol * 0.95)), 1);
            }
            dr._prevSubVol = subVol;
          } else {
            if (dr._prevSubVol) {
              injectWaterRipple(dr.x, dr.y, -dr._prevSubVol * 0.8, 1);
              dr._prevSubVol = 0;
            }
            dr.inWater = false;
          }
          if (!dc || dr.y > 860) dr.life = Math.min(dr.life, 0.5);
        } else {
          // Gatinho empurra troncos/pedras na margem para dentro da água!
          const dCatDr = Math.hypot(dr.x - cat.x, dr.y - cat.y);
          if (dCatDr < 11 && dCatDr > 0.01 && Math.abs(dr.z - cat.z) < 8) {
            const nx = (dr.x - cat.x) / dCatDr;
            const ny = (dr.y - cat.y) / dCatDr;
            const pushSpd = cat.isWalking ? 64 : 26;
            dr.vx = nx * pushSpd;
            dr.vy = ny * pushSpd;
            dr.spin = (Math.random() - 0.5) * 3.0;
          }
          dr.vz -= GRAVITY * 0.45 * dt;
          dr.x += dr.vx * dt;
          dr.y += dr.vy * dt;
          dr.z += dr.vz * dt;
          dr.selfAngle += dr.spin * dt;
          const dc = getCellAt(dr.x, dr.y);
          if (!dc) {
            debrisDrops.splice(i, 1);
            continue;
          }
          if (isWetMat(dc.mat) && dr.z <= waterSurfZ(dc) + 0.5) {
            dr.inWater = true;
            dr.z = waterSurfZ(dc);
            dr.vz = 0;
            const flow = sampleWaterFlow(dr.x, dr.y);
            dr.vx = flow.vx;
            dr.vy = flow.vy;
            injectWaterRipple(dr.x, dr.y, 1.4, 2);
            spawnParticles(dr.x, dr.y, dr.z + 1, 6, ['#93C5FD', '#FFFFFF'], 24);
            if (Math.hypot(dr.x - cat.x, dr.y - cat.y) < 140) {
              guideSpeak('archimedes', 'Eureka! A água desloca! 🛁', 135);
            }
          } else if (!isWetMat(dc.mat) && dr.z <= dc.h) {
            dr.z = dc.h;
            if (Math.abs(dr.vz) > 28 && dr.bounces < 3) {
              dr.vz = -dr.vz * 0.45;
              dr.vx *= 0.65;
              dr.vy *= 0.65;
              dr.spin *= 0.6;
              dr.bounces++;
            } else {
              dr.vz = 0;
              const damp = Math.max(0, 1 - dt * 8);
              dr.vx *= damp;
              dr.vy *= damp;
              dr.spin = 0;
            }
          }
        }
      }

      updateFoliage(dt);

      const lerpFactor = Math.min(1, dt * 9.0);
      camX += (cat.x - camX) * lerpFactor;
      camY += (cat.y - camY) * lerpFactor;
      camZ += (cat.groundZ + (cat.z - cat.groundZ) * 0.45 - camZ) * Math.min(1, dt * 6.5);

      syncWaveOrigin();
      stepFlowStreaks(dt);
      waveAccum += dt;
      while (waveAccum >= 1 / 30) {
        waveAccum -= 1 / 30;
        // Micro-impulsos sutis de onda de proa e flancos de cisalhamento nos obstáculos do rio
        const wObs = cachedWaterObstaclesNoCat;
        for (let i = 0; i < wObs.length; i++) {
          const o = wObs[i];
          if (Math.hypot(o.wx - camX, o.wy - camY) > 420) continue;
          const baseF = sampleBaseWaterFlow(o.wx, o.wy);
          if (baseF.speed > 2 && Math.random() < 0.28) {
            const ux = baseF.vx / baseF.speed;
            const uy = baseF.vy / baseF.speed;
            const px = -uy;
            const py = ux;
            const pick = Math.random();
            let wxWake, wyWake;
            if (pick < 0.4) {
              wxWake = o.wx - ux * (o.r + 1.5) + px * (Math.random() - 0.5) * o.r * 0.4;
              wyWake = o.wy - uy * (o.r + 1.5) + py * (Math.random() - 0.5) * o.r * 0.4;
            } else {
              const side = pick < 0.7 ? 1 : -1;
              wxWake = o.wx + px * side * (o.r + 1.5) + ux * (Math.random() - 0.2) * 3.0;
              wyWake = o.wy + py * side * (o.r + 1.5) + uy * (Math.random() - 0.2) * 3.0;
            }
            const wc = getCellAt(wxWake, wyWake);
            if (wc && isWetMat(wc.mat)) {
              injectWaterRipple(wxWake, wyWake, 0.22, 1);
              if (Math.random() < 0.35) {
                spawnParticles(wxWake, wyWake, waterSurfZ(wc) + 0.4, 1, ['#E0F2FE', '#FFFFFF'], 10, { grav: 40, vz: 6, life: 0.40 });
              }
            }
          }
        }
        stepWaterfallSim(1 / 30, true);
        stepWaveBuffer();
      }
      stepThermodynamics(dt);
      stepVerletChains(dt);
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
            const talus = mat === MAT_SAND ? 2 : 3;
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

    // 1. Varal de bandeirinhas na Vila (entre Cabana 2 e o toco/poste)
    createVerletChain(-214, 210, 34, -262, 153, 22, 14, { pinEnd: true, segLen: 5.8, windScale: 1.35, kind: 'garland' });
    // 2. Fitas do Portal Torii no Jardim Zen
    createVerletChain(-458, -405, 58, -458, -405, 42, 8, { pinEnd: false, segLen: 2.2, windScale: 1.5, kind: 'banner', colors: ['#EF4444', '#FFFDF7'] });
    createVerletChain(-412, -405, 58, -412, -405, 42, 8, { pinEnd: false, segLen: 2.2, windScale: 1.5, kind: 'banner', colors: ['#EF4444', '#FFFDF7'] });
    // 3. Flâmula no topo do Farol da Praia
    createVerletChain(-714, 822, 122, -692, 822, 120, 10, { pinEnd: false, segLen: 2.4, windScale: 2.1, kind: 'banner', colors: ['#F97316', '#FACC15'] });
    // 4. Cipó pendente na Árvore Sakura do Pico
    createVerletChain(468, -576, 62, 468, -576, 40, 9, { pinEnd: false, segLen: 2.6, windScale: 1.4, kind: 'vine', colors: ['#F472B6', '#4ADE80'] });

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

      // Fontes de calor (campfires) + interação com o gatinho
      for (let i = 0; i < props.length; i++) {
        const p = props[i];
        if (p.destroyed || p.modelKey !== 'campfire') continue;
        const dCat = Math.hypot(cat.x - p.wx, cat.y - p.wy);
        if (dCat < 10.5 && cat.z <= p.wz + 14) {
          // Empurra radialmente para fora do colisor sólido (r=7.2 + pad=3.0) para nunca travar em cima
          const nx = dCat > 0.1 ? (cat.x - p.wx) / dCat : 0;
          const ny = dCat > 0.1 ? (cat.y - p.wy) / dCat : 1;
          const safeDist = 12.0;
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
        const cool = 0.22;
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

