    // =========================================================================
    // ENGINE: TERRAIN SCULPTOR, EROSION, STANDABILITY & ARCH BRIDGES
    // =========================================================================
    function pullRidge(points, halfWidth, heights, opts = {}) {
      const {
        steepness = 1.45,
        warpFreq = 0.011,
        warpAmp = 26,
        ridgeAmp = 0.28,
        smoothK = 9,
        terraceStep = 0,
        terraceStrength = 0.45,
        mat = null,
        biome = null,
        isCliff = false
      } = opts;
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const [px, py] of points) {
        if (px < minX) minX = px;
        if (px > maxX) maxX = px;
        if (py < minY) minY = py;
        if (py > maxY) maxY = py;
      }
      const pad = halfWidth + warpAmp + 16;
      const x0 = Math.max(0, Math.floor((minX - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((maxX + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((minY - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((maxY + pad) / VOX + HALF_GRID));

      const maxPreD = halfWidth + warpAmp + 6;
      const nPts = points.length - 1;
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          let rawMinSq = Infinity;
          for (let i = 0; i < nPts; i++) {
            const ds = distToSegmentSq(wx, wy, points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]);
            if (ds < rawMinSq) rawMinSq = ds;
          }
          if (rawMinSq > maxPreD * maxPreD) continue;
          const wp = warp2d(wx, wy, warpFreq, warpAmp);
          let bestDSq = halfWidth * halfWidth;
          let bestSegIdx = -1;
          let bestT = 0;
          for (let i = 0; i < nPts; i++) {
            const ax = points[i][0], ay = points[i][1];
            const vx = points[i + 1][0] - ax, vy = points[i + 1][1] - ay;
            const dpx = wp.x - ax, dpy = wp.y - ay;
            const lenSq = vx * vx + vy * vy;
            const t = lenSq > 0 ? Math.max(0, Math.min(1, (dpx * vx + dpy * vy) / lenSq)) : 0;
            const cx = ax + vx * t - wp.x, cy = ay + vy * t - wp.y;
            const dSq = cx * cx + cy * cy;
            if (dSq < bestDSq) {
              bestDSq = dSq;
              bestSegIdx = i;
              bestT = t;
            }
          }
          if (bestSegIdx >= 0) {
            const bestD = Math.sqrt(bestDSq);
            const bestSegH = heights[bestSegIdx] + (heights[bestSegIdx + 1] - heights[bestSegIdx]) * bestT;
            const k = Math.cos((bestD / halfWidth) * Math.PI * 0.5);
            const ridge = ridgedFbm(wp.x * 0.018 + 2.1, wp.y * 0.018 - 6.3, 2);
            let rawH = bestSegH * Math.pow(Math.max(0, k), steepness) * (1 + (ridge - 0.5) * ridgeAmp);
            if (terraceStep > 0) rawH = rockTerrace(rawH, terraceStep, terraceStrength, wx, wy);
            const idx = row + mx;
            const blended = Math.min(64, Math.round(smax(hmap[idx], rawH, smoothK)));
            if (blended > hmap[idx]) hmap[idx] = blended;
            if (biome !== null && bestD < halfWidth * 0.9) biomeMap[idx] = biome;
            if (mat !== null && rawH > 2) matMap[idx] = mat;
            if (isCliff && bestD < halfWidth * 0.85) cliffMask[idx] = 1;
          }
        }
      }
    }

    function carveBenchTrail(points3D, halfWidth = 13, blendWidth = 28, mat = MAT_PATH, biome = null) {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const [px, py] of points3D) {
        if (px < minX) minX = px;
        if (px > maxX) maxX = px;
        if (py < minY) minY = py;
        if (py > maxY) maxY = py;
      }
      const pad = halfWidth + blendWidth + 16;
      const x0 = Math.max(0, Math.floor((minX - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((maxX + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((minY - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((maxY + pad) / VOX + HALF_GRID));

      const maxTrailSq = (halfWidth + blendWidth + 3.5) * (halfWidth + blendWidth + 3.5);
      const nSegs = points3D.length - 1;
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          let bestDSq = maxTrailSq;
          let bestZ = 0;
          let found = false;
          for (let i = 0; i < nSegs; i++) {
            const p0 = points3D[i], p1 = points3D[i + 1];
            const ax = p0[0], ay = p0[1];
            const vx = p1[0] - ax, vy = p1[1] - ay;
            const dpx = wx - ax, dpy = wy - ay;
            const lenSq = vx * vx + vy * vy;
            const t = lenSq > 0 ? Math.max(0, Math.min(1, (dpx * vx + dpy * vy) / lenSq)) : 0;
            const cx = ax + vx * t - wx, cy = ay + vy * t - wy;
            const dSq = cx * cx + cy * cy;
            if (dSq < bestDSq) {
              bestDSq = dSq;
              bestZ = p0[2] + (p1[2] - p0[2]) * t;
              found = true;
            }
          }
          if (!found) continue;
          const bestD = Math.sqrt(bestDSq);
          const edgeN = fbm2dFast(wx * 0.032 + 4.1, wy * 0.032 - 1.9) * 3.0;
          const innerW = halfWidth + edgeN;
          const idx = row + mx;
          if (bestD <= innerW) {
            hmap[idx] = Math.round(bestZ);
            matMap[idx] = mat;
            cliffMask[idx] = 0;
            if (biome !== null) biomeMap[idx] = biome;
          } else if (bestD <= innerW + blendWidth) {
            const t = (bestD - innerW) / blendWidth;
            const s = t * t * (3 - 2 * t);
            hmap[idx] = Math.max(0, Math.min(64, Math.round(bestZ * (1 - s) + hmap[idx] * s)));
            if (biome !== null && t < 0.6) biomeMap[idx] = biome;
          }
        }
      }
    }

    function pullHill(cx, cy, radius, height, steepness = 1.6, noiseAmp = 0.20, mat = null, biome = null, additive = false) {
      const pad = radius * (1 + noiseAmp) + 28;
      const x0 = Math.max(0, Math.floor((cx - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + pad) / VOX + HALF_GRID));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const wp = warp2d(wx, wy, 0.013, Math.min(26, radius * 0.22));
          const d = Math.hypot(wp.x - cx, wp.y - cy);
          const n = fbm2dFast(wx * 0.016 + 11.3, wy * 0.016 - 5.7);
          const effR = radius * (1 + n * noiseAmp);
          if (d < effR) {
            const k = Math.cos((d / effR) * Math.PI * 0.5);
            const val = Math.round(height * Math.pow(Math.max(0, k), steepness));
            const idx = my * mw + mx;
            if (additive) {
              hmap[idx] = Math.min(64, hmap[idx] + val);
            } else {
              const blended = Math.min(64, Math.round(smax(hmap[idx], val, 6)));
              if (blended > hmap[idx]) hmap[idx] = blended;
            }
            if (biome !== null && d < effR * 0.92) biomeMap[idx] = biome;
            if (mat !== null && val > 1) matMap[idx] = mat;
          }
        }
      }
    }

    function pullPlateau(cx, cy, rx, ry, height, rimWidth, noiseAmp = 0.12, isCliff = false, mat = null, biome = null, lowerAllowed = false, useWarp = true) {
      const warpAmp = useWarp ? Math.min(34, Math.min(rx, ry) * 0.28) : 0;
      const maxR = Math.max(rx, ry) * (1 + noiseAmp) + rimWidth + (useWarp ? warpAmp + 6 : 8);
      const x0 = Math.max(0, Math.floor((cx - maxR) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + maxR) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - maxR) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + maxR) / VOX + HALF_GRID));

      const rimNorm = rimWidth / Math.max(1, Math.min(rx, ry));
      const minR = Math.max(1, Math.min(rx, ry));
      const marginNorm = noiseAmp + (warpAmp / minR) + 0.06;
      const maxNormPre = (1.0 + rimNorm) * (1.0 + noiseAmp) + (warpAmp / minR) + 0.15;
      const maxNormPreSq = maxNormPre * maxNormPre;
      const minInnerPre = Math.max(0, 1.0 - marginNorm);
      const minInnerPreSq = minInnerPre * minInnerPre;
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const rdy = (wy - cy) / ry;
        const rdySq = rdy * rdy;
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const rdx = (wx - cx) / rx;
          const rawNdSq = rdx * rdx + rdySq;
          if (rawNdSq > maxNormPreSq) continue;

          if (rawNdSq <= minInnerPreSq) {
            const idx = row + mx;
            if (lowerAllowed) {
              hmap[idx] = height;
            } else {
              const blended = !isCliff ? Math.min(64, Math.round(smax(hmap[idx], height, 6))) : height;
              if (blended > hmap[idx]) hmap[idx] = blended;
            }
            if (isCliff) cliffMask[idx] = 1;
            if (biome !== null) biomeMap[idx] = biome;
            if (mat !== null) matMap[idx] = mat;
            continue;
          }

          const wp = useWarp ? warp2d(wx, wy, 0.012, warpAmp) : { x: wx, y: wy };
          const dx = (wp.x - cx) / rx;
          const dy = (wp.y - cy) / ry;
          const nd = Math.hypot(dx, dy);
          const n = noiseAmp > 0 ? fbm2dFast(wx * 0.018 - 3.1, wy * 0.018 + 7.9) * noiseAmp : 0;
          const effNd = nd / (1 + n);

          if (effNd <= 1.0 + rimNorm) {
            const idx = row + mx;
            let targetH = height;
            if (effNd > 1.0) {
              const t = 1.0 - (effNd - 1.0) / rimNorm;
              const s = t * t * (3 - 2 * t);
              targetH = Math.round(height * s);
            }
            if (lowerAllowed) {
              hmap[idx] = targetH;
            } else {
              const blended = !isCliff ? Math.min(64, Math.round(smax(hmap[idx], targetH, 6))) : targetH;
              if (blended > hmap[idx]) hmap[idx] = blended;
            }
            if (isCliff && effNd <= 1.0 + rimNorm * 0.95) {
              cliffMask[idx] = 1;
            }
            if (biome !== null && effNd <= 1.0 + rimNorm * 0.6) biomeMap[idx] = biome;
            if (mat !== null && (effNd <= 1.0 || targetH >= 2 || (lowerAllowed && targetH >= 0))) matMap[idx] = mat;
          }
        }
      }
    }

    function pullRuinsBlock(cx, cy, halfW, halfD, height, rimWidth = 2.0, mat = MAT_STONE, biome = 2) {
      const pad = Math.max(halfW, halfD) * 1.15 + rimWidth + 6;
      const x0 = Math.max(0, Math.floor((cx - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + pad) / VOX + HALF_GRID));
      const rimNorm = rimWidth / Math.max(1, Math.min(halfW, halfD));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const nd = Math.max(Math.abs(wx - cx) / halfW, Math.abs(wy - cy) / halfD);
          const chip = fbm2d(wx * 0.08, wy * 0.08) * 0.08;
          const effNd = nd + chip;

          if (effNd <= 1.0 + rimNorm) {
            const idx = my * mw + mx;
            let targetH = height;
            if (effNd > 1.0) {
              const t = 1.0 - (effNd - 1.0) / rimNorm;
              const s = t * t * (3 - 2 * t);
              targetH = Math.round(height * s);
            }
            if (targetH > hmap[idx]) hmap[idx] = targetH;
            if (effNd <= 1.0 + rimNorm * 0.95) cliffMask[idx] = 1;
            if (biome !== null && effNd <= 1.0 + rimNorm * 0.6) biomeMap[idx] = biome;
            if (mat !== null && (effNd <= 1.0 || targetH >= 2)) matMap[idx] = mat;
          }
        }
      }
    }

    function carveOrganicPond(cx, cy, rx, ry, warpAmp = 26, waterH = 13, rimW = 8, rimH = 16, biome = 4) {
      const pad = Math.max(rx, ry) + rimW + warpAmp + 12;
      const x0 = Math.max(0, Math.floor((cx - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + pad) / VOX + HALF_GRID));
      const rimNorm = rimW / Math.max(1, Math.min(rx, ry));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const wp = warp2d(wx, wy, 0.015, warpAmp);
          const nd = Math.hypot((wp.x - cx) / rx, (wp.y - cy) / ry);
          const idx = my * mw + mx;
          if (nd <= 1.0) {
            hmap[idx] = waterH;
            matMap[idx] = MAT_WATER;
            biomeMap[idx] = biome;
            cliffMask[idx] = 1;
          } else if (nd <= 1.0 + rimNorm) {
            hmap[idx] = rimH;
            matMap[idx] = MAT_SAND;
            biomeMap[idx] = biome;
            cliffMask[idx] = 1;
          }
        }
      }
    }

    function distToSegmentSq(px, py, ax, ay, bx, by) {
      const vx = bx - ax, vy = by - ay;
      const wx = px - ax, wy = py - ay;
      const lenSq = vx * vx + vy * vy;
      const t = lenSq > 0 ? Math.max(0, Math.min(1, (wx * vx + wy * vy) / lenSq)) : 0;
      const cx = ax + vx * t, cy = ay + vy * t;
      return (px - cx) * (px - cx) + (py - cy) * (py - cy);
    }

    function paintOrganicPath(points, halfWidth, mat = MAT_PATH, biome = null, forceFlatZ = null) {
      for (let i = 0; i < points.length - 1; i++) {
        const [ax, ay] = points[i];
        const [bx, by] = points[i + 1];
        const pad = halfWidth + 12;
        const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - pad) / VOX + HALF_GRID));
        const x1 = Math.min(mw - 1, Math.ceil((Math.max(ax, bx) + pad) / VOX + HALF_GRID));
        const y0 = Math.max(0, Math.floor((Math.min(ay, by) - pad) / VOX + HALF_GRID));
        const y1 = Math.min(mh - 1, Math.ceil((Math.max(ay, by) + pad) / VOX + HALF_GRID));

        for (let my = y0; my <= y1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const row = my * mw;
          for (let mx = x0; mx <= x1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const dSq = distToSegmentSq(wx, wy, ax, ay, bx, by);
            if (dSq > (halfWidth + 5) * (halfWidth + 5)) continue;
            const d = Math.sqrt(dSq);
            const n = fbm2dFast(wx * 0.028 + 4.2, wy * 0.028 - 2.1) * 4.8;
            if (d <= halfWidth + n) {
              const idx = row + mx;
              if (!isWetMat(matMap[idx]) && matMap[idx] !== MAT_BRIDGE) {
                matMap[idx] = mat;
                if (forceFlatZ !== null && !getBridgeAt(wx, wy)) hmap[idx] = forceFlatZ;
              }
              if (biome !== null) biomeMap[idx] = biome;
            }
          }
        }
      }
    }

    function paintRampPath(ax, ay, az, bx, by, bz, halfWidth, mat = MAT_PATH, biome = null) {
      const pad = halfWidth + 16;
      const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((Math.max(ax, bx) + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((Math.min(ay, by) - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((Math.max(ay, by) + pad) / VOX + HALF_GRID));
      const vx = bx - ax, vy = by - ay;
      const lenSq = vx * vx + vy * vy || 1;

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const t = Math.max(0, Math.min(1, ((wx - ax) * vx + (wy - ay) * vy) / lenSq));
          const px = ax + vx * t, py = ay + vy * t;
          const d = Math.hypot(wx - px, wy - py);
          const n = fbm2d(wx * 0.025, wy * 0.025) * 4.2;
          const effR = halfWidth + n;
          if (d <= effR + 12) {
            const idx = my * mw + mx;
            const targetH = Math.round(az + (bz - az) * t);
            if (d <= effR) {
              hmap[idx] = Math.max(hmap[idx], targetH);
              matMap[idx] = mat;
              if (biome !== null) biomeMap[idx] = biome;
            } else {
              const s = 1 - (d - effR) / 12;
              hmap[idx] = Math.max(hmap[idx], Math.round(targetH * s * s));
              if (biome !== null) biomeMap[idx] = biome;
            }
          }
        }
      }
    }

    function carveRiverPath(points, width, depth = -6) {
      const baseHalfW = width * 0.5;
      const maxMouth = 42;
      const bankPad = baseHalfW + maxMouth + 22;
      for (let i = 0; i < points.length - 1; i++) {
        const [ax, ay] = points[i];
        const [bx, by] = points[i + 1];
        const pad = bankPad + 16;
        const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - pad) / VOX + HALF_GRID));
        const x1 = Math.min(mw - 1, Math.ceil((Math.max(ax, bx) + pad) / VOX + HALF_GRID));
        const y0 = Math.max(0, Math.floor((Math.min(ay, by) - pad) / VOX + HALF_GRID));
        const y1 = Math.min(mh - 1, Math.ceil((Math.max(ay, by) + pad) / VOX + HALF_GRID));

        for (let my = y0; my <= y1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const mouthFlare = wy > 615 ? Math.min(maxMouth, (wy - 615) * 0.24) : 0;
          const halfW = baseHalfW + mouthFlare;
          const bankW = halfW + 20;
          const maxBankSq = (bankW + 10.5) * (bankW + 10.5);
          const minRiverInner = Math.max(0, halfW - 10.2);
          const minRiverInnerSq = minRiverInner * minRiverInner;
          const row = my * mw;
          for (let mx = x0; mx <= x1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const dSq = distToSegmentSq(wx, wy, ax, ay, bx, by);
            if (dSq > maxBankSq) continue;
            const idx = row + mx;
            if (dSq <= minRiverInnerSq) {
              hmap[idx] = depth;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 5;
              continue;
            }
            const d = Math.sqrt(dSq);
            const wobble = fbm2dFast(wx * 0.015 + 9.2, wy * 0.015 - 4.4) * 10.0;
            const effD = d + wobble;
            if (effD <= halfW) {
              hmap[idx] = depth;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 5;
            } else if (effD <= halfW + 6.5) {
              if (matMap[idx] !== MAT_WATER) {
                hmap[idx] = Math.min(hmap[idx], -4);
                matMap[idx] = MAT_WATER;
                biomeMap[idx] = 5;
              }
            } else if (effD <= halfW + 13.0) {
              if (matMap[idx] !== MAT_WATER) {
                hmap[idx] = Math.min(hmap[idx], -1);
                matMap[idx] = MAT_SAND;
                biomeMap[idx] = 5;
              }
            } else if (effD <= bankW) {
              if (matMap[idx] !== MAT_WATER) {
                hmap[idx] = Math.min(hmap[idx], 0);
                matMap[idx] = MAT_SAND;
              }
            }
          }
        }
      }
    }

    function thermalAndHydraulicErosion(thermalIters = 5, dropletCount = 260) {
      const tmp = new Int16Array(mw * mh);
      for (let it = 0; it < thermalIters; it++) {
        tmp.set(hmap);
        for (let my = 1; my < mh - 1; my++) {
          const row = my * mw;
          for (let mx = 1; mx < mw - 1; mx++) {
            const idx = row + mx;
            const m = matMap[idx];
            if (cliffMask[idx] || isWetMat(m) || m === MAT_BRIDGE || m === MAT_LILYPAD) continue;
            const talus = (m === MAT_STONE) ? 4 : 2;
            const nb0 = idx - 1, nb1 = idx + 1, nb2 = idx - mw, nb3 = idx + mw;
            let lowNb = nb0, lowH = hmap[nb0];
            if (hmap[nb1] < lowH) { lowH = hmap[nb1]; lowNb = nb1; }
            if (hmap[nb2] < lowH) { lowH = hmap[nb2]; lowNb = nb2; }
            if (hmap[nb3] < lowH) { lowH = hmap[nb3]; lowNb = nb3; }
            if (hmap[idx] - lowH > talus) {
              const nbMat = matMap[lowNb];
              if (!cliffMask[lowNb] && !isWetMat(nbMat) && nbMat !== MAT_BRIDGE && nbMat !== MAT_LILYPAD) {
                const delta = Math.max(1, Math.round(((hmap[idx] - lowH) - talus) * 0.30));
                tmp[idx] = Math.max(0, tmp[idx] - delta);
                tmp[lowNb] = Math.min(64, tmp[lowNb] + delta);
              }
            }
          }
        }
        hmap.set(tmp);
      }

      let seed = 133742;
      const nextRand = () => {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 4294967296;
      };

      for (let d = 0; d < dropletCount; d++) {
        let mx = 0, my = 0, found = false;
        for (let tries = 0; tries < 8; tries++) {
          const tx = 8 + Math.floor(nextRand() * (mw - 16));
          const ty = 8 + Math.floor(nextRand() * (mh - 16));
          const tidx = ty * mw + tx;
          if (hmap[tidx] >= 14 && !cliffMask[tidx] && matMap[tidx] !== MAT_PATH && !isWetMat(matMap[tidx])) {
            mx = tx;
            my = ty;
            found = true;
            break;
          }
        }
        if (!found) continue;

        let sediment = 0;
        for (let step = 0; step < 24; step++) {
          if (mx <= 1 || mx >= mw - 2 || my <= 1 || my >= mh - 2) break;
          const idx = my * mw + mx;
          const curH = hmap[idx];
          let lowX = mx, lowY = my, lowNb = idx, lowH = curH;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              if (dx === 0 && dy === 0) continue;
              const nx = mx + dx, ny = my + dy;
              const nidx = ny * mw + nx;
              if (hmap[nidx] < lowH) {
                lowH = hmap[nidx];
                lowNb = nidx;
                lowX = nx;
                lowY = ny;
              }
            }
          }
          const drop = curH - lowH;
          const nbMat = matMap[lowNb];
          if (drop <= 0 || cliffMask[lowNb] || isWetMat(nbMat) || nbMat === MAT_BRIDGE || nbMat === MAT_LILYPAD) {
            if (sediment > 0 && !cliffMask[idx] && matMap[idx] !== MAT_PATH) {
              hmap[idx] = Math.min(64, hmap[idx] + 1);
            }
            break;
          }
          if (drop >= 2 && drop <= 7 && matMap[idx] !== MAT_PATH) {
            hmap[idx] = Math.max(0, hmap[idx] - 1);
            sediment++;
          } else if (drop === 1 && sediment > 0 && matMap[idx] !== MAT_PATH) {
            hmap[idx] = Math.min(64, hmap[idx] + 1);
            sediment--;
          }
          mx = lowX;
          my = lowY;
        }
      }
    }

    function elasticChainRelax(iterations = 2) {
      const tmp = new Int16Array(mw * mh);
      for (let it = 0; it < iterations; it++) {
        tmp.set(hmap);
        for (let my = 1; my < mh - 1; my++) {
          const row = my * mw;
          for (let mx = 1; mx < mw - 1; mx++) {
            const idx = row + mx;
            if (cliffMask[idx] || isWetMat(matMap[idx]) || matMap[idx] === MAT_BRIDGE || matMap[idx] === MAT_LILYPAD) {
              continue;
            }
            const hC = hmap[idx];
            const hL = hmap[idx - 1];
            const hR = hmap[idx + 1];
            const hU = hmap[idx - mw];
            const hD = hmap[idx + mw];
            const avg = (hL + hR + hU + hD) * 0.25;
            const maxNb = Math.max(hL, hR, hU, hD);
            const minNb = Math.min(hL, hR, hU, hD);
            let next = hC;
            if (maxNb - hC > 3) {
              next = Math.round(hC + (avg - hC) * 0.55);
              if (maxNb - next > 2) next = Math.max(next, maxNb - 2);
            } else if (hC - minNb > 3) {
              next = Math.round(hC + (avg - hC) * 0.45);
            }
            tmp[idx] = Math.max(Z_MIN, Math.min(64, next));
          }
        }
        hmap.set(tmp);
      }
    }

    function buildStandableMap() {
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const edgeY = my < 2 || my >= mh - 2;
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          const h0 = hmap[idx];
          const mat = matMap[idx];
          cliffTopMap[idx] = h0;

          if (mat === MAT_WATER) {
            standableMap[idx] = 0;
            continue;
          }
          if (mat === MAT_BRIDGE || mat === MAT_LILYPAD || mat === MAT_SHALLOW) {
            standableMap[idx] = 1;
            continue;
          }
          if (edgeY || mx < 2 || mx >= mw - 2) {
            standableMap[idx] = 1;
            continue;
          }

          let min3 = h0, max3 = h0;
          for (let dy = -1; dy <= 1; dy++) {
            const nbRow = (my + dy) * mw;
            for (let dx = -1; dx <= 1; dx++) {
              const hv = hmap[nbRow + mx + dx];
              if (hv < min3) min3 = hv;
              if (hv > max3) max3 = hv;
            }
          }

          if (max3 - h0 <= 3 && h0 - min3 <= 3) {
            standableMap[idx] = 1;
            continue;
          }

          let nearCount = 0;
          let min5 = h0;
          for (let dy = -2; dy <= 2; dy++) {
            const nbRow = (my + dy) * mw;
            for (let dx = -2; dx <= 2; dx++) {
              const nb = nbRow + mx + dx;
              const hv = hmap[nb];
              if (hv < min5) min5 = hv;
              if (matMap[nb] !== MAT_WATER && Math.abs(hv - h0) <= 3) {
                nearCount++;
              }
            }
          }

          if (h0 - min5 <= 2) {
            standableMap[idx] = 1;
            continue;
          }
          if (max3 - h0 > 4 && h0 - min3 > 4) {
            standableMap[idx] = 0;
          } else {
            standableMap[idx] = nearCount >= 14 ? 1 : 0;
          }
        }
      }

      // Segundo passo: para células não-pisáveis em falésias secas, guarda altura máxima local (r=5)
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const y0 = Math.max(0, my - 5);
        const y1 = Math.min(mh - 1, my + 5);
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          if (standableMap[idx] !== 0 || isWetMat(matMap[idx])) continue;
          const x0 = Math.max(0, mx - 5);
          const x1 = Math.min(mw - 1, mx + 5);
          let maxH = hmap[idx];
          for (let ny = y0; ny <= y1; ny++) {
            const nRow = ny * mw;
            for (let nx = x0; nx <= x1; nx++) {
              const hv = hmap[nRow + nx];
              if (hv > maxH) maxH = hv;
            }
          }
          cliffTopMap[idx] = maxH;
        }
      }
    }

    function setCirclePatch(cx, cy, radius, height, mat, biome, isCliff = true) {
      const x0 = Math.max(0, Math.floor((cx - radius - 2) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + radius + 2) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - radius - 2) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + radius + 2) / VOX + HALF_GRID));
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const n = fbm2d(wx * 0.14, wy * 0.14) * 1.1;
          if (Math.hypot(wx - cx, wy - cy) <= radius + n) {
            const idx = my * mw + mx;
            hmap[idx] = height;
            matMap[idx] = mat;
            if (biome !== null) biomeMap[idx] = biome;
            if (isCliff) cliffMask[idx] = 1;
          }
        }
      }
    }

    function setBridgeRect(xMin, xMax, yMin, yMax, z, mat = MAT_BRIDGE, biome = 5) {
      const gx0 = Math.max(0, Math.floor(xMin / VOX + HALF_GRID));
      const gx1 = Math.min(mw - 1, Math.floor(xMax / VOX + HALF_GRID));
      const gy0 = Math.max(0, Math.floor(yMin / VOX + HALF_GRID));
      const gy1 = Math.min(mh - 1, Math.floor(yMax / VOX + HALF_GRID));
      for (let my = gy0; my <= gy1; my++) {
        for (let mx = gx0; mx <= gx1; mx++) {
          const idx = my * mw + mx;
          hmap[idx] = z;
          matMap[idx] = mat;
          biomeMap[idx] = biome;
          cliffMask[idx] = 1;
        }
      }
    }

    const bridges = [];

    function addArchBridge(cfg) {
      bridges.push(cfg);
      const gx0 = Math.max(0, Math.floor(cfg.xMin / VOX + HALF_GRID));
      const gx1 = Math.min(mw - 1, Math.floor(cfg.xMax / VOX + HALF_GRID));
      const gy0 = Math.max(0, Math.floor(cfg.yMin / VOX + HALF_GRID));
      const gy1 = Math.min(mh - 1, Math.floor(cfg.yMax / VOX + HALF_GRID));
      for (let my = gy0; my <= gy1; my++) {
        const row = my * mw;
        for (let mx = gx0; mx <= gx1; mx++) {
          noGrassMask[row + mx] = 1;
        }
      }
    }

    function getBridgeDeckZ(br, wx, wy) {
      const uc = br.axis === 'x'
        ? Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)))
        : Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)));
      return Math.round(br.baseZ + br.archH * (1 - (2 * uc - 1) * (2 * uc - 1)));
    }

    function getBridgeAt(wx, wy, pad = 0) {
      for (let i = 0; i < bridges.length; i++) {
        const br = bridges[i];
        if (wx >= br.xMin - pad && wx <= br.xMax + pad && wy >= br.yMin - pad && wy <= br.yMax + pad) {
          return br;
        }
      }
      return null;
    }

