    // =========================================================================
    // 7. ESTADO DO GATO, FÍSICA CONTÍNUA EM MICRO-VOXELS & TRAVEL
    // =========================================================================
    const SPAWN_X = window.__IS_STUDIO__ ? 0 : -330;
    const SPAWN_Y = window.__IS_STUDIO__ ? 0 : 90;
    const cat = {
      x: SPAWN_X,
      y: SPAWN_Y,
      z: 0,
      vz: 0,
      groundZ: 0,
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
      lastSafeZ: 0,
      maxJumpReached: 0,
      obstacleHint: 'ok',
      obstacleLabel: '✅ Caminho Livre'
    };


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
      const S = cat.scale || 1;
      const r = (onGround ? 2.4 : 3.2) * S;
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

      const S = cat.scale || 1;
      const r = 2.6 * S;
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
          if (isPointInPropCollider(nx, ny, sc, 3.0 * S)) {
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
        if (d < pc.r + 1.2 * S && d <= curD + 0.05 && catZ < pc.topZ - 2.0 && catZ >= pc.baseZ - 4.0) {
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
      const S = cat.scale || 1;
      const fx = dirX !== 0 || dirY !== 0 ? dirX : -Math.sin(cat.selfAngle);
      const fy = dirX !== 0 || dirY !== 0 ? dirY : Math.cos(cat.selfAngle);
      const probeX = cat.x + fx * (11 * S);
      const probeY = cat.y + fy * (11 * S);
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
        if (cat.groundZ < sc.baseZ + sc.colH - 1.5 && isPointInPropCollider(probeX, probeY, sc, 3.2 * S)) {
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
        if (Math.hypot(probeX - pc.wx, probeY - pc.wy) <= pc.r + 2.0 * S && pc.topZ > targetH) {
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
      const host = canvas.parentElement;
      viewW = (host && host.clientWidth > 0) ? host.clientWidth : window.innerWidth;
      viewH = (host && host.clientHeight > 0) ? host.clientHeight : window.innerHeight;
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
        dr.vx = fx * 14;
        dr.vy = fy * 14;
        dr.vz = 10;
        return;
      }
      let best = null;
      let bestD = 24;
      for (let i = 0; i < debrisDrops.length; i++) {
        const dr = debrisDrops[i];
        if (dr.carried) continue;
        const d = Math.hypot(dr.x - cat.x, dr.y - cat.y);
        if (d < bestD && Math.abs(dr.z - cat.z) < 20) { bestD = d; best = dr; }
      }
      if (!best) {
        // Toras e itens pegáveis plantados no mapa viram drop pegável
        for (let i = 0; i < props.length; i++) {
          const p = props[i];
          const pm = PROP_COLLIDER_META[p.modelKey];
          if (p.destroyed || (p.modelKey !== 'wood_log' && !(pm && pm.pickable))) continue;
          const d = Math.hypot(p.wx - cat.x, p.wy - cat.y);
          if (d < bestD && Math.abs(p.wz - cat.z) < 20) {
            bestD = d;
            best = p;
          }
        }
        if (best) {
          best.destroyed = true;
          if (best.solidCollider) best.solidCollider.disabled = true;
          if (best.platCollider) best.platCollider.disabled = true;
          if (best.modelKey === 'wood_log') {
            spawnPushableLog(best.wx, best.wy, best.selfAngle || 0);
          } else {
            const pc = getCellAt(best.wx, best.wy);
            debrisDrops.push({
              modelKey: best.modelKey,
              model: best.model,
              x: best.wx,
              y: best.wy,
              z: best.wz,
              vx: 0, vy: 0, vz: 0,
              scale: best.scale || 0.85,
              selfAngle: best.selfAngle || 0,
              spin: 0,
              bounces: 0,
              inWater: !!(pc && isWetMat(pc.mat)),
              persistent: true,
              life: 999999
            });
          }
          best = debrisDrops[debrisDrops.length - 1];
        }
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
      dr.vx = fx * 110;
      dr.vy = fy * 110;
      dr.vz = 85;
      dr.spin = 5;
      injectWindImpulse(dr.x, dr.y, fx * 1.6, fy * 1.6, 30, 0.4);
      return true;
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
      } else if (code === 'KeyF' && !window.__STUDIO_EDIT_MODE__) {
        if (!throwCarriedItem()) triggerAction();
      } else if (code === 'KeyG' && !window.__STUDIO_EDIT_MODE__) {
        pickOrDropItem();
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
      if (window.__STUDIO_EDIT_MODE__) return;
      isDraggingCam = true;
      dragStartX = e.clientX;
      pointerDownX = e.clientX;
      pointerDownY = e.clientY;
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (window.__STUDIO_EDIT_MODE__) return;
      if (!isDraggingCam) return;
      const dx = e.clientX - dragStartX;
      dragStartX = e.clientX;
      targetTurn -= dx * 0.0085;
      turn = targetTurn;
    });
    canvas.addEventListener('pointerup', (e) => {
      if (window.__STUDIO_EDIT_MODE__) return;
      if (isDraggingCam && Math.hypot(e.clientX - pointerDownX, e.clientY - pointerDownY) < 6) {
        triggerAction();
      }
      isDraggingCam = false;
      try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
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
        if (dr.carried) {
          const S = cat.scale || 1;
          dr.x = cat.x - Math.sin(cat.selfAngle) * 4 * S;
          dr.y = cat.y + Math.cos(cat.selfAngle) * 4 * S;
          dr.z = cat.z + (cat.avatar === 'human' ? 31 : 17) * S;
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
