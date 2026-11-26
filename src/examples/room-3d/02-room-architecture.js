// Projeção Isométrica Global do Quarto (World -> Screen)
function project(x, y, z) {
  const cosA = Math.cos(turn);
  const sinA = Math.sin(turn);
  const rx = x * cosA - y * sinA;
  const ry = x * sinA + y * cosA;
  const cx = Math.floor(LOW_W / 2);
  const cy = Math.floor(LOW_H / 2) + 48;
  return {
    x: Math.round(cx + rx),
    y: Math.round(cy + ry * squash - z),
    depth: ry
  };
}

// Projeção Inversa (Screen -> World no chão Z = 0)
function unproject(screenX, screenY) {
  const cx = Math.floor(LOW_W / 2);
  const cy = Math.floor(LOW_H / 2) + 48;
  const rx = screenX - cx;
  const ry = (screenY - cy) / squash;
  const cosA = Math.cos(turn);
  const sinA = Math.sin(turn);
  const x = rx * cosA + ry * sinA;
  const y = -rx * sinA + ry * cosA;
  return { x, y };
}

// Função para desenhar polígono 4-pontos em 3D
function drawQuad(p1, p2, p3, p4, fillStyle, strokeStyle = null, lineWidth = 1) {
  lowCtx.beginPath();
  lowCtx.moveTo(p1.x, p1.y);
  lowCtx.lineTo(p2.x, p2.y);
  lowCtx.lineTo(p3.x, p3.y);
  lowCtx.lineTo(p4.x, p4.y);
  lowCtx.closePath();
  if (fillStyle) {
    lowCtx.fillStyle = fillStyle;
    lowCtx.fill();
  }
  if (strokeStyle) {
    lowCtx.strokeStyle = strokeStyle;
    lowCtx.lineWidth = lineWidth;
    lowCtx.stroke();
  }
}

// --- HELPER UNIVERSAL PARA CAIXAS 3D ---
function draw3DBox(x0, x1, y0, y1, z0, z1, colors) {
  const faces = [
    // Top (+Z)
    {
      pts: [project(x0, y0, z1), project(x1, y0, z1), project(x1, y1, z1), project(x0, y1, z1)],
      fill: colors.top || colors.main,
      stroke: colors.stroke
    },
    // Bottom (-Z)
    {
      pts: [project(x0, y1, z0), project(x1, y1, z0), project(x1, y0, z0), project(x0, y0, z0)],
      fill: colors.bottom || colors.dark || colors.main,
      stroke: colors.stroke
    },
    // Front (+X)
    {
      pts: [project(x1, y0, z0), project(x1, y1, z0), project(x1, y1, z1), project(x1, y0, z1)],
      fill: colors.front || colors.main,
      stroke: colors.stroke
    },
    // Back (-X)
    {
      pts: [project(x0, y1, z0), project(x0, y0, z0), project(x0, y0, z1), project(x0, y1, z1)],
      fill: colors.back || colors.dark || colors.main,
      stroke: colors.stroke
    },
    // Right (+Y)
    {
      pts: [project(x0, y1, z0), project(x1, y1, z0), project(x1, y1, z1), project(x0, y1, z1)],
      fill: colors.right || colors.main,
      stroke: colors.stroke
    },
    // Left (-Y)
    {
      pts: [project(x1, y0, z0), project(x0, y0, z0), project(x0, y0, z1), project(x1, y0, z1)],
      fill: colors.left || colors.dark || colors.main,
      stroke: colors.stroke
    }
  ];

  faces.forEach(f => {
    f.depth = (f.pts[0].depth + f.pts[1].depth + f.pts[2].depth + f.pts[3].depth) / 4;
  });
  faces.sort((a, b) => a.depth - b.depth);

  for (const f of faces) {
    drawQuad(f.pts[0], f.pts[1], f.pts[2], f.pts[3], f.fill, f.stroke);
  }
}

// Interpolação bilinear
function lerpP(a, b, t) {
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
}

// --- FUNÇÃO UNIVERSAL DE DESENHAR OBJETOS EM SPRITE STACKING 3D ---
function drawStackObject(model, worldX, worldY, liftZ = 0, selfAngle = 0, scale = 1.35) {
  const p = project(worldX, worldY, liftZ);
  const totalAngle = selfAngle + turn; // GIRA JUNTO COM O QUARTO EM 360°!

  const sheet = model.sheet;
  const count = model.count;
  const w = model.w;
  const h = model.h;
  const originX = Math.floor(w / 2);
  const originY = Math.floor(h / 2);

  for (let z = 0; z < count; z++) {
    lowCtx.save();
    lowCtx.translate(p.x, Math.round(p.y - z * scale));
    lowCtx.scale(scale, squash * scale);
    lowCtx.rotate(totalAngle);
    lowCtx.drawImage(
      sheet,
      z * w, 0, w, h,
      -originX, -originY, w, h
    );
    lowCtx.restore();
  }
}

// Renderizador Invertido para Mostrar a Barriguinha (Belly Roll)
function drawStackInverted(model, worldX, worldY, liftZ = 0, selfAngle = 0, scale = 1.35) {
  const p = project(worldX, worldY, liftZ);
  const totalAngle = selfAngle + turn;

  const sheet = model.sheet;
  const count = model.count;
  const w = model.w;
  const h = model.h;
  const originX = Math.floor(w / 2);
  const originY = Math.floor(h / 2);

  // Invertido: fatia count-1 fica no chão, fatia 0 (barriguinha branca) fica no topo voltada para cima!
  for (let layer = 0; layer < count; layer++) {
    const z = count - 1 - layer;
    lowCtx.save();
    lowCtx.translate(p.x, Math.round(p.y - layer * scale));
    lowCtx.scale(scale, squash * scale);
    lowCtx.rotate(totalAngle);
    lowCtx.drawImage(
      sheet,
      z * w, 0, w, h,
      -originX, -originY, w, h
    );
    lowCtx.restore();
  }
}

// --- 1. CHÃO DE MADEIRA COM GRID ---
function drawFloor() {
  const p0 = project(-ROOM_R, -ROOM_R, 0);
  const p1 = project(ROOM_R, -ROOM_R, 0);
  const p2 = project(ROOM_R, ROOM_R, 0);
  const p3 = project(-ROOM_R, ROOM_R, 0);

  if (currentRoomId === 'kitchen') {
    // PISO DE CERÂMICA XADREZ RETRÔ (Off-white e Bege suave com rejunte fino)
    lowCtx.fillStyle = '#FAF5ED';
    lowCtx.beginPath();
    lowCtx.moveTo(p0.x, p0.y); lowCtx.lineTo(p1.x, p1.y);
    lowCtx.lineTo(p2.x, p2.y); lowCtx.lineTo(p3.x, p3.y);
    lowCtx.closePath(); lowCtx.fill();

    const tileSize = 24;
    for (let x = -ROOM_R; x < ROOM_R; x += tileSize) {
      for (let y = -ROOM_R; y < ROOM_R; y += tileSize) {
        const isAlt = (Math.floor((x + ROOM_R) / tileSize) + Math.floor((y + ROOM_R) / tileSize)) % 2 === 1;
        if (isAlt) {
          const tp0 = project(x, y, 0);
          const tp1 = project(x + tileSize, y, 0);
          const tp2 = project(x + tileSize, y + tileSize, 0);
          const tp3 = project(x, y + tileSize, 0);
          lowCtx.fillStyle = '#E5D6C3';
          lowCtx.beginPath();
          lowCtx.moveTo(tp0.x, tp0.y); lowCtx.lineTo(tp1.x, tp1.y);
          lowCtx.lineTo(tp2.x, tp2.y); lowCtx.lineTo(tp3.x, tp3.y);
          lowCtx.closePath(); lowCtx.fill();
        }
      }
    }
    // Linhas de rejunte finas
    lowCtx.strokeStyle = 'rgba(180, 160, 140, 0.45)';
    lowCtx.lineWidth = 1;
    for (let x = -ROOM_R; x <= ROOM_R; x += tileSize) {
      const pa = project(x, -ROOM_R, 0); const pb = project(x, ROOM_R, 0);
      lowCtx.beginPath(); lowCtx.moveTo(pa.x, pa.y); lowCtx.lineTo(pb.x, pb.y); lowCtx.stroke();
    }
    for (let y = -ROOM_R; y <= ROOM_R; y += tileSize) {
      const pa = project(-ROOM_R, y, 0); const pb = project(ROOM_R, y, 0);
      lowCtx.beginPath(); lowCtx.moveTo(pa.x, pa.y); lowCtx.lineTo(pb.x, pb.y); lowCtx.stroke();
    }
  } else if (currentRoomId === 'garden') {
    // GRAMADO VERDE VIBRANTE DO JARDIM ABERTO
    lowCtx.fillStyle = '#5EA82E';
    lowCtx.beginPath();
    lowCtx.moveTo(p0.x, p0.y); lowCtx.lineTo(p1.x, p1.y);
    lowCtx.lineTo(p2.x, p2.y); lowCtx.lineTo(p3.x, p3.y);
    lowCtx.closePath(); lowCtx.fill();

    // Tufos de grama mais claros espalhados
    lowCtx.fillStyle = '#78C838';
    for (let gx = -ROOM_R + 14; gx < ROOM_R; gx += 24) {
      for (let gy = -ROOM_R + 14; gy < ROOM_R; gy += 24) {
        const pTuft = project(gx + ((gy * 7) % 11), gy, 0);
        lowCtx.fillRect(pTuft.x - 1, pTuft.y - 1, 2, 2);
      }
    }

    // Passarela de pedras redondas da varanda até o carvalho
    const steppingStones = [
      { x: -50, y: -ROOM_R + 25 },
      { x: -35, y: -ROOM_R + 45 },
      { x: -18, y: -ROOM_R + 65 },
      { x: -2,  y: -ROOM_R + 85 },
      { x: 12,  y: -ROOM_R + 105 },
      { x: 26,  y: -ROOM_R + 120 }
    ];
    lowCtx.fillStyle = '#CBD5E1';
    for (const st of steppingStones) {
      const sp = project(st.x, st.y, 0.2);
      lowCtx.beginPath();
      lowCtx.ellipse(sp.x, sp.y, 6.5, 3.8, turn, 0, Math.PI * 2);
      lowCtx.fill();
    }

    // ==============================================================
    // BORDAS DE FLORES COLORIDAS EM TODA A EXTENSÃO (OESTE, SUL, LESTE)
    // Menos na parede da porta (Norte)!
    // ==============================================================
    const flowerCols = ['#EF4444', '#F43F5E', '#FACC15', '#A855F7', '#FFFFFF', '#FB923C'];

    // 1. Borda Oeste (x = -ROOM_R + 6, de y = -ROOM_R + 25 até ROOM_R - 6)
    for (let fy = -ROOM_R + 25; fy <= ROOM_R - 6; fy += 5) {
      const fSoil = project(-ROOM_R + 6, fy, 0.1);
      lowCtx.fillStyle = '#3E2723';
      lowCtx.fillRect(fSoil.x - 4, fSoil.y - 2, 8, 4);

      // Folhagem verde
      const fLeaf = project(-ROOM_R + 6, fy, 2);
      lowCtx.fillStyle = '#15803D';
      lowCtx.beginPath(); lowCtx.arc(fLeaf.x, fLeaf.y, 3.5, 0, Math.PI * 2); lowCtx.fill();

      // Flor
      const fP = project(-ROOM_R + 6, fy, 5);
      lowCtx.fillStyle = flowerCols[(Math.floor((fy + ROOM_R) / 5)) % flowerCols.length];
      lowCtx.beginPath(); lowCtx.arc(fP.x, fP.y, 2.5, 0, Math.PI * 2); lowCtx.fill();
    }

    // 2. Borda Sul (y = ROOM_R - 6, de x = -ROOM_R + 6 até ROOM_R - 6)
    for (let fx = -ROOM_R + 6; fx <= ROOM_R - 6; fx += 5) {
      const fSoil = project(fx, ROOM_R - 6, 0.1);
      lowCtx.fillStyle = '#3E2723';
      lowCtx.fillRect(fSoil.x - 4, fSoil.y - 2, 8, 4);

      const fLeaf = project(fx, ROOM_R - 6, 2);
      lowCtx.fillStyle = '#15803D';
      lowCtx.beginPath(); lowCtx.arc(fLeaf.x, fLeaf.y, 3.5, 0, Math.PI * 2); lowCtx.fill();

      const fP = project(fx, ROOM_R - 6, 5);
      lowCtx.fillStyle = flowerCols[(Math.floor((fx + ROOM_R) / 5)) % flowerCols.length];
      lowCtx.beginPath(); lowCtx.arc(fP.x, fP.y, 2.5, 0, Math.PI * 2); lowCtx.fill();
    }

    // 3. Borda Leste (x = ROOM_R - 6, de y = -ROOM_R + 25 até ROOM_R - 6)
    for (let fy = -ROOM_R + 25; fy <= ROOM_R - 6; fy += 5) {
      const fSoil = project(ROOM_R - 6, fy, 0.1);
      lowCtx.fillStyle = '#3E2723';
      lowCtx.fillRect(fSoil.x - 4, fSoil.y - 2, 8, 4);

      const fLeaf = project(ROOM_R - 6, fy, 2);
      lowCtx.fillStyle = '#15803D';
      lowCtx.beginPath(); lowCtx.arc(fLeaf.x, fLeaf.y, 3.5, 0, Math.PI * 2); lowCtx.fill();

      const fP = project(ROOM_R - 6, fy, 5);
      lowCtx.fillStyle = flowerCols[(Math.floor((fy + ROOM_R) / 5) + 3) % flowerCols.length];
      lowCtx.beginPath(); lowCtx.arc(fP.x, fP.y, 2.5, 0, Math.PI * 2); lowCtx.fill();
    }
  } else {
    // Tábuas de madeira dos quartos interiores
    lowCtx.fillStyle = P.woodMid;
    lowCtx.beginPath();
    lowCtx.moveTo(p0.x, p0.y);
    lowCtx.lineTo(p1.x, p1.y);
    lowCtx.lineTo(p2.x, p2.y);
    lowCtx.lineTo(p3.x, p3.y);
    lowCtx.closePath();
    lowCtx.fill();

    lowCtx.strokeStyle = P.plankLine;
    lowCtx.lineWidth = 1;
    const step = 11;
    for (let x = -ROOM_R + step; x < ROOM_R; x += step) {
      const pa = project(x, -ROOM_R, 0);
      const pb = project(x, ROOM_R, 0);
      lowCtx.beginPath();
      lowCtx.moveTo(pa.x, pa.y);
      lowCtx.lineTo(pb.x, pb.y);
      lowCtx.stroke();
    }
  }

  // Grid sutil no Modo Decoração
  if (isDecorMode) {
    lowCtx.strokeStyle = 'rgba(255, 255, 255, 0.32)';
    lowCtx.lineWidth = 1;
    const gridStep = 16;
    for (let gx = -ROOM_R + gridStep; gx < ROOM_R; gx += gridStep) {
      const ga = project(gx, -ROOM_R, 0);
      const gb = project(gx, ROOM_R, 0);
      lowCtx.beginPath(); lowCtx.moveTo(ga.x, ga.y); lowCtx.lineTo(gb.x, gb.y); lowCtx.stroke();
    }
    for (let gy = -ROOM_R + gridStep; gy < ROOM_R; gy += gridStep) {
      const ga = project(-ROOM_R, gy, 0);
      const gb = project(ROOM_R, gy, 0);
      lowCtx.beginPath(); lowCtx.moveTo(ga.x, ga.y); lowCtx.lineTo(gb.x, gb.y); lowCtx.stroke();
    }
  }

  // Tapete central dependendo do cômodo (100% Projetado em 3D e travado no chão!)
  if (currentRoomId === 'living') {
    // Tapete Escandinavo Retangular em espaço de mundo 3D real: rotaciona perfeito com a câmera!
    const rx0 = -85, rx1 = -15;
    const ry0 = -35, ry1 = 35;

    const pA = project(rx0, ry0, 0.1);
    const pB = project(rx1, ry0, 0.1);
    const pC = project(rx1, ry1, 0.1);
    const pD = project(rx0, ry1, 0.1);
    drawQuad(pA, pB, pC, pD, '#E8DEC8'); // Borda de tear artesanal

    // Franjas nas bordas projetadas em 3D
    lowCtx.fillStyle = '#FAF7F2';
    for (let fy = ry0 + 4; fy < ry1 - 4; fy += 5) {
      const fr1 = project(rx0 - 3, fy, 0.15);
      lowCtx.fillRect(fr1.x - 1, fr1.y - 1, 2, 2);
      const fr2 = project(rx1 + 3, fy, 0.15);
      lowCtx.fillRect(fr2.x - 1, fr2.y - 1, 2, 2);
    }

    const pA2 = project(rx0 + 5, ry0 + 5, 0.15);
    const pB2 = project(rx1 - 5, ry0 + 5, 0.15);
    const pC2 = project(rx1 - 5, ry1 - 5, 0.15);
    const pD2 = project(rx0 + 5, ry1 - 5, 0.15);
    drawQuad(pA2, pB2, pC2, pD2, '#F5EFE6'); // Centro creme acolhedor

    const pA3 = project(rx0 + 10, ry0 + 10, 0.2);
    const pB3 = project(rx1 - 10, ry0 + 10, 0.2);
    const pC3 = project(rx1 - 10, ry1 - 10, 0.2);
    const pD3 = project(rx0 + 10, ry1 - 10, 0.2);
    drawQuad(pA3, pB3, pC3, pD3, '#EADCC9'); // Detalhe geométrico
  } else if (currentRoomId === 'kitchen') {
    // Tapete Redondo de Juta sob a Mesa de Jantar (Acompanha a posição da mesa!)
    const table = items.find(it => it.id === 'dining_table');
    const tx = table ? table.x : -10;
    const ty = table ? table.y : 15;
    const rugP = project(tx, ty, 0.1);
    lowCtx.save();
    lowCtx.translate(rugP.x, rugP.y);
    lowCtx.scale(1, squash * 0.95);

    lowCtx.beginPath();
    lowCtx.arc(0, 0, 46, 0, Math.PI * 2);
    lowCtx.fillStyle = '#D4C3A3';
    lowCtx.fill();

    lowCtx.beginPath();
    lowCtx.arc(0, 0, 40, 0, Math.PI * 2);
    lowCtx.fillStyle = '#EADBBD';
    lowCtx.fill();

    lowCtx.beginPath();
    lowCtx.arc(0, 0, 32, 0, Math.PI * 2);
    lowCtx.fillStyle = '#F5ECE1';
    lowCtx.fill();

    lowCtx.restore();
  } else if (currentRoomId === 'bedroom') {
    // Tapete Nuvem Redondo do Quarto
    const rugP = project(0, 0, 0);
    lowCtx.save();
    lowCtx.translate(rugP.x, rugP.y);
    lowCtx.scale(1, squash * 0.95);

    lowCtx.beginPath();
    lowCtx.arc(0, 0, 48, 0, Math.PI * 2);
    lowCtx.fillStyle = '#E8E0D0';
    lowCtx.fill();

    lowCtx.beginPath();
    lowCtx.arc(0, 0, 40, 0, Math.PI * 2);
    lowCtx.fillStyle = '#F2EBE0';
    lowCtx.fill();

    lowCtx.beginPath();
    lowCtx.arc(0, 0, 32, 0, Math.PI * 2);
    lowCtx.fillStyle = '#FAF7F2';
    lowCtx.fill();

    lowCtx.restore();
  }
}

// --- 2. PAREDES 3D INTELIGENTES COM BACK-FACE CULLING ---
const WALLS = [
  { id: 'north', a: { x: -ROOM_R, y: -ROOM_R }, b: { x: ROOM_R, y: -ROOM_R }, normal: { x: 0, y: -1 }, decor: 'window' },
  { id: 'west',  a: { x: -ROOM_R, y: ROOM_R },  b: { x: -ROOM_R, y: -ROOM_R }, normal: { x: -1, y: 0 }, decor: null },
  { id: 'south', a: { x: ROOM_R, y: ROOM_R },   b: { x: -ROOM_R, y: ROOM_R },  normal: { x: 0, y: 1 },  decor: null },
  { id: 'east',  a: { x: ROOM_R, y: -ROOM_R },  b: { x: ROOM_R, y: ROOM_R },   normal: { x: 1, y: 0 },  decor: null },
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
    if (currentRoomId === 'garden') {
      // NO JARDIM NÃO EXISTEM PAREDES LATERAIS OU TRASEIRAS! APENAS A PAREDE NORTE (FACHADA DA CASA)!
      if (w.id !== 'north') {
        continue; // As outras 3 faces são 100% abertas para o céu azul e natureza!
      }
    }

    if (w.isFrontWall) {
      const pA0 = project(w.a.x, w.a.y, 0);
      const pB0 = project(w.b.x, w.b.y, 0);
      const pA1 = project(w.a.x, w.a.y, 3);
      const pB1 = project(w.b.x, w.b.y, 3);

      lowCtx.fillStyle = P.baseboard;
      lowCtx.beginPath();
      lowCtx.moveTo(pA0.x, pA0.y); lowCtx.lineTo(pB0.x, pB0.y);
      lowCtx.lineTo(pB1.x, pB1.y); lowCtx.lineTo(pA1.x, pA1.y);
      lowCtx.closePath(); lowCtx.fill();
      continue;
    }

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

    const rA = project(w.a.x, w.a.y, 7);
    const rB = project(w.b.x, w.b.y, 7);
    lowCtx.fillStyle = P.baseboard;
    lowCtx.beginPath();
    lowCtx.moveTo(bA.x, bA.y); lowCtx.lineTo(bB.x, bB.y);
    lowCtx.lineTo(rB.x, rB.y); lowCtx.lineTo(rA.x, rA.y);
    lowCtx.closePath(); lowCtx.fill();

    if (w.decor === 'window') drawBigWindow();
    else if (w.decor === 'kitchen_window') drawKitchenWindow();
    else if (w.decor === 'garden_facade') drawGardenFacade();
    else if (w.decor === 'pegboard') drawPegboardDecor();
    else if (w.decor === 'garden_window') drawGardenWindow();
    else if (w.decor === 'living_art') drawLivingRoomArt();
  }
}

// --- JANELA PANORÂMICA COM NUVENS 3D VOLUMÉTRICAS ---

// --- JANELA DA COZINHA ACIMA DA PIA ---

// --- FACHADA DA CASA NO JARDIM COM JANELA E ARBUSTINHOS FLORIDOS ---
function drawGardenFacade() {
  const yWall = -ROOM_R;
  const z0 = 34, z1 = 78;
  const x0 = 10, x1 = 65;

  // 1. JANELA DA FACHADA (Conecta com a janela que se vê do lado de dentro da sala!)
  const w1 = project(x0, yWall + 0.5, z0);
  const w2 = project(x1, yWall + 0.5, z0);
  const w3 = project(x1, yWall + 0.5, z1);
  const w4 = project(x0, yWall + 0.5, z1);

  drawQuad(w1, w2, w3, w4, '#FEF3C7'); // Vidro com brilho quente do interior da casa

  lowCtx.save();
  lowCtx.beginPath();
  lowCtx.moveTo(w1.x, w1.y); lowCtx.lineTo(w2.x, w2.y);
  lowCtx.lineTo(w3.x, w3.y); lowCtx.lineTo(w4.x, w4.y);
  lowCtx.closePath();
  lowCtx.clip();

  // Divisórias das vidraças coloniais brancas
  const midX = (x0 + x1) / 2;
  const midZ = (z0 + z1) / 2;
  const vm1 = project(midX, yWall + 0.8, z0);
  const vm2 = project(midX, yWall + 0.8, z1);
  const hm1 = project(x0, yWall + 0.8, midZ);
  const hm2 = project(x1, yWall + 0.8, midZ);
  lowCtx.strokeStyle = '#FFFFFF';
  lowCtx.lineWidth = 2;
  lowCtx.beginPath(); lowCtx.moveTo(vm1.x, vm1.y); lowCtx.lineTo(vm2.x, vm2.y); lowCtx.stroke();
  lowCtx.beginPath(); lowCtx.moveTo(hm1.x, hm1.y); lowCtx.lineTo(hm2.x, hm2.y); lowCtx.stroke();

  // Cortininhas vistas por fora
  const cL1 = project(x0, yWall + 0.8, z0);
  const cL2 = project(x0 + 8, yWall + 0.8, z0);
  const cL3 = project(x0 + 8, yWall + 0.8, z1);
  const cL4 = project(x0, yWall + 0.8, z1);
  drawQuad(cL1, cL2, cL3, cL4, '#FCA5A5');

  const cR1 = project(x1 - 8, yWall + 0.8, z0);
  const cR2 = project(x1, yWall + 0.8, z0);
  const cR3 = project(x1, yWall + 0.8, z1);
  const cR4 = project(x1 - 8, yWall + 0.8, z1);
  drawQuad(cR1, cR2, cR3, cR4, '#FCA5A5');
  lowCtx.restore();

  // Moldura externa da janela branca com peitoril
  lowCtx.strokeStyle = '#FFFFFF';
  lowCtx.lineWidth = 2.5;
  lowCtx.beginPath();
  lowCtx.moveTo(w1.x, w1.y); lowCtx.lineTo(w2.x, w2.y);
  lowCtx.lineTo(w3.x, w3.y); lowCtx.lineTo(w4.x, w4.y);
  lowCtx.closePath(); lowCtx.stroke();

  // Peitoril da janela
  const pS1 = project(x0 - 2, yWall + 2, z0);
  const pS2 = project(x1 + 2, yWall + 2, z0);
  lowCtx.strokeStyle = '#E2E8F0';
  lowCtx.lineWidth = 3;
  lowCtx.beginPath(); lowCtx.moveTo(pS1.x, pS1.y); lowCtx.lineTo(pS2.x, pS2.y); lowCtx.stroke();

  // 2. ARBUSTOS VERDES E FLORIDOS PERTO DA JANELA (Ao longo da base da parede!)
  for (let bx = 6; bx <= 70; bx += 8) {
    const bP = project(bx, yWall + 5, 4);
    lowCtx.fillStyle = (bx % 16 === 0) ? '#15803D' : '#16A34A';
    lowCtx.beginPath();
    lowCtx.arc(bP.x, bP.y, 9, 0, Math.PI * 2);
    lowCtx.fill();

    const bPtop = project(bx + 2, yWall + 4, 10);
    lowCtx.fillStyle = '#22C55E';
    lowCtx.beginPath();
    lowCtx.arc(bPtop.x, bPtop.y, 7, 0, Math.PI * 2);
    lowCtx.fill();

    // Florzinhas rosas e brancas nos arbustos
    const fP = project(bx + 1, yWall + 6, 8);
    lowCtx.fillStyle = (bx % 16 === 0) ? '#F43F5E' : '#FFFFFF';
    lowCtx.fillRect(fP.x - 1, fP.y - 1, 3, 3);
  }
}

function drawKitchenWindow() {
  const z0 = 36, z1 = 76;
  const x0 = 26, x1 = 58;
  const yWall = -ROOM_R;

  const w1 = project(x0, yWall + 0.5, z0);
  const w2 = project(x1, yWall + 0.5, z0);
  const w3 = project(x1, yWall + 0.5, z1);
  const w4 = project(x0, yWall + 0.5, z1);

  drawQuad(w1, w2, w3, w4, '#93C5FD'); // Céu ensolarado

  lowCtx.save();
  lowCtx.beginPath();
  lowCtx.moveTo(w1.x, w1.y); lowCtx.lineTo(w2.x, w2.y);
  lowCtx.lineTo(w3.x, w3.y); lowCtx.lineTo(w4.x, w4.y);
  lowCtx.closePath();
  lowCtx.clip();

  // Sol e nuvenzinha
  const sunP = project(x1 - 6, yWall + 15, z1 - 8);
  lowCtx.fillStyle = '#FEF08A';
  lowCtx.beginPath(); lowCtx.arc(sunP.x, sunP.y, 8, 0, Math.PI * 2); lowCtx.fill();

  // Cortininhas xadrez fofas nas laterais (estilo Cottage / Farmhouse)
  const cL1 = project(x0, yWall + 0.8, z0);
  const cL2 = project(x0 + 8, yWall + 0.8, z0);
  const cL3 = project(x0 + 8, yWall + 0.8, z1);
  const cL4 = project(x0, yWall + 0.8, z1);
  drawQuad(cL1, cL2, cL3, cL4, '#FCA5A5');

  const cR1 = project(x1 - 8, yWall + 0.8, z0);
  const cR2 = project(x1, yWall + 0.8, z0);
  const cR3 = project(x1, yWall + 0.8, z1);
  const cR4 = project(x1 - 8, yWall + 0.8, z1);
  drawQuad(cR1, cR2, cR3, cR4, '#FCA5A5');

  lowCtx.restore();

  // Moldura da janela branca
  lowCtx.strokeStyle = '#FFFFFF';
  lowCtx.lineWidth = 2;
  lowCtx.beginPath();
  lowCtx.moveTo(w1.x, w1.y); lowCtx.lineTo(w2.x, w2.y);
  lowCtx.lineTo(w3.x, w3.y); lowCtx.lineTo(w4.x, w4.y);
  lowCtx.closePath();
  lowCtx.stroke();
}

function drawBigWindow() {
  const z0 = 32, z1 = 82;
  const x0 = -45, x1 = 45;
  const yWall = -ROOM_R;

  const w1 = project(x0, yWall + 0.5, z0);
  const w2 = project(x1, yWall + 0.5, z0);
  const w3 = project(x1, yWall + 0.5, z1);
  const w4 = project(x0, yWall + 0.5, z1);
  drawQuad(w1, w2, w3, w4, P.windowSky);

  // Nuvens 3D com Parallax fora do quarto
  cloudAnimX += 0.08;
  if (cloudAnimX > 110) cloudAnimX = -110;

  lowCtx.save();
  lowCtx.beginPath();
  lowCtx.moveTo(w1.x, w1.y);
  lowCtx.lineTo(w2.x, w2.y);
  lowCtx.lineTo(w3.x, w3.y);
  lowCtx.lineTo(w4.x, w4.y);
  lowCtx.closePath();
  lowCtx.clip();

  function draw3DCloud(cx, cySky, cz) {
    draw3DBox(cx - 16, cx + 16, cySky - 4, cySky + 4, cz - 4, cz + 4, {
      top: '#FFFFFF', front: '#F0F4F8', back: '#DCE5ED', left: '#DCE5ED', right: '#F0F4F8', bottom: '#C8D7E3'
    });
    draw3DBox(cx - 8, cx + 7, cySky - 3, cySky + 3, cz + 4, cz + 10, {
      top: '#FFFFFF', front: '#F0F4F8', back: '#DCE5ED', left: '#DCE5ED', right: '#F0F4F8', bottom: '#C8D7E3'
    });
    draw3DBox(cx + 9, cx + 19, cySky - 3, cySky + 3, cz - 2, cz + 5, {
      top: '#FFFFFF', front: '#F0F4F8', back: '#DCE5ED', left: '#DCE5ED', right: '#F0F4F8', bottom: '#C8D7E3'
    });
  }

  draw3DCloud(cloudAnimX, yWall - 25, 58);
  const c2X = ((cloudAnimX + 90) % 200) - 100;
  draw3DCloud(c2X, yWall - 35, 68);

  lowCtx.restore();

  // Moldura e peitoril 3D
  const cBottom = project(0, yWall + 0.6, z0);
  const cTop = project(0, yWall + 0.6, z1);
  lowCtx.strokeStyle = P.windowFrame;
  lowCtx.lineWidth = 2.5;
  lowCtx.beginPath(); lowCtx.moveTo(cBottom.x, cBottom.y); lowCtx.lineTo(cTop.x, cTop.y); lowCtx.stroke();

  const cLeft = project(x0, yWall + 0.6, (z0 + z1) / 2);
  const cRight = project(x1, yWall + 0.6, (z0 + z1) / 2);
  lowCtx.beginPath(); lowCtx.moveTo(cLeft.x, cLeft.y); lowCtx.lineTo(cRight.x, cRight.y); lowCtx.stroke();

  draw3DBox(x0 - 5, x1 + 5, yWall, yWall + 8, z0 - 2, z0 + 1, {
    top: '#FAF7F2', front: '#E5DFD5', back: '#FAF7F2', left: '#D8D1C5', right: '#E5DFD5', bottom: '#C8BFA8', stroke: '#A89E88'
  });

  // Cortinas 3D
  draw3DBox(x0 - 14, x0 - 1, yWall, yWall + 5, z0 - 8, z1 + 6, {
    top: '#F2B2A7', front: '#E8A598', back: '#D68C7E', left: '#D68C7E', right: '#E8A598', bottom: '#C47768'
  });
  draw3DBox(x1 + 1, x1 + 14, yWall, yWall + 5, z0 - 8, z1 + 6, {
    top: '#F2B2A7', front: '#E8A598', back: '#D68C7E', left: '#E8A598', right: '#D68C7E', bottom: '#C47768'
  });
}

// --- PAINEL PEGBOARD (PAREDE SUL: y = ROOM_R) ---
function drawPegboardDecor() {
  const yWall = ROOM_R;
  const pb1 = project(-30, yWall - 1.5, 42);
  const pb2 = project(15, yWall - 1.5, 42);
  const pb3 = project(15, yWall - 1.5, 82);
  const pb4 = project(-30, yWall - 1.5, 82);
  drawQuad(pb1, pb2, pb3, pb4, '#E5D6C0', '#B59D7E', 1.5);

  const nt1 = project(-22, yWall - 2, 60);
  lowCtx.fillStyle = '#FCE076'; lowCtx.fillRect(nt1.x - 4, nt1.y - 4, 8, 8);

  const nt2 = project(-8, yWall - 2, 65);
  lowCtx.fillStyle = '#A2D5F2'; lowCtx.fillRect(nt2.x - 4, nt2.y - 4, 8, 8);

  const nt3 = project(5, yWall - 2, 54);
  lowCtx.fillStyle = '#F7A8B8'; lowCtx.fillRect(nt3.x - 4, nt3.y - 4, 8, 8);
}

// --- JANELA DO JARDIM NA PAREDE LESTE (x = ROOM_R) ---
function drawGardenWindow() {
  const xWall = ROOM_R;
  const y0 = -65, y1 = -15; // Lado a lado com a porta do jardim que fica em y = 55!
  const z0 = 35, z1 = 80;

  const w1 = project(xWall - 0.5, y0, z0);
  const w2 = project(xWall - 0.5, y1, z0);
  const w3 = project(xWall - 0.5, y1, z1);
  const w4 = project(xWall - 0.5, y0, z1);

  drawQuad(w1, w2, w3, w4, '#93C5FD'); // Céu azul ensolarado do jardim

  lowCtx.save();
  lowCtx.beginPath();
  lowCtx.moveTo(w1.x, w1.y); lowCtx.lineTo(w2.x, w2.y);
  lowCtx.lineTo(w3.x, w3.y); lowCtx.lineTo(w4.x, w4.y);
  lowCtx.closePath();
  lowCtx.clip();

  // Sol e colinas verdes do jardim com grama e árvores
  const sunP = project(xWall + 20, -50, 72);
  lowCtx.fillStyle = '#FEF08A';
  lowCtx.beginPath(); lowCtx.arc(sunP.x, sunP.y, 14, 0, Math.PI * 2); lowCtx.fill();

  // Copa de árvores do quintal
  const treeP1 = project(xWall + 15, -60, 48);
  const treeP2 = project(xWall + 15, -25, 44);
  lowCtx.fillStyle = '#22C55E';
  lowCtx.beginPath(); lowCtx.arc(treeP1.x, treeP1.y, 22, 0, Math.PI * 2); lowCtx.fill();
  lowCtx.fillStyle = '#16A34A';
  lowCtx.beginPath(); lowCtx.arc(treeP2.x, treeP2.y, 18, 0, Math.PI * 2); lowCtx.fill();

  // Flores cor-de-rosa (cerejeira/ipê)
  lowCtx.fillStyle = '#F472B6';
  lowCtx.fillRect(treeP1.x - 6, treeP1.y - 8, 3, 3);
  lowCtx.fillRect(treeP1.x + 8, treeP1.y + 4, 3, 3);
  lowCtx.fillRect(treeP2.x - 4, treeP2.y - 2, 3, 3);

  // Borboletinha voando no jardim
  const bTime = Date.now() * 0.003;
  const bfX = (treeP1.x + treeP2.x) / 2 + Math.sin(bTime) * 12;
  const bfY = (treeP1.y + treeP2.y) / 2 + Math.cos(bTime * 1.5) * 6;
  lowCtx.fillStyle = '#FBBF24';
  lowCtx.fillRect(bfX, bfY, 3, 2);
  lowCtx.fillRect(bfX + 3, bfY - 1, 2, 2);

  lowCtx.restore();

  // Moldura de madeira nobre e cruzeta
  const cBottom = project(xWall - 0.6, (y0 + y1) / 2, z0);
  const cTop = project(xWall - 0.6, (y0 + y1) / 2, z1);
  lowCtx.strokeStyle = '#5B371E';
  lowCtx.lineWidth = 2.2;
  lowCtx.beginPath(); lowCtx.moveTo(cBottom.x, cBottom.y); lowCtx.lineTo(cTop.x, cTop.y); lowCtx.stroke();

  const cLeft = project(xWall - 0.6, y0, (z0 + z1) / 2);
  const cRight = project(xWall - 0.6, y1, (z0 + z1) / 2);
  lowCtx.beginPath(); lowCtx.moveTo(cLeft.x, cLeft.y); lowCtx.lineTo(cRight.x, cRight.y); lowCtx.stroke();

  // Peitoril da janela com floreira
  draw3DBox(xWall - 6, xWall, y0 - 3, y1 + 3, z0 - 2, z0 + 2, {
    top: '#D49D65', front: '#BD834D', back: '#D49D65', left: '#9E6738', right: '#BD834D', bottom: '#5B371E'
  });
  // Floreira com vasinhos de flor colorida
  draw3DBox(xWall - 5, xWall - 1, y0 + 4, y1 - 4, z0 + 2, z0 + 6, {
    top: '#C2410C', front: '#9A3412', back: '#C2410C', left: '#7C2D12', right: '#9A3412', bottom: '#7C2D12'
  });
}

// --- QUADROS DECORATIVOS DA SALA DE ESTAR (PAREDE NORTE: y = -ROOM_R) ---
function drawLivingRoomArt() {
  const yWall = -ROOM_R;
  // === GRANDE QUADRO DE GALINHAS ENTRE AS PORTAS (x=-25..20, z=48..82) ===
  const x0 = -25, x1 = 20;
  const z0 = 48, z1 = 82;

  // 1. Moldura rústica de madeira nobre talhada
  draw3DBox(x0 - 2, x1 + 2, yWall, yWall + 2.5, z0 - 2, z1 + 2, {
    top: '#6B3E1E', front: '#4A2A14', back: '#6B3E1E', left: '#4A2A14', right: '#4A2A14', bottom: '#351C0C'
  });

  // 2. Filete interno dourado decorativo
  const f1 = project(x0 - 0.5, yWall + 1.2, z0 - 0.5);
  const f2 = project(x1 + 0.5, yWall + 1.2, z0 - 0.5);
  const f3 = project(x1 + 0.5, yWall + 1.2, z1 + 0.5);
  const f4 = project(x0 - 0.5, yWall + 1.2, z1 + 0.5);
  drawQuad(f1, f2, f3, f4, '#D4AF37');

  // 3. Fundo da tela: Céu azul ensolarado com nuvens
  const qA = project(x0, yWall + 1.5, z0);
  const qB = project(x1, yWall + 1.5, z0);
  const qC = project(x1, yWall + 1.5, z1);
  const qD = project(x0, yWall + 1.5, z1);
  drawQuad(qA, qB, qC, qD, '#93C5FD');

  lowCtx.save();
  lowCtx.beginPath();
  lowCtx.moveTo(qA.x, qA.y); lowCtx.lineTo(qB.x, qB.y);
  lowCtx.lineTo(qC.x, qC.y); lowCtx.lineTo(qD.x, qD.y);
  lowCtx.closePath();
  lowCtx.clip();

  // Sol dourado no alto
  const sunP = project(x1 - 8, yWall + 1.6, z1 - 8);
  lowCtx.fillStyle = '#FDE047';
  lowCtx.beginPath(); lowCtx.arc(sunP.x, sunP.y, 6.5, 0, Math.PI * 2); lowCtx.fill();

  // Nuvens fofas brancas
  const clP = project(x0 + 10, yWall + 1.6, z1 - 7);
  lowCtx.fillStyle = '#FFFFFF';
  lowCtx.beginPath(); lowCtx.arc(clP.x, clP.y, 5, 0, Math.PI * 2);
  lowCtx.arc(clP.x + 5, clP.y - 1, 4, 0, Math.PI * 2);
  lowCtx.arc(clP.x - 4, clP.y + 1, 3.5, 0, Math.PI * 2);
  lowCtx.fill();

  // Colina verde suave ao fundo
  const h1A = project(x0, yWall + 1.6, z0 + 14);
  const h1B = project(x1, yWall + 1.6, z0 + 10);
  const h1C = project(x1, yWall + 1.6, z0);
  const h1D = project(x0, yWall + 1.6, z0);
  drawQuad(h1A, h1B, h1C, h1D, '#86EFAC');

  // Pasto verde principal
  const h2A = project(x0, yWall + 1.7, z0 + 8);
  const h2B = project(x1, yWall + 1.7, z0 + 7);
  const h2C = project(x1, yWall + 1.7, z0);
  const h2D = project(x0, yWall + 1.7, z0);
  drawQuad(h2A, h2B, h2C, h2D, '#22C55E');

  // Florzinhas coloridas no pasto
  const fl1 = project(x0 + 5, yWall + 1.8, z0 + 3);
  const fl2 = project(x1 - 6, yWall + 1.8, z0 + 4);
  lowCtx.fillStyle = '#FFFFFF';
  lowCtx.fillRect(fl1.x, fl1.y, 2, 2);
  lowCtx.fillRect(fl2.x, fl2.y, 2, 2);
  lowCtx.fillStyle = '#F472B6';
  lowCtx.fillRect(fl1.x + 3, fl1.y + 1, 2, 2);

  // --- GALINHA BRANCA FOFINHA (MAMA CHICKEN) ---
  const chkP = project(-8, yWall + 1.8, z0 + 8);
  // Corpinho gordinho branco
  lowCtx.fillStyle = '#FFFFFF';
  lowCtx.beginPath(); lowCtx.arc(chkP.x, chkP.y, 6.5, 0, Math.PI * 2); lowCtx.fill();
  // Asinha branca sombreada
  lowCtx.fillStyle = '#F1F5F9';
  lowCtx.beginPath(); lowCtx.arc(chkP.x - 2, chkP.y + 1, 4, 0, Math.PI * 2); lowCtx.fill();
  // Crista vermelha vibrante
  lowCtx.fillStyle = '#EF4444';
  lowCtx.fillRect(chkP.x + 1, chkP.y - 8, 3, 3);
  lowCtx.fillRect(chkP.x + 3, chkP.y - 7, 2, 2);
  // Papo vermelho
  lowCtx.fillRect(chkP.x + 5, chkP.y - 1, 2, 2.5);
  // Biquinho amarelo
  lowCtx.fillStyle = '#F59E0B';
  lowCtx.beginPath();
  lowCtx.moveTo(chkP.x + 5, chkP.y - 3);
  lowCtx.lineTo(chkP.x + 9, chkP.y - 2);
  lowCtx.lineTo(chkP.x + 5, chkP.y - 1);
  lowCtx.fill();
  // Olhinho preto kawaii
  lowCtx.fillStyle = '#0F172A';
  lowCtx.fillRect(chkP.x + 3, chkP.y - 4, 1.5, 1.5);

  // --- PINTINHO AMARELINHO (BABY CHICK) SALTITANDO ---
  const ckP = project(5, yWall + 1.8, z0 + 6);
  // Corpinho amarelo dourado
  lowCtx.fillStyle = '#FBBF24';
  lowCtx.beginPath(); lowCtx.arc(ckP.x, ckP.y, 4, 0, Math.PI * 2); lowCtx.fill();
  // Asinha fofa
  lowCtx.fillStyle = '#F59E0B';
  lowCtx.fillRect(ckP.x - 2, ckP.y, 2.5, 2);
  // Biquinho laranja
  lowCtx.fillStyle = '#EA580C';
  lowCtx.fillRect(ckP.x + 3, ckP.y - 1, 2, 1.5);
  // Olhinho brilhante
  lowCtx.fillStyle = '#0F172A';
  lowCtx.fillRect(ckP.x + 1.5, ckP.y - 2, 1.2, 1.2);
  // Coraçõezinhos de afeto subindo
  const hP = project(0, yWall + 1.8, z0 + 16);
  lowCtx.fillStyle = '#F43F5E';
  lowCtx.beginPath();
  lowCtx.arc(hP.x - 1.5, hP.y, 1.5, 0, Math.PI * 2);
  lowCtx.arc(hP.x + 1.5, hP.y, 1.5, 0, Math.PI * 2);
  lowCtx.lineTo(hP.x, hP.y + 3);
  lowCtx.fill();

  lowCtx.restore();
}

// --- ITENS DE PAREDE E PRATELEIRA MODULARES ---

// 1. Tábua da Prateleira Limpa (Alargada para 1 Tile = 18px! SEM Sobreposição!)
// Som aconchegante da porta (abrir / fechar)
function playDoorSound(isOpen) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = isOpen ? 'triangle' : 'sine';
    osc.frequency.setValueAtTime(isOpen ? 110 : 170, now);
    osc.frequency.exponentialRampToValueAtTime(isOpen ? 210 : 85, now + 0.16);
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.exponentialRampToValueAtTime(0.18, now + 0.04);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.22);
  } catch (e) {}
}

// --- PORTA DE MADEIRA NOBRE NA PAREDE LESTE ---
function drawDoor(item) {
  const wall = item.wall || 'east';
  const hw = (item.width || 28) / 2;
  const H = item.height || 76;
  const liftZ = item.liftZ || 0;
  const isOpen = item.isOpen || false;
  const openAngle = isOpen ? 0.95 : 0; // Ângulo positivo abrindo suavemente para DENTRO do cômodo!

  let pS1, pS2, pS3, pS4;
  let pB1, pB2, pT1, pT2;
  let d1, d2, d3, d4;
  let tipX, tipY, hingeX, hingeY;
  const doorW = hw * 2;
  const isGarden = (item.id === 'door_garden');

  if (wall === 'east') {
    const wallX = item.x || ROOM_R;
    const cy = item.y;
    pS1 = project(wallX, cy - hw - 2, liftZ);
    pS2 = project(wallX - 3, cy - hw - 2, liftZ);
    pS3 = project(wallX - 3, cy + hw + 2, liftZ);
    pS4 = project(wallX, cy + hw + 2, liftZ);

    pB1 = project(wallX, cy - hw - 2, liftZ);
    pB2 = project(wallX, cy + hw + 2, liftZ);
    pT1 = project(wallX, cy - hw - 2, liftZ + H + 3);
    pT2 = project(wallX, cy + hw + 2, liftZ + H + 3);

    hingeX = wallX; hingeY = cy + hw;
    // Abre para DENTRO do quarto (-X):
    tipX = wallX - doorW * Math.sin(openAngle);
    tipY = hingeY - doorW * Math.cos(openAngle);

    d1 = project(hingeX, hingeY, liftZ);
    d2 = project(tipX, tipY, liftZ);
    d3 = project(tipX, tipY, liftZ + H);
    d4 = project(hingeX, hingeY, liftZ + H);
  } else if (wall === 'north') {
    const wallY = item.y || -ROOM_R;
    const cx = item.x;
    pS1 = project(cx - hw - 2, wallY, liftZ);
    pS2 = project(cx - hw - 2, wallY + 3, liftZ);
    pS3 = project(cx + hw + 2, wallY + 3, liftZ);
    pS4 = project(cx + hw + 2, wallY, liftZ);

    pB1 = project(cx - hw - 2, wallY, liftZ);
    pB2 = project(cx + hw + 2, wallY, liftZ);
    pT1 = project(cx - hw - 2, wallY, liftZ + H + 3);
    pT2 = project(cx + hw + 2, wallY, liftZ + H + 3);

    hingeX = cx - hw; hingeY = wallY;
    // Abre para DENTRO do quarto (+Y):
    tipX = hingeX + doorW * Math.cos(openAngle);
    tipY = wallY + doorW * Math.sin(openAngle);

    d1 = project(hingeX, hingeY, liftZ);
    d2 = project(tipX, tipY, liftZ);
    d3 = project(tipX, tipY, liftZ + H);
    d4 = project(hingeX, hingeY, liftZ + H);
  } else if (wall === 'west') {
    const wallX = item.x || -ROOM_R;
    const cy = item.y;
    pS1 = project(wallX, cy - hw - 2, liftZ);
    pS2 = project(wallX + 3, cy - hw - 2, liftZ);
    pS3 = project(wallX + 3, cy + hw + 2, liftZ);
    pS4 = project(wallX, cy + hw + 2, liftZ);

    pB1 = project(wallX, cy - hw - 2, liftZ);
    pB2 = project(wallX, cy + hw + 2, liftZ);
    pT1 = project(wallX, cy - hw - 2, liftZ + H + 3);
    pT2 = project(wallX, cy + hw + 2, liftZ + H + 3);

    hingeX = wallX; hingeY = cy - hw;
    // Abre para DENTRO (+X):
    tipX = wallX + doorW * Math.sin(openAngle);
    tipY = hingeY + doorW * Math.cos(openAngle);

    d1 = project(hingeX, hingeY, liftZ);
    d2 = project(tipX, tipY, liftZ);
    d3 = project(tipX, tipY, liftZ + H);
    d4 = project(hingeX, hingeY, liftZ + H);
  } else { // south
    const wallY = item.y || ROOM_R;
    const cx = item.x;
    pS1 = project(cx - hw - 2, wallY, liftZ);
    pS2 = project(cx - hw - 2, wallY - 3, liftZ);
    pS3 = project(cx + hw + 2, wallY - 3, liftZ);
    pS4 = project(cx + hw + 2, wallY, liftZ);

    pB1 = project(cx - hw - 2, wallY, liftZ);
    pB2 = project(cx + hw + 2, wallY, liftZ);
    pT1 = project(cx - hw - 2, wallY, liftZ + H + 3);
    pT2 = project(cx + hw + 2, wallY, liftZ + H + 3);

    hingeX = cx + hw; hingeY = wallY;
    // Abre para DENTRO (-Y):
    tipX = hingeX - doorW * Math.cos(openAngle);
    tipY = wallY - doorW * Math.sin(openAngle);

    d1 = project(hingeX, hingeY, liftZ);
    d2 = project(tipX, tipY, liftZ);
    d3 = project(tipX, tipY, liftZ + H);
    d4 = project(hingeX, hingeY, liftZ + H);
  }

  // 1. Soleira da porta
  drawQuad(pS1, pS2, pS3, pS4, '#4A2E1B');

  // 2. Batente estrutural de madeira
  drawQuad(pB1, pB2, pT2, pT1, '#5A341A');

  // 3. Vão interno escuro quando aberta
  if (isOpen) {
    const vB1 = project(hingeX, hingeY, liftZ);
    const vB2 = project(wall === 'east' || wall === 'west' ? hingeX : (hingeX + (tipX > hingeX ? -doorW : doorW)), wall === 'south' || wall === 'north' ? hingeY : (hingeY + (tipY > hingeY ? -doorW : doorW)), liftZ);
    const vT2 = project(vB2.x, vB2.y, liftZ + H);
    const vT1 = project(vB1.x, vB1.y, liftZ + H);
    drawQuad(pB1, pB2, pT2, pT1, isGarden ? '#93C5FD' : '#1A1412');
  }

  // 4. Folha da porta de madeira
  drawQuad(d1, d2, d3, d4, '#8B542F', '#4A2A14', 1.2);

  // 5. Painéis entalhados em relevo
  const uX = (tipX - hingeX) / doorW;
  const uY = (tipY - hingeY) / doorW;

  function drawDoorPanel(zBot, zTop, isGlass = false) {
    const m = 3;
    const p1 = project(hingeX + uX * m, hingeY + uY * m, liftZ + zBot);
    const p2 = project(tipX - uX * m, tipY - uY * m, liftZ + zBot);
    const p3 = project(tipX - uX * m, tipY - uY * m, liftZ + zTop);
    const p4 = project(hingeX + uX * m, hingeY + uY * m, liftZ + zTop);

    const col = isGlass ? 'rgba(186, 230, 253, 0.85)' : '#784320';
    const strk = isGlass ? '#7DD3FC' : '#522A0F';
    drawQuad(p1, p2, p3, p4, col, strk, 0.8);
  }

  drawDoorPanel(6, 32, false);
  drawDoorPanel(40, 68, isGarden);

  // 6. Maçaneta Dourada de latão
  const knobX = tipX - uX * 4;
  const knobY = tipY - uY * 4;
  const knobP = project(knobX, knobY, liftZ + 36);

  lowCtx.fillStyle = '#3B2219';
  lowCtx.fillRect(knobP.x - 1, knobP.y - 4, 3, 8);
  lowCtx.fillStyle = '#F4B846';
  lowCtx.beginPath();
  lowCtx.arc(knobP.x, knobP.y, 3, 0, Math.PI * 2);
  lowCtx.fill();

  // 7. Plaquinha de madeira artesanal sobre o batente indicando o destino
  const plaqueLabel = item.id === 'door_kitchen' ? '🍽️ COZINHA' :
                      item.id === 'door_bedroom' ? '🛏️ QUARTO' :
                      item.id === 'door_garden' ? '🌳 JARDIM' :
                      (item.targetRoom === 'living' || item.id === 'door') ? '🛋️ SALA' : null;
  if (plaqueLabel) {
    const midX = (hingeX + tipX) / 2;
    const midY = (hingeY + tipY) / 2;
    const plP = project(midX, midY, liftZ + H + 8);
    lowCtx.save();
    lowCtx.font = 'bold 8px sans-serif';
    const plTw = lowCtx.measureText(plaqueLabel).width;
    const plW = plTw + 8;
    const plH = 12;
    const plX = Math.round(plP.x - plW / 2);
    const plY = Math.round(plP.y - plH / 2);

    // Moldura rústica da placa
    lowCtx.fillStyle = '#4A2A14';
    lowCtx.fillRect(plX - 1, plY - 1, plW + 2, plH + 2);
    lowCtx.fillStyle = '#D4A373';
    lowCtx.fillRect(plX, plY, plW, plH);
    lowCtx.fillStyle = '#2C1810';
    lowCtx.fillText(plaqueLabel, plX + 4, plY + 9);
    lowCtx.restore();
  }
}

function drawShelfItem(shelf) {
  const xWall = -ROOM_R;
  const sy = shelf.y;
  const sz = shelf.liftZ;
  const halfLen = (shelf.length || 68) / 2;

  // 1. Suportes / Mísulas desenhados PRIMEIRO (ficam estritamente ABAIXO da tábua!)
  const bOffsets = [-halfLen + 10, halfLen - 10];
  for (const bo of bOffsets) {
    const by = sy + bo;
    draw3DBox(xWall, xWall + 13, by - 1.2, by + 1.2, sz - 11, sz - 0.2, {
      top: '#633A18', front: '#633A18', back: '#532F16', left: '#532F16', right: '#7E4E2C', bottom: '#3B2219', stroke: '#3B2219'
    });
  }

  // 2. Tábua da prateleira desenhada DEPOIS (largura total de 1 Tile = 18px! Cobre 100% o topo dos suportes!)
  draw3DBox(xWall, xWall + 18, sy - halfLen, sy + halfLen, sz, sz + 3.5, {
    top: '#A06842', front: '#804E2B', back: '#6B3E1E', left: '#6B3E1E', right: '#804E2B', bottom: '#5A341A', stroke: '#3B2219'
  });
}

// 2. Livros em Pé (Acessório Universal 3D)
function drawShelfBooks(item) {
  const x = item.x;
  const y = item.y;
  const z = item.liftZ;
  // Livro 1 (Vermelho em pé)
  draw3DBox(x - 5, x + 4, y - 6, y - 2, z, z + 17, {
    top: '#FAF7F2', front: '#C85A48', back: '#A03828', left: '#A03828', right: '#C85A48', bottom: '#802818', stroke: '#3B2219'
  });
  // Livro 2 (Azul em pé)
  draw3DBox(x - 5, x + 3, y - 1, y + 3, z, z + 13, {
    top: '#FAF7F2', front: '#4A7CA8', back: '#325C80', left: '#325C80', right: '#4A7CA8', bottom: '#254460', stroke: '#3B2219'
  });
  // Apoio de metal moderno
  draw3DBox(x - 5.5, x + 2.5, y + 4, y + 5.5, z, z + 9, {
    top: '#94A3B8', front: '#64748B', back: '#475569', left: '#475569', right: '#64748B', bottom: '#334155', stroke: '#1E293B'
  });
}

// 3. Vasinho de Suculenta Terracota (Acessório Universal 3D)
function drawShelfPlant(item) {
  const x = item.x;
  const y = item.y;
  const z = item.liftZ;
  draw3DBox(x - 4, x + 4, y - 4, y + 4, z, z + 8, {
    top: '#4A2E1B', front: '#C26A45', back: '#A04E2D', left: '#A04E2D', right: '#C26A45', bottom: '#3B2219', stroke: '#3B2219'
  });
  draw3DBox(x - 2, x + 2, y - 3, y + 3, z + 8, z + 16, {
    top: '#5BB055', front: '#4D8A48', back: '#386A34', left: '#386A34', right: '#4D8A48', bottom: '#244520', stroke: '#244520'
  });
  draw3DBox(x - 1.5, x + 1.5, y - 5, y - 3, z + 10, z + 13, { top: '#5BB055', front: '#4D8A48', stroke: '#244520' });
  draw3DBox(x - 1.5, x + 1.5, y + 3, y + 5, z + 10, z + 13, { top: '#5BB055', front: '#4D8A48', stroke: '#244520' });
}

// 4. Livros Deitados com Cristal Rosa (Acessório Universal 3D)
function drawShelfCrystal(item) {
  const x = item.x;
  const y = item.y;
  const z = item.liftZ;
  draw3DBox(x - 5, x + 5, y - 5, y + 5, z, z + 3.5, {
    top: '#0D9488', front: '#0F766E', back: '#115E59', left: '#FAF7F2', right: '#FAF7F2', bottom: '#134E4A', stroke: '#042F2C'
  });
  draw3DBox(x - 4, x + 4, y - 4, y + 4, z + 3.5, z + 7, {
    top: '#7C3AED', front: '#6D28D9', back: '#5B21B6', left: '#FAF7F2', right: '#FAF7F2', bottom: '#4C1D95', stroke: '#2E1065'
  });
  draw3DBox(x - 2, x + 2, y - 2, y + 2, z + 7, z + 13, {
    top: '#F472B6', front: '#EC4899', back: '#DB2777', left: '#DB2777', right: '#EC4899', bottom: '#BE185D', stroke: '#831843'
  });
}

// 5. Relógio Cilíndrico de Parede 3D com Ponteiros em Tempo Real
function drawWallClock(item) {
  const xWall = -ROOM_R;
  const clkRadius = 10;
  const clkDepth = 4.5;
  const xBack = xWall + 0.5;
  const xFront = xWall + clkDepth;
  const yCenter = item.y;
  const zCenter = item.liftZ;
  const N = 16;

  const backPts = [];
  const frontPts = [];
  const dialPts = [];

  for (let i = 0; i < N; i++) {
    const ang = (i / N) * Math.PI * 2;
    const dy = Math.sin(ang) * clkRadius;
    const dz = Math.cos(ang) * clkRadius;
    backPts.push(project(xBack, yCenter + dy, zCenter + dz));
    frontPts.push(project(xFront, yCenter + dy, zCenter + dz));
    dialPts.push(project(xFront + 0.1, yCenter + dy * 0.76, zCenter + dz * 0.76));
  }

  const clkFacets = [];
  for (let i = 0; i < N; i++) {
    const j = (i + 1) % N;
    const p1 = backPts[i];
    const p2 = backPts[j];
    const p3 = frontPts[j];
    const p4 = frontPts[i];
    const d = (p1.depth + p2.depth + p3.depth + p4.depth) / 4;
    const ang = (i / N) * Math.PI * 2;
    const shade = Math.cos(ang) > 0 ? '#9E6740' : '#6B3E1E';
    clkFacets.push({ pts: [p1, p2, p3, p4], depth: d, fill: shade, stroke: '#532F16' });
  }

  const frontDepth = frontPts.reduce((s, p) => s + p.depth, 0) / N;
  clkFacets.push({ pts: frontPts, depth: frontDepth, fill: '#804E2B' });
  clkFacets.push({ pts: dialPts, depth: frontDepth + 0.05, fill: '#FAF7F2', stroke: '#3B2A20' });

  clkFacets.sort((a, b) => a.depth - b.depth);

  for (const f of clkFacets) {
    lowCtx.beginPath();
    lowCtx.moveTo(f.pts[0].x, f.pts[0].y);
    for (let k = 1; k < f.pts.length; k++) lowCtx.lineTo(f.pts[k].x, f.pts[k].y);
    lowCtx.closePath();
    if (f.fill) {
      lowCtx.fillStyle = f.fill;
      lowCtx.fill();
    }
    if (f.stroke) {
      lowCtx.strokeStyle = f.stroke;
      lowCtx.lineWidth = 1;
      lowCtx.stroke();
    }
  }

  // Ponteiros 3D com hora real
  const cCenter = project(xFront + 0.2, yCenter, zCenter);
  const tickAngles = [0, Math.PI / 2, Math.PI, Math.PI * 1.5];
  for (const ta of tickAngles) {
    const tA = project(xFront + 0.2, yCenter + Math.sin(ta) * 5.0, zCenter + Math.cos(ta) * 5.0);
    const tB = project(xFront + 0.2, yCenter + Math.sin(ta) * 6.8, zCenter + Math.cos(ta) * 6.8);
    lowCtx.strokeStyle = '#8C6A54';
    lowCtx.lineWidth = 1.2;
    lowCtx.beginPath(); lowCtx.moveTo(tA.x, tA.y); lowCtx.lineTo(tB.x, tB.y); lowCtx.stroke();
  }

  const now = new Date();
  const sec = now.getSeconds() + now.getMilliseconds() / 1000;
  const min = now.getMinutes() + sec / 60;
  const hr = (now.getHours() % 12) + min / 60;

  const hrAng = (hr / 12) * Math.PI * 2;
  const minAng = (min / 60) * Math.PI * 2;

  const hrEnd = project(xFront + 0.3, yCenter + Math.sin(hrAng) * 3.8, zCenter + Math.cos(hrAng) * 3.8);
  lowCtx.strokeStyle = '#3B2A20';
  lowCtx.lineWidth = 1.6;
  lowCtx.beginPath(); lowCtx.moveTo(cCenter.x, cCenter.y); lowCtx.lineTo(hrEnd.x, hrEnd.y); lowCtx.stroke();

  const minEnd = project(xFront + 0.3, yCenter + Math.sin(minAng) * 6.0, zCenter + Math.cos(minAng) * 6.0);
  lowCtx.strokeStyle = '#C85A48';
  lowCtx.lineWidth = 1.2;
  lowCtx.beginPath(); lowCtx.moveTo(cCenter.x, cCenter.y); lowCtx.lineTo(minEnd.x, minEnd.y); lowCtx.stroke();

  lowCtx.fillStyle = '#DE864A';
  lowCtx.fillRect(cCenter.x - 1, cCenter.y - 1, 2, 2);
}

// 6. Quadros 3D Individuais (Parede Leste: x = ROOM_R)
function drawSingleFrame(item, type) {
  const xWall = ROOM_R;
  const frameThick = 4.0;
  // QUADRO DE POST-ITS EXPANDIDO (Quase o dobro do tamanho!)
  const halfW = (type === 'corkboard' ? 24 : 14);
  const halfH = (type === 'corkboard' ? 26 : 16);
  const y0 = item.y - halfW;
  const y1 = item.y + halfW;
  const z0 = item.liftZ - halfH;
  const z1 = item.liftZ + halfH;

  // Moldura externa de madeira bonita
  const p1 = project(xWall - 0.5, y0, z0);
  const p2 = project(xWall - 0.5, y1, z0);
  const p3 = project(xWall - 0.5, y1, z1);
  const p4 = project(xWall - 0.5, y0, z1);
  drawQuad(p1, p2, p3, p4, '#5C3823'); // Moldura de madeira maciça

  if (type === 'corkboard') {
    // Fundo de Cortiça aconchegante
    const innerP1 = lerpP(lerpP(p1, p2, 0.05), lerpP(p4, p3, 0.05), 0.05);
    const innerP2 = lerpP(lerpP(p1, p2, 0.95), lerpP(p4, p3, 0.95), 0.05);
    const innerP3 = lerpP(lerpP(p1, p2, 0.95), lerpP(p4, p3, 0.95), 0.95);
    const innerP4 = lerpP(lerpP(p1, p2, 0.05), lerpP(p4, p3, 0.05), 0.95);
    drawQuad(innerP1, innerP2, innerP3, innerP4, '#D4A373');

    // Mini Post-its Coloridos e Tachinhas espalhados pelo mural expandido!
    const nCols = ['#FEF08A', '#FBCFE8', '#BAE6FD', '#BBF7D0', '#FED7AA', '#DDD6FE'];
    const noteLocs = [
      { u0: 0.10, u1: 0.38, v0: 0.58, v1: 0.88, c: nCols[0] }, // Post-it amarelo
      { u0: 0.42, u1: 0.70, v0: 0.58, v1: 0.88, c: nCols[1] }, // Post-it rosa
      { u0: 0.73, u1: 0.95, v0: 0.52, v1: 0.82, c: nCols[2] }, // Post-it azul
      { u0: 0.12, u1: 0.40, v0: 0.14, v1: 0.46, c: nCols[3] }, // Post-it verde
      { u0: 0.44, u1: 0.72, v0: 0.14, v1: 0.46, c: nCols[4] }, // Post-it laranja
      { u0: 0.74, u1: 0.96, v0: 0.16, v1: 0.44, c: nCols[5] }  // Post-it lilás
    ];

    for (const nl of noteLocs) {
      const np1 = lerpP(lerpP(innerP1, innerP2, nl.u0), lerpP(innerP4, innerP3, nl.u0), nl.v0);
      const np2 = lerpP(lerpP(innerP1, innerP2, nl.u1), lerpP(innerP4, innerP3, nl.u1), nl.v0);
      const np3 = lerpP(lerpP(innerP1, innerP2, nl.u1), lerpP(innerP4, innerP3, nl.u1), nl.v1);
      const np4 = lerpP(lerpP(innerP1, innerP2, nl.u0), lerpP(innerP4, innerP3, nl.u0), nl.v1);
      drawQuad(np1, np2, np3, np4, nl.c);

      // Tachinha vermelha ou dourada no topo
      const pinP = lerpP(np4, np3, 0.5);
      lowCtx.fillStyle = '#EF4444';
      lowCtx.fillRect(pinP.x - 1, pinP.y - 1, 2, 2);
    }
  } else if (type === 'cat') {
    // Arte: Retrato do Gato
    const catHead1 = lerpP(lerpP(p1, p2, 0.25), lerpP(p4, p3, 0.25), 0.35);
    const catHead2 = lerpP(lerpP(p1, p2, 0.75), lerpP(p4, p3, 0.75), 0.35);
    const catHead3 = lerpP(lerpP(p1, p2, 0.75), lerpP(p4, p3, 0.75), 0.75);
    const catHead4 = lerpP(lerpP(p1, p2, 0.25), lerpP(p4, p3, 0.25), 0.75);
    drawQuad(catHead1, catHead2, catHead3, catHead4, '#DE864A');

    const earL1 = lerpP(catHead4, catHead3, 0.15);
    const earL2 = lerpP(catHead4, catHead3, 0.40);
    const earL3 = lerpP(lerpP(p1, p2, 0.30), lerpP(p4, p3, 0.30), 0.90);
    lowCtx.fillStyle = '#3B2219';
    lowCtx.beginPath(); lowCtx.moveTo(earL1.x, earL1.y); lowCtx.lineTo(earL2.x, earL2.y); lowCtx.lineTo(earL3.x, earL3.y); lowCtx.closePath(); lowCtx.fill();

    const earR1 = lerpP(catHead4, catHead3, 0.60);
    const earR2 = lerpP(catHead4, catHead3, 0.85);
    const earR3 = lerpP(lerpP(p1, p2, 0.70), lerpP(p4, p3, 0.70), 0.90);
    lowCtx.beginPath(); lowCtx.moveTo(earR1.x, earR1.y); lowCtx.lineTo(earR2.x, earR2.y); lowCtx.lineTo(earR3.x, earR3.y); lowCtx.closePath(); lowCtx.fill();

    const eyeL = lerpP(lerpP(p1, p2, 0.38), lerpP(p4, p3, 0.38), 0.55);
    const eyeR = lerpP(lerpP(p1, p2, 0.62), lerpP(p4, p3, 0.62), 0.55);
    lowCtx.fillStyle = '#3B2219';
    lowCtx.fillRect(eyeL.x - 1, eyeL.y - 1, 3, 3);
    lowCtx.fillRect(eyeR.x - 1, eyeR.y - 1, 3, 3);
  } else {
    // Arte: Botânica Verde
    const c1 = lerpP(lerpP(p1, p2, 0.4), lerpP(p4, p3, 0.4), 0.2);
    const c2 = lerpP(lerpP(p1, p2, 0.6), lerpP(p4, p3, 0.6), 0.2);
    const c3 = lerpP(lerpP(p1, p2, 0.6), lerpP(p4, p3, 0.6), 0.8);
    const c4 = lerpP(lerpP(p1, p2, 0.4), lerpP(p4, p3, 0.4), 0.8);
    drawQuad(c1, c2, c3, c4, '#4D8A48');

    const h1 = lerpP(lerpP(p1, p2, 0.2), lerpP(p4, p3, 0.2), 0.4);
    const h2 = lerpP(lerpP(p1, p2, 0.8), lerpP(p4, p3, 0.8), 0.4);
    const h3 = lerpP(lerpP(p1, p2, 0.8), lerpP(p4, p3, 0.8), 0.6);
    const h4 = lerpP(lerpP(p1, p2, 0.2), lerpP(p4, p3, 0.2), 0.6);
    drawQuad(h1, h2, h3, h4, '#4D8A48');
  }

  // Moldura 3D saliente
  const pad = 2.5;
  const fOut1 = project(xWall - frameThick, y0 - pad, z0 - pad);
  const fOut2 = project(xWall - frameThick, y1 + pad, z0 - pad);
  const fOut3 = project(xWall - frameThick, y1 + pad, z1 + pad);
  const fOut4 = project(xWall - frameThick, y0 - pad, z1 + pad);

  const fIn1 = project(xWall - frameThick, y0, z0);
  const fIn2 = project(xWall - frameThick, y1, z0);
  const fIn3 = project(xWall - frameThick, y1, z1);
  const fIn4 = project(xWall - frameThick, y0, z1);

  drawQuad(fOut1, fOut2, fIn2, fIn1, '#804E2B');
  drawQuad(fIn4, fIn3, fOut3, fOut4, '#9E6740');
  drawQuad(fOut1, fIn1, fIn4, fOut4, '#6B3E1E');
  drawQuad(fIn2, fOut2, fOut3, fIn3, '#804E2B');

  const wOut1 = project(xWall - 0.5, y0 - pad, z0 - pad);
  const wOut2 = project(xWall - 0.5, y1 + pad, z0 - pad);
  const wOut3 = project(xWall - 0.5, y1 + pad, z1 + pad);
  const wOut4 = project(xWall - 0.5, y0 - pad, z1 + pad);

  drawQuad(fOut1, fOut2, wOut2, wOut1, '#532F16');
  drawQuad(fOut4, fOut3, wOut3, wOut4, '#6B3E1E');
}

