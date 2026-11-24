import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, 'slices_v5.json'), 'r', encoding='utf-8') as f:
    cat_slices = json.load(f)

with open(os.path.join(ROOT, 'hats_pack.json'), 'r', encoding='utf-8') as f:
    hats_pack = json.load(f)

with open(os.path.join(ROOT, 'terrain_props_pack.json'), 'r', encoding='utf-8') as f:
    props_pack = json.load(f)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <link rel="icon" href="data:," />
  <title>Vale Felino 3D — Terreno Voxel & Pulo 2×H</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    body {
      background: linear-gradient(180deg, #8AD2F4 0%, #CBEBFA 55%, #F4E9D7 100%);
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
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #viewport {
      width: 100vw;
      height: 100vh;
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
      top: 14px;
      left: 14px;
      background: rgba(255, 252, 245, 0.90);
      backdrop-filter: blur(10px);
      border: 2px solid #5B3C2B;
      border-radius: 14px;
      padding: 10px 14px;
      box-shadow: 0 8px 22px rgba(59, 34, 25, 0.16);
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-width: 310px;
      z-index: 10;
    }
    .hud-title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .hud-title {
      font-size: 15px;
      font-weight: 800;
      color: #3B2219;
      letter-spacing: -0.3px;
    }
    .fish-badge {
      background: #FEF3C7;
      border: 1.5px solid #D97706;
      color: #92400E;
      font-weight: 800;
      font-size: 13px;
      padding: 3px 9px;
      border-radius: 999px;
      display: flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
    }
    .controls-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
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

    /* Minimapa Topo Direito */
    .minimap-card {
      position: absolute;
      top: 14px;
      right: 14px;
      background: rgba(255, 252, 245, 0.90);
      backdrop-filter: blur(10px);
      border: 2px solid #5B3C2B;
      border-radius: 14px;
      padding: 8px;
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
      letter-spacing: 0.6px;
      color: #6B4E3D;
    }
    #minimapCanvas {
      width: 116px;
      height: 116px;
      border-radius: 8px;
      border: 1.5px solid #7C5C47;
      image-rendering: pixelated;
    }

    /* Rodapé Telemetria */
    .hud-bottom {
      position: absolute;
      bottom: 14px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255, 252, 245, 0.92);
      backdrop-filter: blur(10px);
      border: 2px solid #5B3C2B;
      border-radius: 16px;
      padding: 8px 16px;
      box-shadow: 0 8px 24px rgba(59, 34, 25, 0.18);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 10px;
      max-width: 95vw;
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
      padding: 3px 10px;
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

    /* Botões Mobile / Toque Rápido */
    .mobile-pad {
      position: absolute;
      bottom: 72px;
      right: 16px;
      display: none;
      gap: 6px;
      z-index: 10;
    }
    @media (pointer: coarse) {
      .mobile-pad { display: flex; }
      .keys-hint { display: none; }
    }
  </style>
</head>
<body>
  <div class="stage">
    <canvas id="viewport"></canvas>

    <div class="hud-top-left">
      <div class="hud-title-row">
        <span class="hud-title">🏔️ Vale Felino 3D</span>
        <span class="fish-badge" id="fishCounter">🐟 0 / 10</span>
      </div>
      <div class="controls-row">
        <button class="pill-btn" id="btnSkin">🐱 Mochi</button>
        <button class="pill-btn" id="btnHat">🎩 Sem Chapéu</button>
        <button class="pill-btn" id="btnRotL" title="Girar Câmera (Q)">⟲ Q</button>
        <button class="pill-btn" id="btnRotR" title="Girar Câmera (E)">E ⟳</button>
        <button class="pill-btn primary" id="btnReset" title="Voltar ao Spawn (R)">🏠 Spawn</button>
      </div>
    </div>

    <div class="minimap-card">
      <div class="minimap-title" id="biomeLabel">Clareira do Spawn</div>
      <canvas id="minimapCanvas" width="108" height="108"></canvas>
    </div>

    <div class="hud-bottom">
      <span class="stat-chip">🐱 Altura: 1H (16u) | Pulo: 2H (32u)</span>
      <span class="stat-chip" id="statElev">Chão: Z=0 | Gato: Z=0</span>
      <span class="obstacle-chip obs-ok" id="statObstacle">✅ Caminho Livre</span>
      <span class="keys-hint">
        <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> Mover •
        <kbd>Espaço</kbd> Pular (2×H) •
        <kbd>Q</kbd>/<kbd>E</kbd> ou Arrastar Girar •
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
            const ch = row[x];
            const val = parseInt(ch, 36);
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
    // 3. ÁUDIO RETRO (WebAudio Sintetizado, Zero Assets Externos)
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
    const sfxLand = () => playTone(160, 85, 0.07, 'sine', 0.06);
    const sfxBlocked = () => playTone(180, 110, 0.11, 'square', 0.04);
    const sfxFish = () => {
      playTone(523.25, 783.99, 0.12, 'triangle', 0.09);
      setTimeout(() => playTone(783.99, 1046.5, 0.18, 'triangle', 0.09), 90);
    };
    const sfxMeow = () => playTone(660, 490, 0.16, 'sine', 0.07);

    // =========================================================================
    // 4. MAPA GRANDE 36×36 (6 Regiões Icônicas + Calibração de Altura)
    // =========================================================================
    const GRID_SIZE = 36;
    const TILE = 16;
    const HALF_GRID = GRID_SIZE / 2; // 18
    const WORLD_MIN = -HALF_GRID * TILE;
    const WORLD_MAX = HALF_GRID * TILE;
    const SKIRT_BOTTOM = -22;

    // Alturas canônicas calibradas para CAT_HEIGHT = 16u:
    // AUTO_STEP_MAX = 6.5 (~0.4H) -> sobe andando
    // JUMP_MAX = 32 (2.0H)         -> sobe pulando (pico físico ~35u)
    // > 32 (ex: 48 = 3.0H)         -> intransponível direto do chão!
    const CAT_HEIGHT = 16;
    const AUTO_STEP_MAX = 6.5;
    const GRAVITY = 1200;
    const JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0); // ~289.8 u/s -> apex exato ~35u (>32u, <48u)

    const grid = [];
    function initTerrainGrid() {
      for (let gy = 0; gy < GRID_SIZE; gy++) {
        const row = [];
        for (let gx = 0; gx < GRID_SIZE; gx++) {
          row.push({ gx, gy, h: 0, type: 'grass', biome: 'Clareira do Spawn' });
        }
        grid.push(row);
      }

      const setTile = (gx, gy, h, type = null, biome = null) => {
        if (gx < 0 || gy < 0 || gx >= GRID_SIZE || gy >= GRID_SIZE) return;
        grid[gy][gx].h = h;
        if (type) grid[gy][gx].type = type;
        if (biome) grid[gy][gx].biome = biome;
      };

      const fillRect = (x0, y0, x1, y1, h, type = null, biome = null) => {
        for (let y = y0; y <= y1; y++) {
          for (let x = x0; x <= x1; x++) {
            setTile(x, y, h, type, biome);
          }
        }
      };

      // Bordas suaves arborizadas (anéis externos de elevação decorativa)
      fillRect(0, 0, 35, 1, 24, 'grass', 'Borda da Floresta');
      fillRect(0, 34, 35, 35, 24, 'grass', 'Borda da Floresta');
      fillRect(0, 0, 1, 35, 24, 'grass', 'Borda da Floresta');
      fillRect(34, 0, 35, 35, 24, 'grass', 'Borda da Floresta');

      // 1. CLAREIRA CENTRAL-OESTE (Spawn em gx=10, gy=18)
      fillRect(3, 14, 15, 22, 0, 'grass', 'Clareira do Spawn');
      // Trilhas de terra batida na clareira levando ao leste (ponte), norte (terraços) e sul (ruínas)
      fillRect(9, 17, 15, 19, 0, 'path', 'Clareira do Spawn');
      fillRect(9, 14, 10, 25, 0, 'path', 'Clareira do Spawn');
      // Rampa suave transponível andando (Z=6 <= 0.4H!) para demonstrar AUTO_STEP
      fillRect(7, 13, 9, 14, 6, 'grass', 'Clareira do Spawn');
      fillRect(11, 15, 13, 15, 6, 'path', 'Clareira do Spawn');

      // 2. CIRCUITO DAS RUÍNAS / CALIBRAÇÃO DE ALTURA (Sudoeste: gx=4..14, gy=24..32)
      fillRect(3, 24, 15, 33, 0, 'grass', 'Ruínas da Escala');
      fillRect(4, 25, 14, 31, 0, 'path', 'Ruínas da Escala');
      // Faixas limpas Z=0 ao norte (gy=25..26) e ao sul (gy=29..30) para testar direto do chão!
      // 4 plataformas lado a lado (2 tiles de profundidade cada: gy=27..28)
      fillRect(5, 27, 6, 28, 6,  'stone', 'Ruínas (0.4H Andando)');
      fillRect(7, 27, 8, 28, 16, 'stone', 'Ruínas (1.0H Pulo)');
      fillRect(9, 27, 10, 28, 32, 'stone', 'Ruínas (2.0H Pulo Máx)');
      fillRect(11, 27, 12, 28, 48, 'stone', 'Ruínas (3.0H Torre Alta)');
      // Pilar decorativo elevado ao lado das ruínas
      fillRect(4, 25, 4, 25, 16, 'stone', 'Ruínas da Escala');
      fillRect(14, 25, 14, 25, 16, 'stone', 'Ruínas da Escala');

      // 3. RIO CRISTALINO (Corte Norte-Sul em gx=17..19)
      for (let y = 0; y < GRID_SIZE; y++) {
        for (let x = 17; x <= 19; x++) {
          setTile(x, y, -8, 'water', 'Rio Cristalino');
        }
      }
      // Margem arenosa junto ao rio
      for (let y = 12; y <= 33; y++) {
        if (grid[y][16].h === 0) grid[y][16].type = 'sand';
        if (grid[y][20].h === 0) grid[y][20].type = 'sand';
      }
      // Ponte de madeira central em gy=18..19 (Z=2 sobre a água)
      fillRect(16, 18, 20, 19, 2, 'bridge', 'Ponte do Rio');
      // Pedras de travessia ao sul em gy=27 (pulo sobre água!)
      setTile(17, 27, 2, 'stone', 'Pedras do Rio');
      setTile(19, 27, 2, 'stone', 'Pedras do Rio');

      // 4. TERRAÇOS DOS ARBUSTOS (Noroeste: gx=3..14, gy=3..12)
      fillRect(3, 5, 15, 12, 16, 'grass', 'Terraços Verdes');
      // Acesso suave ao terraço pela borda sul-leste (Z=6 em gx=11..12, gy=13 -> sobe pra 16 com pulo)
      fillRect(11, 13, 12, 13, 6, 'grass', 'Terraços Verdes');
      // Segundo patamar Z=32 (alcançável com 1 pulo a partir de Z=16!)
      fillRect(4, 3, 10, 8, 32, 'grass', 'Terraços Verdes');
      // Terceiro patamar Z=48 no canto noroeste (alcançável a partir de Z=32!)
      fillRect(3, 3, 5, 5, 48, 'stone', 'Mirante Oeste');

      // 5. BOSQUE DOS COGUMELOS SALTITANTES (Sudeste: gx=21..33, gy=21..33)
      fillRect(21, 21, 33, 33, 0, 'grass', 'Bosque dos Cogumelos');
      fillRect(21, 18, 25, 22, 0, 'path', 'Bosque dos Cogumelos');
      // Colinas onduladas no leste do bosque
      fillRect(29, 24, 32, 31, 6, 'grass', 'Bosque dos Cogumelos');
      fillRect(30, 26, 32, 29, 16, 'grass', 'Bosque dos Cogumelos');
      // Plataforma de apoio para o cogumelo mais alto (em Z=12 -> topo cogumelo em 28!)
      fillRect(26, 23, 28, 25, 12, 'stone', 'Bosque dos Cogumelos');

      // 6. MONTANHA DO PICO SAKURA & CACHOEIRA (Nordeste: gx=21..33, gy=2..16)
      // Base da montanha com paredão oeste/sul íngreme intransponível (ΔZ=48..64)
      fillRect(22, 3, 33, 16, 0, 'grass', 'Montanha Sakura');
      // Paredão Sudoeste íngreme (subindo abrupto de 0 para 48 e 64!)
      fillRect(21, 7, 29, 14, 48, 'stone', 'Paredão da Cachoeira');
      fillRect(22, 6, 29, 12, 64, 'stone', 'Montanha Sakura');

      // Nascente de água no alto do paredão despejando no rio (cachoeira visual!)
      fillRect(20, 10, 22, 11, 48, 'water', 'Cachoeira Sakura');
      setTile(19, 10, 24, 'water', 'Queda d\'Água');
      setTile(19, 11, 24, 'water', 'Queda d\'Água');

      // Trilha em espiral pelo Leste/Norte com degraus transponíveis (12 -> 24 -> 36 -> 48 -> 64 -> 80)
      fillRect(30, 15, 33, 16, 12, 'path', 'Trilha da Montanha');
      fillRect(31, 13, 33, 14, 24, 'path', 'Trilha da Montanha');
      fillRect(31, 10, 33, 12, 36, 'path', 'Trilha da Montanha');
      fillRect(30, 6,  33, 9,  48, 'path', 'Trilha da Montanha');
      fillRect(26, 3,  31, 5,  64, 'stone', 'Trilha da Montanha');

      // Cume monumental Z=80!
      fillRect(24, 6, 28, 9, 80, 'peak', 'Pico Sakura (Z=80)');
      // Rampa intermediária garantindo ligação limpa de Z=64 para Z=80
      fillRect(25, 5, 27, 5, 64, 'stone', 'Trilha da Montanha');
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
    // 5. PROPS VOXEL NO MAPA & COLECIONÁVEIS (10 Peixes Dourados)
    // =========================================================================
    const props = [];
    const mushroomPlatforms = [];
    const fishes = [];

    function addProp(modelKey, gx, gy, options = {}) {
      const t = getTile(gx, gy);
      if (!t) return;
      const c = tileCenter(gx, gy);
      const scale = options.scale || 1.0;
      const liftZ = options.liftZ !== undefined ? options.liftZ : t.h;
      const item = {
        id: `${modelKey}_${gx}_${gy}_${props.length}`,
        modelKey,
        model: propModels[modelKey],
        wx: c.wx + (options.ox || 0),
        wy: c.wy + (options.oy || 0),
        wz: liftZ,
        selfAngle: options.angle || 0,
        scale,
        radius: options.radius || 7,
        isFire: modelKey === 'campfire'
      };
      props.push(item);

      if (modelKey === 'mushroom_giant') {
        mushroomPlatforms.push({
          wx: item.wx,
          wy: item.wy,
          r: 7.8 * scale,
          topZ: item.wz + 16 * scale
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
      // Clareira do Spawn
      addProp('campfire', 8, 16);
      addProp('wood_sign', 12, 17, { angle: 0.25 });
      addProp('flower_tuft', 7, 19);
      addProp('flower_tuft', 13, 20);
      addProp('bush_berry', 5, 16);
      addProp('pine_tree', 4, 19, { radius: 9 });

      // Ruínas da Escala (Sudoeste)
      addProp('ruin_pillar', 4, 25);
      addProp('ruin_pillar', 14, 25);
      addProp('boulder_large', 6, 31);
      addProp('flower_tuft', 9, 31);
      addProp('bush_berry', 14, 30);

      // Terraços Noroeste
      addProp('bush_berry', 13, 8);
      addProp('flower_tuft', 12, 10);
      addProp('pine_tree', 6, 10, { radius: 9 });
      addProp('ruin_pillar', 4, 4);
      addProp('boulder_large', 9, 5);

      // Bosque dos Cogumelos Saltitantes (Sudeste)
      addProp('mushroom_giant', 24, 25); // Plataforma Z=16!
      addProp('mushroom_giant', 27, 24); // Em Z=12 -> Plataforma Z=28!
      addProp('mushroom_giant', 30, 28); // Plataforma Z=16!
      addProp('pine_tree', 22, 23, { radius: 9 });
      addProp('pine_tree', 25, 30, { radius: 9 });
      addProp('pine_tree', 31, 22, { radius: 9 });
      addProp('pine_tree', 29, 32, { radius: 9 });
      addProp('bush_berry', 23, 28);
      addProp('flower_tuft', 26, 27);
      addProp('flower_tuft', 31, 27);

      // Montanha & Pico Sakura (Nordeste)
      addProp('pine_tree', 32, 16, { radius: 9 });
      addProp('boulder_large', 24, 13);
      addProp('flower_tuft', 28, 8);
      addProp('flower_tuft', 25, 8);
      addProp('sakura_oak', 26, 6, { scale: 1.0, radius: 13 });

      // Bordas florestadas externas
      for (const [tx, ty] of [[1, 8], [1, 22], [1, 30], [8, 1], [14, 1], [34, 8], [34, 19], [34, 29], [8, 34], [24, 34]]) {
        addProp('pine_tree', tx, ty, { radius: 9 });
      }

      // 10 PEIXES DOURADOS COLECIONÁVEIS espalhados pelas 6 regiões!
      addFish(8, 13, 'Rampa da Clareira');          // #1 (Z=6, sobe andando)
      addFish(11, 27, 'Torre das Ruínas');          // #2 (Z=48, exige escalar via Z=32)
      addFish(18, 18, 'Meio da Ponte');             // #3 (Z=2, ponte do rio)
      addFish(19, 27, 'Pedra do Rio');              // #4 (Z=2, pulo sobre a água)
      addFish(7, 6, 'Terraço Verde');               // #5 (Z=32, platô noroeste)
      addFish(4, 3, 'Mirante das Ruínas');          // #6 (Z=48, pico noroeste)
      addFish(27, 24, 'Cogumelo Gigante', 16);      // #7 (Z=28 no topo do cogumelo!)
      addFish(32, 11, 'Mirante da Trilha');         // #8 (Z=36 na subida leste)
      addFish(28, 4, 'Beira do Abismo');            // #9 (Z=64 perto do cume)
      addFish(27, 8, 'Pico Sakura Lendário');       // #10 (Z=80 sob a cerejeira!)
    }
    populateWorldObjects();

    // =========================================================================
    // 6. ESTADO DO GATO, FÍSICA DE PULO 2×H & PARTÍCULAS
    // =========================================================================
    const spawnCenter = tileCenter(10, 18);
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
      speech: { text: 'Miau! Bora explorar! 🐾', timer: 180 },
      lastSafeX: spawnCenter.wx,
      lastSafeY: spawnCenter.wy,
      lastSafeZ: 0,
      maxJumpReached: 0,
      obstacleHint: 'ok',
      obstacleLabel: '✅ Caminho Livre'
    };

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
          life: 0.45 + Math.random() * 0.35,
          maxLife: 0.8,
          color: colors[i % colors.length],
          size: 2
        });
      }
    }

    function catSpeak(text, timer = 135) {
      cat.speech = { text, timer };
    }

    // Avalia suporte máximo sob (wx, wy) considerando tiles sólidos e chapéus de cogumelo
    function evaluateSupport(wx, wy, currentZ) {
      const r = 2.6;
      const samples = [
        [wx, wy],
        [wx - r, wy], [wx + r, wy],
        [wx, wy - r], [wx, wy + r]
      ];
      let bestH = -999;
      let anyWater = false;
      let centerWater = false;
      const ct = worldToTileCoords(wx, wy);
      const centerTile = getTile(ct.gx, ct.gy);
      if (centerTile && centerTile.type === 'water') centerWater = true;

      for (const [sx, sy] of samples) {
        const tc = worldToTileCoords(sx, sy);
        const t = getTile(tc.gx, tc.gy);
        if (!t) continue;
        if (t.type === 'water') {
          anyWater = true;
        } else if (t.h <= currentZ + AUTO_STEP_MAX + 0.5) {
          if (t.h > bestH) bestH = t.h;
        }
      }

      for (const mp of mushroomPlatforms) {
        const d = Math.hypot(wx - mp.wx, wy - mp.wy);
        if (d <= mp.r && mp.topZ <= currentZ + AUTO_STEP_MAX + 0.5) {
          if (mp.topZ > bestH) bestH = mp.topZ;
        }
      }

      return { bestH, anyWater, centerWater, centerTile };
    }

    // Avalia o tile/plataforma mais alto tocado por (nx, ny) para checar colisão lateral
    function checkCollisionAt(nx, ny, catZ, onGround) {
      if (nx < WORLD_MIN + 6 || nx > WORLD_MAX - 6 || ny < WORLD_MIN + 6 || ny > WORLD_MAX - 6) {
        return { blocked: true, reason: 'high', maxStepH: 999 };
      }

      const r = 2.8;
      const pts = [
        [nx, ny],
        [nx - r, ny - r], [nx + r, ny - r],
        [nx - r, ny + r], [nx + r, ny + r]
      ];

      // Bloqueio imediato na água se estiver andando rente à água
      const ct = worldToTileCoords(nx, ny);
      const centerTile = getTile(ct.gx, ct.gy);
      if (centerTile && centerTile.type === 'water' && (onGround || catZ <= 1.2)) {
        return { blocked: true, reason: 'water', maxStepH: -8 };
      }

      const allowedClimb = onGround ? AUTO_STEP_MAX : 1.5;
      let blocked = false;
      let maxBlockingH = -999;

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

      for (const mp of mushroomPlatforms) {
        const d = Math.hypot(nx - mp.wx, ny - mp.wy);
        if (d <= mp.r - 1.5 && mp.topZ > catZ + allowedClimb) {
          blocked = true;
          if (mp.topZ > maxBlockingH) maxBlockingH = mp.topZ;
        }
      }

      if (blocked) {
        const diff = maxBlockingH - cat.groundZ;
        return {
          blocked: true,
          reason: diff <= CAT_HEIGHT * 2.0 + 0.5 ? 'jump' : 'high',
          maxStepH: maxBlockingH
        };
      }
      return { blocked: false, reason: 'ok', maxStepH: catZ };
    }

    // Sensor frontal de obstáculo para exibir no HUD mesmo parado de frente pro degrau
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
        cat.obstacleLabel = '💧 Rio Intransponível (Pule p/ Ponte/Pedra)';
        return;
      }

      let targetH = t.h;
      for (const mp of mushroomPlatforms) {
        if (Math.hypot(probeX - mp.wx, probeY - mp.wy) <= mp.r + 2) {
          if (mp.topZ > targetH) targetH = mp.topZ;
        }
      }

      const dz = targetH - cat.groundZ;
      if (dz <= AUTO_STEP_MAX) {
        cat.obstacleHint = 'ok';
        cat.obstacleLabel = dz > 0.5 ? '✅ Rampa Suave (≤0.4H)' : '✅ Caminho Livre';
      } else if (dz <= CAT_HEIGHT * 2.0 + 0.5) {
        cat.obstacleHint = 'jump';
        cat.obstacleLabel = `🦘 Degrau ${Math.round(dz)}u — Pule com Espaço!`;
      } else {
        cat.obstacleHint = 'high';
        cat.obstacleLabel = `⛔ Paredão ${Math.round(dz)}u (> 2×H Intransponível)`;
      }
    }

    // =========================================================================
    // 7. CONTROLES & CÂMERA (WASD Relativo à Câmera + Espaço + Q/E + Arraste)
    // =========================================================================
    const keys = {};
    let turn = -Math.PI * 0.25;
    let targetTurn = turn;
    let squash = 0.72;
    let camX = cat.x;
    let camY = cat.y;
    let camZ = cat.z;
    let blockedCooldown = 0;

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
        sfxMeow();
        catSpeak('Miau! 🐾', 110);
      }
    });

    window.addEventListener('keyup', (e) => {
      keys[e.code] = false;
    });

    function resetCatToSpawn() {
      cat.x = spawnCenter.wx;
      cat.y = spawnCenter.wy;
      cat.z = 0;
      cat.vz = 0;
      cat.groundZ = 0;
      cat.onGround = true;
      cat.lastSafeX = cat.x;
      cat.lastSafeY = cat.y;
      cat.lastSafeZ = 0;
      catSpeak('De volta à clareira! 🏡', 120);
    }

    const canvas = document.getElementById('viewport');
    const ctx = canvas.getContext('2d');
    const LOW_W = 480;
    const LOW_H = 300;
    const lowCanvas = document.createElement('canvas');
    lowCanvas.width = LOW_W;
    lowCanvas.height = LOW_H;
    const lowCtx = lowCanvas.getContext('2d');
    lowCtx.imageSmoothingEnabled = false;

    // Scratch canvas com contorno único 1px (zero listras entre fatias!)
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

    // Botões HUD
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

    // =========================================================================
    // 8. UPDATE FÍSICO (Delta Time Fixo & Seguro)
    // =========================================================================
    function updatePhysics(dt) {
      cat.idleTimer += dt;
      if (blockedCooldown > 0) blockedCooldown -= dt;

      if (keys['KeyQ']) targetTurn += 2.2 * dt;
      if (keys['KeyE']) targetTurn -= 2.2 * dt;
      turn += (targetTurn - turn) * Math.min(1, dt * 14);

      // Input direcional na tela -> Mundo 3D rotacionado por `turn`
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
        // Inversa da rotação de projeção `project()` para mapear W=Cima da Tela, D=Direita da Tela
        moveWorldX = ix * cosA + iy * sinA;
        moveWorldY = -ix * sinA + iy * cosA;
        cat.isWalking = true;

        // Direção frontal do gato (+Y local = Frente): Math.atan2(-dx, dy)
        const desiredAngle = Math.atan2(-moveWorldX, moveWorldY);
        let diff = desiredAngle - cat.selfAngle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        cat.selfAngle += diff * Math.min(1, dt * 18);
      } else {
        cat.isWalking = false;
      }

      // Movimento horizontal com deslize separado em X e Y
      const speed = cat.onGround ? 86 : 78;
      if (ilen > 0) {
        const dx = moveWorldX * speed * dt;
        const dy = moveWorldY * speed * dt;

        let blockedNow = null;

        if (dx !== 0) {
          const checkX = checkCollisionAt(cat.x + dx, cat.y, cat.z, cat.onGround);
          if (!checkX.blocked) {
            cat.x += dx;
          } else {
            blockedNow = checkX;
          }
        }
        if (dy !== 0) {
          const checkY = checkCollisionAt(cat.x, cat.y + dy, cat.z, cat.onGround);
          if (!checkY.blocked) {
            cat.y += dy;
          } else {
            blockedNow = checkY;
          }
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

      // Coyote Time + Jump Buffer
      if (cat.onGround) {
        cat.coyoteTimer = 0.11;
      } else {
        cat.coyoteTimer = Math.max(0, cat.coyoteTimer - dt);
      }
      if (cat.jumpBuffer > 0) {
        cat.jumpBuffer = Math.max(0, cat.jumpBuffer - dt);
      }

      // Executar Pulo (2x a altura do gato = 32u!)
      if (cat.jumpBuffer > 0 && cat.coyoteTimer > 0) {
        cat.vz = JUMP_VEL;
        cat.onGround = false;
        cat.coyoteTimer = 0;
        cat.jumpBuffer = 0;
        cat.maxJumpReached = cat.z;
        sfxJump();
        spawnParticles(cat.x, cat.y, cat.z + 1, 7, ['#FFF8EC', '#E7D8C2'], 22);
      }

      // Gravidade & Vertical
      const wasOnGround = cat.onGround;
      cat.vz -= GRAVITY * dt;
      cat.z += cat.vz * dt;
      if (cat.z > cat.maxJumpReached) cat.maxJumpReached = cat.z;

      const sup = evaluateSupport(cat.x, cat.y, cat.z);
      if (sup.bestH > -900) {
        cat.groundZ = sup.bestH;
        // Pouso ou Auto-Step suave
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
          // Rampa suave subindo andando!
          cat.z = sup.bestH;
          cat.vz = 0;
          cat.onGround = true;
          cat.lastSafeX = cat.x;
          cat.lastSafeY = cat.y;
          cat.lastSafeZ = cat.z;
        } else if (wasOnGround && sup.bestH < cat.z && cat.z - sup.bestH <= 4) {
          // Desce degrau pequeno suavemente colado no chão
          cat.z = sup.bestH;
          cat.vz = 0;
          cat.onGround = true;
        } else if (cat.z > sup.bestH + 0.5) {
          cat.onGround = false;
        }
      } else {
        // Sem suporte sólido sob o gato (caindo sobre água!)
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

      // Coletar Peixes Dourados!
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
          catSpeak(`Peixinho! (${collectedCount}/10) 🐟✨`, 130);
          spawnParticles(f.wx, f.wy, f.baseZ + 6, 16, ['#FBBF24', '#FEF08A', '#F97316', '#FFFFFF'], 42);
        }
      }
      document.getElementById('fishCounter').textContent = `🐟 ${collectedCount} / ${fishes.length}`;

      // Atualizar sensor de obstáculo & telemetria HUD
      updateObstacleSensor(moveWorldX, moveWorldY);
      const curTile = sup.centerTile;
      document.getElementById('biomeLabel').textContent = curTile ? curTile.biome : 'Vale Felino';
      document.getElementById('statElev').textContent = `Chão: Z=${Math.round(cat.groundZ)} | Gato: Z=${Math.round(cat.z)}`;
      const obsEl = document.getElementById('statObstacle');
      obsEl.textContent = cat.obstacleLabel;
      obsEl.className = 'obstacle-chip obs-' + cat.obstacleHint;

      // Atualizar Partículas
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vz -= 260 * dt;
        p.z += p.vz * dt;
        p.life -= dt;
        if (p.life <= 0) particles.splice(i, 1);
      }

      // Suavizar câmera seguindo o gato
      const lerpFactor = Math.min(1, dt * 8.5);
      camX += (cat.x - camX) * lerpFactor;
      camY += (cat.y - camY) * lerpFactor;
      camZ += (cat.groundZ + (cat.z - cat.groundZ) * 0.45 - camZ) * Math.min(1, dt * 6.5);
    }

    // =========================================================================
    // 9. MOTOR DE RENDERIZAÇÃO VOXEL 3D (Pure Canvas 2D)
    // =========================================================================
    let cachedTurnAngle = null;
    const propOutlineCache = {};

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
        y: Math.round(LOW_H / 2 + 22 + ry * squash - dz),
        depth: ry
      };
    }

    function drawQuad(p1, p2, p3, p4, fillStyle, strokeSame = true) {
      lowCtx.beginPath();
      lowCtx.moveTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.lineTo(p4.x, p4.y);
      lowCtx.closePath();
      lowCtx.fillStyle = fillStyle;
      lowCtx.fill();
      if (strokeSame) {
        lowCtx.strokeStyle = fillStyle;
        lowCtx.lineWidth = 0.75;
        lowCtx.stroke();
      }
    }

    // Paleta topográfica do terreno com sombreamento direcional entre X e Y
    function getTopColor(t, animTick) {
      const n = ((t.gx * 73856093) ^ (t.gy * 19349663)) & 3;
      if (t.type === 'water') {
        const wave = ((t.gx + t.gy + animTick) % 6 === 0);
        return wave ? '#7DD3FC' : (n === 0 ? '#38BDF8' : '#2EB5F0');
      }
      if (t.type === 'bridge') return n % 2 === 0 ? '#B97A4A' : '#A66A3E';
      if (t.type === 'stone') {
        if (t.h >= 48) return n % 2 === 0 ? '#9CA3AF' : '#8E96A4';
        return n % 2 === 0 ? '#B4BAC4' : '#A3AAB5';
      }
      if (t.type === 'path') return n % 2 === 0 ? '#DFB684' : '#D3A673';
      if (t.type === 'sand') return n % 2 === 0 ? '#F3DDA9' : '#EAD094';
      if (t.type === 'peak') return n % 2 === 0 ? '#F9A8D4' : '#7BC96F';
      // Grass com micro-variação por elevação
      if (t.h >= 32) return n === 0 ? '#78D064' : (n === 1 ? '#6EC45B' : '#65BA53');
      if (t.h >= 12) return n === 0 ? '#69C257' : (n === 1 ? '#5EB74D' : '#56AE45');
      return n === 0 ? '#5CB852' : (n === 1 ? '#53AD49' : '#4BA242');
    }

    // Cache de sprite já contornado para os props estáticos no ângulo atual
    function getOutlinedPropSprite(modelKey, model) {
      const qAngle = Math.round(turn * 180 / Math.PI);
      if (cachedTurnAngle !== qAngle) {
        cachedTurnAngle = qAngle;
        for (const k in propOutlineCache) delete propOutlineCache[k];
      }
      if (propOutlineCache[modelKey]) return propOutlineCache[modelKey];

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
        tctx.rotate(turn);
        tctx.drawImage(model.sheet, z * model.w, 0, model.w, model.h, -originX, -originY, model.w, model.h);
        tctx.restore();
      }

      // Gerar silhueta colorida de contorno único 1px (#3B2219)
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
      propOutlineCache[modelKey] = entry;
      return entry;
    }

    function drawStaticProp(p) {
      const proj = project(p.wx, p.wy, p.wz);
      const spr = getOutlinedPropSprite(p.modelKey, p.model);
      const dw = Math.round(spr.canvas.width * p.scale);
      const dh = Math.round(spr.canvas.height * p.scale);
      const dx = Math.round(proj.x - spr.ox * p.scale);
      const dy = Math.round(proj.y - spr.oy * p.scale);
      lowCtx.drawImage(spr.canvas, dx, dy, dw, dh);

      // Brilho animado para fogueira
      if (p.isFire) {
        const flick = Math.sin(cat.idleTimer * 12) * 1.5;
        lowCtx.fillStyle = 'rgba(255, 210, 80, 0.35)';
        lowCtx.beginPath();
        lowCtx.arc(proj.x, proj.y - 6, 6 + flick * 0.4, 0, Math.PI * 2);
        lowCtx.fill();
      }
    }

    // Desenho de stack arbitrário em tempo real no scratchCanvas (com contorno único!)
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

      // Tint silhueta em silCanvas e carimbar 4 offsets + corpo no lowCtx
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

    function drawCatShadow() {
      const shP = project(cat.x, cat.y, Math.max(cat.groundZ, -5) + 0.3);
      const heightAboveGround = Math.max(0, cat.z - cat.groundZ);
      const shrink = Math.max(0.45, 1.0 - heightAboveGround / 55);
      const rx = 6.5 * shrink;
      const ry = 4.2 * shrink;
      lowCtx.fillStyle = `rgba(38, 22, 14, ${0.32 * shrink})`;
      lowCtx.beginPath();
      lowCtx.ellipse(shP.x, shP.y, rx, ry, 0, 0, Math.PI * 2);
      lowCtx.fill();
    }

    function drawCatEntity() {
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

      // Balão de fala do gato
      if (cat.speech && cat.speech.timer > 0) {
        cat.speech.timer--;
        const sp = project(cat.x, cat.y, cat.z + 24);
        lowCtx.save();
        lowCtx.font = 'bold 8px sans-serif';
        const tw = lowCtx.measureText(cat.speech.text).width;
        const bw = tw + 8;
        const bh = 12;
        const bx = Math.round(sp.x - bw / 2);
        const by = Math.round(sp.y - 12);
        lowCtx.fillStyle = '#FFFDF9';
        lowCtx.strokeStyle = '#3B2219';
        lowCtx.lineWidth = 1;
        lowCtx.fillRect(bx, by, bw, bh);
        lowCtx.strokeRect(bx, by, bw, bh);
        lowCtx.fillStyle = '#3B2219';
        lowCtx.fillText(cat.speech.text, bx + 4, by + 9);
        lowCtx.restore();
      }
    }

    function drawFishCollectible(f) {
      const bob = Math.sin(cat.idleTimer * 3.5 + f.gx) * 2.2;
      const wz = f.baseZ + 4 + bob;
      const spinAngle = cat.idleTimer * 2.5 + f.gx;

      // Sombra no chão abaixo do peixinho
      const sp = project(f.wx, f.wy, f.baseZ + 0.3);
      lowCtx.fillStyle = 'rgba(180, 120, 20, 0.25)';
      lowCtx.beginPath();
      lowCtx.ellipse(sp.x, sp.y, 5, 3, 0, 0, Math.PI * 2);
      lowCtx.fill();

      drawDynamicStackWithOutline((stamp) => {
        stamp(propModels.golden_fish, f.wx, f.wy, wz, spinAngle, 1.0);
      }, f.wx, f.wy, wz);
    }

    // Desenha uma face lateral de coluna de terreno com estratos (grama pendurada + terra + rocha / água cachoeira)
    function drawColumnSideFace(xA, yA, xB, yB, topZ, bottomZ, isXFace, tile, animTick) {
      if (topZ <= bottomZ) return;

      // Cachoeira ou lado de água!
      if (tile.type === 'water' && topZ > 0) {
        const pTopA = project(xA, yA, topZ);
        const pTopB = project(xB, yB, topZ);
        const pBotA = project(xA, yA, bottomZ);
        const pBotB = project(xB, yB, bottomZ);
        drawQuad(pTopA, pTopB, pBotB, pBotA, isXFace ? '#38BDF8' : '#0284C7');
        // Faixas brancas animadas caindo em 8 FPS
        const fallOffset = (animTick % 4) * 3;
        lowCtx.strokeStyle = '#E0F2FE';
        lowCtx.lineWidth = 1;
        for (let t = 0.25; t <= 0.8; t += 0.3) {
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

      // Cores com iluminação direcional distinta entre face X e face Y
      const grassLipCol = isXFace ? '#3D8C37' : '#2C6B28';
      const dirtCol     = isXFace ? '#9B6542' : '#73482E';
      const rockCol     = isXFace ? '#646E7A' : '#48515C';
      const darkRockCol = isXFace ? '#4D5560' : '#353C45';

      // Faixa 1: Borda de Grama/Pedra superior (~3u)
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
      drawQuad(pTopA, pTopB, pLipB, pLipA, lipColor);

      if (lipZ <= bottomZ) return;

      // Faixa 2: Terra ou Rocha principal
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
        drawQuad(pLipA, pLipB, pBotB, pBotA, dirtCol);
      }
    }

    // Calcula em qual bucket (gx, gy) colocar uma entidade para que nenhuma terra plana a cubra
    // mas penhascos mais altos na frente a escondam corretamente!
    function pickEntityBucketCell(wx, wy, wz, radius, sinA, cosA) {
      let bestGx = null, bestGy = null, bestDepth = -Infinity;
      const gMinX = Math.max(0, Math.floor((wx - radius) / TILE + HALF_GRID));
      const gMaxX = Math.min(GRID_SIZE - 1, Math.floor((wx + radius) / TILE + HALF_GRID));
      const gMinY = Math.max(0, Math.floor((wy - radius) / TILE + HALF_GRID));
      const gMaxY = Math.min(GRID_SIZE - 1, Math.floor((wy + radius) / TILE + HALF_GRID));

      for (let gy = gMinY; gy <= gMaxY; gy++) {
        for (let gx = gMinX; gx <= gMaxX; gx++) {
          const t = grid[gy][gx];
          if (t.h <= wz + 3.2) {
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

    function renderScene() {
      // Céu ensolarado com nuvens suaves
      const skyGrad = lowCtx.createLinearGradient(0, 0, 0, LOW_H);
      skyGrad.addColorStop(0, '#78C8F2');
      skyGrad.addColorStop(0.6, '#BEE8FB');
      skyGrad.addColorStop(1, '#F3E7D3');
      lowCtx.fillStyle = skyGrad;
      lowCtx.fillRect(0, 0, LOW_W, LOW_H);

      // Nuvens fofas pixeladas no horizonte
      const cloudShift = (cat.idleTimer * 6) % (LOW_W + 120);
      lowCtx.fillStyle = 'rgba(255, 255, 255, 0.72)';
      for (const [cx0, cy0, w0] of [[40, 28, 46], [190, 18, 60], [340, 38, 42]]) {
        const xPos = ((cx0 + cloudShift) % (LOW_W + 80)) - 40;
        lowCtx.fillRect(Math.round(xPos), cy0, w0, 10);
        lowCtx.fillRect(Math.round(xPos + 8), cy0 - 5, w0 - 16, 6);
      }

      const sinA = Math.sin(turn);
      const cosA = Math.cos(turn);
      const animTick = Math.floor(cat.idleTimer * 8); // 8 FPS stepped animation!

      // Distribuir entidades nos buckets das células do grid
      const buckets = new Map();
      const pushToBucket = (cellIdx, fn, depthKey) => {
        if (!buckets.has(cellIdx)) buckets.set(cellIdx, []);
        buckets.get(cellIdx).push({ fn, depthKey });
      };

      // Props estáticos
      for (const p of props) {
        const cIdx = pickEntityBucketCell(p.wx, p.wy, p.wz, p.radius, sinA, cosA);
        const dp = (p.wx - camX) * sinA + (p.wy - camY) * cosA;
        pushToBucket(cIdx, () => drawStaticProp(p), dp);
      }

      // Peixes Dourados
      for (const f of fishes) {
        if (f.collected) continue;
        const cIdx = pickEntityBucketCell(f.wx, f.wy, f.baseZ, 4.5, sinA, cosA);
        const dp = (f.wx - camX) * sinA + (f.wy - camY) * cosA;
        pushToBucket(cIdx, () => drawFishCollectible(f), dp);
      }

      // Gato Jogável (+ sombra)
      {
        const catCell = pickEntityBucketCell(cat.x, cat.y, cat.z, 4.8, sinA, cosA);
        const dp = (cat.x - camX) * sinA + (cat.y - camY) * cosA;
        pushToBucket(catCell, () => {
          drawCatShadow();
          drawCatEntity();
        }, dp + 0.5);
      }

      // Traversão O(W*H) estritamente Back-to-Front em 360° sem Array.sort
      const stepX = sinA >= 0 ? 1 : -1;
      const stepY = cosA >= 0 ? 1 : -1;
      const startX = stepX > 0 ? 0 : GRID_SIZE - 1;
      const endX   = stepX > 0 ? GRID_SIZE : -1;
      const startY = stepY > 0 ? 0 : GRID_SIZE - 1;
      const endY   = stepY > 0 ? GRID_SIZE : -1;

      // Raio de culling em torno do centro da câmera (~18 tiles cobre 480x300 inteiro)
      const camTile = worldToTileCoords(camX, camY);

      for (let gy = startY; gy !== endY; gy += stepY) {
        if (Math.abs(gy - camTile.gy) > 21) continue;
        for (let gx = startX; gx !== endX; gx += stepX) {
          if (Math.abs(gx - camTile.gx) > 21) continue;
          const t = grid[gy][gx];
          const x0 = (gx - HALF_GRID) * TILE;
          const x1 = x0 + TILE;
          const y0 = (gy - HALF_GRID) * TILE;
          const y1 = y0 + TILE;
          const topZ = t.h;

          // Desenhar apenas as 2 faces verticais voltadas à câmera
          if (sinA > 0.001) {
            const nb = getTile(gx + 1, gy);
            const botZ = nb ? nb.h : SKIRT_BOTTOM;
            drawColumnSideFace(x1, y0, x1, y1, topZ, botZ, true, t, animTick);
          } else if (sinA < -0.001) {
            const nb = getTile(gx - 1, gy);
            const botZ = nb ? nb.h : SKIRT_BOTTOM;
            drawColumnSideFace(x0, y0, x0, y1, topZ, botZ, true, t, animTick);
          }

          if (cosA > 0.001) {
            const nb = getTile(gx, gy + 1);
            const botZ = nb ? nb.h : SKIRT_BOTTOM;
            drawColumnSideFace(x0, y1, x1, y1, topZ, botZ, false, t, animTick);
          } else if (cosA < -0.001) {
            const nb = getTile(gx, gy - 1);
            const botZ = nb ? nb.h : SKIRT_BOTTOM;
            drawColumnSideFace(x0, y0, x1, y0, topZ, botZ, false, t, animTick);
          }

          // Topo da coluna (com espessura de saia de água caso topZ == -8)
          const p00 = project(x0, y0, topZ);
          const p10 = project(x1, y0, topZ);
          const p11 = project(x1, y1, topZ);
          const p01 = project(x0, y1, topZ);
          drawQuad(p00, p10, p11, p01, getTopColor(t, animTick));

          // Florzinhas pixeladas leves em tiles de prado ou pico
          if (t.type === 'grass' && ((gx * 13 + gy * 7) % 11 === 0)) {
            const cp = project((x0 + x1) * 0.5, (y0 + y1) * 0.5, topZ + 0.5);
            lowCtx.fillStyle = (gx + gy) % 2 === 0 ? '#FDE047' : '#FFF1F2';
            lowCtx.fillRect(cp.x, cp.y, 2, 2);
          }

          // Renderizar entidades cujo bucket aponta para este tile
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

      // Renderizar Partículas 3D
      for (const p of particles) {
        const pp = project(p.x, p.y, p.z);
        lowCtx.fillStyle = p.color;
        lowCtx.fillRect(pp.x, pp.y, p.size, p.size);
      }

      // Upscale nítido Nearest-Neighbor para o Viewport inteiro
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);
    }

    // =========================================================================
    // 10. MINIMAPA TOPOGRÁFICO EM TEMPO REAL
    // =========================================================================
    const mmCanvas = document.getElementById('minimapCanvas');
    const mmCtx = mmCanvas.getContext('2d');
    const mmBase = document.createElement('canvas');
    mmBase.width = GRID_SIZE * 3;
    mmBase.height = GRID_SIZE * 3;
    const mmBaseCtx = mmBase.getContext('2d');

    function bakeMinimapBase() {
      for (let gy = 0; gy < GRID_SIZE; gy++) {
        for (let gx = 0; gx < GRID_SIZE; gx++) {
          const t = grid[gy][gx];
          let col = '#65C466';
          if (t.type === 'water') col = '#38BDF8';
          else if (t.type === 'bridge') col = '#B97A4A';
          else if (t.h >= 80) col = '#F472B6';
          else if (t.h >= 64) col = '#9CA3AF';
          else if (t.h >= 48) col = '#A8B1BD';
          else if (t.h >= 32) col = '#94A3B8';
          else if (t.h >= 16) col = '#4EA94C';
          else if (t.type === 'path') col = '#DFB684';
          mmBaseCtx.fillStyle = col;
          mmBaseCtx.fillRect(gx * 3, gy * 3, 3, 3);
        }
      }
    }
    bakeMinimapBase();

    function drawMinimap() {
      mmCtx.imageSmoothingEnabled = false;
      mmCtx.drawImage(mmBase, 0, 0);

      // Peixes restantes em dourado
      for (const f of fishes) {
        if (f.collected) continue;
        mmCtx.fillStyle = '#FACC15';
        mmCtx.fillRect(f.gx * 3, f.gy * 3, 3, 3);
      }

      // Posição e direção do gato em vermelho
      const cx = (cat.x / TILE + HALF_GRID) * 3;
      const cy = (cat.y / TILE + HALF_GRID) * 3;
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
    // 11. LOOP PRINCIPAL & RESIZE + DEBUG HOOKS
    // =========================================================================
    function handleResize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      ctx.imageSmoothingEnabled = false;
    }
    window.addEventListener('resize', handleResize);
    handleResize();

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

    // Hooks leves para inspeção e validação matemática/Playwright
    window.__TERRAIN_DEBUG__ = {
      getState: () => ({
        x: cat.x, y: cat.y, z: cat.z, vz: cat.vz,
        groundZ: cat.groundZ, onGround: cat.onGround,
        selfAngle: cat.selfAngle, turn,
        maxJumpReached: cat.maxJumpReached,
        obstacleHint: cat.obstacleHint,
        obstacleLabel: cat.obstacleLabel,
        speech: cat.speech ? cat.speech.text : null,
        collectedFish: fishes.filter(f => f.collected).length
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
      setTurn: (rad) => {
        turn = rad;
        targetTurn = rad;
      },
      triggerJump: () => {
        cat.jumpBuffer = 0.14;
      },
      setKey: (code, pressed) => {
        keys[code] = pressed;
      },
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
    .replace('__PROPS_PACK__', json.dumps(props_pack))
)

out_path = os.path.join(ROOT, 'terrain-world.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_out)

print(f'SUCCESS: Generated {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)')
