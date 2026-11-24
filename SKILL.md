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

| Requirement | Recommended Paradigm | Key Technologies |
|---|---|---|
| **Simple web gallery, cozy dioramas, social media reels, lightweight mini-games** | **Sprite Stacking** | Canvas 2D, Vite + TypeScript, OffscreenCanvas |
| **Full 3D orbit camera, imported GLTF/GLB rigged characters, organic SDF sculpture** | **Pixel-Art Gaussian Splatting** | Three.js, Spark, WebGL 2, GLSL Post-process |
| **Isometric fixed camera, zero dependencies, single-file games, procedural geometry** | **Software Depth Rasterizer** | Pure JS, Canvas 2D ImageData, Float32Array Z-buffer |

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
3. **Low-Res Offscreen Buffer + Integer Upscale**:
   - Never render directly to high-res display pixels.
   - Render the scene into an offscreen canvas at logical resolution (e.g. `270x480` for 9:16 mobile reels, `320x180` or `480x270` for landscape).
   - Upscale onto the screen canvas by an integer multiplier (`x2`, `x3`, `x4`) with `imageSmoothingEnabled = false`.
   - Snap all entity coordinates to integer values (`Math.round`) inside the low-res buffer to stop subpixel jitter and shimmering.
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

---

## 3. Paradigm 2: Pixel-Art Gaussian Splatting (Three.js + Spark)

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

## 4. Paradigm 3: Software Depth-Buffered Rasterizer (Pure JS)

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
