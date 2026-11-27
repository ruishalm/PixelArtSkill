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
      const customAssets = []; // { key, name, size, pal, slices, kind, solid, hp, dropKey }

      function newVolume(size) {
        N = size;
        vol = Array.from({ length: N }, () => new Uint8Array(N * N));
        front2D = new Uint8Array(N * N);
        side2D = new Uint8Array(N * N);
        curZ = 0;
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
      const cell = () => editCv.width / N;

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
        const cs = cell();
        const x = Math.floor(((e.clientX - r.left) / r.width) * editCv.width / cs);
        const y = Math.floor(((e.clientY - r.top) / r.height) * editCv.height / cs);
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

      editCv.addEventListener('pointerdown', (e) => {
        painting = true;
        editCv.setPointerCapture(e.pointerId);
        applyTool(cellAt(e));
      });
      editCv.addEventListener('pointermove', (e) => {
        hover = cellAt(e);
        if (painting && tool !== 'fill' && tool !== 'pick') applyTool(hover);
        else drawEdit();
      });
      editCv.addEventListener('pointerup', () => { painting = false; });
      editCv.addEventListener('pointerleave', () => { hover = null; drawEdit(); });

      function drawEdit() {
        const cs = cell();
        eCtx.clearRect(0, 0, editCv.width, editCv.height);
        for (let y = 0; y < N; y++) {
          for (let x = 0; x < N; x++) {
            eCtx.fillStyle = ((x + y) & 1) ? '#1F1B19' : '#171412';
            eCtx.fillRect(x * cs, y * cs, cs, cs);
          }
        }
        if (document.getElementById('mOnion').checked && curZ > 0) {
          eCtx.globalAlpha = 0.35;
          const below = vol[curZ - 1];
          for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
            const v = below[y * N + x];
            if (v > 0) { eCtx.fillStyle = pal[v]; eCtx.fillRect(x * cs, y * cs, cs, cs); }
          }
          eCtx.globalAlpha = 1;
        }
        const layer = vol[curZ];
        for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
          const v = layer[y * N + x];
          if (v > 0) { eCtx.fillStyle = pal[v]; eCtx.fillRect(x * cs, y * cs, cs, cs); }
        }
        eCtx.strokeStyle = 'rgba(255,255,255,0.06)';
        eCtx.lineWidth = 1;
        eCtx.beginPath();
        for (let i = 0; i <= N; i++) {
          eCtx.moveTo(i * cs + 0.5, 0); eCtx.lineTo(i * cs + 0.5, editCv.height);
          eCtx.moveTo(0, i * cs + 0.5); eCtx.lineTo(editCv.width, i * cs + 0.5);
        }
        eCtx.stroke();
        if (hover) {
          eCtx.strokeStyle = '#FBBF24';
          eCtx.lineWidth = 2;
          eCtx.strokeRect(hover.x * cs + 1, hover.y * cs + 1, cs - 2, cs - 2);
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

      // ---------- Preview 3D (mesma ideia do sprite-stacking: camadas giradas e empilhadas) ----------
      prevCv.addEventListener('pointerdown', (e) => { dragRotX = e.clientX; prevCv.setPointerCapture(e.pointerId); });
      prevCv.addEventListener('pointermove', (e) => {
        if (dragRotX === null) return;
        angle -= (e.clientX - dragRotX) * 0.012;
        dragRotX = e.clientX;
      });
      prevCv.addEventListener('pointerup', () => { dragRotX = null; });

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
        if (document.getElementById('mAutoSpin').checked && dragRotX === null) angle += 0.012;
        const list = voxCache || buildVoxList();
        const W = prevCv.width, H = prevCv.height;
        pCtx.clearRect(0, 0, W, H);
        const k = Math.max(3, Math.floor(180 / N) + 1);
        const cx = W / 2;
        const baseY = H * 0.78;
        const squash = 0.5;
        const cosA = Math.cos(angle), sinA = Math.sin(angle);
        const c = (N - 1) / 2;

        // chão
        pCtx.fillStyle = 'rgba(255,255,255,0.05)';
        pCtx.beginPath();
        pCtx.ellipse(cx, baseY + 2, N * k * 0.62, N * k * 0.62 * squash, 0, 0, Math.PI * 2);
        pCtx.fill();

        const items = [];
        for (let i = 0; i < list.length; i++) {
          const o = list[i];
          const rx = (o.x - c) * cosA - (o.y - c) * sinA;
          const ry = (o.x - c) * sinA + (o.y - c) * cosA;
          items.push({ rx, ry, z: o.z, v: o.v });
        }
        items.sort((a, b) => (a.z - b.z) || (a.ry - b.ry));

        if (document.getElementById('mRefHuman').checked) {
          // silhueta de referência: humanoide 28u × 8u (mesma unidade voxel)
          const hx = cx - N * k * 0.75;
          pCtx.fillStyle = 'rgba(148,163,184,0.45)';
          pCtx.fillRect(hx, baseY - 28 * k * 0.9, 8 * k, 28 * k * 0.9);
          pCtx.fillStyle = 'rgba(203,213,225,0.7)';
          pCtx.font = '10px sans-serif';
          pCtx.fillText('28u', hx, baseY - 28 * k * 0.9 - 3);
        }

        for (let i = 0; i < items.length; i++) {
          const o = items[i];
          pCtx.fillStyle = pal[o.v];
          pCtx.fillRect(Math.round(cx + o.rx * k), Math.round(baseY + o.ry * k * squash - o.z * k * 0.9), k + 0.5, k * 0.9 + 1);
        }
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

      let charSeed = 1;
      function generateCharacter(charType, headStyle, seed) {
        const rng = makeRng(seed);
        const vary = seed > 1;
        applyPresetAndKind('character', 'avatar', `char_${charType}`);
        for (let z = 0; z < N; z++) vol[z].fill(0);

        const skinOpts = [1, 2, 3];
        const shirtOpts = [8, 10, 12, 14, 13, 15];
        const pantsOpts = [9, 5, 4, 11];
        const hairOpts = [4, 5, 6, 13, 10, 14, 15];
        const pick = (arr, def) => vary ? arr[Math.floor(rng() * arr.length)] : def;

        const skinCol = pick(skinOpts, 1);
        const skinShade = skinCol === 1 ? 2 : (skinCol === 2 ? 3 : 4);
        const shirtCol = pick(shirtOpts, 8);
        const pantsCol = pick(pantsOpts, 9);
        const hairCol = pick(hairOpts, 4);
        const bootCol = 5;
        const eyeCol = 6;
        const trimCol = vary ? pick([13, 10, 7, 14], 13) : 13;
        const monMain = vary ? pick([12, 14, 15, 10, 9], 12) : 12;
        const monDark = monMain === 12 ? 9 : (monMain === 14 ? 11 : 5);
        const furMain = vary ? pick([3, 4, 13, 15, 10], 3) : 3;
        const furLight = furMain === 3 ? 1 : 7;
        const furDark = furMain === 3 ? 4 : 5;

        const s = N / 24;
        const cx = (N - 1) / 2;
        const cy = (N - 1) / 2;
        const hasBelt = vary ? rng() > 0.25 : true;
        const hasCape = vary && rng() > 0.6;
        const monsterEyeCol = vary ? pick([13, 10, 7], 13) : 13;

        // Âncoras da cabeça para encaixar qualquer acessório (frente = +ly)
        let headTopZ = 19.5, headCenterZ = 16.5, headCenterY = 0, headBackY = -2.8, headFrontY = 2.8, headRx = 3.1;
        if (charType === 'chibi') {
          headTopZ = 18.8; headCenterZ = 14.2; headCenterY = 0; headBackY = -4.4; headFrontY = 4.4; headRx = 5.0;
        } else if (charType === 'quadruped') {
          headTopZ = 14.8; headCenterZ = 11.4; headCenterY = 4.2; headBackY = 0.8; headFrontY = 7.6; headRx = 3.5;
        } else if (charType === 'monster') {
          headTopZ = 18.8; headCenterZ = 15.8; headCenterY = 0.5; headBackY = -2.5; headFrontY = 3.5; headRx = 3.8;
        }

        for (let z = 0; z < N; z++) {
          const lz = z / s;
          const layer = vol[z];
          for (let y = 0; y < N; y++) {
            const ly = (y - cy) / s;
            for (let x = 0; x < N; x++) {
              const lx = (x - cx) / s;
              let c = 0;

              if (charType === 'humanoid') {
                if (lz < 2.0) {
                  if (Math.abs(Math.abs(lx) - 2.3) <= 1.35 && ly >= -1.5 && ly <= 2.3) c = bootCol;
                } else if (lz < 7.0) {
                  if (Math.abs(Math.abs(lx) - 2.2) <= 1.2 && Math.abs(ly) <= 1.5) c = pantsCol;
                } else if (lz < 13.5) {
                  if (Math.abs(lx) <= 3.6 && Math.abs(ly) <= 2.0) {
                    c = shirtCol;
                    if (hasBelt && lz < 8.2) c = (Math.abs(lx) <= 0.8 && ly > 1.2) ? trimCol : bootCol;
                    else if (lz >= 12.2 && Math.abs(lx) <= 1.5 && ly > 1.2) c = trimCol;
                  } else if (Math.abs(lx) >= 3.8 && Math.abs(lx) <= 5.4 && Math.abs(ly) <= 1.3 && lz < 13.0) {
                    c = lz < 9.2 ? skinCol : shirtCol;
                  } else if (hasCape && ly < -2.0 && ly >= -3.1 && Math.abs(lx) <= 3.1 && lz >= 5.0 && lz < 13.2) {
                    c = trimCol;
                  }
                } else if (lz < 19.5) {
                  if (Math.abs(lx) <= 3.1 && Math.abs(ly) <= 2.8) {
                    const corner = Math.abs(lx) > 2.5 && Math.abs(ly) > 2.2 && lz > 17.8;
                    if (!corner) {
                      c = lz < 14.3 ? skinShade : skinCol;
                      if (lz >= 15.3 && lz <= 16.8 && ly >= 2.0 && Math.abs(Math.abs(lx) - 1.4) <= 0.6) c = eyeCol;
                    }
                  }
                }
              } else if (charType === 'chibi') {
                if (lz < 1.6) {
                  if (Math.abs(Math.abs(lx) - 2.1) <= 1.3 && ly >= -1.2 && ly <= 2.0) c = bootCol;
                } else if (lz < 4.5) {
                  if (Math.abs(Math.abs(lx) - 2.0) <= 1.1 && Math.abs(ly) <= 1.3) c = pantsCol;
                } else if (lz < 9.5) {
                  if (Math.abs(lx) <= 3.3 && Math.abs(ly) <= 2.0) {
                    c = (hasBelt && lz < 5.6) ? bootCol : shirtCol;
                    if (lz >= 8.2 && Math.abs(lx) <= 1.2 && ly > 1.2) c = trimCol;
                  } else if (Math.abs(lx) >= 3.4 && Math.abs(lx) <= 4.9 && Math.abs(ly) <= 1.2 && lz >= 5.0 && lz < 9.0) {
                    c = lz < 6.4 ? skinCol : shirtCol;
                  }
                } else if (lz < 18.8) {
                  const e = (lx / 5.1) ** 2 + (ly / 4.4) ** 2 + ((lz - 14.2) / 4.7) ** 2;
                  if (e <= 1.0) {
                    c = skinCol;
                    if (lz >= 12.2 && lz <= 14.6 && ly > 3.1 && Math.abs(Math.abs(lx) - 2.0) <= 0.75) {
                      c = (lz > 13.7 && Math.abs(lx) > 1.8) ? 7 : eyeCol;
                    } else if (lz >= 11.4 && lz <= 12.5 && ly > 3.0 && Math.abs(Math.abs(lx) - 3.3) <= 0.75) {
                      c = 10;
                    }
                  }
                }
              } else if (charType === 'quadruped') {
                if (lz < 5.0) {
                  const fl = Math.hypot(Math.abs(lx) - 2.6, ly - 3.5);
                  const bl = Math.hypot(Math.abs(lx) - 2.6, ly + 4.0);
                  if (fl <= 1.35 || bl <= 1.35) c = lz < 1.3 ? 7 : furDark;
                }
                if (!c && lz >= 4.2 && lz < 9.8) {
                  const eb = (lx / 3.8) ** 2 + ((ly + 0.5) / 5.7) ** 2 + ((lz - 6.8) / 3.0) ** 2;
                  if (eb <= 1.0) c = (lz < 5.2 && Math.abs(lx) < 2.1) ? furLight : furMain;
                }
                if (!c && ly < -5.0 && ly >= -9.6 && Math.abs(lx) <= 1.1) {
                  const tz = 7.4 + (-ly - 5.0) * 0.85;
                  if (Math.abs(lz - tz) <= 1.2) c = ly < -8.2 ? 7 : furMain;
                }
                if (lz >= 8.0 && lz < 15.2) {
                  const eh = (lx / 3.6) ** 2 + ((ly - 4.2) / 3.4) ** 2 + ((lz - 11.4) / 3.5) ** 2;
                  if (eh <= 1.0) {
                    c = furMain;
                    if (lz >= 11.4 && lz <= 12.9 && ly >= 6.5 && Math.abs(Math.abs(lx) - 1.55) <= 0.65) c = eyeCol;
                  } else if (lz >= 8.4 && lz < 11.2 && ly >= 6.2 && ly <= 8.5 && Math.abs(lx) <= 1.9) {
                    c = (ly >= 7.7 && lz >= 9.9 && Math.abs(lx) <= 0.8) ? 6 : furLight;
                  }
                }
              } else if (charType === 'monster') {
                if (lz < 5.2) {
                  if (Math.abs(Math.abs(lx) - 3.2) <= 1.8 && Math.abs(ly) <= 2.1) c = monDark;
                } else if (lz < 14.5) {
                  const et = (lx / 6.0) ** 2 + (ly / 3.6) ** 2 + ((lz - 9.8) / 4.9) ** 2;
                  if (et <= 1.0) {
                    c = monMain;
                    if (Math.abs(lx) <= 1.5 && ly > 2.4 && Math.abs(lz - 10.2) <= 1.5) c = trimCol;
                  } else if (Math.abs(lx) >= 5.6 && Math.abs(lx) <= 8.2 && Math.abs(ly) <= 2.0 && lz >= 3.5 && lz < 13.5) {
                    c = lz < 6.0 ? monDark : monMain;
                  }
                }
                if (lz >= 13.2 && lz < 18.8 && Math.abs(lx) <= 3.8 && Math.abs(ly - 0.5) <= 3.0) {
                  c = monMain;
                  if (lz >= 15.0 && lz <= 16.4 && ly >= 2.6 && Math.abs(Math.abs(lx) - 1.6) <= 0.8) c = monsterEyeCol;
                  else if (lz >= 13.4 && lz <= 14.3 && ly >= 2.8 && Math.abs(Math.abs(lx) - 1.5) <= 0.6) c = 7;
                }
              }

              // Acessórios de cabeça (adaptados às âncoras do arquétipo)
              const dyH = ly - headCenterY;
              const topLim = 23.6;
              if (headStyle === 'short_hair') {
                if (lz >= headTopZ - 1.2 && lz <= Math.min(topLim, headTopZ + 1.1) && Math.abs(lx) <= headRx + 0.3 && ly >= headBackY - 0.3 && ly <= headFrontY + 0.2) {
                  c = hairCol;
                } else if (ly <= headBackY + 0.9 && ly >= headBackY - 0.7 && Math.abs(lx) <= headRx + 0.2 && lz >= headCenterZ - 1.0 && lz <= headTopZ) {
                  c = hairCol;
                } else if (ly >= headFrontY - 0.7 && ly <= headFrontY + 0.4 && Math.abs(lx) <= headRx - 0.2 && lz >= headTopZ - 1.6 && lz <= headTopZ) {
                  c = hairCol;
                }
              } else if (headStyle === 'long_hair') {
                if (lz >= headTopZ - 1.2 && lz <= Math.min(topLim, headTopZ + 1.1) && Math.abs(lx) <= headRx + 0.5 && ly >= headBackY - 0.6 && ly <= headFrontY + 0.2) {
                  c = hairCol;
                } else if (ly <= headBackY + 0.8 && ly >= headBackY - 1.2 && Math.abs(lx) <= headRx + 0.5 && lz >= Math.max(4.0, headCenterZ - 7.5) && lz <= headTopZ + 0.6) {
                  c = hairCol;
                } else if (Math.abs(lx) >= headRx - 0.5 && Math.abs(lx) <= headRx + 1.1 && ly >= headBackY && ly <= headCenterY + 1.0 && lz >= Math.max(6.0, headCenterZ - 5.5) && lz <= headTopZ) {
                  c = hairCol;
                }
              } else if (headStyle === 'mohawk') {
                if (Math.abs(lx) <= 1.05 && ly >= headBackY && ly <= headFrontY && lz >= headTopZ - 0.6 && lz <= Math.min(topLim, headTopZ + 4.0)) {
                  c = (lz > headTopZ + 2.2) ? trimCol : hairCol;
                }
              } else if (headStyle === 'helmet') {
                const inHelmBox = Math.abs(lx) <= headRx + 0.9 && ly >= headBackY - 0.8 && ly <= headFrontY + 0.8;
                const visorOpen = ly > headFrontY - 0.9 && lz < headTopZ - 0.6 && Math.abs(lx) <= headRx - 0.5;
                if (inHelmBox && !visorOpen && lz >= headCenterZ - 0.4 && lz <= Math.min(topLim, headTopZ + 1.5)) {
                  c = (lz >= headTopZ - 0.8 && ly > headFrontY - 0.4) ? 13 : 15;
                } else if (Math.abs(lx) <= 0.8 && ly >= headBackY && ly <= headFrontY - 0.5 && lz > headTopZ + 1.4 && lz <= Math.min(topLim, headTopZ + 3.2)) {
                  c = 10;
                }
              } else if (headStyle === 'wizard_hat') {
                const radXZ = Math.hypot(lx, dyH);
                if (lz >= headTopZ - 0.7 && lz <= headTopZ + 0.5 && radXZ <= headRx + 2.6) {
                  c = trimCol === 13 ? 14 : trimCol;
                } else if (lz > headTopZ + 0.5 && lz <= Math.min(topLim, headTopZ + 5.2)) {
                  const hFrac = (lz - (headTopZ + 0.5)) / 4.7;
                  const coneR = Math.max(0.6, (headRx + 0.4) * (1 - hFrac * 0.85));
                  const bendY = dyH + hFrac * 1.4;
                  if (Math.hypot(lx, bendY) <= coneR) c = lz <= headTopZ + 1.5 ? 13 : 14;
                }
              } else if (headStyle === 'ears') {
                if (lz >= headTopZ - 0.6 && lz <= Math.min(topLim, headTopZ + 3.4) && Math.abs(dyH) <= 1.2) {
                  const eOff = Math.abs(Math.abs(lx) - (headRx - 0.6));
                  const halfW = Math.max(0.4, 1.4 - Math.max(0, lz - headTopZ) * 0.35);
                  if (eOff <= halfW) {
                    c = (eOff <= 0.45 && ly > headCenterY && lz < headTopZ + 2.0) ? 10 : (charType === 'quadruped' ? furMain : hairCol);
                  }
                }
              }

              if (c > 0) layer[y * N + x] = c;
            }
          }
        }
        voxCache = null;
        renderPalette();
        drawEdit();
        say(`Personagem "${charType}" (${headStyle}) gerado com seed ${seed}! Retoque ou salve como Avatar.`);
      }

      const btnGenChar = document.getElementById('mBtnGenChar');
      const btnVaryChar = document.getElementById('mBtnVaryChar');
      if (btnGenChar) {
        btnGenChar.addEventListener('click', () => {
          const t = document.getElementById('mCharType')?.value || 'humanoid';
          const h = document.getElementById('mCharHead')?.value || 'short_hair';
          generateCharacter(t, h, charSeed);
        });
      }
      if (btnVaryChar) {
        btnVaryChar.addEventListener('click', () => {
          charSeed++;
          const t = document.getElementById('mCharType')?.value || 'humanoid';
          const h = document.getElementById('mCharHead')?.value || 'short_hair';
          generateCharacter(t, h, charSeed);
        });
      }

      let propSeed = 100;
      function generateProcProp(propKind, seed) {
        const rng = makeRng(seed);
        for (let z = 0; z < N; z++) vol[z].fill(0);
        const s = N / 24;
        const cx = (N - 1) / 2;
        const cy = (N - 1) / 2;

        if (propKind === 'gen_tree') {
          applyPresetAndKind('foliage', 'foliage', `arvore_${seed}`);
          const sakura = rng() > 0.65;
          const leanX = (rng() - 0.5) * 4.2;
          const leanY = (rng() - 0.5) * 4.2;
          const trunkTop = 14 + rng() * 3;
          const lobes = Array.from({ length: 4 + Math.floor(rng() * 3) }, (_, i) => ({
            x: leanX * 0.8 + (i === 0 ? 0 : (rng() - 0.5) * 8.5),
            y: leanY * 0.8 + (i === 0 ? 0 : (rng() - 0.5) * 8.5),
            z: (i === 0 ? 17.5 : 12.0 + rng() * 7.0),
            rx: 4.5 + rng() * 3.0,
            ry: 4.5 + rng() * 3.0,
            rz: 3.4 + rng() * 2.5
          }));
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            const tz = Math.min(1, lz / trunkTop);
            const tx = leanX * tz * tz;
            const ty = leanY * tz * tz;
            const tr = lz < 2.2 ? (3.2 - lz * 0.45) : 1.9 * (1 - 0.35 * tz);
            for (let y = 0; y < N; y++) {
              const ly = (y - cy) / s;
              for (let x = 0; x < N; x++) {
                const lx = (x - cx) / s;
                let c = 0;
                const dTrunk = Math.hypot(lx - tx, ly - ty);
                if (lz <= trunkTop && dTrunk <= tr) {
                  c = (lx - tx < 0) ? 14 : 15;
                }
                for (let k = 0; k < lobes.length; k++) {
                  const lb = lobes[k];
                  const wobble = Math.sin(lx * 0.9 + k) * Math.cos(ly * 0.9 - k) * 0.14;
                  const d = ((lx - lb.x) / lb.rx) ** 2 + ((ly - lb.y) / lb.ry) ** 2 + ((lz - lb.z) / lb.rz) ** 2 + wobble;
                  if (d <= 1.0) {
                    const topness = (lz - (lb.z - lb.rz)) / (2 * lb.rz);
                    if (sakura) c = topness > 0.72 ? 12 : (topness > 0.42 ? 10 : 9);
                    else c = topness > 0.74 ? 6 : (topness > 0.44 ? 4 : 2);
                  }
                }
                if (c > 0) vol[z][y * N + x] = c;
              }
            }
          }
        } else if (propKind === 'gen_rock') {
          applyPresetAndKind('stone', 'destructible', `rocha_${seed}`, 'stone_chunk');
          const isCrystal = rng() > 0.45;
          if (isCrystal) {
            const spires = Array.from({ length: 4 + Math.floor(rng() * 3) }, (_, i) => ({
              ox: (i === 0 ? 0 : (rng() - 0.5) * 9.0),
              oy: (i === 0 ? 0 : (rng() - 0.5) * 9.0),
              tiltX: (rng() - 0.5) * 0.32,
              tiltY: (rng() - 0.5) * 0.32,
              h: i === 0 ? 19 : 11 + rng() * 7,
              r: i === 0 ? 3.4 : 2.1 + rng() * 1.4
            }));
            for (let z = 0; z < N; z++) {
              const lz = z / s;
              for (let y = 0; y < N; y++) {
                const ly = (y - cy) / s;
                for (let x = 0; x < N; x++) {
                  const lx = (x - cx) / s;
                  let c = 0;
                  if (lz < 5.0 && (lx / 8.5) ** 2 + (ly / 8.0) ** 2 + (lz / 5.2) ** 2 <= 1.0) c = lz > 3.5 ? 11 : 10;
                  for (let k = 0; k < spires.length; k++) {
                    const sp = spires[k];
                    if (lz <= sp.h) {
                      const sx = lx - sp.ox - lz * sp.tiltX;
                      const sy = ly - sp.oy - lz * sp.tiltY;
                      const taper = Math.max(0.25, 1 - Math.max(0, lz - sp.h * 0.65) / (sp.h * 0.38));
                      if (Math.abs(sx) + Math.abs(sy) <= sp.r * 1.35 * taper) {
                        c = lz > sp.h * 0.72 ? 8 : (sx + sy > 0 ? 6 : 4);
                      }
                    }
                  }
                  if (c > 0) vol[z][y * N + x] = c;
                }
              }
            }
          } else {
            const pA = rng() * 6.28, pB = rng() * 6.28;
            const rx = 7.2 + rng() * 2.5, ry = 6.8 + rng() * 2.5, rz = 11.0 + rng() * 4.5;
            for (let z = 0; z < N; z++) {
              const lz = z / s;
              for (let y = 0; y < N; y++) {
                const ly = (y - cy) / s;
                for (let x = 0; x < N; x++) {
                  const lx = (x - cx) / s;
                  const facet = Math.abs(Math.sin(lx * 0.55 + pA) * Math.cos(ly * 0.55 + pB)) * 0.22;
                  const d = (lx / rx) ** 2 + (ly / ry) ** 2 + ((lz - 2.0) / rz) ** 2 + facet;
                  if (d <= 1.0 && lz >= 0) {
                    vol[z][y * N + x] = lz > rz * 0.85 ? 14 : (lz > rz * 0.5 ? 6 : 3);
                  }
                }
              }
            }
          }
        } else if (propKind === 'gen_house') {
          applyPresetAndKind('default', 'solid', `casinha_${seed}`);
          const roofCol = [12, 2, 6, 3][Math.floor(rng() * 4)];
          const wallCol = rng() > 0.4 ? 14 : 1;
          const chimSide = rng() > 0.5 ? 4.5 : -4.5;
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let y = 0; y < N; y++) {
              const ly = (y - cy) / s;
              for (let x = 0; x < N; x++) {
                const lx = (x - cx) / s;
                let c = 0;
                if (lz < 2.0 && Math.abs(lx) <= 8.5 && Math.abs(ly) <= 7.5) {
                  c = 10;
                } else if (lz >= 2.0 && lz < 11.5 && Math.abs(lx) <= 7.5 && Math.abs(ly) <= 6.5) {
                  const corner = Math.abs(lx) >= 6.2 && Math.abs(ly) >= 5.2;
                  c = corner ? 4 : wallCol;
                  if (ly >= 5.5 && Math.abs(lx) <= 1.8 && lz <= 8.0) c = (Math.abs(lx) < 0.8 && lz >= 4.0 && lz <= 5.0) ? 13 : 5;
                  else if (Math.abs(lx) >= 6.4 && Math.abs(ly) <= 1.6 && lz >= 5.2 && lz <= 8.2) c = 13;
                  else if (ly >= 5.5 && Math.abs(Math.abs(lx) - 4.4) <= 1.1 && lz >= 5.8 && lz <= 8.4) c = 13;
                } else if (lz >= 11.0 && lz <= 20.5) {
                  const span = 9.2 - (lz - 11.0) * 0.95;
                  if (span >= 0.4 && Math.abs(lx) <= span && Math.abs(ly) <= 8.2) {
                    c = (Math.abs(lx) >= span - 1.2 || Math.abs(ly) >= 7.2) ? roofCol : (Math.abs(ly) <= 6.5 ? wallCol : roofCol);
                  }
                }
                if (Math.abs(lx - chimSide) <= 1.2 && Math.abs(ly + 3.5) <= 1.2 && lz >= 12.0 && lz <= 21.8) c = 11;
                if (c > 0) vol[z][y * N + x] = c;
              }
            }
          }
        } else if (propKind === 'gen_chest') {
          applyPresetAndKind('default', 'solid', `bau_${seed}`);
          const woodMain = rng() > 0.5 ? 6 : 7;
          const woodTrim = 4;
          const metalCol = rng() > 0.35 ? 10 : 15;
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let y = 0; y < N; y++) {
              const ly = (y - cy) / s;
              for (let x = 0; x < N; x++) {
                const lx = (x - cx) / s;
                let c = 0;
                if (lz < 7.0 && Math.abs(lx) <= 8.2 && Math.abs(ly) <= 5.6) {
                  const strap = Math.abs(Math.abs(lx) - 5.2) <= 0.9 || Math.abs(lx) >= 7.2 || Math.abs(ly) >= 4.6;
                  c = strap ? (lz >= 5.8 ? metalCol : woodTrim) : woodMain;
                } else if (lz >= 7.0 && lz <= 13.5 && Math.abs(lx) <= 8.2) {
                  const arch = (ly / 5.6) ** 2 + ((lz - 7.0) / 6.2) ** 2;
                  if (arch <= 1.0) {
                    const strap = Math.abs(Math.abs(lx) - 5.2) <= 0.9 || Math.abs(lx) >= 7.2;
                    c = strap ? metalCol : woodMain;
                  }
                }
                if (ly >= 5.0 && ly <= 6.4 && Math.abs(lx) <= 1.5 && lz >= 5.2 && lz <= 8.4) c = 13;
                if (c > 0) vol[z][y * N + x] = c;
              }
            }
          }
        } else if (propKind === 'gen_mushroom') {
          applyPresetAndKind('default', 'foliage', `cogumelo_${seed}`);
          const capCol = [12, 2, 13, 8][Math.floor(rng() * 4)];
          const leanX = (rng() - 0.5) * 2.4;
          const spots = Array.from({ length: 6 }, () => ({
            ang: rng() * Math.PI * 2,
            r: 2.2 + rng() * 5.2,
            rad: 1.3 + rng() * 0.9
          }));
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let y = 0; y < N; y++) {
              const ly = (y - cy) / s;
              for (let x = 0; x < N; x++) {
                const lx = (x - cx) / s;
                let c = 0;
                const sx = lx - leanX * Math.min(1, lz / 11.0);
                if (lz <= 11.5 && Math.hypot(sx, ly) <= (lz < 2.5 ? 3.5 - lz * 0.35 : 2.3)) {
                  c = lz < 1.2 && Math.hypot(sx, ly) > 2.4 ? 8 : 1;
                }
                const capD = ((lx - leanX) / 8.8) ** 2 + (ly / 8.8) ** 2 + ((lz - 11.0) / 8.2) ** 2;
                if (lz >= 10.5 && capD <= 1.0) {
                  c = capCol;
                  for (let k = 0; k < spots.length; k++) {
                    const sp = spots[k];
                    const px = leanX + Math.cos(sp.ang) * sp.r;
                    const py = Math.sin(sp.ang) * sp.r;
                    if (Math.hypot(lx - px, ly - py) <= sp.rad) c = 14;
                  }
                }
                if (c > 0) vol[z][y * N + x] = c;
              }
            }
          }
        } else if (propKind === 'gen_sword') {
          applyPresetAndKind('default', 'pickable', `espada_${seed}`);
          const gemCol = [12, 2, 13][Math.floor(rng() * 3)];
          const guardW = 4.6 + rng() * 1.6;
          for (let z = 0; z < N; z++) {
            const lz = z / s;
            for (let y = 0; y < N; y++) {
              const ly = (y - cy) / s;
              for (let x = 0; x < N; x++) {
                const lx = (x - cx) / s;
                let c = 0;
                if (lz < 5.5 && (lx / 6.4) ** 2 + (ly / 5.8) ** 2 + (lz / 5.5) ** 2 <= 1.0) {
                  c = lz > 3.8 ? 11 : 10;
                }
                if (lz >= 4.0 && lz < 15.2 && Math.abs(lx) <= 1.4 && Math.abs(ly) <= 0.7) {
                  c = Math.abs(lx) < 0.7 ? 14 : 11;
                } else if (lz >= 15.0 && lz <= 16.6 && Math.abs(lx) <= guardW && Math.abs(ly) <= 1.2) {
                  c = 13;
                } else if (lz > 16.6 && lz <= 20.5 && Math.abs(lx) <= 0.9 && Math.abs(ly) <= 0.9) {
                  c = 4;
                } else if (lz > 20.5 && lz <= 22.6 && Math.hypot(lx, ly) <= 1.6) {
                  c = gemCol;
                }
                if (c > 0) vol[z][y * N + x] = c;
              }
            }
          }
        }
        voxCache = null;
        renderPalette();
        drawEdit();
        say(`Prop "${propKind}" gerado (seed ${seed})! Clique novamente para nova variação.`);
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
      const bindRangeLabel = (id, valId, suffix = '') => {
        const el = document.getElementById(id);
        const out = document.getElementById(valId);
        if (!el) return;
        const sync = () => { if (out) out.textContent = String(el.value) + suffix; };
        el.addEventListener('input', sync);
        el.addEventListener('change', sync);
        sync();
      };
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
          paintLeafLobe(0, 0, 17.2, 7.6, 7.6, 3.8, 3);
          const numStrands = 18;
          for (let k = 0; k < numStrands; k++) {
            const ang = (k / numStrands) * Math.PI * 2 + (rng() - 0.5) * 0.2;
            const rad = 5.2 + rng() * 2.4;
            const sx = Math.cos(ang) * rad;
            const sy = Math.sin(ang) * rad;
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
          buf[c.gz * N + c.gx] = (erase2d || tool === 'eraser') ? 0 : curColor;
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
            img.onload = () => {
              const tmp = document.createElement('canvas');
              tmp.width = N; tmp.height = N;
              const tCtx = tmp.getContext('2d');
              tCtx.imageSmoothingEnabled = false;
              tCtx.clearRect(0, 0, N, N);
              tCtx.drawImage(img, 0, 0, N, N);
              const data = tCtx.getImageData(0, 0, N, N).data;
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
              const halfY = mode === 'edt_blade'
                ? Math.min(maxHalfY, Math.max(0, Math.floor(d - 0.5)))
                : Math.round(maxHalfY * Math.sqrt(Math.min(1, d / Math.max(1, dMax))));
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
        const panelMap = { chars: 'mTabChars', trees: 'mTabTrees', conv2d: 'mTabConv2d' };
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
        generateProcProp,
        generateModularTree,
        convert2dTo3d,
        load2dPreset,
        get2dBuffers: () => ({ front2D, side2D }),
        getPalette: () => pal,
        getSize: () => N,
        getVol: () => vol,
        setZ,
        setTool: (t) => { tool = t; },
        applyCell: (x, y) => applyTool({ x, y })
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

