"""
Gerador aprimorado de Fatias Sprite Stacking da Galinha 3D (24x24 x 16 camadas)
Perfeitamente gordinha, com asas destacadas, cauda volumosa, crista ondulada e patas amarelas.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOXELS_DIR = os.path.join(ROOT, 'assets', 'voxels')
EXAMPLES_DIR = os.path.join(ROOT, 'examples')

W, H = 24, 24
NUM_SLICES = 16

# Paleta da Galinha
chicken_pal = [
    'rgba(0,0,0,0)',
    '#FFFFFF', # 1: Branco pena principal
    '#F1F5F9', # 2: Branco pena sombra suave
    '#CBD5E1', # 3: Contorno / pena profunda
    '#EF4444', # 4: Vermelho vivo crista e barbela
    '#B91C1C', # 5: Vermelho escuro sombra
    '#F59E0B', # 6: Amarelo ouro bico e patas
    '#D97706', # 7: Amarelo escuro sombra patas
    '#0F172A', # 8: Olho preto
    '#FFFFFF'  # 9: Brilho olho
]

slices = [[[0 for _ in range(W)] for _ in range(H)] for _ in range(NUM_SLICES)]

def fill_rect(z, x1, y1, x2, y2, color):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= z < NUM_SLICES and 0 <= y < H and 0 <= x < W:
                slices[z][y][x] = color

def fill_circle(z, cx, cy, r, color):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if (x - cx)**2 + (y - cy)**2 <= r**2:
                if 0 <= z < NUM_SLICES and 0 <= y < H and 0 <= x < W:
                    slices[z][y][x] = color

# Centro da Galinha: cx = 12, cy = 12
# Direção frontal: +X (bico em x=18-20, rabo em x=4-6)
# Laterais: Y (asa esq y=6, asa dir y=18)

# --- Z = 0: Ponta das unhas / 3 dedinhos amarelos ---
# Pata Esquerda (cy=9), Pata Direita (cy=15)
# Dedos Esq:
slices[0][9][14] = 6; slices[0][9][15] = 6; slices[0][9][16] = 6
slices[0][8][15] = 6; slices[0][10][15] = 6
# Dedos Dir:
slices[0][15][14] = 6; slices[0][15][15] = 6; slices[0][15][16] = 6
slices[0][14][15] = 6; slices[0][16][15] = 6

# --- Z = 1: Base dos pés ---
fill_rect(1, 13, 9, 15, 9, 6)
fill_rect(1, 13, 15, 15, 15, 6)
slices[1][8][14] = 7; slices[1][10][14] = 7
slices[1][14][14] = 7; slices[1][16][14] = 7

# --- Z = 2: Pernas amarelas fininhas ---
fill_rect(2, 13, 9, 14, 9, 6)
fill_rect(2, 13, 15, 14, 15, 6)

# --- Z = 3: Pernas canela alta ---
fill_rect(3, 13, 9, 13, 9, 7)
fill_rect(3, 13, 15, 13, 15, 7)

# --- Z = 4: Penugem da barriga inferior (coxas fofas) ---
fill_circle(4, 12, 12, 5.2, 2)
fill_circle(4, 12.2, 12, 4.4, 1)

# --- Z = 5: Barriga gordinha redonda ---
fill_circle(5, 12, 12, 6.8, 2)
fill_circle(5, 12.3, 12, 5.8, 1)
# Base do rabo empinado atrás (x=5-7)
fill_rect(5, 5, 10, 7, 14, 3)

# --- Z = 6: Corpo volumoso + Base das asas nas laterais ---
fill_circle(6, 12.5, 12, 7.5, 2)
fill_circle(6, 12.8, 12, 6.6, 1)
# Asas
fill_rect(6, 9, 5, 15, 5, 3)
fill_rect(6, 9, 19, 15, 19, 3)
# Rabo
fill_rect(6, 4, 10, 6, 14, 1)
fill_rect(6, 3, 11, 4, 13, 3)

# --- Z = 7: Centro do corpo + Asas com penas duplas ---
fill_circle(7, 13, 12, 7.6, 2)
fill_circle(7, 13.2, 12, 6.8, 1)
# Asas com detalhes
fill_rect(7, 8, 5, 16, 5, 2)
fill_rect(7, 9, 6, 15, 6, 1)
fill_rect(7, 8, 19, 16, 19, 2)
fill_rect(7, 9, 18, 15, 18, 1)
# Rabo arrebitado
fill_rect(7, 3, 10, 5, 14, 1)
fill_rect(7, 2, 11, 3, 13, 3)

# --- Z = 8: Peito alto e topo das asas ---
fill_circle(8, 13.5, 12, 7.0, 2)
fill_circle(8, 13.8, 12, 6.2, 1)
# Topo asas
fill_rect(8, 10, 6, 15, 6, 1)
fill_rect(8, 10, 18, 15, 18, 1)
# Rabo
fill_rect(8, 2, 11, 4, 13, 1)

# --- Z = 9: Peito da galinha e início do pescoço ---
fill_circle(9, 14, 12, 5.8, 2)
fill_circle(9, 14.3, 12, 5.0, 1)
# Pontinha final do rabo
fill_rect(9, 3, 11, 4, 13, 2)

# --- Z = 10: Pescoço e queixo com Barbela vermelha pendente ---
fill_circle(10, 15, 12, 4.6, 2)
fill_circle(10, 15.3, 12, 3.8, 1)
# Barbela vermelha (x=19-20, y=11-13)
fill_rect(10, 19, 11, 20, 13, 4)

# --- Z = 11: Cabeça, Bico amarelo e Barbela ---
fill_circle(11, 15.5, 12, 4.2, 2)
fill_circle(11, 15.8, 12, 3.5, 1)
# Barbela vermelha
fill_rect(11, 19, 11, 20, 13, 4)
slices[11][11][20] = 5; slices[11][13][20] = 5
# Bico pontudo amarelo (x=20-22, y=11-13)
fill_rect(11, 20, 11, 21, 13, 6)
slices[11][12][22] = 7

# --- Z = 12: Cabeça com Olhinhos pretos e Bico superior ---
fill_circle(12, 15.5, 12, 3.8, 2)
fill_circle(12, 15.8, 12, 3.2, 1)
# Olhos pretos expressivos (x=16, y=9 e y=15)
slices[12][9][16] = 8; slices[12][15][16] = 8
slices[12][9][17] = 9; slices[12][15][17] = 9 # Brilho fofo
# Bico superior
fill_rect(12, 19, 11, 20, 13, 6)
slices[12][12][21] = 6

# --- Z = 13: Topo da cabeça e base da crista vermelha ---
fill_circle(13, 15.5, 12, 3.2, 1)
# Base da crista (x=13-18, y=11-13)
fill_rect(13, 13, 11, 18, 13, 4)

# --- Z = 14: Crista Vermelha de 3 Pontas (Ondulada) ---
# Ponta Frontal (x=17-18), Ponta Central (x=15), Ponta Traseira (x=13)
fill_rect(14, 13, 11, 18, 13, 4)
slices[14][11][14] = 5; slices[14][13][14] = 5
slices[14][11][16] = 5; slices[14][13][16] = 5

# --- Z = 15: Picos mais altos da crista ---
slices[15][12][18] = 4; slices[15][12][17] = 4
slices[15][12][15] = 4
slices[15][12][13] = 4

with open(os.path.join(VOXELS_DIR, 'chicken_slices.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'name': 'Galinha Cocoricó',
        'width': W,
        'height': H,
        'num_slices': NUM_SLICES,
        'palette': chicken_pal,
        'slices': slices
    }, f, indent=2)

print('chicken_slices.json atualizado com 24x24 x 16 slices!')
