# 🐾 PixelArtSkill — 3D & Pseudo-3D Pixel Art Engine

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-brightgreen?logo=github)](https://ruishalm.github.io/PixelArtSkill/)
[![Tech](https://img.shields.io/badge/HTML5-Canvas%202D-E34F26?logo=html5&logoColor=white)](https://ruishalm.github.io/PixelArtSkill/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Vanilla%20JS)-blue)](#)
[![No WebGL Required](https://img.shields.io/badge/3D%20Engine-No%20WebGL%20%2F%20No%20Three.js-orange)](#)
[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Custom%20Skill-purple)](https://ruishalm.github.io/PixelArtSkill/)

> **Engine de Pixel Art 3D e Diorama Interativo** construída 100% em **HTML5 Canvas 2D puro**, utilizando **Sprite Stacking (Fatiamento Voxel Z)**, rotação orbital 360°, projeção inversa para drag & drop e oclusão inteligente de paredes dinâmicas. Inspirado no universo aconchegante de *PurrModoro*, *The Sims* e *Animal Crossing*.

---

## 🎮 Live Demos (Jogue no Navegador!)

* 🏠 **[Quarto 3D Diorama Completo (room-3d.html / index.html)](https://ruishalm.github.io/PixelArtSkill/)**: Quarto amplo com todos os móveis modulares, modo decoração drag & drop, relógio 3D em tempo real e nuvens passando na janela.
* 🐱 **[Visualizador do Gatinho 3D (cat-3d.html)](https://ruishalm.github.io/PixelArtSkill/cat-3d.html)**: Modelo anatômico quadrupedal de 16 fatias do gatinho calico com olhões expressivos e orelhas empinadas.

---

## ✨ Funcionalidades Principais

### 1. 🏠 Diorama 3D em Canvas 2D Puro
- **Zero WebGL / Zero Three.js**: Todo o render 3D (rotação, projeção de vértices, oclusão, fatiamento em Z e perspectiva) roda na CPU sobre a API padrão do `CanvasRenderingContext2D`.
- **Pixel Art Nítida (Nearest-Neighbor)**: Buffer interno de baixa resolução (`440x440`) com upscale inteiro sem interpolação bilinear borrada (`image-rendering: pixelated`).

### 2. 🧱 Smart Dynamic Wall Culling (Paredes Dinâmicas)
- Cálculo vetorial da normal da parede relativo ao ângulo da câmera (`nyRot = normal.x * sin(turn) + normal.y * cos(turn)`).
- **As paredes que ficam na frente da câmera recolhem automaticamente** virando rodapés baixos de 3px, garantindo que o interior do quarto esteja sempre 100% visível em qualquer ângulo de 360°!

### 3. 🛠️ Modo Decoração (Drag & Drop em 3D Real)
- **Unproject Matemático**: Inversão da matriz de rotação e inclinação isométrica para transformar as coordenadas de clique da tela `(screenX, screenY)` em pontos exatos do chão 3D `(worldX, worldY)`.
- **Grid Isométrico & Snapping**: Grid visual de 16px no piso com snap suave de 4px para alinhamento perfeito.
- **Elevação em Z e Sombra Suave**: Ao arrastar um móvel, ele levita alguns milímetros com sombra projetada dinâmica.
- **Rotação Individual (Tecla R)**: Gire qualquer móvel selecionado em 90° para posicioná-lo onde quiser.

### 4. 📦 Catálogo de Assets & Aba Exclusiva de Pets
- Gaveta lateral flutuante organizada em 4 categorias: `🛋️ Móveis`, `🧸 Quarto`, `🐾 Pets` e `🎩 Chapéus`.
- **Companheiros Modulares**: Ative até 3 bichinhos simultâneos no quarto ou recolha quem quiser:
  - 🐱 **Gatinho Mochi**: 6 pelagens selecionáveis (Calico Original, Kuro Preto, Felix Frajola, Cheddar Laranja, Luna Siamês, Misty Cinza).
  - 🐔 **Galinha Popó**: Galinha rechonchuda que passeia rebolando e cisca milho no chão com bicadas "toc-toc".
  - 🐥 **Pintinho Piu (Pintinho Amarelinho)**: Modelo próprio de 10 fatias ("bolinha" esférica sem crista), patinhas de palito e olhinhos brilhantes.
- Botões rápidos para **Mostrar Todos** ou **Limpar Sala**.

### 5. 📌 Mural de Post-its Interativo & Zoom 3D
- Quadro de cortiça expandido na parede leste com 6 post-its coloridos e tachinhas.
- **Clique Dinâmico em 360°**: Hitbox calculado diretamente a partir da projeção 3D dos 4 vértices da parede com culling automático quando a parede fica de costas.
- **Bloco de Notas & Lembretes**: Ao clicar no quadro fora do modo decoração, abre um modal interativo em tela cheia com bloquinho de notas e persistência via `localStorage`.

### 6. 🐓 Locomoção Biomecânica & Animação Sem Deformação
- **Passada Real em 2 Fases**: Separação física entre *Fase de Balanço* (patinha no ar avançando pelo céu) e *Fase de Apoio* (patinha no chão deslizando para trás e empurrando o corpo), eliminando passos em falso ou patinação.
- **Orientação Direcional Perfeita**: Rotação das fatias alinhada estritamente com o vetor de velocidade (`totalAngle = theta + turn`), fazendo com que o animal ande sempre na exata direção em que está olhando.
- **Articulação de Bloco Sólido (Anti-Shear)**: O bico e cabeça mergulham até o chão para ciscar sem distorção ou colapso horizontal de fatias.
- **Rebolado e Dinâmica Corporal**: Gingado de quadril (`rollWobble`), quique vertical (`bodyBobZ`) e impulso optocinético de cabeça.

### 7. 🖥️ Setup Workstation 100% Modular
- **Mesa de Estudo Ampla (50x30)**: Madeira maciça de carvalho com 4 pernas e tampo chanfrado.
- **Notebook no Suporte Ergonômico**: Base e hastes de alumínio elevadas, teclado com trackpad e tela aberta com display ciano brilhante.
- **Mesa Digitalizadora (Drawing Tablet)**: Corpo fino grafite com express keys, tela com rascunho de gatinho em progresso e caneta stylus ao lado em suporte donut.
- **Livrinhos da Mesa**: Pilha de 3 livros com fita marcadora azul pendurada na borda.
- **Caneca de Café**: Cerâmica branca com café expresso e vapor quentinho subindo.
- *Inteligência de Grupo*: Arrastar a mesa move todos os acessórios de cima juntos; arrastar cada acessório permite reorganizar a mesa ou colocá-los no chão!

### 8. ⏰ Relógio Cilíndrico 3D com Hora Real
- Cilindro de madeira maciça de 16 facetas saliente na parede com mostrador afundado.
- Ponteiros de horas e minutos sincronizados com o horário real do sistema operacional.

### 9. ☁️ Nuvens Volumétricas em Parallax 3D
- As nuvens flutuam **30 unidades fora do quarto** ($y = -ROOM\_R - 30$) com parallax 3D verdadeiro através do vidro da janela.

### 10. 📚 Prateleira Segmentada sem Sobreposição
- Nichos claramente espaçados com ordenação dinâmica de profundidade: livros em pé, suporte metálico com livro inclinado em $22^\circ$, vasinho de suculenta e livros horizontais com cristal.

---

## 📐 Especificação Técnica & Matemática

### Projeção Isométrica (World $\to$ Screen)
$$\begin{cases}
r_x = x \cdot \cos(\theta) - y \cdot \sin(\theta) \\
r_y = x \cdot \sin(\theta) + y \cdot \cos(\theta) \\
\text{screen}_X = \text{center}_X + r_x \\
\text{screen}_Y = \text{center}_Y + r_y \cdot \text{squash} - z
\end{cases}$$

### Desprojeção Inversa (Screen $\to$ World no plano $Z = 0$)
$$\begin{cases}
r_x = \text{screen}_X - \text{center}_X \\
r_y = \frac{\text{screen}_Y - \text{center}_Y}{\text{squash}} \\
x = r_x \cdot \cos(\theta) + r_y \cdot \sin(\theta) \\
y = -r_x \cdot \sin(\theta) + r_y \cdot \cos(\theta)
\end{cases}$$

---

### 🐾 Inteligência de Plataformas & Confinamento Espacial
- **Mesa Ampliada (80x36)**: Espaço generoso para acessórios modulares e pets descansarem e passearem.
- **Gato Mochi na Mesa**: Ao ser colocado na mesa, dorme em postura de pãozinho (`loaf`) por um tempo garantido (`deskSleepTimer`) antes de decidir descer ou passear pelo tampo.
- **Galinha Popó na Prateleira**: Pode voar/subir na prateleira de parede, chocando aconchegada entre os livros (`state = 'brood'`), e descer flutuando com bater de asas suave.
- **Pintinho Piu Confinado**: Onde for colocado (mesa ou prateleira), **não desce sozinho**. Fica "sanzando" e ciscando estritamente dentro dos limites daquela plataforma sem cair.
- **Ajuste Anatômico dos Chapéus**: Chapéus agora repousam confortavelmente no cocuruto da cabeça entre as orelhas do gatinho. Na galinha Popó, o chapéu é inclinado charmosamente ao lado da crista.
- **Pintinho no Chapéu (Walking Hat)**: Ao equipar chapéu no pintinho, ele veste o chapéu inteiro cobrindo o corpinho com leve transparência (88%), com duas patinhas amarelas andando por baixo e olhinhos pretos brilhantes com biquinho espiando pela aba frontal!

---

## 🚀 Como Executar Localmente

Como o projeto usa apenas HTML, CSS e JavaScript puros sem bundler ou dependências, basta clonar e abrir qualquer arquivo:

```bash
# Clone o repositório
git clone https://github.com/ruishalm/PixelArtSkill.git
cd PixelArtSkill

# Inicie um servidor local simples
python -m http.server 8080

# Abra no navegador:
# http://localhost:8080/room-3d.html ou http://localhost:8080/cat-3d.html
```

---

## 📂 Estrutura de Arquivos

```
PixelArtSkill/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions: Deploy automático no GitHub Pages
├── index.html                  # Ponto de entrada padrão do GitHub Pages (Quarto 3D)
├── room-3d.html                # Quartinho 3D Modular com Modo Decoração & Catálogo
├── cat-3d.html                 # Visualizador 3D do gatinho calico Mochi
├── generate_mega_room.py       # Script construtor do diorama 3D
├── generate_modular_furniture.py# Construtor de fatias dos móveis modulares
├── modular_desk_pack.json      # Dados voxel dos acessórios da mesa (note, tablet, livros, caneca)
├── furniture_pack.json         # Dados voxel da caminha, planta monstera e torre
├── slices_v5.json              # 16 fatias anatômicas do gatinho calico
├── README.md                   # Documentação do projeto
└── LICENSE                     # Licença MIT
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
Desenvolvido com carinho e precisão artesanal em Pixel Art 3D! 🐾
