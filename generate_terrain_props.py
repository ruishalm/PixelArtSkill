import json
import math
from collections import deque


def make_grid(w, h, fill=0):
    return [[fill for _ in range(w)] for _ in range(h)]


def make_volume(w, h, z_count, fill=0):
    return [make_grid(w, h, fill) for _ in range(z_count)]


def encode_char(idx):
    if idx < 10:
        return str(idx)
    return chr(ord('a') + idx - 10)


def to_strings(slices):
    return [
        [''.join(encode_char(v) for v in row) for row in s]
        for s in slices
    ]


def hash3(x, y, z):
    n = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791)
    return (n ^ (n >> 13)) & 0xFFFFFFFF


def build_pine_tree():
    """1. pine_tree (20 x 20 x 34)"""
    w, h, z_count = 20, 20, 34
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: sombra escura tronco
        '#6B4226',  # 2: tronco base
        '#8C5A38',  # 3: tronco iluminado
        '#1B4332',  # 4: verde-pinheiro sombra base
        '#2D6A4F',  # 5: verde-pinheiro médio
        '#40916C',  # 6: verde-pinheiro claro
        '#74C69D',  # 7: pontas iluminadas nas bordas/topo
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 9.5, 9.5

    # Tronco central (z=0..8) com leve alargamento na raiz (z=0..1)
    for z in range(9):
        rad = 2.6 if z == 0 else (2.1 if z == 1 else 1.7)
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= rad * rad:
                    if x > cx + 0.5 and y >= cy:
                        vol[z][y][x] = 3
                    elif y < cy - 0.5 or x < cx - 0.8:
                        vol[z][y][x] = 1
                    else:
                        vol[z][y][x] = 2

    # 3 camadas cônicas de copa (z=7..33)
    cones = [
        (7, 17, 9.0, 2.5),   # camada inferior: z=7..17
        (15, 25, 7.6, 2.0),  # camada média: z=15..25
        (23, 33, 5.8, 0.4),  # camada superior: z=23..33
    ]

    for z_start, z_end, r_bot, r_top in cones:
        span = z_end - z_start
        for z in range(z_start, z_end + 1):
            t = (z - z_start) / span
            base_r = r_bot * (1.0 - t) + r_top * t
            for y in range(h):
                for x in range(w):
                    dx = x - cx
                    dy = y - cy
                    dist = (dx * dx + dy * dy) ** 0.5
                    # Recorte orgânico de galhos em estrela/pinho
                    notch = ((abs(int(dx * 2)) + abs(int(dy * 2)) + z) % 3 == 0) * 0.55
                    # Última camada fecha firme no topo
                    if z >= 31:
                        notch = 0.0
                    eff_r = base_r - notch
                    if dist <= eff_r:
                        is_edge = dist >= eff_r - 1.25
                        is_lit_side = (dx + dy) > 0.5
                        if z >= 31 or (is_edge and is_lit_side and t > 0.25):
                            col = 7
                        elif z <= z_start + 1 and t < 0.25 and not is_lit_side:
                            col = 4
                        elif is_edge and (dy >= 0 or dx >= 0):
                            col = 6
                        elif t < 0.35 and dist > eff_r * 0.55:
                            col = 4
                        elif t > 0.65 or is_lit_side:
                            col = 6 if (hash3(x, y, z) % 3 == 0) else 5
                        else:
                            col = 5 if (y >= cy - 1.5) else 4
                        vol[z][y][x] = col

    # Garante topo nítido conectado em z=33
    vol[33][9][9] = 7
    vol[33][9][10] = 7
    vol[33][10][9] = 7
    vol[33][10][10] = 7

    return {'palette': palette, 'slices': to_strings(vol)}


def build_sakura_oak():
    """2. sakura_oak (32 x 32 x 42)"""
    w, h, z_count = 32, 32, 42
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: sombra tronco escura
        '#5C3A28',  # 2: tronco médio
        '#80533B',  # 3: tronco iluminado
        '#9D3B68',  # 4: sombra magenta suave
        '#D95B8A',  # 5: rosa cerejeira profundo
        '#F48FB1',  # 6: rosa cerejeira médio
        '#FFC2D4',  # 7: rosa claro
        '#FFF5F8',  # 8: flores brancas/rosa claro
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 15.5, 15.5

    # Tronco largo com raízes espalhadas (z=0..18)
    roots = [
        (-1.0, 0.0, 4.5),
        (1.0, 0.2, 4.2),
        (0.0, -1.0, 4.2),
        (0.2, 1.0, 4.5),
        (-0.8, 0.8, 3.8),
        (0.8, -0.7, 3.8),
    ]
    for z in range(19):
        t = z / 18.0
        trunk_r = 4.2 - 1.3 * t
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                in_trunk = (dx * dx + dy * dy) <= trunk_r * trunk_r
                in_root = False
                if z < 6:
                    root_reach = (1.0 - z / 6.0)
                    for rx_dir, ry_dir, r_len in roots:
                        rx = cx + rx_dir * (2.5 + r_len * root_reach)
                        ry = cy + ry_dir * (2.5 + r_len * root_reach)
                        r_rad = 1.9 * root_reach + 0.9
                        # Segmento do centro até a ponta da raiz
                        for step in range(4):
                            s = step / 3.0
                            px = cx + (rx - cx) * s
                            py = cy + (ry - cy) * s
                            if (x - px) ** 2 + (y - py) ** 2 <= (r_rad * (1.15 - 0.35 * s)) ** 2:
                                in_root = True
                                break
                if in_trunk or in_root:
                    if dx + dy > 1.2:
                        vol[z][y][x] = 3
                    elif dx + dy < -1.2:
                        vol[z][y][x] = 1
                    else:
                        vol[z][y][x] = 2

    # Galhos principais sustentando a copa (z=13..22)
    branches = [
        ((15.5, 15.5, 13), (8.0, 15.0, 21), 2.1),
        ((15.5, 15.5, 14), (23.0, 16.0, 22), 2.1),
        ((15.5, 15.5, 14), (15.0, 8.0, 21), 2.0),
        ((15.5, 15.5, 15), (16.5, 23.0, 22), 2.1),
        ((15.5, 15.5, 16), (15.5, 15.5, 24), 2.2),
    ]
    for (x0, y0, z0), (x1, y1, z1), r_b in branches:
        steps = 16
        for i in range(steps + 1):
            s = i / steps
            bx = x0 + (x1 - x0) * s
            by = y0 + (y1 - y0) * s
            bz = z0 + (z1 - z0) * s
            rad = r_b * (1.0 - 0.35 * s)
            for z in range(max(0, int(bz - rad - 1)), min(z_count, int(bz + rad + 2))):
                for y in range(max(0, int(by - rad - 1)), min(h, int(by + rad + 2))):
                    for x in range(max(0, int(bx - rad - 1)), min(w, int(bx + rad + 2))):
                        if (x - bx) ** 2 + (y - by) ** 2 + (z - bz) ** 2 <= rad * rad:
                            vol[z][y][x] = 3 if (z > bz and y >= by) else (1 if z < bz - 0.4 else 2)

    # Copa exuberante arredondada em nuvens de cerejeira (z=16..41)
    # Lobos esféricos/elipsoidais conectados formando uma copa majestosa
    lobes = [
        (15.5, 15.5, 28.0, 11.5, 11.5, 12.5),  # massa central até z=40..41
        (9.5, 15.0, 24.5, 7.8, 7.8, 7.5),      # lobo oeste
        (22.0, 16.0, 25.5, 7.8, 7.8, 7.8),     # lobo leste
        (15.0, 9.5, 25.0, 8.0, 7.5, 7.5),      # lobo norte/traseira
        (16.0, 22.0, 25.5, 8.2, 7.6, 7.8),     # lobo sul/frente
        (11.0, 10.5, 31.0, 6.8, 6.8, 6.8),     # coroa NW
        (20.5, 20.5, 32.0, 7.0, 7.0, 7.0),     # coroa SE
        (15.5, 15.5, 35.5, 7.2, 7.2, 6.2),     # cúpula topo (z até 41)
    ]

    for z in range(16, z_count):
        for y in range(h):
            for x in range(w):
                best_d = 999.0
                for lx, ly, lz, rx, ry, rz in lobes:
                    d = ((x - lx) / rx) ** 2 + ((y - ly) / ry) ** 2 + ((z - lz) / rz) ** 2
                    if d < best_d:
                        best_d = d
                if best_d <= 1.0:
                    # Não sobrescrever tronco interno aparente abaixo de z=19
                    if z < 19 and vol[z][y][x] in (1, 2, 3):
                        continue
                    # Sombreamento da copa
                    h_val = hash3(x, y, z)
                    light = (z - 22.0) * 0.08 + (y - cy) * 0.03 + (x - cx) * 0.025
                    if z >= 35 or (z >= 29 and light > 0.35):
                        if h_val % 7 == 0 or (z >= 39 and h_val % 3 == 0):
                            col = 8  # flores brancas/rosa muito claro salpicadas no topo
                        elif h_val % 3 == 0 or z >= 37:
                            col = 7
                        else:
                            col = 6
                    elif z <= 21 or (y < cy - 3 and z < 28) or best_d > 0.88 and z < 26:
                        col = 4  # sombra magenta suave na base/parte inferior
                    elif light < -0.15:
                        col = 5
                    else:
                        if h_val % 13 == 0 and z >= 26:
                            col = 8
                        elif h_val % 5 == 0 and z >= 24:
                            col = 7
                        else:
                            col = 6 if light > 0.1 else 5
                    vol[z][y][x] = col

    return {'palette': palette, 'slices': to_strings(vol)}


def build_boulder_large():
    """3. boulder_large (14 x 14 x 12)"""
    w, h, z_count = 14, 14, 12
    palette = [
        'rgba(0,0,0,0)',
        '#2E3440',  # 1: sombra ardósia profunda
        '#4C566A',  # 2: ardósia escura
        '#6B778D',  # 3: ardósia média
        '#8F9BB0',  # 4: ardósia clara
        '#B4C0D3',  # 5: quina iluminada
        '#3A6B35',  # 6: musgo escuro
        '#65A34E',  # 7: musgo claro
    ]
    vol = make_volume(w, h, z_count, 0)

    # Blocos/facetas assimétricas sobrepostas criando degraus de pedra
    # (cx, cy, cz, rx, ry, rz) com norma L-inf/octogonal facetada
    facets = [
        (6.5, 6.8, 3.5, 5.8, 5.4, 4.5),   # massa principal baixa
        (5.0, 5.5, 5.8, 4.3, 4.0, 5.2),   # bloco alto esquerdo/traseiro (até z=11)
        (8.8, 7.8, 4.0, 3.8, 3.6, 3.5),   # degrau lateral direito (até z=7)
        (6.8, 9.2, 2.5, 4.0, 3.2, 2.8),   # degrau frontal baixo (até z=5)
        (4.5, 5.0, 9.0, 2.8, 2.6, 2.6),   # cume facetado (até z=11)
    ]

    for z in range(z_count):
        for y in range(h):
            for x in range(w):
                inside = False
                for fx, fy, fz, rx, ry, rz in facets:
                    nx = abs(x - fx) / rx
                    ny = abs(y - fy) / ry
                    nz = abs(z - fz) / rz
                    # Métrica facetada (mistura de octaedro + cubo chanfrado)
                    if (nx + ny + nz) <= 1.55 and max(nx, ny, nz) <= 1.0:
                        inside = True
                        break
                if inside:
                    vol[z][y][x] = 3

    # Sombreamento por normais/exposição + musgo verde no topo dos degraus
    for z in range(z_count):
        for y in range(h):
            for x in range(w):
                if vol[z][y][x] == 0:
                    continue
                is_top = (z == z_count - 1) or (vol[z + 1][y][x] == 0)
                is_front = (y == h - 1) or (vol[z][y + 1][x] == 0)
                is_right = (x == w - 1) or (vol[z][y][x + 1] == 0)
                is_back = (y == 0) or (vol[z][y - 1][x] == 0)
                is_left = (x == 0) or (vol[z][y][x - 1] == 0)

                # Manchas de musgo no topo (z >= 4 e exposto acima)
                moss_noise = ((x * 3 + y * 5 + z) % 11)
                in_moss_patch = (
                    ((x - 5) ** 2 + (y - 5) ** 2 <= 9) or
                    ((x - 9) ** 2 + (y - 8) ** 2 <= 4)
                )
                if is_top and z >= 5 and in_moss_patch and moss_noise < 7:
                    vol[z][y][x] = 7 if (x + y >= 10) else 6
                elif is_top and (is_front or is_right):
                    vol[z][y][x] = 5
                elif is_top:
                    vol[z][y][x] = 4
                elif is_back or is_left or z <= 1:
                    vol[z][y][x] = 1 if (z == 0 or (is_back and is_left)) else 2
                elif is_front or is_right:
                    vol[z][y][x] = 4 if z >= 6 else 3
                else:
                    vol[z][y][x] = 3

    return {'palette': palette, 'slices': to_strings(vol)}


def build_mushroom_giant():
    """4. mushroom_giant (16 x 16 x 16)"""
    w, h, z_count = 16, 16, 16
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: sombra sob o chapéu
        '#C9B193',  # 2: caule sombra / lamelas
        '#EAD8BE',  # 3: caule creme médio
        '#FBF3E4',  # 4: caule creme iluminado
        '#9E1F28',  # 5: chapéu vermelho sombra
        '#D93038',  # 6: chapéu vermelho vivo
        '#F2545B',  # 7: chapéu vermelho iluminado
        '#FFF8F0',  # 8: pintinhas brancas
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 7.5, 7.5

    # Caule creme gordinho (z=0..9)
    for z in range(10):
        if z <= 1:
            rad = 3.8
        elif z <= 3:
            rad = 3.5
        elif z <= 6:
            rad = 3.0
        elif z == 7:
            rad = 3.2
        else:
            rad = 3.6
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= rad * rad:
                    if z == 9:
                        vol[z][y][x] = 1  # sombra das lamelas sob o chapéu
                    elif dx + dy > 1.2:
                        vol[z][y][x] = 4
                    elif dx + dy < -1.0 or z == 8:
                        vol[z][y][x] = 2
                    else:
                        vol[z][y][x] = 3

    # Chapéu vermelho vivo arredondado com topo relativamente plano em z=13..15
    cap_radii = {
        9: 6.4,
        10: 7.2,
        11: 7.4,
        12: 7.0,
        13: 6.3,  # topo relativamente plano começa a fechar suave
        14: 5.4,
        15: 4.3,  # plataforma larga no topo para o gato pular!
    }
    # Centros das pintinhas brancas na superfície do chapéu
    spots = [
        (7.5, 7.5, 15.0, 1.4),   # pinta central no topo
        (4.5, 5.5, 14.2, 1.35),  # topo NW
        (10.5, 6.0, 14.2, 1.3),  # topo NE
        (6.5, 10.5, 14.0, 1.3),  # topo S
        (2.2, 7.5, 11.8, 1.35),  # lateral W
        (12.8, 8.0, 11.8, 1.35), # lateral E
        (7.5, 2.2, 11.8, 1.35),  # traseira N
        (7.8, 12.8, 11.6, 1.4),  # frente S
        (4.0, 11.5, 12.2, 1.2),  # frente SW
        (11.5, 11.2, 12.2, 1.2), # frente SE
        (3.8, 3.8, 12.2, 1.2),   # trás NW
        (11.4, 3.8, 12.2, 1.2),  # trás NE
    ]

    for z, rad in cap_radii.items():
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist <= rad:
                    if z == 9 and dist <= 4.2:
                        # Parte interna debaixo do chapéu (lamelas creme)
                        vol[z][y][x] = 1 if dist <= 3.6 else 2
                        continue
                    # Checa se pertence a uma pintinha branca na casca externa
                    is_outer = (z >= 13 and dist >= rad - 1.5) or (z == 15) or (dist >= rad - 1.35)
                    is_spot = False
                    if is_outer and z >= 10:
                        for sx, sy, sz, sr in spots:
                            if (x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2 <= sr * sr:
                                is_spot = True
                                break
                    if is_spot:
                        vol[z][y][x] = 8
                    elif z == 9 or (z == 10 and dist >= rad - 1.0 and dy < 0):
                        vol[z][y][x] = 5
                    elif z >= 14 or (dx + dy > 1.5 and z >= 11):
                        vol[z][y][x] = 7
                    elif dy < -2.0 and z <= 12:
                        vol[z][y][x] = 5
                    else:
                        vol[z][y][x] = 6

    return {'palette': palette, 'slices': to_strings(vol)}


def build_wood_sign():
    """5. wood_sign (10 x 8 x 14)"""
    w, h, z_count = 10, 8, 14
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: sombra madeira & texto gravado
        '#5C3A21',  # 2: madeira escura / moldura
        '#8C5835',  # 3: madeira rústica média
        '#B87B4B',  # 4: face da placa clara
        '#D69F6B',  # 5: realce borda superior
    ]
    vol = make_volume(w, h, z_count, 0)

    # Poste vertical (z=0..13) em x=4..5, y=3..4 (com sapata rústica em z=0)
    for z in range(z_count):
        if z == 0:
            for y in range(2, 6):
                for x in range(3, 7):
                    vol[z][y][x] = 2 if (x in (3, 6) or y in (2, 5)) else 3
        elif z < 13:
            for y in (3, 4):
                for x in (4, 5):
                    vol[z][y][x] = 3 if x == 5 else 2
        else:  # topo do poste z=13
            for y in (3, 4):
                for x in (4, 5):
                    vol[z][y][x] = 5

    # Placa horizontal rústica (z=7..12) voltada para a frente (y = H - 1 = 7)
    # Ocupa y=5..7 para conectar firmemente ao poste (y=4) e ter face em y=7
    for z in range(7, 13):
        for y in range(5, h):
            for x in range(0, w):
                # Cantos levemente chanfrados nas pontas da tábua
                if (x in (0, w - 1)) and (z in (7, 12)):
                    continue
                if y == h - 1:
                    # Face frontal (y=7): moldura e listras simulando texto gravado
                    is_border = (z in (7, 12) or x in (0, w - 1) or
                                 (x in (1, w - 2) and z in (8, 11)))
                    if is_border:
                        vol[z][y][x] = 5 if z == 12 else 2
                    elif z == 11 and 2 <= x <= 7:
                        vol[z][y][x] = 1 if x in (2, 3, 4, 6, 7) else 4  # linha 1 de texto
                    elif z == 9 and 2 <= x <= 7:
                        vol[z][y][x] = 1 if x in (2, 4, 5, 6) else 4     # linha 2 de texto
                    else:
                        vol[z][y][x] = 4
                elif y == 5:
                    vol[z][y][x] = 2 if z < 12 else 3
                else:
                    vol[z][y][x] = 5 if z == 12 else 3

    return {'palette': palette, 'slices': to_strings(vol)}


def build_campfire():
    """6. campfire (12 x 12 x 9)"""
    w, h, z_count = 12, 12, 9
    palette = [
        'rgba(0,0,0,0)',
        '#2B1D16',  # 1: cinza/carvão escuro
        '#4F5866',  # 2: pedra cinza escura
        '#7C8798',  # 3: pedra cinza média
        '#A6B1C2',  # 4: pedra cinza clara
        '#6E4226',  # 5: tora de madeira
        '#9C5E36',  # 6: tora iluminada
        '#D9381E',  # 7: brasa / chama vermelha-laranja
        '#F97316',  # 8: labareda laranja
        '#FACC15',  # 9: miolo amarelo brilhante
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 5.5, 5.5

    # Base de cinzas no centro (z=0) para conectar tudo ao chão
    for y in range(2, 10):
        for x in range(2, 10):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 4.3 ** 2:
                vol[0][y][x] = 1

    # Anel circular de pedrinhas cinzas (z=0..2)
    stone_positions = [
        (5.5, 1.2, 1.4, 2), (8.2, 2.0, 1.35, 2), (9.8, 4.3, 1.35, 2),
        (9.8, 7.2, 1.4, 2), (8.0, 9.6, 1.35, 2), (5.5, 10.2, 1.45, 2),
        (2.8, 9.5, 1.35, 2), (1.3, 7.0, 1.4, 2), (1.4, 4.2, 1.35, 2),
        (3.0, 2.0, 1.35, 2),
    ]
    for idx_s, (sx, sy, sr, max_sz) in enumerate(stone_positions):
        for z in range(max_sz + 1):
            rad = sr if z < 2 else sr * 0.72
            for y in range(h):
                for x in range(w):
                    if (x - sx) ** 2 + (y - sy) ** 2 <= rad * rad:
                        if z == max_sz:
                            vol[z][y][x] = 4 if (idx_s % 2 == 0) else 3
                        elif z == 0:
                            vol[z][y][x] = 2
                        else:
                            vol[z][y][x] = 3 if (x + y >= 10) else 2

    # Toras de madeira cruzadas (z=1..3)
    for z in (1, 2, 3):
        for t_i in range(-4, 5):
            # Tora 1: diagonal NW -> SE
            x1 = int(round(cx + t_i * 0.78))
            y1 = int(round(cy + t_i * 0.78))
            # Tora 2: diagonal NE -> SW
            x2 = int(round(cx + t_i * 0.78))
            y2 = int(round(cy - t_i * 0.78))
            for bx, by, log_z in [(x1, y1, 1 if z == 1 else 2), (x2, y2, 2 if z == 2 else 3)]:
                if z <= log_z and 2 <= bx < w - 2 and 2 <= by < h - 2:
                    dist_c = ((bx - cx) ** 2 + (by - cy) ** 2) ** 0.5
                    for dy in (0, 1) if z < 3 else (0,):
                        for dx in (0, 1) if z < 3 else (0,):
                            nx, ny = bx + dx, by + dy
                            if 2 <= nx < w - 2 and 2 <= ny < h - 2:
                                if dist_c < 1.6:
                                    vol[z][ny][nx] = 1 if z == 1 else 7
                                elif z == log_z:
                                    vol[z][ny][nx] = 6
                                else:
                                    vol[z][ny][nx] = 5

    # Brasas vivas no miolo (z=1..2)
    for z in (1, 2):
        for y in range(4, 8):
            for x in range(4, 8):
                if (x - cx) ** 2 + (y - cy) ** 2 <= 2.1 ** 2:
                    vol[z][y][x] = 7 if (x + y + z) % 2 == 0 else 8

    # Labareda laranja/amarela subindo no centro (z=3..8), toda conectada
    flame_layers = [
        # z=3: base da chama
        [(5, 5, 9), (6, 5, 9), (5, 6, 9), (6, 6, 9),
         (4, 5, 8), (7, 5, 8), (5, 4, 8), (6, 7, 8),
         (4, 6, 7), (7, 6, 7)],
        # z=4: corpo da labareda
        [(5, 5, 9), (6, 5, 9), (5, 6, 9), (6, 6, 8),
         (4, 5, 8), (5, 4, 7), (7, 6, 8), (6, 7, 7)],
        # z=5: afinando e serpenteando
        [(5, 5, 9), (6, 5, 8), (5, 6, 8), (6, 6, 8),
         (7, 6, 7), (4, 5, 7)],
        # z=6: duas pontas
        [(5, 5, 9), (6, 5, 8), (5, 6, 8), (7, 6, 8)],
        # z=7: ponta principal subindo
        [(5, 5, 8), (6, 5, 9)],
        # z=8: centelha final conectada
        [(6, 5, 9)],
    ]
    for idx_z, pts in enumerate(flame_layers):
        z = 3 + idx_z
        for px, py, col in pts:
            vol[z][py][px] = col

    return {'palette': palette, 'slices': to_strings(vol)}


def build_bush_berry():
    """7. bush_berry (12 x 12 x 9)"""
    w, h, z_count = 12, 12, 9
    palette = [
        'rgba(0,0,0,0)',
        '#1E3F20',  # 1: folhagem sombra profunda
        '#2D6A3E',  # 2: verde escuro
        '#40914C',  # 3: verde vivo
        '#6CC05E',  # 4: folha iluminada
        '#D62828',  # 5: frutinha vermelha
        '#FF6B6B',  # 6: frutinha vermelha brilho
        '#F4B400',  # 7: frutinha amarela
    ]
    vol = make_volume(w, h, z_count, 0)

    # Lobos fofos sobrepostos
    puffs = [
        (5.5, 5.5, 3.8, 4.8, 4.8, 4.8),  # centro até z=8
        (3.5, 6.2, 2.8, 3.2, 3.2, 3.2),  # esquerda
        (7.6, 5.8, 3.0, 3.3, 3.3, 3.4),  # direita
        (5.5, 3.5, 2.8, 3.3, 3.0, 3.2),  # trás
        (5.8, 7.6, 2.6, 3.4, 3.0, 3.0),  # frente
    ]

    for z in range(z_count):
        for y in range(h):
            for x in range(w):
                inside = False
                for px, py, pz, rx, ry, rz in puffs:
                    d = ((x - px) / rx) ** 2 + ((y - py) / ry) ** 2 + ((z - pz) / rz) ** 2
                    if d <= 1.0:
                        inside = True
                        break
                if inside:
                    vol[z][y][x] = 3

    # Sombreamento + frutinhas vermelhas e amarelas na superfície externa
    berries = [
        (2, 6, 4, 5), (3, 9, 3, 6), (5, 9, 5, 5), (8, 9, 3, 7),
        (9, 7, 5, 5), (10, 5, 3, 6), (8, 2, 4, 7), (4, 2, 3, 5),
        (5, 5, 8, 7), (7, 6, 7, 5), (3, 4, 6, 7), (8, 4, 6, 6),
        (6, 8, 6, 7), (4, 7, 7, 5),
    ]
    for z in range(z_count):
        for y in range(h):
            for x in range(w):
                if vol[z][y][x] == 0:
                    continue
                is_top = (z == z_count - 1) or (vol[z + 1][y][x] == 0)
                if z == 0 or (y <= 3 and z <= 2):
                    vol[z][y][x] = 1
                elif is_top and (x + y >= 10 or z >= 6):
                    vol[z][y][x] = 4
                elif y >= 6 or z >= 5:
                    vol[z][y][x] = 3
                else:
                    vol[z][y][x] = 2

    for bx, by, bz, bcol in berries:
        if vol[bz][by][bx] != 0:
            vol[bz][by][bx] = bcol

    return {'palette': palette, 'slices': to_strings(vol)}


def build_golden_fish():
    """8. golden_fish (12 x 8 x 6)"""
    w, h, z_count = 12, 8, 6
    palette = [
        'rgba(0,0,0,0)',
        '#2B1D16',  # 1: olhinho escuro
        '#9E4F0E',  # 2: sombra âmbar / ventre
        '#D97706',  # 3: âmbar médio
        '#F59E0B',  # 4: dourado vivo
        '#FBBF24',  # 5: dourado brilhante
        '#FEF08A',  # 6: reflexo amarelo claro no dorso
        '#FFFDF5',  # 7: brilho branco do olho
    ]
    vol = make_volume(w, h, z_count, 0)

    # Corpo rechonchudo do peixinho (x=3..11, centro y=3.5, z=2.5)
    # x=11 é o focinho, x=3 conecta na cauda
    for z in range(z_count):
        for y in range(h):
            for x in range(3, w):
                dx = (x - 7.0) / 4.3
                dy = (y - 3.5) / 2.7
                dz = (z - 2.35) / 2.5
                if dx * dx + dy * dy + dz * dz <= 1.0:
                    if z >= 4 and 4 <= x <= 9:
                        vol[z][y][x] = 6  # reflexo amarelo claro no dorso
                    elif z == 0 or (z == 1 and abs(y - 3.5) > 1.0):
                        vol[z][y][x] = 2
                    elif z == 3 or (z == 2 and x >= 8):
                        vol[z][y][x] = 5
                    else:
                        vol[z][y][x] = 4 if z >= 2 else 3

    # Nadadeira dorsal (x=5..7, y=3..4, z=4..5)
    for x in (5, 6, 7):
        for y in (3, 4):
            vol[4][y][x] = 5
            if x in (5, 6):
                vol[5][y][x] = 6

    # Nadadeiras peitorais laterais (x=7..8, z=1..2)
    for px in (7, 8):
        vol[1][1][px] = 3
        vol[2][1][px] = 5
        vol[1][6][px] = 3
        vol[2][6][px] = 5

    # Pedúnculo e nadadeira caudal bifurcada (x=0..2)
    # x=2 conecta ao corpo, x=0..1 abre em bifurcação superior (z=4..5) e inferior (z=0..1)
    for z in (1, 2, 3, 4):
        for y in (3, 4):
            vol[z][y][2] = 3 if z == 1 else 4
    # x=1: abre em leque
    for y in (2, 3, 4, 5):
        vol[1][y][1] = 3
        vol[4][y][1] = 5
    for y in (3, 4):
        vol[2][y][1] = 4
        vol[3][y][1] = 4
    # x=0: pontas bifurcadas superior (z=4..5) e inferior (z=0..1) com vão central em z=2..3
    for y in (2, 3, 4, 5):
        vol[0][y][0] = 2
        vol[1][y][0] = 3
        vol[4][y][0] = 5
        vol[5][y][0] = 6

    # Olhinho escuro com brilho branco na frente (x=9..10) em ambos os lados
    for ey in (1, 6):
        # Garante face lateral preenchida ao redor do olho
        vol[2][ey][9] = 4
        vol[2][ey][10] = 4
        vol[3][ey][9] = 1   # pupila escura
        vol[3][ey][10] = 7  # brilho branco na frente
    # Também reforça camada y=2 e y=5 caso o corpo arredonde
    for ey in (2, 5):
        vol[3][ey][9] = 1
        vol[3][ey][10] = 7

    return {'palette': palette, 'slices': to_strings(vol)}


def build_ruin_pillar():
    """9. ruin_pillar (12 x 12 x 18)"""
    w, h, z_count = 12, 12, 18
    palette = [
        'rgba(0,0,0,0)',
        '#2B2623',  # 1: rachadura / sombra profunda
        '#5C5852',  # 2: pedra antiga escura
        '#847F77',  # 3: pedra média
        '#ADA79E',  # 4: pedra clara
        '#CFC9BE',  # 5: quina iluminada
        '#3B6E38',  # 6: musgo escuro
        '#68A352',  # 7: musgo claro
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 5.5, 5.5

    # Base quadrada larga (z=0..3)
    for z in range(4):
        pad = 1 if z <= 1 else 2
        for y in range(pad, h - pad):
            for x in range(pad, w - pad):
                is_edge = (x in (pad, w - pad - 1) or y in (pad, h - pad - 1))
                if z == 0 or y < 3 or x < 3:
                    vol[z][y][x] = 2 if is_edge else 3
                elif z in (1, 3) and is_edge and (x + y >= 10):
                    vol[z][y][x] = 5
                else:
                    vol[z][y][x] = 4 if (z == 3 and is_edge) else 3

    # Fuste cilíndrico/octogonal (z=4..13) com estrias e rachaduras
    for z in range(4, 14):
        for y in range(h):
            for x in range(w):
                dx = abs(x - cx)
                dy = abs(y - cy)
                # Octógono: corta apenas os 4 cantos extremos
                if dx <= 3.6 and dy <= 3.6 and (dx + dy) <= 5.4:
                    # Estria/rachadura diagonal
                    is_crack = (
                        (z in (6, 7) and x == 6 and y == 9) or
                        (z in (8, 9) and x == 7 and y == 8) or
                        (z in (10, 11) and x == 8 and y == 7) or
                        (z in (5, 6) and x == 3 and y == 8)
                    )
                    if is_crack:
                        vol[z][y][x] = 1
                    elif x + y >= 12:
                        vol[z][y][x] = 4 if (x == 9 or y == 9) else 3
                    elif x + y <= 8:
                        vol[z][y][x] = 2
                    else:
                        vol[z][y][x] = 3

    # Topo quebrado assimétrico (z=14..17)
    for z in range(14, z_count):
        for y in range(h):
            for x in range(w):
                dx = abs(x - cx)
                dy = abs(y - cy)
                if dx <= 3.6 and dy <= 3.6 and (dx + dy) <= 5.4:
                    # Plano inclinado irregular de quebra: mais alto no canto NW (x<=5, y<=6)
                    break_h = 17.4 - (x * 0.35 + y * 0.25)
                    if (x == 4 and y == 4):
                        break_h = 17.5
                    if z <= break_h:
                        is_top_break = (z + 1 > break_h)
                        vol[z][y][x] = 5 if (is_top_break and x + y >= 8) else (4 if is_top_break else 3)

    # Musgo verde subindo na base (z=0..6)
    moss_spots = [
        (1, 8, 0), (1, 9, 0), (2, 9, 0), (2, 10, 0),
        (1, 9, 1), (2, 9, 1), (2, 10, 1),
        (2, 8, 2), (2, 9, 2), (3, 9, 2),
        (2, 7, 3), (3, 8, 3), (3, 9, 3),
        (3, 7, 4), (3, 8, 4), (4, 8, 4),
        (3, 7, 5), (4, 8, 5),
        (8, 2, 0), (9, 2, 0), (9, 3, 0),
        (8, 2, 1), (9, 3, 1), (8, 3, 2),
    ]
    for mx, my, mz in moss_spots:
        if vol[mz][my][mx] != 0:
            vol[mz][my][mx] = 7 if (mz >= 2 or mx <= 3) else 6

    return {'palette': palette, 'slices': to_strings(vol)}


def build_flower_tuft():
    """10. flower_tuft (10 x 10 x 5)"""
    w, h, z_count = 10, 10, 5
    palette = [
        'rgba(0,0,0,0)',
        '#214E28',  # 1: folha sombra
        '#3A7D44',  # 2: folha verde média
        '#65B85B',  # 3: folha verde clara
        '#FACC15',  # 4: flor amarela
        '#F472B6',  # 5: flor rosa
        '#FFFDF7',  # 6: flor branca
        '#D97706',  # 7: miolo dourado/âmbar
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 4.5, 4.5

    # Moita rasteira de folhas verdes na base (z=0..2), formato orgânico estrelado
    for z in range(3):
        base_r = 4.3 if z == 0 else (3.9 if z == 1 else 2.8)
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                # Pontinhas de folhas irradiando
                leaf_flare = 0.6 if ((x + y) % 2 == 0 and dist > 2.0) else 0.0
                if dist <= base_r - leaf_flare:
                    if z == 0:
                        vol[z][y][x] = 1 if dist > 2.8 else 2
                    elif z == 1:
                        vol[z][y][x] = 3 if (dx + dy > 1.0 and dist > 2.0) else 2
                    else:
                        vol[z][y][x] = 3 if (x + y >= 9) else 2

    # Florzinhas amarelas, rosas e brancas desabrochando (z=2..4) com hastes conectadas
    flowers = [
        (3, 3, 4, 4),  # amarela em z=4
        (7, 3, 3, 5),  # rosa em z=3
        (3, 7, 3, 6),  # branca em z=3
        (6, 7, 4, 5),  # rosa em z=4
        (5, 5, 4, 6),  # branca central em z=4
        (8, 6, 3, 4),  # amarela lateral em z=3
    ]
    for fx, fy, fz, pcol in flowers:
        # Garante haste verde conectada de z=0 até fz-1
        for hz in range(fz):
            if vol[hz][fy][fx] == 0:
                vol[hz][fy][fx] = 2 if hz == 0 else 3
        # Pétalas em cruz ao redor do miolo no nível fz
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            px, py = fx + dx, fy + dy
            if 0 <= px < w and 0 <= py < h:
                vol[fz][py][px] = pcol
                # Garante apoio em fz-1 se necessário para zero partes flutuantes
                if vol[fz - 1][py][px] == 0:
                    vol[fz - 1][py][px] = 2
        vol[fz][fy][fx] = 7  # miolo da flor

    return {'palette': palette, 'slices': to_strings(vol)}


def build_cozy_cabin():
    """11. cozy_cabin (26 x 24 x 28)"""
    w, h, z_count = 26, 24, 28
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: porta marrom escura / sombra vigas
        '#6B4226',  # 2: vigas marrom / molduras
        '#D99B4E',  # 3: macaneta dourada / madeira clara
        '#E6D5BE',  # 4: parede creme sombra
        '#FAF3E8',  # 5: parede creme clara
        '#FDE68A',  # 6: janelinha amarela quente acesa
        '#9E4429',  # 7: telhado terracota sombra
        '#C25E3E',  # 8: telhado terracota principal
        '#7A3222',  # 9: tijolinho chamine escuro
    ]
    vol = make_volume(w, h, z_count, 0)

    # Corpo principal da cabana: x=2..23, y=2..23, z=0..14 (y=23 = H-1 e a fachada frontal)
    for z in range(15):
        for y in range(2, h):
            for x in range(2, w - 2):
                is_wall = (x in (2, w - 3) or y in (2, h - 1))
                is_corner = (x in (2, 3, w - 4, w - 3)) and (y in (2, 3, h - 2, h - 1))
                is_beam = (
                    is_corner
                    or (is_wall and z in (0, 7, 14))
                    or (y in (2, h - 1) and x in (9, 16) and z <= 14)
                    or (x in (2, w - 3) and y in (12, 13))
                )
                if not is_wall and z > 0:
                    # Interior preenchido nas camadas visiveis ou estruturais (economiza mas mantem solido)
                    if z == 14:
                        vol[z][y][x] = 4
                    continue
                if z == 0 and not is_wall:
                    vol[z][y][x] = 2  # piso conectado em z=0
                elif is_beam:
                    vol[z][y][x] = 1 if z == 0 else 2
                else:
                    vol[z][y][x] = 5 if (y >= 12 or x >= 13) else 4

    # Porta marrom escura na frente (y = H - 1 = 23, x=10..15, z=0..10) com macaneta
    for z in range(11):
        for x in range(10, 16):
            if x in (10, 15) or z == 10:
                vol[z][h - 1][x] = 2  # batente marrom
            else:
                vol[z][h - 1][x] = 1  # folha da porta marrom escura
            # Reforca batente interno em y=22 para solidez
            vol[z][h - 2][x] = 1
    vol[4][h - 1][14] = 3
    vol[5][h - 1][14] = 3  # macaneta

    # Janelinhas amarelas quentes acesas (#FDE68A) na frente e laterais
    def carve_window_y(y_pos, x0, x1, z0, z1):
        for z in range(z0 - 1, z1 + 2):
            for x in range(x0 - 1, x1 + 2):
                if x0 <= x <= x1 and z0 <= z <= z1:
                    # Caixilho fino cruzado opcional ou vidro aceso
                    vol[z][y_pos][x] = 6
                else:
                    vol[z][y_pos][x] = 2

    def carve_window_x(x_pos, y0, y1, z0, z1):
        for z in range(z0 - 1, z1 + 2):
            for y in range(y0 - 1, y1 + 2):
                if y0 <= y <= y1 and z0 <= z <= z1:
                    vol[z][y][x_pos] = 6
                else:
                    vol[z][y][x_pos] = 2

    # Frente (y = H - 1 = 23)
    carve_window_y(h - 1, 5, 7, 5, 8)
    carve_window_y(h - 1, 18, 20, 5, 8)
    # Costas (y = 2)
    carve_window_y(2, 6, 8, 5, 8)
    carve_window_y(2, 17, 19, 5, 8)
    # Laterais (x = 2 e x = 23)
    carve_window_x(2, 6, 9, 5, 8)
    carve_window_x(2, 16, 19, 5, 8)
    carve_window_x(w - 3, 6, 9, 5, 8)
    carve_window_x(w - 3, 16, 19, 5, 8)

    # Telhado inclinado dois-aguas terracota (z=15..25), cumeeira ao longo de Y (x=12..13)
    for z in range(15, 26):
        dz = z - 15  # 0..10
        half_span = 12.5 - dz * 1.2  # 12.5 em z=15 (x=0..25), 0.5 em z=25 (x=12..13)
        x_min = max(0, int(round(12.5 - half_span)))
        x_max = min(w - 1, int(round(12.5 + half_span)))
        inner_min = max(2, x_min + 2)
        inner_max = min(w - 3, x_max - 2)

        for y in range(1, h):
            for x in range(x_min, x_max + 1):
                is_roof_shell = (
                    x <= x_min + 1
                    or x >= x_max - 1
                    or z == 25
                    or y in (1, h - 1)
                )
                # Paredes triangulares do oitao na frente (y=23) e atras (y=2)
                if y in (2, h - 1) and inner_min <= x <= inner_max and z < 24:
                    vol[z][y][x] = 2 if x in (inner_min, inner_max) else (5 if y == h - 1 else 4)
                elif is_roof_shell:
                    # Padrao de telhas terracota
                    tile = ((x + y + z) % 3 == 0) or (z == 15) or (z == 25)
                    vol[z][y][x] = 7 if (tile or x < 12) else 8
                elif 2 <= y <= h - 2 and inner_min <= x <= inner_max:
                    # Preenchimento solido abaixo da cumeeira nas bordas do oitao
                    if y in (3, h - 2):
                        vol[z][y][x] = 4

    # Janelinha iluminada no oitao frontal (y=23, x=12..13, z=17..18)
    for z in (17, 18):
        for x in (12, 13):
            vol[z][h - 1][x] = 6
    vol[16][h - 1][12] = 2
    vol[16][h - 1][13] = 2

    # Chamine de tijolinho (x=17..20, y=6..9, z=16..27) conectada firmemente ao telhado
    for z in range(16, 28):
        is_rim = (z == 26)
        x0, x1 = (17, 20) if not is_rim else (16, 21)
        y0, y1 = (6, 9) if not is_rim else (5, 10)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if z == 27 and 18 <= x <= 19 and 7 <= y <= 8:
                    vol[z][y][x] = 1  # boca da chamine escura
                else:
                    brick_alt = (x + y + z * 2) % 3
                    vol[z][y][x] = 9 if brick_alt == 0 else (7 if brick_alt == 1 else 8)

    return {'palette': palette, 'slices': to_strings(vol)}


def build_torii_gate():
    """12. torii_gate (22 x 10 x 26)"""
    w, h, z_count = 22, 10, 26
    palette = [
        'rgba(0,0,0,0)',
        '#24140F',  # 1: sombra base escura
        '#3B2219',  # 2: base escura / detalhe escuro topo kasagi
        '#7F1D1D',  # 3: vermelho sombra profunda
        '#991B1B',  # 4: vermelho escuro
        '#DC2626',  # 5: vermelho vivo principal
        '#EF4444',  # 6: vermelho iluminado
        '#F59E0B',  # 7: detalhe dourado placa central
    ]
    vol = make_volume(w, h, z_count, 0)

    # APENAS 2 pilares laterais nas pontas (x=3..5 e x=16..18 em y=3..6)
    # Vao central x=6..15 fica 100% VAZIO e ABERTO de z=0 ate z=17!
    for z in range(23):
        for x0, x1 in ((3, 5), (16, 18)):
            if z <= 1:
                # Sapata escura mantendo x=6..15 completamente livre
                bx0 = x0 - 1 if x0 == 3 else x0
                bx1 = x1 if x0 == 3 else x1 + 1
                for y in range(2, 8):
                    for x in range(bx0, bx1 + 1):
                        vol[z][y][x] = 1 if (z == 0 or y in (2, 7)) else 2
            elif z <= 3:
                for y in range(3, 7):
                    for x in range(x0, x1 + 1):
                        vol[z][y][x] = 2
            else:
                for y in range(3, 7):
                    for x in range(x0, x1 + 1):
                        if y == 6:
                            vol[z][y][x] = 6 if x in (x0 + 1, x1) else 5
                        elif y == 3:
                            vol[z][y][x] = 4
                        else:
                            vol[z][y][x] = 5

    # Viga horizontal inferior (nuki) em z=18..20
    for z in range(18, 21):
        for y in range(4, 6):
            for x in range(1, w - 1):
                if x in (1, w - 2):
                    vol[z][y][x] = 3 if z == 18 else 4
                elif z == 20:
                    vol[z][y][x] = 6 if y == 5 else 5
                elif z == 18:
                    vol[z][y][x] = 4
                else:
                    vol[z][y][x] = 5

    # Suporte central (gakuzuka) entre nuki (z=20) e kasagi (z=22)
    for z in range(20, 23):
        for y in range(3, 7):
            for x in (10, 11):
                if y in (3, 6) and z == 21:
                    vol[z][y][x] = 7 if y == 6 else 2
                else:
                    vol[z][y][x] = 2 if (y in (3, 6)) else 4

    # Viga superior curva (kasagi) em z=22..25 com pontas arrebitadas e detalhe escuro no topo
    for x in range(w):
        dist_c = abs(x - 10.5)
        if dist_c <= 7.5:
            z_bot, z_top_red, z_cap = 22, 23, 24
        elif dist_c <= 9.5:
            z_bot, z_top_red, z_cap = 23, 24, 25
        else:
            z_bot, z_top_red, z_cap = 24, 24, 25  # pontas extremas x=0 e x=21 arrebitadas

        for y in range(2, 8):
            # Chanfro sutil nas pontas
            if dist_c > 9.5 and y in (2, 7):
                continue
            for z in range(z_bot, z_top_red + 1):
                if z == z_bot:
                    vol[z][y][x] = 4
                elif y >= 6:
                    vol[z][y][x] = 6
                elif y <= 3:
                    vol[z][y][x] = 4
                else:
                    vol[z][y][x] = 5
            # Detalhe escuro no topo do kasagi
            vol[z_cap][y][x] = 1 if y in (2, 7) else 2

    return {'palette': palette, 'slices': to_strings(vol)}


def build_stone_lantern():
    """13. stone_lantern (10 x 10 x 18)"""
    w, h, z_count = 10, 10, 18
    palette = [
        'rgba(0,0,0,0)',
        '#374151',  # 1: pedra sombra profunda
        '#4B5563',  # 2: pedra cinza escura
        '#6B7280',  # 3: pedra cinza media
        '#9CA3AF',  # 4: pedra cinza clara
        '#D1D5DB',  # 5: quina iluminada
        '#FDE68A',  # 6: luz amarela da janela
        '#FEF9C3',  # 7: miolo luminoso
    ]
    vol = make_volume(w, h, z_count, 0)

    def fill_chamfer_square(z, pad, col_edge, col_fill, col_hi=None):
        lo, hi = pad, w - 1 - pad
        for y in range(lo, hi + 1):
            for x in range(lo, hi + 1):
                if pad <= 2 and (x in (lo, hi) and y in (lo, hi)):
                    continue
                is_edge = (x in (lo, hi) or y in (lo, hi))
                if col_hi and is_edge and (x + y >= w - 1):
                    vol[z][y][x] = col_hi
                elif is_edge:
                    vol[z][y][x] = col_edge
                else:
                    vol[z][y][x] = col_fill

    # z=0..3: base larga de pedra
    fill_chamfer_square(0, 1, 1, 2)
    fill_chamfer_square(1, 1, 2, 3, 4)
    fill_chamfer_square(2, 2, 2, 3, 4)
    fill_chamfer_square(3, 3, 3, 4, 5)

    # z=4..8: haste fina
    for z in range(4, 9):
        for y in (4, 5):
            for x in (4, 5):
                vol[z][y][x] = 4 if (x == 5 and y == 5) else (2 if (x == 4 and y == 4) else 3)

    # z=9..12: camara com janela luminosa amarela (#FDE68A)
    fill_chamfer_square(9, 2, 3, 4, 5)  # plataforma inferior da camara
    for z in (10, 11):
        for y in range(3, 7):
            for x in range(3, 7):
                is_corner = (x in (3, 6) and y in (3, 6))
                if is_corner:
                    vol[z][y][x] = 4 if (x == 6 or y == 6) else 2
                elif x in (4, 5) and y in (4, 5):
                    vol[z][y][x] = 7
                else:
                    vol[z][y][x] = 6  # janela luminosa nas 4 faces
    fill_chamfer_square(12, 2, 2, 3, 4)

    # z=13..17: telhadinho piramidal de pedra com pinaculo
    fill_chamfer_square(13, 1, 3, 4, 5)
    # Pontas levemente arrebitadas nos 4 cantos em z=13
    for cx, cy in ((1, 1), (8, 1), (1, 8), (8, 8)):
        vol[13][cy][cx] = 4
    fill_chamfer_square(14, 2, 3, 4, 5)
    fill_chamfer_square(15, 3, 4, 4, 5)
    for y in (4, 5):
        for x in (4, 5):
            vol[16][y][x] = 5 if (x + y >= 9) else 4
    vol[17][4][4] = 5
    vol[17][5][4] = 5
    vol[17][4][5] = 5
    vol[17][5][5] = 5

    return {'palette': palette, 'slices': to_strings(vol)}


def build_lighthouse():
    """14. lighthouse (18 x 18 x 42)"""
    w, h, z_count = 18, 18, 42
    palette = [
        'rgba(0,0,0,0)',
        '#231F28',  # 1: porta escura / varanda escura
        '#4B5563',  # 2: base octogonal cinza escura
        '#8491A3',  # 3: base octogonal cinza clara
        '#CBD5E1',  # 4: branco sombra da torre
        '#F8FAFC',  # 5: branco vivo da torre
        '#991B1B',  # 6: vermelho sombra
        '#DC2626',  # 7: vermelho vivo
        '#F59E0B',  # 8: vidro dourado medio / macaneta
        '#FEF08A',  # 9: vidro dourado brilhante
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 8.5, 8.5

    # Base octogonal cinza (z=0..3)
    for z in range(4):
        lim = 6.6 if z <= 1 else 6.1
        oct_lim = 10.0 if z <= 1 else 9.2
        for y in range(h):
            for x in range(w):
                dx = abs(x - cx)
                dy = abs(y - cy)
                if dx <= lim and dy <= lim and (dx + dy) <= oct_lim:
                    vol[z][y][x] = 3 if (x + y >= 17 and z >= 1) else 2

    # Torre cilindrica listrada branco (#F8FAFC) e vermelho (#DC2626) a cada 6 fatias (z=4..29)
    for z in range(4, 30):
        rad = 5.3 - 1.5 * ((z - 4) / 25.0)
        stripe = ((z - 4) // 6) % 2  # 0: branco, 1: vermelho
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= rad * rad:
                    lit = (dx + dy) > -0.5
                    if stripe == 0:
                        vol[z][y][x] = 5 if lit else 4
                    else:
                        vol[z][y][x] = 7 if lit else 6

    # Portinha escura na frente (y = H - 1 = 17, z=1..7) com moldura conectada a base/torre
    for z in range(9):
        for y in range(13, h):
            for x in range(6, 12):
                if z == 0:
                    vol[z][y][x] = 2
                elif z <= 7 and y == h - 1 and 7 <= x <= 10:
                    if x in (7, 10) or z == 7:
                        vol[z][y][x] = 3
                    else:
                        vol[z][y][x] = 1  # folha da porta escura
                elif z <= 7 and 7 <= x <= 10 and y == h - 2:
                    vol[z][y][x] = 1
                elif z <= 8:
                    vol[z][y][x] = 3 if (y >= 16 or x >= 9) else 2
    vol[4][h - 1][9] = 8  # macaneta dourada

    # Pequenas janelinhas na frente da torre
    for jz in (13, 23):
        for z in (jz, jz + 1):
            for x in (8, 9):
                for y in range(12, h):
                    if vol[z][y][x] != 0 and (y == h - 1 or vol[z][y + 1][x] == 0):
                        vol[z][y][x] = 9 if z == jz + 1 else 8
                        break

    # Varanda circular escura (z=30..32)
    for z in range(30, 33):
        for y in range(h):
            for x in range(w):
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if z == 30:
                    if dist <= 5.5:
                        vol[z][y][x] = 1
                elif z == 31:
                    if 4.5 <= dist <= 5.5 or dist <= 3.3:
                        vol[z][y][x] = 1
                else:  # z == 32: postes da grade + piso da lanterna
                    if dist <= 3.3 or (4.5 <= dist <= 5.5 and (abs(x - cx) < 1.2 or abs(y - cy) < 1.2)):
                        vol[z][y][x] = 1

    # Lanterna de vidro dourado brilhante (z=33..37)
    for z in range(33, 38):
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist <= 3.3:
                    is_mullion = (dist >= 2.2) and (abs(abs(dx) - abs(dy)) <= 0.6)
                    if is_mullion or z == 37 and dist >= 2.5:
                        vol[z][y][x] = 1
                    elif dist <= 1.8:
                        vol[z][y][x] = 9
                    else:
                        vol[z][y][x] = 9 if (z in (34, 35) and dx + dy > 0) else 8

    # Cupula vermelha com ponta (z=38..41)
    dome_radii = {38: 4.1, 39: 3.0, 40: 1.8}
    for z, drad in dome_radii.items():
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= drad * drad:
                    vol[z][y][x] = 7 if (dx + dy >= 0 or z >= 39) else 6
    # Ponta da cupula em z=41
    for y in (8, 9):
        for x in (8, 9):
            vol[41][y][x] = 8 if (x == 9 and y == 9) else 7

    return {'palette': palette, 'slices': to_strings(vol)}


def build_beach_umbrella():
    """15. beach_umbrella (18 x 18 x 18)"""
    w, h, z_count = 18, 18, 18
    palette = [
        'rgba(0,0,0,0)',
        '#5C3A21',  # 1: mastro madeira sombra
        '#8C5835',  # 2: mastro madeira media
        '#B87B4B',  # 3: mastro madeira clara / pinaculo
        '#B91C1C',  # 4: vermelho sombra
        '#EF4444',  # 5: vermelho vivo
        '#CBD5E1',  # 6: branco sombra
        '#FFFDF7',  # 7: branco vivo
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 8.5, 8.5

    # Mastro fino de madeira no centro (x=8..9, y=8..9, z=0..14)
    for z in range(15):
        for y in (8, 9):
            for x in (8, 9):
                vol[z][y][x] = 3 if (x == 9 and y == 9) else (1 if (x == 8 and y == 8) else 2)

    # Cupula octogonal listrada radialmente de vermelho (#EF4444) e branco (#FFFDF7) de z=12..17
    shells = {
        17: (0.0, 1.5),
        16: (0.0, 3.3),
        15: (0.0, 5.2),
        14: (4.0, 6.9),
        13: (5.8, 8.2),
        12: (7.0, 8.5),
    }
    for z, (r_min, r_max) in shells.items():
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                oct_d = max(abs(dx), abs(dy), (abs(dx) + abs(dy)) * 0.72)
                if r_min <= oct_d <= r_max:
                    if z == 17 and oct_d <= 0.8:
                        vol[z][y][x] = 3
                        continue
                    ang = math.atan2(dy, dx)
                    sector = int(((ang + math.pi) / (2.0 * math.pi)) * 8.0) % 8
                    is_red = (sector % 2 == 0)
                    is_shaded = (z == 12) or (dx + dy < -2.0)
                    if is_red:
                        vol[z][y][x] = 4 if is_shaded else 5
                    else:
                        vol[z][y][x] = 6 if is_shaded else 7

    return {'palette': palette, 'slices': to_strings(vol)}


def build_wood_boat():
    """16. wood_boat (20 x 12 x 8)"""
    w, h, z_count = 20, 12, 8
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: borda marrom escura / sombra quilha
        '#5C3A21',  # 2: madeira escura casco externo
        '#7C4D2B',  # 3: madeira media casco / interior
        '#A66E4E',  # 4: madeira clara / bancos
        '#C88E65',  # 5: realce bancos / borda interna
    ]
    vol = make_volume(w, h, z_count, 0)
    cy = 5.5

    # Perfil de largura por X (popa x=0..2, meio x=3..15, proa x=16..19)
    half_widths = {
        0: 0.9, 1: 1.9, 2: 3.1,
        3: 4.1, 4: 4.6, 5: 4.8, 6: 4.9, 7: 4.9, 8: 4.9, 9: 4.9,
        10: 4.9, 11: 4.9, 12: 4.9, 13: 4.8, 14: 4.6, 15: 4.1,
        16: 3.4, 17: 2.6, 18: 1.7, 19: 0.8,
    }
    z_scales = {
        0: 0.48, 1: 0.68, 2: 0.84,
        3: 0.92, 4: 0.96, 5: 0.99, 6: 1.00, 7: 1.02,
    }

    for z in range(z_count):
        zs = z_scales[z]
        for x in range(w):
            hw = half_widths[x] * zs
            # Fundo solido em z=0..2; oco em z=3..7 mantendo espessura da parede
            inner_hw = -1.0 if z <= 2 else max(0.0, hw - 1.35)
            # Proa (x>=18) e popa (x<=1) fechadas com bico
            if x <= 1 or x >= 18:
                inner_hw = -1.0
            for y in range(h):
                dy = abs(y - cy)
                if dy <= hw and dy >= inner_hw:
                    if z == 7:
                        vol[z][y][x] = 1  # borda marrom escura em cima
                    elif z == 0:
                        vol[z][y][x] = 1
                    elif z <= 2:
                        vol[z][y][x] = 3 if (dy < hw - 1.0) else 2
                    elif dy >= hw - 0.8:
                        vol[z][y][x] = 3 if y >= cy else 2
                    else:
                        vol[z][y][x] = 4 if z >= 5 else 3

    # Dois bancos transversais (x=6 e x=12 em z=4)
    for bx in (6, 12):
        hw_seat = half_widths[bx] * z_scales[4]
        for y in range(h):
            if abs(y - cy) <= hw_seat - 0.5:
                vol[4][y][bx] = 5 if y >= cy else 4

    return {'palette': palette, 'slices': to_strings(vol)}


def build_sunflower():
    """17. sunflower (10 x 10 x 16)"""
    w, h, z_count = 10, 10, 16
    palette = [
        'rgba(0,0,0,0)',
        '#1E4D2B',  # 1: caule/folha verde escuro
        '#2E7D32',  # 2: caule/folha verde medio
        '#4CAF50',  # 3: folha verde clara
        '#4A2C1D',  # 4: disco central marrom escuro
        '#784421',  # 5: textura disco marrom
        '#F59E0B',  # 6: petala laranja-ouro
        '#FACC15',  # 7: petala amarelo-ouro
    ]
    vol = make_volume(w, h, z_count, 0)

    # Caule verde fino (z=0..12) com leve inclinacao (com sobreposicao para 6-conectividade)
    prev_sy = 4
    for z in range(13):
        sy = 4 if z < 4 else (5 if z < 8 else (6 if z < 11 else 7))
        for x in (4, 5):
            vol[z][sy][x] = 2 if x == 5 else 1
            if sy != prev_sy:
                vol[z][prev_sy][x] = 1
            if z <= 2:
                vol[z][sy + 1][x] = 2
        prev_sy = sy

    # Duas folhinhas horizontais (z=4..5)
    for z in (4, 5):
        # Folha esquerda
        for x, y in ((3, 5), (2, 5), (2, 6), (1, 6)):
            vol[z][y][x] = 3 if z == 5 else 2
        # Folha direita
        for x, y in ((6, 5), (7, 5), (7, 6), (8, 6)):
            vol[z][y][x] = 3 if z == 5 else 2

    # Calice verde atras da cabeca da flor (y=7..8, z=11..14)
    for z in range(11, 15):
        for x in range(3, 7):
            if (x in (3, 6)) and (z in (11, 14)):
                continue
            vol[z][8][x] = 2 if z <= 12 else 3
            if z in (12, 13) and x in (4, 5):
                vol[z][7][x] = 1

    # Flor voltada para a frente (y = H - 1 = 9, z=10..15)
    fcx, fcz = 4.5, 12.5
    for z in range(10, 16):
        for x in range(1, 9):
            dx = x - fcx
            dz = z - fcz
            dist = (dx * dx + dz * dz) ** 0.5
            ang = math.atan2(dz, dx)
            petal_flare = 0.45 * abs(math.cos(ang * 4.0))
            if dist <= 1.9:
                # Disco central marrom escuro (#4A2C1D)
                vol[z][h - 1][x] = 5 if ((x + z) % 2 == 0 and dist < 1.3) else 4
            elif dist <= 3.7 + petal_flare:
                # Anel de petalas amarelo-ouro (#FACC15 / #F59E0B) em y=8..9
                col = 7 if (z >= 13 or (x + z) % 2 == 0) else 6
                vol[z][h - 1][x] = col
                if dist <= 3.1:
                    vol[z][h - 2][x] = 6

    return {'palette': palette, 'slices': to_strings(vol)}


def build_hay_bale():
    """18. hay_bale (14 x 14 x 10)"""
    w, h, z_count = 14, 14, 10
    palette = [
        'rgba(0,0,0,0)',
        '#4A2C1D',  # 1: corda sombra escura
        '#6B4226',  # 2: corda marrom amarrada
        '#92610A',  # 3: feno sombra escura
        '#CA8A04',  # 4: feno dourado medio
        '#EAB308',  # 5: feno dourado claro
        '#FACC15',  # 6: palha iluminada
    ]
    vol = make_volume(w, h, z_count, 0)

    # Fardo principal x=1..12, y=1..12, z=0..9 com bordas levemente arredondadas e topo plano (z=9)
    for z in range(z_count):
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                # Cantos verticais suavizados (1px)
                if x in (1, w - 2) and y in (1, h - 2):
                    continue
                is_rope = x in (4, 9) and (
                    z in (0, z_count - 1) or y in (1, h - 2) or
                    (x in (4, 9) and (x in (1, w - 2) or y in (2, h - 3) and (x in (1, w - 2))))
                )
                if is_rope:
                    vol[z][y][x] = 1 if z == 0 or y == 1 else 2
                else:
                    straw = hash3(x, y, z) % 5
                    if z == z_count - 1:
                        vol[z][y][x] = 6 if straw == 0 else (5 if straw <= 3 else 4)
                    elif z == 0 or y <= 2:
                        vol[z][y][x] = 3 if straw == 0 else 4
                    else:
                        vol[z][y][x] = 6 if (z >= 7 and straw == 0) else (5 if straw <= 2 else 4)

    # Fiapinhos sutis de feno nas laterais (z=2..7) conectados ao fardo
    tufts = [
        (0, 3, 3), (0, 7, 5), (0, 10, 4),
        (13, 4, 6), (13, 8, 3), (13, 10, 5),
    ]
    for tx, ty, tz in tufts:
        vol[tz][ty][tx] = 5 if tz >= 5 else 4

    return {'palette': palette, 'slices': to_strings(vol)}


def build_tree_stump():
    """19. tree_stump (14 x 14 x 10)"""
    w, h, z_count = 14, 14, 10
    palette = [
        'rgba(0,0,0,0)',
        '#2E1A12',  # 1: casca sombra profunda
        '#4B2E1E',  # 2: casca marrom escura
        '#6D442B',  # 3: casca marrom media
        '#8C5A38',  # 4: casca iluminada
        '#C49A6C',  # 5: anel madeira escura no topo
        '#E7C697',  # 6: madeira clara no topo
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 6.5, 6.5

    root_dirs = [(-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0)]

    for z in range(z_count):
        base_r = 5.1 if z == 0 else (4.8 if z == 1 else (4.4 if z <= 8 else 4.5))
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5

                # Raizes nas 4 quinas (z=0..2)
                in_root = False
                if z <= 2:
                    reach = 1.0 - z * 0.3
                    for rdx, rdy in root_dirs:
                        rx = cx + rdx * (3.6 + 1.6 * reach)
                        ry = cy + rdy * (3.6 + 1.6 * reach)
                        for step in range(4):
                            s = step / 3.0
                            px = cx + (rx - cx) * s
                            py = cy + (ry - cy) * s
                            rr = 1.55 - 0.45 * s
                            if (x - px) ** 2 + (y - py) ** 2 <= rr * rr:
                                in_root = True
                                break

                if dist <= base_r or in_root:
                    if z == z_count - 1:
                        # Topo plano (z=9) com aneis concentricos de madeira clara (#E7C697 / #C49A6C)
                        if dist >= base_r - 1.05:
                            vol[z][y][x] = 3 if (dx + dy >= 0) else 2
                        else:
                            ring = int(round(dist)) % 2
                            vol[z][y][x] = 6 if ring == 0 else 5
                    else:
                        groove = ((int(round(math.atan2(dy, dx) * 4.5)) + x + y) % 4 == 0)
                        if z == 0 or (dx + dy < -2.5) or (groove and dist >= base_r - 1.2):
                            vol[z][y][x] = 1 if (z == 0 and dx + dy < 0) else 2
                        elif dx + dy > 1.8 and not groove:
                            vol[z][y][x] = 4
                        else:
                            vol[z][y][x] = 3

    return {'palette': palette, 'slices': to_strings(vol)}


def build_pumpkin_patch():
    """20. pumpkin_patch (14 x 14 x 8)"""
    w, h, z_count = 14, 14, 8
    palette = [
        'rgba(0,0,0,0)',
        '#1E4D2B',  # 1: folha/cabo verde escuro
        '#2E7D32',  # 2: folha/cabo verde medio
        '#4DB848',  # 3: folha iluminada / vinha
        '#9A3412',  # 4: sombra gomos abobora
        '#EA580C',  # 5: abobora laranja media
        '#F97316',  # 6: abobora laranja viva
        '#FDBA74',  # 7: realce laranja claro
    ]
    vol = make_volume(w, h, z_count, 0)

    # Folhagem verde na base (z=0..1) conectando todo o canteiro
    foliage_blobs = [
        (5.0, 5.0, 4.4),
        (9.5, 8.5, 3.8),
        (3.8, 10.0, 3.3),
        (7.2, 6.8, 3.4),
    ]
    for z in (0, 1):
        scale = 1.0 if z == 0 else 0.78
        for y in range(h):
            for x in range(w):
                for fx, fy, fr in foliage_blobs:
                    dist = ((x - fx) ** 2 + (y - fy) ** 2) ** 0.5
                    flare = 0.45 if ((x + y) % 2 == 0) else 0.0
                    if dist <= fr * scale - flare:
                        if z == 0:
                            vol[z][y][x] = 1 if dist > fr * 0.7 else 2
                        else:
                            vol[z][y][x] = 3 if (x + y) % 3 == 0 else 2
                        break

    # Trio de aboboras laranjas (#F97316 / #EA580C) gordinhas com gomos
    pumpkins = [
        # (px, py, pz_center, rx, ry, rz, stem_top_z, stem_dx)
        (5.0, 5.0, 3.1, 3.3, 3.3, 2.7, 7, 1),   # abobora grande
        (9.5, 8.5, 2.7, 2.8, 2.8, 2.3, 6, -1),  # abobora media
        (3.8, 10.0, 2.4, 2.4, 2.4, 2.0, 6, 1),  # abobora pequena
    ]
    for px, py, pz, rx, ry, rz, stem_z, sdx in pumpkins:
        for z in range(1, z_count):
            for y in range(h):
                for x in range(w):
                    dx = (x - px) / rx
                    dy = (y - py) / ry
                    dz = (z - pz) / rz
                    if dx * dx + dy * dy + dz * dz <= 1.0:
                        ang = math.atan2(dy, dx)
                        rib = abs(math.sin(ang * 4.0))
                        if rib < 0.28 or z == 1:
                            vol[z][y][x] = 4 if (dx + dy < 0 or z == 1) else 5
                        elif z >= pz + rz * 0.45 and (dx + dy > 0):
                            vol[z][y][x] = 7
                        elif dx + dy < -0.2:
                            vol[z][y][x] = 5
                        else:
                            vol[z][y][x] = 6
        # Garante apoio em z=0 sob o centro caso algum pixel lateral precise
        sx, sy = int(round(px)), int(round(py))
        vol[0][sy][sx] = 2
        # Cabinho verde curvo no topo
        top_body_z = int(round(pz + rz * 0.85))
        for cz in range(top_body_z, stem_z + 1):
            cur_x = sx + (sdx if cz == stem_z else 0)
            if 0 <= cur_x < w:
                vol[cz][sy][cur_x] = 3 if cz == stem_z else (2 if cz == stem_z - 1 else 1)
                if cz == stem_z and sx != cur_x:
                    # Garante 6-conectividade na curva do cabo
                    vol[cz - 1][sy][cur_x] = 2

    return {'palette': palette, 'slices': to_strings(vol)}


def build_grass_tuft_short():
    """21. grass_tuft_short (14 x 14 x 3)"""
    w, h, z_count = 14, 14, 3
    palette = [
        'rgba(0,0,0,0)',
        '#1E541B',  # 1: sombra raiz
        '#2F7A2B',  # 2: verde-escuro (z=0)
        '#4DB848',  # 3: verde medio (z=1)
        '#8BE064',  # 4: verde-limao (z=2)
        '#BEF264',  # 5: realce claro
    ]
    vol = make_volume(w, h, z_count, 0)

    # 7 tufinhos variados dentro de 1..12 (1px da borda), de 2 a 3px de altura
    tufts = [
        # (base_coords, mid_coords, tip_coords)
        ([(2, 3), (3, 3)], [(2, 3), (3, 3)], [(3, 3)]),
        ([(6, 2), (7, 2)], [(6, 2)], [(6, 2)]),
        ([(11, 3)], [(11, 3), (11, 4)], []),                 # 2px de altura
        ([(4, 7), (4, 8)], [(4, 7), (5, 7)], [(5, 7)]),
        ([(9, 6), (10, 6)], [(9, 6)], [(9, 6)]),
        ([(3, 11)], [(3, 11), (4, 11)], []),                 # 2px de altura
        ([(10, 11), (11, 11)], [(11, 11)], [(11, 11)]),
    ]
    for base_pts, mid_pts, tip_pts in tufts:
        for x, y in base_pts:
            vol[0][y][x] = 2
        for x, y in mid_pts:
            vol[1][y][x] = 3
        for x, y in tip_pts:
            vol[2][y][x] = 4

    return {'palette': palette, 'slices': to_strings(vol)}


def build_grass_tuft_tall():
    """22. grass_tuft_tall (14 x 14 x 4)"""
    w, h, z_count = 14, 14, 4
    palette = [
        'rgba(0,0,0,0)',
        '#2F7A2B',  # 1: verde-escuro (z=0)
        '#4DB848',  # 2: verde medio (z=1)
        '#8BE064',  # 3: verde-limao (z=2)
        '#A7F3D0',  # 4: ponta verde-menta (z=3)
        '#FDE047',  # 5: micro-flor amarela (z=3)
    ]
    vol = make_volume(w, h, z_count, 0)

    # 7 tufos de 3 a 4px de altura; 4 laminas chegam a z=3 com #A7F3D0 / #FDE047
    tufts = [
        # (z0_pts, z1_pts, z2_pts, z3_pts_with_col)
        ([(2, 2), (3, 2)], [(2, 2), (3, 2)], [(2, 2)], [(2, 2, 4)]),
        ([(7, 2), (7, 3)], [(7, 2), (8, 2)], [(8, 2)], [(8, 2, 5)]),
        ([(11, 4), (11, 5)], [(11, 4)], [(11, 4)], []),
        ([(4, 6), (5, 6)], [(4, 6)], [(4, 6)], [(4, 6, 4)]),
        ([(8, 8), (9, 8)], [(8, 8), (9, 8)], [(9, 8)], []),
        ([(2, 11), (3, 11)], [(2, 11)], [(2, 11)], []),
        ([(10, 11), (11, 11)], [(10, 11), (10, 10)], [(10, 10)], [(10, 10, 5)]),
    ]
    for z0_pts, z1_pts, z2_pts, z3_pts in tufts:
        for x, y in z0_pts:
            vol[0][y][x] = 1
        for x, y in z1_pts:
            vol[1][y][x] = 2
        for x, y in z2_pts:
            vol[2][y][x] = 3
        for x, y, col in z3_pts:
            vol[3][y][x] = col

    return {'palette': palette, 'slices': to_strings(vol)}


def build_baby_chick():
    """23. baby_chick (10 x 10 x 8)"""
    w, h, z_count = 10, 10, 8
    palette = [
        'rgba(0,0,0,0)',
        '#1E1B18',  # 1: olhinho preto suave
        '#FFFDF5',  # 2: brilho branco do olho
        '#EA580C',  # 3: laranja sombra
        '#F97316',  # 4: biquinho e patinhas laranja
        '#EAB308',  # 5: amarelo sombra ventre/asas
        '#FACC15',  # 6: amarelo medio fofo
        '#FDE047',  # 7: amarelo claro cabeca/topo
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy, cz = 4.5, 5.0, 3.8

    # 2 pontinhos de patinhas laranjas em z=0
    vol[0][5][3] = 4
    vol[0][5][6] = 4

    # Corpinho esferico/ovoide amarelo fofo (z=1..7) SEM crista
    for z in range(1, z_count):
        for y in range(h):
            for x in range(w):
                dx = (x - cx) / 3.2
                dy = (y - cy) / 3.4
                dz = (z - cz) / 3.5
                if dx * dx + dy * dy + dz * dz <= 1.0:
                    if z >= 6 or (z == 5 and y >= 5):
                        vol[z][y][x] = 7
                    elif z == 1 or (z == 2 and y <= 4):
                        vol[z][y][x] = 5
                    else:
                        vol[z][y][x] = 6

    # Rabinho sutil atras (y=1, z=3) conectado ao corpo
    vol[3][1][4] = 5
    vol[3][1][5] = 5

    # Asinhas sutis nas laterais (z=3..4)
    for z in (3, 4):
        for y in (4, 5):
            vol[z][y][1] = 5 if z == 3 else 6
            vol[z][y][8] = 5 if z == 3 else 6

    # Rosto voltado para frente (y = H - 1 = 9) em z=4..5:
    # Biquinho laranja (#F97316) em y=9 (z=4..5) conectado a y=8
    for x in (4, 5):
        vol[4][h - 1][x] = 3
        vol[5][h - 1][x] = 4
        vol[4][h - 2][x] = 6
        vol[5][h - 2][x] = 7

    # Olhinhos pretos com brilho branco na face frontal (y=8 conectado ao corpo e visivel na frente)
    for ex in (3, 6):
        vol[5][h - 2][ex] = 1  # pupila preta
        vol[6][h - 2][ex] = 2  # brilho branco acima da pupila
        # Garante suporte atras/abaixo do olho se a esfera arredondar
        if vol[4][h - 2][ex] == 0:
            vol[4][h - 2][ex] = 6

    return {'palette': palette, 'slices': to_strings(vol)}


EXPECTED_SPECS = {
    'pine_tree': (20, 20, 34),
    'sakura_oak': (32, 32, 42),
    'boulder_large': (14, 14, 12),
    'mushroom_giant': (16, 16, 16),
    'wood_sign': (10, 8, 14),
    'campfire': (12, 12, 9),
    'bush_berry': (12, 12, 9),
    'golden_fish': (12, 8, 6),
    'ruin_pillar': (12, 12, 18),
    'flower_tuft': (10, 10, 5),
    'cozy_cabin': (26, 24, 28),
    'torii_gate': (22, 10, 26),
    'stone_lantern': (10, 10, 18),
    'lighthouse': (18, 18, 42),
    'beach_umbrella': (18, 18, 18),
    'wood_boat': (20, 12, 8),
    'sunflower': (10, 10, 16),
    'hay_bale': (14, 14, 10),
    'tree_stump': (14, 14, 10),
    'pumpkin_patch': (14, 14, 8),
    'grass_tuft_short': (14, 14, 3),
    'grass_tuft_tall': (14, 14, 4),
    'baby_chick': (10, 10, 8),
}


def validate_pack(pack):
    assert set(pack.keys()) == set(EXPECTED_SPECS.keys()), (
        f"Chaves divergentes: {set(pack.keys())} vs {set(EXPECTED_SPECS.keys())}"
    )
    results = {}
    for name, (exp_w, exp_h, exp_z) in EXPECTED_SPECS.items():
        model = pack[name]
        assert isinstance(model, dict), f"{name}: deve ser dict"
        assert 'palette' in model and 'slices' in model, f"{name}: faltam campos palette/slices"

        palette = model['palette']
        slices = model['slices']
        assert 6 <= len(palette) <= 10, f"{name}: palette tem {len(palette)} cores (esperado 6..10)"
        assert len(palette) <= 36, f"{name}: palette excede 36 cores"
        assert palette[0] == 'rgba(0,0,0,0)', f"{name}: palette[0] != 'rgba(0,0,0,0)'"
        for c in palette[1:]:
            assert c.lower() not in ('#000000', '#000'), f"{name}: preto puro proibido: {c}"

        assert len(slices) == exp_z, f"{name}: Z={len(slices)} != {exp_z}"
        assert isinstance(slices[0][0], str), f"{name}: slices[0][0] nao e str"

        valid_chars = {encode_char(i) for i in range(len(palette))}
        solid_coords = set()
        for z, s in enumerate(slices):
            assert len(s) == exp_h, f"{name} z={z}: H={len(s)} != {exp_h}"
            for y, row in enumerate(s):
                assert isinstance(row, str), f"{name} z={z} y={y}: linha nao e str"
                assert len(row) == exp_w, f"{name} z={z} y={y}: W={len(row)} != {exp_w}"
                for x, ch in enumerate(row):
                    assert ch in valid_chars, f"{name} ({x},{y},{z}): char '{ch}' fora da paleta"
                    if ch != '0':
                        solid_coords.add((x, y, z))

        # Checa que z=0 nao esta vazio e usa BFS 6-conectado a partir de TODOS os voxels em z=0
        # (permite multiplos componentes independentes apoiados no chao, sem nenhum voxel flutuante em z > 0)
        ground = [p for p in solid_coords if p[2] == 0]
        assert ground, f"{name}: nenhum voxel na base z=0"
        visited = set(ground)
        q = deque(ground)
        while q:
            cx, cy, cz = q.popleft()
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                nb = (cx + dx, cy + dy, cz + dz)
                if nb in solid_coords and nb not in visited:
                    visited.add(nb)
                    q.append(nb)
        floating = [p for p in (solid_coords - visited) if p[2] > 0]
        assert not floating, f"{name}: {len(floating)} voxels desconectados/flutuando em z>0! ex: {floating[0]}"

        results[name] = {
            'dims': (exp_w, exp_h, exp_z),
            'palette_len': len(palette),
            'voxels': len(solid_coords),
        }
    return results


def main():
    pack = {
        'pine_tree': build_pine_tree(),
        'sakura_oak': build_sakura_oak(),
        'boulder_large': build_boulder_large(),
        'mushroom_giant': build_mushroom_giant(),
        'wood_sign': build_wood_sign(),
        'campfire': build_campfire(),
        'bush_berry': build_bush_berry(),
        'golden_fish': build_golden_fish(),
        'ruin_pillar': build_ruin_pillar(),
        'flower_tuft': build_flower_tuft(),
        'cozy_cabin': build_cozy_cabin(),
        'torii_gate': build_torii_gate(),
        'stone_lantern': build_stone_lantern(),
        'lighthouse': build_lighthouse(),
        'beach_umbrella': build_beach_umbrella(),
        'wood_boat': build_wood_boat(),
        'sunflower': build_sunflower(),
        'hay_bale': build_hay_bale(),
        'tree_stump': build_tree_stump(),
        'pumpkin_patch': build_pumpkin_patch(),
        'grass_tuft_short': build_grass_tuft_short(),
        'grass_tuft_tall': build_grass_tuft_tall(),
        'baby_chick': build_baby_chick(),
    }

    out_path = 'C:/github/PixelArt/terrain_props_pack.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pack, f, indent=2)

    with open(out_path, 'r', encoding='utf-8') as f:
        loaded = json.load(f)

    summary = validate_pack(loaded)
    print(f"SUCCESS: {out_path} generated and validated ({len(summary)} models):")
    for name, info in summary.items():
        w, h, z = info['dims']
        print(f"  - {name}: {w}x{h}x{z}, palette={info['palette_len']} colors, voxels={info['voxels']}")


if __name__ == '__main__':
    main()
