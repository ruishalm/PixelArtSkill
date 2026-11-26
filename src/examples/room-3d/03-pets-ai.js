// --- ÁUDIO RETRO PROCEDURAL (Web Audio API - Zero assets externos!) ---
function playMeowSound() {
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    const now = audioCtx.currentTime;

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    // Miau fofinho com modulação de frequência (460Hz -> 760Hz -> 540Hz)
    osc.type = 'sine';
    osc.frequency.setValueAtTime(460, now);
    osc.frequency.exponentialRampToValueAtTime(760, now + 0.12);
    osc.frequency.exponentialRampToValueAtTime(540, now + 0.32);

    // Envelope acústico macio
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.exponentialRampToValueAtTime(0.20, now + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.15, now + 0.22);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

    // Purr vibrato LFO
    const lfo = audioCtx.createOscillator();
    const lfoGain = audioCtx.createGain();
    lfo.frequency.value = 22;
    lfoGain.gain.value = 16;
    lfo.connect(osc.frequency);
    lfo.start(now);
    lfo.stop(now + 0.35);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.35);
  } catch (err) {}
}

function triggerPetReactions(cat) {
  if (!cat) return;
  playMeowSound();

  // Coraçõezinhos flutuantes
  const p = project(cat.x, cat.y, 24);
  for (let i = 0; i < 8; i++) {
    hearts.push({
      x: p.x + (Math.random() * 28 - 14),
      y: p.y - (Math.random() * 20),
      alpha: 1.0
    });
  }

  // Balão de fala carinhoso
  const phrases = ['Purrr... ♥', 'Miau! ♪', 'Nyaa~ ✨', 'Awnn! ♥', 'Meow~ 💕'];
  const text = phrases[Math.floor(Math.random() * phrases.length)];
  cat.speech = { text, timer: 120 };

  // Reação corporal: 50% de chance de rolar e mostrar a barriguinha!
  if (!cat.forcedPosture || cat.forcedPosture === 'auto') {
    if (Math.random() < 0.55) {
      cat.posture = 'belly';
      cat.bellyTimer = 180; // 3 segundos curtindo carinho na barriga
    } else {
      cat.posture = 'sit';
      cat.stateTimer = 120;
    }
  }
}

function drawLoafZzz(cat) {
  const p = project(cat.x, cat.y, 22 * cat.scale);
  const time = (cat.idleTimer || 0);
  const zzzOffset = (time * 1.5) % 3;
  const alpha = Math.max(0, 1 - (zzzOffset / 3));

  lowCtx.save();
  lowCtx.fillStyle = `rgba(100, 130, 180, ${alpha * 0.85})`;
  lowCtx.font = 'bold 8px monospace';
  lowCtx.fillText('Z', p.x + 8 + zzzOffset * 2, p.y - zzzOffset * 6);
  if (zzzOffset > 0.8) {
    lowCtx.fillText('z', p.x + 13 + (zzzOffset - 0.8) * 3, p.y - 4 - (zzzOffset - 0.8) * 8);
  }
  if (zzzOffset > 1.6) {
    lowCtx.fillText('z', p.x + 18 + (zzzOffset - 1.6) * 4, p.y - 8 - (zzzOffset - 1.6) * 10);
  }
  lowCtx.restore();
}

function drawCatSpeech(cat) {
  if (!cat.speech) return;
  if (typeof cat.speech === 'string') {
    cat.speech = { text: cat.speech, timer: 160 };
  }
  if (cat.speech.timer <= 0) {
    cat.speech = null;
    return;
  }
  cat.speech.timer--;

  const p = project(cat.x, cat.y, 26 * cat.scale);
  const text = cat.speech.text;
  if (!text || text === 'undefined') return;

  lowCtx.save();
  lowCtx.font = 'bold 9px sans-serif';
  const tw = lowCtx.measureText(text).width;
  const bw = tw + 10;
  const bh = 14;
  const bx = Math.round(p.x - bw / 2);
  const by = Math.round(p.y - 18);

  // Balão de fala pixel art
  lowCtx.fillStyle = '#FFFFFF';
  lowCtx.strokeStyle = '#3B2219';
  lowCtx.lineWidth = 1;
  lowCtx.fillRect(bx, by, bw, bh);
  lowCtx.strokeRect(bx, by, bw, bh);

  // Rabicho do balão
  lowCtx.fillStyle = '#FFFFFF';
  lowCtx.beginPath();
  lowCtx.moveTo(p.x - 3, by + bh);
  lowCtx.lineTo(p.x, by + bh + 4);
  lowCtx.lineTo(p.x + 3, by + bh);
  lowCtx.fill();

  lowCtx.fillStyle = '#E63946';
  lowCtx.fillText(text, bx + 5, by + 10);
  lowCtx.restore();
}

// --- GATINHO 3D COM PATINHAS ARTICULADAS E ANIMAÇÃO PROCEDURAL ---
function drawCat(cat, baseLiftZ = 0) {
  const posture = cat.forcedPosture || cat.posture || (cat.isWalking ? 'walk' : 'stand');
  const t = cat.walkCycle || 0;
  const isWalking = (posture === 'walk' || cat.isWalking) && (!isDraggingItem || selectedItem !== cat);

  const cosA = Math.cos(cat.selfAngle);
  const sinA = Math.sin(cat.selfAngle);

  function renderPaw(lx, ly, lift, stride, pawZ = 0, angleOffset = 0) {
    const wx = cat.x + lx * cosA - (ly + stride) * sinA;
    const wy = cat.y + lx * sinA + (ly + stride) * cosA;
    const wz = baseLiftZ + lift + pawZ;
    drawStackObject(catSkinModels[currentCatSkin].paw, wx, wy, wz, cat.selfAngle + angleOffset, cat.scale);
  }

  function renderHat(headZ, headPitchOffset = 0, rollOffset = 0) {
    if (!cat.hat || cat.hat === 'none') return;
    const hatModel = HATS[cat.hat];
    if (!hatModel) return;
    const hx = cat.x - (4.5 + headPitchOffset) * sinA;
    const hy = cat.y + (4.5 + headPitchOffset) * cosA;
    const hz = baseLiftZ + (headZ - 2.8) * cat.scale; // Ajuste fino: chapéu pousado perfeitamente no cocuruto entre as orelhinhas
    drawStackObject(hatModel, hx, hy, hz, cat.selfAngle + rollOffset, cat.scale);
  }

  if (posture === 'belly') {
    // === MOSTRAR A BARRIGUINHA (BELLY ROLL) COM CABECINHA DOBRADA OLHANDO PRA BARRIGA ===
    // O corpo apoia suavemente na espinha (chão Z=0) e a cabeça curva para frente sem encostar orelhas no chão!
    const bellyWiggle = Math.sin((cat.idleTimer || 0) * 4) * 0.05;
    drawStackObject(catSkinModels[currentCatSkin].belly, cat.x, cat.y, baseLiftZ + 0.5, cat.selfAngle + bellyWiggle, cat.scale);

    // 4 patinhas fofas abanando no ar acima da barriguinha!
    const pawTime = (cat.idleTimer || 0) * 5;
    const pBL = Math.sin(pawTime) * 1.5;
    const pBR = Math.sin(pawTime + 1.2) * 1.5;
    const pFL = Math.sin(pawTime + 2.4) * 1.5;
    const pFR = Math.sin(pawTime + 3.6) * 1.5;

    renderPaw(-4.0, -4.0, 0, 0, 7.5 + pBL, 0.4);
    renderPaw( 3.0, -4.0, 0, 0, 7.5 + pBR, -0.4);
    renderPaw(-4.0,  2.5, 0, 0, 8.0 + pFL, 0.3);
    renderPaw( 3.0,  2.5, 0, 0, 8.0 + pFR, -0.3);

    // Chapéu na cabecinha dobrada (na testa/orelhas voltadas para trás)
    renderHat(7.2, 3.5, 0.2);

  } else if (posture === 'loaf') {
    // === DEITAR / PÃOZINHO (LOAF) ===
    // 4 patinhas 100% escondidas sob o corpo, corpo no chão
    const loafBreathe = Math.sin((cat.idleTimer || 0) * 1.8) * 0.35;
    drawStackObject(catSkinModels[currentCatSkin].body, cat.x, cat.y, baseLiftZ - 2.2 + loafBreathe, cat.selfAngle, cat.scale);
    renderHat(12.0 + loafBreathe);
    drawLoafZzz(cat);

  } else if (posture === 'sit') {
    // === SENTAR (SIT) ===
    // Patas dianteiras apoiadas, traseiras recolhidas, traseira rebaixada
    renderPaw(-4.5, 3.5, 0, 0);
    renderPaw( 3.5, 3.5, 0, 0);
    const sitBreathe = Math.sin((cat.idleTimer || 0) * 2.0) * 0.3;
    drawStackObject(catSkinModels[currentCatSkin].body, cat.x, cat.y, baseLiftZ - 1.2 + sitBreathe, cat.selfAngle, cat.scale);
    renderHat(13.2 + sitBreathe);

  } else {
    // === ANDAR OU EM PÉ (WALK / STAND) ===
    const liftFL = isWalking ? Math.max(0, Math.sin(t) * 3.5) : 0;
    const strideFL = isWalking ? -Math.cos(t) * 2.5 : 0;

    const liftBR = isWalking ? Math.max(0, Math.sin(t + 0.3) * 3.5) : 0;
    const strideBR = isWalking ? -Math.cos(t + 0.3) * 2.5 : 0;

    const liftFR = isWalking ? Math.max(0, Math.sin(t + Math.PI) * 3.5) : 0;
    const strideFR = isWalking ? -Math.cos(t + Math.PI) * 2.5 : 0;

    const liftBL = isWalking ? Math.max(0, Math.sin(t + Math.PI + 0.3) * 3.5) : 0;
    const strideBL = isWalking ? -Math.cos(t + Math.PI + 0.3) * 2.5 : 0;

    const bodyBob = isWalking ? Math.abs(Math.sin(t * 2)) * 0.8 : Math.sin((cat.idleTimer || 0) * 2.2) * 0.4;
    const bodyRoll = isWalking ? Math.sin(t) * 0.04 : 0;

    renderPaw(-4.5, -7.5, liftBL, strideBL); // Traseira esquerda
    renderPaw( 3.5, -7.5, liftBR, strideBR); // Traseira direita
    renderPaw(-4.5,  3.5, liftFL, strideFL); // Dianteira esquerda
    renderPaw( 3.5,  3.5, liftFR, strideFR); // Dianteira direita

    drawStackObject(catSkinModels[currentCatSkin].body, cat.x, cat.y, baseLiftZ + bodyBob, cat.selfAngle + bodyRoll, cat.scale);
    renderHat(14.8 + bodyBob, 0, bodyRoll);
  }

  drawCatSpeech(cat);
}

// Funções Auxiliares de Restrição para Plataformas (Mesa e Prateleira)
function constrainToDesk(x, y, margin = 4) {
  const desk = items.find(it => it.id === 'desk');
  if (!desk) return { x, y };
  const cosD = Math.cos(desk.selfAngle);
  const sinD = Math.sin(desk.selfAngle);
  const rwx = x - desk.x;
  const rwy = y - desk.y;
  let localX =  rwx * cosD + rwy * sinD;
  let localY = -rwx * sinD + rwy * cosD;
  const limitX = 36 - margin;
  const limitY = 14 - margin;
  localX = Math.max(-limitX, Math.min(limitX, localX));
  localY = Math.max(-limitY, Math.min(limitY, localY));
  return {
    x: desk.x + localX * cosD - localY * sinD,
    y: desk.y + localX * sinD + localY * cosD
  };
}

function constrainToShelf(y, margin = 6) {
  const shelf = items.find(it => it.id === 'shelf');
  if (!shelf) return { x: -ROOM_R + 9, y };
  const minY = shelf.y - shelf.length / 2 + margin;
  const maxY = shelf.y + shelf.length / 2 - margin;
  return {
    x: -ROOM_R + 9,
    y: Math.max(minY, Math.min(maxY, y))
  };
}

// Sistema de Colisão e Navegação do Gatinho com Móveis e Paredes
function checkCatCollision(nx, ny) {
  // 1. Limites com as paredes do quarto
  const wallLimit = ROOM_R - 16;
  nx = Math.max(-wallLimit, Math.min(wallLimit, nx));
  ny = Math.max(-wallLimit, Math.min(wallLimit, ny));

  const catRad = 12;

  // 2. Colisão com a Mesa de Estudo Ampliada (80x36, caixa AABB orientada)
  const desk = items.find(it => it.id === 'desk');
  if (desk && desk.visible !== false) {
    const isRot = (desk.selfAngle === Math.PI / 2 || desk.selfAngle === Math.PI * 1.5);
    const halfW = (isRot ? 20 : 42) + catRad;
    const halfH = (isRot ? 42 : 20) + catRad;
    if (Math.abs(nx - desk.x) < halfW && Math.abs(ny - desk.y) < halfH) {
      const overlapX = halfW - Math.abs(nx - desk.x);
      const overlapY = halfH - Math.abs(ny - desk.y);
      if (overlapX < overlapY) {
        nx = desk.x + (nx > desk.x ? halfW : -halfW);
      } else {
        ny = desk.y + (ny > desk.y ? halfH : -halfH);
      }
    }
  }

  // 3. Colisão com outros móveis de chão (Torre de Gato, Caminha, Planta, etc.)
  const floorObstacles = items.filter(it => 
    it.visible !== false && 
    !it.isCat && 
    !it.isWallItem && 
    it.surface !== 'desk' && 
    it.surface !== 'shelf' && 
    it.id !== 'desk'
  );

  for (const obs of floorObstacles) {
    const obsRad = (obs.radius ? obs.radius * 0.75 : 16) + catRad;
    const dx = nx - obs.x;
    const dy = ny - obs.y;
    const dist = Math.hypot(dx, dy);
    if (dist < obsRad && dist > 0.001) {
      const push = obsRad - dist;
      nx += (dx / dist) * push;
      ny += (dy / dist) * push;
    }
  }

  return { x: nx, y: ny };
}


// --- GALINHA POPÓ 3D ARTICULADA (Andar, Rebolado, Ciscar e Chocar) ---
function drawChicken(chk, baseLiftZ = 0) {
  const t = chk.animTime || 0;
  const isWalking = chk.isWalking && (!isDraggingItem || selectedItem !== chk);
  const isPecking = (chk.state === 'peck') && (!isDraggingItem || selectedItem !== chk);
  const isBrooding = (chk.state === 'brood');
  const chkAngle = chk.selfAngle + turn;

  const isBabyChick = (chk.id === 'chick');
  const activeLegL = isBabyChick ? chickLegL : chickenLegL;
  const activeLegR = isBabyChick ? chickLegR : chickenLegR;
  const activeUpper = isBabyChick ? chickUpper : chickenUpper;
  const legCount = isBabyChick ? 2 : 4;

  let legLOffX = 0, legLLiftZ = 0;
  let legROffX = 0, legRLiftZ = 0;
  let bodyBobZ = 0, rollWobble = 0;
  let headOffX = 0, headOffZ = 0;

  if (isWalking) {
    const swingDist = isBabyChick ? 2.4 : 3.2;
    const maxLift = isBabyChick ? 1.8 : 2.4;
    const speed = isBabyChick ? 0.75 : 0.55;

    function getLegPose(phase) {
      const u = ((phase % 1) + 1) % 1;
      if (u < 0.5) {
        const p = u / 0.5;
        return { offX: -swingDist + (2 * swingDist) * p, liftZ: Math.sin(p * Math.PI) * maxLift };
      } else {
        const p = (u - 0.5) / 0.5;
        return { offX: swingDist - (2 * swingDist) * p, liftZ: 0 };
      }
    }

    const uL = t * speed;
    const uR = uL + 0.5;
    const legL = getLegPose(uL);
    const legR = getLegPose(uR);
    legLOffX = legL.offX; legLLiftZ = legL.liftZ;
    legROffX = legR.offX; legRLiftZ = legR.liftZ;

    rollWobble = Math.sin(t * (isBabyChick ? 4.5 : 3.4)) * (isBabyChick ? 0.16 : 0.12);
    bodyBobZ = Math.abs(Math.sin(t * (isBabyChick ? 4.5 : 3.4))) * (isBabyChick ? 1.6 : 1.3);
    headOffX = Math.sin(t * 3.4) * (isBabyChick ? 1.2 : 2.2);
  } else if (isPecking) {
    // Ciscando
    const cycle = (t * 2.4) % (Math.PI * 2);
    if (cycle < Math.PI * 0.35) {
      const p = Math.sin((cycle / (Math.PI * 0.35)) * Math.PI * 0.5);
      headOffX = p * (isBabyChick ? 2.8 : 4.5);
      headOffZ = -p * (isBabyChick ? 1.2 : 1.5);
    } else if (cycle < Math.PI * 0.70) {
      const p = (cycle - Math.PI * 0.35) / (Math.PI * 0.35);
      const pSin = Math.sin(p * Math.PI * 0.5);
      headOffX = (isBabyChick ? 2.8 : 4.5) + pSin * (isBabyChick ? 0.5 : 0.8);
      headOffZ = (isBabyChick ? -1.2 : -1.5) - pSin * (isBabyChick ? 3.5 : 5.0);
    } else if (cycle < Math.PI * 1.10) {
      const p = (cycle - Math.PI * 0.70) / (Math.PI * 0.40);
      headOffX = (isBabyChick ? 3.3 : 5.3) * (1 - p * 0.3);
      headOffZ = (isBabyChick ? -4.7 : -6.5) * (1 - p);
    } else {
      const p = (cycle - Math.PI * 1.10) / (Math.PI * 0.90);
      headOffX = (isBabyChick ? 2.3 : 3.7) * (1 - p);
      headOffZ = 0;
    }

    // Grãozinhos de milho
    const pFloor = project(chk.x, chk.y, baseLiftZ);
    const dist = (isBabyChick ? 8 : 11) * chk.scale;
    const seedX = pFloor.x + Math.cos(chkAngle) * dist;
    const seedY = pFloor.y + Math.sin(chkAngle) * dist * squash;
    lowCtx.fillStyle = '#F59E0B';
    if (isBabyChick) {
      lowCtx.fillRect(seedX, seedY, 2, 2);
    } else {
      lowCtx.fillRect(seedX - 2, seedY - 1, 3, 2);
      lowCtx.fillRect(seedX + 3, seedY + 1, 2, 2);
    }
  } else if (isBrooding) {
    bodyBobZ = isBabyChick ? -1.8 : -3.2;
  } else {
    bodyBobZ = Math.sin(t * 1.5) * (isBabyChick ? 0.3 : 0.4);
  }

  const zStep = (isBabyChick ? 1.15 : 1.35) * chk.scale;
  const baseDim = isBabyChick ? 18 : 24;
  const sw = baseDim * chk.scale;
  const sh = baseDim * chk.scale;

  // 1. Patas
  if (!isBrooding) {
    for (let i = 0; i < legCount; i++) {
      // Pata Esquerda
      const zL = baseLiftZ + (i + legLLiftZ) * (chk.scale || 1.35);
      const pL = project(chk.x, chk.y, zL);
      const sxL = pL.x + (legLOffX * Math.cos(chkAngle)) * chk.scale;
      const syL = pL.y + (legLOffX * Math.sin(chkAngle)) * chk.scale * squash;
      lowCtx.save();
      lowCtx.translate(sxL, syL);
      lowCtx.scale(1, squash);
      lowCtx.rotate(chkAngle);
      lowCtx.drawImage(activeLegL[i], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();

      // Pata Direita
      const zR = baseLiftZ + (i + legRLiftZ) * (chk.scale || 1.35);
      const pR = project(chk.x, chk.y, zR);
      const sxR = pR.x + (legROffX * Math.cos(chkAngle)) * chk.scale;
      const syR = pR.y + (legROffX * Math.sin(chkAngle)) * chk.scale * squash;
      lowCtx.save();
      lowCtx.translate(sxR, syR);
      lowCtx.scale(1, squash);
      lowCtx.rotate(chkAngle);
      lowCtx.drawImage(activeLegR[i], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();
    }
  }

  // 2. Corpo & Cabeça
  if (isBabyChick) {
    if (chk.hat && chk.hat !== 'none') {
      // === PINTINHO ESCONDIDO DENTRO DO CHAPÉU GIGANTE (Oversized Walking Hat!) ===
      const hatModel = HATS[chk.hat];
      if (hatModel) {
        // O chapéu cobre o pintinho por inteiro com proporção cômica fofa
        const hatScale = 1.45; // Chapéu grandão que realmente cobre a bolinha
        const hatZ = baseLiftZ + (0.5 + bodyBobZ) * (chk.scale || 1.35);

        // Silhueta amarela aconchegada dentro do chapéu (apenas visível por leve transparência interna)
        lowCtx.save();
        lowCtx.globalAlpha = 0.40;
        const totalUpper = activeUpper.length;
        const innerScale = (chk.scale || 1.35) * 0.75; // Reduzido para caber 100% dentro da copa do chapéu
        const isw = baseDim * innerScale;
        const ish = baseDim * innerScale;
        for (let i = 0; i < totalUpper; i++) {
          const zIndex = i + 1;
          const z = baseLiftZ + (zIndex + bodyBobZ) * innerScale;
          const p = project(chk.x, chk.y, z);
          lowCtx.save();
          lowCtx.translate(p.x, p.y);
          lowCtx.scale(1, squash);
          lowCtx.rotate(chkAngle + rollWobble);
          lowCtx.drawImage(activeUpper[i], -isw / 2, -ish / 2, isw, ish);
          lowCtx.restore();
        }
        lowCtx.restore();

        // Chapéu grandão com 92% de opacidade assentado sobre ele
        lowCtx.save();
        lowCtx.globalAlpha = 0.92;
        drawStackObject(hatModel, chk.x, chk.y, hatZ, chk.selfAngle + rollWobble * 1.5, hatScale);
        lowCtx.restore();

        // Olhinhos pretos brilhantes e biquinho laranja espiando pela aba frontal do chapéu!
        const peekZ = baseLiftZ + (2.8 + bodyBobZ) * (chk.scale || 1.35);
        const pFace = project(chk.x, chk.y, peekZ);
        const faceDist = 6.2 * (chk.scale || 1.35);
        const fx = pFace.x + Math.cos(chkAngle) * faceDist;
        const fy = pFace.y + Math.sin(chkAngle) * faceDist * squash;
        lowCtx.save();
        lowCtx.translate(fx, fy);
        // Olho esquerdo
        lowCtx.fillStyle = '#1A1A1A';
        lowCtx.fillRect(-4, -2, 2, 2);
        lowCtx.fillStyle = '#FFFFFF';
        lowCtx.fillRect(-4, -2, 1, 1);
        // Olho direito
        lowCtx.fillStyle = '#1A1A1A';
        lowCtx.fillRect(3, -2, 2, 2);
        lowCtx.fillStyle = '#FFFFFF';
        lowCtx.fillRect(3, -2, 1, 1);
        // Biquinho laranja fofo
        lowCtx.fillStyle = '#F97316';
        lowCtx.fillRect(-1, 0, 3, 2);
        lowCtx.restore();

        return;
      }
    }

    // O pintinho é uma bolinha unificada (slices 2 a 9)
    const totalUpper = activeUpper.length;
    for (let i = 0; i < totalUpper; i++) {
      const zIndex = i + 2;
      // As camadas superiores (olhos e bico) mergulham junto ao ciscar
      const hRatio = i >= 4 ? (i - 3) / 5 : 0;
      const z = baseLiftZ + (zIndex + bodyBobZ + headOffZ * hRatio) * (chk.scale || 1.35);
      const p = project(chk.x, chk.y, z);
      const sx = p.x + (headOffX * hRatio * Math.cos(chkAngle)) * chk.scale;
      const sy = p.y + (headOffX * hRatio * Math.sin(chkAngle)) * chk.scale * squash;
      lowCtx.save();
      lowCtx.translate(sx, sy);
      lowCtx.scale(1, squash);
      lowCtx.rotate(chkAngle + rollWobble);
      lowCtx.drawImage(activeUpper[i], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();
    }
  } else {
    // Galinha Adulta Popó: Corpo (4..9) e Cabeça (10..15)
    for (let i = 4; i <= 9; i++) {
      const z = baseLiftZ + (i + bodyBobZ) * (chk.scale || 1.35);
      const p = project(chk.x, chk.y, z);
      lowCtx.save();
      lowCtx.translate(p.x, p.y);
      lowCtx.scale(1, squash);
      lowCtx.rotate(chkAngle + rollWobble);
      lowCtx.drawImage(activeUpper[i - 4], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();
    }

    for (let i = 10; i < ROOM_CHICKEN_SLICES.length; i++) {
      const z = baseLiftZ + (i + bodyBobZ + headOffZ) * (chk.scale || 1.35);
      const p = project(chk.x, chk.y, z);
      const sx = p.x + (headOffX * Math.cos(chkAngle)) * chk.scale;
      const sy = p.y + (headOffX * Math.sin(chkAngle)) * chk.scale * squash;
      lowCtx.save();
      lowCtx.translate(sx, sy);
      lowCtx.scale(1, squash);
      lowCtx.rotate(chkAngle + rollWobble);
      lowCtx.drawImage(activeUpper[i - 4], -sw / 2, -sh / 2, sw, sh);
      lowCtx.restore();
    }

    // Chapéu charmoso inclinado ao lado da crista da Galinha Popó
    if (chk.hat && chk.hat !== 'none') {
      const hatModel = HATS[chk.hat];
      if (hatModel) {
        const headForward = (6.0 + headOffX) * (chk.scale || 1.35);
        const hx = chk.x + headForward * Math.cos(chkAngle - turn);
        const hy = chk.y + headForward * Math.sin(chkAngle - turn);
        const hz = baseLiftZ + (12.8 + bodyBobZ + headOffZ) * (chk.scale || 1.35);
        drawStackObject(hatModel, hx, hy, hz, chk.selfAngle + 0.18, 0.78);
      }
    }
  }
}

// IA Autônoma das Aves (Popó e Pintinho Piu): Passeiam rebolando, ciscam e descansam
function updateChickenAI() {
  const chickens = items.filter(it => it.isChicken && it.visible !== false);
  const desk = items.find(it => it.id === 'desk' && it.visible !== false);
  const shelf = items.find(it => it.id === 'shelf' && it.visible !== false);

  chickens.forEach(chk => {
    chk.animTime = (chk.animTime || 0) + 0.08;

    if (isDecorMode && isDraggingItem && selectedItem === chk) {
      chk.state = 'idle';
      chk.isWalking = false;
      return;
    }

    const isBabyChick = (chk.id === 'chick');

    // === 1. COMPORTAMENTO EM PLATAFORMAS (MESA OU PRATELEIRA) ===
    // Balanço de pneu em pé no Jardim
    const swingTarget = items.find(it => it.id === 'tire_swing' && it.visible !== false);
    if (chk.surface === 'tire_swing' && swingTarget) {
      chk.x = swingTarget.x;
      chk.y = swingTarget.y + 4;
      chk.liftZ = 6; // Senta visível dentro do vão do pneu em pé!
      chk.selfAngle = swingTarget.selfAngle;
      chk.stateTimer = (chk.stateTimer || 260) - 1;
      if (chk.stateTimer <= 0) {
        chk.surface = null;
        chk.liftZ = 0;
        chk.x = swingTarget.x - 14;
        chk.y = swingTarget.y + 12;
        chk.state = 'walk';
        chk.targetX = -10; chk.targetY = 10;
        chk.speech = { text: "Có có! Pulei do balanço! 🌾", timer: 140 };
      }
      return;
    }

    if (currentRoomId === 'garden' && swingTarget && !chk.surface && !chk.isBabyChick) {
      if (Math.random() < 0.0035) {
        chk.targetX = swingTarget.x;
        chk.targetY = swingTarget.y;
        chk.state = 'walk';
      }
      if (Math.hypot(chk.x - swingTarget.x, chk.y - swingTarget.y) < 16) {
        chk.surface = 'tire_swing';
        chk.stateTimer = 300;
        chk.speech = { text: "Có có! Subi no balanço de pneu! 🛞✨", timer: 160 };
        return;
      }
    }

    if (chk.surface === 'desk' && desk) {
      chk.liftZ = 21;
      chk.stateTimer = (chk.stateTimer || 100) - 1;
      if (chk.stateTimer <= 0) {
        const r = Math.random();
        if (isBabyChick) {
          // Pintinho NÃO consegue descer! Fica sanzando pelo tampo!
          if (r < 0.50) {
            chk.state = 'walk';
            chk.stateTimer = 70 + Math.floor(Math.random() * 60);
            const targetP = constrainToDesk(desk.x + (Math.random() - 0.5) * 48, desk.y + (Math.random() - 0.5) * 18, 4);
            chk.targetX = targetP.x;
            chk.targetY = targetP.y;
            chk.isWalking = true;
          } else if (r < 0.85) {
            chk.state = 'peck';
            chk.stateTimer = 60 + Math.floor(Math.random() * 60);
            chk.isWalking = false;
            if (Math.random() < 0.4) playChickenSound();
          } else {
            chk.state = 'idle';
            chk.stateTimer = 60;
            chk.isWalking = false;
          }
        } else {
          // Galinha adulta na mesa pode ciscar ou pular pro chão
          if (r < 0.35) {
            chk.surface = null;
            chk.liftZ = 0;
            chk.x = desk.x + 24;
            chk.y = desk.y + 28;
            chk.state = 'peck';
            chk.stateTimer = 80;
            chk.isWalking = false;
            playChickenSound();
          } else if (r < 0.70) {
            chk.state = 'peck';
            chk.stateTimer = 80;
            chk.isWalking = false;
          } else {
            chk.state = 'idle';
            chk.stateTimer = 70;
            chk.isWalking = false;
          }
        }
      }

      if (chk.state === 'walk') {
        const dx = (chk.targetX || chk.x) - chk.x;
        const dy = (chk.targetY || chk.y) - chk.y;
        const dist = Math.hypot(dx, dy);
        if (dist > 3) {
          const moveSpeed = isBabyChick ? 0.38 : 0.45;
          const targetAngle = Math.atan2(dy, dx);
          let diff = targetAngle - chk.selfAngle;
          while (diff < -Math.PI) diff += Math.PI * 2;
          while (diff > Math.PI) diff -= Math.PI * 2;
          chk.selfAngle += diff * 0.12;

          const nextX = chk.x + Math.cos(chk.selfAngle) * moveSpeed;
          const nextY = chk.y + Math.sin(chk.selfAngle) * moveSpeed;
          const clamped = constrainToDesk(nextX, nextY, 4);
          chk.x = clamped.x;
          chk.y = clamped.y;
          chk.isWalking = true;
        } else {
          chk.state = 'peck';
          chk.stateTimer = 70;
          chk.isWalking = false;
        }
      }
      return;
    }

    if (chk.surface === 'shelf' && shelf) {
      chk.liftZ = shelf.liftZ + 3.5;
      chk.stateTimer = (chk.stateTimer || 120) - 1;

      if (isBabyChick) {
        // Pintinho na prateleira NÃO desce! Sanza para lá e para cá sem cair!
        if (chk.stateTimer <= 0) {
          const r = Math.random();
          if (r < 0.55) {
            chk.state = 'walk';
            chk.stateTimer = 70 + Math.floor(Math.random() * 50);
            const targetY = shelf.y + (-shelf.length / 2 + 10 + Math.random() * (shelf.length - 20));
            chk.targetX = -ROOM_R + 9;
            chk.targetY = targetY;
            chk.isWalking = true;
          } else if (r < 0.85) {
            chk.state = 'peck';
            chk.stateTimer = 60 + Math.floor(Math.random() * 50);
            chk.isWalking = false;
            if (Math.random() < 0.4) playChickenSound();
          } else {
            chk.state = 'idle';
            chk.stateTimer = 60;
            chk.isWalking = false;
          }
        }

        if (chk.state === 'walk') {
          const dy = (chk.targetY || chk.y) - chk.y;
          if (Math.abs(dy) > 2) {
            const moveSpeed = 0.32;
            chk.selfAngle = dy > 0 ? Math.PI / 2 : -Math.PI / 2;
            const nextY = chk.y + (dy > 0 ? moveSpeed : -moveSpeed);
            const clamped = constrainToShelf(nextY, 8);
            chk.x = clamped.x;
            chk.y = clamped.y;
            chk.isWalking = true;
          } else {
            chk.state = 'peck';
            chk.stateTimer = 60;
            chk.isWalking = false;
          }
        }
        return;
      } else {
        // Galinha Popó na prateleira dorme/choca no ninho entre os livros!
        chk.state = 'brood';
        chk.isWalking = false;
        if (chk.stateTimer <= 0) {
          if (Math.random() < 0.55) {
            // Voa/desce da prateleira para o chão suavemente!
            chk.surface = null;
            chk.liftZ = 0;
            chk.x = -ROOM_R + 32;
            chk.y = shelf.y + (Math.random() - 0.5) * 16;
            chk.state = 'peck';
            chk.stateTimer = 90;
            chk.isWalking = false;
            playChickenSound();
            hearts.push({ x: chk.x, y: chk.y, z: 12, life: 1.0 });
          } else {
            // Continua chocando confortavelmente
            chk.stateTimer = 180 + Math.floor(Math.random() * 150);
          }
        }
        return;
      }
    }

    // === 2. COMPORTAMENTO NO CHÃO ===
    // Se a galinha adulta Popó estiver no chão perto da prateleira, pode voar/subir nela!
    if (!isBabyChick && shelf && Math.abs(chk.x - (-ROOM_R + 28)) < 22 && Math.abs(chk.y - shelf.y) < 28 && Math.random() < 0.08) {
      chk.surface = 'shelf';
      chk.liftZ = shelf.liftZ + 3.5;
      chk.x = -ROOM_R + 9;
      chk.y = shelf.y + (Math.random() - 0.5) * 12;
      chk.state = 'brood';
      chk.stateTimer = 260 + Math.floor(Math.random() * 180);
      chk.isWalking = false;
      playChickenSound();
      hearts.push({ x: chk.x, y: chk.y, z: chk.liftZ + 12, life: 1.0 });
      return;
    }

    // Caminhar normal no chão
    chk.stateTimer = (chk.stateTimer || 100) - 1;
    if (chk.stateTimer <= 0) {
      const r = Math.random();
      if (r < 0.40) {
        chk.state = 'walk';
        chk.stateTimer = 90 + Math.floor(Math.random() * 80);
        chk.targetX = -ROOM_R * 0.7 + Math.random() * (ROOM_R * 1.4);
        chk.targetY = -ROOM_R * 0.7 + Math.random() * (ROOM_R * 1.4);
        chk.isWalking = true;
      } else if (r < 0.75) {
        chk.state = 'peck';
        chk.stateTimer = 80 + Math.floor(Math.random() * 90);
        chk.isWalking = false;
        if (Math.random() < 0.5) playChickenSound();
      } else if (r < 0.90) {
        chk.state = 'brood';
        chk.stateTimer = 120 + Math.floor(Math.random() * 100);
        chk.isWalking = false;
      } else {
        chk.state = 'idle';
        chk.stateTimer = 70 + Math.floor(Math.random() * 60);
        chk.isWalking = false;
      }
    }

    if (chk.state === 'walk') {
      const dx = (chk.targetX || chk.x) - chk.x;
      const dy = (chk.targetY || chk.y) - chk.y;
      const dist = Math.hypot(dx, dy);
      if (dist > 4) {
        const moveSpeed = 0.45;
        const targetAngle = Math.atan2(dy, dx);
        let diff = targetAngle - chk.selfAngle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        chk.selfAngle += diff * 0.1;

        let nextX = chk.x + Math.cos(chk.selfAngle) * moveSpeed;
        let nextY = chk.y + Math.sin(chk.selfAngle) * moveSpeed;

        const maxR = ROOM_R - 22;
        nextX = Math.max(-maxR, Math.min(maxR, nextX));
        nextY = Math.max(-maxR, Math.min(maxR, nextY));

        chk.x = nextX;
        chk.y = nextY;
        chk.isWalking = true;
      } else {
        chk.state = 'peck';
        chk.stateTimer = 90;
        chk.isWalking = false;
      }
    }
  });
}

// IA Autônoma do Gatinho: Passeia pelo quarto, explora e descansa
function updateCatAI() {
  const cat = items.find(it => it.id === 'cat');
  if (!cat) return;
  const desk = items.find(it => it.id === 'desk' && it.visible !== false);

  cat.idleTimer = (cat.idleTimer || 0) + 0.05;

  // Se o usuário estiver arrastando o gato no Modo Decoração, pausa a IA
  if (isDecorMode && isDraggingItem && selectedItem === cat) {
    cat.state = 'idle';
    cat.stateTimer = 180;
    cat.isWalking = false;
    return;
  }

  // Se o usuário fixou uma postura (Sentar, Pãozinho, Barriga):
  if (cat.forcedPosture && cat.forcedPosture !== 'auto') {
    if (cat.forcedPosture === 'walk') {
      // Deixa caminhar livremente
    } else {
      cat.state = 'idle';
      cat.isWalking = false;
      cat.posture = cat.forcedPosture;
      return;
    }
  }

  // Se estiver em reação de carinho na barriguinha
  if (cat.bellyTimer > 0) {
    cat.bellyTimer--;
    cat.state = 'idle';
    cat.isWalking = false;
    cat.posture = 'belly';
    return;
  }

  // === COMPORTAMENTO DO GATO NA MESA ===
  if (cat.surface === 'desk' && desk) {
    cat.liftZ = 21;
    // Se colocado na mesa pelo usuário, dorme por um tempo garantido!
    if (cat.deskSleepTimer && cat.deskSleepTimer > 0) {
      cat.deskSleepTimer--;
      cat.state = 'idle';
      cat.isWalking = false;
      cat.posture = 'loaf';
      return;
    }

    if (cat.state === 'idle') {
      cat.stateTimer = (cat.stateTimer || 180) - 1;
      if (cat.stateTimer <= 0) {
        const r = Math.random();
        if (r < 0.40) {
          // Pula graciosamente da mesa para o chão!
          cat.surface = null;
          cat.liftZ = 0;
          const jumpTarget = checkCatCollision(desk.x + 24, desk.y + 26);
          cat.x = jumpTarget.x;
          cat.y = jumpTarget.y;
          cat.state = 'idle';
          cat.posture = 'stand';
          cat.stateTimer = 120;
          playMeowSound();
          return;
        } else if (r < 0.70) {
          // Muda de postura no tampo (sentado ou barriga relaxada)
          cat.posture = Math.random() < 0.5 ? 'sit' : 'belly';
          cat.stateTimer = 160 + Math.floor(Math.random() * 180);
        } else {
          // Anda um pouquinho pelo tampo sem cair
          cat.state = 'walking';
          cat.posture = 'walk';
          const targetP = constrainToDesk(desk.x + (Math.random() - 0.5) * 44, desk.y + (Math.random() - 0.5) * 16, 4);
          cat.targetX = targetP.x;
          cat.targetY = targetP.y;
        }
      }
    } else if (cat.state === 'walking') {
      const dx = cat.targetX - cat.x;
      const dy = cat.targetY - cat.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 2.5) {
        cat.x = cat.targetX;
        cat.y = cat.targetY;
        cat.state = 'idle';
        cat.stateTimer = 160 + Math.floor(Math.random() * 200);
        cat.isWalking = false;
        cat.posture = Math.random() < 0.5 ? 'sit' : 'loaf';
      } else {
        cat.isWalking = true;
        cat.posture = 'walk';
        const targetAngle = Math.atan2(-dx, dy);
        let diff = targetAngle - cat.selfAngle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        cat.selfAngle += diff * 0.14;
        const speed = 0.45;
        const nextX = cat.x - Math.sin(cat.selfAngle) * speed;
        const nextY = cat.y + Math.cos(cat.selfAngle) * speed;
        const resolved = constrainToDesk(nextX, nextY, 4);
        cat.x = resolved.x;
        cat.y = resolved.y;
        cat.walkCycle = (cat.walkCycle || 0) + speed * 0.35;
      }
    }
    return;
  }

  // === COMPORTAMENTO DO GATO NO CHÃO ===
  if (cat.state === 'idle') {
    cat.isWalking = false;
    cat.stateTimer = (cat.stateTimer || 180) - 1;
    if (cat.stateTimer <= 0) {
      // Se estiver perto da mesa no chão, tem chance de pular pra cima da mesa!
      if (desk && Math.hypot(cat.x - desk.x, cat.y - desk.y) < 55 && Math.random() < 0.28) {
        cat.surface = 'desk';
        cat.liftZ = 21;
        const targetOnDesk = constrainToDesk(desk.x, desk.y);
        cat.x = targetOnDesk.x;
        cat.y = targetOnDesk.y;
        cat.state = 'idle';
        cat.posture = Math.random() < 0.5 ? 'loaf' : 'sit';
        cat.deskSleepTimer = 240 + Math.floor(Math.random() * 200);
        cat.stateTimer = 180;
        playMeowSound();
        return;
      }

      // Escolhe um novo ponto aconchegante pelo quarto
      const waypoints = [
        { x: 0, y: 0 },       // Centro do tapete
        { x: 18, y: 15 },     // Borda do tapete
        { x: -35, y: -20 },   // Frente da caminha nuvem
        { x: -35, y: 25 },    // Perto do arranhador
        { x: 30, y: 35 },     // Perto da plantinha de chão
        { x: 42, y: -30 },    // Frente da cadeira da mesa
        { x: -25, y: -40 },   // Perto da janela
        { x: -10, y: 22 }     // Lado sul do tapete
      ];
      const wp = waypoints[Math.floor(Math.random() * waypoints.length)];
      const validTarget = checkCatCollision(
        wp.x + (Math.random() - 0.5) * 12,
        wp.y + (Math.random() - 0.5) * 12
      );
      cat.targetX = validTarget.x;
      cat.targetY = validTarget.y;
      cat.state = 'walking';
      cat.posture = 'walk';
    }
  } else if (cat.state === 'walking') {
    const dx = cat.targetX - cat.x;
    const dy = cat.targetY - cat.y;
    const dist = Math.hypot(dx, dy);

    if (dist < 2.5) {
      cat.x = cat.targetX;
      cat.y = cat.targetY;
      cat.state = 'idle';
      cat.stateTimer = 180 + Math.floor(Math.random() * 240); // 3 a 7 segundos relaxando
      cat.isWalking = false;
      // Escolhe uma postura aconchegante aleatória fofa!
      const r = Math.random();
      if (r < 0.40) cat.posture = 'sit';
      else if (r < 0.75) cat.posture = 'loaf';
      else if (r < 0.90) cat.posture = 'belly';
      else cat.posture = 'stand';
    } else {
      cat.isWalking = true;
      cat.posture = 'walk';
      const targetAngle = Math.atan2(-dx, dy);

      let diff = targetAngle - cat.selfAngle;
      while (diff < -Math.PI) diff += Math.PI * 2;
      while (diff > Math.PI) diff -= Math.PI * 2;
      cat.selfAngle += diff * 0.14;

      const speed = 0.55;
      const nextX = cat.x - Math.sin(cat.selfAngle) * speed;
      const nextY = cat.y + Math.cos(cat.selfAngle) * speed;

      const resolved = checkCatCollision(nextX, nextY);
      const moved = Math.hypot(resolved.x - cat.x, resolved.y - cat.y);

      if (moved < 0.04 && dist > 8) {
        cat.state = 'idle';
        cat.stateTimer = 120;
        cat.isWalking = false;
        cat.posture = Math.random() < 0.5 ? 'sit' : 'loaf';
      } else {
        cat.x = resolved.x;
        cat.y = resolved.y;
        cat.walkCycle = (cat.walkCycle || 0) + speed * 0.35;
      }
    }
  }
}

