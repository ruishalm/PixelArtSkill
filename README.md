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
* 🏔️ **[Vale Felino 3D v2 — Mundo Aberto 56×56 & Grama Voxel (terrain-world.html)](https://ruishalm.github.io/PixelArtSkill/terrain-world.html)**: Mapa expandido **56×56 tiles** com 8 biomas, **23 modelos voxel** (lâminas de grama de 2–3px animadas ao vento, Portal Torii, Farol, Cabana, Cogumelos escaláveis), NPCs vivos (Popó e Pintinhos), balões vetoriais Hi-Res e controle **WASD + Espaço (pulo 2×H)**.
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

## 🏔️ Vale Felino 3D v2 — Motor de Terreno Voxel, Relevo & Grama Viva (`terrain-world.html`)

Mapa aberto **56×56 tiles (`896×896u`)** separado da casa, demonstrando o **Motor de Terreno Voxel 3D em Canvas 2D**:
- **8 Biomas Conectados**: Vila da Clareira & Cabana (com Galinha Popó NPC), Campos de Girassol (com 2 Pintinhos Piu e Fardos de Feno), Circuito das Ruínas Antigas (`6/16/32/48u`), Praia Dourada (Píer, Vitórias-Régias puláveis e Farol), Jardim Zen com Portal Torii (atravessável pelo vão central), Rio Cristalino com 2 Pontes, Bosque dos Cogumelos Saltitantes (chapéus sólidos até `Z=40`) e Montanha do Pico Sakura (`Z=96`) com cachoeira dupla animada.
- **Estruturas Monumentais em Escala Real (`1:1` Pixel Density)**: Construções modeladas em voxel real grande sem zoom artificial (`Cabana 52×46×54` `3.4×H`, `Farol 34×34×84` `5.25×H`, `Portal Torii 50×16×54`, `Sakura 54×54×68`, `Pinheiros 28×28×48`, `Pilares 18×18×34`, `Guarda-Sol 28×28×28` e `Barco 34×20×12`).
- **23 Modelos Voxel & Grama em Lâminas (`2–3px`)**: Grama modelada no próprio Sprite Stacking sem contorno pesado (`noOutline`), animada em 3 frames de vento (8 FPS) + *rustle* sob as patas do gato.
- **Balões Hi-Res & Responsividade 1:1**: Textos desenhados no `ctx` vetorial após o upscale garantindo letras nítidas (zero pixelização) e pixels 100% quadrados tanto em desktop widescreen quanto em celular vertical (com D-Pad touch).
- **Calibração Física pela Altura do Gato (`H = 16u`) & 5 Modos de Collider**:
  - `ΔZ ≤ 0.4H` (`Z=6`): Rampa suave transponível andando (`AUTO_STEP`).
  - `0.4H < ΔZ ≤ 2.0H` (`Z=16` e `Z=32`): Degraus transponíveis com pulo (`Espaço` = pico `~35u`, Coyote Time & Jump Buffer).
  - `ΔZ > 2.0H` (`Z=48+`) ou **Água**: Intransponíveis com bloqueio por eixo e aviso do gato.
  - **Colliders em Props**: `'solid'` (troncos, farol), `'box'` (paredes retangulares da cabana e barco), `'platform'` (cogumelos, fardos, tocos, pedras), `'arch'` (2 pilares laterais no Torii) e `'none'` (flores/grama).
- **16 Peixes Dourados & Botão `🧭 Viagem`**: Viagem rápida pelos marcos principais, minimapa topográfico em tempo real (`56×56`) e toast de descoberta dos 8 biomas.

* **6 Regiões Conectadas**: Clareira do Spawn, Circuito das Ruínas (escada de calibração `Z=6 / 16 / 32 / 48`), Rio Cristalino com Ponte & Pedras de Travessia, Terraços Noroeste, Bosque dos Cogumelos Saltitantes (chapéus sólidos escaláveis) e Montanha do Pico Sakura (`Z=80`) com cachoeira animada e **10 Peixes Dourados** colecionáveis.
* **Calibração Física pela Altura do Gato (`H = 16u`)**:
  * `ΔZ ≤ 0.4H` (`Z=6`): Rampa suave transponível apenas andando (`AUTO_STEP`).
  * `0.4H < ΔZ ≤ 2.0H` (`Z=16` e `Z=32`): Degraus transponíveis com pulo (`Espaço` = pico `~35u`, com Coyote Time e Jump Buffer).
  * `ΔZ > 2.0H` (`Z=48+`) ou **Água**: Áreas intransponíveis com bloqueio por eixo separado e feedback visual do gato.
* **Controles**: `W A S D` / Setas para mover relativo à câmera, `Espaço` para pular `2×H`, `Q`/`E` ou arraste do mouse para girar 360°, `M` para miar e `R` para voltar ao Spawn.

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
├── terrain-world.html                   # Mundo Aberto 3D 56×56 (8 Biomas, Grama 2–3px, NPCs e Balões Hi-Res)
├── cat-3d.html                          # Visualizador 3D do gatinho
├── chicken-3d.html                      # Visualizador 3D da galinha Popó
├── generate_mega_room.py                # Script principal gerador do mundo 3D multi-cômodos
├── generate_terrain_world.py            # Construtor do Vale Felino 3D v2 (56×56, colisores 4 modos, Hi-Res)
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
