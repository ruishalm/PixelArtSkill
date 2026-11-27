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

    function waterBedZ(cell) {
      if (!cell) return -6;
      if (!isWetMat(cell.mat)) return cell.h;
      if (cell.waterDepth > 0) return Math.max(Z_MIN, waterSurfZ(cell) - cell.waterDepth);
      return cell.h;
    }

    function getEffectiveGroundForCell(c, refZ, scale = cat.scale || 1) {
      if (!c) return null;
      if (c.hasCave && refZ < c.caveCeil - 4) {
        if (c.caveCeil - c.caveFloor < 10 * scale) return c.h;
        return c.caveFloor;
      }
      return (c.mat === MAT_SHALLOW && c.h >= 0 && c.waterDepth > 0)
        ? Math.max(Z_MIN, c.h - Math.min(2, c.waterDepth))
        : c.h;
    }

    function getEffectiveGroundAt(wx, wy, refZ, scale = cat.scale || 1) {
      return getEffectiveGroundForCell(getCellAt(wx, wy), refZ, scale);
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
        if (!c) continue;
        const inLowerCave = c.hasCave && (currentZ < c.caveCeil - 4 || (!onGround && cat.groundZ < c.caveCeil - 4 && currentZ < c.caveCeil));
        if (!inLowerCave && (c.mat === MAT_WATER || !c.standable)) continue;
        const refZ = inLowerCave ? Math.min(currentZ, c.caveCeil - 5) : currentZ;
        const supH = getEffectiveGroundForCell(c, refZ, S);
        if (supH !== null && supH <= currentZ + climbAllowed) {
          if (supH > bestH) bestH = supH;
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
      const centerInCave = centerCell && centerCell.hasCave && (catZ < centerCell.caveCeil - 4 || (!onGround && cat.groundZ < centerCell.caveCeil - 4 && catZ < centerCell.caveCeil));
      if (!onCenterBridge && !centerInCave && centerCell && centerCell.mat === MAT_WATER && (onGround || catZ <= waterSurfZ(centerCell) + 0.3)) {
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
        const inLowerCave = c.hasCave && (catZ < c.caveCeil - 4 || (!onGround && cat.groundZ < c.caveCeil - 4 && catZ < c.caveCeil));
        if (inLowerCave) {
          const effCaveH = getEffectiveGroundForCell(c, Math.min(catZ, c.caveCeil - 5), S);
          if (effCaveH > catZ + allowedClimb) {
            blocked = true;
            if (effCaveH > maxBlockingH) maxBlockingH = effCaveH;
          }
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
      const onProbeCave = c.hasCave && cat.groundZ < c.caveCeil - 4;
      if (!onProbeBr && !onProbeCave && c.mat === MAT_WATER) {
        cat.obstacleHint = 'water';
        cat.obstacleLabel = '💧 Água Intransponível';
        return;
      }
      if (onProbeCave && c.caveCeil - c.caveFloor < 10 * S) {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = '⛔ Caverna Muito Baixa';
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
        : (onProbeCave
          ? c.caveFloor
          : ((!c.standable && c.h > cat.groundZ + AUTO_STEP_MAX) ? Math.max(c.h, c.cliffTop) : c.h));
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
    let camZoom = 1.0;
    let viewW = window.innerWidth;
    let viewH = window.innerHeight;
    let dpr = 1;

    function syncZoomUi() {
      const btnReset = document.getElementById('btnZoomReset');
      if (btnReset) btnReset.textContent = `🔍 ${Math.round(camZoom * 100)}%`;
    }

    function setCamZoom(newZoom) {
      const v = Number.isFinite(newZoom) ? newZoom : 1.0;
      camZoom = Math.max(0.35, Math.min(3.0, +v.toFixed(4)));
      handleResize();
      syncZoomUi();
      return camZoom;
    }

    function adjustCamZoom(delta) {
      return setCamZoom(camZoom + (Number.isFinite(delta) ? delta : 0));
    }

    function handleResize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      const host = canvas.parentElement;
      viewW = (host && host.clientWidth > 0) ? host.clientWidth : window.innerWidth;
      viewH = (host && host.clientHeight > 0) ? host.clientHeight : window.innerHeight;
      const baseScale = Math.max(2, Math.min(4, Math.floor(Math.min(viewW, viewH) / 260) || 2));
      pixelScale = Math.max(1, Math.min(10, +(baseScale * camZoom).toFixed(2)));
      LOW_W = Math.max(64, Math.ceil(viewW / pixelScale));
      LOW_H = Math.max(64, Math.ceil(viewH / pixelScale));

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
    syncZoomUi();

    canvas.addEventListener('wheel', (e) => {
      if (e.preventDefault) e.preventDefault();
      if (e.deltaY < 0) setCamZoom(camZoom * 1.15);
      else if (e.deltaY > 0) setCamZoom(camZoom / 1.15);
    }, { passive: false });

    window.addEventListener('keydown', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
      const modelerEl = document.getElementById('modelerView');
      if (modelerEl && modelerEl.classList && modelerEl.classList.contains('show')) return;

      const code = e.code;
      if (!e.ctrlKey && !e.metaKey && !e.altKey) {
        if (e.key === '+' || e.key === '=' || code === 'Equal' || code === 'NumpadAdd') {
          if (e.preventDefault) e.preventDefault();
          setCamZoom(camZoom * 1.15);
          return;
        } else if (e.key === '-' || e.key === '_' || code === 'Minus' || code === 'NumpadSubtract') {
          if (e.preventDefault) e.preventDefault();
          setCamZoom(camZoom / 1.15);
          return;
        } else if (e.key === '0' || code === 'Digit0' || code === 'Numpad0') {
          if (e.preventDefault) e.preventDefault();
          setCamZoom(1.0);
          return;
        }
      }

      keys[code] = true;
      if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code)) {
        if (e.preventDefault) e.preventDefault();
      }
      if (window.__STUDIO_EDIT_MODE__) return;
      if (code === 'Space') {
        cat.jumpBuffer = 0.13;
      } else if (code === 'KeyR') {
        triggerAction();
      } else if (code === 'KeyF') {
        if (!throwCarriedItem()) triggerAction();
      } else if (code === 'KeyG') {
        pickOrDropItem();
      } else if (code === 'KeyC') {
        resetCatToSpawn();
      } else if (code === 'KeyM') {
        if (typeof triggerMeow === 'function') triggerMeow();
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
          const npcEffH = c ? getEffectiveGroundForCell(c, npc.z, npc.scale || 1) : null;
          const npcInCave = c && c.hasCave && npc.z < c.caveCeil - 4;
          if (c && npcEffH !== null && (npcInCave || !isWetMat(c.mat)) && Math.abs(npcEffH - npc.z) <= 5.5) {
            let hitProp = false;
            for (const sc of propColliders) {
              if (sc.disabled) continue;
              if (isPointInPropCollider(nx, ny, sc, 3.5)) { hitProp = true; break; }
            }
            if (!hitProp) {
              npc.x = nx;
              npc.y = ny;
              npc.z = npcEffH;
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
      const headCell = getCellAt(cat.x, cat.y);
      if (headCell && headCell.hasCave && prevZ < headCell.caveCeil - 2 && cat.vz > 0) {
        const maxHeadZ = Math.max(headCell.caveFloor, headCell.caveCeil - 4.5);
        if (cat.z > maxHeadZ) {
          cat.z = maxHeadZ;
          cat.vz = 0;
        }
      }
      if (cat.z > cat.maxJumpReached) cat.maxJumpReached = cat.z;

      const supportQueryZ = (!wasOnGround && cat.vz <= 0) ? Math.max(cat.z, prevZ) : cat.z;
      const sup = evaluateSupport(cat.x, cat.y, supportQueryZ, wasOnGround);
      const supInCave = sup.centerCell && sup.centerCell.hasCave && cat.z < sup.centerCell.caveCeil - 4;
      if (sup.bestH > -900) {
        cat.groundZ = sup.bestH;
        if (cat.z <= sup.bestH + 0.05 && cat.vz <= 0 && (wasOnGround || prevZ >= sup.bestH - 2.0)) {
              if (!wasOnGround && cat.vz < -90) {
            if (!supInCave && sup.centerCell && sup.centerCell.mat === MAT_SHALLOW) {
              sfxShallowStep();
              injectWaterRipple(cat.x, cat.y, 1.8, 2);
              spawnParticles(cat.x, cat.y, waterSurfZ(sup.centerCell) + 0.5, 6, ['#E0F2FE', '#67E8F9', '#FFFFFF'], 24);
            } else {
              sfxLand();
              spawnParticles(cat.x, cat.y, sup.bestH + 1, 6, ['#FDF6E9', '#D6C4AA'], 24);
              if (!supInCave && sup.centerCell && (sup.centerCell.mat === MAT_SAND || sup.centerCell.mat === MAT_PEAK)) {
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
        const hitHighWater = !supInCave && sup.centerCell && sup.centerCell.mat === MAT_WATER && cat.z <= waterSurfZ(sup.centerCell) - 1.2;
        if (cat.z < -2.5 || hitHighWater) {
          const inWater = !supInCave && sup.centerCell && sup.centerCell.mat === MAT_WATER;
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
      const inCurCave = curCell && curCell.hasCave && cat.z < curCell.caveCeil - 4;
      const curBr = getBridgeAt(cat.x, cat.y);
      const onCurBr = curBr && cat.z >= getBridgeDeckZ(curBr, cat.x, cat.y) - AUTO_STEP_MAX - 1;
      const catSubVol = (curCell && !inCurCave && isWetMat(curCell.mat) && !onCurBr && cat.z <= waterSurfZ(curCell) + 1.0) ? 1.6 : 0;
      const prevCatSub = cat._prevSubVol || 0;
      if (catSubVol !== prevCatSub) {
        injectWaterRipple(cat.x, cat.y, (catSubVol - prevCatSub) * 1.1, 2);
        cat._prevSubVol = catSubVol;
      }
      if (curCell && !inCurCave && curCell.mat === MAT_SHALLOW && !onCurBr && cat.onGround) {
        const wadeFlow = sampleWaterFlow(cat.x, cat.y);
        if (wadeFlow.speed > 2.5) {
          const driftX = wadeFlow.vx * 0.45 * dt;
          const driftY = wadeFlow.vy * 0.45 * dt;
          if (driftX !== 0 && !checkCollisionAt(cat.x + driftX, cat.y, cat.z, true).blocked) cat.x += driftX;
          if (driftY !== 0 && !checkCollisionAt(cat.x, cat.y + driftY, cat.z, true).blocked) cat.y += driftY;
        }
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
        if (!inCurCave && cat.onGround && (curCell.mat === MAT_GRASS || curCell.mat === MAT_PEAK) && cat.isWalking && curCell.idx !== lastRustleCell) {
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

      // Pétalas/itens flutuantes no poço da cachoeira e correnteza do rio até o dreno no mar sul (Vale Felino)
      if (!window.__IS_STUDIO__) {
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

      stepFallingBodies(dt);
      stepDebrisDrops(dt);

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
        if (!window.__IS_STUDIO__) stepWaterfallSim(1 / 30, true);
        stepAutoWaterfallsAndSprings(true);
        stepWaveBuffer();
      }
      stepThermodynamics(dt);
      stepVerletChains(dt);
    }
