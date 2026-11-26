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
      const customAssets = []; // { key, name, size, pal, slices, solid }

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

      // ---------- Edição ----------
      const cell = () => editCv.width / N;

      function cellAt(e) {
        const r = editCv.getBoundingClientRect();
        const cs = cell();
        const x = Math.floor(((e.clientX - r.left) / r.width) * editCv.width / cs);
        const y = Math.floor(((e.clientY - r.top) / r.height) * editCv.height / cs);
        if (x < 0 || y < 0 || x >= N || y >= N) return null;
        return { x, y };
      }

      function setVoxel(x, y, v) {
        vol[curZ][y * N + x] = v;
        if (document.getElementById('mMirror').checked) vol[curZ][y * N + (N - 1 - x)] = v;
      }

      function floodFill(x, y, v) {
        const layer = vol[curZ];
        const target = layer[y * N + x];
        if (target === v) return;
        const stack = [[x, y]];
        while (stack.length) {
          const [cx, cy] = stack.pop();
          if (cx < 0 || cy < 0 || cx >= N || cy >= N) continue;
          if (layer[cy * N + cx] !== target) continue;
          layer[cy * N + cx] = v;
          stack.push([cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]);
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
      (function loop(now) { drawPreview(now); requestAnimationFrame(loop); })();

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
        return String(name || 'modelo').toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '') || 'modelo';
      }

      function addAssetButton(a) {
        const grid = document.getElementById('customAssetGrid');
        if (!grid) return;
        document.getElementById('customAssetEmpty').style.display = 'none';
        const existing = grid.querySelector(`[data-tool="prop_${a.key}"]`);
        if (existing) return;
        const b = document.createElement('button');
        b.className = 'tool-btn';
        b.dataset.tool = 'prop_' + a.key;
        b.textContent = '🧱 ' + a.name;
        grid.appendChild(b);
      }

      function registerAsset(a) {
        const model = buildSliceSheet(a.slices, a.pal);
        propModels[a.key] = model;
        PROP_COLLIDER_META[a.key] = a.solid
          ? { mode: 'solid', r: Math.max(3, a.size * 0.3), h: a.slices.length, shadowR: Math.max(4, a.size * 0.35) }
          : { mode: 'none', shadowR: Math.max(3, a.size * 0.25) };
        const i = customAssets.findIndex((x) => x.key === a.key);
        if (i >= 0) customAssets[i] = a; else customAssets.push(a);
        addAssetButton(a);
      }

      document.getElementById('mBtnSave').addEventListener('click', () => {
        const slices = currentSlices();
        if (!slices) { say('Modelo vazio: pinte alguma coisa antes de salvar.', false); return; }
        const name = document.getElementById('mName').value.trim() || 'modelo';
        let key = 'custom_' + slug(name);
        const solid = document.getElementById('mKind').value === 'solid';
        registerAsset({ key, name, size: N, pal: pal.slice(), slices, solid });
        say(`"${name}" salvo na biblioteca (${slices.length} camadas). Use na aba 🌍 Mundo → Meus Modelos.`);
      });

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
        // formato compatível com assets/voxels (palette + slices em base-36)
        downloadJson(`${slug(name)}.model.json`, { name, size: N, palette: pal, slices, solid: document.getElementById('mKind').value === 'solid' });
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
            const size = slices[0].length;
            if (![16, 24, 32].includes(size) || slices[0][0].length !== size) throw new Error(`grade ${size} não suportada (use 16, 24 ou 32 quadrada)`);
            newVolume(size);
            document.getElementById('mSize').value = String(size);
            pal = (d.palette || d.pal || DEFAULT_PAL).slice(0, 36);
            for (let z = 0; z < Math.min(N, slices.length); z++)
              for (let y = 0; y < N; y++)
                for (let x = 0; x < N; x++) vol[z][y * N + x] = parseInt(slices[z][y][x], 36) || 0;
            if (d.name) document.getElementById('mName').value = d.name;
            document.getElementById('mKind').value = d.solid ? 'solid' : 'decor';
            curColor = Math.min(curColor, pal.length - 1) || 1;
            renderPalette();
            drawEdit();
            say('Modelo importado para edição.');
          } catch (err) {
            say('Falha ao importar: ' + err.message, false);
          }
        };
        reader.readAsText(f);
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
        registerAsset
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

