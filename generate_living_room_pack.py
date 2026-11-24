import json

def make_grid(w, h, fill=0):
    return [[fill for _ in range(w)] for _ in range(h)]

def to_strings(slices):
    res = []
    for s in slices:
        res.append([''.join(str(v) for v in row) for row in s])
    return res

pack = {}

# ==============================================================================
# 1. SOFÁ ACONCHEGANTE (56x30, 16 slices)
# Paleta sugerida:
# 0: transparent
# 1: pernas madeira escura (#4A2E1B)
# 2: tecido base/sombra (#B45339)
# 3: tecido assento almofadado terracota acolhedor (#C8654B)
# 4: encosto/almofada highlight (#DC7A5F)
# 5: manta decorativa jogada (#F3EDE2)
# ==============================================================================
sofa_w, sofa_h = 56, 30
sofa_slices = []
for z in range(16):
    g = make_grid(sofa_w, sofa_h, 0)
    if z < 3: # Pernas de madeira escura e travessa inferior
        for lx, ly in [(4, 4), (sofa_w - 9, 4), (4, sofa_h - 9), (sofa_w - 9, sofa_h - 9)]:
            for dy in range(5):
                for dx in range(5):
                    g[ly + dy][lx + dx] = 1
        if z == 2: # Travessa de base
            for y in range(4, sofa_h - 4):
                for x in range(4, sofa_w - 4):
                    g[y][x] = 2
    elif z < 8: # Almofadão grosso de assento (macio e fofinho!)
        for y in range(3, sofa_h - 3):
            for x in range(3, sofa_w - 3):
                g[y][x] = 3
        # Manta decorativa jogada na lateral direita (estilo Pinterest / Cozy Home)
        for y in range(5, sofa_h - 5):
            for x in range(sofa_w - 18, sofa_w - 8):
                g[y][x] = 5
    elif z < 12: # Braços laterais (esq/dir) e base do encosto traseiro
        # Braço esquerdo (x=3..9, y=3..27)
        for y in range(3, sofa_h - 3):
            for x in range(3, 10):
                g[y][x] = 2 if x in (3, 9) else 4
        # Braço direito (x=46..52, y=3..27)
        for y in range(3, sofa_h - 3):
            for x in range(sofa_w - 10, sofa_w - 3):
                g[y][x] = 2 if x in (sofa_w - 10, sofa_w - 4) else 4
        # Encosto traseiro grosso
        for y in range(3, 11):
            for x in range(10, sofa_w - 10):
                g[y][x] = 3
        # Continuação da manta na frente do assento
        if z == 8:
            for y in range(sofa_h - 10, sofa_h - 4):
                for x in range(sofa_w - 17, sofa_w - 9):
                    g[y][x] = 5
    else: # z=12..15: Topo do encosto traseiro com almofadas fofas
        for y in range(4, 10):
            for x in range(10, sofa_w - 10):
                # Divisão sutil entre as duas almofadas do encosto
                if x == sofa_w // 2:
                    g[y][x] = 2
                else:
                    g[y][x] = 4 if z < 15 else 3
        # Topo arredondado dos braços em z=12
        if z == 12:
            for y in range(5, sofa_h - 5):
                for x in range(4, 9):
                    g[y][x] = 4
                for x in range(sofa_w - 9, sofa_w - 4):
                    g[y][x] = 4
    sofa_slices.append(g)

pack['sofa'] = to_strings(sofa_slices)

# ==============================================================================
# 2. MESINHA DE CENTRO (36x24, 10 slices)
# Paleta sugerida:
# 0: transparent
# 1: pernas madeira maciça (#532F16)
# 2: tampo carvalho maciço (#9E6740)
# 3: chanfro de borda (#B87E52)
# 4: vasinho suculenta verde (#2D6A4F)
# 5: plantinha folha clara (#52B788)
# 6: revista/livro aberto (#FDFBF7)
# ==============================================================================
table_w, table_h = 36, 24
table_slices = []
for z in range(10):
    g = make_grid(table_w, table_h, 0)
    if z < 6: # 4 Pernas cilíndricas de madeira torneada
        for lx, ly in [(4, 4), (table_w - 8, 4), (4, table_h - 8), (table_w - 8, table_h - 8)]:
            for dy in range(4):
                for dx in range(4):
                    g[ly + dy][lx + dx] = 1
    elif z < 8: # Tampo de carvalho maciço
        for y in range(2, table_h - 2):
            for x in range(2, table_w - 2):
                if x in (2, table_w - 3) or y in (2, table_h - 3):
                    g[y][x] = 3
                else:
                    g[y][x] = 2
    else: # Decorações em cima da mesinha (vasinho suculenta e livro)
        if z == 8:
            # Vasinho cerâmica
            for y in range(10, 14):
                for x in range(8, 12):
                    g[y][x] = 4
            # Livro de arte
            for y in range(8, 16):
                for x in range(20, 28):
                    g[y][x] = 6
        elif z == 9:
            # Folhinhas da suculenta
            for y in range(9, 15):
                for x in range(7, 13):
                    if (x, y) in [(8, 10), (11, 10), (8, 13), (11, 13), (9, 11), (10, 11), (9, 12), (10, 12)]:
                        g[y][x] = 5
            # Página do livro
            for y in range(9, 15):
                for x in range(21, 27):
                    g[y][x] = 6
    table_slices.append(g)

pack['coffee_table'] = to_strings(table_slices)

# ==============================================================================
# 3. RACK DE TV COM TV RETRÔ VINTAGE (52x22, 26 slices)
# Paleta sugerida:
# 0: transparent
# 1: madeira escura do rack (#4A2E1B)
# 2: carvalho do rack / prateleira (#8B5A2B)
# 3: chassi da TV retrô creme/bege (#DDD0BF)
# 4: tela da TV escura (#181825)
# 5: tela da TV acesa / canal animado (#38BDF8)
# 6: botões seletores e antena (#DE864A)
# 7: videogames / livros no nicho (#E76F51)
# ==============================================================================
rack_w, rack_h = 52, 22
rack_slices = []
for z in range(26):
    g = make_grid(rack_w, rack_h, 0)
    if z < 3: # 4 Pés modernos inclinados de madeira
        for lx, ly in [(4, 4), (rack_w - 8, 4), (4, rack_h - 8), (rack_w - 8, rack_h - 8)]:
            for dy in range(4):
                for dx in range(4):
                    g[ly + dy][lx + dx] = 1
    elif z < 9: # Corpo do móvel rack com nichos vazados e videogames
        for y in range(3, rack_h - 3):
            for x in range(3, rack_w - 3):
                # Laterais e divisória central
                if x in (3, 4, rack_w // 2, rack_w // 2 + 1, rack_w - 5, rack_w - 4) or y in (3, rack_h - 4):
                    g[y][x] = 1
                else:
                    g[y][x] = 2
        # Livros ou cartuchos no nicho esquerdo
        if z in (4, 5, 6):
            for y in range(5, rack_h - 5):
                for x in range(8, 14):
                    g[y][x] = 7
    elif z == 9: # Tampo superior espaçoso do rack
        for y in range(2, rack_h - 2):
            for x in range(2, rack_w - 2):
                g[y][x] = 2
    elif z < 11: # Base / pezinhos da TV retrô
        for y in range(7, 15):
            for x in range(rack_w // 2 - 10, rack_w // 2 + 10):
                g[y][x] = 1
    else: # z=11..25: TV Retrô de tubo estilizada com tela luminosa
        # Gabinete arredondado da TV
        for y in range(6, 16):
            for x in range(rack_w // 2 - 14, rack_w // 2 + 14):
                g[y][x] = 3
        # Tela da TV (z=13..23, frontal em y=14, 15)
        if 13 <= z <= 23:
            for y in (14, 15):
                for x in range(rack_w // 2 - 12, rack_w // 2 + 6):
                    g[y][x] = 5 if 14 <= z <= 21 else 4
            # Painel com 2 botões giratórios na direita
            for y in (14, 15):
                if z in (16, 20):
                    g[y][rack_w // 2 + 9] = 6
        # Duas antenas em V metálicas no topo (z=24, 25)
        if z >= 24:
            off = (z - 23) * 2
            g[10][rack_w // 2 - 4 - off] = 6
            g[10][rack_w // 2 + 4 + off] = 6

    rack_slices.append(g)

pack['tv_rack'] = to_strings(rack_slices)

# ==============================================================================
# 4. ESTANTE ALTA DE LIVROS & DECORAÇÃO (34x18, 30 slices)
# Paleta sugerida:
# 0: transparent
# 1: madeira maciça (#4A2E1B)
# 2: prateleiras carvalho (#8B5A2B)
# 3: livros lombadas coloridas (#E76F51)
# 4: livros azuis (#2A9D8F)
# 5: vasinho planta pendente (#52B788)
# 6: cristal decorativo (#F4A261)
# ==============================================================================
shelf_w, shelf_h = 34, 18
shelf_slices = []
for z in range(30):
    g = make_grid(shelf_w, shelf_h, 0)
    # 4 Colunas verticais e fundo estrutural
    for y in range(3, shelf_h - 3):
        for x in (3, 4, shelf_w - 5, shelf_w - 4):
            g[y][x] = 1
    for x in range(3, shelf_w - 3):
        g[3][x] = 1 # Fundo contra a parede

    # 4 Prateleiras horizontais (z=1, z=10, z=19, z=28)
    if z in (1, 10, 19, 28):
        for y in range(3, shelf_h - 3):
            for x in range(3, shelf_w - 3):
                g[y][x] = 2

    # Prateleira 1 (z=2..9): Coleção densa de livros enciclopédia
    if 2 <= z <= 8:
        for y in range(4, shelf_h - 4):
            for x in range(6, 16):
                g[y][x] = 3 if (x % 3 == 0) else 4
            for x in range(18, 26):
                g[y][x] = 3

    # Prateleira 2 (z=11..18): Vasinho com planta pendente caindo pela borda
    if 11 <= z <= 15:
        for y in range(5, 12):
            for x in range(8, 14):
                g[y][x] = 5
    if z == 10 or z == 9: # Ramos caindo
        g[shelf_h - 3][11] = 5
        g[shelf_h - 3][12] = 5

    # Prateleira 3 (z=20..27): Cristal reluzente e livros deitados
    if 20 <= z <= 24:
        # Livros deitados
        for y in range(5, 12):
            for x in range(6, 15):
                g[y][x] = 4
        # Cristal piramidal
        if z in (20, 21, 22):
            for y in range(6, 11):
                for x in range(20, 25):
                    g[y][x] = 6

    shelf_slices.append(g)

pack['bookshelf'] = to_strings(shelf_slices)

# Salva o arquivo de móveis da Sala de Estar
with open('C:/github/PixelArt/living_room_pack.json', 'w', encoding='utf-8') as f:
    json.dump(pack, f, indent=2)

print("SUCCESS: living_room_pack.json generated with Sofa, Coffee Table, TV Rack, and Bookshelf!")
