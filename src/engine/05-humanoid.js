    // =========================================================================
    // ENGINE: HUMANOIDE CRU (avatar de teste) — partes voxel articuladas
    // Pernas/braços balançam no passo; braços sobem ao carregar item; braço
    // direito golpeia quando swingTimer > 0. Altura base ≈ 28u (escala 1.0).
    // =========================================================================
    const HUMANOID_PAL = ['rgba(0,0,0,0)', '#F2C9A0', '#4F83C2', '#3E4A6E', '#5B3A22', '#2A2018', '#1B1B1B'];
    let humanoidModels = null;

    function _humBox(w, d, h, fn) {
      const data = [];
      for (let z = 0; z < h; z++) {
        const rows = [];
        for (let y = 0; y < d; y++) {
          let s = '';
          for (let x = 0; x < w; x++) s += (fn(x, y, z) || 0).toString(36);
          rows.push(s);
        }
        data.push(rows);
      }
      return buildSliceSheet(data, HUMANOID_PAL);
    }

    function getHumanoidModels() {
      if (humanoidModels) return humanoidModels;
      humanoidModels = {
        leg: _humBox(3, 3, 11, (x, y, z) => (z < 2 ? 5 : 3)),
        torso: _humBox(8, 4, 9, () => 2),
        arm: _humBox(2, 2, 9, (x, y, z) => (z < 2 ? 1 : 2)),
        head: _humBox(6, 6, 8, (x, y, z) => {
          if (z >= 6) return 4;                         // cabelo (topo)
          if (y === 0 && z >= 3) return 4;              // cabelo (nuca)
          if (y === 5 && z === 3 && (x === 1 || x === 4)) return 6; // olhos (frente = +y)
          return 1;
        })
      };
      return humanoidModels;
    }

    function pushHumanoidDrawables(list, who, cosA, sinA, bob) {
      const M = getHumanoidModels();
      const S = who.scale || 1;
      const t = who.walkPhase;
      const inAir = !who.onGround;
      const walking = !!who.isWalking;
      const cosC = Math.cos(who.selfAngle);
      const sinC = Math.sin(who.selfAngle);
      const carrying = typeof carriedDrop !== 'undefined' && !!carriedDrop;
      const swinging = typeof swingTimer !== 'undefined' && swingTimer > 0;
      let maxTop = -Infinity;

      const part = (model, lx, ly, zOff, depthBias) => {
        const px = who.x + lx * S * cosC - ly * S * sinC;
        const py = who.y + lx * S * sinC + ly * S * cosC;
        const baseZ = Math.round(who.z + zOff * S);
        const topZ = baseZ + Math.ceil(model.count * S);
        const dp = (px - camX) * sinA + (py - camY) * cosA;
        list.push({
          baseZ, topZ, depth: dp + depthBias,
          drawSlice: (z) => {
            const sz = Math.min(model.count - 1, Math.floor((z - baseZ) / S));
            stampModelSlice(entityCtx, model, sz, px, py, z, who.selfAngle, S, cosA, sinA);
          }
        });
        if (topZ > maxTop) maxTop = topZ;
      };

      const swing = (phase) => (walking && !inAir ? Math.sin(t + phase) : 0);
      // Pernas
      part(M.leg, -2.2, inAir ? -1.8 : swing(0) * 3.0, Math.max(0, swing(0)) * 2.2, 0.40);
      part(M.leg, 2.2, inAir ? 1.8 : swing(Math.PI) * 3.0, Math.max(0, swing(Math.PI)) * 2.2, 0.40);
      // Tronco e cabeça
      part(M.torso, 0, 0, 10 + bob, 0.50);
      part(M.head, 0, 0.5, 19 + bob, 0.60);
      // Braços
      if (carrying) {
        part(M.arm, -5, 0.5, 19 + bob, 0.55);
        part(M.arm, 5, 0.5, 19 + bob, 0.55);
      } else {
        const rightSwing = swinging ? 4.5 : -swing(Math.PI) * 3.0;
        part(M.arm, -5, -swing(0) * 3.0, 10.5 + bob, 0.55);
        part(M.arm, 5, rightSwing, (swinging ? 12.5 : 10.5) + bob, 0.55);
      }
      return maxTop;
    }
