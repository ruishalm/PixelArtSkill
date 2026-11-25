    // =========================================================================
    // 5. SISTEMA DE COLISÃO UNIFICADO (5 Modos) & POPULAÇÃO DOS 23 MODELOS
    // =========================================================================
    const PROP_COLLIDER_META = {
      pine_tree:       { mode: 'solid',    r: 7.5,  h: 72,  shadowR: 19 },
      sakura_oak:      { mode: 'solid',    r: 14.0, h: 102, shadowR: 36 },
      cozy_cabin:      { mode: 'box',      halfW: 35.0, halfD: 30.5, h: 80, shadowR: 42 },
      lighthouse:      { mode: 'solid',    r: 21.5, h: 126, shadowR: 30 },
      campfire:        { mode: 'solid',    r: 7.2,  h: 13,  shadowR: 9 },
      wood_sign:       { mode: 'solid',    r: 5.0,  h: 20 },
      ruin_pillar:     { mode: 'solid',    r: 11.0, h: 50,  shadowR: 16 },
      stone_lantern:   { mode: 'solid',    r: 8.0,  h: 36,  shadowR: 12 },
      beach_umbrella:  { mode: 'solid',    r: 3.8,  h: 42,  shadowR: 18 },
      wood_boat:       { mode: 'box',      halfW: 22.5, halfD: 12.8, h: 18, shadowR: 20 },
      bush_berry:      { mode: 'solid',    r: 6.8,  h: 13,  shadowR: 9 },
      sunflower:       { mode: 'solid',    r: 4.5,  h: 21 },
      pumpkin_patch:   { mode: 'solid',    r: 8.2,  h: 11 },
      mushroom_giant:  { mode: 'platform', r: 11.2, h: 22,  shadowR: 15 },
      boulder_large:   { mode: 'platform', r: 8.8,  h: 16,  shadowR: 12 },
      hay_bale:        { mode: 'platform', r: 9.6,  h: 14,  shadowR: 12 },
      tree_stump:      { mode: 'platform', r: 9.2,  h: 14,  shadowR: 12 },
      torii_gate:      { mode: 'arch',     offset: 24.5, r: 5.5, h: 80, shadowR: 26 },
      flower_tuft:     { mode: 'none' },
      grass_tuft_short:{ mode: 'none' },
      grass_tuft_tall: { mode: 'none' }
    };

    const FOLIAGE_META = {
      pine_tree:     { isFoliage: true, rigidity: 0.62, windScale: 3.2, pushRadius: 16, pushStrength: 3.5, leafColors: ['#2D6A4F', '#40916C', '#52B788'] },
      sakura_oak:    { isFoliage: true, rigidity: 0.58, windScale: 3.6, pushRadius: 24, pushStrength: 3.0, leafColors: ['#F9A8D4', '#F472B6', '#FBCFE8'] },
      bush_berry:    { isFoliage: true, rigidity: 0.25, windScale: 2.6, pushRadius: 14, pushStrength: 6.5, leafColors: ['#3A7D44', '#65B85B', '#EF4444'] },
      sunflower:     { isFoliage: true, rigidity: 0.18, windScale: 3.8, pushRadius: 12, pushStrength: 7.5, leafColors: ['#FACC15', '#EAB308', '#4D7C0F'] },
      flower_tuft:   { isFoliage: true, rigidity: 0.12, windScale: 2.4, pushRadius: 10, pushStrength: 6.0, leafColors: ['#FACC15', '#F472B6', '#FFFFFF'] },
      pumpkin_patch: { isFoliage: true, rigidity: 0.72, windScale: 1.0, pushRadius: 12, pushStrength: 2.5, leafColors: ['#EA580C', '#65B85B'] }
    };

    const TOOLS_META = {
      none:         { label: '🐾 Patada',   modelKey: null },
      tool_axe:     { label: '🪓 Machado',  modelKey: 'tool_axe' },
      tool_pickaxe: { label: '⛏️ Picareta', modelKey: 'tool_pickaxe' },
      tool_hoe:     { label: '🌾 Enxada',   modelKey: 'tool_hoe' }
    };
    const TOOL_ORDER = ['none', 'tool_axe', 'tool_pickaxe', 'tool_hoe'];

    const DESTRUCTIBLE_META = {
      pine_tree:     { mode: 'chop',    hp: 3, zCut: 8,  drops: 3, dropKey: 'wood_log',    bestTool: 'tool_axe',     colors: ['#2D6A4F', '#40916C', '#6B4226', '#8C5A37'] },
      sakura_oak:    { mode: 'chop',    hp: 4, zCut: 10, drops: 4, dropKey: 'wood_log',    bestTool: 'tool_axe',     colors: ['#F9A8D4', '#F472B6', '#FBCFE8', '#6B4226'] },
      ruin_pillar:   { mode: 'crumble', hp: 3, zCut: 9,  drops: 3, dropKey: 'stone_chunk', bestTool: 'tool_pickaxe', colors: ['#847F77', '#ADA79E', '#CFC9BE', '#68A352'] },
      boulder_large: { mode: 'crumble', hp: 3, zCut: 5,  drops: 3, dropKey: 'stone_chunk', bestTool: 'tool_pickaxe', colors: ['#5C5852', '#847F77', '#ADA79E'] },
      stone_lantern: { mode: 'crumble', hp: 2, zCut: 7,  drops: 2, dropKey: 'stone_chunk', bestTool: 'tool_pickaxe', colors: ['#847F77', '#FDE68A', '#CFC9BE'] },
      bush_berry:    { mode: 'trim',    hp: 2, drops: 0, bestTool: 'tool_hoe', colors: ['#3A7D44', '#65B85B', '#EF4444'] },
      sunflower:     { mode: 'trim',    hp: 1, drops: 0, bestTool: 'tool_hoe', colors: ['#FACC15', '#EAB308', '#4D7C0F'] },
      pumpkin_patch: { mode: 'trim',    hp: 2, drops: 0, bestTool: 'tool_hoe', colors: ['#EA580C', '#F97316', '#65B85B'] }
    };

    const props = [];
    let damBoulder = null;
    const foliageProps = [];
    const propColliders = [];
    const platformColliders = [];
    const fishes = [];
    const npcs = [];
    const toolPickups = [];
    const fallingBodies = [];
    const debrisDrops = [];
    const destructStats = {
      hits: 0,
      choppedCount: 0,
      crumbledCount: 0,
      trimmedCount: 0
    };

    function stampPropShadowAndClearGrass(wx, wy, shadowR, footprintR) {
      const rMax = Math.max(shadowR || 0, footprintR || 0);
      if (rMax <= 0) return;
      const x0 = Math.max(0, Math.floor((wx - rMax) / VOX + HALF_GRID));
      const x1 = Math.min(mw - 1, Math.ceil((wx + rMax) / VOX + HALF_GRID));
      const y0 = Math.max(0, Math.floor((wy - rMax) / VOX + HALF_GRID));
      const y1 = Math.min(mh - 1, Math.ceil((wy + rMax) / VOX + HALF_GRID));
      for (let my = y0; my <= y1; my++) {
        const gy = (my - HALF_GRID + 0.5) * VOX;
        for (let mx = x0; mx <= x1; mx++) {
          const gx = (mx - HALF_GRID + 0.5) * VOX;
          const d = Math.hypot(gx - wx, gy - wy);
          const idx = my * mw + mx;
          if (footprintR && d <= footprintR + 1.5) noGrassMask[idx] = 1;
          if (shadowR && d <= shadowR) {
            const strength = Math.round((1 - d / shadowR) * 42);
            if (strength > shadowMask[idx]) shadowMask[idx] = strength;
          }
        }
      }
    }

    function addProp(modelKey, wx, wy, options = {}) {
      const c = getCellAt(wx, wy);
      if (!c || !propModels[modelKey]) return;
      const meta = PROP_COLLIDER_META[modelKey] || { mode: 'none' };

      if (!options.allowOnPath && !options.allowInWater && meta.mode !== 'none' && meta.mode !== 'arch') {
        if (c.mat === MAT_PATH || c.mat === MAT_BRIDGE || isWetMat(c.mat) || c.mat === MAT_LILYPAD || getBridgeAt(wx, wy, 2)) {
          return;
        }
      }

      const scale = options.scale || 1.0;
      const liftZ = options.liftZ !== undefined ? options.liftZ : c.h;
      const angle = options.angle || 0;
      const model = propModels[modelKey];
      const baseZ = Math.round(liftZ);
      const topZ = baseZ + Math.ceil(model.count * scale);

      const item = {
        id: `${modelKey}_${props.length}`,
        modelKey,
        model,
        wx, wy,
        wz: liftZ,
        baseZ,
        topZ,
        selfAngle: angle,
        scale,
        isFire: modelKey === 'campfire' || modelKey === 'stone_lantern',
        isDamBoulder: !!options.isDamBoulder,
        isPlatform: meta.mode === 'platform',
        platTopZ: meta.mode === 'platform' ? liftZ + meta.h * scale : liftZ
      };
      if (item.isDamBoulder) damBoulder = item;
      const fMeta = FOLIAGE_META[modelKey];
      if (fMeta) {
        item.foliage = fMeta;
        item.bx = 0;
        item.by = 0;
        item.vx = 0;
        item.vy = 0;
        item.rustleCd = 0;
        foliageProps.push(item);
      }
      const dMeta = DESTRUCTIBLE_META[modelKey];
      if (dMeta) {
        item.destr = { ...dMeta, maxHp: dMeta.hp, hp: dMeta.hp, hitFlash: 0, chopped: false };
      }
      props.push(item);

      const footR = meta.mode === 'box'
        ? Math.max(meta.halfW, meta.halfD) * scale
        : (meta.r || 4) * scale;
      stampPropShadowAndClearGrass(wx, wy, (meta.shadowR || 0) * scale, meta.mode !== 'none' ? footR : 0);

      if (meta.mode === 'solid') {
        const sc = {
          shape: 'circle', wx, wy,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey,
          disabled: false
        };
        propColliders.push(sc);
        item.solidCollider = sc;
      } else if (meta.mode === 'box') {
        const sc = {
          shape: 'box', wx, wy,
          halfW: meta.halfW * scale, halfD: meta.halfD * scale,
          angle, baseZ: liftZ, colH: meta.h * scale, modelKey,
          disabled: false
        };
        propColliders.push(sc);
        item.solidCollider = sc;
      } else if (meta.mode === 'platform') {
        const pc = {
          wx, wy, r: meta.r * scale,
          baseZ: liftZ, topZ: liftZ + meta.h * scale, modelKey,
          disabled: false
        };
        platformColliders.push(pc);
        item.platCollider = pc;
      } else if (meta.mode === 'arch') {
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);
        const off = meta.offset * scale;
        propColliders.push({
          shape: 'circle',
          wx: wx - off * cosA, wy: wy - off * sinA,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey
        });
        propColliders.push({
          shape: 'circle',
          wx: wx + off * cosA, wy: wy + off * sinA,
          r: meta.r * scale, baseZ: liftZ, colH: meta.h * scale, modelKey
        });
      }
    }

    function addFish(wx, wy, label, extraZ = 0) {
      const br = getBridgeAt(wx, wy);
      const c = getCellAt(wx, wy);
      const baseH = br ? getBridgeDeckZ(br, wx, wy) : (c ? c.h : 0);
      fishes.push({
        id: `fish_${fishes.length}`,
        label,
        wx, wy,
        baseZ: baseH + extraZ,
        collected: false
      });
    }

    function isNearPathOrWater(wx, wy, bufferU = 8) {
      const step = VOX;
      for (let dy = -bufferU; dy <= bufferU; dy += step) {
        for (let dx = -bufferU; dx <= bufferU; dx += step) {
          if (getBridgeAt(wx + dx, wy + dy, 0)) return true;
          const c = getCellAt(wx + dx, wy + dy);
          if (!c) return true;
          if (c.mat === MAT_PATH || c.mat === MAT_BRIDGE || isWetMat(c.mat) || c.mat === MAT_LILYPAD) {
            return true;
          }
        }
      }
      return false;
    }

    function addForestProp(modelKey, wx, wy, options = {}) {
      if (isNearPathOrWater(wx, wy, options.pathBuffer || 8)) return;
      if (Math.hypot(wx + 330, wy - 90) < 32) return; // Mantém spawn livre
      const meta = PROP_COLLIDER_META[modelKey] || { r: 5 };
      const minGap = (meta.r || 5) + 6;
      for (const sc of propColliders) {
        if (sc.disabled) continue;
        if (isPointInPropCollider(wx, wy, sc, minGap)) return;
      }
      for (const pc of platformColliders) {
        if (pc.disabled) continue;
        if (Math.hypot(wx - pc.wx, wy - pc.wy) < pc.r + minGap) return;
      }
      addProp(modelKey, wx, wy, options);
    }

    function populateWorldObjects() {
      // 0. Vila da Clareira (Mini-Vila com 2 Cabanas, fogueira, horta e tocos)
      addProp('cozy_cabin', -525, 135);
      addProp('cozy_cabin', -180, 225);
      addProp('campfire', -285, 30);
      addProp('wood_sign', -276, 134, { angle: 0.22 });
      addProp('pumpkin_patch', -465, 252);
      addProp('pumpkin_patch', -426, 261);
      addProp('tree_stump', -262, 153);
      addProp('tree_stump', -378, 195);
      addProp('flower_tuft', -396, 174);
      addProp('flower_tuft', -348, 36);
      addProp('flower_tuft', -231, 276);
      addProp('bush_berry', -204, 297);
      addProp('bush_berry', -579, 228);
      addForestProp('pine_tree', -585, -54);
      addForestProp('pine_tree', -186, -75);
      addForestProp('pine_tree', -570, 288);
      addForestProp('pine_tree', -120, 322);
      addForestProp('pine_tree', -435, 33);
      addForestProp('pine_tree', -75, -52);

      // 1. Campos de Girassol (~30 girassóis + 4 fardos platform)
      for (const [tx, ty] of [
        [-825, 30], [-765, 96], [-864, -30], [-744, -126], [-876, -135],
        [-774, 216], [-855, 264], [-720, 324], [-906, 126], [-705, -36],
        [-930, -60], [-897, 33], [-807, -174], [-684, -186], [-918, 204],
        [-792, 315], [-663, 249], [-741, 36], [-834, 168], [-927, -162],
        [-960, 0], [-950, 90], [-965, 170], [-880, 310], [-750, -210],
        [-850, -220], [-690, 110], [-795, -55], [-890, -200], [-660, -90]
      ]) {
        addProp('sunflower', tx, ty);
      }
      addProp('hay_bale', -675, 186);
      addProp('hay_bale', -765, 156);
      addProp('hay_bale', -840, 270);
      addProp('hay_bale', -720, -45);
      addProp('tree_stump', -696, 312);
      addProp('flower_tuft', -870, 186);
      addProp('flower_tuft', -756, -81);
      addForestProp('pine_tree', -942, -243);
      addForestProp('pine_tree', -936, 360);
      addForestProp('pine_tree', -645, -243);

      // 2. Ruínas Orgânicas (Pátio sul em wy=495)
      addProp('ruin_pillar', -516, 414, { allowOnPath: true });
      addProp('ruin_pillar', 48,   414, { allowOnPath: true });
      addProp('stone_lantern', -516, 576, { allowOnPath: true });
      addProp('stone_lantern', 48,   576, { allowOnPath: true });
      addProp('boulder_large', -504, 495, { allowOnPath: true });
      addProp('flower_tuft', -360, 606);
      addProp('flower_tuft', -82,  606);

      // 3. Praia Dourada, Enseada & Farol Monumental
      addProp('lighthouse', -714, 822);
      addProp('stone_lantern', -606, 774);
      addProp('beach_umbrella', -360, 702);
      addProp('beach_umbrella', -60,  708);
      addProp('beach_umbrella', 270,  702);
      addProp('wood_boat', 345,  720, { angle: 0.16 });
      addProp('wood_boat', -465, 726, { angle: -0.22 });
      addProp('boulder_large', 234, 870);
      addProp('boulder_large', -540, 756, { allowInWater: true });

      // Obstáculos Fluídicos Dinâmicos no Rio & Cachoeira (desvio Rankine Dipole + Barragem Quebrável)
      addProp('boulder_large', 112, 258, { allowInWater: true });
      addProp('boulder_large', 132, -80, { allowInWater: true, liftZ: -4 });
      addProp('boulder_large', 278, -495, { allowInWater: true, allowOnPath: true, liftZ: 44, isDamBoulder: true });
      addProp('ruin_pillar', 154, 375, { allowInWater: true, liftZ: -3 });

      // 4. Jardim Zen & Portal Torii Gigante
      addProp('torii_gate', -435, -405, { angle: 0, allowOnPath: true });
      addProp('stone_lantern', -545, -405);
      addProp('stone_lantern', -325, -405);
      addProp('stone_lantern', -576, -570);
      addProp('bush_berry', -276, -585);
      addProp('flower_tuft', -474, -630);
      addProp('boulder_large', -705, -735);
      addProp('ruin_pillar', -762, -744);
      addForestProp('pine_tree', -252, -675);
      addForestProp('pine_tree', -630, -735);
      addForestProp('pine_tree', -840, -465);
      addForestProp('pine_tree', -210, -840);
      addForestProp('pine_tree', -540, -855);

      // 6. Bosque dos Cogumelos Saltitantes (7 cogumelos gigantes em circuito aéreo)
      addProp('mushroom_giant', 484, 256);  // #1 Cap Z=22
      addProp('mushroom_giant', 518, 272);  // #2 Em Z=12 -> Cap Z=34!
      addProp('mushroom_giant', 552, 288);  // #3 Em Z=24 -> Cap Z=46!
      addProp('mushroom_giant', 586, 288);  // #4 Em Z=24 -> Cap Z=46!
      addProp('mushroom_giant', 620, 272);  // #5 Em Z=12 -> Cap Z=34!
      addProp('mushroom_giant', 654, 256);  // #6 Cap Z=22
      addProp('mushroom_giant', 384, 435);  // #7 Cap Z=22 (âncora sul)
      for (const [tx, ty] of [
        [315, 228], [354, 345], [480, 525], [684, 516], [765, 276],
        [885, 330], [870, 555], [306, 546], [924, 435], [744, 126],
        [510, 435], [630, 405]
      ]) {
        addForestProp('pine_tree', tx, ty);
      }
      addProp('tree_stump', 378, 258);
      addProp('tree_stump', 741, 237);
      addProp('hay_bale', 804, 474);
      addProp('boulder_large', 744, 126);
      addProp('boulder_large', 465, 360);
      addProp('boulder_large', 862, 442);
      addProp('bush_berry', 540, 426);
      addProp('bush_berry', 675, 372);
      addProp('flower_tuft', 408, 216);
      addProp('flower_tuft', 660, 240);

      // 7. Montanha & Pico Sakura (Trilha em espiral mantida 100% livre!)
      addProp('sakura_oak', 450, -576);
      addProp('stone_lantern', 558, -486, { allowOnPath: true });
      addProp('stone_lantern', 408, -474, { allowOnPath: true });
      addProp('flower_tuft', 438, -474);
      addProp('flower_tuft', 546, -576);
      addProp('boulder_large', 336, -288);
      addForestProp('pine_tree', 426, -165);
      addForestProp('pine_tree', 375, -780);
      addForestProp('pine_tree', 900, -705);
      addForestProp('pine_tree', 930, -90);
      addForestProp('pine_tree', 285, -675);

      // Florestas Densas nas bordas arborizadas (Norte, Oeste, Leste) — expansão 1.5× (~85 pinheiros!)
      for (let wx = -960; wx <= 960; wx += 120) {
        if (Math.abs(wx - 120) < 95) continue;
        addForestProp('pine_tree', wx, -1020);
      }
      for (let wy = -870; wy <= 540; wy += 125) {
        addForestProp('pine_tree', -1020, wy);
        addForestProp('pine_tree', 1020, wy);
      }
      // Bosques orgânicos secundários de borda (+ ~25 pinheiros extras)
      for (const [bx, by] of [
        [-960, -915], [-705, -945], [270, -930], [630, -930],
        [-952, -540], [945, -360], [952, 165], [-945, 480],
        [-860, -950], [-560, -960], [-360, -960], [-140, -960], [340, -960],
        [520, -960], [760, -950], [920, -860], [-960, -740], [-960, -340],
        [-960, 120], [-960, 380], [960, -540], [960, -180], [960, 60],
        [960, 320], [960, 520], [-740, -400], [-320, -780], [260, -820],
        [780, -780], [880, -240], [820, 120], [-460, 320], [310, 590]
      ]) {
        addForestProp('pine_tree', bx, by);
      }
      for (const [bx, by] of [
        [-900, -810], [-540, -930], [345, -870], [870, -585], [900, 210], [-915, 435]
      ]) {
        addForestProp('bush_berry', bx, by);
      }

      // Props procedurais extras por Seed (visíveis ao redor da Vila, Campos e Bosque)
      if (WORLD_SEED !== DEFAULT_WORLD_SEED) {
        const extraKeys = ['pine_tree', 'sakura_oak', 'boulder_large', 'bush_berry', 'flower_tuft', 'sunflower', 'tree_stump'];
        for (let i = 0; i < 36; i++) {
          const wx = Math.round(-920 + worldRand() * 1840);
          const wy = Math.round(-880 + worldRand() * 1500);
          if (Math.hypot(wx + 330, wy - 90) < 62) continue; // não bloquear spawn
          const key = extraKeys[Math.floor(worldRand() * extraKeys.length)];
          addForestProp(key, wx, wy, { angle: (worldRand() - 0.5) * Math.PI * 2 });
        }
      }

      // 20 PEIXES DOURADOS COLECIONÁVEIS (distribuídos pelos 8 biomas)
      addFish(-285, -66,  'Rampa da Vila');                  // #1  Vila (Z=6)
      addFish(-262, 153,  'Toco da Vila', 14);               // #2  Vila (Z=14)
      addFish(-675, 186,  'Fardo dos Girassóis', 14);        // #3  Girassóis (Z=14)
      addFish(-825, -75,  'Colina dos Girassóis');           // #4  Girassóis (Z=14)
      addFish(-810, 246,  'Campo Sul dos Girassóis');        // #5  Girassóis (Z=8)
      addFish(-285, 495,  'Monolito Médio das Ruínas');      // #6  Ruínas (Z=16)
      addFish(-15,  495,  'Torre das Ruínas');               // #7  Ruínas (Z=48)
      addFish(-180, 855,  'Ponta do Píer');                  // #8  Praia (Z=2)
      addFish(-615, 846,  'Mirante do Farol');               // #9  Praia (Z=14)
      addFish(198,  858,  'Ilhota das Vitórias-Régias');     // #10 Praia (Z=2)
      addFish(480,  714,  'Enseada Leste');                  // #11 Praia (Z=0)
      addFish(135,  108,  'Ponte Central');                  // #12 Rio (Z=8 topo do arco)
      addFish(124,  495,  'Pedra do Rio');                   // #13 Rio (Z=2)
      addFish(150,  -345, 'Ponte Norte');                    // #14 Rio (Z=21 topo do arco)
      addFish(-435, -585, 'Alameda Pós-Torii');              // #15 Zen (Z=16)
      addFish(-825, -825, 'Mirante Zen');                    // #16 Zen (Z=48)
      addFish(518,  272,  'Cogumelo Médio', 22);             // #17 Cogumelos (Z=34)
      addFish(586,  288,  'Cogumelo Alto', 22);              // #18 Cogumelos (Z=46)
      addFish(819,  -483, 'Patamar da Montanha');            // #19 Montanha (Z=40)
      addFish(528,  -528, 'Pico Sakura Lendário');           // #20 Montanha (Z=64)

      // NPCs: Galinha Popó na Vila + 3 Pintinhos Piu nos Girassóis
      const popoCell = getCellAt(-324, 168);
      npcs.push({
        kind: 'chicken', name: 'Popó', model: chickenModel, scale: 0.72,
        x: -324, y: 168, z: popoCell ? popoCell.h : 0, homeX: -324, homeY: 168, roamR: 60,
        selfAngle: 0, walkPhase: 0, timer: 1.4, moving: true, dirX: 1, dirY: 0,
        speech: null
      });
      for (const [cx, cy] of [[-780, 60], [-795, -45], [-690, 225]]) {
        const c = getCellAt(cx, cy);
        npcs.push({
          kind: 'chick', name: 'Piu', model: propModels.baby_chick, scale: 0.95,
          x: cx, y: cy, z: c ? c.h : 0, homeX: cx, homeY: cy, roamR: 48,
          selfAngle: 0, walkPhase: 0, timer: 0.8 + worldRand(), moving: true, dirX: -1, dirY: 0.5,
          speech: null
        });
      }

      // Pickups das Ferramentas próximos ao Spawn da Vila
      for (const [toolId, wx, wy] of [
        ['tool_axe', -295, 62],
        ['tool_pickaxe', -270, 62],
        ['tool_hoe', -245, 62]
      ]) {
        const baseZ = getHeightAt(wx, wy) || 0;
        toolPickups.push({ toolId, wx, wy, baseZ, inside: false });
      }
    }
    populateWorldObjects();

