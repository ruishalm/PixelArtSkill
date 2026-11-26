const canvas = document.getElementById('viewport');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

// Buffer de baixa resolução amplo
const LOW_W = 440;
const LOW_H = 440;
const lowCanvas = document.createElement('canvas');
lowCanvas.width = LOW_W;
lowCanvas.height = LOW_H;
const lowCtx = lowCanvas.getContext('2d');
lowCtx.imageSmoothingEnabled = false;

// Dimensões do quarto gigante (dobrado: raio 140 = 280x280 de chão útil)
const ROOM_R = 140;
const WALL_H = 100;

// Estado da câmera
let turn = -Math.PI * 0.25;
let targetTurn = -Math.PI * 0.25;
let squash = 0.72;
let autoSpin = false;
let hearts = [];

// Estado de Decoração / Drag & Drop
let isDecorMode = false;
let selectedItem = null;
let hoveredItem = null;
let isDraggingItem = false;
let dragStartPos = { sx: 0, sy: 0 };
let itemStartPos = { x: 0, y: 0, liftZ: 0 };
let dragOffset = { x: 0, y: 0 };

// Nuvem animada na janela
let cloudAnimX = 0;

// Paleta de Cores PurrModoro
const P = {
  bg: '#F8F3EB',
  woodLight: '#E8C596',
  woodMid: '#D4A373',
  woodDark: '#B88252',
  plankLine: '#A57347',
  baseboard: '#7A4926',
  wallInner: '#F5ECE1',
  wallTrim: '#C8B7A1',
  windowFrame: '#FFFFFF',
  windowCurtain: '#E8A598',
  windowSky: '#A2CBE8',
  shelfWood: '#9E6740',
  outline: '#3B2219'
};

const _rvd = window.__ROOM_VOXEL_DATA__ || {};
let audioCtx = null;

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

// 1. GATINHO 3D ARTICULADO (Corpo 16 slices + 4 Patinhas 4x4 com almofadinhas)
// 6 PELAGENS DO GATINHO (Skins Personalizadas)
const CAT_SKINS = {
  calico: {
    id: 'calico', name: 'Mochi (Calico Original)', icon: '🐱', desc: 'Pelagem tricolor clássica (laranja, branco e preto)',
    pal: ['rgba(0,0,0,0)', '#FDFBF7', '#DE864A', '#3B2219', '#F2A2AB', '#FFFFFF', '#B85820', '#E5E0D8']
  },
  black: {
    id: 'black', name: 'Kuro (Gato Preto)', icon: '🐈‍⬛', desc: 'Preto ônix brilhante com olhos dourados brilhantes',
    pal: ['rgba(0,0,0,0)', '#1E293B', '#334155', '#F59E0B', '#F472B6', '#FEF08A', '#0F172A', '#1E293B']
  },
  tuxedo: {
    id: 'tuxedo', name: 'Felix (Frajola)', icon: '🎩', desc: 'Preto e branco estilo smoking elegante com botinhas brancas',
    pal: ['rgba(0,0,0,0)', '#FFFFFF', '#1E293B', '#1E293B', '#F472B6', '#FFFFFF', '#0F172A', '#CBD5E1']
  },
  orange: {
    id: 'orange', name: 'Cheddar (Tabby Laranja)', icon: '🍊', desc: 'Gatinho ruivo tigrado e muito esfomeado',
    pal: ['rgba(0,0,0,0)', '#FED7AA', '#EA580C', '#3B2219', '#F472B6', '#FFFFFF', '#C2410C', '#FDBA74']
  },
  siamese: {
    id: 'siamese', name: 'Luna (Siamês)', icon: '☕', desc: 'Corpo creme com pontas de chocolate e olhos azuis safira',
    pal: ['rgba(0,0,0,0)', '#FAF5EE', '#5C4033', '#0EA5E9', '#F472B6', '#FFFFFF', '#3E2723', '#EADBCA']
  },
  gray: {
    id: 'gray', name: 'Misty (Cinza Chumbo)', icon: '☁️', desc: 'Pelagem cinza prateada aveludada com olhos dourados',
    pal: ['rgba(0,0,0,0)', '#94A3B8', '#64748B', '#F59E0B', '#F472B6', '#FFFFFF', '#475569', '#CBD5E1']
  }
};

let currentCatSkin = 'calico';
const catSkinModels = {};
for (const [key, skin] of Object.entries(CAT_SKINS)) {
  catSkinModels[key] = {
    body: createSliceSheet(_rvd.CAT_BODY_SLICES, skin.pal, 32, 32),
    paw: createSliceSheet(_rvd.CAT_PAW_SLICES, skin.pal, 4, 4),
    belly: createSliceSheet(_rvd.CAT_BELLY_SLICES, skin.pal, 32, 32)
  };
}

const catPal = CAT_SKINS.calico.pal;
const catBodyModel = catSkinModels.calico.body;
const catPawModel = catSkinModels.calico.paw;
const catBellyModel = catSkinModels.calico.belly;

// CHAPÉUZINHOS PURRMODORO
const HATS = {
  witch: createSliceSheet(_rvd.WITCH_HAT_SLICES, ['rgba(0,0,0,0)', '#221533', '#E5A93C', '#38244F'], 16, 16),
  crown: createSliceSheet(_rvd.CROWN_HAT_SLICES, ['rgba(0,0,0,0)', '#F4B846', '#FFD166', '#E63946'], 12, 12),
  beret: createSliceSheet(_rvd.BERET_HAT_SLICES, ['rgba(0,0,0,0)', '#5E1428', '#B82D52', '#3D0C1A'], 14, 14),
  flower: createSliceSheet(_rvd.FLOWER_HAT_SLICES, ['rgba(0,0,0,0)', '#FFB7C5', '#FFD166'], 10, 10),
};

// 2. MESA DE ESTUDO AMPLIADA (15 slices, 80x36)
const deskPal = [
  'rgba(0,0,0,0)',
  '#633A18', // 1: perna madeira escura
  '#9E6740', // 2: tampo carvalho maciço
  '#B87E52'  // 3: chanfro de borda
];
const deskModel = createSliceSheet(_rvd.DESK_SLICES, deskPal, 80, 36);

// 3. NOTEBOOK NO SUPORTE ERGONÔMICO (17 slices, 24x20)
const laptopPal = [
  'rgba(0,0,0,0)',
  '#94A3B8', // 1: suporte metálico prata & logo traseiro
  '#1E293B', // 2: chassi laptop grafite (tampa e base)
  '#0F172A', // 3: bezel moldura preta e teclado
  '#475569', // 4: trackpad e barra de título
  '#181825', // 5: fundo escuro da IDE (Catppuccin / VS Code)
  '#38BDF8', // 6: sintaxe ciano brilhante
  '#F59E0B', // 7: sintaxe âmbar / amarelo dourado
  '#F43F5E', // 8: sintaxe rosa coral / botão fechar
  '#10B981'  // 9: sintaxe verde esmeralda / comentários
];
const laptopModel = createSliceSheet(_rvd.LAPTOP_SLICES, laptopPal, 24, 20);

// 4. MESA DIGITALIZADORA COM CANETA STYLUS E SKETCH (4 slices, 22x16)
const tabletPal = [
  'rgba(0,0,0,0)',
  '#1E293B', // 1: carcaça fina grafite
  '#FAF7F2', // 2: canvas tela branca
  '#DE864A', // 3: rascunho de gatinho na tela
  '#475569', // 4: caneta stylus
  '#38BDF8', // 5: ponta da caneta
  '#0F172A'  // 6: express keys e suporte donut da caneta
];
const tabletModel = createSliceSheet(_rvd.TABLET_SLICES, tabletPal, 22, 16);

// 5. LIVRINHOS EMPILHADOS DA MESA (7 slices, 16x16)
const deskBooksPal = [
  'rgba(0,0,0,0)',
  '#831843', // 1: livro inferior vinho
  '#FAF7F2', // 2: páginas
  '#0F766E', // 3: livro médio turquesa
  '#D97706', // 4: livro superior dourado
  '#2563EB'  // 5: fita azul marcadora
];
const deskBooksModel = createSliceSheet(_rvd.DESK_BOOKS_SLICES, deskBooksPal, 16, 16);

// 6. CANECA DE CAFÉ COM VAPOR (8 slices, 10x10)
const mugPal = [
  'rgba(0,0,0,0)',
  '#FAF7F2', // 1: cerâmica branca
  '#E2E8F0', // 2: sombra cerâmica
  '#4A2A18', // 3: café expresso
  '#CBD5E1'  // 4: vapor
];
const mugModel = createSliceSheet(_rvd.MUG_SLICES, mugPal, 10, 10);

// 7. VASO DE PLANTA MONSTERA (16 slices)
const plantPal = ['rgba(0,0,0,0)', '#C26A45', '#4A2E1B', '#2D5A27', '#4D8A48'];
const plantModel = createSliceSheet(_rvd.PLANT_SLICES, plantPal, 20, 20);

// 8. CAMINHA NUVEM AZUL (8 slices)
const bedPal = ['rgba(0,0,0,0)', '#385D78', '#4D7594', '#E4EFF5'];
const bedModel = createSliceSheet(_rvd.BED_SLICES, bedPal, 32, 32);

// 9. TORRE DE GATO COM SISAL E CESTINHA (28 slices)
const treePal = ['rgba(0,0,0,0)', '#7E6047', '#D9C3A3', '#C29175'];
const treeModel = createSliceSheet(_rvd.TREE_SLICES, treePal, 28, 28);

// MÓVEIS DA SALA DE ESTAR (SPRITE STACKING SLICES)
const sofaPal = ['rgba(0,0,0,0)', '#4A2E1B', '#B45339', '#C8654B', '#DC7A5F', '#F3EDE2'];
const sofaModel = createSliceSheet(_rvd.SOFA_SLICES, sofaPal, 56, 30);

const coffeeTablePal = ['rgba(0,0,0,0)', '#532F16', '#9E6740', '#B87E52', '#2D6A4F', '#52B788', '#FDFBF7'];
const coffeeTableModel = createSliceSheet(_rvd.COFFEE_TABLE_SLICES, coffeeTablePal, 36, 24);

const tvRackPal = ['rgba(0,0,0,0)', '#4A2E1B', '#8B5A2B', '#DDD0BF', '#181825', '#38BDF8', '#DE864A', '#E76F51'];
const tvRackModel = createSliceSheet(_rvd.TV_RACK_SLICES, tvRackPal, 52, 22);

const bookshelfPal = ['rgba(0,0,0,0)', '#381F12', '#5C361E', '#442615', '#7A4B2B', '#8C552A', '#B2723A', '#C88548'];
const bookshelfModel = createSliceSheet(_rvd.BOOKSHELF_SLICES, bookshelfPal, 46, 16);

const bsEncPal = ['rgba(0,0,0,0)', '#9B1C1C', '#1E3A8A', '#065F46', '#B45309', '#F59E0B', '#FEF3C7'];
const bsEncModel = createSliceSheet(_rvd.BS_ENC_SLICES, bsEncPal, 14, 10);

const bsPlantPal = ['rgba(0,0,0,0)', '#9A3412', '#EA580C', '#27170E', '#14532D', '#16A34A', '#4ADE80'];
const bsPlantModel = createSliceSheet(_rvd.BS_PLANT_SLICES, bsPlantPal, 14, 12);

const bsCrystalPal = ['rgba(0,0,0,0)', '#334155', '#475569', '#581C87', '#9333EA', '#C084FC', '#FFFFFF'];
const bsCrystalModel = createSliceSheet(_rvd.BS_CRYSTAL_SLICES, bsCrystalPal, 12, 10);

const bsStackPal = ['rgba(0,0,0,0)', '#0F766E', '#881337', '#D97706', '#FFFBEB', '#EF4444'];
const bsStackModel = createSliceSheet(_rvd.BS_STACK_SLICES, bsStackPal, 14, 10);

const bsTrophyPal = ['rgba(0,0,0,0)', '#3B1D11', '#FDE047', '#B45309', '#FACC15', '#FEF08A', '#EAB308'];
const bsTrophyModel = createSliceSheet(_rvd.BS_TROPHY_SLICES, bsTrophyPal, 12, 10);

// 11. MODELOS DA COZINHA (Bancada, Geladeira, Aparador, Mesa, Cadeiras, Fruteira)
const counterPal = ['rgba(0,0,0,0)', '#E2D9CC', '#B5A998', '#F8FAFC', '#94A3B8', '#CBD5E1', '#1E293B', '#F97316', '#0F172A', '#B45309'];
const counterModel = createSliceSheet(_rvd.COUNTER_SLICES, counterPal, 140, 22);

const retroFridgePal = ['rgba(0,0,0,0)', '#064E3B', '#6EE7B7', '#A7F3D0', '#059669', '#CBD5E1', '#FDE047', '#EF4444', '#38BDF8'];
const retroFridgeModel = createSliceSheet(_rvd.FRIDGE_SLICES, retroFridgePal, 26, 22);

const sideboardPal = ['rgba(0,0,0,0)', '#4A2E1B', '#8B5A2B', '#A26C38', '#DC2626', '#991B1B', '#F8FAFC'];
const sideboardModel = createSliceSheet(_rvd.SIDEBOARD_SLICES, sideboardPal, 32, 16);

const diningTablePal = ['rgba(0,0,0,0)', '#45220E', '#8C552A', '#B2723A', '#FFFBEB', '#FDE68A'];
const diningTableModel = createSliceSheet(_rvd.DINING_TABLE_SLICES, diningTablePal, 48, 48);

const diningChairPal = ['rgba(0,0,0,0)', '#45220E', '#8C552A', '#B2723A', '#FCA5A5'];
const diningChairModel = createSliceSheet(_rvd.DINING_CHAIR_SLICES, diningChairPal, 14, 14);

const fruitBowlPal = ['rgba(0,0,0,0)', '#F1F5F9', '#CBD5E1', '#EF4444', '#FACC15', '#F97316', '#15803D'];
const fruitBowlModel = createSliceSheet(_rvd.FRUIT_BOWL_SLICES, fruitBowlPal, 14, 14);

// 12. MODELOS DO JARDIM (Carvalho Centenário Dobrado, Pneu em Pé Vertical com 1 Corda, Cadeira de Varanda, Carrinho de Flores, Canteiro)
const gardenTreePal = ['rgba(0,0,0,0)', '#2C1810', '#4E2A17', '#784323', '#14532D', '#16A34A', '#4ADE80', '#F43F5E'];
const gardenTreeModel = createSliceSheet(_rvd.GARDEN_TREE_SLICES, gardenTreePal, 72, 64);

const tireSwingPal = ['rgba(0,0,0,0)', '#0F172A', '#334155', '#475569', '#B45309', '#F59E0B'];
const tireSwingModel = createSliceSheet(_rvd.TIRE_SWING_SLICES, tireSwingPal, 18, 20);

const porchChairPal = ['rgba(0,0,0,0)', '#45220E', '#8C552A', '#B2723A', '#FEF3C7'];
const porchChairModel = createSliceSheet(_rvd.PORCH_CHAIR_SLICES, porchChairPal, 18, 20);

const wheelbarrowPal = ['rgba(0,0,0,0)', '#334155', '#78350F', '#B45309', '#27170E', '#EF4444', '#FACC15', '#A855F7', '#22C55E'];
const wheelbarrowModel = createSliceSheet(_rvd.WHEELBARROW_SLICES, wheelbarrowPal, 28, 16);

const flowerBedPal = ['rgba(0,0,0,0)', '#9A3412', '#C2410C', '#27170E', '#EF4444', '#FFFFFF', '#A855F7', '#16A34A'];
const flowerBedModel = createSliceSheet(_rvd.FLOWER_BED_SLICES, flowerBedPal, 36, 14);


// 10. GALINHA COCORICÓ 3D (16 slices)
const ROOM_CHICKEN_SLICES = _rvd.CHICKEN_SLICES;
const chickenPal = ['rgba(0,0,0,0)', '#FFFFFF', '#F1F5F9', '#CBD5E1', '#EF4444', '#B91C1C', '#F59E0B', '#D97706', '#0F172A', '#FFFFFF'];
const chickenModel = createSliceSheet(ROOM_CHICKEN_SLICES, chickenPal, 24, 24);
// CANVASES SEPARADOS DA GALINHA POPÓ (Patas, Corpo e Cabeça Articulados)
// MODELO DA GALINHA POPÓ E DO PINTINHO PIU (Bolinha Amarela Sem Crista)
function createPartCanvas(sliceGrid, filterFn, pal, size = 24) {
  const sc = document.createElement('canvas');
  sc.width = size; sc.height = size;
  const sctx = sc.getContext('2d');
  sctx.imageSmoothingEnabled = false;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const cIdx = sliceGrid[y] ? (sliceGrid[y][x] || 0) : 0;
      if (cIdx > 0) {
        if (filterFn && !filterFn(x, y)) continue;
        sctx.fillStyle = pal[cIdx] || '#FFFFFF';
        sctx.fillRect(x, y, 1, 1);
      }
    }
  }
  return sc;
}

// Paleta Amarela para o Pintinho Piu (Pintinho Amarelinho)
const chickPal = ['rgba(0,0,0,0)', '#FEF08A', '#FACC15', '#EAB308', '#CA8A04', '#FB923C', '#EA580C', '#0F172A', '#FFFFFF', '#F472B6'];
const ROOM_CHICK_SLICES = _rvd.CHICK_SLICES;

const chickenLegL = [];
const chickenLegR = [];
for (let i = 0; i <= 3; i++) {
  chickenLegL.push(createPartCanvas(ROOM_CHICKEN_SLICES[i], (x, y) => y < 12, chickenPal, 24));
  chickenLegR.push(createPartCanvas(ROOM_CHICKEN_SLICES[i], (x, y) => y >= 12, chickenPal, 24));
}
const chickenUpper = [];
for (let i = 4; i < ROOM_CHICKEN_SLICES.length; i++) {
  chickenUpper.push(createPartCanvas(ROOM_CHICKEN_SLICES[i], null, chickenPal, 24));
}

// Partes dedicadas do Pintinho Piu: 18x18, sem crista, pura fofura redonda
const chickLegL = [];
const chickLegR = [];
for (let i = 0; i <= 1; i++) {
  chickLegL.push(createPartCanvas(ROOM_CHICK_SLICES[i], (x, y) => y < 9, chickPal, 18));
  chickLegR.push(createPartCanvas(ROOM_CHICK_SLICES[i], (x, y) => y >= 9, chickPal, 18));
}
const chickUpper = [];
for (let i = 2; i < ROOM_CHICK_SLICES.length; i++) {
  chickUpper.push(createPartCanvas(ROOM_CHICK_SLICES[i], null, chickPal, 18));
}


// --- DEFINIÇÕES DOS CÔMODOS & ENTIDADES PERSISTENTES ---
let currentRoomId = 'bedroom';

// 1. Pets Persistentes (Mochi, Popó e Pintinho que migram juntos!)
const PETS = [
  { id: 'cat',           name: 'Gatinho Mochi',        icon: '🐱', category: 'decor',     model: catBodyModel,   x: 0,   y: 0,   liftZ: 0,  selfAngle: 0,   scale: 1.5,  radius: 20, isCat: true, visible: true, state: 'idle', stateTimer: 180, isWalking: false, walkCycle: 0, idleTimer: 0, hat: 'none', posture: 'sit', forcedPosture: null, speech: null, bellyTimer: 0 },
  { id: 'chicken',       name: 'Galinha Popó',         icon: '🐔', category: 'pets',      model: chickenModel,   x: -35, y: 35,  liftZ: 0,  selfAngle: 0.6, scale: 1.35, radius: 18, isChicken: true, visible: true, state: 'idle', stateTimer: 120, isWalking: false, walkCycle: 0, animTime: 0, targetX: -35, targetY: 35 },
  { id: 'chick',         name: 'Pintinho Piu',         icon: '🐥', category: 'pets',      model: chickenModel,   x: -20, y: 48,  liftZ: 0,  selfAngle: 0.2, scale: 0.85, radius: 12, isChicken: true, visible: true, state: 'idle', stateTimer: 80,  isWalking: false, walkCycle: 0, animTime: 0, targetX: -20, targetY: 48 }
];

// 2. Móveis do Quarto
const BEDROOM_ITEMS = [
  { id: 'laptop',        name: 'Note no Suporte',      icon: '💻', category: 'decor',     model: laptopModel,    x: 55,  y: -74, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 18, isProp: true, surface: 'desk', offX: 0, offY: -9, visible: true },
  { id: 'tablet',        name: 'Tablet de Desenho',    icon: '🎨', category: 'decor',     model: tabletModel,    x: 32,  y: -62, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 16, isProp: true, surface: 'desk', offX: -23, offY: 3, visible: true },
  { id: 'desk_books',    name: 'Livros Empilhados',    icon: '📚', category: 'decor',     model: deskBooksModel, x: 80,  y: -58, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 14, isProp: true, surface: 'desk', offX: 25, offY: 7, visible: true },
  { id: 'mug',           name: 'Caneca de Café',       icon: '☕', category: 'decor',     model: mugModel,       x: 78,  y: -74, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 10, isProp: true, surface: 'desk', offX: 23, offY: -9, visible: true },
  { id: 'shelf_books',   name: 'Livros em Pé',         icon: '📖', category: 'decor',     x: -ROOM_R + 9, y: -28, liftZ: 61.5, radius: 15, isProp: true, surface: 'shelf', offY: -18, visible: true },
  { id: 'shelf_plant',   name: 'Vasinho de Suculenta', icon: '🪴', category: 'decor',     x: -ROOM_R + 9, y: -10, liftZ: 61.5, radius: 14, isProp: true, surface: 'shelf', offY: 0,   visible: true },
  { id: 'shelf_crystal', name: 'Cristal de Quartzo',   icon: '💎', category: 'decor',     x: -ROOM_R + 9, y: 8,   liftZ: 61.5, radius: 14, isProp: true, surface: 'shelf', offY: 18,  visible: true },
  { id: 'clock',         name: 'Relógio de Parede',    icon: '⏰', category: 'decor',     isWallItem: true, wall: 'west', x: -ROOM_R, y: 0, liftZ: 85, radius: 16, visible: true },
  { id: 'corkboard',     name: 'Mural de Post-its',    icon: '📌', category: 'decor',     isWallItem: true, wall: 'east', x: ROOM_R, y: -10, liftZ: 65, radius: 36, visible: true, isCorkboard: true },
  { id: 'plant',         name: 'Planta Monstera',      icon: '🌿', category: 'decor',     model: plantModel,     x: 85,  y: 65,  liftZ: 0,  selfAngle: 0.4, scale: 1.4,  radius: 20, visible: true },
  { id: 'door',          name: 'Porta para a Sala',    icon: '🚪', category: 'furniture', isWallItem: true, isDoor: true, wall: 'east', x: ROOM_R, y: 60, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'living' },
  { id: 'desk',          name: 'Mesa de Estudo',       icon: '🪵', category: 'furniture', model: deskModel,      x: 55,  y: -65, liftZ: 0,  selfAngle: 0,   scale: 1.45, radius: 46, isDesk: true, visible: true },
  { id: 'shelf',         name: 'Prateleira de Madeira',icon: '🪵', category: 'furniture', isWallItem: true, wall: 'west', x: -ROOM_R, y: -10, liftZ: 58, length: 68, radius: 24, visible: true },
  { id: 'bed',           name: 'Caminha Nuvem',        icon: '☁️', category: 'furniture', model: bedModel,       x: -75, y: -70, liftZ: 0,  selfAngle: 0,   scale: 1.4,  radius: 25, visible: true },
  { id: 'tree',          name: 'Torre de Gato',        icon: '🐾', category: 'furniture', model: treeModel,      x: -80, y: 50,  liftZ: 0,  selfAngle: 0,   scale: 1.4,  radius: 24, visible: true }
];

// 3. Móveis da Sala de Estar Central (Hub com 3 portas, Sofá, Mesinha, Rack com TV Retrô, Estante)
const LIVING_ITEMS = [
  // 3 Portas da Sala em paredes 100% VISÍVEIS (Parede Norte e Parede Leste)!
  { id: 'door_kitchen',  name: 'Porta pra Cozinha',    icon: '🍽️', category: 'furniture', isWallItem: true, isDoor: true, wall: 'north', x: -80, y: -ROOM_R, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'kitchen' },
  { id: 'door_bedroom',  name: 'Porta pro Quarto',     icon: '🛏️', category: 'furniture', isWallItem: true, isDoor: true, wall: 'north', x: 75,  y: -ROOM_R, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'bedroom' },
  { id: 'door_garden',   name: 'Porta pro Jardim',     icon: '🌳', category: 'furniture', isWallItem: true, isDoor: true, wall: 'east',  x: ROOM_R, y: 55, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'garden' },

  // MÓVEIS NAS PAREDES VAZIAS:
  // Sofá encostado na Parede Vazia (Oeste) virado para dentro da sala
  { id: 'sofa',          name: 'Sofá Aconchegante',    icon: '🛋️', category: 'furniture', model: sofaModel,      x: -105,y: 0,   liftZ: 0,  selfAngle: -Math.PI / 2, scale: 1.45, radius: 42, isSofa: true, visible: true },
  // Estante Alta encostada na Parede Vazia (Sul) com 3 prateleiras limpas e topo amplo
  { id: 'bookshelf',     name: 'Estante Alta de Livros',icon: '📚', category: 'furniture', model: bookshelfModel, x: -20, y: 112, liftZ: 0,  selfAngle: Math.PI, scale: 1.45, radius: 36, isBookshelf: true, visible: true },

  // ACESSÓRIOS MODULARES E MÓVEIS DA ESTANTE (Arrastáveis para qualquer prateleira!)
  { id: 'bs_enc',        name: 'Coleção de Enciclopédias', icon: '📖', category: 'decor', model: bsEncModel,     x: -12, y: 112, liftZ: 3.5,  selfAngle: Math.PI, scale: 1.4, radius: 14, isProp: true, surface: 'bookshelf', tier: 1, offX: -8,  offY: 0, visible: true },
  { id: 'bs_stack',      name: 'Livros com Marcador',     icon: '📚', category: 'decor', model: bsStackModel,   x: -28, y: 112, liftZ: 3.5,  selfAngle: Math.PI, scale: 1.4, radius: 12, isProp: true, surface: 'bookshelf', tier: 1, offX: 8,   offY: 0, visible: true },
  { id: 'bs_plant',      name: 'Vasinho de Hera Pendente', icon: '🪴', category: 'decor', model: bsPlantModel,   x: -12, y: 112, liftZ: 16.5, selfAngle: Math.PI, scale: 1.4, radius: 12, isProp: true, surface: 'bookshelf', tier: 2, offX: -8,  offY: 0, visible: true },
  { id: 'bs_trophy',     name: 'Troféu PurrModoro Ouro',   icon: '🏆', category: 'decor', model: bsTrophyModel,  x: -28, y: 112, liftZ: 16.5, selfAngle: Math.PI, scale: 1.4, radius: 10, isProp: true, surface: 'bookshelf', tier: 2, offX: 8,   offY: 0, visible: true },
  { id: 'bs_crystal',    name: 'Geodo de Ametista',        icon: '💎', category: 'decor', model: bsCrystalModel,x: -20, y: 112, liftZ: 29.5, selfAngle: Math.PI, scale: 1.4, radius: 10, isProp: true, surface: 'bookshelf', tier: 3, offX: 0,   offY: 0, visible: true },
  // Planta Monstera no cantinho entre as duas paredes vazias
  { id: 'plant_living',  name: 'Planta Monstera',      icon: '🌿', category: 'decor',     model: plantModel,     x: -112,y: 105, liftZ: 0,  selfAngle: 0.8,          scale: 1.4,  radius: 20, visible: true },

  // MEIO DA SALA:
  // Mesinha de Centro na frente do sofá
  { id: 'coffee_table',  name: 'Mesinha de Centro',    icon: '🪵', category: 'furniture', model: coffeeTableModel,x: -50, y: 0,   liftZ: 0,  selfAngle: -Math.PI / 2, scale: 1.45, radius: 26, isCoffeeTable: true, visible: true },
  // TV Retrô na frente do tapete virada de frente para o sofá!
  { id: 'tv_rack',       name: 'Rack com TV Retrô',    icon: '📺', category: 'furniture', model: tvRackModel,    x: 8,   y: 0,   liftZ: 0,  selfAngle: Math.PI / 2,  scale: 1.45, radius: 36, isTvRack: true, visible: true }
];


// 4. Móveis da Cozinha (Bancada contínua de lado a lado na parede Norte, Geladeira retrô, Aparador, Mesa quadrada grande + 4 Cadeiras + Fruteira)
const KITCHEN_ITEMS = [
  // Porta de volta pra Sala na Parede Leste
  { id: 'door_living',   name: 'Porta pra Sala',       icon: '🛋️', category: 'furniture', isWallItem: true, isDoor: true, wall: 'east', x: ROOM_R, y: 55, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'living' },

  // BANCADA CONTÍNUA OCUPANDO TODA A PAREDE NORTE DE LADO A LADO! - FIXO
  { id: 'kitchen_counter', name: 'Bancada com Pia e Fogão', icon: '🍳', category: 'furniture', model: counterModel, x: 0, y: -ROOM_R + 15, liftZ: 0, selfAngle: 0, scale: 1.45, radius: 80, isFixed: true, visible: true },

  // GELADEIRA RETRÔ PASTEL NA PAREDE OESTE (Funcional com Lista de Compras!) - FIXO
  // Regra Canônica de Orientação: selfAngle = 0 deixa a porta e os ímãs virados para o jogador/centro da cozinha!
  { id: 'fridge_retro',    name: 'Geladeira Retrô Pastel', icon: '🧊', category: 'furniture', model: retroFridgeModel, x: -ROOM_R + 20, y: -20, liftZ: 0, selfAngle: 0, scale: 1.4, radius: 32, isFixed: true, isFridge: true, visible: true },

  // APARADOR DE LOUÇAS NA PAREDE OESTE - FIXO
  // Regra Canônica de Orientação: selfAngle = 0 deixa as gavetas e bules voltados para o jogador/centro da cozinha!
  { id: 'kitchen_sideboard', name: 'Aparador de Louças', icon: '🍽️', category: 'furniture', model: sideboardModel, x: -ROOM_R + 16, y: 48, liftZ: 0, selfAngle: 0, scale: 1.4, radius: 30, isFixed: true, visible: true },

  // MESA CENTRAL DE JANTAR QUADRADA BEM MAIOR (Modular e Móvel com Parenting nas 4 Cadeiras e Fruteira!)
  { id: 'dining_table',    name: 'Mesa de Jantar Quadrada', icon: '🪵', category: 'furniture', model: diningTableModel, x: -8, y: 22, liftZ: 0, selfAngle: 0, scale: 1.4, radius: 48, isMovable: true, visible: true },

  // 4 CADEIRAS DE JANTAR PARENTADAS À MESA (Nas 4 faces da mesa quadrada!)
  { id: 'dining_chair_1',  name: 'Cadeira Norte',        icon: '🪑', category: 'furniture', model: diningChairModel, x: -8, y: -20, liftZ: 0, selfAngle: 0, initialAngle: 0, scale: 1.4, radius: 14, surface: 'dining_table', offX: 0, offY: -42, isMovable: true, visible: true },
  { id: 'dining_chair_2',  name: 'Cadeira Sul',          icon: '🪑', category: 'furniture', model: diningChairModel, x: -8, y: 64, liftZ: 0, selfAngle: Math.PI, initialAngle: Math.PI, scale: 1.4, radius: 14, surface: 'dining_table', offX: 0, offY: 42, isMovable: true, visible: true },
  { id: 'dining_chair_3',  name: 'Cadeira Oeste',        icon: '🪑', category: 'furniture', model: diningChairModel, x: -50, y: 22, liftZ: 0, selfAngle: -Math.PI / 2, initialAngle: -Math.PI / 2, scale: 1.4, radius: 14, surface: 'dining_table', offX: -42, offY: 0, isMovable: true, visible: true },
  { id: 'dining_chair_4',  name: 'Cadeira Leste',        icon: '🪑', category: 'furniture', model: diningChairModel, x: 34, y: 22, liftZ: 0, selfAngle: Math.PI / 2, initialAngle: Math.PI / 2, scale: 1.4, radius: 14, surface: 'dining_table', offX: 42, offY: 0, isMovable: true, visible: true },

  // FRUTEIRA COM MAÇÃS, BANANAS E LARANJAS NO CENTRO DA MESA
  { id: 'fruit_bowl',      name: 'Fruteira de Mesa',     icon: '🍎', category: 'decor',     model: fruitBowlModel,   x: -8, y: 22, liftZ: 26, selfAngle: 0, initialAngle: 0, scale: 1.4, radius: 14, isProp: true, surface: 'dining_table', offX: 0, offY: 0, isMovable: true, visible: true }
];

// 5. Móveis do Jardim Externo (Fachada da casa na Parede Norte com Janela e Arbustos, Carvalho Centenário Gigante, Balanço em Pé)
const GARDEN_ITEMS = [
  // Porta de volta pra Sala na Parede Norte (Fachada da Casa)
  { id: 'door_living',     name: 'Porta pra Sala',       icon: '🛋️', category: 'furniture', isWallItem: true, isDoor: true, wall: 'north', x: -65, y: -ROOM_R, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'living' },

  // CADEIRA DE VARANDA ACONCHEGANTE NA PLATAFORMA - MÓVEL
  { id: 'porch_chair',     name: 'Cadeira de Varanda',   icon: '🪑', category: 'furniture', model: porchChairModel, x: -25, y: -ROOM_R + 25, liftZ: 0, selfAngle: Math.PI, scale: 1.45, radius: 22, isMovable: true, visible: true },

  // CARVALHO CENTENÁRIO COM TAMANHO DOBRADO (Tronco massivo em x=45, y=15, galho horizontal saindo para x=21) - FIXO
  { id: 'garden_tree',     name: 'Carvalho Centenário',  icon: '🌳', category: 'furniture', model: gardenTreeModel, x: 45, y: 15, liftZ: 0, selfAngle: 0, scale: 2.0, radius: 72, isFixed: true, visible: true },

  // BALANÇO DE PNEU EM PÉ COM UMA ÚNICA CORDA (Perfeitamente suspenso do galho horizontal da árvore!) - FIXO
  { id: 'tire_swing',      name: 'Balanço de Pneu em Pé',icon: '🛞', category: 'furniture', model: tireSwingModel, x: 21, y: 19, liftZ: 0, selfAngle: 0, scale: 1.4, radius: 20, isFixed: true, isSwing: true, visible: true },

  // CARRINHO DE MÃO RÚSTICO DE MADEIRA RECHEADO DE FLORES - MÓVEL
  { id: 'wheelbarrow_flowers', name: 'Carrinho de Mão Florido', icon: '🪵', category: 'furniture', model: wheelbarrowModel, x: -45, y: 40, liftZ: 0, selfAngle: -0.4, scale: 1.45, radius: 26, isMovable: true, visible: true },
];

const roomState = {
  bedroom: BEDROOM_ITEMS,
  living: LIVING_ITEMS,
  kitchen: KITCHEN_ITEMS,
  garden: GARDEN_ITEMS
};

let items = [ ...PETS, ...roomState[currentRoomId] ];

// Slots inteligentes no tampo da mesa (Snap-to-Slot estilo The Sims / Animal Crossing)
const DESK_SLOTS = [
  { id: 'left',   name: 'Tablet de Desenho', offX: -28, offY: 3 },
  { id: 'center', name: 'Note no Suporte',   offX: 0,   offY: -10 },
  { id: 'front',  name: 'Centro Frontal',    offX: 0,   offY: 6 },
  { id: 'cup',    name: 'Caneca de Café',    offX: 28,  offY: -10 },
  { id: 'books',  name: 'Livros da Mesa',    offX: 30,  offY: 6 }
];

