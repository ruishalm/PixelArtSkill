import json

def make_grid(w, h, fill=0):
    return [[fill for _ in range(w)] for _ in range(h)]

def to_strings(slices):
    res = []
    for s in slices:
        res.append([''.join(str(v) for v in row) for row in s])
    return res

# 1. MESA DE ESTUDO AMPLA & ESPAÇOSA (64x34, 15 slices)
desk_w, desk_h = 64, 34
desk_slices = []
for z in range(15):
    g = make_grid(desk_w, desk_h, 0)
    if z < 10: # 4 Pernas de madeira maciça escura
        for lx, ly in [(4, 4), (54, 4), (4, 24), (54, 24)]:
            for dy in range(6):
                for dx in range(6):
                    g[ly + dy][lx + dx] = 1 # perna escura
    elif z < 12: # Estrutura e travessas reforçadas sob o tampo
        for ly in range(4, 30):
            g[ly][4] = 1; g[ly][5] = 1; g[ly][6] = 1
            g[ly][57] = 1; g[ly][58] = 1; g[ly][59] = 1
        for lx in range(4, 60):
            g[4][lx] = 1; g[5][lx] = 1
            g[28][lx] = 1; g[29][lx] = 1
    else: # Tampo amplo de carvalho aconchegante (z=12, 13, 14)
        for y in range(2, 32):
            for x in range(2, 62):
                if x in (2, 61) or y in (2, 31):
                    g[y][x] = 3 # Chanfro sutil da borda
                else:
                    g[y][x] = 2 # Carvalho acolhedor
    desk_slices.append(g)

# 2. NOTEBOOK ELEGANTE NO SUPORTE (24x20, 17 slices com tela sólida e IDE)
lap_w, lap_h = 24, 20
lap_slices = []
for z in range(17):
    g = make_grid(lap_w, lap_h, 0)
    if z < 2: # Base do suporte no tampo (duas sapatas em U sólidas)
        for y in range(6, 16):
            for x in (6, 7, 16, 17):
                g[y][x] = 1
        for x in range(6, 18):
            g[15][x] = 1 # barra transversal frontal
            g[14][x] = 1
    elif z < 5: # Hastes elevadoras traseiras reforçadas
        ry = 12 - (z - 2) * 2
        for x in range(6, 10):
            g[ry][x] = 1; g[ry+1][x] = 1
        for x in range(14, 18):
            g[ry][x] = 1; g[ry+1][x] = 1
        if z == 4: # Bandeja superior de apoio do notebook
            for y in range(6, 12):
                for x in range(5, 19):
                    g[y][x] = 1
    elif z == 5: # Base inferior do laptop
        for y in range(5, 16):
            for x in range(3, 21):
                g[y][x] = 2
    elif z == 6: # Deck do teclado, trackpad e dobradiça
        for y in range(5, 16):
            for x in range(3, 21):
                g[y][x] = 2
        for y in range(7, 12):
            for x in range(5, 19):
                g[y][x] = 3 # teclado preto
        for y in range(13, 15):
            for x in range(9, 15):
                g[y][x] = 4 # trackpad
        for x in range(6, 18):
            g[5][x] = 1 # dobradiça metálica
    else: # z=7..16: Tela aberta inclinada para trás (10 slices de tela sólida)
        sy = 5 - int((z - 6) * 0.5)
        # sy é a face traseira (tampa de alumínio)
        # sy+1 é a face frontal (display com IDE)
        # Ambos preenchidos para solidez total sem frestas ou listras!
        for x in range(3, 21):
            # Tampa traseira do laptop:
            g[sy][x] = 2
            # Face frontal:
            if z == 16 or x in (3, 20):
                g[sy+1][x] = 3 # moldura bezel preta
            elif z == 15: # Barra de título da janela com botões do SO
                if x in (5,): g[sy+1][x] = 8 # fechar vermelho
                elif x in (7,): g[sy+1][x] = 7 # minimizar amarelo
                elif x in (9,): g[sy+1][x] = 9 # maximizar verde
                elif x in range(11, 18): g[sy+1][x] = 4 # título da aba
                else: g[sy+1][x] = 3
            else: # z=7..14: Editor de código estilo VS Code / Catppuccin
                g[sy+1][x] = 5 # fundo escuro IDE
                if z == 14: # abas de arquivos
                    if x in range(4, 9): g[sy+1][x] = 4
                    elif x in range(10, 14): g[sy+1][x] = 6
                elif z == 13: # import { Cat } from 'purr'
                    if x in (5, 6): g[sy+1][x] = 8
                    elif x in (8, 9): g[sy+1][x] = 6
                    elif x in (11, 12): g[sy+1][x] = 8
                    elif x in range(14, 18): g[sy+1][x] = 7
                elif z == 12: # const cat = new Cat();
                    if x in (5, 6): g[sy+1][x] = 8
                    elif x in (8, 9, 10): g[sy+1][x] = 6
                    elif x in (12,): g[sy+1][x] = 7
                    elif x in range(14, 18): g[sy+1][x] = 9
                elif z == 11: # cat.sleep({ cozy: true });
                    if x in range(6, 10): g[sy+1][x] = 6
                    elif x in range(11, 15): g[sy+1][x] = 9
                    elif x in (16, 17): g[sy+1][x] = 7
                elif z == 10: # // cozy room session
                    if x in range(6, 18): g[sy+1][x] = 9
                elif z == 9: # function purr() {
                    if x in (5, 6, 7): g[sy+1][x] = 8
                    elif x in range(9, 13): g[sy+1][x] = 6
                elif z == 8: #   return 'meow ♥';
                    if x in range(7, 10): g[sy+1][x] = 8
                    elif x in range(12, 18): g[sy+1][x] = 7
                elif z == 7: # borda inferior do display
                    g[sy+1][x] = 3

        # Logo na tampa traseira (visível quando gira a câmera para trás!)
        if z in (11, 12):
            g[sy][11] = 1; g[sy][12] = 1
    lap_slices.append(g)

# 3. MESA DIGITALIZADORA (DRAWING TABLET COM CANETA, 22x16, 4 slices)
tab_w, tab_h = 22, 16
tab_slices = []
for z in range(4):
    g = make_grid(tab_w, tab_h, 0)
    if z == 0: # Base e sapatas emborrachadas
        for y in range(2, 14):
            for x in range(2, 16):
                g[y][x] = 1
        g[4][18] = 6; g[4][19] = 6; g[5][18] = 6; g[5][19] = 6 # suporte de caneta
    elif z == 1: # Corpo da tablet + canvas
        for y in range(2, 14):
            for x in range(2, 16):
                if x in (2, 3, 14, 15) or y in (2, 13):
                    g[y][x] = 1 # borda fina
                else:
                    g[y][x] = 2 # tela branca de desenho
        g[4][3] = 6; g[5][3] = 6; g[8][3] = 6; g[9][3] = 6 # express keys
        for y in range(5, 13):
            g[y][19] = 4 # caneta stylus
        g[4][19] = 5 # ponta da caneta
        g[12][19] = 6
    elif z == 2: # Arte desenhada na tela + botões
        for y in range(3, 13):
            for x in range(4, 14):
                g[y][x] = 2
        # Desenho do gatinho na tablet:
        g[6][8] = 3; g[6][10] = 3 # orelhinhas
        for x in range(7, 12):
            g[7][x] = 3; g[8][x] = 3
        g[8][8] = 1; g[8][10] = 1 # olhinhos
        for y in range(6, 12):
            g[y][19] = 4 # caneta
    elif z == 3: # Leve inclinação traseira
        for x in range(4, 14):
            g[2][x] = 1; g[3][x] = 1
    tab_slices.append(g)

# 4. LIVRINHOS DA MESA (Stack compacto de 3 livros, 16x16, 7 slices)
bk_w, bk_h = 16, 16
bk_slices = []
for z in range(7):
    g = make_grid(bk_w, bk_h, 0)
    if z < 2:
        for y in range(3, 13):
            for x in range(3, 14):
                if z == 1 and x > 4 and y > 3 and y < 12:
                    g[y][x] = 2
                else:
                    g[y][x] = 1
    elif z < 4:
        for y in range(4, 14):
            for x in range(4, 15):
                if z == 3 and x > 5 and y > 4 and y < 13:
                    g[y][x] = 2
                else:
                    g[y][x] = 3
    else:
        for y in range(3, 13):
            for x in range(3, 14):
                if z == 5 and x > 4 and y > 3 and y < 12:
                    g[y][x] = 2
                else:
                    g[y][x] = 4
        if z == 6:
            g[13][8] = 5; g[14][8] = 5
    bk_slices.append(g)

# 5. CANECA DE CAFÉ (10x10, 8 slices)
mug_w, mug_h = 10, 10
mug_slices = []
for z in range(8):
    g = make_grid(mug_w, mug_h, 0)
    if z < 4:
        for y in range(3, 8):
            for x in range(2, 7):
                g[y][x] = 1
        if z in (1, 2):
            g[5][7] = 1
        if z == 3:
            for y in range(4, 7):
                for x in range(3, 6):
                    g[y][x] = 3
    else:
        if z == 4: g[4][4] = 4; g[4][5] = 4
        elif z == 5: g[3][5] = 4; g[3][6] = 4
        elif z == 6: g[4][6] = 4
        elif z == 7: g[3][7] = 4
    mug_slices.append(g)

pack = {
    'desk': to_strings(desk_slices),
    'laptop': to_strings(lap_slices),
    'tablet': to_strings(tab_slices),
    'desk_books': to_strings(bk_slices),
    'mug': to_strings(mug_slices)
}

with open('C:/github/PixelArt/modular_desk_pack.json', 'w', encoding='utf-8') as f:
    json.dump(pack, f, indent=2)

print("SUCCESS: modular_desk_pack.json rebuilt with 64x34 desk!")
