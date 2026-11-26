    // =========================================================================
    // 4. HEIGHTFIELD MICRO-VOXEL 1080×1080 & ESCULTURA ORGÂNICA "PULL-CHAIN"
    // =========================================================================
    const STARTUP_T0 = performance.now();
    const mw = WORLD_CFG.gridW;
    const mh = WORLD_CFG.gridH;
    const VOX = WORLD_CFG.vox;
    const HALF_GRID = mw / 2;
    const HALF_WORLD = HALF_GRID * VOX;
    const WORLD_MIN = -HALF_WORLD;
    const WORLD_MAX = HALF_WORLD;

    const Z_MIN = -6;
    const TERRAIN_Z_MAX = 66;
    const Z_GRASS_MAX = 70;

    const CAT_HEIGHT = 16;
    const AUTO_STEP_MAX = 5.5; // ~0.35H, sobe colinas orgânicas suavemente andando
    let GRAVITY = 1200;
    let JUMP_VEL = Math.sqrt(2 * GRAVITY * 35.0); // ~35u apex (vence 16u e 32u, bloqueia 48u)

    const BIOME_KEYS = ['vila', 'girassol', 'ruinas', 'praia', 'zen', 'rio', 'cogumelos', 'montanha'];
    const BIOME_NAMES = [
      'Vila da Clareira',
      'Campos de Girassol',
      'Ruínas Orgânicas',
      'Praia & Farol',
      'Jardim Zen & Torii',
      'Rio & Cachoeira',
      'Bosque Cogumelos',
      'Pico Sakura'
    ];
    // Materiais: 0: grass, 1: path, 2: sand, 3: stone, 4: water, 5: bridge, 6: peak, 7: lilypad, 8: shallow
    const MAT_GRASS = 0, MAT_PATH = 1, MAT_SAND = 2, MAT_STONE = 3,
          MAT_WATER = 4, MAT_BRIDGE = 5, MAT_PEAK = 6, MAT_LILYPAD = 7, MAT_SHALLOW = 8;
    function isWetMat(m) { return m === MAT_WATER || m === MAT_SHALLOW; }

    const hmap = new Int16Array(mw * mh);
    const biomeMap = new Uint8Array(mw * mh);
    const matMap = new Uint8Array(mw * mh);
    const cliffMask = new Uint8Array(mw * mh);
    const shadowMask = new Uint8Array(mw * mh); // 0..100 escurecimento de sombra estática
    const noGrassMask = new Uint8Array(mw * mh);
    const standableMap = new Uint8Array(mw * mh); // 1 = plataforma/solo pisável (>= ~3.7×3.7 micro-voxels de área), 0 = borda/degrau estreito de falésia
    const cliffTopMap = new Int16Array(mw * mh);  // Altura do topo da falésia vizinha (para bloqueio e HUD precisos)

    function worldToGrid(wx, wy) {
      return {
        mx: Math.floor(wx / VOX + HALF_GRID),
        my: Math.floor(wy / VOX + HALF_GRID)
      };
    }

    function gridToWorld(mx, my) {
      return {
        wx: (mx - HALF_GRID + 0.5) * VOX,
        wy: (my - HALF_GRID + 0.5) * VOX
      };
    }

    // 4.1. Construção dos 8 Biomas no Heightfield Contínuo 1080×1080
    const _rSwing = (base, amp) => (
      WORLD_SEED === DEFAULT_WORLD_SEED
        ? base
        : Math.round(base + (worldRand() - 0.5) * 2 * amp)
    );
    const RIVER_WAYPOINTS = [
      [_rSwing(120, 220), -1078],
      [_rSwing(156, 210), -795],
      [144, -495],
      [148, -345],
      [_rSwing(102, 210), -165],
      [134, 108],
      [_rSwing(144, 230), 435],
      [120, 665],
      [_rSwing(120, 140), 820]
    ];
    const RIVER_SEGMENTS = [];
    for (let i = 0; i < RIVER_WAYPOINTS.length - 1; i++) {
      const [ax, ay] = RIVER_WAYPOINTS[i];
      const [bx, by] = RIVER_WAYPOINTS[i + 1];
      const dx = bx - ax, dy = by - ay;
      const len = Math.hypot(dx, dy) || 1;
      RIVER_SEGMENTS.push({ ax, ay, bx, by, dx, dy, len2: dx * dx + dy * dy, tx: dx / len, ty: dy / len });
    }

    function initOrganicWorld() {
      // Base inicial: plano verde Z=0
      hmap.fill(0);
      matMap.fill(MAT_GRASS);
      biomeMap.fill(0);
      bridges.length = 0;

      // Divisão orgânica inicial dos biomas por região
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const idx = row + mx;
          const wNoise = valueNoise2d(wx * 0.0055, wy * 0.0055) * 54;
          if (wy + wNoise > 645) biomeMap[idx] = 3; // Praia Sul
          else if (wx + wNoise > 126 && wy + wNoise < -15) biomeMap[idx] = 7; // Montanha NE
          else if (wx + wNoise > 126 && wy + wNoise >= -15) biomeMap[idx] = 6; // Bosque SE
          else if (wy + wNoise < -255 && wx + wNoise < 105) biomeMap[idx] = 4; // Jardim Zen NW
          else if (wx + wNoise < -600 && wy + wNoise >= -255) biomeMap[idx] = 1; // Girassóis W
          else if (wy + wNoise >= 360 && wx + wNoise < 90) biomeMap[idx] = 2; // Ruínas
          else biomeMap[idx] = 0; // Vila
        }
      }

      // Moldura natural elevada nas bordas Oeste, Norte e Leste (Sul aberto para o mar!)
      const edgeCols = Math.ceil(132 / VOX);
      for (let my = 0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        if (wy > 645) continue;
        const inTopBand = (wy - WORLD_MIN) < 132;
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          if (!inTopBand && mx >= edgeCols && mx < mw - edgeCols) {
            mx = mw - edgeCols - 1;
            continue;
          }
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const rawEdgeDist = Math.min(wx - WORLD_MIN, WORLD_MAX - wx, wy - WORLD_MIN);
          if (rawEdgeDist >= 132) continue;
          const wp = warp2d(wx, wy, 0.0075, 30);
          const edgeDist = Math.min(wp.x - WORLD_MIN, WORLD_MAX - wp.x, wp.y - WORLD_MIN);
          if (edgeDist >= 102) continue;
          const ridge = ridgedFbm(wp.x * 0.010 + 3.7, wp.y * 0.010 + 1.9, 2);
          const span = 78 + ridge * 24;
          if (edgeDist < span) {
            const t = Math.max(0, Math.min(1, (span - edgeDist) / 54));
            const peakH = 14 + ridge * 12;
            const idx = row + mx;
            hmap[idx] = Math.max(hmap[idx], Math.round(peakH * Math.pow(t, 1.15)));
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 1: CAMPOS DE GIRASSOL (Oeste) — cristas ondulantes orgânicas
      // ---------------------------------------------------------------------
      pullRidge([[-900, -135], [-825, -75], [-735, -15]], 132, [12, 14, 7], { warpAmp: 33, smoothK: 8, ridgeAmp: 0.24, mat: MAT_GRASS, biome: 1 });
      pullRidge([[-870, 210], [-810, 246], [-728, 315]], 114, [10, 8, 5], { warpAmp: 27, smoothK: 7, ridgeAmp: 0.22, mat: MAT_GRASS, biome: 1 });

      // ---------------------------------------------------------------------
      // BIOMA 0: VILA DA CLAREIRA (Centro-Oeste) — rampa orgânica Z=0..6
      // ---------------------------------------------------------------------
      pullHill(-285, -66, 93, 6, 1.35, 0.16, MAT_GRASS, 0);

      // ---------------------------------------------------------------------
      // BIOMA 4: JARDIM ZEN & PORTAL TORII (Noroeste)
      // ---------------------------------------------------------------------
      pullPlateau(-480, -510, 342, 270, 16, 48, 0.14, false, MAT_GRASS, 4);
      // Extensão Leste até Ponte Norte (wx=56, wy=-345)
      pullPlateau(-84, -354, 156, 78, 16, 42, 0.10, false, MAT_GRASS, 4);
      pullPlateau(54, -345, 28, 28, 16, 14, 0.04, false, MAT_STONE, 4, false, false);
      // Rampa larga da Vila (-435, -165) -> Jardim Zen (-435, -324)
      paintRampPath(-435, -165, 0, -435, -324, 16, 38, MAT_PATH, 4);
      // Terraço Superior Zen (Z=32 -> Z=48 orgânico em esporão terraceado)
      pullPlateau(-765, -765, 144, 114, 32, 24, 0.12, false, MAT_GRASS, 4);
      pullRidge([[-680, -760], [-760, -805], [-825, -825], [-890, -860]], 86, [32, 42, 48, 44], {
        warpAmp: 24, smoothK: 8, ridgeAmp: 0.22, terraceStep: 12, terraceStrength: 0.45, mat: MAT_STONE, biome: 4
      });
      pullPlateau(-825, -825, 28, 24, 48, 10, 0.06, false, MAT_STONE, 4, false, false);
      // Alameda Zen (~44u de largura!) passando sob o Torii (-435, -405)
      paintOrganicPath([[-435, -315], [-435, -615]], 22, MAT_PATH, 4, 16);
      // Lago Zen orgânico com warp2d em (-690, -585)
      carveOrganicPond(-690, -585, 66, 46, 26, 13, 8, 16, 4);

      // ---------------------------------------------------------------------
      // BIOMA 6: BOSQUE DOS COGUMELOS SALTITANTES (Sudeste)
      // ---------------------------------------------------------------------
      // Circuito aéreo de cogumelos: apoio Z=12 e Z=24 para caps Z=22 / 34 / 46 (espaçamento proporcional)
      pullPlateau(518, 272, 18, 18, 12, 14, 0.10, false, MAT_STONE, 6, false, false); // Apoio #2 (cap Z=34)
      pullPlateau(569, 288, 30, 16, 24, 12, 0.10, false, MAT_GRASS, 6, false, false); // Apoio #3 e #4 (caps Z=46)
      pullPlateau(620, 272, 18, 18, 12, 14, 0.10, false, MAT_STONE, 6, false, false); // Apoio #5 (cap Z=34)
      pullRidge([[735, 435], [825, 495], [915, 578]], 126, [11, 16, 12], { warpAmp: 33, smoothK: 8, ridgeAmp: 0.25, mat: MAT_GRASS, biome: 6 });

      // ---------------------------------------------------------------------
      // BIOMA 7: MONTANHA DO PICO SAKURA (Nordeste, Z=64 topo)
      // ---------------------------------------------------------------------
      // Contraforte Oeste Z=16 onde chega a Ponte Norte (wx=244, wy=-345)
      pullRidge([[222, -345], [288, -330], [366, -276], [438, -363]], 75, [16, 17, 24, 34], { warpAmp: 30, smoothK: 8, ridgeAmp: 0.26, mat: MAT_STONE, biome: 7 });
      pullPlateau(236, -345, 30, 26, 16, 14, 0.06, false, MAT_STONE, 7, false, false);
      // Paredão escarpado Oeste/Sul (intransponível direto!)
      pullPlateau(480, -540, 216, 186, 48, 9, 0.12, true, MAT_STONE, 7, false, true);
      // Espigões geológicos irradiando da montanha
      pullRidge([[540, -525], [690, -480], [818, -360], [750, -195], [652, -98]], 138, [58, 48, 34, 20, 6], { warpAmp: 39, ridgeAmp: 0.30, smoothK: 10, terraceStep: 14, terraceStrength: 0.35, mat: MAT_GRASS, biome: 7 });
      pullRidge([[525, -585], [660, -682], [802, -645], [848, -510]], 123, [58, 52, 42, 34], { warpAmp: 36, ridgeAmp: 0.30, smoothK: 10, terraceStep: 14, terraceStrength: 0.35, mat: MAT_GRASS, biome: 7 });
      // Cume arredondado do Pico Sakura (Z=64)
      pullPlateau(480, -540, 153, 135, 64, 33, 0.14, false, MAT_PEAK, 7, false, true);
      // Trilha contínua escavada em patamar subindo a encosta (Z=0 -> Z=64)
      carveBenchTrail([
        [615, -66, 0],
        [675, -135, 10],
        [753, -228, 20],
        [822, -339, 30],
        [819, -483, 40],
        [771, -612, 48],
        [681, -693, 56],
        [588, -645, 62],
        [531, -576, 64]
      ], 19, 40, MAT_PATH, 7);

      // ---------------------------------------------------------------------
      // BIOMA 5: RIO SINUOSO & CACHOEIRA ORGÂNICA (largura ~76u)
      // ---------------------------------------------------------------------
      const riverPts = RIVER_WAYPOINTS;
      carveRiverPath(riverPts, 76, -6);

      // Cachoeira Vertical na Falésia Oeste (wy=-495) + Poço + Riacho Plano até o Rio
      // Parte C1: Riacho plano (Z=-5) ligando o pé da cachoeira (wx=225) ao rio principal (wx=144)
      carveRiverPath([[225, -495], [185, -490], [144, -488]], 32, -5);

      // Parte C2: Poço circular com borda rasa caminhável (MAT_SHALLOW, d in [16..26]) ao pé da falésia
      {
        const gx0 = Math.max(0, Math.floor(204 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(282 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(-530 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(-460 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            if (hmap[idx] > 10) continue;
            const d = Math.hypot(wx - 238, wy + 495) + fbm2d(wx * 0.12, wy * 0.12) * 1.6;
            if (d <= 16) {
              hmap[idx] = -5;
              matMap[idx] = MAT_WATER;
              biomeMap[idx] = 5;
              cliffMask[idx] = 1;
            } else if (d <= 26) {
              hmap[idx] = -2;
              matMap[idx] = MAT_SHALLOW;
              biomeMap[idx] = 5;
              cliffMask[idx] = 1;
            } else if (d <= 30 && !isWetMat(matMap[idx]) && hmap[idx] <= 2) {
              hmap[idx] = Math.min(hmap[idx], 0);
              matMap[idx] = MAT_SAND;
              biomeMap[idx] = 5;
            }
          }
        }
      }

      // Partes A & B: Nascente no platô (wx>=309) + Calha úmida escura de pedra (wx=250..308, SEM MAT_WATER estático!)
      // + Terraços Z=48 acessíveis ao norte e sul (incluindo (298, -468))
      {
        const gx0 = Math.max(0, Math.floor(248 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(354 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(-534 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(-456 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const dy = Math.abs(wy + 495);
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            if (dy <= 17.0) {
              if (wx >= 309 && wx <= 346) {
                hmap[idx] = 46;
                matMap[idx] = MAT_WATER;
                biomeMap[idx] = 7;
                cliffMask[idx] = 1;
              } else if (wx >= 272 && wx <= 308) {
                hmap[idx] = wx >= 286 ? 46 : 44;
                matMap[idx] = MAT_STONE;
                shadowMask[idx] = Math.max(shadowMask[idx], 26);
                biomeMap[idx] = 7;
                cliffMask[idx] = 1;
              } else if (wx >= 250 && wx < 272) {
                hmap[idx] = Math.max(0, Math.min(43, Math.round(43 * (wx - 250) / 22)));
                matMap[idx] = MAT_STONE;
                shadowMask[idx] = Math.max(shadowMask[idx], 26);
                biomeMap[idx] = 7;
                cliffMask[idx] = 1;
              }
            } else if (wx >= 284 && wx <= 348) {
              // Margens Z=48 firmes e caminháveis (acesso ao topo da cachoeira em (298, -468) e margem norte)
              hmap[idx] = 48;
              matMap[idx] = MAT_STONE;
              biomeMap[idx] = 7;
              cliffMask[idx] = 1;
            }
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 3: PRAIA DOURADA, BAÍA SUL, PÍER, 8 VITÓRIAS-RÉGIAS & FAROL
      // ---------------------------------------------------------------------
      const shoreYByCol = new Float32Array(mw);
      const sandStartByCol = new Float32Array(mw);
      const shoreAmp = WORLD_SEED === DEFAULT_WORLD_SEED ? 34 : (105 + worldRand() * 65);
      const shoreFreq = WORLD_SEED === DEFAULT_WORLD_SEED ? 0.005 : (0.0028 + worldRand() * 0.0035);
      const shorePhase = WORLD_SEED === DEFAULT_WORLD_SEED ? 2.5 : (worldRand() * 20.0);
      for (let mx = 0; mx < mw; mx++) {
        const wx = (mx - HALF_GRID + 0.5) * VOX;
        const wave = fbm2dFast(wx * shoreFreq + shorePhase, 1.2) * shoreAmp;
        const rawShore = 756 + wave;
        shoreYByCol[mx] = WORLD_SEED === DEFAULT_WORLD_SEED ? rawShore : Math.max(625, Math.min(895, rawShore));
        sandStartByCol[mx] = shoreYByCol[mx] - 115;
      }
      const beachMy0 = Math.max(0, Math.floor(615 / VOX + HALF_GRID));
      for (let my = beachMy0; my < mh; my++) {
        const wy = (my - HALF_GRID + 0.5) * VOX;
        const row = my * mw;
        for (let mx = 0; mx < mw; mx++) {
          const wx = (mx - HALF_GRID + 0.5) * VOX;
          const idx = row + mx;
          const shoreY = shoreYByCol[mx];
          const sandStart = sandStartByCol[mx];

          const shallowWidth = 56 + fbm2d(wx * 0.018 + 3.1, 7.4) * 18;
          const shallowEndY = Math.min(842, shoreY + shallowWidth);
          if (wy >= shallowEndY) {
            hmap[idx] = -6;
            matMap[idx] = MAT_WATER;
            biomeMap[idx] = 3;
          } else if (wy >= shoreY) {
            if (matMap[idx] !== MAT_WATER) {
              hmap[idx] = -2;
              matMap[idx] = MAT_SHALLOW;
              biomeMap[idx] = 3;
            }
          } else if (wy >= shoreY - 10) {
            if (!isWetMat(matMap[idx])) {
              hmap[idx] = -1;
              matMap[idx] = MAT_SAND;
              biomeMap[idx] = 3;
            }
          } else if (wy >= sandStart) {
            if (!isWetMat(matMap[idx])) {
              hmap[idx] = Math.max(0, hmap[idx]);
              matMap[idx] = MAT_SAND;
              biomeMap[idx] = 3;
            }
          }
        }
      }

      // Ilhota Tropical Sul no Mar Sul (leste das 8 vitórias-régias, sempre MAT_SAND em h>=0)
      pullPlateau(198, 858, 72, 58, 2, 10, 0.14, true, MAT_SAND, 3, true);
      // Promontório Rochoso do Farol (Sudoeste) + Rampa de Acesso
      paintRampPath(-555, 714, 0, -636, 768, 14, 24, MAT_SAND, 3);
      pullPlateau(-690, 810, 132, 108, 14, 15, 0.14, true, MAT_STONE, 3);

      // 8 Vitórias-Régias saltáveis sobre o mar do Píer até a Ilhota Tropical Sul!
      for (const [lx, ly] of [
        [-132, 852], [-98, 864], [-64, 852], [-30, 864],
        [4, 852], [38, 864], [72, 852], [106, 858]
      ]) {
        setCirclePatch(lx, ly, 14.0, 0, MAT_LILYPAD, 3, true);
      }

      // ---------------------------------------------------------------------
      // PONTES PARABÓLICAS EM ARCO (rio visível embaixo!) & PEDRAS DE TRAVESSIA
      // ---------------------------------------------------------------------
      // Ponte Central em Arco (Z=2..8, Vila <-> Bosque)
      addArchBridge({ axis: 'x', xMin: 40, xMax: 230, yMin: 84, yMax: 132, baseZ: 2, archH: 6, hasRailings: true, biome: 5 });
      // Ponte Norte Alta em Arco (Z=16..21, Jardim Zen <-> Contraforte da Montanha)
      addArchBridge({ axis: 'x', xMin: 56, xMax: 244, yMin: -368, yMax: -322, baseZ: 16, archH: 5, hasRailings: true, biome: 5 });
      // Passarela Sul da Praia (Z=2..7, Praia Oeste <-> Praia Leste)
      addArchBridge({ axis: 'x', xMin: 30, xMax: 220, yMin: 645, yMax: 685, baseZ: 2, archH: 5, hasRailings: true, biome: 3 });
      // Píer Sul de Madeira (Z=2)
      addArchBridge({ axis: 'y', xMin: -198, xMax: -162, yMin: 690, yMax: 865, baseZ: 2, archH: 0, hasRailings: false, isPier: true, biome: 3 });

      // Garante margens planas e transitáveis nos encontros das pontes de Z=2 e do Píer
      for (const [ax, ay] of [[40, 108], [230, 108], [30, 665], [220, 665], [-180, 690]]) {
        pullPlateau(ax, ay, 24, 24, 0, 10, 0.04, false, MAT_PATH, null, false, false);
      }

      // Pedras de Travessia no Rio Médio-Sul (Z=2, wy=495)
      for (const sx of [96, 124, 152, 180]) {
        setCirclePatch(sx, 495, 12.0, 2, MAT_STONE, 5, true);
      }

      // Vau Raso Orgânico do Rio perto da Vila (sul da Ponte Central) -> MAT_SHALLOW caminhável com contorno fbm2d
      {
        const gx0 = Math.max(0, Math.floor(72 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(208 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(195 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(330 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const tSeg = Math.max(0, Math.min(1, (wy - 108) / (435 - 108)));
          const centerWx = 134 + (144 - 134) * tSeg;
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            if (!isWetMat(matMap[idx]) && hmap[idx] > 1) continue;
            const dRiver = Math.abs(wx - centerWx);
            const diagTilt = (wx - centerWx) * 0.28;
            const yNorth = 226 + diagTilt + fbm2d(wx * 0.028 + 1.3, 4.1) * 26 + Math.sin(wx * 0.055) * 6;
            const ySouth = 296 + diagTilt + fbm2d(wx * 0.028 + 7.7, 9.2) * 26 - Math.cos(wx * 0.05) * 6;
            const inMainSandbar = (wy >= yNorth && wy <= ySouth) && (matMap[idx] === MAT_WATER || dRiver <= 38);
            const inBankShoal = (dRiver >= 27 && dRiver <= 39) && (wy >= yNorth - 22 && wy <= ySouth + 22) && (matMap[idx] === MAT_WATER) && (fbm2d(wx * 0.06, wy * 0.06) > -0.15);
            if (inMainSandbar || inBankShoal) {
              hmap[idx] = -2;
              matMap[idx] = MAT_SHALLOW;
              biomeMap[idx] = 5;
              cliffMask[idx] = 1;
            }
          }
        }
      }

      // ---------------------------------------------------------------------
      // BIOMA 2: RUÍNAS ORGÂNICAS & 4 BLOCOS ERODIOS DE TESTE (cliffMask=1)
      // ---------------------------------------------------------------------
      // Pátio plano Z=0 em volta de wy=378..630 garantindo base limpa para os testes
      {
        const gx0 = Math.max(0, Math.floor(-558 / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(54 / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(378 / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(630 / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const wy = (my - HALF_GRID + 0.5) * VOX;
          const inPathY = (wy >= 408 && wy <= 606);
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const wx = (mx - HALF_GRID + 0.5) * VOX;
            const idx = row + mx;
            if (!isWetMat(matMap[idx])) {
              hmap[idx] = 0;
              biomeMap[idx] = 2;
              cliffMask[idx] = 1;
              if (inPathY && wx >= -498 && wx <= 42) {
                matMap[idx] = MAT_PATH;
              }
            }
          }
        }
      }
      // 4 Blocos Retangulares Erodidos das Ruínas ao longo de wy=495 (halfW=30, halfD=26)
      pullRuinsBlock(-420, 495, 30, 26, 6,  8.0, MAT_STONE, 2); // A: Z=6  (sobe andando!)
      pullRuinsBlock(-285, 495, 30, 26, 16, 2.0, MAT_STONE, 2); // B: Z=16 (pulo 1H!)
      pullRuinsBlock(-150, 495, 30, 26, 32, 2.0, MAT_STONE, 2); // C: Z=32 (pulo 2H máx!)
      pullRuinsBlock(-15,  495, 30, 26, 48, 2.0, MAT_STONE, 2); // D: Z=48 (3H bloqueado!)

      // ---------------------------------------------------------------------
      // TRILHAS ORGÂNICAS CONECTANDO VILA <-> BIOMAS
      // ---------------------------------------------------------------------
      paintOrganicPath([[-330, 90], [40, 108]], 20, MAT_PATH, 0, 0);                            // Vila -> Ponte Central
      paintOrganicPath([[230, 108], [375, 165], [570, 90], [615, -66]], 20, MAT_PATH, 6);       // Ponte -> Bosque / Base Montanha
      paintOrganicPath([[-330, 90], [-630, 90]], 20, MAT_PATH, 0, 0);                           // Vila -> Girassóis
      paintOrganicPath([[-330, 90], [-330, 405]], 20, MAT_PATH, 0, 0);                          // Vila -> Ruínas
      paintOrganicPath([[-330, 90], [-435, -165]], 20, MAT_PATH, 0, 0);                         // Vila -> Rampa Zen
      paintOrganicPath([[-216, 585], [-180, 690]], 20, MAT_PATH, 2, 0);                         // Ruínas -> Píer
      paintOrganicPath([[-180, 665], [30, 665]], 18, MAT_SAND, 3);                              // Praia Oeste -> Passarela Sul
      paintOrganicPath([[220, 665], [480, 714]], 18, MAT_SAND, 3);                              // Passarela Sul -> Praia Leste
      paintOrganicPath([[-330, 90], [-458, 135]], 16, MAT_PATH, 0, 0);                          // Vila -> Cabana 1
      paintOrganicPath([[-330, 90], [-243, 201]], 16, MAT_PATH, 0, 0);                          // Vila -> Cabana 2

      // Garante platôs planos Z=0 sob a Cabana 1 (-525, 135) e Cabana 2 (-180, 225)
      for (const [x0w, x1w, y0w, y1w] of [[-624, -420, 45, 240], [-270, -90, 150, 300]]) {
        const gx0 = Math.max(0, Math.floor(x0w / VOX + HALF_GRID));
        const gx1 = Math.min(mw - 1, Math.ceil(x1w / VOX + HALF_GRID));
        const gy0 = Math.max(0, Math.floor(y0w / VOX + HALF_GRID));
        const gy1 = Math.min(mh - 1, Math.ceil(y1w / VOX + HALF_GRID));
        for (let my = gy0; my <= gy1; my++) {
          const row = my * mw;
          for (let mx = gx0; mx <= gx1; mx++) {
            const idx = row + mx;
            hmap[idx] = 0;
            cliffMask[idx] = 1;
          }
        }
      }

      // Macro-variação procedural por Seed (cordilheiras, lagoas grandes, estradas curvas e ilhotas)
      if (WORLD_SEED !== DEFAULT_WORLD_SEED) {
        // 1. 4 grandes cadeias de montanhas / platôs rochosos com cumes variados
        const ridgeSpots = [
          [-680, -80], [-120, -180], [540, 120], [720, 480],
          [-680, 260], [360, 460], [-180, -780], [780, -240]
        ];
        let ridgesAdded = 0;
        for (let i = 0; i < ridgeSpots.length && ridgesAdded < 4; i++) {
          if (worldRand() < 0.35 && ridgeSpots.length - i > 4 - ridgesAdded) continue;
          const [bx, by] = ridgeSpots[i];
          const cx = bx + (worldRand() - 0.5) * 140;
          const cy = by + (worldRand() - 0.5) * 140;
          if (Math.hypot(cx + 330, cy - 90) < 130) continue; // protege spawn
          if (Math.hypot(cx - 134, cy - 108) < 130) continue; // protege rio/ponte
          const ang = worldRand() * Math.PI;
          const span = 120 + worldRand() * 90;
          const p0 = [cx - Math.cos(ang) * span, cy - Math.sin(ang) * span];
          const p1 = [cx + (worldRand() - 0.5) * 60, cy + (worldRand() - 0.5) * 60];
          const p2 = [cx + Math.cos(ang) * span, cy + Math.sin(ang) * span];
          const peakH = 22 + Math.round(worldRand() * 28);
          const matTop = peakH >= 38 ? MAT_PEAK : (peakH >= 28 ? MAT_STONE : MAT_GRASS);
          pullRidge([p0, p1, p2], 95 + worldRand() * 45, [10, peakH, 12], {
            warpAmp: 36, smoothK: 9, ridgeAmp: 0.28, terraceStep: 12, terraceStrength: 0.35, mat: matTop, biome: null
          });
          ridgesAdded++;
        }

        // 2. 3 grandes lagos orgânicos (visíveis no minimapa!) em planícies seguras
        const lakeZones = [[-620, -160], [450, 140], [-720, 220], [640, 420], [-180, -160]];
        let lakesAdded = 0;
        for (let i = 0; i < lakeZones.length && lakesAdded < 3; i++) {
          if (worldRand() < 0.35 && lakeZones.length - i > 3 - lakesAdded) continue;
          const [px, py] = lakeZones[i];
          const lx = px + (worldRand() - 0.5) * 120;
          const ly = py + (worldRand() - 0.5) * 120;
          if (Math.hypot(lx + 330, ly - 90) < 140) continue;
          carveOrganicPond(lx, ly, 62 + worldRand() * 38, 48 + worldRand() * 32, 22, -4, 10, 2, null);
          lakesAdded++;
        }

        // 3. Ilhotas arenosas extras no mar sul
        for (let k = 0; k < 3; k++) {
          const ix = (worldRand() < 0.5 ? -1 : 1) * (280 + worldRand() * 540);
          const iy = 865 + worldRand() * 90;
          pullPlateau(ix, iy, 52 + worldRand() * 42, 38 + worldRand() * 32, 2, 10, 0.20, true, MAT_SAND, 3, true);
        }

        // 4. Estradas secundárias curvas conectando os novos marcos
        for (let k = 0; k < 2; k++) {
          const tx = (worldRand() < 0.5 ? -1 : 1) * (350 + worldRand() * 400);
          const ty = -250 + worldRand() * 600;
          const mx = (-330 + tx) * 0.5 + (worldRand() - 0.5) * 160;
          const my = (90 + ty) * 0.5 + (worldRand() - 0.5) * 160;
          paintOrganicPath([[-330, 90], [mx, my], [tx, ty]], 16, MAT_PATH, null, null);
        }

        // Re-garante Spawn (-330, 90) plano e seguro após macro-variação
        pullPlateau(-330, 90, 36, 36, 0, 8, 0.02, false, MAT_PATH, 0, true, false);
      }

      // Erosão térmica + hidráulica determinística, seguida por relaxamento elástico final
      thermalAndHydraulicErosion(2, 240);
      elasticChainRelax(1);
      buildStandableMap();
    }
    initOrganicWorld();

    function getCellAt(wx, wy) {
      const mx = Math.floor(wx / VOX + HALF_GRID);
      const my = Math.floor(wy / VOX + HALF_GRID);
      if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
      const idx = my * mw + mx;
      const b = biomeMap[idx];
      return {
        mx, my, idx,
        h: hmap[idx],
        mat: matMap[idx],
        biomeId: b,
        biomeKey: BIOME_KEYS[b],
        biome: BIOME_NAMES[b],
        isCliff: cliffMask[idx] === 1,
        standable: standableMap[idx] === 1,
        cliffTop: cliffTopMap[idx]
      };
    }

    function getHeightAt(wx, wy) {
      const mx = Math.floor(wx / VOX + HALF_GRID);
      const my = Math.floor(wy / VOX + HALF_GRID);
      if (mx < 0 || my < 0 || mx >= mw || my >= mh) return null;
      return hmap[my * mw + mx];
    }

