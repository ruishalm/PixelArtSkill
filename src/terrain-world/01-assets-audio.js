    // =========================================================================
    // 1. DADOS VOXEL EMBUTIDOS (Zero Fetch / 100% Autocontido)
    // =========================================================================
    const CAT_BODY_DATA = __CAT_SLICES__;
    const HATS_DATA = __HATS_PACK__;
    const CHICKEN_DATA = __CHICKEN_DATA__;
    const PROPS_DATA = __PROPS_PACK__;

    const PAW_DATA = [
      ["1441", "4114", "1441", "1111"],
      ["1111", "1111", "1111", "1111"]
    ];

    const CAT_SKINS = [
      { id: 'calico',  name: 'Mochi',   pal: ['rgba(0,0,0,0)', '#FDFBF7', '#DE864A', '#3B2219', '#F2A2AB', '#FFFFFF', '#B85820', '#E5E0D8'] },
      { id: 'black',   name: 'Kuro',    pal: ['rgba(0,0,0,0)', '#1E293B', '#334155', '#F59E0B', '#F472B6', '#FEF08A', '#0F172A', '#1E293B'] },
      { id: 'tuxedo',  name: 'Felix',   pal: ['rgba(0,0,0,0)', '#FFFFFF', '#1E293B', '#1E293B', '#F472B6', '#FFFFFF', '#0F172A', '#CBD5E1'] },
      { id: 'orange',  name: 'Cheddar', pal: ['rgba(0,0,0,0)', '#FED7AA', '#EA580C', '#3B2219', '#F472B6', '#FFFFFF', '#C2410C', '#FDBA74'] },
      { id: 'siamese', name: 'Luna',    pal: ['rgba(0,0,0,0)', '#FAF5EE', '#5C4033', '#0EA5E9', '#F472B6', '#FFFFFF', '#3E2723', '#EADBCA'] },
      { id: 'gray',    name: 'Misty',   pal: ['rgba(0,0,0,0)', '#94A3B8', '#64748B', '#F59E0B', '#F472B6', '#FFFFFF', '#475569', '#CBD5E1'] }
    ];

    const HAT_PRESETS = [
      { id: 'none',   name: 'Sem Chapéu', pal: null },
      { id: 'witch',  name: 'Bruxinho',   pal: ['rgba(0,0,0,0)', '#221533', '#E5A93C', '#38244F'] },
      { id: 'crown',  name: 'Coroa',      pal: ['rgba(0,0,0,0)', '#F4B846', '#FFD166', '#E63946'] },
      { id: 'beret',  name: 'Boina',      pal: ['rgba(0,0,0,0)', '#5E1428', '#B82D52', '#3D0C1A'] },
      { id: 'flower', name: 'Florzinha',  pal: ['rgba(0,0,0,0)', '#FFB7C5', '#FFD166'] }
    ];

    // =========================================================================
    // 2. CONSTRUTOR DE SLICE SHEETS (Base-36 & Nearest-Neighbor)
    // =========================================================================
    function decodeRLERow(row) {
      return row.indexOf('*') !== -1
        ? row.replace(/\*([0-9a-z])(\d+);/g, (_, ch, n) => ch.repeat(+n))
        : row;
    }

    function buildSliceSheet(data, pal) {
      const cnt = data.length;
      const h = data[0].length;
      const w = decodeRLERow(data[0][0]).length;
      const cv = document.createElement('canvas');
      cv.width = w * cnt;
      cv.height = h;
      const cx = cv.getContext('2d');
      cx.imageSmoothingEnabled = false;

      for (let z = 0; z < cnt; z++) {
        const offX = z * w;
        const rows = data[z];
        for (let y = 0; y < h; y++) {
          const row = decodeRLERow(rows[y]);
          for (let x = 0; x < w; x++) {
            const val = parseInt(row[x], 36);
            if (val > 0 && val < pal.length) {
              cx.fillStyle = pal[val];
              cx.fillRect(offX + x, y, 1, 1);
            }
          }
        }
      }
      return { sheet: cv, count: cnt, w, h };
    }

    const catSkinModels = CAT_SKINS.map(sk => ({
      body: buildSliceSheet(CAT_BODY_DATA, sk.pal),
      paw: buildSliceSheet(PAW_DATA, sk.pal)
    }));

    const chickenModel = buildSliceSheet(CHICKEN_DATA.slices, CHICKEN_DATA.palette);

    const hatModels = {};
    for (const h of HAT_PRESETS) {
      if (h.id !== 'none' && HATS_DATA[h.id]) {
        hatModels[h.id] = buildSliceSheet(HATS_DATA[h.id], h.pal);
      }
    }

    const propModels = {};
    for (const [key, entry] of Object.entries(PROPS_DATA)) {
      propModels[key] = buildSliceSheet(entry.slices, entry.palette);
    }

    // =========================================================================
    // 3. ÁUDIO RETRO (WebAudio Sintetizado)
    // =========================================================================
    let audioCtx = null;
    function playTone(freq, endFreq, dur, type = 'sine', gainVal = 0.08) {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(Math.max(40, endFreq), audioCtx.currentTime + dur);
        g.gain.setValueAtTime(gainVal, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
        osc.connect(g);
        g.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + dur);
      } catch (e) {}
    }
    const sfxJump = () => playTone(310, 620, 0.14, 'triangle', 0.08);
    const sfxLand = () => playTone(160, 85, 0.07, 'sine', 0.05);
    const sfxBlocked = () => playTone(180, 110, 0.11, 'square', 0.04);
    const sfxFish = () => {
      playTone(523.25, 783.99, 0.12, 'triangle', 0.09);
      setTimeout(() => playTone(783.99, 1046.5, 0.18, 'triangle', 0.09), 90);
    };
    const sfxBiome = () => {
      playTone(440, 659.25, 0.12, 'sine', 0.07);
      setTimeout(() => playTone(659.25, 880, 0.16, 'sine', 0.07), 85);
    };
    const sfxMeow = () => playTone(660, 490, 0.16, 'sine', 0.07);
    const sfxChop = () => {
      playTone(210, 75, 0.09, 'triangle', 0.10);
      setTimeout(() => playTone(140, 55, 0.07, 'square', 0.05), 20);
    };
    const sfxCrumble = () => {
      playTone(135, 48, 0.18, 'sawtooth', 0.09);
      setTimeout(() => playTone(95, 40, 0.22, 'triangle', 0.08), 55);
    };
    const sfxShallowStep = () => {
      playTone(420, 240, 0.055, 'sine', 0.035);
      playTone(680, 380, 0.04, 'triangle', 0.02);
    };

