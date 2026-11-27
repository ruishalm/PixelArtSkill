    // =========================================================================
    // MODELADOR VOXEL (Sprite-Stacking): edita fatias Z, preview 3D, biblioteca
    // Expõe window.StudioModeler para o Studio de Mundo (props personalizados)
    // =========================================================================
    (function initModeler() {
      const view = document.getElementById('modelerView');
      if (!view) return;

      const editCv = document.getElementById('mEditCanvas');
      const eCtx = editCv.getContext('2d');
      const prevCv = document.getElementById('mPreviewCanvas');
      const pCtx = prevCv.getContext('2d');
      const msgEl = document.getElementById('mMsg');

      const DEFAULT_PAL = [
        'rgba(0,0,0,0)', '#F2C9A0', '#4F83C2', '#3E4A6E', '#5B3A22', '#2A2018', '#8A5A2B', '#B07A3C',
        '#3F8F3A', '#6BBF59', '#9AA3A8', '#C9CED2', '#D94F4F', '#F2C94C', '#FFFFFF', '#1B1B1B'
      ];
      const PAL_PRESETS = {
        default: DEFAULT_PAL,
        wood: [
          'rgba(0,0,0,0)', '#2A1810', '#3E2315', '#5B3A22', '#7A4E2D', '#9B663B', '#B97F4B', '#D49E6A',
          '#E7BC8E', '#4A3728', '#6B5340', '#8C7058', '#A8896E', '#C4A688', '#3F6E35', '#689F52'
        ],
        foliage: [
          'rgba(0,0,0,0)', '#143628', '#1B4332', '#2D6A4F', '#40916C', '#52B788', '#74C69D', '#95D5B2',
          '#9D174D', '#DB2777', '#F472B6', '#F9A8D4', '#FCE7F3', '#FACC15', '#5B3A22', '#8A5A2B'
        ],
        stone: [
          'rgba(0,0,0,0)', '#272A30', '#3B4048', '#525864', '#6E7685', '#8C95A6', '#AAB3C2', '#CBD2DF',
          '#E2E8F0', '#5C5852', '#847F77', '#ADA79E', '#CFC9BE', '#3F8F3A', '#6BBF59', '#D97706'
        ],
        character: [
          'rgba(0,0,0,0)', '#F2C9A0', '#D9A173', '#9E6B47', '#5B3A22', '#2A2018', '#1B1B1B', '#FFFFFF',
          '#4F83C2', '#3E4A6E', '#D94F4F', '#8E2B2B', '#3F8F3A', '#F2C94C', '#9333EA', '#94A3A8'
        ],
        pastel: [
          'rgba(0,0,0,0)', '#FFF5EB', '#FDE2E4', '#FAD2E1', '#E2ECE9', '#BEE1E6', '#DFE7FD', '#CDDAFD',
          '#FDE68A', '#FDBA74', '#FCA5A5', '#A7F3D0', '#93C5FD', '#C4B5FD', '#8C6D59', '#3B2219'
        ]
      };
      let pal = DEFAULT_PAL.slice();
      let N = 24;
      let vol = [];
      let front2D = new Uint8Array(N * N);
      let side2D = new Uint8Array(N * N);
      let curZ = 0;
      let tool = 'pencil';
      let curColor = 2;
      let painting = false;
      let hover = null;
      let angle = 0.6;
      let dragRotX = null;
      let voxCache = null;
      let previewZoom = 1.0;
      let editZoom = 1.0;
      let editPanX = 0;
      let editPanY = 0;
      let isPanningEdit = false;
      let panLastX = 0;
      let panLastY = 0;
      const customAssets = []; // { key, name, size, pal, slices, kind, solid, hp, dropKey }

      function newVolume(size) {
        N = size;
        vol = Array.from({ length: N }, () => new Uint8Array(N * N));
        front2D = new Uint8Array(N * N);
        side2D = new Uint8Array(N * N);
        curZ = 0;
        editPanX = 0;
        editPanY = 0;
        voxCache = null;
        const zEl = document.getElementById('mZ');
        zEl.max = String(N - 1);
        zEl.value = '0';
      }

      function say(text, ok = true) {
        msgEl.style.color = ok ? '#86EFAC' : '#FCA5A5';
        msgEl.textContent = text;
      }

      // ---------- Paleta ----------
      function renderPalette() {
        const box = document.getElementById('mPalette');
        box.innerHTML = '';
        pal.forEach((c, i) => {
          const b = document.createElement('button');
          b.className = 'swatch' + (i === 0 ? ' clear' : '') + (i === curColor ? ' sel' : '');
          if (i > 0) b.style.background = c;
          b.title = i === 0 ? 'Transparente' : `Cor ${i}`;
          b.addEventListener('click', () => {
            curColor = i;
            if (i > 0) document.getElementById('mColor').value = c;
            renderPalette();
          });
          box.appendChild(b);
        });
      }
      document.getElementById('mColor').addEventListener('input', (e) => {
        if (curColor === 0) return;
        pal[curColor] = e.target.value;
        voxCache = null;
        renderPalette();
        drawEdit();
      });

      const palPresetEl = document.getElementById('mPalPreset');
      if (palPresetEl) {
        palPresetEl.addEventListener('change', () => {
          const next = PAL_PRESETS[palPresetEl.value];
          if (!next) return;
          pal = next.slice();
          curColor = Math.min(Math.max(1, curColor), pal.length - 1);
          document.getElementById('mColor').value = pal[curColor];
          voxCache = null;
          renderPalette();
          drawEdit();
          say(`Paleta "${palPresetEl.options[palPresetEl.selectedIndex].textContent}" aplicada.`);
        });
      }

      function parseHexRGB(hex) {
        if (!hex || !hex.startsWith('#') || hex.length < 7) return [200, 200, 200];
        const n = parseInt(hex.slice(1, 7), 16);
        return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
      }
      function shadeHex(hex, factor) {
        const [r0, g0, b0] = parseHexRGB(hex);
        let r, g, b;
        if (factor >= 1) {
          const t = Math.min(0.45, (factor - 1) * 1.1);
          r = Math.round(r0 + (255 - r0) * t);
          g = Math.round(g0 + (250 - g0) * t);
          b = Math.round(b0 + (240 - b0) * t);
        } else {
          r = Math.round(r0 * factor);
          g = Math.round(g0 * factor);
          b = Math.round(b0 * factor);
        }
        const h2 = (v) => Math.max(0, Math.min(255, v)).toString(16).padStart(2, '0');
        return `#${h2(r)}${h2(g)}${h2(b)}`;
      }
      function findOrAddPalColor(hex) {
        const norm = hex.toLowerCase();
        for (let i = 1; i < pal.length; i++) {
          if (String(pal[i]).toLowerCase() === norm) return i;
        }
        if (pal.length < 36) {
          pal.push(hex);
          return pal.length - 1;
        }
        const [tr, tg, tb] = parseHexRGB(hex);
        let bestIdx = 1, bestDist = Infinity;
        for (let i = 1; i < pal.length; i++) {
          const [r, g, b] = parseHexRGB(pal[i]);
          const d = (r - tr) * (r - tr) + (g - tg) * (g - tg) + (b - tb) * (b - tb);
          if (d < bestDist) { bestDist = d; bestIdx = i; }
        }
        return bestIdx;
      }
      const btnAutoShade = document.getElementById('mBtnAutoShade');
      if (btnAutoShade) {
        btnAutoShade.addEventListener('click', () => {
          let zMin = N, zMax = -1;
          for (let z = 0; z < N; z++) {
            const layer = vol[z];
            for (let i = 0; i < layer.length; i++) {
              if (layer[i] > 0) {
                if (z < zMin) zMin = z;
                if (z > zMax) zMax = z;
                break;
              }
            }
          }
          if (zMax < 0) { say('Modelo vazio: pinte algo antes do Auto-Shading.', false); return; }
          if (zMax === zMin) { say('Pinte em mais de uma camada Z para aplicar Auto-Shading.', false); return; }
          const origPal = pal.slice();
          for (let z = zMin; z <= zMax; z++) {
            const t = (z - zMin) / (zMax - zMin);
            const factor = t < 0.33 ? 0.80 : (t > 0.68 ? 1.18 : 1.0);
            if (factor === 1.0) continue;
            const layer = vol[z];
            for (let i = 0; i < layer.length; i++) {
              const v = layer[i];
              if (v > 0 && origPal[v]) {
                layer[i] = findOrAddPalColor(shadeHex(origPal[v], factor));
              }
            }
          }
          voxCache = null;
          renderPalette();
          drawEdit();
          say(`Auto-Shading (Z ${zMin}..${zMax}) aplicado! Paleta com ${pal.length - 1} cores.`);
        });
      }

      // ---------- Edição ----------
      const cell = () => (editCv.width / N) * editZoom;

      function clampEditPan() {
        const maxPanX = Math.max(0, editCv.width * (editZoom - 1));
        const maxPanY = Math.max(0, editCv.height * (editZoom - 1));
        editPanX = Math.max(0, Math.min(maxPanX, editPanX));
        editPanY = Math.max(0, Math.min(maxPanY, editPanY));
      }

      function setEditZoom(newZoom, focusCanvasX = editCv.width / 2, focusCanvasY = editCv.height / 2) {
        const oldZoom = editZoom;
        const v = Number.isFinite(newZoom) ? newZoom : 1.0;
        editZoom = Math.max(1.0, Math.min(4.0, +v.toFixed(4)));
        const worldX = (focusCanvasX + editPanX) / oldZoom;
        const worldY = (focusCanvasY + editPanY) / oldZoom;
        editPanX = worldX * editZoom - focusCanvasX;
        editPanY = worldY * editZoom - focusCanvasY;
        clampEditPan();
        const lbl = document.getElementById('mEditZoomReset');
        if (lbl) lbl.textContent = `${Math.round(editZoom * 100)}%`;
        drawEdit();
        return editZoom;
      }

      function getExtrudeZ() {
        const el = document.getElementById('mExtrudeZ');
        const v = el ? parseInt(el.value, 10) : 1;
        return Math.max(1, Math.min(10, Number.isFinite(v) ? v : 1));
      }
      const extrudeEl = document.getElementById('mExtrudeZ');
      const extrudeValEl = document.getElementById('mExtrudeZVal');
      if (extrudeEl) {
        const syncExt = () => { if (extrudeValEl) extrudeValEl.textContent = String(getExtrudeZ()); };
        extrudeEl.addEventListener('input', syncExt);
        extrudeEl.addEventListener('change', syncExt);
        syncExt();
      }

      function cellAt(e) {
        const r = editCv.getBoundingClientRect();
        if (!r.width || !r.height) return null;
        const cs = cell();
        const px = ((e.clientX - r.left) / r.width) * editCv.width + editPanX;
        const py = ((e.clientY - r.top) / r.height) * editCv.height + editPanY;
        const x = Math.floor(px / cs);
        const y = Math.floor(py / cs);
        if (x < 0 || y < 0 || x >= N || y >= N) return null;
        return { x, y };
      }

      function setVoxel(x, y, v) {
        const zEnd = Math.min(N - 1, curZ + getExtrudeZ() - 1);
        const mirror = !!document.getElementById('mMirror')?.checked;
        for (let z = curZ; z <= zEnd; z++) {
          vol[z][y * N + x] = v;
          if (mirror) vol[z][y * N + (N - 1 - x)] = v;
        }
      }

      function floodFill(x, y, v) {
        const layer = vol[curZ];
        const target = layer[y * N + x];
        if (target === v) return;
        const zEnd = Math.min(N - 1, curZ + getExtrudeZ() - 1);
        const filled = [];
        const stack = [[x, y]];
        while (stack.length) {
          const [cx, cy] = stack.pop();
          if (cx < 0 || cy < 0 || cx >= N || cy >= N) continue;
          const idx = cy * N + cx;
          if (layer[idx] !== target) continue;
          layer[idx] = v;
          filled.push(idx);
          stack.push([cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]);
        }
        for (let z = curZ + 1; z <= zEnd; z++) {
          const zLayer = vol[z];
          for (let i = 0; i < filled.length; i++) zLayer[filled[i]] = v;
        }
      }

      function applyTool(c) {
        if (!c) return;
        if (tool === 'pencil') setVoxel(c.x, c.y, curColor);
        else if (tool === 'eraser') setVoxel(c.x, c.y, 0);
        else if (tool === 'fill') floodFill(c.x, c.y, curColor);
        else if (tool === 'pick') {
          const v = vol[curZ][c.y * N + c.x];
          if (v > 0) { curColor = v; document.getElementById('mColor').value = pal[v]; renderPalette(); }
          return;
        }
        voxCache = null;
        drawEdit();
      }

      editCv.addEventListener('contextmenu', (e) => { if (e.preventDefault) e.preventDefault(); });
      editCv.addEventListener('wheel', (e) => {
        if (e.preventDefault) e.preventDefault();
        const r = editCv.getBoundingClientRect();
        const fx = r.width ? ((e.clientX - r.left) / r.width) * editCv.width : editCv.width / 2;
        const fy = r.height ? ((e.clientY - r.top) / r.height) * editCv.height : editCv.height / 2;
        if (e.deltaY < 0) setEditZoom(editZoom * 1.15, fx, fy);
        else if (e.deltaY > 0) setEditZoom(editZoom / 1.15, fx, fy);
      }, { passive: false });

      const mEditZoomOut = document.getElementById('mEditZoomOut');
      const mEditZoomReset = document.getElementById('mEditZoomReset');
      const mEditZoomIn = document.getElementById('mEditZoomIn');
      if (mEditZoomOut) mEditZoomOut.addEventListener('click', () => setEditZoom(editZoom / 1.25));
      if (mEditZoomReset) mEditZoomReset.addEventListener('click', () => setEditZoom(1.0));
      if (mEditZoomIn) mEditZoomIn.addEventListener('click', () => setEditZoom(editZoom * 1.25));

      editCv.addEventListener('pointerdown', (e) => {
        if (e.button === 1 || e.button === 2) {
          if (e.preventDefault) e.preventDefault();
          if (editZoom > 1) {
            isPanningEdit = true;
            panLastX = e.clientX;
            panLastY = e.clientY;
            if (editCv.style) editCv.style.cursor = 'grabbing';
            editCv.setPointerCapture(e.pointerId);
          }
          return;
        }
        if (e.button !== undefined && e.button !== 0) return;
        painting = true;
        editCv.setPointerCapture(e.pointerId);
        applyTool(cellAt(e));
      });
      editCv.addEventListener('pointermove', (e) => {
        if (isPanningEdit) {
          const r = editCv.getBoundingClientRect();
          const sx = r.width ? (editCv.width / r.width) : 1;
          const sy = r.height ? (editCv.height / r.height) : 1;
          editPanX -= (e.clientX - panLastX) * sx;
          editPanY -= (e.clientY - panLastY) * sy;
          panLastX = e.clientX;
          panLastY = e.clientY;
          clampEditPan();
          drawEdit();
          return;
        }
        hover = cellAt(e);
        if (painting && tool !== 'fill' && tool !== 'pick') applyTool(hover);
        else drawEdit();
      });
      function endEditPointer(e) {
        if (isPanningEdit) {
          isPanningEdit = false;
          if (editCv.style) editCv.style.cursor = '';
        }
        painting = false;
        if (e && e.pointerId !== undefined) {
          try { editCv.releasePointerCapture(e.pointerId); } catch (_) {}
        }
      }
      editCv.addEventListener('pointerup', endEditPointer);
      editCv.addEventListener('pointercancel', endEditPointer);
      editCv.addEventListener('pointerleave', () => { hover = null; drawEdit(); });

      function drawEdit() {
        const cs = cell();
        const ox = -editPanX;
        const oy = -editPanY;
        const gridSpan = N * cs;
        eCtx.clearRect(0, 0, editCv.width, editCv.height);
        for (let y = 0; y < N; y++) {
          for (let x = 0; x < N; x++) {
            eCtx.fillStyle = ((x + y) & 1) ? '#1F1B19' : '#171412';
            eCtx.fillRect(x * cs + ox, y * cs + oy, cs, cs);
          }
        }
        if (document.getElementById('mOnion').checked && curZ > 0) {
          eCtx.globalAlpha = 0.35;
          const below = vol[curZ - 1];
          for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
            const v = below[y * N + x];
            if (v > 0) { eCtx.fillStyle = pal[v]; eCtx.fillRect(x * cs + ox, y * cs + oy, cs, cs); }
          }
          eCtx.globalAlpha = 1;
        }
        const layer = vol[curZ];
        for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
          const v = layer[y * N + x];
          if (v > 0) { eCtx.fillStyle = pal[v]; eCtx.fillRect(x * cs + ox, y * cs + oy, cs, cs); }
        }
        eCtx.strokeStyle = 'rgba(255,255,255,0.06)';
        eCtx.lineWidth = 1;
        eCtx.beginPath();
        for (let i = 0; i <= N; i++) {
          eCtx.moveTo(i * cs + ox + 0.5, oy); eCtx.lineTo(i * cs + ox + 0.5, oy + gridSpan);
          eCtx.moveTo(ox, i * cs + oy + 0.5); eCtx.lineTo(ox + gridSpan, i * cs + oy + 0.5);
        }
        eCtx.stroke();
        if (hover) {
          eCtx.strokeStyle = '#FBBF24';
          eCtx.lineWidth = 2;
          eCtx.strokeRect(hover.x * cs + ox + 1, hover.y * cs + oy + 1, cs - 2, cs - 2);
        }
        document.getElementById('mZLabel').textContent = `Z ${curZ} / ${N - 1}`;
      }

      // ---------- Camadas ----------
      function setZ(z) {
        curZ = Math.max(0, Math.min(N - 1, z));
        document.getElementById('mZ').value = String(curZ);
        drawEdit();
      }
      document.getElementById('mZ').addEventListener('input', (e) => setZ(parseInt(e.target.value, 10)));
      document.getElementById('mZUp').addEventListener('click', () => setZ(curZ + 1));
      document.getElementById('mZDown').addEventListener('click', () => setZ(curZ - 1));
      document.getElementById('mCopyDown').addEventListener('click', () => {
        if (curZ > 0) { vol[curZ].set(vol[curZ - 1]); voxCache = null; drawEdit(); }
      });
      document.getElementById('mCopyUp').addEventListener('click', () => {
        if (curZ < N - 1) { vol[curZ + 1].set(vol[curZ]); voxCache = null; setZ(curZ + 1); }
      });
      document.getElementById('mBtnClearLayer').addEventListener('click', () => {
        vol[curZ].fill(0); voxCache = null; drawEdit();
      });
      document.getElementById('mBtnNew').addEventListener('click', () => {
        if (!confirm('Descartar o modelo atual e começar um novo?')) return;
        newVolume(parseInt(document.getElementById('mSize').value, 10));
        drawEdit();
        if (typeof drawAll2d === 'function') drawAll2d();
      });
      document.getElementById('mSize').addEventListener('change', () => {
        const s = parseInt(document.getElementById('mSize').value, 10);
        if (s === N) return;
        if (!confirm('Mudar o tamanho descarta o modelo atual. Continuar?')) {
          document.getElementById('mSize').value = String(N);
          return;
        }
        newVolume(s);
        drawEdit();
        if (typeof drawAll2d === 'function') drawAll2d();
      });
      document.getElementById('mOnion').addEventListener('change', drawEdit);
      document.querySelectorAll('#mTools .tool-btn').forEach((b) => {
        b.addEventListener('click', () => {
          document.querySelectorAll('#mTools .tool-btn').forEach((o) => o.classList.remove('active'));
          b.classList.add('active');
          tool = b.dataset.mtool;
        });
      });

      // ---------- Preview 3D Real da Engine (Sprite-Stacking + silhueta 1px #3B2219 + aro curZ) ----------
      const PREV_LW = 100, PREV_LH = 100;
      let prevLowCv = null, prevLowCtx = null;
      let prevEntCv = null, prevEntCtx = null;
      let prevSilCv = null, prevSilCtx = null;
      let prevSheetModel = null;

      function ensurePreviewBuffers() {
        if (prevLowCv) return;
        const makeOff = (w, h) => {
          const cv = document.createElement('canvas');
          cv.width = w;
          cv.height = h;
          const cx = cv.getContext ? cv.getContext('2d') : null;
          if (cx) cx.imageSmoothingEnabled = false;
          return { cv, cx };
        };
        const low = makeOff(PREV_LW, PREV_LH);
        const ent = makeOff(PREV_LW, PREV_LH);
        const sil = makeOff(PREV_LW, PREV_LH);
        prevLowCv = low.cv; prevLowCtx = low.cx;
        prevEntCv = ent.cv; prevEntCtx = ent.cx;
        prevSilCv = sil.cv; prevSilCtx = sil.cx;
      }

      function rebuildPreviewModel() {
        const top = topUsedLayer();
        if (top < 0) {
          prevSheetModel = null;
          return null;
        }
        const count = top + 1;
        const shadedSlices = [];
        const shadedPal = ['rgba(0,0,0,0)'];
        const shadedMap = new Map();
        const getShadedIdx = (hex) => {
          const key = hex.toLowerCase();
          if (shadedMap.has(key)) return shadedMap.get(key);
          const idx = shadedPal.length;
          shadedPal.push(hex);
          shadedMap.set(key, idx);
          return idx;
        };
        const shColors = [];
        for (let z = 0; z < count; z++) {
          const layer = vol[z];
          const zFrac = count > 1 ? z / (count - 1) : 0.5;
          const zFactor = 0.90 + zFrac * 0.16;
          const rows = [];
          for (let y = 0; y < N; y++) {
            let rowStr = '';
            for (let x = 0; x < N; x++) {
              const v = layer[y * N + x];
              if (v > 0 && pal[v]) {
                const shHex = shadeHex(pal[v], zFactor);
                shColors.push({ z, y, x, shHex });
                rowStr += getShadedIdx(shHex).toString(36);
              } else {
                rowStr += '0';
              }
            }
            rows.push(rowStr);
          }
          shadedSlices.push(rows);
        }
        if (typeof buildSliceSheet === 'function' && shadedPal.length <= 36) {
          const built = buildSliceSheet(shadedSlices, shadedPal);
          if (built && built.count === count && built.sheet && built.w === N) {
            prevSheetModel = built;
            return prevSheetModel;
          }
        }
        const cv = document.createElement('canvas');
        cv.width = N * count;
        cv.height = N;
        const cx = cv.getContext ? cv.getContext('2d') : null;
        if (cx) {
          cx.imageSmoothingEnabled = false;
          for (let i = 0; i < shColors.length; i++) {
            const p = shColors[i];
            cx.fillStyle = p.shHex;
            cx.fillRect(p.z * N + p.x, p.y, 1, 1);
          }
        }
        prevSheetModel = { sheet: cv, count, w: N, h: N };
        return prevSheetModel;
      }

      function stampPreviewSlice(targetCtx, model, sz, lcx, sy, vScale, squash, rotAngle) {
        const ox = model.w / 2;
        const oy = model.h / 2;
        targetCtx.save();
        targetCtx.translate(lcx, sy);
        targetCtx.scale(vScale, squash * vScale);
        targetCtx.rotate(rotAngle);
        targetCtx.drawImage(model.sheet, sz * model.w, 0, model.w, model.h, -ox, -oy, model.w, model.h);
        targetCtx.restore();
      }

      function setPreviewZoom(z) {
        const v = Number.isFinite(z) ? z : 1.0;
        previewZoom = Math.max(0.4, Math.min(3.0, +v.toFixed(4)));
        const lbl = document.getElementById('mPrevZoomReset');
        if (lbl) lbl.textContent = `${Math.round(previewZoom * 100)}%`;
        return previewZoom;
      }

      prevCv.addEventListener('wheel', (e) => {
        if (e.preventDefault) e.preventDefault();
        if (e.deltaY < 0) setPreviewZoom(previewZoom * 1.12);
        else if (e.deltaY > 0) setPreviewZoom(previewZoom / 1.12);
      }, { passive: false });

      const mPrevZoomOut = document.getElementById('mPrevZoomOut');
      const mPrevZoomReset = document.getElementById('mPrevZoomReset');
      const mPrevZoomIn = document.getElementById('mPrevZoomIn');
      if (mPrevZoomOut) mPrevZoomOut.addEventListener('click', () => setPreviewZoom(previewZoom / 1.15));
      if (mPrevZoomReset) mPrevZoomReset.addEventListener('click', () => setPreviewZoom(1.0));
      if (mPrevZoomIn) mPrevZoomIn.addEventListener('click', () => setPreviewZoom(previewZoom * 1.15));

      function selectZFromPreviewEvent(e) {
        const r = prevCv.getBoundingClientRect();
        if (!r || !r.height) return curZ;
        const H = prevCv.height || 300;
        const py = ((e.clientY - r.top) / r.height) * H;
        const drawH = H * previewZoom;
        const dy = (H - drawH) / 2;
        const lBaseY = PREV_LH * 0.78;
        const vScale = 40 / N;
        const zStep = vScale * 0.95;
        const lyClick = ((py - dy) / drawH) * PREV_LH;
        const zPick = Math.max(0, Math.min(N - 1, Math.round((lBaseY - lyClick) / zStep)));
        setZ(zPick);
        say(`Camada Z=${zPick} selecionada pelo Preview 3D.`);
        return zPick;
      }

      prevCv.addEventListener('pointerdown', (e) => {
        if (e.altKey) {
          if (e.preventDefault) e.preventDefault();
          selectZFromPreviewEvent(e);
          return;
        }
        dragRotX = e.clientX;
        if (prevCv.setPointerCapture) prevCv.setPointerCapture(e.pointerId);
      });
      prevCv.addEventListener('dblclick', (e) => {
        if (e.preventDefault) e.preventDefault();
        selectZFromPreviewEvent(e);
      });
      prevCv.addEventListener('pointermove', (e) => {
        if (dragRotX === null) return;
        angle -= (e.clientX - dragRotX) * 0.012;
        dragRotX = e.clientX;
      });
      prevCv.addEventListener('pointerup', (e) => {
        dragRotX = null;
        if (e && e.pointerId !== undefined && prevCv.releasePointerCapture) {
          try { prevCv.releasePointerCapture(e.pointerId); } catch (_) {}
        }
      });
      prevCv.addEventListener('pointercancel', () => { dragRotX = null; });

      function buildVoxList() {
        const list = [];
        for (let z = 0; z < N; z++) {
          const layer = vol[z];
          for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
            const v = layer[y * N + x];
            if (v > 0) list.push({ x, y, z, v });
          }
        }
        voxCache = list;
        return list;
      }

      function drawPreview(now) {
        if (!view.classList.contains('show')) return;
        if (document.getElementById('mAutoSpin')?.checked && dragRotX === null) angle += 0.012;
        if (!voxCache) {
          buildVoxList();
          prevSheetModel = null;
        }
        const model = prevSheetModel || rebuildPreviewModel();
        ensurePreviewBuffers();

        const W = prevCv.width, H = prevCv.height;
        const squash = 0.5;
        const cosA = Math.cos(angle), sinA = Math.sin(angle);
        const lcx = PREV_LW / 2;
        const lBaseY = PREV_LH * 0.78;
        const vScale = 40 / N;
        const zStep = vScale * 0.95;

        const drawW = W * previewZoom;
        const drawH = H * previewZoom;
        const dx = (W - drawW) / 2;
        const dy = (H - drawH) / 2;
        const toScreenX = (lx) => dx + (lx / PREV_LW) * drawW;
        const toScreenY = (ly) => dy + (ly / PREV_LH) * drawH;
        const kScreen = vScale * (drawW / PREV_LW);

        pCtx.clearRect(0, 0, W, H);

        // Chão
        pCtx.fillStyle = 'rgba(255,255,255,0.05)';
        pCtx.beginPath();
        pCtx.ellipse(toScreenX(lcx), toScreenY(lBaseY + 2), N * kScreen * 0.60, N * kScreen * 0.60 * squash, 0, 0, Math.PI * 2);
        pCtx.fill();

        if (document.getElementById('mRefHuman')?.checked) {
          const hx = toScreenX(lcx) - N * kScreen * 0.78;
          const hyBot = toScreenY(lBaseY);
          const hPx = 28 * (zStep * (drawH / PREV_LH));
          const wPx = 8 * kScreen;
          pCtx.fillStyle = 'rgba(148,163,184,0.45)';
          pCtx.fillRect(hx, hyBot - hPx, wPx, hPx);
          pCtx.fillStyle = 'rgba(203,213,225,0.7)';
          pCtx.font = '10px sans-serif';
          pCtx.fillText('28u', hx, hyBot - hPx - 3);
        }

        if (model && prevEntCtx && prevSilCtx && prevLowCtx) {
          prevEntCtx.globalCompositeOperation = 'source-over';
          prevEntCtx.clearRect(0, 0, PREV_LW, PREV_LH);
          const totalPy = Math.max(1, Math.ceil(model.count * zStep));
          for (let pz = 0; pz < totalPy; pz++) {
            const sz = Math.min(model.count - 1, Math.floor(pz / zStep));
            stampPreviewSlice(prevEntCtx, model, sz, lcx, Math.round(lBaseY - pz), vScale, squash, angle);
          }

          // Contorno externo único 1px (#3B2219) por dilatação 4-vizinhos (idêntico à engine 04-renderer.js)
          prevSilCtx.globalCompositeOperation = 'source-over';
          prevSilCtx.clearRect(0, 0, PREV_LW, PREV_LH);
          prevSilCtx.drawImage(prevEntCv, 0, 0);
          prevSilCtx.globalCompositeOperation = 'source-in';
          prevSilCtx.fillStyle = '#3B2219';
          prevSilCtx.fillRect(0, 0, PREV_LW, PREV_LH);
          prevSilCtx.globalCompositeOperation = 'source-over';

          prevLowCtx.clearRect(0, 0, PREV_LW, PREV_LH);
          prevLowCtx.drawImage(prevSilCv, -1, 0);
          prevLowCtx.drawImage(prevSilCv, 1, 0);
          prevLowCtx.drawImage(prevSilCv, 0, -1);
          prevLowCtx.drawImage(prevSilCv, 0, 1);
          prevLowCtx.drawImage(prevEntCv, 0, 0);

          pCtx.imageSmoothingEnabled = false;
          pCtx.drawImage(prevLowCv, dx, dy, drawW, drawH);
        }

        // Aro luminoso da camada Z atual (plano rotacionado amarelo #FBBF24)
        const halfN = N / 2;
        const corners = [
          [-halfN, -halfN],
          [halfN, -halfN],
          [halfN, halfN],
          [-halfN, halfN]
        ];
        const ringPts = corners.map(([mx, my]) => {
          const rx = mx * cosA - my * sinA;
          const ry = mx * sinA + my * cosA;
          return {
            x: toScreenX(lcx + rx * vScale),
            y: toScreenY(lBaseY + ry * vScale * squash - curZ * zStep)
          };
        });
        pCtx.save();
        pCtx.fillStyle = 'rgba(251, 191, 36, 0.08)';
        pCtx.strokeStyle = '#FBBF24';
        pCtx.lineWidth = 1.5;
        if (typeof pCtx.setLineDash === 'function') pCtx.setLineDash([4, 3]);
        pCtx.beginPath();
        pCtx.moveTo(ringPts[0].x, ringPts[0].y);
        for (let i = 1; i < ringPts.length; i++) pCtx.lineTo(ringPts[i].x, ringPts[i].y);
        pCtx.closePath();
        pCtx.fill();
        pCtx.stroke();
        if (typeof pCtx.setLineDash === 'function') pCtx.setLineDash([]);
        pCtx.fillStyle = '#FDE68A';
        pCtx.font = 'bold 10px sans-serif';
        pCtx.fillText(`Z=${curZ}`, Math.min(W - 34, ringPts[2].x + 4), Math.max(12, Math.min(H - 6, ringPts[2].y)));
        pCtx.restore();
      }
      (function loop(now) {
        drawPreview(now);
        if (typeof requestAnimationFrame === 'function') requestAnimationFrame(loop);
      })();

      // ---------- Biblioteca / import / export ----------
      function topUsedLayer() {
        for (let z = N - 1; z >= 0; z--) {
          const layer = vol[z];
          for (let i = 0; i < layer.length; i++) if (layer[i] > 0) return z;
        }
        return -1;
      }

      function currentSlices() {
        const top = topUsedLayer();
        if (top < 0) return null;
        const slices = [];
        for (let z = 0; z <= top; z++) {
          const rows = [];
          for (let y = 0; y < N; y++) {
            let s = '';
            for (let x = 0; x < N; x++) s += vol[z][y * N + x].toString(36);
            rows.push(s);
          }
          slices.push(rows);
        }
        return slices;
      }

      function slug(name) {
        return String(name || 'modelo')
          .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
          .toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '') || 'modelo';
      }

      const KIND_ICONS = {
        decor: '🧱',
        solid: '🧊',
        destructible: '🪓',
        pickable: '🎒',
        foliage: '🌿',
        fire: '🔥',
        avatar: '🧍'
      };

      function syncAvatarOption(a, isAvatar) {
        const avSel = document.getElementById('avatarSelect');
        if (!avSel) return;
        let opt = avSel.querySelector ? avSel.querySelector(`option[value="${a.key}"]`) : null;
        if (!opt && avSel.options) {
          for (let oi = 0; oi < avSel.options.length; oi++) {
            if (avSel.options[oi] && avSel.options[oi].value === a.key) { opt = avSel.options[oi]; break; }
          }
        }
        if (isAvatar) {
          if (!opt && typeof document.createElement === 'function') {
            opt = document.createElement('option');
            opt.value = a.key;
            if (avSel.appendChild) avSel.appendChild(opt);
            else if (Array.isArray(avSel.options)) avSel.options.push(opt);
          }
          if (opt) opt.textContent = `🧍 ${a.name}`;
        } else if (opt) {
          if (opt.remove) opt.remove();
          else if (opt.parentNode && opt.parentNode.removeChild) opt.parentNode.removeChild(opt);
        }
      }

      function addAssetButton(a) {
        const grid = document.getElementById('customAssetGrid');
        if (!grid) return;
        document.getElementById('customAssetEmpty').style.display = 'none';
        const kind = a.kind || a.category || (a.solid ? 'solid' : 'decor');
        const label = `${KIND_ICONS[kind] || '🧱'} ${a.name}`;
        const existing = grid.querySelector(`[data-tool="prop_${a.key}"]`);
        if (existing) {
          existing.textContent = label;
          return;
        }
        const b = document.createElement('button');
        b.className = 'tool-btn';
        b.dataset.tool = 'prop_' + a.key;
        b.textContent = label;
        grid.appendChild(b);
      }

      function registerAsset(a) {
        const kind = a.kind || a.category || (a.solid ? 'solid' : 'decor');
        const model = buildSliceSheet(a.slices, a.pal);
        propModels[a.key] = model;
        if (typeof window !== 'undefined') {
          window.customAvatarModels = window.customAvatarModels || {};
          if (kind === 'avatar') window.customAvatarModels[a.key] = model;
          else delete window.customAvatarModels[a.key];
        }
        syncAvatarOption(a, kind === 'avatar');
        const colors = (a.pal || []).filter(c => c && !c.startsWith('rgba')).slice(0, 4);
        const leafColors = colors.length ? colors : ['#6BBF59', '#3F8F3A'];
        const isSolid = kind === 'solid' || kind === 'destructible' || kind === 'fire';
        PROP_COLLIDER_META[a.key] = {
          mode: isSolid ? 'solid' : 'none',
          r: Math.max(3, a.size * 0.3),
          h: a.slices.length,
          shadowR: Math.max(3, a.size * (isSolid ? 0.35 : 0.25)),
          pickable: kind === 'pickable',
          isFire: kind === 'fire'
        };
        if (kind === 'destructible' && typeof DESTRUCTIBLE_META !== 'undefined') {
          DESTRUCTIBLE_META[a.key] = {
            mode: 'crumble',
            hp: Math.max(1, parseInt(a.hp, 10) || 3),
            zCut: Math.max(1, Math.floor(a.slices.length * 0.25)),
            drops: a.drops !== undefined ? a.drops : 2,
            dropKey: a.dropKey || 'stone_chunk',
            bestTool: 'none',
            colors: leafColors
          };
        } else if (typeof DESTRUCTIBLE_META !== 'undefined') {
          delete DESTRUCTIBLE_META[a.key];
        }
        if (kind === 'foliage' && typeof FOLIAGE_META !== 'undefined') {
          FOLIAGE_META[a.key] = {
            isFoliage: true,
            rigidity: 0.22,
            windScale: 3.0,
            pushRadius: Math.max(10, a.size * 0.6),
            pushStrength: 6.0,
            leafColors
          };
        } else if (typeof FOLIAGE_META !== 'undefined') {
          delete FOLIAGE_META[a.key];
        }
        const saved = { ...a, kind, category: kind, solid: isSolid };
        const i = customAssets.findIndex((x) => x.key === a.key);
        if (i >= 0) customAssets[i] = saved; else customAssets.push(saved);
        addAssetButton(saved);
      }

      const kindSel = document.getElementById('mKind');
      const destrOptsEl = document.getElementById('mDestrOpts');
      if (kindSel && destrOptsEl) {
        kindSel.addEventListener('change', () => {
          destrOptsEl.style.display = kindSel.value === 'destructible' ? 'flex' : 'none';
        });
      }

      document.getElementById('mBtnSave').addEventListener('click', () => {
        const slices = currentSlices();
        if (!slices) { say('Modelo vazio: pinte alguma coisa antes de salvar.', false); return; }
        const name = document.getElementById('mName').value.trim() || 'modelo';
        const key = 'custom_' + slug(name);
        const kind = kindSel.value;
        const hp = parseInt(document.getElementById('mHp')?.value || '3', 10) || 3;
        const dropKey = document.getElementById('mDropKey')?.value || 'stone_chunk';
        registerAsset({
          key, name, size: N, pal: pal.slice(), slices,
          kind, solid: kind === 'solid' || kind === 'destructible' || kind === 'fire',
          hp, drops: 2, dropKey
        });
        say(`"${name}" (${kind}) salvo na biblioteca (${slices.length} camadas). ${kind === 'avatar' ? 'Selecione em Avatar de Teste na aba 🌍 Mundo!' : 'Use na aba 🌍 Mundo → Meus Modelos.'}`);
      });

      // ---------- Geradores Procedurais (100% SDF + mulberry32) ----------
      function makeRng(seed) {
        if (typeof mulberry32 === 'function') return mulberry32(seed >>> 0);
        let t = seed >>> 0;
        return () => {
          t = (t + 0x6D2B79F5) | 0;
          let r = Math.imul(t ^ (t >>> 15), 1 | t);
          r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
          return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
        };
      }

      function applyPresetAndKind(presetKey, kindVal, suggestedName, dropKey) {
        const nextPal = PAL_PRESETS[presetKey] || DEFAULT_PAL;
        pal = nextPal.slice();
        if (palPresetEl) palPresetEl.value = presetKey;
        if (kindSel) kindSel.value = kindVal;
        if (destrOptsEl) destrOptsEl.style.display = kindVal === 'destructible' ? 'flex' : 'none';
        if (dropKey && document.getElementById('mDropKey')) document.getElementById('mDropKey').value = dropKey;
        if (suggestedName && document.getElementById('mName')) document.getElementById('mName').value = suggestedName;
        curColor = Math.min(Math.max(1, curColor), pal.length - 1);
        const colEl = document.getElementById('mColor');
        if (colEl && pal[curColor]) colEl.value = pal[curColor];
      }

      const bindRangeLabel = (id, valId, suffix = '') => {
        const el = document.getElementById(id);
        const out = document.getElementById(valId);
        if (!el) return;
        const sync = () => { if (out) out.textContent = String(el.value) + suffix; };
        el.addEventListener('input', sync);
        el.addEventListener('change', sync);
        sync();
      };

      function centerAndGroundVolume() {
        let minX = N, maxX = -1, minY = N, maxY = -1, minZ = N, maxZ = -1;
        for (let z = 0; z < N; z++) {
          const layer = vol[z];
          for (let y = 0; y < N; y++) {
            for (let x = 0; x < N; x++) {
              if (layer[y * N + x] > 0) {
                if (x < minX) minX = x; if (x > maxX) maxX = x;
                if (y < minY) minY = y; if (y > maxY) maxY = y;
                if (z < minZ) minZ = z; if (z > maxZ) maxZ = z;
              }
            }
          }
        }
        if (maxZ < 0) return;
        const shiftX = Math.round((N - 1) / 2 - (minX + maxX) / 2);
        const shiftY = Math.round((N - 1) / 2 - (minY + maxY) / 2);
        const shiftZ = -minZ;
        if (shiftX === 0 && shiftY === 0 && shiftZ === 0) return;
        const nextVol = Array.from({ length: N }, () => new Uint8Array(N * N));
        for (let z = minZ; z <= maxZ; z++) {
          const nz = z + shiftZ;
          if (nz < 0 || nz >= N) continue;
          const src = vol[z], dst = nextVol[nz];
          for (let y = minY; y <= maxY; y++) {
            const ny = y + shiftY;
            if (ny < 0 || ny >= N) continue;
            for (let x = minX; x <= maxX; x++) {
              const nx = x + shiftX;
              if (nx < 0 || nx >= N) continue;
              const v = src[y * N + x];
              if (v > 0) dst[ny * N + nx] = v;
            }
          }
        }
        for (let z = 0; z < N; z++) vol[z].set(nextVol[z]);
      }

      function setUiKindAndName(kindVal, suggestedName, dropKey) {
        if (kindSel) kindSel.value = kindVal;
        if (destrOptsEl) destrOptsEl.style.display = kindVal === 'destructible' ? 'flex' : 'none';
        if (dropKey && document.getElementById('mDropKey')) document.getElementById('mDropKey').value = dropKey;
        if (suggestedName && document.getElementById('mName')) document.getElementById('mName').value = suggestedName;
        curColor = Math.min(Math.max(1, curColor), pal.length - 1);
        const colEl = document.getElementById('mColor');
        if (colEl && pal[curColor]) colEl.value = pal[curColor];
      }

      // ---------- Construtor Modular de Personagens, Bichos (2 e 4 patas, Dino, Lagarto) & Equips Soltos ----------
      bindRangeLabel('mCharLegH', 'mCharLegHVal');
      bindRangeLabel('mCharTorsoW', 'mCharTorsoWVal');
      bindRangeLabel('mCharHeadS', 'mCharHeadSVal');

      let charSeed = 1;
      function getCharUiOpts() {
        return {
          charType: document.getElementById('mCharType')?.value || 'humanoid',
          legH: parseInt(document.getElementById('mCharLegH')?.value || '6', 10) || 6,
          torsoW: parseInt(document.getElementById('mCharTorsoW')?.value || '6', 10) || 6,
          headS: parseInt(document.getElementById('mCharHeadS')?.value || '6', 10) || 6,
          partMode: document.getElementById('mCharPartMode')?.value || 'full',
          headStyle: document.getElementById('mCharHead')?.value || 'short_hair',
          hatStyle: document.getElementById('mCharHat')?.value || 'none',
          torsoStyle: document.getElementById('mCharTorso')?.value || 'shirt',
          legsStyle: document.getElementById('mCharLegs')?.value || 'pants',
          backStyle: document.getElementById('mCharBack')?.value || 'none',
          rhandStyle: document.getElementById('mCharRHand')?.value || 'none',
          lhandStyle: document.getElementById('mCharLHand')?.value || 'none',
          colSkin: document.getElementById('mCharColSkin')?.value || '#F2C9A0',
          colHair: document.getElementById('mCharColHair')?.value || '#5B3A22',
          colShirt: document.getElementById('mCharColShirt')?.value || '#3B82F6',
          colPants: document.getElementById('mCharColPants')?.value || '#374151',
          colArmor: document.getElementById('mCharColArmor')?.value || '#9CA3AF',
          colEquip: document.getElementById('mCharColEquip')?.value || '#F59E0B'
        };
      }

      function generateCharacter(arg1 = {}, arg2, arg3) {
        const ui = getCharUiOpts();
        let opts, seed;
        if (typeof arg1 === 'string') {
          opts = { ...ui, charType: arg1, headStyle: arg2 ?? ui.headStyle };
          seed = arg3 ?? charSeed;
        } else {
          opts = { ...ui, ...(arg1 || {}) };
          seed = arg2 ?? charSeed;
        }
        const rng = makeRng(seed);
        const charType = String(opts.charType || 'humanoid');
        const partMode = String(opts.partMode || 'full');
        const legH = Math.max(3, Math.min(9, parseInt(opts.legH, 10) || 6));
        const torsoW = Math.max(4, Math.min(10, parseInt(opts.torsoW, 10) || 6));
        const headS = Math.max(4, Math.min(10, parseInt(opts.headS, 10) || 6));

        const headStyle = String(opts.headStyle || 'short_hair');
        const hatStyle = String(opts.hatStyle || 'none');
        const torsoStyle = String(opts.torsoStyle || 'shirt');
        const legsStyle = String(opts.legsStyle || 'pants');
        const backStyle = String(opts.backStyle || 'none');
        const rhandStyle = String(opts.rhandStyle || 'none');
        const lhandStyle = String(opts.lhandStyle || 'none');

        const cSkin = opts.colSkin || '#F2C9A0';
        const cHair = opts.colHair || '#5B3A22';
        const cShirt = opts.colShirt || '#3B82F6';
        const cPants = opts.colPants || '#374151';
        const cArmor = opts.colArmor || '#9CA3AF';
        const cEquip = opts.colEquip || '#F59E0B';

        // Paleta modular sombreada (claro/médio/escuro por parte)
        // 1..3 Skin | 4..6 Hair | 7..9 Shirt | 10..12 Pants | 13..15 Armor | 16..18 Equip | 19 Eye | 20 White | 21 Boots/Leather | 22 Wood | 23 Glow/Gem
        pal = [
          'rgba(0,0,0,0)',
          shadeHex(cSkin, 0.78), cSkin, shadeHex(cSkin, 1.18),
          shadeHex(cHair, 0.75), cHair, shadeHex(cHair, 1.22),
          shadeHex(cShirt, 0.76), cShirt, shadeHex(cShirt, 1.20),
          shadeHex(cPants, 0.76), cPants, shadeHex(cPants, 1.22),
          shadeHex(cArmor, 0.75), cArmor, shadeHex(cArmor, 1.24),
          shadeHex(cEquip, 0.76), cEquip, shadeHex(cEquip, 1.25),
          '#1B1B1B', '#FFFFFF', '#2A2018', '#7A4E2D', '#38BDF8'
        ];
        if (palPresetEl) palPresetEl.value = 'character';

        const SKIN_D = 1, SKIN = 2, SKIN_L = 3;
        const HAIR_D = 4, HAIR = 5, HAIR_L = 6;
        const SHIRT_D = 7, SHIRT = 8, SHIRT_L = 9;
        const PANTS_D = 10, PANTS = 11, PANTS_L = 12;
        const ARMOR_D = 13, ARMOR = 14, ARMOR_L = 15;
        const EQUIP_D = 16, EQUIP = 17, EQUIP_L = 18;
        const EYE = 19, WHITE = 20, BOOT = 21, WOOD = 22, GLOW = 23;

        for (let z = 0; z < N; z++) vol[z].fill(0);
        const s = N / 24;
        const cx = (N - 1) / 2;
        const cy = (N - 1) / 2;

        const putL = (lx, ly, lz, col) => {
          if (!col) return;
          const ix = Math.round(cx + lx * s);
          const iy = Math.round(cy + ly * s);
          const iz = Math.round(lz * s);
          if (ix < 0 || ix >= N || iy < 0 || iy >= N || iz < 0 || iz >= N) return;
          vol[iz][iy * N + ix] = col;
        };
        const boxL = (x0, x1, y0, y1, z0, z1, fn) => {
          const ix0 = Math.max(0, Math.floor(cx + x0 * s)), ix1 = Math.min(N - 1, Math.ceil(cx + x1 * s));
          const iy0 = Math.max(0, Math.floor(cy + y0 * s)), iy1 = Math.min(N - 1, Math.ceil(cy + y1 * s));
          const iz0 = Math.max(0, Math.floor(z0 * s)), iz1 = Math.min(N - 1, Math.ceil(z1 * s));
          for (let iz = iz0; iz <= iz1; iz++) {
            const lz = iz / s;
            for (let iy = iy0; iy <= iy1; iy++) {
              const ly = (iy - cy) / s;
              for (let ix = ix0; ix <= ix1; ix++) {
                const lx = (ix - cx) / s;
                if (lx >= x0 - 0.15 && lx <= x1 + 0.15 && ly >= y0 - 0.15 && ly <= y1 + 0.15 && lz >= z0 - 0.15 && lz <= z1 + 0.15) {
                  const v = typeof fn === 'function' ? fn(lx, ly, lz) : fn;
                  if (v > 0) vol[iz][iy * N + ix] = v;
                }
              }
            }
          }
        };
        const ellipL = (ox, oy, oz, rx, ry, rz, fn) => {
          const ix0 = Math.max(0, Math.floor(cx + (ox - rx) * s)), ix1 = Math.min(N - 1, Math.ceil(cx + (ox + rx) * s));
          const iy0 = Math.max(0, Math.floor(cy + (oy - ry) * s)), iy1 = Math.min(N - 1, Math.ceil(cy + (oy + ry) * s));
          const iz0 = Math.max(0, Math.floor((oz - rz) * s)), iz1 = Math.min(N - 1, Math.ceil((oz + rz) * s));
          for (let iz = iz0; iz <= iz1; iz++) {
            const lz = iz / s;
            for (let iy = iy0; iy <= iy1; iy++) {
              const ly = (iy - cy) / s;
              for (let ix = ix0; ix <= ix1; ix++) {
                const lx = (ix - cx) / s;
                const d = ((lx - ox) / rx) ** 2 + ((ly - oy) / ry) ** 2 + ((lz - oz) / rz) ** 2;
                if (d <= 1.04) {
                  const v = typeof fn === 'function' ? fn(lx, ly, lz, d) : fn;
                  if (v > 0) vol[iz][iy * N + ix] = v;
                }
              }
            }
          }
        };

        // Âncoras anatômicas parametrizadas por arquétipo e sliders de forma
        const rawTorsoHalfW = torsoW * 0.56;
        const isDwarf = charType === 'dwarf';
        const isChibi = charType === 'chibi';
        const isBipedBeast = charType === 'biped_beast';
        const isLizard = charType === 'lizard';
        const isQuad = charType === 'quadruped';
        const isMonster = charType === 'monster';

        const legTopRaw = isChibi ? Math.max(2.5, legH * 0.65)
          : (isDwarf ? Math.max(2.5, legH * 0.72)
          : (isLizard ? Math.max(1.8, legH * 0.42)
          : (isQuad ? Math.max(3.0, legH * 0.78)
          : (isBipedBeast ? Math.max(2.8, legH * 0.75) : legH))));
        const torsoHRaw = isChibi ? 4.8 : (isDwarf ? 6.0 : (isBipedBeast ? 5.8 : (isLizard ? 3.8 : (isQuad ? 4.8 : (isMonster ? 8.2 : 6.4)))));
        const headHRaw = isChibi ? headS * 1.32 : (isBipedBeast ? headS * 0.85 : (isLizard ? headS * 0.68 : (isQuad ? headS * 0.88 : headS * 0.94)));
        const totalRaw = legTopRaw + torsoHRaw + headHRaw;
        const vFit = totalRaw > 20.5 ? 20.5 / totalRaw : 1.0;

        const legTop = legTopRaw * vFit;
        const torsoH = torsoHRaw * vFit;
        const torsoTop = legTop + torsoH;
        const headH = headHRaw * vFit;
        let headTopZ = Math.min(22.2, torsoTop + headH);
        let headCenterZ = (torsoTop + headTopZ) * 0.5;

        const torsoHalfW = rawTorsoHalfW * (isDwarf ? 1.18 : (isMonster ? 1.32 : (isChibi ? 0.92 : 1.0)));
        const torsoDepth = isDwarf ? 2.4 : (isMonster ? 3.2 : (isBipedBeast ? 3.4 : (isLizard ? 4.8 : (isQuad ? 5.2 : 2.0))));
        const legSep = Math.max(1.6, torsoHalfW * 0.62);
        const legR = isDwarf ? 1.35 : (isMonster ? 1.7 : (isBipedBeast ? 0.95 : 1.12));

        let headCenterY = 0;
        let headRx = Math.min(5.8, headS * (isChibi ? 0.78 : (isMonster ? 0.62 : (isLizard ? 0.44 : 0.52))));
        let headRy = Math.min(4.8, headS * (isChibi ? 0.68 : (isLizard ? 0.60 : 0.48)));
        if (isBipedBeast) {
          headCenterY = 2.6;
          headRx = Math.min(4.4, headS * 0.52);
          headRy = Math.min(4.2, headS * 0.50);
        } else if (isLizard) {
          headCenterY = 4.6;
          headCenterZ = legTop + torsoH * 0.85;
          headTopZ = Math.min(22.2, headCenterZ + headH * 0.52);
        } else if (isQuad) {
          headCenterY = 4.2;
        } else if (isMonster) {
          headCenterY = 0.4;
        }
        const headBackY = headCenterY - headRy;
        const headFrontY = headCenterY + headRy;

        const armX = torsoHalfW + (isMonster ? 1.6 : 1.0);
        const handX = isBipedBeast ? torsoHalfW + 1.0 : (isQuad || isLizard ? torsoHalfW + 1.2 : armX + 0.3);
        const handY = isBipedBeast ? 2.4 : (isQuad || isLizard ? 3.2 : 1.4);
        const handZ = isBipedBeast ? legTop + 2.2 : (isQuad || isLizard ? legTop : legTop + 1.5);

        const drawBody = (partMode === 'full' || partMode === 'body_only');
        const withEquips = (partMode === 'full');
        const emptyOutfit = (torsoStyle === 'none' && legsStyle === 'none');
        const effTorso = withEquips ? torsoStyle : (partMode === 'outfit_only' ? (emptyOutfit ? 'armor' : torsoStyle) : 'none');
        const effLegs = withEquips ? legsStyle : (partMode === 'outfit_only' ? (emptyOutfit ? 'greaves' : legsStyle) : 'none');
        const effHead = withEquips ? headStyle : (partMode === 'headgear_only' && hatStyle === 'none' ? headStyle : 'none');
        const effHat = withEquips ? hatStyle : (partMode === 'headgear_only' ? (hatStyle === 'none' && headStyle === 'none' ? 'helmet' : hatStyle) : 'none');
        const effBack = withEquips ? backStyle : (partMode === 'back_only' ? (backStyle === 'none' ? 'cape' : backStyle) : 'none');
        const effRHand = withEquips ? rhandStyle : (partMode === 'rhand_only' ? (rhandStyle === 'none' ? 'sword' : rhandStyle) : 'none');
        const effLHand = withEquips ? lhandStyle : (partMode === 'lhand_only' ? (lhandStyle === 'none' ? 'shield' : lhandStyle) : 'none');

        const drawOutfitEnabled = (partMode === 'full' || partMode === 'outfit_only');

        // --- 1. Corpo Base & Roupas (Pernas + Tronco + Braços + Cabeça) ---
        if (drawBody || partMode === 'outfit_only') {
          if (isBipedBeast && partMode !== 'outfit_only') {
            // Bicho 2 Patas (Galinha / Dino): 2 patas com garras, corpo inclinado, asas/bracinhos, cauda, pescoço e bico/focinho
            if (drawBody) {
              for (const sx of [-1, 1]) {
                const px = sx * legSep;
                // 3 dedos com garras na frente
                boxL(px - 1.1, px + 1.1, -0.4, 2.4, 0, 0.9, (lx, ly) => (Math.abs(lx - px) < 0.45 || Math.abs(Math.abs(lx - px) - 0.85) < 0.35 || ly < 0.8) ? EQUIP : 0);
                // Canela bípede inclinada
                for (let lz = 0.8; lz <= legTop; lz += 0.5) {
                  const ky = 0.2 - (lz / legTop) * 1.0;
                  ellipL(px, ky, lz, 0.75, 0.8, 0.65, lz < 1.8 ? EQUIP_D : EQUIP);
                }
                // Coxa fofa
                ellipL(px, -0.8, legTop + 0.5, 1.5, 1.7, 1.3, SKIN_D);
              }
              // Corpo inclinado (+ly frente mais alta, -ly trás mais baixa)
              ellipL(0, 0.4, legTop + torsoH * 0.48, torsoHalfW, torsoDepth, torsoH * 0.52, (lx, ly, lz) => {
                if (effTorso !== 'none' && lz > legTop + 1.4 && Math.abs(lx) <= torsoHalfW * 0.85) {
                  if (effTorso === 'armor') return (Math.abs(lx) < 1.2 && ly > 1.0) ? EQUIP : ARMOR;
                  return SHIRT;
                }
                if (lz < legTop + 1.4 && Math.abs(lx) < torsoHalfW * 0.6) return SKIN_L;
                return ly > 1.2 && lz > legTop + 2.0 ? SKIN_L : SKIN;
              });
              // Asinhas / Bracinhos curtos nas laterais
              for (const sx of [-1, 1]) {
                ellipL(sx * (torsoHalfW + 0.5), 0.6, legTop + torsoH * 0.52, 0.9, 1.9, 1.2, effTorso === 'armor' ? ARMOR_L : SKIN_D);
              }
              // Cauda traseira inclinada para trás/cima
              for (let t = 0; t <= 1; t += 0.08) {
                const ty = -2.2 - t * 4.8;
                const tz = legTop + 2.2 + t * 3.0;
                const tr = (1.6 - t * 1.1) * (torsoW / 6);
                ellipL(0, ty, tz, Math.max(0.5, tr), 1.0, Math.max(0.5, tr), t > 0.7 ? SKIN_L : SKIN_D);
              }
              // Pescoço & Cabeça avançada (+ly)
              ellipL(0, 2.0, torsoTop - 0.4, 1.9, 2.0, 1.8, SKIN);
              ellipL(0, headCenterY, headCenterZ, headRx, headRy, headH * 0.52, (lx, ly, lz) => {
                if (lz >= headCenterZ - 0.3 && lz <= headCenterZ + 1.1 && Math.abs(Math.abs(lx) - headRx * 0.68) <= 0.65 && ly >= headCenterY + 0.6 && ly <= headCenterY + headRy * 0.85) {
                  return lz > headCenterZ + 0.45 && Math.abs(lx) > headRx * 0.6 ? WHITE : EYE;
                }
                return lz < headCenterZ - headH * 0.25 ? SKIN_D : SKIN;
              });
              // Bico / Focinho Dino-Galinha
              for (let t = 0; t <= 1; t += 0.14) {
                const by = headFrontY - 0.3 + t * 2.4;
                const bw = Math.max(0.45, 1.35 * (1 - t * 0.65));
                const bh = Math.max(0.4, 0.95 * (1 - t * 0.55));
                ellipL(0, by, headCenterZ - 0.4, bw, 0.7, bh, t > 0.6 ? EQUIP_D : EQUIP);
              }
              // Barbela / Crista sutil padrão quando não há cabelo/elmo
              if (effHead === 'none' || effHead === 'mohawk') {
                boxL(-0.55, 0.55, headCenterY - 1.2, headFrontY - 0.2, headTopZ - 0.3, Math.min(23.5, headTopZ + 1.8), (lx, ly, lz) => (Math.sin(ly * 1.6) > -0.2 || lz < headTopZ + 0.6) ? HAIR : 0);
              }
            }
          } else if (isLizard && partMode !== 'outfit_only') {
            // Lagarto / Réptil: 4 patas abertas com garras, corpo reptiliano baixo, cauda longa curvada, focinho alongado e escamas dorsais
            if (drawBody) {
              const splay = torsoHalfW + 1.3;
              for (const sx of [-1, 1]) {
                for (const py of [2.8, -2.8]) {
                  // Pata aberta com garras
                  boxL(sx * (splay - 0.6), sx * (splay + 1.2), py - 0.8, py + 1.4, 0, 1.0, (lx, ly) => (ly > py + 0.6 && Math.abs(lx - sx * splay) > 0.3) ? EQUIP_L : SKIN_D);
                  boxL(sx * (torsoHalfW - 0.3), sx * (splay + 0.3), py - 0.8, py + 0.8, 0.8, legTop + 1.2, SKIN_D);
                }
              }
              // Corpo alongado e barriga clara
              ellipL(0, 0, legTop + torsoH * 0.52, torsoHalfW * 0.92, torsoDepth, torsoH * 0.56, (lx, ly, lz) => {
                if (lz < legTop + 1.2 && Math.abs(lx) < torsoHalfW * 0.58) return SKIN_L;
                if (effTorso !== 'none' && lz > legTop + torsoH * 0.35 && Math.abs(ly) < torsoDepth * 0.55) {
                  return effTorso === 'armor' ? ARMOR : SHIRT;
                }
                return SKIN;
              });
              // Escamas / crista dorsal ao longo do dorso
              for (let ly = -3.2; ly <= 3.6; ly += 1.4) {
                boxL(-0.55, 0.55, ly - 0.35, ly + 0.35, torsoTop - 0.3, torsoTop + 0.8, HAIR);
              }
              // Cauda longa sinuosa em S (-ly)
              for (let t = 0; t <= 1; t += 0.04) {
                const ty = -3.6 - t * 6.8;
                const tx = Math.sin(t * Math.PI * 1.4) * 1.8;
                const tz = legTop + 1.6 - t * 0.7 + Math.sin(t * Math.PI) * 0.6;
                const tr = Math.max(0.45, 1.85 * (1 - t * 0.78));
                ellipL(tx, ty, tz, tr, 0.85, tr * 0.85, (lx, ly, lz) => (Math.abs(lx - tx) < 0.45 && lz > tz + tr * 0.45 && (Math.round(t * 14) & 1) === 0) ? HAIR : (t > 0.65 ? SKIN_D : SKIN));
              }
              // Pescoço conectando tronco à cabeça reptiliana
              ellipL(0, 2.8, legTop + torsoH * 0.68, torsoHalfW * 0.52, 2.0, torsoH * 0.46, (lx, ly, lz) => lz < legTop + 1.5 ? SKIN_L : SKIN);
              // Cabeça reptiliana + focinho alongado
              ellipL(0, headCenterY, headCenterZ, headRx, headRy * 1.05, headH * 0.52, (lx, ly, lz) => {
                if (lz >= headCenterZ - 0.1 && lz <= headCenterZ + 1.0 && Math.abs(Math.abs(lx) - headRx * 0.75) <= 0.55 && ly >= headCenterY - 0.2 && ly <= headCenterY + 1.2) {
                  return Math.abs(lx) > headRx * 0.7 ? EQUIP_L : EYE;
                }
                return lz < headCenterZ - 0.5 ? SKIN_L : SKIN;
              });
              for (let t = 0; t <= 1; t += 0.12) {
                const sy = Math.min(10.6, headFrontY - 0.4 + t * 2.5);
                const sw = Math.max(0.65, headRx * 0.76 * (1 - t * 0.5));
                const sh = Math.max(0.55, headH * 0.36 * (1 - t * 0.4));
                ellipL(0, sy, headCenterZ - 0.2, sw, 0.8, sh, (lx, ly, lz) => (t > 0.78 && Math.abs(Math.abs(lx) - 0.5) < 0.35 && lz > headCenterZ) ? SKIN_D : SKIN);
              }
            }
          } else if (isQuad && partMode !== 'outfit_only') {
            // Bicho 4 Patas (Gato / Lobo)
            if (drawBody) {
              for (const sx of [-1, 1]) {
                for (const py of [3.5, -4.0]) {
                  boxL(sx * legSep - 1.1, sx * legSep + 1.1, py - 1.1, py + 1.1, 0, legTop, (lx, ly, lz) => lz < 1.2 ? SKIN_L : SKIN_D);
                }
              }
              ellipL(0, -0.4, legTop + torsoH * 0.45, torsoHalfW * 0.9, torsoDepth, torsoH * 0.55, (lx, ly, lz) => (lz < legTop + 1.2 && Math.abs(lx) < torsoHalfW * 0.5) ? SKIN_L : SKIN);
              // Cauda curvada
              for (let t = 0; t <= 1; t += 0.08) {
                const ty = -5.0 - t * 4.4;
                const tz = legTop + 2.2 + t * 3.8;
                ellipL(0, ty, tz, 0.95, 0.95, 0.95, t > 0.75 ? SKIN_L : SKIN);
              }
              ellipL(0, headCenterY, headCenterZ, headRx, headRy, headH * 0.55, (lx, ly, lz) => {
                if (lz >= headCenterZ - 0.2 && lz <= headCenterZ + 1.1 && ly >= headFrontY - 1.2 && Math.abs(Math.abs(lx) - headRx * 0.45) <= 0.6) return EYE;
                return SKIN;
              });
              ellipL(0, headFrontY + 0.6, headCenterZ - 0.7, headRx * 0.52, 1.3, 1.1, (lx, ly, lz) => (ly >= headFrontY + 1.3 && lz >= headCenterZ - 0.4 && Math.abs(lx) <= 0.65) ? EYE : SKIN_L);
            }
          } else {
            // Bípedes verticais: humanoid, chibi, dwarf, monster
            // Pernas / Calças / Grevas / Saia
            if (effLegs === 'robe' && drawOutfitEnabled) {
              for (let lz = 0.8; lz < legTop + 0.6; lz += 0.5) {
                const frac = lz / Math.max(1, legTop);
                const rX = torsoHalfW * (1.18 - frac * 0.22);
                const rY = torsoDepth * (1.18 - frac * 0.2);
                ellipL(0, 0, lz, rX, rY, 0.6, (lx, ly) => Math.abs(lx) < 0.8 && ly > rY * 0.6 ? EQUIP : (lz < 1.6 ? PANTS_D : PANTS));
              }
              if (drawBody) {
                for (const sx of [-1, 1]) boxL(sx * legSep - legR, sx * legSep + legR, -1.2, 1.8, 0, 1.3, BOOT);
              }
            } else {
              for (const sx of [-1, 1]) {
                const px = sx * legSep;
                if (drawBody) {
                  boxL(px - legR, px + legR, -1.3, 2.0, 0, Math.min(1.8, legTop * 0.35), isMonster ? SKIN_D : BOOT);
                  boxL(px - legR * 0.9, px + legR * 0.9, -1.2, 1.2, Math.min(1.8, legTop * 0.35), legTop, isMonster ? SKIN_D : SKIN);
                }
                if (drawOutfitEnabled && effLegs !== 'none') {
                  const zStart = effLegs === 'shorts' ? legTop * 0.45 : 0;
                  const colLeg = effLegs === 'greaves' ? ARMOR : PANTS;
                  const colLegD = effLegs === 'greaves' ? ARMOR_D : PANTS_D;
                  const colLegL = effLegs === 'greaves' ? ARMOR_L : PANTS_L;
                  boxL(px - legR * 1.05, px + legR * 1.05, -1.35, 1.45, zStart, legTop + 0.2, (lx, ly, lz) => {
                    if (lz < 1.6) return effLegs === 'greaves' ? ARMOR_D : BOOT;
                    if (effLegs === 'greaves' && ly > 0.7 && Math.abs(lz - legTop * 0.65) < 0.7) return ARMOR_L;
                    return lx * sx > 0 ? colLegD : colLeg;
                  });
                }
              }
            }

            // Tronco + Braços
            if (drawBody) {
              ellipL(0, 0, legTop + torsoH * 0.5, torsoHalfW, torsoDepth, torsoH * 0.54, (lx, ly, lz) => {
                if (isMonster && Math.abs(lx) <= 1.3 && ly > torsoDepth * 0.55 && Math.abs(lz - (legTop + torsoH * 0.5)) <= 1.3) return EQUIP;
                return lz < legTop + 1.2 ? SKIN_D : SKIN;
              });
              // Braços
              for (const sx of [-1, 1]) {
                const ax = sx * armX;
                const aR = isMonster ? 1.35 : (isDwarf ? 1.05 : 0.85);
                boxL(ax - aR, ax + aR, -aR, aR, legTop + 0.5, torsoTop - 0.5, (lx, ly, lz) => (lz > torsoTop - 1.5 && effTorso === 'armor') ? ARMOR_L : SKIN);
              }
            }
            if (drawOutfitEnabled && effTorso !== 'none') {
              const pad = effTorso === 'armor' ? 0.55 : 0.3;
              const zBot = effTorso === 'tunic' ? Math.max(1.2, legTop - 2.2) : legTop - 0.2;
              boxL(-torsoHalfW - pad, torsoHalfW + pad, -torsoDepth - pad * 0.6, torsoDepth + pad * 0.6, zBot, torsoTop + 0.1, (lx, ly, lz) => {
                if (effTorso === 'vest' && Math.abs(lx) < 1.3 && ly > 0) return 0; // colete aberto na frente
                if (lz >= legTop - 0.2 && lz <= legTop + 1.0) return (Math.abs(lx) <= 0.9 && ly > torsoDepth * 0.6) ? EQUIP : BOOT;
                if (effTorso === 'armor') {
                  if (lz > torsoTop - 1.2 && Math.abs(lx) <= 1.4 && ly > torsoDepth * 0.5) return EQUIP;
                  return ly > torsoDepth * 0.5 && Math.abs(lx) < torsoHalfW * 0.55 ? ARMOR_L : ARMOR;
                }
                if (effTorso === 'tunic' && Math.abs(lx) < 0.7 && ly > torsoDepth * 0.6) return EQUIP;
                return lz > torsoTop - 1.0 ? SHIRT_L : SHIRT;
              });
              // Mangas / ombreiras nos braços
              if (effTorso !== 'vest') {
                for (const sx of [-1, 1]) {
                  const ax = sx * armX;
                  const aR = (isMonster ? 1.45 : (isDwarf ? 1.15 : 0.95));
                  const sleeveBot = effTorso === 'armor' ? torsoTop - 2.6 : legTop + 2.5;
                  boxL(ax - aR, ax + aR, -aR, aR, sleeveBot, torsoTop - 0.2, effTorso === 'armor' ? ARMOR_L : SHIRT);
                }
              }
            }

            // Cabeça
            if (drawBody) {
              if (isChibi) {
                ellipL(0, headCenterY, headCenterZ, headRx, headRy, headH * 0.52, (lx, ly, lz) => {
                  if (lz >= headCenterZ - 1.2 && lz <= headCenterZ + 0.9 && ly > headRy * 0.62 && Math.abs(Math.abs(lx) - headRx * 0.42) <= 0.72) {
                    return (lz > headCenterZ + 0.2 && Math.abs(lx) > headRx * 0.38) ? WHITE : EYE;
                  }
                  if (lz >= headCenterZ - 2.1 && lz <= headCenterZ - 1.1 && ly > headRy * 0.6 && Math.abs(Math.abs(lx) - headRx * 0.68) <= 0.65) return EQUIP_L;
                  return SKIN;
                });
              } else {
                ellipL(0, headCenterY, headCenterZ, headRx, headRy, headH * 0.52, (lx, ly, lz) => {
                  if (lz >= headCenterZ - 0.4 && lz <= headCenterZ + 0.9 && ly >= headFrontY - 0.9 && Math.abs(Math.abs(lx) - headRx * 0.45) <= 0.6) {
                    return isMonster ? EQUIP_L : EYE;
                  }
                  if (isMonster && lz >= headCenterZ - 1.9 && lz <= headCenterZ - 1.1 && ly >= headFrontY - 0.7 && Math.abs(Math.abs(lx) - headRx * 0.4) <= 0.5) return WHITE;
                  return lz < headCenterZ - headH * 0.28 ? SKIN_D : SKIN;
                });
              }
            }
          }
        }

        // --- 2. Cabelo / Barba / Orelhas / Chifres / Crista ---
        const topLim = 23.4;
        if (effHead !== 'none') {
          if (effHead === 'short_hair') {
            boxL(-headRx - 0.3, headRx + 0.3, headBackY - 0.3, headFrontY + 0.2, headTopZ - 1.3, Math.min(topLim, headTopZ + 1.0), HAIR);
            boxL(-headRx - 0.2, headRx + 0.2, headBackY - 0.7, headBackY + 0.8, headCenterZ - 1.0, headTopZ, HAIR_D);
            boxL(-headRx + 0.2, headRx - 0.2, headFrontY - 0.7, headFrontY + 0.4, headTopZ - 1.6, headTopZ, HAIR_L);
          } else if (effHead === 'long_hair') {
            boxL(-headRx - 0.5, headRx + 0.5, headBackY - 0.6, headFrontY + 0.2, headTopZ - 1.3, Math.min(topLim, headTopZ + 1.0), HAIR);
            boxL(-headRx - 0.5, headRx + 0.5, headBackY - 1.2, headBackY + 0.7, Math.max(3.0, headCenterZ - 7.5), headTopZ + 0.5, HAIR_D);
            for (const sx of [-1, 1]) {
              boxL(sx * (headRx - 0.4), sx * (headRx + 1.0), headBackY, headCenterY + 1.0, Math.max(5.0, headCenterZ - 5.5), headTopZ, HAIR);
            }
          } else if (effHead === 'mohawk' && !isBipedBeast) {
            boxL(-0.95, 0.95, headBackY - 0.2, headFrontY + 0.2, headTopZ - 0.6, Math.min(topLim, headTopZ + 3.6), (lx, ly, lz) => (lz > headTopZ + 1.8) ? EQUIP : HAIR);
          } else if (effHead === 'ponytail') {
            boxL(-headRx - 0.3, headRx + 0.3, headBackY - 0.3, headFrontY + 0.2, headTopZ - 1.2, Math.min(topLim, headTopZ + 0.9), HAIR);
            boxL(-1.1, 1.1, headBackY - 1.4, headBackY, headCenterZ - 0.5, headCenterZ + 1.2, EQUIP);
            for (let t = 0; t <= 1; t += 0.12) {
              ellipL(0, headBackY - 1.2 - t * 1.6, headCenterZ + 0.5 - t * 4.5, 1.15 - t * 0.4, 1.0, 1.0, HAIR_D);
            }
          } else if (effHead === 'ears') {
            for (const sx of [-1, 1]) {
              for (let lz = headTopZ - 0.6; lz <= Math.min(topLim, headTopZ + 3.2); lz += 0.5) {
                const halfW = Math.max(0.4, 1.35 - Math.max(0, lz - headTopZ) * 0.35);
                boxL(sx * (headRx - 0.6) - halfW, sx * (headRx - 0.6) + halfW, headCenterY - 1.0, headCenterY + 1.0, lz, lz + 0.5, (lx, ly) => (Math.abs(lx - sx * (headRx - 0.6)) <= 0.4 && ly > headCenterY) ? SKIN_L : HAIR);
              }
            }
          } else if (effHead === 'horns') {
            for (const sx of [-1, 1]) {
              for (let t = 0; t <= 1; t += 0.1) {
                const hx = sx * (headRx * 0.75 + t * 1.6);
                const hy = headCenterY + 0.4 + t * 1.1;
                const hz = Math.min(topLim, headTopZ - 0.5 + t * 3.2);
                ellipL(hx, hy, hz, Math.max(0.45, 1.05 - t * 0.55), 0.9, 0.9, t > 0.7 ? EQUIP_L : EQUIP_D);
              }
            }
          } else if (effHead === 'beard') {
            boxL(-headRx * 0.85, headRx * 0.85, headFrontY - 0.6, headFrontY + 1.2, Math.max(torsoTop - 2.2, headCenterZ - 3.6), headCenterZ - 0.4, (lx, ly, lz) => lz < headCenterZ - 2.0 ? HAIR_D : HAIR);
            boxL(-1.4, 1.4, headFrontY + 0.3, headFrontY + 1.3, headCenterZ - 1.2, headCenterZ - 0.2, HAIR_L);
          }
        }

        // --- 3. Chapéu / Elmo ---
        if (effHat !== 'none') {
          if (effHat === 'helmet') {
            const z0 = headCenterZ - 0.4, z1 = Math.min(topLim, headTopZ + 1.4);
            boxL(-headRx - 0.8, headRx + 0.8, headBackY - 0.7, headFrontY + 0.7, z0, z1, (lx, ly, lz) => {
              const visorOpen = ly > headFrontY - 0.8 && lz < headTopZ - 0.7 && Math.abs(lx) <= headRx - 0.5;
              if (visorOpen) return 0;
              return (lz >= headTopZ - 0.6 && ly > headFrontY - 0.3) ? EQUIP : ARMOR;
            });
            boxL(-0.7, 0.7, headBackY, headFrontY - 0.4, z1, Math.min(topLim, z1 + 1.9), EQUIP_L);
          } else if (effHat === 'wizard_hat') {
            ellipL(0, headCenterY, headTopZ, headRx + 2.4, headRy + 2.4, 0.7, ARMOR_D);
            for (let t = 0; t <= 1; t += 0.08) {
              const cz = Math.min(topLim, headTopZ + 0.5 + t * 4.5);
              const cr = Math.max(0.5, (headRx + 0.3) * (1 - t * 0.85));
              ellipL(0, headCenterY - t * 1.4, cz, cr, cr, 0.75, t < 0.2 ? EQUIP : ARMOR);
            }
          } else if (effHat === 'crown') {
            const zBase = headTopZ - 0.4;
            boxL(-headRx - 0.3, headRx + 0.3, headBackY - 0.3, headFrontY + 0.3, zBase, Math.min(topLim, zBase + 1.1), EQUIP);
            for (const [px, py] of [[-headRx, headCenterY], [headRx, headCenterY], [0, headFrontY], [0, headBackY]]) {
              boxL(px - 0.7, px + 0.7, py - 0.7, py + 0.7, zBase + 1.0, Math.min(topLim, zBase + 2.4), EQUIP_L);
            }
            putL(0, headFrontY + 0.4, zBase + 0.6, GLOW);
          } else if (effHat === 'hood') {
            boxL(-headRx - 0.8, headRx + 0.8, headBackY - 0.9, headFrontY + 0.5, headCenterZ - 1.2, Math.min(topLim, headTopZ + 1.2), (lx, ly, lz) => {
              const faceOpen = ly > headFrontY - 0.8 && lz < headTopZ - 0.5 && Math.abs(lx) <= headRx - 0.3;
              return faceOpen ? 0 : (ly > headFrontY - 0.3 ? ARMOR_L : ARMOR_D);
            });
          } else if (effHat === 'straw_hat') {
            ellipL(0, headCenterY, headTopZ - 0.1, headRx + 2.8, headRy + 2.8, 0.65, EQUIP_L);
            ellipL(0, headCenterY, Math.min(topLim, headTopZ + 1.1), headRx + 0.2, headRy + 0.2, 1.3, (lx, ly, lz) => lz < headTopZ + 0.7 ? SHIRT : EQUIP);
          }
        }

        // --- 4. Costas (Capa / Mochila / Asas) ---
        if (effBack !== 'none') {
          const isLongBack = (isQuad || isLizard);
          const bY = isLongBack ? -0.6 : (-torsoDepth - 0.7);
          const bZTop = isLongBack ? Math.min(22.0, torsoTop + 1.2) : torsoTop;
          if (effBack === 'cape') {
            for (let lz = Math.max(1.5, legTop - 3.5); lz <= torsoTop - 0.2; lz += 0.5) {
              const frac = (torsoTop - lz) / Math.max(1, torsoTop - 1.5);
              const w = torsoHalfW * (0.85 + frac * 0.28);
              const yOff = -torsoDepth - 0.7 - frac * 1.1;
              boxL(-w, w, yOff - 0.6, yOff + 0.4, lz, lz + 0.6, (lz > torsoTop - 1.5 ? EQUIP : ARMOR));
            }
          } else if (effBack === 'backpack') {
            const z0 = isLongBack ? torsoTop - 0.4 : legTop + 0.8;
            const z1 = isLongBack ? Math.min(22.0, torsoTop + 3.2) : torsoTop - 0.5;
            boxL(-torsoHalfW * 0.75, torsoHalfW * 0.75, bY - 2.3, bY + 0.2, z0, z1, (lx, ly, lz) => {
              if (lz > z1 - 1.1) return EQUIP;
              return ly < bY - 1.6 ? PANTS_D : WOOD;
            });
          } else if (effBack === 'wings') {
            for (const sx of [-1, 1]) {
              for (let t = 0; t <= 1; t += 0.08) {
                const wx = sx * (torsoHalfW * 0.6 + t * 5.2);
                const wy = bY - 0.6 - t * 1.6;
                const wz = bZTop - 1.2 + Math.sin(t * Math.PI * 0.7) * 4.5;
                boxL(wx - 0.7, wx + 0.7, wy - 0.5, wy + 0.5, wz - 2.2 * (1 - t * 0.4), wz + 0.9, t < 0.2 ? ARMOR_D : ARMOR_L);
              }
            }
          }
        }

        // --- 5. Armas & Itens de Mão (Acoplados ou Soltos Centralizados!) ---
        const drawHandWeapon = (wType, wx, wy, wz, sc = 1.0) => {
          if (wType === 'sword') {
            boxL(wx - 0.5 * sc, wx + 0.5 * sc, wy - 0.5 * sc, wy + 0.5 * sc, wz - 1.5 * sc, wz + 1.5 * sc, WOOD);
            boxL(wx - 2.2 * sc, wx + 2.2 * sc, wy - 0.7 * sc, wy + 0.7 * sc, wz + 1.4 * sc, wz + 2.4 * sc, EQUIP);
            boxL(wx - 0.8 * sc, wx + 0.8 * sc, wy - 0.4 * sc, wy + 0.4 * sc, wz + 2.4 * sc, Math.min(23.5, wz + 11.2 * sc), (lx) => Math.abs(lx - wx) < 0.35 * sc ? WHITE : ARMOR_L);
          } else if (wType === 'axe') {
            boxL(wx - 0.5 * sc, wx + 0.5 * sc, wy - 0.5 * sc, wy + 0.5 * sc, wz - 2.0 * sc, Math.min(23.5, wz + 9.5 * sc), WOOD);
            boxL(wx - 2.8 * sc, wx + 2.8 * sc, wy - 0.5 * sc, wy + 0.5 * sc, wz + 5.8 * sc, Math.min(23.5, wz + 9.2 * sc), (lx) => Math.abs(lx - wx) > 1.9 * sc ? WHITE : ARMOR);
          } else if (wType === 'staff') {
            boxL(wx - 0.5 * sc, wx + 0.5 * sc, wy - 0.5 * sc, wy + 0.5 * sc, wz - 3.0 * sc, Math.min(22.0, wz + 9.8 * sc), WOOD);
            ellipL(wx, wy, Math.min(22.2, wz + 10.6 * sc), 1.4 * sc, 1.4 * sc, 1.4 * sc, GLOW);
          } else if (wType === 'hammer') {
            boxL(wx - 0.5 * sc, wx + 0.5 * sc, wy - 0.5 * sc, wy + 0.5 * sc, wz - 2.0 * sc, Math.min(22.5, wz + 8.5 * sc), WOOD);
            boxL(wx - 2.5 * sc, wx + 2.5 * sc, wy - 1.3 * sc, wy + 1.3 * sc, wz + 6.2 * sc, Math.min(23.5, wz + 9.6 * sc), (lx) => Math.abs(lx - wx) > 1.8 * sc ? EQUIP : ARMOR);
          } else if (wType === 'torch') {
            boxL(wx - 0.5 * sc, wx + 0.5 * sc, wy - 0.5 * sc, wy + 0.5 * sc, wz - 1.5 * sc, wz + 5.0 * sc, WOOD);
            ellipL(wx, wy, wz + 6.2 * sc, 1.2 * sc, 1.2 * sc, 1.8 * sc, (lx, ly, lz) => lz > wz + 6.8 * sc ? WHITE : EQUIP_L);
          }
        };

        const drawLeftItem = (lType, lx0, ly0, lz0, sc = 1.0) => {
          if (lType === 'shield') {
            boxL(lx0 - 2.4 * sc, lx0 + 2.4 * sc, ly0 - 0.5 * sc, ly0 + 0.9 * sc, lz0 - 2.2 * sc, lz0 + 4.4 * sc, (lx, ly, lz) => {
              const edge = Math.abs(lx - lx0) > 1.7 * sc || lz < lz0 - 1.4 * sc || lz > lz0 + 3.6 * sc;
              if (Math.hypot(lx - lx0, lz - (lz0 + 1.1 * sc)) <= 1.0 * sc) return EQUIP_L;
              return edge ? EQUIP : ARMOR;
            });
          } else if (lType === 'book') {
            boxL(lx0 - 1.6 * sc, lx0 + 1.6 * sc, ly0 - 1.2 * sc, ly0 + 1.2 * sc, lz0 - 0.5 * sc, lz0 + 3.6 * sc, (lx, ly, lz) => {
              if (lx > lx0 + 0.8 * sc) return WHITE;
              if (Math.abs(lz - (lz0 + 1.5 * sc)) < 0.6 * sc && ly > ly0 + 0.5 * sc) return EQUIP_L;
              return SHIRT_D;
            });
          } else if (lType === 'lantern') {
            boxL(lx0 - 0.4 * sc, lx0 + 0.4 * sc, ly0 - 0.4 * sc, ly0 + 0.4 * sc, lz0 + 2.4 * sc, lz0 + 4.0 * sc, ARMOR_D);
            boxL(lx0 - 1.3 * sc, lx0 + 1.3 * sc, ly0 - 1.3 * sc, ly0 + 1.3 * sc, lz0 - 1.2 * sc, lz0 + 2.4 * sc, (lx, ly, lz) => {
              const frame = Math.abs(lx - lx0) > 0.85 * sc && Math.abs(ly - ly0) > 0.85 * sc;
              if (frame || lz < lz0 - 0.6 * sc || lz > lz0 + 1.8 * sc) return ARMOR_D;
              return EQUIP_L;
            });
          }
        };

        if (partMode === 'rhand_only') {
          drawHandWeapon(effRHand, 0, 0, 4.0, 1.35);
        } else if (partMode === 'lhand_only') {
          drawLeftItem(effLHand, 0, 0, 4.0, 1.45);
        } else {
          if (effRHand !== 'none') drawHandWeapon(effRHand, handX, handY, handZ, 1.0);
          if (effLHand !== 'none') drawLeftItem(effLHand, -handX, handY, handZ, 1.0);
        }

        // Centraliza e assenta em z = 0 para qualquer peça solta exportável!
        const isLoosePart = partMode !== 'full' && partMode !== 'body_only';
        if (isLoosePart) centerAndGroundVolume();

        // Define nome e tipo sugerido automaticamente para salvar/exportar
        const hatNames = { helmet: 'elmo_cavaleiro', wizard_hat: 'chapeu_mago', crown: 'coroa_ouro', hood: 'capuz_sombra', straw_hat: 'chapeu_palha' };
        const backNames = { cape: 'capa_heroi', backpack: 'mochila_aventureiro', wings: 'asas_heroi' };
        const rhandNames = { sword: 'espada_heroi', axe: 'machado_heroi', staff: 'cajado_magico', hammer: 'martelo_guerra', torch: 'tocha_aventureiro' };
        const lhandNames = { shield: 'escudo_heroi', book: 'grimorio_magico', lantern: 'lanterna_mao' };
        const torsoNames = { armor: 'armadura_peitoral', tunic: 'tunica_heroi', shirt: 'camisa_heroi', vest: 'colete_aventureiro' };

        let outKind = 'avatar';
        let outName = `char_${charType}`;
        if (partMode === 'body_only') {
          outKind = 'avatar';
          outName = `base_${charType}`;
        } else if (partMode === 'outfit_only') {
          outKind = 'pickable';
          outName = torsoNames[effTorso] || 'roupa_heroi';
        } else if (partMode === 'headgear_only') {
          outKind = 'pickable';
          outName = hatNames[effHat] || `cabelo_${effHead}`;
        } else if (partMode === 'back_only') {
          outKind = 'pickable';
          outName = backNames[effBack] || 'capa_heroi';
        } else if (partMode === 'rhand_only') {
          outKind = 'pickable';
          outName = rhandNames[effRHand] || 'espada_heroi';
        } else if (partMode === 'lhand_only') {
          outKind = 'pickable';
          outName = lhandNames[effLHand] || 'escudo_heroi';
        }
        setUiKindAndName(outKind, outName);

        voxCache = null;
        renderPalette();
        drawEdit();
        say(`Modelo "${outName}" (${charType} / ${partMode}) gerado! Edite ou salve na biblioteca.`);
      }

      const charControlIds = [
        'mCharType', 'mCharLegH', 'mCharTorsoW', 'mCharHeadS',
        'mCharPartMode', 'mCharHead', 'mCharHat', 'mCharTorso', 'mCharLegs',
        'mCharBack', 'mCharRHand', 'mCharLHand',
        'mCharColSkin', 'mCharColHair', 'mCharColShirt', 'mCharColPants', 'mCharColArmor', 'mCharColEquip'
      ];
      const syncCharDefaultsForType = (cType) => {
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
        const curHead = document.getElementById('mCharHead')?.value;
        const curTorso = document.getElementById('mCharTorso')?.value;
        const curLegs = document.getElementById('mCharLegs')?.value;
        const humanHairs = ['short_hair', 'long_hair', 'ponytail', 'beard'];
        if (cType === 'biped_beast') {
          if (humanHairs.includes(curHead) || curHead === 'ears') setVal('mCharHead', 'mohawk');
          if (curTorso === 'shirt') setVal('mCharTorso', 'none');
          if (curLegs === 'pants') setVal('mCharLegs', 'none');
        } else if (cType === 'lizard' || cType === 'quadruped') {
          if (humanHairs.includes(curHead)) setVal('mCharHead', cType === 'quadruped' ? 'ears' : 'none');
          if (curTorso === 'shirt') setVal('mCharTorso', 'none');
          if (curLegs === 'pants') setVal('mCharLegs', 'none');
        } else {
          if (curHead === 'none') setVal('mCharHead', 'short_hair');
          if (curTorso === 'none') setVal('mCharTorso', 'shirt');
          if (curLegs === 'none') setVal('mCharLegs', 'pants');
        }
      };
      charControlIds.forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        const evName = (el.type === 'range' || el.type === 'color') ? 'input' : 'change';
        el.addEventListener(evName, () => {
          if (id === 'mCharType') syncCharDefaultsForType(el.value);
          generateCharacter({}, charSeed);
        });
      });

      const btnGenChar = document.getElementById('mBtnGenChar');
      const btnVaryChar = document.getElementById('mBtnVaryChar');
      if (btnGenChar) {
        btnGenChar.addEventListener('click', () => generateCharacter({}, charSeed));
      }
      if (btnVaryChar) {
        btnVaryChar.addEventListener('click', () => {
          charSeed++;
          const rng = makeRng(charSeed);
          const pick = (arr) => arr[Math.floor(rng() * arr.length)];
          const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
          const cType = document.getElementById('mCharType')?.value || 'humanoid';
          setVal('mCharColSkin', pick(['#F2C9A0', '#D9A173', '#8D5524', '#6BBF59', '#93C5FD', '#FCA5A5']));
          setVal('mCharColHair', pick(['#5B3A22', '#1F2937', '#D97706', '#DC2626', '#9333EA', '#FDE68A']));
          setVal('mCharColShirt', pick(['#3B82F6', '#EF4444', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899']));
          setVal('mCharColPants', pick(['#374151', '#1E3A8A', '#78350F', '#1F2937', '#4B5563']));
          setVal('mCharColArmor', pick(['#9CA3AF', '#D97706', '#475569', '#DC2626', '#6366F1']));
          setVal('mCharColEquip', pick(['#F59E0B', '#38BDF8', '#EF4444', '#A855F7', '#FDE047']));
          if (cType === 'biped_beast') {
            setVal('mCharHead', pick(['mohawk', 'horns', 'none']));
            setVal('mCharHat', pick(['none', 'none', 'crown', 'helmet']));
            setVal('mCharTorso', pick(['none', 'none', 'armor']));
            setVal('mCharLegs', 'none');
            setVal('mCharBack', pick(['none', 'wings', 'cape']));
          } else if (cType === 'lizard' || cType === 'quadruped') {
            setVal('mCharHead', pick(cType === 'quadruped' ? ['ears', 'horns', 'none'] : ['none', 'horns', 'mohawk']));
            setVal('mCharHat', pick(['none', 'none', 'crown', 'helmet']));
            setVal('mCharTorso', pick(['none', 'none', 'armor']));
            setVal('mCharLegs', 'none');
            setVal('mCharBack', pick(['none', 'wings', 'backpack']));
          } else {
            setVal('mCharHead', pick(['short_hair', 'long_hair', 'mohawk', 'ponytail', 'ears', 'horns', 'beard', 'none']));
            setVal('mCharHat', pick(['none', 'helmet', 'wizard_hat', 'crown', 'hood', 'straw_hat']));
            setVal('mCharTorso', pick(['shirt', 'tunic', 'armor', 'vest']));
            setVal('mCharLegs', pick(['pants', 'shorts', 'robe', 'greaves']));
            setVal('mCharBack', pick(['none', 'cape', 'backpack', 'wings']));
          }
          generateCharacter({}, charSeed);
        });
      }

      // ---------- Construtor Modular de Props (Armas, Casas, Baús, Rochas & Plantas) ----------
      const PROP_SUBTYPES = {
        weapon: [
          ['sword', '🗡️ Espada'],
          ['greatsword', '⚔️ Espadão'],
          ['axe', '🪓 Machado Duplo'],
          ['hammer', '🔨 Martelo de Guerra'],
          ['staff', '🪄 Cajado com Orbe'],
          ['shield', '🛡️ Escudo Brasão']
        ],
        house: [
          ['gable', '🏠 Cabana 2 Águas'],
          ['steep', '🏡 Chalé Íngreme'],
          ['tower', '🏰 Torre com Ameias'],
          ['dome', '⛺ Casa Domo']
        ],
        chest: [
          ['chest_round', '📦 Baú Arredondado'],
          ['chest_flat', '🧰 Baú Reto'],
          ['barrel', '🛢️ Barril'],
          ['crate', '📦 Caixote Reforçado'],
          ['table', '🪑 Mesa / Altar']
        ],
        rock: [
          ['boulder', '🪨 Pedregulho'],
          ['crystal', '💎 Cluster de Cristais'],
          ['pillar', '🏛️ Pilar de Ruína'],
          ['arch', '🌉 Arco de Pedra']
        ],
        plant: [
          ['mushroom', '🍄 Cogumelo'],
          ['cluster', '🍄 Família de Cogumelos'],
          ['flower', '🌺 Flor Gigante'],
          ['cactus', '🌵 Cacto']
        ]
      };

      function syncPropSubtypes(family, preferredSubtype) {
        const subEl = document.getElementById('mPropSubtype');
        const list = PROP_SUBTYPES[family] || PROP_SUBTYPES.weapon;
        if (!subEl) return list[0][0];
        const prev = preferredSubtype || subEl.value;
        const valid = list.some(([k]) => k === prev);
        if (typeof document.createElement === 'function' && subEl.innerHTML !== undefined) {
          subEl.innerHTML = '';
          list.forEach(([val, label]) => {
            const opt = document.createElement('option');
            opt.value = val;
            opt.textContent = label;
            if (subEl.appendChild) subEl.appendChild(opt);
          });
        }
        const chosen = valid ? prev : list[0][0];
        subEl.value = chosen;
        return chosen;
      }

      bindRangeLabel('mPropWidth', 'mPropWidthVal');
      bindRangeLabel('mPropHeight', 'mPropHeightVal');
      bindRangeLabel('mPropDepth', 'mPropDepthVal');

      let propSeed = 100;
      function getPropUiOpts() {
        const fam = document.getElementById('mPropFamily')?.value || 'weapon';
        const list = PROP_SUBTYPES[fam] || PROP_SUBTYPES.weapon;
        const rawSub = document.getElementById('mPropSubtype')?.value;
        const sub = list.some(([k]) => k === rawSub) ? rawSub : list[0][0];
        return {
          family: fam,
          subtype: sub,
          width: parseInt(document.getElementById('mPropWidth')?.value || '6', 10) || 6,
          height: parseInt(document.getElementById('mPropHeight')?.value || '14', 10) || 14,
          depth: parseInt(document.getElementById('mPropDepth')?.value || '5', 10) || 5,
          detail: parseInt(document.getElementById('mPropDetail')?.value ?? '1', 10),
          colMain: document.getElementById('mPropColMain')?.value || '#8A5A2B',
          colSec: document.getElementById('mPropColSec')?.value || '#9AA3A8',
          colAcc: document.getElementById('mPropColAcc')?.value || '#F59E0B',
          colGem: document.getElementById('mPropColGem')?.value || '#38BDF8'
        };
      }

      function generateModularProp(opts = {}, seed = propSeed) {
        const ui = getPropUiOpts();
        const o = { ...ui, ...(opts || {}) };
        const family = String(o.family || 'weapon');
        const famSubs = PROP_SUBTYPES[family] || PROP_SUBTYPES.weapon;
        const subtype = famSubs.some(([k]) => k === o.subtype) ? o.subtype : famSubs[0][0];
        const width = Math.max(3, Math.min(11, parseInt(o.width, 10) || 6));
        const height = Math.max(6, Math.min(22, parseInt(o.height, 10) || 14));
        const depth = Math.max(2, Math.min(10, parseInt(o.depth, 10) || 5));
        const detail = Math.max(0, Math.min(2, Number.isFinite(o.detail) ? o.detail : 1));
        const rng = makeRng(seed);

        const cMain = o.colMain || '#8A5A2B';
        const cSec = o.colSec || '#9AA3A8';
        const cAcc = o.colAcc || '#F59E0B';
        const cGem = o.colGem || '#38BDF8';

        // 1..3 Main | 4..6 Sec | 7..9 Acc | 10..12 Gem | 13 White | 14 Dark | 15 Outline
        pal = [
          'rgba(0,0,0,0)',
          shadeHex(cMain, 0.74), cMain, shadeHex(cMain, 1.24),
          shadeHex(cSec, 0.74), cSec, shadeHex(cSec, 1.24),
          shadeHex(cAcc, 0.75), cAcc, shadeHex(cAcc, 1.25),
          shadeHex(cGem, 0.75), cGem, shadeHex(cGem, 1.28),
          '#FFFFFF', '#1B1B1B', '#3B2219'
        ];
        const MAIN_D = 1, MAIN = 2, MAIN_L = 3;
        const SEC_D = 4, SEC = 5, SEC_L = 6;
        const ACC_D = 7, ACC = 8, ACC_L = 9;
        const GEM_D = 10, GEM = 11, GEM_L = 12;
        const WHITE = 13, DARK = 14;

        for (let z = 0; z < N; z++) vol[z].fill(0);
        const s = N / 24;
        const cx = (N - 1) / 2;
        const cy = (N - 1) / 2;

        const pBox = (x0, x1, y0, y1, z0, z1, fn) => {
          const ix0 = Math.max(0, Math.floor(cx + x0 * s)), ix1 = Math.min(N - 1, Math.ceil(cx + x1 * s));
          const iy0 = Math.max(0, Math.floor(cy + y0 * s)), iy1 = Math.min(N - 1, Math.ceil(cy + y1 * s));
          const iz0 = Math.max(0, Math.floor(z0 * s)), iz1 = Math.min(N - 1, Math.ceil(z1 * s));
          for (let iz = iz0; iz <= iz1; iz++) {
            const lz = iz / s;
            for (let iy = iy0; iy <= iy1; iy++) {
              const ly = (iy - cy) / s;
              for (let ix = ix0; ix <= ix1; ix++) {
                const lx = (ix - cx) / s;
                if (lx >= x0 - 0.15 && lx <= x1 + 0.15 && ly >= y0 - 0.15 && ly <= y1 + 0.15 && lz >= z0 - 0.15 && lz <= z1 + 0.15) {
                  const v = typeof fn === 'function' ? fn(lx, ly, lz) : fn;
                  if (v > 0) vol[iz][iy * N + ix] = v;
                }
              }
            }
          }
        };
        const pEllip = (ox, oy, oz, rx, ry, rz, fn) => {
          const ix0 = Math.max(0, Math.floor(cx + (ox - rx) * s)), ix1 = Math.min(N - 1, Math.ceil(cx + (ox + rx) * s));
          const iy0 = Math.max(0, Math.floor(cy + (oy - ry) * s)), iy1 = Math.min(N - 1, Math.ceil(cy + (oy + ry) * s));
          const iz0 = Math.max(0, Math.floor((oz - rz) * s)), iz1 = Math.min(N - 1, Math.ceil((oz + rz) * s));
          for (let iz = iz0; iz <= iz1; iz++) {
            const lz = iz / s;
            for (let iy = iy0; iy <= iy1; iy++) {
              const ly = (iy - cy) / s;
              for (let ix = ix0; ix <= ix1; ix++) {
                const lx = (ix - cx) / s;
                const d = ((lx - ox) / rx) ** 2 + ((ly - oy) / ry) ** 2 + ((lz - oz) / rz) ** 2;
                if (d <= 1.04) {
                  const v = typeof fn === 'function' ? fn(lx, ly, lz, d) : fn;
                  if (v > 0) vol[iz][iy * N + ix] = v;
                }
              }
            }
          }
        };

        let outKind = 'solid';
        let dropKey = null;

        if (family === 'weapon') {
          outKind = 'pickable';
          const hTop = Math.min(22.5, height + 2);
          const halfW = width * 0.65;
          const halfD = Math.max(0.7, depth * 0.22);
          if (subtype === 'sword' || subtype === 'greatsword') {
            const bladeW = subtype === 'greatsword' ? Math.max(1.8, width * 0.34) : Math.max(1.1, width * 0.22);
            const guardW = Math.max(2.6, halfW * 1.15);
            const guardZ = 4.8;
            // Pommel + Grip
            pEllip(0, 0, 1.0, 1.2, 1.1, 1.0, detail >= 2 ? ACC_L : ACC);
            pBox(-0.7, 0.7, -0.7, 0.7, 1.6, guardZ, MAIN);
            // Guard
            if (detail >= 1) {
              pBox(-guardW, guardW, -halfD - 0.3, halfD + 0.3, guardZ, guardZ + 1.4, ACC);
              if (detail >= 2) pEllip(0, 0, guardZ + 0.7, 1.1, halfD + 0.5, 0.9, GEM_L);
            }
            // Blade
            for (let lz = guardZ + 1.2; lz <= hTop; lz += 0.5) {
              const tipFrac = lz > hTop - 3.2 ? (lz - (hTop - 3.2)) / 3.2 : 0;
              const bw = Math.max(0.45, bladeW * (1 - tipFrac * 0.78));
              pBox(-bw, bw, -halfD * 0.7, halfD * 0.7, lz, lz + 0.6, (lx) => Math.abs(lx) < bw * 0.45 ? SEC_L : SEC);
            }
          } else if (subtype === 'axe') {
            pBox(-0.75, 0.75, -0.75, 0.75, 0.5, hTop, MAIN);
            if (detail >= 1) pEllip(0, 0, 1.0, 1.1, 1.1, 0.8, ACC);
            const headBot = Math.max(6, hTop - 6.5);
            for (let lz = headBot; lz <= hTop - 0.5; lz += 0.5) {
              const flare = 1 + Math.abs(lz - (headBot + hTop - 0.5) * 0.5) * 0.14;
              const axW = Math.min(8.5, halfW * 1.15 * flare);
              pBox(-axW, axW, -halfD * 0.7, halfD * 0.7, lz, lz + 0.6, (lx) => {
                if (Math.abs(lx) < 1.1) return ACC;
                return Math.abs(lx) > axW - 1.1 ? SEC_L : SEC;
              });
            }
            if (detail >= 2) pEllip(0, 0, (headBot + hTop) * 0.5, 1.1, halfD + 0.6, 1.1, GEM);
          } else if (subtype === 'hammer') {
            pBox(-0.75, 0.75, -0.75, 0.75, 0.5, hTop - 1.5, MAIN);
            const hBot = Math.max(6, hTop - 5.5);
            const hw = Math.min(8.5, halfW * 1.15);
            pBox(-hw, hw, -halfD * 1.4, halfD * 1.4, hBot, hTop, (lx) => (Math.abs(lx) > hw - 1.0 || (detail >= 1 && Math.abs(lx) < 1.1)) ? ACC : SEC);
            if (detail >= 2) pEllip(0, 0, hTop + 0.4, 1.2, 1.2, 0.9, GEM_L);
          } else if (subtype === 'staff') {
            pBox(-0.65, 0.65, -0.65, 0.65, 0.5, hTop - 3.0, MAIN);
            const orbZ = hTop - 1.6;
            if (detail >= 1) pBox(-2.2, 2.2, -0.8, 0.8, orbZ - 2.2, orbZ - 1.2, ACC);
            pEllip(0, 0, orbZ, Math.max(1.6, halfW * 0.42), Math.max(1.6, halfD + 0.5), 2.0, (lx, ly, lz, d) => d < 0.35 ? GEM_L : GEM);
            if (detail >= 2) {
              pBox(-2.6, -1.8, -0.6, 0.6, orbZ - 1.5, orbZ + 1.2, ACC_L);
              pBox(1.8, 2.6, -0.6, 0.6, orbZ - 1.5, orbZ + 1.2, ACC_L);
            }
          } else {
            // shield
            const sw = Math.min(9.5, halfW * 1.45);
            const sd = Math.max(1.0, halfD * 0.85);
            for (let lz = 0.5; lz <= hTop; lz += 0.5) {
              const taper = lz < 4.5 ? Math.max(0.35, lz / 4.5) : 1.0;
              const rw = sw * taper;
              pBox(-rw, rw, -sd, sd, lz, lz + 0.6, (lx) => {
                const isRim = detail >= 1 && (Math.abs(lx) >= rw - 1.1 || lz > hTop - 1.2 || lz < 1.8);
                return isRim ? ACC : MAIN;
              });
            }
            if (detail >= 1) pEllip(0, sd + 0.4, hTop * 0.52, 1.6, 0.9, 1.6, detail >= 2 ? GEM_L : SEC_L);
          }
        } else if (family === 'house') {
          outKind = 'solid';
          const hw = Math.min(9.5, width * 0.85);
          const hd = Math.min(8.5, Math.max(4.0, depth * 0.85));
          const wallTop = Math.max(4.5, Math.min(14, height * 0.58));
          const roofTop = Math.min(22.2, height + 2);
          // Fundação de pedra
          pBox(-hw - 0.6, hw + 0.6, -hd - 0.6, hd + 0.6, 0, 1.8, SEC_D);
          if (subtype === 'tower') {
            const rad = Math.min(hw, hd);
            for (let lz = 1.8; lz <= roofTop - 2.0; lz += 0.5) {
              pEllip(0, 0, lz, rad, rad, 0.55, (lx, ly) => {
                if (detail >= 1 && ly > rad * 0.72 && Math.abs(lx) < 1.5 && lz < 7.2) return MAIN_D;
                if (detail >= 1 && ly > rad * 0.72 && Math.abs(lx) < 1.2 && lz > roofTop - 7 && lz < roofTop - 4.2) return GEM_L;
                return ((Math.round(lx + ly + lz) & 1) === 0) ? SEC : SEC_L;
              });
            }
            // Ameias no topo
            for (let a = 0; a < 8; a++) {
              const ang = (a / 8) * Math.PI * 2;
              pBox(Math.cos(ang) * rad - 0.9, Math.cos(ang) * rad + 0.9, Math.sin(ang) * rad - 0.9, Math.sin(ang) * rad + 0.9, roofTop - 2.0, roofTop, SEC_L);
            }
            if (detail >= 2) pBox(-0.4, 0.4, -0.4, 0.4, roofTop, Math.min(23.5, roofTop + 3), ACC);
          } else if (subtype === 'dome') {
            const rx = hw, ry = hd, rz = Math.max(6, roofTop - 1.8);
            pEllip(0, 0, 1.8, rx, ry, rz, (lx, ly, lz) => {
              if (detail >= 1 && ly > ry * 0.65 && Math.abs(lx) <= 1.7 && lz <= 6.5) return MAIN_D;
              if (detail >= 1 && Math.abs(lx) >= rx * 0.72 && Math.abs(ly) <= 1.4 && lz >= 4.5 && lz <= 7.5) return GEM_L;
              return lz > rz * 0.55 ? ACC : MAIN;
            });
          } else {
            // gable / steep
            pBox(-hw, hw, -hd, hd, 1.8, wallTop, (lx, ly, lz) => {
              if (detail >= 1 && Math.abs(lx) >= hw - 1.1 && Math.abs(ly) >= hd - 1.1) return MAIN_D;
              if (detail >= 1 && ly >= hd - 0.8 && Math.abs(lx) <= 1.6 && lz <= 7.2) return (Math.abs(lx) < 0.7 && lz > 3.6 && lz < 4.6) ? ACC_L : MAIN_D;
              if (detail >= 1 && ((Math.abs(lx) >= hw - 0.8 && Math.abs(ly) <= 1.4) || (ly >= hd - 0.8 && Math.abs(Math.abs(lx) - hw * 0.55) <= 1.1)) && lz >= 4.5 && lz <= 7.2) return GEM_L;
              return MAIN_L;
            });
            const roofH = Math.max(3.5, roofTop - wallTop);
            const steepFactor = subtype === 'steep' ? 1.25 : 0.95;
            for (let lz = wallTop; lz <= roofTop; lz += 0.5) {
              const frac = (lz - wallTop) / roofH;
              const span = Math.max(0.5, (hw + 1.2) * (1 - frac * steepFactor));
              pBox(-span, span, -hd - 1.0, hd + 1.0, lz, lz + 0.6, (lx, ly) => (Math.abs(lx) >= span - 1.1 || Math.abs(ly) >= hd + 0.1) ? ACC : MAIN_L);
            }
            if (detail >= 2) pBox(hw * 0.4, hw * 0.4 + 2.0, -hd * 0.6, -hd * 0.6 + 2.0, wallTop, Math.min(23.2, roofTop + 1.5), SEC);
          }
        } else if (family === 'chest') {
          outKind = 'solid';
          const hw = Math.min(9.5, width * 0.88);
          const hd = Math.min(7.5, Math.max(3.0, depth * 0.78));
          const topZ = Math.min(18.0, Math.max(6.0, height * 0.82));
          if (subtype === 'barrel') {
            const rad = Math.min(hw, hd);
            for (let lz = 0; lz <= topZ; lz += 0.5) {
              const bulge = 1 + Math.sin((lz / topZ) * Math.PI) * 0.22;
              const isBand = detail >= 1 && (Math.abs(lz - topZ * 0.22) < 0.8 || Math.abs(lz - topZ * 0.78) < 0.8);
              pEllip(0, 0, lz, rad * bulge, rad * bulge, 0.55, isBand ? SEC : MAIN);
            }
          } else if (subtype === 'table') {
            const legTop = Math.max(3.5, topZ - 2.0);
            for (const sx of [-1, 1]) for (const sy of [-1, 1]) {
              pBox(sx * (hw - 1.4), sx * (hw - 0.2), sy * (hd - 1.4), sy * (hd - 0.2), 0, legTop, MAIN_D);
            }
            pBox(-hw, hw, -hd, hd, legTop, topZ, (lx, ly) => (detail >= 1 && (Math.abs(lx) > hw - 1.0 || Math.abs(ly) > hd - 1.0)) ? ACC : MAIN_L);
            if (detail >= 2) {
              pBox(-1.0, 1.0, -1.0, 1.0, topZ, topZ + 2.4, WHITE);
              pEllip(0, 0, topZ + 3.0, 0.8, 0.8, 0.9, ACC_L);
            }
          } else if (subtype === 'crate') {
            pBox(-hw, hw, -hd, hd, 0, topZ, (lx, ly, lz) => {
              const rim = detail >= 1 && (Math.abs(lx) >= hw - 1.1 || Math.abs(ly) >= hd - 1.1 || lz < 1.1 || lz > topZ - 1.1 || Math.abs(lx - ly) < 0.9);
              return rim ? (detail >= 2 ? SEC : MAIN_D) : MAIN;
            });
          } else {
            // chest_round / chest_flat
            const baseH = topZ * 0.55;
            pBox(-hw, hw, -hd, hd, 0, baseH, (lx, ly, lz) => {
              const strap = detail >= 1 && (Math.abs(Math.abs(lx) - hw * 0.62) <= 0.8 || Math.abs(lx) >= hw - 0.9 || Math.abs(ly) >= hd - 0.8);
              return strap ? SEC : MAIN;
            });
            if (detail >= 2) {
              // Baú aberto com ouro & joias!
              pBox(-hw + 0.8, hw - 0.8, -hd + 0.8, hd - 0.8, baseH - 1.0, baseH + 1.5, (lx, ly) => ((Math.round(lx * 2 + ly) & 3) === 0) ? GEM_L : ACC_L);
              pBox(-hw, hw, -hd - 1.2, -hd + 1.2, baseH, Math.min(22.5, topZ + 2.0), MAIN_D);
            } else {
              for (let lz = baseH; lz <= topZ; lz += 0.5) {
                const frac = (lz - baseH) / Math.max(1, topZ - baseH);
                const ry = subtype === 'chest_round' ? hd * Math.sqrt(Math.max(0.08, 1 - frac * frac)) : hd;
                pBox(-hw, hw, -ry, ry, lz, lz + 0.6, (lx) => (detail >= 1 && (Math.abs(Math.abs(lx) - hw * 0.62) <= 0.8 || Math.abs(lx) >= hw - 0.9)) ? SEC : MAIN);
              }
            }
            if (detail >= 1) pBox(-1.4, 1.4, hd - 0.2, hd + 1.1, baseH - 1.4, baseH + 1.2, ACC_L);
          }
        } else if (family === 'rock') {
          outKind = 'destructible';
          dropKey = 'stone_chunk';
          const rx = Math.min(9.5, width * 0.92);
          const ry = Math.min(9.5, Math.max(3.5, depth * 0.95));
          const rz = Math.min(20.0, height * 0.92);
          if (subtype === 'crystal') {
            pEllip(0, 0, 2.0, rx * 0.85, ry * 0.85, 3.2, SEC_D);
            const spires = 4 + detail * 2;
            for (let k = 0; k < spires; k++) {
              const ang = (k / spires) * Math.PI * 2 + rng() * 0.4;
              const ox = k === 0 ? 0 : Math.cos(ang) * (rx * 0.48);
              const oy = k === 0 ? 0 : Math.sin(ang) * (ry * 0.48);
              const sh = k === 0 ? rz : rz * (0.55 + rng() * 0.35);
              const sr = k === 0 ? Math.max(1.8, rx * 0.36) : Math.max(1.2, rx * 0.24);
              for (let lz = 0; lz <= sh; lz += 0.5) {
                const taper = Math.max(0.25, 1 - Math.max(0, lz - sh * 0.65) / (sh * 0.36));
                pEllip(ox, oy, lz, sr * taper, sr * taper, 0.55, lz > sh * 0.75 ? GEM_L : GEM);
              }
            }
          } else if (subtype === 'pillar') {
            pBox(-rx * 0.65, rx * 0.65, -ry * 0.65, ry * 0.65, 0, 2.2, MAIN_D);
            pBox(-rx * 0.45, rx * 0.45, -ry * 0.45, ry * 0.45, 2.0, rz, (lx, ly, lz) => {
              if (detail >= 1 && lz < 5.0 && ((Math.round(lx + ly) & 1) === 0)) return ACC;
              if (detail >= 2 && Math.abs(lz - rz * 0.5) < 1.2) return GEM;
              return MAIN;
            });
            pBox(-rx * 0.62, rx * 0.62, -ry * 0.62, ry * 0.62, Math.max(3, rz - 2.0), rz, MAIN_L);
          } else if (subtype === 'arch') {
            const span = Math.max(3.5, rx * 0.55);
            for (const sx of [-1, 1]) pBox(sx * span - 1.8, sx * span + 1.8, -ry * 0.5, ry * 0.5, 0, rz * 0.65, MAIN);
            pBox(-span - 2.2, span + 2.2, -ry * 0.55, ry * 0.55, rz * 0.62, rz, (lx, ly, lz) => (detail >= 2 && Math.abs(lx) < 1.2) ? GEM : MAIN_L);
          } else {
            // boulder
            const pA = rng() * 6.28, pB = rng() * 6.28;
            for (let z = 0; z < N; z++) {
              const lz = z / s;
              for (let y = 0; y < N; y++) {
                const ly = (y - cy) / s;
                for (let x = 0; x < N; x++) {
                  const lx = (x - cx) / s;
                  const facet = Math.abs(Math.sin(lx * 0.55 + pA) * Math.cos(ly * 0.55 + pB)) * 0.22;
                  const d = (lx / rx) ** 2 + (ly / ry) ** 2 + ((lz - 1.5) / rz) ** 2 + facet;
                  if (d <= 1.0 && lz >= 0) {
                    let col = lz > rz * 0.78 ? MAIN_L : (lz > rz * 0.42 ? MAIN : MAIN_D);
                    if (detail >= 1 && lz > rz * 0.62 && Math.sin(lx + ly) > 0.4) col = ACC;
                    if (detail >= 2 && lz > rz * 0.88 && Math.hypot(lx, ly) < 2.2) col = GEM_L;
                    vol[z][y * N + x] = col;
                  }
                }
              }
            }
          }
        } else {
          // plant: mushroom, cluster, flower, cactus
          outKind = 'foliage';
          const rw = Math.min(9.5, width * 0.9);
          const rh = Math.min(21.0, height);
          const stemH = rh * 0.58;
          if (subtype === 'flower') {
            pBox(-0.8, 0.8, -0.8, 0.8, 0, stemH, SEC);
            if (detail >= 1) {
              pEllip(-2.5, 0, stemH * 0.45, 2.0, 1.0, 0.7, SEC_L);
              pEllip(2.5, 0, stemH * 0.55, 2.0, 1.0, 0.7, SEC_L);
            }
            const petals = 5 + detail;
            for (let k = 0; k < petals; k++) {
              const ang = (k / petals) * Math.PI * 2;
              pEllip(Math.cos(ang) * rw * 0.52, Math.sin(ang) * rw * 0.52, stemH + 1.0, rw * 0.35, rw * 0.35, 1.3, MAIN_L);
            }
            pEllip(0, 0, stemH + 1.6, rw * 0.28, rw * 0.28, 1.5, ACC_L);
          } else if (subtype === 'cactus') {
            const cr = Math.max(1.8, depth * 0.42);
            pBox(-cr, cr, -cr, cr, 0, rh, (lx, ly) => (detail >= 1 && ((Math.round(lx + ly) & 1) === 1)) ? SEC_L : SEC);
            pBox(-rw * 0.85, -cr, -cr * 0.7, cr * 0.7, rh * 0.38, rh * 0.72, SEC);
            pBox(cr, rw * 0.85, -cr * 0.7, cr * 0.7, rh * 0.48, rh * 0.82, SEC);
            if (detail >= 2) pEllip(0, 0, rh + 0.6, 1.5, 1.5, 1.2, MAIN_L);
          } else {
            // mushroom / cluster
            const caps = subtype === 'cluster' ? [[0, 0, rw * 0.82, rh], [-4.2, 2.6, rw * 0.46, rh * 0.62], [4.0, -2.5, rw * 0.42, rh * 0.56]] : [[0, 0, rw, rh]];
            caps.forEach(([ox, oy, cr, ch], idx) => {
              const sh = ch * 0.55;
              pEllip(ox, oy, sh * 0.5, Math.max(1.2, cr * 0.28), Math.max(1.2, cr * 0.28), sh * 0.55, SEC_L);
              pEllip(ox, oy, sh + 1.0, cr, cr, ch * 0.36, (lx, ly, lz) => {
                if (lz < sh) return 0;
                if (detail >= 1 && Math.abs(Math.sin((lx - ox) * 0.9) * Math.cos((ly - oy) * 0.9)) > 0.55) return WHITE;
                return idx === 0 ? MAIN : MAIN_L;
              });
            });
            if (detail >= 2) pEllip(2.8, 2.5, 1.2, 1.3, 1.3, 1.0, GEM_L);
          }
        }

        const outName = `${subtype}_${seed}`;
        setUiKindAndName(outKind, outName, dropKey);
        voxCache = null;
        renderPalette();
        drawEdit();
        say(`Prop "${family}/${subtype}" gerado (seed ${seed})!`);
      }

      const propFamEl = document.getElementById('mPropFamily');
      if (propFamEl) {
        propFamEl.addEventListener('change', () => {
          syncPropSubtypes(propFamEl.value);
          generateModularProp({}, propSeed);
        });
      }
      ['mPropWidth', 'mPropHeight', 'mPropDepth', 'mPropSubtype', 'mPropDetail', 'mPropColMain', 'mPropColSec', 'mPropColAcc', 'mPropColGem'].forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        const evName = (el.type === 'range' || el.type === 'color') ? 'input' : 'change';
        el.addEventListener(evName, () => generateModularProp({}, propSeed));
      });

      const btnGenProp = document.getElementById('mBtnGenProp');
      const btnVaryProp = document.getElementById('mBtnVaryProp');
      if (btnGenProp) btnGenProp.addEventListener('click', () => generateModularProp({}, propSeed));
      if (btnVaryProp) {
        btnVaryProp.addEventListener('click', () => {
          propSeed++;
          const rng = makeRng(propSeed);
          const pick = (arr) => arr[Math.floor(rng() * arr.length)];
          const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
          setVal('mPropColMain', pick(['#8A5A2B', '#64748B', '#DC2626', '#7C3AED', '#059669', '#D97706']));
          setVal('mPropColSec', pick(['#9AA3A8', '#E2E8F0', '#3F8F3A', '#F5E6C8', '#475569']));
          setVal('mPropColAcc', pick(['#F59E0B', '#B91C1C', '#6BBF59', '#D97706', '#94A3B8']));
          setVal('mPropColGem', pick(['#38BDF8', '#A855F7', '#F43F5E', '#4ADE80', '#FACC15']));
          generateModularProp({}, propSeed);
        });
      }

      function generateProcProp(propKind, seed = ++propSeed) {
        const setPropUi = (fam, sub, c1, c2, c3, c4) => {
          const famEl = document.getElementById('mPropFamily');
          if (famEl) famEl.value = fam;
          syncPropSubtypes(fam, sub);
          const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
          setVal('mPropColMain', c1);
          setVal('mPropColSec', c2);
          setVal('mPropColAcc', c3);
          setVal('mPropColGem', c4);
        };
        if (propKind === 'gen_tree') {
          generateModularTree({}, seed);
          return;
        } else if (propKind === 'gen_rock') {
          setPropUi('rock', (seed & 1) ? 'crystal' : 'boulder', '#6E7685', '#9AA3A8', '#3F8F3A', '#38BDF8');
        } else if (propKind === 'gen_house') {
          setPropUi('house', 'gable', '#E7D5BE', '#6E7685', '#B91C1C', '#FDE68A');
        } else if (propKind === 'gen_chest') {
          setPropUi('chest', 'chest_round', '#8A5A2B', '#9AA3A8', '#F59E0B', '#38BDF8');
        } else if (propKind === 'gen_mushroom') {
          setPropUi('plant', 'mushroom', '#D94F4F', '#F2C9A0', '#6BBF59', '#38BDF8');
        } else if (propKind === 'gen_sword') {
          setPropUi('weapon', 'sword', '#7A4E2D', '#CBD5E1', '#F59E0B', '#38BDF8');
        }
        generateModularProp({}, seed);
      }

      const procPropsBox = document.getElementById('mProcProps');
      if (procPropsBox) {
        procPropsBox.addEventListener('click', (e) => {
          const btn = e.target && e.target.closest ? e.target.closest('[data-genprop]') : null;
          const kind = btn && btn.dataset ? btn.dataset.genprop : null;
          if (!kind) return;
          propSeed++;
          generateProcProp(kind, propSeed);
        });
      }

      // ---------- 8.1 Tree & Flora Studio Modular ----------
      bindRangeLabel('mTreeThick', 'mTreeThickVal');
      bindRangeLabel('mTreeCurve', 'mTreeCurveVal');
      bindRangeLabel('mTreeFlowerPct', 'mTreeFlowerPctVal', '%');
      bindRangeLabel('mTreeFruitPct', 'mTreeFruitPctVal', '%');
      bindRangeLabel('m2dThickness', 'm2dThicknessVal');

      let modTreeSeed = 200;
      function generateModularTree(opts = {}, seed = 201) {
        const rng = makeRng(seed);
        const branchCount = Math.max(1, Math.min(4, parseInt(opts.branchCount ?? document.getElementById('mTreeBranch')?.value ?? '2', 10) || 2));
        const thick = Math.max(1, Math.min(5, parseInt(opts.thick ?? document.getElementById('mTreeThick')?.value ?? '2', 10) || 2));
        const curve = Math.max(0, Math.min(3, parseInt(opts.curve ?? document.getElementById('mTreeCurve')?.value ?? '1', 10) || 0));
        const crownType = String(opts.crownType ?? document.getElementById('mTreeCrown')?.value ?? 'spheres');
        const flowerPct = Math.max(0, Math.min(40, parseInt(opts.flowerPct ?? document.getElementById('mTreeFlowerPct')?.value ?? '0', 10) || 0));
        const fruitPct = Math.max(0, Math.min(30, parseInt(opts.fruitPct ?? document.getElementById('mTreeFruitPct')?.value ?? '0', 10) || 0));
        const colTrunk = String(opts.colTrunk ?? document.getElementById('mTreeColTrunk')?.value ?? '#7C4D2B');
        const colLeaf = String(opts.colLeaf ?? document.getElementById('mTreeColLeaf')?.value ?? '#3F8F3A');
        const colFlower = String(opts.colFlower ?? document.getElementById('mTreeColFlower')?.value ?? '#F472B6');
        const colFruit = String(opts.colFruit ?? document.getElementById('mTreeColFruit')?.value ?? '#EF4444');

        pal = [
          'rgba(0,0,0,0)',
          shadeHex(colTrunk, 0.72), colTrunk, shadeHex(colTrunk, 1.22),
          shadeHex(colLeaf, 0.65), shadeHex(colLeaf, 0.85), colLeaf, shadeHex(colLeaf, 1.24),
          colFlower, shadeHex(colFlower, 1.28),
          shadeHex(colFruit, 0.78), colFruit,
          '#FDE68A', '#FFFFFF', '#6B7280', '#1B1B1B'
        ];
        if (kindSel) kindSel.value = 'foliage';
        if (destrOptsEl) destrOptsEl.style.display = 'none';
        if (document.getElementById('mName')) document.getElementById('mName').value = `arvore_mod_${seed}`;
        curColor = 6;
        const colEl = document.getElementById('mColor');
        if (colEl) colEl.value = pal[curColor];

        for (let z = 0; z < N; z++) vol[z].fill(0);
        const s = N / 24;
        const cx = (N - 1) / 2;
        const cy = (N - 1) / 2;

        const putV = (vx, vy, vz, colIdx) => {
          const ix = Math.round(vx), iy = Math.round(vy), iz = Math.round(vz);
          if (ix < 0 || ix >= N || iy < 0 || iy >= N || iz < 0 || iz >= N) return;
          vol[iz][iy * N + ix] = colIdx;
        };
        const stampSphere = (lx, ly, lz, r, colFn) => {
          const rV = r * s;
          const vx = cx + lx * s, vy = cy + ly * s, vz = lz * s;
          const x0 = Math.max(0, Math.floor(vx - rV - 0.5)), x1 = Math.min(N - 1, Math.ceil(vx + rV + 0.5));
          const y0 = Math.max(0, Math.floor(vy - rV - 0.5)), y1 = Math.min(N - 1, Math.ceil(vy + rV + 0.5));
          const z0 = Math.max(0, Math.floor(vz - rV - 0.5)), z1 = Math.min(N - 1, Math.ceil(vz + rV + 0.5));
          for (let iz = z0; iz <= z1; iz++) {
            for (let iy = y0; iy <= y1; iy++) {
              for (let ix = x0; ix <= x1; ix++) {
                const dx = ix - vx, dy = iy - vy, dz = iz - vz;
                if (dx * dx + dy * dy + dz * dz <= rV * rV + 0.05) {
                  const c = colFn(dx, dy, dz);
                  if (c > 0) vol[iz][iy * N + ix] = c;
                }
              }
            }
          }
        };
        const drawSegment = (p0, p1, r0, r1, bendX, bendY) => {
          const dist = Math.hypot(p1.x - p0.x, p1.y - p0.y, p1.z - p0.z);
          const steps = Math.max(8, Math.ceil(dist * s * 2.4));
          for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const b = Math.sin(t * Math.PI);
            const px = p0.x + (p1.x - p0.x) * t + bendX * b;
            const py = p0.y + (p1.y - p0.y) * t + bendY * b;
            const pz = p0.z + (p1.z - p0.z) * t;
            const r = r0 + (r1 - r0) * t;
            stampSphere(px, py, pz, r, (dx, dy) => (dx + dy < -0.2 ? 3 : dx + dy > 0.4 ? 1 : 2));
          }
        };

        const baseR = 0.65 + thick * 0.48;
        const topR = Math.max(0.55, baseR * 0.54);
        // Raizes radiais na base quando curvatura > 0
        if (curve > 0) {
          const numRoots = 2 + curve;
          const rAng0 = rng() * Math.PI * 2;
          for (let i = 0; i < numRoots; i++) {
            const ang = rAng0 + (i * Math.PI * 2) / numRoots + (rng() - 0.5) * 0.4;
            const reach = baseR + 1.1 + curve * 0.55;
            drawSegment(
              { x: Math.cos(ang) * reach, y: Math.sin(ang) * reach, z: 0.3 },
              { x: Math.cos(ang) * baseR * 0.4, y: Math.sin(ang) * baseR * 0.4, z: 2.2 + curve * 0.6 },
              Math.max(0.55, baseR * 0.42),
              Math.max(0.45, baseR * 0.32),
              0, 0
            );
          }
        }

        const leanAng = rng() * Math.PI * 2;
        const trunkBendX = Math.cos(leanAng) * curve * 0.85;
        const trunkBendY = Math.sin(leanAng) * curve * 0.85;
        const crownAnchors = [];

        if (branchCount === 1) {
          const trunkTop = crownType === 'cones' ? 20.0 : 15.5;
          const tipX = trunkBendX * 0.55, tipY = trunkBendY * 0.55;
          drawSegment(
            { x: 0, y: 0, z: 0 },
            { x: tipX, y: tipY, z: trunkTop },
            baseR, Math.max(0.5, topR * 0.65),
            trunkBendX * 0.5, trunkBendY * 0.5
          );
          if (crownType === 'cones') {
            crownAnchors.push({ x: tipX * 0.5, y: tipY * 0.5, z: 12.5 });
          }
          crownAnchors.push({ x: tipX, y: tipY, z: trunkTop });
        } else {
          const splitZ = 6.8 + rng() * 2.2;
          const splitX = trunkBendX * 0.5;
          const splitY = trunkBendY * 0.5;
          drawSegment(
            { x: 0, y: 0, z: 0 },
            { x: splitX, y: splitY, z: splitZ },
            baseR, topR,
            trunkBendX * 0.45, trunkBendY * 0.45
          );
          const baseAz = rng() * Math.PI * 2;
          for (let b = 0; b < branchCount; b++) {
            const az = baseAz + (b * Math.PI * 2) / branchCount + (rng() - 0.5) * 0.45;
            const reach = (branchCount === 4 ? 5.8 : 4.8) + rng() * 1.8;
            const endZ = (crownType === 'none' ? 16.5 : 13.8) + rng() * 3.2;
            const bx = splitX + Math.cos(az) * reach;
            const by = splitY + Math.sin(az) * reach;
            const bendAmp = (0.6 + curve * 0.55) * (b % 2 === 0 ? 1 : -1);
            const perpX = -Math.sin(az) * bendAmp;
            const perpY = Math.cos(az) * bendAmp;
            drawSegment(
              { x: splitX, y: splitY, z: splitZ - 0.5 },
              { x: bx, y: by, z: endZ },
              topR * 0.84, Math.max(0.48, topR * 0.4),
              perpX, perpY
            );
            crownAnchors.push({ x: bx, y: by, z: endZ });

            if (branchCount === 4 || crownType === 'none') {
              const subT = 0.52 + rng() * 0.2;
              const sx0 = splitX + (bx - splitX) * subT;
              const sy0 = splitY + (by - splitY) * subT;
              const sz0 = splitZ + (endZ - splitZ) * subT;
              const saz = az + (b % 2 === 0 ? 0.75 : -0.75);
              const sReach = 2.6 + rng() * 1.6;
              const sx1 = sx0 + Math.cos(saz) * sReach;
              const sy1 = sy0 + Math.sin(saz) * sReach;
              const sz1 = Math.min(21.5, sz0 + 2.6 + rng() * 2.0);
              drawSegment(
                { x: sx0, y: sy0, z: sz0 },
                { x: sx1, y: sy1, z: sz1 },
                Math.max(0.45, topR * 0.48), 0.42,
                0, 0
              );
              if (branchCount === 4) crownAnchors.push({ x: sx1, y: sy1, z: sz1 });
            }
          }
        }

        // Copa Modular
        const paintLeafLobe = (cxL, cyL, czL, rx, ry, rz, wobblePhase) => {
          const x0 = Math.max(0, Math.floor(cx + (cxL - rx) * s)), x1 = Math.min(N - 1, Math.ceil(cx + (cxL + rx) * s));
          const y0 = Math.max(0, Math.floor(cy + (cyL - ry) * s)), y1 = Math.min(N - 1, Math.ceil(cy + (cyL + ry) * s));
          const z0 = Math.max(0, Math.floor((czL - rz) * s)), z1 = Math.min(N - 1, Math.ceil((czL + rz) * s));
          for (let iz = z0; iz <= z1; iz++) {
            const lz = iz / s;
            const topness = (lz - (czL - rz)) / (2 * rz);
            for (let iy = y0; iy <= y1; iy++) {
              const ly = (iy - cy) / s;
              for (let ix = x0; ix <= x1; ix++) {
                const lx = (ix - cx) / s;
                const wobble = Math.sin(lx * 0.9 + wobblePhase) * Math.cos(ly * 0.9 - wobblePhase) * 0.14;
                const d = ((lx - cxL) / rx) ** 2 + ((ly - cyL) / ry) ** 2 + ((lz - czL) / rz) ** 2 + wobble;
                if (d <= 1.0) {
                  vol[iz][iy * N + ix] = topness > 0.76 ? 7 : (topness > 0.50 ? 6 : (topness > 0.25 ? 5 : 4));
                }
              }
            }
          }
        };

        if (crownType === 'spheres') {
          crownAnchors.forEach((a, idx) => {
            paintLeafLobe(a.x, a.y, a.z + 1.0, 3.8 + rng() * 1.3, 3.8 + rng() * 1.3, 2.9 + rng() * 1.0, idx);
            if (idx < 4) {
              paintLeafLobe(
                a.x + (rng() - 0.5) * 3.0, a.y + (rng() - 0.5) * 3.0, a.z + 2.2,
                2.8 + rng() * 1.0, 2.8 + rng() * 1.0, 2.4 + rng() * 0.8, idx + 7
              );
            }
          });
          paintLeafLobe(trunkBendX * 0.35, trunkBendY * 0.35, 18.2, 4.4, 4.4, 3.2, 99);
        } else if (crownType === 'cones') {
          const tiers = branchCount === 1 ? 4 : 3;
          const baseCz = branchCount === 1 ? 7.0 : 12.0;
          const totalH = branchCount === 1 ? 15.5 : 10.5;
          const cxC = branchCount === 1 ? trunkBendX * 0.45 : 0;
          const cyC = branchCount === 1 ? trunkBendY * 0.45 : 0;
          for (let tIdx = 0; tIdx < tiers; tIdx++) {
            const zBot = baseCz + (tIdx * totalH) / (tiers + 0.6);
            const tierH = totalH * (0.48 - tIdx * 0.05);
            const rMax = (branchCount === 1 ? 8.2 : 8.8) * (1 - tIdx * 0.2);
            const z0 = Math.max(0, Math.floor(zBot * s)), z1 = Math.min(N - 1, Math.ceil((zBot + tierH) * s));
            for (let iz = z0; iz <= z1; iz++) {
              const frac = (iz / s - zBot) / tierH;
              if (frac < 0 || frac > 1) continue;
              const rLim = rMax * (1 - frac * 0.92);
              for (let iy = 0; iy < N; iy++) {
                const ly = (iy - cy) / s - cyC;
                for (let ix = 0; ix < N; ix++) {
                  const lx = (ix - cx) / s - cxC;
                  const ang = Math.atan2(ly, lx);
                  const rad = Math.hypot(lx, ly);
                  const scallop = 1 + 0.13 * Math.cos(5 * ang + tIdx);
                  if (rad <= rLim * scallop) {
                    vol[iz][iy * N + ix] = frac > 0.72 ? 7 : (frac > 0.42 ? 6 : (frac > 0.18 ? 5 : 4));
                  }
                }
              }
            }
          }
        } else if (crownType === 'weeping') {
          const avgX = crownAnchors.reduce((acc, a) => acc + a.x, 0) / crownAnchors.length;
          const avgY = crownAnchors.reduce((acc, a) => acc + a.y, 0) / crownAnchors.length;
          paintLeafLobe(avgX, avgY, 17.2, 7.6, 7.6, 3.8, 3);
          const numStrands = 18;
          for (let k = 0; k < numStrands; k++) {
            const ang = (k / numStrands) * Math.PI * 2 + (rng() - 0.5) * 0.2;
            const rad = 5.2 + rng() * 2.4;
            const sx = avgX + Math.cos(ang) * rad;
            const sy = avgY + Math.sin(ang) * rad;
            const zTop = 16.2 + rng() * 1.5;
            const zBot = 4.2 + rng() * 4.5;
            for (let lz = zBot; lz <= zTop; lz += 0.6) {
              const frac = (lz - zBot) / (zTop - zBot);
              const swayX = sx + Math.sin(lz * 0.4 + k) * 0.35;
              const swayY = sy + Math.cos(lz * 0.4 + k) * 0.35;
              const vx = cx + swayX * s, vy = cy + swayY * s, vz = lz * s;
              const cIdx = frac > 0.7 ? 6 : (frac > 0.35 ? 5 : 4);
              putV(vx, vy, vz, cIdx);
              if (thick >= 2) putV(vx + 1, vy, vz, cIdx);
            }
          }
        } else if (crownType === 'dome') {
          const avgX = crownAnchors.reduce((acc, a) => acc + a.x, 0) / crownAnchors.length;
          const avgY = crownAnchors.reduce((acc, a) => acc + a.y, 0) / crownAnchors.length;
          const maxZ = crownAnchors.reduce((acc, a) => Math.max(acc, a.z), 14);
          paintLeafLobe(avgX, avgY, Math.min(18.5, maxZ + 1.4), 8.6, 8.6, 3.8, 5);
          crownAnchors.forEach((a, idx) => {
            paintLeafLobe(a.x * 0.75, a.y * 0.75, a.z + 0.8, 4.2, 4.2, 2.5, idx + 11);
          });
        }

        // Flores (%) e Frutas (%) na superfície externa da copa
        if (crownType !== 'none' && (flowerPct > 0 || fruitPct > 0)) {
          const surface = [];
          const dirs = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
          for (let iz = 0; iz < N; iz++) {
            for (let iy = 0; iy < N; iy++) {
              for (let ix = 0; ix < N; ix++) {
                const v = vol[iz][iy * N + ix];
                if (v < 4 || v > 7) continue;
                let exposed = false;
                for (let d = 0; d < 6; d++) {
                  const nx = ix + dirs[d][0], ny = iy + dirs[d][1], nz = iz + dirs[d][2];
                  if (nx < 0 || nx >= N || ny < 0 || ny >= N || nz < 0 || nz >= N || vol[nz][ny * N + nx] === 0) {
                    exposed = true;
                    break;
                  }
                }
                if (exposed) {
                  const topExposed = (iz === N - 1 || vol[iz + 1][iy * N + ix] === 0);
                  surface.push({ ix, iy, iz, topExposed });
                }
              }
            }
          }
          // Embaralha determinístico com rng
          for (let i = surface.length - 1; i > 0; i--) {
            const j = Math.floor(rng() * (i + 1));
            const tmp = surface[i]; surface[i] = surface[j]; surface[j] = tmp;
          }
          let cursor = 0;
          if (flowerPct > 0 && surface.length > 0) {
            const nFlowers = Math.max(1, Math.round(surface.length * (flowerPct / 100) * 0.7));
            for (let i = 0; i < surface.length && cursor < nFlowers; i++) {
              const p = surface[i];
              vol[p.iz][p.iy * N + p.ix] = p.topExposed ? 9 : 8;
              cursor++;
            }
          }
          if (fruitPct > 0 && surface.length > cursor) {
            const nFruits = Math.max(1, Math.round(surface.length * (fruitPct / 100) * 0.55));
            let placed = 0;
            for (let i = cursor; i < surface.length && placed < nFruits; i++) {
              const p = surface[i];
              if (!p.topExposed || i + (nFruits - placed) >= surface.length) {
                vol[p.iz][p.iy * N + p.ix] = rng() > 0.35 ? 11 : 10;
                placed++;
              }
            }
          }
        }

        voxCache = null;
        renderPalette();
        drawEdit();
        say(`Árvore modular (${branchCount} galhos, copa "${crownType}") gerada (seed ${seed})!`);
      }

      const btnModTree = document.getElementById('mBtnGenModularTree');
      if (btnModTree) {
        btnModTree.addEventListener('click', () => {
          modTreeSeed++;
          generateModularTree({}, modTreeSeed);
        });
      }
      const btnVaryTree = document.getElementById('mBtnVaryTree');
      if (btnVaryTree) {
        btnVaryTree.addEventListener('click', () => {
          modTreeSeed++;
          generateModularTree({}, modTreeSeed);
        });
      }
      ['mTreeBranch', 'mTreeThick', 'mTreeCurve', 'mTreeCrown', 'mTreeFlowerPct', 'mTreeFruitPct', 'mTreeColTrunk', 'mTreeColLeaf', 'mTreeColFlower', 'mTreeColFruit'].forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        const evName = (el.type === 'range' || el.type === 'color') ? 'input' : 'change';
        el.addEventListener(evName, () => generateModularTree({}, modTreeSeed));
      });

      // ---------- 8.2 Conversor Matemático 2D -> 3D (Sem IA) ----------
      const f2dCv = document.getElementById('m2dFrontCanvas');
      const s2dCv = document.getElementById('m2dSideCanvas');

      function draw2dCanvas(cv, buf) {
        if (!cv || typeof cv.getContext !== 'function') return;
        const ctx = cv.getContext('2d');
        if (!ctx) return;
        const W = cv.width, H = cv.height;
        const cs = W / N;
        ctx.clearRect(0, 0, W, H);
        for (let row = 0; row < N; row++) {
          const z = N - 1 - row;
          for (let col = 0; col < N; col++) {
            const v = buf[z * N + col];
            ctx.fillStyle = v > 0 ? (pal[v] || '#FFFFFF') : (((row + col) & 1) ? '#1F1B19' : '#171412');
            ctx.fillRect(col * cs, row * cs, cs + 0.3, cs + 0.3);
          }
        }
        ctx.strokeStyle = 'rgba(251, 191, 36, 0.25)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(W / 2, 0);
        ctx.lineTo(W / 2, H);
        ctx.stroke();
      }
      function drawAll2d() {
        draw2dCanvas(f2dCv, front2D);
        draw2dCanvas(s2dCv, side2D);
      }

      function bind2dCanvasPaint(cv, getBuf) {
        if (!cv) return;
        let active2d = false;
        let erase2d = false;
        const cell2d = (e) => {
          const r = cv.getBoundingClientRect();
          const gx = Math.floor(((e.clientX - r.left) / r.width) * N);
          const row = Math.floor(((e.clientY - r.top) / r.height) * N);
          if (gx < 0 || gx >= N || row < 0 || row >= N) return null;
          return { gx, gz: N - 1 - row };
        };
        const paint2d = (c) => {
          if (!c) return;
          const buf = getBuf();
          if (tool === 'pick' && !erase2d) {
            const v = buf[c.gz * N + c.gx];
            if (v > 0) {
              curColor = v;
              if (document.getElementById('mColor')) document.getElementById('mColor').value = pal[v];
              renderPalette();
            }
            return;
          }
          const nextV = (erase2d || tool === 'eraser') ? 0 : curColor;
          if (tool === 'fill' && !erase2d) {
            const target = buf[c.gz * N + c.gx];
            if (target !== nextV) {
              const st = [[c.gx, c.gz]];
              while (st.length) {
                const [px, pz] = st.pop();
                if (px < 0 || px >= N || pz < 0 || pz >= N) continue;
                const idx = pz * N + px;
                if (buf[idx] !== target) continue;
                buf[idx] = nextV;
                st.push([px + 1, pz], [px - 1, pz], [px, pz + 1], [px, pz - 1]);
              }
            }
            drawAll2d();
            return;
          }
          buf[c.gz * N + c.gx] = nextV;
          drawAll2d();
        };
        cv.addEventListener('contextmenu', (e) => e.preventDefault());
        cv.addEventListener('pointerdown', (e) => {
          active2d = true;
          erase2d = e.button === 2 || e.buttons === 2;
          if (cv.setPointerCapture) cv.setPointerCapture(e.pointerId);
          paint2d(cell2d(e));
        });
        cv.addEventListener('pointermove', (e) => {
          if (!active2d) return;
          paint2d(cell2d(e));
        });
        cv.addEventListener('pointerup', () => { active2d = false; erase2d = false; });
      }
      bind2dCanvasPaint(f2dCv, () => front2D);
      bind2dCanvasPaint(s2dCv, () => side2D);

      const btn2dFromSlice = document.getElementById('m2dFromSlice');
      if (btn2dFromSlice) {
        btn2dFromSlice.addEventListener('click', () => {
          const layer = vol[curZ];
          for (let y = 0; y < N; y++) {
            const z = N - 1 - y;
            for (let x = 0; x < N; x++) front2D[z * N + x] = layer[y * N + x];
          }
          drawAll2d();
          say(`Fatia Z=${curZ} copiada para a Vista Frontal 2D!`);
        });
      }
      const btn2dCopySide = document.getElementById('m2dCopyFrontToSide');
      if (btn2dCopySide) {
        btn2dCopySide.addEventListener('click', () => {
          side2D.set(front2D);
          drawAll2d();
          say('Vista Frontal copiada para Vista Lateral!');
        });
      }
      const btn2dClear = document.getElementById('m2dClear');
      if (btn2dClear) {
        btn2dClear.addEventListener('click', () => {
          front2D.fill(0);
          side2D.fill(0);
          drawAll2d();
          say('Grades 2D limpas.');
        });
      }
      const btn2dImport = document.getElementById('m2dImportImg');
      const file2dImg = document.getElementById('m2dFileImg');
      if (btn2dImport && file2dImg) {
        btn2dImport.addEventListener('click', () => file2dImg.click());
        file2dImg.addEventListener('change', (e) => {
          const file = e.target.files && e.target.files[0];
          if (!file) return;
          const reader = new FileReader();
          reader.onload = () => {
            const img = new Image();
            img.onerror = () => say(`Falha ao carregar imagem "${file.name}".`, false);
            img.onload = () => {
              const tmp = document.createElement('canvas');
              tmp.width = N; tmp.height = N;
              const tCtx = tmp.getContext('2d');
              tCtx.imageSmoothingEnabled = false;
              tCtx.clearRect(0, 0, N, N);
              const sc = Math.min(N / Math.max(1, img.width), N / Math.max(1, img.height));
              const dw = Math.max(1, Math.round(img.width * sc));
              const dh = Math.max(1, Math.round(img.height * sc));
              const dx = Math.floor((N - dw) / 2);
              const dy = N - dh;
              tCtx.drawImage(img, dx, dy, dw, dh);
              const data = tCtx.getImageData(0, 0, N, N).data;
              let sideUsed = false;
              for (let i = 0; i < side2D.length; i++) if (side2D[i] > 0) { sideUsed = true; break; }
              if (!sideUsed) {
                const baseKey = palPresetEl?.value || 'default';
                pal = (PAL_PRESETS[baseKey] || DEFAULT_PAL).slice();
              }
              front2D.fill(0);
              const h2 = (v) => Math.max(0, Math.min(255, v)).toString(16).padStart(2, '0');
              for (let row = 0; row < N; row++) {
                const gz = N - 1 - row;
                for (let col = 0; col < N; col++) {
                  const p = (row * N + col) * 4;
                  if (data[p + 3] < 64) continue;
                  const hex = `#${h2(data[p])}${h2(data[p + 1])}${h2(data[p + 2])}`;
                  front2D[gz * N + col] = findOrAddPalColor(hex);
                }
              }
              renderPalette();
              drawAll2d();
              say(`Imagem "${file.name}" importada para Vista Frontal ${N}×${N}!`);
            };
            img.src = reader.result;
          };
          reader.readAsDataURL(file);
          e.target.value = '';
        });
      }

      function load2dPreset(presetName) {
        front2D.fill(0);
        side2D.fill(0);
        const s = N / 24;
        const cx = (N - 1) / 2;
        if (presetName === 'sword') {
          applyPresetAndKind('default', 'pickable', 'espada_2d3d');
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let x = 0; x < N; x++) {
              const lx = (x - cx) / s;
              let c = 0;
              if (lz >= 1 && lz < 3.2 && Math.hypot(lx, lz - 2.0) <= 1.8) c = 13;
              else if (lz >= 3 && lz < 7 && Math.abs(lx) <= 1.0) c = 4;
              else if (lz >= 7 && lz < 8.8 && Math.abs(lx) <= 4.6) c = 13;
              else if (lz >= 8.8 && lz <= 22.2) {
                const tipTaper = lz > 18.5 ? Math.max(0.4, 2.2 - (lz - 18.5) * 0.52) : 2.2;
                if (Math.abs(lx) <= tipTaper) c = Math.abs(lx) <= 0.9 ? 14 : 11;
              }
              if (c > 0) front2D[z * N + x] = c;
            }
          }
        } else if (presetName === 'vase') {
          applyPresetAndKind('default', 'decor', 'vaso_2d3d');
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let x = 0; x < N; x++) {
              const ax = Math.abs((x - cx) / s);
              let c = 0;
              if (lz >= 1 && lz < 2.6 && ax <= 4.2) c = 10;
              else if (lz >= 2.6 && lz < 13.5) {
                const belly = 3.2 + Math.sin(((lz - 2.6) / 10.9) * Math.PI) * 4.4;
                if (ax <= belly) c = ax > belly - 1.2 ? 2 : (lz < 9.5 ? 12 : 14);
              } else if (lz >= 13.5 && lz < 17.5 && ax <= 2.4) {
                c = ax > 1.2 ? 2 : 14;
              } else if (lz >= 17.5 && lz < 19.3 && ax <= 3.6) {
                c = 13;
              } else if (lz >= 19.3 && lz <= 21.5 && ax <= 1.8) {
                c = 6;
              }
              if (c > 0) front2D[z * N + x] = c;
            }
          }
        } else {
          // creature: silhueta bichinho Frente + Lado
          applyPresetAndKind('character', 'solid', 'bichinho_2d3d');
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let x = 0; x < N; x++) {
              const lx = (x - cx) / s;
              let cf = 0;
              if (lz >= 1 && lz < 5 && Math.abs(Math.abs(lx) - 2.6) <= 1.3) cf = 4;
              else if (lz >= 4.5 && lz < 12.5 && (lx / 5.2) ** 2 + ((lz - 8.5) / 4.2) ** 2 <= 1) cf = Math.abs(lx) < 2.2 ? 1 : 3;
              if (lz >= 11.5 && lz <= 18.8 && (lx / 4.8) ** 2 + ((lz - 15.0) / 3.8) ** 2 <= 1) {
                cf = (lz >= 14.5 && lz <= 16.0 && Math.abs(Math.abs(lx) - 1.8) <= 0.65) ? 6 : 3;
              } else if (lz >= 17.5 && lz <= 21.5 && Math.abs(Math.abs(lx) - 3.0) <= 1.1) {
                cf = 4;
              }
              if (cf > 0) front2D[z * N + x] = cf;

              const ly = (x - cx) / s; // eixo horizontal = Y na Vista Lateral
              let cs = 0;
              if (lz >= 1 && lz < 5 && (Math.abs(ly - 2.4) <= 1.3 || Math.abs(ly + 2.4) <= 1.3)) cs = 4;
              else if (lz >= 4.5 && lz < 12.5 && (ly / 5.4) ** 2 + ((lz - 8.5) / 4.2) ** 2 <= 1) cs = 3;
              if (lz >= 6.5 && lz <= 12.0 && ly < -4.2 && ly >= -8.8 && Math.abs(lz - (8.0 + (-ly - 4.2) * 0.8)) <= 1.2) cs = 1;
              if (lz >= 11.5 && lz <= 18.8 && ((ly - 1.0) / 4.4) ** 2 + ((lz - 15.0) / 3.8) ** 2 <= 1) cs = 3;
              if (lz >= 12.5 && lz <= 15.2 && ly >= 4.2 && ly <= 7.2) cs = (ly >= 6.2 && lz >= 14.0) ? 6 : 1;
              if (lz >= 17.5 && lz <= 21.5 && Math.abs(ly - 0.2) <= 1.2) cs = 4;
              if (cs > 0) side2D[z * N + x] = cs;
            }
          }
        }
        renderPalette();
        drawAll2d();
        say(`Silhueta 2D "${presetName}" carregada!`);
      }

      const btn2dLoadPreset = document.getElementById('m2dLoadPreset');
      if (btn2dLoadPreset) {
        btn2dLoadPreset.addEventListener('click', () => {
          const p = document.getElementById('m2dPreset')?.value || 'sword';
          load2dPreset(p);
        });
      }

      function computeEDT2D(buf) {
        const dist = new Float32Array(N * N);
        const boundaryEmpty = [];
        for (let ez = -1; ez <= N; ez++) {
          for (let ex = -1; ex <= N; ex++) {
            const inB = ex >= 0 && ex < N && ez >= 0 && ez < N;
            if (inB && buf[ez * N + ex] > 0) continue;
            let touchesFilled = false;
            for (let dz = -1; dz <= 1 && !touchesFilled; dz++) {
              for (let dx = -1; dx <= 1; dx++) {
                const nx = ex + dx, nz = ez + dz;
                if (nx >= 0 && nx < N && nz >= 0 && nz < N && buf[nz * N + nx] > 0) {
                  touchesFilled = true;
                  break;
                }
              }
            }
            if (touchesFilled) boundaryEmpty.push(ex, ez);
          }
        }
        let dMax = 0;
        for (let z = 0; z < N; z++) {
          for (let x = 0; x < N; x++) {
            const idx = z * N + x;
            if (buf[idx] === 0) continue;
            let best2 = Infinity;
            for (let k = 0; k < boundaryEmpty.length; k += 2) {
              const dx = x - boundaryEmpty[k], dz = z - boundaryEmpty[k + 1];
              const d2 = dx * dx + dz * dz;
              if (d2 < best2) best2 = d2;
            }
            const d = Math.sqrt(best2);
            dist[idx] = d;
            if (d > dMax) dMax = d;
          }
        }
        return { dist, dMax };
      }

      function convert2dTo3d(modeOpt, thickOpt) {
        const mode = String(modeOpt ?? document.getElementById('m2dMode')?.value ?? 'edt_blade');
        const thickness = Math.max(2, Math.min(N, parseInt(thickOpt ?? document.getElementById('m2dThickness')?.value ?? '10', 10) || 10));

        let hasFront = false;
        for (let i = 0; i < front2D.length; i++) if (front2D[i] > 0) { hasFront = true; break; }
        if (!hasFront) {
          say('Vista Frontal 2D vazia: desenhe ou carregue uma silhueta antes de converter.', false);
          return { ok: false, voxels: 0 };
        }
        if (mode === 'visual_hull') {
          let hasSide = false;
          for (let i = 0; i < side2D.length; i++) if (side2D[i] > 0) { hasSide = true; break; }
          if (!hasSide) {
            say('Vista Lateral 2D vazia: desenhe a lateral ou use "Frente → Lado" para Cruzamento.', false);
            return { ok: false, voxels: 0 };
          }
        }

        for (let z = 0; z < N; z++) vol[z].fill(0);
        const yc = Math.floor((N - 1) / 2);
        const xc = (N - 1) / 2;
        const ycF = (N - 1) / 2;

        if (mode === 'edt_blade' || mode === 'edt_organic') {
          const { dist, dMax } = computeEDT2D(front2D);
          const maxHalfY = Math.max(1, Math.floor(thickness / 2));
          for (let z = 0; z < N; z++) {
            for (let x = 0; x < N; x++) {
              const col = front2D[z * N + x];
              if (col === 0) continue;
              const d = dist[z * N + x];
              const orgNorm = dMax > 1 ? Math.max(0, d - 1) / (dMax - 1) : 0.25;
              const halfY = mode === 'edt_blade'
                ? Math.min(maxHalfY, Math.max(0, Math.floor(d - 0.5)))
                : Math.round(maxHalfY * Math.sqrt(Math.min(1, orgNorm)));
              const y0 = Math.max(0, yc - halfY);
              const y1 = Math.min(N - 1, yc + halfY);
              for (let y = y0; y <= y1; y++) vol[z][y * N + x] = col;
            }
          }
        } else if (mode === 'lathe') {
          for (let z = 0; z < N; z++) {
            for (let y = 0; y < N; y++) {
              for (let x = 0; x < N; x++) {
                const r = Math.floor(Math.hypot(x - xc, y - ycF));
                const ixR = Math.ceil(xc) + r;
                const ixL = Math.floor(xc) - r;
                const cR = (ixR >= 0 && ixR < N) ? front2D[z * N + ixR] : 0;
                const cL = (ixL >= 0 && ixL < N) ? front2D[z * N + ixL] : 0;
                const col = x >= xc ? (cR || cL) : (cL || cR);
                if (col > 0) vol[z][y * N + x] = col;
              }
            }
          }
        } else if (mode === 'visual_hull') {
          for (let z = 0; z < N; z++) {
            let xMin = N, xMax = -1, yMin = N, yMax = -1;
            for (let i = 0; i < N; i++) {
              if (front2D[z * N + i] > 0) { if (i < xMin) xMin = i; if (i > xMax) xMax = i; }
              if (side2D[z * N + i] > 0) { if (i < yMin) yMin = i; if (i > yMax) yMax = i; }
            }
            if (xMax < xMin || yMax < yMin) continue;
            const wX = xMax - xMin + 1;
            const wY = yMax - yMin + 1;
            for (let y = yMin; y <= yMax; y++) {
              const cyCol = side2D[z * N + y];
              if (cyCol === 0) continue;
              const dY = Math.min(y - yMin, yMax - y);
              for (let x = xMin; x <= xMax; x++) {
                const cxCol = front2D[z * N + x];
                if (cxCol === 0) continue;
                if (wX >= 4 && wY >= 4 && (x === xMin || x === xMax) && (y === yMin || y === yMax)) continue;
                const dX = Math.min(x - xMin, xMax - x);
                vol[z][y * N + x] = (dX < dY) ? cyCol : cxCol;
              }
            }
          }
        }

        let count = 0;
        for (let z = 0; z < N; z++) for (let i = 0; i < vol[z].length; i++) if (vol[z][i] > 0) count++;
        voxCache = null;
        drawEdit();
        say(`Conversão "${mode}" gerou ${count} voxels 3D!`);
        return { ok: true, mode, voxels: count };
      }

      const btnConvert2d = document.getElementById('mBtnConvert2d3d');
      if (btnConvert2d) {
        btnConvert2d.addEventListener('click', () => convert2dTo3d());
      }

      // Sub-abas da barra direita do Modelador
      const rightTabsBox = document.getElementById('mRightTabs');
      if (rightTabsBox) {
        const panelMap = { chars: 'mTabChars', props: 'mTabProps', trees: 'mTabTrees', conv2d: 'mTabConv2d' };
        rightTabsBox.addEventListener('click', (e) => {
          const btn = e.target && e.target.closest ? e.target.closest('[data-mtab]') : null;
          const tab = btn && btn.dataset ? btn.dataset.mtab : null;
          if (!tab || !panelMap[tab]) return;
          rightTabsBox.querySelectorAll('.m-rtab-btn').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
          Object.values(panelMap).forEach((pid) => {
            const p = document.getElementById(pid);
            if (p) p.classList.remove('active');
          });
          const targetP = document.getElementById(panelMap[tab]);
          if (targetP) targetP.classList.add('active');
          if (tab === 'conv2d') drawAll2d();
        });
      }

      const btnOpenSide = document.getElementById('btnOpenModelerSide');
      if (btnOpenSide) {
        btnOpenSide.addEventListener('click', () => {
          const tm = document.getElementById('btnTabModeler');
          if (tm) tm.click();
        });
      }

      function downloadJson(filename, obj) {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob([JSON.stringify(obj)], { type: 'application/json' }));
        a.download = filename;
        a.click();
      }

      document.getElementById('mBtnExport').addEventListener('click', () => {
        const slices = currentSlices();
        if (!slices) { say('Modelo vazio: nada para exportar.', false); return; }
        const name = document.getElementById('mName').value.trim() || 'modelo';
        const kind = kindSel.value;
        const hp = parseInt(document.getElementById('mHp')?.value || '3', 10) || 3;
        const dropKey = document.getElementById('mDropKey')?.value || 'stone_chunk';
        // formato compatível com assets/voxels (palette + slices em base-36)
        downloadJson(`${slug(name)}.model.json`, {
          name, size: N, palette: pal, slices,
          kind, solid: kind === 'solid' || kind === 'destructible' || kind === 'fire',
          hp, dropKey
        });
        say('Modelo exportado.');
      });

      document.getElementById('mBtnImport').addEventListener('click', () => document.getElementById('mFileImport').click());
      document.getElementById('mFileImport').addEventListener('change', (e) => {
        const f = e.target.files[0];
        if (!f) return;
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const d = JSON.parse(reader.result);
            const slices = d.slices;
            if (!Array.isArray(slices) || !slices.length) throw new Error('arquivo sem "slices"');
            const firstRow = typeof decodeRLERow === 'function' ? decodeRLERow(slices[0][0]) : slices[0][0];
            const size = slices[0].length;
            if (![16, 24, 32].includes(size) || firstRow.length !== size) throw new Error(`grade ${size} não suportada (use 16, 24 ou 32 quadrada)`);
            newVolume(size);
            document.getElementById('mSize').value = String(size);
            pal = (d.palette || d.pal || DEFAULT_PAL).slice(0, 36);
            for (let z = 0; z < Math.min(N, slices.length); z++)
              for (let y = 0; y < N; y++) {
                const rawRow = (slices[z] && slices[z][y]) || '';
                const row = typeof decodeRLERow === 'function' ? decodeRLERow(rawRow) : rawRow;
                for (let x = 0; x < N; x++) vol[z][y * N + x] = parseInt(row[x], 36) || 0;
              }
            if (d.name) document.getElementById('mName').value = d.name;
            const impKind = d.kind || d.category || (d.solid ? 'solid' : 'decor');
            kindSel.value = impKind;
            if (destrOptsEl) destrOptsEl.style.display = impKind === 'destructible' ? 'flex' : 'none';
            if (d.hp && document.getElementById('mHp')) document.getElementById('mHp').value = String(d.hp);
            if (d.dropKey && document.getElementById('mDropKey')) document.getElementById('mDropKey').value = d.dropKey;
            curColor = Math.min(curColor, pal.length - 1) || 1;
            renderPalette();
            drawEdit();
            drawAll2d();
            say('Modelo importado para edição.');
          } catch (err) {
            say('Falha ao importar: ' + err.message, false);
          }
        };
        reader.readAsText(f);
        e.target.value = '';
      });

      // ---------- Abas Mundo <-> Modelador ----------
      const workspace = document.querySelector('.workspace');
      const tabW = document.getElementById('btnTabWorld');
      const tabM = document.getElementById('btnTabModeler');
      tabW.addEventListener('click', () => {
        view.classList.remove('show');
        document.body.classList.remove('in-modeler');
        workspace.style.display = 'flex';
        tabW.className = 'mode-btn active-edit';
        tabM.className = 'mode-btn';
        window.dispatchEvent(new Event('resize'));
      });
      tabM.addEventListener('click', () => {
        workspace.style.display = 'none';
        view.classList.add('show');
        document.body.classList.add('in-modeler');
        tabM.className = 'mode-btn active-edit';
        tabW.className = 'mode-btn';
        drawEdit();
        drawAll2d();
      });

      // ---------- API para o Studio de Mundo ----------
      window.StudioModeler = {
        exportAssets: () => customAssets.map((a) => ({ ...a })),
        importAssets: (list) => { (list || []).forEach((a) => { try { registerAsset(a); } catch (e) { console.error(e); } }); },
        registerAsset,
        generateCharacter,
        generateModularProp,
        generateProcProp,
        generateModularTree,
        PROP_SUBTYPES,
        convert2dTo3d,
        load2dPreset,
        get2dBuffers: () => ({ front2D, side2D }),
        getPalette: () => pal,
        getSize: () => N,
        getVol: () => vol,
        getZ: () => curZ,
        setZ,
        setTool: (t) => { tool = t; },
        applyCell: (x, y) => applyTool({ x, y }),
        getPreviewZoom: () => previewZoom,
        setPreviewZoom,
        getEditZoom: () => editZoom,
        setEditZoom,
        getEditPan: () => ({ x: editPanX, y: editPanY }),
        cellAt
      };

      // modelo inicial: uma "caixa de madeira" simples para o usuário ver o fluxo funcionando
      newVolume(24);
      for (let z = 0; z < 8; z++) for (let y = 8; y < 16; y++) for (let x = 8; x < 16; x++) {
        const edge = (x === 8 || x === 15 || y === 8 || y === 15);
        vol[z][y * N + x] = edge || z === 0 || z === 7 ? 7 : 6;
      }
      renderPalette();
      drawEdit();
      drawAll2d();
    })();

