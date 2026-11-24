import json
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

        # Checa que z=0 nao esta vazio e que todos os voxels estao conectados (6-conectividade) ao chao
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
        floating = solid_coords - visited
        assert not floating, f"{name}: {len(floating)} voxels desconectados/flutuando! ex: {next(iter(floating))}"

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
