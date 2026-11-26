    // =========================================================================
    // 11. MINIMAPA TOPOGRÁFICO ORGÂNICO (1080×1080 passo 9 -> 120×120)
    // =========================================================================
    const mmCanvas = document.getElementById('minimapCanvas');
    const mmCtx = mmCanvas.getContext('2d');
    const MM_RES = 120;
    const mmBase = document.createElement('canvas');
    mmBase.width = MM_RES;
    mmBase.height = MM_RES;
    const mmBaseCtx = mmBase.getContext('2d');

    function bakeMinimapBase() {
      const img = mmBaseCtx.createImageData(MM_RES, MM_RES);
      const buf = new Uint32Array(img.data.buffer);
      for (let gy = 0; gy < MM_RES; gy++) {
        const my = gy * 9;
        for (let gx = 0; gx < MM_RES; gx++) {
          const mx = gx * 9;
          const idx = my * mw + mx;
          const h = hmap[idx];
          const mat = matMap[idx];
          const hL = mx >= 9 ? hmap[my * mw + (mx - 9)] : h;
          const hU = my >= 9 ? hmap[(my - 9) * mw + mx] : h;
          const isContour = !isWetMat(mat) && mat !== MAT_BRIDGE &&
            (Math.floor(h / 10) !== Math.floor(hL / 10) || Math.floor(h / 10) !== Math.floor(hU / 10));

          let rgb;
          if (mat === MAT_WATER) rgb = [56, 189, 248];
          else if (mat === MAT_SHALLOW) rgb = [103, 232, 249];
          else if (mat === MAT_LILYPAD) rgb = [34, 197, 94];
          else if (mat === MAT_BRIDGE) rgb = [185, 122, 74];
          else if (mat === MAT_SAND) rgb = [243, 221, 169];
          else if (mat === MAT_PEAK || h >= 62) rgb = [244, 114, 182];
          else if (h >= 46) rgb = [156, 163, 175];
          else if (h >= 28) rgb = [148, 163, 184];
          else if (h >= 14) rgb = [78, 169, 76];
          else if (mat === MAT_PATH) rgb = [223, 182, 132];
          else rgb = [101, 196, 102];

          buf[gy * MM_RES + gx] = isContour
            ? packRGBA(Math.round(rgb[0] * 0.78), Math.round(rgb[1] * 0.78), Math.round(rgb[2] * 0.78))
            : packRGBA(rgb[0], rgb[1], rgb[2]);
        }
      }
      mmBaseCtx.putImageData(img, 0, 0);
      const toMm = (w) => (w / VOX + HALF_GRID) * (MM_RES / mw);
      mmBaseCtx.fillStyle = '#B97A4A';
      for (const br of bridges) {
        const x0 = Math.floor(toMm(br.xMin));
        const y0 = Math.floor(toMm(br.yMin));
        const bw = Math.max(2, Math.ceil(toMm(br.xMax) - x0));
        const bh = Math.max(2, Math.ceil(toMm(br.yMax) - y0));
        mmBaseCtx.fillRect(x0, y0, bw, bh);
      }
    }
    bakeMinimapBase();

    function drawMinimap() {
      mmCtx.imageSmoothingEnabled = false;
      mmCtx.drawImage(mmBase, 0, 0, 120, 120);

      const toMm = (w) => (w / VOX + HALF_GRID) * (120 / mw);

      for (const f of fishes) {
        if (f.collected) continue;
        mmCtx.fillStyle = '#FACC15';
        mmCtx.fillRect(Math.round(toMm(f.wx)) - 1, Math.round(toMm(f.wy)) - 1, 3, 3);
      }

      for (const npc of npcs) {
        mmCtx.fillStyle = '#FDBA74';
        mmCtx.fillRect(Math.round(toMm(npc.x)) - 1, Math.round(toMm(npc.y)) - 1, 3, 3);
      }

      const cx = toMm(cat.x);
      const cy = toMm(cat.y);
      mmCtx.fillStyle = '#EF4444';
      mmCtx.beginPath();
      mmCtx.arc(cx, cy, 3, 0, Math.PI * 2);
      mmCtx.fill();
      mmCtx.strokeStyle = '#FFFFFF';
      mmCtx.lineWidth = 1;
      mmCtx.stroke();

      const fx = -Math.sin(cat.selfAngle);
      const fy = Math.cos(cat.selfAngle);
      mmCtx.beginPath();
      mmCtx.moveTo(cx, cy);
      mmCtx.lineTo(cx + fx * 6, cy + fy * 6);
      mmCtx.strokeStyle = '#7F1D1D';
      mmCtx.lineWidth = 1.5;
      mmCtx.stroke();
    }

    // =========================================================================
    // 12. LOOP PRINCIPAL + TELEMETRIA FPS & HOOKS DE DEBUG/TESTE
    // =========================================================================
    let lastTime = performance.now();
    let fpsAccum = 0;
    let fpsFrames = 0;
    let currentFps = 60;

    function loop(now) {
      const rawDt = Math.max(0.001, (now - lastTime) / 1000);
      lastTime = now;
      fpsAccum += rawDt;
      fpsFrames++;
      if (fpsAccum >= 0.5) {
        currentFps = Math.round(fpsFrames / fpsAccum);
        fpsAccum = 0;
        fpsFrames = 0;
      }

      const dt = Math.min(0.05, rawDt);
      updatePhysics(dt);
      renderScene();
      drawMinimap();
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

    window.__TERRAIN_DEBUG__ = {
      getState: () => ({
        fps: currentFps,
        startupMs: STARTUP_MS,
        x: cat.x, y: cat.y, z: cat.z, vz: cat.vz,
        groundZ: cat.groundZ, onGround: cat.onGround,
        hurtTimer: cat.hurtTimer,
        selfAngle: cat.selfAngle, turn,
        maxJumpReached: cat.maxJumpReached,
        obstacleHint: cat.obstacleHint,
        obstacleLabel: cat.obstacleLabel,
        speech: cat.speech ? cat.speech.text : null,
        collectedFish: fishes.filter(f => f.collected).length,
        visitedBiomes: Array.from(visitedBiomes),
        viewport: { viewW, viewH, LOW_W, LOW_H, pixelScale, dpr }
      }),
      setCatWorld: (wx, wy, z = null) => {
        teleportToWorld(wx, wy, null, z);
      },
      getHeightAt: (wx, wy) => getHeightAt(wx, wy),
      getCellAt: (wx, wy) => getCellAt(wx, wy),
      isStandable: (wx, wy) => { const c = getCellAt(wx, wy); return c ? c.standable : false; },
      getCliffTop: (wx, wy) => { const c = getCellAt(wx, wy); return c ? c.cliffTop : null; },
      sampleTrail: (pts) => pts.map(([x, y]) => ({ x, y, h: getHeightAt(x, y), standable: (getCellAt(x, y) || {}).standable })),
      getBridgeAt: (wx, wy) => getBridgeAt(wx, wy),
      getBridgeDeckZ: (br, wx, wy) => getBridgeDeckZ(br, wx, wy),
      getBridges: () => bridges,
      getFishes: () => fishes,
      getRuinsCoords: () => ({
        approachSouth: { wx: -285, wy: 562, z: getHeightAt(-285, 562) },
        monoliths: [
          { name: 'A', wx: -420, wy: 495, halfW: 30, halfD: 26, targetZ: 6,  topZ: getHeightAt(-420, 495), southApproach: { wx: -420, wy: 562, z: getHeightAt(-420, 562) } },
          { name: 'B', wx: -285, wy: 495, halfW: 30, halfD: 26, targetZ: 16, topZ: getHeightAt(-285, 495), southApproach: { wx: -285, wy: 562, z: getHeightAt(-285, 562) } },
          { name: 'C', wx: -150, wy: 495, halfW: 30, halfD: 26, targetZ: 32, topZ: getHeightAt(-150, 495), southApproach: { wx: -150, wy: 562, z: getHeightAt(-150, 562) } },
          { name: 'D', wx: -15,  wy: 495, halfW: 30, halfD: 26, targetZ: 48, topZ: getHeightAt(-15,  495), southApproach: { wx: -15,  wy: 562, z: getHeightAt(-15,  562) } }
        ]
      }),
      setTurn: (rad) => { turn = rad; targetTurn = rad; },
      triggerJump: () => { cat.jumpBuffer = 0.14; },
      speak: (text) => { catSpeak(text, 240); },
      sampleWind: (wx, wy, t = fluidTime) => sampleWind(wx, wy, t),
      sampleWaterFlow: (wx, wy) => sampleWaterFlow(wx, wy),
      getWaterfallSplitStats: () => getWaterfallSplitStats(),
      getStreamlineStats: () => {
        let total = 0;
        let deflectedCount = 0;
        for (let i = 0; i < flowStreaks.length; i++) {
          const s = flowStreaks[i];
          if (s.hLen > 0) {
            total++;
            if (s.deflect > 0.18) deflectedCount++;
          }
        }
        return {
          total,
          deflectedCount,
          obsCount: cachedWaterObstacles.length,
          obsPositions: cachedWaterObstacles.map(o => ({ wx: o.wx, wy: o.wy, r: o.r, isCat: !!o.isCat }))
        };
      },
      getShallowState: () => {
        const c = getCellAt(cat.x, cat.y);
        const br = getBridgeAt(cat.x, cat.y);
        const onBr = br && cat.z >= getBridgeDeckZ(br, cat.x, cat.y) - AUTO_STEP_MAX - 1;
        return {
          inShallow: !!(c && c.mat === MAT_SHALLOW && !onBr && cat.onGround),
          mat: c ? c.mat : null,
          pos: { x: cat.x, y: cat.y, z: cat.z },
          hurtTimer: cat.hurtTimer
        };
      },
      injectWaterRipple: (wx, wy, strength = 1.0, radiusCells = 2) => injectWaterRipple(wx, wy, strength, radiusCells),
      injectWindImpulse: (wx, wy, vx, vy, r = 42, life = 0.75) => injectWindImpulse(wx, wy, vx, vy, r, life),
      getFluidStats: () => ({
        floatingCount: floatingItems.length,
        activeImpulses: windImpulses.length,
        windAtCat: sampleWind(cat.x, cat.y, fluidTime)
      }),
      getWaveStats: () => {
        let sum = 0, max = 0, nan = 0;
        for (let i = 0; i < waveCurr.length; i++) {
          const v = waveCurr[i];
          if (Number.isNaN(v)) nan++;
          const a = Math.abs(v);
          sum += a;
          if (a > max) max = a;
        }
        return { sum, max, nan };
      },
      stepFluidForTest: (dt) => {
        syncWaveOrigin();
        injectWaterRipple(cat.x, cat.y, 0, 0);
        updatePhysics(dt);
      },
      getPropsByType: (key) => props.filter(p => p.modelKey === key).map(p => ({
        id: p.id, modelKey: p.modelKey, wx: p.wx, wy: p.wy, wz: p.wz, topZ: p.topZ,
        destroyed: !!p.destroyed,
        renderMaxSlice: p.renderMaxSlice !== undefined ? p.renderMaxSlice : null,
        destr: p.destr ? { hp: p.destr.hp, maxHp: p.destr.maxHp, chopped: p.destr.chopped, mode: p.destr.mode } : null
      })),
      getFoliageState: () => foliageProps.filter(p => !p.destroyed && p.foliage).map(p => ({
        id: p.id, key: p.modelKey, wx: p.wx, wy: p.wy,
        bx: +(p.bx || 0).toFixed(3), by: +(p.by || 0).toFixed(3),
        r: p.foliage.pushRadius
      })),
      triggerAction: () => triggerAction(),
      equipTool: (toolId, quiet = true) => equipTool(toolId, quiet),
      getDestructionStats: () => ({
        ...destructStats,
        fallingCount: fallingBodies.length,
        dropCount: debrisDrops.length,
        equippedTool
      })
    };
