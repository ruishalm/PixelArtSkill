const CHICKEN_DATA = window.__CHICKEN_VOXEL_DATA__;

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
function createPartCanvas(sliceGrid, filterFn) {
  const sc = document.createElement('canvas');
  sc.width = CHICKEN_DATA.width;
  sc.height = CHICKEN_DATA.height;
  const sctx = sc.getContext('2d');
  sctx.imageSmoothingEnabled = false;
  const idata = sctx.createImageData(CHICKEN_DATA.width, CHICKEN_DATA.height);
  const data = idata.data;

  function hexToRgba(hex) {
    if (hex.startsWith('rgba')) return [0, 0, 0, 0];
    const num = parseInt(hex.slice(1), 16);
    return [(num >> 16) & 255, (num >> 8) & 255, num & 255, 255];
  }

  for (let y = 0; y < CHICKEN_DATA.height; y++) {
    for (let x = 0; x < CHICKEN_DATA.width; x++) {
      if (filterFn && !filterFn(x, y)) continue;
      const cIdx = sliceGrid[y][x];
      if (cIdx > 0) {
        const rgba = hexToRgba(CHICKEN_DATA.palette[cIdx]);
        const pIdx = (y * CHICKEN_DATA.width + x) * 4;
        data[pIdx]     = rgba[0];
        data[pIdx + 1] = rgba[1];
        data[pIdx + 2] = rgba[2];
        data[pIdx + 3] = rgba[3];
      }
    }
  }
  sctx.putImageData(idata, 0, 0);
  return sc;
}

// Slices 0 a 3: Patas separadas (Esq y < 12, Dir y >= 12)
const legLCanvases = [];
const legRCanvases = [];
for (let i = 0; i <= 3; i++) {
  legLCanvases.push(createPartCanvas(CHICKEN_DATA.slices[i], (x, y) => y < 12));
  legRCanvases.push(createPartCanvas(CHICKEN_DATA.slices[i], (x, y) => y >= 12));
}

// Slices 4 a 15: Corpo e Cabeça
const upperCanvases = [];
for (let i = 4; i < CHICKEN_DATA.slices.length; i++) {
  upperCanvases.push(createPartCanvas(CHICKEN_DATA.slices[i], null));
}

// Estados da Galinha
let currentAnim = 'walk';
let animTime = 0;
let turn = 0.8;
let autoSpin = true;
let scale = 2.5;
let squash = 0.65;

// Web Audio API para Cluck / Cocoricó
let audioCtx = null;
function playCluckSound(pitchMult = 1.0) {
  try {
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
  } catch (e) {}
}

function playPeckSound() {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(260, now);
    osc.frequency.exponentialRampToValueAtTime(65, now + 0.04);
    gain.gain.setValueAtTime(0.28, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.05);
  } catch (e) {}
}

function render() {
  animTime += 0.08;
  if (autoSpin) turn += 0.012;

  lowCtx.clearRect(0, 0, lowCanvas.width, lowCanvas.height);

  const cx = lowCanvas.width / 2;
  const cy = lowCanvas.height / 2 + 38;

  let legLOffX = 0, legLLiftZ = 0;
  let legROffX = 0, legRLiftZ = 0;
  let bodyBobZ = 0, rollWobble = 0;
  let headOffX = 0, headOffZ = 0;

  if (currentAnim === 'walk') {
    const walkCycle = animTime * 3.0;
    const swingDist = 3.6;

    const lStep = Math.sin(walkCycle);
    legLOffX = lStep * swingDist;
    legLLiftZ = (lStep > 0) ? Math.sin(lStep * Math.PI) * 2.2 : 0;

    const rStep = -Math.sin(walkCycle);
    legROffX = rStep * swingDist;
    legRLiftZ = (rStep > 0) ? Math.sin(rStep * Math.PI) * 2.2 : 0;

    bodyBobZ = Math.abs(Math.sin(walkCycle)) * 1.2;
    rollWobble = Math.cos(walkCycle * 0.5) * 0.05;

    headOffX = Math.sin(walkCycle) * 2.0;
  } else if (currentAnim === 'peck') {
    legLOffX = 0; legLLiftZ = 0;
    legROffX = 0; legRLiftZ = 0;
    bodyBobZ = 0; rollWobble = 0;

    const cycle = (animTime * 2.4) % (Math.PI * 2);

    if (cycle < Math.PI * 0.35) {
      const p = Math.sin((cycle / (Math.PI * 0.35)) * Math.PI * 0.5);
      headOffX = p * 4.5;
      headOffZ = -p * 1.5;
    } else if (cycle < Math.PI * 0.70) {
      const p = (cycle - Math.PI * 0.35) / (Math.PI * 0.35);
      const pSin = Math.sin(p * Math.PI * 0.5);
      headOffX = 4.5 + pSin * 0.8;
      headOffZ = -1.5 - pSin * 5.0;
      if (p > 0.85 && Math.random() < 0.28) {
        playPeckSound();
      }
    } else if (cycle < Math.PI * 1.10) {
      const p = (cycle - Math.PI * 0.70) / (Math.PI * 0.40);
      headOffX = 5.3 * (1 - p * 0.3);
      headOffZ = -6.5 * (1 - p);
    } else {
      const p = (cycle - Math.PI * 1.10) / (Math.PI * 0.90);
      headOffX = 3.7 * (1 - p);
      headOffZ = 0;
    }
  } else if (currentAnim === 'flap') {
    bodyBobZ = Math.max(0, Math.sin(animTime * 2.8)) * 8.0;
    legLLiftZ = bodyBobZ;
    legRLiftZ = bodyBobZ;
    headOffX = Math.sin(animTime * 4.0) * 1.5;
  } else if (currentAnim === 'loaf') {
    bodyBobZ = -3.8;
  }

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

  // 1. Renderiza Patas (Z=0 a 3) com projeção isométrica verdadeira
  if (currentAnim !== 'loaf') {
    for (let i = 0; i <= 3; i++) {
      const zL = i + legLLiftZ;
      const sLx = cx + (legLOffX * Math.cos(turn)) * scale;
      const sLy = cy + (legLOffX * Math.sin(turn)) * scale * squash - (zL * zStep) * squash;
      lowCtx.save();
      lowCtx.translate(sLx, sLy);
      lowCtx.scale(1, squash);
      lowCtx.rotate(turn);
      lowCtx.drawImage(legLCanvases[i], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();

      const zR = i + legRLiftZ;
      const sRx = cx + (legROffX * Math.cos(turn)) * scale;
      const sRy = cy + (legROffX * Math.sin(turn)) * scale * squash - (zR * zStep) * squash;
      lowCtx.save();
      lowCtx.translate(sRx, sRy);
      lowCtx.scale(1, squash);
      lowCtx.rotate(turn);
      lowCtx.drawImage(legRCanvases[i], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();
    }
  }

  // 2. Renderiza Corpo e Asas (Z=4 a 9)
  for (let i = 4; i <= 9; i++) {
    const z = i + bodyBobZ;
    const sX = cx;
    const sY = cy - (z * zStep) * squash;
    lowCtx.save();
    lowCtx.translate(sX, sY);
    lowCtx.scale(1, squash);
    lowCtx.rotate(turn + rollWobble);
    lowCtx.drawImage(upperCanvases[i - 4], -sw / 2, -sh / 2, sw, sh);
    lowCtx.restore();
  }

  // 3. Renderiza Cabeça Sólida (Z=10 a 15) como um bloco redondo e fofo sem distorção
  for (let i = 10; i < CHICKEN_DATA.slices.length; i++) {
    const z = i + bodyBobZ + headOffZ;
    const sX = cx + (headOffX * Math.cos(turn)) * scale;
    const sY = cy + (headOffX * Math.sin(turn)) * scale * squash - (z * zStep) * squash;

    lowCtx.save();
    lowCtx.translate(sX, sY);
    lowCtx.scale(1, squash);
    lowCtx.rotate(turn + rollWobble);
    lowCtx.drawImage(upperCanvases[i - 4], -sw / 2, -sh / 2, sw, sh);
    lowCtx.restore();
  }

  // Grãozinhos de milho no chão quando ciscando
  if (currentAnim === 'peck') {
    const seedDist = (CHICKEN_DATA.width / 2 + 3) * scale;
    const seedX = cx + seedDist * Math.cos(turn);
    const seedY = cy + seedDist * Math.sin(turn) * squash + 4;
    lowCtx.fillStyle = '#F59E0B';
    lowCtx.fillRect(seedX - 2, seedY - 1, 3, 2);
    lowCtx.fillRect(seedX + 4, seedY + 2, 2, 2);
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

  requestAnimationFrame(render);
}

let isDragging = false;
let lastMouseX = 0;

canvas.addEventListener('pointerdown', (e) => {
  isDragging = true;
  lastMouseX = e.clientX;
  autoSpin = false;
  document.getElementById('btnAutoSpin').classList.remove('active');
  playCluckSound(0.9 + Math.random() * 0.3);
});

window.addEventListener('pointermove', (e) => {
  if (isDragging) {
    const dx = e.clientX - lastMouseX;
    lastMouseX = e.clientX;
    turn += dx * 0.02;
  }
});

window.addEventListener('pointerup', () => {
  isDragging = false;
});

canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  scale = Math.max(1.2, Math.min(3.8, scale - e.deltaY * 0.002));
  document.getElementById('zoomSlider').value = scale;
});

const animBtns = {
  walk: document.getElementById('btnWalk'),
  peck: document.getElementById('btnPeck'),
  flap: document.getElementById('btnFlap'),
  loaf: document.getElementById('btnLoaf')
};

function setAnim(name) {
  currentAnim = name;
  Object.keys(animBtns).forEach(k => animBtns[k].classList.toggle('active', k === name));
  if (name === 'flap') playCluckSound(1.25);
  else if (name === 'peck') playPeckSound();
  else if (name === 'walk') playCluckSound(1.0);
}

animBtns.walk.addEventListener('click', () => setAnim('walk'));
animBtns.peck.addEventListener('click', () => setAnim('peck'));
animBtns.flap.addEventListener('click', () => setAnim('flap'));
animBtns.loaf.addEventListener('click', () => setAnim('loaf'));

const btnAutoSpin = document.getElementById('btnAutoSpin');
btnAutoSpin.addEventListener('click', () => {
  autoSpin = !autoSpin;
  btnAutoSpin.classList.toggle('active', autoSpin);
});

document.getElementById('btnSound').addEventListener('click', () => {
  playCluckSound(0.85 + Math.random() * 0.35);
});

document.getElementById('zoomSlider').addEventListener('input', (e) => {
  scale = parseFloat(e.target.value);
});

document.getElementById('tiltSlider').addEventListener('input', (e) => {
  squash = parseFloat(e.target.value);
});

render();
