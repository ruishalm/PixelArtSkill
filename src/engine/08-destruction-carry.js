    // =========================================================================
    // 8C. DESTRUIÇÃO, CARREGAMENTO (G/F), FOLHAGEM & CORPOS EM QUEDA
    // =========================================================================
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
        const ang = Math.atan2(biasDy, biasDx) + (Math.random() - 0.5) * 1.1;
        const hSpd = 30 + Math.random() * 34;
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

      // 3ª Lei de Newton (Ação e Reação): leve recuo do gato na direção oposta ao golpe
      const rawDx = bestTarget.wx - cat.x;
      const rawDy = bestTarget.wy - cat.y;
      const rawLen = Math.hypot(rawDx, rawDy) || 1;
      const hitDirX = (rawDx / rawLen) * 0.65 + fx * 0.35;
      const hitDirY = (rawDy / rawLen) * 0.65 + fy * 0.35;
      const hLen = Math.hypot(hitDirX, hitDirY) || 1;
      const dirX = hitDirX / hLen;
      const dirY = hitDirY / hLen;
      const recX = cat.x - dirX * 2.0;
      const recY = cat.y - dirY * 2.0;
      if (!checkCollisionAt(recX, recY, cat.z, cat.onGround).blocked) {
        cat.x = recX;
        cat.y = recY;
      }

      if (d.hp <= 0) {
        d.chopped = true;
        if (bestTarget.solidCollider) bestTarget.solidCollider.disabled = true;
        if (bestTarget.platCollider) bestTarget.platCollider.disabled = true;

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

    // Interação [Pegar / Soltar / Arremessar]: carrega drops (toras, pedras) acima da cabeça
    let carriedDrop = null;

    function pickOrDropItem() {
      const fx = -Math.sin(cat.selfAngle);
      const fy = Math.cos(cat.selfAngle);
      if (carriedDrop) {
        const dr = carriedDrop;
        carriedDrop = null;
        dr.carried = false;
        dr.x = cat.x + fx * 7 * (cat.scale || 1);
        dr.y = cat.y + fy * 7 * (cat.scale || 1);
        const dropCell = getCellAt(dr.x, dr.y) || getCellAt(cat.x, cat.y);
        if (dropCell && dropCell.hasCave && cat.z < dropCell.caveCeil - 2) {
          dr.z = Math.min(cat.z + 4 * (cat.scale || 1), dropCell.caveCeil - 3.5);
        }
        dr.vx = fx * 14;
        dr.vy = fy * 14;
        dr.vz = 10;
        return;
      }
      let bestDrop = null;
      let bestProp = null;
      let bestD = 24;
      for (let i = 0; i < debrisDrops.length; i++) {
        const dr = debrisDrops[i];
        if (dr.carried) continue;
        const d = Math.hypot(dr.x - cat.x, dr.y - cat.y);
        if (d < bestD && Math.abs(dr.z - cat.z) < 20) { bestD = d; bestDrop = dr; }
      }
      // Toras e itens pegáveis plantados no mapa viram drop pegável (compete por distância real)
      for (let i = 0; i < props.length; i++) {
        const p = props[i];
        const pm = PROP_COLLIDER_META[p.modelKey];
        if (p.destroyed || (p.modelKey !== 'wood_log' && !(pm && pm.pickable))) continue;
        const d = Math.hypot(p.wx - cat.x, p.wy - cat.y);
        if (d < bestD && Math.abs(p.wz - cat.z) < 20) {
          bestD = d;
          bestDrop = null;
          bestProp = p;
        }
      }
      let best = bestDrop;
      if (bestProp) {
        bestProp.destroyed = true;
        if (bestProp.solidCollider) bestProp.solidCollider.disabled = true;
        if (bestProp.platCollider) bestProp.platCollider.disabled = true;
        if (bestProp.modelKey === 'wood_log') {
          spawnPushableLog(bestProp.wx, bestProp.wy, bestProp.selfAngle || 0);
        } else {
          const pc = getCellAt(bestProp.wx, bestProp.wy);
          debrisDrops.push({
            modelKey: bestProp.modelKey,
            model: bestProp.model,
            x: bestProp.wx,
            y: bestProp.wy,
            z: bestProp.wz,
            vx: 0, vy: 0, vz: 0,
            scale: bestProp.scale || 0.85,
            selfAngle: bestProp.selfAngle || 0,
            spin: 0,
            bounces: 0,
            inWater: !!(pc && isWetMat(pc.mat)),
            persistent: true,
            life: 999999
          });
        }
        best = debrisDrops[debrisDrops.length - 1];
      }
      if (!best) return;
      best.carried = true;
      best.inWater = false;
      best.vx = 0; best.vy = 0; best.vz = 0;
      best.life = Math.max(best.life, 30);
      carriedDrop = best;
      catSpeak('Peguei!', 70);
    }

    function throwCarriedItem() {
      if (!carriedDrop) return false;
      const dr = carriedDrop;
      const fx = -Math.sin(cat.selfAngle);
      const fy = Math.cos(cat.selfAngle);
      carriedDrop = null;
      dr.carried = false;
      dr.x = cat.x + fx * 6 * (cat.scale || 1);
      dr.y = cat.y + fy * 6 * (cat.scale || 1);
      const throwCell = getCellAt(dr.x, dr.y) || getCellAt(cat.x, cat.y);
      if (throwCell && throwCell.hasCave && cat.z < throwCell.caveCeil - 2) {
        dr.z = Math.min(cat.z + 4 * (cat.scale || 1), throwCell.caveCeil - 3.5);
      }
      dr.vx = fx * 110;
      dr.vy = fy * 110;
      dr.vz = 85;
      dr.spin = 5;
      injectWindImpulse(dr.x, dr.y, fx * 1.6, fy * 1.6, 30, 0.4);
      return true;
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

    function stepFallingBodies(dt) {
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
    }

    function stepDebrisDrops(dt) {
    // Drops balísticos (toras & pedregulhos) + empurrão do gatinho + correnteza + Arquimedes local
    for (let i = debrisDrops.length - 1; i >= 0; i--) {
      const dr = debrisDrops[i];
      if (!dr.persistent) dr.life -= dt;
      if (dr.life <= 0) {
        debrisDrops.splice(i, 1);
        continue;
      }
      if (dr.carried) {
        const S = cat.scale || 1;
        const customAv = (typeof cat.avatar === 'string' && cat.avatar.startsWith('custom_'))
          ? ((typeof customAvatarModels !== 'undefined' && customAvatarModels[cat.avatar]) ||
             (typeof window !== 'undefined' && window.customAvatarModels && window.customAvatarModels[cat.avatar]) ||
             propModels[cat.avatar])
          : null;
        const carryH = cat.avatar === 'human' ? 31 : (customAv ? (customAv.count + 3) : 17);
        dr.x = cat.x - Math.sin(cat.selfAngle) * 4 * S;
        dr.y = cat.y + Math.cos(cat.selfAngle) * 4 * S;
        dr.z = cat.z + carryH * S;
        dr.vx = 0; dr.vy = 0; dr.vz = 0;
        dr.selfAngle = cat.selfAngle;
        dr.inWater = false;
        dr.life = Math.max(dr.life, 30);
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
            // Pedregulho (densidade > 1): afunda até o leito sólido (bedZ) deslocando seu volume inteiro
            const bedZ = waterBedZ(dc);
            dr.vz -= 180 * dt;
            dr.z = Math.max(bedZ, dr.z + dr.vz * dt);
            if (dr.z <= bedZ + 0.1) { dr.vz = 0; dr.vx *= 0.2; dr.vy *= 0.2; }
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
        if (!dc || (!window.__IS_STUDIO__ && dr.y > 860)) dr.life = Math.min(dr.life, 0.5);
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
        const prevDrZ = dr.z;
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
        if (dc.hasCave && prevDrZ < dc.caveCeil - 2 && dr.vz > 0 && dr.z > dc.caveCeil - 3) {
          dr.z = dc.caveCeil - 3;
          dr.vz = -dr.vz * 0.4;
        }
        const dcInCave = dc.hasCave && dr.z < dc.caveCeil - 2;
        if (!dcInCave && isWetMat(dc.mat) && dr.z <= waterSurfZ(dc) + 0.5) {
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
        } else {
          const effGroundZ = dcInCave ? dc.caveFloor : dc.h;
          if ((dcInCave || !isWetMat(dc.mat)) && dr.z <= effGroundZ) {
            dr.z = effGroundZ;
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
    }
    }
