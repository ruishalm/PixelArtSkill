---
name: pixel-art-3d
description: Build 3D and pseudo-3D pixel art applications, dioramas, and games using Sprite Stacking (HTML5 Canvas 2D), Pixel-Art Gaussian Splatting (Three.js / Spark / WebGL 2), and Software Depth-Buffered Rasterizers. Covers voxel-to-slice generation, squash camera tilt, single-outline dilation, low-res integer scaling buffers, palette voting, OKLab color matching, Bayer dithering, and stepped-frame animations.
---

# pixel-art-3d

Comprehensive engine and design rules for rendering rotatable, interactive, and procedural **3D Pixel Art**.

Covers three modern engineering paradigms:
1. **Sprite Stacking (Canvas 2D)**: Fake 3D rendered from stacked 2D slices. Zero WebGL/3D engine dependencies. 60 FPS on any device.
2. **Pixel-Art Gaussian Splatting (Three.js / WebGL 2)**: True 3D orbiting worlds and rigged GLB characters converted to surfel splats with palette voting and shader ink outlines.
3. **Software Depth-Buffered Rasterizer (Pure JS Isometric)**: 100% dependency-free custom software rasterizer with a float depth buffer, hue-shifted ramps, and Bayer-dithered cast shadows.

---

## 1. Paradigm Selector

> [!CAUTION]
> **PADRÃO OURO OFICIAL E OBRIGATÓRIO DESTE PROJETO:**
> **Pure HTML5 Canvas 2D Sprite Stacking + Matrizes Voxel JSON geradas por scripts Python** é a **ÚNICA** arquitetura autorizada para dioramas, personagens, móveis, cômodos e terrenos 3D neste repositório.
>
> **PROIBIDO:** NÃO utilize Three.js, WebGL, shaders GLSL, `Canvas` 3D ou bibliotecas externas de renderização para este estilo. Zero dependências em runtime — tudo deve rodar diretamente em Canvas 2D puro (`imageSmoothingEnabled = false`) com fatias voxel JSON e integer upscaling.

| Requirement | Recommended Paradigm | Key Technologies |
|---|---|---|
| **Dioramas, personagens, cômodos, terrenos, mini-games e UI pixel art 3D (PADRÃO OFICIAL)** | **Sprite Stacking (OBRIGATÓRIO)** | Pure HTML5 Canvas 2D, OffscreenCanvas, Matrizes Voxel JSON (Python) |
| *(Legado / Opcional — NÃO usar por padrão)* Orbit 3D / GLTF importado | *Pixel-Art Gaussian Splatting* | Three.js, Spark, WebGL 2 *(Proibido no padrão oficial)* |
| *(Legado / Opcional — NÃO usar por padrão)* Câmera isométrica fixa | *Software Depth Rasterizer* | ImageData, Float32Array Z-buffer |

---

## 2. Paradigm 1: Sprite Stacking Engine (Canvas 2D)

Based on the architecture of `@nazim.builds` (Pixel Stack & Stack Farm).

### The Math & Drawing Loop
Each 3D object is composed of a series of horizontal 2D slices stacked along the Z-axis (slice 0 = base, slice N-1 = top).

```typescript
function drawStack(
  ctx: CanvasRenderingContext2D,
  sheet: CanvasImageSource,
  count: number,
  pos: { x: number; y: number },
  turn: number,          // object rotation in radians
  squash: number = 0.75, // camera tilt (1.0 = top-down, ~0.6 min)
  spacing: number = 1    // layer height lift in pixels
) {
  const w = (sheet.width as number) / count;
  const h = sheet.height as number;
  const rect = [-Math.floor(w / 2), -Math.floor(h / 2), w, h];

  for (let z = 0; z < count; z++) {
    ctx.save();
    // 1. Move to integer screen coordinates with height lift
    ctx.translate(Math.round(pos.x), Math.round(pos.y - Math.round(z * spacing)));
    // 2. Camera squash (vertical compression creating the oblique perspective)
    ctx.scale(1, squash);
    // 3. Rotate every slice around its center
    ctx.rotate(turn);
    // 4. Draw slice with nearest-neighbor sampling
    ctx.drawImage(sheet, z * w, 0, w, h, rect[0], rect[1], rect[2], rect[3]);
    ctx.restore();
  }
}
```

### Golden Rules for Sprite Stacking
1. **Camera Squash Factor**:
   - Default: `0.75`.
   - Never drop below `0.60`, or horizontal roofs become paper-thin and artifacted.
2. **Nearest-Neighbor Scaling Only**:
   - Set `ctx.imageSmoothingEnabled = false` on every canvas and buffer.
3. **Low-Res Offscreen Buffer + Integer Upscale (e Regra Obrigatória de Texto Hi-Res)**:
   - Never render 3D geometry directly to high-res display pixels.
   - Render the scene into an offscreen canvas (`lowCanvas`) at logical resolution (e.g. `270x480` for 9:16 mobile reels, `320x180`, `440x440`, or `480x300` for landscape/diorama).
   - Upscale onto the screen canvas by an integer multiplier (`x2`, `x3`, `x4`) with `imageSmoothingEnabled = false`.
   - Snap all entity coordinates to integer values (`Math.round`) inside the low-res buffer to stop subpixel jitter and shimmering.
   - **NUNCA Pixelizar Letras nem Balões**: É **proibido** desenhar balões de fala, textos ou emojis dentro do `lowCanvas` (`440x440` ou `480x300`) antes do upscale *nearest-neighbor* — isso pixeliza e borra as letras e pode cortar o balão atrás de paredes ou penhascos. Sempre use o padrão obrigatório **Overlay Pass Hi-Res** (ver snippet 5 abaixo).
   - **Regra de Viewport Responsivo 1:1 (Sem Distorção de Pixels)**: Nunca estique um `lowCanvas` de razão de aspecto fixa (`480x300`) diretamente para `window.innerWidth x window.innerHeight` — isso achata ou alonga pixels em telas quadradas, ultrawide ou celulares verticais. No resize, calcule uma escala inteira quadrada (`pixelScale = Math.max(2, Math.min(4, Math.floor(Math.min(viewW, viewH) / 260) || 2))`), dimensione `LOW_W = Math.ceil(viewW / pixelScale)` e `LOW_H = Math.ceil(viewH / pixelScale)`, configure `canvas.width = Math.round(viewW * dpr)` com `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)`, escale para `LOW_W * pixelScale` por `LOW_H * pixelScale` mantendo **pixels 1:1 quadrados** em qualquer tela, e calcule o raio de culling dinamicamente (`Math.ceil(Math.hypot(LOW_W, LOW_H) / (TILE * 1.45)) + 5`).
4. **Single Silhouette Outline (Crucial Rule)**:
   - **NEVER outline individual slices** (this creates horizontal striped lines through the body).
   - Draw the finished stack into its own offscreen canvas.
   - Dilate the alpha mask by 1px (or draw 1px offset in 4/8 cardinal directions).
   - Fill the dilated silhouette with a dark outline color (e.g. `#3B2A20`, warm dark brown, never pure black).
   - Draw the original stack on top of the outline.
5. **Depth Sorting (Z-Order)**:
   - Never interleave slices from different objects.
   - Sort entire objects by their screen ground contact point `pos.y` (back to front).
   - Tie-break equal `pos.y` by `pos.x`, then by a persistent entity ID.
6. **Moving Entity Orientation & Directional Coherence**:
   - Entities must move strictly in the direction they are facing (no sideways crab-walking or moonwalking):
     - World velocity angle: `theta = Math.atan2(velocity.y, velocity.x)`.
     - When voxel model forward axis is $+X$, the 2D slice rotation angle on screen must match:
       ```typescript
       const totalAngle = theta + cameraTurn;
       ctx.rotate(totalAngle);
       ```
     - Never invert `cameraTurn` sign or introduce arbitrary $\pm \pi/2$ phase shifts without matching the voxel grid's forward axis.
     - Interpolate heading (`lerp` or angular difference) to produce smooth natural turns.

7. **Biomechanical Locomotion & Limb Cycles (No Treadmill Sliding)**:
   - For walking bipeds, quadrupeds, or birds, decompose each limb into a continuous 2-phase cycle:
     - **Swing Phase (No ar, $u \in [0, 0.5)$)**: Limb lifts off the ground at the back ($-D$) and arcs forward through the air to the front ($+D$):
       $$\text{offset}_X = -D + 2D \cdot (u / 0.5)$$
       $$\text{lift}_Z = \sin(\pi \cdot u / 0.5) \cdot H$$
     - **Stance Phase (No chão, $u \in [0.5, 1.0)$)**: Limb plants firmly on the ground ($\text{lift}_Z = 0$) and glides smoothly from front to back ($+D \to -D$) supporting body weight:
       $$\text{offset}_X = +D - 2D \cdot ((u - 0.5) / 0.5)$$
     - Right limb offset by half a period: $u_R = (u_L + 0.5) \pmod 1$.
     - Limb offsets on screen must project along the entity's facing vector:
       $$\text{screenOff}_X = \text{offset}_X \cdot \cos(\text{totalAngle}) \cdot \text{scale}$$
       $$\text{screenOff}_Y = \text{offset}_X \cdot \sin(\text{totalAngle}) \cdot \text{scale} \cdot \text{squash}$$

8. **Rigid Sub-Stack Articulation vs Slice Shearing**:
   - **The Shearing Trap**: In 2D horizontal sprite stacking, attempting to tilt or pitch a sub-mesh (such as a pecking head) by shearing slices horizontally ($x += h \cdot \sin\theta$) collapses the volume into an elongated, flat staircase/tube.
   - **The Solid Unit Rule**: Move sub-assemblies (head, ears, limbs) as **rigid solid blocks** by translating their entire slice sub-stack uniformly in local $(X_{\text{fwd}}, Z_{\text{down}})$:
     - The head plunges down to the ground to peck/eat while maintaining its 100% round, plump spherical 3D volume.
     - Body and feet stay completely still during isolated head gestures (pecking, nodding).

9. **Volume & Morphology: Adults vs Babies ("The Bolinha Principle")**:
   - **Never just scale down an adult mesh**: A baby animal (e.g. Pintinho Amarelinho) is morphologically distinct from a miniature adult.
   - **Baby Proportions**:
     - Monolithic spherical/ovoid silhouette ("bolinha") where head and body merge without a long neck.
     - Absence of mature secondary traits (e.g. ZERO red comb/crista on baby chicks; smooth rounded fluffy dome).
     - Higher eye-to-head ratio with shiny dark pupils and white specular highlights.
     - Stubby, rounded wing/ear bumps and miniature stick feet.
     - More energetic, bouncy waddle (`rollWobble` and `bodyBobZ` frequency $1.3\times - 1.5\times$ faster).

10. **Dynamic 3D Hitboxes for Wall and Movable Items**:
    - Interactive elements on walls (like corkboards, clocks, frames) move and rotate in 3D:
      - Project the 4 wall corners to screen: $p_1(x_w, y_0, z_0) \dots p_4(x_w, y_1, z_1)$.
      - Compute screen bounding box: `minX..maxX, minY..maxY`.
      - **Wall Culling Gate**: Check wall normal visibility (`Math.sin(turn) <= 0.05`). When a wall is facing away / culled, disable clicks immediately so invisible items cannot be clicked in empty space.
      - On `pointermove`, provide visual feedback (`canvas.style.cursor = 'pointer'`) when hovering inside the projected 3D bounding box.

11. **Baking Voxel Models in Code**:
    - Represent objects as a 3D grid `Volume(w, d, h)` of palette indices (`0 = empty`).
    - Use CSG primitives: `box`, `cylinder`, `cone`, `sphere`, `wedge`, `carve` (subtraction), `paint(fn)`, and `mirrorX`.
    - Bake 3 directional shades per material: Top (highlight), Light-facing side (mid), Shadow-facing side (dark).
    - Pre-render static stacks to offscreen canvases and cache them per camera angle.

### Template Oficial Python -> JSON de Modelagem Voxel

Todo novo asset (móvel, prop, árvore, personagem) deve ser gerado em Python para JSON seguindo esta estrutura exata:

- **Convenção de Eixos da Fatia (`slices[z][y][x]`)**:
  - `z = 0`: base / chão; `z = count - 1`: topo.
  - `y = 0`: **TRASEIRA (Back)** do modelo.
  - `y = H - 1`: **FRENTE (Front)** do modelo (portas, gavetas, puxadores, rostos, telas).
  - `x = 0 .. W - 1`: esquerda para direita.
- **Paleta Base-36**:
  - Suporta índices `'0'..'9'` e `'a'..'z'` (até 36 cores por objeto; no JS decodifique cada caractere com `parseInt(ch, 36)`).
  - Índice `'0'` é **sempre transparente** (`'rgba(0,0,0,0)'`).
- **Schema JSON Padrão**:
  ```json
  {
    "palette": ["rgba(0,0,0,0)", "#381F12", "#5C361E", "#9E6740"],
    "slices": [
      ["0000", "0110", "0220", "0330"]
    ]
  }
  ```
- **AVISO CRÍTICO DE FORMATAÇÃO**: **NUNCA** concatene todas as linhas `y` de uma fatia em uma única string plana! Cada fatia `slices[z]` DEVE ser uma lista de `H` strings, cada uma de comprimento exatamente `W` (`list[list[str]]`).

```python
import json

BASE36_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"

def encode_val(v: int) -> str:
    if not (0 <= v < 36):
        raise ValueError(f"Voxel index out of base-36 range (0..35): {v}")
    return BASE36_CHARS[v]

def make_grid(w: int, h: int, fill: int = 0) -> list[list[int]]:
    return [[fill for _ in range(w)] for _ in range(h)]

def fill_box(
    slices: list[list[list[int]]],
    x0: int, x1: int,
    y0: int, y1: int,
    z0: int, z1: int,
    val: int
) -> None:
    """Preenche um paralelepípedo inclusivo/exclusivo [x0,x1) x [y0,y1) x [z0,z1) com segurança de bordas."""
    d_z = len(slices)
    if d_z == 0:
        return
    h, w = len(slices[0]), len(slices[0][0])
    for z in range(max(0, z0), min(d_z, z1)):
        grid = slices[z]
        for y in range(max(0, y0), min(h, y1)):
            for x in range(max(0, x0), min(w, x1)):
                grid[y][x] = val

def to_strings(slices: list[list[list[int]]]) -> list[list[str]]:
    """Converte slices[z][y][x] em list[list[str]].
    NUNCA concatene todas as linhas de uma fatia em uma única string:
    cada fatia slices[z] DEVE ser uma lista de H strings de comprimento W.
    """
    return [
        [''.join(encode_val(v) for v in row) for row in s]
        for s in slices
    ]

# Exemplo de uso:
# W, H, D = 24, 16, 12
# slices = [make_grid(W, H, 0) for _ in range(D)]
# fill_box(slices, 2, 22, 0, 14, 0, 10, 1)  # Corpo traseiro (y=0..13)
# fill_box(slices, 4, 20, 14, 16, 2, 8, 2)  # Frente detalhada (y=H-2..H-1)
# asset = { "palette": ["rgba(0,0,0,0)", "#5C361E", "#9E6740"], "slices": to_strings(slices) }
```

### Core Matemático Copiável do Diorama 3D

Snippets de referência direta usados na engine oficial em Canvas 2D:

#### 1. Projeção Global (`project` e `unproject` com `squash = 0.75` e `turn`)
```javascript
const squash = 0.75; // Fator oficial de inclinação da câmera (nunca < 0.60)

function project(x, y, z) {
  const cosA = Math.cos(turn);
  const sinA = Math.sin(turn);
  const rx = x * cosA - y * sinA;
  const ry = x * sinA + y * cosA;
  const cx = Math.floor(LOW_W / 2);
  const cy = Math.floor(LOW_H / 2) + 48;
  return {
    x: Math.round(cx + rx),
    y: Math.round(cy + ry * squash - z),
    depth: ry
  };
}

// Projeção Inversa (Screen -> World no plano do chão Z = 0)
function unproject(screenX, screenY) {
  const cx = Math.floor(LOW_W / 2);
  const cy = Math.floor(LOW_H / 2) + 48;
  const rx = screenX - cx;
  const ry = (screenY - cy) / squash;
  const cosA = Math.cos(turn);
  const sinA = Math.sin(turn);
  return {
    x: rx * cosA + ry * sinA,
    y: -rx * sinA + ry * cosA
  };
}
```

#### 2. `drawStackObject(...)` + Pipeline de Contorno Único de Silhueta 1px
```javascript
function drawStackObject(targetCtx, model, worldX, worldY, liftZ = 0, selfAngle = 0, scale = 1.35) {
  const p = project(worldX, worldY, liftZ);
  const totalAngle = selfAngle + turn;
  const { sheet, count, w, h } = model;
  const originX = Math.floor(w / 2);
  const originY = Math.floor(h / 2);

  for (let z = 0; z < count; z++) {
    targetCtx.save();
    targetCtx.translate(p.x, Math.round(p.y - z * scale));
    targetCtx.scale(scale, squash * scale);
    targetCtx.rotate(totalAngle);
    targetCtx.drawImage(sheet, z * w, 0, w, h, -originX, -originY, w, h);
    targetCtx.restore();
  }
}

// Pipeline de Contorno Único em Canvas Scratch/Offscreen (ZERO listras entre fatias)
// OUTLINE_COLOR: '#3B2A20' ou '#3B2219' (nunca preto puro)
function compositeWithSingleOutline(lowCtx, stackCanvas, outlineCanvas, outlineColor = '#3B2219') {
  const outCtx = outlineCanvas.getContext('2d');
  outCtx.imageSmoothingEnabled = false;
  outCtx.globalCompositeOperation = 'source-over';
  outCtx.clearRect(0, 0, outlineCanvas.width, outlineCanvas.height);

  const offsets = [[-1, 0], [1, 0], [0, -1], [0, 1]];
  for (const [dx, dy] of offsets) {
    outCtx.drawImage(stackCanvas, dx, dy);
  }
  outCtx.globalCompositeOperation = 'source-in';
  outCtx.fillStyle = outlineColor;
  outCtx.fillRect(0, 0, outlineCanvas.width, outlineCanvas.height);

  lowCtx.drawImage(outlineCanvas, 0, 0);
  lowCtx.drawImage(stackCanvas, 0, 0);
}
```

#### 3. Smart Dynamic Wall Culling & Hitbox Gate
Paredes voltadas para a câmera colapsam em um rodapé de `3px` para nunca tampar o interior, e itens montados nessas paredes consultam o culling antes de aceitar cliques:
```javascript
function drawWalls(WALLS, ROOM_R, WALL_H) {
  const cosA = Math.cos(turn);
  const sinA = Math.sin(turn);

  const sortedWalls = WALLS.map(w => {
    const mx = (w.a.x + w.b.x) / 2;
    const my = (w.a.y + w.b.y) / 2;
    const rCenter = project(mx, my, WALL_H / 2);
    const nyRot = w.normal.x * sinA + w.normal.y * cosA;
    return { ...w, depth: rCenter.depth, isFrontWall: nyRot > 0.05 };
  }).sort((a, b) => a.depth - b.depth);

  for (const w of sortedWalls) {
    if (w.isFrontWall) {
      // Colapsa a parede frontal para um rodapé discreto de 3px
      const pA0 = project(w.a.x, w.a.y, 0), pB0 = project(w.b.x, w.b.y, 0);
      const pA1 = project(w.a.x, w.a.y, 3), pB1 = project(w.b.x, w.b.y, 3);
      lowCtx.fillStyle = P.baseboard;
      lowCtx.beginPath();
      lowCtx.moveTo(pA0.x, pA0.y); lowCtx.lineTo(pB0.x, pB0.y);
      lowCtx.lineTo(pB1.x, pB1.y); lowCtx.lineTo(pA1.x, pA1.y);
      lowCtx.closePath(); lowCtx.fill();
      continue;
    }
    // Renderiza parede completa (traseira/lateral visível) até WALL_H...
  }
}

// Gate de clique para itens de parede (ex.: parede Leste normal +X -> nyRot = Math.sin(turn))
function getEastWallItemQuad(item, ROOM_R) {
  if (Math.sin(turn) > -0.08) return null; // Parede oculta / culled: desativa cliques!
  const p1 = project(ROOM_R - 0.5, item.y - 24, item.liftZ - 26);
  const p2 = project(ROOM_R - 0.5, item.y + 24, item.liftZ - 26);
  const p3 = project(ROOM_R - 0.5, item.y + 24, item.liftZ + 26);
  const p4 = project(ROOM_R - 0.5, item.y - 24, item.liftZ + 26);
  const projW = Math.max(p1.x, p2.x, p3.x, p4.x) - Math.min(p1.x, p2.x, p3.x, p4.x);
  return projW < 8 ? null : { p1, p2, p3, p4 };
}
```

#### 4. Oclusão Angular de Móveis Ocos (Estantes, Nichos e Balanços)
Móveis com vãos internos (ex.: estantes de 3 nichos) devem possuir fundo (`y = 0`) e painéis laterais (`x = 0..wallThick` e `x = w - wallThick..w - 1`) sólidos na matriz voxel e usar ordenação/culling angular para impedir que itens internos atravessem as paredes laterais ou traseira quando a câmera gira:
```javascript
function drawHollowCabinetWithOcclusion(shelfItem, propsByTier, renderItem) {
  const totalAngle = (shelfItem.selfAngle || 0) + turn;
  const cosFront = Math.cos(totalAngle);
  // Abertura frontal está em +Y (y = H - 1).
  // Se cosFront <= 0.22, a câmera olha de lado ou de trás: fundo e laterais ocluem 100% o interior!
  const isFrontVisible = cosFront > 0.22;

  if (!isFrontVisible) {
    drawShelfSlices(0, shelfItem.model.count - 1);
    for (const prop of propsByTier.top) renderItem(prop); // Só o topo fica visível
    return;
  }

  // Visão frontal/isométrica: desenha por faixas Z intercalando props e sobrepondo paredes laterais
  for (const tier of tiers) { // Ex: [0..13], [14..26], [27..39]
    drawShelfSlices(tier.z0, tier.z1);
    tier.props.sort((a, b) => a.depth - b.depth);
    for (const prop of tier.props) renderItem(prop);
    drawShelfSideWalls(tier.z0, tier.z1, 5); // Redesenha bordas laterais sólidas (wallThick = 5px) por cima
  }
  drawShelfSlices(topZ0, shelfItem.model.count - 1);
  for (const prop of propsByTier.top) renderItem(prop);
}
```

#### 5. Regra Obrigatória de Texto Hi-Res (`Overlay Pass Hi-Res`)
**PROIBIDO** desenhar balões de fala, textos ou emojis dentro do `lowCanvas` (`440x440` ou `480x300`) antes do upscale *nearest-neighbor* — isso pixeliza e borra as letras e pode cortar o balão atrás de paredes/penhascos. Use sempre o fluxo em 3 passos:

1. Durante a passada de render 3D no `lowCanvas`, apenas enfileire `{ lowX, lowY, text }` em `speechQueue`.
2. Faça o `ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height)` no canvas principal da tela.
3. **Depois** do upscale (usando a API vetorial do `ctx` principal em alta resolução, escalando `sx = item.lowX * (canvas.width / LOW_W)` e `sy = item.lowY * (canvas.height / LOW_H)`), desenhe todos os balões de fala com `roundRect`, borda `#3B2219`, fonte nítida (`13px bold`) e rabicho apontando para o personagem. Resultado: texto 100% legível e sempre acima de qualquer penhasco ou mobília!

```javascript
const speechQueue = [];

// Passo 1 (durante o render 3D no lowCanvas): apenas enfileira coordenadas lógicas
function queueSpeechBubble(worldX, worldY, headZ, text) {
  const p = project(worldX, worldY, headZ);
  speechQueue.push({ lowX: p.x, lowY: p.y, text });
}

// Passo 2 + Passo 3 (no loop principal de render):
function renderFrame(ctx, canvas, lowCanvas) {
  // ... renderiza todo o mundo 3D no lowCanvas (chamando queueSpeechBubble) ...

  // 2. Upscale nearest-neighbor do lowCanvas para o canvas principal
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

  // 3. Overlay Pass Hi-Res: desenha textos e balões vetoriais em alta resolução
  const scaleX = canvas.width / LOW_W;
  const scaleY = canvas.height / LOW_H;
  ctx.save();
  ctx.font = 'bold 13px sans-serif';
  ctx.textBaseline = 'middle';

  while (speechQueue.length > 0) {
    const item = speechQueue.shift();
    const sx = item.lowX * scaleX;
    const sy = item.lowY * scaleY;
    const padX = 10;
    const textW = ctx.measureText(item.text).width;
    const boxW = textW + padX * 2;
    const boxH = 26;
    const bx = Math.round(sx - boxW / 2);
    const by = Math.round(sy - boxH - 12);

    // Balão com roundRect e borda #3B2219
    ctx.fillStyle = '#FFFDF7';
    ctx.strokeStyle = '#3B2219';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(bx, by, boxW, boxH, 8);
    ctx.fill();
    ctx.stroke();

    // Rabicho apontando para o personagem
    ctx.beginPath();
    ctx.moveTo(sx - 5, by + boxH - 1);
    ctx.lineTo(sx, by + boxH + 7);
    ctx.lineTo(sx + 5, by + boxH - 1);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Texto nítido em alta resolução
    ctx.fillStyle = '#3B2219';
    ctx.fillText(item.text, bx + padX, by + boxH / 2);
  }
  ctx.restore();
}
```

---

## 3. Paradigm 2: Pixel-Art Gaussian Splatting (Three.js + Spark) *(Referência Legada / Opcional — NÃO usar por padrão neste repositório)*

Based on `cobanov/pixelart-gaussiansplat` and `siliconjungle/shapeshift-labs-ink-studio`.

### Splats as Surfels
- Each Gaussian splat is flattened into a thin disc (*surfel*) lying flat on a geometry surface.
- The splat's rotation quaternion encodes the surface normal.
- Splat spacing `h` with radius `0.66 h` provides seamless surface coverage without holes.

### The Pixel Shader Post-Process Pipeline
To turn 3D Gaussian splats into hand-crafted pixel art:

1. **Hard Disc Splats (`falloff: 0`)**:
   - Disable Gaussian exponential falloff so splats render as solid discs instead of blurry clouds.
2. **Supersampled Coverage Pass (`ss = 2`)**:
   - Render splats at `2x` the target pixel resolution (4 source samples per art pixel).
   - If at least 2 out of 4 samples are solid (`cov >= 0.5`), the art pixel is treated as solid object; otherwise, it is background.
3. **Palette Snapping by Vote (Eliminates Material Blurring)**:
   - Each solid sample snaps to its nearest palette color.
   - The final art pixel takes the **most voted color** among the 4 samples.
   - *Result*: Pixels on the border between two materials never produce an averaged muddy color.
4. **Shader Ink Silhouette Outline**:
   ```glsl
   int n = int(coverage(cell + vec2(1.0, 0.0)) >= 0.5) +
           int(coverage(cell - vec2(1.0, 0.0)) >= 0.5) +
           int(coverage(cell + vec2(0.0, 1.0)) >= 0.5) +
           int(coverage(cell - vec2(0.0, 1.0)) >= 0.5);
   bool edge = (n > 0 && n < 4); // boundary pixel
   if (edge) {
     col = ink(col); // darker shade of its own color with minimum brightness floor
   }
   ```
5. **OKLab Color Matching for Translucent Light & Haze**:
   - Volumetric sun shafts, halos, and smoke are blended in OKLab color space with a penalty against shifting hue (`hueDir`), ensuring light beams remain warm/golden rather than snapping to greenish or purplish greys.
6. **4x4 Bayer Matrix Ordered Dithering**:
   ```glsl
   float bayer(vec2 p) {
     int i = int(mod(p.x, 4.0)) + int(mod(p.y, 4.0)) * 4;
     float m[16] = float[16](
       0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0,
       3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0
     );
     return (m[i] + 0.5) / 16.0;
   }
   ```

---

## 4. Paradigm 3: Software Depth-Buffered Rasterizer (Pure JS) *(Referência Legada / Opcional — NÃO usar por padrão neste repositório)*

Based on `amirmushichge/pixel-plays`.

### Pure JavaScript Software Engine
- Render into an `ImageData(W, H)` via `Uint32Array(image.data.buffer)`.
- Maintain a separate Z-buffer: `const zb = new Float32Array(W * H)`.
- Canvas resolution: typical `360x280` or `320x240`.
- 30-degree isometric projection:
  ```javascript
  const SIN = 0.5, COS = Math.sqrt(3) / 2, R2 = Math.SQRT2;
  function project(x, y, z) {
    const u = (x - y) / R2, v = (x + y) / R2;
    return {
      sx: OX + u * S,
      sy: OY + (v * SIN - z * COS) * S,
      d: v * COS + z * SIN // depth
    };
  }
  ```

### Hue-Shifted Color Ramps
Never shade with pure black or white. Shift hue dynamically:
- **Shadows**: Drift toward cool violet (`COOL = [46, 38, 84]`).
- **Highlights**: Drift toward warm golden yellow (`WARM = [255, 232, 180]`).

### Depth-Buffer Edge Shading
Calculate pixel-art silhouettes and rim lights directly from the depth buffer without costly edge-detection post-filters:
- If a pixel borders an empty background or the ground plane, darken its own silhouette (`tint(i, 0.68, 0.66, 0.76)`).
- If a pixel is in front of another 3D object on the top/left, give it a 1px warm rim highlight (`WARM` mix).

### Stepped Animation Rate (Simulated Hand-Crafted Feel)
- Run wind sway, foliage flutter, and character bobs at **8 FPS** (`const WIND_FPS = 8`).
- Stepped discrete movement feels hand-drawn and stops mathematical floating smoothness from ruining the pixel aesthetic.

### Platform-Aware Pet AI & Spatial Confinement
- **Platform Attachment**: Elevating pets to surface heights (`liftZ = 21` for desks, `liftZ = 61.5` for shelves) while tracking local coordinates (`offX, offY`) so rotating/moving furniture moves occupants seamlessly.
- **Sleep & Rest Loops**: Grounded/elevated resting states (`cat.deskSleepTimer`) ensuring pets placed on surfaces loaf and sleep for an authentic period before choosing to jump down.
- **Avian Shelf Brooding**: Larger birds (Popó) can flutter up to high book shelves to brood (`state = 'brood'`) between props, then flutter down to floor level.
- **Baby Spatial Confinement ("Sanzando sem Cair")**: Vulnerable baby pets (Pintinho Piu) are strictly clamped to platform bounds (`constrainToDesk`, `constrainToShelf`) and never jump down autonomously, wandering safely within perimeter limits.

### Headwear Anatomy & The "Walking Hat" Chick
- **Cranial Anchor Alignment**: Hats must never sit on ear tips. Anchor hats to the skull/forehead crown between ears (`headZ - 2.8`).
- **Avian Comb Offsets**: For animals with combs or crests, tilt hats slightly (~0.18 rad) beside the comb.
- **Oversized Walking Disguise**: Baby chicks wearing oversized hats become a walking hat: the hat model covers the chick with ~88% opacity (showing the warm yellow body inside), while 2 little stick feet waddle underneath and shiny eyes + orange beak peek out from under the front brim.

### Multi-Room Architectural Blueprints & Pet Migration
- **Blueprint Modal ("Modalzinho")**: 2D architectural blueprint map with grid paper styling (`blueprint-container`), displaying connected room cards with live presence indicator ("📍 Você está aqui") and persistent pet badges (`🐱 🐔 🐥`).
- **Seamless Pet Migration**: When transitioning between rooms (either via door click or blueprint modal), pets turn towards the door with happy speech bubbles ("Nya~!", "Có có!", "Piu piu!"), little floating heart bursts, and smooth camera wipe/fade transitions, appearing naturally at the threshold of the next room.
- **Cozy Wall Harmonization**: Placing a door and window on the same wall side-by-side (e.g. Garden Door with glass panes and sunny garden window with flowerbox and animated butterfly) preserves natural lighting continuity, room depth, and architectural believability.
- **Living Room Micro-Interactions**: Sofas allow loafing/sleeping cats with custom nap timers, coffee tables provide sitting/perching surfaces, and tall multi-tier bookshelves offer high roosting spots for adult birds, while strictly confining baby chicks to the safe cushion/table surface.

---

## 5. Verification & Quality Checklist

Before completing any pixel art 3D implementation:

1. [ ] **No Subpixel Shimmering**: During slow camera movement or object rotation, do pixel edges remain completely crisp with zero blurring or shimmering?
2. [ ] **No Slice Striping**: Does every stacked object have a single continuous outer outline rather than visible horizontal slice lines?
3. [ ] **Palette Discipline**: Are all colors strictly snapped to a controlled 4-6 tone palette without intermediate gradient fuzz?
4. [ ] **Depth Sorting**: Do characters, trees, and buildings properly occlude each other based on ground Y coordinates?
5. [ ] **Integer Coordinates**: Are all render coordinates snapped using `Math.round` or integer shifts inside the low-res buffer?
6. [ ] **Reduced Motion Support**: Does the application respect `prefers-reduced-motion` by skipping fast tweens and excessive camera pans?

### Living Room L-Shape Layout & Wall Furniture Rule
1. **Parede Norte (Frente para o Sul / Câmera)**:
   - Móveis retos encostados: Estante de Livros (selfAngle = 0) e TV Rack Retrô (selfAngle = 0).
   - A tela azul e as prateleiras ficam 100% visíveis e voltadas para o interior do cômodo e para a câmera.
2. **Parede Leste (Frente para o Oeste / Interior)**:
   - Sofá Aconchegante encostado sob a janela do jardim (selfAngle = Math.PI / 2).
   - O assento, almofadas e manta ficam voltados para dentro da sala e em direção à TV.
3. **Centro & Tapete 3D**:
   - Mesinha de centro posicionada em frente ao sofá com xícara de café e livro aberto.
   - Tapete Escandinavo em coordenadas 3D de mundo travado exatamente sob a mesinha e os pés do sofá.
4. **Plaquinhas Rústicas sobre os Batentes**:
   - Cada porta de transição possui uma plaquinha artesanal de madeira nobre sobre o batente (liftZ + H + 8): 🍽️ COZINHA, 🛏️ QUARTO, 🌳 JARDIM, 🛋️ SALA.

### Living Room Center-TV Layout & Top-Right Square Minimap Button
1. **Botão da Planta Baixa (Top-Right Square Button)**:
   - Posicionado no canto superior direito (	op: 16px; right: 16px; width: 50px; height: 50px;) em container relativo ao redor do #viewport.
   - Estilizado como um quadradinho fofo (order-radius: 14px, order: 2.5px solid #4F46E5, blur backdrop).
   - Remove a sobrecarga da barra de HUD inferior, melhorando o layout mobile.
2. **Parede das Portas (Norte)**:
   - Mantida livre e desimpedida de móveis volumosos.
   - Centro ocupado pelo **Quadro de Galinhas** (drawLivingRoomArt): moldura rústica, céu azul, sol dourado e a Mama Galinha e o Pintinho no pasto.
3. **Parede da Direita (Leste)**:
   - Sofá Aconchegante encostado sob a janela do jardim (selfAngle = Math.PI / 2).
   - Estante Alta de Livros no canto recuado (x = 118, y = -95, selfAngle = Math.PI / 2).
4. **Centro da Sala**:
   - Tapete Escandinavo em 3D e Mesinha de Centro em carvalho com café e livro na frente do sofá.
   - TV Retrô Vintage posicionada no meio da sala (x = -12, y = 12, selfAngle = -Math.PI / 2), de frente para o tapete e sofá.


---

## 6. Taxonomia e Arquitetura de Classes de Assets

Para garantir escalabilidade, integridade de arrasto e comportamentos autônomos sem bugs, todo elemento do mundo 3D pertence estritamente a uma das seguintes 5 classes:

### 1. Personagens / Pets (`isPet: true`)
- **Exemplos**: Popó (galinha adulta), Pipoca (gatinho calico), Pompom (pintinho amarelo).
- **Propriedades Principais**: `isPet: true`, `isCat: true`, `isChicken: true`, `isChick: true`.
- **Comportamentos**:
  - **IA Autônoma & Máquina de Estados**: `wander`, `peck`, `sit`, `loaf`, `brood`, `sleep`, `perch`, `swing`.
  - **Ciclo de Locomoção Biomecânica em 2 Fases**: Swing (avanço aéreo $+D$) e Stance (apoio no solo $-D$) sincronizados ao vetor de velocidade real (`theta = atan2(vy, vx)`).
  - **Poleiros & Superfícies**: Subida em superfícies elevadas (mesas `liftZ = 21`, estantes `liftZ = 61.5`, balanço de pneu `liftZ = 34`).
  - **Confinamento Infantil ("Bolinha")**: Filhotes (Pompom) são confinados aos limites do móvel onde sobem, sem risco de queda desajeitada.
  - **Migração Coesa entre Cômodos**: Ao mudar de cômodo via portas ou minimapa, os pets se despedem com balões de fala fofos e migram para o novo ambiente.

### 2. Móveis Fixos (`isFixed: true`)
- **Exemplos**: Bancada contínua de ponta a ponta na Cozinha (com pia e fogão embutidos), Geladeira Retrô pastel interativa, Carvalho Centenário massivo no Jardim, Balanço de Pneu vertical ancorado, Canteiros de flores nas bordas perimetrais.
- **Propriedades Principais**: `isFixed: true`, `isMovable: false`, `category: 'furniture'`.
- **Regras no Modo Decoração**:
  - **Não Arrastáveis**: Não podem ser deslocados nem rotacionados pelo jogador no modo Decor, servindo como a âncora arquitetural do cômodo.
  - **Interatividade Especial**: Podem abrir modais dedicados (ex: Geladeira Retrô abre a lista de compras/post-its funcional estilizada como porta de geladeira pastel com ímãs).

### 3. Móveis Móveis (`isMovable: true`)
- **Exemplos**: Mesa de Jantar Quadrada grande, Cadeiras de Jantar, Sofá Aconchegante, TV Retrô central, Cadeira de Varanda rústica, Carrinho de Mão com flores.
- **Propriedades Principais**: `isMovable: true`, `category: 'furniture'`, `radius`, `selfAngle`.
- **Regras & Parenting Hierárquico Sincronizado**:
  - **Arrastáveis e Rotacionáveis**: Podem ser reposicionados e girados no modo Decor.
  - **Parenting Hierárquico Sincronizado (Regra de Ouro)**:
    - Qualquer móvel que sirva de base ou suporte para outros itens (ex: Mesa de Jantar é pai de 4 Cadeiras e da Fruteira; Estante de Livros é pai dos livros em cada prateleira).
    - **Ao arrastar ou rotacionar o móvel pai, todos os filhos se movem e giram juntos**, mantendo suas posições relativas (`offX, offY, liftZ, initialAngle`).
    - **Fórmula de Atualização dos Filhos no Drag do Pai**:
      ```javascript
      const rad = parent.selfAngle;
      child.x = parent.x + child.offX * Math.cos(rad) - child.offY * Math.sin(rad);
      child.y = parent.y + child.offX * Math.sin(rad) + child.offY * Math.cos(rad);
      child.selfAngle = parent.selfAngle + child.initialAngle;
      ```

### 4. Acessórios de Superfície / Props (`isProp: true`)
- **Exemplos**: Fruteira com maçãs/bananas/laranjas, bule de chá e xícaras de cerâmica, livros e tomos encadernados, luminária de cabeceira, vaso de plantas de mesa.
- **Propriedades Principais**: `isProp: true`, `surface: '<parent_id>'`, `offX`, `offY`, `liftZ`, `tier` (para prateleiras múltiplas).
- **Regras**:
  - **Snapping Inteligente de Superfície**: Possuem altura de repouso (`liftZ`) correspondente ao tampo do móvel de apoio.
  - **Deslocamento com o Móvel**: Permanecem colados ao topo do móvel mesmo durante rotações ou deslocamentos da mobília base.

### 5. Itens de Parede e Portas (`isWallItem: true`, `isDoor: true`)
- **Exemplos**: Portas de transição de cômodos com plaquinhas rústicas de batente, Janelas coloniais com cortinas e floreiras, Lousa de Cortiça com post-its coloridos funcionais, Quadros artísticos e Relógios de parede.
- **Propriedades Principais**: `isWallItem: true`, `wall: 'north' | 'west' | 'east' | 'south'`, `isDoor: true`, `targetRoom`.
- **Regras**:
  - **Hitbox 3D Projetada com Wall Culling**: Coordenadas de clique calculadas projetando os 4 vértices do quad 3D da parede na tela. Se a parede estiver de costas para a câmera (`Math.sin(turn) <= 0.05`), o clique é estritamente ignorado.
  - **Placas de Batente**: Cada porta renderiza uma plaquinha estilizada acima do vão com o nome do cômodo de destino.

---

## 7. Regra Canônica de Orientação e Rotação no Código

Para eliminar ambiguidades de móveis virados para a parede de costas para a câmera, adota-se esta convenção geométrica universal para todo o codebase:

### 1. Convenção do Slice Grid 2D
Ao modelar ou programar as fatias horizontais `grid[y][x]` de um voxel model:
- `y = 0`: **TRASEIRA (Back)** do móvel (costas de estantes, parte de trás da geladeira, encosto traseiro do sofá).
- `y = H - 1`: **FRENTE (Front)** do móvel (onde ficam portas, puxadores, ímãs, gavetas, telas de TV, rostos de personagens).
- `x = 0`: Lateral Esquerda.
- `x = W - 1`: Lateral Direita.

### 2. Relação com a Câmera Isométrica
- A câmera padrão do diorama utiliza ângulo `turn = -Math.PI * 0.25` (-45°).
- O ângulo total de rotação na tela é `totalAngle = selfAngle + turn`.
- **Com `selfAngle = 0`**, a face frontal (`y = H - 1`) aponta diretamente para o **Sul-Sudeste**, ou seja, voltada 100% para o interior da sala e para o observador/câmera!

### 3. Tabela Canônica de Orientação por Parede

| Parede de Fixação / Posição | Direção Desejada da Frente | Ângulo Canônico (`selfAngle`) | Resultado Visual |
|---|---|---|---|
| **Parede Norte (`y = -ROOM_R`)** | Voltado para o Sul / Interior da Sala | **`selfAngle = 0`** | Frente totalmente exposta para o jogador e centro do cômodo. |
| **Parede Oeste (`x = -ROOM_R`)** *(Modo Foco no Jogador)* | Voltado para o Sudeste / Câmera | **`selfAngle = 0`** | Portas, gavetas, ímãs e puxadores ficam visíveis em ângulo aberto para o jogador. |
| **Parede Oeste (`x = -ROOM_R`)** *(Modo 90° Perpendicular)* | Voltado para o Leste (+X, centro) | **`selfAngle = Math.PI / 2`** | Móvel fica alinhado estritamente perpendicular à parede Oeste. |
| **Parede Leste (`x = ROOM_R`)** | Voltado para o Oeste (-X, centro) | **`selfAngle = Math.PI / 2`** | Sofá e estantes olham para dentro da sala e em direção à parede Oeste. |
| **Parede Sul (`y = ROOM_R`)** | Voltado para o Norte (-Y, interior) | **`selfAngle = Math.PI`** | Móvel olha de volta para o fundo do diorama. |
| **Centro da Sala (Ponto Focal)** | Orientado ao ponto de interesse | Variável | Ex: TV Retrô no centro voltada para o Sofá (`selfAngle = -Math.PI / 2`). |

---

## 8. Questionário de Concepção de Novos Assets (Checklist Pré-Modelagem)

Antes de escrever qualquer código gerador de fatias (Python/JS) ou modelar um novo asset para o diorama, responda obrigatoriamente a este checklist de 8 perguntas:

1. **Qual é a Categoria Estrita do Asset?**
   - É um *Pet/Personagem*, um *Móvel Fixo* (estrutural), um *Móvel Móvel* (arrastável), um *Prop de Superfície* ou um *Item de Parede/Porta*?
2. **Qual é o Voxel Budget e Dimensões do Grid?**
   - Dimensões exatas em voxels ($W \times D \times H$ fatias).
   - Altura por fatia (`spacing = 1` ou escalonado) e escala global do render (`scale = 1.4` a `2.0`).
3. **Onde está a Frente do Modelo?**
   - A frente (com gavetas, portas, puxadores, telas ou faces) está estritamente localizada em `y = H - 1` e as costas em `y = 0`?
4. **Qual é a Parede ou Ponto Focal e seu `selfAngle` Canônico?**
   - Onde o objeto nasce? Parede Norte (`selfAngle = 0`), Parede Leste (`Math.PI / 2`), Parede Sul (`Math.PI`) ou Parede Oeste (`0` ou `Math.PI / 2`)?
5. **Possui Hierarquia / Filhos Parentados?**
   - Ele carrega outros itens? Se sim, quais os offsets relativos (`offX, offY, liftZ, initialAngle`) de cada filho para que se movam em perfeita sincronia?
6. **Possui Superfície para Apoio de Props ou Pets?**
   - Qual a altura útil do tampo (`surfaceHeight` / `liftZ`)? Há slots específicos para fruteiras, copos, livros ou para o descanso de gatos e galinhas?
7. **É Interativo ao Clique do Jogador?**
   - O que acontece ao clicar? Abre um modal estilizado (ex: Geladeira, Lousa, Livro)? Toca um som retro? Dispara partículas de amor/estrelinhas?
8. **Qual é a Paleta Reduzida e Animações Procedurais?**
   - Máximo de 8 a 12 tons indexados por objeto (sem interpolações frouxas, índice 0 transparente).
   - Tem partes dinâmicas (vapor subindo da panela, pneu balançando no vento, asas batendo, rabo abanando)?

---

## 9. Arquitetura de Persistência de Decoração (3 Slots, LocalStorage & Cloud-Ready)

Para permitir que o jogador decore sua casa e salve seus layouts personalizados:

### 1. Modelo de Dados Serializável (Deco State JSON)
Apenas as posições e rotações de itens móveis e props são salvas (móveis fixos e paredes mantêm coordenadas estruturais):
```typescript
interface SavedFurnitureItem {
  id: string;
  room: 'living' | 'kitchen' | 'bedroom' | 'garden';
  x: number;
  y: number;
  selfAngle: number;
  surface?: string;
  offX?: number;
  offY?: number;
}

interface RoomDecorSlot {
  version: 1;
  slotIndex: number; // 0, 1 ou 2
  slotName: string;  // Ex: "Meu Cantinho Aconchegante"
  updatedAt: string;
  items: SavedFurnitureItem[];
}
```

### 2. Três Slots de Decoração
- **Slot 1**: "Padrão / Original" (com botão de restaurar layout de fábrica).
- **Slot 2**: "Customizado A".
- **Slot 3**: "Customizado B".

### 3. Camada de Abstração Desacoplada (LocalStorage -> Cloud Auth)
- A interface de persistência utiliza um serviço único `DecorStorageService`:
  ```typescript
  const DecorStorageService = {
    async saveSlot(slotIndex: number, name: string, items: SavedFurnitureItem[]) {
      const payload = { slotIndex, slotName: name, updatedAt: new Date().toISOString(), items };
      localStorage.setItem(`pixel_decor_slot_${slotIndex}`, JSON.stringify(payload));
      // Hook preparado para envio à nuvem quando o jogador efetuar login:
      // if (UserAuth.isLoggedIn()) await api.saveCloudDecor(slotIndex, payload);
    },
    async loadSlot(slotIndex: number): Promise<RoomDecorSlot | null> {
      const data = localStorage.getItem(`pixel_decor_slot_${slotIndex}`);
      return data ? JSON.parse(data) : null;
    }
  };
  ```
- Isso garante que a funcionalidade funcione imediatamente no navegador via `localStorage` e fique 100% pronta para a futura integração de autenticação e contas de usuário.

---

## 10. Motor de Terreno Voxel 3D com Relevo, Colisão por Altura e Controle WASD + Pulo

> [!IMPORTANT]
> **Padrão Preferencial para Paisagens Naturais:** Utilize a **Seção 10B (Terreno Micro-Voxel Orgânico em Fatias "Pull-Chain" `1080×1080` com Tight-Crop Bounded Slices)** sempre que criar mapas externos naturais, colinas contínuas, rios sinuosos e falésias orgânicas. A **Seção 10A** abaixo fica preservada como referência para terrenos discretos em blocos geométricos (`16×16`).

### 10B. Terreno Micro-Voxel Orgânico em Fatias ("Pull-Chain" + Tight-Crop Bounded Slices — Padrão Preferencial para Paisagens Naturais)

Arquitetura de relevo contínuo sobre **Pure HTML5 Canvas 2D** (`squash = 0.75`, rotação orbital 360°), substituindo cubões quadriculados de `16×16` por um **heightfield fino `1080 × 1080` micro-voxels com `VOX = 2u`** (`2.160 × 2.160u` de mundo contínuo, proporção **Anti-Kaiju `1.5×`**) fatiado horizontalmente em pixel art orgânica via **Tight-Crop Bounded Slices** (~60 FPS).

#### 1. Heightfield Fino `1080 × 1080` (`VOX = 2u`), Escultura "Pull-Chain" & Regra Anti-Kaiju
Em vez de degraus cúbicos rígidos por tile, o solo é esculpido sobre uma grade densa `Float32Array(1080 * 1080)` com resolução espacial de `2u` por micro-célula através de operadores geológicos em corrente elástica:

- **`fbm2d(x, y, octaves, ...)`**: Ruído fractal multi-oitava (*Fractional Brownian Motion*) aplicado para micro-ondulação orgânica de planícies, bordas de praia, textura de solo e variação natural de declives. Para *domain warping*, use **`fbm2dFast`** (2 oitavas rápidas) visando manter o pré-bake em `1080 × 1080` ágil.
- **`pullHill(cx, cy, radius, height, steepness)`**: Puxa uma colina orgânica usando curva elástica **`cos^steepness`** a partir do raio normalizado, produzindo cumes arredondados e transições suaves sem cantos quadrados.
- **`pullPlateau(cx, cy, radius, height, cliffMask)`**: Eleva platôs e terraços de topo nivelado; quando `cliffMask` está ativo na borda selecionada, mantém encosta abrupta de **falésia rochosa**, enquanto nas demais direções decai suavemente para rampa caminhável.
- **`carveRiverPath(waypoints, width, depth)`**: Escava o leito de rios sinuosos ao longo de curvas contínuas, moldando **margens em degraus suaves** para leitura em pixel art e entrada gradual na água.
- **`elasticChainRelax(iterations)`**: Relaxamento em corrente elástica ("Pull-Chain"): **puxar 1 pixel arrasta os vizinhos em corrente proporcionalmente enquanto o chão ancora e segura a base**, eliminando picos isolados e serrilhados de escultura sem destruir falésias mascaradas.
- **Proporção Mundo vs. Personagem (Anti-Kaiju `1.5×`)**: No mapa `1080 × 1080` (`2.160 × 2.160u`), mantenha folga espacial realista `1.5×` relativa ao personagem (`~18u` de largura, `H = 16u`) para evitar que construções/biomas se espremam e o personagem pareça um gigante: rios principais com largura **`>= 3×`** a largura do personagem (`~54u`); trilhas e alamedas **`>= 2×`**; lagos **`>= 4×`**; e biomas com **`>= 250–400u`** de diâmetro/espaçamento.

##### Kit de 6 Fórmulas Geológicas Procedurais + Primitivas Hidrológicas & Ruínas
Para gerar relevo orgânico com silhuetas geológicas verossímeis em vez de elipses ou discos empilhados:
- **Domain Warping 2-Pass (`warp2d` com `fbm2dFast`)**: $\mathbf{p}' = \mathbf{p} + A \cdot \text{fbm2dFast}(\mathbf{p}f + A\,\text{fbm2dFast}(\mathbf{p}f_1))$ — distorce as coordenadas antes da avaliação de distância para gerar baías, escarpas e penínsulas assimétricas sem elipses visíveis, preservando performance rápida no grid `1080×1080`.
- **Smooth Union / Carve (`smax` / `smin`)**: interpolação polinomial $h = \text{clamp}(0.5 + 0.5(b-a)/k,\, 0,\, 1)$, $\text{smax}(a,b,k) = a + (b-a)h + k\,h(1-h)$ — funde esporões e morros como argila sem vincos duros.
- **Ridged Multifractal & Espinhas (`ridgedFbm` + `pullRidge`)**: cristas em $\sum w_i\,(1 - |\text{noise}|)^2$ ao longo de polilinhas com ramificações naturais em vez de cones/discos isolados.
- **Estratos Rochosos Irregulares (`rockTerrace`)**: degraus suaves com passo modulado por ruído (`step * (1 + 0.22*fbm)`) para falésias geológicas orgânicas.
- **Trilha Recortada na Encosta (`carveBenchTrail`)**: após esculpir a montanha inteira, uma spline 3D recorta uma faixa estreita na própria encosta (`innerW` plano em `MAT_PATH` + `blendWidth` com *smoothstep* no talude), eliminando "panquecas marrons" empilhadas.
- **Erosão Térmica & Gotas Hidráulicas (`thermalAndHydraulicErosion`)**: relaxamento por ângulo de talus (`talus = 4` pedra, `2` terra) + ~260 gotas determinísticas descendo o gradiente formando saias aluviais e sulcos naturais.
- **Lagos Orgânicos (`warp2d`)**: escave bacias lacustres passando as coordenadas por `warp2d` antes do teste radial para criar contornos naturais assimétricos (enseadas e reentrâncias orgânicas) em vez de círculos perfeitos.
- **Blocos de Ruína Desgastados (`pullRuinsBlock`)**: SDF retangular $\max(|dx|/\text{halfW},\, |dy|/\text{halfD})$ com bordas lascadas via `fbm2d` (`* 0.08`), reservado exclusivamente a estruturas antigas e ruínas humanas (`useWarp = false` em `pullPlateau` para fundações retas; todo relevo natural usa o Kit Geológico).
- **Ponte em Arco Parabólico com Vão Real (`addArchBridge` / `getBridgeDeckZ`)**: tabuleiro elevado segundo a parábola $z_{\text{deck}}(u) = z_{\text{base}} + H_{\text{arch}}(1 - (2u - 1)^2)$ para $u \in [0, 1]$, com tabuleiro fino de **`3` fatias** sobre **`MAT_WATER` intacto** (preservando o vão livre sobre a água), pilares apenas nas margens (**`u <= 0.09 || u >= 0.91`**) e guarda-corpos laterais; `getBridgeDeckZ(wx, wy)` retorna a cota contínua do tabuleiro para física e travessia caminhável.

#### 2. Pré-Bake em Tight-Crop Bounded Slices (`terrainSlices[z]`), Água Calma vs. Cachoeira & Grama (`fbm2d`)
Em tempo de inicialização, o heightfield `1080 × 1080` é convertido em fatias horizontais pré-renderizadas:
- **Tight-Crop Bounded Slices (`{ canvas, offX, offY, w, h }`)**: Durante o pré-bake de cada fatia `z`, calcule os limites ocupados `[minX, maxX, minY, maxY]` e aloque o canvas apenas no recorte justo **`{ canvas, offX, offY, w, h }`** escrevendo pixels ABGR via **`Uint32Array`**. Isso evita alocar buffers `1080 × 1080` inteiros para fatias parciais, mantendo a RAM enxuta e **~60 FPS** mesmo na escala `2.160 × 2.160u`.
- **Casca com Espessura `min8 - 2` (Zero Pinholes em 360°)**: Para cada micro-voxel `(gx, gy)` de altura `h`, em vez de preencher apenas a superfície `z = h`, calcula-se `min8` (a menor altura entre os 8 vizinhos imediatos) e preenche-se a coluna da casca de `Math.max(Z_MIN, min8 - 2)` até `h`. Isso garante **zero pinholes** (zero frestas transparentes entre fatias) em qualquer ângulo de câmera `360°`.
- **Água Calma vs. Cachoeira (`h - min8 > 4`)**: Listras verticais de espuma são estritamente restritas a quedas d'água reais onde **`h - min8 > 4`**; lagos elevados, rios calmos e nascentes mantêm superfície cristalina e casca fina (**`max(Z_MIN, h - 1)..h`**) sem espuma artificial.
- **Iluminação Direcional por Gradiente Local**: A cor de cada micro-voxel em `terrainSlices[z]` consulta o gradiente local $(\nabla_x h, \nabla_y h)$ para aplicar destaque ensolarado nas faces voltadas à luz, tom base nos platôs e sombreamento frio/terroso nas contra-encostas e falésias rochosas.
- **Moitas Orgânicas de Grama (`fbm2d`)**: Distribua lâminas de grama `2–3px` (`grassTipSlices`, `noOutline: true`) usando ruído coerente (**`fbm2d > 0.43`**) + hash sem grade, alternando clareiras limpas com moitas vivas animadas ao vento em **8 FPS** (+ *rustle* ao pisar) e evitando padrões quadriculados repetitivos.

#### 3. Renderização Unificada Slice-by-Slice, `entityLayer` (`destination-out`) & Oclusão 360° de Partículas (`particlesByZ`)
Para que personagens, partículas e props gigantes convivam com morros curvos, pontes em arco e portais sem *clipping* nem ordenação quebrada:
1. **Interseção de Janela Visível & Skip em `O(1)`**: No render loop, intersecte a janela visível da câmera com **`[offX..offX+w]`** (e o intervalo `Y` correspondente) de cada fatia `{ canvas, offX, offY, w, h }`, **pulando fatias sem interseção em `O(1)`** e blitando apenas a sub-região `srcRect` visível — mantendo **~60 FPS** estáveis mesmo em mapas `1080 × 1080` (`2.160 × 2.160u`).
2. **Passagem Unificada Slice-by-Slice + `entityLayer`**:
   - Renderiza-se o mundo verticalmente fatia por fatia (`z = Z_MIN .. MAX_Z`), alternando `terrainSlices[z]` + `grassTipSlices` com o buffer auxiliar **`entityLayer`** (onde entidades e estruturas `1:1` são compostas na faixa Z correspondente).
   - As fatias superiores do terreno/arcos aplicam **`globalCompositeOperation = 'destination-out'`** sobre o `entityLayer` para recortar com precisão sub-voxel qualquer parte de entidade oculta atrás de um morro, penhasco ou pilar.
   - Em seguida, aplica-se a **Silhueta Única 1px `#3B2219`** ao contorno externo composto e desenha-se sobre o `lowCanvas`, garantindo **100% de oclusão real atrás de morros e sob arcos/pontes**.
3. **Oclusão 360° de Partículas 3D (`particlesByZ`)**:
   - Agrupe as partículas ativas por **`Math.round(p.z)`** no mapa/array `particlesByZ`.
   - Desenhe cada camada de partículas no `lowCtx` **dentro** do loop *slice-by-slice*, imediatamente após `terrainSlices[z]` (e **nunca** após o fim do loop `z`), garantindo ocultação real atrás de morros, pontes e falésias em `360°` **sem contorno preto**.

#### 4. Física Contínua (`AUTO_STEP_MAX = 5.5`) & Deslizamento Tangencial (`±35°`)
- **Amostragem Contínua**: A altura do solo `getGroundHeight(wx, wy)` interpola o heightfield `1080 × 1080` (`VOX = 2u`) continuamente e considera `getBridgeDeckZ(wx, wy)` para travessia sobre pontes em arco parabólico.
- **Escalabilidade Orgânica (`AUTO_STEP_MAX = 5.5`)**: Subidas suaves com $\Delta Z \le \text{AUTO\_STEP\_MAX}$ (`5.5u`) são escaladas continuamente andando, permitindo subir colinas curvas, pontes em arco e margens em degraus suaves com fluidez.
- **Deslizamento Tangencial (`±35°`) em Encostas Curvas**: Quando o movimento esbarra em uma falésia (`ΔZ > AUTO_STEP_MAX`), borda de rio profundo ou collider sólido, em vez de testar apenas desvios rígidos nos eixos X/Y (que travam em encostas diagonais/curvas), o resolvedor testa rotações incrementais do vetor de movimento em até **`±35°`** ao longo da tangente da curva, deslizando organicamente ao redor de morros e rochedos.
- **Threshold Mínimo de Plataforma (`standableMap` + `cliffTopMap`)**: Pré-computar após `elasticChainRelax()` uma máscara `standableMap` (`Uint8Array`) exigindo área mínima de apoio (`>= 14` de `25` micro-voxels na janela `5×5` com `|Δh| <= 3u`, equivalente a ~`3.7×3.7` pixels, preservando pisos de vale com `h0 - min5 <= 2` e pontes/vitórias-régias, enquanto rejeita degraus estreitos de meio de falésia). `evaluateSupport()` ignora células com `standable === 0` e `checkCollisionAt()` bloqueia contra `cliffTopMap` (pico local `r = 5` da falésia), impedindo escalar paredões verticais usando saliências de `1–2px` como apoio.

---

### 10A. Referência de Terrenos em Blocos Geométricos (Grid Discreto)

Arquitetura clássica para ilhas modulares, escadas em degraus rígidos e tabuleiros em grid (`16×16u` por tile) sobre o mesmo motor **Pure HTML5 Canvas 2D** (`squash = 0.75`, `turn` livre 360°).

### 1. Traversão Back-to-Front em 360° sem `Array.sort` no Grid
Na projeção oficial, a profundidade de uma célula cresce ao longo do vetor da câmera:
$$\text{depth} = \Delta x \cdot \sin(\text{turn}) + \Delta y \cdot \cos(\text{turn})$$

Portanto, a ordem exata de trás para frente (*back-to-front*) em qualquer ângulo `turn` é determinística em $O(W \times H)$ sem nenhuma alocação ou `Array.sort` nos tiles do terreno:

```javascript
const stepX = Math.sin(turn) >= 0 ? 1 : -1;
const stepY = Math.cos(turn) >= 0 ? 1 : -1;

const startX = stepX > 0 ? 0 : GRID_W - 1;
const endX   = stepX > 0 ? GRID_W : -1;
const startY = stepY > 0 ? 0 : GRID_H - 1;
const endY   = stepY > 0 ? GRID_H : -1;

for (let gx = startX; gx !== endX; gx += stepX) {
  for (let gy = startY; gy !== endY; gy += stepY) {
    drawTerrainColumn(gx, gy);
    drawCellBucketEntities(gx, gy); // Desenhadas imediatamente após a coluna!
  }
}
```

### 2. Cell-Bucketing de Entidades + Promoção de Ledge em Pulo
- **Cell-Bucketing**: Cada prop estático e personagem entra no bucket `(gx, gy)` correspondente à célula onde seu pé toca o plano (`gx = clamp(Math.floor(x / TILE), 0, GRID_W - 1)`), sendo desenhado logo após a coluna `(gx, gy)` (com ordenação por `depth` apenas dentro de células que contenham mais de uma entidade).
- **Promoção de Ledge em Pulo**: Quando o personagem está no ar (`!entity.grounded`) próximo a uma borda frontal de degrau onde a célula adjacente em direção à câmera (`(gx + stepX, gy)` ou `(gx, gy + stepY)`) possui altura `h <= entity.z + 2`, promova o bucket do personagem para a célula frontal (`gx + stepX` e/ou `gy + stepY`) em direção à câmera. Isso evita que patas ou parte do corpo sofram *clipping* atrás da quina do degrau recém-saltado.

### 3. Face Culling Vertical e Estratos Geológicos
Para cada coluna `(gx, gy)` com altura de topo `z`:
- **Desenhe apenas as 2 faces verticais voltadas à câmera**:
  - **Face X**: desenhe a face `+X` (`x + TILE`) se `Math.sin(turn) > 0`; caso contrário desenhe a face `-X` (`x`).
  - **Face Y**: desenhe a face `+Y` (`y + TILE`) se `Math.cos(turn) > 0`; caso contrário desenhe a face `-Y` (`y`).
- **Oclusão por Vizinho (`minNeighborZ`)**: Para cada uma das 2 faces visíveis, consulte a altura `neighborZ` da célula adjacente naquela direção (`0` se estiver fora do mapa, formando a "saia" nas bordas externas). Só desenhe o paredão vertical do topo `z` até `minNeighborZ` quando `z > minNeighborZ`.
- **Estratos Geológicos nas Faces Verticais**:
  1. **Borda de grama / musgo pendurada (`~3px`)**: Faixa superior no topo da face (`z` até `z - 3`).
  2. **Terra quente (`soil`)**: Camada intermediária com **sombreamento direcional distinto** entre a face X (tom mais iluminado) e a face Y (tom mais sombreado) para leitura volumétrica imediata.
  3. **Rocha ardósia estratificada (`slate`)**: Camada basal abaixo da terra com listras horizontais de estratificação rochosa.

### 4. Regras de Transponibilidade Calibradas pela Altura do Personagem (`H`)
Sendo `H` a altura física total do personagem em unidades Z do mundo e $\Delta Z = Z_{\text{destino}} - Z_{\text{atual}}$:

| Condição de Altura / Tile | Classificação | Comportamento Físico |
|---|---|---|
| `ΔZ <= 0.4 * H` | **Rampa / Degrau Suave (`AUTO_STEP`)** | Transponível andando automaticamente sem precisar pular. |
| `0.4 * H < ΔZ <= 2.0 * H` | **Degrau de Pulo** | Bloqueia caminhada; transponível com pulo usando `vz = Math.sqrt(2 * g * (2 * H + margin))`. |
| `ΔZ > 2.0 * H` ou `type === 'water'` | **Parede / Água (Intransponível)** | Bloqueia entrada com **deslizamento separado nos eixos X e Y** (testa `X` e `Y` independentemente) + feedback visual/balão (ex.: *"Muito alto!"*, *"Água!"*). |

- **Game Feel de Pulo Obrigatório**:
  - **Coyote Time**: `~0.10s–0.11s` de tolerância após deixar uma borda onde o pulo ainda é aceito.
  - **Jump Buffer**: `~0.12s` de buffer ao pressionar pulo logo antes de aterrissar.

### 5. Controle WASD Relativo à Câmera + Coerência de Direção (`+Y` = Frente)
Com `ix` (`-1` esquerda / `+1` direita) e `iy` (`-1` W / `+1` S) vindos do teclado/D-pad, converta o input para o espaço de mundo invertendo a rotação `turn` da câmera e alinhe à convenção canônica `+Y` (`y = H - 1`) = Frente:

```javascript
const worldMoveX = ix * Math.cos(turn) + iy * Math.sin(turn);
const worldMoveY = -ix * Math.sin(turn) + iy * Math.cos(turn);
const targetAngle = Math.atan2(-worldMoveX, worldMoveY);
```

### 6. Overlay Pass Hi-Res para Balões e Textos de Terreno (NUNCA no `lowCanvas`)
- **Proibido** desenhar balões de fala, textos ou emojis dentro do `lowCanvas` (`440x440` ou `480x300`) antes do upscale *nearest-neighbor* — isso pixeliza/borra as letras e pode cortar o balão atrás de paredes ou penhascos.
- **Padrão Obrigatório (`Overlay Pass Hi-Res`)**:
  1. Durante a passada de render 3D no `lowCanvas`, apenas enfileire `{ lowX, lowY, text }` em `speechQueue`.
  2. Faça o `ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height)` no canvas principal da tela.
  3. **Depois** do upscale (usando a API vetorial do `ctx` principal em alta resolução, escalando `sx = item.lowX * (canvas.width / LOW_W)` e `sy = item.lowY * (canvas.height / LOW_H)`), desenhe todos os balões de fala com `roundRect`, borda `#3B2219`, fonte nítida (`13px bold`) e rabicho apontando para o personagem. Assim o texto fica 100% legível e sempre acima de qualquer penhasco ou mobília!

### 7. 5 Modos de Collider para Props de Terreno (`propColliders`) + Desobstrução de Trilhas
Todo prop colocado sobre o terreno deve declarar explicitamente seu modo em `propColliders`:

| Modo | Geometria / Regra de Colisão | Exemplos |
|---|---|---|
| `'solid'` | Cilindro `(wx, wy, colR, baseZ, colH)` bloqueando quando `cat.z < baseZ + colH - 1.5`. | Árvores altas, faróis, fogueiras, placas, pilares, lanternas. |
| `'box'` | Caixa retangular rotacionada `(halfW, halfD, angle, baseZ, colH)` — permite deslizar rente às paredes retas sem cantos invisíveis. | Cabanas (`cozy_cabin`), barcos (`wood_boat`), casas grandes. |
| `'platform'` | Bloqueia lateralmente abaixo de `topZ - 2` e fornece superfície de pouso sólida no topo `topZ` ao pular. **Atenção**: nunca disparar `AUTO_STEP` se `topZ - cat.z > 4` para props altos. | Cogumelos gigantes, pedras grandes, fardos de feno, tocos de árvore. |
| `'arch'` | Dois cilindros apenas nas colunas laterais, deixando o vão central 100% livre para passar por baixo. | Portal Torii gigante (`torii_gate`). |
| `'none'` | Decorativo atravessável (sem bloqueio físico). | Florzinhas, tufos de grama. |

- **Desobstrução Automática de Trilhas e Escadas**: Implemente um validador explícito em `addProp(...)` que impeça gerar props sólidos (`'solid'`, `'platform'` ou colunas de `'arch'`) sobre células com `type === 'path'`, `type === 'bridge'` ou degraus estreitos de escada, garantindo rotas de circulação sempre livres:

```javascript
function addProp(prop) {
  const gx = clamp(Math.floor(prop.wx / TILE), 0, GRID_W - 1);
  const gy = clamp(Math.floor(prop.wy / TILE), 0, GRID_H - 1);
  const cell = grid[gx][gy];
  const blocksRoute = prop.colliderMode && prop.colliderMode !== 'none';
  if (blocksRoute && (cell.type === 'path' || cell.type === 'bridge' || cell.isNarrowStair)) {
    return false; // Protege trilhas, pontes e escadas estreitas contra obstrução
  }
  props.push(prop);
  return true;
}
```

### 8. Sistema de Lâminas de Grama Voxel (2–3px de Altura no mesmo Sprite Stacking)
Para vegetação baixa densa e leve diretamente no motor de Sprite Stacking:
- **Modelagem em `3–4` fatias finas**:
  - `z = 0`: base verde-escuro `#2F7A2B` dando ancoragem visual sem contorno.
  - `z = 1`: corpo verde médio `#4DB848`.
  - `z = 2..3`: pontinhas `1px` em verde claro `#8BE064`.
- **Renderização com `noOutline: true`**: Sem contorno `#3B2219`, pois `1px` de contorno transformaria uma lâmina fina de `1px` num bloco grosso de `3px`.
- **Pré-cache em 3 frames de vento (8 FPS)** por ângulo quantizado `qAngle`:
  - Desloque as fatias superiores conforme a fase do vento `wf` em `+0.5 * wf`, `+1.0 * wf`, `+1.5 * wf` para `z = 1, 2, 3`.
  - Aplique nos tiles `grass` com onda espacial baseada em `(gx + gy)` + efeito de ***rustle*** (inclinação extra + partícula verde) quando o personagem pisa no tile.

### 9. Proporção Arquitetural em Densidade `1:1` (Estruturas Monumentais)
Para que construções e árvores grandes imponham presença ao lado do personagem (`H = 16u`) no mundo `1080×1080` **sem nunca esticar o `scale` deixando pixels borrados/gigantes**:
- Modele estruturas arquiteturais diretamente em **resolução voxel real monumental (`1.5×`)** mantendo `scale = 1.0` (mesma densidade `1:1` do personagem e do chão):
  - **Cabanas / Casas**: `~5.0×H` (`78×69×81` fatias) com porta aberta de `~33u` de altura.
  - **Faróis / Torres**: `~7.9×H` (`51×51×126` fatias) com base octogonal, varanda e cúpula luminosa.
  - **Portais / Arcos (`torii_gate`)**: `~5.0×H` (`75×24×81` fatias) com vão central livre superior a `3×H` de altura.
  - **Árvores Monumentais (`pine_tree` / `sakura_oak`)**: `~4.5×H` (`pine_tree` `42×42×72` fatias) a `~6.4×H` (`sakura_oak` `81×81×102` fatias).
- Quantize o cache de pré-render dessas estruturas gigantes em passos de `3°` (`Math.round((turn * 180 / Math.PI) / 3) * 3`) para garantir rotação orbital fluida a 60 FPS mesmo com `72–126` fatias.
- **Compressão RLE em Linha Base-36 (`*ch<len>;`)**: para embutir pacotes voxel monumentais dentro de HTMLs autocontidos de arquivo único de forma leve (~75% menor no JSON sem penalizar o tempo de decodificação de `buildSliceSheet`), comprima repetições consecutivas de um mesmo caractere Base-36 em cada linha usando o marcador `*<ch><len>;` e expanda na inicialização do `buildSliceSheet`.

---

## 11. Guia Rápido de Prompt para Qualquer IA Reproduzir o Padrão

Copie e cole este bloco como instrução base ao pedir para qualquer IA criar novos assets, cômodos, personagens ou terrenos neste repositório:

```text
REGRAS INEGOCIÁVEIS DO PROJETO (Pure Canvas 2D Sprite Stacking):
1. TECNOLOGIA: Use EXCLUSIVAMENTE HTML5 Canvas 2D puro (ctx.imageSmoothingEnabled = false), buffer offscreen em baixa resolução + upscale inteiro e matrizes voxel JSON geradas em Python. PROIBIDO usar Three.js, WebGL, shaders ou bibliotecas 3D externas.
2. MODELAGEM PYTHON -> JSON: Gere cada modelo com make_grid(w, h, fill=0), fill_box(...) e to_strings(slices) retornando list[list[str]] (NUNCA concatene todas as linhas de uma fatia em uma única string). Suporte base-36 ('0'..'9','a'..'z'), '0' transparente, y=0 TRASEIRA e y=H-1 FRENTE.
3. RENDER & SILHUETA: Use squash = 0.75, drawStackObject com totalAngle = selfAngle + turn, e contorno único 1px (#3B2219 ou #3B2A20) via canvas offscreen após empilhar todas as fatias (PROIBIDO contornar fatias individuais).
4. PAREDES & MÓVEIS OCOS: Use Wall Culling dinâmico (nyRot = nx*sin(turn) + ny*cos(turn) > 0.05 -> rodapé 3px + desativar hitbox) e oclusão angular em estantes/nichos (fundo + laterais sólidas + redesenho de paredes laterais por tier quando cosFront > 0.22).
5. TERRENO & FÍSICA (se aplicável): Para paisagens naturais, prefira o Motor Micro-Voxel Orgânico 1080x1080 ("Pull-Chain", VOX=2u = 2.160x2.160u, Anti-Kaiju 1.5x; rios >= 3x largura do personagem ~54u, trilhas >= 2x, lagos >= 4x, biomas >= 250-400u): escultura via fbm2d/fbm2dFast/pullHill(cos^steepness)/pullPlateau(cliffMask; useWarp=false apenas em ruínas/estruturas humanas)/carveRiverPath/elasticChainRelax + Kit de 6 Fórmulas Geológicas (warp2d com fbm2dFast, smax/smin, ridgedFbm/pullRidge, rockTerrace, carveBenchTrail, thermalAndHydraulicErosion) + addArchBridge/getBridgeDeckZ (z_deck(u) = z_base + H_arch*(1-(2u-1)^2), tabuleiro 3 fatias sobre MAT_WATER intacto, pilares u <= 0.09 || u >= 0.91 + guarda-corpos) + lagos orgânicos (warp2d) + listras de espuma restritas a quedas reais (h - min8 > 4; lagos/nascentes com superfície cristalina max(Z_min, h-1)..h) + pullRuinsBlock (max(|dx|/halfW, |dy|/halfD) com bordas lascadas fbm2d * 0.08), pré-bake em Tight-Crop Bounded Slices ({canvas,offX,offY,w,h} via Uint32Array) com casca min8-2 + iluminação por gradiente + moitas orgânicas de grama 2-3px (fbm2d > 0.43 + hash sem grade, noOutline, 8 FPS), render slice-by-slice com interseção da câmera e skip em O(1) + entityLayer (destination-out + silhueta única 1px #3B2219) + particlesByZ (agrupar por Math.round(p.z) e desenhar no lowCtx dentro do loop após terrainSlices[z], sem contorno preto) e física contínua (AUTO_STEP_MAX=5.5 + deslizamento tangencial ±35° + threshold mínimo de plataforma standableMap/cliffTopMap >= ~3.7x3.7 micro-voxels na janela 5x5). Para terrenos em blocos discretos (16x16), use traversão back-to-front O(W*H) via stepX/stepY, cell-bucketing, face culling até minNeighborZ e WASD relativo à câmera com targetAngle = Math.atan2(-worldMoveX, worldMoveY).
```
