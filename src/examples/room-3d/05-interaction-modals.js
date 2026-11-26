// --- SISTEMA DE HIT DETECTION E DRAG & DROP MODULAR ---
function getCanvasCoords(e) {
  const rect = canvas.getBoundingClientRect();
  const sx = ((e.clientX - rect.left) / rect.width) * LOW_W;
  const sy = ((e.clientY - rect.top) / rect.height) * LOW_H;
  return { sx, sy };
}

function findItemAt(worldPos, screenPos) {
  const sinA = Math.sin(turn);
  const isWestWallVisible = (-1 * sinA <= 0.05);
  const isEastWallVisible = (1 * sinA <= 0.05);

  const activeItems = items.filter(it => {
    if (it.visible === false) return false;
    if (isDecorMode) {
      if (currentRoomId === 'kitchen') {
        const isMovableKitchen = (it.id === 'dining_table' || it.id.startsWith('dining_chair') || it.id === 'fruit_bowl');
        if (!isMovableKitchen) return false;
      } else if (currentRoomId === 'garden') {
        const isMovableGarden = (it.id === 'porch_chair' || it.id === 'wheelbarrow_flowers');
        if (!isMovableGarden) return false;
      } else {
        if (it.isFixed || it.isDoor || it.isWallItem) return false;
      }
    }
    return true;
  });

  // FASE 1: Prioridade Máxima para acessórios universais (na mesa, na prateleira ou no chão)
  // Se o usuário clicar em qualquer acessório, SEMPRE seleciona o acessório diretamente!
  const props = activeItems.filter(it => it.isProp);
  for (const item of props) {
    const p = project(item.x, item.y, item.liftZ + 6);
    const dScreen = Math.hypot(screenPos.sx - p.x, screenPos.sy - p.y);
    if (dScreen < (item.radius || 15)) {
      return item;
    }
  }

  // FASE 2: Itens de parede (se a parede estiver visível)
  const wallProps = activeItems.filter(it => it.isWallItem);
  for (const item of wallProps) {
    if (item.wall === 'west' && !isWestWallVisible) continue;
    if (item.wall === 'east' && !isEastWallVisible) continue;
    const p = project(item.x, item.y, item.liftZ);
    const dScreen = Math.hypot(screenPos.sx - p.x, screenPos.sy - p.y);
    if (dScreen < (item.radius || 20)) {
      return item;
    }
  }

  // FASE 3: O Gatinho e outros itens de chão
  const floorMobiles = activeItems.filter(it => !it.isWallItem && !it.isProp && !it.isDesk);
  const sortedFloor = [...floorMobiles].sort((a, b) => b.depth - a.depth);
  for (const item of sortedFloor) {
    const h = item.model ? item.model.count * (item.scale || 1.3) : 20;
    const pBot = project(item.x, item.y, item.liftZ);
    const pTop = project(item.x, item.y, item.liftZ + h);
    const midY = (pBot.y + pTop.y) / 2;
    const dScreen = Math.hypot(screenPos.sx - pBot.x, screenPos.sy - midY);
    if (dScreen < (item.radius || 20)) {
      return item;
    }
    const dWorld = Math.hypot(worldPos.x - item.x, worldPos.y - item.y);
    if (dWorld < (item.radius || 20)) {
      return item;
    }
  }

  // FASE 4: Móvel Grande (A Mesa de Estudo)
  // "Pegar pelo Pé": detecta clique nos 4 pés da mesa no chão ou na base do piso!
  const desk = activeItems.find(it => it.id === 'desk');
  if (desk) {
    // Checa distância aos 4 pés no chão
    const cosD = Math.cos(desk.selfAngle);
    const sinD = Math.sin(desk.selfAngle);
    const legOffsets = [
      [-33, -11], [33, -11],
      [-33,  11], [33,  11]
    ];
    for (const [ox, oy] of legOffsets) {
      const lx = desk.x + ox * cosD - oy * sinD;
      const ly = desk.y + ox * sinD + oy * cosD;
      const pLeg = project(lx, ly, 0);
      const dLeg = Math.hypot(screenPos.sx - pLeg.x, screenPos.sy - pLeg.y);
      if (dLeg < 16) {
        return desk; // Pegou diretamente por um dos pés!
      }
    }

    // Também permite pegar clicando no centro/sombra no chão
    const pCenterFloor = project(desk.x, desk.y, 0);
    const dFloor = Math.hypot(screenPos.sx - pCenterFloor.x, screenPos.sy - pCenterFloor.y);
    if (dFloor < 30) {
      return desk;
    }

    // Ou clicando no tampo livre onde não tem acessório
    const dWorld = Math.hypot(worldPos.x - desk.x, worldPos.y - desk.y);
    if (dWorld < desk.radius) {
      return desk;
    }
  }

  return null;
}

function rotateSelectedItem() {
  if (selectedItem && !selectedItem.isWallItem) {
    selectedItem.selfAngle = (selectedItem.selfAngle + Math.PI / 2) % (Math.PI * 2);

    // SISTEMA UNIFICADO DE PARENTING: Se rotacionar qualquer móvel de superfície (mesa, estante, mesinha), rotaciona todos os itens apoiados nele!
    if (selectedItem.id === 'desk' || selectedItem.id === 'bookshelf' || selectedItem.isBookshelf || selectedItem.id === 'coffee_table' || selectedItem.id === 'dining_table') {
      const surfId = (selectedItem.id === 'bookshelf' || selectedItem.isBookshelf) ? 'bookshelf' : selectedItem.id;
      const cosP = Math.cos(selectedItem.selfAngle || 0);
      const sinP = Math.sin(selectedItem.selfAngle || 0);
      for (const it of items) {
        if (it.surface === surfId) {
          it.x = selectedItem.x + (it.offX || 0) * cosP - (it.offY || 0) * sinP;
          it.y = selectedItem.y + (it.offX || 0) * sinP + (it.offY || 0) * cosP;
          it.selfAngle = selectedItem.selfAngle;
        }
      }
    }
  }
}

window.addEventListener('keydown', (e) => {
  if (e.key === 'r' || e.key === 'R') {
    rotateSelectedItem();
  }
});

// Funções de Bounding Quad e Culling do Mural de Post-its
function isPointInWallQuad(px, py, p1, p2, p3, p4, tolerance = 3) {
  function cross(a, b, x, y) {
    return (b.x - a.x) * (y - a.y) - (b.y - a.y) * (x - a.x);
  }
  const c1 = cross(p1, p2, px, py);
  const c2 = cross(p2, p3, px, py);
  const c3 = cross(p3, p4, px, py);
  const c4 = cross(p4, p1, px, py);
  const allPos = (c1 >= -tolerance && c2 >= -tolerance && c3 >= -tolerance && c4 >= -tolerance);
  const allNeg = (c1 <= tolerance && c2 <= tolerance && c3 <= tolerance && c4 <= tolerance);
  return allPos || allNeg;
}

function getCorkboardQuad() {
  const corkboard = items.find(it => (it.id === 'corkboard' || it.id === 'frame_cat') && it.visible !== false);
  if (!corkboard) return null;

  // Se a parede leste estiver sumindo ou virando para a frente (culled), a área de clique some 100%!
  const sinA = Math.sin(turn);
  if (sinA > -0.08) return null; // Parede oculta ou de perfil extremo

  const xWall = ROOM_R;
  const p1 = project(xWall - 0.5, corkboard.y - 24, corkboard.liftZ - 26);
  const p2 = project(xWall - 0.5, corkboard.y + 24, corkboard.liftZ - 26);
  const p3 = project(xWall - 0.5, corkboard.y + 24, corkboard.liftZ + 26);
  const p4 = project(xWall - 0.5, corkboard.y - 24, corkboard.liftZ + 26);

  // Conforme a parede vira, a largura na tela diminui: se for < 8px, já sumiu para o clique!
  const projW = Math.max(p1.x, p2.x, p3.x, p4.x) - Math.min(p1.x, p2.x, p3.x, p4.x);
  if (projW < 8) return null;

  return { p1, p2, p3, p4, projW };
}

let isDraggingView = false;
let lastX = 0;
let pointerDownPos = { x: 0, y: 0 };
let isPressedOnCorkboard = false;

canvas.addEventListener('pointerdown', (e) => {
  const { sx, sy } = getCanvasCoords(e);
  const worldPos = unproject(sx, sy);
  pointerDownPos = { x: e.clientX, y: e.clientY };
  isPressedOnCorkboard = false;

  if (!isDecorMode) {
    // A área de clique acompanha perfeitamente a perspectiva 3D e some quando a parede vira!
    const q = getCorkboardQuad();
    if (q && isPointInWallQuad(sx, sy, q.p1, q.p2, q.p3, q.p4, 3)) {
      isPressedOnCorkboard = true;
      return;
    }
  }

  if (isDecorMode) {
    const item = findItemAt(worldPos, { sx, sy });
    if (item) {
      selectedItem = item;
      isDraggingItem = true;
      dragStartPos = { sx, sy };
      itemStartPos = { x: item.x, y: item.y, liftZ: item.liftZ };
      dragOffset.x = item.x - worldPos.x;
      dragOffset.y = item.y - worldPos.y;
      btnRotateMob.style.display = item.isWallItem ? 'none' : 'inline-flex';
      canvas.classList.add('decor-dragging');
      return;
    } else {
      selectedItem = null;
      btnRotateMob.style.display = 'none';
    }
  }

  isDraggingView = true;
  lastX = e.clientX;
  autoSpin = false;
  btnAutoSpin.classList.remove('active');
});

window.addEventListener('pointermove', (e) => {
  const { sx, sy } = getCanvasCoords(e);
  const worldPos = unproject(sx, sy);

  if (!isDecorMode && !isDraggingView) {
    const corkboard = items.find(it => (it.id === 'corkboard' || it.id === 'frame_cat') && it.visible !== false);
    if (corkboard) {
      const pBoard = project(corkboard.x, corkboard.y, corkboard.liftZ);
      if (Math.hypot(sx - pBoard.x, sy - pBoard.y) < 48) {
        canvas.style.cursor = 'pointer';
        canvas.title = '📌 Clique para abrir o Mural de Post-its!';
      } else {
        canvas.style.cursor = '';
        canvas.title = '';
      }
    }
  }

  if (isDecorMode && !isDraggingItem && !isDraggingView) {
    hoveredItem = findItemAt(worldPos, { sx, sy });
    if (hoveredItem) {
      canvas.classList.add('decor-hover');
      if (hoveredItem.isDesk) {
        bannerInfo.innerHTML = `<span>🐾 <b>Móvel:</b> 🪵 Mesa de Estudo — arraste pelos pés para mover tudo!</span>`;
      } else if (hoveredItem.onDesk) {
        bannerInfo.innerHTML = `<span>🐾 <b>Acessório:</b> ${hoveredItem.icon || ''} ${hoveredItem.name} — clique para reposicionar no tampo!</span>`;
      } else if (hoveredItem.isWallItem) {
        bannerInfo.innerHTML = `<span>🐾 <b>Parede:</b> ${hoveredItem.icon || ''} ${hoveredItem.name} — arraste para subir, descer ou deslizar!</span>`;
      } else {
        bannerInfo.innerHTML = `<span>🐾 <b>Item:</b> ${hoveredItem.icon || ''} ${hoveredItem.name} — arraste pelo quarto!</span>`;
      }
    } else {
      canvas.classList.remove('decor-hover');
      if (selectedItem) {
        bannerInfo.innerHTML = `<span>🛠️ <b>Selecionado:</b> ${selectedItem.icon || ''} ${selectedItem.name} (Girar com Tecla R)</span>`;
      } else {
        bannerInfo.innerHTML = `<span>🛠️ <b>Modo Decoração:</b> Arraste móveis, prateleira, quadros, relógio ou o gatinho!</span>`;
      }
    }
  }

  // Arrastando objeto selecionado
  if (isDraggingItem && selectedItem) {
    if (selectedItem.isWallItem) {
      // Arrastando item de parede na horizontal e vertical (altura Z)
      const dsx = sx - dragStartPos.sx;
      const dsy = sy - dragStartPos.sy;

      const newZ = Math.round(itemStartPos.liftZ - dsy * 0.8);
      selectedItem.liftZ = Math.max(35, Math.min(92, newZ));

      const sinA = Math.sin(turn);
      // O movimento horizontal na tela dxScreen = -sinA * dy, portanto dir = (sinA > 0 ? -1 : 1)
      // Isso garante que puxar o mouse para a direita SEMPRE mova o item para a direita na tela!
      const dir = (sinA > 0 ? -1 : 1);
      const newY = Math.round(itemStartPos.y + dsx * dir * 0.8);
      const limit = ROOM_R - 30;
      selectedItem.y = Math.max(-limit, Math.min(limit, newY));

      // Se moveu a prateleira inteira, atualiza os itens apoiados nela PRESERVANDO sua posição offY exata!
      if (selectedItem.id === 'shelf') {
        for (const it of items) {
          if (it.surface === 'shelf') {
            it.x = -ROOM_R + 9;
            it.y = selectedItem.y + it.offY;
            it.liftZ = selectedItem.liftZ + 3.5;
          }
        }
      }
      return;
    }

    // Arrastando item de chão / mesa
    let newX = worldPos.x + dragOffset.x;
    let newY = worldPos.y + dragOffset.y;

    newX = Math.round(newX / 4) * 4;
    newY = Math.round(newY / 4) * 4;

    const desk = items.find(it => it.id === 'desk');

    // Cálculo de limites de colisão com a parede (SEM vazar nem atravessar!)
    let halfW = 20;
    let halfH = 20;
    if (selectedItem.id === 'desk') {
      const isRot = (selectedItem.selfAngle === Math.PI / 2 || selectedItem.selfAngle === Math.PI * 1.5);
      halfW = isRot ? 18 : 33;
      halfH = isRot ? 33 : 18;
    } else if (selectedItem.radius) {
      halfW = Math.round(selectedItem.radius * 0.85);
      halfH = Math.round(selectedItem.radius * 0.85);
    }

    const limitX = ROOM_R - halfW - 2;
    const limitY = ROOM_R - halfH - 2;

    // Snap magnético alinhando com o rodapé das paredes
    if (selectedItem.id === 'desk') {
      if (newY < -limitY + 10) newY = -limitY;
      if (newY > limitY - 10) newY = limitY;
      if (newX < -limitX + 10) newX = -limitX;
      if (newX > limitX - 10) newX = limitX;
    }

    selectedItem.x = Math.max(-limitX, Math.min(limitX, newX));
    selectedItem.y = Math.max(-limitY, Math.min(limitY, newY));

    // SISTEMA UNIFICADO DE PARENTING: Se estiver arrastando qualquer móvel com superfície (mesa, estante, mesinha), move todos os itens apoiados nele juntos!
    if (selectedItem.id === 'desk' || selectedItem.id === 'bookshelf' || selectedItem.isBookshelf || selectedItem.id === 'coffee_table' || selectedItem.id === 'dining_table') {
      const surfId = (selectedItem.id === 'bookshelf' || selectedItem.isBookshelf) ? 'bookshelf' : selectedItem.id;
      const cosP = Math.cos(selectedItem.selfAngle || 0);
      const sinP = Math.sin(selectedItem.selfAngle || 0);
      for (const it of items) {
        if (it.surface === surfId) {
          it.x = selectedItem.x + (it.offX || 0) * cosP - (it.offY || 0) * sinP;
          it.y = selectedItem.y + (it.offX || 0) * sinP + (it.offY || 0) * cosP;
          it.selfAngle = selectedItem.selfAngle;
        }
      }
    } else if (selectedItem.isProp || selectedItem.isCat || selectedItem.isChicken) {
      // ACESSÓRIO UNIVERSAL OU PET: pode ser colocado na mesa, sofá, mesinha, estante, prateleira ou chão!
      const shelf = items.find(it => it.id === 'shelf');
      const sofa = items.find(it => it.id === 'sofa');
      const coffeeTable = items.find(it => it.id === 'coffee_table');
      const bookshelf = items.find(it => it.id === 'bookshelf' || it.isBookshelf);

      // Checa se está sobre a ESTANTE
      let onBookshelfArea = false;
      let bsLocalX = 0, bsLocalY = 0, cosB = 1, sinB = 0;
      if (bookshelf && bookshelf.visible !== false) {
        cosB = Math.cos(bookshelf.selfAngle || 0);
        sinB = Math.sin(bookshelf.selfAngle || 0);
        const rbx = selectedItem.x - bookshelf.x;
        const rby = selectedItem.y - bookshelf.y;
        bsLocalX =  rbx * cosB + rby * sinB;
        bsLocalY = -rbx * sinB + rby * cosB;
        onBookshelfArea = Math.abs(bsLocalX) < 28 && Math.abs(bsLocalY) < 18;
      }

      // Checa se está sobre o SOFÁ
      const onSofaArea = sofa && sofa.visible !== false && Math.abs(selectedItem.x - sofa.x) < 32 && Math.abs(selectedItem.y - sofa.y) < 18;
      // Checa se está sobre a MESINHA DE CENTRO
      const onTableArea = coffeeTable && coffeeTable.visible !== false && Math.abs(selectedItem.x - coffeeTable.x) < 20 && Math.abs(selectedItem.y - coffeeTable.y) < 14;

      // Checa se está sobre a MESA DO QUARTO
      let onDeskArea = false;
      let localX = 0, localY = 0, cosD = 1, sinD = 0;
      if (desk) {
        cosD = Math.cos(desk.selfAngle);
        sinD = Math.sin(desk.selfAngle);
        const rwx = selectedItem.x - desk.x;
        const rwy = selectedItem.y - desk.y;
        localX =  rwx * cosD + rwy * sinD;
        localY = -rwx * sinD + rwy * cosD;
        onDeskArea = Math.abs(localX) < 44 && Math.abs(localY) < 22;
      }

      // Checa se está sobre a PRATELEIRA DA PAREDE
      const onShelfArea = shelf && Math.abs(selectedItem.x - (-ROOM_R + 9)) < 22 && Math.abs(selectedItem.y - shelf.y) < (shelf.length / 2 + 6);

      if (onBookshelfArea) {
        // Colocou NA ESTANTE!
        selectedItem.surface = 'bookshelf';

        // Determina a prateleira com base na altura ou mouse
        const currentZ = selectedItem.liftZ || 0;
        let tierZ = 3.5; // Prateleira 1 (Inferior)
        let tierNum = 1;
        if (currentZ > 36) {
          tierZ = 43.5; // Topo da estante
          tierNum = 4;
        } else if (currentZ > 23) {
          tierZ = 29.5; // Prateleira 3 (Superior)
          tierNum = 3;
        } else if (currentZ > 10) {
          tierZ = 16.5; // Prateleira 2 (Média)
          tierNum = 2;
        }
        selectedItem.liftZ = tierZ;
        selectedItem.tier = tierNum;

        // Snap magnético inteligente nos 3 slots (Esq: -8, Centro: 0, Dir: 8)
        let snapSlotX = 0;
        if (bsLocalX < -4.5) snapSlotX = -8;
        else if (bsLocalX > 4.5) snapSlotX = 8;
        else snapSlotX = 0;

        selectedItem.offX = snapSlotX;
        selectedItem.offY = 0;
        selectedItem.x = bookshelf.x + snapSlotX * cosB;
        selectedItem.y = bookshelf.y + snapSlotX * sinB;
        selectedItem.selfAngle = bookshelf.selfAngle;

        if (selectedItem.isCat) {
          selectedItem.liftZ = 41.5; // Gatinho dorme no topo da estante!
          selectedItem.state = 'idle';
          selectedItem.posture = 'loaf';
          selectedItem.isWalking = false;
        } else if (selectedItem.isChicken) {
          selectedItem.liftZ = tierZ;
          selectedItem.state = selectedItem.id === 'chicken' ? 'brood' : 'idle';
          selectedItem.isWalking = false;
        }
      } else if (onSofaArea) {
        selectedItem.surface = 'sofa';
        selectedItem.liftZ = 9;
        if (selectedItem.isCat) {
          selectedItem.sofaSleepTimer = 360;
          selectedItem.state = 'idle';
          selectedItem.posture = 'loaf';
          selectedItem.isWalking = false;
        }
      } else if (onTableArea) {
        selectedItem.surface = 'coffee_table';
        selectedItem.liftZ = 9;
        if (selectedItem.isCat) {
          selectedItem.state = 'idle';
          selectedItem.posture = 'sit';
          selectedItem.isWalking = false;
        }
      } else if (onDeskArea) {
        // Colocou NA MESA!
        selectedItem.surface = 'desk';
        selectedItem.liftZ = 21;

        if (selectedItem.isProp) {
          // Snap magnético aos slots do tampo (The Sims / Animal Crossing)
          let closestSlot = null;
          let minDist = 14;
          for (const slot of DESK_SLOTS) {
            const d = Math.hypot(localX - slot.offX, localY - slot.offY);
            if (d < minDist) {
              minDist = d;
              closestSlot = slot;
            }
          }
          const snapLocalX = closestSlot ? closestSlot.offX : localX;
          const snapLocalY = closestSlot ? closestSlot.offY : localY;

          const worldOffX = snapLocalX * cosD - snapLocalY * sinD;
          const worldOffY = snapLocalX * sinD + snapLocalY * cosD;

          selectedItem.offX = worldOffX;
          selectedItem.offY = worldOffY;
          selectedItem.x = desk.x + worldOffX;
          selectedItem.y = desk.y + worldOffY;
          selectedItem.selfAngle = desk.selfAngle;
        } else if (selectedItem.isCat) {
          // Gato colocado na mesa: dorme ali por um tempo antes de descer!
          const clampLX = Math.max(-32, Math.min(32, localX));
          const clampLY = Math.max(-11, Math.min(11, localY));
          selectedItem.offX = clampLX * cosD - clampLY * sinD;
          selectedItem.offY = clampLX * sinD + clampLY * cosD;
          selectedItem.x = desk.x + selectedItem.offX;
          selectedItem.y = desk.y + selectedItem.offY;
          selectedItem.deskSleepTimer = 360 + Math.floor(Math.random() * 240); // 6 a 10s dormindo
          selectedItem.state = 'idle';
          selectedItem.posture = 'loaf';
          selectedItem.isWalking = false;
        } else if (selectedItem.isChicken) {
          // Pintinho ou Popó na mesa
          const clampLX = Math.max(-34, Math.min(34, localX));
          const clampLY = Math.max(-12, Math.min(12, localY));
          selectedItem.offX = clampLX * cosD - clampLY * sinD;
          selectedItem.offY = clampLX * sinD + clampLY * cosD;
          selectedItem.x = desk.x + selectedItem.offX;
          selectedItem.y = desk.y + selectedItem.offY;
          selectedItem.state = 'idle';
          selectedItem.stateTimer = 90;
          selectedItem.isWalking = false;
        }
      } else if (onShelfArea) {
        // Colocou NA PRATELEIRA!
        selectedItem.surface = 'shelf';
        selectedItem.liftZ = shelf.liftZ + 3.5;
        selectedItem.x = -ROOM_R + 9;
        selectedItem.offY = Math.max(-shelf.length / 2 + 8, Math.min(shelf.length / 2 - 8, selectedItem.y - shelf.y));
        selectedItem.y = shelf.y + selectedItem.offY;
        selectedItem.selfAngle = 0;
        if (selectedItem.isCat) {
          selectedItem.state = 'idle';
          selectedItem.posture = 'loaf';
          selectedItem.isWalking = false;
        } else if (selectedItem.isChicken) {
          selectedItem.state = selectedItem.id === 'chicken' ? 'brood' : 'idle';
          selectedItem.stateTimer = 240;
          selectedItem.isWalking = false;
        }
      } else {
        // Colocou NO CHÃO!
        selectedItem.surface = null;
        selectedItem.liftZ = 0;
        if (selectedItem.isCat) selectedItem.deskSleepTimer = 0;
      }
    }
    return;
  }

  // Arrastando visão do quarto
  if (isDraggingView) {
    const dx = e.clientX - lastX;
    lastX = e.clientX;
    targetTurn += dx * 0.015;
  }
});

window.addEventListener('pointerup', (e) => {
  if (!isDecorMode && !isDraggingItem && pointerDownPos) {
    const moved = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y);
    const { sx, sy } = getCanvasCoords(e);
    const worldPos = unproject(sx, sy);

    // Clique no Mural de Post-its abre o Zoom / Modal de Lembretes!
    const q = getCorkboardQuad();
    if (q) {
      const isInside = isPointInWallQuad(sx, sy, q.p1, q.p2, q.p3, q.p4, 4);
      if (isPressedOnCorkboard || (moved < 25 && isInside)) {
        isPressedOnCorkboard = false;
        openCorkboardModal();
        return;
      }
    }
    isPressedOnCorkboard = false;

    if (moved < 18) {

      // Clique na Galinha Cocoricó faz ela cacarejar alegremente!
      const chk = items.find(it => it.id === 'chicken' && it.visible !== false);
      if (chk) {
        const dChk = Math.hypot(worldPos.x - chk.x, worldPos.y - chk.y);
        if (dChk < 22) {
          playChickenSound();
          hearts.push({ x: chk.x, y: chk.y, z: chk.liftZ + 16, life: 1.0 });
          return;
        }
      }

      // Checa clique em qualquer porta do cômodo atual
      // Clique na Geladeira Retrô abre a Lista de Compras na porta da geladeira!
      const fridgeItem = items.find(it => (it.id === 'fridge_retro' || it.isFridge) && it.visible !== false);
      if (fridgeItem) {
        const dFridge = Math.hypot(worldPos.x - fridgeItem.x, worldPos.y - fridgeItem.y);
        if (dFridge < 30) {
          openFridgeModal();
          return;
        }
      }

      const clickedDoor = items.find(it => (it.isDoor || it.id === 'door' || it.id.startsWith('door_')) && it.visible !== false && (() => {
        const wallNorm = (it.wall === 'west') ? {x:-1, y:0} : (it.wall === 'south') ? {x:0, y:1} : (it.wall === 'north') ? {x:0, y:-1} : {x:1, y:0};
        const isWallVis = (wallNorm.x * Math.sin(turn) + wallNorm.y * Math.cos(turn) <= 0.05);
        if (!isWallVis) return false;
        const pDoor = project(it.x, it.y, 38);
        return Math.hypot(sx - pDoor.x, sy - pDoor.y) < 32;
      })());

      if (clickedDoor) {
        clickedDoor.isOpen = !clickedDoor.isOpen;
        playDoorSound(clickedDoor.isOpen);
        if (clickedDoor.targetRoom) {
          if (clickedDoor.targetRoom === 'kitchen' || clickedDoor.targetRoom === 'garden') {
            switchRoom(clickedDoor.targetRoom);
          } else {
            migratePetsToDoor(clickedDoor, () => switchRoom(clickedDoor.targetRoom, true));
          }
        }
        return;
      }
      const cat = items.find(it => it.id === 'cat');
      if (cat) {
        const dCat = Math.hypot(worldPos.x - cat.x, worldPos.y - cat.y);
        if (dCat < 24) {
          triggerPetReactions(cat);
        } else if (Math.abs(worldPos.x) < ROOM_R - 18 && Math.abs(worldPos.y) < ROOM_R - 18) {
          const valid = checkCatCollision(worldPos.x, worldPos.y);
          cat.targetX = valid.x;
          cat.targetY = valid.y;
          cat.state = 'walking';
          cat.posture = 'walk';
        }
      }
    }
  }
  isDraggingItem = false;
  isDraggingView = false;
  canvas.classList.remove('decor-dragging');
});


// --- ÁUDIO DA GALINHA E TACHINHA ---
function playChickenSound() {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(360, now);
    osc.frequency.exponentialRampToValueAtTime(580, now + 0.05);
    osc.frequency.exponentialRampToValueAtTime(260, now + 0.16);
    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(1400, now);
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.2, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.19);
  } catch(e) {}
}

function playTackSound() {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(540, now);
    osc.frequency.exponentialRampToValueAtTime(120, now + 0.04);
    gain.gain.setValueAtTime(0.18, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.05);
  } catch(e) {}
}

// --- GERENCIADOR DO MURAL DE POST-ITS (localStorage) ---
const corkboardModal = document.getElementById('corkboardModal');
const btnCloseCorkboard = document.getElementById('btnCloseCorkboard');
const corkboardSurface = document.getElementById('corkboardSurface');
const corkboardPadBtn = document.getElementById('corkboardPadBtn');

const noteEditorModal = document.getElementById('noteEditorModal');
const noteEditorCard = document.getElementById('noteEditorCard');
const noteTextarea = document.getElementById('noteTextarea');
const btnSaveNote = document.getElementById('btnSaveNote');
const btnDeleteNote = document.getElementById('btnDeleteNote');
const btnCancelNote = document.getElementById('btnCancelNote');
const colorDots = document.querySelectorAll('.color-dot');

let currentEditingNoteId = null;
let selectedNoteColor = '#FEF08A';

const PASTEL_COLORS = ['#FEF08A', '#FBCFE8', '#BBF7D0', '#BAE6FD', '#E9D5FF', '#FED7AA'];

function getSavedNotes() {
  try {
    const raw = localStorage.getItem('purrmodoro_notes');
    if (raw) return JSON.parse(raw);
  } catch(e) {}
  // Notas padrão de boas-vindas
  return [
    { id: 1, text: "✨ Bem-vindo ao cantinho do Mochi!\n\n- Fazer carinho no gatinho 💕\n- Regar as plantinhas 🪴\n- Tomar um café quentinho ☕", color: '#FEF08A', rot: -2 },
    { id: 2, text: "🐾 Metas:\n- Cuidar da galinha 🐔\n- Estudar 2 pomodoros 🍅\n- Testar novos chapéus!", color: '#FBCFE8', rot: 1.5 },
    { id: 3, text: "💡 Lembrete:\nVocê pode girar a mesa com a tecla R e organizar tudo!", color: '#BAE6FD', rot: -1 }
  ];
}

function saveNotesToStorage(notes) {
  try {
    localStorage.setItem('purrmodoro_notes', JSON.stringify(notes));
  } catch(e) {}
}

function renderCorkboardNotes() {
  corkboardSurface.innerHTML = '';
  const notes = getSavedNotes();
  notes.forEach(note => {
    const card = document.createElement('div');
    card.className = 'postit-card';
    card.style.background = note.color || '#FEF08A';
    card.style.transform = `rotate(${note.rot || 0}deg)`;
    card.innerHTML = `
      <div class="postit-pin"></div>
      <div style="white-space: pre-wrap; flex:1; overflow:hidden;">${note.text || ''}</div>
    `;
    card.addEventListener('click', () => {
      openNoteEditor(note.id);
    });
    corkboardSurface.appendChild(card);
  });
}


// --- MODAL RETRÔ DA PORTA DA GELADEIRA (LISTA DE COMPRAS FUNCIONAL) ---
const fridgeModal = document.getElementById('fridgeModal');
const btnCloseFridge = document.getElementById('btnCloseFridge');
const shoppingListContainer = document.getElementById('shoppingListContainer');
const fridgeInput = document.getElementById('fridgeInput');
const btnFridgeAdd = document.getElementById('btnFridgeAdd');
const fridgeItemCount = document.getElementById('fridgeItemCount');

const DEFAULT_FRIDGE_ITEMS = [
  { text: "🐟 Sachê de Salmão pro Mochi", checked: false },
  { text: "🌽 Milho Dourado pra Popó", checked: true },
  { text: "🍎 Frutas frescas pra fruteira", checked: false },
  { text: "🥛 Leite integral cremoso", checked: false },
  { text: "☕ Grãos de café torrado", checked: true }
];

function getFridgeItems() {
  try {
    const raw = localStorage.getItem('purrmodoro_fridge_list');
    if (!raw) return DEFAULT_FRIDGE_ITEMS;
    return JSON.parse(raw);
  } catch (e) {
    return DEFAULT_FRIDGE_ITEMS;
  }
}

function saveFridgeItems(list) {
  try {
    localStorage.setItem('purrmodoro_fridge_list', JSON.stringify(list));
  } catch (e) {}
}

function playFridgeClickSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(650, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1150, ctx.currentTime + 0.05);
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.05);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.06);
  } catch (e) {}
}

function renderFridgeShoppingList() {
  if (!shoppingListContainer) return;
  const list = getFridgeItems();
  shoppingListContainer.innerHTML = '';

  const doneCount = list.filter(it => it.checked).length;
  if (fridgeItemCount) {
    fridgeItemCount.textContent = `${doneCount}/${list.length} comprados`;
  }

  list.forEach((it, idx) => {
    const li = document.createElement('li');
    li.className = 'shopping-item' + (it.checked ? ' checked' : '');

    const checkIcon = document.createElement('span');
    checkIcon.style.marginRight = '8px';
    checkIcon.style.fontSize = '14px';
    checkIcon.textContent = it.checked ? '✅' : '⚪';

    const textSpan = document.createElement('span');
    textSpan.style.flex = '1';
    textSpan.textContent = it.text;

    const delBtn = document.createElement('button');
    delBtn.className = 'del-btn';
    delBtn.textContent = '✕';
    delBtn.title = 'Remover item';
    delBtn.onclick = (e) => {
      e.stopPropagation();
      list.splice(idx, 1);
      saveFridgeItems(list);
      renderFridgeShoppingList();
    };

    li.appendChild(checkIcon);
    li.appendChild(textSpan);
    li.appendChild(delBtn);

    li.onclick = () => {
      playFridgeClickSound();
      it.checked = !it.checked;
      saveFridgeItems(list);
      renderFridgeShoppingList();
    };

    shoppingListContainer.appendChild(li);
  });
}

function openFridgeModal() {
  if (fridgeModal) {
    playFridgeClickSound();
    fridgeModal.classList.add('open');
    renderFridgeShoppingList();
    if (fridgeInput) setTimeout(() => fridgeInput.focus(), 80);
  }
}

function closeFridgeModal() {
  if (fridgeModal) fridgeModal.classList.remove('open');
}

if (btnCloseFridge) btnCloseFridge.addEventListener('click', closeFridgeModal);
if (fridgeModal) {
  fridgeModal.addEventListener('click', (e) => {
    if (e.target === fridgeModal) closeFridgeModal();
  });
}

function handleAddFridgeItem() {
  if (!fridgeInput) return;
  const val = fridgeInput.value.trim();
  if (!val) return;
  const list = getFridgeItems();
  list.push({ text: val, checked: false });
  saveFridgeItems(list);
  fridgeInput.value = '';
  playFridgeClickSound();
  renderFridgeShoppingList();
}

if (btnFridgeAdd) btnFridgeAdd.addEventListener('click', handleAddFridgeItem);
if (fridgeInput) {
  fridgeInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleAddFridgeItem();
  });
}

function openCorkboardModal() {
  playTackSound();
  renderCorkboardNotes();
  corkboardModal.classList.add('open');
}

function closeCorkboardModal() {
  corkboardModal.classList.remove('open');
}

btnCloseCorkboard.addEventListener('click', closeCorkboardModal);

// Abrir editor para novo post-it ou editar existente
function openNoteEditor(noteId) {
  playTackSound();
  currentEditingNoteId = noteId;
  if (noteId) {
    const notes = getSavedNotes();
    const note = notes.find(n => n.id === noteId);
    if (note) {
      noteTextarea.value = note.text;
      selectedNoteColor = note.color || '#FEF08A';
      btnDeleteNote.style.display = 'inline-flex';
    }
  } else {
    // Novo post-it: cor pastel aleatória
    selectedNoteColor = PASTEL_COLORS[Math.floor(Math.random() * PASTEL_COLORS.length)];
    noteTextarea.value = '';
    btnDeleteNote.style.display = 'none';
  }

  noteEditorCard.style.background = selectedNoteColor;
  colorDots.forEach(d => {
    d.classList.toggle('active', d.dataset.color === selectedNoteColor);
  });

  noteEditorModal.classList.add('open');
  setTimeout(() => noteTextarea.focus(), 100);
}

function closeNoteEditor() {
  noteEditorModal.classList.remove('open');
}

corkboardPadBtn.addEventListener('click', () => {
  openNoteEditor(null);
});

colorDots.forEach(dot => {
  dot.addEventListener('click', () => {
    selectedNoteColor = dot.dataset.color;
    colorDots.forEach(d => d.classList.remove('active'));
    dot.classList.add('active');
    noteEditorCard.style.background = selectedNoteColor;
  });
});

btnCancelNote.addEventListener('click', closeNoteEditor);

btnSaveNote.addEventListener('click', () => {
  const text = noteTextarea.value.trim();
  if (!text) {
    closeNoteEditor();
    return;
  }
  playTackSound();
  const notes = getSavedNotes();
  if (currentEditingNoteId) {
    const note = notes.find(n => n.id === currentEditingNoteId);
    if (note) {
      note.text = text;
      note.color = selectedNoteColor;
    }
  } else {
    notes.push({
      id: Date.now(),
      text: text,
      color: selectedNoteColor,
      rot: Math.round((Math.random() * 6 - 3) * 10) / 10
    });
  }
  saveNotesToStorage(notes);
  closeNoteEditor();
  renderCorkboardNotes();
});

btnDeleteNote.addEventListener('click', () => {
  if (currentEditingNoteId) {
    playTackSound();
    let notes = getSavedNotes();
    notes = notes.filter(n => n.id !== currentEditingNoteId);
    saveNotesToStorage(notes);
    closeNoteEditor();
    renderCorkboardNotes();
  }
});

