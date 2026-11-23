import json

with open('C:/github/PixelArt/slices_v5.json', 'r', encoding='utf-8') as f:
    slices_raw = json.load(f)

# Criando slices do corpo (fatias 0 e 1 sem as patas)
cat_body_slices = [ [list(r) for r in s] for s in slices_raw ]
for z in (0, 1):
    for y in range(32):
        for x in range(32):
            cat_body_slices[z][y][x] = '0'

cat_body_slices = [[''.join(r) for r in s] for s in cat_body_slices]

# Criando slices de 1 patinha (4x4, 2 fatias com almofadinha rosa na base!)
cat_paw_slices = [
    [
        '1441',
        '4114',
        '1441',
        '1111'
    ],
    [
        '1111',
        '1111',
        '1111',
        '1111'
    ]
]

template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gatinho Pixel Art 3D - Sprite Stacking Animado</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    body {
      background: #F3EEE4;
      color: #3B2A20;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    #viewport {
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      box-shadow: 0 20px 50px rgba(74, 46, 27, 0.12);
      border-radius: 16px;
      background: #FAF7F2;
      cursor: grab;
      touch-action: none;
    }
    #viewport:active { cursor: grabbing; }
    .hud {
      position: absolute;
      bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
      background: rgba(255, 255, 255, 0.90);
      backdrop-filter: blur(12px);
      padding: 10px 20px;
      border-radius: 40px;
      border: 1px solid rgba(59, 42, 32, 0.15);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
      align-items: center;
      font-size: 13px;
      font-weight: 500;
      max-width: 90vw;
    }
    .btn {
      background: #3B2A20;
      color: #FAF7F2;
      border: none;
      padding: 7px 15px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }
    .btn:hover { background: #5A3F2F; transform: translateY(-1px); }
    .btn.active { background: #D87D4A; }
    .btn-secondary {
      background: #EDE6DA;
      color: #3B2A20;
    }
    .btn-secondary:hover {
      background: #DDD4C4;
    }
    .label { color: #6B4E3D; display: flex; align-items: center; gap: 6px; }
    input[type=range] { accent-color: #D87D4A; cursor: pointer; }
    .badge { position: absolute; top: 20px; text-align: center; }
    .badge h1 { font-size: 22px; font-weight: 700; color: #3B2A20; letter-spacing: -0.5px; }
    .badge p { font-size: 13px; color: #6B4E3D; margin-top: 4px; }
  </style>
</head>
<body>

  <div class="badge">
    <h1>🐱 Gatinho Pixel Art 3D Animado</h1>
    <p>Patinhas articuladas com almofadinhas rosa | Arraste para girar 360°</p>
  </div>

  <canvas id="viewport" width="540" height="540"></canvas>

  <div class="hud">
    <button id="btnFront" class="btn btn-secondary">Frente</button>
    <button id="btnIso" class="btn btn-secondary">3/4 Iso</button>
    <button id="btnSide" class="btn btn-secondary">Lado</button>
    <button id="btnBack" class="btn btn-secondary">Costas</button>
    <button id="btnAutoSpin" class="btn">🔄 Girar</button>
    <button id="btnWalk" class="btn active">🐾 Andar</button>
    <button id="btnSlices" class="btn btn-secondary">🥞 Fatias</button>
    <div class="label">
      <span>Inclinação:</span>
      <input type="range" id="squashSlider" min="0.60" max="0.95" step="0.01" value="0.75">
    </div>
  </div>

  <script>
    const PALETTE = [
      'rgba(0,0,0,0)',       // 0: Vazio
      '#FDFBF7',             // 1: Pelo Branco
      '#DE864A',             // 2: Laranja (Manchas)
      '#3B2219',             // 3: Olhos / Nariz / Boca
      '#F2A2AB',             // 4: Rosa (Almofadinhas / Orelha interna)
      '#FFFFFF',             // 5: Brilho branco do olho (Olho O)
      '#B85820',             // 6: Laranja escuro / Pontas das orelhas / Bigodes
      '#E5E0D8',             // 7: Sombra suave
    ];

    const OUTLINE_COLOR = '#3B2219';
    const BODY_DATA = __BODY_SLICES__;
    const PAW_DATA = __PAW_SLICES__;

    const SLICE_W = 32;
    const SLICE_H = 32;
    const COUNT = BODY_DATA.length;

    function buildSliceSheet(data, w, h) {
      const cnt = data.length;
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
            const val = parseInt(row[x], 10);
            if (val > 0) {
              cx.fillStyle = PALETTE[val];
              cx.fillRect(offX + x, y, 1, 1);
            }
          }
        }
      }
      return cv;
    }

    const bodySheet = buildSliceSheet(BODY_DATA, 32, 32);
    const pawSheet = buildSliceSheet(PAW_DATA, 4, 4);

    const canvas = document.getElementById('viewport');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    // Buffer de baixa resolução (80x80)
    const LOW_W = 80;
    const LOW_H = 80;
    const lowCanvas = document.createElement('canvas');
    lowCanvas.width = LOW_W;
    lowCanvas.height = LOW_H;
    const lowCtx = lowCanvas.getContext('2d');
    lowCtx.imageSmoothingEnabled = false;

    const stackCanvas = document.createElement('canvas');
    stackCanvas.width = LOW_W;
    stackCanvas.height = LOW_H;
    const stackCtx = stackCanvas.getContext('2d');
    stackCtx.imageSmoothingEnabled = false;

    // Inicia de FRENTE exata (turn = 0)
    let turn = 0;
    let targetTurn = 0;
    let squash = 0.75;
    let spacing = 1.0;
    let targetSpacing = 1.0;
    let autoSpin = false;
    let isWalking = true;
    let walkCycle = 0;
    let idleTimer = 0;

    function draw() {
      turn += (targetTurn - turn) * 0.12;
      spacing += (targetSpacing - spacing) * 0.1;

      if (autoSpin) {
        targetTurn += 0.012;
      }

      if (isWalking) {
        walkCycle += 0.16;
      } else {
        idleTimer += 0.05;
      }

      stackCtx.clearRect(0, 0, LOW_W, LOW_H);

      const cx = Math.floor(LOW_W / 2);
      const cy = Math.floor(LOW_H / 2) + 14;
      const originX = Math.floor(SLICE_W / 2);
      const originY = Math.floor(SLICE_H / 2);

      const t = walkCycle;
      const liftFL = isWalking ? Math.max(0, Math.sin(t) * 3.5) : 0;
      const strideFL = isWalking ? Math.cos(t) * 2.5 : 0;

      const liftBR = isWalking ? Math.max(0, Math.sin(t + 0.3) * 3.5) : 0;
      const strideBR = isWalking ? Math.cos(t + 0.3) * 2.5 : 0;

      const liftFR = isWalking ? Math.max(0, Math.sin(t + Math.PI) * 3.5) : 0;
      const strideFR = isWalking ? Math.cos(t + Math.PI) * 2.5 : 0;

      const liftBL = isWalking ? Math.max(0, Math.sin(t + Math.PI + 0.3) * 3.5) : 0;
      const strideBL = isWalking ? Math.cos(t + Math.PI + 0.3) * 2.5 : 0;

      const bodyBob = isWalking ? Math.abs(Math.sin(t * 2)) * 0.8 : Math.sin(idleTimer * 2.2) * 0.4;
      const bodyRoll = isWalking ? Math.sin(t) * 0.04 : 0;

      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);

      function renderPaw(lx, ly, lift, stride) {
        const px = cx + (lx * cosA - (ly + stride) * sinA);
        const py = cy + (lx * sinA + (ly + stride) * cosA) * squash - lift * spacing;
        const originPaw = 2;

        for (let z = 0; z < 2; z++) {
          stackCtx.save();
          stackCtx.translate(Math.round(px), Math.round(py - z * spacing));
          stackCtx.scale(1, squash);
          stackCtx.rotate(turn);
          stackCtx.drawImage(
            pawSheet,
            z * 4, 0, 4, 4,
            -originPaw, -originPaw, 4, 4
          );
          stackCtx.restore();
        }
      }

      // 1. As 4 patinhas articuladas no piso do pedestal
      renderPaw(-4.5, -7.5, liftBL, strideBL); // Traseira esquerda
      renderPaw( 3.5, -7.5, liftBR, strideBR); // Traseira direita
      renderPaw(-4.5,  3.5, liftFL, strideFL); // Dianteira esquerda
      renderPaw( 3.5,  3.5, liftFR, strideFR); // Dianteira direita

      // 2. O corpo (slices 0 a 15) com bobbing
      for (let z = 0; z < COUNT; z++) {
        stackCtx.save();
        stackCtx.translate(cx, Math.round(cy - (z * spacing + bodyBob)));
        stackCtx.scale(1, squash);
        stackCtx.rotate(turn + bodyRoll);
        stackCtx.drawImage(
          bodySheet,
          z * SLICE_W, 0, SLICE_W, SLICE_H,
          -originX, -originY, SLICE_W, SLICE_H
        );
        stackCtx.restore();
      }

      // Fundo suave
      lowCtx.fillStyle = '#FAF7F2';
      lowCtx.fillRect(0, 0, LOW_W, LOW_H);

      // Sombra sob as 4 patas
      lowCtx.save();
      lowCtx.translate(cx, cy + 2);
      lowCtx.scale(1, 0.42);
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 16, 0, Math.PI * 2);
      lowCtx.fillStyle = 'rgba(74, 46, 27, 0.15)';
      lowCtx.fill();
      lowCtx.restore();

      // Dilatação de contorno único
      const offsets = [[-1, 0], [1, 0], [0, -1], [0, 1]];
      const outlineCanvas = document.createElement('canvas');
      outlineCanvas.width = LOW_W;
      outlineCanvas.height = LOW_H;
      const outCtx = outlineCanvas.getContext('2d');
      outCtx.imageSmoothingEnabled = false;

      for (const [dx, dy] of offsets) {
        outCtx.drawImage(stackCanvas, dx, dy);
      }
      outCtx.globalCompositeOperation = 'source-in';
      outCtx.fillStyle = OUTLINE_COLOR;
      outCtx.fillRect(0, 0, LOW_W, LOW_H);

      lowCtx.drawImage(outlineCanvas, 0, 0);
      lowCtx.drawImage(stackCanvas, 0, 0);

      // Upscale nítido
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

      requestAnimationFrame(draw);
    }

    draw();

    // Controles de rotação com mouse e touch
    let isDragging = false;
    let lastX = 0;

    canvas.addEventListener('pointerdown', (e) => {
      isDragging = true;
      lastX = e.clientX;
      autoSpin = false;
      document.getElementById('btnAutoSpin').classList.remove('active');
    });

    window.addEventListener('pointermove', (e) => {
      if (!isDragging) return;
      const dx = e.clientX - lastX;
      lastX = e.clientX;
      targetTurn += dx * 0.02;
    });

    window.addEventListener('pointerup', () => { isDragging = false; });

    // Presets de visualização
    document.getElementById('btnFront').addEventListener('click', () => {
      targetTurn = 0;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    document.getElementById('btnIso').addEventListener('click', () => {
      targetTurn = Math.PI * 0.25;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    document.getElementById('btnSide').addEventListener('click', () => {
      targetTurn = Math.PI * 0.5;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    document.getElementById('btnBack').addEventListener('click', () => {
      targetTurn = Math.PI;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    const btnAutoSpin = document.getElementById('btnAutoSpin');
    btnAutoSpin.addEventListener('click', () => {
      autoSpin = !autoSpin;
      btnAutoSpin.classList.toggle('active', autoSpin);
    });

    const btnWalk = document.getElementById('btnWalk');
    btnWalk.addEventListener('click', () => {
      isWalking = !isWalking;
      btnWalk.classList.toggle('active', isWalking);
    });

    const btnSlices = document.getElementById('btnSlices');
    let exploded = false;
    btnSlices.addEventListener('click', () => {
      exploded = !exploded;
      targetSpacing = exploded ? 3.0 : 1.0;
      btnSlices.classList.toggle('active', exploded);
    });

    const squashSlider = document.getElementById('squashSlider');
    squashSlider.addEventListener('input', (e) => {
      squash = parseFloat(e.target.value);
    });
  </script>
</body>
</html>
"""

output = template.replace('__BODY_SLICES__', json.dumps(cat_body_slices))\
                 .replace('__PAW_SLICES__', json.dumps(cat_paw_slices))

with open('C:/github/PixelArt/cat-3d.html', 'w', encoding='utf-8') as f:
    f.write(output)

print('cat-3d.html regenerated with articulated walking animation!')
