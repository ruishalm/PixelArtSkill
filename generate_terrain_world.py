import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, 'slices_v5.json'), 'r', encoding='utf-8') as f:
    cat_slices = json.load(f)

with open(os.path.join(ROOT, 'hats_pack.json'), 'r', encoding='utf-8') as f:
    hats_pack = json.load(f)

with open(os.path.join(ROOT, 'chicken_slices.json'), 'r', encoding='utf-8') as f:
    chicken_data = json.load(f)

with open(os.path.join(ROOT, 'terrain_props_pack.json'), 'r', encoding='utf-8') as f:
    props_pack = json.load(f)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <link rel="icon" href="data:," />
  <title>Vale Felino 3D — Terreno Micro-Voxel Orgânico 720×720</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-tap-highlight-color: transparent; }
    body {
      background: linear-gradient(180deg, #86CFF4 0%, #CBEBFA 55%, #F4E9D7 100%);
      color: #3B2219;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .stage {
      position: relative;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }
    #viewport {
      position: absolute;
      inset: 0;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      cursor: grab;
      touch-action: none;
      display: block;
    }
    #viewport:active { cursor: grabbing; }

    /* HUD Topo Esquerdo */
    .hud-top-left {
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(255, 252, 245, 0.92);
      backdrop-filter: blur(10px);
      border: 2px solid #5B3C2B;
      border-radius: 14px;
      padding: 10px 13px;
      box-shadow: 0 8px 22px rgba(59, 34, 25, 0.16);
      display: flex;
      flex-direction: column;
      gap: 7px;
      max-width: 345px;
      z-index: 10;
    }
    .hud-title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
    }
    .hud-title {
      font-size: 15px;
      font-weight: 800;
      color: #3B2219;
      letter-spacing: -0.3px;
    }
    .badges-group {
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .fish-badge {
      background: #FEF3C7;
      border: 1.5px solid #D97706;
      color: #92400E;
      font-weight: 800;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 999px;
      white-space: nowrap;
    }
    .biome-badge {
      background: #DCFCE7;
      border: 1.5px solid #16A34A;
      color: #166534;
      font-weight: 800;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 999px;
      white-space: nowrap;
    }
    .controls-row {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      align-items: center;
    }
    .pill-btn {
      background: #EFE7D8;
      color: #3B2219;
      border: 1.5px solid #8C6D59;
      border-radius: 8px;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.1s, background 0.15s;
    }
    .pill-btn:hover { background: #E4D7C0; transform: translateY(-1px); }
    .pill-btn.primary {
      background: #D97706;
      color: #FFFDF9;
      border-color: #92400E;
    }
    .pill-btn.travel {
      background: #E0F2FE;
      color: #075985;
      border-color: #0284C7;
    }

    /* Toast de Descoberta de Bioma */
    .biome-toast {
      position: absolute;
      top: 16px;
      left: 50%;
      transform: translateX(-50%) translateY(-16px);
      background: rgba(59, 34, 25, 0.92);
      color: #FEF3C7;
      border: 2px solid #FBBF24;
      border-radius: 999px;
      padding: 6px 16px;
      font-size: 13px;
      font-weight: 800;
      box-shadow: 0 8px 20px rgba(0,0,0,0.22);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s, transform 0.3s;
      z-index: 20;
      white-space: nowrap;
    }
    .biome-toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    /* Minimapa Topo Direito */
    .minimap-card {
      position: absolute;
      top: 12px;
      right: 12px;
      background: rgba(255, 252, 245, 0.92);
      backdrop-filter: blur(10px);
      border: 2px solid #5B3C2B;
      border-radius: 14px;
      padding: 7px;
      box-shadow: 0 8px 22px rgba(59, 34, 25, 0.16);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      z-index: 10;
    }
    .minimap-title {
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #6B4E3D;
      max-width: 120px;
      text-align: center;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    #minimapCanvas {
      width: 120px;
      height: 120px;
      border-radius: 8px;
      border: 1.5px solid #7C5C47;
      image-rendering: pixelated;
    }

    /* Rodapé Telemetria */
    .hud-bottom {
      position: absolute;
      bottom: 12px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255, 252, 245, 0.92);
      backdrop-filter: blur(10px);
      border: 2px solid #5B3C2B;
      border-radius: 16px;
      padding: 7px 14px;
      box-shadow: 0 8px 24px rgba(59, 34, 25, 0.18);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 8px;
      max-width: 96vw;
      font-size: 12px;
      z-index: 10;
    }
    .stat-chip {
      background: #F3ECE0;
      border: 1px solid #C8B59B;
      border-radius: 8px;
      padding: 3px 8px;
      font-weight: 700;
      color: #3B2219;
      white-space: nowrap;
    }
    .obstacle-chip {
      border-radius: 8px;
      padding: 3px 9px;
      font-weight: 800;
      white-space: nowrap;
      border: 1.5px solid transparent;
    }
    .obs-ok { background: #DCFCE7; color: #166534; border-color: #22C55E; }
    .obs-jump { background: #FEF3C7; color: #92400E; border-color: #F59E0B; }
    .obs-high { background: #FEE2E2; color: #991B1B; border-color: #EF4444; }
    .obs-water { background: #DBEAFE; color: #1E40AF; border-color: #3B82F6; }

    .keys-hint {
      font-size: 11px;
      color: #6B4E3D;
      font-weight: 600;
      white-space: nowrap;
    }
    kbd {
      background: #FFFDF8;
      border: 1px solid #B59F84;
      border-bottom-width: 2px;
      border-radius: 4px;
      padding: 1px 5px;
      font-family: inherit;
      font-size: 10px;
      font-weight: 800;
      color: #3B2219;
    }

    /* Controles Touch Responsivos para Celular / Tablet */
    .touch-controls {
      position: absolute;
      bottom: 84px;
      left: 14px;
      right: 14px;
      display: none;
      justify-content: space-between;
      align-items: flex-end;
      pointer-events: none;
      z-index: 15;
    }
    .touch-dpad {
      display: grid;
      grid-template-columns: repeat(3, 42px);
      grid-template-rows: repeat(2, 42px);
      gap: 4px;
      pointer-events: auto;
    }
    .touch-btn {
      background: rgba(255, 252, 245, 0.85);
      border: 2px solid #5B3C2B;
      border-radius: 10px;
      font-size: 16px;
      font-weight: 800;
      color: #3B2219;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    .touch-btn:active { background: #E4D7C0; }
    .touch-jump {
      pointer-events: auto;
      width: 72px;
      height: 54px;
      border-radius: 14px;
      background: rgba(217, 119, 6, 0.9);
      color: #FFFDF9;
      border: 2px solid #78350F;
      font-size: 13px;
      font-weight: 800;
    }

    @media (pointer: coarse) {
      .touch-controls { display: flex; }
      .keys-hint { display: none; }
    }
    @media (max-width: 640px) {
      .hud-top-left {
        top: 8px;
        left: 8px;
        padding: 7px 9px;
        max-width: calc(100vw - 118px);
        gap: 5px;
      }
      .hud-title { font-size: 13px; }
      .pill-btn { padding: 3px 6px; font-size: 10px; }
      .minimap-card { top: 8px; right: 8px; padding: 5px; }
      #minimapCanvas { width: 84px; height: 84px; }
      .minimap-title { font-size: 9px; max-width: 84px; }
      .hud-bottom { bottom: 8px; padding: 5px 10px; gap: 5px; font-size: 11px; }
      .keys-hint { display: none; }
      .biome-toast { top: 124px; font-size: 12px; padding: 5px 12px; }
    }
  </style>
</head>
<body>
  <div class="stage">
    <canvas id="viewport"></canvas>

    <div class="biome-toast" id="biomeToast">🗺️ Novo Bioma Descoberto!</div>

    <div class="hud-top-left">
      <div class="hud-title-row">
        <span class="hud-title">🏔️ Vale Felino 3D</span>
        <div class="badges-group">
          <span class="fish-badge" id="fishCounter">🐟 0 / 20</span>
          <span class="biome-badge" id="biomeCounter">🗺️ 1 / 8</span>
        </div>
      </div>
      <div class="controls-row">
        <button class="pill-btn" id="btnSkin">🐱 Mochi</button>
        <button class="pill-btn" id="btnHat">🎩 Sem Chapéu</button>
        <button class="pill-btn" id="btnRotL" title="Girar Câmera (Q)">⟲ Q</button>
        <button class="pill-btn" id="btnRotR" title="Girar Câmera (E)">E ⟳</button>
        <button class="pill-btn travel" id="btnTravel" title="Viajar pelos Biomas">🧭 Viagem</button>
        <button class="pill-btn primary" id="btnReset" title="Voltar ao Spawn (R)">🏠 Spawn</button>
      </div>
    </div>

    <div class="minimap-card">
      <div class="minimap-title" id="biomeLabel">Vila da Clareira</div>
      <canvas id="minimapCanvas" width="120" height="120"></canvas>
    </div>

    <div class="touch-controls">
      <div class="touch-dpad">
        <div></div>
        <button class="touch-btn" data-key="KeyW">▲</button>
        <div></div>
        <button class="touch-btn" data-key="KeyA">◀</button>
        <button class="touch-btn" data-key="KeyS">▼</button>
        <button class="touch-btn" data-key="KeyD">▶</button>
      </div>
      <button class="touch-btn touch-jump" id="btnTouchJump">PULAR<br/>(2×H)</button>
    </div>

    <div class="hud-bottom">
      <span class="stat-chip">🐱 1H=16u | Pulo=2H (32u)</span>
      <span class="stat-chip" id="statElev">Chão: Z=0 | Gato: Z=0</span>
      <span class="obstacle-chip obs-ok" id="statObstacle">✅ Caminho Livre</span>
      <span class="keys-hint">
        <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> Mover •
        <kbd>Shift</kbd> Correr •
        <kbd>Espaço</kbd> Pular •
        <kbd>Q</kbd>/<kbd>E</kbd> Girar •
        <kbd>M</kbd> Miar •
        <kbd>R</kbd> Spawn
      </span>
    </div>
  </div>

  <script>
    // =========================================================================
    // 1. DADOS VOXEL EMBUTIDOS (Zero Fetch / 100% Autocontido)
    // =========================================================================
    const CAT_BODY_DATA = __CAT_SLICES__;
    const HATS_DATA = __HATS_PACK__;
    const CHICKEN_DATA = __CHICKEN_DATA__;
    const PROPS_DATA = __PROPS_PACK__;

    const PAW_DATA = [
      ["1441", "4114", "1441", "1111"],
      ["1111", "1111", "1111", "1111"]
    ];

    const CAT_SKINS = [
      { id: 'calico',  name: 'Mochi',   pal: ['rgba(0,0,0,0)', '#FDFBF7', '#DE864A', '#3B2219', '#F2A2AB', '#FFFFFF', '#B85820', '#E5E0D8'] },
      { id: 'black',   name: 'Kuro',    pal: ['rgba(0,0,0,0)', '#1E293B', '#334155', '#F59E0B', '#F472B6', '#FEF08A', '#0F172A', '#1E293B'] },
      { id: 'tuxedo',  name: 'Felix',   pal: ['rgba(0,0,0,0)', '#FFFFFF', '#1E293B', '#1E293B', '#F472B6', '#FFFFFF', '#0F172A', '#CBD5E1'] },
      { id: 'orange',  name: 'Cheddar', pal: ['rgba(0,0,0,0)', '#FED7AA', '#EA580C', '#3B2219', '#F472B6', '#FFFFFF', '#C2410C', '#FDBA74'] },
      { id: 'siamese', name: 'Luna',    pal: ['rgba(0,0,0,0)', '#FAF5EE', '#5C4033', '#0EA5E9', '#F472B6', '#FFFFFF', '#3E2723', '#EADBCA'] },
      { id: 'gray',    name: 'Misty',   pal: ['rgba(0,0,0,0)', '#94A3B8', '#64748B', '#F59E0B', '#F472B6', '#FFFFFF', '#475569', '#CBD5E1'] }
    ];

    const HAT_PRESETS = [
      { id: 'none',   name: 'Sem Chapéu', pal: null },
      { id: 'witch',  name: 'Bruxinho',   pal: ['rgba(0,0,0,0)', '#221533', '#E5A93C', '#38244F'] },
      { id: 'crown',  name: 'Coroa',      pal: ['rgba(0,0,0,0)', '#F4B846', '#FFD166', '#E63946'] },
      { id: 'beret',  name: 'Boina',      pal: ['rgba(0,0,0,0)', '#5E1428', '#B82D52', '#3D0C1A'] },
      { id: 'flower', name: 'Florzinha',  pal: ['rgba(0,0,0,0)', '#FFB7C5', '#FFD166'] }
    ];

    // =========================================================================
    // 2. CONSTRUTOR DE SLICE SHEETS (Base-36 & Nearest-Neighbor)
    // =========================================================================
    function buildSliceSheet(data, pal) {
      const cnt = data.length;
      const h = data[0].length;
      const w = data[0][0].length;
      const cv = document.createElement('canvas');
      cv.width = w * cnt;
      cv.height = h;
      const cx = cv.getContext('2d');
      cx.imageSmoothingEnabled = false;

      for (let z = 0; z < cnt; z++) {
        const offX = z * w;
        const rows = data[z];
        for (let y = 0; y < h; y++) {
          const row = rows[y];
          for (let x = 0; x < w; x++) {
            const val = parseInt(row[x], 36);
            if (val > 0 && val < pal.length) {
              cx.fillStyle = pal[val];
              cx.fillRect(offX + x, y, 1, 1);
            }
          }
        }
      }
      return { sheet: cv, count: cnt, w, h };
    }

    const catSkinModels = CAT_SKINS.map(sk => ({
      body: buildSliceSheet(CAT_BODY_DATA, sk.pal),
      paw: buildSliceSheet(PAW_DATA, sk.pal)
    }));

    const chickenModel = buildSliceSheet(CHICKEN_DATA.slices, CHICKEN_DATA.palette);

    const hatModels = {};
    for (const h of HAT_PRESETS) {
      if (h.id !== 'none' && HATS_DATA[h.id]) {
        hatModels[h.id] = buildSliceSheet(HATS_DATA[h.id], h.pal);
      }
    }

    const propModels = {};
    for (const [key, entry] of Object.entries(PROPS_DATA)) {
      propModels[key] = buildSliceSheet(entry.slices, entry.palette);
    }

    // =========================================================================
    // 3. ÁUDIO RETRO (WebAudio Sintetizado)
    // =========================================================================
    let audioCtx = null;
    function playTone(freq, endFreq, dur, type = 'sine', gainVal = 0.08) {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(Math.max(40, endFreq), audioCtx.currentTime + dur);
        g.gain.setValueAtTime(gainVal, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
        osc.connect(g);
        g.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + dur);
      } catch (e) {}
    }
    const sfxJump = () => playTone(310, 620, 0.14, 'triangle', 0.08);
    const sfxLand = () => playTone(160, 85, 0.07, 'sine', 0.05);
    const sfxBlocked = () => playTone(180, 110, 0.11, 'square', 0.04);
    const sfxFish = () => {
      playTone(523.25, 783.99, 0.12, 'triangle', 0.09);
      setTimeout(() => playTone(783.99, 1046.5, 0.18, 'triangle', 0.09), 90);
    };
    const sfxBiome = () => {
      playTone(440, 659.25, 0.12, 'sine', 0.07);
      setTimeout(() => playTone(659.25, 880, 0.16, 'sine', 0.07), 85);
    };
    const sfxMeow = () => playTone(660, 490, 0.16, 'sine', 0.07);

    // =========================================================================
    // 4. HEIGHTFIELD MICRO-VOXEL 720×720 & ESCULTURA ORGÂNICA "PULL-CHAIN"
    // =========================================================================
    const STARTUP_T0 = performance.now();
    const mw = 720;
    const mh = 720;
    const VOX = 2;
    const HALF_GRID = 360;
    const HALF_WORLD = 720;
    const WORLD_MIN = -720;
    const WORLD_MAX = 720;

    const Z_MIN = -6;
    const TERRAIN_Z_MAX = 66;
    const Z_GRASS_MAX = 70;

    const CAT_HEIGHT = 16;
    const AUTO_STEP_MAX = 5.5; // ~0.35H, sobe colinas orgânicas suavemente andando
    const GRAVITY = 1200;
    const JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0); // ~35u apex (vence 16u e 32u, bloqueia 48u)

    const BIOME_KEYS = ['vila', 'girassol', 'ruinas', 'praia', 'zen', 'rio', 'cogumelos', 'montanha'];
    const BIOME_NAMES = [
      'Vila da Clareira',
      'Campos de Girassol',
      'Ruínas Orgânicas',
      'Praia & Farol',
      'Jardim Zen & Torii',
      'Rio & Cachoeira',
      'Bosque Cogumelos',
      'Pico Sakura'
    ];
    // Materiais: 0: grass, 1: path, 2: sand, 3: stone, 4: water, 5: bridge, 6: peak, 7: lilypad
    const MAT_GRASS = 0, MAT_PATH = 1, MAT_SAND = 2, MAT_STONE = 3,
          MAT_WATER = 4, MAT_BRIDGE = 5, MAT_PEAK = 6, MAT_LILYPAD = 7;

    const hmap = new Int16Array(mw * mh);
    const biomeMap = new Uint8Array(mw * mh);
    const matMap = new Uint8Array(mw * mh);
    const cliffMask = new Uint8Array(mw * mh);
    const shadowMask = new Uint8Array(mw * mh); // 0..100 escurecimento de sombra estática
    const noGrassMask = new Uint8Array(mw * mh);
    const standableMap = new Uint8Array(mw * mh); // 1 = plataforma/solo pisável (>= ~3.7×3.7 micro-voxels de área), 0 = borda/degrau estreito de falésia
    const cliffTopMap = new Int16Array(mw * mh);  // Altura do topo da falésia vizinha (para bloqueio e HUD precisos)

    function worldToGrid(wx, wy) {
      return {
        mx: Math.floor(wx / VOX + HALF_GRID),
        my: Math.floor(wy / VOX + HALF_GRID)
      };
    }

    function gridToWorld(mx, my) {
      return {
        wx: (mx - HALF_GRID + 0.5) * VOX,
        wy: (my - HALF_GRID + 0.5) * VOX
      };
    }

    // Ruído 2D determinístico (3 oitavas suaves) para contornos orgânicos
    function hash2i(ix, iy) {
      let n = (ix * 374761393 + iy * 668265263) | 0;
      n = (n ^ (n >>> 13)) * 1274126177;
      return ((n ^ (n >>> 16)) >>> 0) / 4294967295;
    }

    function valueNoise2d(x, y) {
      const ix = Math.floor(x);
      const iy = Math.floor(y);
      const fx = x - ix;
      const fy = y - iy;
      const u = fx * fx * (3 - 2 * fx);
      const v = fy * fy * (3 - 2 * fy);
      const a = hash2i(ix, iy);
      const b = hash2i(ix + 1, iy);
      const c = hash2i(ix, iy + 1);
      const d = hash2i(ix + 1, iy + 1);
      return (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v) * 2 - 1;
    }

    function fbm2d(x, y) {
      let sum = 0;
      let amp = 0.55;
      let freq = 1.0;
      for (let i = 0; i < 3; i++) {
        sum += amp * valueNoise2d(x * freq, y * freq);
        freq *= 2.05;
        amp *= 0.45;
      }
      return sum;
    }

    function warp2d(wx, wy, freq = 0.012, amp = 24) {
      const qx = fbm2d(wx * freq + 5.2, wy * freq + 1.3);
      const qy = fbm2d(wx * freq + 1.7, wy * freq + 9.2);
      const f2 = freq * 1.35;
      const rx = fbm2d((wx + qx * amp) * f2 + 8.3, (wy + qy * amp) * f2 + 2.8);
      const ry = fbm2d((wx + qx * amp) * f2 + 1.2, (wy + qy * amp) * f2 + 6.4);
      return { x: wx + rx * amp, y: wy + ry * amp };
    }

    function smax(a, b, k) {
      if (k <= 0.001) return Math.max(a, b);
      const h = Math.max(0, Math.min(1, 0.5 + 0.5 * (b - a) / k));
      return a + (b - a) * h + k * h * (1 - h);
    }

    function smin(a, b, k) {
      return -smax(-a, -b, k);
    }

    function ridgedFbm(x, y, octaves = 3) {
      let sum = 0, amp = 0.55, freq = 1.0, norm = 0;
      for (let i = 0; i < octaves; i++) {
        const n = 1.0 - Math.abs(valueNoise2d(x * freq, y * freq));
        sum += n * n * amp;
        norm += amp;
        freq *= 2.05;
        amp *= 0.48;
      }
      return sum / norm;
    }

    function rockTerrace(h, step = 12, strength = 0.5, wx = 0, wy = 0) {
      if (h <= 2 || step <= 0 || strength <= 0) return h;
      const s = step * (1 + fbm2d(wx * 0.014 + 3.1, wy * 0.014 - 4.7) * 0.22);
      const u = h / s;
      const base = Math.floor(u);
      const frac = u - base;
      const smooth = frac * frac * (3 - 2 * frac);
      const terraced = (base + smooth * smooth) * s;
      return h + (terraced - h) * strength;
    }

    function segDistAndT(px, py, ax, ay, bx, by) {
      const vx = bx - ax, vy = by - ay;
      const wx = px - ax, wy = py - ay;
      const lenSq = vx * vx + vy * vy;
      const t = lenSq > 0 ? Math.max(0, Math.min(1, (wx * vx + wy * vy) / lenSq)) : 0;
      const cx = ax + vx * t, cy = ay + vy * t;
      return { d: Math.hypot(px - cx, py - cy), t };
    }

    function pullRidge(points, halfWidth, heights, opts = {}) {
      const {
        steepness = 1.45,
        warpFreq = 0.011,
        warpAmp = 26,
        ridgeAmp = 0.28,
        smoothK = 9,
        terraceStep = 0,
        terraceStrength = 0.45,
        mat = null,
        biome = null,
        isCliff = false
      } = opts;
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const [px, py] of points) {
        if (px < minX) minX = px;
        if (px > maxX) maxX = px;
        if (py < minY) minY = py;
        if (py > maxY) maxY = py;
      }
      const pad = halfWidth + warpAmp + 16;
      const x0 = Math.max(0, Math.floor((minX - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((maxX + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((minY - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((maxY + pad) / VOX + HALF_GRID));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const wp = warp2d(wx, wy, warpFreq, warpAmp);
          let bestD = Infinity;
          let bestSegH = 0;
          for (let i = 0; i < points.length - 1; i++) {
            const [ax, ay] = points[i];
            const [bx, by] = points[i + 1];
            const { d, t } = segDistAndT(wp.x, wp.y, ax, ay, bx, by);
            if (d < bestD) {
              bestD = d;
              bestSegH = heights[i] + (heights[i + 1] - heights[i]) * t;
            }
          }
          if (bestD < halfWidth) {
            const k = Math.cos((bestD / halfWidth) * Math.PI * 0.5);
            const ridge = ridgedFbm(wp.x * 0.018 + 2.1, wp.y * 0.018 - 6.3, 3);
            let rawH = bestSegH * Math.pow(Math.max(0, k), steepness) * (1 + (ridge - 0.5) * ridgeAmp);
            if (terraceStep > 0) rawH = rockTerrace(rawH, terraceStep, terraceStrength, wx, wy);
            const idx = my * mw + mx;
            const blended = Math.min(64, Math.round(smax(hmap[idx], rawH, smoothK)));
            if (blended > hmap[idx]) hmap[idx] = blended;
            if (biome !== null && bestD < halfWidth * 0.9) biomeMap[idx] = biome;
            if (mat !== null && rawH > 2) matMap[idx] = mat;
            if (isCliff && bestD < halfWidth * 0.85) cliffMask[idx] = 1;
          }
        }
      }
    }

    function carveBenchTrail(points3D, halfWidth = 13, blendWidth = 28, mat = MAT_PATH, biome = null) {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const [px, py] of points3D) {
        if (px < minX) minX = px;
        if (px > maxX) maxX = px;
        if (py < minY) minY = py;
        if (py > maxY) maxY = py;
      }
      const pad = halfWidth + blendWidth + 16;
      const x0 = Math.max(0, Math.floor((minX - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((maxX + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((minY - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((maxY + pad) / VOX + HALF_GRID));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          let bestD = Infinity;
          let bestZ = 0;
          for (let i = 0; i < points3D.length - 1; i++) {
            const [ax, ay, az] = points3D[i];
            const [bx, by, bz] = points3D[i + 1];
            const { d, t } = segDistAndT(wx, wy, ax, ay, bx, by);
            if (d < bestD) {
              bestD = d;
              bestZ = az + (bz - az) * t;
            }
          }
          const edgeN = fbm2d(wx * 0.032 + 4.1, wy * 0.032 - 1.9) * 3.0;
          const innerW = halfWidth + edgeN;
          const idx = my * mw + mx;
          if (bestD <= innerW) {
            hmap[idx] = Math.round(bestZ);
            matMap[idx] = mat;
            cliffMask[idx] = 0;
            if (biome !== null) biomeMap[idx] = biome;
          } else if (bestD <= innerW + blendWidth) {
            const t = (bestD - innerW) / blendWidth;
            const s = t * t * (3 - 2 * t);
            hmap[idx] = Math.max(0, Math.min(64, Math.round(bestZ * (1 - s) + hmap[idx] * s)));
            if (biome !== null && t < 0.6) biomeMap[idx] = biome;
          }
        }
      }
    }

    function pullHill(cx, cy, radius, height, steepness = 1.6, noiseAmp = 0.20, mat = null, biome = null, additive = false) {
      const pad = radius * (1 + noiseAmp) + 28;
      const x0 = Math.max(0, Math.floor((cx - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + pad) / VOX + HALF_GRID));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const wp = warp2d(wx, wy, 0.013, Math.min(26, radius * 0.22));
          const d = Math.hypot(wp.x - cx, wp.y - cy);
          const n = fbm2d(wx * 0.016 + 11.3, wy * 0.016 - 5.7);
          const effR = radius * (1 + n * noiseAmp);
          if (d < effR) {
            const k = Math.cos((d / effR) * Math.PI * 0.5);
            const val = Math.round(height * Math.pow(Math.max(0, k), steepness));
            const idx = my * mw + mx;
            if (additive) {
              hmap[idx] = Math.min(64, hmap[idx] + val);
            } else {
              const blended = Math.min(64, Math.round(smax(hmap[idx], val, 6)));
              if (blended > hmap[idx]) hmap[idx] = blended;
            }
            if (biome !== null && d < effR * 0.92) biomeMap[idx] = biome;
            if (mat !== null && val > 1) matMap[idx] = mat;
          }
        }
      }
    }

    function pullPlateau(cx, cy, rx, ry, height, rimWidth, noiseAmp = 0.12, isCliff = false, mat = null, biome = null, lowerAllowed = false, useWarp = true) {
      const maxR = Math.max(rx, ry) * (1 + noiseAmp) + rimWidth + (useWarp ? 28 : 8);
      const x0 = Math.max(0, Math.floor((cx - maxR) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + maxR) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - maxR) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + maxR) / VOX + HALF_GRID));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const wp = useWarp ? warp2d(wx, wy, 0.012, Math.min(24, Math.min(rx, ry) * 0.16)) : { x: wx, y: wy };
          const dx = (wp.x - cx) / rx;
          const dy = (wp.y - cy) / ry;
          const nd = Math.hypot(dx, dy);
          const n = noiseAmp > 0 ? fbm2d(wx * 0.018 - 3.1, wy * 0.018 + 7.9) * noiseAmp : 0;
          const effNd = nd / (1 + n);
          const rimNorm = rimWidth / Math.max(1, Math.min(rx, ry));

          if (effNd <= 1.0 + rimNorm) {
            const idx = my * mw + mx;
            let targetH = height;
            if (effNd > 1.0) {
              const t = 1.0 - (effNd - 1.0) / rimNorm;
              const s = t * t * (3 - 2 * t);
              targetH = Math.round(height * s);
            }
            if (lowerAllowed) {
              hmap[idx] = targetH;
            } else {
              const blended = !isCliff ? Math.min(64, Math.round(smax(hmap[idx], targetH, 6))) : targetH;
              if (blended > hmap[idx]) hmap[idx] = blended;
            }
            if (isCliff && effNd <= 1.0 + rimNorm * 0.95) {
              cliffMask[idx] = 1;
            }
            if (biome !== null && effNd <= 1.0 + rimNorm * 0.6) biomeMap[idx] = biome;
            if (mat !== null && (effNd <= 1.0 || targetH >= 2)) matMap[idx] = mat;
          }
        }
      }
    }

    function distToSegmentSq(px, py, ax, ay, bx, by) {
      const vx = bx - ax, vy = by - ay;
      const wx = px - ax, wy = py - ay;
      const lenSq = vx * vx + vy * vy;
      const t = lenSq > 0 ? Math.max(0, Math.min(1, (wx * vx + wy * vy) / lenSq)) : 0;
      const cx = ax + vx * t, cy = ay + vy * t;
      return (px - cx) * (px - cx) + (py - cy) * (py - cy);
    }

    function paintOrganicPath(points, halfWidth, mat = MAT_PATH, biome = null, forceFlatZ = null) {
      for (let i = 0; i < points.length - 1; i++) {
        const [ax, ay] = points[i];
        const [bx, by] = points[i + 1];
        const pad = halfWidth + 12;
        const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - pad) / VOX + HALF_GRID));
        const x1 = Math.min(mw - 1, Math.ceil((Math.max(ax, bx) + pad) / VOX + HALF_GRID));
        const y0 = Math.max(0, Math.floor((Math.min(ay, by) - pad) / VOX + HALF_GRID));
        const y1 = Math.min(mh - 1, Math.ceil((Math.max(ay, by) + pad) / VOX + HALF_GRID));

        for (let my = y0; my <= y1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          for (let mx = x0; mx <= x1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const d = Math.sqrt(distToSegmentSq(wx, wy, ax, ay, bx, by));
            const n = fbm2d(wx * 0.028 + 4.2, wy * 0.028 - 2.1) * 4.8;
            if (d <= halfWidth + n) {
              const idx = my * mw + mx;
              if (matMap[idx] !== MAT_WATER && matMap[idx] !== MAT_BRIDGE) {
                matMap[idx] = mat;
              }
              if (biome !== null) biomeMap[idx] = biome;
              if (forceFlatZ !== null) hmap[idx] = forceFlatZ;
            }
          }
        }
      }
    }

    function paintRampPath(ax, ay, az, bx, by, bz, halfWidth, mat = MAT_PATH, biome = null) {
      const pad = halfWidth + 16;
      const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((Math.max(ax, bx) + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((Math.min(ay, by) - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((Math.max(ay, by) + pad) / VOX + HALF_GRID));
      const vx = bx - ax, vy = by - ay;
      const lenSq = vx * vx + vy * vy || 1;

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const t = Math.max(0, Math.min(1, ((wx - ax) * vx + (wy - ay) * vy) / lenSq));
          const px = ax + vx * t, py = ay + vy * t;
          const d = Math.hypot(wx - px, wy - py);
          const n = fbm2d(wx * 0.025, wy * 0.025) * 4.2;
          const effR = halfWidth + n;
          if (d <= effR + 12) {
            const idx = my * mw + mx;
            const targetH = Math.round(az + (bz - az) * t);
            if (d <= effR) {
              hmap[idx] = Math.max(hmap[idx], targetH);
              matMap[idx] = mat;
              if (biome !== null) biomeMap[idx] = biome;
            } else {
              const s = 1 - (d - effR) / 12;
              hmap[idx] = Math.max(hmap[idx], Math.round(targetH * s * s));
              if (biome !== null) biomeMap[idx] = biome;
            }
          }
        }
      }
    }

    function carveRiverPath(points, width, depth = -6) {
      const baseHalfW = width * 0.5;
      const maxMouth = 32;
      const bankPad = baseHalfW + maxMouth + 22;
      for (let i = 0; i < points.length - 1; i++) {
        const [ax, ay] = points[i];
        const [bx, by] = points[i + 1];
        const pad = bankPad + 16;
        const x0 = Math.max(0, Math.floor((Math.min(ax, bx) - pad) / VOX + HALF_GRID));
        const x1 = Math.min(mw - 1, Math.ceil((Math.max(ax, bx) + pad) / VOX + HALF_GRID));
        const y0 = Math.max(0, Math.floor((Math.min(ay, by) - pad) / VOX + HALF_GRID));
        const y1 = Math.min(mh - 1, Math.ceil((Math.max(ay, by) + pad) / VOX + HALF_GRID));

        for (let my = y0; my <= y1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const mouthFlare = wy > 410 ? Math.min(maxMouth, (wy - 410) * 0.28) : 0;
          const halfW = baseHalfW + mouthFlare;
          const bankW = halfW + 20;
          for (let mx = x0; mx <= x1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const d = Math.sqrt(distToSegmentSq(wx, wy, ax, ay, bx, by));
            const wobble = fbm2d(wx * 0.015 + 9.2, wy * 0.015 - 4.4) * 10.0;
            const effD = d + wobble;
            const idx = my * mw + mx;
            if (effD <= halfW) {
              hmap[idx] = depth;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 5;
            } else if (effD <= halfW + 6.5) {
              if (matMap[idx] !== MAT_WATER) {
                hmap[idx] = Math.min(hmap[idx], -4);
                matMap[idx] = MAT_WATER;
                biomeMap[idx] = 5;
              }
            } else if (effD <= halfW + 13.0) {
              if (matMap[idx] !== MAT_WATER) {
                hmap[idx] = Math.min(hmap[idx], -1);
                matMap[idx] = MAT_SAND;
                biomeMap[idx] = 5;
              }
            } else if (effD <= bankW) {
              if (matMap[idx] !== MAT_WATER) {
                hmap[idx] = Math.min(hmap[idx], 0);
                matMap[idx] = MAT_SAND;
              }
            }
          }
        }
      }
    }

    function thermalAndHydraulicErosion(thermalIters = 5, dropletCount = 260) {
      const tmp = new Int16Array(mw * mh);
      for (let it = 0; it < thermalIters; it++) {
        tmp.set(hmap);
        for (let my = 1; my < mh - 1; my++) {
          const row = my * mw;
          for (let mx = 1; mx < mw - 1; mx++) {
            const idx = row + mx;
            const m = matMap[idx];
            if (cliffMask[idx] || m === MAT_WATER || m === MAT_BRIDGE || m === MAT_LILYPAD) continue;
            const talus = (m === MAT_STONE) ? 4 : 2;
            const nbs = [idx - 1, idx + 1, idx - mw, idx + mw];
            let lowNb = nbs[0];
            let lowH = hmap[lowNb];
            for (let k = 1; k < 4; k++) {
              const nb = nbs[k];
              if (hmap[nb] < lowH) {
                lowH = hmap[nb];
                lowNb = nb;
              }
            }
            if (hmap[idx] - lowH > talus) {
              const nbMat = matMap[lowNb];
              if (!cliffMask[lowNb] && nbMat !== MAT_WATER && nbMat !== MAT_BRIDGE && nbMat !== MAT_LILYPAD) {
                const delta = Math.max(1, Math.round(((hmap[idx] - lowH) - talus) * 0.30));
                tmp[idx] = Math.max(0, tmp[idx] - delta);
                tmp[lowNb] = Math.min(64, tmp[lowNb] + delta);
              }
            }
          }
        }
        hmap.set(tmp);
      }

      let seed = 133742;
      const nextRand = () => {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 4294967296;
      };

      for (let d = 0; d < dropletCount; d++) {
        let mx = 0, my = 0, found = false;
        for (let tries = 0; tries < 8; tries++) {
          const tx = 8 + Math.floor(nextRand() * (mw - 16));
          const ty = 8 + Math.floor(nextRand() * (mh - 16));
          const tidx = ty * mw + tx;
          if (hmap[tidx] >= 14 && !cliffMask[tidx] && matMap[tidx] !== MAT_PATH && matMap[tidx] !== MAT_WATER) {
            mx = tx;
            my = ty;
            found = true;
            break;
          }
        }
        if (!found) continue;

        let sediment = 0;
        for (let step = 0; step < 24; step++) {
          if (mx <= 1 || mx >= mw - 2 || my <= 1 || my >= mh - 2) break;
          const idx = my * mw + mx;
          const curH = hmap[idx];
          let lowX = mx, lowY = my, lowNb = idx, lowH = curH;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              if (dx === 0 && dy === 0) continue;
              const nx = mx + dx, ny = my + dy;
              const nidx = ny * mw + nx;
              if (hmap[nidx] < lowH) {
                lowH = hmap[nidx];
                lowNb = nidx;
                lowX = nx;
                lowY = ny;
              }
            }
          }
          const drop = curH - lowH;
          const nbMat = matMap[lowNb];
          if (drop <= 0 || cliffMask[lowNb] || nbMat === MAT_WATER || nbMat === MAT_BRIDGE || nbMat === MAT_LILYPAD) {
            if (sediment > 0 && !cliffMask[idx] && matMap[idx] !== MAT_PATH) {
              hmap[idx] = Math.min(64, hmap[idx] + 1);
            }
            break;
          }
          if (drop >= 2 && drop <= 7 && matMap[idx] !== MAT_PATH) {
            hmap[idx] = Math.max(0, hmap[idx] - 1);
            sediment++;
          } else if (drop === 1 && sediment > 0 && matMap[idx] !== MAT_PATH) {
            hmap[idx] = Math.min(64, hmap[idx] + 1);
            sediment--;
          }
          mx = lowX;
          my = lowY;
        }
      }
    }

    function elasticChainRelax(iterations = 2) {
      const tmp = new Int16Array(mw * mh);
      for (let it = 0; it < iterations; it++) {
        tmp.set(hmap);
        for (let my = 1; my < mh - 1; my++) {
          const row = my * mw;
          for (let mx = 1; mx < mw - 1; mx++) {
            const idx = row + mx;
            if (cliffMask[idx] || matMap[idx] === MAT_WATER || matMap[idx] === MAT_BRIDGE || matMap[idx] === MAT_LILYPAD) {
              continue;
            }
            const hC = hmap[idx];
            const hL = hmap[idx - 1];
            const hR = hmap[idx + 1];
            const hU = hmap[idx - mw];
            const hD = hmap[idx + mw];
            const avg = (hL + hR + hU + hD) * 0.25;
            const maxNb = Math.max(hL, hR, hU, hD);
            const minNb = Math.min(hL, hR, hU, hD);
            let next = hC;
            if (maxNb - hC > 3) {
              next = Math.round(hC + (avg - hC) * 0.55);
              if (maxNb - next > 2) next = Math.max(next, maxNb - 2);
            } else if (hC - minNb > 3) {
              next = Math.round(hC + (avg - hC) * 0.45);
            }
            tmp[idx] = Math.max(Z_MIN, Math.min(64, next));
          }
        }
        hmap.set(tmp);
      }
    }

    function buildStandableMap() {
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const edgeY = my < 2 || my >= mh - 2;
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          const h0 = hmap[idx];
          const mat = matMap[idx];
          cliffTopMap[idx] = h0;

          if (mat === MAT_WATER) {
            standableMap[idx] = 0;
            continue;
          }
          if (mat === MAT_BRIDGE || mat === MAT_LILYPAD) {
            standableMap[idx] = 1;
            continue;
          }
          if (edgeY || mx < 2 || mx >= mw - 2) {
            standableMap[idx] = 1;
            continue;
          }

          let min3 = h0, max3 = h0;
          for (let dy = -1; dy <= 1; dy++) {
            const nbRow = (my + dy) * mw;
            for (let dx = -1; dx <= 1; dx++) {
              const hv = hmap[nbRow + mx + dx];
              if (hv < min3) min3 = hv;
              if (hv > max3) max3 = hv;
            }
          }

          if (max3 - h0 <= 3 && h0 - min3 <= 3) {
            standableMap[idx] = 1;
            continue;
          }

          let nearCount = 0;
          let min5 = h0;
          for (let dy = -2; dy <= 2; dy++) {
            const nbRow = (my + dy) * mw;
            for (let dx = -2; dx <= 2; dx++) {
              const nb = nbRow + mx + dx;
              const hv = hmap[nb];
              if (hv < min5) min5 = hv;
              if (matMap[nb] !== MAT_WATER && Math.abs(hv - h0) <= 3) {
                nearCount++;
              }
            }
          }

          if (h0 - min5 <= 2) {
            standableMap[idx] = 1;
            continue;
          }
          if (max3 - h0 > 4 && h0 - min3 > 4) {
            standableMap[idx] = 0;
          } else {
            standableMap[idx] = nearCount >= 14 ? 1 : 0;
          }
        }
      }

      // Segundo passo: para células não-pisáveis em falésias secas, guarda altura máxima local (r=5)
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const y0 = Math.max(0, my - 5);
        const y1 = Math.min(mh - 1, my + 5);
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          if (standableMap[idx] !== 0 || matMap[idx] === MAT_WATER) continue;
          const x0 = Math.max(0, mx - 5);
          const x1 = Math.min(mw - 1, mx + 5);
          let maxH = hmap[idx];
          for (let ny = y0; ny <= y1; ny++) {
            const nRow = ny * mw;
            for (let nx = x0; nx <= x1; nx++) {
              const hv = hmap[nRow + nx];
              if (hv > maxH) maxH = hv;
            }
          }
          cliffTopMap[idx] = maxH;
        }
      }
    }

    function setCirclePatch(cx, cy, radius, height, mat, biome, isCliff = true) {
      const x0 = Math.max(0, Math.floor((cx - radius - 2) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + radius + 2) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - radius - 2) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + radius + 2) / VOX + HALF_GRID));
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const n = fbm2d(wx * 0.14, wy * 0.14) * 1.1;
          if (Math.hypot(wx - cx, wy - cy) <= radius + n) {
            const idx = my * mw + mx;
            hmap[idx] = height;
            matMap[idx] = mat;
            if (biome !== null) biomeMap[idx] = biome;
            if (isCliff) cliffMask[idx] = 1;
          }
        }
      }
    }

    function setBridgeRect(xMin, xMax, yMin, yMax, z, mat = MAT_BRIDGE, biome = 5) {
      const gx0 = Math.max(0, Math.floor(xMin / VOX + HALF_GRID));
      const gx1 = Math.min(mw - 1, Math.floor(xMax / VOX + HALF_GRID));
      const gy0 = Math.max(0, Math.floor(yMin / VOX + HALF_GRID));
      const gy1 = Math.min(mh - 1, Math.floor(yMax / VOX + HALF_GRID));
      for (let my = gy0; my <= gy1; my++) {
        for (let mx = gx0; mx <= gx1; mx++) {
          const idx = my * mw + mx;
          hmap[idx] = z;
          matMap[idx] = mat;
          biomeMap[idx] = biome;
          cliffMask[idx] = 1;
        }
      }
    }

    // 4.1. Construção dos 8 Biomas no Heightfield Contínuo 720×720
    function initOrganicWorld() {
      // Base inicial: plano verde Z=0
      hmap.fill(0);
      matMap.fill(MAT_GRASS);
      biomeMap.fill(0);

      // Divisão orgânica inicial dos biomas por região
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const idx = my * mw + mx;
          const wNoise = fbm2d(wx * 0.008, wy * 0.008) * 36;
          if (wy + wNoise > 430) biomeMap[idx] = 3; // Praia Sul
          else if (wx + wNoise > 84 && wy + wNoise < -10) biomeMap[idx] = 7; // Montanha NE
          else if (wx + wNoise > 84 && wy + wNoise >= -10) biomeMap[idx] = 6; // Bosque SE
          else if (wy + wNoise < -170 && wx + wNoise < 70) biomeMap[idx] = 4; // Jardim Zen NW
          else if (wx + wNoise < -400 && wy + wNoise >= -170) biomeMap[idx] = 1; // Girassóis W
          else if (wy + wNoise >= 240 && wx + wNoise < 60) biomeMap[idx] = 2; // Ruínas
          else biomeMap[idx] = 0; // Vila
        }
      }

      // Moldura natural elevada nas bordas Oeste, Norte e Leste (Sul aberto para o mar!)
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy > 430) continue;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const rawEdgeDist = Math.min(wx - WORLD_MIN, WORLD_MAX - wx, wy - WORLD_MIN);
          if (rawEdgeDist >= 88) continue;
          const wp = warp2d(wx, wy, 0.010, 20);
          const edgeDist = Math.min(wp.x - WORLD_MIN, WORLD_MAX - wp.x, wp.y - WORLD_MIN);
          if (edgeDist >= 68) continue;
          const ridge = ridgedFbm(wp.x * 0.014 + 3.7, wp.y * 0.014 + 1.9, 3);
          const span = 52 + ridge * 16;
          if (edgeDist < span) {
            const t = Math.max(0, Math.min(1, (span - edgeDist) / 36));
            const peakH = 14 + ridge * 12;
            const idx = my * mw + mx;
            hmap[idx] = Math.max(hmap[idx], Math.round(peakH * Math.pow(t, 1.15)));
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 1: CAMPOS DE GIRASSOL (Oeste) — cristas ondulantes orgânicas
      // ---------------------------------------------------------------------
      pullRidge([[-600, -90], [-550, -50], [-490, -10]], 88, [12, 14, 7], { warpAmp: 22, smoothK: 8, ridgeAmp: 0.24, mat: MAT_GRASS, biome: 1 });
      pullRidge([[-580, 140], [-540, 164], [-485, 210]], 76, [10, 8, 5], { warpAmp: 18, smoothK: 7, ridgeAmp: 0.22, mat: MAT_GRASS, biome: 1 });

      // ---------------------------------------------------------------------
      // BIOMA 0: VILA DA CLAREIRA (Centro-Oeste) — rampa orgânica Z=0..6
      // ---------------------------------------------------------------------
      pullHill(-190, -44, 62, 6, 1.35, 0.16, MAT_GRASS, 0);

      // ---------------------------------------------------------------------
      // BIOMA 4: JARDIM ZEN & PORTAL TORII (Noroeste)
      // ---------------------------------------------------------------------
      pullPlateau(-320, -340, 228, 180, 16, 32, 0.14, false, MAT_GRASS, 4);
      // Extensão Leste até Ponte Norte (wx=28, wy=-230)
      pullPlateau(-64, -236, 104, 52, 16, 28, 0.10, false, MAT_GRASS, 4);
      // Rampa larga da Vila (-290, -110) -> Jardim Zen (-290, -216)
      paintRampPath(-290, -110, 0, -290, -216, 16, 26, MAT_PATH, 4);
      // Terraço Superior Zen (Z=32 -> Z=48)
      pullPlateau(-510, -510, 96, 76, 32, 16, 0.12, false, MAT_GRASS, 4);
      pullPlateau(-550, -550, 48, 40, 48, 8, 0.10, true, MAT_STONE, 4);
      // Alameda Zen (~34u de largura!) passando sob o Torii (-290, -270)
      paintOrganicPath([[-290, -210], [-290, -410]], 17, MAT_PATH, 4, 16);
      // Lago Zen (~76u de diâmetro!) em (-460, -390)
      setCirclePatch(-460, -390, 46, 16, MAT_SAND, 4, true);
      setCirclePatch(-460, -390, 38, 13, MAT_WATER, 4, true);

      // ---------------------------------------------------------------------
      // BIOMA 6: BOSQUE DOS COGUMELOS SALTITANTES (Sudeste)
      // ---------------------------------------------------------------------
      // Circuito aéreo de cogumelos: apoio Z=12 e Z=24 para caps Z=16 / 28 / 40
      pullPlateau(330, 176, 14, 14, 12, 16, 0.12, false, MAT_STONE, 6, false, false); // Apoio #2 (cap Z=28)
      pullPlateau(379, 192, 26, 14, 24, 18, 0.12, false, MAT_GRASS, 6, false, false); // Apoio #3 e #4 (caps Z=40)
      pullPlateau(428, 176, 14, 14, 12, 16, 0.12, false, MAT_STONE, 6, false, false); // Apoio #5 (cap Z=28)
      pullRidge([[490, 290], [550, 330], [610, 385]], 84, [11, 16, 12], { warpAmp: 22, smoothK: 8, ridgeAmp: 0.25, mat: MAT_GRASS, biome: 6 });

      // ---------------------------------------------------------------------
      // BIOMA 7: MONTANHA DO PICO SAKURA (Nordeste, Z=64 topo)
      // ---------------------------------------------------------------------
      // Contraforte Oeste Z=16 onde chega a Ponte Norte (wx=140..210, wy=-230)
      pullRidge([[148, -230], [192, -220], [244, -184], [292, -242]], 50, [16, 17, 24, 34], { warpAmp: 20, smoothK: 8, ridgeAmp: 0.26, mat: MAT_STONE, biome: 7 });
      pullPlateau(156, -230, 20, 16, 16, 10, 0.06, false, MAT_STONE, 7, false, false);
      // Paredão escarpado Oeste/Sul (intransponível direto!)
      pullPlateau(320, -360, 144, 124, 48, 6, 0.12, true, MAT_STONE, 7, false, true);
      // Espigões geológicos irradiando da montanha
      pullRidge([[360, -350], [460, -320], [545, -240], [500, -130], [435, -65]], 92, [58, 48, 34, 20, 6], { warpAmp: 26, ridgeAmp: 0.30, smoothK: 10, terraceStep: 14, terraceStrength: 0.35, mat: MAT_GRASS, biome: 7 });
      pullRidge([[350, -390], [440, -455], [535, -430], [565, -340]], 82, [58, 52, 42, 34], { warpAmp: 24, ridgeAmp: 0.30, smoothK: 10, terraceStep: 14, terraceStrength: 0.35, mat: MAT_GRASS, biome: 7 });
      // Cume arredondado do Pico Sakura (Z=64)
      pullPlateau(320, -360, 102, 90, 64, 22, 0.14, false, MAT_PEAK, 7, false, true);
      // Trilha contínua escavada em patamar subindo a encosta (Z=0 -> Z=64)
      carveBenchTrail([
        [410, -44, 0],
        [450, -90, 10],
        [502, -152, 20],
        [548, -226, 30],
        [546, -322, 40],
        [514, -408, 48],
        [454, -462, 56],
        [392, -430, 62],
        [354, -384, 64]
      ], 13, 28, MAT_PATH, 7);

      // ---------------------------------------------------------------------
      // BIOMA 5: RIO SINUOSO & CACHOEIRA ORGÂNICA (largura ~54u)
      // ---------------------------------------------------------------------
      const riverPts = [
        [80, -716], [104, -530], [88, -304], [56, -110],
        [76, 80], [96, 290], [68, 490], [76, 620]
      ];
      carveRiverPath(riverPts, 54, -6);

      // Cachoeira Vertical na Falésia Oeste (wy=-330) + Poço + Riacho Plano até o Rio
      // Parte C1: Riacho plano (Z=-5) ligando o pé da cachoeira (wx=144) ao rio principal (wx=90)
      carveRiverPath([[144, -330], [120, -326], [90, -324]], 24, -5);

      // Parte C2: Poço circular com borda rasa arenosa ao pé da falésia (sem corroer a rocha alta h > 10)
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy < -356 || wy > -304) continue;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          if (wx < 134 || wx > 190) continue;
          const idx = my * mw + mx;
          if (hmap[idx] > 10) continue;
          const d = Math.hypot(wx - 158, wy + 330) + fbm2d(wx * 0.12, wy * 0.12) * 1.4;
          if (d <= 17) {
            hmap[idx] = -5;
            matMap[idx] = MAT_WATER;
            biomeMap[idx] = 5;
            cliffMask[idx] = 1;
          } else if (d <= 21 && matMap[idx] !== MAT_WATER && hmap[idx] <= 2) {
            hmap[idx] = Math.min(hmap[idx], 0);
            matMap[idx] = MAT_SAND;
            biomeMap[idx] = 5;
          }
        }
      }

      // Partes A & B: Nascente rebaixada no platô (h>=44 -> 46) + Cortina vertical colada à encosta da falésia (1<=h<=48)
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy < -350 || wy > -310) continue;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          if (wx < 150 || wx > 226) continue;
          const idx = my * mw + mx;
          const curH = hmap[idx];
          const n = fbm2d(wx * 0.05, wy * 0.05) * 4.5;
          if (Math.abs(wy + 330 + n) <= 12.0) {
            if (wx >= 172 && curH >= 44) {
              // Parte A: Nascente encaixada 2u abaixo da borda Z=48 da montanha
              hmap[idx] = 46;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 7;
              cliffMask[idx] = 1;
            } else if (wx <= 198 && curH >= 1 && curH <= 48) {
              // Parte B: Cortina vertical acompanhando o relevo real da falésia (zero rampa flutuante)
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 7;
              cliffMask[idx] = 1;
            }
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 3: PRAIA DOURADA, BAÍA SUL, PÍER, 6 VITÓRIAS-RÉGIAS & FAROL
      // ---------------------------------------------------------------------
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy < 410) continue;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const idx = my * mw + mx;
          const wave = fbm2d(wx * 0.007 + 2.5, 1.2) * 28;
          const shoreY = 504 + wave;
          const sandStart = 424 + wave * 0.7;

          if (wy >= shoreY + 8) {
            hmap[idx] = -6;
            matMap[idx] = MAT_WATER;
            biomeMap[idx] = 3;
          } else if (wy >= shoreY) {
            hmap[idx] = -4;
            matMap[idx] = MAT_WATER;
            biomeMap[idx] = 3;
          } else if (wy >= shoreY - 10) {
            if (matMap[idx] !== MAT_WATER) {
              hmap[idx] = -1;
              matMap[idx] = MAT_SAND;
              biomeMap[idx] = 3;
            }
          } else if (wy >= sandStart) {
            if (matMap[idx] !== MAT_WATER) {
              hmap[idx] = Math.max(0, hmap[idx]);
              matMap[idx] = MAT_SAND;
              biomeMap[idx] = 3;
            }
          }
        }
      }

      // Ilhota Tropical Sul no Mar Sul
      pullPlateau(132, 572, 48, 40, 1, 10, 0.14, true, MAT_SAND, 3, true);
      // Promontório Rochoso do Farol (Sudoeste) + Rampa de Acesso
      paintRampPath(-370, 476, 0, -424, 512, 14, 20, MAT_SAND, 3);
      pullPlateau(-460, 540, 88, 72, 14, 10, 0.14, true, MAT_STONE, 3);

      // Píer Longo de Madeira (Z=2)
      setBridgeRect(-132, -108, 460, 590, 2, MAT_BRIDGE, 3);
      // 6 Vitórias-Régias saltáveis sobre a água até a ilhota tropical sul!
      for (const [lx, ly] of [[-82, 574], [-48, 588], [-14, 572], [20, 588], [54, 572], [86, 582]]) {
        setCirclePatch(lx, ly, 12.0, 0, MAT_LILYPAD, 3, true);
      }

      // ---------------------------------------------------------------------
      // PONTES SOBRE O RIO & PEDRAS DE TRAVESSIA
      // ---------------------------------------------------------------------
      // Ponte Central de Madeira (Z=2, Vila <-> Bosque)
      setBridgeRect(16, 136, 56, 88, 2, MAT_BRIDGE, 5);
      // Ponte Norte de Pedra (Z=16, Jardim Zen <-> Contraforte da Montanha)
      setBridgeRect(24, 144, -246, -214, 16, MAT_BRIDGE, 5);
      // Pedras de Travessia ao Sul (Z=2) cruzando os ~54u do rio
      setCirclePatch(66, 330, 10.0, 2, MAT_STONE, 5, true);
      setCirclePatch(90, 330, 10.0, 2, MAT_STONE, 5, true);
      setCirclePatch(114, 330, 10.0, 2, MAT_STONE, 5, true);

      // ---------------------------------------------------------------------
      // BIOMA 2: RUÍNAS ORGÂNICAS & 4 MONOLITOS DE TESTE (cliffMask=1)
      // ---------------------------------------------------------------------
      // Pátio plano Z=0 em volta de wy=252..420 garantindo base limpa para os testes
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy < 252 || wy > 420) continue;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          if (wx < -372 || wx > 36) continue;
          const idx = my * mw + mx;
          if (matMap[idx] !== MAT_WATER) {
            hmap[idx] = 0;
            biomeMap[idx] = 2;
            cliffMask[idx] = 1;
            if (wy >= 272 && wy <= 404 && wx >= -332 && wx <= 28) {
              matMap[idx] = MAT_PATH;
            }
          }
        }
      }
      // 4 Monolitos Arredondados bem espaçados em wy=330 (rx=26, ry=22, x=-280,-190,-100,-10)
      pullPlateau(-280, 330, 26, 22, 6,  8.0, 0.06, true, MAT_STONE, 2, false, false); // A: Z=6  (sobe andando!)
      pullPlateau(-190, 330, 26, 22, 16, 2.0, 0.06, true, MAT_STONE, 2, false, false); // B: Z=16 (pulo 1H!)
      pullPlateau(-100, 330, 26, 22, 32, 2.0, 0.06, true, MAT_STONE, 2, false, false); // C: Z=32 (pulo 2H máx!)
      pullPlateau(-10,  330, 26, 22, 48, 2.0, 0.06, true, MAT_STONE, 2, false, false); // D: Z=48 (3H bloqueado!)

      // ---------------------------------------------------------------------
      // TRILHAS ORGÂNICAS CONECTANDO VILA <-> BIOMAS
      // ---------------------------------------------------------------------
      paintOrganicPath([[-220, 60], [16, 72]], 16, MAT_PATH, 0, 0);          // Vila -> Ponte Central
      paintOrganicPath([[136, 72], [250, 110], [380, 60], [410, -44]], 15, MAT_PATH, 6); // Ponte -> Bosque / Base Montanha
      paintOrganicPath([[-220, 60], [-420, 60]], 15, MAT_PATH, 0, 0);      // Vila -> Girassóis
      paintOrganicPath([[-220, 60], [-220, 270]], 16, MAT_PATH, 0, 0);     // Vila -> Ruínas
      paintOrganicPath([[-220, 60], [-290, -110]], 15, MAT_PATH, 0, 0);    // Vila -> Rampa Zen
      paintOrganicPath([[-144, 390], [-120, 460]], 15, MAT_PATH, 2, 0);    // Ruínas -> Píer
      paintOrganicPath([[-220, 60], [-305, 90]], 11, MAT_PATH, 0, 0);      // Vila -> Cabana 1
      paintOrganicPath([[-220, 60], [-162, 134]], 11, MAT_PATH, 0, 0);     // Vila -> Cabana 2

      // Garante platôs planos Z=0 sob a Cabana 1 (-350, 90) e Cabana 2 (-120, 150)
      for (const [x0w, x1w, y0w, y1w] of [[-416, -280, 30, 160], [-180, -60, 100, 200]]) {
        const gx0 = Math.max(0, Math.floor(x0w / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(x1w / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(y0w / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(y1w / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const idx = row + mx;
            hmap[idx] = 0;
            cliffMask[idx] = 1;
          }
        }
      }

      // Erosão térmica + hidráulica determinística, seguida por relaxamento elástico final
      thermalAndHydraulicErosion(5, 260);
      elasticChainRelax(1);
      buildStandableMap();
    }
    initOrganicWorld();

    function getCellAt(wx, wy) {
      const mx = Math.floor(wx / VOX + HALF_GRID);
      const my = Math.floor(wy / VOX + HALF_GRID);
      if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
      const idx = my * mw + mx;
      const b = biomeMap[idx];
      return {
        mx, my, idx,
        h: hmap[idx],
        mat: matMap[idx],
        biomeId: b,
        biomeKey: BIOME_KEYS[b],
        biome: BIOME_NAMES[b],
        isCliff: cliffMask[idx] === 1,
        standable: standableMap[idx] === 1,
        cliffTop: cliffTopMap[idx]
      };
    }

    function getHeightAt(wx, wy) {
      const mx = Math.floor(wx / VOX + HALF_GRID);
      const my = Math.floor(wy / VOX + HALF_GRID);
      if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
      return hmap[my * mw + mx];
    }

    // =========================================================================
    // 5. SISTEMA DE COLISÃO UNIFICADO (5 Modos) & POPULAÇÃO DOS 23 MODELOS
    // =========================================================================
    const PROP_COLLIDER_META = {
      pine_tree:       { mode: 'solid',    r: 5.0,  h: 48, shadowR: 13 },
      sakura_oak:      { mode: 'solid',    r: 9.5,  h: 68, shadowR: 25 },
      cozy_cabin:      { mode: 'box',      halfW: 23.5, halfD: 20.5, h: 54, shadowR: 28 },
      lighthouse:      { mode: 'solid',    r: 14.5, h: 84, shadowR: 20 },
      campfire:        { mode: 'solid',    r: 5.2,  h: 9,  shadowR: 6 },
      wood_sign:       { mode: 'solid',    r: 3.6,  h: 14 },
      ruin_pillar:     { mode: 'solid',    r: 7.5,  h: 34, shadowR: 11 },
      stone_lantern:   { mode: 'solid',    r: 5.5,  h: 24, shadowR: 8 },
      beach_umbrella:  { mode: 'solid',    r: 2.5,  h: 28, shadowR: 12 },
      wood_boat:       { mode: 'box',      halfW: 15.0, halfD: 8.5,  h: 12, shadowR: 14 },
      bush_berry:      { mode: 'solid',    r: 4.8,  h: 9,  shadowR: 6 },
      sunflower:       { mode: 'solid',    r: 3.2,  h: 15 },
      pumpkin_patch:   { mode: 'solid',    r: 5.8,  h: 8 },
      mushroom_giant:  { mode: 'platform', r: 7.8,  h: 16, shadowR: 10 },
      boulder_large:   { mode: 'platform', r: 6.2,  h: 12, shadowR: 8 },
      hay_bale:        { mode: 'platform', r: 6.8,  h: 10, shadowR: 8 },
      tree_stump:      { mode: 'platform', r: 6.5,  h: 10, shadowR: 8 },
      torii_gate:      { mode: 'arch',     offset: 16.5, r: 3.8, h: 54, shadowR: 18 },
      flower_tuft:     { mode: 'none' },
      grass_tuft_short:{ mode: 'none' },
      grass_tuft_tall: { mode: 'none' }
    };

    const props = [];
    const propColliders = [];
    const platformColliders = [];
    const fishes = [];
    const npcs = [];

    function stampPropShadowAndClearGrass(wx, wy, shadowR, footprintR) {
      const rMax = Math.max(shadowR || 0, footprintR || 0);
      if (rMax <= 0) return;
      const x0 = Math.max(0, Math.floor((wx - rMax) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((wx + rMax) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((wy - rMax) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((wy + rMax) / VOX + HALF_GRID));
      for (let my = y0; my <= y1; my++) {
        const gy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const gx = (mx - HALF_GRID + 0.5) * VOX;
          const d = Math.hypot(gx - wx, gy - wy);
          const idx = my * mw + mx;
          if (footprintR && d <= footprintR + 1.5) noGrassMask[idx] = 1;
          if (shadowR && d <= shadowR) {
            const strength = Math.round((1 - d / shadowR) * 42);
            if (strength > shadowMask[idx]) shadowMask[idx] = strength;
          }
        }
      }
    }

    function addProp(modelKey, wx, wy, options = {}) {
      const c = getCellAt(wx, wy);
      if (!c || !propModels[modelKey]) return;
      const meta = PROP_COLLIDER_META[modelKey] || { mode: 'none' };

      if (!options.allowOnPath && meta.mode !== 'none' && meta.mode !== 'arch') {
        if (c.mat === MAT_PATH || c.mat === MAT_BRIDGE || c.mat === MAT_WATER || c.mat === MAT_LILYPAD) {
          return;
        }
      }

      const scale = options.scale || 1.0;
      const liftZ = options.liftZ !== undefined ? options.liftZ : c.h;
      const angle = options.angle || 0;
      const model = propModels[modelKey];
      const baseZ = Math.round(liftZ);
      const topZ = baseZ + Math.ceil(model.count * scale);

      const item = {
        id: `${modelKey}_${props.length}`,
        modelKey,
        model,
        wx, wy,
        wz: liftZ,
        baseZ,
        topZ,
        selfAngle: angle,
        scale,
        isFire: modelKey === 'campfire' || modelKey === 'stone_lantern',
        isPlatform: meta.mode === 'platform',
        platTopZ: meta.mode === 'platform' ? liftZ + meta.h * scale : liftZ
      };
      props.push(item);

      const footR = meta.mode === 'box'
        ? Math.max(meta.halfW, meta.halfD) * scale
        : (meta.r || 4) * scale;
      stampPropShadowAndClearGrass(wx, wy, (meta.shadowR || 0) * scale, meta.mode !== 'none' ? footR : 0);

      if (meta.mode === 'solid') {
        propColliders.push({
          shape: 'circle', wx, wy,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey
        });
      } else if (meta.mode === 'box') {
        propColliders.push({
          shape: 'box', wx, wy,
          halfW: meta.halfW * scale, halfD: meta.halfD * scale,
          angle, baseZ: liftZ, colH: meta.h * scale, modelKey
        });
      } else if (meta.mode === 'platform') {
        platformColliders.push({
          wx, wy, r: meta.r * scale,
          baseZ: liftZ, topZ: liftZ + meta.h * scale, modelKey
        });
      } else if (meta.mode === 'arch') {
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);
        const off = meta.offset * scale;
        propColliders.push({
          shape: 'circle',
          wx: wx - off * cosA, wy: wy - off * sinA,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey
        });
        propColliders.push({
          shape: 'circle',
          wx: wx + off * cosA, wy: wy + off * sinA,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey
        });
      }
    }

    function addFish(wx, wy, label, extraZ = 0) {
      const c = getCellAt(wx, wy);
      const baseH = c ? c.h : 0;
      fishes.push({
        id: `fish_${fishes.length}`,
        label,
        wx, wy,
        baseZ: baseH + extraZ,
        collected: false
      });
    }

    function isNearPathOrWater(wx, wy, bufferU = 8) {
      const step = VOX;
      for (let dy = -bufferU; dy <= bufferU; dy += step) {
        for (let dx = -bufferU; dx <= bufferU; dx += step) {
          const c = getCellAt(wx + dx, wy + dy);
          if (!c) return true;
          if (c.mat === MAT_PATH || c.mat === MAT_BRIDGE || c.mat === MAT_WATER || c.mat === MAT_LILYPAD) {
            return true;
          }
        }
      }
      return false;
    }

    function addForestProp(modelKey, wx, wy, options = {}) {
      if (isNearPathOrWater(wx, wy, options.pathBuffer || 8)) return;
      if (Math.hypot(wx + 220, wy - 60) < 26) return; // Mantém spawn livre
      const meta = PROP_COLLIDER_META[modelKey] || { r: 5 };
      const minGap = (meta.r || 5) + 6;
      for (const sc of propColliders) {
        if (isPointInPropCollider(wx, wy, sc, minGap)) return;
      }
      for (const pc of platformColliders) {
        if (Math.hypot(wx - pc.wx, wy - pc.wy) < pc.r + minGap) return;
      }
      addProp(modelKey, wx, wy, options);
    }

    function populateWorldObjects() {
      // 0. Vila da Clareira (Mini-Vila com 2 Cabanas, fogueira, horta e tocos)
      addProp('cozy_cabin', -350, 90);
      addProp('cozy_cabin', -120, 150);
      addProp('campfire', -190, 20);
      addProp('wood_sign', -180, 96, { angle: 0.22 });
      addProp('pumpkin_patch', -310, 168);
      addProp('pumpkin_patch', -284, 174);
      addProp('tree_stump', -175, 102);
      addProp('tree_stump', -252, 130);
      addProp('flower_tuft', -264, 116);
      addProp('flower_tuft', -232, 24);
      addProp('flower_tuft', -154, 184);
      addProp('bush_berry', -136, 198);
      addProp('bush_berry', -386, 152);
      addForestProp('pine_tree', -390, -36);
      addForestProp('pine_tree', -124, -50);
      addForestProp('pine_tree', -380, 192);
      addForestProp('pine_tree', -80, 215);
      addForestProp('pine_tree', -290, 22);
      addForestProp('pine_tree', -50, -35);

      // 1. Campos de Girassol (~20 girassóis + 4 fardos platform)
      for (const [tx, ty] of [
        [-550, 20], [-510, 64], [-576, -20], [-496, -84], [-584, -90],
        [-516, 144], [-570, 176], [-480, 216], [-604, 84], [-470, -24],
        [-620, -40], [-598, 22], [-538, -116], [-456, -124], [-612, 136],
        [-528, 210], [-442, 166], [-494, 24], [-556, 112], [-618, -108]
      ]) {
        addProp('sunflower', tx, ty);
      }
      addProp('hay_bale', -450, 124);
      addProp('hay_bale', -510, 104);
      addProp('hay_bale', -560, 180);
      addProp('hay_bale', -480, -30);
      addProp('tree_stump', -464, 208);
      addProp('flower_tuft', -580, 124);
      addProp('flower_tuft', -504, -54);
      addForestProp('pine_tree', -628, -162);
      addForestProp('pine_tree', -624, 240);
      addForestProp('pine_tree', -430, -162);

      // 2. Ruínas Orgânicas (Pátio sul em wy=330)
      addProp('ruin_pillar', -344, 276, { allowOnPath: true });
      addProp('ruin_pillar', 32,   276, { allowOnPath: true });
      addProp('stone_lantern', -344, 384, { allowOnPath: true });
      addProp('stone_lantern', 32,   384, { allowOnPath: true });
      addProp('boulder_large', -336, 330, { allowOnPath: true });
      addProp('flower_tuft', -240, 404);
      addProp('flower_tuft', -55,  404);

      // 3. Praia Dourada, Enseada & Farol Monumental
      addProp('lighthouse', -476, 548);
      addProp('stone_lantern', -404, 516);
      addProp('beach_umbrella', -240, 468);
      addProp('beach_umbrella', -40,  472);
      addProp('beach_umbrella', 180,  468);
      addProp('wood_boat', 230,  480, { angle: 0.16 });
      addProp('wood_boat', -310, 484, { angle: -0.22 });
      addProp('boulder_large', 156, 580);
      addProp('boulder_large', -360, 504);

      // 4. Jardim Zen & Portal Torii Gigante
      addProp('torii_gate', -290, -270, { angle: 0, allowOnPath: true });
      addProp('stone_lantern', -364, -270);
      addProp('stone_lantern', -216, -270);
      addProp('stone_lantern', -384, -380);
      addProp('bush_berry', -184, -390);
      addProp('flower_tuft', -316, -420);
      addProp('boulder_large', -470, -490);
      addProp('ruin_pillar', -508, -496);
      addForestProp('pine_tree', -168, -450);
      addForestProp('pine_tree', -420, -490);
      addForestProp('pine_tree', -560, -310);
      addForestProp('pine_tree', -140, -560);
      addForestProp('pine_tree', -360, -570);

      // 6. Bosque dos Cogumelos Saltitantes (7 cogumelos gigantes em circuito aéreo)
      addProp('mushroom_giant', 296, 160);  // #1 Cap Z=16
      addProp('mushroom_giant', 330, 176);  // #2 Em Z=12 -> Cap Z=28!
      addProp('mushroom_giant', 362, 192);  // #3 Em Z=24 -> Cap Z=40!
      addProp('mushroom_giant', 396, 192);  // #4 Em Z=24 -> Cap Z=40!
      addProp('mushroom_giant', 428, 176);  // #5 Em Z=12 -> Cap Z=28!
      addProp('mushroom_giant', 462, 160);  // #6 Cap Z=16
      addProp('mushroom_giant', 256, 290);  // #7 Cap Z=16 (âncora sul)
      for (const [tx, ty] of [
        [210, 152], [236, 230], [320, 350], [456, 344], [510, 184],
        [590, 220], [580, 370], [204, 364], [616, 290], [496, 84],
        [340, 290], [420, 270]
      ]) {
        addForestProp('pine_tree', tx, ty);
      }
      addProp('tree_stump', 252, 172);
      addProp('tree_stump', 494, 158);
      addProp('hay_bale', 536, 316);
      addProp('boulder_large', 496, 84);
      addProp('boulder_large', 310, 240);
      addProp('boulder_large', 575, 295);
      addProp('bush_berry', 360, 284);
      addProp('bush_berry', 450, 248);
      addProp('flower_tuft', 272, 144);
      addProp('flower_tuft', 440, 160);

      // 7. Montanha & Pico Sakura (Trilha em espiral mantida 100% livre!)
      addProp('sakura_oak', 300, -384);
      addProp('stone_lantern', 372, -324, { allowOnPath: true });
      addProp('stone_lantern', 272, -316, { allowOnPath: true });
      addProp('flower_tuft', 292, -316);
      addProp('flower_tuft', 364, -384);
      addProp('boulder_large', 224, -192);
      addForestProp('pine_tree', 284, -110);
      addForestProp('pine_tree', 250, -520);
      addForestProp('pine_tree', 600, -470);
      addForestProp('pine_tree', 620, -60);
      addForestProp('pine_tree', 190, -450);

      // Florestas Densas nas bordas arborizadas (Norte, Oeste, Leste) — total ~60 pinheiros!
      for (let wx = -640; wx <= 640; wx += 116) {
        if (Math.abs(wx - 80) < 68) continue;
        addForestProp('pine_tree', wx, -682);
      }
      for (let wy = -580; wy <= 360; wy += 118) {
        addForestProp('pine_tree', -682, wy);
        addForestProp('pine_tree', 682, wy);
      }
      // Bosques orgânicos secundários de borda
      for (const [bx, by] of [
        [-640, -610], [-470, -630], [180, -620], [420, -620],
        [-635, -360], [630, -240], [635, 110], [-630, 320]
      ]) {
        addForestProp('pine_tree', bx, by);
      }
      for (const [bx, by] of [
        [-600, -540], [-360, -620], [230, -580], [580, -390], [600, 140], [-610, 290]
      ]) {
        addForestProp('bush_berry', bx, by);
      }

      // 20 PEIXES DOURADOS COLECIONÁVEIS (distribuídos pelos 8 biomas)
      addFish(-190, -44,  'Rampa da Vila');                  // #1  Vila (Z=6)
      addFish(-175, 102,  'Toco da Vila', 10);               // #2  Vila (Z=10)
      addFish(-450, 124,  'Fardo dos Girassóis', 10);        // #3  Girassóis (Z=10)
      addFish(-550, -50,  'Colina dos Girassóis');           // #4  Girassóis (Z=14)
      addFish(-540, 164,  'Campo Sul dos Girassóis');        // #5  Girassóis (Z=8)
      addFish(-190, 330,  'Monolito Médio das Ruínas');      // #6  Ruínas (Z=16)
      addFish(-10,  330,  'Torre das Ruínas');               // #7  Ruínas (Z=48)
      addFish(-120, 580,  'Ponta do Píer');                  // #8  Praia (Z=2)
      addFish(-410, 564,  'Mirante do Farol');               // #9  Praia (Z=14)
      addFish(132,  572,  'Ilhota das Vitórias-Régias');     // #10 Praia (Z=1)
      addFish(320,  476,  'Enseada Leste');                  // #11 Praia (Z=0)
      addFish(76,   72,   'Ponte Central');                  // #12 Rio (Z=2)
      addFish(90,   330,  'Pedra do Rio');                   // #13 Rio (Z=2)
      addFish(84,   -230, 'Ponte Norte');                    // #14 Rio (Z=16)
      addFish(-290, -390, 'Alameda Pós-Torii');              // #15 Zen (Z=16)
      addFish(-550, -550, 'Mirante Zen');                    // #16 Zen (Z=48)
      addFish(330,  176,  'Cogumelo Médio', 16);             // #17 Cogumelos (Z=28)
      addFish(396,  192,  'Cogumelo Alto', 16);              // #18 Cogumelos (Z=40)
      addFish(546,  -322, 'Patamar da Montanha');            // #19 Montanha (Z=40)
      addFish(352,  -352, 'Pico Sakura Lendário');           // #20 Montanha (Z=64)

      // NPCs: Galinha Popó na Vila + 3 Pintinhos Piu nos Girassóis
      const popoCell = getCellAt(-216, 112);
      npcs.push({
        kind: 'chicken', name: 'Popó', model: chickenModel, scale: 0.72,
        x: -216, y: 112, z: popoCell ? popoCell.h : 0, homeX: -216, homeY: 112, roamR: 48,
        selfAngle: 0, walkPhase: 0, timer: 1.4, moving: true, dirX: 1, dirY: 0,
        speech: null
      });
      for (const [cx, cy] of [[-520, 40], [-530, -30], [-460, 150]]) {
        const c = getCellAt(cx, cy);
        npcs.push({
          kind: 'chick', name: 'Piu', model: propModels.baby_chick, scale: 0.95,
          x: cx, y: cy, z: c ? c.h : 0, homeX: cx, homeY: cy, roamR: 38,
          selfAngle: 0, walkPhase: 0, timer: 0.8 + Math.random(), moving: true, dirX: -1, dirY: 0.5,
          speech: null
        });
      }
    }
    populateWorldObjects();

    // =========================================================================
    // 6. PRÉ-BAKE TIGHT-CROP BOUNDED SLICES (terrainSlices + grassTipSlices)
    // =========================================================================
    const IS_LE = (new Uint8Array(new Uint32Array([0x11223344]).buffer))[0] === 0x44;
    function packRGBA(r, g, b, a = 255) {
      if (IS_LE) return ((a & 255) << 24) | ((b & 255) << 16) | ((g & 255) << 8) | (r & 255);
      return ((r & 255) << 24) | ((g & 255) << 16) | ((b & 255) << 8) | (a & 255);
    }

    function shadePack(rgb, delta, shadowPct = 0) {
      const f = 1 - shadowPct * 0.01;
      const r = Math.max(0, Math.min(255, Math.round((rgb[0] + delta) * f)));
      const g = Math.max(0, Math.min(255, Math.round((rgb[1] + delta) * f)));
      const b = Math.max(0, Math.min(255, Math.round((rgb[2] + delta) * f)));
      return packRGBA(r, g, b, 255);
    }

    const PAL_GRASS_BASE = [
      [88, 178, 78], [80, 168, 72], [96, 188, 84], [108, 198, 90]
    ];
    const PAL_PATH = [[223, 182, 132], [211, 166, 115]];
    const PAL_SAND = [[243, 221, 169], [234, 208, 148]];
    const PAL_STONE = [[180, 186, 196], [163, 170, 181]];
    const PAL_BRIDGE = [[185, 122, 74], [166, 106, 62]];
    const PAL_PEAK = [[249, 168, 212], [123, 201, 111]];
    const PAL_LILYPAD = [[74, 222, 128], [34, 197, 94]];

    const COL_GRASS_TIP_BASE = packRGBA(45, 120, 41, 255);   // #2D7829
    const COL_GRASS_TIP_MID  = packRGBA(82, 193, 75, 255);   // #52C14B
    const COL_GRASS_TIP_HIGH = packRGBA(139, 232, 101, 255); // #8BE865
    const COL_WILDFLOWERS = [
      packRGBA(253, 224, 71, 255),  // Amarelo
      packRGBA(255, 255, 255, 255), // Branco
      packRGBA(249, 168, 212, 255)  // Rosa
    ];

    const terrainSlices = {};
    const grassTipSlices = {};

    function bakeTerrainSlices() {
      const nTerrain = TERRAIN_Z_MAX - Z_MIN + 1;
      const tMinX = new Int16Array(nTerrain).fill(mw);
      const tMaxX = new Int16Array(nTerrain).fill(-1);
      const tMinY = new Int16Array(nTerrain).fill(mh);
      const tMaxY = new Int16Array(nTerrain).fill(-1);

      const nGrass = Z_GRASS_MAX - Z_MIN + 1;
      const gMinX = new Int16Array(nGrass).fill(mw);
      const gMaxX = new Int16Array(nGrass).fill(-1);
      const gMinY = new Int16Array(nGrass).fill(mh);
      const gMaxY = new Int16Array(nGrass).fill(-1);

      const min8Cache = new Int16Array(mw * mh);
      const grassType = new Uint8Array(mw * mh); // 0=none, 1=2px, 2=3px verde, 3..5=3px flor

      const markT = (z, mx, my) => {
        const si = z - Z_MIN;
        if (mx < tMinX[si]) tMinX[si] = mx;
        if (mx > tMaxX[si]) tMaxX[si] = mx;
        if (my < tMinY[si]) tMinY[si] = my;
        if (my > tMaxY[si]) tMaxY[si] = my;
      };
      const markG = (z, mx, my) => {
        const gi = z - Z_MIN;
        if (mx < gMinX[gi]) gMinX[gi] = mx;
        if (mx > gMaxX[gi]) gMaxX[gi] = mx;
        if (my < gMinY[gi]) gMinY[gi] = my;
        if (my > gMaxY[gi]) gMaxY[gi] = my;
      };

      // Passo 1: Descobrir bounding boxes exatos + distribuir moitas orgânicas de grama
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const onBorderY = (my === 0 || my === mh - 1);
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          let h = hmap[idx];
          if (h < Z_MIN) h = Z_MIN;
          else if (h >= TERRAIN_Z_MAX) h = TERRAIN_Z_MAX - 1;
          const mat = matMap[idx];

          let min8 = 999;
          let max4 = h;
          let hL = h, hR = h, hU = h, hD = h;
          if (onBorderY || mx === 0 || mx === mw - 1) {
            min8 = -8;
          } else {
            hL = hmap[idx - 1];
            hR = hmap[idx + 1];
            hU = hmap[idx - mw];
            hD = hmap[idx + mw];
            const hLU = hmap[idx - mw - 1];
            const hRU = hmap[idx - mw + 1];
            const hLD = hmap[idx + mw - 1];
            const hRD = hmap[idx + mw + 1];
            min8 = hL;
            if (hR < min8) min8 = hR;
            if (hU < min8) min8 = hU;
            if (hD < min8) min8 = hD;
            if (hLU < min8) min8 = hLU;
            if (hRU < min8) min8 = hRU;
            if (hLD < min8) min8 = hLD;
            if (hRD < min8) min8 = hRD;
            max4 = hL;
            if (hR > max4) max4 = hR;
            if (hU > max4) max4 = hU;
            if (hD > max4) max4 = hD;
          }
          min8Cache[idx] = min8;

          if (mat === MAT_WATER) {
            if (h < 0) {
              const zEnd = h + 1 < -4 ? h + 1 : -4;
              for (let z = Z_MIN; z <= zEnd; z++) markT(z, mx, my);
              markT(-2, mx, my);
            } else {
              const zFrom = Math.max(Z_MIN, Math.min(h - 1, min8 - 2));
              for (let z = zFrom; z <= h; z++) markT(z, mx, my);
            }
            continue;
          }

          const zStart = min8 - 2 > Z_MIN ? min8 - 2 : Z_MIN;
          for (let z = zStart; z <= h; z++) {
            const si = z - Z_MIN;
            if (mx < tMinX[si]) tMinX[si] = mx;
            if (mx > tMaxX[si]) tMaxX[si] = mx;
            if (my < tMinY[si]) tMinY[si] = my;
            if (my > tMaxY[si]) tMaxY[si] = my;
          }

          // Grama orgânica em moitas usando fbm2d(mx*0.14, my*0.14) + hash XOR sem listras
          if ((mat === MAT_GRASS || mat === MAT_PEAK) && !noGrassMask[idx] && max4 <= h) {
            let nh = ((mx * 73856093) ^ (my * 19349663)) >>> 0;
            nh ^= nh >>> 13;
            nh = Math.imul(nh, 1274126177) >>> 0;
            const fine01 = nh / 4294967295;
            if (fine01 > 0.18) {
              const clumpVal = fbm2d(mx * 0.14, my * 0.14) + fine01 * 0.42;
              if (clumpVal > 0.43) {
                let gt = (clumpVal > 0.50 || (nh & 3) !== 0) ? 2 : 1;
                if (gt === 2 && (nh % 29 === 0)) {
                  gt = 3 + ((nh >>> 8) % 3);
                }
                grassType[idx] = gt;
                if (h + 1 <= TERRAIN_Z_MAX) markT(h + 1, mx, my);
                if (h + 2 <= Z_GRASS_MAX) markG(h + 2, mx, my);
                if (gt >= 2 && h + 3 <= Z_GRASS_MAX) markG(h + 3, mx, my);
              }
            }
          }
        }
      }

      // Aloca SOMENTE os buffers no tamanho justo (bw × bh) por fatia usada
      const terrainBufs = new Array(nTerrain).fill(null);
      const tW = new Int16Array(nTerrain);
      const tH = new Int16Array(nTerrain);
      for (let i = 0; i < nTerrain; i++) {
        if (tMaxX[i] >= tMinX[i]) {
          tW[i] = tMaxX[i] - tMinX[i] + 1;
          tH[i] = tMaxY[i] - tMinY[i] + 1;
          terrainBufs[i] = new Uint32Array(tW[i] * tH[i]);
        }
      }

      const grassBufs = new Array(nGrass).fill(null);
      const gW = new Int16Array(nGrass);
      const gH = new Int16Array(nGrass);
      for (let i = 0; i < nGrass; i++) {
        if (gMaxX[i] >= gMinX[i]) {
          gW[i] = gMaxX[i] - gMinX[i] + 1;
          gH[i] = gMaxY[i] - gMinY[i] + 1;
          grassBufs[i] = new Uint32Array(gW[i] * gH[i]);
        }
      }

      // Passo 2: Preenche diretamente os buffers recortados (Tight-Crop)
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          const h = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX - 1, hmap[idx]));
          const mat = matMap[idx];
          const sh = shadowMask[idx];
          const min8 = min8Cache[idx];
          const nHash = ((mx * 73856093) ^ (my * 19349663)) >>> 0;
          const microTex = ((nHash & 7) - 3) * 2;

          if (mat === MAT_WATER) {
            if (h < 0) {
              const zEnd = Math.min(-4, h + 1);
              const bedCol = packRGBA(28, 66, 108, 255);
              for (let z = Z_MIN; z <= zEnd; z++) {
                const si = z - Z_MIN;
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = bedCol;
              }
              const siSurf = -2 - Z_MIN;
              const isShallow = h > -6;
              const wxSurf = (mx - HALF_GRID + 0.5) * VOX;
              const wySurf = (my - HALF_GRID + 0.5) * VOX;
              const isPlungeFoam = (Math.hypot(wxSurf - 168, wySurf + 330) < 16) && ((nHash & 3) === 0);
              terrainBufs[siSurf][(my - tMinY[siSurf]) * tW[siSurf] + (mx - tMinX[siSurf])] = isPlungeFoam
                ? packRGBA(236, 248, 255, 245)
                : (isShallow
                  ? ((nHash & 1) ? packRGBA(72, 202, 245, 225) : packRGBA(95, 215, 250, 225))
                  : ((nHash & 3) === 0 ? packRGBA(56, 189, 248, 235) : packRGBA(42, 172, 236, 235)));
            } else {
              const zFrom = Math.max(Z_MIN, Math.min(h - 1, min8 - 2));
              const streakHash = ((mx * 17) ^ (my * 31)) & 7;
              for (let z = zFrom; z <= h; z++) {
                const si = z - Z_MIN;
                const isTop = (z === h);
                const isFoam = isTop
                  ? ((mx + my) % 3 === 0 && h < 45)
                  : ((streakHash < 2 && ((z + (mx & 1)) % 3 !== 0)) || (z <= 2));
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = isFoam
                  ? packRGBA(224, 242, 254, 255)
                  : (isTop ? packRGBA(56, 189, 248, 240) : packRGBA(28, 158, 224, 255));
              }
            }
            continue;
          }

          const hL = mx > 0 ? hmap[idx - 1] : h;
          const hR = mx < mw - 1 ? hmap[idx + 1] : h;
          const hU = my > 0 ? hmap[idx - mw] : h;
          const hD = my < mh - 1 ? hmap[idx + mw] : h;
          const gx = hR - hL;
          const gy = hD - hU;
          const sunShade = Math.max(-22, Math.min(22, Math.round((-gx - gy) * 1.4)));
          const exposedEdge = (hL < h || hU < h) ? 10 : 0;
          const zStart = Math.max(Z_MIN, min8 - 2);

          for (let z = zStart; z <= h; z++) {
            const si = z - Z_MIN;
            let col;
            if (z === h) {
              let baseRGB;
              if (mat === MAT_PATH) baseRGB = PAL_PATH[nHash & 1];
              else if (mat === MAT_SAND) baseRGB = PAL_SAND[nHash & 1];
              else if (mat === MAT_STONE) baseRGB = PAL_STONE[nHash & 1];
              else if (mat === MAT_BRIDGE) {
                const plank = ((mx >> 1) + (my >> 2)) & 1;
                baseRGB = PAL_BRIDGE[plank];
              } else if (mat === MAT_PEAK) {
                baseRGB = (nHash % 5 === 0) ? PAL_PEAK[0] : PAL_PEAK[1];
              } else if (mat === MAT_LILYPAD) {
                baseRGB = PAL_LILYPAD[nHash & 1];
              } else {
                const tier = h >= 42 ? 3 : (h >= 24 ? 2 : (h >= 10 ? 1 : 0));
                baseRGB = PAL_GRASS_BASE[tier];
              }
              const altLift = Math.min(14, Math.max(-6, Math.round(h * 0.16)));
              col = shadePack(baseRGB, microTex + altLift + exposedEdge, sh);
            } else {
              const d = h - z;
              if (mat === MAT_BRIDGE) {
                col = shadePack([118, 72, 42], sunShade, sh * 0.5);
              } else if (mat === MAT_LILYPAD) {
                col = shadePack([22, 130, 58], sunShade, 0);
              } else if (mat === MAT_SAND && d <= 5) {
                col = shadePack([196, 168, 112], sunShade, sh * 0.5);
              } else if (d <= 3 && mat !== MAT_STONE) {
                const moss = (nHash & 1) ? [58, 143, 56] : [41, 107, 39];
                col = shadePack(moss, sunShade, sh * 0.6);
              } else if (d <= 12 && mat !== MAT_STONE) {
                const strata = (z & 2) ? 6 : -5;
                const earth = (nHash & 1) ? [156, 102, 68] : [128, 79, 50];
                col = shadePack(earth, sunShade + strata, sh * 0.4);
              } else {
                const strata = ((z >> 1) & 1) ? 9 : -8;
                const rock = (nHash & 1) ? [109, 118, 132] : [86, 95, 108];
                col = shadePack(rock, sunShade + strata, sh * 0.3);
              }
            }
            terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = col;
          }

          const gt = grassType[idx];
          if (gt > 0) {
            if (h + 1 <= TERRAIN_Z_MAX) {
              const si1 = (h + 1) - Z_MIN;
              terrainBufs[si1][(my - tMinY[si1]) * tW[si1] + (mx - tMinX[si1])] = COL_GRASS_TIP_BASE;
            }
            if (h + 2 <= Z_GRASS_MAX) {
              const gi2 = (h + 2) - Z_MIN;
              grassBufs[gi2][(my - gMinY[gi2]) * gW[gi2] + (mx - gMinX[gi2])] = COL_GRASS_TIP_MID;
            }
            if (gt >= 2 && h + 3 <= Z_GRASS_MAX) {
              const gi3 = (h + 3) - Z_MIN;
              const tipCol = gt >= 3 ? COL_WILDFLOWERS[gt - 3] : COL_GRASS_TIP_HIGH;
              grassBufs[gi3][(my - gMinY[gi3]) * gW[gi3] + (mx - gMinX[gi3])] = tipCol;
            }
          }
        }
      }

      const uploadTightSlices = (bufs, minXArr, minYArr, wArr, hArr, targetMap, zMax) => {
        for (let z = Z_MIN; z <= zMax; z++) {
          const i = z - Z_MIN;
          const buf = bufs[i];
          if (!buf) {
            targetMap[z] = null;
            continue;
          }
          const bw = wArr[i];
          const bh = hArr[i];
          const cv = document.createElement('canvas');
          cv.width = bw;
          cv.height = bh;
          const cx = cv.getContext('2d');
          const img = cx.createImageData(bw, bh);
          new Uint32Array(img.data.buffer).set(buf);
          cx.putImageData(img, 0, 0);
          targetMap[z] = { canvas: cv, offX: minXArr[i], offY: minYArr[i], w: bw, h: bh };
        }
      };

      uploadTightSlices(terrainBufs, tMinX, tMinY, tW, tH, terrainSlices, TERRAIN_Z_MAX);
      uploadTightSlices(grassBufs, gMinX, gMinY, gW, gH, grassTipSlices, Z_GRASS_MAX);
    }
    bakeTerrainSlices();
    const STARTUP_MS = Math.round((performance.now() - STARTUP_T0) * 10) / 10;

    // =========================================================================
    // 7. ESTADO DO GATO, FÍSICA CONTÍNUA EM MICRO-VOXELS & TRAVEL
    // =========================================================================
    const SPAWN_X = -220;
    const SPAWN_Y = 60;
    const spawnH = getHeightAt(SPAWN_X, SPAWN_Y) || 0;

    const cat = {
      x: SPAWN_X,
      y: SPAWN_Y,
      z: spawnH,
      vz: 0,
      groundZ: spawnH,
      onGround: true,
      coyoteTimer: 0,
      jumpBuffer: 0,
      selfAngle: 0,
      walkPhase: 0,
      isWalking: false,
      idleTimer: 0,
      scale: 1.0,
      skinIdx: 0,
      hatIdx: 0,
      speech: { text: 'Miau! Vale Orgânico 720×720! 🐾', timer: 190 },
      lastSafeX: SPAWN_X,
      lastSafeY: SPAWN_Y,
      lastSafeZ: spawnH,
      maxJumpReached: spawnH,
      obstacleHint: 'ok',
      obstacleLabel: '✅ Caminho Livre'
    };

    const TRAVEL_SPOTS = [
      { wx: -220, wy: 60,   label: '🏡 Vila da Clareira' },
      { wx: -165, wy: 150,  label: '🏠 Cabana 2' },
      { wx: -520, wy: 60,   label: '🌻 Campos de Girassol' },
      { wx: -190, wy: 375,  label: '🏛️ Ruínas Orgânicas' },
      { wx: -120, wy: 456,  label: '🏖️ Praia Dourada' },
      { wx: -410, wy: 530,  label: '🗼 Farol Monumental' },
      { wx: -290, wy: -210, label: '⛩️ Jardim Zen & Torii' },
      { wx: 284,  wy: 152,  label: '🍄 Bosque Cogumelos' },
      { wx: 410,  wy: -44,  label: '🥾 Base da Montanha' },
      { wx: 320,  wy: -330, label: '🌸 Pico Sakura (Z=64)' }
    ];
    let travelIdx = 0;

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
    function spawnParticles(wx, wy, wz, count, colors, speed = 28) {
      for (let i = 0; i < count; i++) {
        const a = Math.random() * Math.PI * 2;
        const sp = (0.35 + Math.random() * 0.65) * speed;
        particles.push({
          x: wx, y: wy, z: wz,
          vx: Math.cos(a) * sp,
          vy: Math.sin(a) * sp,
          vz: 20 + Math.random() * 42,
          life: 0.42 + Math.random() * 0.32,
          color: colors[i % colors.length],
          size: 2
        });
      }
    }

    function catSpeak(text, timer = 140) {
      cat.speech = { text, timer };
    }

    function waterSurfZ(cell) {
      return cell.h < 0 ? -2 : cell.h;
    }

    function evaluateSupport(wx, wy, currentZ, onGround) {
      const r = 2.4;
      const samples = [
        [wx, wy],
        [wx - r, wy], [wx + r, wy],
        [wx, wy - r], [wx, wy + r]
      ];
      let bestH = -999;
      const centerCell = getCellAt(wx, wy);
      const climbAllowed = onGround ? AUTO_STEP_MAX + 0.5 : 2.0;

      for (const [sx, sy] of samples) {
        const c = getCellAt(sx, sy);
        if (!c || c.mat === MAT_WATER || !c.standable) continue;
        if (c.h <= currentZ + climbAllowed) {
          if (c.h > bestH) bestH = c.h;
        }
      }

      for (const pc of platformColliders) {
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

      const centerCell = getCellAt(nx, ny);
      if (centerCell && centerCell.mat === MAT_WATER && (onGround || catZ <= waterSurfZ(centerCell) + 1.5)) {
        return { blocked: true, reason: 'water', maxStepH: waterSurfZ(centerCell) };
      }

      const r = 2.6;
      const pts = [
        [nx, ny],
        [nx - r, ny - r], [nx + r, ny - r],
        [nx - r, ny + r], [nx + r, ny + r]
      ];

      const allowedClimb = onGround ? AUTO_STEP_MAX : 1.5;
      let blocked = false;
      let maxBlockingH = -999;
      let propBlocked = false;

      for (const [px, py] of pts) {
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
        if (catZ >= sc.baseZ - 2 && catZ < sc.baseZ + sc.colH - 1.5) {
          if (isPointInPropCollider(nx, ny, sc, 3.0)) {
            blocked = true;
            propBlocked = true;
            const topH = sc.baseZ + sc.colH;
            if (topH > maxBlockingH) maxBlockingH = topH;
          }
        }
      }

      for (const pc of platformColliders) {
        const d = Math.hypot(nx - pc.wx, ny - pc.wy);
        if (d < pc.r + 1.2 && catZ < pc.topZ - 2.0 && catZ >= pc.baseZ - 4.0) {
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
      const fx = dirX !== 0 || dirY !== 0 ? dirX : -Math.sin(cat.selfAngle);
      const fy = dirX !== 0 || dirY !== 0 ? dirY : Math.cos(cat.selfAngle);
      const probeX = cat.x + fx * 11;
      const probeY = cat.y + fy * 11;
      const c = getCellAt(probeX, probeY);

      if (!c) {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = '⛔ Limite do Vale';
        return;
      }
      if (c.mat === MAT_WATER) {
        cat.obstacleHint = 'water';
        cat.obstacleLabel = '💧 Água Intransponível';
        return;
      }

      for (const sc of propColliders) {
        if (cat.groundZ < sc.baseZ + sc.colH - 1.5 && isPointInPropCollider(probeX, probeY, sc, 3.2)) {
          cat.obstacleHint = 'high';
          cat.obstacleLabel = sc.shape === 'box' ? '🏠 Parede / Estrutura' : '🌲 Obstáculo Sólido';
          return;
        }
      }

      let targetH = (!c.standable && c.h > cat.groundZ + AUTO_STEP_MAX) ? Math.max(c.h, c.cliffTop) : c.h;
      for (const pc of platformColliders) {
        if (Math.hypot(probeX - pc.wx, probeY - pc.wy) <= pc.r + 2.0 && pc.topZ > targetH) {
          targetH = pc.topZ;
        }
      }

      const dz = targetH - cat.groundZ;
      if (dz <= AUTO_STEP_MAX) {
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
      viewW = window.innerWidth;
      viewH = window.innerHeight;
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

    window.addEventListener('keydown', (e) => {
      const code = e.code;
      keys[code] = true;
      if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code)) {
        e.preventDefault();
      }
      if (code === 'Space') {
        cat.jumpBuffer = 0.13;
      } else if (code === 'KeyR') {
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

    function triggerMeow() {
      sfxMeow();
      catSpeak('Miau! 🐾', 110);
      for (const npc of npcs) {
        if (Math.hypot(npc.x - cat.x, npc.y - cat.y) < 110) {
          npc.speech = { text: npc.kind === 'chicken' ? 'Có có!! 💕' : 'Piu piu! 💛', timer: 110 };
        }
      }
    }

    function teleportToWorld(wx, wy, msg = null, zOverride = null) {
      const c = getCellAt(wx, wy);
      cat.x = wx;
      cat.y = wy;
      const gz = zOverride !== null ? zOverride : (c ? c.h : 0);
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
      if (msg) catSpeak(msg, 125);
    }

    function resetCatToSpawn() {
      teleportToWorld(SPAWN_X, SPAWN_Y, 'De volta à Vila! 🏡');
    }

    let isDraggingCam = false;
    let dragStartX = 0;
    canvas.addEventListener('pointerdown', (e) => {
      isDraggingCam = true;
      dragStartX = e.clientX;
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!isDraggingCam) return;
      const dx = e.clientX - dragStartX;
      dragStartX = e.clientX;
      targetTurn -= dx * 0.0085;
      turn = targetTurn;
    });
    canvas.addEventListener('pointerup', (e) => {
      isDraggingCam = false;
      try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
    });

    const btnSkin = document.getElementById('btnSkin');
    const btnHat = document.getElementById('btnHat');
    btnSkin.addEventListener('click', () => {
      cat.skinIdx = (cat.skinIdx + 1) % CAT_SKINS.length;
      btnSkin.textContent = `🐱 ${CAT_SKINS[cat.skinIdx].name}`;
      sfxMeow();
    });
    btnHat.addEventListener('click', () => {
      cat.hatIdx = (cat.hatIdx + 1) % HAT_PRESETS.length;
      btnHat.textContent = `🎩 ${HAT_PRESETS[cat.hatIdx].name}`;
    });
    document.getElementById('btnRotL').addEventListener('click', () => { targetTurn += Math.PI / 4; });
    document.getElementById('btnRotR').addEventListener('click', () => { targetTurn -= Math.PI / 4; });
    document.getElementById('btnReset').addEventListener('click', resetCatToSpawn);
    document.getElementById('btnTravel').addEventListener('click', () => {
      travelIdx = (travelIdx + 1) % TRAVEL_SPOTS.length;
      const spot = TRAVEL_SPOTS[travelIdx];
      teleportToWorld(spot.wx, spot.wy, spot.label);
      sfxBiome();
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
          if (c && c.mat !== MAT_WATER && Math.abs(c.h - npc.z) <= 5.5) {
            let hitProp = false;
            for (const sc of propColliders) {
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
    function updatePhysics(dt) {
      cat.idleTimer += dt;
      if (blockedCooldown > 0) blockedCooldown -= dt;

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
      const baseSpeed = isSprinting ? 168 : 112;
      const speed = cat.onGround ? baseSpeed : Math.round(baseSpeed * 0.85);
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
      }

      const wasOnGround = cat.onGround;
      cat.vz -= GRAVITY * dt;
      cat.z += cat.vz * dt;
      if (cat.z > cat.maxJumpReached) cat.maxJumpReached = cat.z;

      const sup = evaluateSupport(cat.x, cat.y, cat.z, wasOnGround);
      if (sup.bestH > -900) {
        cat.groundZ = sup.bestH;
        if (cat.z <= sup.bestH + 0.05 && cat.vz <= 0) {
          if (!wasOnGround && cat.vz < -90) {
            sfxLand();
            spawnParticles(cat.x, cat.y, sup.bestH + 1, 6, ['#FDF6E9', '#D6C4AA'], 24);
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
        } else if (wasOnGround && sup.bestH < cat.z && cat.z - sup.bestH <= 4.5) {
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
          cat.x = cat.lastSafeX;
          cat.y = cat.lastSafeY;
          cat.vz = 0;
          cat.onGround = true;
          if (inWater) {
            cat.z = cat.lastSafeZ + 2;
            sfxBlocked();
            catSpeak('Splash! De volta à margem! 💦', 110);
            spawnParticles(cat.x, cat.y, cat.z + 2, 10, ['#93C5FD', '#FFFFFF'], 32);
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
      }

      // Grama rustle & descoberta de bioma
      const curCell = sup.centerCell;
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

      if (Math.hypot(cat.x - 168, cat.y + 330) < 320 && Math.random() < dt * 14) {
        spawnParticles(
          168 + (Math.random() - 0.5) * 12,
          -330 + (Math.random() - 0.5) * 14,
          1, 1, ['#E0F2FE', '#FFFFFF', '#7DD3FC'], 16
        );
      }

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vz -= 260 * dt;
        p.z += p.vz * dt;
        p.life -= dt;
        if (p.life <= 0) particles.splice(i, 1);
      }

      const lerpFactor = Math.min(1, dt * 9.0);
      camX += (cat.x - camX) * lerpFactor;
      camY += (cat.y - camY) * lerpFactor;
      camZ += (cat.groundZ + (cat.z - cat.groundZ) * 0.45 - camZ) * Math.min(1, dt * 6.5);
    }

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

    function stampModelSlice(targetCtx, model, sz, wx, wy, wz, selfAngle, scale, cosA, sinA) {
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
      const windOff = Math.round(Math.sin(animTick * 0.65) * 1.0);
      const speechQueue = [];

      // 2. Bounding box visível no grid 720×720 (culling exato por viewport!)
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

      const minVisWx = (viewMinMx - HALF_GRID) * VOX - 36;
      const maxVisWx = (viewMaxMx - HALF_GRID) * VOX + 36;
      const minVisWy = (viewMinMy - HALF_GRID) * VOX - 36;
      const maxVisWy = (viewMaxMy - HALF_GRID) * VOX + 36;

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
        if (p.wx < minVisWx || p.wx > maxVisWx || p.wy < minVisWy || p.wy > maxVisWy) continue;
        const dp = (p.wx - camX) * sinA + (p.wy - camY) * cosA;
        activeDrawables.push({
          baseZ: p.baseZ,
          topZ: p.topZ,
          depth: dp,
          drawSlice: (z) => {
            const sz = Math.min(p.model.count - 1, Math.floor((z - p.baseZ) / p.scale));
            stampModelSlice(entityCtx, p.model, sz, p.wx, p.wy, z, p.selfAngle, p.scale, cosA, sinA);
          }
        });
        if (p.topZ > maxEntityTopZ) maxEntityTopZ = p.topZ;
        if (p.isFire) {
          const fz = Math.min(TERRAIN_Z_MAX, p.baseZ + (p.modelKey === 'stone_lantern' ? 12 : 6));
          if (!firesByZ.has(fz)) firesByZ.set(fz, []);
          firesByZ.get(fz).push(p);
        }
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
        registerShadow(cat.x, cat.y, cat.groundZ, cat.z, 6.2 * shrink, 4.0 * shrink, 0.32 * shrink);

        const pawSpecs = [
          [-4.5, -7.5, inAir ? 0.0 : (cat.isWalking ? Math.max(0, Math.sin(t + Math.PI + 0.3) * 3.0) : 0), inAir ? -2.2 : (cat.isWalking ? -Math.cos(t + Math.PI + 0.3) * 2.3 : 0)],
          [ 3.5, -7.5, inAir ? 0.0 : (cat.isWalking ? Math.max(0, Math.sin(t + 0.3) * 3.0) : 0), inAir ? -2.2 : (cat.isWalking ? -Math.cos(t + 0.3) * 2.3 : 0)],
          [-4.5,  3.5, inAir ? 0.5 : (cat.isWalking ? Math.max(0, Math.sin(t) * 3.0) : 0), inAir ? 2.2 : (cat.isWalking ? -Math.cos(t) * 2.3 : 0)],
          [ 3.5,  3.5, inAir ? 0.5 : (cat.isWalking ? Math.max(0, Math.sin(t + Math.PI) * 3.0) : 0), inAir ? 2.2 : (cat.isWalking ? -Math.cos(t + Math.PI) * 2.3 : 0)]
        ];
        for (const [lx, ly, lift, stride] of pawSpecs) {
          const px = cat.x + lx * cosC - (ly + stride) * sinC;
          const py = cat.y + lx * sinC + (ly + stride) * cosC;
          const pBaseZ = Math.round(cat.z + lift);
          const pTopZ = pBaseZ + sk.paw.count;
          const pDp = (px - camX) * sinA + (py - camY) * cosA;
          activeDrawables.push({
            baseZ: pBaseZ,
            topZ: pTopZ,
            depth: pDp + 0.4,
            drawSlice: (z) => {
              stampModelSlice(entityCtx, sk.paw, z - pBaseZ, px, py, z, cat.selfAngle, cat.scale, cosA, sinA);
            }
          });
          if (pTopZ > maxEntityTopZ) maxEntityTopZ = pTopZ;
        }

        const bob = inAir ? 0 : (cat.isWalking ? Math.abs(Math.sin(t * 2)) * 0.7 : Math.sin(cat.idleTimer * 2.4) * 0.35);
        const bodyBaseZ = Math.round(cat.z + 1.5 + bob);
        const bodyTopZ = bodyBaseZ + sk.body.count;
        activeDrawables.push({
          baseZ: bodyBaseZ,
          topZ: bodyTopZ,
          depth: dpCat + 0.5,
          drawSlice: (z) => {
            stampModelSlice(entityCtx, sk.body, z - bodyBaseZ, cat.x, cat.y, z, cat.selfAngle, cat.scale, cosA, sinA);
          }
        });
        if (bodyTopZ > maxEntityTopZ) maxEntityTopZ = bodyTopZ;

        if (hatModel) {
          const hx = cat.x - 4.5 * sinC;
          const hy = cat.y + 4.5 * cosC;
          const hatBaseZ = Math.round(cat.z + (15.0 + bob - 2.8) * cat.scale);
          const hatTopZ = hatBaseZ + hatModel.count;
          activeDrawables.push({
            baseZ: hatBaseZ,
            topZ: hatTopZ,
            depth: dpCat + 0.6,
            drawSlice: (z) => {
              stampModelSlice(entityCtx, hatModel, z - hatBaseZ, hx, hy, z, cat.selfAngle, cat.scale, cosA, sinA);
            }
          });
          if (hatTopZ > maxEntityTopZ) maxEntityTopZ = hatTopZ;
        }

        if (cat.speech && cat.speech.timer > 0) {
          cat.speech.timer--;
          const sp = project(cat.x, cat.y, cat.z + 24);
          speechQueue.push({ lowX: sp.x, lowY: sp.y, text: cat.speech.text });
        }
      }

      // Ordenar uma única vez por profundidade para desenhar back-to-front em cada fatia z
      activeDrawables.sort((a, b) => a.depth - b.depth);

      // 4. Loop Unificado Slice-by-Slice (Terreno + Destination-Out + Grama + Entidades)
      entityCtx.globalCompositeOperation = 'source-over';
      entityCtx.clearRect(0, 0, LOW_W, LOW_H);
      let entityStarted = false;

      for (let z = Z_MIN; z <= maxEntityTopZ; z++) {
        // 4a. Fatia do terreno (Tight-Crop Bounded Slice + skip O(1))
        const tSlice = z <= TERRAIN_Z_MAX ? terrainSlices[z] : null;
        if (tSlice && viewMaxMx > viewMinMx && viewMaxMy > viewMinMy) {
          drawBoundedSliceTo(lowCtx, tSlice, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy);

          // Brilho animado na superfície da água (z = -2)
          if (z === -2) {
            lowCtx.fillStyle = 'rgba(224, 242, 254, 0.55)';
            const step = 12;
            const startX = Math.floor(minVisWx / step) * step;
            const startY = Math.floor(minVisWy / step) * step;
            for (let wy = startY; wy <= maxVisWy; wy += step) {
              for (let wx = startX; wx <= maxVisWx; wx += step) {
                const c = getCellAt(wx, wy);
                if (!c || c.mat !== MAT_WATER || c.h >= 0) continue;
                if (((c.mx + c.my + animTick) % 9) === 0) {
                  const wp = project(wx, wy, -1.8);
                  lowCtx.fillRect(Math.round(wp.x), Math.round(wp.y), 3, 1);
                }
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
          drawBoundedSliceTo(lowCtx, gSlice, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy, windOff);
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

      // 6. Partículas 3D
      for (const p of particles) {
        const pp = project(p.x, p.y, p.z);
        lowCtx.fillStyle = p.color;
        lowCtx.fillRect(Math.round(pp.x), Math.round(pp.y), p.size, p.size);
      }

      // 7. Upscale 1:1 quadrado Nearest-Neighbor para o canvas principal + Balões Hi-Res
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, viewW, viewH);
      ctx.drawImage(lowCanvas, 0, 0, LOW_W * pixelScale, LOW_H * pixelScale);

      drawSpeechOverlaysHiRes(speechQueue);
    }

    // =========================================================================
    // 11. MINIMAPA TOPOGRÁFICO ORGÂNICO (720×720 passo 6 -> 120×120)
    // =========================================================================
    const mmCanvas = document.getElementById('minimapCanvas');
    const mmCtx = mmCanvas.getContext('2d');
    const MM_RES = 120;
    const mmBase = document.createElement('canvas');
    mmBase.width = MM_RES;
    mmBase.height = MM_RES;
    const mmBaseCtx = mmBase.getContext('2d');

    function bakeMinimapBase() {
      const img = mmBaseCtx.createImageData(MM_RES, MM_RES);
      const buf = new Uint32Array(img.data.buffer);
      for (let gy = 0; gy < MM_RES; gy++) {
        const my = gy * 6;
        for (let gx = 0; gx < MM_RES; gx++) {
          const mx = gx * 6;
          const idx = my * mw + mx;
          const h = hmap[idx];
          const mat = matMap[idx];
          const hL = mx >= 6 ? hmap[my * mw + (mx - 6)] : h;
          const hU = my >= 6 ? hmap[(my - 6) * mw + mx] : h;
          const isContour = mat !== MAT_WATER && mat !== MAT_BRIDGE &&
            (Math.floor(h / 10) !== Math.floor(hL / 10) || Math.floor(h / 10) !== Math.floor(hU / 10));

          let rgb;
          if (mat === MAT_WATER) rgb = [56, 189, 248];
          else if (mat === MAT_LILYPAD) rgb = [34, 197, 94];
          else if (mat === MAT_BRIDGE) rgb = [185, 122, 74];
          else if (mat === MAT_SAND) rgb = [243, 221, 169];
          else if (mat === MAT_PEAK || h >= 62) rgb = [244, 114, 182];
          else if (h >= 46) rgb = [156, 163, 175];
          else if (h >= 28) rgb = [148, 163, 184];
          else if (h >= 14) rgb = [78, 169, 76];
          else if (mat === MAT_PATH) rgb = [223, 182, 132];
          else rgb = [101, 196, 102];

          buf[gy * MM_RES + gx] = isContour
            ? packRGBA(Math.round(rgb[0] * 0.78), Math.round(rgb[1] * 0.78), Math.round(rgb[2] * 0.78))
            : packRGBA(rgb[0], rgb[1], rgb[2]);
        }
      }
      mmBaseCtx.putImageData(img, 0, 0);
    }
    bakeMinimapBase();

    function drawMinimap() {
      mmCtx.imageSmoothingEnabled = false;
      mmCtx.drawImage(mmBase, 0, 0, 120, 120);

      const toMm = (w) => (w / VOX + HALF_GRID) * (120 / mw);

      for (const f of fishes) {
        if (f.collected) continue;
        mmCtx.fillStyle = '#FACC15';
        mmCtx.fillRect(Math.round(toMm(f.wx)) - 1, Math.round(toMm(f.wy)) - 1, 3, 3);
      }

      for (const npc of npcs) {
        mmCtx.fillStyle = '#FDBA74';
        mmCtx.fillRect(Math.round(toMm(npc.x)) - 1, Math.round(toMm(npc.y)) - 1, 3, 3);
      }

      const cx = toMm(cat.x);
      const cy = toMm(cat.y);
      mmCtx.fillStyle = '#EF4444';
      mmCtx.beginPath();
      mmCtx.arc(cx, cy, 3, 0, Math.PI * 2);
      mmCtx.fill();
      mmCtx.strokeStyle = '#FFFFFF';
      mmCtx.lineWidth = 1;
      mmCtx.stroke();

      const fx = -Math.sin(cat.selfAngle);
      const fy = Math.cos(cat.selfAngle);
      mmCtx.beginPath();
      mmCtx.moveTo(cx, cy);
      mmCtx.lineTo(cx + fx * 6, cy + fy * 6);
      mmCtx.strokeStyle = '#7F1D1D';
      mmCtx.lineWidth = 1.5;
      mmCtx.stroke();
    }

    // =========================================================================
    // 12. LOOP PRINCIPAL + TELEMETRIA FPS & HOOKS DE DEBUG/TESTE
    // =========================================================================
    let lastTime = performance.now();
    let fpsAccum = 0;
    let fpsFrames = 0;
    let currentFps = 60;

    function loop(now) {
      const rawDt = Math.max(0.001, (now - lastTime) / 1000);
      lastTime = now;
      fpsAccum += rawDt;
      fpsFrames++;
      if (fpsAccum >= 0.5) {
        currentFps = Math.round(fpsFrames / fpsAccum);
        fpsAccum = 0;
        fpsFrames = 0;
      }

      const dt = Math.min(0.05, rawDt);
      updatePhysics(dt);
      renderScene();
      drawMinimap();
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

    window.__TERRAIN_DEBUG__ = {
      getState: () => ({
        fps: currentFps,
        startupMs: STARTUP_MS,
        x: cat.x, y: cat.y, z: cat.z, vz: cat.vz,
        groundZ: cat.groundZ, onGround: cat.onGround,
        selfAngle: cat.selfAngle, turn,
        maxJumpReached: cat.maxJumpReached,
        obstacleHint: cat.obstacleHint,
        obstacleLabel: cat.obstacleLabel,
        speech: cat.speech ? cat.speech.text : null,
        collectedFish: fishes.filter(f => f.collected).length,
        visitedBiomes: Array.from(visitedBiomes),
        viewport: { viewW, viewH, LOW_W, LOW_H, pixelScale, dpr }
      }),
      setCatWorld: (wx, wy, z = null) => {
        teleportToWorld(wx, wy, null, z);
      },
      getHeightAt: (wx, wy) => getHeightAt(wx, wy),
      getCellAt: (wx, wy) => getCellAt(wx, wy),
      isStandable: (wx, wy) => { const c = getCellAt(wx, wy); return c ? c.standable : false; },
      getCliffTop: (wx, wy) => { const c = getCellAt(wx, wy); return c ? c.cliffTop : null; },
      sampleTrail: (pts) => pts.map(([x, y]) => ({ x, y, h: getHeightAt(x, y), standable: (getCellAt(x, y) || {}).standable })),
      getRuinsCoords: () => ({
        approachSouth: { wx: -190, wy: 375, z: getHeightAt(-190, 375) },
        monoliths: [
          { name: 'A', wx: -280, wy: 330, rx: 26, ry: 22, targetZ: 6,  topZ: getHeightAt(-280, 330), southApproach: { wx: -280, wy: 375, z: getHeightAt(-280, 375) } },
          { name: 'B', wx: -190, wy: 330, rx: 26, ry: 22, targetZ: 16, topZ: getHeightAt(-190, 330), southApproach: { wx: -190, wy: 375, z: getHeightAt(-190, 375) } },
          { name: 'C', wx: -100, wy: 330, rx: 26, ry: 22, targetZ: 32, topZ: getHeightAt(-100, 330), southApproach: { wx: -100, wy: 375, z: getHeightAt(-100, 375) } },
          { name: 'D', wx: -10,  wy: 330, rx: 26, ry: 22, targetZ: 48, topZ: getHeightAt(-10,  330), southApproach: { wx: -10,  wy: 375, z: getHeightAt(-10,  375) } }
        ]
      }),
      setTurn: (rad) => { turn = rad; targetTurn = rad; },
      triggerJump: () => { cat.jumpBuffer = 0.14; },
      speak: (text) => { catSpeak(text, 240); },
      getPropsByType: (key) => props.filter(p => p.modelKey === key).map(p => ({
        id: p.id, modelKey: p.modelKey, wx: p.wx, wy: p.wy, wz: p.wz, topZ: p.topZ
      }))
    };
  </script>
</body>
</html>
"""

html_out = (
    HTML_TEMPLATE
    .replace('__CAT_SLICES__', json.dumps(cat_slices))
    .replace('__HATS_PACK__', json.dumps(hats_pack))
    .replace('__CHICKEN_DATA__', json.dumps(chicken_data))
    .replace('__PROPS_PACK__', json.dumps(props_pack))
)

out_path = os.path.join(ROOT, 'terrain-world.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_out)

print(f'SUCCESS: Generated {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)')
