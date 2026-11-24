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
    """1. pine_tree (28 x 28 x 48)"""
    w, h, z_count = 28, 28, 48
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: sombra escura tronco
        '#6B4226',  # 2: tronco base
        '#8C5A38',  # 3: tronco iluminado
        '#143628',  # 4: verde-pinheiro contorno escuro interno natural
        '#1B4332',  # 5: verde-pinheiro sombra base
        '#2D6A4F',  # 6: verde-pinheiro médio
        '#40916C',  # 7: verde-pinheiro claro
        '#74C69D',  # 8: pontas iluminadas nas bordas/topo
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 13.5, 13.5

    # Tronco marrom reto central (z=0..11) com r=3.2 e leve alargamento de raiz na base (z=0..1)
    # Estende nucleo interno ate z=38 para garantir 100% de conexao entre as camadas
    for z in range(39):
        if z == 0:
            rad = 4.2
        elif z == 1:
            rad = 3.6
        elif z <= 11:
            rad = 3.2
        else:
            rad = 2.2
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= rad * rad:
                    if dx + dy > 1.2:
                        vol[z][y][x] = 3
                    elif dx + dy < -1.2:
                        vol[z][y][x] = 1
                    else:
                        vol[z][y][x] = 2

    # 4 camadas cônicas bem definidas de copa verde-pinheiro (z=10..47)
    cones = [
        (10, 21, 13.2, 4.4),  # camada 1: z=10..21
        (19, 30, 11.4, 3.6),  # camada 2: z=19..30
        (28, 38, 9.2, 2.8),   # camada 3: z=28..38
        (36, 47, 7.0, 0.5),   # camada 4: z=36..47
    ]

    for tier_idx, (z_start, z_end, r_bot, r_top) in enumerate(cones):
        span = z_end - z_start
        for z in range(z_start, z_end + 1):
            t = (z - z_start) / span
            base_r = r_bot * (1.0 - t) + r_top * t
            for y in range(h):
                for x in range(w):
                    dx = x - cx
                    dy = y - cy
                    dist = (dx * dx + dy * dy) ** 0.5
                    ang = math.atan2(dy, dx)
                    # Recorte estrelado de galhos de pinheiro
                    bough_wave = 0.85 * math.cos(ang * 8.0 + tier_idx * 0.7)
                    if z >= 45:
                        bough_wave = 0.0
                    eff_r = max(0.6, base_r + bough_wave * (1.0 - 0.65 * t))
                    if dist <= eff_r:
                        is_edge = dist >= eff_r - 1.4
                        is_lit = (dx + dy) > 0.8
                        is_deep_under = (z <= z_start + 1) and (dist > eff_r * 0.52)
                        if z >= 45:
                            col = 8
                        elif is_deep_under:
                            col = 4  # contorno escuro interno natural sob cada camada
                        elif is_edge and is_lit and t > 0.15:
                            col = 8
                        elif is_edge and (dx >= -1.0 or dy >= -1.0):
                            col = 7
                        elif t < 0.30 and not is_lit:
                            col = 5
                        elif t > 0.65 or is_lit:
                            col = 7 if (hash3(x, y, z) % 4 == 0) else 6
                        else:
                            col = 6 if (dx + dy >= -2.0) else 5
                        vol[z][y][x] = col

    # Ponta nítida conectada em z=47
    for y in (13, 14):
        for x in (13, 14):
            vol[47][y][x] = 8

    return {'palette': palette, 'slices': to_strings(vol)}


def build_sakura_oak():
    """2. sakura_oak (54 x 54 x 68)"""
    w, h, z_count = 54, 54, 68
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: sombra tronco escura
        '#5C3A28',  # 2: tronco médio
        '#80533B',  # 3: tronco iluminado
        '#9D174D',  # 4: sombra magenta profunda sob a copa
        '#DB2777',  # 5: rosa cerejeira profundo
        '#F472B6',  # 6: rosa cerejeira vivo
        '#F9A8D4',  # 7: rosa cerejeira médio/claro
        '#FCE7F3',  # 8: rosa muito claro
        '#FFFFFF',  # 9: flores brancas salpicadas
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 26.5, 26.5

    # Tronco largo orgânico com raízes grossas espalhadas (z=0..6: r=14 -> r=6) até z=28
    roots = [
        (0.0, 1.0, 14.0),
        (1.0, 0.25, 13.8),
        (0.7, -0.75, 13.5),
        (-0.2, -1.0, 13.8),
        (-0.95, -0.2, 14.0),
        (-0.75, 0.75, 13.6),
    ]
    for z in range(29):
        if z <= 6:
            t_root = z / 6.0
            trunk_r = 8.4 * (1.0 - t_root) + 6.0 * t_root
        else:
            t_up = (z - 6) / 22.0
            trunk_r = 6.0 - 1.1 * t_up
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                ang = math.atan2(dy, dx)
                bark_flute = 0.45 * math.sin(ang * 7.0 + z * 0.12)
                in_trunk = (dx * dx + dy * dy) <= (trunk_r + bark_flute) ** 2
                in_root = False
                if z <= 6:
                    root_reach = 1.0 - (z / 6.5)
                    for rx_dir, ry_dir, max_r in roots:
                        length = max_r * (0.45 + 0.55 * root_reach)
                        for step in range(8):
                            s = step / 7.0
                            px = cx + rx_dir * length * s
                            py = cy + ry_dir * length * s
                            r_rad = (3.4 - 1.7 * s) * (0.55 + 0.45 * root_reach)
                            if (x - px) ** 2 + (y - py) ** 2 <= r_rad * r_rad:
                                in_root = True
                                break
                        if in_root:
                            break
                if in_trunk or in_root:
                    if dx + dy > 2.2:
                        vol[z][y][x] = 3
                    elif dx + dy < -2.2:
                        vol[z][y][x] = 1
                    else:
                        vol[z][y][x] = 2

    # Galhos principais se abrindo em z=20..30+ sustentando toda a copa (z=24..67)
    branches = [
        ((26.5, 26.5, 20.0), (13.0, 26.0, 32.0), 3.3),
        ((26.5, 26.5, 21.0), (40.0, 27.0, 33.0), 3.3),
        ((26.5, 26.5, 20.5), (26.0, 13.0, 32.0), 3.2),
        ((26.5, 26.5, 21.5), (27.5, 40.0, 33.0), 3.3),
        ((26.5, 26.5, 22.0), (16.5, 16.5, 35.0), 2.9),
        ((26.5, 26.5, 22.5), (37.0, 16.5, 35.0), 2.9),
        ((26.5, 26.5, 22.5), (16.5, 37.0, 35.0), 2.9),
        ((26.5, 26.5, 23.0), (37.0, 37.0, 36.0), 2.9),
        ((26.5, 26.5, 24.0), (26.5, 26.5, 42.0), 3.5),
    ]
    for (x0, y0, z0), (x1, y1, z1), r_b in branches:
        steps = 24
        for i in range(steps + 1):
            s = i / steps
            bx = x0 + (x1 - x0) * s
            by = y0 + (y1 - y0) * s
            bz = z0 + (z1 - z0) * s
            rad = r_b * (1.0 - 0.4 * s)
            for z in range(max(0, int(bz - rad - 1)), min(z_count, int(bz + rad + 2))):
                for y in range(max(0, int(by - rad - 1)), min(h, int(by + rad + 2))):
                    for x in range(max(0, int(bx - rad - 1)), min(w, int(bx + rad + 2))):
                        if (x - bx) ** 2 + (y - by) ** 2 + (z - bz) ** 2 <= rad * rad:
                            vol[z][y][x] = 3 if (z > bz and y >= by) else (1 if z < bz - 0.5 else 2)

    # Copa exuberante arredondada em nuvens de flores rosa-cerejeira (z=24..67)
    lobes = [
        (26.5, 26.5, 45.5, 18.0, 18.0, 17.5),  # núcleo majestoso
        (26.5, 26.5, 57.5, 13.5, 13.5, 10.2),  # cúpula topo até z=67
        (13.0, 26.0, 38.0, 11.2, 11.5, 12.0),  # nuvem W
        (40.0, 27.0, 39.0, 11.2, 11.5, 12.0),  # nuvem E
        (26.0, 13.0, 38.5, 11.5, 11.2, 12.0),  # nuvem N
        (27.0, 40.0, 39.5, 11.5, 11.2, 12.2),  # nuvem S
        (16.5, 16.5, 42.0, 10.5, 10.5, 11.5),  # nuvem NW
        (36.5, 16.5, 43.0, 10.5, 10.5, 11.5),  # nuvem NE
        (16.5, 36.5, 42.5, 10.5, 10.5, 11.5),  # nuvem SW
        (36.5, 36.5, 43.5, 10.8, 10.8, 11.8),  # nuvem SE
        (19.0, 20.0, 52.5, 9.5, 9.5, 9.5),     # coroa alta NW
        (34.0, 33.0, 53.5, 9.8, 9.8, 9.8),     # coroa alta SE
        (34.0, 20.0, 52.0, 9.0, 9.0, 9.0),     # coroa alta NE
        (19.5, 33.5, 52.5, 9.2, 9.2, 9.2),     # coroa alta SW
    ]

    for z in range(24, z_count):
        for y in range(h):
            for x in range(w):
                best_d = 999.0
                for lx, ly, lz, rx, ry, rz in lobes:
                    d = ((x - lx) / rx) ** 2 + ((y - ly) / ry) ** 2 + ((z - lz) / rz) ** 2
                    if d < best_d:
                        best_d = d
                # Leve recorte orgânico nas bordas externas das nuvens
                edge_ripple = 0.045 * math.sin(x * 0.55) * math.cos(y * 0.55)
                if best_d <= 1.0 + edge_ripple:
                    # Mantem galhos inferiores visiveis ate z=29
                    if z <= 29 and vol[z][y][x] in (1, 2, 3):
                        continue
                    h_val = hash3(x, y, z)
                    light = (z - 38.0) * 0.045 + (y - cy) * 0.02 + (x - cx) * 0.018
                    if z <= 28 or (z < 36 and best_d > 0.85 and light < -0.1):
                        col = 4
                    elif z >= 59 or (z >= 50 and light > 0.35):
                        if h_val % 6 == 0 or (z >= 64 and h_val % 3 == 0):
                            col = 9  # flores brancas no topo
                        elif h_val % 3 == 0 or z >= 62:
                            col = 8
                        else:
                            col = 7
                    elif light < -0.25:
                        col = 5
                    else:
                        if h_val % 14 == 0 and z >= 42:
                            col = 9
                        elif h_val % 5 == 0 and z >= 38:
                            col = 8
                        elif light > 0.12:
                            col = 7
                        else:
                            col = 6
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
    """9. ruin_pillar (18 x 18 x 34)"""
    w, h, z_count = 18, 18, 34
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
    cx, cy = 8.5, 8.5

    # z=0..5: base quadrada escalonada (plinto)
    for z in range(6):
        pad = 1 if z <= 1 else (2 if z <= 3 else 3)
        for y in range(pad, h - pad):
            for x in range(pad, w - pad):
                # Cantos chanfrados no degrau superior da base
                if z >= 4 and x in (pad, w - pad - 1) and y in (pad, h - pad - 1):
                    continue
                is_edge = (x in (pad, w - pad - 1) or y in (pad, h - pad - 1))
                if z == 0 or (is_edge and (x < 4 or y < 4)):
                    vol[z][y][x] = 2
                elif z in (1, 3, 5) and is_edge and (x + y >= 16):
                    vol[z][y][x] = 5
                elif is_edge:
                    vol[z][y][x] = 4 if z in (3, 5) else 2
                else:
                    vol[z][y][x] = 3

    # z=6..28: fuste octogonal estriado com rachaduras
    for z in range(6, 29):
        for y in range(h):
            for x in range(w):
                dx = abs(x - cx)
                dy = abs(y - cy)
                if dx <= 5.5 and dy <= 5.5 and (dx + dy) <= 8.2:
                    # Estrias verticais nas faces cardinais/diagonais
                    is_flute = (
                        (dx >= 4.6 and abs(dy - 2.0) <= 0.6) or
                        (dy >= 4.6 and abs(dx - 2.0) <= 0.6)
                    )
                    # Rachaduras diagonais marcantes
                    is_crack = (
                        (10 <= z <= 13 and x == 9 + (z - 10) // 2 and y == 13) or
                        (14 <= z <= 17 and x == 11 and y == 12 - (z - 14) // 2) or
                        (19 <= z <= 22 and x == 5 + (z - 19) // 2 and y == 12) or
                        (8 <= z <= 11 and x == 4 and y == 10 - (z - 8) // 2)
                    )
                    if is_crack:
                        vol[z][y][x] = 1
                    elif is_flute:
                        vol[z][y][x] = 2 if (x + y < 17) else 3
                    elif x + y >= 21:
                        vol[z][y][x] = 4 if (dx >= 4.5 or dy >= 4.5) else 3
                    elif x + y <= 13:
                        vol[z][y][x] = 2
                    else:
                        vol[z][y][x] = 3

    # z=29..33: capitel quebrado assimétrico
    for z in range(29, z_count):
        pad = 2 if z >= 30 else 3
        for y in range(pad, h - pad):
            for x in range(pad, w - pad):
                # Plano inclinado irregular de quebra: mais alto no canto NW (x<=8, y<=8)
                break_h = 33.4 - (x * 0.22 + y * 0.18)
                if (x <= 6 and y <= 7) or (x <= 5 and y <= 10):
                    break_h += 0.8
                if x >= 11 and y >= 11:
                    break_h -= 1.2
                if z <= break_h:
                    is_top_break = (z + 1 > break_h)
                    if is_top_break:
                        vol[z][y][x] = 5 if (x + y >= 14) else 4
                    elif x + y <= 12:
                        vol[z][y][x] = 2
                    else:
                        vol[z][y][x] = 4 if (z == 30 and (x in (pad, w - pad - 1) or y in (pad, h - pad - 1))) else 3

    # Musgo verde subindo na base e nas quebras (z=0..11 e degraus)
    for z in range(12):
        for y in range(h):
            for x in range(w):
                if vol[z][y][x] in (2, 3, 4, 5):
                    # Manchas organicas de musgo na frente-esquerda e tras-direita
                    patch1 = (x - 4.0) ** 2 + (y - 13.0) ** 2 + (z * 0.65) ** 2 <= 22.0
                    patch2 = (x - 13.5) ** 2 + (y - 4.0) ** 2 + (z * 0.75) ** 2 <= 16.0
                    if (patch1 or patch2) and (hash3(x, y, z) % 3 != 0 or z <= 2):
                        vol[z][y][x] = 7 if (z >= 3 or x + y >= 16) else 6

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
    """11. cozy_cabin (52 x 46 x 54)"""
    w, h, z_count = 52, 46, 54
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: madeira escura / vigas / batente / argamassa
        '#6B4226',  # 2: madeira média / tábua da porta / venezianas
        '#64748B',  # 3: fundação sólida pedra cinza/ardósia
        '#F5EBDC',  # 4: parede creme aconchegante
        '#FACC15',  # 5: maçaneta dourada
        '#FDE68A',  # 6: brilho janela amarelo claro
        '#F59E0B',  # 7: brilho janela âmbar quente
        '#C25E3E',  # 8: telhado terracota principal / tijolo claro
        '#9E4429',  # 9: telhado terracota sombra / tijolo escuro
    ]
    vol = make_volume(w, h, z_count, 0)

    # z=0..4: fundação sólida de pedra cinza/ardósia (x=4..47, y=4..41)
    for z in range(5):
        for y in range(4, 42):
            for x in range(4, 48):
                # Rebaixo nos degraus da entrada em y=41 diante da porta (x=19..32, z=3..4)
                if y == 41 and z >= 3 and 19 <= x <= 32:
                    continue
                is_mortar = (z in (0, 2) and (x + (z // 2) * 3) % 6 == 0) and (x in (4, 47) or y in (4, 41))
                vol[z][y][x] = 1 if (z == 0 and (x in (4, 47) or y in (4, 41))) or is_mortar else 3

    # Degrau de pedra frontal acolhedor (y=42..43, x=19..32, z=0..1)
    for z in range(2):
        for y in range(42, 44 - z):
            for x in range(19, 33):
                vol[z][y][x] = 3

    # z=5..28: paredes creme/madeira (x=5..46, y=5..40) com vigas nos 4 cantos, meio e moldura superior
    for z in range(5, 29):
        for y in range(5, 41):
            for x in range(5, 47):
                is_wall = (x in (5, 6, 45, 46) or y in (5, 6, 39, 40))
                if not is_wall:
                    if z == 28:
                        vol[z][y][x] = 2  # laje de teto sólida
                    continue
                is_corner = (x in (5, 6, 45, 46)) and (y in (5, 6, 39, 40))
                is_mid_x = (y in (5, 6, 39, 40)) and (x in (17, 18, 33, 34) or (y in (5, 6) and x in (25, 26)))
                is_mid_y = (x in (5, 6, 45, 46)) and (y in (23, 24))
                is_top_frame = (z in (27, 28))
                is_base_beam = (z == 5)
                if is_corner or is_mid_x or is_mid_y or is_top_frame or is_base_beam:
                    vol[z][y][x] = 1 if (z in (5, 28) or (x in (5, 46) and y in (5, 40))) else 2
                else:
                    vol[z][y][x] = 4

    # Porta frontal convidativa e grande em y = H - 6 = 40 (x=19..32, z=3..24)
    # Selo interno em y=38..39 + folha da porta em y=39 + batente em y=40 + macaneta dourada (#FACC15)
    for z in range(3, 25):
        for x in range(19, 33):
            vol[z][38][x] = 1
            is_frame = (x in (19, 20, 31, 32) or z in (23, 24))
            if is_frame:
                vol[z][39][x] = 1
                vol[z][40][x] = 1 if (x in (19, 32) or z == 24) else 2
            else:
                # Tabuas verticais da porta em y=39 e abertura livre em y=40 para profundidade 3D
                vol[z][40][x] = 0
                is_seam = (x in (23, 26, 28)) or (z in (6, 15, 20))
                vol[z][39][x] = 1 if is_seam else 2
    # Macaneta dourada (#FACC15) bem visivel
    for kz in (12, 13):
        vol[kz][39][29] = 5
        vol[kz][40][29] = 5

    # Janelas duplas com venezianas e brilho amarelo aconchegante (#FDE68A / #F59E0B)
    def build_window_y(y_face, y_back, y_out, x0, x1, z0, z1):
        # x0..x1: largura 7 (ex: 9..15 ou 36..42), z0..z1 = 12..21
        for z in range(z0 - 1, z1 + 2):
            for x in range(x0, x1 + 1):
                vol[z][y_back][x] = 1
                if z == z0 - 1 or z == z1 + 1:
                    # Peitoril e verga de madeira
                    vol[z][y_face][x] = 2
                    if z == z0 - 1:
                        vol[z][y_out][x] = 2
                elif x in (x0, x1):
                    # Venezianas laterais com ripas
                    col = 1 if (z % 2 == 0) else 2
                    vol[z][y_face][x] = col
                    vol[z][y_out][x] = col
                elif z in (z0, z1) or x == (x0 + x1) // 2 or z == (z0 + z1) // 2:
                    vol[z][y_face][x] = 1  # caixilho cruzado de janela dupla
                else:
                    vol[z][y_face][x] = 6 if (z >= 15 and (x + z) % 3 != 0) else 7

    def build_window_x(x_face, x_back, x_out, y0, y1, z0, z1):
        # y0..y1: largura 8 (ex: 15..22 ou 26..33), z0..z1 = 12..21
        for z in range(z0 - 1, z1 + 2):
            for y in range(y0, y1 + 1):
                vol[z][y][x_back] = 1
                if z == z0 - 1 or z == z1 + 1:
                    vol[z][y][x_face] = 2
                    if z == z0 - 1:
                        vol[z][y][x_out] = 2
                elif y in (y0, y1):
                    col = 1 if (z % 2 == 0) else 2
                    vol[z][y][x_face] = col
                    vol[z][y][x_out] = col
                elif z in (z0, z1) or y == (y0 + y1) // 2 or z == (z0 + z1) // 2:
                    vol[z][y][x_face] = 1
                else:
                    vol[z][y][x_face] = 6 if (z >= 15 and (y + z) % 3 != 0) else 7

    # Frente (y=40) aos lados da porta: x=9..15 e x=36..42
    build_window_y(40, 39, 41, 9, 15, 12, 21)
    build_window_y(40, 39, 41, 36, 42, 12, 21)
    # Traseira (y=5) simetrica
    build_window_y(5, 6, 4, 9, 15, 12, 21)
    build_window_y(5, 6, 4, 36, 42, 12, 21)
    # 2 laterais (x=5 e x=46): y=15..22 e y=26..33, z=12..21
    build_window_x(5, 6, 4, 15, 22, 12, 21)
    build_window_x(5, 6, 4, 26, 33, 12, 21)
    build_window_x(46, 45, 47, 15, 22, 12, 21)
    build_window_x(46, 45, 47, 26, 33, 12, 21)

    # z=28..48: telhado inclinado dois-águas em terracota (#C25E3E / #9E4429)
    # Beiral saliente (x=2..49, y=2..43), afunilando em y até a cumeeira central y=22..23 em z=48
    for z in range(28, 49):
        dz = z - 28  # 0..20
        half_span = 20.5 - dz * 1.0  # 20.5 em z=28 -> 0.5 em z=48
        y_min = max(2, int(round(22.5 - half_span)))
        y_max = min(43, int(round(22.5 + half_span)))
        inner_y0 = max(5, y_min + 2)
        inner_y1 = min(40, y_max - 2)

        for y in range(y_min, y_max + 1):
            for x in range(2, 50):
                is_roof_shell = (
                    y <= y_min + 1
                    or y >= y_max - 1
                    or z == 48
                    or x in (2, 3, 48, 49)
                )
                # Oitões triangulares nas laterais (x=5..6 e x=45..46)
                if x in (5, 6, 45, 46) and inner_y0 <= y <= inner_y1 and z < 47:
                    if y in (inner_y0, inner_y1):
                        vol[z][y][x] = 2
                    else:
                        vol[z][y][x] = 4
                elif is_roof_shell:
                    # Padrao de telhas terracota
                    tile = ((x // 2 + y + z) % 3 == 0) or (z in (28, 48)) or (x in (2, 49))
                    if y > 22 and not tile:
                        vol[z][y][x] = 8
                    elif tile:
                        vol[z][y][x] = 9
                    else:
                        vol[z][y][x] = 8 if (x + z) % 4 != 0 else 9

    # Janelinhas iluminadas nos oitões laterais (x=5 e x=46, y=21..24, z=32..36)
    for gx in (5, 46):
        for z in range(32, 37):
            for y in range(21, 25):
                if z in (32, 36) or y in (21, 24):
                    vol[z][y][gx] = 2
                else:
                    vol[z][y][gx] = 6 if z >= 34 else 7

    # z=34..53: chaminé de tijolinho (x=36..42, y=12..18) subindo acima do telhado
    for z in range(34, 54):
        is_cap = (z == 51)
        x0, x1 = (35, 43) if is_cap else (36, 42)
        y0, y1 = (11, 19) if is_cap else (12, 18)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if z == 53 and 38 <= x <= 40 and 14 <= y <= 16:
                    vol[z][y][x] = 1  # boca da chamine escura
                else:
                    brick = (x + y * 2 + z * 2) % 4
                    vol[z][y][x] = 9 if brick in (0, 3) else 8

    return {'palette': palette, 'slices': to_strings(vol)}


def build_torii_gate():
    """12. torii_gate (50 x 16 x 54)"""
    w, h, z_count = 50, 16, 54
    palette = [
        'rgba(0,0,0,0)',
        '#1C1917',  # 1: telhado preto suave / placa central preta
        '#2B1D16',  # 2: nemaki pedra escura sombra
        '#3F3F46',  # 3: nemaki pedra escura cinza
        '#7F1D1D',  # 4: vermelho sombra profunda
        '#991B1B',  # 5: vermelho escuro
        '#DC2626',  # 6: vermelho vivo principal
        '#EF4444',  # 7: vermelho iluminado
        '#FACC15',  # 8: centro dourado placa central
    ]
    vol = make_volume(w, h, z_count, 0)

    # z=0..5: duas bases de pedra escura (nemaki) nas extremidades sem invadir x=12..37
    # Colunas ocupam x=6..11 e x=38..43; nemaki ocupa x=5..11 e x=38..44 (y=4..11)
    for z in range(6):
        for x0, x1 in ((5, 11), (38, 44)):
            for y in range(4, 12):
                for x in range(x0, x1 + 1):
                    # Chanfra os cantos externos nos topos do nemaki (z=4..5)
                    if z >= 4 and (x in (x0, x1) and y in (4, 11)):
                        continue
                    is_edge = (z == 0 or y in (4, 11) or x in (x0, x1))
                    vol[z][y][x] = 2 if is_edge else 3

    # z=4..46: duas colunas vermelhas grossas em x=6..11 e x=38..43 (y=5..10)
    # VAO CENTRAL x=12..37 (26px) fica 100% VAZIO de z=0 ate z=35!
    for z in range(4, 47):
        for x0, x1 in ((6, 11), (38, 43)):
            for y in range(5, 11):
                for x in range(x0, x1 + 1):
                    # Arredonda levemente os 4 cantos de cada pilar (6x6 octogonal)
                    if x in (x0, x1) and y in (5, 10):
                        continue
                    if z <= 5:
                        vol[z][y][x] = 3  # encaixe firme no nemaki
                    elif y >= 9:
                        vol[z][y][x] = 7 if (x in (x0 + 1, x0 + 2, x1 - 1)) else 6
                    elif y <= 6:
                        vol[z][y][x] = 5 if y == 6 else 4
                    else:
                        vol[z][y][x] = 6

    # z=36..40: travessa inferior vermelha (nuki) cobrindo x=2..47, y=6..9
    for z in range(36, 41):
        for y in range(6, 10):
            for x in range(2, 48):
                # Pontas chanfradas em x=2 e x=47
                if x in (2, 47) and z in (36, 40):
                    continue
                if z == 40:
                    vol[z][y][x] = 7 if y >= 8 else 6
                elif z == 36:
                    vol[z][y][x] = 4 if y <= 7 else 5
                elif y == 9:
                    vol[z][y][x] = 7
                elif y == 6:
                    vol[z][y][x] = 5
                else:
                    vol[z][y][x] = 6

    # z=41..46: suportes sobre os pilares + placa central (gakuzuka) em x=22..27, y=5..10
    for z in range(41, 47):
        # Aneis/suportes sobre os pilares
        for x0, x1 in ((5, 12), (37, 44)):
            if z >= 45:
                for y in range(5, 11):
                    for x in range(x0, x1 + 1):
                        vol[z][y][x] = 1 if z == 46 else 2
        # Placa central (gakuzuka) preta com centro dourado (#FACC15)
        for y in range(5, 11):
            for x in range(22, 28):
                is_front_back = (y in (5, 10))
                is_gold = is_front_back and (23 <= x <= 26) and (42 <= z <= 45)
                if is_gold:
                    # Detalhe interno escuro sutil no centro do medalhao dourado
                    if z in (43, 44) and x in (24, 25) and (x + z) % 2 == 0:
                        vol[z][y][x] = 1
                    else:
                        vol[z][y][x] = 8
                else:
                    vol[z][y][x] = 1 if (x in (22, 27) or z in (41, 46)) else 2

    # z=47..53: viga superior curva (kasagi) cobrindo x=0..49, y=4..11
    # Camadas vermelha (z=47..49) e telhado preto (z=50..53) subindo 2 fatias nas pontas (x=0..5 e x=44..49)
    for x in range(w):
        if x <= 5 or x >= 44:
            z_red0, z_red1 = 49, 51
            z_blk0, z_blk1 = 52, 53
        elif x <= 9 or x >= 40:
            z_red0, z_red1 = 48, 50
            z_blk0, z_blk1 = 51, 52
        else:
            z_red0, z_red1 = 47, 49
            z_blk0, z_blk1 = 50, 51

        for y in range(4, 12):
            # Chanfro elegante nas pontas extremas
            if (x in (0, 49)) and y in (4, 11):
                continue
            for z in range(z_red0, z_red1 + 1):
                if z == z_red0 and y in (4, 11):
                    continue
                if z == z_red0:
                    vol[z][y][x] = 5
                elif y >= 10:
                    vol[z][y][x] = 7
                elif y <= 5:
                    vol[z][y][x] = 5
                else:
                    vol[z][y][x] = 6
            for z in range(z_blk0, z_blk1 + 1):
                if z == z_blk1 and y in (4, 11):
                    continue
                vol[z][y][x] = 1 if (z == z_blk1 or y in (4, 11)) else 2

    return {'palette': palette, 'slices': to_strings(vol)}


def build_stone_lantern():
    """13. stone_lantern (14 x 14 x 24)"""
    w, h, z_count = 14, 14, 24
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
                if pad <= 3 and (x in (lo, hi) and y in (lo, hi)):
                    continue
                is_edge = (x in (lo, hi) or y in (lo, hi))
                if col_hi and is_edge and (x + y >= w - 1):
                    vol[z][y][x] = col_hi
                elif is_edge:
                    vol[z][y][x] = col_edge
                else:
                    vol[z][y][x] = col_fill

    # z=0..4: base escalonada robusta
    fill_chamfer_square(0, 1, 1, 2)
    fill_chamfer_square(1, 1, 2, 3, 4)
    fill_chamfer_square(2, 2, 2, 3, 4)
    fill_chamfer_square(3, 2, 3, 4, 5)
    fill_chamfer_square(4, 3, 3, 4, 5)

    # z=5..11: haste de pedra com anel central (z=8)
    for z in range(5, 12):
        lo, hi = (4, 9) if z == 11 else (5, 8)
        for y in range(lo, hi + 1):
            for x in range(lo, hi + 1):
                if z == 11 and x in (lo, hi) and y in (lo, hi):
                    continue
                if z == 8 and (x in (5, 8) or y in (5, 8)):
                    vol[z][y][x] = 5 if (x + y >= 14) else 2
                elif x + y >= 15:
                    vol[z][y][x] = 4
                elif x + y <= 11:
                    vol[z][y][x] = 2
                else:
                    vol[z][y][x] = 3

    # z=12..17: camara com janela luminosa (#FDE68A)
    fill_chamfer_square(12, 2, 3, 4, 5)
    for z in range(13, 17):
        for y in range(3, 11):
            for x in range(3, 11):
                is_post = (x in (3, 4, 9, 10)) and (y in (3, 4, 9, 10))
                if is_post:
                    if x in (3, 10) and y in (3, 10):
                        continue
                    vol[z][y][x] = 4 if (x + y >= 14) else (2 if x + y <= 11 else 3)
                elif 5 <= x <= 8 and 5 <= y <= 8:
                    vol[z][y][x] = 7
                elif 4 <= x <= 9 and 4 <= y <= 9:
                    vol[z][y][x] = 6  # janela luminosa reentrante nas 4 faces
    fill_chamfer_square(17, 2, 2, 3, 4)

    # z=18..23: telhadinho piramidal com pontas arrebitadas e ponta no topo
    fill_chamfer_square(18, 0, 2, 3, 4)
    # Pontas arrebitadas nos 4 cantos
    for cx_t, cy_t in ((1, 1), (12, 1), (1, 12), (12, 12)):
        vol[18][cy_t][cx_t] = 4
        vol[19][cy_t][cx_t] = 5
    fill_chamfer_square(19, 1, 3, 4, 5)
    fill_chamfer_square(20, 2, 3, 4, 5)
    fill_chamfer_square(21, 4, 4, 4, 5)
    fill_chamfer_square(22, 5, 4, 5, 5)
    for y in (6, 7):
        for x in (6, 7):
            vol[23][y][x] = 5

    return {'palette': palette, 'slices': to_strings(vol)}


def build_lighthouse():
    """14. lighthouse (34 x 34 x 84)"""
    w, h, z_count = 34, 34, 84
    palette = [
        'rgba(0,0,0,0)',
        '#231F28',  # 1: ferro escuro varanda / pilastras / vigias / batente
        '#4B5563',  # 2: pedra cinza escura base octogonal
        '#8491A3',  # 3: pedra cinza clara base octogonal
        '#CBD5E1',  # 4: branco sombra torre
        '#F8FAFC',  # 5: branco vivo torre
        '#991B1B',  # 6: vermelho sombra torre/cupula
        '#DC2626',  # 7: vermelho vivo torre/cupula
        '#F59E0B',  # 8: vidro dourado medio / macaneta / para-raios
        '#FEF08A',  # 9: vidro dourado brilhante
    ]
    vol = make_volume(w, h, z_count, 0)
    cx, cy = 16.5, 16.5

    # z=0..9: base octogonal robusta de pedra cinza (cx=16.5, cy=16.5, r=14.5)
    for z in range(10):
        rad = 14.5 if z <= 7 else (13.8 if z == 8 else 12.8)
        oct_lim = rad * 1.42
        for y in range(h):
            for x in range(w):
                dx = abs(x - cx)
                dy = abs(y - cy)
                if dx <= rad and dy <= rad and (dx + dy) <= oct_lim:
                    is_rim = (z in (0, 8, 9)) or (max(dx, dy) >= rad - 1.1) or ((dx + dy) >= oct_lim - 1.3)
                    if z == 0 or (dx + dy < 2.0 and False):
                        vol[z][y][x] = 2
                    elif is_rim and (x + y >= 33) and z >= 1:
                        vol[z][y][x] = 3
                    elif (x + y) >= 34 and z >= 2:
                        vol[z][y][x] = 3
                    else:
                        vol[z][y][x] = 2

    # z=10..61: torre cilindrica afunilando suavemente de r=11.5 (z=10) ate r=7.8 (z=61)
    for z in range(10, 62):
        rad = 11.5 - (11.5 - 7.8) * ((z - 10) / 51.0)
        if z <= 19:
            is_white = True
        elif z <= 29:
            is_white = False
        elif z <= 39:
            is_white = True
        elif z <= 49:
            is_white = False
        else:
            is_white = True
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= rad * rad:
                    lit = (dx + dy) > -1.0
                    if is_white:
                        vol[z][y][x] = 5 if lit else 4
                    else:
                        vol[z][y][x] = 7 if lit else 6

    # Portinha arqueada na frente (y=28..31, x=13..20, z=2..18) com batente escuro e macaneta dourada
    # Degrau de entrada em z=0..1 para transicao limpa ate z=2
    for z in range(2):
        for y in range(29, 33):
            for x in range(12, 22):
                vol[z][y][x] = 2 if z == 0 else 3
    for z in range(2, 19):
        for y in range(28, 32):
            for x in range(13, 21):
                # Arco superior fechando suavemente em z=15..18
                if z >= 15 and x in (13, 20):
                    continue
                if z >= 17 and x in (14, 19):
                    continue
                if z == 18 and y == 31:
                    continue
                # Abertura interna da porta para o arco
                in_arch_hole = (
                    (z <= 13 and 15 <= x <= 18) or
                    (z == 14 and 15 <= x <= 18) or
                    (z == 15 and 16 <= x <= 17)
                )
                if y == 31 and in_arch_hole:
                    continue  # recuo de 1px revelando a folha em y=30
                elif y == 30 and in_arch_hole:
                    vol[z][y][x] = 2 if (x in (16, 17) and z % 3 != 0) else 1
                elif y == 29 and in_arch_hole:
                    vol[z][y][x] = 1
                elif y >= 30 and (x in (14, 19) or (z in (14, 15, 16) and 14 <= x <= 19)):
                    vol[z][y][x] = 1  # batente escuro ao redor da porta
                else:
                    vol[z][y][x] = 3 if (x >= 17 or y == 31) else 2
    # Macaneta dourada
    vol[9][30][18] = 8
    vol[9][31][18] = 8
    vol[10][30][18] = 8

    # Janelinhas vigia pequenas escuras em z=24 e z=44 (frente + laterais/tras)
    for jz in (24, 44):
        for z in (jz - 1, jz, jz + 1):
            for ox in (15, 16, 17, 18):
                if z in (jz - 1, jz + 1) and ox in (15, 18):
                    continue
                for y in range(22, h):
                    if vol[z][y][ox] != 0 and (y == h - 1 or vol[z][y + 1][ox] == 0):
                        vol[z][y][ox] = 1
                        vol[z][y - 1][ox] = 1
                        break

    # z=62..66: varanda circular saliente de ferro escuro (r=10.5), guarda-corpo (r=9.5..10.5, oco z=64..66)
    for z in range(62, 67):
        for y in range(h):
            for x in range(w):
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if z == 62:
                    if dist <= 9.2:
                        vol[z][y][x] = 1
                elif z == 63:
                    if dist <= 10.5:
                        vol[z][y][x] = 1
                else:
                    # Nucleo base da camara de vidro (r<=6.8) + guarda-corpo em r=9.5..10.5
                    in_core = (dist <= 6.8)
                    on_rail_ring = (9.5 <= dist <= 10.5) if z < 66 else (9.0 <= dist <= 10.5)
                    is_post = (abs(x - cx) <= 1.1 or abs(y - cy) <= 1.1 or abs(abs(x - cx) - abs(y - cy)) <= 1.0)
                    if in_core:
                        vol[z][y][x] = 1
                    elif (on_rail_ring and z == 66) or (on_rail_ring and is_post):
                        vol[z][y][x] = 1

    # z=67..75: camara de vidro dourado brilhante (r=6.8, #FEF08A / #F59E0B) com 4 pilastras escuras
    for z in range(67, 76):
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist <= 6.8:
                    is_pillar = (dist >= 5.3) and (abs(abs(dx) - abs(dy)) <= 0.85)
                    if is_pillar or (z == 75 and dist >= 5.6):
                        vol[z][y][x] = 1
                    elif dist <= 3.6:
                        vol[z][y][x] = 9
                    else:
                        vol[z][y][x] = 9 if (69 <= z <= 73 and dx + dy > -1.0) else 8

    # z=76..83: cupula conica vermelha (r=8.2 ate r=1) com haste/para-raios no topo (z=81..83)
    dome_radii = {
        76: 8.2,
        77: 6.8,
        78: 5.4,
        79: 4.0,
        80: 2.5,
        81: 1.3,
    }
    for z, drad in dome_radii.items():
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= drad * drad:
                    vol[z][y][x] = 7 if (dx + dy >= -0.5 or z >= 79) else 6
    # Haste / para-raios no topo (z=81..83)
    for z in (81, 82, 83):
        for y in (16, 17):
            for x in (16, 17):
                if z == 83 and not (x == 16 and y == 16):
                    continue
                vol[z][y][x] = 8 if z == 83 else 1

    return {'palette': palette, 'slices': to_strings(vol)}


def build_beach_umbrella():
    """15. beach_umbrella (28 x 28 x 28)"""
    w, h, z_count = 28, 28, 28
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
    cx, cy = 13.5, 13.5

    # Mastro fino de madeira no centro (x=13..14, y=13..14, z=0..22, estendendo ate z=26 dentro da cupula)
    for z in range(27):
        for y in (13, 14):
            for x in (13, 14):
                vol[z][y][x] = 3 if (x == 14 and y == 14) else (1 if (x == 13 and y == 13) else 2)

    # Cupula octogonal listrada vermelho/branco grande (z=19..27, r=12.5)
    shells = {
        27: (0.0, 2.2),
        26: (0.0, 4.3),
        25: (2.6, 6.4),
        24: (4.6, 8.3),
        23: (6.5, 9.9),
        22: (8.2, 11.1),
        21: (9.5, 11.9),
        20: (10.6, 12.5),
        19: (11.4, 12.5),
    }
    for z, (r_min, r_max) in shells.items():
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                oct_d = max(abs(dx), abs(dy), (abs(dx) + abs(dy)) * 0.72)
                if r_min <= oct_d <= r_max:
                    if z == 27 and oct_d <= 1.1:
                        vol[z][y][x] = 3
                        continue
                    ang = math.atan2(dy, dx)
                    sector = int(((ang + math.pi + math.pi / 8.0) / (2.0 * math.pi)) * 8.0) % 8
                    is_red = (sector % 2 == 0)
                    is_shaded = (z == 19) or (dx + dy < -3.0)
                    if is_red:
                        vol[z][y][x] = 4 if is_shaded else 5
                    else:
                        vol[z][y][x] = 6 if is_shaded else 7

    return {'palette': palette, 'slices': to_strings(vol)}


def build_wood_boat():
    """16. wood_boat (34 x 20 x 12)"""
    w, h, z_count = 34, 20, 12
    palette = [
        'rgba(0,0,0,0)',
        '#3B2219',  # 1: borda marrom escura / sombra quilha
        '#5C3A21',  # 2: madeira escura casco externo
        '#7C4D2B',  # 3: madeira media casco / interior
        '#A66E4E',  # 4: madeira clara / bancos
        '#C88E65',  # 5: realce bancos / borda interna
    ]
    vol = make_volume(w, h, z_count, 0)
    cy = 9.5

    # Perfil de largura por X (popa x=0..4, meio x=5..26, proa afilada x=27..33)
    half_widths = []
    for x in range(w):
        if x <= 5:
            # Popa arredondada/afilada
            t = x / 5.0
            hw = 1.6 + 6.9 * math.sin(t * math.pi * 0.5)
        elif x <= 24:
            hw = 8.5
        else:
            # Proa afilada ate x=33
            t = (33 - x) / 9.0
            hw = 1.0 + 7.5 * (t ** 0.78)
        half_widths.append(hw)

    z_scales = {
        0: 0.45, 1: 0.62, 2: 0.76, 3: 0.86,
        4: 0.92, 5: 0.96, 6: 0.98, 7: 1.00,
        8: 1.01, 9: 1.02, 10: 1.03, 11: 1.04,
    }

    for z in range(z_count):
        zs = z_scales[z]
        for x in range(w):
            # Quilha sobe ligeiramente nas pontas extremas
            if z == 0 and (x <= 1 or x >= 32):
                continue
            hw = half_widths[x] * zs
            # Fundo solido em z=0..3; interior oco de z=4..11
            inner_hw = -1.0 if z <= 3 else max(0.0, hw - 1.9)
            if x <= 2 or x >= 30:
                inner_hw = -1.0
            for y in range(h):
                dy = abs(y - cy)
                if dy <= hw and dy >= inner_hw:
                    if z == 11 or (z == 10 and dy >= hw - 1.0):
                        vol[z][y][x] = 1  # borda marrom escura
                    elif z == 0:
                        vol[z][y][x] = 1
                    elif z <= 3:
                        vol[z][y][x] = 3 if (dy < hw - 1.4 and z == 3) else 2
                    elif dy >= hw - 0.9:
                        vol[z][y][x] = 3 if y >= cy else 2
                    else:
                        vol[z][y][x] = 4 if z >= 8 else 3

    # 2 bancos internos (x=10..11 e x=21..22 em z=5..6)
    for bx in (10, 11, 21, 22):
        hw_seat = half_widths[bx] * z_scales[6]
        for z in (5, 6):
            for y in range(h):
                if abs(y - cy) <= hw_seat - 0.8:
                    vol[z][y][bx] = 5 if (z == 6 and y >= cy) else (4 if z == 6 else 3)

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
    'pine_tree': (28, 28, 48),
    'sakura_oak': (54, 54, 68),
    'boulder_large': (14, 14, 12),
    'mushroom_giant': (16, 16, 16),
    'wood_sign': (10, 8, 14),
    'campfire': (12, 12, 9),
    'bush_berry': (12, 12, 9),
    'golden_fish': (12, 8, 6),
    'ruin_pillar': (18, 18, 34),
    'flower_tuft': (10, 10, 5),
    'cozy_cabin': (52, 46, 54),
    'torii_gate': (50, 16, 54),
    'stone_lantern': (14, 14, 24),
    'lighthouse': (34, 34, 84),
    'beach_umbrella': (28, 28, 28),
    'wood_boat': (34, 20, 12),
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

        if name == 'torii_gate':
            # Confirmacao explicita: vao central x=12..37, z=0..35 deve ser 100% vazio ('0')
            for z_chk in range(0, 36):
                for y_chk in range(exp_h):
                    for x_chk in range(12, 38):
                        assert slices[z_chk][y_chk][x_chk] == '0', (
                            f"torii_gate vao central nao vazio em ({x_chk},{y_chk},{z_chk})"
                        )

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
