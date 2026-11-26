    // =========================================================================
    // ENGINE: CONSTRUTOR DE SLICE SHEETS (Base-36 / RLE) & ÁUDIO RETRO
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
