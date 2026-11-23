import json

with open('C:/github/PixelArt/slices_v5.json', 'r', encoding='utf-8') as f:
    slices_data = f.read().strip()

html_code = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quartinho do Gato 3D Ampliado - PurrModoro</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }
    body {
      background: #EFE7DB;
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
      box-shadow: 0 25px 60px rgba(74, 46, 27, 0.18);
      border-radius: 20px;
      background: #F8F3EB;
      cursor: grab;
      touch-action: none;
    }
    #viewport:active {
      cursor: grabbing;
    }
    .hud {
      position: absolute;
      bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(12px);
      padding: 10px 22px;
      border-radius: 40px;
      border: 1px solid rgba(59, 42, 32, 0.15);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
      align-items: center;
      font-size: 13px;
      font-weight: 500;
      max-width: 95vw;
    }
    .btn {
      background: #3B2A20;
      color: #FAF7F2;
      border: none;
      padding: 7px 16px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }
    .btn:hover {
      background: #5A3F2F;
      transform: translateY(-1px);
    }
    .btn.active {
      background: #D87D4A;
    }
    .btn-secondary {
      background: #EDE4D6;
      color: #3B2A20;
    }
    .btn-secondary:hover {
      background: #DDD0BF;
    }
    .label {
      color: #6B4E3D;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    input[type=range] {
      accent-color: #D87D4A;
      cursor: pointer;
    }
    .badge {
      position: absolute;
      top: 16px;
      text-align: center;
    }
    .badge h1 {
      font-size: 22px;
      font-weight: 700;
      color: #3B2A20;
      letter-spacing: -0.5px;
    }
    .badge p {
      font-size: 13px;
      color: #8C6A54;
      margin-top: 2px;
    }
  </style>
</head>
<body>

  <div class="badge">
    <h1>🏠 Quartinho do Gato 3D (Tamanho Duplo & Detalhado)</h1>
    <p>O quarto, móveis e o gatinho giram juntos em 3D | Paredes frontais cortam sozinhas</p>
  </div>

  <canvas id="viewport" width="700" height="700"></canvas>

  <div class="hud">
    <button id="btnIso1" class="btn btn-secondary">Vista 1 (Janela/Mesa)</button>
    <button id="btnIso2" class="btn btn-secondary">Vista 2 (Torre/Caminha)</button>
    <button id="btnFront" class="btn btn-secondary">Frente</button>
    <button id="btnSide" class="btn btn-secondary">Lado</button>
    <button id="btnAutoSpin" class="btn active">Girar Tudo Auto</button>
    <button id="btnPet" class="btn btn-secondary">🐾 Fazer Carinho</button>
    <div class="label">
      <span>Inclinação:</span>
      <input type="range" id="squashSlider" min="0.62" max="0.88" step="0.01" value="0.75">
    </div>
  </div>

  <script>
    const canvas = document.getElementById('viewport');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    // Buffer de baixa resolução ampliado (220x220 para caber o quarto dobrado)
    const LOW_W = 220;
    const LOW_H = 220;
    const lowCanvas = document.createElement('canvas');
    lowCanvas.width = LOW_W;
    lowCanvas.height = LOW_H;
    const lowCtx = lowCanvas.getContext('2d');
    lowCtx.imageSmoothingEnabled = false;

    // Dimensões do quarto dobrado
    const ROOM_R = 64;   // Raio do piso (128x128 pixels de área útil)
    const WALL_H = 54;   // Paredes mais altas e imponentes

    // Estado da câmera
    let turn = Math.PI * 0.25; // Ângulo isométrico inicial
    let targetTurn = Math.PI * 0.25;
    let squash = 0.75;
    let autoSpin = true;
    let hearts = [];

    // Paleta de Cores Aconchegante (PurrModoro)
    const P = {
      bg: '#F8F3EB',
      woodLight: '#E8C596',
      woodMid: '#D4A373',
      woodDark: '#B88252',
      plankLine: '#9E6B3F',
      baseboard: '#804E2B',
      wallInner: '#F4ECE1',
      wallTrim: '#C8B7A1',
      windowFrame: '#FFFFFF',
      windowCurtain: '#E8A598',
      windowSky: '#A2CBE8',
      shelfWood: '#9E6740',
      plantGreen: '#4D8A48',
      plantLeaf: '#68B062',
      potClay: '#C26A45',
      deskTop: '#A06840',
      deskLeg: '#754624',
      chairBlue: '#5A84B0',
      rugBase: '#E8DEC8',
      rugPattern: '#C8B79B',
      boxCardboard: '#C79A63',
      boxFlap: '#B3854E',
      catTreePole: '#D9C3A3',
      catTreePlat: '#7E6047',
      bedOuter: '#4D7594',
      bedInner: '#E4EFF5',
      outline: '#3B2219'
    };

    // --- CARREGA O SPRITE-STACKING DO GATINHO 3D ---
    const CAT_SLICES = __CAT_SLICES__;
    const CAT_W = 32;
    const CAT_H = 32;
    const CAT_COUNT = CAT_SLICES.length;

    const catSheet = document.createElement('canvas');
    catSheet.width = CAT_W * CAT_COUNT;
    catSheet.height = CAT_H;
    const catSheetCtx = catSheet.getContext('2d');
    catSheetCtx.imageSmoothingEnabled = false;

    const CAT_PAL = [
      'rgba(0,0,0,0)',
      '#FDFBF7', // 1: Branco
      '#DE864A', // 2: Laranja
      '#3B2219', // 3: Olhos/Boca
      '#F2A2AB', // 4: Rosa
      '#FFFFFF', // 5: Brilho olho
      '#B85820', // 6: Laranja escuro
      '#E5E0D8'  // 7: Sombra
    ];

    for (let z = 0; z < CAT_COUNT; z++) {
      const offX = z * CAT_W;
      const rows = CAT_SLICES[z];
      for (let y = 0; y < CAT_H; y++) {
        const row = rows[y];
        for (let x = 0; x < CAT_W; x++) {
          const val = parseInt(row[x], 10);
          if (val > 0) {
            catSheetCtx.fillStyle = CAT_PAL[val];
            catSheetCtx.fillRect(offX + x, y, 1, 1);
          }
        }
      }
    }

    // Projeção isométrica 3D centralizada
    function project(x, y, z) {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const rx = x * cosA - y * sinA;
      const ry = x * sinA + y * cosA;
      const cx = Math.floor(LOW_W / 2);
      const cy = Math.floor(LOW_H / 2) + 24;
      return {
        x: Math.round(cx + rx),
        y: Math.round(cy + ry * squash - z),
        depth: ry
      };
    }

    // --- 1. CHÃO DE MADEIRA AMPLIADO (128x128) ---
    function drawFloor() {
      const p0 = project(-ROOM_R, -ROOM_R, 0);
      const p1 = project(ROOM_R, -ROOM_R, 0);
      const p2 = project(ROOM_R, ROOM_R, 0);
      const p3 = project(-ROOM_R, ROOM_R, 0);

      // Chão preenchido
      lowCtx.fillStyle = P.woodMid;
      lowCtx.beginPath();
      lowCtx.moveTo(p0.x, p0.y);
      lowCtx.lineTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.closePath();
      lowCtx.fill();

      // Tábuas de madeira desenhadas
      lowCtx.strokeStyle = P.plankLine;
      lowCtx.lineWidth = 1;
      const step = 8;
      for (let x = -ROOM_R + step; x < ROOM_R; x += step) {
        const pa = project(x, -ROOM_R, 0);
        const pb = project(x, ROOM_R, 0);
        lowCtx.beginPath();
        lowCtx.moveTo(pa.x, pa.y);
        lowCtx.lineTo(pb.x, pb.y);
        lowCtx.stroke();
      }

      // Tapete grande oval no centro
      const rugC = project(0, 0, 0);
      lowCtx.save();
      lowCtx.translate(rugC.x, rugC.y);
      lowCtx.scale(1, squash);
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 26, 0, Math.PI * 2);
      lowCtx.fillStyle = P.rugBase;
      lowCtx.fill();
      lowCtx.lineWidth = 2;
      lowCtx.strokeStyle = P.rugPattern;
      lowCtx.stroke();

      // Padrão interno no tapete
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 18, 0, Math.PI * 2);
      lowCtx.strokeStyle = '#D4C4A8';
      lowCtx.stroke();
      lowCtx.restore();

      // Rodapé
      lowCtx.strokeStyle = P.baseboard;
      lowCtx.lineWidth = 1;
      lowCtx.beginPath();
      lowCtx.moveTo(p0.x, p0.y);
      lowCtx.lineTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.closePath();
      lowCtx.stroke();
    }

    // --- 2. AS 4 PAREDES COM CULLING DINÂMICO ---
    const WALLS = [
      {
        id: 'north',
        name: 'Norte (Janela Dupla & Cortinas)',
        a: { x: -ROOM_R, y: -ROOM_R },
        b: { x: ROOM_R, y: -ROOM_R },
        normal: { x: 0, y: -1 },
        decor: 'window_curtains'
      },
      {
        id: 'west',
        name: 'Oeste (Prateleiras & Relógio)',
        a: { x: -ROOM_R, y: ROOM_R },
        b: { x: -ROOM_R, y: -ROOM_R },
        normal: { x: -1, y: 0 },
        decor: 'shelves_clock'
      },
      {
        id: 'south',
        name: 'Sul (Pegboard & Espelho)',
        a: { x: ROOM_R, y: ROOM_R },
        b: { x: -ROOM_R, y: ROOM_R },
        normal: { x: 0, y: 1 },
        decor: 'pegboard'
      },
      {
        id: 'east',
        name: 'Leste (Quadros & Luzinhas)',
        a: { x: ROOM_R, y: -ROOM_R },
        b: { x: ROOM_R, y: ROOM_R },
        normal: { x: 1, y: 0 },
        decor: 'gallery'
      }
    ];

    function drawWalls() {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);

      const sortedWalls = [...WALLS].map(w => {
        const mx = (w.a.x + w.b.x) / 2;
        const my = (w.a.y + w.b.y) / 2;
        const rCenter = project(mx, my, WALL_H / 2);
        const nyRot = w.normal.x * sinA + w.normal.y * cosA;
        return {
          ...w,
          depth: rCenter.depth,
          isFrontWall: nyRot > 0.05
        };
      });

      sortedWalls.sort((a, b) => a.depth - b.depth);

      for (const w of sortedWalls) {
        if (w.isFrontWall) {
          // Parede da frente é cortada baixa (rodapé de 2px)
          const pA0 = project(w.a.x, w.a.y, 0);
          const pB0 = project(w.b.x, w.b.y, 0);
          const pA1 = project(w.a.x, w.a.y, 2);
          const pB1 = project(w.b.x, w.b.y, 2);

          lowCtx.fillStyle = P.baseboard;
          lowCtx.beginPath();
          lowCtx.moveTo(pA0.x, pA0.y);
          lowCtx.lineTo(pB0.x, pB0.y);
          lowCtx.lineTo(pB1.x, pB1.y);
          lowCtx.lineTo(pA1.x, pA1.y);
          lowCtx.closePath();
          lowCtx.fill();
          continue;
        }

        // Parede de trás completa
        const bA = project(w.a.x, w.a.y, 0);
        const bB = project(w.b.x, w.b.y, 0);
        const tA = project(w.a.x, w.a.y, WALL_H);
        const tB = project(w.b.x, w.b.y, WALL_H);

        lowCtx.fillStyle = P.wallInner;
        lowCtx.beginPath();
        lowCtx.moveTo(bA.x, bA.y);
        lowCtx.lineTo(bB.x, bB.y);
        lowCtx.lineTo(tB.x, tB.y);
        lowCtx.lineTo(tA.x, tA.y);
        lowCtx.closePath();
        lowCtx.fill();

        lowCtx.strokeStyle = P.wallTrim;
        lowCtx.lineWidth = 1;
        lowCtx.beginPath();
        lowCtx.moveTo(tA.x, tA.y);
        lowCtx.lineTo(tB.x, tB.y);
        lowCtx.lineTo(bB.x, bB.y);
        lowCtx.stroke();

        // Rodapé
        const rA = project(w.a.x, w.a.y, 5);
        const rB = project(w.b.x, w.b.y, 5);
        lowCtx.fillStyle = P.baseboard;
        lowCtx.beginPath();
        lowCtx.moveTo(bA.x, bA.y);
        lowCtx.lineTo(bB.x, bB.y);
        lowCtx.lineTo(rB.x, rB.y);
        lowCtx.lineTo(rA.x, rA.y);
        lowCtx.closePath();
        lowCtx.fill();

        // Decoração da parede de trás
        if (w.decor === 'window_curtains') drawWindowDecor();
        else if (w.decor === 'shelves_clock') drawShelvesDecor();
        else if (w.decor === 'gallery') drawGalleryDecor();
        else if (w.decor === 'pegboard') drawPegboardDecor();
      }
    }

    // Janela com cortinas na parede Norte
    function drawWindowDecor() {
      const z0 = 16, z1 = 44;
      const wA = project(-18, -ROOM_R + 0.5, z0);
      const wB = project(18, -ROOM_R + 0.5, z0);
      const wC = project(18, -ROOM_R + 0.5, z1);
      const wD = project(-18, -ROOM_R + 0.5, z1);

      // Vidro
      lowCtx.fillStyle = P.windowSky;
      lowCtx.beginPath();
      lowCtx.moveTo(wA.x, wA.y);
      lowCtx.lineTo(wB.x, wB.y);
      lowCtx.lineTo(wC.x, wC.y);
      lowCtx.lineTo(wD.x, wD.y);
      lowCtx.closePath();
      lowCtx.fill();

      // Nuvens
      const c1 = project(-4, -ROOM_R + 0.6, 34);
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.fillRect(c1.x - 6, c1.y - 3, 12, 4);
      lowCtx.fillRect(c1.x - 3, c1.y - 5, 8, 7);

      // Moldura
      lowCtx.strokeStyle = P.windowFrame;
      lowCtx.lineWidth = 1.5;
      lowCtx.stroke();

      // Cortinas rosas nas laterais
      const crtL0 = project(-22, -ROOM_R + 1, z0 - 2);
      const crtL1 = project(-16, -ROOM_R + 1, z1 + 2);
      lowCtx.fillStyle = P.windowCurtain;
      lowCtx.fillRect(crtL0.x, crtL1.y, 6, crtL0.y - crtL1.y);

      const crtR0 = project(16, -ROOM_R + 1, z0 - 2);
      const crtR1 = project(22, -ROOM_R + 1, z1 + 2);
      lowCtx.fillRect(crtR0.x, crtR1.y, 6, crtR0.y - crtR1.y);
    }

    // Prateleiras duplas e relógio na parede Oeste
    function drawShelvesDecor() {
      // Prateleira alta (Z = 34)
      const s1A = project(-ROOM_R + 0.5, -20, 34);
      const s1B = project(-ROOM_R + 0.5, 15, 34);
      const s1C = project(-ROOM_R + 5, 15, 34);
      const s1D = project(-ROOM_R + 5, -20, 34);

      lowCtx.fillStyle = P.shelfWood;
      lowCtx.beginPath();
      lowCtx.moveTo(s1A.x, s1A.y);
      lowCtx.lineTo(s1B.x, s1B.y);
      lowCtx.lineTo(s1C.x, s1C.y);
      lowCtx.lineTo(s1D.x, s1D.y);
      lowCtx.closePath();
      lowCtx.fill();

      // Livros coloridos
      const b1 = project(-ROOM_R + 2, -15, 34);
      lowCtx.fillStyle = '#C85A48'; lowCtx.fillRect(b1.x - 2, b1.y - 7, 3, 7);
      const b2 = project(-ROOM_R + 2, -11, 34);
      lowCtx.fillStyle = '#4A7CA8'; lowCtx.fillRect(b2.x - 2, b2.y - 8, 3, 8);
      const b3 = project(-ROOM_R + 2, -7, 34);
      lowCtx.fillStyle = '#5C9A68'; lowCtx.fillRect(b3.x - 2, b3.y - 6, 3, 6);

      // Relógio redondo na parede
      const clk = project(-ROOM_R + 0.5, 0, 44);
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.beginPath();
      lowCtx.arc(clk.x, clk.y, 5, 0, Math.PI * 2);
      lowCtx.fill();
      lowCtx.strokeStyle = '#3B2A20';
      lowCtx.lineWidth = 1;
      lowCtx.stroke();
      // Ponteiros
      lowCtx.fillStyle = '#C85A48';
      lowCtx.fillRect(clk.x - 1, clk.y - 3, 2, 3);
      lowCtx.fillRect(clk.x, clk.y - 1, 3, 2);

      // Prateleira baixa (Z = 20) com plantinha hera caindo
      const s2A = project(-ROOM_R + 0.5, -10, 20);
      const s2B = project(-ROOM_R + 0.5, 20, 20);
      const s2C = project(-ROOM_R + 5, 20, 20);
      const s2D = project(-ROOM_R + 5, -10, 20);

      lowCtx.fillStyle = P.shelfWood;
      lowCtx.beginPath();
      lowCtx.moveTo(s2A.x, s2A.y);
      lowCtx.lineTo(s2B.x, s2B.y);
      lowCtx.lineTo(s2C.x, s2C.y);
      lowCtx.lineTo(s2D.x, s2D.y);
      lowCtx.closePath();
      lowCtx.fill();

      // Vaso de planta com hera caindo
      const plt = project(-ROOM_R + 2, 10, 20);
      lowCtx.fillStyle = P.potClay;
      lowCtx.fillRect(plt.x - 3, plt.y - 4, 6, 4);
      lowCtx.fillStyle = P.plantGreen;
      lowCtx.fillRect(plt.x - 4, plt.y - 8, 8, 5);
      // Folhinhas caindo
      lowCtx.fillStyle = P.plantLeaf;
      lowCtx.fillRect(plt.x - 2, plt.y, 2, 4);
      lowCtx.fillRect(plt.x + 1, plt.y + 1, 2, 5);
    }

    // Galeria de quadros na parede Leste
    function drawGalleryDecor() {
      // Quadro de gato
      const q1 = project(ROOM_R - 0.5, -10, 28);
      lowCtx.fillStyle = '#804E2B'; lowCtx.fillRect(q1.x - 7, q1.y - 8, 14, 16);
      lowCtx.fillStyle = '#FAF7F2'; lowCtx.fillRect(q1.x - 5, q1.y - 6, 10, 12);
      // Silhueta de gatinho no quadro
      lowCtx.fillStyle = '#DE864A'; lowCtx.fillRect(q1.x - 3, q1.y - 2, 6, 5);
      lowCtx.fillStyle = '#3B2219'; lowCtx.fillRect(q1.x - 2, q1.y - 4, 2, 2); lowCtx.fillRect(q1.x + 1, q1.y - 4, 2, 2);

      // Quadro botânico
      const q2 = project(ROOM_R - 0.5, 12, 26);
      lowCtx.fillStyle = '#804E2B'; lowCtx.fillRect(q2.x - 6, q2.y - 7, 12, 14);
      lowCtx.fillStyle = '#FAF7F2'; lowCtx.fillRect(q2.x - 4, q2.y - 5, 8, 10);
      lowCtx.fillStyle = P.plantGreen; lowCtx.fillRect(q2.x - 1, q2.y - 3, 2, 7);
      lowCtx.fillRect(q2.x - 3, q2.y - 1, 6, 3);
    }

    // Pegboard na parede Sul
    function drawPegboardDecor() {
      const pb = project(-10, ROOM_R - 0.5, 26);
      lowCtx.fillStyle = '#D9C8B0'; lowCtx.fillRect(pb.x - 10, pb.y - 10, 20, 20);
      lowCtx.strokeStyle = '#BBA488'; lowCtx.lineWidth = 1; lowCtx.strokeRect(pb.x - 10, pb.y - 10, 20, 20);
      // Fones de ouvido pendurados
      lowCtx.fillStyle = '#4A7CA8'; lowCtx.fillRect(pb.x - 5, pb.y - 4, 10, 3);
      lowCtx.fillRect(pb.x - 6, pb.y - 2, 3, 5); lowCtx.fillRect(pb.x + 3, pb.y - 2, 3, 5);
    }

    // --- 3. MÓVEIS 3D NO CHÃO (COM ORDENAÇÃO DE PROFUNDIDADE) ---
    // Todos os objetos no chão são ordenados dinamicamente por profundidade
    function drawFurnitureAndCat() {
      const items = [
        // 1. Caminha Nuvem Azul
        { type: 'bed', x: -38, y: -36 },
        // 2. Mesinha de Estudo com Computador e Café
        { type: 'desk', x: 34, y: -28 },
        // 3. Torre de Gato / Arranhador de 2 andares
        { type: 'cat_tree', x: -40, y: 24 },
        // 4. Caixa de Papelão
        { type: 'box', x: -16, y: -44 },
        // 5. Potinhos de Comida e Água
        { type: 'bowls', x: -46, y: -10 },
        // 6. Vaso de Planta Monstera Grande
        { type: 'monstera', x: 44, y: 36 },
        // 7. O Gatinho 3D Mochi (no centro do tapete)
        { type: 'cat', x: 0, y: 0 }
      ];

      // Calcula a profundidade de cada objeto conforme a rotação atual
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);

      items.forEach(item => {
        item.depth = item.x * sinA + item.y * cosA;
        item.p = project(item.x, item.y, 0);
      });

      // Ordena de trás para frente (menor depth desenha primeiro)
      items.sort((a, b) => a.depth - b.depth);

      // Renderiza na ordem correta!
      for (const item of items) {
        if (item.type === 'bed') drawBed(item.p);
        else if (item.type === 'desk') drawDesk(item.p);
        else if (item.type === 'cat_tree') drawCatTree(item.p);
        else if (item.type === 'box') drawCardboardBox(item.p);
        else if (item.type === 'bowls') drawBowls(item.p);
        else if (item.type === 'monstera') drawMonstera(item.p);
        else if (item.type === 'cat') draw3DCat(item.p);
      }
    }

    // Caminha Azul Fofinha
    function drawBed(p) {
      lowCtx.save();
      lowCtx.translate(p.x, p.y);
      lowCtx.scale(1, squash);
      // Borda
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 16, 0, Math.PI * 2);
      lowCtx.fillStyle = P.bedOuter;
      lowCtx.fill();
      lowCtx.lineWidth = 2;
      lowCtx.strokeStyle = '#32546E';
      lowCtx.stroke();
      // Almofada interna macia
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 11, 0, Math.PI * 2);
      lowCtx.fillStyle = P.bedInner;
      lowCtx.fill();
      lowCtx.restore();
    }

    // Mesa de estudo com laptop e caneca de café
    function drawDesk(p) {
      const tz = 12;
      const tw = 16, td = 10;
      // 4 Pernas
      const legs = [[-tw + 2, -td + 2], [tw - 2, -td + 2], [-tw + 2, td - 2], [tw - 2, td - 2]];
      for (const [lx, ly] of legs) {
        const lp0 = project(34 + lx, -28 + ly, 0);
        const lp1 = project(34 + lx, -28 + ly, tz);
        lowCtx.strokeStyle = P.deskLeg;
        lowCtx.lineWidth = 1.5;
        lowCtx.beginPath(); lowCtx.moveTo(lp0.x, lp0.y); lowCtx.lineTo(lp1.x, lp1.y); lowCtx.stroke();
      }

      // Tampo
      const t0 = project(34 - tw, -28 - td, tz);
      const t1 = project(34 + tw, -28 - td, tz);
      const t2 = project(34 + tw, -28 + td, tz);
      const t3 = project(34 - tw, -28 + td, tz);

      lowCtx.fillStyle = P.deskTop;
      lowCtx.beginPath();
      lowCtx.moveTo(t0.x, t0.y); lowCtx.lineTo(t1.x, t1.y); lowCtx.lineTo(t2.x, t2.y); lowCtx.lineTo(t3.x, t3.y);
      lowCtx.closePath(); lowCtx.fill();
      lowCtx.strokeStyle = '#6B4426'; lowCtx.stroke();

      // Laptop aberto
      const lap = project(34, -28, tz);
      lowCtx.fillStyle = '#64748B'; lowCtx.fillRect(lap.x - 5, lap.y - 4, 10, 5); // base
      lowCtx.fillStyle = '#38BDF8'; lowCtx.fillRect(lap.x - 4, lap.y - 10, 8, 6); // tela acesa
      lowCtx.strokeStyle = '#1E293B'; lowCtx.lineWidth = 1; lowCtx.strokeRect(lap.x - 4, lap.y - 10, 8, 6);

      // Caneca de café
      const cup = project(34 + 9, -28 - 2, tz);
      lowCtx.fillStyle = '#FAF7F2'; lowCtx.fillRect(cup.x - 2, cup.y - 3, 4, 3);
      lowCtx.fillStyle = '#4A2A18'; lowCtx.fillRect(cup.x - 1, cup.y - 3, 2, 1);
      const steamY = (Date.now() * 0.003) % 4;
      lowCtx.fillStyle = 'rgba(216, 212, 204, 0.7)';
      lowCtx.fillRect(cup.x - 1, cup.y - 5 - steamY, 2, 2);
    }

    // Torre de Gato / Arranhador de 2 andares
    function drawCatTree(p) {
      // Base redonda
      lowCtx.save();
      lowCtx.translate(p.x, p.y);
      lowCtx.scale(1, squash);
      lowCtx.beginPath(); lowCtx.arc(0, 0, 10, 0, Math.PI * 2);
      lowCtx.fillStyle = P.catTreePlat; lowCtx.fill();
      lowCtx.restore();

      // Poste de sisal
      const pole0 = project(-40, 24, 0);
      const pole1 = project(-40, 24, 22);
      lowCtx.strokeStyle = P.catTreePole;
      lowCtx.lineWidth = 4;
      lowCtx.beginPath(); lowCtx.moveTo(pole0.x, pole0.y); lowCtx.lineTo(pole1.x, pole1.y); lowCtx.stroke();

      // Plataforma 1 (Z = 22)
      const plat1 = project(-40, 24, 22);
      lowCtx.save();
      lowCtx.translate(plat1.x, plat1.y);
      lowCtx.scale(1, squash);
      lowCtx.beginPath(); lowCtx.arc(0, 0, 9, 0, Math.PI * 2);
      lowCtx.fillStyle = P.catTreePlat; lowCtx.fill();
      lowCtx.restore();

      // Poste 2
      const pole2 = project(-40, 24, 36);
      lowCtx.strokeStyle = P.catTreePole;
      lowCtx.lineWidth = 3;
      lowCtx.beginPath(); lowCtx.moveTo(plat1.x, plat1.y); lowCtx.lineTo(pole2.x, pole2.y); lowCtx.stroke();

      // Cestinha topo (Z = 36)
      lowCtx.save();
      lowCtx.translate(pole2.x, pole2.y);
      lowCtx.scale(1, squash);
      lowCtx.beginPath(); lowCtx.arc(0, 0, 8, 0, Math.PI * 2);
      lowCtx.fillStyle = '#D9A384'; lowCtx.fill();
      lowCtx.restore();

      // Ratinho de brinquedo pendurado
      const toy = project(-40 + 6, 24, 18);
      lowCtx.fillStyle = '#C85A48'; lowCtx.fillRect(toy.x, toy.y, 3, 2);
    }

    // Caixa de papelão com pegadas
    function drawCardboardBox(p) {
      const b0 = project(-16 - 7, -44 - 6, 0);
      const b1 = project(-16 + 7, -44 - 6, 0);
      const b2 = project(-16 + 7, -44 + 6, 0);
      const b3 = project(-16 - 7, -44 + 6, 0);

      const t0 = project(-16 - 7, -44 - 6, 8);
      const t1 = project(-16 + 7, -44 - 6, 8);
      const t2 = project(-16 + 7, -44 + 6, 8);
      const t3 = project(-16 - 7, -44 + 6, 8);

      // Caixa
      lowCtx.fillStyle = P.boxCardboard;
      lowCtx.beginPath();
      lowCtx.moveTo(b0.x, b0.y); lowCtx.lineTo(b1.x, b1.y); lowCtx.lineTo(t1.x, t1.y); lowCtx.lineTo(t0.x, t0.y);
      lowCtx.closePath(); lowCtx.fill();

      lowCtx.fillStyle = P.boxFlap;
      lowCtx.beginPath();
      lowCtx.moveTo(b1.x, b1.y); lowCtx.lineTo(b2.x, b2.y); lowCtx.lineTo(t2.x, t2.y); lowCtx.lineTo(t1.x, t1.y);
      lowCtx.closePath(); lowCtx.fill();

      // Topo aberto (escuro)
      lowCtx.fillStyle = '#634421';
      lowCtx.beginPath();
      lowCtx.moveTo(t0.x, t0.y); lowCtx.lineTo(t1.x, t1.y); lowCtx.lineTo(t2.x, t2.y); lowCtx.lineTo(t3.x, t3.y);
      lowCtx.closePath(); lowCtx.fill();
    }

    // Potinhos de comida e água
    function drawBowls(p) {
      const p1 = project(-46, -10, 0);
      lowCtx.fillStyle = '#4A7CA8'; lowCtx.fillRect(p1.x - 3, p1.y - 2, 6, 3);
      lowCtx.fillStyle = '#C88B52'; lowCtx.fillRect(p1.x - 2, p1.y - 3, 4, 1);

      const p2 = project(-46, -4, 0);
      lowCtx.fillStyle = '#5CA88B'; lowCtx.fillRect(p2.x - 3, p2.y - 2, 6, 3);
      lowCtx.fillStyle = '#A2DCF0'; lowCtx.fillRect(p2.x - 2, p2.y - 3, 4, 1);
    }

    // Vaso de planta grande Monstera
    function drawMonstera(p) {
      lowCtx.fillStyle = P.potClay;
      lowCtx.beginPath();
      lowCtx.moveTo(p.x - 5, p.y); lowCtx.lineTo(p.x + 5, p.y);
      lowCtx.lineTo(p.x + 6, p.y - 9); lowCtx.lineTo(p.x - 6, p.y - 9);
      lowCtx.closePath(); lowCtx.fill();
      lowCtx.strokeStyle = '#8C4425'; lowCtx.stroke();

      // Folhas grandes da monstera
      lowCtx.fillStyle = P.plantGreen;
      lowCtx.fillRect(p.x - 8, p.y - 18, 7, 10);
      lowCtx.fillRect(p.x + 1, p.y - 20, 8, 11);
      lowCtx.fillRect(p.x - 4, p.y - 24, 9, 12);

      // Recortes nas folhas (fenestrações clássicas da monstera)
      lowCtx.fillStyle = P.plantLeaf;
      lowCtx.fillRect(p.x - 6, p.y - 15, 2, 2);
      lowCtx.fillRect(p.x + 3, p.y - 17, 2, 2);
    }

    // --- 4. O GATINHO 3D EM SPRITE STACKING (GIRA JUNTO COM O QUARTO EM 360°) ---
    function draw3DCat(p) {
      // Sombra projetada sob o gato
      lowCtx.save();
      lowCtx.translate(p.x, p.y);
      lowCtx.scale(1, squash * 0.45);
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 11, 0, Math.PI * 2);
      lowCtx.fillStyle = 'rgba(74, 46, 27, 0.22)';
      lowCtx.fill();
      lowCtx.restore();

      // Renderiza as 16 fatias do gatinho com rotação acoplada ao quarto!
      // 'turn' é o ângulo da câmera: portanto o gato roda perfeitamente em 3D
      const originX = Math.floor(CAT_W / 2);
      const originY = Math.floor(CAT_H / 2);

      // Buffer temporário para desenhar o gato e aplicar contorno único
      const catBuf = document.createElement('canvas');
      catBuf.width = 48;
      catBuf.height = 48;
      const catBufCtx = catBuf.getContext('2d');
      catBufCtx.imageSmoothingEnabled = false;

      const cbX = 24;
      const cbY = 32;

      for (let z = 0; z < CAT_COUNT; z++) {
        catBufCtx.save();
        catBufCtx.translate(cbX, Math.round(cbY - z));
        catBufCtx.scale(1, squash);
        // O gato gira em 3D conforme a rotação do quarto!
        catBufCtx.rotate(turn);
        catBufCtx.drawImage(
          catSheet,
          z * CAT_W, 0, CAT_W, CAT_H,
          -originX, -originY, CAT_W, CAT_H
        );
        catBufCtx.restore();
      }

      // Dilatação de contorno limpo de nanquim
      const outBuf = document.createElement('canvas');
      outBuf.width = 48;
      outBuf.height = 48;
      const outBufCtx = outBuf.getContext('2d');
      outBufCtx.imageSmoothingEnabled = false;

      const offsets = [[-1, 0], [1, 0], [0, -1], [0, 1]];
      for (const [dx, dy] of offsets) {
        outBufCtx.drawImage(catBuf, dx, dy);
      }
      outBufCtx.globalCompositeOperation = 'source-in';
      outBufCtx.fillStyle = '#3B2219';
      outBufCtx.fillRect(0, 0, 48, 48);

      // Desenha contorno e depois o gatinho no quarto
      lowCtx.drawImage(outBuf, p.x - cbX, p.y - cbY);
      lowCtx.drawImage(catBuf, p.x - cbX, p.y - cbY);
    }

    // Coraçõezinhos ao fazer carinho
    function drawHearts() {
      for (let i = hearts.length - 1; i >= 0; i--) {
        const h = hearts[i];
        h.y -= 0.6;
        h.alpha -= 0.015;
        if (h.alpha <= 0) {
          hearts.splice(i, 1);
          continue;
        }
        lowCtx.fillStyle = `rgba(235, 94, 120, ${h.alpha})`;
        lowCtx.fillRect(h.x, h.y, 3, 3);
        lowCtx.fillRect(h.x - 1, h.y - 1, 2, 2);
        lowCtx.fillRect(h.x + 2, h.y - 1, 2, 2);
      }
    }

    // --- LOOP PRINCIPAL ---
    function render() {
      turn += (targetTurn - turn) * 0.1;

      if (autoSpin) {
        targetTurn += 0.006;
      }

      // Fundo suave
      lowCtx.fillStyle = P.bg;
      lowCtx.fillRect(0, 0, LOW_W, LOW_H);

      // 1. Paredes de trás
      drawWalls();

      // 2. Piso de madeira
      drawFloor();

      // 3. Móveis e o gatinho 3D (ordenados por profundidade!)
      drawFurnitureAndCat();

      // 4. Corações
      drawHearts();

      // Upscale nítido (3.18x) para o canvas de 700x700
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

      requestAnimationFrame(render);
    }

    render();

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
      targetTurn += dx * 0.018;
    });

    window.addEventListener('pointerup', () => { isDragging = false; });

    // Presets rápidos
    document.getElementById('btnIso1').addEventListener('click', () => {
      targetTurn = Math.PI * 0.25;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    document.getElementById('btnIso2').addEventListener('click', () => {
      targetTurn = Math.PI * 0.75;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    document.getElementById('btnFront').addEventListener('click', () => {
      targetTurn = 0;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    document.getElementById('btnSide').addEventListener('click', () => {
      targetTurn = Math.PI * 0.5;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    const btnAutoSpin = document.getElementById('btnAutoSpin');
    btnAutoSpin.addEventListener('click', () => {
      autoSpin = !autoSpin;
      btnAutoSpin.classList.toggle('active', autoSpin);
    });

    document.getElementById('btnPet').addEventListener('click', () => {
      const p = project(0, 0, 16);
      for (let i = 0; i < 5; i++) {
        hearts.push({
          x: p.x + (Math.random() * 16 - 8),
          y: p.y - (Math.random() * 10),
          alpha: 1.0
        });
      }
    });

    const squashSlider = document.getElementById('squashSlider');
    squashSlider.addEventListener('input', (e) => {
      squash = parseFloat(e.target.value);
    });
  </script>
</body>
</html>
"""

final_html = html_code.replace('__CAT_SLICES__', slices_data)

with open('C:/github/PixelArt/room-3d.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print('room-3d.html regenerated with doubled size and true 3D rotating cat!')
