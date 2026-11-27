    // =========================================================================
    // 10. RENDERIZAÇÃO UNIFICADA SLICE-BY-SLICE + entityLayer + HI-RES OVERLAYS
    // =========================================================================
    function project(wx, wy, wz) {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const dx = wx - camX;
      const dy = wy - camY;
      const dz = wz - camZ;
      const rx = dx * cosA - dy * sinA;
      const ry = dx * sinA + dy * cosA;
      return {
        x: LOW_W / 2 + rx,
        y: LOW_H / 2 + 16 + ry * squash - dz,
        depth: ry
      };
    }

    function unprojectToGrid(px, py, z, cosA, sinA) {
      const rx = px - LOW_W / 2;
      const ry = (py - (LOW_H / 2 + 16 - (z - camZ))) / squash;
      const dx = rx * cosA + ry * sinA;
      const dy = -rx * sinA + ry * cosA;
      return {
        gx: (camX + dx) / VOX + HALF_GRID,
        gy: (camY + dy) / VOX + HALF_GRID
      };
    }

    function drawBoundedSliceTo(targetCtx, sl, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy, windOffX = 0) {
      if (!sl) return;
      const ix0 = Math.max(viewMinMx, sl.offX);
      const ix1 = Math.min(viewMaxMx, sl.offX + sl.w);
      if (ix1 <= ix0) return;
      const iy0 = Math.max(viewMinMy, sl.offY);
      const iy1 = Math.min(viewMaxMy, sl.offY + sl.h);
      if (iy1 <= iy0) return;

      const sx = ix0 - sl.offX;
      const sy = iy0 - sl.offY;
      const dw = ix1 - ix0;
      const dh = iy1 - iy0;

      targetCtx.save();
      targetCtx.translate(LOW_W / 2 + windOffX, LOW_H / 2 + 16 - (z - camZ));
      targetCtx.scale(1, squash);
      targetCtx.rotate(turn);
      targetCtx.scale(VOX, VOX);
      targetCtx.translate(-camX / VOX, -camY / VOX);
      targetCtx.drawImage(sl.canvas, sx, sy, dw, dh, ix0 - HALF_GRID, iy0 - HALF_GRID, dw, dh);
      targetCtx.restore();
    }

    function stampModelSlice(targetCtx, model, sz, wx, wy, wz, selfAngle, scale, cosA, sinA, bendX = 0, bendY = 0) {
      if (bendX !== 0 || bendY !== 0) {
        const bf = model.count > 1 ? Math.pow(sz / (model.count - 1), 2) : 0;
        wx += bendX * bf;
        wy += bendY * bf;
      }
      const dx = wx - camX;
      const dy = wy - camY;
      const rx = dx * cosA - dy * sinA;
      const ry = dx * sinA + dy * cosA;
      const sx = Math.round(LOW_W / 2 + rx);
      const sy = Math.round(LOW_H / 2 + 16 + ry * squash - (wz - camZ));
      const ox = Math.floor(model.w / 2);
      const oy = Math.floor(model.h / 2);

      targetCtx.save();
      targetCtx.translate(sx, sy);
      targetCtx.scale(scale, squash * scale);
      targetCtx.rotate(turn + selfAngle);
      targetCtx.drawImage(model.sheet, sz * model.w, 0, model.w, model.h, -ox, -oy, model.w, model.h);
      targetCtx.restore();
    }

    function drawSpeechOverlaysHiRes(speechQueue) {
      if (speechQueue.length === 0) return;
      ctx.save();
      ctx.font = 'bold 13px "Segoe UI", system-ui, -apple-system, sans-serif';
      ctx.textBaseline = 'middle';

      for (const item of speechQueue) {
        const sx = Math.round(item.lowX * pixelScale);
        const sy = Math.round(item.lowY * pixelScale) - 10;
        const tw = ctx.measureText(item.text).width;
        const padX = 11;
        const bw = Math.round(tw + padX * 2);
        const bh = 28;
        const bx = Math.max(8, Math.min(viewW - bw - 8, Math.round(sx - bw / 2)));
        const by = Math.max(8, sy - bh);

        ctx.fillStyle = 'rgba(59, 34, 25, 0.16)';
        ctx.beginPath();
        ctx.roundRect(bx + 2, by + 3, bw, bh, 10);
        ctx.fill();

        ctx.fillStyle = '#FFFDF8';
        ctx.strokeStyle = '#3B2219';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, bw, bh, 10);
        ctx.fill();
        ctx.stroke();

        const tailX = Math.max(bx + 12, Math.min(bx + bw - 12, sx));
        ctx.fillStyle = '#FFFDF8';
        ctx.beginPath();
        ctx.moveTo(tailX - 5, by + bh - 1);
        ctx.lineTo(tailX, by + bh + 6);
        ctx.lineTo(tailX + 5, by + bh - 1);
        ctx.closePath();
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(tailX - 5, by + bh);
        ctx.lineTo(tailX, by + bh + 6);
        ctx.lineTo(tailX + 5, by + bh);
        ctx.stroke();

        ctx.fillStyle = '#3B2219';
        ctx.fillText(item.text, bx + padX, by + bh / 2 + 0.5);
      }
      ctx.restore();
    }

    function renderScene() {
      const prevCamX = camX;
      const prevCamY = camY;
      if (shakeTimer > 0) {
        const sAmp = shakeMag * Math.min(1, shakeTimer / 0.16);
        camX += (Math.random() - 0.5) * 2 * sAmp;
        camY += (Math.random() - 0.5) * 2 * sAmp;
      }
      try {
      // 1. Céu + Nuvens
      const skyGrad = lowCtx.createLinearGradient(0, 0, 0, LOW_H);
      skyGrad.addColorStop(0, '#78C8F2');
      skyGrad.addColorStop(0.6, '#BEE8FB');
      skyGrad.addColorStop(1, '#F3E7D3');
      lowCtx.fillStyle = skyGrad;
      lowCtx.fillRect(0, 0, LOW_W, LOW_H);

      const cloudShift = (cat.idleTimer * 6) % (LOW_W + 140);
      lowCtx.fillStyle = 'rgba(255, 255, 255, 0.72)';
      for (const [cx0, cy0, w0] of [[40, 26, 48], [190, 18, 62], [360, 36, 44], [520, 22, 54]]) {
        const xPos = ((cx0 + cloudShift) % (LOW_W + 100)) - 50;
        lowCtx.fillRect(Math.round(xPos), cy0, w0, 10);
        lowCtx.fillRect(Math.round(xPos + 8), cy0 - 5, w0 - 16, 6);
      }

      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const animTick = Math.floor(cat.idleTimer * 8); // 8 FPS stepped animation
      const animTime = animTick / 8;
      const camWind = sampleWind(camX, camY, fluidTime);
      const grassAmp = Math.min(1.6, 0.5 + camWind.mag * 0.55);
      const grassLean = camWind.wx * 0.35;
      const speechQueue = [];

      // 2. Bounding box visível no grid 1080×1080 (culling exato por viewport!)
      let minGx = 9999, maxGx = -9999, minGy = 9999, maxGy = -9999;
      for (const zTest of [Z_MIN, TERRAIN_Z_MAX]) {
        for (const [cx, cy] of [[0, 0], [LOW_W, 0], [0, LOW_H], [LOW_W, LOW_H]]) {
          const g = unprojectToGrid(cx, cy, zTest, cosA, sinA);
          if (g.gx < minGx) minGx = g.gx;
          if (g.gx > maxGx) maxGx = g.gx;
          if (g.gy < minGy) minGy = g.gy;
          if (g.gy > maxGy) maxGy = g.gy;
        }
      }
      const viewMinMx = Math.max(0, Math.floor(minGx) - 4);
      const viewMinMy = Math.max(0, Math.floor(minGy) - 4);
      const viewMaxMx = Math.min(mw, Math.ceil(maxGx) + 4);
      const viewMaxMy = Math.min(mh, Math.ceil(maxGy) + 4);

      const minVisWx = (viewMinMx - HALF_GRID) * VOX - 72;
      const maxVisWx = (viewMaxMx - HALF_GRID) * VOX + 72;
      const minVisWy = (viewMinMy - HALF_GRID) * VOX - 72;
      const maxVisWy = (viewMaxMy - HALF_GRID) * VOX + 72;

      // 3. Coleta de todas as entidades visíveis [baseZ, topZ) para o loop unificado
      const activeDrawables = [];
      const shadowsByZ = new Map();
      const firesByZ = new Map();
      let maxEntityTopZ = TERRAIN_Z_MAX;

      const registerShadow = (x, y, groundZ, z, radiusX, radiusY, alpha) => {
        const gz = Math.max(Z_MIN, Math.round(groundZ));
        if (!shadowsByZ.has(gz)) shadowsByZ.set(gz, []);
        shadowsByZ.get(gz).push({ x, y, groundZ, z, radiusX, radiusY, alpha });
      };

      // Props estáticos visíveis
      for (const p of props) {
        if (p.destroyed) continue;
        if (p.wx < minVisWx || p.wx > maxVisWx || p.wy < minVisWy || p.wy > maxVisWy) continue;
        const maxDrawZ = p.renderMaxSlice !== undefined
          ? Math.min(p.topZ, p.baseZ + Math.ceil(p.renderMaxSlice * p.scale))
          : p.topZ;
        const maxSliceIdx = p.renderMaxSlice !== undefined
          ? Math.min(p.model.count - 1, p.renderMaxSlice - 1)
          : (p.model.count - 1);
        const dp = (p.wx - camX) * sinA + (p.wy - camY) * cosA;
        activeDrawables.push({
          baseZ: p.baseZ,
          topZ: maxDrawZ,
          depth: dp,
          drawSlice: (z) => {
            const sz = Math.min(maxSliceIdx, Math.floor((z - p.baseZ) / p.scale));
            const flashOff = (p.destr && p.destr.hitFlash > 0) ? Math.sin(fluidTime * 75) * 1.4 : 0;
            stampModelSlice(entityCtx, p.model, sz, p.wx, p.wy, z, p.selfAngle, p.scale, cosA, sinA, (p.bx || 0) + flashOff, p.by || 0);
          }
        });
        if (maxDrawZ > maxEntityTopZ) maxEntityTopZ = maxDrawZ;
        if (p.isFire) {
          const fz = p.baseZ + (p.modelKey === 'stone_lantern' ? 20 : (p.modelKey === 'campfire' ? 8 : Math.max(4, Math.round((p.topZ - p.baseZ) * 0.65))));
          if (fz > maxEntityTopZ) maxEntityTopZ = fz;
          if (!firesByZ.has(fz)) firesByZ.set(fz, []);
          firesByZ.get(fz).push(p);
        }
      }

      // Pickups das Ferramentas visíveis
      for (const pk of toolPickups) {
        if (pk.wx < minVisWx || pk.wx > maxVisWx || pk.wy < minVisWy || pk.wy > maxVisWy) continue;
        const tKey = TOOLS_META[pk.toolId].modelKey;
        const tModel = tKey ? propModels[tKey] : null;
        if (!tModel) continue;
        const tScale = 1.0;
        const bob = Math.sin(cat.idleTimer * 3.2 + pk.wx * 0.05) * 2.0;
        const pBaseZ = Math.round(pk.baseZ + 4 + bob);
        const pTopZ = pBaseZ + Math.ceil(tModel.count * tScale);
        const spinAngle = cat.idleTimer * 1.8 + pk.wx * 0.04;
        const dp = (pk.wx - camX) * sinA + (pk.wy - camY) * cosA;
        registerShadow(pk.wx, pk.wy, pk.baseZ, pBaseZ, 4.5, 2.8, 0.24);
        activeDrawables.push({
          baseZ: pBaseZ,
          topZ: pTopZ,
          depth: dp,
          drawSlice: (z) => {
            const sz = Math.min(tModel.count - 1, Math.floor((z - pBaseZ) / tScale));
            stampModelSlice(entityCtx, tModel, sz, pk.wx, pk.wy, z, spinAngle, tScale, cosA, sinA);
          }
        });
        if (pTopZ > maxEntityTopZ) maxEntityTopZ = pTopZ;
      }

      // Corpos em queda (Pêndulo Invertido 3D)
      for (const fb of fallingBodies) {
        const sinP = Math.sin(fb.phi);
        const cosP = Math.cos(fb.phi);
        for (let sz = fb.zCut; sz < fb.model.count; sz++) {
          const dz = (sz - fb.zCut) * fb.scale;
          const sx = fb.wx + dz * sinP * fb.dx;
          const sy = fb.wy + dz * sinP * fb.dy;
          const szWorld = Math.round(fb.baseZ + fb.zCut * fb.scale + dz * cosP);
          const dp = (sx - camX) * sinA + (sy - camY) * cosA;
          activeDrawables.push({
            baseZ: szWorld,
            topZ: szWorld + 1,
            depth: dp + 0.15,
            drawSlice: (z) => {
              stampModelSlice(entityCtx, fb.model, sz, sx, sy, z, fb.selfAngle, fb.scale, cosA, sinA);
            }
          });
          if (szWorld + 1 > maxEntityTopZ) maxEntityTopZ = szWorld + 1;
        }
      }

      // Drops balísticos (wood_log / stone_chunk)
      for (const dr of debrisDrops) {
        if (!dr.model) continue;
        if (dr.x < minVisWx || dr.x > maxVisWx || dr.y < minVisWy || dr.y > maxVisWy) continue;
        const dBaseZ = Math.round(dr.z);
        const dTopZ = dBaseZ + Math.ceil(dr.model.count * dr.scale);
        const dp = (dr.x - camX) * sinA + (dr.y - camY) * cosA;
        const gH = getHeightAt(dr.x, dr.y);
        if (gH !== null && !dr.inWater) {
          registerShadow(dr.x, dr.y, gH, dr.z, 3.8, 2.4, 0.22);
        }
        activeDrawables.push({
          baseZ: dBaseZ,
          topZ: dTopZ,
          depth: dp + 0.1,
          drawSlice: (z) => {
            const sz = Math.min(dr.model.count - 1, Math.floor((z - dBaseZ) / dr.scale));
            stampModelSlice(entityCtx, dr.model, sz, dr.x, dr.y, z, dr.selfAngle, dr.scale, cosA, sinA);
          }
        });
        if (dTopZ > maxEntityTopZ) maxEntityTopZ = dTopZ;
      }

      // Peixes dourados visíveis
      for (const f of fishes) {
        if (f.collected) continue;
        if (f.wx < minVisWx || f.wx > maxVisWx || f.wy < minVisWy || f.wy > maxVisWy) continue;
        const bob = Math.sin(cat.idleTimer * 3.5 + f.wx * 0.05) * 2.2;
        const fBaseZ = Math.round(f.baseZ + 4 + bob);
        const fModel = propModels.golden_fish;
        const fTopZ = fBaseZ + fModel.count;
        const spinAngle = cat.idleTimer * 2.5 + f.wx * 0.03;
        const dp = (f.wx - camX) * sinA + (f.wy - camY) * cosA;
        registerShadow(f.wx, f.wy, f.baseZ, fBaseZ, 5, 3, 0.25);
        activeDrawables.push({
          baseZ: fBaseZ,
          topZ: fTopZ,
          depth: dp,
          drawSlice: (z) => {
            stampModelSlice(entityCtx, fModel, z - fBaseZ, f.wx, f.wy, z, spinAngle, 1.0, cosA, sinA);
          }
        });
        if (fTopZ > maxEntityTopZ) maxEntityTopZ = fTopZ;
      }

      // NPCs visíveis
      for (const npc of npcs) {
        if (npc.x < minVisWx || npc.x > maxVisWx || npc.y < minVisWy || npc.y > maxVisWy) continue;
        const bob = npc.moving ? Math.abs(Math.sin(npc.walkPhase * 2)) * 0.8 : Math.sin(cat.idleTimer * 2.5) * 0.3;
        const nBaseZ = Math.round(npc.z + bob);
        const nTopZ = nBaseZ + Math.ceil(npc.model.count * npc.scale);
        const dp = (npc.x - camX) * sinA + (npc.y - camY) * cosA;
        registerShadow(npc.x, npc.y, npc.z, npc.z, 5.2, 3.4, 0.28);
        activeDrawables.push({
          baseZ: nBaseZ,
          topZ: nTopZ,
          depth: dp + 0.2,
          drawSlice: (z) => {
            const sz = Math.min(npc.model.count - 1, Math.floor((z - nBaseZ) / npc.scale));
            stampModelSlice(entityCtx, npc.model, sz, npc.x, npc.y, z, npc.selfAngle, npc.scale, cosA, sinA);
          }
        });
        if (nTopZ > maxEntityTopZ) maxEntityTopZ = nTopZ;
        if (npc.speech && npc.speech.timer > 0) {
          const sp = project(npc.x, npc.y, npc.z + 18);
          speechQueue.push({ lowX: sp.x, lowY: sp.y, text: npc.speech.text });
        }
      }

      // Gato Jogável (Patas + Corpo + Chapéu em suas respectivas alturas Z)
      {
        const sk = catSkinModels[cat.skinIdx];
        const hatPreset = HAT_PRESETS[cat.hatIdx];
        const hatModel = hatPreset.id !== 'none' ? hatModels[hatPreset.id] : null;
        const cosC = Math.cos(cat.selfAngle);
        const sinC = Math.sin(cat.selfAngle);
        const t = cat.walkPhase;
        const inAir = !cat.onGround;
        const dpCat = (cat.x - camX) * sinA + (cat.y - camY) * cosA;

        const hAbove = Math.max(0, cat.z - cat.groundZ);
        const shrink = Math.max(0.45, 1.0 - hAbove / 55);
        registerShadow(cat.x, cat.y, cat.groundZ, cat.z, 6.2 * shrink * (cat.scale || 1), 4.0 * shrink * (cat.scale || 1), 0.32 * shrink);

        const catBlinkHidden = cat.hurtTimer > 0 && (Math.floor((1.0 - cat.hurtTimer) * 6) % 2 === 0);
        const bob = inAir ? 0 : (cat.isWalking ? Math.abs(Math.sin(t * 2)) * 0.7 : Math.sin(cat.idleTimer * 2.4) * 0.35);
        if (!catBlinkHidden && cat.avatar === 'human' && typeof pushHumanoidDrawables === 'function') {
          const humanTop = pushHumanoidDrawables(activeDrawables, cat, cosA, sinA, bob);
          if (humanTop > maxEntityTopZ) maxEntityTopZ = humanTop;
        } else if (!catBlinkHidden) {
          const pawSpecs = [
            [-4.5, -7.5, inAir ? 0.0 : (cat.isWalking ? Math.max(0, Math.sin(t + Math.PI + 0.3) * 3.0) : 0), inAir ? -2.2 : (cat.isWalking ? -Math.cos(t + Math.PI + 0.3) * 2.3 : 0)],
            [ 3.5, -7.5, inAir ? 0.0 : (cat.isWalking ? Math.max(0, Math.sin(t + 0.3) * 3.0) : 0), inAir ? -2.2 : (cat.isWalking ? -Math.cos(t + 0.3) * 2.3 : 0)],
            [-4.5,  3.5, inAir ? 0.5 : (cat.isWalking ? Math.max(0, Math.sin(t) * 3.0) : 0), inAir ? 2.2 : (cat.isWalking ? -Math.cos(t) * 2.3 : 0)],
            [ 3.5,  3.5, inAir ? 0.5 : (cat.isWalking ? Math.max(0, Math.sin(t + Math.PI) * 3.0) : 0), inAir ? 2.2 : (cat.isWalking ? -Math.cos(t + Math.PI) * 2.3 : 0)]
          ];
          const S = cat.scale || 1;
          for (const [lx, ly, lift, stride] of pawSpecs) {
            const px = cat.x + (lx * S) * cosC - ((ly + stride) * S) * sinC;
            const py = cat.y + (lx * S) * sinC + ((ly + stride) * S) * cosC;
            const pBaseZ = Math.round(cat.z + lift * S);
            const pTopZ = pBaseZ + Math.ceil(sk.paw.count * S);
            const pDp = (px - camX) * sinA + (py - camY) * cosA;
            activeDrawables.push({
              baseZ: pBaseZ,
              topZ: pTopZ,
              depth: pDp + 0.4,
              drawSlice: (z) => {
                const psz = Math.min(sk.paw.count - 1, Math.floor((z - pBaseZ) / S));
                stampModelSlice(entityCtx, sk.paw, psz, px, py, z, cat.selfAngle, S, cosA, sinA);
              }
            });
            if (pTopZ > maxEntityTopZ) maxEntityTopZ = pTopZ;
          }

          const bodyBaseZ = Math.round(cat.z + (1.5 + bob) * S);
          const bodyTopZ = bodyBaseZ + Math.ceil(sk.body.count * S);
          activeDrawables.push({
            baseZ: bodyBaseZ,
            topZ: bodyTopZ,
            depth: dpCat + 0.5,
            drawSlice: (z) => {
              const bsz = Math.min(sk.body.count - 1, Math.floor((z - bodyBaseZ) / S));
              stampModelSlice(entityCtx, sk.body, bsz, cat.x, cat.y, z, cat.selfAngle, S, cosA, sinA);
            }
          });
          if (bodyTopZ > maxEntityTopZ) maxEntityTopZ = bodyTopZ;

          if (hatModel) {
            const hx = cat.x - 4.5 * S * sinC;
            const hy = cat.y + 4.5 * S * cosC;
            const hatBaseZ = Math.round(cat.z + (15.0 + bob - 2.8) * S);
            const hatTopZ = hatBaseZ + Math.ceil(hatModel.count * S);
            activeDrawables.push({
              baseZ: hatBaseZ,
              topZ: hatTopZ,
              depth: dpCat + 0.6,
              drawSlice: (z) => {
                const hsz = Math.min(hatModel.count - 1, Math.floor((z - hatBaseZ) / S));
                stampModelSlice(entityCtx, hatModel, hsz, hx, hy, z, cat.selfAngle, S, cosA, sinA);
              }
            });
            if (hatTopZ > maxEntityTopZ) maxEntityTopZ = hatTopZ;
          }

          if (swingTimer > 0 && equippedTool !== 'none') {
            const tKey = TOOLS_META[equippedTool].modelKey;
            const tModel = tKey ? propModels[tKey] : null;
            if (tModel) {
              const prog = 1 - Math.max(0, Math.min(1, swingTimer / 0.22));
              const arcAngle = (prog - 0.5) * 2.1;
              const swAngle = cat.selfAngle + arcAngle;
              const fxC = -Math.sin(swAngle);
              const fyC = Math.cos(swAngle);
              const tx = cat.x + fxC * 10;
              const ty = cat.y + fyC * 10;
              const tScale = 0.68;
              const tBaseZ = Math.round(cat.z + 3 + Math.sin(prog * Math.PI) * 3);
              const tTopZ = tBaseZ + Math.ceil(tModel.count * tScale);
              const tDp = (tx - camX) * sinA + (ty - camY) * cosA;
              activeDrawables.push({
                baseZ: tBaseZ,
                topZ: tTopZ,
                depth: tDp + 0.65,
                drawSlice: (z) => {
                  const sz = Math.min(tModel.count - 1, Math.floor((z - tBaseZ) / tScale));
                  stampModelSlice(entityCtx, tModel, sz, tx, ty, z, swAngle, tScale, cosA, sinA);
                }
              });
              if (tTopZ > maxEntityTopZ) maxEntityTopZ = tTopZ;
            }
          }
        }

        if (cat.speech && cat.speech.timer > 0) {
          cat.speech.timer--;
          const sp = project(cat.x, cat.y, cat.z + 24 * (cat.scale || 1));
          speechQueue.push({ lowX: sp.x, lowY: sp.y, text: cat.speech.text });
        }
      }

      // Ordenar uma única vez por profundidade para desenhar back-to-front em cada fatia z
      activeDrawables.sort((a, b) => a.depth - b.depth);

      // Bucket das partículas 3D por fatia Z para oclusão correta atrás de falésias
      const particlesByZ = new Map();
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        const pz = Math.max(Z_MIN, Math.min(maxEntityTopZ, Math.round(p.z)));
        if (!particlesByZ.has(pz)) particlesByZ.set(pz, []);
        particlesByZ.get(pz).push(p);
      }

      // Buckets dinâmicos por fatia Z para WaveBuffer, FlowStreaks, FloatingItems e Cachoeiras de Montanha
      const wavesByZ = new Map();
      for (let dy = 1; dy < WAVE_H - 1; dy++) {
        const cwy = waveOriginY + (dy + 0.5) * WAVE_CELL;
        if (cwy < minVisWy || cwy > maxVisWy) continue;
        const row = dy * WAVE_W;
        for (let dx = 1; dx < WAVE_W - 1; dx++) {
          const val = waveCurr[row + dx];
          if (Math.abs(val) < 0.14) continue;
          const cwx = waveOriginX + (dx + 0.5) * WAVE_CELL;
          if (cwx < minVisWx || cwx > maxVisWx) continue;
          const mx = Math.floor(cwx / VOX + HALF_GRID);
          const my = Math.floor(cwy / VOX + HALF_GRID);
          if (mx < 0 || mx >= mw || my < 0 || my >= mh) continue;
          const wIdx = my * mw + mx;
          const wMat = matMap[wIdx];
          if (!isWetMat(wMat)) continue;
          const surfZ = wMat === MAT_SHALLOW ? (hmap[wIdx] < 0 ? -1 : hmap[wIdx]) : (hmap[wIdx] < 0 ? -2 : hmap[wIdx]);
          if (!wavesByZ.has(surfZ)) wavesByZ.set(surfZ, []);
          wavesByZ.get(surfZ).push({ wx: cwx, wy: cwy, val });
        }
      }

      const streaksByZ = new Map();
      for (let i = 0; i < flowStreaks.length; i++) {
        const s = flowStreaks[i];
        if (s.hLen < 2) continue;
        if (s.x < minVisWx - 24 || s.x > maxVisWx + 24 || s.y < minVisWy - 24 || s.y > maxVisWy + 24) continue;
        const sz = Math.round(s.z);
        if (!streaksByZ.has(sz)) streaksByZ.set(sz, []);
        streaksByZ.get(sz).push(s);
      }

      const floatingByZ = new Map();
      for (let i = 0; i < floatingItems.length; i++) {
        const f = floatingItems[i];
        if (f.x < minVisWx || f.x > maxVisWx || f.y < minVisWy || f.y > maxVisWy) continue;
        const fz = Math.round(f.z);
        if (!floatingByZ.has(fz)) floatingByZ.set(fz, []);
        floatingByZ.get(fz).push(f);
      }

      const visWaterfalls = [];
      for (let i = 0; i < waterfallDrops.length; i++) {
        const wd = waterfallDrops[i];
        if (wd.wx >= minVisWx && wd.wx <= maxVisWx && wd.wy >= minVisWy && wd.wy <= maxVisWy) {
          visWaterfalls.push(wd);
        }
      }

      // 4. Loop Unificado Slice-by-Slice (Terreno + Destination-Out + Grama + Partículas + Entidades)
      entityCtx.globalCompositeOperation = 'source-over';
      entityCtx.clearRect(0, 0, LOW_W, LOW_H);
      let entityStarted = false;
      const wfVisible = maxVisWx >= WF_X0 && minVisWx <= WF_X0 + WF_W * WF_CELL && maxVisWy >= WF_Y0 && minVisWy <= WF_Y0 + WF_H * WF_CELL;
      const dropStreakTick = Math.floor(fluidTime * 10);

      for (let z = Z_MIN; z <= maxEntityTopZ; z++) {
        // 4a. Fatia do terreno (Tight-Crop Bounded Slice + skip O(1))
        const tSlice = z <= TERRAIN_Z_MAX ? terrainSlices[z] : null;
        if (tSlice && viewMaxMx > viewMinMx && viewMaxMy > viewMinMy) {
          drawBoundedSliceTo(lowCtx, tSlice, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy);

          // Brilho animado na superfície da água (z = -2 profunda, z = -1 rasa)
          if (z === -2 || z === -1) {
            lowCtx.fillStyle = z === -1 ? 'rgba(236, 254, 255, 0.62)' : 'rgba(224, 242, 254, 0.55)';
            const step = 12;
            const startX = Math.floor(minVisWx / step) * step;
            const startY = Math.floor(minVisWy / step) * step;
            const targetMat = z === -1 ? MAT_SHALLOW : MAT_WATER;
            for (let wy = startY; wy <= maxVisWy; wy += step) {
              for (let wx = startX; wx <= maxVisWx; wx += step) {
                const c = getCellAt(wx, wy);
                if (!c || c.mat !== targetMat || c.h >= 0) continue;
                if (((c.mx + c.my + animTick) % 9) === 0) {
                  const wp = project(wx, wy, z + 0.2);
                  lowCtx.fillRect(Math.round(wp.x), Math.round(wp.y), 3, 1);
                }
              }
            }
          }

          // WaveBuffer (cristas/cavas), FlowStreaks & FloatingItems em qualquer cota Z com oclusão 3D
          const wList = wavesByZ.get(z);
          if (wList) {
            for (let i = 0; i < wList.length; i++) {
              const wv = wList[i];
              const wp = project(wv.wx, wv.wy, z + 0.2);
              const px = Math.round(wp.x);
              const py = Math.round(wp.y);
              if (px < -4 || px >= LOW_W + 4 || py < -4 || py >= LOW_H + 4) continue;
              if (wv.val > 0) {
                lowCtx.fillStyle = wv.val > 0.7 ? 'rgba(240, 249, 255, 0.72)' : 'rgba(224, 242, 254, 0.45)';
              } else {
                lowCtx.fillStyle = wv.val < -0.7 ? 'rgba(24, 118, 186, 0.52)' : 'rgba(36, 148, 214, 0.34)';
              }
              lowCtx.fillRect(px - 1, py, 3, 1);
            }
          }

          const sList = streaksByZ.get(z);
          if (sList) {
            for (let i = 0; i < sList.length; i++) {
              const s = sList[i];
              const isDefl = s.deflect >= 0.16;
              lowCtx.strokeStyle = isDefl ? 'rgba(248, 253, 255, 0.88)' : 'rgba(224, 242, 254, 0.48)';
              lowCtx.lineWidth = s.deflect > 0.35 ? 1.5 : 1;
              lowCtx.beginPath();
              const p0 = project(s.hist[0], s.hist[1], z + 0.25);
              lowCtx.moveTo(p0.x, p0.y);
              for (let k = 1; k < s.hLen; k++) {
                const pk = project(s.hist[k * 2], s.hist[k * 2 + 1], z + 0.25);
                lowCtx.lineTo(pk.x, pk.y);
              }
              lowCtx.stroke();
            }
          }

          const flList = floatingByZ.get(z);
          if (flList) {
            for (let i = 0; i < flList.length; i++) {
              const f = flList[i];
              const bob = Math.sin(fluidTime * 3.2 + f.phase) * 0.25;
              const fp = project(f.x, f.y, z + 0.3 + bob);
              const px = Math.round(fp.x);
              const py = Math.round(fp.y);
              if (px < -4 || px >= LOW_W + 4 || py < -4 || py >= LOW_H + 4) continue;
              lowCtx.fillStyle = f.color;
              lowCtx.fillRect(px, py, 2, 2);
            }
          }

          // Espuma animada nas quedas de cachoeiras dinâmicas (ΔZ >= 3)
          if (visWaterfalls.length > 0) {
            lowCtx.fillStyle = 'rgba(240, 249, 255, 0.82)';
            for (let i = 0; i < visWaterfalls.length; i++) {
              const wd = visWaterfalls[i];
              if (z < wd.botZ || z > wd.topZ) continue;
              if (((z + dropStreakTick + wd.mx * 3 + wd.my * 5) % 4) === 0 || z <= wd.botZ + 1) {
                const wp = project(wd.wx, wd.wy, z + 0.2);
                lowCtx.fillRect(Math.round(wp.x) - 1, Math.round(wp.y), 2, 2);
              }
            }
          }

          // 4b. Recorte matemático de oclusão 3D em entityCanvas
          if (entityStarted) {
            entityCtx.globalCompositeOperation = 'destination-out';
            drawBoundedSliceTo(entityCtx, tSlice, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy);
            entityCtx.globalCompositeOperation = 'source-over';
          }
        }

        // 4a-bis. Colunas e cortinas dinâmicas da cachoeira Virtual Pipe (waterfallSim)
        if (wfVisible && z >= -2 && z <= 50) {
          lowCtx.save();
          lowCtx.translate(LOW_W / 2, LOW_H / 2 + 16 - (z - camZ));
          lowCtx.scale(1, squash);
          lowCtx.rotate(turn);
          lowCtx.scale(VOX, VOX);
          lowCtx.translate(-camX / VOX, -camY / VOX);
          const wfCellVox = WF_CELL / VOX;
          const streakTick = Math.floor(fluidTime * 10);
          for (let iy = 0; iy < WF_H; iy++) {
            const row = iy * WF_W;
            const laneOff = ((iy * 13) ^ (iy >> 1)) & 3;
            for (let ix = 0; ix < WF_W; ix++) {
              const idx = row + ix;
              const d = wfH[idx];
              if (d <= 0.12) continue;
              const bed = wfBedZ[idx];
              let minNb = bed;
              if (ix > 0 && wfBedZ[idx - 1] < minNb) minNb = wfBedZ[idx - 1];
              if (ix < WF_W - 1 && wfBedZ[idx + 1] < minNb) minNb = wfBedZ[idx + 1];
              if (iy > 0 && wfBedZ[idx - WF_W] < minNb) minNb = wfBedZ[idx - WF_W];
              if (iy < WF_H - 1 && wfBedZ[idx + WF_W] < minNb) minNb = wfBedZ[idx + WF_W];
              const zTop = Math.min(50, Math.round(bed + Math.min(2.0, Math.max(0.8, d))));
              const zBot = Math.max(Z_MIN, Math.round(Math.min(bed - 1, minNb)));
              if (z < zBot || z > zTop) continue;
              const isTop = (z === zTop);
              const isDrop = (bed - minNb) > 2;
              const alpha = Math.min(0.94, Math.max(0.28, (d - 0.10) / 0.45));
              const colOff = (ix * 5 + iy * 3) & 3;
              const foam = (d > 0.22) && (isTop
                ? ((d > 0.65 && (((ix + streakTick + laneOff) % 6) === 0)) || isDrop)
                : ((((z + streakTick + colOff) % 4) === 0) || z <= 1));
              lowCtx.fillStyle = foam
                ? `rgba(224, 242, 254, ${alpha.toFixed(2)})`
                : (isTop ? `rgba(103, 232, 249, ${alpha.toFixed(2)})` : `rgba(56, 189, 248, ${alpha.toFixed(2)})`);
              lowCtx.fillRect((WF_X0 + ix * WF_CELL) / VOX, (WF_Y0 + iy * WF_CELL) / VOX, wfCellVox, wfCellVox);
            }
          }
          lowCtx.restore();
        }

        // Sombras dinâmicas no chão na altura z
        const shList = shadowsByZ.get(z);
        if (shList) {
          for (const sh of shList) {
            const c = getCellAt(sh.x, sh.y);
            const onTerrain = c && Math.abs(sh.groundZ - c.h) <= 1.2;
            const targetShadowCtx = onTerrain ? lowCtx : entityCtx;
            const sp = project(sh.x, sh.y, sh.groundZ + 0.3);
            targetShadowCtx.fillStyle = `rgba(38, 22, 14, ${sh.alpha})`;
            targetShadowCtx.beginPath();
            targetShadowCtx.ellipse(sp.x, sp.y, sh.radiusX, sh.radiusY, 0, 0, Math.PI * 2);
            targetShadowCtx.fill();
          }
        }

        // 4c. Pontas de grama animadas pelo vento (8 FPS, Tight-Crop)
        const gSlice = z <= Z_GRASS_MAX ? grassTipSlices[z] : null;
        if (gSlice && viewMaxMx > viewMinMx && viewMaxMy > viewMinMy) {
          const grassOff = Math.round(Math.sin(animTime * 4.5 + (z * 0.7)) * grassAmp + grassLean);
          drawBoundedSliceTo(lowCtx, gSlice, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy, grassOff);
        }

        // 4c-bis. Partículas 3D na fatia Z (ocluídas por falésias mais altas!)
        const pList = particlesByZ.get(z);
        if (pList) {
          for (let i = 0; i < pList.length; i++) {
            const p = pList[i];
            const pp = project(p.x, p.y, p.z);
            lowCtx.fillStyle = p.color;
            lowCtx.fillRect(Math.round(pp.x), Math.round(pp.y), p.size, p.size);
          }
        }

        // 4c-ter. Tecidos, cordas e bandeirinhas Verlet na fatia Z (com oclusão 3D real!)
        for (let ci = 0; ci < verletChains.length; ci++) {
          const ch = verletChains[ci];
          const nodes = ch.nodes;
          if (Math.hypot(nodes[0].x - camX, nodes[0].y - camY) > 420) continue;
          for (let ni = 0; ni < nodes.length - 1; ni++) {
            const a = nodes[ni], b = nodes[ni + 1];
            const midZ = Math.round((a.z + b.z) * 0.5);
            if (midZ !== z) continue;
            const pa = project(a.x, a.y, a.z);
            const pb = project(b.x, b.y, b.z);
            lowCtx.strokeStyle = ch.kind === 'vine' ? '#166534' : '#5C3A21';
            lowCtx.lineWidth = 1;
            lowCtx.beginPath();
            lowCtx.moveTo(Math.round(pa.x), Math.round(pa.y));
            lowCtx.lineTo(Math.round(pb.x), Math.round(pb.y));
            lowCtx.stroke();
            if (ch.kind === 'garland' && (ni & 1) === 1) {
              lowCtx.fillStyle = ch.colors[ni % ch.colors.length];
              lowCtx.fillRect(Math.round(pa.x) - 1, Math.round(pa.y) + 1, 2, 3);
            } else if (ch.kind === 'banner' && ni >= 2) {
              lowCtx.fillStyle = ch.colors[ni % ch.colors.length];
              lowCtx.fillRect(Math.round(pa.x) - 1, Math.round(pa.y), 3, 2);
            } else if (ch.kind === 'vine' && (ni & 1) === 0) {
              lowCtx.fillStyle = ch.colors[ni % ch.colors.length];
              lowCtx.fillRect(Math.round(pa.x) - 1, Math.round(pa.y), 2, 2);
            }
          }
        }

        // 4d. Entidades cujo [baseZ, topZ) contém z
        for (let i = 0; i < activeDrawables.length; i++) {
          const d = activeDrawables[i];
          if (z >= d.baseZ && z < d.topZ) {
            entityStarted = true;
            d.drawSlice(z);
          }
        }

        // Brilho de fogueira / lanternas na altura z
        const fList = firesByZ.get(z);
        if (fList) {
          const flick = Math.sin(cat.idleTimer * 12) * 1.5;
          for (const p of fList) {
            const fp = project(p.wx, p.wy, z);
            lowCtx.fillStyle = 'rgba(255, 210, 80, 0.32)';
            lowCtx.beginPath();
            lowCtx.arc(fp.x, fp.y, 6.5 + flick * 0.4, 0, Math.PI * 2);
            lowCtx.fill();
          }
        }
      }

      // 5. Silhueta Única 1px (#3B2219) + Composição de entityCanvas sobre lowCtx
      if (entityStarted) {
        entitySilCtx.globalCompositeOperation = 'source-over';
        entitySilCtx.clearRect(0, 0, LOW_W, LOW_H);
        entitySilCtx.drawImage(entityCanvas, 0, 0);
        entitySilCtx.globalCompositeOperation = 'source-in';
        entitySilCtx.fillStyle = '#3B2219';
        entitySilCtx.fillRect(0, 0, LOW_W, LOW_H);
        entitySilCtx.globalCompositeOperation = 'source-over';

        lowCtx.drawImage(entitySilCanvas, -1, 0);
        lowCtx.drawImage(entitySilCanvas,  1, 0);
        lowCtx.drawImage(entitySilCanvas,  0, -1);
        lowCtx.drawImage(entitySilCanvas,  0,  1);
        lowCtx.drawImage(entityCanvas, 0, 0);
      }

      // 6. Upscale 1:1 quadrado Nearest-Neighbor para o canvas principal + Balões Hi-Res
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, viewW, viewH);
      ctx.drawImage(lowCanvas, 0, 0, LOW_W * pixelScale, LOW_H * pixelScale);

      drawSpeechOverlaysHiRes(speechQueue);
      } finally {
        camX = prevCamX;
        camY = prevCamY;
      }
    }

