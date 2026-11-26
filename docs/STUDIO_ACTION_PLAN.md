# Plano de AÃ§Ã£o â€” PixelArt 3D Engine & Voxel 3D Studio

> Documento vivo de arquitetura e execuÃ§Ã£o para evoluir o projeto de um mostruÃ¡rio hardcodado (`Vale Felino 3D`) para uma **engine 2.5D/3D Sprite-Stacking desacoplada** e um **Studio completo de navegador** (Editor de Mundo + Editor de Modelos Voxel + Exportador Autocontido).

---

## 1. DiagnÃ³stico Atual e Arquitetura Alvo

### O que temos hoje
- `src/engine/` jÃ¡ possui 5 mÃ³dulos extraÃ­dos (`00-math-noise.js`, `01-voxel-audio.js`, `02-slice-baker.js`, `03-terrain-sculptor.js`, `04-renderer.js`), mas parte da fÃ­sica, fluidos, resize e constantes do grid (`mw = 1080`, `mh = 1080`) ainda vivem em `src/terrain-world/`.
- `studio/index.html` jÃ¡ tem pincÃ©is ao vivo, vento/correnteza, seleÃ§Ã£o/trava (`pin`), `Novo Plano`, `Borracha` e `Undo`, porÃ©m o bundler `scripts/generate_studio.py` ainda inclui `src/terrain-world/*.js`, herdando o tamanho fixo `1080Ã—1080`, a escala exagerada do gato e cÃ³digo do mostruÃ¡rio.

### Arquitetura Alvo (SeparaÃ§Ã£o Limpa)
```mermaid
flowchart TD
  E["src/engine/ (NÃºcleo Puro & Parametrizado)"]
  W["src/terrain-world/ (Demo Vale Felino 3D)"]
  S["src/studio/ (Voxel 3D Studio: Mundo + Modelador)"]
  A["assets/voxels/ (Biblioteca Base RLE/Base-36)"]

  E --> W
  E --> S
  A --> W
  A --> S
```

### PolÃ­tica de Branches
- **`main` e `dev`**: permanecem intactas (estado estÃ¡vel do repositÃ³rio/skill).
- **`dev-engine`**: refatoraÃ§Ãµes puras de `src/engine/` e compatibilidade com `examples/terrain-world.html`.
- **`dev-studio`**: desenvolvimento do `Voxel 3D Studio` (`src/studio/`, `scripts/generate_studio.py`, `studio/index.html` e este plano).

---

## 2. Fase 1 â€” Desacoplamento Total do NÃºcleo (`src/engine/`)

**Objetivo:** eliminar qualquer dependÃªncia de `src/terrain-world/` no Studio e tornar o tamanho do mapa e a fÃ­sica 100% configurÃ¡veis.

### Passos
1. **Parametrizar o Grid do Mundo (`initWorldGrid`):**
   - Trocar constantes fixas (`const mw = 1080`, `const mh = 1080`, `HALF_GRID`, `WORLD_MIN/MAX`) por um estado mutÃ¡vel/configurÃ¡vel (`initWorldGrid(gridW, gridH, voxSize, zMin, zMax)`).
   - Recriar dinamicamente `hmap`, `matMap`, `biomeMap`, `cliffMask`, `shadowMask`, `noGrassMask`, `standableMap`, `cliffTopMap`, `pinnedMask`, alÃ©m das grades de vento/correnteza (`FLOW_GRID_W = Math.ceil(mw / FLOW_GRID_STEP)`) e dos caches de fatias em `02-slice-baker.js`.
   - Suportar presets de tamanho nativamente:
     - **Micro Diorama:** `128Ã—128` (`256Ã—256u`, bake ultra-rÃ¡pido)
     - **Diorama:** `256Ã—256` (`512Ã—512u`)
     - **Ilha / Fase MÃ©dia:** `512Ã—512` (`1024Ã—1024u`)
     - **Mundo Aberto:** `1080Ã—1080` (`2160Ã—2160u`)
2. **Extrair FÃ­sica & Fluidos GenÃ©ricos para `src/engine/`:**
   - Criar `src/engine/05-physics-core.js`:
     - Movimento de entidade/player (colisÃ£o com terreno, `AUTO_STEP_MAX`, deslizamento tangencial, pulo com coyote time e jump buffer, gravidade configurÃ¡vel).
     - Colisores de props genÃ©ricos (`PROP_COLLIDER_META` extensÃ­vel em runtime).
     - Destrutibilidade genÃ©rica (HP, impacto, queda rÃ­gida/balanÃ§o e spawn de drops) + **sistema de pegar/carregar/arremessar itens (`carry/throw`)**.
   - Criar `src/engine/06-fluids-weather.js`:
     - Campo de vento (`sampleWind`, `injectWindImpulse`, grade pintÃ¡vel `customWindVx/Vy`, `ENGINE_TUNING.windMul`).
     - Campo de correnteza (`sampleWaterFlow`, deflexÃ£o Rankine-dipole em obstÃ¡culos, grade pintÃ¡vel `customFlowVx/Vy`, streaks e flutuabilidade de Arquimedes).
     - AutÃ´mato granular (areia/talus), difusÃ£o tÃ©rmica de fogo (`fireCool`) e tecidos/bandeiras Verlet.
3. **Manter `Vale Felino 3D` 100% Ã­ntegro:**
   - `src/terrain-world/` passa a conter apenas a configuraÃ§Ã£o especÃ­fica do Vale Felino (8 biomas, NPCs, peixes, galinhas, falas do gato, HUD do mostruÃ¡rio).
   - **CritÃ©rio de aceite:** `python scripts/generate_terrain_world.py` + `python tests/test_physics_invariants.py` passando **5/5 `OK`** sem regressÃ£o visual ou fÃ­sica.

---

## 3. Fase 2 â€” Studio de Mundo Independente, ProporÃ§Ãµes & Humanoide de Teste

**Objetivo:** desligar `src/terrain-world/` do Studio e transformar `studio/index.html` em um editor de mundos/dioramas de verdade.

### Passos
1. **Desligar `src/terrain-world/` de `scripts/generate_studio.py`:**
   - `generate_studio.py` passa a empacotar apenas `src/engine/*.js` + biblioteca base de assets (`assets/voxels/`) + `src/studio/*.js`.
   - Zero cÃ³digo de peixes, galinhas, HUD de biomas do Vale Felino ou pontes hardcodadas no Studio.
2. **Fluxo "Novo Projeto" (Modal/Barra):**
   - Escolher **Tamanho do Mapa:** `128Ã—128 (Micro Diorama)`, `256Ã—256 (Diorama)`, `512Ã—512 (MÃ©dio)`, `1080Ã—1080 (Grande)`.
   - Escolher **Base Inicial:**
     - `Plano Vazio` (grama em `Z=0`, sem props â€” modo 100% manual)
     - `Ilha Procedural` (relevo `fbm2d + ridgedFbm` com praia e Ã¡gua nas bordas)
     - `Terreno Continental` (colinas, vales e lagos internos)
   - Definir `WORLD_SEED` inicial.
3. **ProporÃ§Ãµes Reais & Avatares de Teste:**
   - **Humanoide Cru (Avatar PadrÃ£o de Teste):**
     - Modelo voxel limpo (cabeÃ§a, tronco, braÃ§os e pernas em fatias ou sub-partes articuladas) dimensionado em escala realista frente a portas, cabanas, Ã¡rvores e toras (nÃ£o gigante).
     - AnimaÃ§Ã£o de caminhada (passo/braÃ§os), pulo, golpe de quebra e pose carregando item.
   - **Gato (Avatar Alternativo):**
     - Escala padrÃ£o corrigida para **`0.45x`** (proporÃ§Ã£o realista de um gato ao lado de uma casa/humano), com slider de escala (`0.35x` atÃ© `1.2x`) no painel de Teste para quem quiser estilo chibi ou realista.
4. **AÃ§Ãµes de InteraÃ§Ã£o Separadas no Modo Testar:**
   - **Interagir â€” Quebrar (`Clique Esq` ou `F`):**
     - Atinge o prop destrutÃ­vel Ã  frente (Ã¡rvore, pedregulho, tora, asset customizado com flag `destructible`), reduz HP, dispara partÃ­culas/som e gera drops fÃ­sicos no chÃ£o.
   - **Interagir â€” Pegar / Soltar / Arremessar (`E`):**
     - Se mÃ£os vazias: procura o item pegÃ¡vel (`pickable` ou drop de tora/pedra) mais prÃ³ximo na frente do avatar e acopla acima da cabeÃ§a/mÃ£os.
     - Se segurando item: solta suavemente (toque curto em `E`) ou arremessa na direÃ§Ã£o do olhar (segurar/apertar `F` ou `E` em movimento), reagindo Ã  gravidade, terreno, vento e correnteza.
5. **Polimento das Ferramentas do Editor de Mundo:**
   - Adicionar **Redo (`Ctrl+Y` / `Ctrl+Shift+Z`)** junto ao `Undo (Ctrl+Z)`.
   - Atalhos rÃ¡pidos de pincel (`[` e `]` para raio, `1..9` para ferramentas, `EspaÃ§o` no modo Editar para alternar rÃ¡pido com Teste).
   - Seletor explÃ­cito de **Modo de GeraÃ§Ã£o**: `Tudo Procedural` | `HÃ­brido (Fixo + Procedural)` | `Tudo Fixo (Manual)` com botÃ£o `Travar Tudo` / `Destravar Tudo`.

---

## 4. Fase 3 â€” Aba `ðŸ§± EstÃºdio de Modelos Pixel` (Editor Voxel / Sprite-Stacking)

**Objetivo:** permitir que o usuÃ¡rio crie seus prÃ³prios props, itens pegÃ¡veis, estruturas e personagens pixel 3D dentro do mesmo `studio/index.html`, sem precisar de ferramentas externas.

### Passos
1. **NavegaÃ§Ã£o por Abas na Topbar do Studio:**
   - **`ðŸŒ Mundo`**: editor de terreno, fluidos, props e teste.
   - **`ðŸ§± Modelador`**: editor de modelos voxel em fatias 2D empilhadas.
2. **Canvas de EdiÃ§Ã£o por Camadas (`Z`):**
   - DimensÃµes suportadas: `16Ã—16Ã—16` (itens/objetos), `24Ã—24Ã—24` (personagens/props mÃ©dios) e `32Ã—32Ã—32` (estruturas/Ã¡rvores).
   - Slider + botÃµes `â–²/â–¼` para subir/descer fatia `Z`, com **Onion Skin** (camada `Z-1` visÃ­vel semi-transparente abaixo para alinhar o volume 3D com precisÃ£o).
   - Ferramentas de pintura de fatia:
     - `âœï¸ LÃ¡pis` (voxel 1Ã—1)
     - `ðŸ§½ Borracha`
     - `ðŸª£ Balde (Flood Fill)`
     - `ðŸ’‰ Conta-Gotas`
     - `ðŸªž Espelho X` (simetria bilateral â€” essencial para personagens e mÃ³veis)
     - `ðŸ“‹ Copiar Fatia Anterior` / `â¬†ï¸ Duplicar para Z+1` / `ðŸ§¹ Limpar Fatia`
3. **Editor de Paleta Indexada (Base-36):**
   - Paleta editÃ¡vel com cor `0` sempre transparente e atÃ© 35 cores sÃ³lidas (compatÃ­vel 1:1 com o encoder Base-36/RLE da engine).
   - Presets prontos de paleta (Madeira, Folhagem, Pedra, Personagem/Roupas, Cozy Pastel).
   - BotÃ£o opcional de **Auto-Shading por Altura `Z`** (escurece sutilmente base e clareia topo).
4. **Preview 3D GiratÃ³rio ao Vivo:**
   - Painel lateral renderizando o modelo em tempo real via `buildSliceSheet` + `stampModelSlice` (a mesma matemÃ¡tica de Sprite Stacking da engine).
   - BotÃ£o de **Auto-Girar**, arraste para orbitar `360Â°`, zoom e opÃ§Ã£o **"Comparar escala com Humanoide"** lado a lado.
5. **Propriedades de Comportamento & Biblioteca DinÃ¢mica:**
   - FormulÃ¡rio compacto por asset:
     - Nome e ID do modelo
     - Categoria: `Prop EstÃ¡tico` | `DestrutÃ­vel` (HP + drop) | `Item PegÃ¡vel` | `Folhagem (Vento)` | `Fogo/Luz` | `Avatar de Teste`
     - Raio de colisÃ£o e escala padrÃ£o
   - BotÃ£o **`âž• Salvar na Biblioteca do Mundo`**: compila o `sliceSheet`, registra na paleta da Aba `ðŸŒ Mundo` imediatamente e permite plantar no mapa (ou escolher como Avatar no modo Testar).
   - Importar / Exportar modelo individual no formato `.json` RLE compatÃ­vel com `assets/voxels/`.

---

## 5. Fase 4 â€” ExportaÃ§Ã£o de Projeto e Build JogÃ¡vel Autocontido

**Objetivo:** fechar o ciclo de criaÃ§Ã£o, permitindo salvar o trabalho em andamento ou publicar um diorama/jogo pronto.

### Passos
1. **Exportar / Importar Projeto Completo (`.voxelstudio.json`):**
   - Salva `version`, `gridW`, `gridH`, `voxSize`, `seed`, `generationMode`, `tuning`, `pinnedCells` (compactado em RLE), `windSparse`, `flowSparse`, `props` (fixos + procedurais se `Tudo Fixo`) e `customAssets` (todos os modelos criados no Modelador em formato RLE).
2. **Exportar HTML Autocontido (`ðŸš€ Publicar .html`):**
   - Gera no prÃ³prio navegador um arquivo `.html` standalone contendo apenas o runtime mÃ­nimo (`src/engine/` + dados da cena exportada + avatar de teste escolhido + controles simples), sem sidebar de ediÃ§Ã£o â€” pronto para abrir offline ou hospedar direto no GitHub Pages / itch.io.

---

## 6. Ordem de ExecuÃ§Ã£o & VerificaÃ§Ã£o por Etapa

| Etapa | EntregÃ¡vel Principal | VerificaÃ§Ã£o ObrigatÃ³ria |
|---|---|---|
| **1A** | `initWorldGrid(w, h, vox)` em `src/engine/` | `terrain-world.html` gera `1080Ã—1080` idÃªntico; teste em Node cria `128Ã—128` e `256Ã—256` sem erros |
| **1B** | `05-physics-core.js` e `06-fluids-weather.js` em `src/engine/` | `tests/test_physics_invariants.py` **5/5 `OK`** |
| **2A** | `generate_studio.py` sem `src/terrain-world/` + Modal Novo Projeto (tamanhos) | `node --check` saÃ­da `0`; alternar `256Ã—256` â†” `512Ã—512` â†” `1080Ã—1080` sem travar |
| **2B** | Humanoide Cru + Gato `0.45x` + AÃ§Ãµes `[Quebrar]` e `[Pegar/Soltar]` | Teste em modo Testar: cortar Ã¡rvore, pegar tora, carregar, arremessar na Ã¡gua e ver boiar/derivar |
| **3** | Aba `ðŸ§± Modelador Voxel` integrada Ã  Biblioteca da Aba Mundo | Criar um prop/item no Modelador, salvar na biblioteca, plantar no mapa e interagir no modo Testar |
| **4** | ExportaÃ§Ã£o `.voxelstudio.json` (com assets) + `.html` autocontido | Exportar cena, reimportar em aba limpa e abrir o `.html` exportado sem erros de console |

