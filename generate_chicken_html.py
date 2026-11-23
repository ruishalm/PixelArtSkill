"""
Gera o visualizador independente da Galinha 3D (chicken-3d.html)
Zero dependências externas, puro HTML5 Canvas 2D + Sprite Stacking + Web Audio API.
Refinamentos:
1. Andando: Perninhas se movem alternadas pra frente e pra trás e levantam o pezinho!
2. Ciscando: Corpo e pés 100% PARADINHOS! Cabeça vai pra frente, pra baixo, sobe e volta!
3. Chocando: Mantido perfeito!
"""
import json

with open('chicken_slices.json', 'r', encoding='utf-8') as f:
    chicken_data = json.load(f)

chicken_json_str = json.dumps(chicken_data)

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Galinha Cocoricó 3D 🐔 — Sprite Stacking Pixel Art</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
    }}
    body {{
      background: radial-gradient(circle at 50% 40%, #FFFDF9 0%, #F5EDE0 100%);
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #3B2A20;
      overflow: hidden;
    }}
    .app-container {{
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .canvas-card {{
      position: relative;
      background: #FDFBF7;
      border: 3px solid #E8D9C5;
      border-radius: 24px;
      box-shadow: 0 20px 50px rgba(59, 42, 32, 0.12), 0 4px 12px rgba(0,0,0,0.04);
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    canvas {{
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      border-radius: 18px;
      background: radial-gradient(circle at 50% 50%, #FAF8F5 0%, #EFE8DE 100%);
      cursor: grab;
      touch-action: none;
    }}
    canvas:active {{
      cursor: grabbing;
    }}
    .header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 4px 8px 14px;
    }}
    .title-group {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .title-group h1 {{
      font-size: 20px;
      font-weight: 800;
      color: #3B2A20;
      letter-spacing: -0.3px;
    }}
    .tag {{
      background: #FEF3C7;
      color: #D97706;
      border: 1px solid #FDE68A;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 12px;
    }}
    .nav-btn {{
      background: #EDE4D6;
      border: 1px solid #D9C8B4;
      color: #5C4333;
      padding: 6px 14px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }}
    .nav-btn:hover {{
      background: #E2D5C3;
      transform: translateY(-1px);
    }}
    .controls {{
      margin-top: 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      max-width: 580px;
    }}
    .btn {{
      background: #FFFFFF;
      border: 2px solid #E4D5C3;
      color: #4A3525;
      padding: 8px 16px;
      border-radius: 14px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      transition: all 0.15s ease;
    }}
    .btn:hover {{
      background: #FDF8F2;
      border-color: #D4A373;
      transform: translateY(-2px);
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }}
    .btn:active {{
      transform: translateY(0);
    }}
    .btn.active {{
      background: #D97706;
      color: #FFFFFF;
      border-color: #B45309;
      box-shadow: 0 4px 12px rgba(217, 119, 6, 0.35);
    }}
    .btn-sound {{
      background: #FEE2E2;
      border-color: #FCA5A5;
      color: #DC2626;
    }}
    .btn-sound:hover {{
      background: #FEE2E2;
      border-color: #EF4444;
    }}
    .slider-row {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-top: 12px;
      font-size: 12px;
      font-weight: 700;
      color: #7A5C45;
    }}
    .slider-row input[type="range"] {{
      accent-color: #D97706;
      cursor: pointer;
    }}
    .hint {{
      margin-top: 10px;
      font-size: 11px;
      color: #9C8270;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
  </style>
</head>
<body>

  <div class="app-container">
    <div class="canvas-card">
      <div class="header">
        <div class="title-group">
          <h1>🐔 Galinha Cocoricó 3D</h1>
          <span class="tag">Sprite Stacking (16 Slices)</span>
        </div>
        <a href="index.html" class="nav-btn">🏠 Voltar ao Quarto</a>
      </div>

      <canvas id="viewCanvas" width="480" height="420"></canvas>

      <div class="controls">
        <button id="btnWalk" class="btn active">🚶 Andando</button>
        <button id="btnPeck" class="btn">🌾 Ciscando</button>
        <button id="btnFlap" class="btn">🪽 Bater Asas</button>
        <button id="btnLoaf" class="btn">🥚 Chocando</button>
        <button id="btnAutoSpin" class="btn active">🔄 Girar</button>
        <button id="btnSound" class="btn btn-sound">🔊 Có-có-ró-có!</button>
      </div>

      <div class="slider-row">
        <span>🔍 Zoom:</span>
        <input type="range" id="zoomSlider" min="1.2" max="3.8" step="0.1" value="2.5">
        <span>📐 Inclinação:</span>
        <input type="range" id="tiltSlider" min="0.4" max="0.9" step="0.05" value="0.65">
      </div>

      <div class="hint">
        <span>🖱️ Arraste para orbitar 360° • 📜 Scroll para zoom • Clique na galinha para cocoricó!</span>
      </div>
    </div>
  </div>

  <script>
    const CHICKEN_DATA = {chicken_json_str};

    const canvas = document.getElementById('viewCanvas');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    // Buffer interno de baixa resolução para pixel art perfeita
    const lowCanvas = document.createElement('canvas');
    lowCanvas.width = 240;
    lowCanvas.height = 210;
    const lowCtx = lowCanvas.getContext('2d');
    lowCtx.imageSmoothingEnabled = false;

    // Constrói os sprites pré-renderizados: Patas separadas (Esq/Dir), Corpo e Cabeça
    function createPartCanvas(sliceGrid, filterFn) {{
      const sc = document.createElement('canvas');
      sc.width = CHICKEN_DATA.width;
      sc.height = CHICKEN_DATA.height;
      const sctx = sc.getContext('2d');
      sctx.imageSmoothingEnabled = false;
      const idata = sctx.createImageData(CHICKEN_DATA.width, CHICKEN_DATA.height);
      const data = idata.data;

      function hexToRgba(hex) {{
        if (hex.startsWith('rgba')) return [0,0,0,0];
        const num = parseInt(hex.slice(1), 16);
        return [(num >> 16) & 255, (num >> 8) & 255, num & 255, 255];
      }}

      for (let y = 0; y < CHICKEN_DATA.height; y++) {{
        for (let x = 0; x < CHICKEN_DATA.width; x++) {{
          if (filterFn && !filterFn(x, y)) continue;
          const cIdx = sliceGrid[y][x];
          if (cIdx > 0) {{
            const rgba = hexToRgba(CHICKEN_DATA.palette[cIdx]);
            const pIdx = (y * CHICKEN_DATA.width + x) * 4;
            data[pIdx]     = rgba[0];
            data[pIdx + 1] = rgba[1];
            data[pIdx + 2] = rgba[2];
            data[pIdx + 3] = rgba[3];
          }}
        }}
      }}
      sctx.putImageData(idata, 0, 0);
      return sc;
    }}

    // Slices 0 a 3: Patas separadas (Esq y < 12, Dir y >= 12)
    const legLCanvases = [];
    const legRCanvases = [];
    for (let i = 0; i <= 3; i++) {{
      legLCanvases.push(createPartCanvas(CHICKEN_DATA.slices[i], (x, y) => y < 12));
      legRCanvases.push(createPartCanvas(CHICKEN_DATA.slices[i], (x, y) => y >= 12));
    }}

    // Slices 4 a 15: Corpo e Cabeça
    const upperCanvases = [];
    for (let i = 4; i < CHICKEN_DATA.slices.length; i++) {{
      upperCanvases.push(createPartCanvas(CHICKEN_DATA.slices[i], null));
    }}

    // Estados da Galinha
    let currentAnim = 'walk';
    let animTime = 0;
    let turn = 0.8;
    let autoSpin = true;
    let scale = 2.5;
    let squash = 0.65;

    // Web Audio API para Cluck / Cocoricó
    let audioCtx = null;
    function playCluckSound(pitchMult = 1.0) {{
      try {{
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const now = audioCtx.currentTime;

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';

        const baseF = 380 * pitchMult;
        osc.frequency.setValueAtTime(baseF, now);
        osc.frequency.exponentialRampToValueAtTime(baseF * 1.6, now + 0.05);
        osc.frequency.exponentialRampToValueAtTime(baseF * 0.7, now + 0.16);

        const filter = audioCtx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1400, now);

        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.22, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start(now);
        osc.stop(now + 0.19);
      }} catch(e) {{}}
    }}

    function playPeckSound() {{
      try {{
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(240, now);
        osc.frequency.exponentialRampToValueAtTime(70, now + 0.04);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
      }} catch(e) {{}}
    }}

    function render() {{
      animTime += 0.08;
      if (autoSpin) turn += 0.012;

      lowCtx.clearRect(0, 0, lowCanvas.width, lowCanvas.height);

      const cx = lowCanvas.width / 2;
      const cy = lowCanvas.height / 2 + 38;

      // Variáveis de animação desacopladas por membro
      let legLOffX = 0, legLLiftZ = 0;
      let legROffX = 0, legRLiftZ = 0;
      let bodyBobZ = 0, rollWobble = 0;
      let headOffX = 0, headOffZ = 0;

      if (currentAnim === 'walk') {{
        // 1. ANDANDO: Perninhas se movem alternadas e levantam do chão!
        const walkCycle = animTime * 3.0;
        const swingDist = 3.8;

        const lStep = Math.sin(walkCycle);
        legLOffX = lStep * swingDist;
        legLLiftZ = (lStep > 0) ? Math.sin(lStep * Math.PI) * 2.2 : 0;

        const rStep = -Math.sin(walkCycle);
        legROffX = rStep * swingDist;
        legRLiftZ = (rStep > 0) ? Math.sin(rStep * Math.PI) * 2.2 : 0;

        // Corpo dá leve balanço e quique
        bodyBobZ = Math.abs(Math.sin(walkCycle)) * 1.2;
        rollWobble = Math.cos(walkCycle * 0.5) * 0.05;

        // Cabeça dá bicadinhas rítmicas pra frente/trás acompanhando os passos
        headOffX = Math.sin(walkCycle) * 2.0;
        headOffZ = bodyBobZ;
      }} else if (currentAnim === 'peck') {{
        // 2. CISCANDO:
        // REGRA DE OURO: Corpo e pés ficam 100% PARADINHOS!
        legLOffX = 0; legLLiftZ = 0;
        legROffX = 0; legRLiftZ = 0;
        bodyBobZ = 0; rollWobble = 0;

        // Ciclo exato da cabeça: vai pra frente, pra baixo, sobe e volta!
        const cycle = (animTime * 2.2) % (Math.PI * 2);

        if (cycle < Math.PI * 0.35) {{
          // Fase 1: Cabeça vai pra frente
          const p = cycle / (Math.PI * 0.35);
          headOffX = Math.sin(p * Math.PI * 0.5) * 6.5;
          headOffZ = -Math.sin(p * Math.PI * 0.5) * 1.5;
        }} else if (cycle < Math.PI * 0.70) {{
          // Fase 2: Cabeça mergulha pra baixo rente ao chão (Bicada no chão "toc-toc"!)
          const p = (cycle - Math.PI * 0.35) / (Math.PI * 0.35);
          headOffX = 6.5 - p * 0.5;
          headOffZ = -1.5 - Math.sin(p * Math.PI * 0.5) * 8.2; // Chega a Z=-9.7 (no chão!)
          if (p > 0.85 && Math.random() < 0.25) {{
            playPeckSound();
          }}
        }} else if (cycle < Math.PI * 1.10) {{
          // Fase 3: Cabeça sobe de volta
          const p = (cycle - Math.PI * 0.70) / (Math.PI * 0.40);
          headOffX = 6.0 * (1 - p * 0.3);
          headOffZ = -9.7 * (1 - p); // Sobe de -9.7 até 0
        }} else {{
          // Fase 4: Cabeça volta pra posição inicial de repouso
          const p = (cycle - Math.PI * 1.10) / (Math.PI * 0.90);
          headOffX = 4.2 * (1 - Math.sin(p * Math.PI * 0.5));
          headOffZ = 0;
        }}
      }} else if (currentAnim === 'flap') {{
        // 3. BATER ASAS: pulinho animado
        bodyBobZ = Math.max(0, Math.sin(animTime * 2.8)) * 8.0;
        legLLiftZ = bodyBobZ;
        legRLiftZ = bodyBobZ;
        headOffX = Math.sin(animTime * 4.0) * 1.5;
      }} else if (currentAnim === 'loaf') {{
        // 4. CHOCANDO (PERFEITO!): pés somem, corpo repousa achatado
        bodyBobZ = -3.8;
      }}

      // Sombra projetada no chão
      lowCtx.save();
      lowCtx.translate(cx, cy + 4);
      lowCtx.scale(1, squash * 0.5);
      lowCtx.beginPath();
      const shadowR = Math.max(10, 26 - bodyBobZ * 0.6) * (scale / 2.5);
      lowCtx.arc(0, 0, shadowR, 0, Math.PI * 2);
      lowCtx.fillStyle = 'rgba(74, 46, 27, 0.22)';
      lowCtx.fill();
      lowCtx.restore();

      const zStep = 1.35 * scale;
      const sw = CHICKEN_DATA.width * scale;
      const sh = CHICKEN_DATA.height * scale;

      // 1. Renderiza Patas (Z=0 a 3) - apenas se não estiver chocando
      if (currentAnim !== 'loaf') {{
        for (let i = 0; i <= 3; i++) {{
          // Pata Esquerda
          const zL = i + legLLiftZ;
          const sLx = cx + (legLOffX * Math.cos(turn)) * scale;
          const sLy = cy - (zL * zStep) * squash;
          lowCtx.save();
          lowCtx.translate(sLx, sLy);
          lowCtx.scale(1, squash);
          lowCtx.rotate(turn);
          lowCtx.drawImage(legLCanvases[i], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();

          // Pata Direita
          const zR = i + legRLiftZ;
          const sRx = cx + (legROffX * Math.cos(turn)) * scale;
          const sRy = cy - (zR * zStep) * squash;
          lowCtx.save();
          lowCtx.translate(sRx, sRy);
          lowCtx.scale(1, squash);
          lowCtx.rotate(turn);
          lowCtx.drawImage(legRCanvases[i], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();
        }}
      }}

      // 2. Renderiza Corpo e Asas (Z=4 a 9)
      for (let i = 4; i <= 9; i++) {{
        const z = i + bodyBobZ;
        const sX = cx;
        const sY = cy - (z * zStep) * squash;
        lowCtx.save();
        lowCtx.translate(sX, sY);
        lowCtx.scale(1, squash);
        lowCtx.rotate(turn + rollWobble);
        lowCtx.drawImage(upperCanvases[i - 4], -sw / 2, -sh / 2, sw, sh);
        lowCtx.restore();
      }}

      // 3. Renderiza Pescoço, Cabeça, Bico e Crista (Z=10 a 15)
      for (let i = 10; i < CHICKEN_DATA.slices.length; i++) {{
        const headWeight = (i === 10) ? 0.65 : 1.0;
        const z = i + bodyBobZ + headOffZ * headWeight;
        const sX = cx + (headOffX * headWeight * Math.cos(turn)) * scale;
        const sY = cy - (z * zStep) * squash;
        lowCtx.save();
        lowCtx.translate(sX, sY);
        lowCtx.scale(1, squash);
        lowCtx.rotate(turn + rollWobble);
        lowCtx.drawImage(upperCanvases[i - 4], -sw / 2, -sh / 2, sw, sh);
        lowCtx.restore();
      }}

      // Grãozinhos de milho no chão quando ciscando
      if (currentAnim === 'peck') {{
        const seedDist = (CHICKEN_DATA.width / 2 + 4) * scale;
        const seedX = cx + seedDist * Math.cos(turn);
        const seedY = cy + seedDist * Math.sin(turn) * squash + 4;
        lowCtx.fillStyle = '#F59E0B';
        lowCtx.fillRect(seedX - 2, seedY - 1, 3, 2);
        lowCtx.fillRect(seedX + 4, seedY + 2, 2, 2);
      }}

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

      requestAnimationFrame(render);
    }}

    let isDragging = false;
    let lastMouseX = 0;

    canvas.addEventListener('pointerdown', (e) => {{
      isDragging = true;
      lastMouseX = e.clientX;
      autoSpin = false;
      document.getElementById('btnAutoSpin').classList.remove('active');
      playCluckSound(0.9 + Math.random() * 0.3);
    }});

    window.addEventListener('pointermove', (e) => {{
      if (isDragging) {{
        const dx = e.clientX - lastMouseX;
        lastMouseX = e.clientX;
        turn += dx * 0.02;
      }}
    }});

    window.addEventListener('pointerup', () => {{
      isDragging = false;
    }});

    canvas.addEventListener('wheel', (e) => {{
      e.preventDefault();
      scale = Math.max(1.2, Math.min(3.8, scale - e.deltaY * 0.002));
      document.getElementById('zoomSlider').value = scale;
    }});

    const animBtns = {{
      walk: document.getElementById('btnWalk'),
      peck: document.getElementById('btnPeck'),
      flap: document.getElementById('btnFlap'),
      loaf: document.getElementById('btnLoaf')
    }};

    function setAnim(name) {{
      currentAnim = name;
      Object.keys(animBtns).forEach(k => animBtns[k].classList.toggle('active', k === name));
      if (name === 'flap') playCluckSound(1.25);
      else if (name === 'peck') playPeckSound();
      else if (name === 'walk') playCluckSound(1.0);
    }}

    animBtns.walk.addEventListener('click', () => setAnim('walk'));
    animBtns.peck.addEventListener('click', () => setAnim('peck'));
    animBtns.flap.addEventListener('click', () => setAnim('flap'));
    animBtns.loaf.addEventListener('click', () => setAnim('loaf'));

    const btnAutoSpin = document.getElementById('btnAutoSpin');
    btnAutoSpin.addEventListener('click', () => {{
      autoSpin = !autoSpin;
      btnAutoSpin.classList.toggle('active', autoSpin);
    }});

    document.getElementById('btnSound').addEventListener('click', () => {{
      playCluckSound(0.85 + Math.random() * 0.35);
    }});

    document.getElementById('zoomSlider').addEventListener('input', (e) => {{
      scale = parseFloat(e.target.value);
    }});

    document.getElementById('tiltSlider').addEventListener('input', (e) => {{
      squash = parseFloat(e.target.value);
    }});

    render();
  </script>
</body>
</html>
"""

with open('chicken-3d.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('chicken-3d.html atualizado com perninhas e ciscada perfeitas!')
