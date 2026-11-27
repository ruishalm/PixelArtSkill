    // =========================================================================
    // VOXEL 3D STUDIO — ESTADO, PICKER 3D, PINCÉIS & OVERLAY DE EDIÇÃO
    // =========================================================================
    (function initStudioStateAndBrushes() {
      if (!document.getElementById('studioOverlay')) return;

      const S = (window.__STUDIO__ = window.__STUDIO__ || {});
      window.__STUDIO_EDIT_MODE__ = true;

      const overlay = document.getElementById('studioOverlay');
      const octx = overlay.getContext('2d');
      const pinnedMask = new Uint8Array(mw * mh);
      const sculptH = new Float32Array(mw * mh);

      S.overlay = overlay;
      S.octx = octx;
      S.pinnedMask = pinnedMask;
      S.sculptH = sculptH;
      S.syncSculptFromHmap = function () { sculptH.set(hmap); };

      S.activeTool = 'raise';
      S.brushRadius = 16;
      S.brushStrength = 1.2;
      S.selectionBox = null; // { x0, y0, x1, y1 } em coordenadas do mundo
      S.undoStack = [];
      S.redoStack = [];
      S.baseKindSel = document.getElementById('baseKindSelect');
      S.genModeSel = document.getElementById('genModeSelect');

      let hoverWorld = null;
      S.hoverWorld = null;
      let isPainting = false;
      let isOrbiting = false;
      let orbitLastX = 0;
      let flattenTargetZ = 0;
      let caveTargetFloorZ = 0;
      let lastVecWorld = null;
      let selStartWorld = null;
      let terrainPaintedInStroke = false;
      let lastWaterCellKey = -1;
      let strokeMinMx = mw, strokeMinMy = mh, strokeMaxMx = -1, strokeMaxMy = -1;
      let strokeNeedsBreachCheck = false;

      const touchHydroIdx = (idx) => {
        sculptH[idx] = hmap[idx];
        pinnedMask[idx] = 1;
      };

      const expandStrokeBounds = (x0, y0, x1, y1) => {
        if (x0 < strokeMinMx) strokeMinMx = x0;
        if (y0 < strokeMinMy) strokeMinMy = y0;
        if (x1 > strokeMaxMx) strokeMaxMx = x1;
        if (y1 > strokeMaxMy) strokeMaxMy = y1;
      };

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
        carriedDrop = null;
      }
      function resetTerrainLayers() {
        shadowMask.fill(0);
        noGrassMask.fill(0);
        biomeMap.fill(0);
        cliffMask.fill(0);
      }

      S.removePropObj = removePropObj;
      S.clearAllProps = clearAllProps;
      S.resetTerrainLayers = resetTerrainLayers;

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
        const activeTool = S.activeTool;
        const brushRadius = S.brushRadius;
        const brushStrength = S.brushStrength;
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
        if (activeTool === 'cave_carve' && isInitialClick) {
          const centerIdx = cy * mw + cx;
          const centerH = hmap[centerIdx];
          if (caveCeil[centerIdx] > caveFloor[centerIdx] && centerH > caveCeil[centerIdx]) {
            caveTargetFloorZ = caveFloor[centerIdx];
          } else {
            let maxH = centerH;
            const r2Init = rCells * rCells;
            for (let my = my0; my <= my1; my++) {
              const dy = my - cy;
              for (let mx = mx0; mx <= mx1; mx++) {
                const dx = mx - cx;
                if (dx * dx + dy * dy <= r2Init) {
                  const hv = hmap[my * mw + mx];
                  if (hv > maxH) maxH = hv;
                }
              }
            }
            if (maxH >= centerH + 12) {
              caveTargetFloorZ = Math.max(-1, centerH);
            } else if (centerH >= 16) {
              caveTargetFloorZ = Math.max(0, centerH - 18);
            } else {
              const hz = hoverWorld ? Math.round(hoverWorld.z) : centerH;
              caveTargetFloorZ = Math.max(-1, Math.min(hz, centerH - 14));
            }
          }
        }

        if (activeTool === 'mat_water' || activeTool === 'mat_shallow') {
          const cellKey = cy * mw + cx;
          if (!isInitialClick && cellKey === lastWaterCellKey) return;
          lastWaterCellKey = cellKey;
          const b = applyWaterBrushHydrology(cx, cy, rCells, activeTool, touchHydroIdx, isInitialClick);
          terrainPaintedInStroke = true;
          const bx0 = Math.max(1, Math.min(mx0, b.minMx) - 1);
          const by0 = Math.max(1, Math.min(my0, b.minMy) - 1);
          const bx1 = Math.min(mw - 2, Math.max(mx1, b.maxMx) + 1);
          const by1 = Math.min(mh - 2, Math.max(my1, b.maxMy) + 1);
          expandStrokeBounds(bx0, by0, bx1, by1);
          if ((bx1 - bx0) * (by1 - by0) <= 6400) {
            rebakeTerrainDirtyRect(bx0, by0, bx1, by1);
          } else {
            bakeTerrainSlices();
          }
          bakeMinimapBase();
          return;
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
              const oldH = hmap[idx];
              sculptH[idx] = Math.min(TERRAIN_Z_MAX, sculptH[idx] + brushStrength * 1.4 * w);
              const newH = Math.round(sculptH[idx]);
              if (isWetMat(matMap[idx])) {
                const lift = Math.max(0, newH - oldH);
                if (waterDepth[idx] > 0) {
                  if (lift > 0 && lift < waterDepth[idx]) {
                    waterDepth[idx] -= lift;
                    hmap[idx] = oldH;
                    sculptH[idx] -= lift;
                    matMap[idx] = waterDepth[idx] <= 2 ? MAT_SHALLOW : MAT_WATER;
                  } else if (lift >= waterDepth[idx]) {
                    const rem = lift - waterDepth[idx];
                    waterDepth[idx] = 0;
                    hmap[idx] = oldH + rem;
                    sculptH[idx] = hmap[idx];
                    if (hmap[idx] > -2) matMap[idx] = dryMatForHeight(hmap[idx]);
                  }
                } else {
                  hmap[idx] = newH;
                  if (newH > -2) {
                    waterDepth[idx] = 0;
                    matMap[idx] = dryMatForHeight(newH);
                  }
                }
              } else {
                hmap[idx] = newH;
              }
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool === 'lower') {
              const oldH = hmap[idx];
              sculptH[idx] = Math.max(Z_MIN, sculptH[idx] - brushStrength * 1.4 * w);
              const newH = Math.round(sculptH[idx]);
              const isContained = oldH >= 0 && waterDepth[idx] > 0 &&
                hmap[idx - 1] >= oldH && hmap[idx + 1] >= oldH && hmap[idx - mw] >= oldH && hmap[idx + mw] >= oldH;
              if (isWetMat(matMap[idx]) && isContained) {
                const drop = Math.max(0, oldH - newH);
                if (drop > 0) {
                  const newBed = Math.max(Z_MIN, getSolidBedAtIdx(idx) - drop);
                  waterDepth[idx] = Math.min(255, oldH - newBed);
                  hmap[idx] = oldH;
                  sculptH[idx] += drop;
                  matMap[idx] = waterDepth[idx] <= 2 ? MAT_SHALLOW : MAT_WATER;
                }
              } else {
                const prevWet = isWetMat(matMap[idx]);
                const bed = prevWet ? getSolidBedAtIdx(idx) : oldH;
                hmap[idx] = newH;
                if (newH <= -2 && prevWet) {
                  waterDepth[idx] = 0;
                } else if (prevWet) {
                  if (newH <= bed) {
                    waterDepth[idx] = 0;
                    matMap[idx] = dryMatForHeight(newH);
                  } else {
                    waterDepth[idx] = Math.min(255, newH - bed);
                    matMap[idx] = waterDepth[idx] <= 2 ? MAT_SHALLOW : MAT_WATER;
                  }
                }
              }
              pinnedMask[idx] = 1;
              strokeNeedsBreachCheck = true;
              terrainDirty = true;
              if (caveCeil[idx] > caveFloor[idx] && hmap[idx] <= caveCeil[idx]) {
                if (hmap[idx] - 3 > caveFloor[idx] + 3) {
                  caveCeil[idx] = hmap[idx] - 3;
                } else {
                  caveFloor[idx] = -32768;
                  caveCeil[idx] = -32768;
                }
              }
            } else if (activeTool === 'flatten') {
              const oldH = hmap[idx];
              sculptH[idx] = sculptH[idx] + (flattenTargetZ - sculptH[idx]) * Math.min(1, 0.35 * brushStrength * w);
              const newH = Math.round(sculptH[idx]);
              if (isWetMat(matMap[idx]) && newH > -2) {
                if (newH > oldH || waterDepth[idx] === 0) {
                  hmap[idx] = newH;
                  waterDepth[idx] = 0;
                  matMap[idx] = dryMatForHeight(newH);
                } else {
                  const bed = getSolidBedAtIdx(idx);
                  if (newH < bed) {
                    waterDepth[idx] = Math.min(255, oldH - newH);
                    matMap[idx] = waterDepth[idx] <= 2 ? MAT_SHALLOW : MAT_WATER;
                  }
                  hmap[idx] = oldH;
                  sculptH[idx] = oldH;
                }
              } else {
                hmap[idx] = newH;
              }
              if (caveCeil[idx] > caveFloor[idx] && hmap[idx] <= caveCeil[idx]) {
                if (hmap[idx] - 3 > caveFloor[idx] + 3) {
                  caveCeil[idx] = hmap[idx] - 3;
                } else {
                  caveFloor[idx] = -32768;
                  caveCeil[idx] = -32768;
                }
              }
              pinnedMask[idx] = 1;
              strokeNeedsBreachCheck = true;
              terrainDirty = true;
            } else if (activeTool === 'smooth') {
              const oldH = hmap[idx];
              const avg = (sculptH[idx - 1] + sculptH[idx + 1] + sculptH[idx - mw] + sculptH[idx + mw]) * 0.25;
              sculptH[idx] = sculptH[idx] + (avg - sculptH[idx]) * Math.min(1, 0.45 * brushStrength * w);
              const newH = Math.round(sculptH[idx]);
              if (isWetMat(matMap[idx]) && newH > -2) {
                if (newH > oldH || waterDepth[idx] === 0) {
                  hmap[idx] = newH;
                  waterDepth[idx] = 0;
                  matMap[idx] = dryMatForHeight(newH);
                } else {
                  const bed = getSolidBedAtIdx(idx);
                  if (newH < bed) {
                    waterDepth[idx] = Math.min(255, oldH - newH);
                    matMap[idx] = waterDepth[idx] <= 2 ? MAT_SHALLOW : MAT_WATER;
                  }
                  hmap[idx] = oldH;
                  sculptH[idx] = oldH;
                }
              } else {
                hmap[idx] = newH;
              }
              if (caveCeil[idx] > caveFloor[idx] && hmap[idx] <= caveCeil[idx]) {
                if (hmap[idx] - 3 > caveFloor[idx] + 3) {
                  caveCeil[idx] = hmap[idx] - 3;
                } else {
                  caveFloor[idx] = -32768;
                  caveCeil[idx] = -32768;
                }
              }
              pinnedMask[idx] = 1;
              strokeNeedsBreachCheck = true;
              terrainDirty = true;
            } else if (activeTool === 'cave_carve') {
              const roofBase = isWetMat(matMap[idx]) ? getSolidBedAtIdx(idx) : hmap[idx];
              if (roofBase >= caveTargetFloorZ + 12) {
                caveFloor[idx] = caveTargetFloorZ;
                caveCeil[idx] = Math.min(roofBase - 3, caveTargetFloorZ + 14);
                pinnedMask[idx] = 1;
                terrainDirty = true;
              } else if (hmap[idx] > caveTargetFloorZ) {
                hmap[idx] = caveTargetFloorZ;
                sculptH[idx] = caveTargetFloorZ;
                caveFloor[idx] = -32768;
                caveCeil[idx] = -32768;
                if (isWetMat(matMap[idx])) {
                  waterDepth[idx] = 0;
                  matMap[idx] = dryMatForHeight(caveTargetFloorZ);
                  strokeNeedsBreachCheck = true;
                }
                pinnedMask[idx] = 1;
                terrainDirty = true;
              }
            } else if (activeTool === 'cave_fill') {
              if (caveCeil[idx] > caveFloor[idx]) {
                caveFloor[idx] = -32768;
                caveCeil[idx] = -32768;
                pinnedMask[idx] = 1;
                terrainDirty = true;
              }
            } else if (activeTool.startsWith('mat_')) {
              let m = MAT_GRASS;
              if (activeTool === 'mat_sand') m = MAT_SAND;
              else if (activeTool === 'mat_peak') m = MAT_PEAK;
              else if (activeTool === 'mat_path') m = MAT_PATH;
              if (isWetMat(matMap[idx])) {
                if (hmap[idx] >= 0) strokeNeedsBreachCheck = true;
                hmap[idx] = getSolidBedAtIdx(idx);
                sculptH[idx] = hmap[idx];
                waterDepth[idx] = 0;
              }
              matMap[idx] = m;
              pinnedMask[idx] = 1;
              terrainDirty = true;
            } else if (activeTool === 'pin') {
              pinnedMask[idx] = 1;
            } else if (activeTool === 'unpin') {
              pinnedMask[idx] = 0;
            } else if (activeTool === 'eraser') {
              sculptH[idx] = 0;
              hmap[idx] = 0;
              caveFloor[idx] = -32768;
              caveCeil[idx] = -32768;
              matMap[idx] = MAT_GRASS;
              waterDepth[idx] = 0;
              pinnedMask[idx] = 0;
              strokeNeedsBreachCheck = true;
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
          for (let i = waterSprings.length - 1; i >= 0; i--) {
            if (Math.hypot(waterSprings[i].wx - wx, waterSprings[i].wy - wy) <= brushRadius) {
              waterSprings.splice(i, 1);
            }
          }
        }

        if (terrainDirty) {
          terrainPaintedInStroke = true;
          expandStrokeBounds(mx0, my0, mx1, my1);
          rebakeTerrainDirtyRect(mx0 - 2, my0 - 2, mx1 + 2, my1 + 2);
          bakeMinimapBase();
        }
      }
      S.applyTerrainBrush = applyTerrainBrush;

      function applyVectorBrush(wx, wy) {
        const activeTool = S.activeTool;
        const brushRadius = S.brushRadius;
        const brushStrength = S.brushStrength;
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
        const activeTool = S.activeTool;
        const brushRadius = S.brushRadius;
        if (activeTool === 'prop_erase') {
          let bestIdx = -1;
          let bestD = brushRadius * 1.25;
          for (let i = 0; i < props.length; i++) {
            const d = Math.hypot(props[i].wx - wx, props[i].wy - wy);
            if (d < bestD) { bestD = d; bestIdx = i; }
          }
          if (bestIdx >= 0) {
            S.pushUndoSnapshot();
            removePropObj(props[bestIdx]);
          }
          return;
        }

        const modelKey = activeTool.replace('prop_', '');
        S.pushUndoSnapshot();
        const beforeLen = props.length;
        addProp(modelKey, wx, wy, { allowOnPath: true, allowInWater: false });
        if (props.length > beforeLen) {
          props[props.length - 1].pinned = true;
        } else {
          S.undoStack.pop();
        }
      }

      function handlePaintAt(clientX, clientY, isInitialClick) {
        const hit = pickTerrainAtClient(clientX, clientY);
        if (!hit) return;
        hoverWorld = hit;
        S.hoverWorld = hoverWorld;
        const activeTool = S.activeTool;
        if (activeTool === 'select_box') {
          if (isInitialClick) {
            selStartWorld = { wx: hit.wx, wy: hit.wy };
            S.selectionBox = { x0: hit.wx, y0: hit.wy, x1: hit.wx, y1: hit.wy };
          } else if (selStartWorld) {
            S.selectionBox = {
              x0: Math.min(selStartWorld.wx, hit.wx),
              y0: Math.min(selStartWorld.wy, hit.wy),
              x1: Math.max(selStartWorld.wx, hit.wx),
              y1: Math.max(selStartWorld.wy, hit.wy)
            };
          }
          return;
        }
        if (activeTool === 'spring') {
          if (isInitialClick) {
            S.pushUndoSnapshot();
            const cx = Math.max(1, Math.min(mw - 2, Math.floor(hit.wx / VOX + HALF_GRID)));
            const cy = Math.max(1, Math.min(mh - 2, Math.floor(hit.wy / VOX + HALF_GRID)));
            const spWx = (cx - HALF_GRID + 0.5) * VOX;
            const spWy = (cy - HALF_GRID + 0.5) * VOX;
            const exists = waterSprings.some(sp => Math.hypot(sp.wx - spWx, sp.wy - spWy) < 6);
            if (!exists) {
              waterSprings.push({ wx: spWx, wy: spWy, z: getSolidBedAtIdx(cy * mw + cx) });
            }
            placeSpringHydrology(cx, cy, touchHydroIdx);
            if (typeof buildStandableMap === 'function') buildStandableMap();
            if (typeof initFlowStreaks === 'function') initFlowStreaks();
            bakeTerrainSlices();
            bakeMinimapBase();
          }
          return;
        }
        if (activeTool.startsWith('prop_')) {
          if (isInitialClick) applyPropTool(hit.wx, hit.wy);
        } else if (activeTool === 'wind' || activeTool === 'flow' || activeTool === 'vec_erase') {
          applyVectorBrush(hit.wx, hit.wy);
        } else {
          if (isInitialClick) S.pushUndoSnapshot();
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
        S.hoverWorld = hoverWorld;
        if (hoverWorld) {
          const c = getCellAt(hoverWorld.wx, hoverWorld.wy);
          const caveTxt = c && c.hasCave ? ` | Caverna ${c.caveFloor}..${c.caveCeil}` : '';
          document.getElementById('coordPill').textContent =
            `wx: ${Math.round(hoverWorld.wx)}, wy: ${Math.round(hoverWorld.wy)}, z: ${hoverWorld.z.toFixed(1)} | ${c ? c.biome : ''}${caveTxt}`;
        }
        if (isPainting) {
          handlePaintAt(e.clientX, e.clientY, false);
        }
      });

      canvas.addEventListener('pointerleave', () => {
        hoverWorld = null;
        S.hoverWorld = null;
      });

      window.addEventListener('pointerup', (e) => {
        if (!window.__STUDIO_EDIT_MODE__) return;
        if (terrainPaintedInStroke) {
          terrainPaintedInStroke = false;
          if (strokeNeedsBreachCheck && strokeMaxMx >= strokeMinMx && typeof drainBreachedLakesInRect === 'function') {
            drainBreachedLakesInRect(strokeMinMx, strokeMinMy, strokeMaxMx, strokeMaxMy, touchHydroIdx);
          }
          strokeNeedsBreachCheck = false;
          strokeMinMx = mw; strokeMinMy = mh; strokeMaxMx = -1; strokeMaxMy = -1;
          if (typeof buildStandableMap === 'function') buildStandableMap();
          if (typeof initFlowStreaks === 'function') initFlowStreaks();
          bakeTerrainSlices();
          bakeMinimapBase();
        }
        lastWaterCellKey = -1;
        isPainting = false;
        isOrbiting = false;
        lastVecWorld = null;
        try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
      });

      // 4. Tick de Edição (câmera livre WASD + vento/água vivos) & Overlay 2D
      window.__STUDIO_TICK__ = function (dt) {
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
        if (typeof syncWaveOrigin === 'function') syncWaveOrigin();
        if (typeof stepFlowStreaks === 'function') stepFlowStreaks(dt);
        if (typeof stepWaveBuffer === 'function') {
          waveAccum += dt;
          while (waveAccum >= 1 / 30) {
            waveAccum -= 1 / 30;
            if (typeof stepAutoWaterfallsAndSprings === 'function') stepAutoWaterfallsAndSprings(true);
            stepWaveBuffer();
          }
        }
        for (let i = particles.length - 1; i >= 0; i--) {
          const p = particles[i];
          p.x += p.vx * dt;
          p.y += p.vy * dt;
          p.vz -= (p.grav !== undefined ? p.grav : 260) * dt;
          p.z += p.vz * dt;
          p.life -= dt;
          if (p.life <= 0) particles.splice(i, 1);
        }
      };

      window.__STUDIO_OVERLAY__ = function () {
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
        const selectionBox = S.selectionBox;
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

        // Marcadores das nascentes (waterSprings) próximas à câmera
        if (typeof waterSprings !== 'undefined') {
          for (let i = 0; i < waterSprings.length; i++) {
            const sp = waterSprings[i];
            if (Math.abs(sp.wx - camX) > 260 || Math.abs(sp.wy - camY) > 260) continue;
            const sz = (getHeightAt(sp.wx, sp.wy) ?? sp.z) + 1.5;
            const scr = project(sp.wx, sp.wy, sz);
            octx.strokeStyle = '#38BDF8';
            octx.fillStyle = 'rgba(224, 242, 254, 0.85)';
            octx.lineWidth = 2;
            octx.beginPath();
            octx.arc(scr.x * pixelScale, scr.y * pixelScale, 6, 0, Math.PI * 2);
            octx.fill();
            octx.stroke();
          }
        }

        // Anel 3D do pincel sob o cursor
        const activeTool = S.activeTool;
        const brushRadius = S.brushRadius;
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
          const isWaterTool = activeTool === 'pin' || activeTool === 'spring' || activeTool === 'mat_water' || activeTool === 'mat_shallow';
          octx.strokeStyle = isWaterTool ? '#38BDF8' : (activeTool === 'wind' ? '#FACC15' : '#F59E0B');
          octx.lineWidth = 2;
          octx.stroke();
        }
      };
    })();
