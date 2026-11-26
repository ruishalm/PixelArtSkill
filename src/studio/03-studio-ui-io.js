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
        document.getElementById('helpPill').textContent = 'Editar: Clique/Arraste pincel • [ ] Raio • Ctrl+Z/Y • Dir. orbita • WASD câmera • Q/E gira';
      });
      document.getElementById('btnModeTest').addEventListener('click', () => {
        window.__STUDIO_EDIT_MODE__ = false;
        document.getElementById('btnModeEdit').className = 'mode-btn';
        document.getElementById('btnModeTest').className = 'mode-btn active-test';
        const safe = S.findSafeSpawnNear(camX, camY);
        teleportToWorld(safe.x, safe.y, 'Testando cena! 🐱', safe.z);
        document.getElementById('helpPill').textContent = document.body.classList.contains('play-only')
          ? 'WASD anda • Espaço pula • F quebra/arremessa • G pega/solta • Q/E gira'
          : 'Testar: WASD anda • Espaço pula • F quebra/arremessa • G pega/solta • Volte p/ Editar';
      });

      document.querySelector('.sidebar').addEventListener('click', (e) => {
        const btn = e.target.closest('.tool-btn');
        if (!btn || !btn.dataset.tool) return;
        document.querySelectorAll('.sidebar .tool-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        S.activeTool = btn.dataset.tool;
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
        cat.scale = kind === 'human' ? 1.0 : 0.45;
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
        return {
          version: 2,
          gridW: mw,
          gridH: mh,
          seed: WORLD_SEED,
          baseKind: baseKindSel ? baseKindSel.value : 'island',
          generationMode: genModeSel ? genModeSel.value : 'hybrid',
          avatar: cat.avatar || 'cat',
          avatarScale: cat.scale,
          tuning: { ...ENGINE_TUNING, gravity: GRAVITY },
          customAssets: window.StudioModeler ? window.StudioModeler.exportAssets() : [],
          pinnedCells,
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
        if (Array.isArray(data.pinnedCells)) {
          for (const [idx, h, m] of data.pinnedCells) {
            if (idx < 0 || idx >= hmap.length) continue;
            pinnedMask[idx] = 1;
            hmap[idx] = h;
            matMap[idx] = m;
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
          if (cloneBody) cloneBody.classList.remove('play-only');
          const cloneWorkspace = docClone.querySelector('.workspace');
          if (cloneWorkspace) cloneWorkspace.style.display = '';
          const cloneModeler = docClone.querySelector('#modelerView');
          if (cloneModeler) cloneModeler.classList.remove('show');
          const cloneAssetGrid = docClone.querySelector('#customAssetGrid');
          if (cloneAssetGrid) cloneAssetGrid.innerHTML = '';
          const cloneAssetEmpty = docClone.querySelector('#customAssetEmpty');
          if (cloneAssetEmpty) cloneAssetEmpty.style.display = '';
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

      // Cena publicada (.html exportado): carrega o projeto embutido e abre direto em modo Testar
      if (window.__STUDIO_BOOT__) {
        document.getElementById('modelerView')?.classList.remove('show');
        const ws = document.querySelector('.workspace');
        if (ws) ws.style.display = 'flex';
        try { loadProject(window.__STUDIO_BOOT__); } catch (err) { console.error(err); }
        document.body.classList.add('play-only');
        document.getElementById('btnModeTest').click();
        window.dispatchEvent(new Event('resize'));
      }
    })();
