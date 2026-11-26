    // =========================================================================
    // VOXEL 3D STUDIO CONTROLLER (EDITAR <-> TESTAR, PINCÉIS, VETORES, HÍBRIDO)
    // =========================================================================
    (function initStudio() {
      if (!document.getElementById('studioOverlay')) return;

      window.__STUDIO_EDIT_MODE__ = true;
      const overlay = document.getElementById('studioOverlay');
      const octx = overlay.getContext('2d');
      const pinnedMask = new Uint8Array(mw * mh);

      let activeTool = 'raise';
      let brushRadius = 16;
      let brushStrength = 1.2;
      let hoverWorld = null;
      let isPainting = false;
      let isOrbiting = false;
      let orbitLastX = 0;
      let flattenTargetZ = 0;
      let lastVecWorld = null;
      let selectionBox = null; // { x0, y0, x1, y1 } em coordenadas do mundo
      let selStartWorld = null;
      const undoStack = [];

      // Remoção segura de props: desativa colisores ligados ao prop e tira das listas da engine
      function removePropObj(p) {
        const i = props.indexOf(p);
        if (i >= 0) props.splice(i, 1);
        const fi = foliageProps.indexOf(p);
        if (fi >= 0) foliageProps.splice(fi, 1);
        if (p.solidCollider) p.solidCollider.disabled = true;
        if (p.platCollider) p.platCollider.disabled = true;
      }
      function clearAllProps() {
        props.length = 0;
        foliageProps.length = 0;
        propColliders.length = 0;
        platformColliders.length = 0;
        fallingBodies.length = 0;
        debrisDrops.length = 0;
      }
      function resetTerrainLayers() {
        shadowMask.fill(0);
        noGrassMask.fill(0);
        biomeMap.fill(0);
        cliffMask.fill(0);
      }

      function pushUndoSnapshot() {
        if (undoStack.length >= 12) undoStack.shift();
        undoStack.push({
          h: new Float32Array(hmap),
          m: new Uint8Array(matMap),
          p: new Uint8Array(pinnedMask)
        });
      }

      function popUndoSnapshot() {
        const snap = undoStack.pop();
        if (!snap) return;
        hmap.set(snap.h);
        matMap.set(snap.m);
        pinnedMask.set(snap.p);
        if (typeof buildStandableMap === 'function') buildStandableMap();
        bakeTerrainSlices();
        bakeMinimapBase();
      }

      // Garante que props iniciais possam ser diferenciados de props fixos do usuário
      for (let i = 0; i < props.length; i++) {
        props[i].pinned = false;
      }

      // 1. Picker 3D no Canvas usando unprojectToGrid + raymarch em Z
      function pickTerrainAtClient(clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return null;
        const px = (clientX - rect.left) / pixelScale;
        const py = (clientY - rect.top) / pixelScale;
        const cosA = Math.cos(turn);
        const sinA = Math.sin(turn);

        for (let z = TERRAIN_Z_MAX; z >= Z_MIN; z -= 1.0) {
          const g = unprojectToGrid(px, py, z, cosA, sinA);
          const wx = (g.gx - HALF_GRID) * VOX;
          const wy = (g.gy - HALF_GRID) * VOX;
          if (wx < WORLD_MIN || wx >= WORLD_MAX || wy < WORLD_MIN || wy >= WORLD_MAX) continue;
          const h = getHeightAt(wx, wy);
          if (h !== null && z <= h + 0.5) {
            return { wx, wy, z: h, gx: g.gx, gy: g.gy };
          }
        }
        const g0 = unprojectToGrid(px, py, 0, cosA, sinA);
        return {
          wx: Math.max(WORLD_MIN, Math.min(WORLD_MAX - 1, (g0.gx - HALF_GRID) * VOX)),
          wy: Math.max(WORLD_MIN, Math.min(WORLD_MAX - 1, (g0.gy - HALF_GRID) * VOX)),
          z: 0,
          gx: g0.gx,
          gy: g0.gy
        };
      }

      // 2. Aplicação dos pincéis de terreno, material, vento, correnteza e pin
      function applyTerrainBrush(wx, wy, isInitialClick) {
        const cx = Math.floor(wx / VOX + HALF_GRID);
        const cy = Math.floor(wy / VOX + HALF_GRID);
        const rCells = Math.max(1, Math.round(brushRadius / VOX));
        const mx0 = Math.max(1, cx - rCells - 1);
        const mx1 = Math.min(mw - 2, cx + rCells + 1);
        const my0 = Math.max(1, cy - rCells - 1);
        const my1 = Math.min(mh - 2, cy + rCells + 1);

        if (activeTool === 'flatten' && isInitialClick) {
          const c = getCellAt(wx, wy);
          flattenTargetZ = c ? c.h : 0;
        }

        let terrainDirty = false;
        const r2 = rCells * rCells;

        for (let my = my0; my <= my1; my++) {
          const dy = my - cy;
          for (let mx = mx0; mx <= mx1; mx++) {
            const dx = mx - cx;
            const d2 = dx * dx + dy * dy;
            if (d2 > r2) continue;
            const idx = my * mw + mx;
            const falloff = 1 - Math.sqrt(d2) / (rCells + 0.001);
            const w = falloff * falloff * (3 - 2 * falloff);

            if (activeTool === 'raise') {
              hmap[idx] = Math.min(TERRAIN_Z_MAX, hmap[idx] + brushStrength * 1.4 * w);
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool === 'lower') {
              hmap[idx] = Math.max(Z_MIN, hmap[idx] - brushStrength * 1.4 * w);
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool === 'flatten') {
              hmap[idx] = hmap[idx] + (flattenTargetZ - hmap[idx]) * Math.min(1, 0.35 * brushStrength * w);
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool === 'smooth') {
              const avg = (hmap[idx - 1] + hmap[idx + 1] + hmap[idx - mw] + hmap[idx + mw]) * 0.25;
              hmap[idx] = hmap[idx] + (avg - hmap[idx]) * Math.min(1, 0.45 * brushStrength * w);
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool.startsWith('mat_')) {
              let m = MAT_GRASS;
              if (activeTool === 'mat_sand') m = MAT_SAND;
              else if (activeTool === 'mat_peak') m = MAT_PEAK;
              else if (activeTool === 'mat_path') m = MAT_PATH;
              else if (activeTool === 'mat_water') {
                m = MAT_WATER;
                if (hmap[idx] > -4) hmap[idx] = -4;
              } else if (activeTool === 'mat_shallow') {
                m = MAT_SHALLOW;
                if (hmap[idx] > -1) hmap[idx] = -1;
              }
              matMap[idx] = m;
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool === 'pin') {
              pinnedMask[idx] = 1;
            } else if (activeTool === 'unpin') {
              pinnedMask[idx] = 0;
            } else if (activeTool === 'eraser') {
              hmap[idx] = 0;
              matMap[idx] = MAT_GRASS;
              pinnedMask[idx] = 0;
              terrainDirty = true;
            }
          }
        }

        if (activeTool === 'eraser') {
          const gcx = (wx / VOX + HALF_GRID) / FLOW_GRID_STEP;
          const gcy = (wy / VOX + HALF_GRID) / FLOW_GRID_STEP;
          const rGrid = Math.max(1.5, (brushRadius / VOX) / FLOW_GRID_STEP);
          for (let gy = Math.max(0, Math.floor(gcy - rGrid)); gy <= Math.min(FLOW_GRID_W - 1, Math.ceil(gcy + rGrid)); gy++) {
            for (let gx = Math.max(0, Math.floor(gcx - rGrid)); gx <= Math.min(FLOW_GRID_W - 1, Math.ceil(gcx + rGrid)); gx++) {
              if (Math.hypot(gx - gcx, gy - gcy) <= rGrid) {
                const vi = gy * FLOW_GRID_W + gx;
                customWindVx[vi] = 0; customWindVy[vi] = 0;
                customFlowVx[vi] = 0; customFlowVy[vi] = 0;
              }
            }
          }
          for (let i = props.length - 1; i >= 0; i--) {
            if (Math.hypot(props[i].wx - wx, props[i].wy - wy) <= brushRadius) {
              removePropObj(props[i]);
            }
          }
        }

        if (terrainDirty) {
          rebakeTerrainDirtyRect(mx0 - 1, my0 - 1, mx1 + 1, my1 + 1);
          bakeMinimapBase();
        }
      }

      function applyVectorBrush(wx, wy) {
        const gcx = (wx / VOX + HALF_GRID) / FLOW_GRID_STEP;
        const gcy = (wy / VOX + HALF_GRID) / FLOW_GRID_STEP;
        const rGrid = Math.max(1.5, (brushRadius / VOX) / FLOW_GRID_STEP);
        const gx0 = Math.max(0, Math.floor(gcx - rGrid));
        const gx1 = Math.min(FLOW_GRID_W - 1, Math.ceil(gcx + rGrid));
        const gy0 = Math.max(0, Math.floor(gcy - rGrid));
        const gy1 = Math.min(FLOW_GRID_W - 1, Math.ceil(gcy + rGrid));

        if (activeTool === 'vec_erase') {
          for (let gy = gy0; gy <= gy1; gy++) {
            for (let gx = gx0; gx <= gx1; gx++) {
              const d = Math.hypot(gx - gcx, gy - gcy);
              if (d > rGrid) continue;
              const idx = gy * FLOW_GRID_W + gx;
              customWindVx[idx] = 0;
              customWindVy[idx] = 0;
              customFlowVx[idx] = 0;
              customFlowVy[idx] = 0;
            }
          }
          return;
        }

        if (!lastVecWorld) {
          lastVecWorld = { wx, wy };
          return;
        }
        const dx = wx - lastVecWorld.wx;
        const dy = wy - lastVecWorld.wy;
        const len = Math.hypot(dx, dy);
        if (len < 1.5) return;
        const ux = dx / len;
        const uy = dy / len;
        lastVecWorld = { wx, wy };

        const isWind = activeTool === 'wind';
        const arrVx = isWind ? customWindVx : customFlowVx;
        const arrVy = isWind ? customWindVy : customFlowVy;
        const targetMag = isWind ? (1.8 * brushStrength) : (32 * brushStrength);

        for (let gy = gy0; gy <= gy1; gy++) {
          for (let gx = gx0; gx <= gx1; gx++) {
            const d = Math.hypot(gx - gcx, gy - gcy);
            if (d > rGrid) continue;
            const w = 1 - d / rGrid;
            const idx = gy * FLOW_GRID_W + gx;
            arrVx[idx] = arrVx[idx] * (1 - 0.55 * w) + ux * targetMag * (0.55 * w);
            arrVy[idx] = arrVy[idx] * (1 - 0.55 * w) + uy * targetMag * (0.55 * w);
          }
        }
        if (isWind) {
          injectWindImpulse(wx, wy, ux * 2.5 * brushStrength, uy * 2.5 * brushStrength, brushRadius * 2, 0.7);
        }
      }

      function applyPropTool(wx, wy) {
        if (activeTool === 'prop_erase') {
          let bestIdx = -1;
          let bestD = brushRadius * 1.25;
          for (let i = 0; i < props.length; i++) {
            const d = Math.hypot(props[i].wx - wx, props[i].wy - wy);
            if (d < bestD) { bestD = d; bestIdx = i; }
          }
          if (bestIdx >= 0) removePropObj(props[bestIdx]);
          return;
        }

        const modelKey = activeTool.replace('prop_', '');
        const beforeLen = props.length;
        addProp(modelKey, wx, wy, { allowOnPath: true, allowInWater: false });
        if (props.length > beforeLen) {
          props[props.length - 1].pinned = true;
        }
      }

      function handlePaintAt(clientX, clientY, isInitialClick) {
        const hit = pickTerrainAtClient(clientX, clientY);
        if (!hit) return;
        hoverWorld = hit;
        if (activeTool === 'select_box') {
          if (isInitialClick) {
            selStartWorld = { wx: hit.wx, wy: hit.wy };
            selectionBox = { x0: hit.wx, y0: hit.wy, x1: hit.wx, y1: hit.wy };
          } else if (selStartWorld) {
            selectionBox = {
              x0: Math.min(selStartWorld.wx, hit.wx),
              y0: Math.min(selStartWorld.wy, hit.wy),
              x1: Math.max(selStartWorld.wx, hit.wx),
              y1: Math.max(selStartWorld.wy, hit.wy)
            };
          }
          return;
        }
        if (activeTool.startsWith('prop_')) {
          if (isInitialClick) applyPropTool(hit.wx, hit.wy);
        } else if (activeTool === 'wind' || activeTool === 'flow' || activeTool === 'vec_erase') {
          applyVectorBrush(hit.wx, hit.wy);
        } else {
          if (isInitialClick) pushUndoSnapshot();
          applyTerrainBrush(hit.wx, hit.wy, isInitialClick);
        }
      }

      // 3. Eventos do Canvas no Modo Editar
      canvas.addEventListener('contextmenu', (e) => {
        if (window.__STUDIO_EDIT_MODE__) e.preventDefault();
      });

      canvas.addEventListener('pointerdown', (e) => {
        if (!window.__STUDIO_EDIT_MODE__) return;
        if (e.button === 2 || e.altKey) {
          isOrbiting = true;
          orbitLastX = e.clientX;
          canvas.setPointerCapture(e.pointerId);
          return;
        }
        if (e.button === 0) {
          isPainting = true;
          lastVecWorld = null;
          canvas.setPointerCapture(e.pointerId);
          handlePaintAt(e.clientX, e.clientY, true);
        }
      });

      canvas.addEventListener('pointermove', (e) => {
        if (!window.__STUDIO_EDIT_MODE__) return;
        if (isOrbiting) {
          const dx = e.clientX - orbitLastX;
          orbitLastX = e.clientX;
          targetTurn -= dx * 0.0085;
          turn = targetTurn;
          return;
        }
        hoverWorld = pickTerrainAtClient(e.clientX, e.clientY);
        if (hoverWorld) {
          const c = getCellAt(hoverWorld.wx, hoverWorld.wy);
          document.getElementById('coordPill').textContent =
            `wx: ${Math.round(hoverWorld.wx)}, wy: ${Math.round(hoverWorld.wy)}, z: ${hoverWorld.z.toFixed(1)} | ${c ? c.biome : ''}`;
        }
        if (isPainting) {
          handlePaintAt(e.clientX, e.clientY, false);
        }
      });

      window.addEventListener('pointerup', (e) => {
        if (!window.__STUDIO_EDIT_MODE__) return;
        isPainting = false;
        isOrbiting = false;
        lastVecWorld = null;
        try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
      });

      // 4. Tick de Edição (câmera livre WASD + vento/água vivos) & Overlay 2D
      window.__STUDIO_TICK__ = function(dt) {
        fluidTime += dt;
        const speed = 220 * dt;
        const cosA = Math.cos(turn);
        const sinA = Math.sin(turn);
        let mx = 0, my = 0;
        if (keys['KeyW'] || keys['ArrowUp']) my -= 1;
        if (keys['KeyS'] || keys['ArrowDown']) my += 1;
        if (keys['KeyA'] || keys['ArrowLeft']) mx -= 1;
        if (keys['KeyD'] || keys['ArrowRight']) mx += 1;
        if (mx !== 0 || my !== 0) {
          const len = Math.hypot(mx, my);
          mx /= len; my /= len;
          const wx = mx * cosA + my * sinA;
          const wy = -mx * sinA + my * cosA;
          camX = Math.max(WORLD_MIN, Math.min(WORLD_MAX, camX + wx * speed));
          camY = Math.max(WORLD_MIN, Math.min(WORLD_MAX, camY + wy * speed));
        }
        if (keys['KeyQ']) targetTurn += 1.8 * dt;
        if (keys['KeyE']) targetTurn -= 1.8 * dt;
        turn += (targetTurn - turn) * Math.min(1, dt * 14);
        if (typeof stepFlowStreaks === 'function') stepFlowStreaks(dt);
      };

      window.__STUDIO_OVERLAY__ = function() {
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        if (overlay.width !== w || overlay.height !== h) {
          overlay.width = w;
          overlay.height = h;
        }
        octx.clearRect(0, 0, w, h);
        if (!window.__STUDIO_EDIT_MODE__) return;

        // Desenha setas de vento e correnteza pintados na região visível
        const stepDraw = 2;
        for (let gy = 0; gy < FLOW_GRID_W; gy += stepDraw) {
          for (let gx = 0; gx < FLOW_GRID_W; gx += stepDraw) {
            const idx = gy * FLOW_GRID_W + gx;
            const wvx = customWindVx[idx], wvy = customWindVy[idx];
            const fvx = customFlowVx[idx], fvy = customFlowVy[idx];
            if ((wvx * wvx + wvy * wvy) < 0.02 && (fvx * fvx + fvy * fvy) < 0.5) continue;

            const wx = (gx * FLOW_GRID_STEP - HALF_GRID) * VOX;
            const wy = (gy * FLOW_GRID_STEP - HALF_GRID) * VOX;
            if (Math.abs(wx - camX) > 260 || Math.abs(wy - camY) > 260) continue;
            const z = getHeightAt(wx, wy) || 0;
            const p0 = project(wx, wy, z + 2);

            if ((wvx * wvx + wvy * wvy) >= 0.02) {
              const p1 = project(wx + wvx * 8, wy + wvy * 8, z + 2);
              octx.strokeStyle = 'rgba(250, 204, 21, 0.85)';
              octx.lineWidth = 2;
              octx.beginPath();
              octx.moveTo(p0.x * pixelScale, p0.y * pixelScale);
              octx.lineTo(p1.x * pixelScale, p1.y * pixelScale);
              octx.stroke();
            }
            if ((fvx * fvx + fvy * fvy) >= 0.5) {
              const p1 = project(wx + fvx * 0.55, wy + fvy * 0.55, z + 1);
              octx.strokeStyle = 'rgba(56, 189, 248, 0.9)';
              octx.lineWidth = 2;
              octx.beginPath();
              octx.moveTo(p0.x * pixelScale, p0.y * pixelScale);
              octx.lineTo(p1.x * pixelScale, p1.y * pixelScale);
              octx.stroke();
            }
          }
        }

        // Visualização sutil das células travadas (pinnedMask) próximas à câmera
        const cMinMx = Math.max(0, Math.floor((camX - 240) / VOX + HALF_GRID));
        const cMaxMx = Math.min(mw - 1, Math.ceil((camX + 240) / VOX + HALF_GRID));
        const cMinMy = Math.max(0, Math.floor((camY - 240) / VOX + HALF_GRID));
        const cMaxMy = Math.min(mh - 1, Math.ceil((camY + 240) / VOX + HALF_GRID));
        octx.fillStyle = 'rgba(56, 189, 248, 0.45)';
        for (let my = cMinMy; my <= cMaxMy; my += 6) {
          for (let mx = cMinMx; mx <= cMaxMx; mx += 6) {
            if (pinnedMask[my * mw + mx] !== 1) continue;
            const wx = (mx - HALF_GRID) * VOX;
            const wy = (my - HALF_GRID) * VOX;
            const scr = project(wx, wy, hmap[my * mw + mx] + 1);
            octx.fillRect(scr.x * pixelScale - 1.5, scr.y * pixelScale - 1.5, 3, 3);
          }
        }

        // Anel ciano nos props travados (pinned)
        octx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
        octx.lineWidth = 1.5;
        for (let i = 0; i < props.length; i++) {
          const p = props[i];
          if (!p.pinned || Math.abs(p.wx - camX) > 250 || Math.abs(p.wy - camY) > 250) continue;
          const scr = project(p.wx, p.wy, (p.wz || 0) + 2);
          octx.beginPath();
          octx.arc(scr.x * pixelScale, scr.y * pixelScale, 6, 0, Math.PI * 2);
          octx.stroke();
        }

        // Retângulo de seleção 3D
        if (selectionBox) {
          const corners = [
            [selectionBox.x0, selectionBox.y0],
            [selectionBox.x1, selectionBox.y0],
            [selectionBox.x1, selectionBox.y1],
            [selectionBox.x0, selectionBox.y1]
          ];
          octx.beginPath();
          for (let i = 0; i < 4; i++) {
            const [cx, cy] = corners[i];
            const cz = (getHeightAt(cx, cy) || 0) + 2;
            const scr = project(cx, cy, cz);
            if (i === 0) octx.moveTo(scr.x * pixelScale, scr.y * pixelScale);
            else octx.lineTo(scr.x * pixelScale, scr.y * pixelScale);
          }
          octx.closePath();
          octx.fillStyle = 'rgba(56, 189, 248, 0.14)';
          octx.fill();
          octx.strokeStyle = '#38BDF8';
          octx.lineWidth = 2;
          octx.stroke();
        }

        // Anel 3D do pincel sob o cursor
        if (hoverWorld && activeTool !== 'select_box') {
          const steps = 24;
          octx.beginPath();
          for (let i = 0; i <= steps; i++) {
            const a = (i / steps) * Math.PI * 2;
            const px = hoverWorld.wx + Math.cos(a) * brushRadius;
            const py = hoverWorld.wy + Math.sin(a) * brushRadius;
            const pz = getHeightAt(px, py) ?? hoverWorld.z;
            const scr = project(px, py, pz + 1.5);
            if (i === 0) octx.moveTo(scr.x * pixelScale, scr.y * pixelScale);
            else octx.lineTo(scr.x * pixelScale, scr.y * pixelScale);
          }
          octx.strokeStyle = activeTool === 'pin' ? '#38BDF8' : (activeTool === 'wind' ? '#FACC15' : '#F59E0B');
          octx.lineWidth = 2;
          octx.stroke();
        }
      };

      // 5. Terreno Procedural Genérico do Studio (sem mapa hardcodado do Vale Felino)
      function generateProceduralStudioTerrain(seed) {
        setWorldSeed(seed);
        document.getElementById('seedInput').value = WORLD_SEED;
        if (typeof bridges !== 'undefined') bridges.length = 0;
        if (typeof npcs !== 'undefined') npcs.length = 0;
        if (typeof fishes !== 'undefined') fishes.length = 0;

        const fs = 1080 / mw; // mantém o "tamanho" das feições: diorama pequeno mostra o relevo inteiro
        for (let my = 0; my < mh; my++) {
          const wy = (my - HALF_GRID) * VOX;
          for (let mx = 0; mx < mw; mx++) {
            const wx = (mx - HALF_GRID) * VOX;
            const idx = my * mw + mx;
            const nBase = fbm2d(wx * 0.0022 * fs, wy * 0.0022 * fs, 4);
            const nRidge = ridgedFbm(wx * 0.0018 * fs + 19.3, wy * 0.0018 * fs - 7.1, 3);
            const distEdge = Math.max(Math.abs(wx), Math.abs(wy)) / HALF_WORLD;
            const islandMask = Math.max(0, 1 - Math.pow(distEdge, 3.2));
            let h = (nBase * 24 + nRidge * 28 - 4) * islandMask - (1 - islandMask) * 6;
            h = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX, h));
            hmap[idx] = h;
            if (h <= -3.5) matMap[idx] = MAT_WATER;
            else if (h <= -0.8) matMap[idx] = MAT_SHALLOW;
            else if (h <= 2.2) matMap[idx] = MAT_SAND;
            else if (h >= 42) matMap[idx] = MAT_PEAK;
            else matMap[idx] = MAT_GRASS;
          }
        }
      }

      // 6. Regeneração Total vs Híbrida (preserva áreas e props fixos)
      function regenWorld(newSeed, preservePinned) {
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

        generateProceduralStudioTerrain(newSeed);

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

        // Espalha natureza procedural leve fora das áreas travadas
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

        if (preservePinned && savedProps) {
          for (const sp of savedProps) {
            const before = props.length;
            addProp(sp.modelKey, sp.wx, sp.wy, { allowOnPath: true, angle: sp.angle, scale: sp.scale });
            if (props.length > before) props[props.length - 1].pinned = true;
          }
        }
        if (typeof buildStandableMap === 'function') buildStandableMap();

        bakeTerrainSlices();
        bakeMinimapBase();
      }

      // Inicializa o Studio com terreno procedural neutro (sem o mapa hardcodado do Vale Felino)
      camX = 0; camY = 0;
      regenWorld(WORLD_SEED, false);

      // 6. Bindings da UI (Modo, Ferramentas, Sliders, Export/Import)
      document.getElementById('btnModeEdit').addEventListener('click', () => {
        window.__STUDIO_EDIT_MODE__ = true;
        document.getElementById('btnModeEdit').className = 'mode-btn active-edit';
        document.getElementById('btnModeTest').className = 'mode-btn';
        document.getElementById('helpPill').textContent = 'Editar: Clique/Arraste aplica pincel • Botão Direito orbita • WASD move câmera • Q/E gira';
      });
      document.getElementById('btnModeTest').addEventListener('click', () => {
        window.__STUDIO_EDIT_MODE__ = false;
        document.getElementById('btnModeEdit').className = 'mode-btn';
        document.getElementById('btnModeTest').className = 'mode-btn active-test';
        const c = getCellAt(camX, camY);
        teleportToWorld(camX, camY, 'Testando cena! 🐱', c ? c.h : 0);
        document.getElementById('helpPill').textContent = 'Testar: WASD anda • Espaço pula • Clique usa ferramenta • Volte para Editar quando quiser';
      });

      document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          activeTool = btn.dataset.tool;
        });
      });

      const bindSlider = (id, valId, fmt, fn) => {
        const el = document.getElementById(id);
        const out = document.getElementById(valId);
        el.addEventListener('input', () => {
          const v = parseFloat(el.value);
          out.textContent = fmt(v);
          fn(v);
        });
      };
      bindSlider('slRadius', 'valRadius', v => `${v}`, v => { brushRadius = v; });
      cat.scale = 0.45; // proporção realista frente a casas/árvores (no Vale Felino segue 1.0)
      bindSlider('slAvatarScale', 'valAvatarScale', v => `${v.toFixed(2)}x`, v => { cat.scale = v; });
      bindSlider('slStrength', 'valStrength', v => v.toFixed(1), v => { brushStrength = v; });
      bindSlider('slWind', 'valWind', v => `${v.toFixed(1)}x`, v => { ENGINE_TUNING.windMul = v; });
      bindSlider('slGravity', 'valGravity', v => `${v}`, v => {
        GRAVITY = v;
        JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0);
      });
      bindSlider('slCool', 'valCool', v => v.toFixed(2), v => { ENGINE_TUNING.fireCool = v; });
      bindSlider('slTalus', 'valTalus', v => `${v}`, v => { ENGINE_TUNING.sandTalus = v; });

      document.getElementById('btnRandSeed').addEventListener('click', () => {
        const s = 1000 + Math.floor(Math.random() * 90000);
        document.getElementById('seedInput').value = s;
      });
      const gridSel = document.getElementById('gridSizeSelect');
      gridSel.value = String(WORLD_CFG.gridW);
      gridSel.addEventListener('change', () => {
        if (!confirm('Trocar o tamanho do mapa recarrega o Studio e descarta a cena atual. Continuar?')) {
          gridSel.value = String(WORLD_CFG.gridW);
          return;
        }
        const url = new URL(window.location.href);
        url.searchParams.set('grid', gridSel.value);
        window.location.href = url.toString();
      });
      document.getElementById('btnNewFlat').addEventListener('click', () => {
        pushUndoSnapshot();
        hmap.fill(0);
        matMap.fill(MAT_GRASS);
        pinnedMask.fill(0);
        customWindVx.fill(0); customWindVy.fill(0);
        customFlowVx.fill(0); customFlowVy.fill(0);
        clearAllProps();
        resetTerrainLayers();
        if (typeof bridges !== 'undefined') bridges.length = 0;
        if (typeof buildStandableMap === 'function') buildStandableMap();
        camX = 0; camY = 0;
        bakeTerrainSlices();
        bakeMinimapBase();
      });
      document.getElementById('btnUndo').addEventListener('click', popUndoSnapshot);
      window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && window.__STUDIO_EDIT_MODE__) {
          e.preventDefault();
          popUndoSnapshot();
        }
      });

      function applyBoxPinState(pinVal) {
        if (!selectionBox) return;
        const mx0 = Math.max(0, Math.floor(selectionBox.x0 / VOX + HALF_GRID));
        const mx1 = Math.min(mw - 1, Math.ceil(selectionBox.x1 / VOX + HALF_GRID));
        const my0 = Math.max(0, Math.floor(selectionBox.y0 / VOX + HALF_GRID));
        const my1 = Math.min(mh - 1, Math.ceil(selectionBox.y1 / VOX + HALF_GRID));
        for (let my = my0; my <= my1; my++) {
          for (let mx = mx0; mx <= mx1; mx++) {
            pinnedMask[my * mw + mx] = pinVal;
          }
        }
        for (let i = 0; i < props.length; i++) {
          const p = props[i];
          if (p.wx >= selectionBox.x0 && p.wx <= selectionBox.x1 && p.wy >= selectionBox.y0 && p.wy <= selectionBox.y1) {
            p.pinned = pinVal === 1;
          }
        }
      }
      document.getElementById('btnPinSel').addEventListener('click', () => applyBoxPinState(1));
      document.getElementById('btnUnpinSel').addEventListener('click', () => applyBoxPinState(0));
      document.getElementById('btnClearSel').addEventListener('click', () => {
        if (!selectionBox) return;
        pushUndoSnapshot();
        const mx0 = Math.max(0, Math.floor(selectionBox.x0 / VOX + HALF_GRID));
        const mx1 = Math.min(mw - 1, Math.ceil(selectionBox.x1 / VOX + HALF_GRID));
        const my0 = Math.max(0, Math.floor(selectionBox.y0 / VOX + HALF_GRID));
        const my1 = Math.min(mh - 1, Math.ceil(selectionBox.y1 / VOX + HALF_GRID));
        for (let my = my0; my <= my1; my++) {
          for (let mx = mx0; mx <= mx1; mx++) {
            const idx = my * mw + mx;
            hmap[idx] = 0;
            matMap[idx] = MAT_GRASS;
            pinnedMask[idx] = 0;
          }
        }
        for (let i = props.length - 1; i >= 0; i--) {
          const p = props[i];
          if (p.wx >= selectionBox.x0 && p.wx <= selectionBox.x1 && p.wy >= selectionBox.y0 && p.wy <= selectionBox.y1) {
            removePropObj(p);
          }
        }
        rebakeTerrainDirtyRect(mx0 - 1, my0 - 1, mx1 + 1, my1 + 1);
        bakeMinimapBase();
        selectionBox = null;
      });
      document.getElementById('btnRegenAll').addEventListener('click', () => {
        const s = parseInt(document.getElementById('seedInput').value, 10) || DEFAULT_WORLD_SEED;
        regenWorld(s, false);
      });
      document.getElementById('btnRegenUnpinned').addEventListener('click', () => {
        const s = parseInt(document.getElementById('seedInput').value, 10) || DEFAULT_WORLD_SEED;
        regenWorld(s, true);
      });

      // Exportar / Importar JSON
      document.getElementById('btnExportJson').addEventListener('click', () => {
        const pinnedCells = [];
        for (let i = 0; i < pinnedMask.length; i++) {
          if (pinnedMask[i] === 1) {
            pinnedCells.push([i, Math.round(hmap[i] * 10) / 10, matMap[i]]);
          }
        }
        const windSparse = [];
        const flowSparse = [];
        for (let i = 0; i < customWindVx.length; i++) {
          if (Math.abs(customWindVx[i]) > 0.01 || Math.abs(customWindVy[i]) > 0.01) {
            windSparse.push([i, +customWindVx[i].toFixed(2), +customWindVy[i].toFixed(2)]);
          }
          if (Math.abs(customFlowVx[i]) > 0.05 || Math.abs(customFlowVy[i]) > 0.05) {
            flowSparse.push([i, +customFlowVx[i].toFixed(2), +customFlowVy[i].toFixed(2)]);
          }
        }
        const payload = {
          version: 1,
          seed: WORLD_SEED,
          tuning: { ...ENGINE_TUNING, gravity: GRAVITY },
          pinnedCells,
          windSparse,
          flowSparse,
          pinnedProps: props.filter(p => p.pinned).map(p => ({
            modelKey: p.modelKey, wx: +p.wx.toFixed(1), wy: +p.wy.toFixed(1),
            angle: +p.selfAngle.toFixed(3), scale: +p.scale.toFixed(2)
          }))
        };
        const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `voxel-scene-seed-${WORLD_SEED}.json`;
        a.click();
      });

      document.getElementById('btnImportJson').addEventListener('click', () => {
        document.getElementById('fileImportInput').click();
      });
      document.getElementById('fileImportInput').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const data = JSON.parse(reader.result);
            if (data.tuning) {
              ENGINE_TUNING.windMul = data.tuning.windMul ?? 1.0;
              ENGINE_TUNING.fireCool = data.tuning.fireCool ?? 0.22;
              ENGINE_TUNING.sandTalus = data.tuning.sandTalus ?? 2;
              if (data.tuning.gravity) {
                GRAVITY = data.tuning.gravity;
                JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0);
              }
            }
            regenWorld(data.seed || DEFAULT_WORLD_SEED, false);
            if (Array.isArray(data.pinnedCells)) {
              for (const [idx, h, m] of data.pinnedCells) {
                pinnedMask[idx] = 1;
                hmap[idx] = h;
                matMap[idx] = m;
              }
            }
            if (Array.isArray(data.windSparse)) {
              for (const [idx, vx, vy] of data.windSparse) {
                customWindVx[idx] = vx; customWindVy[idx] = vy;
              }
            }
            if (Array.isArray(data.flowSparse)) {
              for (const [idx, vx, vy] of data.flowSparse) {
                customFlowVx[idx] = vx; customFlowVy[idx] = vy;
              }
            }
            if (Array.isArray(data.pinnedProps)) {
              for (const sp of data.pinnedProps) {
                const before = props.length;
                addProp(sp.modelKey, sp.wx, sp.wy, { allowOnPath: true, angle: sp.angle, scale: sp.scale });
                if (props.length > before) props[props.length - 1].pinned = true;
              }
            }
            bakeTerrainSlices();
            bakeMinimapBase();
          } catch (err) {
            alert('Erro ao importar cena JSON: ' + err.message);
          }
        };
        reader.readAsText(file);
      });
    })();

