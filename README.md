# 🎨 `pixel-art-3d` — Skill de Pixel Art 3D & Sprite Stacking (Pure HTML5 Canvas 2D)

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demos-brightgreen?logo=github)](https://ruishalm.github.io/PixelArtSkill/)
[![Tech](https://img.shields.io/badge/HTML5-Canvas%202D%20Puro-E34F26?logo=html5&logoColor=white)](https://ruishalm.github.io/PixelArtSkill/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Vanilla%20JS)-blue)](#)
[![No WebGL](https://img.shields.io/badge/3D%20Engine-No%20WebGL%20%2F%20No%20Three.js-orange)](#)
[![Skill](https://img.shields.io/badge/Antigravity-pixel--art--3d%20Skill-purple)](./SKILL.md)

> **`pixel-art-3d`** ([`SKILL.md`](./SKILL.md)) é uma skill de engenharia para agentes de IA criarem **cenas, objetos, personagens, dioramas e mundos abertos 3D/pseudo-3D** em **HTML5 Canvas 2D puro** usando **Sprite Stacking (fatiamento voxel no eixo Z)** — com **zero WebGL, zero Three.js e zero dependências externas em runtime**, gerando arquivos HTML totalmente autocontidos a ~60 FPS.

---

## ⚡ Como Instalar & Usar

### Caminho da Skill
- **Global (Antigravity):** `~/.gemini/config/skills/pixel-art-3d/SKILL.md`
- **Local (este repositório):** [`./SKILL.md`](./SKILL.md)

### Fluxo Padrão em 3 Passos
1. **Gerador Python (`make_grid` / `fill_box` / `to_strings`)**: modela cada asset em fatias horizontais `slices[z][y][x]` com paleta Base-36 (`'0'..'9'`, `'a'..'z'`).
2. **Pacote JSON Base-36 / Heightfield**: exporta `{ "palette": [...], "slices": [[...]] }` (ou terreno procedural `1080×1080` diretamente no gerador).
3. **HTML5 Canvas 2D Autocontido**: injeta os dados no template da engine (`imageSmoothingEnabled = false`), aplicando buffer *low-res*, upscale inteiro `1:1` e **Overlay Pass Hi-Res** para UI e textos.

### Prompt Rápido Copiável

```text
REGRAS INEGOCIÁVEIS DO PROJETO (Pure Canvas 2D Sprite Stacking):
1. TECNOLOGIA: Use EXCLUSIVAMENTE HTML5 Canvas 2D puro (ctx.imageSmoothingEnabled = false), buffer offscreen em baixa resolução + upscale inteiro e matrizes voxel JSON geradas em Python. PROIBIDO usar Three.js, WebGL, shaders ou bibliotecas 3D externas.
2. MODELAGEM PYTHON -> JSON: Gere cada modelo com make_grid(w, h, fill=0), fill_box(...) e to_strings(slices) retornando list[list[str]] (NUNCA concatene todas as linhas de uma fatia em uma única string). Suporte base-36 ('0'..'9','a'..'z'), '0' transparente, y=0 TRASEIRA e y=H-1 FRENTE.
3. RENDER & SILHUETA: Use squash = 0.75, drawStackObject com totalAngle = selfAngle + turn, e contorno único 1px (#3B2219 ou #3B2A20) via canvas offscreen após empilhar todas as fatias (PROIBIDO contornar fatias individuais).
4. PAREDES & MÓVEIS OCOS: Use Wall Culling dinâmico (nyRot = nx*sin(turn) + ny*cos(turn) > 0.05 -> rodapé 3px + desativar hitbox) e oclusão angular em estantes/nichos (fundo + laterais sólidas + redesenho de paredes laterais por tier quando cosFront > 0.22).
5. TERRENO & FÍSICA (se aplicável): Para paisagens naturais, prefira o Motor Micro-Voxel Orgânico 1080x1080 ("Pull-Chain", VOX=2u = 2.160x2.160u, Anti-Kaiju 1.5x): escultura via fbm2d/fbm2dFast/pullHill(cos^steepness)/pullPlateau(cliffMask; useWarp=false apenas em ruínas)/carveRiverPath/elasticChainRelax + Kit de 6 Fórmulas Geológicas (warp2d com fbm2dFast, smax/smin, ridgedFbm/pullRidge, rockTerrace, carveBenchTrail, thermalAndHydraulicErosion) + addArchBridge/getBridgeDeckZ (z_deck(u) = z_base + H_arch*(1-(2u-1)^2), tabuleiro 3 fatias sobre MAT_WATER, pilares u <= 0.09 || u >= 0.91 + guarda-corpos) + lagos orgânicos (warp2d) + espuma apenas em h - min8 > 4 (água calma max(Z_min, h-1)..h, sem espuma estática pintada no poço) + pullRuinsBlock (max(|dx|/halfW, |dy|/halfD) com fbm2d * 0.08), pré-bake em Tight-Crop Bounded Slices ({canvas,offX,offY,w,h} via Uint32Array) com casca min8-2 + iluminação por gradiente + moitas orgânicas de grama 2-3px (fbm2d > 0.43 + hash sem grade, noOutline, 8 FPS), render slice-by-slice com skip em O(1) + entityLayer (destination-out + silhueta única 1px #3B2219) + particlesByZ (Math.round(p.z) desenhadas dentro do loop após terrainSlices[z], sem contorno preto) + Mecânica de Fluidos 2.5D (WindField com altBoost e sombra ∇h·W<0; WaterFlow/sampleWaterFlow tangente com Dipolo de Rankine sobre getActiveWaterObstacles em cache por frame para boulders/ruin_pillar/logs/Character(r) dividindo floatingItems + wake foam e flowStreaks pool 180 integrados por Midpoint RK2 com estêncil de 5 pontos e cisalhamento por deflect + Drain Sink obrigatório via smoothstep até u->0 e despawn; waterfallSim conservativo 40x26 WF_CELL=4 por tubos virtuais 4-vizinhos sobre carga h+bedZ com supressão lateral em falésias latGain=0.025/latDamp=0.45 para vão seco real entre jatos bifurcados, inflow, plunge-pool sink no WaveBuffer e wfBlockH reconstruído por rebuildWaterfallBlocks() com estilhaçamento limpo de isDamBoulder; MAT_SHALLOW=8 standable=1 em margens/vaus/poços com isWetMat, arrasto 0.86x, wake ripples/splash e zero dano; WaveBuffer 120x80 a 30 Hz com margens !isWetMat + máscara sólida de obstáculos u=0, advecção semi-Lagrangiana upwind de waveCurr formando esteiras de Kelvin em V, borda esponja 6 células γ=0.72 vs 0.955 + cutoff |u|<0.008->0 no loop Z-slice em z=-2/13) e física contínua (AUTO_STEP_MAX=5.5 + deslizamento tangencial ±35° + standableMap/cliffTopMap 5x5). Para terrenos discretos (16x16), use traversão back-to-front O(W*H) via stepX/stepY, cell-bucketing, face culling até minNeighborZ e WASD relativo à câmera com targetAngle = Math.atan2(-worldMoveX, worldMoveY).
6. TAXONOMIA DE 6 CLASSES & FOLHAGEM REATIVA (isCharacter / isFoliage): Classifique todo asset estritamente em uma das 6 classes oficiais: Character (isCharacter, humanos/NPCs/animais/criaturas; alias legado isPet), Fixed (isFixed), Movable (isMovable), Surface Prop (isProp), Wall/Portal (isWallItem/isDoor) ou Foliage (isFoliage com rigidity 0..1, windScale, pushRadius, pushStrength, leafColors). Para Foliage, aplique Flexão Parabólica em Balanço Δp(s_z) = (s_z/(H-1))^2 * b (base s_z=0 cravada no solo, sem rotacionar/borrar pixels), Mola Amortecida a = k_stiff*(W(x,y,t)*windScale*(1-rigidity) - b) + F_push(entidades) - c_damp*v, e acoplamento Fluido<->Folhagem: personagens desprendem folhas/pétalas para particlesByZ (WindField), e pétalas que tocam MAT_WATER viram floatingItems levados por WaterFlow até o Drain Sink.
7. DESTRUIÇÃO PROCEDURAL (Destructible & zCut): Sem modelar sprites de queda separados, divida o mesmo slice sheet em base fixa (0..zCut-1 -> collider 'platform') e topo dinâmico (zCut..count-1), suportando 'chop' (pêndulo invertido 3D com 3ª Lei de Newton — queda na direção do golpe + recuo no personagem), 'crumble' (base lascada 'platform' + stone_chunk; em isDamBoulder estilhaço limpo sem toco nem resíduo em wfBlockH + rebuildWaterfallBlocks()) e 'trim' (mola Foliage + nuvem no WindField), acionados por KeyR ou clique no canvas (KeyQ/KeyE para girar, KeyC para spawn) com multiplicador 2x por ferramenta (tool_axe, tool_pickaxe, tool_hoe).
```

---

## 🧭 O que há na Skill (`SKILL.md`)

1. **Seletor de Paradigma (Pure Canvas 2D Obrigatório)**: define *Sprite Stacking* sobre Canvas 2D (`imageSmoothingEnabled = false`) como única arquitetura oficial, proibindo Three.js/WebGL/GLSL no fluxo padrão.
2. **Taxonomia Estrita de 6 Classes de Assets**:

   | # | Classe | Flag Canônica | Papel Estrutural & Comportamento |
   |---|---|---|---|
   | 1 | **Character** | `isCharacter` *(compat. `isPet`)* | Humanos, NPCs, animais e criaturas; locomoção biomecânica em 2 fases (*Swing* + *Stance*) e sub-pilhas rígidas articuladas (sem cisalhamento horizontal de fatias). |
   | 2 | **Fixed** | `isFixed` | Âncoras arquiteturais e cenográficas protegidas contra arrasto. |
   | 3 | **Movable** | `isMovable` | Móveis reposicionáveis e rotacionáveis com **Parenting Hierárquico Sincronizado** (filhos rotacionam e transladam solidários ao pai). |
   | 4 | **Surface Prop** | `isProp` | Objetos de superfície com encaixe automático na cota `liftZ` do suporte pai. |
   | 5 | **Wall / Portal** | `isWallItem` / `isDoor` | Itens de parede, janelas e portas com hitbox 3D projetada e bloqueio automático quando a parede é ocultada. |
   | 6 | **Foliage** | `isFoliage` | Vegetação reativa (`rigidity` `0..1`, `windScale`, `pushRadius`, `pushStrength`, `leafColors`) com flexão parabólica em balanço, mola amortecida (`WindField` + entidades) e desprendimento de folhas/pétalas para `particlesByZ` e `floatingItems`. |
3. **Convenção Canônica de Eixos (`+Y = Frente`)**: `y = 0` é a traseira, `y = H - 1` é a frente do modelo, `z = 0..D-1` cresce da base ao topo; tabela exata de `selfAngle` por parede (`0`, `π/2`, `π`, `-π/2`) para câmera padrão em `-45°`.
4. **Formato Python → JSON Base-36 & RLE (`*ch<len>;`)**: helpers `make_grid(w, h, fill=0)`, `fill_box(...)` e `to_strings(slices)` retornando obrigatoriamente `list[list[str]]` (nunca string única achatada), com índice `'0'` transparente e `'1'..'z'` indexando até 35 cores; pacotes monumentais suportam compressão RLE por linha (`*<ch><len>;`) reduzindo o JSON em ~75% sem perda de velocidade no `buildSliceSheet`.
5. **Silhueta Única `1px` & Exceção de Vegetação**: dilatação ortogonal `[-1,0],[1,0],[0,-1],[0,1]` em canvas auxiliar após empilhar todo o objeto (`#3B2219` ou `#3B2A20`, nunca preto puro e nunca por fatia individual); lâminas de grama `2–3px` usam `noOutline: true` para não virarem blocos de `3px`.
6. **Wall Culling & Oclusão Angular**: colapso de paredes frontais (`nyRot > 0.05`) para rodapé `3px` com desativação de cliques, e oclusão por faixas Z em móveis ocos (`cosFront > 0.22`) redesenhando paredes laterais sólidas sobre props internos.
7. **Motor de Terreno `1080×1080` (`VOX = 2u` = `2.160×2.160u`), Anti-Kaiju `1.5×` & Arquitetura `1:1` Monumental**: escultura *Pull-Chain*, Kit Geológico de 6 fórmulas, *Tight-Crop Bounded Slices*, oclusão `destination-out` via `entityLayer`, partículas 3D `particlesByZ`, pontes em arco parabólico, lagos orgânicos vs. quedas d'água, ruínas SDF e estruturas em densidade `1:1` real sem esticar `scale` (edificações `~5.0×H` a `~7.9×H`, arcos `~5.0×H` com vão `> 3×H`, árvores `~4.5×H` a `~6.4×H`).
8. **5 Modos de Collider de Props**: `'solid'` (cilindro), `'box'` (caixa rotacionada), `'platform'` (pouso superior sem `AUTO_STEP` indevido), `'arch'` (dois pilares laterais com vão livre) e `'none'` (decorativo), além de desobstrução automática de trilhas/pontes em `addProp`.
9. **Overlay Pass Hi-Res & Responsividade `1:1`**: textos e balões vetoriais (`roundRect`) sempre desenhados após o upscale *nearest-neighbor* no canvas principal, preservando pixels perfeitamente quadrados em qualquer viewport.
10. **Checklist Pré-Modelagem de 8 Etapas & Persistência**: questionário obrigatório antes de gerar assets (categoria, voxel budget, frente em `y = H - 1`, `selfAngle`, hierarquia, superfície `liftZ`, interatividade e paleta/animação) + camada `DecorStorageService` em 3 slots.

---

## 🧮 Fórmulas Matemáticas & Engenharia Completa da Engine

### 1. Projeção 3D (`project`) & Projeção Inversa (`unproject` / `unprojectToGrid`)
Dado $(\Delta x, \Delta y, \Delta z) = (w_x - \text{cam}_x,\, w_y - \text{cam}_y,\, w_z - \text{cam}_z)$ e o ângulo orbital da câmera $\theta = \text{turn}$ (com $\text{squash} = 0.75$ no padrão oficial, nunca $< 0.60$):

$$r_x = \Delta x \cos\theta - \Delta y \sin\theta, \qquad r_y = \Delta x \sin\theta + \Delta y \cos\theta$$

$$s_x = c_x + r_x, \qquad s_y = c_y + r_y \cdot \text{squash} - \Delta z, \qquad \text{depth} = r_y$$

- **Projeção Inversa (`unproject` / `unprojectToGrid`)**: mapeia coordenadas da tela $(p_x, p_y)$ de volta ao plano $Z$ (para drag & drop e cálculo da sub-região visível do grid `1080×1080`):

$$r_x = p_x - c_x, \qquad r_y = \frac{p_y - \big(c_y - (z - \text{cam}_z)\big)}{\text{squash}}$$

$$\Delta x = r_x \cos\theta + r_y \sin\theta, \qquad \Delta y = -r_x \sin\theta + r_y \cos\theta$$

$$g_x = \frac{\text{cam}_x + \Delta x}{\text{VOX}} + \text{HALF\_GRID}, \qquad g_y = \frac{\text{cam}_y + \Delta y}{\text{VOX}} + \text{HALF\_GRID}$$

### 2. Wall Culling Dinâmico & Oclusão Angular de Móveis Ocos
- **Wall Culling Dinâmico**: para cada parede de normal unitária $(n_x, n_y)$:

$$n_{y,\text{rot}} = n_x \sin\theta + n_y \cos\theta > 0.05$$

  Quando verdadeiro, a parede volta-se para a câmera, colapsa para rodapé de `3px` (`z = 0..3`) e desativa os hitboxes de cliques nos itens montados nela.
- **Oclusão Angular de Móveis Ocos** (abertura frontal em $+Y$):

$$\cos(\text{selfAngle} + \theta) > 0.22$$

  Se $> 0.22$, intercala fatias por faixa Z, props internos ordenados por `depth` e redesenho das laterais sólidas (`wallThick`); se $\le 0.22$, o fundo e as laterais ocluem 100% do interior.

### 3. Controles WASD Relativos à Câmera & Direção Canônica (`+Y` = Frente)
Dado o vetor de entrada em tela $(i_x, i_y)$:

$$\text{moveWorld}_x = i_x \cos\theta + i_y \sin\theta, \qquad \text{moveWorld}_y = -i_x \sin\theta + i_y \cos\theta$$

$$\text{targetAngle} = \operatorname{atan2}(-\text{moveWorld}_x,\, \text{moveWorld}_y)$$

Alinha estritamente a face frontal canônica (`y = H - 1`) ao vetor real de deslocamento sem inversões de eixo.

### 4. Física Vertical (`H = 16u`), Plataforma Mínima (`standableMap`) & Deslizamento (`±35°`)
- **Cinemática de Pulo (`H = 16u`, `g = 1200`)**:

$$v_0 = \sqrt{2g(2H + \text{margem})} = \sqrt{2 \cdot 1200 \cdot 35.0} \approx 289.8\,\text{u/s}$$

  Atinge ápice de `~35u`, com **`AUTO_STEP_MAX = 5.5u`** para subidas orgânicas caminhando, **Coyote Time (`0.11s`)** e **Jump Buffer (`0.13s`)**.
- **Plataforma Mínima (`standableMap` + `cliffTopMap`)**: janela **`5×5`** exigindo **`nearCount >= 14`** de `25` micro-voxels não-água com $|h_v - h_0| \le 3\text{u}$, com **guarda de piso de vale** ($h_0 - \min_5 \le 2$) e rejeição de saliências estreitas de falésia (`max3 - h0 > 4 && h0 - min3 > 4`), complementada por `cliffTopMap` em raio **`r = 5`**.
- **Deslizamento Tangencial (`±35°`)**: ao colidir com falésias ou bordas de água após tentativa nos eixos X/Y, rotaciona o vetor de movimento em até **`±35°`** para deslizar suavemente ao longo de encostas curvas.

### 5. Tight-Crop Slices, Casca `min8 - 2`, Gradiente, Grama, Upscale `1:1`, Hi-Res Overlay & `particlesByZ`
- **Tight-Crop Bounded Slices & Skip em $O(1)$**: cada fatia pré-assada `{ canvas, offX, offY, w, h }` em `Uint32Array` recorta apenas o bounding box ocupado; no render, `unprojectToGrid` intersecta a janela visível e pula fatias fora da tela em $O(1)$, intercalando `entityLayer` (`destination-out` + silhueta única `1px` `#3B2219`).
- **Casca Anti-Pinhole (`min8 - 2`)**: preenche cada coluna de $[\max(Z_{\min}, \min_8 - 2),\, h]$ para zero frestas transparentes em 360°.
- **Iluminação Direcional por Gradiente Local**:

$$\nabla_x h = h_R - h_L, \qquad \nabla_y h = h_D - h_U, \qquad \text{sunShade} = \operatorname{clamp}\!\left(\operatorname{round}\big((-\nabla_x h - \nabla_y h)\cdot 1.4\big),\, -22,\, 22\right)$$

- **Grama em Moitas (`fbm2d > 0.43`)**: lâminas `2–3px` (`noOutline: true`) distribuídas por ruído coerente + hash sem grade e animadas em **8 FPS** (`Math.floor(t * 8)`).
- **Upscale Inteiro `1:1` & Hi-Res Overlay Pass**:

$$\text{pixelScale} = \operatorname{clamp}\!\left(\left\lfloor \frac{\min(W, H)}{260} \right\rfloor,\, 2,\, 4\right), \qquad \text{LOW\_W} = \left\lceil \frac{W}{\text{pixelScale}} \right\rceil, \qquad \text{LOW\_H} = \left\lceil \frac{H}{\text{pixelScale}} \right\rceil$$

  Após `drawImage(lowCanvas, 0, 0, canvas.width, canvas.height)` com `imageSmoothingEnabled = false`, todos os balões e textos são desenhados em alta resolução no `ctx` principal.
- **Oclusão 360° de Partículas 3D (`particlesByZ`)**: partículas são agrupadas por **`Math.round(p.z)`** e renderizadas no `lowCtx` **dentro** do loop *slice-by-slice* imediatamente após `terrainSlices[z]` (nunca após o fim do loop `z`), garantindo ocultação real atrás de morros e falésias sem contorno preto.
- **Proporção Arquitetural Monumental `1:1` (`1.5×`) & Compressão RLE (`*ch<len>;`)**: estruturas monumentais preservam `scale = 1.0` ao lado do personagem (`H = 16u`) em resoluções reais (`~5.0×H` em `78×69×81` com porta `~33u`, `~7.9×H` em `51×51×126`, arcos `torii_gate` `~5.0×H` em `75×24×81` com vão `> 3×H`, e árvores de `~4.5×H` `42×42×72` a `~6.4×H` `81×81×102`), com pré-render quantizado em passos de `3°` e compressão RLE por linha (`*<ch><len>;`) reduzindo o JSON em ~75% sem custo perceptível no `buildSliceSheet`.

### 6. Kit de 6 Fórmulas Geológicas Procedurais
1. **Domain Warping 2-Pass (`warp2d` com `fbm2dFast`)**:

$$\mathbf{p}' = \mathbf{p} + A \cdot \text{fbm2dFast}\!\big(\mathbf{p}f + A\,\text{fbm2dFast}(\mathbf{p}f_1)\big)$$

2. **Smooth Union / Carve (`smax` / `smin`)**:

$$h = \operatorname{clamp}\!\left(0.5 + \frac{0.5(b - a)}{k},\, 0,\, 1\right), \qquad \text{smax}(a, b, k) = a + (b - a)h + k\,h(1 - h)$$

$$\text{smin}(a, b, k) = a + (b - a)h' - k\,h'(1 - h'), \qquad h' = \operatorname{clamp}\!\left(0.5 - \frac{0.5(b - a)}{k},\, 0,\, 1\right)$$

3. **Ridged Multifractal & Espinhas (`ridgedFbm` + `pullRidge`)**:

$$\text{ridgedFbm}(\mathbf{p}) = \sum_i w_i\,\big(1 - |\text{noise}_i(\mathbf{p})|\big)^2$$

4. **Estratos Rochosos Irregulares (`rockTerrace`)**:

$$\text{step}_{\text{eff}} = \text{step} \cdot \big(1 + 0.22 \cdot \text{fbm}(\mathbf{p})\big)$$

5. **Trilha Recortada na Encosta (`carveBenchTrail`)**: aplica spline 3D após esculpir o maciço, mantendo faixa interna plana `innerW` em `MAT_PATH` e talude em `blendWidth` com *smoothstep* ($3t^2 - 2t^3$).
6. **Erosão Térmica & Gotas Hidráulicas (`thermalAndHydraulicErosion`)**: relaxamento por ângulo de talus (`talus = 4` pedra, `2` terra) + `~260` gotas determinísticas descendo o gradiente.

### 7. Ponte em Arco Parabólico, Lagos Orgânicos, Cachoeiras & Blocos de Ruína SDF
- **Ponte em Arco Parabólico com Vão Real (`addArchBridge` / `getBridgeDeckZ`)**:

$$z_{\text{deck}}(u) = z_{\text{base}} + H_{\text{arch}}\,\big(1 - (2u - 1)^2\big), \qquad u \in [0, 1]$$

  Tabuleiro fino de **`3` fatias** sobre **`MAT_WATER` intacto**, pilares restritos às margens (**`u <= 0.09 || u >= 0.91`**) e guarda-corpos laterais.
- **Lagos Orgânicos (`warp2d`) & Água Calma vs. Cachoeira (`h - min8 > 4`)**: bacias de lagos deformadas via `warp2d` para contornos naturais; listras verticais de espuma aplicadas estritamente onde **`h - min8 > 4`** (quedas d'água reais), mantendo lagos elevados e nascentes com superfície cristalina (**`max(Z_min, h - 1)..h`**).
- **Blocos de Ruína Desgastados (`pullRuinsBlock`)**: distância retangular SDF com lascas procedurais nas bordas via `fbm2d`:

$$d_{\text{rect}} = \max\!\left(\frac{|dx|}{\text{halfW}},\, \frac{|dy|}{\text{halfD}}\right) + 0.08 \cdot \text{fbm2d}(x, y)$$

### 10. Mecânica de Fluidos (`WindField`, `sampleWaterFlow` + Dipolo de Rankine, `waterfallSim`, `MAT_SHALLOW` & `WaveBuffer` 2D)
- **Campo de Vento Vetorial (`WindField`)**:

$$\mathbf{W}(x,y,t) = \mathbf{W}_{\text{base}} + \mathbf{W}_{\text{gust}}\sin(\mathbf{k}\cdot\mathbf{p} - \omega t) + A_{\text{turb}}\,\text{fbm}(\mathbf{p}f - \mathbf{v}_w t) + \sum_i \mathbf{I}_i e^{-d^2/r^2}$$

  Modulado por ganho de altitude (**`altBoost`**) e **sombra topográfica de paredões (`∇h · W < 0`)**, reduzindo o vento a sotavento de falésias enquanto impulsiona lâminas de grama e partículas em `particlesByZ`.
- **Correnteza (`WaterFlow` / `sampleWaterFlow`), Dipolo de Rankine & Sumidouro (*Drain Sink*)**:

$$\mathbf{u}(\mathbf{p}) = \mathbf{u}_0 + \sum_k \frac{r_k^2}{\|\mathbf{d}_k\|^4}\Big(\|\mathbf{d}_k\|^2\mathbf{u}_0 - 2(\mathbf{u}_0\cdot\mathbf{d}_k)\mathbf{d}_k\Big), \qquad \mathbf{u}_{\text{eff}}(\mathbf{p}) = \mathbf{u}(\mathbf{p}) \cdot \operatorname{smoothstep}(d_{\text{sink}}) \xrightarrow[d_{\text{sink}} \to 0]{} \mathbf{0}$$

  - **Fluxo Potencial por Dipolo de Rankine (`sampleWaterFlow`) & Linhas de Corrente RK2 (`flowStreaks`, pool `180`)**: deflexão analítica ao redor de obstáculos cilíndricos (`boulders`, pilares de margem `ruin_pillar`, `logs` e `Character` vadeando em `MAT_SHALLOW` com raio `r`) fornecidos por **`getActiveWaterObstacles`** (em cache por frame), dividindo `floatingItems`, desprendendo espuma de esteira (*wake foam*) e integrando **`flowStreaks`** (pool `180`) por **Runge-Kutta de 2ª ordem (Midpoint RK2)** diretamente em `sampleWaterFlow`, com estêncil detector de obstáculo em 5 pontos para partir linhas de fluxo e modulação de cor/opacidade no cisalhamento de proa/flanco pela deflexão normalizada **`deflect`**.
  - **Advecção & Escoamento (*Drain Sink*)**: partículas e `floatingItems` seguem $\mathbf{p}_{t+\Delta t} = \mathbf{p}_t + \mathbf{u}_{\text{eff}}(\mathbf{p}_t)\,\Delta t$ com **atenuação obrigatória por *smoothstep* até zero (`u -> 0`)** na foz/mar aberto (ou centro de lago) seguida de *despawn*, evitando acúmulo infinito.
- **Cachoeira Conservativa por Tubos Virtuais (`waterfallSim` `40×26`, `WF_CELL = 4`)**:
  - Solver local conservativo em grade `40×26` (`WF_CELL = 4`) com fluxos nos **4 vizinhos** conduzidos pelo gradiente de carga hidráulica total ($H = h + \text{bedZ}$), fonte de entrada (*inflow source*) no topo e sumidouro no poço de impacto (*plunge-pool sink*) conectado ao `WaveBuffer`. Em declives íngremes de falésia, a **supressão de tubos laterais** (**`latGain = 0.025`**, **`latDamp = 0.45`**) impede sangramento transversal artificial na queda vertical para que rochas intactas esculpam um vão de rocha seca real entre jatos bifurcados; qualquer espuma estática pintada no poço é removida para que a espuma de base siga apenas os jatos vivos.
  - Acoplado dinamicamente a `Destructible` pela grade **`wfBlockH`**: obstáculos dividem a lâmina d'água e, quando uma rocha de represa (**`isDamBoulder`**) é fragmentada (`'crumble'` via `tool_pickaxe`), ela estilhaça completamente (sem toco remanescente nem obstrução residual em `wfBlockH`) e **`rebuildWaterfallBlocks()`** reconstrói `wfBlockH` para que a queda volte a convergir.
- **Água Rasa Caminhável (`MAT_SHALLOW = 8`)**:
  - Faixas de praia, vaus de rio e bordas de poço com **`standable = 1`** (zero dano/respawn), integradas ao `WaveBuffer` via **`isWetMat`** (`MAT_WATER` / `MAT_SHALLOW`), aplicando arrasto de vadeio **`0.86×`** ao `Character`, marolas direcionais de esteira (*wake ripples*) e partículas de respingo.
- **Buffer Local de Ondas 2D (`WaveBuffer` `120×80`, 30 Hz)**:

$$u_{t+1}(x,y) = \left(\frac{u(x-1,y) + u(x+1,y) + u(x,y-1) + u(x,y+1)}{2} - u_{t-1}(x,y)\right)\cdot\gamma$$

  Simulado localmente à janela da câmera em **30 Hz** com margens secas (`!isWetMat`) e máscara sólida de obstáculos (`getActiveWaterObstacles`) impondo **$u = 0$** (reflexão natural enquanto `MAT_SHALLOW` propaga ondas), **advecção semi-Lagrangiana *upwind*** (deslocamento de `waveCurr` a montante ao longo do fluxo) convertendo anéis estáticos em **esteiras de Kelvin em V a jusante**, **camada esponja nas 6 células de borda** (**$\gamma = 0.72$** vs **$\gamma = 0.955$** no interior + cutoff **`|u| < 0.008 -> 0`**) e renderizado **dentro do loop Z-slice (`z = -2` / `13`)** para oclusão 3D real.

### 11. Folhagem Reativa (`Foliage` / `isFoliage`): Flexão Parabólica, Mola Amortecida & Acoplamento Fluido
Propriedades da 6ª classe oficial: `isFoliage: true`, `rigidity` (`0..1`), `windScale`, `pushRadius`, `pushStrength`, `leafColors`.

1. **Flexão Parabólica em Balanço (*Cantilever Slice Bend*)**:

$$\Delta\mathbf{p}(s_z) = \left(\frac{s_z}{H - 1}\right)^2 \mathbf{b}$$

   Base (`s_z = 0`) fica 100% cravada no solo enquanto a copa se curva suavemente sem rotacionar ou borrar pixels.

2. **Mola Amortecida + Interferência (`WindField` & Entidades)**:

$$\mathbf{a} = k_{\text{stiff}}\big(\mathbf{W}(x,y,t)\cdot \text{windScale}\cdot(1 - \text{rigidity}) - \mathbf{b}\big) + \mathbf{F}_{\text{push}}(\text{entidades}) - c_{\text{damp}}\,\mathbf{v}$$

   Integra a deflexão $\mathbf{b}$ combinando vento local ponderado por `windScale * (1 - rigidity)` e empurrão radial $\mathbf{F}_{\text{push}}$ de personagens (`Character`) dentro de `pushRadius` com intensidade `pushStrength`.

3. **Acoplamento Fluido ↔ Folhagem**: personagens abrindo caminho desprendem folhas/pétalas (`leafColors`) para `particlesByZ` (conduzidas pelo vento `WindField`), e pétalas que tocam `MAT_WATER` viram `floatingItems` levados pela correnteza `WaterFlow` até o ponto de escoamento (*Drain Sink*).

### 12. Destruição Procedural de Componentes (`zCut`, Pêndulo Invertido & Fratura)
- **Divisão por Fatia de Corte (`zCut`)**: sem duplicar *slice sheets*, o mesmo modelo é particionado em base/toco fixo (**`0 .. zCut - 1`**, convertido dinamicamente em collider `'platform'`) e parte superior dinâmica (**`zCut .. count - 1`**).
- **Modo `'chop'` (Árvores — Pêndulo Invertido 3D)**:

$$\ddot{\phi} = \frac{3g}{2L}\sin(\phi) \quad (\phi_0 = 0.08 \to \pi/2), \qquad \Delta z = s_z - z_{\text{cut}}$$

$$x(s_z) = x_0 + \Delta z\sin(\phi)\hat{d}_x, \qquad y(s_z) = y_0 + \Delta z\sin(\phi)\hat{d}_y, \qquad z(s_z) = z_{\text{cut}} + \Delta z\cos(\phi)$$

  Cada fatia $s_z$ é projetada e desenhada **dentro do loop *slice-by-slice*** (oclusão 3D real); ao atingir o solo, dispara folhas da própria paleta (`particlesByZ`), gera onda no `WaveBuffer` caso caia na água e solta `wood_log` quicando com gravidade e correnteza.
- **Modo `'crumble'` (Estruturas/Ruínas/Pedras)**: preserva a base lascada `0 .. zCut - 1` como `'platform'`, fratura o topo em fragmentos balísticos (`stone_chunk`) e poeira amostrada da própria paleta; em rochas de represa de cachoeira (**`isDamBoulder`**), estilhaça completamente sem deixar toco remanescente nem obstrução residual em `wfBlockH` e dispara **`rebuildWaterfallBlocks()`** (`tool_pickaxe`).
- **Modo `'trim'` (Folhagem Baixa)**: aplica vibração elástica forte na mola da `Foliage` e colhe a copa em nuvem de pétalas/folhas conduzidas pelo `WindField`.
- **Ação & Multiplicadores de Ferramenta (`KeyR` / Clique = Ação / `KeyQ` & `KeyE` = Girar / `KeyC` = Spawn)**: `tool_axe` (`2×` em `'chop'`), `tool_pickaxe` (`2×` em `'crumble'`), `tool_hoe` (`2×` em `'trim'`) e interação padrão sem ferramenta (`1×` em todos os modos).

---

## 🎮 Exemplos Gerados com a Skill (Live Demos)

| Demo | Módulo Demonstrado da Skill | Link |
|---|---|---|
| **Terreno Micro-Voxel `1080×1080`** | Engine *Pull-Chain*, Tight-Crop Bounded Slices, `sampleWaterFlow` (dipolo de Rankine), `waterfallSim` (`wfBlockH`), `MAT_SHALLOW`, `Foliage`, `Destructible` (`zCut`) e Overlay Hi-Res | [examples/terrain-world.html](https://ruishalm.github.io/PixelArtSkill/examples/terrain-world.html) |
| **Diorama Multi-Ambientes** | *Wall Culling*, oclusão angular de móveis ocos, drag & drop por `unproject`, *Parenting Hierárquico* e persistência em 3 slots | [`index.html` / `examples/room-3d.html`](https://ruishalm.github.io/PixelArtSkill/) |
| **Modelo Voxel Quadrúpede** | Fatiamento Base-36 em 16 fatias, rotação orbital 360°, `squash = 0.75` e silhueta única `1px` | [examples/cat-3d.html](https://ruishalm.github.io/PixelArtSkill/examples/cat-3d.html) |
| **Modelo Voxel Articulado** | Sub-pilhas rígidas anti-cisalhamento e ciclo de locomoção biomecânica em 2 fases (*Swing* / *Stance*) | [examples/chicken-3d.html](https://ruishalm.github.io/PixelArtSkill/examples/chicken-3d.html) |

---

## 🚀 Como Rodar Localmente

Zero build, zero npm, zero WebGL:

```bash
git clone https://github.com/ruishalm/PixelArtSkill.git
cd PixelArtSkill
python -m http.server 8088
# Abra http://localhost:8088/index.html ou http://localhost:8088/examples/terrain-world.html
```

Para regenerar as demos HTML a partir das matrizes voxel em `assets/voxels/`, execute os scripts em `scripts/`:

```bash
python scripts/generate_terrain_world.py
```

---

## 📂 Estrutura do Repositório

```text
PixelArtSkill/
├── .github/workflows/deploy.yml   # GitHub Pages: deploy contínuo automático na main
├── .gitignore
├── LICENSE
├── README.md                      # Documentação oficial, fórmulas matemáticas e guia da skill
├── SKILL.md                       # Antigravity Skill blindada (regras, fórmulas e prompt)
├── index.html                     # Ponto de entrada padrão (GitHub Pages)
├── docs/
│   └── sprite-stacking-prompt-guide.md
├── examples/                      # Demos autocontidas geradas com a skill
│   ├── terrain-world.html
│   ├── room-3d.html
│   ├── cat-3d.html
│   └── chicken-3d.html
├── scripts/                       # Geradores e bundlers Python portáteis (leem src/ e assets/voxels → escrevem examples/)
│   ├── generate_terrain_world.py  # Bundler zero-dependency de src/terrain-world/ → examples/terrain-world.html
│   ├── generate_terrain_props.py
│   ├── generate_mega_room.py
│   ├── generate_kitchen_and_garden_packs.py
│   ├── generate_living_room_pack.py
│   ├── generate_modular_furniture.py
│   ├── generate_full_3d_room.py
│   ├── generate_room.py
│   ├── generate_html.py
│   ├── generate_chicken_html.py
│   └── build_chicken_slices.py
├── src/
│   └── terrain-world/             # Módulos JS limpos (shell.html + 01..06: geologia, fluidos, folhagem, render)
├── tests/
│   └── test_physics_invariants.py # Suíte automatizada de packs voxel, sintaxe JS e invariantes físicos (Python + Node)
└── assets/
    ├── voxels/                    # 13 matrizes/packs JSON Base-36 (cabana, torii, ferramentas, móveis...)
    └── previews/                  # 15 imagens de referência e renders de validação
```

---

## 🗺️ Roadmap — Próximas Fórmulas & Física de Materiais

Baliza de evolução do laboratório de **funções matemáticas aplicadas a voxels** em Pure HTML5 Canvas 2D:

- [x] **Geração Procedural por Seed (`WORLD_SEED` + `--seed`)**: PRNG determinístico (*Mulberry32* no JS + `set_seed(seed)` / `--seed` em `generate_terrain_props.py`), parâmetro `?seed=<N>` na URL e botão `🎲 Seed` no HUD variando o `fbm2d`, contornos orgânicos, meandros do rio, lagos, cordilheiras e **árvores procedurais únicas** (troncos curvos, galhos lenhosos e copas assimétricas em `pine_tree` e `sakura_oak`), mantendo `seed=1337` como mapa clássico.
- [x] **Termodinâmica, Fogo & Combustão**: equação de difusão de calor ($\alpha\nabla^2 T + \beta(\mathbf{W}\cdot\nabla T) - \lambda T$) + umidade ($M$) e combustível finito (`fuel`) acoplados ao `WindField` (vento inclina brasas em `particlesByZ`) e `MAT_WATER` / `MAT_SHALLOW` (água zera $T$ e solta vapor), com a `campfire` servindo de fonte térmica (conforto próximo e *3-blink* ao pisar direto).
- [x] **Empuxo de Arquimedes & Acoplamento Onda ↔ Corpo Rígido**: `wood_log`, `stone_chunk` e `floatingItems` lendo altura $u(x,y)$ e gradiente $\nabla u$ do `WaveBuffer` (`sampleWaveHeightAndGrad`): toras boiam e oscilam com as ondas devolvendo micro-impulsos ao buffer, enquanto pedras afundam até o leito.
- [ ] **Viscosidade & Fluidos Não-Newtonianos ($\nu \nabla^2 \mathbf{u}$)**: difusão viscosa de momento e escoamento lento para lama, mel ou lava (acoplada à temperatura $T$ — quanto maior $T$, menor a viscosidade $\nu(T)$).
- [x] **Matéria Granular & Re-Bake Incremental (*Dirty Rect*)**: areia (`MAT_SAND`) e neve (`MAT_PEAK`) com ângulo de repouso dinâmico (`talus = 2`/`3` em `relaxGranularBox`), pegadas de impacto e escavação (`KeyR` / `tool_hoe`), atualizando apenas o retângulo sujo nas `terrainSlices[z]` via `rebakeTerrainDirtyRect`.
- [x] **Tecidos, Cordas & Pontes Pênseis (Integração de Verlet)**: cadeias de nós 3D (`verletChains` — varal de bandeirinhas na Vila, fitas do Portal Torii, flâmula do Farol e cipó da Árvore Sakura) acopladas ao `WindField` e empurrão do `Character`, renderizadas por fatia Z com oclusão 3D real.
- [ ] **Streaming de Chunks (`Web Worker` + `OffscreenCanvas`)**: opcional para mundos abertos contínuos maiores que `1080×1080`, mantendo apenas a janela `3×3` de chunks pré-assados em RAM a 60 FPS.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte [`LICENSE`](./LICENSE) para mais detalhes.
