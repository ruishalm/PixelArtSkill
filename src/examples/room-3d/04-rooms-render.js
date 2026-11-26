// --- RENDERIZADOR DE ITEM INDIVIDUAL COM INDICADORES ---
    // --- SISTEMA DE MIGRAÇÃO DE PETS & TROCA DE CÔMODOS ---
function showToast(msg) {
  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed; bottom:70px; left:50%; transform:translateX(-50%); background:rgba(30,27,24,0.92); color:#FDFBF7; padding:8px 18px; border-radius:20px; font-size:12px; font-weight:bold; z-index:99999; box-shadow:0 6px 18px rgba(0,0,0,0.3); animation:fadeIn 0.2s ease;';
  toast.innerText = msg;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

function updateHousePlanBadges() {
  const rooms = ['bedroom', 'living', 'kitchen', 'garden'];
  for (const r of rooms) {
    const isCur = (currentRoomId === r);
    const cap = r.charAt(0).toUpperCase() + r.slice(1);
    const b = document.getElementById('badge' + cap);
    const c = document.getElementById('roomCard' + cap);
    const p = document.getElementById('pets' + cap);
    if (b) b.style.display = isCur ? 'inline-block' : 'none';
    if (c) c.classList.toggle('active-room', isCur);
    if (p) p.innerHTML = isCur ? '🐱 🐔 🐥' : '';
  }
}

function migratePetsToDoor(door, onComplete) {
  const cat = PETS.find(it => it.id === 'cat');
  const chicken = PETS.find(it => it.id === 'chicken');
  const chick = PETS.find(it => it.id === 'chick');

  if (cat) {
    cat.surface = null; cat.liftZ = 0;
    cat.targetX = door.x * 0.75; cat.targetY = door.y * 0.75;
    cat.state = 'walk'; cat.posture = 'walk';
    cat.speech = { text: "Nya~! Vamos lá! 🚪", timer: 160 };
    setTimeout(() => cat.speech = null, 2500);
  }
  if (chicken) {
    chicken.surface = null; chicken.liftZ = 0;
    chicken.targetX = door.x * 0.70; chicken.targetY = door.y * 0.70;
    chicken.state = 'walk';
    chicken.speech = { text: "Có có! 💕", timer: 160 };
    setTimeout(() => chicken.speech = null, 2500);
  }
  if (chick) {
    chick.surface = null; chick.liftZ = 0;
    chick.targetX = door.x * 0.65; chick.targetY = door.y * 0.65;
    chick.state = 'walk';
    chick.speech = { text: "Piu! ❤️", timer: 160 };
    setTimeout(() => chick.speech = null, 2500);
  }

  for (let i = 0; i < 5; i++) {
    hearts.push({ x: door.x * 0.7 + (Math.random() - 0.5) * 20, y: door.y * 0.7 + (Math.random() - 0.5) * 20, z: 25, life: 1.0 });
  }

  setTimeout(() => {
    if (onComplete) onComplete();
  }, 500);
}

function switchRoom(targetRoomId, viaDoor = false) {
  if (currentRoomId === targetRoomId) return;

  const fade = document.getElementById('roomFadeOverlay');
  if (fade) fade.style.opacity = '1';

  setTimeout(() => {
    // Salva mobília do cômodo anterior
    roomState[currentRoomId] = items.filter(it => !it.isCat && !it.isChicken);
    currentRoomId = targetRoomId;

    const cat = PETS.find(it => it.id === 'cat');
    const chicken = PETS.find(it => it.id === 'chicken');
    const chick = PETS.find(it => it.id === 'chick');

    if (targetRoomId === 'living') {
      // Entrando na Sala vindo da Porta do Quarto na Parede Norte (x=75, y=-ROOM_R)
      if (cat) {
        cat.x = 68; cat.y = -ROOM_R + 38; cat.liftZ = 0;
        cat.targetX = -25; cat.targetY = 0; cat.state = 'walk'; cat.posture = 'walk';
        cat.speech = { text: "Nya~! Chegamos na Sala! ✨", timer: 180 };
      }
      if (chicken) {
        chicken.x = 78; chicken.y = -ROOM_R + 42; chicken.liftZ = 0;
        chicken.targetX = -35; chicken.targetY = -8; chicken.state = 'walk';
        chicken.speech = { text: "Có có! 🛋️", timer: 180 };
      }
      if (chick) {
        chick.x = 74; chick.y = -ROOM_R + 48; chick.liftZ = 0;
        chick.targetX = -30; chick.targetY = 8; chick.state = 'walk';
        chick.speech = { text: "Piu piu! ❤️", timer: 180 };
      }

      WALLS[0].decor = 'living_art'; // North
      WALLS[1].decor = null;         // West
      WALLS[2].decor = null;         // South
      WALLS[3].decor = 'garden_window'; // East (Janela do Jardim lado a lado com a porta do jardim!)
    } else if (targetRoomId === 'kitchen') {
      // Entrando na Cozinha vindo da Sala (Porta na Parede Leste: x=ROOM_R, y=55)
      if (cat) {
        cat.x = ROOM_R - 35; cat.y = 50; cat.liftZ = 0;
        cat.targetX = -10; cat.targetY = 15; cat.state = 'walk'; cat.posture = 'walk';
        cat.speech = { text: "Nya~! Cheirinho bom de salmão fresco! 🐟✨", timer: 180 };
      }
      if (chicken) {
        chicken.x = ROOM_R - 30; chicken.y = 65; chicken.liftZ = 0;
        chicken.targetX = -10; chicken.targetY = 35; chicken.state = 'walk';
        chicken.speech = { text: "Có có! Frutinhas frescas na mesa! 🍇", timer: 180 };
      }
      if (chick) {
        chick.x = ROOM_R - 25; chick.y = 75; chick.liftZ = 0;
        chick.targetX = 15; chick.targetY = 15; chick.state = 'walk';
        chick.speech = { text: "Piu piu! 💛", timer: 180 };
      }

      WALLS[0].decor = 'kitchen_window'; // North (Janela acima da pia)
      WALLS[1].decor = null;             // West (Geladeira e Aparador)
      WALLS[2].decor = null;             // South
      WALLS[3].decor = null;             // East (Porta pra Sala)
    } else if (targetRoomId === 'garden') {
      // Entrando no Jardim vindo da Sala (Porta na Parede Norte: x=-65, y=-ROOM_R)
      if (cat) {
        cat.x = -50; cat.y = -ROOM_R + 35; cat.liftZ = 0;
        cat.targetX = 10; cat.targetY = 0; cat.state = 'walk'; cat.posture = 'walk';
        cat.speech = { text: "Nya~! Céu azul e sol quentinho no jardim! ☀️🐾", timer: 180 };
      }
      if (chicken) {
        chicken.x = -40; chicken.y = -ROOM_R + 40; chicken.liftZ = 0;
        chicken.targetX = 21; chicken.targetY = 19; chicken.state = 'walk';
        chicken.speech = { text: "Có có! Olha o balanço de pneu em pé na árvore! 🛞🌳", timer: 180 };
      }
      if (chick) {
        chick.x = -45; chick.y = -ROOM_R + 50; chick.liftZ = 0;
        chick.targetX = -10; chick.targetY = 25; chick.state = 'walk';
        chick.speech = { text: "Piu piu! Quanta flor na borda! 🌸🌼", timer: 180 };
      }

      WALLS[0].decor = 'garden_facade'; // North (Fachada com Janela e Arbustos)
      WALLS[1].decor = null;
      WALLS[2].decor = null;
      WALLS[3].decor = null;
    } else if (targetRoomId === 'bedroom') {
      // Entrando no Quarto vindo da porta Leste (Sala)
      if (cat) {
        cat.x = ROOM_R - 35; cat.y = 50; cat.liftZ = 0;
        cat.targetX = 10; cat.targetY = 0; cat.state = 'walk'; cat.posture = 'walk';
        cat.speech = { text: "De volta ao quartinho! 🛏️", timer: 180 };
      }
      if (chicken) {
        chicken.x = ROOM_R - 30; chicken.y = 65; chicken.liftZ = 0;
        chicken.targetX = -20; chicken.targetY = 30; chicken.state = 'walk';
      }
      if (chick) {
        chick.x = ROOM_R - 25; chick.y = 75; chick.liftZ = 0;
        chick.targetX = -10; chick.targetY = 40; chick.state = 'walk';
      }

      WALLS[0].decor = 'window';     // North
      WALLS[1].decor = null;         // West
      WALLS[2].decor = 'pegboard';   // South
      WALLS[3].decor = null;         // East
    }

    items = [ ...PETS, ...roomState[currentRoomId] ];

    const titleEl = document.getElementById('roomTitle');
    const subEl = document.getElementById('roomSubtitle');
    if (currentRoomId === 'living') {
      if (titleEl) titleEl.innerHTML = "🛋️ Sala de Estar Central (Hub da Casa)";
      if (subEl) subEl.innerHTML = "Sofá aconchegante, TV retrô vintage e vista para o jardim!";
    } else if (currentRoomId === 'kitchen') {
      if (titleEl) titleEl.innerHTML = "🍽️ Cozinha Retrô Pastel (Bancada, Geladeira & Jantar)";
      if (subEl) subEl.innerHTML = "Geladeira funcional com lista de compras, pia, fogão e mesa modular!";
    } else if (currentRoomId === 'garden') {
      if (titleEl) titleEl.innerHTML = "🌳 Jardim Externo Ensolarado (Varandinha, Árvore & Balanço)";
      if (subEl) subEl.innerHTML = "Árvore com balanço de pneu pra Popó, carrinho de flores e ar puro!";
    } else {
      if (titleEl) titleEl.innerHTML = "🛏️ Mega Quartinho 3D (Tudo Modular & Movível!)";
      if (subEl) subEl.innerHTML = "Mesa personalizável, gatinho inteligente, caminha e decoração!";
    }

    updateHousePlanBadges();

    if (assetDrawer && assetDrawer.style.display !== 'none') {
      renderAssetList();
    }

    if (fade) fade.style.opacity = '0';
  }, 300);
}


// --- RENDERIZADOR ARQUITETÔNICO 100% SÓLIDO COM OCLUSÃO TOTAL (ZERO-CLIPPING & SOLID BACK/SIDES) ---
function drawModularBookshelf(shelfItem, activeItems) {
  const isSel = (shelfItem === selectedItem);
  const isHov = (shelfItem === hoveredItem && isDecorMode);
  const effectiveLiftZ = shelfItem.liftZ || 0;

  // 1. Sombra retangular da estante orientada no chão
  const cosD = Math.cos(shelfItem.selfAngle || 0);
  const sinD = Math.sin(shelfItem.selfAngle || 0);
  const hw = 23 * (shelfItem.scale || 1.45) / 1.35;
  const hh = 8 * (shelfItem.scale || 1.45) / 1.35;
  const corners = [
    { x: shelfItem.x - hw * cosD + hh * sinD, y: shelfItem.y - hw * sinD - hh * cosD },
    { x: shelfItem.x + hw * cosD + hh * sinD, y: shelfItem.y + hw * sinD - hh * cosD },
    { x: shelfItem.x + hw * cosD - hh * sinD, y: shelfItem.y + hw * sinD + hh * cosD },
    { x: shelfItem.x - hw * cosD - hh * sinD, y: shelfItem.y - hw * sinD + hh * cosD }
  ];
  const pC = corners.map(c => project(c.x, c.y, 0));
  lowCtx.beginPath();
  lowCtx.moveTo(pC[0].x, pC[0].y);
  for (let k = 1; k < 4; k++) lowCtx.lineTo(pC[k].x, pC[k].y);
  lowCtx.closePath();
  lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
  lowCtx.fill();
  if (isSel || isHov) {
    lowCtx.lineWidth = isSel ? 2 : 1;
    lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
    lowCtx.stroke();
  }

  // Parâmetros de projeção e fatias
  const model = shelfItem.model;
  const p = project(shelfItem.x, shelfItem.y, effectiveLiftZ);
  const totalAngle = (shelfItem.selfAngle || 0) + turn;
  const scale = shelfItem.scale || 1.45;
  const sheet = model.sheet;
  const count = model.count;
  const w = model.w;
  const h = model.h;
  const originX = Math.floor(w / 2);
  const originY = Math.floor(h / 2);

  // CÁLCULO DE VISIBILIDADE DO VÃO FRONTAL (Visto de Frente vs de Lado vs de Trás)
  // Em coordenadas de fatia: o vão frontal aberto fica em +Y (y = h - 1).
  // Ao girar por totalAngle, o vetor normal frontal tem componente de tela Y = cos(totalAngle).
  const cosFront = Math.cos(totalAngle);
  // Se cosFront > 0.22: a abertura frontal da estante está voltada para a câmera (visão frontal/isométrica).
  // Se cosFront <= 0.22: a câmera está olhando a estante DE LADO ou DE TRÁS! O fundo maciço de madeira e as laterais bloqueiam a visão interna!
  const isFrontVisible = (cosFront > 0.22);

  // Agrupa props da estante por tier
  const props = activeItems.filter(it => it.surface === 'bookshelf' && !(it === selectedItem && isDraggingItem));
  const t1Props = props.filter(it => (it.tier || 1) === 1);
  const t2Props = props.filter(it => it.tier === 2);
  const t3Props = props.filter(it => it.tier === 3);
  const topProps = props.filter(it => it.tier === 4 || it.tier === 'top');

  function drawShelfSlices(fromZ, toZ) {
    for (let z = fromZ; z <= toZ && z < count; z++) {
      lowCtx.save();
      lowCtx.translate(p.x, Math.round(p.y - z * scale));
      lowCtx.scale(scale, squash * scale);
      lowCtx.rotate(totalAngle);
      lowCtx.drawImage(sheet, z * w, 0, w, h, -originX, -originY, w, h);
      lowCtx.restore();
    }
  }

  // Helper para redesenhar as paredes laterais maciças sobre os itens (garante 100% de oclusão lateral em qualquer ângulo)
  function drawShelfSideWalls(fromZ, toZ) {
    const wallThick = 5; // 5 pixels de espessura de madeira maciça em cada lateral
    for (let z = fromZ; z <= toZ && z < count; z++) {
      lowCtx.save();
      lowCtx.translate(p.x, Math.round(p.y - z * scale));
      lowCtx.scale(scale, squash * scale);
      lowCtx.rotate(totalAngle);
      // Lateral esquerda (x = 0 .. 4)
      lowCtx.drawImage(sheet, z * w, 0, wallThick, h, -originX, -originY, wallThick, h);
      // Lateral direita (x = w - wallThick .. w - 1)
      lowCtx.drawImage(sheet, z * w + (w - wallThick), 0, wallThick, h, -originX + (w - wallThick), -originY, wallThick, h);
      lowCtx.restore();
    }
  }

  if (!isFrontVisible) {
    // === VISÃO DE COSTAS OU DE LADO: ESTANTE 100% SÓLIDA E MACIÇA ===
    // O fundo de madeira maciça e as laterais cobrem totalmente o interior!
    // Não desenha os itens das prateleiras 1, 2 e 3 (estão fisicamente dentro da estante oculta).
    drawShelfSlices(0, count - 1);
    // Itens apoiados NO TOPO da estante continuam visíveis em 360°!
    topProps.sort((a, b) => a.depth - b.depth);
    for (const prop of topProps) renderItem(prop);
  } else {
    // === VISÃO FRONTAL OU 3/4: DESENHO EM CAMADAS COM OCLUSÃO LATERAL ===
    // 1. Plinto e Vão Inferior (z = 0 .. 13)
    drawShelfSlices(0, 13);
    t1Props.sort((a, b) => a.depth - b.depth);
    for (const prop of t1Props) renderItem(prop);
    drawShelfSideWalls(0, 13); // Paredes laterais cobrem as laterais dos livros!

    // 2. Prancha da Prateleira 2 e Vão Médio (z = 14 .. 26)
    drawShelfSlices(14, 26);
    t2Props.sort((a, b) => a.depth - b.depth);
    for (const prop of t2Props) renderItem(prop);
    drawShelfSideWalls(14, 26); // Paredes laterais cobrem as laterais das plantas/troféu!

    // 3. Prancha da Prateleira 3 e Vão Superior (z = 27 .. 39)
    drawShelfSlices(27, 39);
    t3Props.sort((a, b) => a.depth - b.depth);
    for (const prop of t3Props) renderItem(prop);
    drawShelfSideWalls(27, 39); // Paredes laterais cobrem o cristal!

    // 4. Cornija e Topo Esculpido (z = 40 .. 43)
    drawShelfSlices(40, count - 1);
    topProps.sort((a, b) => a.depth - b.depth);
    for (const prop of topProps) renderItem(prop);
  }

  // Marcador de seleção no Modo Decoração
  if (isSel && isDecorMode) {
    const topH = count * scale;
    const topP = project(shelfItem.x, shelfItem.y, effectiveLiftZ + topH + 10);
    lowCtx.fillStyle = '#D87D4A';
    lowCtx.beginPath();
    lowCtx.moveTo(topP.x, topP.y);
    lowCtx.lineTo(topP.x - 4, topP.y - 7);
    lowCtx.lineTo(topP.x + 4, topP.y - 7);
    lowCtx.closePath();
    lowCtx.fill();
  }
}

function renderItem(item) {
  const isSel = (item === selectedItem);
  const isHov = (item === hoveredItem && isDecorMode);

  const targetLift = (isSel && isDraggingItem && !item.isWallItem) ? 6 : 0;
  item.dragLift = item.dragLift || 0;
  item.dragLift += (targetLift - item.dragLift) * 0.3;
  const effectiveLiftZ = item.liftZ + item.dragLift;

  // Sombras e anéis de seleção
  if (!item.isWallItem) {
    // REGRA DE OURO: Itens sobre móveis (mesa ou prateleira) NÃO têm sombra no chão!
    const hasFloorShadow = !item.surface && (item.liftZ === 0 || item.isCat || item.isDesk || item.isSofa || item.isCoffeeTable || item.isTvRack || item.isBookshelf);

    if (hasFloorShadow) {
      if (item.isDesk || item.isSofa || item.isTvRack || item.isCoffeeTable || item.isBookshelf) {
        // Sombra retangular orientada e rotacionada com o móvel!
        const cosD = Math.cos(item.selfAngle || 0);
        const sinD = Math.sin(item.selfAngle || 0);
        const hw = item.isDesk ? 39 : (item.isSofa ? 27 : (item.isTvRack ? 25 : (item.isCoffeeTable ? 17 : 16)));
        const hh = item.isDesk ? 17 : (item.isSofa ? 14 : (item.isTvRack ? 10 : (item.isCoffeeTable ? 11 : 8)));
        const corners = [
          { x: item.x - hw * cosD + hh * sinD, y: item.y - hw * sinD - hh * cosD },
          { x: item.x + hw * cosD + hh * sinD, y: item.y + hw * sinD - hh * cosD },
          { x: item.x + hw * cosD - hh * sinD, y: item.y + hw * sinD + hh * cosD },
          { x: item.x - hw * cosD - hh * sinD, y: item.y - hw * sinD + hh * cosD }
        ];
        const pC = corners.map(c => project(c.x, c.y, 0));
        lowCtx.beginPath();
        lowCtx.moveTo(pC[0].x, pC[0].y);
        for (let k = 1; k < 4; k++) lowCtx.lineTo(pC[k].x, pC[k].y);
        lowCtx.closePath();
        lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
        lowCtx.fill();

        if (isSel || isHov) {
          lowCtx.lineWidth = isSel ? 2 : 1;
          lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
          lowCtx.stroke();
        }
      } else if (false) {
        // Sombra poligonal 100% orientada e rotacionada com a mesa!
        const cosD = Math.cos(item.selfAngle);
        const sinD = Math.sin(item.selfAngle);
        const hw = 39;
        const hh = 17;
        const corners = [
          { x: item.x - hw * cosD + hh * sinD, y: item.y - hw * sinD - hh * cosD },
          { x: item.x + hw * cosD + hh * sinD, y: item.y + hw * sinD - hh * cosD },
          { x: item.x + hw * cosD - hh * sinD, y: item.y + hw * sinD + hh * cosD },
          { x: item.x - hw * cosD - hh * sinD, y: item.y - hw * sinD + hh * cosD }
        ];
        const pC = corners.map(c => project(c.x, c.y, 0));
        lowCtx.beginPath();
        lowCtx.moveTo(pC[0].x, pC[0].y);
        for (let k = 1; k < 4; k++) lowCtx.lineTo(pC[k].x, pC[k].y);
        lowCtx.closePath();
        lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
        lowCtx.fill();

        if (isSel || isHov) {
          lowCtx.lineWidth = isSel ? 2 : 1;
          lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
          lowCtx.stroke();
        }
      } else {
        const shadowP = project(item.x, item.y, 0);
        lowCtx.save();
        lowCtx.translate(shadowP.x, shadowP.y);
        lowCtx.scale(1, squash * 0.45);
        lowCtx.beginPath();
        const baseRadius = (item.isCat ? 15 : (item.isChicken ? 14 : 20)) * (item.scale ? item.scale / 1.3 : 1);
        const shadowRadius = baseRadius * (1 + (item.dragLift || 0) * 0.05);
        lowCtx.arc(0, 0, shadowRadius, 0, Math.PI * 2);
        lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
        lowCtx.fill();

        if (isSel || isHov) {
          lowCtx.lineWidth = isSel ? 2 : 1;
          lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
          lowCtx.stroke();
        }
        lowCtx.restore();
      }
    } else if ((isSel || isHov) && isDecorMode) {
      // Apenas anel de seleção luminoso no plano da própria mesa ou prateleira
      const ringP = project(item.x, item.y, effectiveLiftZ);
      lowCtx.save();
      lowCtx.translate(ringP.x, ringP.y);
      lowCtx.scale(1, squash * 0.5);
      lowCtx.beginPath();
      const ringRadius = 16 * (item.scale ? item.scale / 1.3 : 1);
      lowCtx.arc(0, 0, ringRadius, 0, Math.PI * 2);
      lowCtx.lineWidth = isSel ? 2 : 1;
      lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
      lowCtx.stroke();
      lowCtx.restore();
    }

    // Indicadores nos 4 pés da mesa quando selecionada ou em hover no Modo Decoração
    if (item.isDesk && (isSel || isHov) && isDecorMode) {
      const cosD = Math.cos(item.selfAngle);
      const sinD = Math.sin(item.selfAngle);
      const legOffsets = [
        [-33, -11], [33, -11],
        [-33,  11], [33,  11]
      ];
      for (const [ox, oy] of legOffsets) {
        const lx = item.x + ox * cosD - oy * sinD;
        const ly = item.y + ox * sinD + oy * cosD;
        const pLeg = project(lx, ly, 0);
        lowCtx.save();
        lowCtx.translate(pLeg.x, pLeg.y);
        lowCtx.scale(1, squash * 0.5);
        lowCtx.beginPath();
        lowCtx.arc(0, 0, 7, 0, Math.PI * 2);
        lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.8)';
        lowCtx.lineWidth = isSel ? 2 : 1;
        lowCtx.stroke();
        lowCtx.restore();
      }
    }
  }

  // Desenho do objeto correspondente
  if (item.id === 'bookshelf' || item.isBookshelf) {
    drawModularBookshelf(item, items.filter(it => it.visible !== false));
    return;
  } else if (item.isCat) {
    drawCat(item, effectiveLiftZ);
  } else if (item.isChicken) {
    drawChicken(item, effectiveLiftZ);
  } else if (item.model) {
    drawStackObject(item.model, item.x, item.y, effectiveLiftZ, item.selfAngle, item.scale);
  } else if (item.id === 'shelf') {
    drawShelfItem(item);
  } else if (item.id === 'shelf_books') {
    drawShelfBooks(item);
  } else if (item.id === 'shelf_plant') {
    drawShelfPlant(item);
  } else if (item.id === 'shelf_crystal') {
    drawShelfCrystal(item);
  } else if (item.id === 'clock') {
    drawWallClock(item);
  } else if (item.id === 'corkboard' || item.id === 'frame_cat') {
    drawSingleFrame(item, 'corkboard');
  } else if (item.id === 'frame_plant') {
    drawSingleFrame(item, 'plant');
  } else if (item.isDoor || item.id === 'door' || (item.id && item.id.startsWith('door_'))) {
    drawDoor(item);
  }

  // Marcador e caixa de seleção no Modo Decoração
  if (isSel && isDecorMode) {
    const h = item.model ? item.model.count * (item.scale || 1.3) : 18;
    const topP = project(item.x, item.y, effectiveLiftZ + h + 10);
    lowCtx.fillStyle = '#D87D4A';
    lowCtx.beginPath();
    lowCtx.moveTo(topP.x, topP.y);
    lowCtx.lineTo(topP.x - 4, topP.y - 7);
    lowCtx.lineTo(topP.x + 4, topP.y - 7);
    lowCtx.closePath();
    lowCtx.fill();

    if (item.isWallItem) {
      const pC = project(item.x, item.y, effectiveLiftZ);
      lowCtx.strokeStyle = '#D87D4A';
      lowCtx.lineWidth = 1;
      lowCtx.strokeRect(pC.x - 14, pC.y - 14, 28, 28);
    }
  }
}

// --- 3. SISTEMA DE ORDENAÇÃO E RENDERIZAÇÃO 3D (ZERO CLIPPING NA MESA!) ---
function drawAll3DObjects() {
  const cosA = Math.cos(turn);
  const sinA = Math.sin(turn);

  const activeItems = items.filter(it => it.visible !== false);

  activeItems.forEach(item => {
    item.depth = item.x * sinA + item.y * cosA;
    item.p = project(item.x, item.y, item.liftZ);
  });

  // 1. Itens da Parede Oeste (só renderiza se a parede oeste for parede de trás)
  const isWestWallVisible = (-1 * sinA <= 0.05);
  if (isWestWallVisible) {
    // Exclui itens apoiados na prateleira para renderizá-los diretamente em cima dela
    const westWallMains = activeItems.filter(it => it.isWallItem && it.wall === 'west' && it.surface !== 'shelf');
    westWallMains.sort((a, b) => a.depth - b.depth);
    for (const item of westWallMains) {
      renderItem(item);

      // Ao renderizar a prateleira, desenha IMEDIATAMENTE todos os acessórios apoiados nela!
      if (item.id === 'shelf') {
        const shelfProps = activeItems.filter(it => it.surface === 'shelf');
        shelfProps.sort((a, b) => a.depth - b.depth);
        for (const prop of shelfProps) {
          renderItem(prop);
        }
      }
    }
  }

  // 2. Itens da Parede Leste (só renderiza se a parede leste for parede de trás)
  const isEastWallVisible = (1 * sinA <= 0.05);
  if (isEastWallVisible) {
    const eastWallItems = activeItems.filter(it => it.isWallItem && it.wall === 'east');
    eastWallItems.sort((a, b) => a.depth - b.depth);
    for (const item of eastWallItems) {
      renderItem(item);
    }
  }

  // 3. Itens da Parede Sul (só renderiza se a parede sul for parede de trás)
  const isSouthWallVisible = (1 * cosA <= 0.05);
  if (isSouthWallVisible) {
    const southWallItems = activeItems.filter(it => it.isWallItem && it.wall === 'south');
    southWallItems.sort((a, b) => a.depth - b.depth);
    for (const item of southWallItems) {
      renderItem(item);
    }
  }

  // 4. Itens da Parede Norte (só renderiza se a parede norte for parede de trás)
  const isNorthWallVisible = (-1 * cosA <= 0.05);
  if (isNorthWallVisible) {
    const northWallItems = activeItems.filter(it => it.isWallItem && it.wall === 'north');
    northWallItems.sort((a, b) => a.depth - b.depth);
    for (const item of northWallItems) {
      renderItem(item);
    }
  }

  // 3. Itens de chão (exclui itens de parede, itens na mesa, prateleira e estante)
  const floorItems = activeItems.filter(it => !it.isWallItem && it.surface !== 'desk' && it.surface !== 'shelf' && it.surface !== 'bookshelf');
  floorItems.sort((a, b) => a.depth - b.depth);

  for (const item of floorItems) {
    renderItem(item);

// Bookshelf modular rendering handled in drawModularBookshelf

    // SE O ITEM FOR A MESA, DESENHA IMEDIATAMENTE TODOS OS ITENS APOIADOS NELA!
    if (item.id === 'desk') {
      // Indicadores sutis de Snap-to-Slot no tampo da mesa no Modo Decoração
      if (isDecorMode && (isDraggingItem || hoveredItem)) {
        const cosD = Math.cos(item.selfAngle);
        const sinD = Math.sin(item.selfAngle);
        for (const slot of DESK_SLOTS) {
          const sx = item.x + slot.offX * cosD - slot.offY * sinD;
          const sy = item.y + slot.offX * sinD + slot.offY * cosD;
          const sp = project(sx, sy, 21.2);
          lowCtx.save();
          lowCtx.translate(sp.x, sp.y);
          lowCtx.scale(1, squash * 0.5);
          lowCtx.beginPath();
          lowCtx.arc(0, 0, 6, 0, Math.PI * 2);
          lowCtx.strokeStyle = 'rgba(216, 125, 74, 0.65)';
          lowCtx.lineWidth = 1.2;
          lowCtx.stroke();
          lowCtx.restore();
        }
      }

      const deskProps = activeItems.filter(it => it.surface === 'desk');
      deskProps.sort((a, b) => a.depth - b.depth);
      for (const prop of deskProps) {
        renderItem(prop);
      }
    }
  }

  // DESENHA O ITEM ARRASTADO NO TOPO DE TUDO (NUNCA SOME DA TELA!)
  if (isDraggingItem && selectedItem && !selectedItem.isWallItem) {
    renderItem(selectedItem);
  }
}

// Corações flutuantes de carinho
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

// --- LOOP PRINCIPAL DE RENDERIZAÇÃO ---
function render() {
  turn += (targetTurn - turn) * 0.1;

  if (autoSpin) {
    targetTurn += 0.006;
  }

  // Atualiza a IA e animação do gatinho a 60 FPS
  updateCatAI();
updateChickenAI();

// Oscilação suave do Balanço de Pneu no Jardim
const swingObj = items.find(it => it.id === 'tire_swing');
if (swingObj) {
  swingObj.selfAngle = Math.sin(Date.now() * 0.002) * 0.10;
}

  if (currentRoomId === 'garden') {
    // CÉU AZUL ENSOLARADO DO JARDIM EXTERNO ABERTO!
    const skyGrad = lowCtx.createLinearGradient(0, 0, 0, LOW_H);
    skyGrad.addColorStop(0, '#38BDF8');   // Azul céu ensolarado
    skyGrad.addColorStop(0.40, '#7DD3FC'); // Azul suave
    skyGrad.addColorStop(0.75, '#BAE6FD'); // Horizonte claro
    skyGrad.addColorStop(1, '#E0F2FE');
    lowCtx.fillStyle = skyGrad;
    lowCtx.fillRect(0, 0, LOW_W, LOW_H);

    // Nuvens brancas suaves no topo do céu
    lowCtx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    lowCtx.beginPath(); lowCtx.arc(50, 40, 22, 0, Math.PI * 2); lowCtx.fill();
    lowCtx.beginPath(); lowCtx.arc(70, 36, 16, 0, Math.PI * 2); lowCtx.fill();
    lowCtx.beginPath(); lowCtx.arc(260, 55, 28, 0, Math.PI * 2); lowCtx.fill();
    lowCtx.beginPath(); lowCtx.arc(285, 50, 20, 0, Math.PI * 2); lowCtx.fill();
  } else {
    lowCtx.fillStyle = P.bg;
    lowCtx.fillRect(0, 0, LOW_W, LOW_H);
  }

  // 1. Paredes de trás
  drawWalls();

  // 2. Chão com grid
  drawFloor();

  // 3. Móveis e itens modulares 3D
  drawAll3DObjects();

  // 4. Efeitos
  drawHearts();

  // Upscale nítido para o viewport principal (Canvas 800x800)
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

  requestAnimationFrame(render);
}

