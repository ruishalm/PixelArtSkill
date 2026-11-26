import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOXELS_DIR = os.path.join(ROOT, 'assets', 'voxels')

def make_grid(w, h, fill=0):
    return [[fill for _ in range(w)] for _ in range(h)]

def to_strings(slices):
    res = []
    for s in slices:
        res.append([''.join(str(v) for v in row) for row in s])
    return res

# ==============================================================================
# A. COZINHA (kitchen_pack.json)
# ==============================================================================
k_pack = {}

# 1. BANCADA CONTÍNUA DE PAREDE A PAREDE (140 x 22 x 24 slices)
# Ocupa toda a parede norte de lado a lado!
# Esquerda: armário e gaveteiro (x: 2..26)
# Centro-esquerda: fogão 4 bocas com forno de vidro (x: 28..58)
# Centro: bancada de preparo com tábua de corte (x: 60..86)
# Centro-direita: pia inox com cuba dupla e torneira curva cromada (x: 88..118)
# Direita: escorredor e bancada final (x: 120..138)
kw, kh = 140, 22
k_slices = []
for z in range(24):
    g = make_grid(kw, kh, 0)
    if z == 0:
        # Rodapé contínuo em toda a extensão
        for y in range(4, kh):
            for x in range(2, kw - 2):
                g[y][x] = 1 if (y == kh - 1 or x in (2, kw - 3)) else 2
    elif 1 <= z <= 15:
        # Gabinetes, gavetas e forno
        for y in range(3, kh):
            for x in range(1, kw - 1):
                # FOGÃO RETRÔ (x: 28..58)
                if 28 <= x <= 58:
                    if y == kh - 1:
                        if z in (5, 6, 7, 8, 9, 10) and 34 <= x <= 52:
                            g[y][x] = 8 # Visor de vidro do forno
                        elif z == 12 and 33 <= x <= 53:
                            g[y][x] = 5 # Barra puxador cromada
                        elif z == 14 and (x - 30) % 6 in (0, 1):
                            g[y][x] = 2 # 4 Botões do fogão
                        else:
                            g[y][x] = 6 # Corpo inox/aço
                    else:
                        g[y][x] = 6
                else:
                    # ARMÁRIOS E GAVETAS DE COZINHA (Off-white com puxadores)
                    if y == kh - 1:
                        # Divisórias verticais e puxadores
                        if x in (2, 27, 59, 87, 119, kw - 2):
                            g[y][x] = 1 # Divisória
                        elif z in (7, 13) and (x % 14 in (6, 7)):
                            g[y][x] = 2 # Puxador
                        else:
                            g[y][x] = 1 if z in (6, 12) else 3 # Portas/frente
                    else:
                        g[y][x] = 1
    elif z in (16, 17):
        # TAMPO CONTÍNUO DE MÁRMORE BRANCO (Chanfrado na frente)
        for y in range(2, kh):
            for x in range(0, kw):
                # Cuba da pia afundada (x: 88..114, y: 5..17)
                if 88 <= x <= 114 and 5 <= y <= 17:
                    g[y][x] = 4 if z == 16 else 0 # Cuba rebaixada
                elif 30 <= x <= 56 and 4 <= y <= 18:
                    g[y][x] = 6 # Mesa de inox do fogão
                else:
                    g[y][x] = 3 # Mármore branco brilhante
    elif 18 <= z <= 23:
        # ACESSÓRIOS SOBRE O TAMPO: Bocas do fogão, torneira alta e tábuas
        # 4 Bocas de fogão (x: 30..56, y: 4..18)
        if z in (18, 19):
            for bx, by in [(36, 8), (50, 8), (36, 14), (50, 14)]:
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if abs(dx) + abs(dy) <= 2:
                            g[by + dy][bx + dx] = 6
                            if z == 18 and dx == 0 and dy == 0:
                                g[by][bx] = 7 # Chama acesa laranja
        # Tábua de corte rústica no centro (x: 68..78, y: 7..15, z=18)
        if z == 18:
            for ty in range(7, 16):
                for tx in range(68, 79):
                    g[ty][tx] = 9
        # Torneira alta curva cromada sobre a pia (x: 101, y: 4..8, z=18..23)
        if 18 <= z <= 21:
            g[5][101] = 5
        elif z == 22:
            g[5][101] = 5; g[6][101] = 5; g[7][101] = 5
        elif z == 23:
            g[8][101] = 5
        # Pote de temperos à esquerda (x: 10..14, y: 6..10, z=18..20)
        if 18 <= z <= 20:
            for py in range(6, 11):
                for px in range(10, 15):
                    g[py][px] = 9 if z == 20 else 2
    k_slices.append(g)
k_pack['kitchen_counter'] = to_strings(k_slices)

# 2. GELADEIRA RETRÔ VINTAGE (26 x 22 x 44 slices)
fw, fh = 26, 22
f_slices = []
for z in range(44):
    g = make_grid(fw, fh, 0)
    is_top = (z >= 41)
    for y in range(2, fh):
        for x in range(2, fw - 2):
            if (x in (2, fw - 3) and y in (2, fh - 1)): continue
            if z == 0:
                g[y][x] = 1
            elif is_top:
                if z == 43 and (x in (2, 3, fw - 4, fw - 3) or y in (2, 3, fh - 1)): continue
                g[y][x] = 3
            else:
                if y == fh - 1:
                    if z == 26: g[y][x] = 4
                    elif 16 <= z <= 24 and x == 4: g[y][x] = 5
                    elif 30 <= z <= 38 and x == 4: g[y][x] = 5
                    elif z == 20 and x in (12, 13): g[y][x] = 6
                    elif z == 16 and x in (16, 17): g[y][x] = 7
                    elif z == 34 and x in (14, 15): g[y][x] = 8
                    else: g[y][x] = 3 if x > 14 else 2
                else:
                    g[y][x] = 2 if x > 4 else 4
    f_slices.append(g)
k_pack['fridge_retro'] = to_strings(f_slices)

# 3. APARADOR DE MADEIRA (32 x 16 x 22 slices)
sw, sh = 32, 16
s_slices = []
for z in range(22):
    g = make_grid(sw, sh, 0)
    if z < 3:
        for y in (3, sh - 3):
            for x in (3, 4, sw - 5, sw - 4): g[y][x] = 1
    elif 3 <= z <= 15:
        for y in range(2, sh):
            for x in range(2, sw - 2):
                if y == sh - 1:
                    g[y][x] = 3 if z in (7, 12) else (1 if x in (sw//2, 2, sw-3) else 2)
                else: g[y][x] = 2
    elif z in (16, 17):
        for y in range(1, sh):
            for x in range(1, sw - 1): g[y][x] = 3 if y == sh - 1 else 2
    elif 18 <= z <= 21:
        for by in range(6, 11):
            for bx in range(10, 15): g[by][bx] = 4
        g[8][9] = 5; g[8][15] = 5
        if z in (18, 19):
            for cy in range(7, 10):
                for cx in range(21, 24): g[cy][cx] = 6
            g[8][24] = 6
    s_slices.append(g)
k_pack['kitchen_sideboard'] = to_strings(s_slices)

# 4. MESA DE JANTAR QUADRADA BEM MAIOR (48 x 48 x 20 slices)
# Formato Quadrado robusto com 4 pernas chanfradas e tampo amplo
dt_w, dt_h = 48, 48
dt_slices = []
for z in range(20):
    g = make_grid(dt_w, dt_h, 0)
    if z < 15: # 4 Pernas quadradas de madeira maciça torneadas
        for py in (4, dt_h - 10):
            for px in (4, dt_w - 10):
                for dy in range(6):
                    for dx in range(6):
                        # Perna chanfrada
                        val = 3 if (dx == 0 or dy == 0) else (1 if (dx == 5 or dy == 5) else 2)
                        g[py + dy][px + dx] = val
        if z in (13, 14): # Travessa/saia estrutural inferior da mesa
            for y in range(6, dt_h - 6):
                for x in (6, 7, dt_w - 8, dt_w - 7): g[y][x] = 2
            for x in range(6, dt_w - 6):
                for y in (6, 7, dt_h - 8, dt_h - 7): g[y][x] = 2
    elif 15 <= z <= 17: # Tampo quadrado maciço de carvalho
        for y in range(2, dt_h - 2):
            for x in range(2, dt_w - 2):
                # Borda chanfrada destacada
                if x in (2, dt_w - 3) or y in (2, dt_h - 3):
                    g[y][x] = 1 if (x == 2 or y == 2) else 3
                else:
                    g[y][x] = 2
    elif z in (18, 19): # Toalha central quadrada ou detalhe de marchetaria
        for y in range(10, dt_h - 10):
            for x in range(10, dt_w - 10):
                g[y][x] = 4 if z == 18 else (5 if (x in (10, dt_w - 11) or y in (10, dt_h - 11)) else 4)
    dt_slices.append(g)
k_pack['dining_table'] = to_strings(dt_slices)

# 5. CADEIRAS DE JANTAR (14 x 14 x 22 slices)
cw, ch = 14, 14
c_slices = []
for z in range(22):
    g = make_grid(cw, ch, 0)
    if z < 9:
        for py in (2, ch - 3):
            for px in (2, cw - 3): g[py][px] = 1
    elif z in (9, 10):
        for y in range(1, ch - 1):
            for x in range(1, cw - 1): g[y][x] = 3 if y >= ch - 3 else 2
    elif z == 11:
        for y in range(2, ch - 2):
            for x in range(2, cw - 2): g[y][x] = 4
    elif 12 <= z <= 21:
        for x in (2, 3, cw - 4, cw - 3, 6, 7): g[2][x] = 2 if (z < 20) else 3
        if z in (20, 21):
            for x in range(1, cw - 1): g[2][x] = 3
    c_slices.append(g)
k_pack['dining_chair'] = to_strings(c_slices)

# 6. FRUTEIRA DE MESA (14 x 14 x 8 slices)
bw, bh = 14, 14
b_slices = []
for z in range(8):
    g = make_grid(bw, bh, 0)
    if z == 0:
        for y in range(4, 10):
            for x in range(4, 10): g[y][x] = 2
    elif z in (1, 2):
        for y in range(2, bh - 2):
            for x in range(2, bw - 2):
                dist = (x - 6.5)**2 + (y - 6.5)**2
                if 3**2 <= dist <= 5.5**2: g[y][x] = 1
    elif 3 <= z <= 7:
        for y in range(4, 8):
            for x in range(4, 8): g[y][x] = 3
        for y in range(4, 8):
            for x in range(7, 11):
                if (x + y) % 2 == 0 or z in (4, 5): g[y][x] = 4
        for y in range(7, 11):
            for x in range(5, 9): g[y][x] = 5
        if z == 7: g[5][5] = 6; g[6][5] = 6
    b_slices.append(g)
k_pack['fruit_bowl'] = to_strings(b_slices)

with open(os.path.join(VOXELS_DIR, 'kitchen_pack.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(k_pack, f, indent=2)
print("SUCCESS: kitchen_pack.json generated with wall-to-wall counter and big square table!")

# ==============================================================================
# B. JARDIM (garden_pack.json)
# ==============================================================================
g_pack = {}

# 1. CARVALHO CENTENÁRIO COM TAMANHO DOBRADO E GALHO HORIZONTAL ROBUSTO
# (72 x 64 x 60 slices) - Imponente, tronco maciço com raízes espalhadas,
# galho horizontal grosso saindo para a esquerda (onde o pneu é amarrado!)
# e copa majestosa volumosa em camadas!
tw, th = 72, 64
tree_slices = []
# Centro do tronco: cx = 46, cy = 34
for z in range(60):
    g = make_grid(tw, th, 0)
    
    # RAÍZES E TRONCO MACIÇO
    if z < 36:
        # Tronco afunila suavemente de raio 9 até raio 6.5
        tr_rad = 9.0 - (z * 0.08)
        for y in range(22, 46):
            for x in range(34, 58):
                dist = (x - 46)**2 + ((y - 34) * 1.1)**2
                if dist <= tr_rad**2:
                    val = 3 if x > 47 else (1 if x < 44 else 2)
                    g[y][x] = val
        # Raízes antigas espalhadas no chão
        if z < 8:
            for rx, ry, rrad in [(32, 34, 4), (58, 36, 4.5), (46, 22, 4), (48, 45, 5), (36, 42, 3.5)]:
                for dy in range(-int(rrad), int(rrad) + 1):
                    for dx in range(-int(rrad), int(rrad) + 1):
                        if dx*dx + dy*dy <= rrad*rrad:
                            g[ry + dy][rx + dx] = 1

    # GALHO HORIZONTAL LONGO E ROBUSTO (z = 32 .. 39)
    # Estende do tronco (x=46) até x=16 em y=32..36!
    # O pneu ficará pendurado exatamente em x=24, y=34!
    if 32 <= z <= 39:
        for x in range(16, 48):
            for y in (33, 34, 35):
                val = 3 if (z >= 36 and y == 33) else (1 if y == 35 else 2)
                g[y][x] = val
        # Reforço de bifurcação do galho no tronco
        if z <= 36:
            for x in range(38, 48):
                for y in range(31, 38):
                    g[y][x] = 2

    # COPA FRONDOSA GIGANTE EM NUVENS DE FOLHAS (z = 30 .. 59)
    if z >= 30:
        # Raio da copa esférica
        canopy_rad = min(30, (z - 28) * 1.8) if z < 50 else max(10, (60 - z) * 3.0)
        for y in range(6, th - 6):
            for x in range(8, tw - 4):
                # Centro da copa em cx=42, cy=33
                dist = ((x - 42) * 0.9)**2 + (y - 33)**2
                if dist <= canopy_rad**2:
                    val = 6 if (z >= 48 and y >= 32) else (5 if dist <= (canopy_rad - 3)**2 else 4)
                    # Frutinhas vermelhas / flores na copa
                    if (x * 11 + y * 17 + z * 5) % 41 == 0:
                        val = 7
                    g[y][x] = val
    tree_slices.append(g)
g_pack['garden_tree'] = to_strings(tree_slices)

# 2. BALANÇO DE PNEU EM PÉ (VERTICAL / UPRIGHT TIRE) COM UMA ÚNICA CORDA
# (18 x 20 x 48 slices)
# O pneu fica EM PÉ (vertical), com o furo circular aberto de frente para a câmera!
# Popó senta no fundo do pneu!
# Uma ÚNICA corda amarrada no topo do pneu sobe reta até o galho da árvore!
# Paleta: 0:trans, 1:borracha preta (#0F172A), 2:borracha cinza (#334155), 3:borracha friso (#475569), 4:corda juta (#B45309), 5:corda luz (#F59E0B)
tw_t, th_t = 18, 20
tire_slices = []
# O pneu tem diâmetro 22 slices (z=0..21)
# Centro em x=9, y=10
for z in range(48):
    g = make_grid(tw_t, th_t, 0)
    
    if z <= 21:
        # PNEU EM PÉ: O círculo do pneu está no plano vertical (x, z)
        # cz = 10.5, cx = 9.0. Raio externo: 9.5, Raio interno: 5.0
        # Espessura do pneu em y: de y=6 até y=14
        r_outer = 9.8
        r_inner = 4.8
        dist_z = abs(z - 10.5)
        
        for y in range(6, 15):
            for x in range(0, tw_t):
                dist_x = abs(x - 9.0)
                dist_sq = dist_x**2 + dist_z**2
                
                if (r_inner**2 <= dist_sq <= r_outer**2):
                    # Borracha do pneu com textura e profundidade
                    is_rim = (y in (6, 14) or x in (0, tw_t - 1) or z in (0, 21))
                    g[y][x] = 3 if is_rim else (2 if y >= 10 else 1)
                    
        # Nó de amarração da corda no topo do pneu (z=20..21, x=8..10, y=9..11)
        if z in (20, 21):
            for y in (9, 10, 11):
                for x in (8, 9, 10):
                    g[y][x] = 5 if z == 21 else 4

    elif z >= 22:
        # UMA ÚNICA CORDA CENTRAL SUBINDO ATÉ O GALHO DA ÁRVORE (z=22..47)
        # Corda rústica de juta em x=9, y=10
        g[10][9] = 5 if (z % 2 == 0) else 4
        g[10][8] = 4
        g[9][9] = 4

    tire_slices.append(g)
g_pack['tire_swing'] = to_strings(tire_slices)

# 3. CADEIRA DE VARANDA (18 x 20 x 24 slices)
pw, ph = 18, 20
p_slices = []
for z in range(24):
    g = make_grid(pw, ph, 0)
    if z < 3:
        for x in (2, 3, pw - 4, pw - 3):
            for y in range(2, ph - 2): g[y][x] = 1
    elif 3 <= z <= 8:
        for x in (2, 3, pw - 4, pw - 3):
            for y in (3, 4, ph - 5, ph - 4): g[y][x] = 1
    elif z in (9, 10):
        for y in range(2, ph - 2):
            for x in range(2, pw - 2): g[y][x] = 3 if y >= ph - 4 else 2
    elif z == 11:
        for y in range(3, ph - 3):
            for x in range(3, pw - 3): g[y][x] = 4
    elif 12 <= z <= 23:
        for x in range(2, pw - 2): g[3][x] = 3 if (z >= 21) else (2 if (x in (2, pw - 3) or x % 3 == 0) else 0)
        if 12 <= z <= 17:
            for y in range(3, ph - 3): g[y][2] = 2; g[y][pw - 3] = 2
    p_slices.append(g)
g_pack['porch_chair'] = to_strings(p_slices)

# 4. CARRINHO DE MÃO COM FLORES (28 x 16 x 18 slices)
ww, wh = 28, 16
w_slices = []
for z in range(18):
    g = make_grid(ww, wh, 0)
    if z < 5:
        if z in (1, 2, 3):
            for y in range(6, 10): g[y][4] = 1
        for y in (3, wh - 4):
            for x in (20, 21): g[y][x] = 2
    elif 5 <= z <= 11:
        for y in range(2, wh - 2):
            for x in range(6, ww - 2):
                if z in (5, 6) or x in (6, ww - 3) or y in (2, wh - 3): g[y][x] = 3
                else: g[y][x] = 4
        if z == 10:
            for x in range(22, ww): g[4][x] = 2; g[wh - 5][x] = 2
    elif 12 <= z <= 17:
        for y in range(3, wh - 3):
            for x in range(8, ww - 4):
                f_type = (x * 5 + y * 7 + z * 3) % 4
                if f_type == 0: g[y][x] = 5
                elif f_type == 1: g[y][x] = 6
                elif f_type == 2: g[y][x] = 7
                else: g[y][x] = 8
    w_slices.append(g)
g_pack['wheelbarrow_flowers'] = to_strings(w_slices)

# 5. CANTEIRO DE FLORES (36 x 14 x 8 slices)
fb_w, fb_h = 36, 14
fb_slices = []
for z in range(8):
    g = make_grid(fb_w, fb_h, 0)
    if z < 3:
        for y in range(1, fb_h - 1):
            for x in range(1, fb_w - 1):
                if x in (1, fb_w - 2) or y in (1, fb_h - 2): g[y][x] = 2
                else: g[y][x] = 3
    elif 3 <= z <= 7:
        for y in range(2, fb_h - 2):
            for x in range(2, fb_w - 2):
                if (x + y + z) % 3 == 0:
                    if x % 4 == 0: g[y][x] = 4
                    elif x % 4 == 1: g[y][x] = 5
                    elif x % 4 == 2: g[y][x] = 6
                    elif x % 4 == 3: g[y][x] = 7
    fb_slices.append(g)
g_pack['flower_bed'] = to_strings(fb_slices)

with open(os.path.join(VOXELS_DIR, 'garden_pack.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(g_pack, f, indent=2)
print("SUCCESS: garden_pack.json generated with giant oak, upright tire swing, and flowerbeds!")
