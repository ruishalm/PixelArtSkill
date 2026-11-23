import json

with open('C:/github/PixelArt/slices_v5.json', 'r', encoding='utf-8') as f:
    cat_slices = f.read().strip()

with open('C:/github/PixelArt/furniture_pack.json', 'r', encoding='utf-8') as f:
    furn_pack = json.load(f)

desk_slices = json.dumps(furn_pack['desk'])
plant_slices = json.dumps(furn_pack['plant'])
bed_slices = json.dumps(furn_pack['bed'])
tree_slices = json.dumps(furn_pack['cat_tree'])

html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mega Quartinho 3D - PurrModoro Diorama</title>
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
      box-shadow: 0 30px 70px rgba(74, 46, 27, 0.20);
      border-radius: 24px;
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
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(14px);
      padding: 10px 24px;
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
      padding: 8px 18px;
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
    <h1>🏠 Mega Quartinho Isométrico 3D (Tudo em Sprite Stacking!)</h1>
    <p>O quarto, mesa, note, planta, quadros e o gato giram em 360° com camadas reais</p>
  </div>

  <canvas id="viewport" width="760" height="760"></canvas>

  <div class="hud">
    <button id="btnIso1" class="btn btn-secondary">Vista 1 (Mesa/Laptop)</button>
    <button id="btnIso2" class="btn btn-secondary">Vista 2 (Torre/Cama)</button>
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

    // Buffer de baixa resolução ampliado (320x320 para o quarto GIGANTE com detalhes)
    const LOW_W = 320;
    const LOW_H = 320;
    const lowCanvas = document.createElement('canvas');
    lowCanvas.width = LOW_W;
    lowCanvas.height = LOW_H;
    const lowCtx = lowCanvas.getContext('2d');
    lowCtx.imageSmoothingEnabled = false;

    // Dimensões do quarto gigante (200x200 de chão útil)
    const ROOM_R = 100;
    const WALL_H = 75;

    // Estado da câmera
    let turn = Math.PI * 0.25;
    let targetTurn = Math.PI * 0.25;
    let squash = 0.75;
    let autoSpin = true;
    let hearts = [];

    // Paleta de Cores PurrModoro
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
      outline: '#3B2219'
    };

    // Helper genérico para compilar dados de fatias para um Canvas Image Sheet
    function createSliceSheet(slicesData, palette, w, h) {
      const count = slicesData.length;
      const sheet = document.createElement('canvas');
      sheet.width = w * count;
      sheet.height = h;
      const sCtx = sheet.getContext('2d');
      sCtx.imageSmoothingEnabled = false;

      for (let z = 0; z < count; z++) {
        const offX = z * w;
        const rows = slicesData[z];
        for (let y = 0; y < h; y++) {
          const row = rows[y];
          for (let x = 0; x < w; x++) {
            const val = parseInt(row[x], 10);
            if (val > 0 && val < palette.length) {
              sCtx.fillStyle = palette[val];
              sCtx.fillRect(offX + x, y, 1, 1);
            }
          }
        }
      }
      return { sheet, count, w, h };
    }

    // 1. GATINHO 3D (16 slices)
    const catPal = ['rgba(0,0,0,0)', '#FDFBF7', '#DE864A', '#3B2219', '#F2A2AB', '#FFFFFF', '#B85820', '#E5E0D8'];
    const catModel = createSliceSheet(__CAT_SLICES__, catPal, 32, 32);

    // 2. MESA + LAPTOP ABERTO + CAFÉ (18 slices)
    const deskPal = [
      'rgba(0,0,0,0)',
      '#633A18', // 1: perna madeira escura
      '#9E6740', // 2: tampo madeira
      '#B87E52', // 3: borda clara
      '#475569', // 4: chassi do laptop
      '#38BDF8', // 5: tela ciano acesa
      '#FAF7F2', // 6: caneca branca
      '#4A2A18', // 7: café
      '#D8D4CC'  // 8: vapor
    ];
    const deskModel = createSliceSheet(__DESK_SLICES__, deskPal, 32, 24);

    // 3. VASO DE PLANTA MONSTERA (16 slices)
    const plantPal = [
      'rgba(0,0,0,0)',
      '#C26A45', // 1: cerâmica terracota
      '#4A2E1B', // 2: terra fértil
      '#2D5A27', // 3: caule verde escuro
      '#4D8A48'  // 4: folha monstera verde viva
    ];
    const plantModel = createSliceSheet(__PLANT_SLICES__, plantPal, 20, 20);

    // 4. CAMINHA NUVEM AZUL COM BORDA MACIA (8 slices)
    const bedPal = [
      'rgba(0,0,0,0)',
      '#385D78', // 1: base azul
      '#4D7594', // 2: borda macia elevada
      '#E4EFF5'  // 3: almofada branca interna
    ];
    const bedModel = createSliceSheet(__BED_SLICES__, bedPal, 32, 32);

    // 5. TORRE DE GATO COM SISAL E CESTINHA (28 slices)
    const treePal = [
      'rgba(0,0,0,0)',
      '#7E6047', // 1: plataforma madeira
      '#D9C3A3', // 2: poste corda de sisal
      '#C29175'  // 3: cesta alta fofa
    ];
    const treeModel = createSliceSheet(__TREE_SLICES__, treePal, 28, 28);

    // Função de Projeção Isométrica Global do Quarto
    function project(x, y, z) {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const rx = x * cosA - y * sinA;
      const ry = x * sinA + y * cosA;
      const cx = Math.floor(LOW_W / 2);
      const cy = Math.floor(LOW_H / 2) + 36;
      return {
        x: Math.round(cx + rx),
        y: Math.round(cy + ry * squash - z),
        depth: ry
      };
    }

    // --- FUNÇÃO UNIVERSAL DE DESENHAR OBJETOS EM SPRITE STACKING 3D ---
    function drawStackObject(model, worldX, worldY, selfAngle = 0, withOutline = true) {
      const p = project(worldX, worldY, 0);
      const totalAngle = selfAngle + turn; // GIRA JUNTO COM O QUARTO EM 360°!

      const sheet = model.sheet;
      const count = model.count;
      const w = model.w;
      const h = model.h;
      const originX = Math.floor(w / 2);
      const originY = Math.floor(h / 2);

      // Renderiza as fatias do objeto empilhadas em Z
      for (let z = 0; z < count; z++) {
        lowCtx.save();
        lowCtx.translate(p.x, Math.round(p.y - z));
        lowCtx.scale(1, squash);
        lowCtx.rotate(totalAngle);
        lowCtx.drawImage(
          sheet,
          z * w, 0, w, h,
          -originX, -originY, w, h
        );
        lowCtx.restore();
      }
    }

    // --- 1. CHÃO DE MADEIRA GIGANTE ---
    function drawFloor() {
      const p0 = project(-ROOM_R, -ROOM_R, 0);
      const p1 = project(ROOM_R, -ROOM_R, 0);
      const p2 = project(ROOM_R, ROOM_R, 0);
      const p3 = project(-ROOM_R, ROOM_R, 0);

      lowCtx.fillStyle = P.woodMid;
      lowCtx.beginPath();
      lowCtx.moveTo(p0.x, p0.y);
      lowCtx.lineTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.closePath();
      lowCtx.fill();

      // Tábuas de madeira
      lowCtx.strokeStyle = P.plankLine;
      lowCtx.lineWidth = 1;
      const step = 9;
      for (let x = -ROOM_R + step; x < ROOM_R; x += step) {
        const pa = project(x, -ROOM_R, 0);
        const pb = project(x, ROOM_R, 0);
        lowCtx.beginPath();
        lowCtx.moveTo(pa.x, pa.y);
        lowCtx.lineTo(pb.x, pb.y);
        lowCtx.stroke();
      }

      // Tapete central oval amplo
      const rugC = project(0, 0, 0);
      lowCtx.save();
      lowCtx.translate(rugC.x, rugC.y);
      lowCtx.scale(1, squash);
      lowCtx.beginPath();
      lowCtx.arc(0, 0, 42, 0, Math.PI * 2);
      lowCtx.fillStyle = '#E8DEC8';
      lowCtx.fill();
      lowCtx.lineWidth = 2.5;
      lowCtx.strokeStyle = '#C8B79B';
      lowCtx.stroke();

      lowCtx.beginPath();
      lowCtx.arc(0, 0, 30, 0, Math.PI * 2);
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

    // --- 2. PAREDES COM CULLING INTELIGENTE ---
    const WALLS = [
      { id: 'north', a: { x: -ROOM_R, y: -ROOM_R }, b: { x: ROOM_R, y: -ROOM_R }, normal: { x: 0, y: -1 }, decor: 'window' },
      { id: 'west',  a: { x: -ROOM_R, y: ROOM_R },  b: { x: -ROOM_R, y: -ROOM_R }, normal: { x: -1, y: 0 }, decor: 'shelves' },
      { id: 'south', a: { x: ROOM_R, y: ROOM_R },   b: { x: -ROOM_R, y: ROOM_R },  normal: { x: 0, y: 1 },  decor: 'pegboard' },
      { id: 'east',  a: { x: ROOM_R, y: -ROOM_R },  b: { x: ROOM_R, y: ROOM_R },   normal: { x: 1, y: 0 },  decor: 'frames' }
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
          // Parede da frente corta e vira rodapé baixo de 2px
          const pA0 = project(w.a.x, w.a.y, 0);
          const pB0 = project(w.b.x, w.b.y, 0);
          const pA1 = project(w.a.x, w.a.y, 2);
          const pB1 = project(w.b.x, w.b.y, 2);

          lowCtx.fillStyle = P.baseboard;
          lowCtx.beginPath();
          lowCtx.moveTo(pA0.x, pA0.y); lowCtx.lineTo(pB0.x, pB0.y);
          lowCtx.lineTo(pB1.x, pB1.y); lowCtx.lineTo(pA1.x, pA1.y);
          lowCtx.closePath(); lowCtx.fill();
          continue;
        }

        // Parede de trás completa
        const bA = project(w.a.x, w.a.y, 0);
        const bB = project(w.b.x, w.b.y, 0);
        const tA = project(w.a.x, w.a.y, WALL_H);
        const tB = project(w.b.x, w.b.y, WALL_H);

        lowCtx.fillStyle = P.wallInner;
        lowCtx.beginPath();
        lowCtx.moveTo(bA.x, bA.y); lowCtx.lineTo(bB.x, bB.y);
        lowCtx.lineTo(tB.x, tB.y); lowCtx.lineTo(tA.x, tA.y);
        lowCtx.closePath(); lowCtx.fill();

        lowCtx.strokeStyle = P.wallTrim;
        lowCtx.lineWidth = 1;
        lowCtx.beginPath();
        lowCtx.moveTo(tA.x, tA.y); lowCtx.lineTo(tB.x, tB.y); lowCtx.lineTo(bB.x, bB.y);
        lowCtx.stroke();

        // Rodapé de 5px
        const rA = project(w.a.x, w.a.y, 5);
        const rB = project(w.b.x, w.b.y, 5);
        lowCtx.fillStyle = P.baseboard;
        lowCtx.beginPath();
        lowCtx.moveTo(bA.x, bA.y); lowCtx.lineTo(bB.x, bB.y);
        lowCtx.lineTo(rB.x, rB.y); lowCtx.lineTo(rA.x, rA.y);
        lowCtx.closePath(); lowCtx.fill();

        // Decoração da parede
        if (w.decor === 'window') drawBigWindow();
        else if (w.decor === 'shelves') drawBigShelves();
        else if (w.decor === 'frames') draw3DFrames();
        else if (w.decor === 'pegboard') drawPegboardDecor();
      }
    }

    // Janela dupla ampla com cortinas
    function drawBigWindow() {
      const z0 = 24, z1 = 62;
      const wA = project(-28, -ROOM_R + 0.5, z0);
      const wB = project(28, -ROOM_R + 0.5, z0);
      const wC = project(28, -ROOM_R + 0.5, z1);
      const wD = project(-28, -ROOM_R + 0.5, z1);

      lowCtx.fillStyle = P.windowSky;
      lowCtx.beginPath();
      lowCtx.moveTo(wA.x, wA.y); lowCtx.lineTo(wB.x, wB.y); lowCtx.lineTo(wC.x, wC.y); lowCtx.lineTo(wD.x, wD.y);
      lowCtx.closePath(); lowCtx.fill();

      // Nuvens
      const c1 = project(-6, -ROOM_R + 0.6, 48);
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.fillRect(c1.x - 10, c1.y - 4, 20, 6);
      lowCtx.fillRect(c1.x - 5, c1.y - 7, 12, 10);

      lowCtx.strokeStyle = P.windowFrame;
      lowCtx.lineWidth = 2;
      lowCtx.stroke();

      // Cortinas rosas elegantes nas laterais
      const crtL0 = project(-35, -ROOM_R + 1, z0 - 4);
      const crtL1 = project(-26, -ROOM_R + 1, z1 + 4);
      lowCtx.fillStyle = P.windowCurtain;
      lowCtx.fillRect(crtL0.x, crtL1.y, 9, crtL0.y - crtL1.y);

      const crtR0 = project(26, -ROOM_R + 1, z0 - 4);
      const crtR1 = project(35, -ROOM_R + 1, z1 + 4);
      lowCtx.fillRect(crtR0.x, crtR1.y, 9, crtR0.y - crtR1.y);
    }

    // Prateleiras duplas com livros, relógio e plantas
    function drawBigShelves() {
      // Prateleira 1
      const s1A = project(-ROOM_R + 0.5, -35, 48);
      const s1B = project(-ROOM_R + 0.5, 20, 48);
      const s1C = project(-ROOM_R + 6, 20, 48);
      const s1D = project(-ROOM_R + 6, -35, 48);

      lowCtx.fillStyle = P.shelfWood;
      lowCtx.beginPath();
      lowCtx.moveTo(s1A.x, s1A.y); lowCtx.lineTo(s1B.x, s1B.y); lowCtx.lineTo(s1C.x, s1C.y); lowCtx.lineTo(s1D.x, s1D.y);
      lowCtx.closePath(); lowCtx.fill();

      // Livros
      const b1 = project(-ROOM_R + 2, -25, 48);
      lowCtx.fillStyle = '#C85A48'; lowCtx.fillRect(b1.x - 2, b1.y - 10, 4, 10);
      const b2 = project(-ROOM_R + 2, -19, 48);
      lowCtx.fillStyle = '#4A7CA8'; lowCtx.fillRect(b2.x - 2, b2.y - 12, 4, 12);
      const b3 = project(-ROOM_R + 2, -13, 48);
      lowCtx.fillStyle = '#5C9A68'; lowCtx.fillRect(b3.x - 2, b3.y - 8, 4, 8);

      // Relógio
      const clk = project(-ROOM_R + 0.5, 0, 60);
      lowCtx.fillStyle = '#FFFFFF'; lowCtx.beginPath(); lowCtx.arc(clk.x, clk.y, 7, 0, Math.PI * 2); lowCtx.fill();
      lowCtx.strokeStyle = '#3B2A20'; lowCtx.lineWidth = 1.5; lowCtx.stroke();
      lowCtx.fillStyle = '#C85A48'; lowCtx.fillRect(clk.x - 1, clk.y - 4, 2, 4);
    }

    // --- QUADROS EM 3D COM 2 CAMADAS (MOLDURA QUE SALTA EM 3D!) ---
    function draw3DFrames() {
      // Quadro 1: Retrato do Gato (Camada 0: Pintura, Camada 1: Moldura que salta 1px da parede)
      const qX = ROOM_R - 0.5;
      const qY = -15;
      const qZ = 38;

      // Camada 0: A pintura do gato (no fundo da parede)
      const pCanvas = project(qX, qY, qZ);
      lowCtx.fillStyle = '#FAF7F2';
      lowCtx.fillRect(pCanvas.x - 8, pCanvas.y - 10, 16, 20);
      // Arte interna do gato
      lowCtx.fillStyle = '#DE864A'; lowCtx.fillRect(pCanvas.x - 5, pCanvas.y - 4, 10, 9);
      lowCtx.fillStyle = '#3B2219'; lowCtx.fillRect(pCanvas.x - 4, pCanvas.y - 7, 3, 3); lowCtx.fillRect(pCanvas.x + 1, pCanvas.y - 7, 3, 3);

      // Camada 1: A moldura de madeira que SALTA 1px DA PAREDE (verdadeiro relevo 3D!)
      const pFrame = project(qX - 1.5, qY, qZ);
      lowCtx.strokeStyle = '#804E2B';
      lowCtx.lineWidth = 2.5;
      lowCtx.strokeRect(pFrame.x - 10, pFrame.y - 12, 20, 24);

      // Quadro 2: Arte Botânica
      const q2Canvas = project(qX, 22, 34);
      lowCtx.fillStyle = '#FAF7F2';
      lowCtx.fillRect(q2Canvas.x - 7, q2Canvas.y - 9, 14, 18);
      lowCtx.fillStyle = '#4D8A48'; lowCtx.fillRect(q2Canvas.x - 2, q2Canvas.y - 5, 4, 10);
      lowCtx.fillRect(q2Canvas.x - 5, q2Canvas.y - 2, 10, 4);

      const q2Frame = project(qX - 1.5, 22, 34);
      lowCtx.strokeStyle = '#804E2B';
      lowCtx.lineWidth = 2;
      lowCtx.strokeRect(q2Frame.x - 8, q2Frame.y - 10, 16, 20);
    }

    function drawPegboardDecor() {
      const pb = project(-15, ROOM_R - 0.5, 36);
      lowCtx.fillStyle = '#D9C8B0'; lowCtx.fillRect(pb.x - 14, pb.y - 14, 28, 28);
      lowCtx.strokeStyle = '#BBA488'; lowCtx.lineWidth = 1; lowCtx.strokeRect(pb.x - 14, pb.y - 14, 28, 28);
      lowCtx.fillStyle = '#4A7CA8'; lowCtx.fillRect(pb.x - 8, pb.y - 6, 16, 4);
    }

    // --- 3. TODOS OS MÓVEIS 3D E O GATO EM SPRITE STACKING ORDENADOS ---
    function drawAll3DObjects() {
      const items = [
        // 1. Caminha Nuvem Azul (3D Sprite Stacking)
        { model: bedModel, x: -55, y: -50, selfAngle: 0 },
        // 2. Mesinha de Estudo com Laptop e Café (3D Sprite Stacking)
        { model: deskModel, x: 50, y: -45, selfAngle: 0 },
        // 3. Vaso de Planta Monstera Grande (3D Sprite Stacking)
        { model: plantModel, x: 65, y: 50, selfAngle: 0.4 },
        // 4. Torre de Gato / Arranhador de 2 Andares (3D Sprite Stacking)
        { model: treeModel, x: -60, y: 35, selfAngle: 0 },
        // 5. O Gatinho Mochi 3D com Olhões e Orelhonas (3D Sprite Stacking)
        { model: catModel, x: 0, y: 0, selfAngle: 0, isCat: true }
      ];

      // Ordena todos os objetos 3D por profundidade atual da câmera
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);

      items.forEach(item => {
        item.depth = item.x * sinA + item.y * cosA;
        item.p = project(item.x, item.y, 0);
      });

      items.sort((a, b) => a.depth - b.depth);

      // Desenha cada móvel e o gato em SPRITE STACKING 3D REAL!
      for (const item of items) {
        // Sombra sob o objeto
        lowCtx.save();
        lowCtx.translate(item.p.x, item.p.y);
        lowCtx.scale(1, squash * 0.45);
        lowCtx.beginPath();
        lowCtx.arc(0, 0, item.isCat ? 12 : 16, 0, Math.PI * 2);
        lowCtx.fillStyle = 'rgba(74, 46, 27, 0.20)';
        lowCtx.fill();
        lowCtx.restore();

        // Desenha o objeto fatiado com rotação acoplada ao quarto!
        drawStackObject(item.model, item.x, item.y, item.selfAngle);
      }
    }

    // Corações
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
        lowCtx.fillRect(h.x, h.y, 4, 4);
        lowCtx.fillRect(h.x - 1, h.y - 1, 2, 2);
        lowCtx.fillRect(h.x + 3, h.y - 1, 2, 2);
      }
    }

    // --- LOOP PRINCIPAL ---
    function render() {
      turn += (targetTurn - turn) * 0.1;

      if (autoSpin) {
        targetTurn += 0.006;
      }

      lowCtx.fillStyle = P.bg;
      lowCtx.fillRect(0, 0, LOW_W, LOW_H);

      // 1. Paredes de trás
      drawWalls();

      // 2. Chão de madeira ampliado
      drawFloor();

      // 3. Todos os móveis 3D e o gatinho em Sprite Stacking (girando juntos!)
      drawAll3DObjects();

      // 4. Efeitos
      drawHearts();

      // Upscale em pixels perfeitos para o viewport principal (Canvas 760x760)
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

      requestAnimationFrame(render);
    }

    render();

    // Controles de arraste do mouse e toque
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
      targetTurn += dx * 0.016;
    });

    window.addEventListener('pointerup', () => { isDragging = false; });

    // Presets rápidos de câmera
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
      const p = project(0, 0, 20);
      for (let i = 0; i < 5; i++) {
        hearts.push({
          x: p.x + (Math.random() * 20 - 10),
          y: p.y - (Math.random() * 12),
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

html_final = html_template.replace('__CAT_SLICES__', cat_slices)\
                          .replace('__DESK_SLICES__', desk_slices)\
                          .replace('__PLANT_SLICES__', plant_slices)\
                          .replace('__BED_SLICES__', bed_slices)\
                          .replace('__TREE_SLICES__', tree_slices)

with open('C:/github/PixelArt/room-3d.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

print('room-3d.html regenerated with full 3D sprite-stacked furniture!')
