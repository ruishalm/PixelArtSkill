// Botão Modo Decoração
const btnDecorMode = document.getElementById('btnDecorMode');
const bannerInfo = document.getElementById('bannerInfo');
const btnRotateMob = document.getElementById('btnRotateMob');
const btnRotateSelected = document.getElementById('btnRotateSelected');

btnDecorMode.addEventListener('click', () => {
  isDecorMode = !isDecorMode;
  btnDecorMode.classList.toggle('active', isDecorMode);
  bannerInfo.style.display = isDecorMode ? 'flex' : 'none';
  canvas.classList.toggle('decor-mode', isDecorMode);
  if (!isDecorMode) {
    selectedItem = null;
    btnRotateMob.style.display = 'none';
  }
});

btnRotateMob.addEventListener('click', rotateSelectedItem);
btnRotateSelected.addEventListener('click', rotateSelectedItem);

const btnAutoSpin = document.getElementById('btnAutoSpin');
btnAutoSpin.addEventListener('click', () => {
  autoSpin = !autoSpin;
  btnAutoSpin.classList.toggle('active', autoSpin);
});

// Botão de Chapéu (Ciclo: Nenhum -> Bruxo -> Coroa -> Boina -> Sakura)
const hatKeys = ['none', 'witch', 'crown', 'beret', 'flower'];
const hatNames = {
  none: '🎩 Chapéu: Nenhum',
  witch: '🧙 Bruxo',
  crown: '👑 Coroa',
  beret: '🧑‍🎨 Boina',
  flower: '🌸 Sakura'
};
let currentHatIdx = 0;
let selectedHatPetId = 'cat';
const btnHat = document.getElementById('btnHat');
btnHat.addEventListener('click', () => {
  currentHatIdx = (currentHatIdx + 1) % hatKeys.length;
  const hatKey = hatKeys[currentHatIdx];
  const targetPet = items.find(it => it.id === selectedHatPetId) || items.find(it => it.id === 'cat');
  if (targetPet) {
    targetPet.hat = hatKey;
    if (targetPet.id === 'cat') playMeowSound();
    else playChickenSound();
  }
  btnHat.textContent = hatNames[hatKey];
  if (currentDrawerTab === 'hats') renderAssetList();
});

// Botão de Postura (Ciclo: Auto -> Andar -> Sentar -> Pãozinho -> Barriga)
const postures = [
  { key: 'auto', label: '🐾 Modo: Auto' },
  { key: 'walk', label: '🚶 Andando' },
  { key: 'sit', label: '🐱 Sentado' },
  { key: 'loaf', label: '🍞 Pãozinho' },
  { key: 'belly', label: '💖 Barriguinha' }
];
let currentPostureIdx = 0;
const btnPosture = document.getElementById('btnPosture');
btnPosture.addEventListener('click', () => {
  currentPostureIdx = (currentPostureIdx + 1) % postures.length;
  const p = postures[currentPostureIdx];
  const cat = items.find(it => it.id === 'cat');
  if (cat) {
    cat.forcedPosture = (p.key === 'auto') ? null : p.key;
    if (p.key !== 'auto') cat.posture = p.key;
  }
  btnPosture.textContent = p.label;
});

// Botão de Carinho
document.getElementById('btnPet').addEventListener('click', () => {
  const cat = items.find(it => it.id === 'cat');
  if (cat) triggerPetReactions(cat);
});

const squashSlider = document.getElementById('squashSlider');
squashSlider.addEventListener('input', (e) => {
  squash = parseFloat(e.target.value);
});

// Gerenciador do Catálogo de Assets
const btnCatalog = document.getElementById('btnCatalog');
const assetDrawer = document.getElementById('assetDrawer');
const btnCloseDrawer = document.getElementById('btnCloseDrawer');
const btnShowAll = document.getElementById('btnShowAll');
const btnHideAll = document.getElementById('btnHideAll');
const assetList = document.getElementById('assetList');

let currentDrawerTab = 'furniture';
const drawerActions = document.getElementById('drawerActions');

// Tab buttons wiring
document.querySelectorAll('.drawer-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.drawer-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentDrawerTab = tab.getAttribute('data-cat');
    renderAssetList();
  });
});

const hatOptions = [
  { key: 'none',   name: 'Sem Chapéu',           icon: '❌', desc: 'Gatinho ao natural' },
  { key: 'witch',  name: 'Chapéu de Bruxo',      icon: '🧙', desc: 'Cone místico roxo com fivela dourada' },
  { key: 'crown',  name: 'Coroa Real',           icon: '👑', desc: 'Ouro nobre com pedras de rubi' },
  { key: 'beret',  name: 'Boina Artista',        icon: '🧑‍🎨', desc: 'Lã carmesim estilosa de pintor' },
  { key: 'flower', name: 'Flor de Sakura',       icon: '🌸', desc: 'Pétalas rosadas japonesas' },
];

function renderAssetList() {
  assetList.innerHTML = '';
  const cat = items.find(it => it.id === 'cat');

  if (currentDrawerTab === 'hats') {
    drawerActions.style.display = 'none';

    // 1. SELETOR DE PET PARA VESTIR CHAPÉU (Mochi, Popó, Pintinho)
    const petSelectorRow = document.createElement('div');
    petSelectorRow.style.cssText = 'display:flex; gap:6px; margin-bottom:12px; background:#F5EDE2; padding:4px; border-radius:10px;';

    const petChoices = [
      { id: 'cat', name: '🐱 Mochi' },
      { id: 'chicken', name: '🐔 Popó' },
      { id: 'chick', name: '🐥 Pintinho' }
    ];

    petChoices.forEach(pc => {
      const btnP = document.createElement('button');
      btnP.textContent = pc.name;
      const isAct = (selectedHatPetId === pc.id);
      btnP.style.cssText = `flex:1; border:none; padding:6px 4px; border-radius:8px; font-size:11px; font-weight:700; cursor:pointer; background:${isAct ? '#D87D4A' : 'transparent'}; color:${isAct ? '#FFF' : '#6E472D'}; transition:0.2s;`;
      btnP.addEventListener('click', () => {
        selectedHatPetId = pc.id;
        renderAssetList();
      });
      petSelectorRow.appendChild(btnP);
    });
    assetList.appendChild(petSelectorRow);

    const currentTargetPet = items.find(it => it.id === selectedHatPetId);

    hatOptions.forEach(h => {
      const card = document.createElement('div');
      card.className = 'asset-card';
      const isEquipped = (currentTargetPet && (currentTargetPet.hat || 'none') === h.key);
      const hatDesc = selectedHatPetId === 'chick' && h.key !== 'none' 
        ? `${h.desc} (Pintinho fica escondido dentro!)`
        : (selectedHatPetId === 'chicken' && h.key !== 'none' ? `${h.desc} (Inclinado charmoso na crista)` : h.desc);

      card.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:2px;">
          <span class="asset-name">${h.icon} ${h.name}</span>
          <span style="font-size:10px; color:#8C6A54;">${hatDesc}</span>
        </div>
        <button class="btn-toggle ${isEquipped ? 'on' : 'off'}">
          ${isEquipped ? '✓ Equipado' : 'Equipar'}
        </button>
      `;
      card.querySelector('.btn-toggle').addEventListener('click', () => {
        if (currentTargetPet) {
          currentTargetPet.hat = h.key;
          if (selectedHatPetId === 'cat') {
            currentHatIdx = hatKeys.indexOf(h.key);
            btnHat.textContent = hatNames[h.key];
            playMeowSound();
          } else {
            playChickenSound();
          }
          renderAssetList();
        }
      });
      assetList.appendChild(card);
    });

  } else if (currentDrawerTab === 'pets') {
    drawerActions.style.display = 'none';

    // 1. PRESENÇA DOS BICHINHOS NO QUARTO (Pode ter Gato, Popó e Pintinho juntos ou tirar quem quiser!)
    const hPetsPresence = document.createElement('div');
    hPetsPresence.style.cssText = 'font-size:12px; font-weight:800; color:#532F16; margin:6px 0 6px;';
    hPetsPresence.textContent = '🐾 Companheiros no Quarto (Ative até 3 bichinhos):';
    assetList.appendChild(hPetsPresence);

    const petItems = items.filter(it => it.id === 'cat' || it.id === 'chicken' || it.id === 'chick');
    petItems.forEach(pet => {
      const card = document.createElement('div');
      card.className = 'asset-card';
      const isVis = pet.visible !== false;
      card.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:2px;">
          <span class="asset-name">${pet.icon || '🐾'} ${pet.name}</span>
          <span style="font-size:10px; color:#8C6A54;">${pet.id === 'cat' ? 'Gatinho companheiro de estudos' : (pet.id === 'chicken' ? 'Galinha que cisca e passeia rebolando' : 'Filhotinho fofo da Popó')}</span>
        </div>
        <button class="btn-toggle ${isVis ? 'on' : 'off'}">
          ${isVis ? '✓ No Quarto' : '+ Chamar'}
        </button>
      `;
      card.querySelector('.btn-toggle').addEventListener('click', () => {
        pet.visible = !isVis;
        if (pet.id === 'cat') playMeowSound();
        else playChickenSound();
        renderAssetList();
      });
      assetList.appendChild(card);
    });

    // 2. PELAGENS DO GATINHO MOCHI
    const hCatSkins = document.createElement('div');
    hCatSkins.style.cssText = 'font-size:12px; font-weight:800; color:#532F16; margin:16px 0 6px;';
    hCatSkins.textContent = '🎨 Escolha a Pelagem do Gatinho:';
    assetList.appendChild(hCatSkins);

    for (const [key, skin] of Object.entries(CAT_SKINS)) {
      const card = document.createElement('div');
      card.className = 'asset-card';
      const isSelected = (currentCatSkin === key);
      card.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:2px;">
          <span class="asset-name">${skin.icon} ${skin.name}</span>
          <span style="font-size:10px; color:#8C6A54;">${skin.desc}</span>
        </div>
        <button class="btn-toggle ${isSelected ? 'on' : 'off'}">
          ${isSelected ? '✓ Ativo' : 'Escolher'}
        </button>
      `;
      card.querySelector('.btn-toggle').addEventListener('click', () => {
        currentCatSkin = key;
        const cat = items.find(it => it.id === 'cat');
        if (cat) cat.visible = true; // Ativa o gatinho se escolher uma pelagem
        playMeowSound();
        renderAssetList();
      });
      assetList.appendChild(card);
    }

  } else {
    drawerActions.style.display = 'flex';
    const filtered = items.filter(it => it.category === currentDrawerTab && !it.isCat && !it.isChicken);

    filtered.forEach(item => {
      const card = document.createElement('div');
      card.className = 'asset-card';
      const isVis = item.visible !== false;
      card.innerHTML = `
        <span class="asset-name">${item.icon || '📦'} ${item.name}</span>
        <div style="display:flex; gap:6px; align-items:center;">
          <button class="btn-focus" title="Focar e Selecionar" style="border:none; background:#EDE4D6; color:#3B2A20; border-radius:8px; padding:3px 7px; font-size:12px; cursor:pointer; font-weight:600;">🎯</button>
          <button class="btn-toggle ${isVis ? 'on' : 'off'}">
            ${isVis ? '✓ Ativo' : '+ Adicionar'}
          </button>
        </div>
      `;
      card.querySelector('.btn-focus').addEventListener('click', () => {
        item.visible = true;
        if (!isDecorMode) {
          isDecorMode = true;
          btnDecorMode.classList.add('active');
          bannerInfo.style.display = 'flex';
          canvas.classList.add('decor-mode');
        }
        selectedItem = item;
        btnRotateMob.style.display = item.isWallItem ? 'none' : 'inline-flex';
        bannerInfo.innerHTML = `<span>🎯 <b>Item Focado:</b> ${item.icon || ''} ${item.name} selecionado!</span>`;
        renderAssetList();
      });
      card.querySelector('.btn-toggle').addEventListener('click', () => {
        item.visible = !isVis;
        renderAssetList();
      });
      assetList.appendChild(card);
    });
  }
}

    // --- EVENTOS DO MODAL DA PLANTA BAIXA ---
const btnHousePlan = document.getElementById('btnHousePlan');
const housePlanModal = document.getElementById('housePlanModal');
const btnCloseHousePlan = document.getElementById('btnCloseHousePlan');
const roomCardBedroom = document.getElementById('roomCardBedroom');
const roomCardLiving = document.getElementById('roomCardLiving');
const roomCardKitchen = document.getElementById('roomCardKitchen');
const roomCardGarden = document.getElementById('roomCardGarden');

if (btnHousePlan && housePlanModal) {
  btnHousePlan.addEventListener('click', () => {
    housePlanModal.classList.add('open');
    updateHousePlanBadges();
  });
  btnCloseHousePlan.addEventListener('click', () => {
    housePlanModal.classList.remove('open');
  });
  housePlanModal.addEventListener('click', (e) => {
    if (e.target === housePlanModal) housePlanModal.classList.remove('open');
  });

  roomCardBedroom.addEventListener('click', () => {
    housePlanModal.classList.remove('open');
    if (currentRoomId !== 'bedroom') {
      const doorToBed = items.find(it => it.targetRoom === 'bedroom');
      if (doorToBed) migratePetsToDoor(doorToBed, () => switchRoom('bedroom'));
      else switchRoom('bedroom');
    }
  });

  roomCardLiving.addEventListener('click', () => {
    housePlanModal.classList.remove('open');
    if (currentRoomId !== 'living') {
      const doorToLiv = items.find(it => it.targetRoom === 'living');
      if (doorToLiv) migratePetsToDoor(doorToLiv, () => switchRoom('living'));
      else switchRoom('living');
    }
  });

  roomCardKitchen.addEventListener('click', () => {
    housePlanModal.classList.remove('open');
    if (currentRoomId !== 'kitchen') {
      const doorToK = items.find(it => it.targetRoom === 'kitchen');
      if (doorToK) migratePetsToDoor(doorToK, () => switchRoom('kitchen'));
      else switchRoom('kitchen');
    }
  });

  roomCardGarden.addEventListener('click', () => {
    housePlanModal.classList.remove('open');
    if (currentRoomId !== 'garden') {
      const doorToG = items.find(it => it.targetRoom === 'garden');
      if (doorToG) migratePetsToDoor(doorToG, () => switchRoom('garden'));
      else switchRoom('garden');
    }
  });
}

btnCatalog.addEventListener('click', () => {
  const isVisible = assetDrawer.style.display !== 'none';
  assetDrawer.style.display = isVisible ? 'none' : 'flex';
  btnCatalog.classList.toggle('active', !isVisible);
  if (!isVisible) renderAssetList();
});

btnCloseDrawer.addEventListener('click', () => {
  assetDrawer.style.display = 'none';
  btnCatalog.classList.remove('active');
});

btnShowAll.addEventListener('click', () => {
  items.forEach(it => it.visible = true);
  renderAssetList();
});

btnHideAll.addEventListener('click', () => {
  items.forEach(it => it.visible = false);
  renderAssetList();
});

renderAssetList();

render();
