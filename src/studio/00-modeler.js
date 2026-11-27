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
        workspace.style.display = 'flex';
        tabW.className = 'mode-btn active-edit';
        tabM.className = 'mode-btn';
        window.dispatchEvent(new Event('resize'));
      });
      tabM.addEventListener('click', () => {
        workspace.style.display = 'none';
        view.classList.add('show');
        tabM.className = 'mode-btn active-edit';
        tabW.className = 'mode-btn';
        drawEdit();
      });

      // ---------- API para o Studio de Mundo ----------
      window.StudioModeler = {
        exportAssets: () => customAssets.map((a) => ({ ...a })),
        importAssets: (list) => { (list || []).forEach((a) => { try { registerAsset(a); } catch (e) { console.error(e); } }); },
        registerAsset,
        generateCharacter,
        generateProcProp,
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
    })();

