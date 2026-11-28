    // =========================================================================
    // VOXEL 3D STUDIO — UI, EXPORT/IMPORT JSON, PUBLICAR .HTML STANDALONE
    // =========================================================================
    (function initStudioUiAndIo() {
      const S = window.__STUDIO__;
      if (!document.getElementById('studioOverlay') || !S) return;

      const {
        pinnedMask, sculptH, syncSculptFromHmap,
        removePropObj, clearAllProps, resetTerrainLayers,
        baseKindSel, genModeSel
      } = S;

      // 6. Bindings da UI (Modo, Ferramentas, Sliders, Export/Import)
      document.getElementById('btnModeEdit').addEventListener('click', () => {
        window.__STUDIO_EDIT_MODE__ = true;
        document.getElementById('btnModeEdit').className = 'mode-btn active-edit';
        document.getElementById('btnModeTest').className = 'mode-btn';
        document.getElementById('helpPill').textContent = 'Editar: Clique/Arraste pincel • Scroll: Zoom • [ ] Raio • Ctrl+Z/Y • Dir. orbita • WASD câmera • Q/E gira';
      });
      document.getElementById('btnModeTest').addEventListener('click', () => {
        window.__STUDIO_EDIT_MODE__ = false;
        document.getElementById('btnModeEdit').className = 'mode-btn';
        document.getElementById('btnModeTest').className = 'mode-btn active-test';
        const safe = S.findSafeSpawnNear(camX, camY);
        teleportToWorld(safe.x, safe.y, 'Testando cena! 🐱', safe.z);
        document.getElementById('helpPill').textContent = document.body.classList.contains('play-only')
          ? 'WASD anda • Espaço pula • Scroll: Zoom • F quebra/arremessa • G pega/solta • Q/E gira'
          : 'Testar: WASD anda • Espaço pula • Scroll: Zoom • F quebra/arremessa • G pega/solta • Volte p/ Editar';
      });

      const btnZoomOut = document.getElementById('btnZoomOut');
      const btnZoomReset = document.getElementById('btnZoomReset');
      const btnZoomIn = document.getElementById('btnZoomIn');
      if (btnZoomOut) btnZoomOut.addEventListener('click', () => {
        if (typeof setCamZoom === 'function') setCamZoom(camZoom / 1.15);
      });
      if (btnZoomReset) btnZoomReset.addEventListener('click', () => {
        if (typeof setCamZoom === 'function') setCamZoom(1.0);
      });
      if (btnZoomIn) btnZoomIn.addEventListener('click', () => {
        if (typeof setCamZoom === 'function') setCamZoom(camZoom * 1.15);
      });
      if (typeof syncZoomUi === 'function') syncZoomUi();

      document.querySelectorAll('.sidebar').forEach((sb) => {
        sb.addEventListener('click', (e) => {
          const btn = e.target.closest('.tool-btn');
          if (!btn || !btn.dataset.tool) return;
          document.querySelectorAll('.sidebar .tool-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          S.activeTool = btn.dataset.tool;
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
      bindSlider('slRadius', 'valRadius', v => `${v}`, v => { S.brushRadius = v; });

      // Avatar de teste: humanoide (escala 1.0) ou gato em escala realista (0.45)
      const avatarSel = document.getElementById('avatarSelect');
      const avatarScaleEl = document.getElementById('slAvatarScale');
      const avatarScaleVal = document.getElementById('valAvatarScale');
      function setAvatar(kind) {
        cat.avatar = kind;
        cat.scale = kind === 'cat' ? 0.45 : 1.0;
        avatarScaleEl.value = String(cat.scale);
        avatarScaleVal.textContent = `${cat.scale.toFixed(2)}x`;
      }
      avatarSel.addEventListener('change', () => setAvatar(avatarSel.value));
      setAvatar('human');
      bindSlider('slAvatarScale', 'valAvatarScale', v => `${v.toFixed(2)}x`, v => { cat.scale = v; });
      bindSlider('slStrength', 'valStrength', v => v.toFixed(1), v => { S.brushStrength = v; });
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
        S.pushUndoSnapshot();
        if (baseKindSel) baseKindSel.value = 'flat';
        hmap.fill(0);
        caveFloor.fill(-32768);
        caveCeil.fill(-32768);
        waterDepth.fill(0);
        waterSprings.length = 0;
        syncSculptFromHmap();
        matMap.fill(MAT_GRASS);
        pinnedMask.fill(0);
        customWindVx.fill(0); customWindVy.fill(0);
        customFlowVx.fill(0); customFlowVy.fill(0);
        clearAllProps();
        resetTerrainLayers();
        if (typeof bridges !== 'undefined') bridges.length = 0;
        if (typeof buildStandableMap === 'function') buildStandableMap();
        if (typeof initFlowStreaks === 'function') initFlowStreaks();
        camX = 0; camY = 0;
        bakeTerrainSlices();
        bakeMinimapBase();
      });
      document.getElementById('btnUndo').addEventListener('click', S.popUndoSnapshot);
      document.getElementById('btnRedo').addEventListener('click', S.popRedoSnapshot);
      window.addEventListener('keydown', (e) => {
        const tag = (e.target && e.target.tagName) || '';
        if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
        const modelerOpen = document.getElementById('modelerView')?.classList.contains('show');
        if (modelerOpen || !window.__STUDIO_EDIT_MODE__) return;

        const key = e.key.toLowerCase();
        if ((e.ctrlKey || e.metaKey) && key === 'z') {
          e.preventDefault();
          if (e.shiftKey) S.popRedoSnapshot();
          else S.popUndoSnapshot();
        } else if ((e.ctrlKey || e.metaKey) && key === 'y') {
          e.preventDefault();
          S.popRedoSnapshot();
        } else if (e.key === '[' || (e.key !== ']' && e.code === 'BracketLeft')) {
          S.brushRadius = Math.max(4, S.brushRadius - 2);
          document.getElementById('slRadius').value = String(S.brushRadius);
          document.getElementById('valRadius').textContent = String(S.brushRadius);
        } else if (e.key === ']' || (e.key !== '[' && e.code === 'BracketRight')) {
          S.brushRadius = Math.min(48, S.brushRadius + 2);
          document.getElementById('slRadius').value = String(S.brushRadius);
          document.getElementById('valRadius').textContent = String(S.brushRadius);
        }
      });

      function applyBoxPinState(pinVal) {
        const selectionBox = S.selectionBox;
        if (!selectionBox) return;
        S.pushUndoSnapshot();
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
      document.getElementById('btnPinAll').addEventListener('click', () => {
        S.pushUndoSnapshot();
        pinnedMask.fill(1);
        for (let i = 0; i < props.length; i++) props[i].pinned = true;
      });
      document.getElementById('btnUnpinAll').addEventListener('click', () => {
        S.pushUndoSnapshot();
        pinnedMask.fill(0);
        for (let i = 0; i < props.length; i++) props[i].pinned = false;
      });
      if (baseKindSel) {
        baseKindSel.addEventListener('change', () => {
          S.pushUndoSnapshot();
          const s = parseInt(document.getElementById('seedInput').value, 10) || DEFAULT_WORLD_SEED;
          const preserve = genModeSel && genModeSel.value === 'hybrid';
          S.regenWorld(s, preserve, baseKindSel.value);
        });
      }
      if (genModeSel) {
        genModeSel.addEventListener('change', () => {
          if (genModeSel.value === 'manual') {
            pinnedMask.fill(1);
            for (let i = 0; i < props.length; i++) props[i].pinned = true;
          } else if (genModeSel.value === 'procedural') {
            pinnedMask.fill(0);
            for (let i = 0; i < props.length; i++) props[i].pinned = false;
          }
        });
      }
      document.getElementById('btnClearSel').addEventListener('click', () => {
        const selectionBox = S.selectionBox;
        if (!selectionBox) return;
        S.pushUndoSnapshot();
        const mx0 = Math.max(0, Math.floor(selectionBox.x0 / VOX + HALF_GRID));
        const mx1 = Math.min(mw - 1, Math.ceil(selectionBox.x1 / VOX + HALF_GRID));
        const my0 = Math.max(0, Math.floor(selectionBox.y0 / VOX + HALF_GRID));
        const my1 = Math.min(mh - 1, Math.ceil(selectionBox.y1 / VOX + HALF_GRID));
        for (let my = my0; my <= my1; my++) {
          for (let mx = mx0; mx <= mx1; mx++) {
            const idx = my * mw + mx;
            sculptH[idx] = 0;
            hmap[idx] = 0;
            caveFloor[idx] = -32768;
            caveCeil[idx] = -32768;
            waterDepth[idx] = 0;
            matMap[idx] = MAT_GRASS;
            pinnedMask[idx] = 0;
          }
        }
        for (let i = waterSprings.length - 1; i >= 0; i--) {
          const sp = waterSprings[i];
          if (sp.wx >= selectionBox.x0 && sp.wx <= selectionBox.x1 && sp.wy >= selectionBox.y0 && sp.wy <= selectionBox.y1) {
            waterSprings.splice(i, 1);
          }
        }
        for (let i = props.length - 1; i >= 0; i--) {
          const p = props[i];
          if (p.wx >= selectionBox.x0 && p.wx <= selectionBox.x1 && p.wy >= selectionBox.y0 && p.wy <= selectionBox.y1) {
            removePropObj(p);
          }
        }
        if (typeof drainBreachedLakesInRect === 'function') {
          drainBreachedLakesInRect(mx0, my0, mx1, my1, idx => { sculptH[idx] = hmap[idx]; pinnedMask[idx] = 1; });
        }
        if (typeof buildStandableMap === 'function') buildStandableMap();
        if (typeof initFlowStreaks === 'function') initFlowStreaks();
        bakeTerrainSlices();
        bakeMinimapBase();
        S.selectionBox = null;
      });
      document.getElementById('btnRegenAll').addEventListener('click', () => {
        S.pushUndoSnapshot();
        const s = parseInt(document.getElementById('seedInput').value, 10) || DEFAULT_WORLD_SEED;
        S.regenWorld(s, false);
      });
      document.getElementById('btnRegenUnpinned').addEventListener('click', () => {
        S.pushUndoSnapshot();
        const s = parseInt(document.getElementById('seedInput').value, 10) || DEFAULT_WORLD_SEED;
        S.regenWorld(s, true);
      });

      // Exportar / Importar / Publicar projeto
      function buildProjectPayload() {
        const pinnedCells = [];
        for (let i = 0; i < pinnedMask.length; i++) {
          if (pinnedMask[i] === 1) {
            pinnedCells.push([i, Math.round(hmap[i] * 10) / 10, matMap[i], waterDepth[i]]);
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
        const caveSparse = [];
        for (let i = 0; i < caveFloor.length; i++) {
          if (caveCeil[i] > caveFloor[i] && hmap[i] > caveCeil[i]) {
            caveSparse.push([i, caveFloor[i], caveCeil[i]]);
          }
        }
        return {
          version: 3,
          gridW: mw,
          gridH: mh,
          seed: WORLD_SEED,
          baseKind: baseKindSel ? baseKindSel.value : 'island',
          generationMode: genModeSel ? genModeSel.value : 'hybrid',
          avatar: cat.avatar || 'cat',
          avatarScale: cat.scale,
          tuning: { ...ENGINE_TUNING, gravity: GRAVITY },
          customScript: currentCustomScript,
          customAssets: window.StudioModeler ? window.StudioModeler.exportAssets() : [],
          pinnedCells,
          caveSparse,
          springs: waterSprings.map(sp => ({ wx: +sp.wx.toFixed(1), wy: +sp.wy.toFixed(1), z: sp.z || 0 })),
          windSparse,
          flowSparse,
          pinnedProps: props.filter(p => p.pinned).map(p => ({
            modelKey: p.modelKey, wx: +p.wx.toFixed(1), wy: +p.wy.toFixed(1),
            angle: +p.selfAngle.toFixed(3), scale: +p.scale.toFixed(2)
          }))
        };
      }

      function loadProject(data) {
        if (data.gridW && (data.gridW !== mw || (data.gridH || data.gridW) !== mh)) {
          throw new Error(`A cena é ${data.gridW}×${data.gridH || data.gridW}; abra o Studio com ?grid=${data.gridW}`);
        }
        if (data.tuning) {
          ENGINE_TUNING.windMul = data.tuning.windMul ?? 1.0;
          ENGINE_TUNING.fireCool = data.tuning.fireCool ?? 0.22;
          ENGINE_TUNING.sandTalus = data.tuning.sandTalus ?? 2;
          if (data.tuning.gravity) {
            GRAVITY = data.tuning.gravity;
            JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0);
          }
          const syncSl = (id, vid, val, fmt) => {
            const el = document.getElementById(id), vEl = document.getElementById(vid);
            if (el) el.value = String(val);
            if (vEl) vEl.textContent = fmt(val);
          };
          syncSl('slWind', 'valWind', ENGINE_TUNING.windMul, v => `${v.toFixed(1)}x`);
          syncSl('slGravity', 'valGravity', GRAVITY, v => `${v}`);
          syncSl('slCool', 'valCool', ENGINE_TUNING.fireCool, v => v.toFixed(2));
          syncSl('slTalus', 'valTalus', ENGINE_TUNING.sandTalus, v => `${v}`);
        }
        if (window.StudioModeler && Array.isArray(data.customAssets)) {
          window.StudioModeler.importAssets(data.customAssets);
        }
        if (data.baseKind && baseKindSel) baseKindSel.value = data.baseKind;
        if (data.generationMode && genModeSel) genModeSel.value = data.generationMode;
        S.regenWorld(data.seed || DEFAULT_WORLD_SEED, false, data.baseKind || null);
        caveFloor.fill(-32768);
        caveCeil.fill(-32768);
        waterDepth.fill(0);
        waterSprings.length = 0;
        if (Array.isArray(data.pinnedCells)) {
          for (const entry of data.pinnedCells) {
            const idx = entry[0], h = entry[1], m = entry[2], wd = entry[3] || 0;
            if (idx < 0 || idx >= hmap.length) continue;
            pinnedMask[idx] = 1;
            hmap[idx] = h;
            matMap[idx] = m;
            waterDepth[idx] = wd;
          }
        }
        if (Array.isArray(data.caveSparse)) {
          for (const [idx, cf, cc] of data.caveSparse) {
            if (idx < 0 || idx >= caveFloor.length) continue;
            caveFloor[idx] = cf;
            caveCeil[idx] = cc;
          }
        }
        if (Array.isArray(data.springs)) {
          for (const sp of data.springs) {
            waterSprings.push({ wx: sp.wx, wy: sp.wy, z: sp.z || 0 });
          }
        }
        if (Array.isArray(data.windSparse)) {
          for (const [idx, vx, vy] of data.windSparse) {
            if (idx < 0 || idx >= customWindVx.length) continue;
            customWindVx[idx] = vx; customWindVy[idx] = vy;
          }
        }
        if (Array.isArray(data.flowSparse)) {
          for (const [idx, vx, vy] of data.flowSparse) {
            if (idx < 0 || idx >= customFlowVx.length) continue;
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
        if (data.avatar) {
          avatarSel.value = data.avatar;
          setAvatar(data.avatar);
          if (data.avatarScale) {
            cat.scale = data.avatarScale;
            avatarScaleEl.value = String(cat.scale);
            avatarScaleVal.textContent = `${cat.scale.toFixed(2)}x`;
          }
        }
        syncSculptFromHmap();
        if (typeof buildStandableMap === 'function') buildStandableMap();
        if (typeof initFlowStreaks === 'function') initFlowStreaks();
        if (typeof data.customScript === 'string' && window.VoxelEngine) {
          const ta = document.getElementById('customScriptInput');
          if (ta) ta.value = data.customScript;
          window.VoxelEngine.runScript(data.customScript);
        }
        bakeTerrainSlices();
        bakeMinimapBase();
      }

      function downloadText(filename, text, mime) {
        const blob = new Blob([text], { type: mime });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.click();
      }

      async function fetchAssetText(url) {
        const absUrl = new URL(url, window.location.href).href;
        try {
          const res = await fetch(absUrl);
          if (!res.ok) throw new Error(`HTTP ${res.status} (${url})`);
          return await res.text();
        } catch (fetchErr) {
          return await new Promise((resolve, reject) => {
            try {
              const xhr = new XMLHttpRequest();
              xhr.open('GET', absUrl, true);
              xhr.onload = () => {
                if ((xhr.status === 200 || xhr.status === 0) && xhr.responseText) {
                  resolve(xhr.responseText);
                } else {
                  reject(fetchErr);
                }
              };
              xhr.onerror = () => reject(fetchErr);
              xhr.send();
            } catch (_) {
              reject(fetchErr);
            }
          });
        }
      }

      document.getElementById('btnExportJson').addEventListener('click', () => {
        downloadText(`voxel-scene-${mw}-seed-${WORLD_SEED}.json`, JSON.stringify(buildProjectPayload()), 'application/json');
      });

      const btnPublish = document.getElementById('btnPublishHtml');
      btnPublish.addEventListener('click', async () => {
        const origLabel = btnPublish.textContent;
        btnPublish.disabled = true;
        btnPublish.textContent = '⏳ Publicando...';
        try {
          const payload = buildProjectPayload();
          const cfg = JSON.stringify({ gridW: mw, gridH: mh });
          const bootJson = JSON.stringify(payload).replace(/</g, '\\u003c');
          const docClone = document.documentElement.cloneNode(true);

          const cloneBody = docClone.querySelector('body');
          if (cloneBody) cloneBody.classList.remove('play-only', 'in-modeler');
          const cloneWorkspace = docClone.querySelector('.workspace');
          if (cloneWorkspace) cloneWorkspace.style.display = '';
          const cloneModeler = docClone.querySelector('#modelerView');
          if (cloneModeler) cloneModeler.classList.remove('show');
          const cloneAssetGrid = docClone.querySelector('#customAssetGrid');
          if (cloneAssetGrid) cloneAssetGrid.innerHTML = '';
          const cloneAssetEmpty = docClone.querySelector('#customAssetEmpty');
          if (cloneAssetEmpty) cloneAssetEmpty.style.display = '';
          const cloneZoomReset = docClone.querySelector('#btnZoomReset');
          if (cloneZoomReset) cloneZoomReset.textContent = '🔍 100%';
          docClone.querySelectorAll('#avatarSelect option[value^="custom_"]').forEach(el => el.remove());
          docClone.querySelectorAll('script[data-studio-boot]').forEach(el => el.remove());

          const cssLinks = Array.from(docClone.querySelectorAll('link[rel="stylesheet"][href]'));
          const scriptTags = Array.from(docClone.querySelectorAll('script[src]'));

          const [cssTexts, jsTexts] = await Promise.all([
            Promise.all(cssLinks.map(el => fetchAssetText(el.getAttribute('href')))),
            Promise.all(scriptTags.map(el => fetchAssetText(el.getAttribute('src'))))
          ]);

          cssLinks.forEach((linkEl, i) => {
            const styleEl = document.createElement('style');
            styleEl.textContent = cssTexts[i].replace(/<\/style/gi, '<\\/style');
            linkEl.replaceWith(styleEl);
          });

          scriptTags.forEach((scriptEl, i) => {
            scriptEl.removeAttribute('src');
            scriptEl.textContent = jsTexts[i].replace(/<\/script/gi, '<\\/script');
          });

          const bootEl = document.createElement('script');
          bootEl.setAttribute('data-studio-boot', '1');
          bootEl.textContent = `window.__WORLD_CFG__=${cfg};window.__STUDIO_BOOT__=${bootJson};`;
          const firstScript = (cloneBody || docClone).querySelector('script');
          if (firstScript && firstScript.parentNode) {
            firstScript.parentNode.insertBefore(bootEl, firstScript);
          } else if (cloneBody) {
            cloneBody.appendChild(bootEl);
          }

          const html = '<!DOCTYPE html>\n' + docClone.outerHTML;
          downloadText(`diorama-${mw}-seed-${WORLD_SEED}.html`, html, 'text/html');
        } catch (err) {
          alert(
            'Erro ao publicar .html standalone: ' + err.message +
            '\nDica: sirva a pasta via HTTP (ex: python -m http.server) ou GitHub Pages.'
          );
        } finally {
          btnPublish.disabled = false;
          btnPublish.textContent = origLabel;
        }
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
            loadProject(JSON.parse(reader.result));
          } catch (err) {
            alert('Erro ao importar cena JSON: ' + err.message);
          }
        };
        reader.readAsText(file);
        e.target.value = '';
      });

      // API Pública de Injeção de Script (Mod / Gameplay)
      const _scriptTickCbs = [];
      const _scriptKeyCbs = [];
      let currentCustomScript = '';

      window.VoxelEngine = {
        get player() { return cat; },
        get props() { return props; },
        get drops() { return debrisDrops; },
        onTick: (fn) => { if (typeof fn === 'function') _scriptTickCbs.push(fn); },
        onKeyDown: (fn) => { if (typeof fn === 'function') _scriptKeyCbs.push(fn); },
        clearHooks: () => { _scriptTickCbs.length = 0; _scriptKeyCbs.length = 0; },
        getGroundAt: (wx, wy) => {
          const c = getCellAt(wx, wy);
          return c ? (c.hasCave && cat.z < c.caveCeil - 4 ? c.caveFloor : c.h) : 0;
        },
        spawnParticles: (wx, wy, wz, count = 8, colors = ['#38BDF8', '#E0F2FE'], speed = 35) => {
          if (typeof spawnParticles === 'function') spawnParticles(wx, wy, wz, count, colors, speed);
        },
        speak: (msg, frames = 60) => { if (typeof catSpeak === 'function') catSpeak(msg, frames); },
        teleportForward: (dist = 10) => {
          const fx = -Math.sin(cat.selfAngle);
          const fy = Math.cos(cat.selfAngle);
          const tx = Math.max(WORLD_MIN + 4, Math.min(WORLD_MAX - 4, cat.x + fx * dist));
          const ty = Math.max(WORLD_MIN + 4, Math.min(WORLD_MAX - 4, cat.y + fy * dist));
          const col = checkCollisionAt(tx, ty, cat.z, cat.onGround);
          if (col && col.blocked) return false;
          if (typeof spawnParticles === 'function') {
            spawnParticles(cat.x, cat.y, cat.z + 6, 8, ['#38BDF8', '#BAE6FD', '#FFFDF8'], 28);
          }
          cat.x = tx;
          cat.y = ty;
          const gz = window.VoxelEngine.getGroundAt(tx, ty);
          if (cat.onGround) { cat.z = gz; cat.groundZ = gz; }
          if (typeof spawnParticles === 'function') {
            spawnParticles(tx, ty, cat.z + 6, 10, ['#38BDF8', '#FDE68A', '#FFFDF8'], 34);
          }
          if (typeof playTone === 'function') playTone(520, 880, 0.09, 'triangle', 0.07);
          return true;
        },
        runScript: (code) => {
          window.VoxelEngine.clearHooks();
          currentCustomScript = String(code || '');
          const msgEl = document.getElementById('scriptStatusMsg');
          if (!currentCustomScript.trim()) {
            if (msgEl) { msgEl.style.color = '#A8A29E'; msgEl.textContent = 'Nenhum script ativo.'; }
            return true;
          }
          try {
            const fn = new Function('ThreeDish', 'VoxelEngine', currentCustomScript);
            fn(window.ThreeDish, window.VoxelEngine);
            if (msgEl) { msgEl.style.color = '#86EFAC'; msgEl.textContent = '✅ Script ativo no modo Testar!'; }
            return true;
          } catch (err) {
            if (msgEl) { msgEl.style.color = '#FCA5A5'; msgEl.textContent = '❌ Erro: ' + err.message; }
            return false;
          }
        }
      };
      window.ThreeDish = window.VoxelEngine;

      window.addEventListener('keydown', (e) => {
        if (window.__STUDIO_EDIT_MODE__) return;
        const tag = e.target && e.target.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (e.target && e.target.isContentEditable)) return;
        for (let i = 0; i < _scriptKeyCbs.length; i++) {
          try { _scriptKeyCbs[i](e.code, e); } catch (err) { console.error(err); }
        }
      });

      let _lastScriptTick = performance.now();
      (function scriptTickLoop(now) {
        const dt = Math.min(0.05, Math.max(0.001, (now - _lastScriptTick) / 1000));
        _lastScriptTick = now;
        if (!window.__STUDIO_EDIT_MODE__ && _scriptTickCbs.length > 0) {
          for (let i = 0; i < _scriptTickCbs.length; i++) {
            try { _scriptTickCbs[i](dt); } catch (err) { console.error(err); }
          }
        }
        if (typeof requestAnimationFrame === 'function') requestAnimationFrame(scriptTickLoop);
      })(performance.now());

      const BLINK_PRESET_CODE =
`// Blink: mini-teleport de 10 unidades (Tecla B ou Shift)
ThreeDish.onKeyDown((code) => {
  if (code === 'KeyB' || code === 'ShiftLeft') {
    if (ThreeDish.teleportForward(10)) {
      ThreeDish.speak('⚡ Blink!', 45);
    }
  }
});`;

      document.getElementById('btnPresetBlink')?.addEventListener('click', () => {
        const ta = document.getElementById('customScriptInput');
        if (ta) ta.value = BLINK_PRESET_CODE;
        window.VoxelEngine.runScript(BLINK_PRESET_CODE);
      });
      document.getElementById('btnRunScript')?.addEventListener('click', () => {
        const ta = document.getElementById('customScriptInput');
        window.VoxelEngine.runScript(ta ? ta.value : '');
      });
      document.getElementById('btnLoadScriptFile')?.addEventListener('click', () => {
        document.getElementById('fileScriptInput')?.click();
      });
      document.getElementById('fileScriptInput')?.addEventListener('change', (e) => {
        const f = e.target.files[0];
        if (!f) return;
        const r = new FileReader();
        r.onload = () => {
          const ta = document.getElementById('customScriptInput');
          if (ta) ta.value = r.result;
          window.VoxelEngine.runScript(r.result);
        };
        r.readAsText(f);
        e.target.value = '';
      });

      // Gerador PKZIP (Store + CRC32) em JS puro sem dependências
      function buildZipBlob(entries) {
        const enc = new TextEncoder();
        const crcTable = new Uint32Array(256);
        for (let i = 0; i < 256; i++) {
          let c = i;
          for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
          crcTable[i] = c >>> 0;
        }
        const crc32 = (u8) => {
          let c = 0xFFFFFFFF;
          for (let i = 0; i < u8.length; i++) c = crcTable[(c ^ u8[i]) & 0xFF] ^ (c >>> 8);
          return (c ^ 0xFFFFFFFF) >>> 0;
        };
        const locals = [];
        const centrals = [];
        let offset = 0;
        for (const ent of entries) {
          const nameBytes = enc.encode(ent.name);
          const dataBytes = typeof ent.data === 'string' ? enc.encode(ent.data) : ent.data;
          const crc = crc32(dataBytes);
          const sz = dataBytes.length;

          const lh = new Uint8Array(30 + nameBytes.length);
          const lv = new DataView(lh.buffer);
          lv.setUint32(0, 0x04034B50, true);
          lv.setUint16(4, 20, true);
          lv.setUint16(6, 0x0800, true); // UTF-8
          lv.setUint32(14, crc, true);
          lv.setUint32(18, sz, true);
          lv.setUint32(22, sz, true);
          lv.setUint16(26, nameBytes.length, true);
          lh.set(nameBytes, 30);
          locals.push(lh, dataBytes);

          const ch = new Uint8Array(46 + nameBytes.length);
          const cv = new DataView(ch.buffer);
          cv.setUint32(0, 0x02014B50, true);
          cv.setUint16(4, 20, true);
          cv.setUint16(6, 20, true);
          cv.setUint16(8, 0x0800, true);
          cv.setUint32(16, crc, true);
          cv.setUint32(20, sz, true);
          cv.setUint32(24, sz, true);
          cv.setUint16(28, nameBytes.length, true);
          cv.setUint32(42, offset, true);
          ch.set(nameBytes, 46);
          centrals.push(ch);

          offset += lh.length + sz;
        }
        let cdSize = 0;
        for (const c of centrals) cdSize += c.length;
        const eocd = new Uint8Array(22);
        const ev = new DataView(eocd.buffer);
        ev.setUint32(0, 0x06054B50, true);
        ev.setUint16(8, entries.length, true);
        ev.setUint16(10, entries.length, true);
        ev.setUint32(12, cdSize, true);
        ev.setUint32(16, offset, true);
        return new Blob([...locals, ...centrals, eocd], { type: 'application/zip' });
      }

      const btnExportZip = document.getElementById('btnExportZip');
      btnExportZip?.addEventListener('click', async () => {
        const origLabel = btnExportZip.textContent;
        btnExportZip.disabled = true;
        btnExportZip.textContent = '⏳ Zipando...';
        try {
          const payload = buildProjectPayload();
          const cfg = JSON.stringify({ gridW: mw, gridH: mh });
          const bootJson = JSON.stringify(payload).replace(/</g, '\\u003c');
          const entries = [];

          // 1. Assets customizados separados por tipo
          for (const a of (payload.customAssets || [])) {
            const catType = a.category || (a.solid ? 'solid' : 'decor');
            const folder = catType === 'avatar' ? 'assets/characters'
              : (catType === 'pickable' ? 'assets/equips'
              : (catType === 'foliage' ? 'assets/foliage' : 'assets/props'));
            entries.push({ name: `${folder}/${a.key}.json`, data: JSON.stringify(a, null, 2) });
          }

          // 2. Metadados do projeto + script customizado
          entries.push({ name: 'project.json', data: JSON.stringify(payload, null, 2) });
          entries.push({ name: 'scripts/custom.js', data: currentCustomScript || '// Scripts do projeto (ThreeDish API)\n' });
          entries.push({ name: 'project-boot.js', data: `window.__WORLD_CFG__=${cfg};window.__STUDIO_BOOT__=${bootJson};` });

          // 3. Clona o HTML e mapeia CSS/JS locais para pastas do projeto
          const docClone = document.documentElement.cloneNode(true);
          const cloneBody = docClone.querySelector('body');
          if (cloneBody) cloneBody.classList.remove('play-only', 'in-modeler');
          const cloneAssetGrid = docClone.querySelector('#customAssetGrid');
          if (cloneAssetGrid) cloneAssetGrid.innerHTML = '';
          docClone.querySelectorAll('#avatarSelect option[value^="custom_"]').forEach(el => el.remove());
          docClone.querySelectorAll('script[data-studio-boot]').forEach(el => el.remove());

          const cssLinks = Array.from(docClone.querySelectorAll('link[rel="stylesheet"][href]'));
          const scriptTags = Array.from(docClone.querySelectorAll('script[src]'));
          const [cssTexts, jsTexts] = await Promise.all([
            Promise.all(cssLinks.map(el => fetchAssetText(el.getAttribute('href')))),
            Promise.all(scriptTags.map(el => fetchAssetText(el.getAttribute('src'))))
          ]);

          cssLinks.forEach((el, i) => {
            const name = i === 0 ? 'style.css' : `style-${i}.css`;
            el.setAttribute('href', name);
            entries.push({ name, data: cssTexts[i] });
          });

          scriptTags.forEach((el, i) => {
            const rawSrc = el.getAttribute('src') || '';
            const clean = rawSrc.replace(/^(\.\.\/)+/, '').replace(/^src\//, '');
            el.setAttribute('src', clean);
            entries.push({ name: clean, data: jsTexts[i] });
          });

          const bootTag = document.createElement('script');
          bootTag.setAttribute('data-studio-boot', '1');
          bootTag.setAttribute('src', 'project-boot.js');
          const firstScript = (cloneBody || docClone).querySelector('script');
          if (firstScript && firstScript.parentNode) firstScript.parentNode.insertBefore(bootTag, firstScript);

          const zipHtml = '<!DOCTYPE html>\n' + docClone.outerHTML;
          entries.push({ name: 'index.html', data: zipHtml });

          const zipBlob = buildZipBlob(entries);
          const a = document.createElement('a');
          a.href = URL.createObjectURL(zipBlob);
          a.download = `3dish-project-${mw}-seed-${WORLD_SEED}.zip`;
          a.click();
        } catch (err) {
          alert(
            'Erro ao exportar .zip do projeto: ' + err.message +
            '\nDica: sirva a pasta via HTTP (ex: python -m http.server) ou GitHub Pages.'
          );
        } finally {
          btnExportZip.disabled = false;
          btnExportZip.textContent = origLabel;
        }
      });

      // Cena publicada (.html exportado): carrega o projeto embutido e abre direto em modo Testar
      if (window.__STUDIO_BOOT__) {
        document.getElementById('modelerView')?.classList.remove('show');
        document.body.classList.remove('in-modeler');
        const ws = document.querySelector('.workspace');
        if (ws) ws.style.display = 'flex';
        try { loadProject(window.__STUDIO_BOOT__); } catch (err) { console.error(err); }
        document.body.classList.add('play-only');
        document.getElementById('btnModeTest').click();
        window.dispatchEvent(new Event('resize'));
      }

      // Firebase Auth (Google) + Firestore 3 Slots (users/{uid}/projects/slot1..slot3)
      const FIREBASE_CONFIG = {
        apiKey: 'AIzaSyDbpwPefMoOSplja9lr3y3IQXXgHt1wei0',
        authDomain: 'studio-3dish.firebaseapp.com',
        projectId: 'studio-3dish',
        storageBucket: 'studio-3dish.firebasestorage.app',
        messagingSenderId: '213287230738',
        appId: '1:213287230738:web:cae71b9155c68c236167cb'
      };
      const SLOT_IDS = ['slot1', 'slot2', 'slot3'];
      const authGate = document.getElementById('authGateOverlay');
      const authMsg = document.getElementById('authGateMsg');
      const userBadge = document.getElementById('authUserBadge');
      const btnLogout = document.getElementById('btnAuthLogout');
      const btnCloud = document.getElementById('btnCloudProjects');
      const cloudModal = document.getElementById('cloudProjectsModal');
      const cloudList = document.getElementById('cloudSlotsList');
      const cloudMsg = document.getElementById('cloudModalMsg');

      let fbAuth = null;
      let fbDb = null;
      let fbUser = null;
      let fbSdk = null;
      const cloudCache = { slot1: null, slot2: null, slot3: null };

      function compactPayloadForCloud(payload) {
        let json = JSON.stringify(payload);
        if (json.length <= 580000) return json;
        const trimmed = {
          ...payload,
          pinnedCells: (payload.pinnedCells || []).filter(([, h, m, wd]) => Math.abs(h) > 0.05 || m !== MAT_GRASS || (wd || 0) > 0)
        };
        json = JSON.stringify(trimmed);
        if (json.length > 580000) {
          throw new Error(`Projeto muito grande (${Math.round(json.length / 1024)} KB > 580 KB) para nuvem; use Exportar .json/.zip.`);
        }
        return json;
      }

      function renderCloudSlots() {
        if (!cloudList) return;
        cloudList.innerHTML = '';
        SLOT_IDS.forEach((slotId, idx) => {
          const docData = cloudCache[slotId];
          const row = document.createElement('div');
          row.className = 'cloud-slot-row';
          const nameInput = document.createElement('input');
          nameInput.type = 'text';
          nameInput.className = 'mtxt';
          nameInput.maxLength = 80;
          nameInput.value = docData ? docData.name : `Projeto ${idx + 1}`;
          nameInput.style.flex = '1';

          const topRow = document.createElement('div');
          topRow.className = 'mrow';
          const tag = document.createElement('span');
          tag.textContent = `Slot ${idx + 1}`;
          tag.style.cssText = 'font-size:11px;font-weight:800;color:#FDE68A;min-width:44px;';
          topRow.append(tag, nameInput);

          const meta = document.createElement('div');
          meta.className = 'cloud-slot-meta';
          if (docData) {
            const dt = new Date(docData.updatedAt || Date.now()).toLocaleString();
            meta.textContent = `${docData.gridW}×${docData.gridW} • Seed ${docData.seed} • ${dt}`;
          } else {
            meta.textContent = 'Vazio';
          }

          const actions = document.createElement('div');
          actions.className = 'mrow';
          const bSave = document.createElement('button');
          bSave.className = 'btn accent';
          bSave.textContent = '☁️ Salvar aqui';
          bSave.onclick = async () => {
            if (!fbUser || !fbDb || !fbSdk) return;
            try {
              const name = (nameInput.value || `Projeto ${idx + 1}`).trim().slice(0, 80);
              const payload = buildProjectPayload();
              const payloadJson = compactPayloadForCloud(payload);
              const record = {
                uid: fbUser.uid,
                name,
                gridW: mw,
                seed: WORLD_SEED,
                updatedAt: Date.now(),
                payloadJson
              };
              await fbSdk.setDoc(fbSdk.doc(fbDb, 'users', fbUser.uid, 'projects', slotId), record);
              cloudCache[slotId] = record;
              renderCloudSlots();
              if (cloudMsg) { cloudMsg.style.color = '#86EFAC'; cloudMsg.textContent = `✅ Salvo no Slot ${idx + 1}!`; }
            } catch (err) {
              if (cloudMsg) { cloudMsg.style.color = '#FCA5A5'; cloudMsg.textContent = '❌ ' + err.message; }
            }
          };

          const bLoad = document.createElement('button');
          bLoad.className = 'btn pin';
          bLoad.textContent = '📂 Carregar';
          bLoad.disabled = !docData;
          bLoad.onclick = () => {
            if (!docData) return;
            try {
              const parsed = JSON.parse(docData.payloadJson);
              if (parsed.gridW && parsed.gridW !== mw) {
                alert(`Este projeto é ${parsed.gridW}×${parsed.gridW}. Troque o seletor "Mapa" para ${parsed.gridW} e carregue novamente.`);
                return;
              }
              loadProject(parsed);
              if (cloudModal) cloudModal.style.display = 'none';
            } catch (err) {
              if (cloudMsg) { cloudMsg.style.color = '#FCA5A5'; cloudMsg.textContent = '❌ ' + err.message; }
            }
          };

          const bDel = document.createElement('button');
          bDel.className = 'btn';
          bDel.textContent = '🗑️ Apagar';
          bDel.disabled = !docData;
          bDel.onclick = async () => {
            if (!fbUser || !fbDb || !fbSdk || !docData) return;
            if (!confirm(`Apagar "${docData.name}" do Slot ${idx + 1}?`)) return;
            try {
              await fbSdk.deleteDoc(fbSdk.doc(fbDb, 'users', fbUser.uid, 'projects', slotId));
              cloudCache[slotId] = null;
              renderCloudSlots();
              if (cloudMsg) { cloudMsg.style.color = '#FDE68A'; cloudMsg.textContent = `Slot ${idx + 1} apagado.`; }
            } catch (err) {
              if (cloudMsg) { cloudMsg.style.color = '#FCA5A5'; cloudMsg.textContent = '❌ ' + err.message; }
            }
          };

          actions.append(bSave, bLoad, bDel);
          row.append(topRow, meta, actions);
          cloudList.appendChild(row);
        });
      }

      async function refreshCloudSlots() {
        if (!fbUser || !fbDb || !fbSdk) return;
        for (const s of SLOT_IDS) cloudCache[s] = null;
        const snap = await fbSdk.getDocs(fbSdk.collection(fbDb, 'users', fbUser.uid, 'projects'));
        snap.forEach((d) => {
          if (SLOT_IDS.includes(d.id)) cloudCache[d.id] = d.data();
        });
        renderCloudSlots();
      }

      btnCloud?.addEventListener('click', async () => {
        if (!fbUser) {
          if (authGate) authGate.style.display = 'flex';
          return;
        }
        if (cloudMsg) cloudMsg.textContent = '';
        if (cloudModal) cloudModal.style.display = 'flex';
        try { await refreshCloudSlots(); } catch (err) {
          if (cloudMsg) { cloudMsg.style.color = '#FCA5A5'; cloudMsg.textContent = '❌ ' + err.message; }
        }
      });
      document.getElementById('btnCloseCloudModal')?.addEventListener('click', () => {
        if (cloudModal) cloudModal.style.display = 'none';
      });

      const canUseFirebase = !window.__STUDIO_BOOT__ && typeof window.location === 'object' && /^https?:$/.test(window.location.protocol);
      if (canUseFirebase && authGate) {
        authGate.style.display = 'flex';
        (async () => {
          try {
            const [appMod, authMod, fsMod] = await Promise.all([
              import('https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js'),
              import('https://www.gstatic.com/firebasejs/11.0.2/firebase-auth.js'),
              import('https://www.gstatic.com/firebasejs/11.0.2/firebase-firestore.js')
            ]);
            const fbApp = appMod.initializeApp(FIREBASE_CONFIG);
            fbAuth = authMod.getAuth(fbApp);
            fbDb = fsMod.getFirestore(fbApp);
            fbSdk = { ...authMod, ...fsMod };
            const provider = new authMod.GoogleAuthProvider();

            authMod.onAuthStateChanged(fbAuth, async (user) => {
              fbUser = user;
              if (user) {
                authGate.style.display = 'none';
                if (userBadge) {
                  userBadge.textContent = user.displayName || user.email || 'Conectado';
                  userBadge.style.display = '';
                }
                if (btnLogout) btnLogout.style.display = '';
                try { await refreshCloudSlots(); } catch (_) {}
              } else {
                authGate.style.display = 'flex';
                if (userBadge) userBadge.style.display = 'none';
                if (btnLogout) btnLogout.style.display = 'none';
              }
            });

            document.getElementById('btnGoogleLogin')?.addEventListener('click', async () => {
              if (authMsg) { authMsg.style.color = '#FDE68A'; authMsg.textContent = 'Abrindo login Google...'; }
              try {
                await authMod.signInWithPopup(fbAuth, provider);
              } catch (err) {
                const hint = err.code === 'auth/unauthorized-domain'
                  ? ` Domínio "${window.location.hostname}" não autorizado em Firebase Auth > Settings > Authorized domains.`
                  : '';
                if (authMsg) { authMsg.style.color = '#FCA5A5'; authMsg.textContent = (err.message || err.code) + hint; }
              }
            });

            btnLogout?.addEventListener('click', async () => {
              await authMod.signOut(fbAuth);
            });
          } catch (err) {
            if (authMsg) { authMsg.style.color = '#FCA5A5'; authMsg.textContent = 'Falha ao carregar Firebase: ' + err.message; }
          }
        })();
      }
    })();
