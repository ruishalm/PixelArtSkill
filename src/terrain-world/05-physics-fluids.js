    // =========================================================================
    // 7B. CONFIGURAÇÃO DO VALE FELINO: SPAWN, TRAVEL, LOGS, VERLET & HUD
    // =========================================================================
    {
      const spawnH = getHeightAt(SPAWN_X, SPAWN_Y) || 0;
      cat.z = spawnH;
      cat.groundZ = spawnH;
      cat.lastSafeZ = spawnH;
      cat.maxJumpReached = spawnH;
      camZ = spawnH;
      syncWaveOrigin();
    }

    const TRAVEL_SPOTS = [
      { wx: -330, wy: 90,   label: '🏡 Vila da Clareira' },
      { wx: -248, wy: 225,  label: '🏠 Cabana 2' },
      { wx: -780, wy: 90,   label: '🌻 Campos de Girassol' },
      { wx: -285, wy: 562,  label: '🏛️ Ruínas Orgânicas' },
      { wx: -180, wy: 684,  label: '🏖️ Praia Dourada' },
      { wx: -615, wy: 795,  label: '🗼 Farol Monumental' },
      { wx: -435, wy: -315, label: '⛩️ Jardim Zen & Torii' },
      { wx: 426,  wy: 228,  label: '🍄 Bosque Cogumelos' },
      { wx: 112,  wy: 232,  label: '💧 Vau Raso do Rio' },
      { wx: 615,  wy: -66,  label: '🥾 Base da Montanha' },
      { wx: 298,  wy: -468, label: '🌊 Topo da Cachoeira (Pedra)' },
      { wx: 480,  wy: -495, label: '🌸 Pico Sakura (Z=64)' }
    ];
    let travelIdx = 0;

    if (!window.__IS_STUDIO__) {
      rebuildWaterfallBlocks();
      for (let i = 0; i < 70; i++) {
        stepWaterfallSim(1 / 30, false);
      }
      initFlowStreaks();
    }

    if (!window.__IS_STUDIO__) {
      spawnPushableLog(86, 248, 0.4);     // Tronco empurrável na margem do vau do Rio (perto da Vila)
      spawnPushableLog(-618, -585, 0.8);  // Tronco empurrável na borda do Lago Zen
    }

    if (!window.__IS_STUDIO__) {
      // 1. Varal de bandeirinhas na Vila (entre Cabana 2 e o toco/poste)
      createVerletChain(-214, 210, 34, -262, 153, 22, 14, { pinEnd: true, segLen: 5.8, windScale: 1.35, kind: 'garland' });
      // 2. Fitas do Portal Torii no Jardim Zen
      createVerletChain(-458, -405, 58, -458, -405, 42, 8, { pinEnd: false, segLen: 2.2, windScale: 1.5, kind: 'banner', colors: ['#EF4444', '#FFFDF7'] });
      createVerletChain(-412, -405, 58, -412, -405, 42, 8, { pinEnd: false, segLen: 2.2, windScale: 1.5, kind: 'banner', colors: ['#EF4444', '#FFFDF7'] });
      // 3. Flâmula no topo do Farol da Praia
      createVerletChain(-714, 822, 122, -692, 822, 120, 10, { pinEnd: false, segLen: 2.4, windScale: 2.1, kind: 'banner', colors: ['#F97316', '#FACC15'] });
      // 4. Cipó pendente na Árvore Sakura do Pico
      createVerletChain(468, -576, 62, 468, -576, 40, 9, { pinEnd: false, segLen: 2.6, windScale: 1.4, kind: 'vine', colors: ['#F472B6', '#4ADE80'] });
    }

    function triggerMeow() {
      sfxMeow();
      catSpeak('Miau! 🐾', 110);
      for (const npc of npcs) {
        if (Math.hypot(npc.x - cat.x, npc.y - cat.y) < 110) {
          npc.speech = { text: npc.kind === 'chicken' ? 'Có có!! 💕' : 'Piu piu! 💛', timer: 110 };
        }
      }
    }

    const btnSkin = document.getElementById('btnSkin');
    const btnHat = document.getElementById('btnHat');
    if (btnSkin) btnSkin.addEventListener('click', () => {
      cat.skinIdx = (cat.skinIdx + 1) % CAT_SKINS.length;
      btnSkin.textContent = `🐱 ${CAT_SKINS[cat.skinIdx].name}`;
      sfxMeow();
    });
    if (btnHat) btnHat.addEventListener('click', () => {
      cat.hatIdx = (cat.hatIdx + 1) % HAT_PRESETS.length;
      btnHat.textContent = `🎩 ${HAT_PRESETS[cat.hatIdx].name}`;
    });
    const btnToolEl = document.getElementById('btnTool');
    if (btnToolEl) btnToolEl.addEventListener('click', () => {
      const nextIdx = (TOOL_ORDER.indexOf(equippedTool) + 1) % TOOL_ORDER.length;
      equipTool(TOOL_ORDER[nextIdx]);
    });
    const btnActionEl = document.getElementById('btnAction');
    if (btnActionEl) btnActionEl.addEventListener('click', () => {
      triggerAction();
    });
    const btnRotLEl = document.getElementById('btnRotL');
    if (btnRotLEl) btnRotLEl.addEventListener('click', () => { targetTurn += Math.PI / 4; });
    const btnRotREl = document.getElementById('btnRotR');
    if (btnRotREl) btnRotREl.addEventListener('click', () => { targetTurn -= Math.PI / 4; });
    const btnResetEl = document.getElementById('btnReset');
    if (btnResetEl) btnResetEl.addEventListener('click', resetCatToSpawn);
    const btnSeedEl = document.getElementById('btnSeed');
    if (btnSeedEl) {
      btnSeedEl.textContent = `🎲 Seed: ${WORLD_SEED}`;
      btnSeedEl.addEventListener('click', () => {
        const nextSeed = 1000 + Math.floor(Math.random() * 90000);
        const url = new URL(window.location.href);
        url.searchParams.set('seed', String(nextSeed));
        window.location.href = url.toString();
      });
    }
    const btnTravelEl = document.getElementById('btnTravel');
    if (btnTravelEl) btnTravelEl.addEventListener('click', () => {
      travelIdx = (travelIdx + 1) % TRAVEL_SPOTS.length;
      const spot = TRAVEL_SPOTS[travelIdx];
      teleportToWorld(spot.wx, spot.wy, spot.label);
      sfxBiome();
    });
