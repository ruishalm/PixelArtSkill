import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOXELS_DIR = os.path.join(ROOT, 'assets', 'voxels')
EXAMPLES_DIR = os.path.join(ROOT, 'examples')
_RLE_RE = re.compile(r'(.)\1{2,}')


def rle_compress_props(pack):
    compressed = {}
    for key, entry in pack.items():
        compressed[key] = {
            'palette': entry['palette'],
            'slices': [
                [_RLE_RE.sub(lambda m: f'*{m.group(1)}{len(m.group(0))};', row) for row in sl]
                for sl in entry['slices']
            ],
        }
    return compressed

with open(os.path.join(VOXELS_DIR, 'slices_v5.json'), 'r', encoding='utf-8') as f:
    cat_slices = json.load(f)

with open(os.path.join(VOXELS_DIR, 'hats_pack.json'), 'r', encoding='utf-8') as f:
    hats_pack = json.load(f)

with open(os.path.join(VOXELS_DIR, 'chicken_slices.json'), 'r', encoding='utf-8') as f:
    chicken_data = json.load(f)

with open(os.path.join(VOXELS_DIR, 'terrain_props_pack.json'), 'r', encoding='utf-8') as f:
    props_pack = json.load(f)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <link rel="icon" href="data:," />
  <title>Vale Felino 3D — Terreno Micro-Voxel Orgânico 1080×1080</title>
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
        <button class="pill-btn" id="btnTool" title="Trocar Ferramenta">🐾 Patada</button>
        <button class="pill-btn" id="btnAction" title="Patada / Usar Ferramenta (E)">⚡ E Ação</button>
        <button class="pill-btn" id="btnRotL" title="Girar Câmera (Q)">⟲ Q</button>
        <button class="pill-btn" id="btnRotR" title="Girar Câmera (C)">C ⟳</button>
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
        <kbd>E</kbd> Ação •
        <kbd>Q</kbd>/<kbd>C</kbd> Girar •
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
    function decodeRLERow(row) {
      return row.indexOf('*') !== -1
        ? row.replace(/\*([0-9a-z])(\d+);/g, (_, ch, n) => ch.repeat(+n))
        : row;
    }

    function buildSliceSheet(data, pal) {
      const cnt = data.length;
      const h = data[0].length;
      const w = decodeRLERow(data[0][0]).length;
      const cv = document.createElement('canvas');
      cv.width = w * cnt;
      cv.height = h;
      const cx = cv.getContext('2d');
      cx.imageSmoothingEnabled = false;

      for (let z = 0; z < cnt; z++) {
        const offX = z * w;
        const rows = data[z];
        for (let y = 0; y < h; y++) {
          const row = decodeRLERow(rows[y]);
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
    const sfxChop = () => {
      playTone(210, 75, 0.09, 'triangle', 0.10);
      setTimeout(() => playTone(140, 55, 0.07, 'square', 0.05), 20);
    };
    const sfxCrumble = () => {
      playTone(135, 48, 0.18, 'sawtooth', 0.09);
      setTimeout(() => playTone(95, 40, 0.22, 'triangle', 0.08), 55);
    };

    // =========================================================================
    // 4. HEIGHTFIELD MICRO-VOXEL 1080×1080 & ESCULTURA ORGÂNICA "PULL-CHAIN"
    // =========================================================================
    const STARTUP_T0 = performance.now();
    const mw = 1080;
    const mh = 1080;
    const VOX = 2;
    const HALF_GRID = 540;
    const HALF_WORLD = 1080;
    const WORLD_MIN = -1080;
    const WORLD_MAX = 1080;

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
      let n = (Math.imul(ix, 374761393) + Math.imul(iy, 668265263)) | 0;
      n = Math.imul(n ^ (n >>> 13), 1274126177);
      return ((n ^ (n >>> 16)) >>> 0) * 2.3283064365386963e-10;
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

    function fbm2dFast(x, y) {
      return 0.60 * valueNoise2d(x, y) + 0.30 * valueNoise2d(x * 2.05, y * 2.05);
    }

    const _wp = { x: 0, y: 0 };
    function warp2d(wx, wy, freq = 0.012, amp = 24) {
      const qx = fbm2dFast(wx * freq + 5.2, wy * freq + 1.3);
      const qy = fbm2dFast(wx * freq + 1.7, wy * freq + 9.2);
      const f2 = freq * 1.35;
      const rx = valueNoise2d((wx + qx * amp) * f2 + 8.3, (wy + qy * amp) * f2 + 2.8);
      const ry = valueNoise2d((wx + qx * amp) * f2 + 1.2, (wy + qy * amp) * f2 + 6.4);
      _wp.x = wx + rx * amp;
      _wp.y = wy + ry * amp;
      return _wp;
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
      const s = step * (1 + fbm2dFast(wx * 0.014 + 3.1, wy * 0.014 - 4.7) * 0.22);
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

      const maxPreD = halfWidth + warpAmp + 6;
      const nPts = points.length - 1;
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          let rawMinSq = Infinity;
          for (let i = 0; i < nPts; i++) {
            const ds = distToSegmentSq(wx, wy, points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]);
            if (ds < rawMinSq) rawMinSq = ds;
          }
          if (rawMinSq > maxPreD * maxPreD) continue;
          const wp = warp2d(wx, wy, warpFreq, warpAmp);
          let bestDSq = halfWidth * halfWidth;
          let bestSegIdx = -1;
          let bestT = 0;
          for (let i = 0; i < nPts; i++) {
            const ax = points[i][0], ay = points[i][1];
            const vx = points[i + 1][0] - ax, vy = points[i + 1][1] - ay;
            const dpx = wp.x - ax, dpy = wp.y - ay;
            const lenSq = vx * vx + vy * vy;
            const t = lenSq > 0 ? Math.max(0, Math.min(1, (dpx * vx + dpy * vy) / lenSq)) : 0;
            const cx = ax + vx * t - wp.x, cy = ay + vy * t - wp.y;
            const dSq = cx * cx + cy * cy;
            if (dSq < bestDSq) {
              bestDSq = dSq;
              bestSegIdx = i;
              bestT = t;
            }
          }
          if (bestSegIdx >= 0) {
            const bestD = Math.sqrt(bestDSq);
            const bestSegH = heights[bestSegIdx] + (heights[bestSegIdx + 1] - heights[bestSegIdx]) * bestT;
            const k = Math.cos((bestD / halfWidth) * Math.PI * 0.5);
            const ridge = ridgedFbm(wp.x * 0.018 + 2.1, wp.y * 0.018 - 6.3, 2);
            let rawH = bestSegH * Math.pow(Math.max(0, k), steepness) * (1 + (ridge - 0.5) * ridgeAmp);
            if (terraceStep > 0) rawH = rockTerrace(rawH, terraceStep, terraceStrength, wx, wy);
            const idx = row + mx;
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

      const maxTrailSq = (halfWidth + blendWidth + 3.5) * (halfWidth + blendWidth + 3.5);
      const nSegs = points3D.length - 1;
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          let bestDSq = maxTrailSq;
          let bestZ = 0;
          let found = false;
          for (let i = 0; i < nSegs; i++) {
            const p0 = points3D[i], p1 = points3D[i + 1];
            const ax = p0[0], ay = p0[1];
            const vx = p1[0] - ax, vy = p1[1] - ay;
            const dpx = wx - ax, dpy = wy - ay;
            const lenSq = vx * vx + vy * vy;
            const t = lenSq > 0 ? Math.max(0, Math.min(1, (dpx * vx + dpy * vy) / lenSq)) : 0;
            const cx = ax + vx * t - wx, cy = ay + vy * t - wy;
            const dSq = cx * cx + cy * cy;
            if (dSq < bestDSq) {
              bestDSq = dSq;
              bestZ = p0[2] + (p1[2] - p0[2]) * t;
              found = true;
            }
          }
          if (!found) continue;
          const bestD = Math.sqrt(bestDSq);
          const edgeN = fbm2dFast(wx * 0.032 + 4.1, wy * 0.032 - 1.9) * 3.0;
          const innerW = halfWidth + edgeN;
          const idx = row + mx;
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
          const n = fbm2dFast(wx * 0.016 + 11.3, wy * 0.016 - 5.7);
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
      const warpAmp = useWarp ? Math.min(34, Math.min(rx, ry) * 0.28) : 0;
      const maxR = Math.max(rx, ry) * (1 + noiseAmp) + rimWidth + (useWarp ? warpAmp + 6 : 8);
      const x0 = Math.max(0, Math.floor((cx - maxR) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + maxR) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - maxR) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + maxR) / VOX + HALF_GRID));

      const rimNorm = rimWidth / Math.max(1, Math.min(rx, ry));
      const minR = Math.max(1, Math.min(rx, ry));
      const marginNorm = noiseAmp + (warpAmp / minR) + 0.06;
      const maxNormPre = (1.0 + rimNorm) * (1.0 + noiseAmp) + (warpAmp / minR) + 0.15;
      const maxNormPreSq = maxNormPre * maxNormPre;
      const minInnerPre = Math.max(0, 1.0 - marginNorm);
      const minInnerPreSq = minInnerPre * minInnerPre;
      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const rdy = (wy - cy) / ry;
        const rdySq = rdy * rdy;
        const row = my * mw;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const rdx = (wx - cx) / rx;
          const rawNdSq = rdx * rdx + rdySq;
          if (rawNdSq > maxNormPreSq) continue;

          if (rawNdSq <= minInnerPreSq) {
            const idx = row + mx;
            if (lowerAllowed) {
              hmap[idx] = height;
            } else {
              const blended = !isCliff ? Math.min(64, Math.round(smax(hmap[idx], height, 6))) : height;
              if (blended > hmap[idx]) hmap[idx] = blended;
            }
            if (isCliff) cliffMask[idx] = 1;
            if (biome !== null) biomeMap[idx] = biome;
            if (mat !== null) matMap[idx] = mat;
            continue;
          }

          const wp = useWarp ? warp2d(wx, wy, 0.012, warpAmp) : { x: wx, y: wy };
          const dx = (wp.x - cx) / rx;
          const dy = (wp.y - cy) / ry;
          const nd = Math.hypot(dx, dy);
          const n = noiseAmp > 0 ? fbm2dFast(wx * 0.018 - 3.1, wy * 0.018 + 7.9) * noiseAmp : 0;
          const effNd = nd / (1 + n);

          if (effNd <= 1.0 + rimNorm) {
            const idx = row + mx;
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
            if (mat !== null && (effNd <= 1.0 || targetH >= 2 || (lowerAllowed && targetH >= 0))) matMap[idx] = mat;
          }
        }
      }
    }

    function pullRuinsBlock(cx, cy, halfW, halfD, height, rimWidth = 2.0, mat = MAT_STONE, biome = 2) {
      const pad = Math.max(halfW, halfD) * 1.15 + rimWidth + 6;
      const x0 = Math.max(0, Math.floor((cx - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + pad) / VOX + HALF_GRID));
      const rimNorm = rimWidth / Math.max(1, Math.min(halfW, halfD));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const nd = Math.max(Math.abs(wx - cx) / halfW, Math.abs(wy - cy) / halfD);
          const chip = fbm2d(wx * 0.08, wy * 0.08) * 0.08;
          const effNd = nd + chip;

          if (effNd <= 1.0 + rimNorm) {
            const idx = my * mw + mx;
            let targetH = height;
            if (effNd > 1.0) {
              const t = 1.0 - (effNd - 1.0) / rimNorm;
              const s = t * t * (3 - 2 * t);
              targetH = Math.round(height * s);
            }
            if (targetH > hmap[idx]) hmap[idx] = targetH;
            if (effNd <= 1.0 + rimNorm * 0.95) cliffMask[idx] = 1;
            if (biome !== null && effNd <= 1.0 + rimNorm * 0.6) biomeMap[idx] = biome;
            if (mat !== null && (effNd <= 1.0 || targetH >= 2)) matMap[idx] = mat;
          }
        }
      }
    }

    function carveOrganicPond(cx, cy, rx, ry, warpAmp = 26, waterH = 13, rimW = 8, rimH = 16, biome = 4) {
      const pad = Math.max(rx, ry) + rimW + warpAmp + 12;
      const x0 = Math.max(0, Math.floor((cx - pad) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((cx + pad) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((cy - pad) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((cy + pad) / VOX + HALF_GRID));
      const rimNorm = rimW / Math.max(1, Math.min(rx, ry));

      for (let my = y0; my <= y1; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const wp = warp2d(wx, wy, 0.015, warpAmp);
          const nd = Math.hypot((wp.x - cx) / rx, (wp.y - cy) / ry);
          const idx = my * mw + mx;
          if (nd <= 1.0) {
            hmap[idx] = waterH;
            matMap[idx] = MAT_WATER;
            biomeMap[idx] = biome;
            cliffMask[idx] = 1;
          } else if (nd <= 1.0 + rimNorm) {
            hmap[idx] = rimH;
            matMap[idx] = MAT_SAND;
            biomeMap[idx] = biome;
            cliffMask[idx] = 1;
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
          const row = my * mw;
          for (let mx = x0; mx <= x1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const dSq = distToSegmentSq(wx, wy, ax, ay, bx, by);
            if (dSq > (halfWidth + 5) * (halfWidth + 5)) continue;
            const d = Math.sqrt(dSq);
            const n = fbm2dFast(wx * 0.028 + 4.2, wy * 0.028 - 2.1) * 4.8;
            if (d <= halfWidth + n) {
              const idx = row + mx;
              if (matMap[idx] !== MAT_WATER && matMap[idx] !== MAT_BRIDGE) {
                matMap[idx] = mat;
                if (forceFlatZ !== null && !getBridgeAt(wx, wy)) hmap[idx] = forceFlatZ;
              }
              if (biome !== null) biomeMap[idx] = biome;
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
      const maxMouth = 42;
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
          const mouthFlare = wy > 615 ? Math.min(maxMouth, (wy - 615) * 0.24) : 0;
          const halfW = baseHalfW + mouthFlare;
          const bankW = halfW + 20;
          const maxBankSq = (bankW + 10.5) * (bankW + 10.5);
          const minRiverInner = Math.max(0, halfW - 10.2);
          const minRiverInnerSq = minRiverInner * minRiverInner;
          const row = my * mw;
          for (let mx = x0; mx <= x1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const dSq = distToSegmentSq(wx, wy, ax, ay, bx, by);
            if (dSq > maxBankSq) continue;
            const idx = row + mx;
            if (dSq <= minRiverInnerSq) {
              hmap[idx] = depth;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 5;
              continue;
            }
            const d = Math.sqrt(dSq);
            const wobble = fbm2dFast(wx * 0.015 + 9.2, wy * 0.015 - 4.4) * 10.0;
            const effD = d + wobble;
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
            const nb0 = idx - 1, nb1 = idx + 1, nb2 = idx - mw, nb3 = idx + mw;
            let lowNb = nb0, lowH = hmap[nb0];
            if (hmap[nb1] < lowH) { lowH = hmap[nb1]; lowNb = nb1; }
            if (hmap[nb2] < lowH) { lowH = hmap[nb2]; lowNb = nb2; }
            if (hmap[nb3] < lowH) { lowH = hmap[nb3]; lowNb = nb3; }
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

    const bridges = [];

    function addArchBridge(cfg) {
      bridges.push(cfg);
      const gx0 = Math.max(0, Math.floor(cfg.xMin / VOX + HALF_GRID));
      const gx1 = Math.min(mw - 1, Math.floor(cfg.xMax / VOX + HALF_GRID));
      const gy0 = Math.max(0, Math.floor(cfg.yMin / VOX + HALF_GRID));
      const gy1 = Math.min(mh - 1, Math.floor(cfg.yMax / VOX + HALF_GRID));
      for (let my = gy0; my <= gy1; my++) {
        const row = my * mw;
        for (let mx = gx0; mx <= gx1; mx++) {
          noGrassMask[row + mx] = 1;
        }
      }
    }

    function getBridgeDeckZ(br, wx, wy) {
      const uc = br.axis === 'x'
        ? Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)))
        : Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)));
      return Math.round(br.baseZ + br.archH * (1 - (2 * uc - 1) * (2 * uc - 1)));
    }

    function getBridgeAt(wx, wy, pad = 0) {
      for (let i = 0; i < bridges.length; i++) {
        const br = bridges[i];
        if (wx >= br.xMin - pad && wx <= br.xMax + pad && wy >= br.yMin - pad && wy <= br.yMax + pad) {
          return br;
        }
      }
      return null;
    }

    // 4.1. Construção dos 8 Biomas no Heightfield Contínuo 1080×1080
    const RIVER_WAYPOINTS = [
      [120, -1078], [156, -795], [144, -495], [148, -345],
      [102, -165], [134, 108], [144, 435], [120, 665], [120, 770]
    ];
    const RIVER_SEGMENTS = [];
    for (let i = 0; i < RIVER_WAYPOINTS.length - 1; i++) {
      const [ax, ay] = RIVER_WAYPOINTS[i];
      const [bx, by] = RIVER_WAYPOINTS[i + 1];
      const dx = bx - ax, dy = by - ay;
      const len = Math.hypot(dx, dy) || 1;
      RIVER_SEGMENTS.push({ ax, ay, bx, by, dx, dy, len2: dx * dx + dy * dy, tx: dx / len, ty: dy / len });
    }

    function initOrganicWorld() {
      // Base inicial: plano verde Z=0
      hmap.fill(0);
      matMap.fill(MAT_GRASS);
      biomeMap.fill(0);
      bridges.length = 0;

      // Divisão orgânica inicial dos biomas por região
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const idx = row + mx;
          const wNoise = valueNoise2d(wx * 0.0055, wy * 0.0055) * 54;
          if (wy + wNoise > 645) biomeMap[idx] = 3; // Praia Sul
          else if (wx + wNoise > 126 && wy + wNoise < -15) biomeMap[idx] = 7; // Montanha NE
          else if (wx + wNoise > 126 && wy + wNoise >= -15) biomeMap[idx] = 6; // Bosque SE
          else if (wy + wNoise < -255 && wx + wNoise < 105) biomeMap[idx] = 4; // Jardim Zen NW
          else if (wx + wNoise < -600 && wy + wNoise >= -255) biomeMap[idx] = 1; // Girassóis W
          else if (wy + wNoise >= 360 && wx + wNoise < 90) biomeMap[idx] = 2; // Ruínas
          else biomeMap[idx] = 0; // Vila
        }
      }

      // Moldura natural elevada nas bordas Oeste, Norte e Leste (Sul aberto para o mar!)
      const edgeCols = Math.ceil(132 / VOX);
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy > 645) continue;
        const inTopBand = (wy - WORLD_MIN) < 132;
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          if (!inTopBand && mx >= edgeCols && mx < mw - edgeCols) {
            mx = mw - edgeCols - 1;
            continue;
          }
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const rawEdgeDist = Math.min(wx - WORLD_MIN, WORLD_MAX - wx, wy - WORLD_MIN);
          if (rawEdgeDist >= 132) continue;
          const wp = warp2d(wx, wy, 0.0075, 30);
          const edgeDist = Math.min(wp.x - WORLD_MIN, WORLD_MAX - wp.x, wp.y - WORLD_MIN);
          if (edgeDist >= 102) continue;
          const ridge = ridgedFbm(wp.x * 0.010 + 3.7, wp.y * 0.010 + 1.9, 2);
          const span = 78 + ridge * 24;
          if (edgeDist < span) {
            const t = Math.max(0, Math.min(1, (span - edgeDist) / 54));
            const peakH = 14 + ridge * 12;
            const idx = row + mx;
            hmap[idx] = Math.max(hmap[idx], Math.round(peakH * Math.pow(t, 1.15)));
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 1: CAMPOS DE GIRASSOL (Oeste) — cristas ondulantes orgânicas
      // ---------------------------------------------------------------------
      pullRidge([[-900, -135], [-825, -75], [-735, -15]], 132, [12, 14, 7], { warpAmp: 33, smoothK: 8, ridgeAmp: 0.24, mat: MAT_GRASS, biome: 1 });
      pullRidge([[-870, 210], [-810, 246], [-728, 315]], 114, [10, 8, 5], { warpAmp: 27, smoothK: 7, ridgeAmp: 0.22, mat: MAT_GRASS, biome: 1 });

      // ---------------------------------------------------------------------
      // BIOMA 0: VILA DA CLAREIRA (Centro-Oeste) — rampa orgânica Z=0..6
      // ---------------------------------------------------------------------
      pullHill(-285, -66, 93, 6, 1.35, 0.16, MAT_GRASS, 0);

      // ---------------------------------------------------------------------
      // BIOMA 4: JARDIM ZEN & PORTAL TORII (Noroeste)
      // ---------------------------------------------------------------------
      pullPlateau(-480, -510, 342, 270, 16, 48, 0.14, false, MAT_GRASS, 4);
      // Extensão Leste até Ponte Norte (wx=56, wy=-345)
      pullPlateau(-84, -354, 156, 78, 16, 42, 0.10, false, MAT_GRASS, 4);
      pullPlateau(54, -345, 28, 28, 16, 14, 0.04, false, MAT_STONE, 4, false, false);
      // Rampa larga da Vila (-435, -165) -> Jardim Zen (-435, -324)
      paintRampPath(-435, -165, 0, -435, -324, 16, 38, MAT_PATH, 4);
      // Terraço Superior Zen (Z=32 -> Z=48 orgânico em esporão terraceado)
      pullPlateau(-765, -765, 144, 114, 32, 24, 0.12, false, MAT_GRASS, 4);
      pullRidge([[-680, -760], [-760, -805], [-825, -825], [-890, -860]], 86, [32, 42, 48, 44], {
        warpAmp: 24, smoothK: 8, ridgeAmp: 0.22, terraceStep: 12, terraceStrength: 0.45, mat: MAT_STONE, biome: 4
      });
      pullPlateau(-825, -825, 28, 24, 48, 10, 0.06, false, MAT_STONE, 4, false, false);
      // Alameda Zen (~44u de largura!) passando sob o Torii (-435, -405)
      paintOrganicPath([[-435, -315], [-435, -615]], 22, MAT_PATH, 4, 16);
      // Lago Zen orgânico com warp2d em (-690, -585)
      carveOrganicPond(-690, -585, 66, 46, 26, 13, 8, 16, 4);

      // ---------------------------------------------------------------------
      // BIOMA 6: BOSQUE DOS COGUMELOS SALTITANTES (Sudeste)
      // ---------------------------------------------------------------------
      // Circuito aéreo de cogumelos: apoio Z=12 e Z=24 para caps Z=22 / 34 / 46 (espaçamento proporcional)
      pullPlateau(518, 272, 18, 18, 12, 14, 0.10, false, MAT_STONE, 6, false, false); // Apoio #2 (cap Z=34)
      pullPlateau(569, 288, 30, 16, 24, 12, 0.10, false, MAT_GRASS, 6, false, false); // Apoio #3 e #4 (caps Z=46)
      pullPlateau(620, 272, 18, 18, 12, 14, 0.10, false, MAT_STONE, 6, false, false); // Apoio #5 (cap Z=34)
      pullRidge([[735, 435], [825, 495], [915, 578]], 126, [11, 16, 12], { warpAmp: 33, smoothK: 8, ridgeAmp: 0.25, mat: MAT_GRASS, biome: 6 });

      // ---------------------------------------------------------------------
      // BIOMA 7: MONTANHA DO PICO SAKURA (Nordeste, Z=64 topo)
      // ---------------------------------------------------------------------
      // Contraforte Oeste Z=16 onde chega a Ponte Norte (wx=244, wy=-345)
      pullRidge([[222, -345], [288, -330], [366, -276], [438, -363]], 75, [16, 17, 24, 34], { warpAmp: 30, smoothK: 8, ridgeAmp: 0.26, mat: MAT_STONE, biome: 7 });
      pullPlateau(236, -345, 30, 26, 16, 14, 0.06, false, MAT_STONE, 7, false, false);
      // Paredão escarpado Oeste/Sul (intransponível direto!)
      pullPlateau(480, -540, 216, 186, 48, 9, 0.12, true, MAT_STONE, 7, false, true);
      // Espigões geológicos irradiando da montanha
      pullRidge([[540, -525], [690, -480], [818, -360], [750, -195], [652, -98]], 138, [58, 48, 34, 20, 6], { warpAmp: 39, ridgeAmp: 0.30, smoothK: 10, terraceStep: 14, terraceStrength: 0.35, mat: MAT_GRASS, biome: 7 });
      pullRidge([[525, -585], [660, -682], [802, -645], [848, -510]], 123, [58, 52, 42, 34], { warpAmp: 36, ridgeAmp: 0.30, smoothK: 10, terraceStep: 14, terraceStrength: 0.35, mat: MAT_GRASS, biome: 7 });
      // Cume arredondado do Pico Sakura (Z=64)
      pullPlateau(480, -540, 153, 135, 64, 33, 0.14, false, MAT_PEAK, 7, false, true);
      // Trilha contínua escavada em patamar subindo a encosta (Z=0 -> Z=64)
      carveBenchTrail([
        [615, -66, 0],
        [675, -135, 10],
        [753, -228, 20],
        [822, -339, 30],
        [819, -483, 40],
        [771, -612, 48],
        [681, -693, 56],
        [588, -645, 62],
        [531, -576, 64]
      ], 19, 40, MAT_PATH, 7);

      // ---------------------------------------------------------------------
      // BIOMA 5: RIO SINUOSO & CACHOEIRA ORGÂNICA (largura ~76u)
      // ---------------------------------------------------------------------
      const riverPts = RIVER_WAYPOINTS;
      carveRiverPath(riverPts, 76, -6);

      // Cachoeira Vertical na Falésia Oeste (wy=-495) + Poço + Riacho Plano até o Rio
      // Parte C1: Riacho plano (Z=-5) ligando o pé da cachoeira (wx=225) ao rio principal (wx=144)
      carveRiverPath([[225, -495], [185, -490], [144, -488]], 32, -5);

      // Parte C2: Poço circular com borda rasa arenosa ao pé da falésia (sem corroer a rocha alta h > 10)
      {
        const gx0 = Math.max(0, Math.floor(204 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(282 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(-530 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(-460 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            if (hmap[idx] > 10) continue;
            const d = Math.hypot(wx - 238, wy + 495) + fbm2d(wx * 0.12, wy * 0.12) * 1.6;
            if (d <= 22) {
              hmap[idx] = -5;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 5;
              cliffMask[idx] = 1;
            } else if (d <= 27 && matMap[idx] !== MAT_WATER && hmap[idx] <= 2) {
              hmap[idx] = Math.min(hmap[idx], 0);
              matMap[idx] = MAT_SAND;
              biomeMap[idx] = 5;
            }
          }
        }
      }

      // Partes A & B: Nascente rebaixada no platô (h>=44 -> 46) + Cortina vertical colada à encosta da falésia (1<=h<=48)
      {
        const gx0 = Math.max(0, Math.floor(224 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(348 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(-525 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(-465 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            const curH = hmap[idx];
            const n = fbm2d(wx * 0.05, wy * 0.05) * 4.5;
            if (Math.abs(wy + 495 + n) <= 15.0) {
              if (wx >= 265 && curH >= 44) {
                // Parte A: Nascente encaixada 2u abaixo da borda Z=48 da montanha
                hmap[idx] = 46;
                matMap[idx] = MAT_WATER;
                biomeMap[idx] = 7;
                cliffMask[idx] = 1;
              } else if (wx <= 315 && curH >= 1 && curH <= 48) {
                // Parte B: Cortina vertical acompanhando o relevo real da falésia (zero rampa flutuante)
                matMap[idx] = MAT_WATER;
                biomeMap[idx] = 7;
                cliffMask[idx] = 1;
              }
            }
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 3: PRAIA DOURADA, BAÍA SUL, PÍER, 8 VITÓRIAS-RÉGIAS & FAROL
      // ---------------------------------------------------------------------
      const shoreYByCol = new Float32Array(mw);
      const sandStartByCol = new Float32Array(mw);
      for (let mx = 0; mx < mw; mx++) {
        const wx = (mx - HALF_GRID + 0.5) * VOX;
        const wave = fbm2dFast(wx * 0.005 + 2.5, 1.2) * 34;
        shoreYByCol[mx] = 756 + wave;
        sandStartByCol[mx] = 636 + wave * 0.7;
      }
      const beachMy0 = Math.max(0, Math.floor(615 / VOX + HALF_GRID));
      for (let my = beachMy0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          const shoreY = shoreYByCol[mx];
          const sandStart = sandStartByCol[mx];

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

      // Ilhota Tropical Sul no Mar Sul (leste das 8 vitórias-régias, sempre MAT_SAND em h>=0)
      pullPlateau(198, 858, 72, 58, 2, 10, 0.14, true, MAT_SAND, 3, true);
      // Promontório Rochoso do Farol (Sudoeste) + Rampa de Acesso
      paintRampPath(-555, 714, 0, -636, 768, 14, 24, MAT_SAND, 3);
      pullPlateau(-690, 810, 132, 108, 14, 15, 0.14, true, MAT_STONE, 3);

      // 8 Vitórias-Régias saltáveis sobre o mar do Píer até a Ilhota Tropical Sul!
      for (const [lx, ly] of [
        [-132, 852], [-98, 864], [-64, 852], [-30, 864],
        [4, 852], [38, 864], [72, 852], [106, 858]
      ]) {
        setCirclePatch(lx, ly, 14.0, 0, MAT_LILYPAD, 3, true);
      }

      // ---------------------------------------------------------------------
      // PONTES PARABÓLICAS EM ARCO (rio visível embaixo!) & PEDRAS DE TRAVESSIA
      // ---------------------------------------------------------------------
      // Ponte Central em Arco (Z=2..8, Vila <-> Bosque)
      addArchBridge({ axis: 'x', xMin: 40, xMax: 230, yMin: 84, yMax: 132, baseZ: 2, archH: 6, hasRailings: true, biome: 5 });
      // Ponte Norte Alta em Arco (Z=16..21, Jardim Zen <-> Contraforte da Montanha)
      addArchBridge({ axis: 'x', xMin: 56, xMax: 244, yMin: -368, yMax: -322, baseZ: 16, archH: 5, hasRailings: true, biome: 5 });
      // Passarela Sul da Praia (Z=2..7, Praia Oeste <-> Praia Leste)
      addArchBridge({ axis: 'x', xMin: 30, xMax: 220, yMin: 645, yMax: 685, baseZ: 2, archH: 5, hasRailings: true, biome: 3 });
      // Píer Sul de Madeira (Z=2)
      addArchBridge({ axis: 'y', xMin: -198, xMax: -162, yMin: 690, yMax: 865, baseZ: 2, archH: 0, hasRailings: false, isPier: true, biome: 3 });

      // Garante margens planas e transitáveis nos encontros das pontes de Z=2 e do Píer
      for (const [ax, ay] of [[40, 108], [230, 108], [30, 665], [220, 665], [-180, 690]]) {
        pullPlateau(ax, ay, 24, 24, 0, 10, 0.04, false, MAT_PATH, null, false, false);
      }

      // Pedras de Travessia no Rio Médio-Sul (Z=2, wy=495)
      for (const sx of [96, 124, 152, 180]) {
        setCirclePatch(sx, 495, 12.0, 2, MAT_STONE, 5, true);
      }

      // ---------------------------------------------------------------------
      // BIOMA 2: RUÍNAS ORGÂNICAS & 4 BLOCOS ERODIOS DE TESTE (cliffMask=1)
      // ---------------------------------------------------------------------
      // Pátio plano Z=0 em volta de wy=378..630 garantindo base limpa para os testes
      {
        const gx0 = Math.max(0, Math.floor(-558 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(54 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(378 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(630 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const inPathY = (wy >= 408 && wy <= 606);
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            if (matMap[idx] !== MAT_WATER) {
              hmap[idx] = 0;
              biomeMap[idx] = 2;
              cliffMask[idx] = 1;
              if (inPathY && wx >= -498 && wx <= 42) {
                matMap[idx] = MAT_PATH;
              }
            }
          }
        }
      }
      // 4 Blocos Retangulares Erodidos das Ruínas ao longo de wy=495 (halfW=30, halfD=26)
      pullRuinsBlock(-420, 495, 30, 26, 6,  8.0, MAT_STONE, 2); // A: Z=6  (sobe andando!)
      pullRuinsBlock(-285, 495, 30, 26, 16, 2.0, MAT_STONE, 2); // B: Z=16 (pulo 1H!)
      pullRuinsBlock(-150, 495, 30, 26, 32, 2.0, MAT_STONE, 2); // C: Z=32 (pulo 2H máx!)
      pullRuinsBlock(-15,  495, 30, 26, 48, 2.0, MAT_STONE, 2); // D: Z=48 (3H bloqueado!)

      // ---------------------------------------------------------------------
      // TRILHAS ORGÂNICAS CONECTANDO VILA <-> BIOMAS
      // ---------------------------------------------------------------------
      paintOrganicPath([[-330, 90], [40, 108]], 20, MAT_PATH, 0, 0);                            // Vila -> Ponte Central
      paintOrganicPath([[230, 108], [375, 165], [570, 90], [615, -66]], 20, MAT_PATH, 6);       // Ponte -> Bosque / Base Montanha
      paintOrganicPath([[-330, 90], [-630, 90]], 20, MAT_PATH, 0, 0);                           // Vila -> Girassóis
      paintOrganicPath([[-330, 90], [-330, 405]], 20, MAT_PATH, 0, 0);                          // Vila -> Ruínas
      paintOrganicPath([[-330, 90], [-435, -165]], 20, MAT_PATH, 0, 0);                         // Vila -> Rampa Zen
      paintOrganicPath([[-216, 585], [-180, 690]], 20, MAT_PATH, 2, 0);                         // Ruínas -> Píer
      paintOrganicPath([[-180, 665], [30, 665]], 18, MAT_SAND, 3);                              // Praia Oeste -> Passarela Sul
      paintOrganicPath([[220, 665], [480, 714]], 18, MAT_SAND, 3);                              // Passarela Sul -> Praia Leste
      paintOrganicPath([[-330, 90], [-458, 135]], 16, MAT_PATH, 0, 0);                          // Vila -> Cabana 1
      paintOrganicPath([[-330, 90], [-243, 201]], 16, MAT_PATH, 0, 0);                          // Vila -> Cabana 2

      // Garante platôs planos Z=0 sob a Cabana 1 (-525, 135) e Cabana 2 (-180, 225)
      for (const [x0w, x1w, y0w, y1w] of [[-624, -420, 45, 240], [-270, -90, 150, 300]]) {
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
      thermalAndHydraulicErosion(2, 240);
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
      pine_tree:       { mode: 'solid',    r: 7.5,  h: 72,  shadowR: 19 },
      sakura_oak:      { mode: 'solid',    r: 14.0, h: 102, shadowR: 36 },
      cozy_cabin:      { mode: 'box',      halfW: 35.0, halfD: 30.5, h: 80, shadowR: 42 },
      lighthouse:      { mode: 'solid',    r: 21.5, h: 126, shadowR: 30 },
      campfire:        { mode: 'solid',    r: 7.2,  h: 13,  shadowR: 9 },
      wood_sign:       { mode: 'solid',    r: 5.0,  h: 20 },
      ruin_pillar:     { mode: 'solid',    r: 11.0, h: 50,  shadowR: 16 },
      stone_lantern:   { mode: 'solid',    r: 8.0,  h: 36,  shadowR: 12 },
      beach_umbrella:  { mode: 'solid',    r: 3.8,  h: 42,  shadowR: 18 },
      wood_boat:       { mode: 'box',      halfW: 22.5, halfD: 12.8, h: 18, shadowR: 20 },
      bush_berry:      { mode: 'solid',    r: 6.8,  h: 13,  shadowR: 9 },
      sunflower:       { mode: 'solid',    r: 4.5,  h: 21 },
      pumpkin_patch:   { mode: 'solid',    r: 8.2,  h: 11 },
      mushroom_giant:  { mode: 'platform', r: 11.2, h: 22,  shadowR: 15 },
      boulder_large:   { mode: 'platform', r: 8.8,  h: 16,  shadowR: 12 },
      hay_bale:        { mode: 'platform', r: 9.6,  h: 14,  shadowR: 12 },
      tree_stump:      { mode: 'platform', r: 9.2,  h: 14,  shadowR: 12 },
      torii_gate:      { mode: 'arch',     offset: 24.5, r: 5.5, h: 80, shadowR: 26 },
      flower_tuft:     { mode: 'none' },
      grass_tuft_short:{ mode: 'none' },
      grass_tuft_tall: { mode: 'none' }
    };

    const FOLIAGE_META = {
      pine_tree:     { isFoliage: true, rigidity: 0.62, windScale: 3.2, pushRadius: 16, pushStrength: 3.5, leafColors: ['#2D6A4F', '#40916C', '#52B788'] },
      sakura_oak:    { isFoliage: true, rigidity: 0.58, windScale: 3.6, pushRadius: 24, pushStrength: 3.0, leafColors: ['#F9A8D4', '#F472B6', '#FBCFE8'] },
      bush_berry:    { isFoliage: true, rigidity: 0.25, windScale: 2.6, pushRadius: 14, pushStrength: 6.5, leafColors: ['#3A7D44', '#65B85B', '#EF4444'] },
      sunflower:     { isFoliage: true, rigidity: 0.18, windScale: 3.8, pushRadius: 12, pushStrength: 7.5, leafColors: ['#FACC15', '#EAB308', '#4D7C0F'] },
      flower_tuft:   { isFoliage: true, rigidity: 0.12, windScale: 2.4, pushRadius: 10, pushStrength: 6.0, leafColors: ['#FACC15', '#F472B6', '#FFFFFF'] },
      pumpkin_patch: { isFoliage: true, rigidity: 0.72, windScale: 1.0, pushRadius: 12, pushStrength: 2.5, leafColors: ['#EA580C', '#65B85B'] }
    };

    const TOOLS_META = {
      none:         { label: '🐾 Patada',   modelKey: null },
      tool_axe:     { label: '🪓 Machado',  modelKey: 'tool_axe' },
      tool_pickaxe: { label: '⛏️ Picareta', modelKey: 'tool_pickaxe' },
      tool_hoe:     { label: '🌾 Enxada',   modelKey: 'tool_hoe' }
    };
    const TOOL_ORDER = ['none', 'tool_axe', 'tool_pickaxe', 'tool_hoe'];

    const DESTRUCTIBLE_META = {
      pine_tree:     { mode: 'chop',    hp: 3, zCut: 8,  drops: 3, dropKey: 'wood_log',    bestTool: 'tool_axe',     colors: ['#2D6A4F', '#40916C', '#6B4226', '#8C5A37'] },
      sakura_oak:    { mode: 'chop',    hp: 4, zCut: 10, drops: 4, dropKey: 'wood_log',    bestTool: 'tool_axe',     colors: ['#F9A8D4', '#F472B6', '#FBCFE8', '#6B4226'] },
      ruin_pillar:   { mode: 'crumble', hp: 3, zCut: 9,  drops: 3, dropKey: 'stone_chunk', bestTool: 'tool_pickaxe', colors: ['#847F77', '#ADA79E', '#CFC9BE', '#68A352'] },
      boulder_large: { mode: 'crumble', hp: 3, zCut: 5,  drops: 3, dropKey: 'stone_chunk', bestTool: 'tool_pickaxe', colors: ['#5C5852', '#847F77', '#ADA79E'] },
      stone_lantern: { mode: 'crumble', hp: 2, zCut: 7,  drops: 2, dropKey: 'stone_chunk', bestTool: 'tool_pickaxe', colors: ['#847F77', '#FDE68A', '#CFC9BE'] },
      bush_berry:    { mode: 'trim',    hp: 2, drops: 0, bestTool: 'tool_hoe', colors: ['#3A7D44', '#65B85B', '#EF4444'] },
      sunflower:     { mode: 'trim',    hp: 1, drops: 0, bestTool: 'tool_hoe', colors: ['#FACC15', '#EAB308', '#4D7C0F'] },
      pumpkin_patch: { mode: 'trim',    hp: 2, drops: 0, bestTool: 'tool_hoe', colors: ['#EA580C', '#F97316', '#65B85B'] }
    };

    const props = [];
    const foliageProps = [];
    const propColliders = [];
    const platformColliders = [];
    const fishes = [];
    const npcs = [];
    const toolPickups = [];
    const fallingBodies = [];
    const debrisDrops = [];
    const destructStats = {
      hits: 0,
      choppedCount: 0,
      crumbledCount: 0,
      trimmedCount: 0
    };

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
        if (c.mat === MAT_PATH || c.mat === MAT_BRIDGE || c.mat === MAT_WATER || c.mat === MAT_LILYPAD || getBridgeAt(wx, wy, 2)) {
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
      const fMeta = FOLIAGE_META[modelKey];
      if (fMeta) {
        item.foliage = fMeta;
        item.bx = 0;
        item.by = 0;
        item.vx = 0;
        item.vy = 0;
        item.rustleCd = 0;
        foliageProps.push(item);
      }
      const dMeta = DESTRUCTIBLE_META[modelKey];
      if (dMeta) {
        item.destr = { ...dMeta, maxHp: dMeta.hp, hp: dMeta.hp, hitFlash: 0, chopped: false };
      }
      props.push(item);

      const footR = meta.mode === 'box'
        ? Math.max(meta.halfW, meta.halfD) * scale
        : (meta.r || 4) * scale;
      stampPropShadowAndClearGrass(wx, wy, (meta.shadowR || 0) * scale, meta.mode !== 'none' ? footR : 0);

      if (meta.mode === 'solid') {
        const sc = {
          shape: 'circle', wx, wy,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey,
          disabled: false
        };
        propColliders.push(sc);
        item.solidCollider = sc;
      } else if (meta.mode === 'box') {
        const sc = {
          shape: 'box', wx, wy,
          halfW: meta.halfW * scale, halfD: meta.halfD * scale,
          angle, baseZ: liftZ, colH: meta.h * scale, modelKey,
          disabled: false
        };
        propColliders.push(sc);
        item.solidCollider = sc;
      } else if (meta.mode === 'platform') {
        const pc = {
          wx, wy, r: meta.r * scale,
          baseZ: liftZ, topZ: liftZ + meta.h * scale, modelKey,
          disabled: false
        };
        platformColliders.push(pc);
        item.platCollider = pc;
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
      const br = getBridgeAt(wx, wy);
      const c = getCellAt(wx, wy);
      const baseH = br ? getBridgeDeckZ(br, wx, wy) : (c ? c.h : 0);
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
          if (getBridgeAt(wx + dx, wy + dy, 0)) return true;
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
      if (Math.hypot(wx + 330, wy - 90) < 32) return; // Mantém spawn livre
      const meta = PROP_COLLIDER_META[modelKey] || { r: 5 };
      const minGap = (meta.r || 5) + 6;
      for (const sc of propColliders) {
        if (sc.disabled) continue;
        if (isPointInPropCollider(wx, wy, sc, minGap)) return;
      }
      for (const pc of platformColliders) {
        if (pc.disabled) continue;
        if (Math.hypot(wx - pc.wx, wy - pc.wy) < pc.r + minGap) return;
      }
      addProp(modelKey, wx, wy, options);
    }

    function populateWorldObjects() {
      // 0. Vila da Clareira (Mini-Vila com 2 Cabanas, fogueira, horta e tocos)
      addProp('cozy_cabin', -525, 135);
      addProp('cozy_cabin', -180, 225);
      addProp('campfire', -285, 30);
      addProp('wood_sign', -276, 134, { angle: 0.22 });
      addProp('pumpkin_patch', -465, 252);
      addProp('pumpkin_patch', -426, 261);
      addProp('tree_stump', -262, 153);
      addProp('tree_stump', -378, 195);
      addProp('flower_tuft', -396, 174);
      addProp('flower_tuft', -348, 36);
      addProp('flower_tuft', -231, 276);
      addProp('bush_berry', -204, 297);
      addProp('bush_berry', -579, 228);
      addForestProp('pine_tree', -585, -54);
      addForestProp('pine_tree', -186, -75);
      addForestProp('pine_tree', -570, 288);
      addForestProp('pine_tree', -120, 322);
      addForestProp('pine_tree', -435, 33);
      addForestProp('pine_tree', -75, -52);

      // 1. Campos de Girassol (~30 girassóis + 4 fardos platform)
      for (const [tx, ty] of [
        [-825, 30], [-765, 96], [-864, -30], [-744, -126], [-876, -135],
        [-774, 216], [-855, 264], [-720, 324], [-906, 126], [-705, -36],
        [-930, -60], [-897, 33], [-807, -174], [-684, -186], [-918, 204],
        [-792, 315], [-663, 249], [-741, 36], [-834, 168], [-927, -162],
        [-960, 0], [-950, 90], [-965, 170], [-880, 310], [-750, -210],
        [-850, -220], [-690, 110], [-795, -55], [-890, -200], [-660, -90]
      ]) {
        addProp('sunflower', tx, ty);
      }
      addProp('hay_bale', -675, 186);
      addProp('hay_bale', -765, 156);
      addProp('hay_bale', -840, 270);
      addProp('hay_bale', -720, -45);
      addProp('tree_stump', -696, 312);
      addProp('flower_tuft', -870, 186);
      addProp('flower_tuft', -756, -81);
      addForestProp('pine_tree', -942, -243);
      addForestProp('pine_tree', -936, 360);
      addForestProp('pine_tree', -645, -243);

      // 2. Ruínas Orgânicas (Pátio sul em wy=495)
      addProp('ruin_pillar', -516, 414, { allowOnPath: true });
      addProp('ruin_pillar', 48,   414, { allowOnPath: true });
      addProp('stone_lantern', -516, 576, { allowOnPath: true });
      addProp('stone_lantern', 48,   576, { allowOnPath: true });
      addProp('boulder_large', -504, 495, { allowOnPath: true });
      addProp('flower_tuft', -360, 606);
      addProp('flower_tuft', -82,  606);

      // 3. Praia Dourada, Enseada & Farol Monumental
      addProp('lighthouse', -714, 822);
      addProp('stone_lantern', -606, 774);
      addProp('beach_umbrella', -360, 702);
      addProp('beach_umbrella', -60,  708);
      addProp('beach_umbrella', 270,  702);
      addProp('wood_boat', 345,  720, { angle: 0.16 });
      addProp('wood_boat', -465, 726, { angle: -0.22 });
      addProp('boulder_large', 234, 870);
      addProp('boulder_large', -540, 756);

      // 4. Jardim Zen & Portal Torii Gigante
      addProp('torii_gate', -435, -405, { angle: 0, allowOnPath: true });
      addProp('stone_lantern', -545, -405);
      addProp('stone_lantern', -325, -405);
      addProp('stone_lantern', -576, -570);
      addProp('bush_berry', -276, -585);
      addProp('flower_tuft', -474, -630);
      addProp('boulder_large', -705, -735);
      addProp('ruin_pillar', -762, -744);
      addForestProp('pine_tree', -252, -675);
      addForestProp('pine_tree', -630, -735);
      addForestProp('pine_tree', -840, -465);
      addForestProp('pine_tree', -210, -840);
      addForestProp('pine_tree', -540, -855);

      // 6. Bosque dos Cogumelos Saltitantes (7 cogumelos gigantes em circuito aéreo)
      addProp('mushroom_giant', 484, 256);  // #1 Cap Z=22
      addProp('mushroom_giant', 518, 272);  // #2 Em Z=12 -> Cap Z=34!
      addProp('mushroom_giant', 552, 288);  // #3 Em Z=24 -> Cap Z=46!
      addProp('mushroom_giant', 586, 288);  // #4 Em Z=24 -> Cap Z=46!
      addProp('mushroom_giant', 620, 272);  // #5 Em Z=12 -> Cap Z=34!
      addProp('mushroom_giant', 654, 256);  // #6 Cap Z=22
      addProp('mushroom_giant', 384, 435);  // #7 Cap Z=22 (âncora sul)
      for (const [tx, ty] of [
        [315, 228], [354, 345], [480, 525], [684, 516], [765, 276],
        [885, 330], [870, 555], [306, 546], [924, 435], [744, 126],
        [510, 435], [630, 405]
      ]) {
        addForestProp('pine_tree', tx, ty);
      }
      addProp('tree_stump', 378, 258);
      addProp('tree_stump', 741, 237);
      addProp('hay_bale', 804, 474);
      addProp('boulder_large', 744, 126);
      addProp('boulder_large', 465, 360);
      addProp('boulder_large', 862, 442);
      addProp('bush_berry', 540, 426);
      addProp('bush_berry', 675, 372);
      addProp('flower_tuft', 408, 216);
      addProp('flower_tuft', 660, 240);

      // 7. Montanha & Pico Sakura (Trilha em espiral mantida 100% livre!)
      addProp('sakura_oak', 450, -576);
      addProp('stone_lantern', 558, -486, { allowOnPath: true });
      addProp('stone_lantern', 408, -474, { allowOnPath: true });
      addProp('flower_tuft', 438, -474);
      addProp('flower_tuft', 546, -576);
      addProp('boulder_large', 336, -288);
      addForestProp('pine_tree', 426, -165);
      addForestProp('pine_tree', 375, -780);
      addForestProp('pine_tree', 900, -705);
      addForestProp('pine_tree', 930, -90);
      addForestProp('pine_tree', 285, -675);

      // Florestas Densas nas bordas arborizadas (Norte, Oeste, Leste) — expansão 1.5× (~85 pinheiros!)
      for (let wx = -960; wx <= 960; wx += 120) {
        if (Math.abs(wx - 120) < 95) continue;
        addForestProp('pine_tree', wx, -1020);
      }
      for (let wy = -870; wy <= 540; wy += 125) {
        addForestProp('pine_tree', -1020, wy);
        addForestProp('pine_tree', 1020, wy);
      }
      // Bosques orgânicos secundários de borda (+ ~25 pinheiros extras)
      for (const [bx, by] of [
        [-960, -915], [-705, -945], [270, -930], [630, -930],
        [-952, -540], [945, -360], [952, 165], [-945, 480],
        [-860, -950], [-560, -960], [-360, -960], [-140, -960], [340, -960],
        [520, -960], [760, -950], [920, -860], [-960, -740], [-960, -340],
        [-960, 120], [-960, 380], [960, -540], [960, -180], [960, 60],
        [960, 320], [960, 520], [-740, -400], [-320, -780], [260, -820],
        [780, -780], [880, -240], [820, 120], [-460, 320], [310, 590]
      ]) {
        addForestProp('pine_tree', bx, by);
      }
      for (const [bx, by] of [
        [-900, -810], [-540, -930], [345, -870], [870, -585], [900, 210], [-915, 435]
      ]) {
        addForestProp('bush_berry', bx, by);
      }

      // 20 PEIXES DOURADOS COLECIONÁVEIS (distribuídos pelos 8 biomas)
      addFish(-285, -66,  'Rampa da Vila');                  // #1  Vila (Z=6)
      addFish(-262, 153,  'Toco da Vila', 14);               // #2  Vila (Z=14)
      addFish(-675, 186,  'Fardo dos Girassóis', 14);        // #3  Girassóis (Z=14)
      addFish(-825, -75,  'Colina dos Girassóis');           // #4  Girassóis (Z=14)
      addFish(-810, 246,  'Campo Sul dos Girassóis');        // #5  Girassóis (Z=8)
      addFish(-285, 495,  'Monolito Médio das Ruínas');      // #6  Ruínas (Z=16)
      addFish(-15,  495,  'Torre das Ruínas');               // #7  Ruínas (Z=48)
      addFish(-180, 855,  'Ponta do Píer');                  // #8  Praia (Z=2)
      addFish(-615, 846,  'Mirante do Farol');               // #9  Praia (Z=14)
      addFish(198,  858,  'Ilhota das Vitórias-Régias');     // #10 Praia (Z=2)
      addFish(480,  714,  'Enseada Leste');                  // #11 Praia (Z=0)
      addFish(135,  108,  'Ponte Central');                  // #12 Rio (Z=8 topo do arco)
      addFish(124,  495,  'Pedra do Rio');                   // #13 Rio (Z=2)
      addFish(150,  -345, 'Ponte Norte');                    // #14 Rio (Z=21 topo do arco)
      addFish(-435, -585, 'Alameda Pós-Torii');              // #15 Zen (Z=16)
      addFish(-825, -825, 'Mirante Zen');                    // #16 Zen (Z=48)
      addFish(518,  272,  'Cogumelo Médio', 22);             // #17 Cogumelos (Z=34)
      addFish(586,  288,  'Cogumelo Alto', 22);              // #18 Cogumelos (Z=46)
      addFish(819,  -483, 'Patamar da Montanha');            // #19 Montanha (Z=40)
      addFish(528,  -528, 'Pico Sakura Lendário');           // #20 Montanha (Z=64)

      // NPCs: Galinha Popó na Vila + 3 Pintinhos Piu nos Girassóis
      const popoCell = getCellAt(-324, 168);
      npcs.push({
        kind: 'chicken', name: 'Popó', model: chickenModel, scale: 0.72,
        x: -324, y: 168, z: popoCell ? popoCell.h : 0, homeX: -324, homeY: 168, roamR: 60,
        selfAngle: 0, walkPhase: 0, timer: 1.4, moving: true, dirX: 1, dirY: 0,
        speech: null
      });
      for (const [cx, cy] of [[-780, 60], [-795, -45], [-690, 225]]) {
        const c = getCellAt(cx, cy);
        npcs.push({
          kind: 'chick', name: 'Piu', model: propModels.baby_chick, scale: 0.95,
          x: cx, y: cy, z: c ? c.h : 0, homeX: cx, homeY: cy, roamR: 48,
          selfAngle: 0, walkPhase: 0, timer: 0.8 + Math.random(), moving: true, dirX: -1, dirY: 0.5,
          speech: null
        });
      }

      // Pickups das Ferramentas próximos ao Spawn da Vila
      for (const [toolId, wx, wy] of [
        ['tool_axe', -295, 62],
        ['tool_pickaxe', -270, 62],
        ['tool_hoe', -245, 62]
      ]) {
        const baseZ = getHeightAt(wx, wy) || 0;
        toolPickups.push({ toolId, wx, wy, baseZ, inside: false });
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
      let r, g, b;
      if (shadowPct === 0) {
        r = rgb[0] + delta; r = r < 0 ? 0 : (r > 255 ? 255 : r);
        g = rgb[1] + delta; g = g < 0 ? 0 : (g > 255 ? 255 : g);
        b = rgb[2] + delta; b = b < 0 ? 0 : (b > 255 ? 255 : b);
      } else {
        const f = 1 - shadowPct * 0.01;
        r = Math.round((rgb[0] + delta) * f); r = r < 0 ? 0 : (r > 255 ? 255 : r);
        g = Math.round((rgb[1] + delta) * f); g = g < 0 ? 0 : (g > 255 ? 255 : g);
        b = Math.round((rgb[2] + delta) * f); b = b < 0 ? 0 : (b > 255 ? 255 : b);
      }
      if (IS_LE) return -16777216 | (b << 16) | (g << 8) | r;
      return (r << 24) | (g << 16) | (b << 8) | 255;
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

    const PAL_BRIDGE_SIDE = [118, 72, 42];
    const PAL_LILYPAD_SIDE = [22, 130, 58];
    const PAL_SAND_SIDE = [196, 168, 112];
    const PAL_MOSS = [[58, 143, 56], [41, 107, 39]];
    const PAL_EARTH = [[156, 102, 68], [128, 79, 50]];
    const PAL_ROCK = [[109, 118, 132], [86, 95, 108]];

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
              const isWaterfallDrop = (h - min8) > 4;
              const zFrom = isWaterfallDrop
                ? Math.max(Z_MIN, Math.min(h - 1, min8 - 2))
                : Math.max(Z_MIN, h - 1);
              for (let z = zFrom; z <= h; z++) markT(z, mx, my);
            }
            continue;
          }

          const zStart = min8 - 2 > Z_MIN ? min8 - 2 : Z_MIN;
          if (zStart <= h) {
            for (let z = zStart; z <= h; z++) {
              const si = z - Z_MIN;
              if (mx < tMinX[si]) tMinX[si] = mx;
              if (mx > tMaxX[si]) tMaxX[si] = mx;
              if (my < tMinY[si]) tMinY[si] = my;
              if (my > tMaxY[si]) tMaxY[si] = my;
            }
          }

          // Grama orgânica em moitas usando fbm2dFast(mx*0.14, my*0.14) + hash XOR sem listras
          if ((mat === MAT_GRASS || mat === MAT_PEAK) && !noGrassMask[idx] && max4 <= h) {
            let nh = ((mx * 73856093) ^ (my * 19349663)) >>> 0;
            nh ^= nh >>> 13;
            nh = Math.imul(nh, 1274126177) >>> 0;
            const fine01 = nh / 4294967295;
            if (fine01 > 0.18) {
              const clumpVal = valueNoise2d(mx * 0.14, my * 0.14) * 0.9 + fine01 * 0.42;
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

      // Passo 1b: Bounding boxes das pontes parabólicas em arco & píer
      for (const br of bridges) {
        const gx0 = Math.max(0, Math.floor(br.xMin / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.floor(br.xMax / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(br.yMin / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.floor(br.yMax / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const u = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)))
              : Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)));
            const v = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)))
              : Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)));
            const zDeck = Math.min(TERRAIN_Z_MAX - 1, getBridgeDeckZ(br, wx, wy));
            const zDeckStart = Math.max(Z_MIN, zDeck - 2);
            for (let z = zDeckStart; z <= zDeck; z++) markT(z, mx, my);

            const isPiling = br.isPier && ((Math.floor(wy - br.yMin) % 24) < 6) && (v <= 0.14 || v >= 0.86);
            const isAbutment = !br.isPier && (u <= 0.09 || u >= 0.91);
            if (isPiling || isAbutment) {
              for (let z = Z_MIN; z < zDeckStart; z++) markT(z, mx, my);
            }

            if (br.hasRailings && (v <= 0.08 || v >= 0.92)) {
              const alongIdx = br.axis === 'x' ? (mx - gx0) : (my - gy0);
              const isPost = (alongIdx % 7) === 0;
              const rStart = isPost ? zDeck + 1 : zDeck + 5;
              const rEnd = Math.min(TERRAIN_Z_MAX, zDeck + 6);
              for (let z = rStart; z <= rEnd; z++) markT(z, mx, my);
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

      // Pre-cache packed colors for flat shadow-free water & terrain
      const COL_BED = packRGBA(28, 66, 108, 255);
      const COL_FOAM_PLUNGE = packRGBA(236, 248, 255, 245);
      const COL_SHALLOW_A = packRGBA(72, 202, 245, 225);
      const COL_SHALLOW_B = packRGBA(95, 215, 250, 225);
      const COL_DEEP_A = packRGBA(56, 189, 248, 235);
      const COL_DEEP_B = packRGBA(42, 172, 236, 235);
      const COL_CALM_SHIMMER = packRGBA(186, 230, 253, 240);
      const COL_CALM_A = packRGBA(56, 189, 248, 235);
      const COL_CALM_B = packRGBA(72, 202, 245, 235);
      const COL_CALM_SUB = packRGBA(36, 168, 232, 235);
      const COL_DROP_FOAM = packRGBA(224, 242, 254, 255);
      const COL_DROP_TOP = packRGBA(56, 189, 248, 240);
      const COL_DROP_BODY = packRGBA(28, 158, 224, 255);

      // Passo 2: Preenche diretamente os buffers recortados (Tight-Crop)
      for (let my = 0; my < mh; my++) {
        const row = my * mw;
        const wySurf = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = 0; mx < mw; mx++) {
          const idx = row + mx;
          const h = Math.max(Z_MIN, Math.min(TERRAIN_Z_MAX - 1, hmap[idx]));
          const mat = matMap[idx];
          const sh = shadowMask[idx];
          const min8 = min8Cache[idx];
          const nHash = ((Math.imul(mx, 73856093)) ^ (Math.imul(my, 19349663))) >>> 0;
          const microTex = ((nHash & 7) - 3) * 2;

          if (mat === MAT_WATER) {
            if (h < 0) {
              const zEnd = Math.min(-4, h + 1);
              for (let z = Z_MIN; z <= zEnd; z++) {
                const si = z - Z_MIN;
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = COL_BED;
              }
              const siSurf = -2 - Z_MIN;
              const isShallow = h > -6;
              const wxSurf = (mx - HALF_GRID + 0.5) * VOX;
              const isPlungeFoam = (Math.hypot(wxSurf - 242, wySurf + 495) < 20) && ((nHash & 3) === 0);
              terrainBufs[siSurf][(my - tMinY[siSurf]) * tW[siSurf] + (mx - tMinX[siSurf])] = isPlungeFoam
                ? COL_FOAM_PLUNGE
                : (isShallow
                  ? ((nHash & 1) ? COL_SHALLOW_A : COL_SHALLOW_B)
                  : ((nHash & 3) === 0 ? COL_DEEP_A : COL_DEEP_B));
            } else {
              const isWaterfallDrop = (h - min8) > 4;
              if (!isWaterfallDrop) {
                const zFrom = Math.max(Z_MIN, h - 1);
                const shimmer = (nHash % 19) === 0;
                const topCol = shimmer ? COL_CALM_SHIMMER : ((nHash & 1) ? COL_CALM_A : COL_CALM_B);
                for (let z = zFrom; z <= h; z++) {
                  const si = z - Z_MIN;
                  terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = (z === h) ? topCol : COL_CALM_SUB;
                }
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
                    ? COL_DROP_FOAM
                    : (isTop ? COL_DROP_TOP : COL_DROP_BODY);
                }
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
                col = shadePack(PAL_BRIDGE_SIDE, sunShade, sh * 0.5);
              } else if (mat === MAT_LILYPAD) {
                col = shadePack(PAL_LILYPAD_SIDE, sunShade, 0);
              } else if (mat === MAT_SAND && d <= 5) {
                col = shadePack(PAL_SAND_SIDE, sunShade, sh * 0.5);
              } else if (d <= 3 && mat !== MAT_STONE) {
                col = shadePack(PAL_MOSS[nHash & 1], sunShade, sh * 0.6);
              } else if (d <= 12 && mat !== MAT_STONE) {
                const strata = (z & 2) ? 6 : -5;
                col = shadePack(PAL_EARTH[nHash & 1], sunShade + strata, sh * 0.4);
              } else {
                const strata = ((z >> 1) & 1) ? 9 : -8;
                col = shadePack(PAL_ROCK[nHash & 1], sunShade + strata, sh * 0.3);
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

      // Passo 2b: Rasteriza pontes parabólicas em arco & píer (rio visível embaixo)
      const COL_PLANK_A = packRGBA(185, 122, 74, 255);   // #B97A4A
      const COL_PLANK_B = packRGBA(166, 106, 62, 255);   // #A66A3E
      const COL_PLANK_SEAM = packRGBA(139, 83, 43, 255); // #8B532B
      const COL_DECK_UNDER = packRGBA(118, 72, 42, 255);
      const COL_RAIL_POST = packRGBA(124, 72, 37, 255);  // #7C4825
      const COL_RAIL_TOP = packRGBA(158, 98, 54, 255);   // #9E6236
      const COL_PIER_PILE_A = packRGBA(110, 68, 38, 255);
      const COL_PIER_PILE_B = packRGBA(92, 56, 30, 255);
      const COL_ABUT_A = packRGBA(126, 134, 146, 255);
      const COL_ABUT_B = packRGBA(104, 112, 124, 255);

      for (const br of bridges) {
        const gx0 = Math.max(0, Math.floor(br.xMin / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.floor(br.xMax / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(br.yMin / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.floor(br.yMax / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const u = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)))
              : Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)));
            const v = br.axis === 'x'
              ? Math.max(0, Math.min(1, (wy - br.yMin) / (br.yMax - br.yMin)))
              : Math.max(0, Math.min(1, (wx - br.xMin) / (br.xMax - br.xMin)));
            const zDeck = Math.min(TERRAIN_Z_MAX - 1, getBridgeDeckZ(br, wx, wy));
            const zDeckStart = Math.max(Z_MIN, zDeck - 2);
            const alongIdx = br.axis === 'x' ? (mx - gx0) : (my - gy0);
            const isSeam = (alongIdx % 3) === 0;
            const topPlankCol = isSeam ? COL_PLANK_SEAM : ((Math.floor(alongIdx / 3) & 1) ? COL_PLANK_B : COL_PLANK_A);

            for (let z = zDeckStart; z <= zDeck; z++) {
              const si = z - Z_MIN;
              terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = (z === zDeck) ? topPlankCol : COL_DECK_UNDER;
            }

            const isPiling = br.isPier && ((Math.floor(wy - br.yMin) % 24) < 6) && (v <= 0.14 || v >= 0.86);
            const isAbutment = !br.isPier && (u <= 0.09 || u >= 0.91);
            if (isPiling || isAbutment) {
              for (let z = Z_MIN; z < zDeckStart; z++) {
                const si = z - Z_MIN;
                const col = isPiling
                  ? (((mx + my + z) & 1) ? COL_PIER_PILE_A : COL_PIER_PILE_B)
                  : (((mx + my + z) & 1) ? COL_ABUT_A : COL_ABUT_B);
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = col;
              }
            }

            if (br.hasRailings && (v <= 0.08 || v >= 0.92)) {
              const isPost = (alongIdx % 7) === 0;
              const rStart = isPost ? zDeck + 1 : zDeck + 5;
              const rEnd = Math.min(TERRAIN_Z_MAX, zDeck + 6);
              for (let z = rStart; z <= rEnd; z++) {
                const si = z - Z_MIN;
                terrainBufs[si][(my - tMinY[si]) * tW[si] + (mx - tMinX[si])] = (z === zDeck + 6) ? COL_RAIL_TOP : COL_RAIL_POST;
              }
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
    const SPAWN_X = -330;
    const SPAWN_Y = 90;
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
      hurtTimer: 0,
      selfAngle: 0,
      walkPhase: 0,
      isWalking: false,
      idleTimer: 0,
      scale: 1.0,
      skinIdx: 0,
      hatIdx: 0,
      speech: { text: 'Miau! Vale Orgânico 1080×1080! 🐾', timer: 190 },
      lastSafeX: SPAWN_X,
      lastSafeY: SPAWN_Y,
      lastSafeZ: spawnH,
      maxJumpReached: spawnH,
      obstacleHint: 'ok',
      obstacleLabel: '✅ Caminho Livre'
    };

    const TRAVEL_SPOTS = [
      { wx: -330, wy: 90,   label: '🏡 Vila da Clareira' },
      { wx: -248, wy: 225,  label: '🏠 Cabana 2' },
      { wx: -780, wy: 90,   label: '🌻 Campos de Girassol' },
      { wx: -285, wy: 562,  label: '🏛️ Ruínas Orgânicas' },
      { wx: -180, wy: 684,  label: '🏖️ Praia Dourada' },
      { wx: -615, wy: 795,  label: '🗼 Farol Monumental' },
      { wx: -435, wy: -315, label: '⛩️ Jardim Zen & Torii' },
      { wx: 426,  wy: 228,  label: '🍄 Bosque Cogumelos' },
      { wx: 615,  wy: -66,  label: '🥾 Base da Montanha' },
      { wx: 480,  wy: -495, label: '🌸 Pico Sakura (Z=64)' }
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

    function waterSurfZ(cell) {
      return cell.h < 0 ? -2 : cell.h;
    }

    function evaluateSupport(wx, wy, currentZ, onGround) {
      const r = onGround ? 2.4 : 3.2;
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

      const r = 2.6;
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
          if (isPointInPropCollider(nx, ny, sc, 3.0)) {
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
        if (d < pc.r + 1.2 && d <= curD + 0.05 && catZ < pc.topZ - 2.0 && catZ >= pc.baseZ - 4.0) {
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
        if (cat.groundZ < sc.baseZ + sc.colH - 1.5 && isPointInPropCollider(probeX, probeY, sc, 3.2)) {
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

    // =========================================================================
    // 8B. FLUIDOS 2.5D: WINDFIELD + WATERFLOW (DRAIN SINK) + WAVEBUFFER
    // =========================================================================
    let fluidTime = 0;
    const windImpulses = [];
    function injectWindImpulse(wx, wy, vx, vy, r = 42, life = 0.75) {
      if (windImpulses.length >= 16) windImpulses.shift();
      windImpulses.push({ wx, wy, vx, vy, r, life, maxLife: life });
    }

    function sampleWind(wx, wy, t = fluidTime) {
      const gust = Math.sin((wx * 0.009 + wy * 0.006) - t * 2.1) * 0.55 + 0.55;
      const turb = fbm2dFast(wx * 0.008 - t * 0.25, wy * 0.008 + t * 0.14) * 0.45;
      let vx = 0.72 + gust * 0.52 + turb * 0.35;
      let vy = 0.34 + gust * 0.24 - turb * 0.25;

      const h = getHeightAt(wx, wy) || 0;
      const hL = getHeightAt(wx - 4, wy) ?? h;
      const hR = getHeightAt(wx + 4, wy) ?? h;
      const hU = getHeightAt(wx, wy - 4) ?? h;
      const hD = getHeightAt(wx, wy + 4) ?? h;
      const altBoost = 1 + Math.max(0, h) / 75;
      const windDotGrad = (hR - hL) * vx + (hD - hU) * vy;
      const shelter = windDotGrad < -6 ? 0.38 : 1.0;
      vx *= altBoost * shelter;
      vy *= altBoost * shelter;

      for (let i = 0; i < windImpulses.length; i++) {
        const imp = windImpulses[i];
        const dx = wx - imp.wx;
        const dy = wy - imp.wy;
        const d2 = dx * dx + dy * dy;
        const r2 = imp.r * imp.r;
        if (d2 < r2 * 6) {
          const w = Math.exp(-d2 / r2) * (imp.life / imp.maxLife);
          vx += imp.vx * w;
          vy += imp.vy * w;
        }
      }
      return { wx: vx, wy: vy, mag: Math.hypot(vx, vy) };
    }

    function sampleWaterFlow(wx, wy) {
      const c = getCellAt(wx, wy);
      if (!c || c.mat !== MAT_WATER) return { vx: 0, vy: 0, speed: 0 };

      let drainFactor = 1.0;
      if (wy >= 740) {
        const t = Math.max(0, Math.min(1, (wy - 740) / 220));
        drainFactor = 1 - t * t * (3 - 2 * t);
        if (drainFactor <= 0.001) return { vx: 0, vy: 0, speed: 0 };
      }

      if (wx < -450 && wy < -420 && c.h > 5) {
        const dx = -690 - wx;
        const dy = -585 - wy;
        const dist = Math.hypot(dx, dy);
        if (dist < 1) return { vx: 0, vy: 0, speed: 0 };
        const rad = Math.min(1, dist / 48);
        const speedScale = 7.5 * rad * rad;
        if (speedScale < 0.02) return { vx: 0, vy: 0, speed: 0 };
        const nx = dx / dist, ny = dy / dist;
        const vx = (-ny * 0.78 + nx * 0.35) * speedScale;
        const vy = (nx * 0.78 + ny * 0.35) * speedScale;
        const speed = Math.hypot(vx, vy);
        if (speed < 0.02) return { vx: 0, vy: 0, speed: 0 };
        return { vx, vy, speed };
      }

      if (wx >= 130 && wx <= 280 && wy >= -540 && wy <= -450) {
        const vx = -34 * drainFactor;
        const vy = 4 * drainFactor;
        return { vx, vy, speed: Math.hypot(vx, vy) };
      }

      let bestD2 = Infinity;
      let bestTx = 0, bestTy = 1;
      for (let i = 0; i < RIVER_SEGMENTS.length; i++) {
        const seg = RIVER_SEGMENTS[i];
        const t = seg.len2 > 0
          ? Math.max(0, Math.min(1, ((wx - seg.ax) * seg.dx + (wy - seg.ay) * seg.dy) / seg.len2))
          : 0;
        const px = seg.ax + seg.dx * t;
        const py = seg.ay + seg.dy * t;
        const d2 = (wx - px) * (wx - px) + (wy - py) * (wy - py);
        if (d2 < bestD2) {
          bestD2 = d2;
          bestTx = seg.tx;
          bestTy = seg.ty;
        }
      }
      const speed = 26 * drainFactor;
      return { vx: bestTx * speed, vy: bestTy * speed, speed };
    }

    const floatingItems = [];
    const PETAL_COLORS = ['#FBCFE8', '#E0F2FE', '#FEF08A'];
    let floatingSpawnAccum = 0;

    function spawnFloatingPetal(wx, wy, color = null, z = -2) {
      if (floatingItems.length >= 48) return;
      floatingItems.push({
        x: wx,
        y: wy,
        z,
        life: 1.0,
        phase: Math.random() * Math.PI * 2,
        color: color || PETAL_COLORS[Math.floor(Math.random() * PETAL_COLORS.length)]
      });
    }

    const WAVE_W = 120, WAVE_H = 80, WAVE_CELL = 6;
    let waveCurr = new Float32Array(WAVE_W * WAVE_H);
    let wavePrev = new Float32Array(WAVE_W * WAVE_H);
    let waveTmp = new Float32Array(WAVE_W * WAVE_H);
    let waveOriginX = Math.floor(camX / WAVE_CELL) * WAVE_CELL - (WAVE_W * WAVE_CELL) * 0.5;
    let waveOriginY = Math.floor(camY / WAVE_CELL) * WAVE_CELL - (WAVE_H * WAVE_CELL) * 0.5;
    let waveAccum = 0;

    function isWaterFast(wx, wy) {
      const mx = Math.floor(wx / VOX + HALF_GRID);
      const my = Math.floor(wy / VOX + HALF_GRID);
      if (mx < 0 || my < 0 || mx >= mw || my >= mh) return false;
      return matMap[my * mw + mx] === MAT_WATER;
    }

    function syncWaveOrigin() {
      const targetOX = Math.floor(camX / WAVE_CELL) * WAVE_CELL - (WAVE_W * WAVE_CELL) * 0.5;
      const targetOY = Math.floor(camY / WAVE_CELL) * WAVE_CELL - (WAVE_H * WAVE_CELL) * 0.5;
      const shiftX = Math.round((targetOX - waveOriginX) / WAVE_CELL);
      const shiftY = Math.round((targetOY - waveOriginY) / WAVE_CELL);
      if (shiftX === 0 && shiftY === 0) return;

      if (Math.abs(shiftX) >= WAVE_W || Math.abs(shiftY) >= WAVE_H) {
        waveCurr.fill(0);
        wavePrev.fill(0);
        waveOriginX = targetOX;
        waveOriginY = targetOY;
        return;
      }

      const xStart = Math.max(0, -shiftX);
      const xEnd = Math.min(WAVE_W, WAVE_W - shiftX);
      const yStart = Math.max(0, -shiftY);
      const yEnd = Math.min(WAVE_H, WAVE_H - shiftY);

      waveTmp.fill(0);
      for (let dy = yStart; dy < yEnd; dy++) {
        const srcRow = (dy + shiftY) * WAVE_W;
        const dstRow = dy * WAVE_W;
        for (let dx = xStart; dx < xEnd; dx++) {
          waveTmp[dstRow + dx] = waveCurr[srcRow + dx + shiftX];
        }
      }
      waveCurr.set(waveTmp);

      waveTmp.fill(0);
      for (let dy = yStart; dy < yEnd; dy++) {
        const srcRow = (dy + shiftY) * WAVE_W;
        const dstRow = dy * WAVE_W;
        for (let dx = xStart; dx < xEnd; dx++) {
          waveTmp[dstRow + dx] = wavePrev[srcRow + dx + shiftX];
        }
      }
      wavePrev.set(waveTmp);

      waveOriginX = targetOX;
      waveOriginY = targetOY;
    }

    function injectWaterRipple(wx, wy, strength = 1.0, radiusCells = 2) {
      const cx = Math.floor((wx - waveOriginX) / WAVE_CELL);
      const cy = Math.floor((wy - waveOriginY) / WAVE_CELL);
      if (cx < -radiusCells || cx >= WAVE_W + radiusCells || cy < -radiusCells || cy >= WAVE_H + radiusCells) return;
      const r2 = radiusCells * radiusCells + 0.25;
      const y0 = Math.max(1, cy - radiusCells);
      const y1 = Math.min(WAVE_H - 2, cy + radiusCells);
      const x0 = Math.max(1, cx - radiusCells);
      const x1 = Math.min(WAVE_W - 2, cx + radiusCells);
      for (let dy = y0; dy <= y1; dy++) {
        const cwy = waveOriginY + (dy + 0.5) * WAVE_CELL;
        for (let dx = x0; dx <= x1; dx++) {
          const d2 = (dx - cx) * (dx - cx) + (dy - cy) * (dy - cy);
          if (d2 > r2) continue;
          const cwx = waveOriginX + (dx + 0.5) * WAVE_CELL;
          if (!isWaterFast(cwx, cwy)) continue;
          const falloff = 1 - Math.sqrt(d2) / (radiusCells + 0.8);
          const idx = dy * WAVE_W + dx;
          waveCurr[idx] = Math.max(-4.0, Math.min(4.0, waveCurr[idx] + strength * falloff));
        }
      }
    }

    function stepWaveBuffer() {
      waveTmp.fill(0);
      for (let dy = 1; dy < WAVE_H - 1; dy++) {
        const wy = waveOriginY + (dy + 0.5) * WAVE_CELL;
        const my = Math.floor(wy / VOX + HALF_GRID);
        if (my < 0 || my >= mh) continue;
        const row = dy * WAVE_W;
        const isSpongeY = dy < 6 || dy >= WAVE_H - 6;
        for (let dx = 1; dx < WAVE_W - 1; dx++) {
          const idx = row + dx;
          const wx = waveOriginX + (dx + 0.5) * WAVE_CELL;
          const mx = Math.floor(wx / VOX + HALF_GRID);
          if (mx < 0 || mx >= mw || matMap[my * mw + mx] !== MAT_WATER) {
            waveTmp[idx] = 0;
            continue;
          }
          const isSponge = isSpongeY || dx < 6 || dx >= WAVE_W - 6;
          const damp = isSponge ? 0.72 : 0.955;
          let next = ((waveCurr[idx - 1] + waveCurr[idx + 1] + waveCurr[idx - WAVE_W] + waveCurr[idx + WAVE_W]) * 0.5 - wavePrev[idx]) * damp;
          if (Math.abs(next) < 0.008) next = 0;
          else if (next > 4.0) next = 4.0;
          else if (next < -4.0) next = -4.0;
          waveTmp[idx] = next;
        }
      }
      const oldPrev = wavePrev;
      wavePrev = waveCurr;
      waveCurr = waveTmp;
      waveTmp = oldPrev;
    }

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
      for (let i = 0; i < count; i++) {
        const ang = Math.atan2(biasDy, biasDx) + (Math.random() - 0.5) * 2.2;
        const hSpd = 24 + Math.random() * 34;
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
          life: 18.0
        });
      }
      if (debrisDrops.length > 64) {
        debrisDrops.splice(0, debrisDrops.length - 64);
      }
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

      if (d.hp <= 0) {
        d.chopped = true;
        if (bestTarget.solidCollider) bestTarget.solidCollider.disabled = true;
        if (bestTarget.platCollider) bestTarget.platCollider.disabled = true;

        let dirX = bestTarget.wx - cat.x;
        let dirY = bestTarget.wy - cat.y;
        const dLen = Math.hypot(dirX, dirY);
        if (dLen < 0.001) {
          dirX = fx;
          dirY = fy;
        } else {
          dirX /= dLen;
          dirY /= dLen;
        }

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
          destructStats.crumbledCount++;
        } else if (d.mode === 'trim') {
          bestTarget.destroyed = true;
          bestTarget.foliage = null;
          spawnParticles(bestTarget.wx, bestTarget.wy, bestTarget.wz + 6, 14, d.colors, 36, {
            isLeaf: true, grav: 32, vz: 18 + Math.random() * 14, life: 2.0
          });
          destructStats.trimmedCount++;
        }
      }
    }

    window.addEventListener('keydown', (e) => {
      const code = e.code;
      keys[code] = true;
      if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code)) {
        e.preventDefault();
      }
      if (code === 'Space') {
        cat.jumpBuffer = 0.13;
      } else if (code === 'KeyE') {
        triggerAction();
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
      isDraggingCam = true;
      dragStartX = e.clientX;
      pointerDownX = e.clientX;
      pointerDownY = e.clientY;
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
      if (isDraggingCam && Math.hypot(e.clientX - pointerDownX, e.clientY - pointerDownY) < 6) {
        triggerAction();
      }
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
    document.getElementById('btnTool').addEventListener('click', () => {
      const nextIdx = (TOOL_ORDER.indexOf(equippedTool) + 1) % TOOL_ORDER.length;
      equipTool(TOOL_ORDER[nextIdx]);
    });
    document.getElementById('btnAction').addEventListener('click', () => {
      triggerAction();
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

    function updatePhysics(dt) {
      fluidTime += dt;
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
      if (keys['KeyC']) targetTurn -= 2.2 * dt;
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
        injectWindImpulse(cat.x, cat.y, -Math.sin(cat.selfAngle) * 1.4, Math.cos(cat.selfAngle) * 1.4, 36, 0.5);
        const jc = getCellAt(cat.x, cat.y);
        if (jc && jc.mat === MAT_WATER) injectWaterRipple(cat.x, cat.y, 2.2, 2);
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

      if (Math.hypot(cat.x - 242, cat.y + 495) < 420 && Math.random() < dt * 14) {
        spawnParticles(
          242 + (Math.random() - 0.5) * 16,
          -495 + (Math.random() - 0.5) * 18,
          1, 1, ['#E0F2FE', '#FFFFFF', '#7DD3FC'], 16
        );
      }

      // Pétalas/itens flutuantes no poço da cachoeira e correnteza do rio até o dreno no mar sul
      floatingSpawnAccum += dt;
      const nearWaterfall = Math.hypot(camX - 232, camY + 495) < 480;
      const spawnInterval = nearWaterfall ? 0.28 : 0.65;
      if (floatingSpawnAccum >= spawnInterval) {
        floatingSpawnAccum = 0;
        if (floatingItems.length < 48) {
          spawnFloatingPetal(
            232 + (Math.random() - 0.5) * 14,
            -495 + (Math.random() - 0.5) * 14,
            null,
            -2
          );
        }
      }

      for (let i = floatingItems.length - 1; i >= 0; i--) {
        const f = floatingItems[i];
        const flow = sampleWaterFlow(f.x, f.y);
        f.x += flow.vx * dt;
        f.y += flow.vy * dt;
        const fc = getCellAt(f.x, f.y);
        if (fc && fc.mat === MAT_WATER) {
          f.z = waterSurfZ(fc);
        }
        if (f.y > 820 || flow.speed < 0.8 || !fc || fc.mat !== MAT_WATER) {
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
        if (pc && pc.mat === MAT_WATER && p.z <= waterSurfZ(pc) + 0.5) {
          const isSplashDrop = p.color === '#93C5FD' || p.color === '#FFFFFF' || p.color === '#7DD3FC';
          if (!isSplashDrop && floatingItems.length < 48) {
            spawnFloatingPetal(p.x, p.y, p.color, waterSurfZ(pc));
          }
          injectWaterRipple(p.x, p.y, isSplashDrop ? 0.55 : 0.35, 1);
          particles.splice(i, 1);
          continue;
        }
        if (p.isLeaf && pc && pc.mat !== MAT_WATER && p.z < pc.h + 0.4) {
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
            if (ic && ic.mat === MAT_WATER) {
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

      // Drops balísticos (toras & pedregulhos) + correnteza da água
      for (let i = debrisDrops.length - 1; i >= 0; i--) {
        const dr = debrisDrops[i];
        dr.life -= dt;
        if (dr.life <= 0) {
          debrisDrops.splice(i, 1);
          continue;
        }
        if (dr.inWater) {
          const flow = sampleWaterFlow(dr.x, dr.y);
          dr.vx = flow.vx;
          dr.vy = flow.vy;
          dr.x += dr.vx * dt;
          dr.y += dr.vy * dt;
          dr.selfAngle += dt * 0.6;
          const dc = getCellAt(dr.x, dr.y);
          if (dc && dc.mat === MAT_WATER) {
            dr.z = waterSurfZ(dc) + Math.sin(fluidTime * 3.5 + dr.x * 0.1) * 0.35;
          } else {
            dr.inWater = false;
          }
          if (!dc || dr.y > 860) dr.life = Math.min(dr.life, 0.5);
        } else {
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
          if (dc.mat === MAT_WATER && dr.z <= waterSurfZ(dc) + 0.5) {
            dr.inWater = true;
            dr.z = waterSurfZ(dc);
            dr.vz = 0;
            const flow = sampleWaterFlow(dr.x, dr.y);
            dr.vx = flow.vx;
            dr.vy = flow.vy;
            injectWaterRipple(dr.x, dr.y, 1.4, 2);
            spawnParticles(dr.x, dr.y, dr.z + 1, 6, ['#93C5FD', '#FFFFFF'], 24);
          } else if (dc.mat !== MAT_WATER && dr.z <= dc.h) {
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
      waveAccum += dt;
      while (waveAccum >= 1 / 30) {
        waveAccum -= 1 / 30;
        if (Math.hypot(camX - 242, camY + 495) < 420 && Math.random() < 0.45) {
          injectWaterRipple(242 + (Math.random() - 0.5) * 10, -495 + (Math.random() - 0.5) * 10, 0.65, 2);
        }
        stepWaveBuffer();
      }
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

    function stampModelSlice(targetCtx, model, sz, wx, wy, wz, selfAngle, scale, cosA, sinA, bendX = 0, bendY = 0) {
      if (bendX !== 0 || bendY !== 0) {
        const bf = model.count > 1 ? Math.pow(sz / (model.count - 1), 2) : 0;
        wx += bendX * bf;
        wy += bendY * bf;
      }
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
      const prevCamX = camX;
      const prevCamY = camY;
      if (shakeTimer > 0) {
        const sAmp = shakeMag * Math.min(1, shakeTimer / 0.16);
        camX += (Math.random() - 0.5) * 2 * sAmp;
        camY += (Math.random() - 0.5) * 2 * sAmp;
      }
      try {
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
      const animTime = animTick / 8;
      const camWind = sampleWind(camX, camY, fluidTime);
      const grassAmp = Math.min(1.6, 0.5 + camWind.mag * 0.55);
      const grassLean = camWind.wx * 0.35;
      const speechQueue = [];

      // 2. Bounding box visível no grid 1080×1080 (culling exato por viewport!)
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

      const minVisWx = (viewMinMx - HALF_GRID) * VOX - 72;
      const maxVisWx = (viewMaxMx - HALF_GRID) * VOX + 72;
      const minVisWy = (viewMinMy - HALF_GRID) * VOX - 72;
      const maxVisWy = (viewMaxMy - HALF_GRID) * VOX + 72;

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
        if (p.destroyed) continue;
        if (p.wx < minVisWx || p.wx > maxVisWx || p.wy < minVisWy || p.wy > maxVisWy) continue;
        const maxDrawZ = p.renderMaxSlice !== undefined
          ? Math.min(p.topZ, p.baseZ + Math.ceil(p.renderMaxSlice * p.scale))
          : p.topZ;
        const maxSliceIdx = p.renderMaxSlice !== undefined
          ? Math.min(p.model.count - 1, p.renderMaxSlice - 1)
          : (p.model.count - 1);
        const dp = (p.wx - camX) * sinA + (p.wy - camY) * cosA;
        activeDrawables.push({
          baseZ: p.baseZ,
          topZ: maxDrawZ,
          depth: dp,
          drawSlice: (z) => {
            const sz = Math.min(maxSliceIdx, Math.floor((z - p.baseZ) / p.scale));
            const flashOff = (p.destr && p.destr.hitFlash > 0) ? Math.sin(fluidTime * 75) * 1.4 : 0;
            stampModelSlice(entityCtx, p.model, sz, p.wx, p.wy, z, p.selfAngle, p.scale, cosA, sinA, (p.bx || 0) + flashOff, p.by || 0);
          }
        });
        if (maxDrawZ > maxEntityTopZ) maxEntityTopZ = maxDrawZ;
        if (p.isFire) {
          const fz = p.baseZ + (p.modelKey === 'stone_lantern' ? 20 : 8);
          if (fz > maxEntityTopZ) maxEntityTopZ = fz;
          if (!firesByZ.has(fz)) firesByZ.set(fz, []);
          firesByZ.get(fz).push(p);
        }
      }

      // Pickups das Ferramentas visíveis
      for (const pk of toolPickups) {
        if (pk.wx < minVisWx || pk.wx > maxVisWx || pk.wy < minVisWy || pk.wy > maxVisWy) continue;
        const tKey = TOOLS_META[pk.toolId].modelKey;
        const tModel = tKey ? propModels[tKey] : null;
        if (!tModel) continue;
        const tScale = 0.78;
        const bob = Math.sin(cat.idleTimer * 3.2 + pk.wx * 0.05) * 2.0;
        const pBaseZ = Math.round(pk.baseZ + 4 + bob);
        const pTopZ = pBaseZ + Math.ceil(tModel.count * tScale);
        const spinAngle = cat.idleTimer * 1.8 + pk.wx * 0.04;
        const dp = (pk.wx - camX) * sinA + (pk.wy - camY) * cosA;
        registerShadow(pk.wx, pk.wy, pk.baseZ, pBaseZ, 4.5, 2.8, 0.24);
        activeDrawables.push({
          baseZ: pBaseZ,
          topZ: pTopZ,
          depth: dp,
          drawSlice: (z) => {
            const sz = Math.min(tModel.count - 1, Math.floor((z - pBaseZ) / tScale));
            stampModelSlice(entityCtx, tModel, sz, pk.wx, pk.wy, z, spinAngle, tScale, cosA, sinA);
          }
        });
        if (pTopZ > maxEntityTopZ) maxEntityTopZ = pTopZ;
      }

      // Corpos em queda (Pêndulo Invertido 3D)
      for (const fb of fallingBodies) {
        const sinP = Math.sin(fb.phi);
        const cosP = Math.cos(fb.phi);
        for (let sz = fb.zCut; sz < fb.model.count; sz++) {
          const dz = (sz - fb.zCut) * fb.scale;
          const sx = fb.wx + dz * sinP * fb.dx;
          const sy = fb.wy + dz * sinP * fb.dy;
          const szWorld = Math.round(fb.baseZ + fb.zCut * fb.scale + dz * cosP);
          const dp = (sx - camX) * sinA + (sy - camY) * cosA;
          activeDrawables.push({
            baseZ: szWorld,
            topZ: szWorld + 1,
            depth: dp + 0.15,
            drawSlice: (z) => {
              stampModelSlice(entityCtx, fb.model, sz, sx, sy, z, fb.selfAngle, fb.scale, cosA, sinA);
            }
          });
          if (szWorld + 1 > maxEntityTopZ) maxEntityTopZ = szWorld + 1;
        }
      }

      // Drops balísticos (wood_log / stone_chunk)
      for (const dr of debrisDrops) {
        if (!dr.model) continue;
        if (dr.x < minVisWx || dr.x > maxVisWx || dr.y < minVisWy || dr.y > maxVisWy) continue;
        const dBaseZ = Math.round(dr.z);
        const dTopZ = dBaseZ + Math.ceil(dr.model.count * dr.scale);
        const dp = (dr.x - camX) * sinA + (dr.y - camY) * cosA;
        const gH = getHeightAt(dr.x, dr.y);
        if (gH !== null && !dr.inWater) {
          registerShadow(dr.x, dr.y, gH, dr.z, 3.8, 2.4, 0.22);
        }
        activeDrawables.push({
          baseZ: dBaseZ,
          topZ: dTopZ,
          depth: dp + 0.1,
          drawSlice: (z) => {
            const sz = Math.min(dr.model.count - 1, Math.floor((z - dBaseZ) / dr.scale));
            stampModelSlice(entityCtx, dr.model, sz, dr.x, dr.y, z, dr.selfAngle, dr.scale, cosA, sinA);
          }
        });
        if (dTopZ > maxEntityTopZ) maxEntityTopZ = dTopZ;
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

        const catBlinkHidden = cat.hurtTimer > 0 && (Math.floor((1.0 - cat.hurtTimer) * 6) % 2 === 0);
        const bob = inAir ? 0 : (cat.isWalking ? Math.abs(Math.sin(t * 2)) * 0.7 : Math.sin(cat.idleTimer * 2.4) * 0.35);
        if (!catBlinkHidden) {
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

          if (swingTimer > 0 && equippedTool !== 'none') {
            const tKey = TOOLS_META[equippedTool].modelKey;
            const tModel = tKey ? propModels[tKey] : null;
            if (tModel) {
              const prog = 1 - Math.max(0, Math.min(1, swingTimer / 0.22));
              const arcAngle = (prog - 0.5) * 2.1;
              const swAngle = cat.selfAngle + arcAngle;
              const fxC = -Math.sin(swAngle);
              const fyC = Math.cos(swAngle);
              const tx = cat.x + fxC * 10;
              const ty = cat.y + fyC * 10;
              const tScale = 0.68;
              const tBaseZ = Math.round(cat.z + 3 + Math.sin(prog * Math.PI) * 3);
              const tTopZ = tBaseZ + Math.ceil(tModel.count * tScale);
              const tDp = (tx - camX) * sinA + (ty - camY) * cosA;
              activeDrawables.push({
                baseZ: tBaseZ,
                topZ: tTopZ,
                depth: tDp + 0.65,
                drawSlice: (z) => {
                  const sz = Math.min(tModel.count - 1, Math.floor((z - tBaseZ) / tScale));
                  stampModelSlice(entityCtx, tModel, sz, tx, ty, z, swAngle, tScale, cosA, sinA);
                }
              });
              if (tTopZ > maxEntityTopZ) maxEntityTopZ = tTopZ;
            }
          }
        }

        if (cat.speech && cat.speech.timer > 0) {
          cat.speech.timer--;
          const sp = project(cat.x, cat.y, cat.z + 24);
          speechQueue.push({ lowX: sp.x, lowY: sp.y, text: cat.speech.text });
        }
      }

      // Ordenar uma única vez por profundidade para desenhar back-to-front em cada fatia z
      activeDrawables.sort((a, b) => a.depth - b.depth);

      // Bucket das partículas 3D por fatia Z para oclusão correta atrás de falésias
      const particlesByZ = new Map();
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        const pz = Math.max(Z_MIN, Math.min(maxEntityTopZ, Math.round(p.z)));
        if (!particlesByZ.has(pz)) particlesByZ.set(pz, []);
        particlesByZ.get(pz).push(p);
      }

      // 4. Loop Unificado Slice-by-Slice (Terreno + Destination-Out + Grama + Partículas + Entidades)
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

          // WaveBuffer (cristas/cavas) + FloatingItems respeitando oclusão 3D nas fatias z=-2 e z=13
          if (z === -2 || z === 13) {
            for (let dy = 1; dy < WAVE_H - 1; dy++) {
              const cwy = waveOriginY + (dy + 0.5) * WAVE_CELL;
              if (cwy < minVisWy || cwy > maxVisWy) continue;
              const row = dy * WAVE_W;
              for (let dx = 1; dx < WAVE_W - 1; dx++) {
                const val = waveCurr[row + dx];
                if (Math.abs(val) < 0.14) continue;
                const cwx = waveOriginX + (dx + 0.5) * WAVE_CELL;
                if (cwx < minVisWx || cwx > maxVisWx) continue;
                const mx = Math.floor(cwx / VOX + HALF_GRID);
                const my = Math.floor(cwy / VOX + HALF_GRID);
                if (mx < 0 || mx >= mw || my < 0 || my >= mh) continue;
                const wIdx = my * mw + mx;
                if (matMap[wIdx] !== MAT_WATER) continue;
                const surfZ = hmap[wIdx] < 0 ? -2 : hmap[wIdx];
                if (surfZ !== z) continue;
                const wp = project(cwx, cwy, z + 0.2);
                const px = Math.round(wp.x);
                const py = Math.round(wp.y);
                if (px < -4 || px >= LOW_W + 4 || py < -4 || py >= LOW_H + 4) continue;
                if (val > 0) {
                  lowCtx.fillStyle = val > 0.7 ? 'rgba(240, 249, 255, 0.72)' : 'rgba(224, 242, 254, 0.45)';
                } else {
                  lowCtx.fillStyle = val < -0.7 ? 'rgba(24, 118, 186, 0.52)' : 'rgba(36, 148, 214, 0.34)';
                }
                lowCtx.fillRect(px - 1, py, 3, 1);
              }
            }

            for (let i = 0; i < floatingItems.length; i++) {
              const f = floatingItems[i];
              if (Math.round(f.z) !== z) continue;
              if (f.x < minVisWx || f.x > maxVisWx || f.y < minVisWy || f.y > maxVisWy) continue;
              const bob = Math.sin(fluidTime * 3.2 + f.phase) * 0.25;
              const fp = project(f.x, f.y, z + 0.3 + bob);
              const px = Math.round(fp.x);
              const py = Math.round(fp.y);
              if (px < -4 || px >= LOW_W + 4 || py < -4 || py >= LOW_H + 4) continue;
              lowCtx.fillStyle = f.color;
              lowCtx.fillRect(px, py, 2, 2);
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
          const grassOff = Math.round(Math.sin(animTime * 4.5 + (z * 0.7)) * grassAmp + grassLean);
          drawBoundedSliceTo(lowCtx, gSlice, z, viewMinMx, viewMinMy, viewMaxMx, viewMaxMy, grassOff);
        }

        // 4c-bis. Partículas 3D na fatia Z (ocluídas por falésias mais altas!)
        const pList = particlesByZ.get(z);
        if (pList) {
          for (let i = 0; i < pList.length; i++) {
            const p = pList[i];
            const pp = project(p.x, p.y, p.z);
            lowCtx.fillStyle = p.color;
            lowCtx.fillRect(Math.round(pp.x), Math.round(pp.y), p.size, p.size);
          }
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

      // 6. Upscale 1:1 quadrado Nearest-Neighbor para o canvas principal + Balões Hi-Res
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, viewW, viewH);
      ctx.drawImage(lowCanvas, 0, 0, LOW_W * pixelScale, LOW_H * pixelScale);

      drawSpeechOverlaysHiRes(speechQueue);
      } finally {
        camX = prevCamX;
        camY = prevCamY;
      }
    }

    // =========================================================================
    // 11. MINIMAPA TOPOGRÁFICO ORGÂNICO (1080×1080 passo 9 -> 120×120)
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
        const my = gy * 9;
        for (let gx = 0; gx < MM_RES; gx++) {
          const mx = gx * 9;
          const idx = my * mw + mx;
          const h = hmap[idx];
          const mat = matMap[idx];
          const hL = mx >= 9 ? hmap[my * mw + (mx - 9)] : h;
          const hU = my >= 9 ? hmap[(my - 9) * mw + mx] : h;
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
      const toMm = (w) => (w / VOX + HALF_GRID) * (MM_RES / mw);
      mmBaseCtx.fillStyle = '#B97A4A';
      for (const br of bridges) {
        const x0 = Math.floor(toMm(br.xMin));
        const y0 = Math.floor(toMm(br.yMin));
        const bw = Math.max(2, Math.ceil(toMm(br.xMax) - x0));
        const bh = Math.max(2, Math.ceil(toMm(br.yMax) - y0));
        mmBaseCtx.fillRect(x0, y0, bw, bh);
      }
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
        hurtTimer: cat.hurtTimer,
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
      getBridgeAt: (wx, wy) => getBridgeAt(wx, wy),
      getBridgeDeckZ: (br, wx, wy) => getBridgeDeckZ(br, wx, wy),
      getBridges: () => bridges,
      getFishes: () => fishes,
      getRuinsCoords: () => ({
        approachSouth: { wx: -285, wy: 562, z: getHeightAt(-285, 562) },
        monoliths: [
          { name: 'A', wx: -420, wy: 495, halfW: 30, halfD: 26, targetZ: 6,  topZ: getHeightAt(-420, 495), southApproach: { wx: -420, wy: 562, z: getHeightAt(-420, 562) } },
          { name: 'B', wx: -285, wy: 495, halfW: 30, halfD: 26, targetZ: 16, topZ: getHeightAt(-285, 495), southApproach: { wx: -285, wy: 562, z: getHeightAt(-285, 562) } },
          { name: 'C', wx: -150, wy: 495, halfW: 30, halfD: 26, targetZ: 32, topZ: getHeightAt(-150, 495), southApproach: { wx: -150, wy: 562, z: getHeightAt(-150, 562) } },
          { name: 'D', wx: -15,  wy: 495, halfW: 30, halfD: 26, targetZ: 48, topZ: getHeightAt(-15,  495), southApproach: { wx: -15,  wy: 562, z: getHeightAt(-15,  562) } }
        ]
      }),
      setTurn: (rad) => { turn = rad; targetTurn = rad; },
      triggerJump: () => { cat.jumpBuffer = 0.14; },
      speak: (text) => { catSpeak(text, 240); },
      sampleWind: (wx, wy, t = fluidTime) => sampleWind(wx, wy, t),
      sampleWaterFlow: (wx, wy) => sampleWaterFlow(wx, wy),
      injectWaterRipple: (wx, wy, strength = 1.0, radiusCells = 2) => injectWaterRipple(wx, wy, strength, radiusCells),
      injectWindImpulse: (wx, wy, vx, vy, r = 42, life = 0.75) => injectWindImpulse(wx, wy, vx, vy, r, life),
      getFluidStats: () => ({
        floatingCount: floatingItems.length,
        activeImpulses: windImpulses.length,
        windAtCat: sampleWind(cat.x, cat.y, fluidTime)
      }),
      getWaveStats: () => {
        let sum = 0, max = 0, nan = 0;
        for (let i = 0; i < waveCurr.length; i++) {
          const v = waveCurr[i];
          if (Number.isNaN(v)) nan++;
          const a = Math.abs(v);
          sum += a;
          if (a > max) max = a;
        }
        return { sum, max, nan };
      },
      stepFluidForTest: (dt) => {
        syncWaveOrigin();
        injectWaterRipple(cat.x, cat.y, 0, 0);
        updatePhysics(dt);
      },
      getPropsByType: (key) => props.filter(p => p.modelKey === key).map(p => ({
        id: p.id, modelKey: p.modelKey, wx: p.wx, wy: p.wy, wz: p.wz, topZ: p.topZ,
        destroyed: !!p.destroyed,
        renderMaxSlice: p.renderMaxSlice !== undefined ? p.renderMaxSlice : null,
        destr: p.destr ? { hp: p.destr.hp, maxHp: p.destr.maxHp, chopped: p.destr.chopped, mode: p.destr.mode } : null
      })),
      getFoliageState: () => foliageProps.filter(p => !p.destroyed && p.foliage).map(p => ({
        id: p.id, key: p.modelKey, wx: p.wx, wy: p.wy,
        bx: +(p.bx || 0).toFixed(3), by: +(p.by || 0).toFixed(3),
        r: p.foliage.pushRadius
      })),
      triggerAction: () => triggerAction(),
      equipTool: (toolId, quiet = true) => equipTool(toolId, quiet),
      getDestructionStats: () => ({
        ...destructStats,
        fallingCount: fallingBodies.length,
        dropCount: debrisDrops.length,
        equippedTool
      })
    };
  </script>
</body>
</html>
"""

html_out = (
    HTML_TEMPLATE
    .replace('__CAT_SLICES__', json.dumps(cat_slices, separators=(',', ':')))
    .replace('__HATS_PACK__', json.dumps(hats_pack, separators=(',', ':')))
    .replace('__CHICKEN_DATA__', json.dumps(chicken_data, separators=(',', ':')))
    .replace('__PROPS_PACK__', json.dumps(rle_compress_props(props_pack), separators=(',', ':')))
)

out_path = os.path.join(EXAMPLES_DIR, 'terrain-world.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_out)

print(f'SUCCESS: Generated {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)')
