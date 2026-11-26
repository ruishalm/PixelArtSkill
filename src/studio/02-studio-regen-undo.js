    // =========================================================================
    // VOXEL 3D STUDIO — UNDO/REDO & REGENERAÇÃO PROCEDURAL / HÍBRIDA
    // =========================================================================
    (function initStudioRegenAndUndo() {
      const S = window.__STUDIO__;
      if (!document.getElementById('studioOverlay') || !S) return;

      const {
        pinnedMask, sculptH, syncSculptFromHmap,
        clearAllProps, resetTerrainLayers,
        undoStack, redoStack,
        baseKindSel, genModeSel
      } = S;

      function makeSnapshot() {
        return {
          h: new Float32Array(sculptH),
          m: new Uint8Array(matMap),
          p: new Uint8Array(pinnedMask),
          props: props.filter(p => !p.destroyed).map(p => ({
            modelKey: p.modelKey, wx: p.wx, wy: p.wy, liftZ: p.wz,
            angle: p.selfAngle, scale: p.scale, pinned: !!p.pinned
          }))
        };
      }

      function restoreSnapshot(snap) {
        sculptH.set(snap.h);
        for (let i = 0; i < hmap.length; i++) hmap[i] = Math.round(sculptH[i]);
        matMap.set(snap.m);
        pinnedMask.set(snap.p);
        if (Array.isArray(snap.props)) {
          clearAllProps();
          for (const sp of snap.props) {
            const before = props.length;
            addProp(sp.modelKey, sp.wx, sp.wy, {
              allowOnPath: true, allowInWater: true,
              liftZ: sp.liftZ, angle: sp.angle, scale: sp.scale
            });
            if (props.length > before) props[props.length - 1].pinned = !!sp.pinned;
          }
        }
        if (typeof buildStandableMap === 'function') buildStandableMap();
        bakeTerrainSlices();
        bakeMinimapBase();
      }

      function pushUndoSnapshot(clearRedo = true) {
        if (undoStack.length >= 12) undoStack.shift();
        undoStack.push(makeSnapshot());
        if (clearRedo) redoStack.length = 0;
      }

      function popUndoSnapshot() {
        const snap = undoStack.pop();
        if (!snap) return;
        if (redoStack.length >= 12) redoStack.shift();
        redoStack.push(makeSnapshot());
        restoreSnapshot(snap);
      }

      function popRedoSnapshot() {
        const snap = redoStack.pop();
        if (!snap) return;
        if (undoStack.length >= 12) undoStack.shift();
        undoStack.push(makeSnapshot());
        restoreSnapshot(snap);
      }

      // 5. Terreno Procedural Genérico do Studio (sem mapa hardcodado do Vale Felino)
      function generateProceduralStudioTerrain(seed, baseKind = (baseKindSel ? baseKindSel.value : 'island')) {
        setWorldSeed(seed);
        document.getElementById('seedInput').value = WORLD_SEED;
        if (typeof bridges !== 'undefined') bridges.length = 0;
        if (typeof npcs !== 'undefined') npcs.length = 0;
        if (typeof fishes !== 'undefined') fishes.length = 0;

        if (baseKind === 'flat') {
          hmap.fill(0);
          matMap.fill(MAT_GRASS);
          return;
        }

        const fs = 1080 / mw; // mantém o "tamanho" das feições: diorama pequeno mostra o relevo inteiro
        for (let my = 0; my < mh; my++) {
          const wy = (my - HALF_GRID) * VOX;
          for (let mx = 0; mx < mw; mx++) {
            const wx = (mx - HALF_GRID) * VOX;
            const idx = my * mw + mx;
            const nBase = fbm2d(wx * 0.0022 * fs, wy * 0.0022 * fs);
            const nRidge = ridgedFbm(wx * 0.0018 * fs + 19.3, wy * 0.0018 * fs - 7.1, 3);
            let h;
            if (baseKind === 'continental') {
              const nVal = fbm2d(wx * 0.0014 * fs - 11.7, wy * 0.0014 * fs + 5.3);
              h = nBase * 20 + nRidge * 28 + nVal * 12 - 2;
            } else {
              const distEdge = Math.max(Math.abs(wx), Math.abs(wy)) / HALF_WORLD;
              const islandMask = Math.max(0, 1 - Math.pow(distEdge, 3.2));
              h = (nBase * 24 + nRidge * 28 - 4) * islandMask - (1 - islandMask) * 6;
            }
            h = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX, h));
            hmap[idx] = h;
            if (h <= -3.5) matMap[idx] = MAT_WATER;
            else if (h <= -0.8) matMap[idx] = MAT_SHALLOW;
            else if (h <= (baseKind === 'continental' ? 0.6 : 2.2)) matMap[idx] = MAT_SAND;
            else if (h >= 42) matMap[idx] = MAT_PEAK;
            else matMap[idx] = MAT_GRASS;
          }
        }
      }

      // 6. Regeneração Total vs Híbrida (preserva áreas e props fixos)
      function regenWorld(newSeed, preservePinned, baseKindOverride = null) {
        const baseKind = baseKindOverride || (baseKindSel ? baseKindSel.value : 'island');
        const genMode = genModeSel ? genModeSel.value : 'hybrid';
        let savedH = null, savedM = null, savedProps = null;
        if (preservePinned) {
          savedH = new Float32Array(hmap);
          savedM = new Uint8Array(matMap);
          savedProps = props.filter(p => p.pinned).map(p => ({
            modelKey: p.modelKey, wx: p.wx, wy: p.wy, angle: p.selfAngle, scale: p.scale
          }));
        } else {
          pinnedMask.fill(0);
          customWindVx.fill(0); customWindVy.fill(0);
          customFlowVx.fill(0); customFlowVy.fill(0);
        }

        generateProceduralStudioTerrain(newSeed, baseKind);

        if (preservePinned && savedH) {
          for (let i = 0; i < hmap.length; i++) {
            if (pinnedMask[i] === 1) {
              hmap[i] = savedH[i];
              matMap[i] = savedM[i];
            }
          }
          // Transição suave de 3 células na borda das áreas fixas
          const copyH = new Float32Array(hmap);
          for (let y = 2; y < mh - 2; y++) {
            for (let x = 2; x < mw - 2; x++) {
              const i = y * mw + x;
              if (pinnedMask[i] === 1) continue;
              let nearPinned = 0;
              for (let dy = -2; dy <= 2; dy++) {
                for (let dx = -2; dx <= 2; dx++) {
                  if (pinnedMask[(y + dy) * mw + (x + dx)] === 1) nearPinned++;
                }
              }
              if (nearPinned > 0) {
                const avg = (copyH[i - 1] + copyH[i + 1] + copyH[i - mw] + copyH[i + mw]) * 0.25;
                hmap[i] = copyH[i] * 0.45 + avg * 0.55;
              }
            }
          }
        }

        if (typeof buildStandableMap === 'function') buildStandableMap();

        clearAllProps();
        resetTerrainLayers();

        // Espalha natureza procedural leve fora das áreas travadas (exceto Plano Vazio ou Tudo Fixo)
        if (baseKind !== 'flat' && genMode !== 'manual') {
          const rng = mulberry32((WORLD_SEED ^ 0x9E3779B9) >>> 0);
          const propCount = Math.max(8, Math.round(140 * (mw / 1080) * (mh / 1080)));
          const spread = HALF_WORLD * 0.72;
          for (let i = 0; i < propCount; i++) {
            const wx = (rng() * 2 - 1) * spread;
            const wy = (rng() * 2 - 1) * spread;
            const mx = Math.floor(wx / VOX + HALF_GRID);
            const my = Math.floor(wy / VOX + HALF_GRID);
            if (mx < 0 || my < 0 || mx >= mw || my >= mh) continue;
            if (pinnedMask[my * mw + mx] === 1) continue;
            const c = getCellAt(wx, wy);
            if (!c || isWetMat(c.mat) || c.h > 38) continue;
            const key = rng() < 0.55 ? 'pine_tree' : (rng() < 0.8 ? 'sakura_oak' : 'boulder_large');
            const before = props.length;
            addProp(key, wx, wy, { allowOnPath: false });
            if (props.length > before) props[props.length - 1].pinned = false;
          }
        }

        if (preservePinned && savedProps) {
          for (const sp of savedProps) {
            const before = props.length;
            addProp(sp.modelKey, sp.wx, sp.wy, { allowOnPath: true, angle: sp.angle, scale: sp.scale });
            if (props.length > before) props[props.length - 1].pinned = true;
          }
        }
        if (genMode === 'manual') {
          pinnedMask.fill(1);
          for (let i = 0; i < props.length; i++) props[i].pinned = true;
        }
        syncSculptFromHmap();
        if (typeof buildStandableMap === 'function') buildStandableMap();
        if (typeof initFlowStreaks === 'function') initFlowStreaks();

        bakeTerrainSlices();
        bakeMinimapBase();
      }

      function findSafeSpawnNear(wx, wy) {
        const isDry = (x, y) => {
          const br = getBridgeAt(x, y);
          if (br) return { x, y, z: getBridgeDeckZ(br, x, y) };
          const c = getCellAt(x, y);
          if (c && !isWetMat(c.mat) && c.standable) return { x, y, z: c.h };
          return null;
        };
        const direct = isDry(wx, wy);
        if (direct) return direct;
        for (let rad = VOX * 2; rad <= HALF_WORLD; rad += VOX * 3) {
          for (let a = 0; a < 16; a++) {
            const ang = (a / 16) * Math.PI * 2;
            const hit = isDry(wx + Math.cos(ang) * rad, wy + Math.sin(ang) * rad);
            if (hit) return hit;
          }
        }
        const c0 = getCellAt(wx, wy);
        return { x: wx, y: wy, z: c0 ? Math.max(0, c0.h) : 0 };
      }

      S.pushUndoSnapshot = pushUndoSnapshot;
      S.popUndoSnapshot = popUndoSnapshot;
      S.popRedoSnapshot = popRedoSnapshot;
      S.generateProceduralStudioTerrain = generateProceduralStudioTerrain;
      S.regenWorld = regenWorld;
      S.findSafeSpawnNear = findSafeSpawnNear;

      // Inicializa o Studio com terreno procedural neutro (sem o mapa hardcodado do Vale Felino)
      camX = 0; camY = 0;
      regenWorld(WORLD_SEED, false);
    })();
