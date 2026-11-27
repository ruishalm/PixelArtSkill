    // =========================================================================
    // 6. PRÉ-BAKE TIGHT-CROP BOUNDED SLICES (terrainSlices + grassTipSlices)
    // =========================================================================
    const IS_LE = (new Uint8Array(new Uint32Array([0x11223344]).buffer))[0] === 0x44;
    function packRGBA(r, g, b, a = 255) {
      if (IS_LE) return ((a & 255) << 24) | ((b & 255) << 16) | ((g & 255) << 8) | (r & 255);
      return ((r & 255) << 24) | ((g & 255) << 16) | ((b & 255) << 8) | (a & 255);
    }

    function shadePack(rgb, delta, shadowPct = 0) {
      let r, g, b;
      if (shadowPct === 0) {
        r = rgb[0] + delta; r = r < 0 ? 0 : (r > 255 ? 255 : r);
        g = rgb[1] + delta; g = g < 0 ? 0 : (g > 255 ? 255 : g);
        b = rgb[2] + delta; b = b < 0 ? 0 : (b > 255 ? 255 : b);
      } else {
        const f = 1 - shadowPct * 0.01;
        r = Math.round((rgb[0] + delta) * f); r = r < 0 ? 0 : (r > 255 ? 255 : r);
        g = Math.round((rgb[1] + delta) * f); g = g < 0 ? 0 : (g > 255 ? 255 : g);
        b = Math.round((rgb[2] + delta) * f); b = b < 0 ? 0 : (b > 255 ? 255 : b);
      }
      if (IS_LE) return -16777216 | (b << 16) | (g << 8) | r;
      return (r << 24) | (g << 16) | (b << 8) | 255;
    }

    const PAL_GRASS_BASE = [
      [88, 178, 78], [80, 168, 72], [96, 188, 84], [108, 198, 90]
    ];
    const PAL_PATH = [[223, 182, 132], [211, 166, 115]];
    const PAL_SAND = [[243, 221, 169], [234, 208, 148]];
    const PAL_STONE = [[180, 186, 196], [163, 170, 181]];
    const PAL_BRIDGE = [[185, 122, 74], [166, 106, 62]];
    const PAL_PEAK = [[249, 168, 212], [123, 201, 111]];
    const PAL_LILYPAD = [[74, 222, 128], [34, 197, 94]];

    const PAL_BRIDGE_SIDE = [118, 72, 42];
    const PAL_LILYPAD_SIDE = [22, 130, 58];
    const PAL_SAND_SIDE = [196, 168, 112];
    const PAL_MOSS = [[58, 143, 56], [41, 107, 39]];
    const PAL_EARTH = [[156, 102, 68], [128, 79, 50]];
    const PAL_ROCK = [[109, 118, 132], [86, 95, 108]];

    const COL_GRASS_TIP_BASE = packRGBA(45, 120, 41, 255);   // #2D7829
    const COL_GRASS_TIP_MID  = packRGBA(82, 193, 75, 255);   // #52C14B
    const COL_GRASS_TIP_HIGH = packRGBA(139, 232, 101, 255); // #8BE865
    const COL_WILDFLOWERS = [
      packRGBA(253, 224, 71, 255),  // Amarelo
      packRGBA(255, 255, 255, 255), // Branco
      packRGBA(249, 168, 212, 255)  // Rosa
    ];

    const terrainSlices = {};
    const grassTipSlices = {};
    const waterfallDrops = [];

    const COL_BED = packRGBA(28, 66, 108, 255);
    const COL_FOAM_PLUNGE = packRGBA(236, 248, 255, 245);
    const COL_SHALLOW_A = packRGBA(72, 202, 245, 225);
    const COL_SHALLOW_B = packRGBA(95, 215, 250, 225);
    const COL_DEEP_A = packRGBA(56, 189, 248, 235);
    const COL_DEEP_B = packRGBA(42, 172, 236, 235);
    const COL_CALM_SHIMMER = packRGBA(186, 230, 253, 240);
    const COL_CALM_A = packRGBA(56, 189, 248, 235);
    const COL_CALM_B = packRGBA(72, 202, 245, 235);
    const COL_CALM_SUB = packRGBA(36, 168, 232, 235);
    const COL_DROP_FOAM = packRGBA(224, 242, 254, 255);
    const COL_DROP_TOP = packRGBA(56, 189, 248, 240);
    const COL_DROP_BODY = packRGBA(28, 158, 224, 255);
    const COL_SHALLOW_BED_A = packRGBA(198, 178, 134, 255);
    const COL_SHALLOW_BED_B = packRGBA(182, 162, 120, 255);
    const COL_SHALLOW_SURF_A = packRGBA(103, 232, 249, 200);
    const COL_SHALLOW_SURF_B = packRGBA(125, 240, 252, 200);
    const COL_SHALLOW_SHIMMER = packRGBA(224, 252, 255, 225);

    function getMinWetDropInfo(mx, my, surfZ) {
      let minWet = surfZ;
      let botMx = mx;
      let botMy = my;
      for (let dy = -1; dy <= 1; dy++) {
        const ny = my + dy;
        if (ny < 0 || ny >= mh) continue;
        const row = ny * mw;
        for (let dx = -1; dx <= 1; dx++) {
          if (dx === 0 && dy === 0) continue;
          const nx = mx + dx;
          if (nx < 0 || nx >= mw) continue;
          const nIdx = row + nx;
          if (!isWetMat(matMap[nIdx])) continue;
          const nh = hmap[nIdx];
          const ns = nh < 0 ? (matMap[nIdx] === MAT_SHALLOW ? -1 : -2) : nh;
          if (ns < minWet) {
            minWet = ns;
            botMx = nx;
            botMy = ny;
          }
        }
      }
      return { minWet, botMx, botMy };
    }

    function getMinWetDropNeighborZ(mx, my, surfZ) {
      return getMinWetDropInfo(mx, my, surfZ).minWet;
    }

    function computeWaterfallDrops() {
      waterfallDropMask.fill(0);
      waterfallDrops.length = 0;
      for (let my = 1; my < mh - 1; my++) {
        const row = my * mw;
        for (let mx = 1; mx < mw - 1; mx++) {
          const idx = row + mx;
          if (!isWetMat(matMap[idx])) continue;
          const h = hmap[idx];
          if (h < 0) continue;
          const info = getMinWetDropInfo(mx, my, h);
          if (h - info.minWet >= 3) {
            waterfallDropMask[idx] = 1;
            waterfallDrops.push({
              mx, my,
              wx: (mx - HALF_GRID + 0.5) * VOX,
              wy: (my - HALF_GRID + 0.5) * VOX,
              botWx: (info.botMx - HALF_GRID + 0.5) * VOX,
              botWy: (info.botMy - HALF_GRID + 0.5) * VOX,
              topZ: h,
              botZ: info.minWet
            });
          }
        }
      }
    }

    function bakeTerrainSlices() {
      computeWaterfallDrops();
      const nTerrain = TERRAIN_Z_MAX - Z_MIN + 1;
      const tMinX = new Int16Array(nTerrain).fill(mw);
      const tMaxX = new Int16Array(nTerrain).fill(-1);
      const tMinY = new Int16Array(nTerrain).fill(mh);
      const tMaxY = new Int16Array(nTerrain).fill(-1);

      const nGrass = Z_GRASS_MAX - Z_MIN + 1;
      const gMinX = new Int16Array(nGrass).fill(mw);
      const gMaxX = new Int16Array(nGrass).fill(-1);
      const gMinY = new Int16Array(nGrass).fill(mh);
      const gMaxY = new Int16Array(nGrass).fill(-1);

      const min8Cache = new Int16Array(mw * mh);
      const grassType = new Uint8Array(mw * mh); // 0=none, 1=2px, 2=3px verde, 3..5=3px flor

      const markT = (z, mx, my) => {
        const si = z - Z_MIN;
        if (mx < tMinX[si]) tMinX[si] = mx;
        if (mx > tMaxX[si]) tMaxX[si] = mx;
        if (my < tMinY[si]) tMinY[si] = my;
        if (my > tMaxY[si]) tMaxY[si] = my;
      };
      const markG = (z, mx, my) => {
        const gi = z - Z_MIN;
        if (mx < gMinX[gi]) gMinX[gi] = mx;
        if (mx > gMaxX[gi]) gMaxX[gi] = mx;
        if (my < gMinY[gi]) gMinY[gi] = my;
        if (my > gMaxY[gi]) gMaxY[gi] = my;
      };

      // Passo 1: Descobrir bounding boxes exatos + distribuir moitas orgânicas de grama
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const onBorderY = (my === 0 || my === mh - 1);
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          let h = hmap[idx];
          if (h < Z_MIN) h = Z_MIN;
          else if (h >= TERRAIN_Z_MAX) h = TERRAIN_Z_MAX - 1;
          const mat = matMap[idx];

          let min8 = 999;
          let max4 = h;
          let hL = h, hR = h, hU = h, hD = h;
          if (onBorderY || mx === 0 || mx === mw - 1) {
            min8 = -8;
          } else {
            hL = hmap[idx - 1];
            hR = hmap[idx + 1];
            hU = hmap[idx - mw];
            hD = hmap[idx + mw];
            const hLU = hmap[idx - mw - 1];
            const hRU = hmap[idx - mw + 1];
            const hLD = hmap[idx + mw - 1];
            const hRD = hmap[idx + mw + 1];
            min8 = hL;
            if (hR < min8) min8 = hR;
            if (hU < min8) min8 = hU;
            if (hD < min8) min8 = hD;
            if (hLU < min8) min8 = hLU;
            if (hRU < min8) min8 = hRU;
            if (hLD < min8) min8 = hLD;
            if (hRD < min8) min8 = hRD;
            max4 = hL;
            if (hR > max4) max4 = hR;
            if (hU > max4) max4 = hU;
            if (hD > max4) max4 = hD;
          }
          min8Cache[idx] = min8;

          if (mat === MAT_WATER || mat === MAT_SHALLOW) {
            const wd = waterDepth[idx];
            if (h < 0 && wd === 0) {
              if (mat === MAT_WATER) {
                const zEnd = h + 1 < -4 ? h + 1 : -4;
                for (let z = Z_MIN; z <= zEnd; z++) markT(z, mx, my);
                markT(-2, mx, my);
              } else {
                const zStartBed = Math.max(Z_MIN, min8 - 2);
                for (let z = zStartBed; z <= h; z++) markT(z, mx, my);
                markT(-1, mx, my);
              }
            } else {
              const surfZ = h < 0 ? (mat === MAT_SHALLOW ? -1 : -2) : h;
              const effDepth = wd > 0 ? wd : (mat === MAT_SHALLOW ? 1 : 2);
              const bedZ = Math.max(Z_MIN, surfZ - effDepth);
              if (waterfallDropMask[idx] === 1) {
                const minWet = getMinWetDropNeighborZ(mx, my, surfZ);
                const zDropBot = Math.max(Z_MIN, minWet - 1);
                const zStart = Math.max(Z_MIN, Math.min(min8 - 2, zDropBot));
                for (let z = zStart; z <= surfZ; z++) markT(z, mx, my);
              } else {
                const zStart = Math.max(Z_MIN, Math.min(min8 - 2, bedZ));
                for (let z = zStart; z <= surfZ; z++) markT(z, mx, my);
              }
            }
            continue;
          }

          const zStart = min8 - 2 > Z_MIN ? min8 - 2 : Z_MIN;
          if (zStart <= h) {
            for (let z = zStart; z <= h; z++) {
              const si = z - Z_MIN;
              if (mx < tMinX[si]) tMinX[si] = mx;
              if (mx > tMaxX[si]) tMaxX[si] = mx;
              if (my < tMinY[si]) tMinY[si] = my;
              if (my > tMaxY[si]) tMaxY[si] = my;
            }
          }

          // Grama orgânica em moitas usando fbm2dFast(mx*0.14, my*0.14) + hash XOR sem listras
          if ((mat === MAT_GRASS || mat === MAT_PEAK) && !noGrassMask[idx] && max4 <= h) {
            let nh = ((mx * 73856093) ^ (my * 19349663)) >>> 0;
            nh ^= nh >>> 13;
            nh = Math.imul(nh, 1274126177) >>> 0;
            const fine01 = nh / 4294967295;
            if (fine01 > 0.18) {
              const clumpVal = valueNoise2d(mx * 0.14, my * 0.14) * 0.9 + fine01 * 0.42;
              if (clumpVal > 0.43) {
                let gt = (clumpVal > 0.50 || (nh & 3) !== 0) ? 2 : 1;
                if (gt === 2 && (nh % 29 === 0)) {
                  gt = 3 + ((nh >>> 8) % 3);
                }
                grassType[idx] = gt;
                if (h + 1 <= TERRAIN_Z_MAX) markT(h + 1, mx, my);
                if (h + 2 <= Z_GRASS_MAX) markG(h + 2, mx, my);
                if (gt >= 2 && h + 3 <= Z_GRASS_MAX) markG(h + 3, mx, my);
              }
            }
          }
        }
      }

      // Passo 1b: Bounding boxes das pontes parabólicas em arco & píer
      for (const br of bridges) {
        const gx0 = Math.max(0, Math.floor(br.xMin / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.floor(br.xMax / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(br.yMin / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.floor(br.yMax / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const u = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)))
              : Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)));
            const v = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)))
              : Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)));
            const zDeck = Math.min(TERRAIN_Z_MAX - 1, getBridgeDeckZ(br, wx, wy));
            const zDeckStart = Math.max(Z_MIN, zDeck - 2);
            for (let z = zDeckStart; z <= zDeck; z++) markT(z, mx, my);

            const isPiling = br.isPier && ((Math.floor(wy - br.yMin) % 24) < 6) && (v <= 0.14 || v >= 0.86);
            const isAbutment = !br.isPier && (u <= 0.09 || u >= 0.91);
            if (isPiling || isAbutment) {
              for (let z = Z_MIN; z < zDeckStart; z++) markT(z, mx, my);
            }

            if (br.hasRailings && (v <= 0.08 || v >= 0.92)) {
              const alongIdx = br.axis === 'x' ? (mx - gx0) : (my - gy0);
              const isPost = (alongIdx % 7) === 0;
              const rStart = isPost ? zDeck + 1 : zDeck + 5;
              const rEnd = Math.min(TERRAIN_Z_MAX, zDeck + 6);
              for (let z = rStart; z <= rEnd; z++) markT(z, mx, my);
            }
          }
        }
      }

      // Aloca SOMENTE os buffers no tamanho justo (bw × bh) por fatia usada
      const terrainBufs = new Array(nTerrain).fill(null);
      const tW = new Int16Array(nTerrain);
      const tH = new Int16Array(nTerrain);
      for (let i = 0; i < nTerrain; i++) {
        if (tMaxX[i] >= tMinX[i]) {
          tW[i] = tMaxX[i] - tMinX[i] + 1;
          tH[i] = tMaxY[i] - tMinY[i] + 1;
          terrainBufs[i] = new Uint32Array(tW[i] * tH[i]);
        }
      }

      const grassBufs = new Array(nGrass).fill(null);
      const gW = new Int16Array(nGrass);
      const gH = new Int16Array(nGrass);
      for (let i = 0; i < nGrass; i++) {
        if (gMaxX[i] >= gMinX[i]) {
          gW[i] = gMaxX[i] - gMinX[i] + 1;
          gH[i] = gMaxY[i] - gMinY[i] + 1;
          grassBufs[i] = new Uint32Array(gW[i] * gH[i]);
        }
      }

      // Passo 2: Preenche diretamente os buffers recortados (Tight-Crop)
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const wySurf = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          const h = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX - 1, hmap[idx]));
          const mat = matMap[idx];
          const sh = shadowMask[idx];
          const min8 = min8Cache[idx];
          const nHash = ((Math.imul(mx, 73856093)) ^ (Math.imul(my, 19349663))) >>> 0;
          const microTex = ((nHash & 7) - 3) * 2;

          if (mat === MAT_WATER || mat === MAT_SHALLOW) {
            const wd = waterDepth[idx];
            if (h < 0 && wd === 0) {
              if (mat === MAT_WATER) {
                const zEnd = Math.min(-4, h + 1);
                for (let z = Z_MIN; z <= zEnd; z++) {
                  const si = z - Z_MIN;
                  terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = COL_BED;
                }
                const siSurf = -2 - Z_MIN;
                const isShallow = h > -6;
                terrainBufs[siSurf][(my - tMinY[siSurf]) * tW[siSurf] + (mx - tMinX[siSurf])] = isShallow
                  ? ((nHash & 1) ? COL_SHALLOW_A : COL_SHALLOW_B)
                  : ((nHash & 3) === 0 ? COL_DEEP_A : COL_DEEP_B);
              } else {
                const zStartBed = Math.max(Z_MIN, min8 - 2);
                const bedCol = (nHash & 1) ? COL_SHALLOW_BED_A : COL_SHALLOW_BED_B;
                for (let z = zStartBed; z <= h; z++) {
                  const si = z - Z_MIN;
                  terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = bedCol;
                }
                const siSurf = -1 - Z_MIN;
                const shimmer = (nHash % 17) === 0;
                terrainBufs[siSurf][(my - tMinY[siSurf]) * tW[siSurf] + (mx - tMinX[siSurf])] = shimmer
                  ? COL_SHALLOW_SHIMMER
                  : ((nHash & 1) ? COL_SHALLOW_SURF_A : COL_SHALLOW_SURF_B);
              }
            } else {
              const hL = mx > 0 ? hmap[idx - 1] : h;
              const hR = mx < mw - 1 ? hmap[idx + 1] : h;
              const hU = my > 0 ? hmap[idx - mw] : h;
              const hD = my < mh - 1 ? hmap[idx + mw] : h;
              const sunShade = Math.max(-22, Math.min(22, Math.round((-(hR - hL) - (hD - hU)) * 1.4)));
              const surfZ = h < 0 ? (mat === MAT_SHALLOW ? -1 : -2) : h;
              const effDepth = wd > 0 ? wd : (mat === MAT_SHALLOW ? 1 : 2);
              const bedZ = Math.max(Z_MIN, surfZ - effDepth);

              if (waterfallDropMask[idx] === 1) {
                const minWet = getMinWetDropNeighborZ(mx, my, surfZ);
                const zDropBot = Math.max(Z_MIN, minWet - 1);
                const zStart = Math.max(Z_MIN, Math.min(min8 - 2, zDropBot));
                const streakHash = ((mx * 17) ^ (my * 31)) & 7;
                for (let z = zStart; z <= surfZ; z++) {
                  const si = z - Z_MIN;
                  let col;
                  if (z < zDropBot) {
                    const strata = ((z >> 1) & 1) ? 9 : -8;
                    col = shadePack(PAL_ROCK[nHash & 1], sunShade + strata, sh * 0.3);
                  } else {
                    const isTop = (z === surfZ);
                    const isFoam = isTop
                      ? ((mx + my) % 3 === 0)
                      : ((streakHash < 3 && ((z + (mx & 1)) % 3 !== 0)) || (z <= zDropBot + 1));
                    col = isFoam ? COL_DROP_FOAM : (isTop ? COL_DROP_TOP : COL_DROP_BODY);
                  }
                  terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = col;
                }
              } else {
                const zStart = Math.max(Z_MIN, Math.min(min8 - 2, bedZ));
                const bedCol = mat === MAT_SHALLOW
                  ? ((nHash & 1) ? COL_SHALLOW_BED_A : COL_SHALLOW_BED_B)
                  : COL_BED;
                const shimmer = (nHash % (mat === MAT_SHALLOW ? 17 : 19)) === 0;
                const topCol = mat === MAT_SHALLOW
                  ? (shimmer ? COL_SHALLOW_SHIMMER : ((nHash & 1) ? COL_SHALLOW_SURF_A : COL_SHALLOW_SURF_B))
                  : (shimmer ? COL_CALM_SHIMMER : ((nHash & 1) ? COL_CALM_A : COL_CALM_B));
                const subCol = mat === MAT_SHALLOW ? COL_SHALLOW_SURF_B : COL_CALM_SUB;

                for (let z = zStart; z <= surfZ; z++) {
                  const si = z - Z_MIN;
                  let col;
                  if (z === surfZ) {
                    col = topCol;
                  } else if (z === bedZ) {
                    col = (min8 < z)
                      ? shadePack(PAL_ROCK[nHash & 1], sunShade + (((z >> 1) & 1) ? 9 : -8), sh * 0.3)
                      : bedCol;
                  } else if (z < bedZ || min8 < z) {
                    // Parede de contenção rochosa sólida (anti-aquário!)
                    const d = surfZ - z;
                    if (d <= 8 && z < bedZ && mat === MAT_SHALLOW) {
                      const strata = (z & 2) ? 6 : -5;
                      col = shadePack(PAL_EARTH[nHash & 1], sunShade + strata, sh * 0.4);
                    } else {
                      const strata = ((z >> 1) & 1) ? 9 : -8;
                      col = shadePack(PAL_ROCK[nHash & 1], sunShade + strata, sh * 0.3);
                    }
                  } else {
                    col = subCol;
                  }
                  terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = col;
                }
              }
            }
            continue;
          }

          const hL = mx > 0 ? hmap[idx - 1] : h;
          const hR = mx < mw - 1 ? hmap[idx + 1] : h;
          const hU = my > 0 ? hmap[idx - mw] : h;
          const hD = my < mh - 1 ? hmap[idx + mw] : h;
          const gx = hR - hL;
          const gy = hD - hU;
          const sunShade = Math.max(-22, Math.min(22, Math.round((-gx - gy) * 1.4)));
          const exposedEdge = (hL < h || hU < h) ? 10 : 0;
          const zStart = Math.max(Z_MIN, min8 - 2);

          for (let z = zStart; z <= h; z++) {
            const si = z - Z_MIN;
            let col;
            if (z === h) {
              let baseRGB;
              if (mat === MAT_PATH) baseRGB = PAL_PATH[nHash & 1];
              else if (mat === MAT_SAND) baseRGB = PAL_SAND[nHash & 1];
              else if (mat === MAT_STONE) baseRGB = PAL_STONE[nHash & 1];
              else if (mat === MAT_BRIDGE) {
                const plank = ((mx >> 1) + (my >> 2)) & 1;
                baseRGB = PAL_BRIDGE[plank];
              } else if (mat === MAT_PEAK) {
                baseRGB = (nHash % 5 === 0) ? PAL_PEAK[0] : PAL_PEAK[1];
              } else if (mat === MAT_LILYPAD) {
                baseRGB = PAL_LILYPAD[nHash & 1];
              } else {
                const tier = h >= 42 ? 3 : (h >= 24 ? 2 : (h >= 10 ? 1 : 0));
                baseRGB = PAL_GRASS_BASE[tier];
              }
              const altLift = Math.min(14, Math.max(-6, Math.round(h * 0.16)));
              col = shadePack(baseRGB, microTex + altLift + exposedEdge, sh);
            } else {
              const d = h - z;
              if (mat === MAT_BRIDGE) {
                col = shadePack(PAL_BRIDGE_SIDE, sunShade, sh * 0.5);
              } else if (mat === MAT_LILYPAD) {
                col = shadePack(PAL_LILYPAD_SIDE, sunShade, 0);
              } else if (mat === MAT_SAND && d <= 5) {
                col = shadePack(PAL_SAND_SIDE, sunShade, sh * 0.5);
              } else if (d <= 3 && mat !== MAT_STONE) {
                col = shadePack(PAL_MOSS[nHash & 1], sunShade, sh * 0.6);
              } else if (d <= 12 && mat !== MAT_STONE) {
                const strata = (z & 2) ? 6 : -5;
                col = shadePack(PAL_EARTH[nHash & 1], sunShade + strata, sh * 0.4);
              } else {
                const strata = ((z >> 1) & 1) ? 9 : -8;
                col = shadePack(PAL_ROCK[nHash & 1], sunShade + strata, sh * 0.3);
              }
            }
            terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = col;
          }

          const gt = grassType[idx];
          if (gt > 0) {
            if (h + 1 <= TERRAIN_Z_MAX) {
              const si1 = (h + 1) - Z_MIN;
              terrainBufs[si1][(my - tMinY[si1]) * tW[si1] + (mx - tMinX[si1])] = COL_GRASS_TIP_BASE;
            }
            if (h + 2 <= Z_GRASS_MAX) {
              const gi2 = (h + 2) - Z_MIN;
              grassBufs[gi2][(my - gMinY[gi2]) * gW[gi2] + (mx - gMinX[gi2])] = COL_GRASS_TIP_MID;
            }
            if (gt >= 2 && h + 3 <= Z_GRASS_MAX) {
              const gi3 = (h + 3) - Z_MIN;
              const tipCol = gt >= 3 ? COL_WILDFLOWERS[gt - 3] : COL_GRASS_TIP_HIGH;
              grassBufs[gi3][(my - gMinY[gi3]) * gW[gi3] + (mx - gMinX[gi3])] = tipCol;
            }
          }
        }
      }

      // Passo 2b: Rasteriza pontes parabólicas em arco & píer (rio visível embaixo)
      const COL_PLANK_A = packRGBA(185, 122, 74, 255);   // #B97A4A
      const COL_PLANK_B = packRGBA(166, 106, 62, 255);   // #A66A3E
      const COL_PLANK_SEAM = packRGBA(139, 83, 43, 255); // #8B532B
      const COL_DECK_UNDER = packRGBA(118, 72, 42, 255);
      const COL_RAIL_POST = packRGBA(124, 72, 37, 255);  // #7C4825
      const COL_RAIL_TOP = packRGBA(158, 98, 54, 255);   // #9E6236
      const COL_PIER_PILE_A = packRGBA(110, 68, 38, 255);
      const COL_PIER_PILE_B = packRGBA(92, 56, 30, 255);
      const COL_ABUT_A = packRGBA(126, 134, 146, 255);
      const COL_ABUT_B = packRGBA(104, 112, 124, 255);

      for (const br of bridges) {
        const gx0 = Math.max(0, Math.floor(br.xMin / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.floor(br.xMax / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(br.yMin / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.floor(br.yMax / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const u = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)))
              : Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)));
            const v = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)))
              : Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)));
            const zDeck = Math.min(TERRAIN_Z_MAX - 1, getBridgeDeckZ(br, wx, wy));
            const zDeckStart = Math.max(Z_MIN, zDeck - 2);
            const alongIdx = br.axis === 'x' ? (mx - gx0) : (my - gy0);
            const isSeam = (alongIdx % 3) === 0;
            const topPlankCol = isSeam ? COL_PLANK_SEAM : ((Math.floor(alongIdx / 3) & 1) ? COL_PLANK_B : COL_PLANK_A);

            for (let z = zDeckStart; z <= zDeck; z++) {
              const si = z - Z_MIN;
              terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = (z === zDeck) ? topPlankCol : COL_DECK_UNDER;
            }

            const isPiling = br.isPier && ((Math.floor(wy - br.yMin) % 24) < 6) && (v <= 0.14 || v >= 0.86);
            const isAbutment = !br.isPier && (u <= 0.09 || u >= 0.91);
            if (isPiling || isAbutment) {
              for (let z = Z_MIN; z < zDeckStart; z++) {
                const si = z - Z_MIN;
                const col = isPiling
                  ? (((mx + my + z) & 1) ? COL_PIER_PILE_A : COL_PIER_PILE_B)
                  : (((mx + my + z) & 1) ? COL_ABUT_A : COL_ABUT_B);
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = col;
              }
            }

            if (br.hasRailings && (v <= 0.08 || v >= 0.92)) {
              const isPost = (alongIdx % 7) === 0;
              const rStart = isPost ? zDeck + 1 : zDeck + 5;
              const rEnd = Math.min(TERRAIN_Z_MAX, zDeck + 6);
              for (let z = rStart; z <= rEnd; z++) {
                const si = z - Z_MIN;
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = (z === zDeck + 6) ? COL_RAIL_TOP : COL_RAIL_POST;
              }
            }
          }
        }
      }

      const uploadTightSlices = (bufs, minXArr, minYArr, wArr, hArr, targetMap, zMax) => {
        for (let z = Z_MIN; z <= zMax; z++) {
          const i = z - Z_MIN;
          const buf = bufs[i];
          if (!buf) {
            targetMap[z] = null;
            continue;
          }
          const bw = wArr[i];
          const bh = hArr[i];
          const cv = document.createElement('canvas');
          cv.width = bw;
          cv.height = bh;
          const cx = cv.getContext('2d');
          const img = cx.createImageData(bw, bh);
          new Uint32Array(img.data.buffer).set(buf);
          cx.putImageData(img, 0, 0);
          targetMap[z] = { canvas: cv, offX: minXArr[i], offY: minYArr[i], w: bw, h: bh };
        }
      };

      uploadTightSlices(terrainBufs, tMinX, tMinY, tW, tH, terrainSlices, TERRAIN_Z_MAX);
      uploadTightSlices(grassBufs, gMinX, gMinY, gW, gH, grassTipSlices, Z_GRASS_MAX);
    }

    // Re-bake incremental por Dirty Rect (para Matéria Granular & Pincéis ao vivo)
    function rebakeTerrainDirtyRect(mx0, my0, mx1, my1) {
      const x0 = Math.max(1, mx0);
      const y0 = Math.max(1, my0);
      const x1 = Math.min(mw - 2, mx1);
      const y1 = Math.min(mh - 2, my1);
      if (x1 < x0 || y1 < y0) return;

      const PAL_DIRTY_SOIL = [[138, 96, 62], [116, 79, 50]];
      const PAL_DIRTY_ROCK = [[104, 110, 122], [84, 90, 102]];

      let minZDirty = TERRAIN_Z_MAX;
      let maxZDirty = Z_MIN;
      const cellInfo = [];

      for (let my = y0; my <= y1; my++) {
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const idx = row + mx;
          const mat = matMap[idx];
          if (mat === MAT_BRIDGE) continue;
          const h = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX - 1, hmap[idx]));
          const hL = hmap[idx - 1], hR = hmap[idx + 1], hU = hmap[idx - mw], hD = hmap[idx + mw];
          const min8 = Math.min(
            hL, hR, hU, hD,
            hmap[idx - mw - 1], hmap[idx - mw + 1], hmap[idx + mw - 1], hmap[idx + mw + 1]
          );
          const wet = isWetMat(mat);
          const wd = waterDepth[idx];
          let surfZ = h;
          let bedZ = h;
          let isDrop = false;
          let zDropBot = Z_MIN;
          let zStart = Math.max(Z_MIN, min8 - 2);
          if (wet) {
            if (h < 0 && wd === 0) {
              surfZ = mat === MAT_SHALLOW ? -1 : -2;
              zStart = Z_MIN;
              bedZ = mat === MAT_SHALLOW ? h : Math.min(-4, h + 1);
            } else {
              surfZ = h < 0 ? (mat === MAT_SHALLOW ? -1 : -2) : h;
              const effD = wd > 0 ? wd : (mat === MAT_SHALLOW ? 1 : 2);
              bedZ = Math.max(Z_MIN, surfZ - effD);
              const minWet = surfZ >= 0 ? getMinWetDropNeighborZ(mx, my, surfZ) : surfZ;
              isDrop = surfZ >= 0 && (surfZ - minWet >= 3);
              zDropBot = Math.max(Z_MIN, minWet - 1);
              zStart = isDrop
                ? Math.max(Z_MIN, Math.min(min8 - 2, zDropBot))
                : Math.max(Z_MIN, Math.min(min8 - 2, bedZ));
            }
          }
          if (zStart < minZDirty) minZDirty = zStart;
          if (surfZ > maxZDirty) maxZDirty = surfZ;
          cellInfo.push({ mx, my, idx, h: surfZ, rawH: h, mat, wet, wd, bedZ, min8, isDrop, zDropBot, zStart, hL, hR, hU, hD });
        }
      }

      if (maxZDirty < minZDirty) return;
      const clearTopZ = TERRAIN_Z_MAX - 1;
      for (let z = minZDirty; z <= clearTopZ; z++) {
        let sl = terrainSlices[z];
        if (!sl && z <= maxZDirty) {
          const cv = document.createElement('canvas');
          cv.width = x1 - x0 + 1;
          cv.height = y1 - y0 + 1;
          sl = { canvas: cv, offX: x0, offY: y0, w: cv.width, h: cv.height };
          terrainSlices[z] = sl;
        }
        if (!sl) continue;
        const rx0 = Math.max(sl.offX, x0);
        const ry0 = Math.max(sl.offY, y0);
        const rx1 = Math.min(sl.offX + sl.w - 1, x1);
        const ry1 = Math.min(sl.offY + sl.h - 1, y1);
        if (rx1 < rx0 || ry1 < ry0) continue;

        const rw = rx1 - rx0 + 1;
        const rh = ry1 - ry0 + 1;
        const sctx = sl.canvas.getContext('2d');
        const img = sctx.getImageData(rx0 - sl.offX, ry0 - sl.offY, rw, rh);
        const buf = new Uint32Array(img.data.buffer);

        for (let i = 0; i < cellInfo.length; i++) {
          const ci = cellInfo[i];
          if (ci.mx < rx0 || ci.mx > rx1 || ci.my < ry0 || ci.my > ry1) continue;
          const outIdx = (ci.my - ry0) * rw + (ci.mx - rx0);
          if (z < ci.zStart || z > ci.h) {
            buf[outIdx] = 0;
            continue;
          }
          const nHash = ((Math.imul(ci.mx, 73856093)) ^ (Math.imul(ci.my, 19349663))) >>> 0;
          const microTex = ((nHash & 7) - 3) * 2;
          const sunShade = Math.max(-22, Math.min(22, Math.round((-(ci.hR - ci.hL) - (ci.hD - ci.hU)) * 1.4)));

          if (ci.wet) {
            if (ci.rawH < 0 && ci.wd === 0) {
              if (ci.mat === MAT_WATER) {
                if (z === -2) {
                  buf[outIdx] = ci.rawH > -6 ? ((nHash & 1) ? COL_SHALLOW_A : COL_SHALLOW_B) : ((nHash & 3) === 0 ? COL_DEEP_A : COL_DEEP_B);
                } else if (z <= ci.bedZ) {
                  buf[outIdx] = COL_BED;
                } else {
                  buf[outIdx] = 0;
                }
              } else {
                buf[outIdx] = z === -1
                  ? ((nHash % 17) === 0 ? COL_SHALLOW_SHIMMER : ((nHash & 1) ? COL_SHALLOW_SURF_A : COL_SHALLOW_SURF_B))
                  : ((nHash & 1) ? COL_SHALLOW_BED_A : COL_SHALLOW_BED_B);
              }
            } else if (ci.isDrop) {
              if (z < ci.zDropBot) {
                buf[outIdx] = shadePack(PAL_DIRTY_ROCK[(nHash + z) & 1], sunShade + microTex, shadowMask[ci.idx]);
              } else {
                const isTop = (z === ci.h);
                const streakHash = ((ci.mx * 17) ^ (ci.my * 31)) & 7;
                const isFoam = isTop ? ((ci.mx + ci.my) % 3 === 0) : ((streakHash < 3 && ((z + (ci.mx & 1)) % 3 !== 0)) || (z <= ci.zDropBot + 1));
                buf[outIdx] = isFoam ? COL_DROP_FOAM : (isTop ? COL_DROP_TOP : COL_DROP_BODY);
              }
            } else {
              if (z === ci.h) {
                const shM = (nHash % (ci.mat === MAT_SHALLOW ? 17 : 19)) === 0;
                buf[outIdx] = ci.mat === MAT_SHALLOW
                  ? (shM ? COL_SHALLOW_SHIMMER : ((nHash & 1) ? COL_SHALLOW_SURF_A : COL_SHALLOW_SURF_B))
                  : (shM ? COL_CALM_SHIMMER : ((nHash & 1) ? COL_CALM_A : COL_CALM_B));
              } else if (z === ci.bedZ && ci.min8 >= z) {
                buf[outIdx] = ci.mat === MAT_SHALLOW ? ((nHash & 1) ? COL_SHALLOW_BED_A : COL_SHALLOW_BED_B) : COL_BED;
              } else if (z < ci.bedZ || ci.min8 < z) {
                buf[outIdx] = shadePack(PAL_DIRTY_ROCK[(nHash + z) & 1], sunShade + microTex, shadowMask[ci.idx]);
              } else {
                buf[outIdx] = ci.mat === MAT_SHALLOW ? COL_SHALLOW_SURF_B : COL_CALM_SUB;
              }
            }
            continue;
          }

          const exposedEdge = (ci.hL < ci.h || ci.hU < ci.h) ? 10 : 0;
          if (z === ci.h) {
            let baseRGB;
            if (ci.mat === MAT_SAND) baseRGB = PAL_SAND[nHash & 1];
            else if (ci.mat === MAT_PEAK) baseRGB = PAL_PEAK[nHash & 1];
            else if (ci.mat === MAT_PATH) baseRGB = PAL_PATH[nHash & 1];
            else {
              const tier = ci.h >= 42 ? 3 : (ci.h >= 24 ? 2 : (ci.h >= 10 ? 1 : 0));
              baseRGB = PAL_GRASS_BASE[tier];
            }
            buf[outIdx] = shadePack(baseRGB, sunShade + exposedEdge + microTex, shadowMask[ci.idx]);
          } else {
            const depth = ci.h - z;
            const cliffRGB = depth <= 4 ? PAL_DIRTY_SOIL[(nHash + z) & 1] : PAL_DIRTY_ROCK[(nHash + z) & 1];
            buf[outIdx] = shadePack(cliffRGB, sunShade - depth * 2 + microTex, shadowMask[ci.idx]);
          }
        }
        sctx.putImageData(img, rx0 - sl.offX, ry0 - sl.offY);
      }
    }

