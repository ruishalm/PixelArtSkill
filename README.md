# 🐾 PixelArtSkill — 3D & Pseudo-3D Pixel Art Multi-Room Engine & Antigravity Skill

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-brightgreen?logo=github)](https://ruishalm.github.io/PixelArtSkill/)
[![Tech](https://img.shields.io/badge/HTML5-Canvas%202D-E34F26?logo=html5&logoColor=white)](https://ruishalm.github.io/PixelArtSkill/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Vanilla%20JS)-blue)](#)
[![No WebGL Required](https://img.shields.io/badge/3D%20Engine-No%20WebGL%20%2F%20No%20Three.js-orange)](#)
[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Custom%20Skill-purple)](https://ruishalm.github.io/PixelArtSkill/)

> **Engine de Pixel Art 3D e Mansão Diorama Interativa Multi-Ambientes** construída 100% em **HTML5 Canvas 2D puro**, utilizando **Sprite Stacking (Fatiamento Voxel Z)**, rotação orbital 360°, projeção inversa para drag & drop com parenting hierárquico sincronizado, IA comportamental de pets, oclusão dinâmica de paredes e navegação por planta baixa arquitetural. Inspirado no universo aconchegante de *PurrModoro*, *The Sims* e *Animal Crossing*.

---

## 🎮 Live Demos (Jogue no Navegador!)

* 🏡 **[Diorama Multi-Ambientes Completo (room-3d.html / index.html)](https://ruishalm.github.io/PixelArtSkill/)**: Navegue livremente pelos 4 cômodos (Quarto, Sala de Estar, Cozinha e Jardim Externo), decore no modo Drag & Drop e interaja com os pets e murais!
* 🏔️ **[Vale Felino 3D — Terreno Micro-Voxel Orgânico 720×720 ("Pull-Chain") (terrain-world.html)](https://ruishalm.github.io/PixelArtSkill/terrain-world.html)**: Paisagem contínua **720×720 micro-voxels (`VOX = 2u` = `1.440×1.440u`, `4×` mais área)** com **Tight-Crop Bounded Slices** (~50 MB RAM, 60 FPS), 8 biomas com proporção **Anti-Kaiju**, 2 cabanas na Vila, ~60 pinheiros, 7 cogumelos gigantes, 20 peixes dourados, grama em moitas orgânicas (`fbm2d`), oclusão unificada via `destination-out`, NPCs vivos (Popó e Pintinhos), balões vetoriais Hi-Res e controle **WASD + `Shift` (Sprint) + Espaço (pulo 2×H)**.
* 🐱 **[Visualizador Anatômico do Gatinho 3D (cat-3d.html)](https://ruishalm.github.io/PixelArtSkill/cat-3d.html)**: Modelo quadrupedal de 16 fatias do gatinho com olhões expressivos e orelhas empinadas.
* 🐔 **[Visualizador da Galinha Popó 3D (chicken-3d.html)](https://ruishalm.github.io/PixelArtSkill/chicken-3d.html)**: Modelo rechonchudo da galinha com crista, bico articulado anti-cisalhamento e ciclo de bicadas.

---

## 🗺️ Os 4 Cômodos do Diorama Interativo

Navegue clicando nas portas 3D com placas rústicas de madeira nobre ou abrindo o botão de **Planta Baixa (Minimapa 🗺️)** no canto superior direito:

```
                  ┌──────────────────────┐
                  │   🌳 Jardim Externo   │
                  │ (Carvalho & Balanço) │
                  └──────────▲───────────┘
                             │ Porta Norte
                             ▼
┌──────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│    🛏️ Quarto     │◄────►│  🛋️ Sala de Estar    │◄────►│     🍽️ Cozinha       │
│  (Setup & Cama)  │      │ (TV, Sofá & Estante) │      │(Mesa, Fogão & Gelad.)│
└──────────────────┘      └──────────────────────┘      └──────────────────────┘
```

1. **🛏️ Quarto Aconchegante**:
   * Cama quentinha, lousa de cortiça com post-its funcionais interativos, estante modular e setup workstation de carvalho (laptop, tablet digitalizador, caneca fumegante, pilha de livros).
   * Relógio de parede cilíndrico sincronizado com o horário real do seu sistema e janela com nuvens volumétricas em parallax.

2. **🛋️ Sala de Estar Retrô**:
   * Sofá aconchegante de veludo com manta bordada, tapete escandinavo 3D, mesa de centro com café e livro aberto.
   * TV retrô com tela azul e rack de madeira no centro da sala.
   * Estante imponente de livros com 3 nichos fechados por painéis de nogueira maciça (anti-clipping lateral e traseiro).
   * Quadro temático de galinhas no campo e janela colonial com vista ensolarada para o jardim.

3. **🍽️ Cozinha Pastel & Café**:
   * Bancada contínua de ponta a ponta na parede Norte com pia de aço inox, cooktop e forno embutidos sob a janela.
   * **Geladeira Retrô Pastel**: Interativa ao clique, abre um modal estilizado em formato de porta de geladeira com ímãs de frutas e lista de compras funcional com post-its.
   * Mesa de jantar quadrada maciça e espaçosa com 4 cadeiras e fruteira central de cerâmica (maçãs, bananas e laranjas).
   * Aparador rústico com gaveteiros e bule de louça na parede Oeste.

4. **🌳 Jardim Externo & Céu Aberto**:
   * Piso de grama viva com flores coloridas perimetrais ao longo de todas as bordas do diorama.
   * **Carvalho Centenário Gigante**: Árvore com tronco massivo de 72x64 fatias e copa frondosa com brotos cor-de-rosa.
   * **Balanço de Pneu Vertical**: Suspenso no galho horizontal da árvore por uma única corda trançada, onde a galinha Popó sobe para balançar no vento!
   * Fachada colonial da casa com janela com floreiras, arbustos e cadeira de varanda aconchegante.
   * Paredes substituídas por um horizonte panorâmico de céu azul infinito e nuvens ensolaradas.

---

## 🏔️ Vale Felino 3D — Motor de Terreno Micro-Voxel Orgânico `720×720` ("Pull-Chain" + Tight-Crop Bounded Slices) (`terrain-world.html`)

Mapa aberto contínuo dobrado em **`720×720` micro-voxels (`VOX = 2u` = `1.440×1.440u`, `4×` mais área)**, substituindo blocos quadriculados por relevo orgânico fatiado horizontalmente sobre o motor **Pure HTML5 Canvas 2D**:
- **Escultura "Pull-Chain" & Kit de 6 Fórmulas Geológicas**:
  - **Colinas Suaves Escaláveis (`pullHill` + `elasticChainRelax`)**: Elevações orgânicas com curva elástica `cos^steepness` e relaxamento em corrente (puxar 1 pixel arrasta vizinhos proporcionalmente enquanto o chão ancora), gerando morros curvos e caminháveis.
  - **Falésias Rochosas Naturais (`pullPlateau` + `cliffMask` + `fbm2d`)**: Terraços nivelados com paredões rochosos abruptos nas bordas mascaradas e iluminação direcional calculada pelo gradiente local de altura (`useWarp = false` reservado apenas a ruínas/estruturas humanas).
  - **Kit de 6 Primitivas Geológicas Procedurais**: Combina **Domain Warping 2-Pass (`warp2d`)**, **Smooth Union/Carve (`smax`/`smin`)**, **Espinhas Multifractais (`ridgedFbm` + `pullRidge`)**, **Estratos Rochosos (`rockTerrace`)**, **Trilha Recortada na Encosta (`carveBenchTrail`)** sobre spline 3D e **Erosão Térmica & Gotas Hidráulicas (`thermalAndHydraulicErosion`)** para substituir "panquecas" e círculos uniformes por relevo geológico natural.
  - **Rio Sinuoso (`carveRiverPath`) & Proporção Mundo vs. Personagem (Anti-Kaiju)**: Rios principais largos (`>= 3×` a largura do personagem, `~54u`), trilhas `>= 2×`, lagos `>= 4×` e biomas espaçados em `>= 250–400u` para que construções e paisagens respirem sem encolher o mundo.
- **8 Biomas Conectados em Escala Ampla**: Vila da Clareira com **2 Cabanas** & Galinha Popó NPC, Campos de Girassol (2 Pintinhos Piu e Fardos de Feno), Circuito das Ruínas Antigas, Praia Dourada (Píer, Vitórias-Régias e Farol), Jardim Zen com Portal Torii (atravessável pelo vão central), Rio Cristalino com 2 Pontes, Bosque com **~60 Pinheiros** e **7 Cogumelos Gigantes** saltitantes (chapéus sólidos até `Z=40`) e Montanha do Pico Sakura (`Z=96`) com cachoeira dupla animada.
- **Estruturas Monumentais em Escala Real (`1:1` Pixel Density)**: Construções modeladas em voxel real grande sem zoom artificial (`Cabana 52×46×54` `3.4×H`, `Farol 34×34×84` `5.25×H`, `Portal Torii 50×16×54`, `Sakura 54×54×68`, `Pinheiros 28×28×48`, `Pilares 18×18×34`, `Guarda-Sol 28×28×28` e `Barco 34×20×12`).
- **Tight-Crop Bounded Slices (`terrainSlices[z]`) & Oclusão Unificada via `destination-out`**:
  - Durante o pré-bake, calcula `[minX, maxX, minY, maxY]` de cada fatia `z` e aloca apenas o recorte justo `{ canvas, offX, offY, w, h }` via `Uint32Array` com espessura `min8 - 2` (**zero pinholes** em `360°`).
  - No render loop, intersecta a janela visível da câmera com `[offX..offX+w]` e pula fatias fora da tela em **`O(1)`**, mantendo **~50 MB de RAM e 60 FPS** mesmo no mapa `4×` maior.
  - Renderização unificada *slice-by-slice* intercalada com `entityLayer`, usando `globalCompositeOperation = 'destination-out'` e silhueta única `1px` (`#3B2219`) para **100% de oclusão** atrás de morros e sob arcos (como o Portal Torii).
- **23 Modelos Voxel & Grama em Moitas Orgânicas (`fbm2d`)**: Lâminas de grama `2–3px` (`grassTipSlices`, `noOutline`) distribuídas via ruído coerente (`fbm2d > 0.43`) + hash sem grade, alternando clareiras limpas com moitas vivas animadas em 3 frames de vento a **8 FPS** + *rustle* sob as patas do gato.
- **Balões Hi-Res & Responsividade 1:1**: Textos desenhados no `ctx` vetorial após o upscale garantindo letras nítidas (zero pixelização) e pixels 100% quadrados tanto em desktop widescreen quanto em celular vertical (com D-Pad touch).
- **Física Contínua Calibrada pela Altura do Gato (`H = 16u`) & 5 Modos de Collider**:
  - `ΔZ ≤ AUTO_STEP_MAX` (`5.5u`): Colinas orgânicas e margens suaves escaláveis andando continuamente.
  - `5.5u < ΔZ ≤ 2.0H`: Degraus e plataformas transponíveis com pulo (`Espaço` = pico `~35u`, Coyote Time & Jump Buffer).
  - `ΔZ > 2.0H` (falésias) ou **Água**: Intransponíveis com **deslizamento tangencial (`±35°`)** ao longo de encostas curvas e aviso visual do gato.
  - **Colliders em Props**: `'solid'` (troncos, farol), `'box'` (paredes retangulares da cabana e barco), `'platform'` (cogumelos, fardos, tocos, pedras), `'arch'` (2 pilares laterais no Torii) e `'none'` (flores/grama).
- **20 Peixes Dourados, Minimapa Topográfico (`720×720`) & Controles**: Botão `🧭 Viagem` rápida pelos marcos principais, toast de descoberta dos 8 biomas, `W A S D` / Setas relativos à câmera, **`Shift` para Sprint**, `Espaço` para pular `2×H`, `Q`/`E` ou arraste do mouse para girar 360°, `M` para miar e `R` para voltar ao Spawn.

---

## ✨ Arquitetura & Taxonomia de Classes de Assets

O ecossistema implementa rigorosamente a taxonomia descrita na skill oficial [SKILL.md](./SKILL.md):

| Classe | Descrição | Exemplos | Comportamento no Modo Decor |
| --- | --- | --- | --- |
| **🐾 Pets / Personagens** | Entidades autônomas vivas com IA, ciclo de 2 fases e poleiros | Popó (galinha), Pipoca (gato), Pompom (pintinho) | Caminham, descansam, sobem em mesas/balanço e migram de cômodo |
| **🧱 Móveis Fixos (`isFixed`)** | Estruturas arquiteturais âncoras do cômodo | Bancada da cozinha, geladeira retrô, carvalho gigante, canteiros | **Imóveis e protegidos contra arrasto**; podem abrir modais ao clique |
| **🛋️ Móveis Móveis (`isMovable`)** | Mobília reposicionável com suporte a *Parenting Hierárquico* | Mesa de jantar, cadeiras, sofás, carrinho de mão, estante | **Arrastáveis e rotacionáveis (tecla R)**; movem todos os filhos juntos |
| **🍎 Props / Superfície (`isProp`)** | Acessórios de tampo e prateleira com snapping inteligente | Fruteira, notebook, bule de chá, xícaras, livros, luminária | Snapping automático de altura (`liftZ`) e sincronizados ao móvel pai |
| **🚪 Parede e Portas (`isWallItem`)** | Portas de transição, janelas, lousas e quadros | Portas rústicas com plaquinha, janela do jardim, lousa de post-its | Hitbox 3D na parede com culling automático se de costas para a câmera |

---

## 📐 Regras Canônicas de Orientação e Rotação

Para garantir que novos móveis nunca fiquem de costas para a câmera ou virados para a parede:

* **Convenção das Fatias Voxel (`grid[y][x]`)**:
  * `y = 0`: **Traseira (Costas)** do móvel.
  * `y = H - 1`: **Frente** do móvel (portas, puxadores, gavetas, telas, ímãs e rostos).
* **Ângulos Canônicos por Parede** (com câmera padrão em `-45°`):
  * **Parede Norte (`y = -ROOM_R`)**: `selfAngle = 0` (frente voltada para o Sul / centro do cômodo).
  * **Parede Oeste (`x = -ROOM_R`)**: `selfAngle = 0` (foco aberto para a câmera) ou `Math.PI / 2` (perpendicular para o Leste).
  * **Parede Leste (`x = ROOM_R`)**: `selfAngle = Math.PI / 2` (voltado para o Oeste / centro).
  * **Parede Sul (`y = ROOM_R`)**: `selfAngle = Math.PI` (voltado para o Norte / fundo).

---

## 📋 Checklist Pré-Modelagem para Novos Assets

Antes de gerar qualquer novo modelo para a engine, siga o questionário de 8 etapas do [SKILL.md](./SKILL.md):

1. **Categoria**: Pet, Fixo, Móvel, Prop de Superfície ou Item de Parede?
2. **Voxel Budget & Dimensões**: Largura $\times$ Profundidade $\times$ Altura de fatias.
3. **Frente do Modelo**: A frente rica em detalhes está em `y = H - 1` e costas em `y = 0`?
4. **Parede & Ângulo Canônico**: Posição e `selfAngle` segundo a tabela canônica.
5. **Parenting Hierárquico**: O objeto carrega outros itens? Quais os offsets relativos (`offX, offY, liftZ`)?
6. **Superfície de Apoio**: Qual o `liftZ` útil para descanso de pets ou apoio de props?
7. **Interatividade**: Abre modal? Emite som? Tem física ou partículas?
8. **Paleta & Animação**: Paleta restrita indexada e partes procedurais dinâmicas.

---

## 💾 Sistema de Persistência (3 Slots & Cloud-Ready)

* **3 Slots de Decoração**: Salve e restaure configurações da casa ("Original", "Custom A", "Custom B").
* **Camada Desacoplada (`DecorStorageService`)**: Persiste instantaneamente via `localStorage` e já conta com ganchos nativos para envio de payloads JSON a backends e sistemas de login.

---

## 🧮 Fórmulas Matemáticas & Engenharia da Engine

Abaixo estão todas as equações centrais que governam a projeção, oclusão, controle, física, renderização micro-voxel e geologia procedural do repositório:

### 1. Projeção 3D Sprite Stacking & Profundidade (`squash = 0.72–0.75`)
Dado um ponto relativo à câmera $(\Delta x, \Delta y, \Delta z) = (w_x - \text{cam}_x,\, w_y - \text{cam}_y,\, w_z - \text{cam}_z)$ e o ângulo orbital da câmera $\theta = \text{turn}$:

$$r_x = \Delta x \cos\theta - \Delta y \sin\theta, \qquad r_y = \Delta x \sin\theta + \Delta y \cos\theta$$

$$s_x = c_x + r_x, \qquad s_y = c_y + r_y \cdot \text{squash} - \Delta z, \qquad \text{depth} = r_y$$

- `squash` opera em **`0.72`** (`room-3d.html` / `terrain-world.html`) e **`0.75`** no padrão canônico da `SKILL.md` (nunca inferior a `0.60`), enquanto `depth = r_y` ordena entidades *back-to-front*.
- **Projeção Inversa (`unproject` & `unprojectToGrid`)**: converte coordenadas de tela $(p_x, p_y)$ de volta para o plano do chão (Drag & Drop no diorama) ou para o índice contínuo do grid `720×720` em qualquer fatia $z$ (para calcular a janela visível da câmera):

$$r_x = p_x - c_x, \qquad r_y = \frac{p_y - \big(c_y - (z - \text{cam}_z)\big)}{\text{squash}}$$

$$\Delta x = r_x \cos\theta + r_y \sin\theta, \qquad \Delta y = -r_x \sin\theta + r_y \cos\theta$$

$$g_x = \frac{\text{cam}_x + \Delta x}{\text{VOX}} + \text{HALF\_GRID}, \qquad g_y = \frac{\text{cam}_y + \Delta y}{\text{VOX}} + \text{HALF\_GRID}$$

### 2. Wall Culling Dinâmico & Oclusão Angular de Móveis Ocos
- **Wall Culling Dinâmico**: para cada parede de normal unitária $(n_x, n_y)$, projeta-se a componente de profundidade da normal após a rotação $\theta$:

$$n_{y,\text{rot}} = n_x \sin\theta + n_y \cos\theta > 0.05$$

  Quando verdadeira, a parede está entre a câmera e o interior do cômodo: colapsa para um rodapé discreto de `3px` (`z = 0..3`) e desativa os hitboxes de cliques nos itens pendurados nela.
- **Oclusão Angular de Móveis Ocos** (estantes/nichos com frente aberta em `+Y`): avalia-se o ângulo total da câmera relativa ao móvel:

$$\cos(\text{selfAngle} + \theta) > 0.22$$

  Se `> 0.22`, a abertura frontal está visível e o desenho intercala faixas Z de fatias, props internos ordenados por `depth` e redesenho das bordas laterais sólidas (`wallThick`); se `<= 0.22`, as paredes laterais e o fundo sólido do modelo ocluem 100% do interior.

### 3. Controles WASD Relativos à Câmera & Direção Canônica (`+Y` = Frente)
O vetor de entrada normalizado em tela $(i_x, i_y)$ é convertido para o espaço do mundo pela rotação inversa de `turn` e alinhado à orientação canônica dos modelos (`y = H - 1` = frente):

$$\text{moveWorld}_x = i_x \cos\theta + i_y \sin\theta, \qquad \text{moveWorld}_y = -i_x \sin\theta + i_y \cos\theta$$

$$\text{targetAngle} = \operatorname{atan2}(-\text{moveWorld}_x,\, \text{moveWorld}_y)$$

O ângulo `selfAngle` interpola suavemente até `targetAngle` pelo menor arco em $[-\pi, \pi]$.

### 4. Física Vertical (`H = 16u`), Plataforma Mínima (`standableMap`) & Deslizamento (`±35°`)
- **Cinemática de Pulo (`CAT_HEIGHT = 16u`, `GRAVITY = 1200`)**:

$$v_0 = \sqrt{2g(2H + \text{margem})} = \sqrt{2 \cdot 1200 \cdot 35.0} \approx 289.8\,\text{u/s}$$

  Atinge ápice de **`~35u`** (supera degraus de `1H = 16u` e `2H = 32u`, bloqueia paredões `3H = 48u`), com **`AUTO_STEP_MAX = 5.5u`** (`~0.35H`) para subir colinas andando, **Coyote Time (`0.11s`)** e **Jump Buffer (`0.13s` teclado / `0.14s` touch)**.
- **Filtro de Plataforma Mínima (`standableMap` + `cliffTopMap`)**: pré-calcula em janela **`5×5`** quais micro-voxels oferecem apoio real (`nearCount >= 14` de `25` células não-água com $|h_v - h_0| \le 3\text{u}$, equivalente a `~3.7×3.7` micro-voxels), mantendo **guarda de piso de vale** ($h_0 - \min_5 \le 2$) para não bloquear bases côncavas e rejeitando saliências isoladas de falésia (`max3 - h0 > 4 && h0 - min3 > 4`). Um segundo passe grava em `cliffTopMap` o pico local no raio `r = 5` para impedir escalar paredões por micro-degraus de `1–2px`.
- **Deslizamento Tangencial (`±35°`)**: quando X e Y individuais encontram bloqueio em encostas curvas ou margens de rio, o resolvedor rotaciona o deslocamento $(\mathrm{d}x, \mathrm{d}y)$ em **`±35°`** (fator `0.85`), deslizando organicamente ao redor da curvatura.

### 5. Renderização Slice-by-Slice, Casca Anti-Pinhole (`min8 - 2`), Iluminação por Gradiente & Grama `fbm2d`
- **Casca Anti-Pinhole (`min8 - 2`)**: para cada micro-voxel de altura $h$, calcula-se $\min_8$ (menor altura entre os 8 vizinhos) e preenche-se a coluna de fatias no intervalo $[\max(Z_{\min}, \min_8 - 2),\, h]$, garantindo zero frestas transparentes em `360°`.
- **Iluminação Direcional por Gradiente Local**:

$$\nabla_x h = h_R - h_L, \qquad \nabla_y h = h_D - h_U, \qquad \text{sunShade} = \operatorname{clamp}\!\left(\operatorname{round}\big((-\nabla_x h - \nabla_y h)\cdot 1.4\big),\, -22,\, 22\right)$$

  Somado ao realce de quina exposta (`+10` quando $h_L < h$ ou $h_U < h$) para leitura nítida de relevo e sombras.
- **Tight-Crop Bounded Slices & Skip em $O(1)$**: cada fatia `z` armazena apenas o retângulo ocupado `{ canvas, offX, offY, w, h }` em `Uint32Array`; no loop de render, `unprojectToGrid` nos 4 cantos da tela recorta a sub-região visível e pula fatias fora da janela em $O(1)$, intercalando `entityLayer` com `globalCompositeOperation = 'destination-out'` e contorno único `1px` (`#3B2219`).
- **Grama em Moitas (`fbm2d > 0.43`)**: distribui lâminas `2–3px` (`noOutline`) quando `fbm2d(mx * 0.14, my * 0.14) + fine01 * 0.42 > 0.43` (`fine01 > 0.18` via hash XOR sem grade), animadas ao vento em **8 FPS** (`floor(t * 8)`).
- **Upscale Inteiro 1:1 & Hi-Res Overlay Pass**:

$$\text{pixelScale} = \operatorname{clamp}\!\left(\left\lfloor \frac{\min(W, H)}{260} \right\rfloor,\, 2,\, 4\right), \qquad \text{LOW\_W} = \left\lceil \frac{W}{\text{pixelScale}} \right\rceil, \qquad \text{LOW\_H} = \left\lceil \frac{H}{\text{pixelScale}} \right\rceil$$

  O mundo 3D é renderizado no buffer `lowCanvas` com `imageSmoothingEnabled = false`, ampliado para o canvas principal e sobreposto por um **Hi-Res Overlay Pass** vetorial para balões de fala e textos sem pixelização.

### 6. Kit de 6 Fórmulas Geológicas Procedurais
Substitui formas uniformes ("panquecas" e elipses empilhadas) por geologia natural contínua (reservando `useWarp = false` em `pullPlateau` apenas para estruturas/ruínas humanas):

1. **Domain Warping 2-Pass (`warp2d`)**: distorce o domínio antes de medir distâncias para gerar baías, escarpas e penínsulas assimétricas:

$$\mathbf{p}' = \mathbf{p} + A \cdot \text{fbm}\!\big(\mathbf{p}f + A\,\text{fbm}(\mathbf{p}f_1)\big)$$

2. **Smooth Union / Carve (`smax` / `smin`)**: fusão e escavação polinomial suave de morros e esporões como argila, sem vincos duros:

$$h = \operatorname{clamp}\!\left(0.5 + \frac{0.5(b - a)}{k},\, 0,\, 1\right), \qquad \text{smax}(a, b, k) = a + (b - a)h + k\,h(1 - h)$$

$$\text{smin}(a, b, k) = a + (b - a)h' - k\,h'(1 - h'), \qquad h' = \operatorname{clamp}\!\left(0.5 - \frac{0.5(b - a)}{k},\, 0,\, 1\right)$$

3. **Ridged Multifractal & Espinhas (`ridgedFbm` + `pullRidge`)**: acumula cristas geológicas afiladas ao longo de polilinhas com ramificações naturais:

$$\text{ridgedFbm}(\mathbf{p}) = \sum_i w_i\,\big(1 - |\text{noise}_i(\mathbf{p})|\big)^2$$

4. **Estratos Rochosos Irregulares (`rockTerrace`)**: cria degraus sedimentares orgânicos modulando o passo da camada por ruído coerente:

$$\text{step}_{\text{eff}} = \text{step} \cdot \big(1 + 0.22 \cdot \text{fbm}(\mathbf{p})\big)$$

5. **Trilha Recortada na Encosta (`carveBenchTrail`)**: executada *após* esculpir a montanha inteira, projeta uma spline 3D diretamente na encosta mantendo faixa interna plana `innerW` em `MAT_PATH` e mesclando o talude em `blendWidth` com interpolação *smoothstep* ($3t^2 - 2t^3$).
6. **Erosão Térmica & Gotas Hidráulicas (`thermalAndHydraulicErosion`)**: relaxa declives acima do ângulo de repouso (`talus = 4` em pedra, `2` em terra) e simula `~260` gotas determinísticas descendo o gradiente para formar sulcos naturais e saias aluviais.

---

## 🚀 Como Rodar Localmente

Zero build, zero npm, zero WebGL. Funciona imediatamente em qualquer navegador:

```bash
# Clone o repositório
git clone https://github.com/ruishalm/PixelArtSkill.git
cd PixelArtSkill

# Inicie um servidor local simples
python -m http.server 8088

# Abra no navegador:
# http://localhost:8088/index.html
```

---

## 📂 Estrutura do Repositório

```
PixelArtSkill/
├── .github/workflows/deploy.yml         # GitHub Actions: Deploy contínuo no GitHub Pages
├── SKILL.md                             # Antigravity Skill blindada (regras de render, terreno, modelagem e IA)
├── index.html                           # Ponto de entrada padrão (Diorama 3D Multi-Ambientes)
├── room-3d.html                         # Diorama 3D com os 4 cômodos e modo Decor
├── terrain-world.html                   # Mundo Aberto 3D 720×720 ("Pull-Chain", Tight-Crop Bounded Slices, 8 Biomas Anti-Kaiju, Moitas fbm2d & Shift Sprint)
├── cat-3d.html                          # Visualizador 3D do gatinho
├── chicken-3d.html                      # Visualizador 3D da galinha Popó
├── generate_mega_room.py                # Script principal gerador do mundo 3D multi-cômodos
├── generate_terrain_world.py            # Construtor do Vale Felino 3D (Micro-Voxel 720×720 Pull-Chain, Tight-Crop, Anti-Kaiju, Hi-Res)
├── generate_terrain_props.py            # Construtor dos 23 modelos voxel do mapa aberto (incl. grama e pintinho)
├── generate_kitchen_and_garden_packs.py # Construtor voxel da Cozinha e Jardim
├── generate_living_room_pack.py         # Construtor voxel da Sala de Estar
├── generate_modular_furniture.py        # Construtor voxel do Quarto e Móveis Modulares
├── build_chicken_slices.py              # Construtor anatômico da galinha e pintinho
├── terrain_props_pack.json              # Voxel slices dos 23 modelos do terreno (cabana, torii, farol, grama, etc.)
├── kitchen_pack.json                    # Voxel slices da Cozinha (bancada, geladeira, mesa, fruteira)
├── garden_pack.json                     # Voxel slices do Jardim (carvalho gigante, balanço de pneu, cadeira)
├── living_room_pack.json                # Voxel slices da Sala (sofá, estante sólida, TV retrô, mesa)
├── furniture_pack.json                  # Voxel slices do Quarto (caminha, monstera, torre)
├── modular_desk_pack.json               # Voxel slices da Workstation (mesa, note, tablet, caneca)
├── chicken_slices.json                  # Fatias anatômicas da galinha e pintinho
├── slices_v5.json                       # Fatias anatômicas do gatinho calico
├── README.md                            # Documentação completa da engine
└── LICENSE                              # Licença MIT
```

---

## 📄 Licença

Distribuído sob a licença MIT. Desenvolvido com carinho e precisão artesanal em Pixel Art 3D! 🐾
