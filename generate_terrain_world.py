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
  <title>Vale Felino 3D v2 — Mapa 56×56, Grama Voxel & Pulo 2×H</title>
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
      width: 112px;
      height: 112px;
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
          <span class="fish-badge" id="fishCounter">🐟 0 / 16</span>
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
      <canvas id="minimapCanvas" width="112" height="112"></canvas>
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
    // 4. MAPA AMPLIADO 56×56 TILES (8 Biomas Conectados + Relevo Calibrado)
    // =========================================================================
    const GRID_SIZE = 56;
    const TILE = 16;
    const HALF_GRID = GRID_SIZE / 2; // 28
    const WORLD_MIN = -HALF_GRID * TILE; // -448
    const WORLD_MAX = HALF_GRID * TILE;  // +448
    const SKIRT_BOTTOM = -22;

    const CAT_HEIGHT = 16;
    const AUTO_STEP_MAX = 6.5; // ~0.4 * CAT_HEIGHT
    const GRAVITY = 1200;
    const JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0); // Pico ~35u (vence 32u = 2xH, bloqueia em 48u = 3xH)

    const BIOME_NAMES = {
      vila:       'Vila da Clareira',
      girassol:   'Campos de Girassol',
      ruinas:     'Ruínas Antigas',
      praia:      'Praia & Farol',
      zen:        'Jardim Zen & Torii',
      rio:        'Rio Cristalino',
      cogumelos:  'Bosque Cogumelos',
      montanha:   'Pico Sakura'
    };

    const grid = [];
    function initTerrainGrid() {
      for (let gy = 0; gy < GRID_SIZE; gy++) {
        const row = [];
        for (let gx = 0; gx < GRID_SIZE; gx++) {
          row.push({ gx, gy, h: 0, type: 'grass', biomeKey: 'vila', biome: BIOME_NAMES.vila });
        }
        grid.push(row);
      }

      const setTile = (gx, gy, h, type = null, biomeKey = null) => {
        if (gx < 0 || gy < 0 || gx >= GRID_SIZE || gy >= GRID_SIZE) return;
        grid[gy][gx].h = h;
        if (type) grid[gy][gx].type = type;
        if (biomeKey) {
          grid[gy][gx].biomeKey = biomeKey;
          grid[gy][gx].biome = BIOME_NAMES[biomeKey] || biomeKey;
        }
      };

      const fillRect = (x0, y0, x1, y1, h, type = null, biomeKey = null) => {
        for (let y = y0; y <= y1; y++) {
          for (let x = x0; x <= x1; x++) {
            setTile(x, y, h, type, biomeKey);
          }
        }
      };

      // Moldura natural arborizada (Oeste, Norte e Leste; Sul fica aberto para o mar da Praia!)
      fillRect(0, 0, 55, 1, 24, 'grass', 'zen');
      fillRect(0, 0, 1, 47, 24, 'grass', 'girassol');
      fillRect(54, 0, 55, 47, 24, 'grass', 'cogumelos');
      fillRect(32, 0, 55, 1, 24, 'grass', 'montanha');

      // 1. VILA DA CLAREIRA & CABANA (Spawn em gx=19, gy=29)
      fillRect(13, 21, 25, 35, 0, 'grass', 'vila');
      // Trilhas limpas ligando Vila -> Ponte Leste, Girassóis Oeste, Ruínas Sul, Jardim Zen Norte
      fillRect(19, 27, 25, 29, 0, 'path', 'vila');
      fillRect(13, 25, 19, 26, 0, 'path', 'vila');
      fillRect(18, 29, 19, 36, 0, 'path', 'vila');
      fillRect(16, 18, 17, 25, 0, 'path', 'vila');
      // Rampas suaves de demonstração Z=6 (<= 0.4H, sobe andando!)
      fillRect(21, 24, 23, 25, 6, 'grass', 'vila');
      fillRect(14, 21, 15, 22, 6, 'path', 'vila');

      // 2. CAMPOS DE GIRASSOL & FARDOS (Oeste: gx=2..12, gy=18..34)
      fillRect(2, 18, 12, 34, 0, 'grass', 'girassol');
      fillRect(9, 25, 12, 26, 0, 'path', 'girassol');
      fillRect(3, 19, 11, 24, 6, 'grass', 'girassol');
      fillRect(4, 19, 8, 22, 16, 'grass', 'girassol');
      // Segunda colina dourada ao sul dos girassóis
      fillRect(3, 29, 8, 33, 6, 'grass', 'girassol');

      // 3. CIRCUITO DAS RUÍNAS ANTIGAS (Centro-Sul: gx=6..21, gy=36..44)
      fillRect(6, 36, 21, 44, 0, 'grass', 'ruinas');
      // Pátio plano Z=0 em volta de todo o circuito (gy=37..38 e gy=41..43 livres!)
      fillRect(7, 37, 19, 43, 0, 'path', 'ruinas');
      // 4 Plataformas de calibração 2x2 lado a lado em gy=39..40:
      fillRect(8,  39, 9,  40, 6,  'stone', 'ruinas'); // 0.4H andando
      fillRect(10, 39, 11, 40, 16, 'stone', 'ruinas'); // 1.0H pulo fácil
      fillRect(12, 39, 13, 40, 32, 'stone', 'ruinas'); // 2.0H pulo máx direto do chão!
      fillRect(14, 39, 15, 40, 48, 'stone', 'ruinas'); // 3.0H intransponível do chão!
      // Pedestais de pilares laterais (afastados das rotas)
      fillRect(6, 37, 6, 37, 16, 'stone', 'ruinas');
      fillRect(17, 37, 17, 37, 16, 'stone', 'ruinas');
      // Caminho conectando Ruínas até a Praia Dourada
      fillRect(18, 43, 19, 46, 0, 'path', 'ruinas');

      // 4. PRAIA DOURADA, PÍER, VITÓRIAS-RÉGIAS & FAROL (Sul: gx=0..55, gy=45..55)
      fillRect(2, 45, 53, 48, 0, 'sand', 'praia');
      fillRect(0, 49, 55, 55, -8, 'water', 'praia');
      // Caminho arenoso ligando Rio e Píer
      fillRect(18, 45, 19, 47, 0, 'sand', 'praia');
      // Píer de madeira avançando mar adentro (Z=2)
      fillRect(18, 48, 19, 52, 2, 'bridge', 'praia');
      // Vitórias-régias escaláveis (Z=0 sobre a água!) para ir pulando pelo mar até a ilhota leste
      setTile(21, 50, 0, 'lilypad', 'praia');
      setTile(23, 51, 0, 'lilypad', 'praia');
      setTile(25, 50, 0, 'lilypad', 'praia');
      setTile(27, 51, 0, 'lilypad', 'praia');
      setTile(29, 50, 0, 'lilypad', 'praia');
      // Ilhota arenosa leste do mar sul com tesouro!
      fillRect(31, 49, 34, 52, 0, 'sand', 'praia');

      // Promontório rochoso do Farol (Sudoeste marítimo: gx=5..11, gy=48..53)
      fillRect(11, 47, 12, 49, 6, 'sand', 'praia');   // Rampa de acesso andando!
      fillRect(5,  48, 10, 53, 16, 'stone', 'praia'); // Platô do Farol (Z=16)

      // 5. JARDIM ZEN & PORTAL TORII (Noroeste: gx=3..24, gy=2..17)
      fillRect(3, 3, 24, 17, 16, 'grass', 'zen');
      // Acesso por degraus largos pela vila (Z=6 em gx=15..18, gy=17..18 -> Z=16)
      fillRect(15, 17, 18, 18, 6, 'path', 'zen');
      // Alameda Zen passando por baixo do Portal Torii (gx=16..17, gy=8..16)
      fillRect(15, 7, 17, 16, 16, 'path', 'zen');
      // Laguinho Zen contemplativo em Z=10
      fillRect(8, 9, 11, 12, 10, 'water', 'zen');
      // Segundo terraço Zen (Z=32) e Mirante Oeste (Z=48)
      fillRect(3, 3, 11, 7, 32, 'grass', 'zen');
      fillRect(3, 3, 6, 5, 48, 'stone', 'zen');

      // 6. RIO CRISTALINO & PONTES (Norte-Sul: gx=26..29, gy=2..48)
      for (let y = 2; y <= 48; y++) {
        for (let x = 26; x <= 29; x++) {
          setTile(x, y, -8, 'water', 'rio');
        }
      }
      // Margens arenosas ao longo do rio baixo
      for (let y = 20; y <= 44; y++) {
        if (grid[y][25].h === 0) grid[y][25].type = 'sand';
        if (grid[y][30].h === 0) grid[y][30].type = 'sand';
      }
      // Ponte Central de Madeira (Z=2)
      fillRect(25, 28, 30, 29, 2, 'bridge', 'rio');
      // Ponte Norte de Pedra ligando Jardim Zen (Z=16) ao Contraforte da Montanha (Z=16)
      fillRect(24, 14, 31, 15, 16, 'bridge', 'rio');
      // Pedras de travessia ao sul em gy=39 (Z=2, pulo sobre a água!)
      setTile(26, 39, 2, 'stone', 'rio');
      setTile(28, 39, 2, 'stone', 'rio');

      // 7. BOSQUE ENCANTADO DOS COGUMELOS (Sudeste: gx=31..53, gy=27..45)
      fillRect(31, 27, 53, 44, 0, 'grass', 'cogumelos');
      fillRect(31, 28, 36, 30, 0, 'path', 'cogumelos');
      // Clareiras elevadas dentro do bosque
      fillRect(39, 32, 41, 35, 12, 'stone', 'cogumelos'); // Apoio Cogumelo #2 (topo Z=28!)
      fillRect(42, 35, 45, 38, 24, 'grass', 'cogumelos'); // Apoio Cogumelo #3 (topo Z=40!)
      fillRect(46, 38, 52, 43, 6,  'grass', 'cogumelos');
      fillRect(48, 39, 51, 42, 16, 'grass', 'cogumelos');

      // 8. MONTANHA DO PICO SAKURA & CACHOEIRA DUPLA (Nordeste: gx=31..53, gy=2..26)
      fillRect(31, 3, 53, 26, 0, 'grass', 'montanha');
      // Contraforte Oeste Z=16 onde chega a Ponte Norte (gx=31..33, gy=14..16)
      fillRect(31, 14, 33, 17, 16, 'stone', 'montanha');

      // Maciço do Paredão Íngreme (Oeste/Sul da Montanha: Z=48..80 intransponível direto!)
      fillRect(32, 8, 47, 20, 48, 'stone', 'montanha');
      fillRect(34, 7, 45, 18, 64, 'stone', 'montanha');

      // Cachoeira Dupla despejando no Rio (gy=10..11 e gy=18..19)
      fillRect(30, 10, 34, 11, 64, 'water', 'montanha');
      fillRect(29, 10, 29, 11, 32, 'water', 'rio');
      fillRect(30, 18, 33, 19, 48, 'water', 'montanha');
      fillRect(29, 18, 29, 19, 20, 'water', 'rio');

      // TRILHA EM ESPIRAL AMPLA (3 tiles de largura, 100% LIVRE DE OBSTÁCULOS!)
      // Degraus regulares de +16u (<= 2.0H): 0 -> 16 -> 32 -> 48 -> 64 -> 80 -> 96!
      fillRect(45, 23, 51, 25, 16, 'path', 'montanha'); // Patamar 1 (Z=16)
      fillRect(48, 18, 52, 22, 32, 'path', 'montanha'); // Patamar 2 (Z=32)
      fillRect(48, 12, 52, 17, 48, 'path', 'montanha'); // Patamar 3 (Z=48)
      fillRect(46, 5,  52, 11, 64, 'path', 'montanha'); // Patamar 4 (Z=64)
      fillRect(39, 3,  45, 7,  80, 'path', 'montanha'); // Patamar 5 (Z=80)

      // CUME MONUMENTAL DO PICO SAKURA (Z=96!)
      fillRect(35, 8, 43, 14, 96, 'peak', 'montanha');
      // Degrau de entrada Z=80 conectando Patamar 5 ao Cume
      fillRect(38, 6, 42, 7, 80, 'stone', 'montanha');
    }
    initTerrainGrid();

    function getTile(gx, gy) {
      if (gx < 0 || gy < 0 || gx >= GRID_SIZE || gy >= GRID_SIZE) return null;
      return grid[gy][gx];
    }

    function worldToTileCoords(wx, wy) {
      return {
        gx: Math.floor(wx / TILE + HALF_GRID),
        gy: Math.floor(wy / TILE + HALF_GRID)
      };
    }

    function tileCenter(gx, gy) {
      return {
        wx: (gx - HALF_GRID + 0.5) * TILE,
        wy: (gy - HALF_GRID + 0.5) * TILE
      };
    }

    // =========================================================================
    // 5. SISTEMA DE COLISÃO UNIFICADO PARA PROPS (4 Modos) & ANTI-BLOQUEIO
    // =========================================================================
    // Modos:
    // - 'solid': cilindro bloqueante até (baseZ + h)
    // - 'box': caixa retangular bloqueante até (baseZ + h) para edificações/barcos
    // - 'platform': bloqueia abaixo do topo e fornece apoio escalável em (baseZ + h)
    // - 'arch': 2 pilares laterais deixando vão central 100% passável!
    // - 'none': atravessável
    const PROP_COLLIDER_META = {
      pine_tree:       { mode: 'solid',    r: 5.0,  h: 48 },
      sakura_oak:      { mode: 'solid',    r: 9.5,  h: 68 },
      cozy_cabin:      { mode: 'box',      halfW: 23.5, halfD: 20.5, h: 54 },
      lighthouse:      { mode: 'solid',    r: 14.5, h: 84 },
      campfire:        { mode: 'solid',    r: 5.2,  h: 9 },
      wood_sign:       { mode: 'solid',    r: 3.6,  h: 14 },
      ruin_pillar:     { mode: 'solid',    r: 7.5,  h: 34 },
      stone_lantern:   { mode: 'solid',    r: 5.5,  h: 24 },
      beach_umbrella:  { mode: 'solid',    r: 2.5,  h: 28 },
      wood_boat:       { mode: 'box',      halfW: 15.0, halfD: 8.5,  h: 12 },
      bush_berry:      { mode: 'solid',    r: 4.8,  h: 9 },
      sunflower:       { mode: 'solid',    r: 3.2,  h: 15 },
      pumpkin_patch:   { mode: 'solid',    r: 5.8,  h: 8 },
      mushroom_giant:  { mode: 'platform', r: 7.8,  h: 16 },
      boulder_large:   { mode: 'platform', r: 6.2,  h: 12 },
      hay_bale:        { mode: 'platform', r: 6.8,  h: 10 },
      tree_stump:      { mode: 'platform', r: 6.5,  h: 10 },
      torii_gate:      { mode: 'arch',     offset: 16.5, r: 3.8, h: 54 },
      flower_tuft:     { mode: 'none' },
      grass_tuft_short:{ mode: 'none' },
      grass_tuft_tall: { mode: 'none' }
    };

    const props = [];
    const propColliders = [];     // Cilindros sólidos, caixas ('box') e pilares de arco ('arch')
    const platformColliders = []; // Tops escaláveis (cogumelos, pedras, fardos, tocos)
    const fishes = [];
    const npcs = [];

    function addProp(modelKey, gx, gy, options = {}) {
      const t = getTile(gx, gy);
      if (!t || !propModels[modelKey]) return;
      const meta = PROP_COLLIDER_META[modelKey] || { mode: 'none' };

      // Validador explícito: nunca obstruir trilhas, pontes ou água com props sólidos/plataformas!
      if (!options.allowOnPath && meta.mode !== 'none' && meta.mode !== 'arch') {
        if (t.type === 'path' || t.type === 'bridge' || t.type === 'water' || t.type === 'lilypad') {
          return;
        }
      }

      const c = tileCenter(gx, gy);
      const scale = options.scale || 1.0;
      const liftZ = options.liftZ !== undefined ? options.liftZ : t.h;
      const angle = options.angle || 0;
      const wx = c.wx + (options.ox || 0);
      const wy = c.wy + (options.oy || 0);

      const item = {
        id: `${modelKey}_${gx}_${gy}_${props.length}`,
        modelKey,
        model: propModels[modelKey],
        gx, gy,
        wx, wy,
        wz: liftZ,
        selfAngle: angle,
        scale,
        radius: options.radius || 7,
        isFire: modelKey === 'campfire' || modelKey === 'stone_lantern',
        isPlatform: meta.mode === 'platform',
        topZ: meta.mode === 'platform' ? liftZ + meta.h * scale : liftZ,
        promoteWide: (modelKey === 'sakura_oak' || modelKey === 'cozy_cabin' || modelKey === 'lighthouse' || modelKey === 'wood_boat')
      };
      props.push(item);

      if (meta.mode === 'solid') {
        propColliders.push({
          shape: 'circle',
          wx, wy,
          r: meta.r * scale,
          baseZ: liftZ,
          colH: meta.h * scale,
          modelKey
        });
      } else if (meta.mode === 'box') {
        propColliders.push({
          shape: 'box',
          wx, wy,
          halfW: meta.halfW * scale,
          halfD: meta.halfD * scale,
          angle,
          baseZ: liftZ,
          colH: meta.h * scale,
          modelKey
        });
      } else if (meta.mode === 'platform') {
        platformColliders.push({
          wx, wy,
          r: meta.r * scale,
          baseZ: liftZ,
          topZ: liftZ + meta.h * scale,
          modelKey
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

    function addFish(gx, gy, label, extraZ = 0) {
      const t = getTile(gx, gy);
      if (!t) return;
      const c = tileCenter(gx, gy);
      fishes.push({
        id: `fish_${fishes.length}`,
        gx, gy, label,
        wx: c.wx,
        wy: c.wy,
        baseZ: t.h + extraZ,
        collected: false
      });
    }

    function populateWorldObjects() {
      // 1. Vila da Clareira
      addProp('cozy_cabin', 15, 31, { radius: 22 });
      addProp('campfire', 22, 27);
      addProp('wood_sign', 23, 30, { angle: 0.2 });
      addProp('pumpkin_patch', 15, 34);
      addProp('tree_stump', 23, 32);
      addProp('flower_tuft', 17, 33);
      addProp('flower_tuft', 21, 31);
      addProp('pine_tree', 14, 23, { radius: 10 });
      addProp('pine_tree', 24, 23, { radius: 10 });
      addProp('bush_berry', 24, 34);

      // 2. Campos de Girassol
      for (const [tx, ty] of [[5, 27], [7, 26], [6, 28], [4, 24], [8, 23], [10, 21], [5, 20], [7, 21], [5, 31], [7, 32]]) {
        addProp('sunflower', tx, ty);
      }
      addProp('hay_bale', 11, 28);
      addProp('hay_bale', 8, 29);
      addProp('tree_stump', 10, 32);
      addProp('flower_tuft', 4, 29);

      // 3. Circuito das Ruínas
      addProp('ruin_pillar', 6, 37, { radius: 8 });
      addProp('ruin_pillar', 17, 37, { radius: 8 });
      addProp('stone_lantern', 6, 41);
      addProp('stone_lantern', 17, 41);
      addProp('boulder_large', 20, 41);
      addProp('flower_tuft', 8, 43);

      // 4. Praia Dourada, Píer & Farol Monumental
      addProp('lighthouse', 7, 50, { ox: 8, oy: 8, radius: 16 });
      addProp('stone_lantern', 10, 48);
      addProp('beach_umbrella', 15, 47, { radius: 9 });
      addProp('beach_umbrella', 23, 47, { radius: 9 });
      addProp('wood_boat', 33, 47, { angle: 0.15, radius: 15 });
      addProp('boulder_large', 33, 51);

      // 5. Jardim Zen & Portal Torii Gigante (Centralizado em gx=16; pilares em 15 e 17, vão livre de 25.4u!)
      addProp('torii_gate', 16, 13, { ox: 0, angle: 0, radius: 18, allowOnPath: true });
      addProp('stone_lantern', 13, 15);
      addProp('stone_lantern', 19, 15);
      addProp('stone_lantern', 13, 10);
      addProp('bush_berry', 21, 9);
      addProp('flower_tuft', 14, 7);
      addProp('boulder_large', 7, 5);
      addProp('ruin_pillar', 4, 4, { radius: 8 });
      addProp('pine_tree', 21, 5, { radius: 10 });

      // 6. Bosque dos Cogumelos Saltitantes (Sudeste)
      addProp('mushroom_giant', 37, 34); // Cap Z=16
      addProp('mushroom_giant', 40, 34); // Em Z=12 -> Cap Z=28!
      addProp('mushroom_giant', 43, 36); // Em Z=24 -> Cap Z=40!
      addProp('mushroom_giant', 45, 31); // Cap Z=16
      addProp('mushroom_giant', 36, 40); // Cap Z=16
      for (const [tx, ty] of [[33, 32], [35, 37], [38, 42], [44, 41], [47, 33], [51, 35], [49, 41], [33, 43], [52, 43]]) {
        addProp('pine_tree', tx, ty, { radius: 10 });
      }
      addProp('tree_stump', 34, 34);
      addProp('hay_bale', 49, 40);
      addProp('boulder_large', 47, 29);
      addProp('bush_berry', 39, 37);
      addProp('flower_tuft', 35, 32);
      addProp('flower_tuft', 44, 32);

      // 7. Montanha & Pico Sakura Monumental (Trilha em espiral mantida 100% livre!)
      addProp('sakura_oak', 38, 10, { scale: 1.0, radius: 18 });
      addProp('stone_lantern', 42, 13);
      addProp('stone_lantern', 36, 13);
      addProp('flower_tuft', 37, 13);
      addProp('flower_tuft', 41, 9);
      addProp('boulder_large', 34, 21);
      addProp('pine_tree', 36, 22, { radius: 10 });

      // Pinheiros altos nas bordas arborizadas (fora de caminhos/água/mar)
      for (let gx = 1; gx <= 54; gx += 7) {
        addProp('pine_tree', gx, 1, { radius: 10 });
      }
      for (let gy = 4; gy <= 44; gy += 6) {
        addProp('pine_tree', 1, gy, { radius: 10 });
        addProp('pine_tree', 54, gy, { radius: 10 });
      }

      // 16 PEIXES DOURADOS COLECIONÁVEIS distribuídos pelos 8 biomas!
      addFish(21, 24, 'Rampa da Vila');                  // #1 (Z=6, sobe andando)
      addFish(11, 28, 'Fardo dos Girassóis', 10);        // #2 (Z=10 no topo do fardo!)
      addFish(5,  20, 'Colina dos Girassóis');           // #3 (Z=16)
      addFish(14, 39, 'Torre das Ruínas');               // #4 (Z=48)
      addFish(18, 52, 'Ponta do Píer');                  // #5 (Z=2)
      addFish(9,  52, 'Mirante do Farol');               // #6 (Z=16 bem visível frente ao Farol!)
      addFish(32, 50, 'Ilhota das Vitórias-Régias');     // #7 (Z=0 pós pulos)
      addFish(27, 28, 'Ponte Central');                  // #8 (Z=2)
      addFish(27, 39, 'Pedra do Rio', 0);
      fishes[fishes.length - 1].gx = 28;
      fishes[fishes.length - 1].wx = tileCenter(28, 39).wx;
      fishes[fishes.length - 1].baseZ = 2;               // #9 (Z=2 pedra do rio)
      addFish(16, 8,  'Alameda Pós-Torii');              // #10 (Z=16)
      addFish(4,  3,  'Mirante Zen');                    // #11 (Z=48)
      addFish(27, 14, 'Ponte Norte');                    // #12 (Z=16)
      addFish(40, 34, 'Cogumelo Médio', 16);             // #13 (Z=28 topo do cogumelo!)
      addFish(43, 36, 'Cogumelo Alto', 16);              // #14 (Z=40 topo do cogumelo!)
      addFish(50, 14, 'Patamar da Montanha');            // #15 (Z=48 trilha)
      addFish(41, 12, 'Pico Sakura Lendário');           // #16 (Z=96 no cume!)

      // NPCs VIVOS (Popó na Vila + 2 Pintinhos nos Girassóis!)
      const p1 = tileCenter(20, 30);
      npcs.push({
        kind: 'chicken', name: 'Popó', model: chickenModel, scale: 0.72,
        x: p1.wx, y: p1.wy, z: 0, homeX: p1.wx, homeY: p1.wy, roamR: 48,
        selfAngle: 0, walkPhase: 0, timer: 1.5, moving: true, dirX: 1, dirY: 0,
        speech: null
      });
      for (const [cx, cy] of [[6, 26], [8, 22]]) {
        const tc = tileCenter(cx, cy);
        const t = getTile(cx, cy);
        npcs.push({
          kind: 'chick', name: 'Piu', model: propModels.baby_chick, scale: 0.95,
          x: tc.wx, y: tc.wy, z: t ? t.h : 0, homeX: tc.wx, homeY: tc.wy, roamR: 30,
          selfAngle: 0, walkPhase: 0, timer: 0.8 + Math.random(), moving: true, dirX: -1, dirY: 0.5,
          speech: null
        });
      }
    }
    populateWorldObjects();

    // =========================================================================
    // 6. ESTADO DO GATO, FÍSICA DE PULO 2×H & TRAVEL LANDMARKS
    // =========================================================================
    const spawnCenter = tileCenter(19, 29);
    const cat = {
      x: spawnCenter.wx,
      y: spawnCenter.wy,
      z: 0,
      vz: 0,
      groundZ: 0,
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
      speech: { text: 'Miau! Bora explorar o Vale! 🐾', timer: 190 },
      lastSafeX: spawnCenter.wx,
      lastSafeY: spawnCenter.wy,
      lastSafeZ: 0,
      maxJumpReached: 0,
      obstacleHint: 'ok',
      obstacleLabel: '✅ Caminho Livre'
    };

    const TRAVEL_SPOTS = [
      { gx: 19, gy: 29, label: '🏡 Vila da Clareira' },
      { gx: 11, gy: 42, label: '🏛️ Ruínas Antigas' },
      { gx: 16, gy: 47, label: '🏖️ Praia & Farol' },
      { gx: 16, gy: 15, label: '⛩️ Jardim Zen & Torii' },
      { gx: 36, gy: 34, label: '🍄 Bosque Cogumelos' },
      { gx: 47, gy: 24, label: '🥾 Base da Montanha' },
      { gx: 40, gy: 12, label: '🌸 Pico Sakura (Z=96)' }
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

    function evaluateSupport(wx, wy, currentZ, onGround) {
      const r = 2.6;
      const samples = [
        [wx, wy],
        [wx - r, wy], [wx + r, wy],
        [wx, wy - r], [wx, wy + r]
      ];
      let bestH = -999;
      let centerTile = null;
      const ct = worldToTileCoords(wx, wy);
      centerTile = getTile(ct.gx, ct.gy);

      for (const [sx, sy] of samples) {
        const tc = worldToTileCoords(sx, sy);
        const t = getTile(tc.gx, tc.gy);
        if (!t || t.type === 'water') continue;
        if (t.h <= currentZ + AUTO_STEP_MAX + 0.5) {
          if (t.h > bestH) bestH = t.h;
        }
      }

      for (const pc of platformColliders) {
        const d = Math.hypot(wx - pc.wx, wy - pc.wy);
        // Só apoia no topo da plataforma se o gato estiver acima dela ou num passo <= 4u!
        const climbAllowed = onGround ? 4.0 : 1.5;
        if (d <= pc.r && pc.topZ <= currentZ + climbAllowed) {
          if (pc.topZ > bestH) bestH = pc.topZ;
        }
      }

      return { bestH, centerTile };
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

      const ct = worldToTileCoords(nx, ny);
      const centerTile = getTile(ct.gx, ct.gy);
      if (centerTile && centerTile.type === 'water' && (onGround || catZ <= 1.2)) {
        return { blocked: true, reason: 'water', maxStepH: -8 };
      }

      const r = 2.8;
      const pts = [
        [nx, ny],
        [nx - r, ny - r], [nx + r, ny - r],
        [nx - r, ny + r], [nx + r, ny + r]
      ];

      const allowedClimb = onGround ? AUTO_STEP_MAX : 1.5;
      let blocked = false;
      let maxBlockingH = -999;
      let propBlocked = false;

      // 1. Terreno (altura dos tiles)
      for (const [px, py] of pts) {
        const tc = worldToTileCoords(px, py);
        const t = getTile(tc.gx, tc.gy);
        if (!t) {
          blocked = true;
          maxBlockingH = 999;
          continue;
        }
        if (t.type === 'water') continue;
        if (t.h > catZ + allowedClimb) {
          blocked = true;
          if (t.h > maxBlockingH) maxBlockingH = t.h;
        }
      }

      // 2. Props Sólidos, Caixas ('box' como cabana/barco) e Pilares de Arco ('arch' Torii)
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

      // 3. Props-Plataforma (cogumelos, fardos, tocos, pedras) — bloqueia abaixo do topo!
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
      const tc = worldToTileCoords(probeX, probeY);
      const t = getTile(tc.gx, tc.gy);

      if (!t) {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = '⛔ Limite do Vale';
        return;
      }
      if (t.type === 'water') {
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

      let targetH = t.h;
      for (const pc of platformColliders) {
        if (Math.hypot(probeX - pc.wx, probeY - pc.wy) <= pc.r + 2.0 && pc.topZ > targetH) {
          targetH = pc.topZ;
        }
      }

      const dz = targetH - cat.groundZ;
      if (dz <= AUTO_STEP_MAX) {
        cat.obstacleHint = 'ok';
        cat.obstacleLabel = dz > 0.5 ? '✅ Rampa Suave (≤0.4H)' : '✅ Caminho Livre';
      } else if (dz <= CAT_HEIGHT * 2.0 + 0.5) {
        cat.obstacleHint = 'jump';
        cat.obstacleLabel = `🦘 Degrau ${Math.round(dz)}u — Espaço p/ Pular!`;
      } else {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = `⛔ Paredão ${Math.round(dz)}u (> 2×H)`;
      }
    }

    // =========================================================================
    // 7. CONTROLES, TOUCH & VIEWPORT RESPONSIVO 1:1 (ZERO DISTORÇÃO!)
    // =========================================================================
    const keys = {};
    let turn = -Math.PI * 0.25;
    let targetTurn = turn;
    let squash = 0.72;
    let camX = cat.x;
    let camY = cat.y;
    let camZ = cat.z;
    let blockedCooldown = 0;

    // Responsividade 1:1 — `lowCanvas` adapta dimensões exatas à janela para pixels 100% quadrados!
    const canvas = document.getElementById('viewport');
    const ctx = canvas.getContext('2d');
    const lowCanvas = document.createElement('canvas');
    const lowCtx = lowCanvas.getContext('2d');
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
      lowCanvas.width = LOW_W;
      lowCanvas.height = LOW_H;
      lowCtx.imageSmoothingEnabled = false;

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

    // Touch D-Pad + Jump
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

    function teleportToTile(gx, gy, msg = null) {
      const t = getTile(gx, gy);
      const c = tileCenter(gx, gy);
      cat.x = c.wx;
      cat.y = c.wy;
      const gz = t ? t.h : 0;
      cat.z = gz;
      cat.vz = 0;
      cat.groundZ = gz;
      cat.onGround = true;
      cat.lastSafeX = c.wx;
      cat.lastSafeY = c.wy;
      cat.lastSafeZ = gz;
      cat.maxJumpReached = gz;
      camX = cat.x;
      camY = cat.y;
      camZ = cat.z;
      if (msg) catSpeak(msg, 125);
    }

    function resetCatToSpawn() {
      teleportToTile(19, 29, 'De volta à Vila! 🏡');
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
      teleportToTile(spot.gx, spot.gy, spot.label);
      sfxBiome();
    });

    // =========================================================================
    // 8. UPDATE FÍSICO, NPCS & GRAMA RUSTLE
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
          const tc = worldToTileCoords(nx, ny);
          const t = getTile(tc.gx, tc.gy);
          if (t && t.type !== 'water' && Math.abs(t.h - npc.z) <= 6.5) {
            let hitProp = false;
            for (const sc of propColliders) {
              if (isPointInPropCollider(nx, ny, sc, 3.5)) { hitProp = true; break; }
            }
            if (!hitProp) {
              npc.x = nx;
              npc.y = ny;
              npc.z = t.h;
            } else {
              npc.dirX = -npc.dirX;
              npc.dirY = -npc.dirY;
            }
          } else {
            npc.dirX = -npc.dirX;
            npc.dirY = -npc.dirY;
          }
          // Popó (chicken_slices.json) olha para +X -> atan2(dy, dx). Pintinho olha para +Y -> atan2(-dx, dy).
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

    let lastRustleTile = -1;
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

      const speed = cat.onGround ? 90 : 80;
      if (ilen > 0) {
        const dx = moveWorldX * speed * dt;
        const dy = moveWorldY * speed * dt;
        let blockedNow = null;

        if (dx !== 0) {
          const checkX = checkCollisionAt(cat.x + dx, cat.y, cat.z, cat.onGround);
          if (!checkX.blocked) cat.x += dx;
          else blockedNow = checkX;
        }
        if (dy !== 0) {
          const checkY = checkCollisionAt(cat.x, cat.y + dy, cat.z, cat.onGround);
          if (!checkY.blocked) cat.y += dy;
          else blockedNow = checkY;
        }

        if (blockedNow && blockedCooldown <= 0) {
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
        } else if (wasOnGround && sup.bestH < cat.z && cat.z - sup.bestH <= 4) {
          cat.z = sup.bestH;
          cat.vz = 0;
          cat.onGround = true;
        } else if (cat.z > sup.bestH + 0.5) {
          cat.onGround = false;
        }
      } else {
        cat.groundZ = -8;
        cat.onGround = false;
        if (cat.z < -2) {
          cat.x = cat.lastSafeX;
          cat.y = cat.lastSafeY;
          cat.z = cat.lastSafeZ + 2;
          cat.vz = 0;
          cat.onGround = true;
          sfxBlocked();
          catSpeak('Splash! De volta à margem! 💦', 110);
          spawnParticles(cat.x, cat.y, cat.z + 2, 10, ['#93C5FD', '#FFFFFF'], 32);
        }
      }

      if (cat.isWalking && cat.onGround) {
        cat.walkPhase += dt * 11;
      }

      // Grama rustle ao entrar num tile verde
      const curTile = sup.centerTile;
      if (curTile) {
        const tidx = curTile.gy * GRID_SIZE + curTile.gx;
        if (cat.onGround && curTile.type === 'grass' && cat.isWalking && tidx !== lastRustleTile) {
          lastRustleTile = tidx;
          if ((curTile.gx * 73 + curTile.gy * 37) % 10 < 7 && Math.random() < 0.45) {
            spawnParticles(cat.x, cat.y, cat.z + 2, 2, ['#4DB848', '#8BE064'], 14);
          }
        }
        // Descoberta de Bioma!
        if (!visitedBiomes.has(curTile.biomeKey)) {
          visitedBiomes.add(curTile.biomeKey);
          sfxBiome();
          showBiomeToast(curTile.biome);
        }
      }

      // Coleta de Peixes Dourados (16)
      let collectedCount = 0;
      for (const f of fishes) {
        if (f.collected) {
          collectedCount++;
          continue;
        }
        const dx = cat.x - f.wx;
        const dy = cat.y - f.wy;
        const dz = Math.abs(cat.z - f.baseZ);
        if (Math.hypot(dx, dy) < 12 && dz < 14) {
          f.collected = true;
          collectedCount++;
          sfxFish();
          catSpeak(`Peixinho! (${collectedCount}/16) 🐟✨`, 135);
          spawnParticles(f.wx, f.wy, f.baseZ + 6, 16, ['#FBBF24', '#FEF08A', '#F97316', '#FFFFFF'], 44);
        }
      }
      document.getElementById('fishCounter').textContent = `🐟 ${collectedCount} / ${fishes.length}`;
      document.getElementById('biomeCounter').textContent = `🗺️ ${visitedBiomes.size} / 8`;

      updateObstacleSensor(moveWorldX, moveWorldY);
      document.getElementById('biomeLabel').textContent = curTile ? curTile.biome : 'Vale Felino';
      document.getElementById('statElev').textContent = `Chão: Z=${Math.round(cat.groundZ)} | Gato: Z=${Math.round(cat.z)}`;
      const obsEl = document.getElementById('statObstacle');
      obsEl.textContent = cat.obstacleLabel;
      obsEl.className = 'obstacle-chip obs-' + cat.obstacleHint;

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
    // 9. RENDERIZAÇÃO VOXEL 3D + GRAMA EM LÂMINAS + BALÕES HI-RES
    // =========================================================================
    let cachedTurnAngle = null;
    const propOutlineCache = {};
    const grassWindCache = {};

    const scratchCanvas = document.createElement('canvas');
    scratchCanvas.width = 72;
    scratchCanvas.height = 72;
    const scratchCtx = scratchCanvas.getContext('2d');
    scratchCtx.imageSmoothingEnabled = false;

    const silCanvas = document.createElement('canvas');
    silCanvas.width = 72;
    silCanvas.height = 72;
    const silCtx = silCanvas.getContext('2d');
    silCtx.imageSmoothingEnabled = false;

    function project(wx, wy, wz) {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const dx = wx - camX;
      const dy = wy - camY;
      const dz = wz - camZ;
      const rx = dx * cosA - dy * sinA;
      const ry = dx * sinA + dy * cosA;
      return {
        x: Math.round(LOW_W / 2 + rx),
        y: Math.round(LOW_H / 2 + 16 + ry * squash - dz),
        depth: ry
      };
    }

    function drawQuad(p1, p2, p3, p4, fillStyle) {
      lowCtx.beginPath();
      lowCtx.moveTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.lineTo(p4.x, p4.y);
      lowCtx.closePath();
      lowCtx.fillStyle = fillStyle;
      lowCtx.fill();
      lowCtx.strokeStyle = fillStyle;
      lowCtx.lineWidth = 0.75;
      lowCtx.stroke();
    }

    function getTopColor(t, animTick) {
      const n = ((t.gx * 73856093) ^ (t.gy * 19349663)) & 3;
      if (t.type === 'water') {
        const wave = ((t.gx + t.gy + animTick) % 6 === 0);
        return wave ? '#7DD3FC' : (n === 0 ? '#38BDF8' : '#2EB5F0');
      }
      if (t.type === 'lilypad') return n % 2 === 0 ? '#4ADE80' : '#22C55E';
      if (t.type === 'bridge') return n % 2 === 0 ? '#B97A4A' : '#A66A3E';
      if (t.type === 'stone') {
        if (t.h >= 48) return n % 2 === 0 ? '#9CA3AF' : '#8E96A4';
        return n % 2 === 0 ? '#B4BAC4' : '#A3AAB5';
      }
      if (t.type === 'path') return n % 2 === 0 ? '#DFB684' : '#D3A673';
      if (t.type === 'sand') return n % 2 === 0 ? '#F3DDA9' : '#EAD094';
      if (t.type === 'peak') return n % 2 === 0 ? '#F9A8D4' : '#7BC96F';
      if (t.h >= 32) return n === 0 ? '#78D064' : (n === 1 ? '#6EC45B' : '#65BA53');
      if (t.h >= 12) return n === 0 ? '#69C257' : (n === 1 ? '#5EB74D' : '#56AE45');
      return n === 0 ? '#5CB852' : (n === 1 ? '#53AD49' : '#4BA242');
    }

    function invalidateAngleCachesIfNeeded() {
      const qAngle = Math.round((turn * 180 / Math.PI) / 3) * 3;
      if (cachedTurnAngle !== qAngle) {
        cachedTurnAngle = qAngle;
        for (const k in propOutlineCache) delete propOutlineCache[k];
        for (const k in grassWindCache) delete grassWindCache[k];
      }
    }

    function getOutlinedPropSprite(modelKey, model, extraAngle = 0) {
      invalidateAngleCachesIfNeeded();
      const cacheKey = extraAngle === 0 ? modelKey : `${modelKey}_${Math.round(extraAngle * 100)}`;
      if (propOutlineCache[cacheKey]) return propOutlineCache[cacheKey];

      const pad = 6;
      const bw = Math.ceil(model.w * 1.6) + pad * 2;
      const bh = Math.ceil(model.h * 1.4 + model.count) + pad * 2;

      const tmp = document.createElement('canvas');
      tmp.width = bw;
      tmp.height = bh;
      const tctx = tmp.getContext('2d');
      tctx.imageSmoothingEnabled = false;

      const ox = Math.floor(bw / 2);
      const oy = bh - Math.floor(model.h / 2) - pad;
      const originX = Math.floor(model.w / 2);
      const originY = Math.floor(model.h / 2);

      for (let z = 0; z < model.count; z++) {
        tctx.save();
        tctx.translate(ox, Math.round(oy - z));
        tctx.scale(1, squash);
        tctx.rotate(turn + extraAngle);
        tctx.drawImage(model.sheet, z * model.w, 0, model.w, model.h, -originX, -originY, model.w, model.h);
        tctx.restore();
      }

      const out = document.createElement('canvas');
      out.width = bw;
      out.height = bh;
      const octx = out.getContext('2d');
      octx.imageSmoothingEnabled = false;

      const sil = document.createElement('canvas');
      sil.width = bw;
      sil.height = bh;
      const sctx = sil.getContext('2d');
      sctx.drawImage(tmp, 0, 0);
      sctx.globalCompositeOperation = 'source-in';
      sctx.fillStyle = '#3B2219';
      sctx.fillRect(0, 0, bw, bh);

      octx.drawImage(sil, -1, 0);
      octx.drawImage(sil,  1, 0);
      octx.drawImage(sil,  0, -1);
      octx.drawImage(sil,  0,  1);
      octx.drawImage(tmp,  0,  0);

      const entry = { canvas: out, ox, oy };
      propOutlineCache[cacheKey] = entry;
      return entry;
    }

    // Sistema de Lâminas de Grama Voxel 2–3px (noOutline: true, 3 frames de vento a 8 FPS!)
    function getGrassBladeSprite(modelKey, windFrame) {
      invalidateAngleCachesIfNeeded();
      const cacheKey = `${modelKey}_w${windFrame}`;
      if (grassWindCache[cacheKey]) return grassWindCache[cacheKey];

      const model = propModels[modelKey];
      const bw = 24;
      const bh = 24;
      const cv = document.createElement('canvas');
      cv.width = bw;
      cv.height = bh;
      const cx = cv.getContext('2d');
      cx.imageSmoothingEnabled = false;

      const ox = 12;
      const oy = 14;
      const originX = Math.floor(model.w / 2);
      const originY = Math.floor(model.h / 2);

      for (let z = 0; z < model.count; z++) {
        const swayX = z * 0.55 * windFrame; // desloca suavemente pontinhas sem borrar!
        cx.save();
        cx.translate(Math.round(ox + swayX), Math.round(oy - z));
        cx.scale(1, squash);
        cx.rotate(turn);
        cx.drawImage(model.sheet, z * model.w, 0, model.w, model.h, -originX, -originY, model.w, model.h);
        cx.restore();
      }

      const entry = { canvas: cv, ox, oy };
      grassWindCache[cacheKey] = entry;
      return entry;
    }

    function drawStaticProp(p) {
      const proj = project(p.wx, p.wy, p.wz);
      const spr = getOutlinedPropSprite(p.modelKey, p.model, p.selfAngle);
      const dw = Math.round(spr.canvas.width * p.scale);
      const dh = Math.round(spr.canvas.height * p.scale);
      const dx = Math.round(proj.x - spr.ox * p.scale);
      const dy = Math.round(proj.y - spr.oy * p.scale);
      lowCtx.drawImage(spr.canvas, dx, dy, dw, dh);

      if (p.isFire) {
        const flick = Math.sin(cat.idleTimer * 12) * 1.5;
        lowCtx.fillStyle = 'rgba(255, 210, 80, 0.34)';
        lowCtx.beginPath();
        lowCtx.arc(proj.x, proj.y - (p.modelKey === 'stone_lantern' ? 11 : 6), 6 + flick * 0.4, 0, Math.PI * 2);
        lowCtx.fill();
      }
    }

    function drawDynamicStackWithOutline(drawFn, centerWorldX, centerWorldY, centerWorldZ) {
      scratchCtx.clearRect(0, 0, 72, 72);
      const anchorX = 36;
      const anchorY = 48;

      function stampSlice(model, wx, wy, wz, selfAngle, scale) {
        const dx = wx - centerWorldX;
        const dy = wy - centerWorldY;
        const dz = wz - centerWorldZ;
        const cosA = Math.cos(turn);
        const sinA = Math.sin(turn);
        const rx = dx * cosA - dy * sinA;
        const ry = dx * sinA + dy * cosA;
        const sx = Math.round(anchorX + rx);
        const sy = Math.round(anchorY + ry * squash - dz);
        const totalAngle = selfAngle + turn;
        const ox = Math.floor(model.w / 2);
        const oy = Math.floor(model.h / 2);
        for (let z = 0; z < model.count; z++) {
          scratchCtx.save();
          scratchCtx.translate(sx, Math.round(sy - z * scale));
          scratchCtx.scale(scale, squash * scale);
          scratchCtx.rotate(totalAngle);
          scratchCtx.drawImage(model.sheet, z * model.w, 0, model.w, model.h, -ox, -oy, model.w, model.h);
          scratchCtx.restore();
        }
      }

      drawFn(stampSlice);

      silCtx.clearRect(0, 0, 72, 72);
      silCtx.globalCompositeOperation = 'source-over';
      silCtx.drawImage(scratchCanvas, 0, 0);
      silCtx.globalCompositeOperation = 'source-in';
      silCtx.fillStyle = '#3B2219';
      silCtx.fillRect(0, 0, 72, 72);

      const p = project(centerWorldX, centerWorldY, centerWorldZ);
      const bx = p.x - anchorX;
      const by = p.y - anchorY;
      lowCtx.drawImage(silCanvas, bx - 1, by);
      lowCtx.drawImage(silCanvas, bx + 1, by);
      lowCtx.drawImage(silCanvas, bx, by - 1);
      lowCtx.drawImage(silCanvas, bx, by + 1);
      lowCtx.drawImage(scratchCanvas, bx, by);
    }

    function drawCatShadow(x, y, groundZ, z) {
      const shP = project(x, y, Math.max(groundZ, -5) + 0.3);
      const hAbove = Math.max(0, z - groundZ);
      const shrink = Math.max(0.45, 1.0 - hAbove / 55);
      lowCtx.fillStyle = `rgba(38, 22, 14, ${0.32 * shrink})`;
      lowCtx.beginPath();
      lowCtx.ellipse(shP.x, shP.y, 6.2 * shrink, 4.0 * shrink, 0, 0, Math.PI * 2);
      lowCtx.fill();
    }

    function drawCatEntity(speechQueue) {
      const sk = catSkinModels[cat.skinIdx];
      const hatPreset = HAT_PRESETS[cat.hatIdx];
      const hatModel = hatPreset.id !== 'none' ? hatModels[hatPreset.id] : null;
      const cosC = Math.cos(cat.selfAngle);
      const sinC = Math.sin(cat.selfAngle);
      const t = cat.walkPhase;
      const inAir = !cat.onGround;

      drawDynamicStackWithOutline((stamp) => {
        function paw(lx, ly, lift, stride) {
          const wx = cat.x + lx * cosC - (ly + stride) * sinC;
          const wy = cat.y + lx * sinC + (ly + stride) * cosC;
          stamp(sk.paw, wx, wy, cat.z + lift, cat.selfAngle, cat.scale);
        }

        const liftFL = inAir ? 0.5 : (cat.isWalking ? Math.max(0, Math.sin(t) * 3.0) : 0);
        const strideFL = inAir ? 2.2 : (cat.isWalking ? -Math.cos(t) * 2.3 : 0);
        const liftBR = inAir ? 0.0 : (cat.isWalking ? Math.max(0, Math.sin(t + 0.3) * 3.0) : 0);
        const strideBR = inAir ? -2.2 : (cat.isWalking ? -Math.cos(t + 0.3) * 2.3 : 0);
        const liftFR = inAir ? 0.5 : (cat.isWalking ? Math.max(0, Math.sin(t + Math.PI) * 3.0) : 0);
        const strideFR = inAir ? 2.2 : (cat.isWalking ? -Math.cos(t + Math.PI) * 2.3 : 0);
        const liftBL = inAir ? 0.0 : (cat.isWalking ? Math.max(0, Math.sin(t + Math.PI + 0.3) * 3.0) : 0);
        const strideBL = inAir ? -2.2 : (cat.isWalking ? -Math.cos(t + Math.PI + 0.3) * 2.3 : 0);

        const bob = inAir ? 0 : (cat.isWalking ? Math.abs(Math.sin(t * 2)) * 0.7 : Math.sin(cat.idleTimer * 2.4) * 0.35);

        paw(-4.5, -7.5, liftBL, strideBL);
        paw( 3.5, -7.5, liftBR, strideBR);
        paw(-4.5,  3.5, liftFL, strideFL);
        paw( 3.5,  3.5, liftFR, strideFR);

        stamp(sk.body, cat.x, cat.y, cat.z + 1.5 + bob, cat.selfAngle, cat.scale);

        if (hatModel) {
          const hx = cat.x - 4.5 * sinC;
          const hy = cat.y + 4.5 * cosC;
          const hz = cat.z + (15.0 + bob - 2.8) * cat.scale;
          stamp(hatModel, hx, hy, hz, cat.selfAngle, cat.scale);
        }
      }, cat.x, cat.y, cat.z);

      if (cat.speech && cat.speech.timer > 0) {
        cat.speech.timer--;
        const sp = project(cat.x, cat.y, cat.z + 24);
        speechQueue.push({ lowX: sp.x, lowY: sp.y, text: cat.speech.text });
      }
    }

    function drawNpcEntity(npc, speechQueue) {
      drawCatShadow(npc.x, npc.y, npc.z, npc.z);
      const bob = npc.moving ? Math.abs(Math.sin(npc.walkPhase * 2)) * 0.8 : Math.sin(cat.idleTimer * 2.5) * 0.3;
      drawDynamicStackWithOutline((stamp) => {
        stamp(npc.model, npc.x, npc.y, npc.z + bob, npc.selfAngle, npc.scale);
      }, npc.x, npc.y, npc.z);

      if (npc.speech && npc.speech.timer > 0) {
        const sp = project(npc.x, npc.y, npc.z + 18);
        speechQueue.push({ lowX: sp.x, lowY: sp.y, text: npc.speech.text });
      }
    }

    function drawFishCollectible(f) {
      const bob = Math.sin(cat.idleTimer * 3.5 + f.gx) * 2.2;
      const wz = f.baseZ + 4 + bob;
      const spinAngle = cat.idleTimer * 2.5 + f.gx;

      const sp = project(f.wx, f.wy, f.baseZ + 0.3);
      lowCtx.fillStyle = 'rgba(180, 120, 20, 0.25)';
      lowCtx.beginPath();
      lowCtx.ellipse(sp.x, sp.y, 5, 3, 0, 0, Math.PI * 2);
      lowCtx.fill();

      drawDynamicStackWithOutline((stamp) => {
        stamp(propModels.golden_fish, f.wx, f.wy, wz, spinAngle, 1.0);
      }, f.wx, f.wy, wz);
    }

    function drawColumnSideFace(xA, yA, xB, yB, topZ, bottomZ, isXFace, tile, animTick) {
      if (topZ <= bottomZ) return;

      if (tile.type === 'water' && topZ > 0) {
        const pTopA = project(xA, yA, topZ);
        const pTopB = project(xB, yB, topZ);
        const pBotA = project(xA, yA, bottomZ);
        const pBotB = project(xB, yB, bottomZ);
        drawQuad(pTopA, pTopB, pBotB, pBotA, isXFace ? '#38BDF8' : '#0284C7');
        const fallOffset = (animTick % 4) * 3;
        lowCtx.strokeStyle = '#E0F2FE';
        lowCtx.lineWidth = 1;
        for (let t = 0.22; t <= 0.85; t += 0.28) {
          const mx = pTopA.x + (pTopB.x - pTopA.x) * t;
          const myTop = pTopA.y + (pTopB.y - pTopA.y) * t + fallOffset;
          const myBot = pBotA.y + (pBotB.y - pBotA.y) * t;
          if (myTop < myBot - 2) {
            lowCtx.beginPath();
            lowCtx.moveTo(mx, myTop);
            lowCtx.lineTo(mx, Math.min(myBot, myTop + 9));
            lowCtx.stroke();
          }
        }
        return;
      }

      const grassLipCol = isXFace ? '#3D8C37' : '#2C6B28';
      const dirtCol     = isXFace ? '#9B6542' : '#73482E';
      const rockCol     = isXFace ? '#646E7A' : '#48515C';
      const darkRockCol = isXFace ? '#4D5560' : '#353C45';

      const lipZ = Math.max(bottomZ, topZ - (tile.type === 'stone' || tile.type === 'peak' ? 4 : 3.2));
      const pTopA = project(xA, yA, topZ);
      const pTopB = project(xB, yB, topZ);
      const pLipA = project(xA, yA, lipZ);
      const pLipB = project(xB, yB, lipZ);

      let lipColor = grassLipCol;
      if (tile.type === 'stone') lipColor = isXFace ? '#7C8591' : '#5D6570';
      else if (tile.type === 'bridge') lipColor = isXFace ? '#85522F' : '#633B20';
      else if (tile.type === 'sand') lipColor = isXFace ? '#CBAE75' : '#A68B58';
      else if (tile.type === 'path') lipColor = dirtCol;
      else if (tile.type === 'lilypad') lipColor = isXFace ? '#16A34A' : '#15803D';
      drawQuad(pTopA, pTopB, pLipB, pLipA, lipColor);

      if (lipZ <= bottomZ) return;

      if (tile.type === 'stone' || tile.h >= 32) {
        const midZ = Math.max(bottomZ, lipZ - 16);
        const pMidA = project(xA, yA, midZ);
        const pMidB = project(xB, yB, midZ);
        drawQuad(pLipA, pLipB, pMidB, pMidA, tile.type === 'stone' ? rockCol : dirtCol);
        if (midZ > bottomZ) {
          const pBotA = project(xA, yA, bottomZ);
          const pBotB = project(xB, yB, bottomZ);
          drawQuad(pMidA, pMidB, pBotB, pBotA, darkRockCol);
        }
      } else {
        const pBotA = project(xA, yA, bottomZ);
        const pBotB = project(xB, yB, bottomZ);
        drawQuad(pLipA, pLipB, pBotB, pBotA, tile.type === 'lilypad' ? '#166534' : dirtCol);
      }
    }

    // Bucket cuidadoso: gato só promove para vizinho se t.h <= wz + 1.2 (não puxa atrás de degraus altos!)
    function pickCatBucketCell(wx, wy, wz, radius, sinA, cosA) {
      let bestGx = null, bestGy = null, bestDepth = -Infinity;
      const gMinX = Math.max(0, Math.floor((wx - radius) / TILE + HALF_GRID));
      const gMaxX = Math.min(GRID_SIZE - 1, Math.floor((wx + radius) / TILE + HALF_GRID));
      const gMinY = Math.max(0, Math.floor((wy - radius) / TILE + HALF_GRID));
      const gMaxY = Math.min(GRID_SIZE - 1, Math.floor((wy + radius) / TILE + HALF_GRID));

      for (let gy = gMinY; gy <= gMaxY; gy++) {
        for (let gx = gMinX; gx <= gMaxX; gx++) {
          const t = grid[gy][gx];
          if (t.h <= wz + 1.2) {
            const d = (gx - HALF_GRID + 0.5) * sinA + (gy - HALF_GRID + 0.5) * cosA;
            if (d > bestDepth) {
              bestDepth = d;
              bestGx = gx;
              bestGy = gy;
            }
          }
        }
      }
      if (bestGx === null) {
        const tc = worldToTileCoords(wx, wy);
        bestGx = Math.max(0, Math.min(GRID_SIZE - 1, tc.gx));
        bestGy = Math.max(0, Math.min(GRID_SIZE - 1, tc.gy));
      }
      return bestGy * GRID_SIZE + bestGx;
    }

    function pickPropBucketCell(p, sinA, cosA) {
      if (!p.promoteWide) {
        return p.gy * GRID_SIZE + p.gx;
      }
      return pickCatBucketCell(p.wx, p.wy, p.wz, p.radius, sinA, cosA);
    }

    // Desenho Hi-Res de Balões de Fala DIRETAMENTE no ctx principal após o upscale!
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

        // Sombra suave
        ctx.fillStyle = 'rgba(59, 34, 25, 0.16)';
        ctx.beginPath();
        ctx.roundRect(bx + 2, by + 3, bw, bh, 10);
        ctx.fill();

        // Corpo do balão
        ctx.fillStyle = '#FFFDF8';
        ctx.strokeStyle = '#3B2219';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, bw, bh, 10);
        ctx.fill();
        ctx.stroke();

        // Rabicho apontando pro personagem
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

        // Texto vetorial super nítido!
        ctx.fillStyle = '#3B2219';
        ctx.fillText(item.text, bx + padX, by + bh / 2 + 0.5);
      }
      ctx.restore();
    }

    function renderScene() {
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

      const sinA = Math.sin(turn);
      const cosA = Math.cos(turn);
      const animTick = Math.floor(cat.idleTimer * 8); // 8 FPS stepped animation!
      const windWaveCycle = [0, 1, 2, 1];
      const speechQueue = [];

      const buckets = new Map();
      const pushToBucket = (cellIdx, fn, depthKey) => {
        if (!buckets.has(cellIdx)) buckets.set(cellIdx, []);
        buckets.get(cellIdx).push({ fn, depthKey });
      };

      // 1. Props Estáticos
      for (const p of props) {
        const cIdx = pickPropBucketCell(p, sinA, cosA);
        const dp = (p.wx - camX) * sinA + (p.wy - camY) * cosA;
        pushToBucket(cIdx, () => drawStaticProp(p), dp);
      }

      // 2. Peixes Dourados (+1000 se acima de plataforma para nunca cortar atrás do cogumelo/fardo!)
      for (const f of fishes) {
        if (f.collected) continue;
        const cIdx = pickCatBucketCell(f.wx, f.wy, f.baseZ, 4.0, sinA, cosA);
        const dp = (f.wx - camX) * sinA + (f.wy - camY) * cosA;
        const tileBaseH = grid[f.gy][f.gx].h;
        const bonus = f.baseZ > tileBaseH + 2 ? 1000 : 0;
        pushToBucket(cIdx, () => drawFishCollectible(f), dp + bonus);
      }

      // 3. NPCs (Popó + Pintinhos)
      for (const npc of npcs) {
        const cIdx = pickCatBucketCell(npc.x, npc.y, npc.z, 4.0, sinA, cosA);
        const dp = (npc.x - camX) * sinA + (npc.y - camY) * cosA;
        pushToBucket(cIdx, () => drawNpcEntity(npc, speechQueue), dp + 0.2);
      }

      // 4. Gato Jogável (com bônus de prioridade se estiver em cima de plataforma como cogumelo/fardo/toco!)
      {
        const catCell = pickCatBucketCell(cat.x, cat.y, cat.z, 4.5, sinA, cosA);
        const dp = (cat.x - camX) * sinA + (cat.y - camY) * cosA;
        let onPlatformBonus = 0;
        for (const pc of platformColliders) {
          if (Math.hypot(cat.x - pc.wx, cat.y - pc.wy) <= pc.r + 3 && cat.z >= pc.topZ - 2) {
            onPlatformBonus = 1000;
            break;
          }
        }
        pushToBucket(catCell, () => {
          drawCatShadow(cat.x, cat.y, cat.groundZ, cat.z);
          drawCatEntity(speechQueue);
        }, dp + 0.5 + onPlatformBonus);
      }

      const stepX = sinA >= 0 ? 1 : -1;
      const stepY = cosA >= 0 ? 1 : -1;
      const startX = stepX > 0 ? 0 : GRID_SIZE - 1;
      const endX   = stepX > 0 ? GRID_SIZE : -1;
      const startY = stepY > 0 ? 0 : GRID_SIZE - 1;
      const endY   = stepY > 0 ? GRID_SIZE : -1;

      const camTile = worldToTileCoords(camX, camY);
      const cullR = Math.ceil(Math.hypot(LOW_W, LOW_H) / (TILE * 1.45)) + 5;

      for (let gy = startY; gy !== endY; gy += stepY) {
        if (Math.abs(gy - camTile.gy) > cullR) continue;
        for (let gx = startX; gx !== endX; gx += stepX) {
          if (Math.abs(gx - camTile.gx) > cullR) continue;
          const t = grid[gy][gx];
          const x0 = (gx - HALF_GRID) * TILE;
          const x1 = x0 + TILE;
          const y0 = (gy - HALF_GRID) * TILE;
          const y1 = y0 + TILE;
          const topZ = t.h;

          if (sinA > 0.001) {
            const nb = getTile(gx + 1, gy);
            drawColumnSideFace(x1, y0, x1, y1, topZ, nb ? nb.h : SKIRT_BOTTOM, true, t, animTick);
          } else if (sinA < -0.001) {
            const nb = getTile(gx - 1, gy);
            drawColumnSideFace(x0, y0, x0, y1, topZ, nb ? nb.h : SKIRT_BOTTOM, true, t, animTick);
          }

          if (cosA > 0.001) {
            const nb = getTile(gx, gy + 1);
            drawColumnSideFace(x0, y1, x1, y1, topZ, nb ? nb.h : SKIRT_BOTTOM, false, t, animTick);
          } else if (cosA < -0.001) {
            const nb = getTile(gx, gy - 1);
            drawColumnSideFace(x0, y0, x1, y0, topZ, nb ? nb.h : SKIRT_BOTTOM, false, t, animTick);
          }

          const p00 = project(x0, y0, topZ);
          const p10 = project(x1, y0, topZ);
          const p11 = project(x1, y1, topZ);
          const p01 = project(x0, y1, topZ);
          drawQuad(p00, p10, p11, p01, getTopColor(t, animTick));

          // GRAMA EM LÂMINAS VOXEL (2–3px de altura) com onda de vento a 8 FPS + rustle!
          if (t.type === 'grass' || t.type === 'peak') {
            const gHash = ((gx * 73 + gy * 37) >>> 0) % 10;
            if (gHash < 7) {
              const isTall = (t.biomeKey === 'girassol' || t.biomeKey === 'cogumelos' || t.biomeKey === 'zen') && gHash < 3;
              const grassKey = isTall ? 'grass_tuft_tall' : 'grass_tuft_short';
              const wf = windWaveCycle[(animTick + ((gx + gy) >> 1)) & 3];
              const gSpr = getGrassBladeSprite(grassKey, wf);
              const gp = project((x0 + x1) * 0.5, (y0 + y1) * 0.5, topZ);
              const rustlePush = (Math.hypot(cat.x - (x0 + 8), cat.y - (y0 + 8)) < 9.5 && Math.abs(cat.z - topZ) < 5) ? 1 : 0;
              lowCtx.drawImage(gSpr.canvas, gp.x - gSpr.ox + rustlePush, gp.y - gSpr.oy + rustlePush);
            }
          }

          const cellIdx = gy * GRID_SIZE + gx;
          const bucket = buckets.get(cellIdx);
          if (bucket) {
            if (bucket.length > 1) {
              bucket.sort((a, b) => a.depthKey - b.depthKey);
            }
            for (const entry of bucket) {
              entry.fn();
            }
          }
        }
      }

      for (const p of particles) {
        const pp = project(p.x, p.y, p.z);
        lowCtx.fillStyle = p.color;
        lowCtx.fillRect(pp.x, pp.y, p.size, p.size);
      }

      // Upscale 1:1 quadrado Nearest-Neighbor para o Viewport inteiro (com DPR!)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, viewW, viewH);
      ctx.drawImage(lowCanvas, 0, 0, LOW_W * pixelScale, LOW_H * pixelScale);

      // PASSADA DE OVERLAY HI-RES: balões nítidos e sempre visíveis acima de tudo!
      drawSpeechOverlaysHiRes(speechQueue);
    }

    // =========================================================================
    // 10. MINIMAPA TOPOGRÁFICO 56×56 (112×112 px = 2×2 por tile)
    // =========================================================================
    const mmCanvas = document.getElementById('minimapCanvas');
    const mmCtx = mmCanvas.getContext('2d');
    const mmBase = document.createElement('canvas');
    mmBase.width = GRID_SIZE * 2;
    mmBase.height = GRID_SIZE * 2;
    const mmBaseCtx = mmBase.getContext('2d');

    function bakeMinimapBase() {
      for (let gy = 0; gy < GRID_SIZE; gy++) {
        for (let gx = 0; gx < GRID_SIZE; gx++) {
          const t = grid[gy][gx];
          let col = '#65C466';
          if (t.type === 'water') col = '#38BDF8';
          else if (t.type === 'lilypad') col = '#22C55E';
          else if (t.type === 'bridge') col = '#B97A4A';
          else if (t.type === 'sand') col = '#F3DDA9';
          else if (t.h >= 96) col = '#F472B6';
          else if (t.h >= 64) col = '#9CA3AF';
          else if (t.h >= 48) col = '#A8B1BD';
          else if (t.h >= 32) col = '#94A3B8';
          else if (t.h >= 16) col = '#4EA94C';
          else if (t.type === 'path') col = '#DFB684';
          mmBaseCtx.fillStyle = col;
          mmBaseCtx.fillRect(gx * 2, gy * 2, 2, 2);
        }
      }
    }
    bakeMinimapBase();

    function drawMinimap() {
      mmCtx.imageSmoothingEnabled = false;
      mmCtx.drawImage(mmBase, 0, 0);

      for (const f of fishes) {
        if (f.collected) continue;
        mmCtx.fillStyle = '#FACC15';
        mmCtx.fillRect(f.gx * 2 - 1, f.gy * 2 - 1, 3, 3);
      }

      for (const npc of npcs) {
        const nx = (npc.x / TILE + HALF_GRID) * 2;
        const ny = (npc.y / TILE + HALF_GRID) * 2;
        mmCtx.fillStyle = '#FDBA74';
        mmCtx.fillRect(Math.round(nx) - 1, Math.round(ny) - 1, 3, 3);
      }

      const cx = (cat.x / TILE + HALF_GRID) * 2;
      const cy = (cat.y / TILE + HALF_GRID) * 2;
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
    // 11. LOOP PRINCIPAL + HOOKS DE DEBUG/TESTE
    // =========================================================================
    let lastTime = performance.now();
    function loop(now) {
      const dt = Math.min(0.05, Math.max(0.001, (now - lastTime) / 1000));
      lastTime = now;
      updatePhysics(dt);
      renderScene();
      drawMinimap();
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

    window.__TERRAIN_DEBUG__ = {
      getState: () => ({
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
      setCatTile: (gx, gy, z = null) => {
        const t = getTile(gx, gy);
        const c = tileCenter(gx, gy);
        cat.x = c.wx;
        cat.y = c.wy;
        const gz = z !== null ? z : (t ? t.h : 0);
        cat.z = gz;
        cat.groundZ = gz;
        cat.vz = 0;
        cat.onGround = true;
        cat.lastSafeX = c.wx;
        cat.lastSafeY = c.wy;
        cat.lastSafeZ = gz;
        cat.maxJumpReached = gz;
        camX = cat.x;
        camY = cat.y;
        camZ = cat.z;
      },
      setTurn: (rad) => { turn = rad; targetTurn = rad; },
      triggerJump: () => { cat.jumpBuffer = 0.14; },
      speak: (text) => { catSpeak(text, 240); },
      getPropsByType: (modelKey) => props.filter(p => p.modelKey === modelKey).map(p => ({ gx: p.gx, gy: p.gy, wx: p.wx, wy: p.wy, wz: p.wz })),
      getTileAtWorld: (wx, wy) => {
        const tc = worldToTileCoords(wx, wy);
        return getTile(tc.gx, tc.gy);
      }
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
