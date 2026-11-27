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
            else if (hmap[idx] > -2 && isWetMat(matMap[idx])) matMap[idx] = dryMatForHeight(hmap[idx]);
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
            else if (hmap[idx] > -2 && isWetMat(matMap[idx])) matMap[idx] = dryMatForHeight(hmap[idx]);
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
            else if (hmap[idx] > -2 && isWetMat(matMap[idx])) matMap[idx] = dryMatForHeight(hmap[idx]);
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
            waterDepth[idx] = waterH >= 0 ? Math.max(2, Math.round(3 + (1 - nd) * 2)) : 0;
            biomeMap[idx] = biome;
            cliffMask[idx] = 1;
          } else if (nd <= 1.0 + rimNorm) {
            hmap[idx] = rimH;
            matMap[idx] = MAT_SAND;
            waterDepth[idx] = 0;
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
              if (hmap[idx] > -2 && isWetMat(matMap[idx])) matMap[idx] = dryMatForHeight(hmap[idx]);
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

    // =========================================================================
    // HIDROLOGIA: BACIAS, TRANSBORDO, ESCOAMENTO AO NÍVEL DO MAR & CACHOEIRAS
    // =========================================================================
    const HYDRO_HEAP_CAP = 32768;
    let _hydroVisit = null;
    let _hydroParent = null;
    let _streamVisit = null;
    let _hydroStamp = 1;
    let _streamStamp = 1;
    const _heapIdx = new Int32Array(HYDRO_HEAP_CAP);
    const _heapKey = new Int16Array(HYDRO_HEAP_CAP);
    const _heapSeq = new Uint32Array(HYDRO_HEAP_CAP);
    let _heapLen = 0;
    let _heapSeqCounter = 0;

    function _ensureHydroBuffers() {
      const n = mw * mh;
      if (!_hydroVisit || _hydroVisit.length !== n) {
        _hydroVisit = new Uint32Array(n);
        _hydroParent = new Int32Array(n);
        _streamVisit = new Uint32Array(n);
        _hydroStamp = 1;
        _streamStamp = 1;
      }
    }

    function _nextHydroStamp() {
      _ensureHydroBuffers();
      _hydroStamp++;
      if (_hydroStamp >= 0x7fffffff) {
        _hydroVisit.fill(0);
        _hydroStamp = 1;
      }
      return _hydroStamp;
    }

    function _nextStreamStamp() {
      _ensureHydroBuffers();
      _streamStamp++;
      if (_streamStamp >= 0x7fffffff) {
        _streamVisit.fill(0);
        _streamStamp = 1;
      }
      return _streamStamp;
    }

    function _heapReset() {
      _heapLen = 0;
      _heapSeqCounter = 0;
    }

    function _heapLess(a, b) {
      if (_heapKey[a] !== _heapKey[b]) return _heapKey[a] < _heapKey[b];
      return _heapSeq[a] < _heapSeq[b];
    }

    function _heapPush(idx, key) {
      if (_heapLen >= HYDRO_HEAP_CAP) return false;
      let i = _heapLen++;
      _heapIdx[i] = idx;
      _heapKey[i] = key;
      _heapSeq[i] = _heapSeqCounter++;
      while (i > 0) {
        const p = (i - 1) >> 1;
        if (!_heapLess(i, p)) break;
        const ti = _heapIdx[p], tk = _heapKey[p], ts = _heapSeq[p];
        _heapIdx[p] = _heapIdx[i]; _heapKey[p] = _heapKey[i]; _heapSeq[p] = _heapSeq[i];
        _heapIdx[i] = ti; _heapKey[i] = tk; _heapSeq[i] = ts;
        i = p;
      }
      return true;
    }

    function _heapPop() {
      const idx = _heapIdx[0];
      const key = _heapKey[0];
      _heapLen--;
      if (_heapLen > 0) {
        _heapIdx[0] = _heapIdx[_heapLen];
        _heapKey[0] = _heapKey[_heapLen];
        _heapSeq[0] = _heapSeq[_heapLen];
        let i = 0;
        while (true) {
          const l = (i << 1) + 1;
          const r = l + 1;
          let smallest = i;
          if (l < _heapLen && _heapLess(l, smallest)) smallest = l;
          if (r < _heapLen && _heapLess(r, smallest)) smallest = r;
          if (smallest === i) break;
          const ti = _heapIdx[i], tk = _heapKey[i], ts = _heapSeq[i];
          _heapIdx[i] = _heapIdx[smallest]; _heapKey[i] = _heapKey[smallest]; _heapSeq[i] = _heapSeq[smallest];
          _heapIdx[smallest] = ti; _heapKey[smallest] = tk; _heapSeq[smallest] = ts;
          i = smallest;
        }
      }
      return { idx, key };
    }

    function getSolidBedAtIdx(idx) {
      if (!isWetMat(matMap[idx])) return hmap[idx];
      if (waterDepth[idx] > 0) return Math.max(Z_MIN, hmap[idx] - waterDepth[idx]);
      return Math.max(Z_MIN, hmap[idx]);
    }

    function dryMatForHeight(h) {
      if (h >= 42) return MAT_PEAK;
      if (h <= 2) return MAT_SAND;
      return MAT_GRASS;
    }

    function drainElevatedWetCell(idx, onTouchIdx = null) {
      if (!isWetMat(matMap[idx])) return false;
      const h = hmap[idx];
      if (h <= -2) return false;
      waterDepth[idx] = 0;
      matMap[idx] = dryMatForHeight(h);
      if (onTouchIdx) onTouchIdx(idx);
      return true;
    }

    function paintWetCell(idx, surfZ, bedZ, preferredMat = null, onTouchIdx = null) {
      const clampedSurf = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX - 1, surfZ));
      const clampedBed = Math.max(Z_MIN, Math.min(clampedSurf, bedZ));
      if (clampedSurf <= -2) {
        if (preferredMat === MAT_SHALLOW) {
          hmap[idx] = -2;
          waterDepth[idx] = 0;
          matMap[idx] = MAT_SHALLOW;
        } else {
          hmap[idx] = Math.min(-4, clampedBed <= -4 ? clampedBed : -4);
          waterDepth[idx] = 0;
          matMap[idx] = MAT_WATER;
        }
      } else {
        const depth = Math.max(1, Math.min(255, clampedSurf - clampedBed));
        hmap[idx] = clampedSurf;
        waterDepth[idx] = depth;
        matMap[idx] = preferredMat === MAT_SHALLOW
          ? MAT_SHALLOW
          : (depth >= 3 ? MAT_WATER : MAT_SHALLOW);
      }
      if (typeof caveFloor !== 'undefined' && typeof caveCeil !== 'undefined' && caveCeil[idx] > caveFloor[idx]) {
        const effTop = clampedSurf <= -2 ? clampedSurf : clampedBed;
        if (effTop <= caveCeil[idx]) {
          if (effTop - 3 > caveFloor[idx] + 3) {
            caveCeil[idx] = effTop - 3;
          } else {
            caveFloor[idx] = -32768;
            caveCeil[idx] = -32768;
          }
        }
      }
      if (onTouchIdx) onTouchIdx(idx);
    }

    function findBasinOrOutlet(seedMx, seedMy, maxCells = 6000) {
      const sIdx = seedMy * mw + seedMx;
      const seedBed = getSolidBedAtIdx(sIdx);
      if (seedBed <= -2) {
        return { type: 'sea', spillZ: -2, saddleIdx: -1, outletIdx: sIdx, basinCells: [], pathToSaddle: [] };
      }

      const stamp = _nextHydroStamp();
      _heapReset();
      _hydroVisit[sIdx] = stamp;
      _hydroParent[sIdx] = -1;
      _heapPush(sIdx, seedBed);

      let maxLevel = seedBed;
      const poppedIdx = [];
      const poppedBed = [];
      const nOff = [-1, 1, -mw, mw];

      while (_heapLen > 0 && poppedIdx.length < maxCells) {
        const cur = _heapPop();
        const u = cur.idx;
        const uBed = cur.key;
        if (uBed > maxLevel) maxLevel = uBed;
        poppedIdx.push(u);
        poppedBed.push(uBed);

        const ux = u % mw;
        const uy = (u / mw) | 0;
        if (ux === 0 || ux === mw - 1 || uy === 0 || uy === mh - 1 || uBed <= -2) {
          const basinCells = [];
          for (let i = 0; i < poppedIdx.length; i++) {
            if (poppedBed[i] < maxLevel) basinCells.push(poppedIdx[i]);
          }
          const pathToSaddle = [];
          let p = u;
          while (p >= 0 && pathToSaddle.length < 512) {
            pathToSaddle.push(p);
            p = _hydroParent[p];
          }
          pathToSaddle.reverse();
          return { type: 'spill', spillZ: maxLevel, saddleIdx: u, outletIdx: u, basinCells, pathToSaddle };
        }

        for (let k = 0; k < 4; k++) {
          const v = u + nOff[k];
          if (_hydroVisit[v] === stamp) continue;
          const vBed = getSolidBedAtIdx(v);
          if (vBed < maxLevel) {
            const basinCells = [];
            for (let i = 0; i < poppedIdx.length; i++) {
              if (poppedBed[i] < maxLevel) basinCells.push(poppedIdx[i]);
            }
            const pathToSaddle = [];
            let p = u;
            while (p >= 0 && pathToSaddle.length < 512) {
              pathToSaddle.push(p);
              p = _hydroParent[p];
            }
            pathToSaddle.reverse();
            return { type: 'spill', spillZ: maxLevel, saddleIdx: u, outletIdx: v, basinCells, pathToSaddle };
          }
          _hydroVisit[v] = stamp;
          _hydroParent[v] = u;
          if (!_heapPush(v, vBed)) {
            break;
          }
        }
      }

      return { type: 'flat_or_huge', spillZ: maxLevel, saddleIdx: -1, outletIdx: -1, basinCells: poppedIdx, pathToSaddle: [] };
    }

    function fillBasinCells(basinCells, surfZ, preferredMat = null, onTouchIdx = null) {
      let minMx = mw, minMy = mh, maxMx = -1, maxMy = -1;
      for (let i = 0; i < basinCells.length; i++) {
        const idx = basinCells[i];
        const bed = getSolidBedAtIdx(idx);
        if (bed >= surfZ) continue;
        paintWetCell(idx, surfZ, bed, preferredMat, onTouchIdx);
        const mx = idx % mw;
        const my = (idx / mw) | 0;
        if (mx < minMx) minMx = mx;
        if (mx > maxMx) maxMx = mx;
        if (my < minMy) minMy = my;
        if (my > maxMy) maxMy = my;
      }
      return { minMx, minMy, maxMx, maxMy };
    }

    function traceSteepestStream(startMx, startMy, onTouchIdx = null, maxSteps = 4096) {
      const sStamp = _nextStreamStamp();
      let curIdx = startMy * mw + startMx;
      let minMx = startMx, minMy = startMy, maxMx = startMx, maxMy = startMy;
      const expandBounds = (idx) => {
        const mx = idx % mw;
        const my = (idx / mw) | 0;
        if (mx < minMx) minMx = mx;
        if (mx > maxMx) maxMx = mx;
        if (my < minMy) minMy = my;
        if (my > maxMy) maxMy = my;
      };

      const dxs = [-1, 1, 0, 0, -1, 1, -1, 1];
      const dys = [0, 0, -1, 1, -1, -1, 1, 1];
      let prevDx = 0, prevDy = 0;
      let steps = 0;
      let legCount = 0;

      while (steps < maxSteps && legCount < 1024) {
        legCount++;
        while (steps < maxSteps) {
          steps++;
          const mx = curIdx % mw;
          const my = (curIdx / mw) | 0;
          if (mx <= 0 || mx >= mw - 1 || my <= 0 || my >= mh - 1) {
            return { minMx, minMy, maxMx, maxMy };
          }
          _streamVisit[curIdx] = sStamp;
          const curBed = getSolidBedAtIdx(curIdx);
          if (curBed <= -2) {
            paintWetCell(curIdx, -2, curBed, MAT_SHALLOW, onTouchIdx);
            expandBounds(curIdx);
            return { minMx, minMy, maxMx, maxMy };
          }

          let bestNb = -1;
          let bestScore = -Infinity;
          let bestBed = curBed;
          let bestDx = 0, bestDy = 0;

          for (let k = 0; k < 8; k++) {
            const nx = mx + dxs[k];
            const ny = my + dys[k];
            if (nx < 0 || nx >= mw || ny < 0 || ny >= mh) continue;
            const nIdx = ny * mw + nx;
            if (_streamVisit[nIdx] === sStamp) continue;
            const nBed = getSolidBedAtIdx(nIdx);
            if (nBed >= curBed) continue;
            const dist = k < 4 ? 1.0 : 1.414;
            const slope = (curBed - nBed) / dist;
            const align = (dxs[k] * prevDx + dys[k] * prevDy) > 0 ? 0.08 : 0;
            const score = slope + align;
            if (score > bestScore) {
              bestScore = score;
              bestNb = nIdx;
              bestBed = nBed;
              bestDx = dxs[k];
              bestDy = dys[k];
            }
          }

          if (bestNb < 0) break; // Local minimum or flat shelf

          const drop = curBed - bestBed;
          const isDrop = drop >= 3;
          // Crest / stream cell
          paintWetCell(curIdx, curBed + 1, curBed, isDrop ? MAT_WATER : MAT_SHALLOW, onTouchIdx);
          expandBounds(curIdx);

          // Widen gentle stream slightly on flat/lower side cells without climbing walls
          if (!isDrop) {
            for (let k = 0; k < 4; k++) {
              const sx = mx + dxs[k];
              const sy = my + dys[k];
              if (sx <= 0 || sx >= mw - 1 || sy <= 0 || sy >= mh - 1) continue;
              const sIdx = sy * mw + sx;
              if (isWetMat(matMap[sIdx])) continue;
              const sBed = getSolidBedAtIdx(sIdx);
              if (sBed <= curBed && sBed >= curBed - 1 && sBed > -2) {
                paintWetCell(sIdx, sBed + 1, sBed, MAT_SHALLOW, onTouchIdx);
                expandBounds(sIdx);
              }
            }
          }

          if (bestBed <= -2) {
            paintWetCell(bestNb, -2, bestBed, MAT_SHALLOW, onTouchIdx);
            expandBounds(bestNb);
            return { minMx, minMy, maxMx, maxMy };
          }

          // Plunge pool at foot of a steep waterfall drop
          if (isDrop) {
            const bmx = bestNb % mw;
            const bmy = (bestNb / mw) | 0;
            const poolSurf = bestBed + 2;
            for (let pdy = -1; pdy <= 1; pdy++) {
              const py = bmy + pdy;
              if (py <= 0 || py >= mh - 1) continue;
              for (let pdx = -1; pdx <= 1; pdx++) {
                const px = bmx + pdx;
                if (px <= 0 || px >= mw - 1) continue;
                const pIdx = py * mw + px;
                const pBed = getSolidBedAtIdx(pIdx);
                if (pBed <= bestBed + 1) {
                  const isCenter = (pdx === 0 && pdy === 0);
                  const d = isCenter ? 2 : 1;
                  paintWetCell(pIdx, Math.max(poolSurf, pBed + d), Math.min(pBed, poolSurf - d), isCenter ? MAT_WATER : MAT_SHALLOW, onTouchIdx);
                  expandBounds(pIdx);
                }
              }
            }
          }

          prevDx = bestDx;
          prevDy = bestDy;
          curIdx = bestNb;
        }

        // Hit a local minimum or flat shelf: find basin spillover or flat path to next drop
        const cmx = curIdx % mw;
        const cmy = (curIdx / mw) | 0;
        const res = findBasinOrOutlet(cmx, cmy, 8000);
        if (res.type === 'sea') {
          paintWetCell(curIdx, -2, getSolidBedAtIdx(curIdx), MAT_SHALLOW, onTouchIdx);
          expandBounds(curIdx);
          break;
        }
        if (res.type === 'spill') {
          if (res.basinCells.length > 0) {
            const bBounds = fillBasinCells(res.basinCells, res.spillZ, null, onTouchIdx);
            if (bBounds.maxMx >= 0) {
              if (bBounds.minMx < minMx) minMx = bBounds.minMx;
              if (bBounds.minMy < minMy) minMy = bBounds.minMy;
              if (bBounds.maxMx > maxMx) maxMx = bBounds.maxMx;
              if (bBounds.maxMy > maxMy) maxMy = bBounds.maxMy;
            }
            for (let i = 0; i < res.basinCells.length; i++) {
              _streamVisit[res.basinCells[i]] = sStamp;
            }
          }
          if (res.pathToSaddle.length > 0) {
            for (let i = 0; i < res.pathToSaddle.length; i++) {
              const pIdx = res.pathToSaddle[i];
              _streamVisit[pIdx] = sStamp;
              const pBed = getSolidBedAtIdx(pIdx);
              if (res.basinCells.length === 0 || pBed >= res.spillZ) {
                paintWetCell(pIdx, pBed + 1, pBed, MAT_SHALLOW, onTouchIdx);
                expandBounds(pIdx);
              }
            }
          }
          if (res.saddleIdx >= 0 && res.saddleIdx !== res.outletIdx) {
            const sBed = getSolidBedAtIdx(res.saddleIdx);
            paintWetCell(res.saddleIdx, Math.max(res.spillZ, sBed + 1), sBed, MAT_SHALLOW, onTouchIdx);
            expandBounds(res.saddleIdx);
            _streamVisit[res.saddleIdx] = sStamp;
          }
          if (res.outletIdx < 0 || res.outletIdx === curIdx || _streamVisit[res.outletIdx] === sStamp) break;
          curIdx = res.outletIdx;
          prevDx = 0; prevDy = 0;
        } else {
          // Flat plain with no outlet within range: form a small terminal pool
          const curBed = getSolidBedAtIdx(curIdx);
          if (curBed > -2) {
            paintWetCell(curIdx, curBed, Math.max(Z_MIN, curBed - 2), MAT_SHALLOW, onTouchIdx);
            expandBounds(curIdx);
          }
          break;
        }
      }

      return { minMx, minMy, maxMx, maxMy };
    }

    function applyWaterBrushHydrology(cx, cy, rCells, toolId, onTouchIdx = null, isInitialClick = true) {
      const prefMat = toolId === 'mat_shallow' ? MAT_SHALLOW : MAT_WATER;
      const cIdx = cy * mw + cx;
      const bedC = getSolidBedAtIdx(cIdx);
      let minMx = Math.max(1, cx - rCells - 1);
      let maxMx = Math.min(mw - 2, cx + rCells + 1);
      let minMy = Math.max(1, cy - rCells - 1);
      let maxMy = Math.min(mh - 2, cy + rCells + 1);
      const mergeBounds = (b) => {
        if (!b || b.maxMx < 0) return;
        if (b.minMx < minMx) minMx = b.minMx;
        if (b.minMy < minMy) minMy = b.minMy;
        if (b.maxMx > maxMx) maxMx = b.maxMx;
        if (b.maxMy > maxMy) maxMy = b.maxMy;
      };

      // 1. Nível do mar ou abaixo (Z <= -2): pintura clássica sem afundar montanhas
      if (bedC <= -2) {
        const r2 = rCells * rCells;
        for (let my = minMy; my <= maxMy; my++) {
          const dy = my - cy;
          for (let mx = minMx; mx <= maxMx; mx++) {
            const dx = mx - cx;
            if (dx * dx + dy * dy > r2) continue;
            const idx = my * mw + mx;
            const b = getSolidBedAtIdx(idx);
            if (b <= -1) {
              paintWetCell(idx, -2, Math.min(b, prefMat === MAT_SHALLOW ? -2 : -4), prefMat, onTouchIdx);
            }
          }
        }
        return { minMx, minMy, maxMx, maxMy };
      }

      // 2. Acima do nível do mar: detectar se está dentro de uma bacia/cratera fechada
      const res = findBasinOrOutlet(cx, cy, 16384);
      const hasRealOutlet = res.type === 'spill' && res.outletIdx >= 0 &&
        (getSolidBedAtIdx(res.outletIdx) < res.spillZ || res.spillZ <= -2);
      if (hasRealOutlet && res.basinCells.length > 0) {
        let minBasinBed = bedC;
        for (let i = 0; i < res.basinCells.length; i++) {
          const b = getSolidBedAtIdx(res.basinCells[i]);
          if (b < minBasinBed) minBasinBed = b;
        }
        const targetSurf = res.spillZ - minBasinBed >= 2 ? (res.spillZ - 1) : res.spillZ;
        const alreadyFilled = isWetMat(matMap[cIdx]) && hmap[cIdx] >= targetSurf;
        if (!alreadyFilled) {
          const b = fillBasinCells(res.basinCells, targetSurf, toolId === 'mat_shallow' ? MAT_SHALLOW : null, onTouchIdx);
          mergeBounds(b);
        } else if (isInitialClick) {
          // Segundo clique em bacia já cheia: transborda pela fenda mais baixa até o nível do mar!
          const b = fillBasinCells(res.basinCells, res.spillZ, toolId === 'mat_shallow' ? MAT_SHALLOW : null, onTouchIdx);
          mergeBounds(b);
          if (res.saddleIdx >= 0) {
            const sBed = getSolidBedAtIdx(res.saddleIdx);
            paintWetCell(res.saddleIdx, Math.max(res.spillZ, sBed + 1), sBed, MAT_SHALLOW, onTouchIdx);
          }
          if (res.outletIdx >= 0) {
            mergeBounds(traceSteepestStream(res.outletIdx % mw, (res.outletIdx / mw) | 0, onTouchIdx));
          }
        }
        return { minMx, minMy, maxMx, maxMy };
      }

      if (hasRealOutlet && res.basinCells.length === 0 && getSolidBedAtIdx(res.outletIdx) < bedC) {
        // Só escoa se não estiver apenas arrastando a borda de uma lagoa já aberta em platô plano
        const draggingIntoFlatPond = !isInitialClick && isWetMat(matMap[res.outletIdx]);
        if (!draggingIntoFlatPond) {
          // Encosta aberta / fenda: escoa morro abaixo até o mar!
          mergeBounds(traceSteepestStream(cx, cy, onTouchIdx));
          return { minMx, minMy, maxMx, maxMy };
        }
      }

      // 3. Planície/platô plano sem borda ao redor: cria/expande lagoa rasa sem perfurar o solo repetidamente
      const r2 = rCells * rCells;
      let pondSurfZ = isWetMat(matMap[cIdx]) && hmap[cIdx] >= 0 ? hmap[cIdx] : null;
      if (pondSurfZ === null) {
        for (let my = minMy; my <= maxMy && pondSurfZ === null; my++) {
          const dy = my - cy;
          for (let mx = minMx; mx <= maxMx; mx++) {
            const dx = mx - cx;
            if (dx * dx + dy * dy > r2) continue;
            const idx = my * mw + mx;
            if (isWetMat(matMap[idx]) && hmap[idx] >= 0) {
              pondSurfZ = hmap[idx];
              break;
            }
          }
        }
      }
      if (pondSurfZ === null) pondSurfZ = bedC >= 0 ? bedC - 1 : -1;

      for (let my = minMy; my <= maxMy; my++) {
        const dy = my - cy;
        for (let mx = minMx; mx <= maxMx; mx++) {
          const dx = mx - cx;
          const d2 = dx * dx + dy * dy;
          if (d2 > r2) continue;
          const idx = my * mw + mx;
          const edgeDist = rCells - Math.sqrt(d2);
          let depth = edgeDist >= 2.0 ? 3 : (edgeDist >= 0.8 ? 2 : 1);
          if (toolId === 'mat_shallow') depth = Math.min(2, depth);
          if (isWetMat(matMap[idx])) {
            if (hmap[idx] === pondSurfZ && depth > waterDepth[idx]) {
              const bedZ = Math.max(Z_MIN, pondSurfZ - depth);
              paintWetCell(idx, pondSurfZ, bedZ, depth >= 3 && toolId !== 'mat_shallow' ? MAT_WATER : MAT_SHALLOW, onTouchIdx);
            }
            continue;
          }
          const origBed = getSolidBedAtIdx(idx);
          if (origBed < pondSurfZ) continue;
          const bedZ = Math.max(Z_MIN, pondSurfZ - depth);
          paintWetCell(idx, pondSurfZ, bedZ, depth >= 3 && toolId !== 'mat_shallow' ? MAT_WATER : MAT_SHALLOW, onTouchIdx);
        }
      }
      return { minMx, minMy, maxMx, maxMy };
    }

    function placeSpringHydrology(cx, cy, onTouchIdx = null) {
      const cIdx = cy * mw + cx;
      const bedC = getSolidBedAtIdx(cIdx);
      paintWetCell(cIdx, bedC > -2 ? bedC + 1 : -2, bedC, MAT_WATER, onTouchIdx);
      const b = traceSteepestStream(cx, cy, onTouchIdx);
      return {
        minMx: Math.min(Math.max(1, cx - 2), b.minMx),
        minMy: Math.min(Math.max(1, cy - 2), b.minMy),
        maxMx: Math.max(Math.min(mw - 2, cx + 2), b.maxMx),
        maxMy: Math.max(Math.min(mh - 2, cy + 2), b.maxMy)
      };
    }

    function drainBreachedLakesInRect(mx0, my0, mx1, my1, onTouchIdx = null) {
      const x0 = Math.max(1, mx0 - 1);
      const x1 = Math.min(mw - 2, mx1 + 1);
      const y0 = Math.max(1, my0 - 1);
      const y1 = Math.min(mh - 2, my1 + 1);
      const nOff8 = [-1, 1, -mw, mw, -mw - 1, -mw + 1, mw - 1, mw + 1];
      let changed = false;
      let minMx = x0, minMy = y0, maxMx = x1, maxMy = y1;
      const expand = (b) => {
        if (!b || b.maxMx < 0) return;
        if (b.minMx < minMx) minMx = b.minMx;
        if (b.minMy < minMy) minMy = b.minMy;
        if (b.maxMx > maxMx) maxMx = b.maxMx;
        if (b.maxMy > maxMy) maxMy = b.maxMy;
      };

      const seenLakes = new Set();
      for (let my = y0; my <= y1; my++) {
        for (let mx = x0; mx <= x1; mx++) {
          const idx = my * mw + mx;
          if (!isWetMat(matMap[idx]) || hmap[idx] < 0) continue;
          const wSurf = hmap[idx];
          if (seenLakes.has(idx)) continue;

          let hasLowerWet = false;
          let breachIdx = -1;
          let breachH = wSurf;
          for (let k = 0; k < 8; k++) {
            const nb = idx + nOff8[k];
            if (isWetMat(matMap[nb])) {
              if (hmap[nb] < wSurf) hasLowerWet = true;
            } else if (k < 4 && hmap[nb] < breachH) {
              breachH = hmap[nb];
              breachIdx = nb;
            }
          }
          if (hasLowerWet || breachIdx < 0) continue;

          // Coleta o lago conectado na cota wSurf
          const queue = [idx];
          const lakeCells = [];
          seenLakes.add(idx);
          let minRim = breachH;
          let minRimIdx = breachIdx;
          let maxLakeDepth = waterDepth[idx];
          while (queue.length > 0 && lakeCells.length < 16384) {
            const cur = queue.pop();
            lakeCells.push(cur);
            if (waterDepth[cur] > maxLakeDepth) maxLakeDepth = waterDepth[cur];
            for (let k = 0; k < 8; k++) {
              const nb = cur + nOff8[k];
              const nmx = nb % mw;
              const nmy = (nb / mw) | 0;
              if (nmx <= 0 || nmx >= mw - 1 || nmy <= 0 || nmy >= mh - 1) continue;
              if (isWetMat(matMap[nb])) {
                if (hmap[nb] < wSurf) hasLowerWet = true;
                else if (k < 4 && !seenLakes.has(nb) && hmap[nb] === wSurf) {
                  seenLakes.add(nb);
                  queue.push(nb);
                }
              } else if (k < 4 && hmap[nb] < minRim) {
                minRim = hmap[nb];
                minRimIdx = nb;
              }
            }
          }
          if (hasLowerWet) continue;
          if (maxLakeDepth < 2 && lakeCells.length < 4) continue;

          const newSurf = Math.max(Z_MIN, minRim);
          for (let i = 0; i < lakeCells.length; i++) {
            const c = lakeCells[i];
            const bed = getSolidBedAtIdx(c);
            if (bed >= newSurf) {
              hmap[c] = bed;
              waterDepth[c] = 0;
              matMap[c] = dryMatForHeight(bed);
              if (onTouchIdx) onTouchIdx(c);
            } else {
              paintWetCell(c, newSurf, bed, null, onTouchIdx);
            }
            const cmx = c % mw;
            const cmy = (c / mw) | 0;
            if (cmx < minMx) minMx = cmx;
            if (cmx > maxMx) maxMx = cmx;
            if (cmy < minMy) minMy = cmy;
            if (cmy > maxMy) maxMy = cmy;
          }
          if (minRimIdx >= 0) {
            expand(traceSteepestStream(minRimIdx % mw, (minRimIdx / mw) | 0, onTouchIdx));
          }
          changed = true;
        }
      }
      return { changed, minMx, minMy, maxMx, maxMy };
    }

