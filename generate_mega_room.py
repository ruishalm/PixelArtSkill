import json

# 1. Carrega dados de fatias
with open('C:/github/PixelArt/slices_v5.json', 'r', encoding='utf-8') as f:
    cat_slices_raw = json.load(f)

# Criando slices do corpo (fatias 0 e 1 sem as patas)
cat_body_slices = [ [list(r) for r in s] for s in cat_slices_raw ]
for z in (0, 1):
    for y in range(32):
        for x in range(32):
            cat_body_slices[z][y][x] = '0'

# Cute Anime Butt Mark (*) under the tail on slices 2, 3, 4 at y=8
cat_body_slices[2][8][15] = '4'
cat_body_slices[2][8][16] = '4'
cat_body_slices[3][8][14] = '4'
cat_body_slices[3][8][15] = '4'
cat_body_slices[3][8][16] = '4'
cat_body_slices[3][8][17] = '4'
cat_body_slices[4][8][14] = '4'
cat_body_slices[4][8][17] = '4'

cat_body_slices = [[''.join(r) for r in s] for s in cat_body_slices]

with open('C:/github/PixelArt/cat_belly_slices.json', 'r', encoding='utf-8') as f:
    cat_belly_slices_raw = json.load(f)
cat_belly_slices_json = json.dumps(cat_belly_slices_raw)

with open('C:/github/PixelArt/hats_pack.json', 'r', encoding='utf-8') as f:
    hats_pack = json.load(f)

witch_hat_slices = json.dumps(hats_pack['witch'])
crown_hat_slices = json.dumps(hats_pack['crown'])
beret_hat_slices = json.dumps(hats_pack['beret'])
flower_hat_slices = json.dumps(hats_pack['flower'])

# Criando slices de 1 patinha (4x4, 2 fatias com almofadinha rosa na base!)
cat_paw_slices = [
    [
        '1441',
        '4114',
        '1441',
        '1111'
    ],
    [
        '1111',
        '1111',
        '1111',
        '1111'
    ]
]

cat_body_slices_json = json.dumps(cat_body_slices)
cat_paw_slices_json = json.dumps(cat_paw_slices)

with open('C:/github/PixelArt/furniture_pack.json', 'r', encoding='utf-8') as f:
    furn_pack = json.load(f)

with open('C:/github/PixelArt/modular_desk_pack.json', 'r', encoding='utf-8') as f:
    mod_pack = json.load(f)

desk_slices = json.dumps(mod_pack['desk'])
laptop_slices = json.dumps(mod_pack['laptop'])
tablet_slices = json.dumps(mod_pack['tablet'])
desk_books_slices = json.dumps(mod_pack['desk_books'])
mug_slices = json.dumps(mod_pack['mug'])

plant_slices = json.dumps(furn_pack['plant'])
bed_slices = json.dumps(furn_pack['bed'])
tree_slices = json.dumps(furn_pack['cat_tree'])

with open('C:/github/PixelArt/living_room_pack.json', 'r', encoding='utf-8') as f:
    living_pack = json.load(f)

sofa_slices = json.dumps(living_pack['sofa'])
coffee_table_slices = json.dumps(living_pack['coffee_table'])
tv_rack_slices = json.dumps(living_pack['tv_rack'])
bookshelf_slices = json.dumps(living_pack['bookshelf'])
bs_enc_slices = json.dumps(living_pack['bs_encyclopedia'])
bs_plant_slices = json.dumps(living_pack['bs_plant'])
bs_crystal_slices = json.dumps(living_pack['bs_crystal'])
bs_stack_slices = json.dumps(living_pack['bs_stack'])
bs_trophy_slices = json.dumps(living_pack['bs_trophy'])

html_template = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Mega Quartinho 3D Modular - PurrModoro Diorama</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }
    body {
      background: #EAE2D5;
      color: #3B2A20;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      min-height: 100dvh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    :root {
      --paw-open: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Cellipse cx='14' cy='16' rx='9' ry='8' fill='rgba(0,0,0,0.18)'/%3E%3Cpath d='M7 14 C7 8, 21 8, 21 14 C21 21, 7 21, 7 14 Z' fill='%23FDFBF7' stroke='%233B2A20' stroke-width='1.5'/%3E%3Cpath d='M14 9 C18 9, 20 12, 19 16 C16 16, 14 12, 14 9 Z' fill='%23DE864A'/%3E%3Cpath d='M11 16 C11 14, 17 14, 17 16 C17 18.5, 11 18.5, 11 16 Z' fill='%23F497A4'/%3E%3Ccircle cx='8.5' cy='11.5' r='1.8' fill='%23F497A4'/%3E%3Ccircle cx='12' cy='8.5' r='2' fill='%23F497A4'/%3E%3Ccircle cx='16' cy='8.5' r='2' fill='%23F497A4'/%3E%3Ccircle cx='19.5' cy='11.5' r='1.8' fill='%23F497A4'/%3E%3C/svg%3E") 14 14, grab;
      --paw-grab: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Cellipse cx='14' cy='15' rx='8' ry='7' fill='rgba(0,0,0,0.22)'/%3E%3Ccircle cx='14' cy='14' r='7.5' fill='%23FDFBF7' stroke='%233B2A20' stroke-width='1.5'/%3E%3Cpath d='M14 8 C18 8, 20 11, 18 14 C15 14, 14 11, 14 8 Z' fill='%23DE864A'/%3E%3Ccircle cx='10' cy='12' r='1.8' fill='%23F497A4'/%3E%3Ccircle cx='14' cy='11' r='2' fill='%23F497A4'/%3E%3Ccircle cx='18' cy='12' r='1.8' fill='%23F497A4'/%3E%3Ccircle cx='14' cy='16' r='2.5' fill='%23F497A4'/%3E%3C/svg%3E") 14 14, grabbing;
    }
    .canvas-container {
      position: relative;
      width: min(94vw, calc(100vh - 120px));
      height: min(94vw, calc(100vh - 120px));
      max-width: 800px;
      max-height: 800px;
      aspect-ratio: 1 / 1;
    }
    #viewport {
      width: 100%;
      height: 100%;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      box-shadow: 0 30px 70px rgba(74, 46, 27, 0.22);
      border-radius: 28px;
      background: #F8F3EB;
      cursor: var(--paw-open);
      touch-action: none;
      display: block;
    }
    .btn-house-plan-square {
      position: absolute;
      top: 16px;
      right: 16px;
      width: 50px;
      height: 50px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 2.5px solid #4F46E5;
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1px;
      box-shadow: 0 6px 18px rgba(79, 70, 229, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.9);
      cursor: pointer;
      z-index: 50;
      transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .btn-house-plan-square:hover {
      transform: translateY(-2px) scale(1.08);
      background: #EEF2FF;
      box-shadow: 0 10px 24px rgba(79, 70, 229, 0.35);
      border-color: #4338CA;
    }
    .btn-house-plan-square:active {
      transform: translateY(1px) scale(0.95);
    }
    .btn-house-plan-square .plan-icon {
      font-size: 20px;
      line-height: 1;
    }
    .btn-house-plan-square .plan-txt {
      font-size: 8px;
      font-weight: 800;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      color: #4338CA;
      line-height: 1;
    }
    #viewport:active {
      cursor: var(--paw-grab);
    }
    #viewport.decor-mode {
      cursor: var(--paw-open);
    }
    #viewport.decor-hover {
      cursor: var(--paw-open);
    }
    #viewport.decor-dragging {
      cursor: var(--paw-grab);
    }
    .hud {
      position: absolute;
      bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 12px;
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(14px);
      padding: 10px 24px;
      border-radius: 40px;
      border: 1px solid rgba(59, 42, 32, 0.15);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
      align-items: center;
      font-size: 13px;
      font-weight: 500;
      max-width: 95vw;
    }
    .btn {
      background: #3B2A20;
      color: #FAF7F2;
      border: none;
      padding: 8px 18px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .btn:hover {
      background: #5A3F2F;
      transform: translateY(-1px);
    }
    .btn.active {
      background: #D87D4A;
      box-shadow: 0 4px 12px rgba(216, 125, 74, 0.35);
    }
    .btn-secondary {
      background: #EDE4D6;
      color: #3B2A20;
    }
    .btn-secondary:hover {
      background: #DDD0BF;
    }
    .btn-action {
      background: #2D6A4F;
      color: #FFFFFF;
    }
    .btn-action:hover {
      background: #1B4332;
    }
    .label {
      color: #6B4E3D;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    input[type=range] {
      accent-color: #D87D4A;
      cursor: pointer;
    }
    .badge {
      position: absolute;
      top: 16px;
      text-align: center;
    }
    .badge h1 {
      font-size: 22px;
      font-weight: 700;
      color: #3B2A20;
      letter-spacing: -0.5px;
    }
    .badge p {
      font-size: 13px;
      color: #8C6A54;
      margin-top: 2px;
    }
    .banner-info {
      position: absolute;
      top: 74px;
      background: rgba(255, 255, 255, 0.90);
      backdrop-filter: blur(10px);
      padding: 6px 18px;
      border-radius: 20px;
      font-size: 12px;
      color: #5A3F2F;
      border: 1px solid rgba(90, 63, 47, 0.15);
      display: flex;
      gap: 12px;
      align-items: center;
      box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    .banner-info b {
      color: #D87D4A;
    }
    .asset-drawer {
      position: absolute;
      top: 70px;
      right: 20px;
      width: 290px;
      max-height: calc(100vh - 110px);
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(16px);
      border-radius: 20px;
      border: 1px solid rgba(59, 42, 32, 0.15);
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 100;
      animation: fadeIn 0.2s ease-out;
    }
    .drawer-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(59, 42, 32, 0.1);
    }
    .drawer-header h3 {
      font-size: 15px;
      font-weight: 700;
      color: #3B2A20;
    }
    .btn-close {
      background: none;
      border: none;
      font-size: 18px;
      cursor: pointer;
      color: #8C6A54;
      line-height: 1;
      padding: 2px 6px;
    }
    .drawer-actions {
      display: flex;
      gap: 8px;
    }
    .btn-pill {
      flex: 1;
      padding: 6px 10px;
      font-size: 11px;
      border-radius: 12px;
      border: none;
      background: #EDE4D6;
      color: #3B2A20;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }
    .btn-pill:hover { background: #DDD0BF; }
    .btn-pill-alt { background: #FDE8E8; color: #9B1C1C; }
    .btn-pill-alt:hover { background: #F8D4D4; }
    .drawer-tabs {
      display: flex;
      gap: 6px;
      margin-bottom: 12px;
      background: #EDE6DA;
      padding: 4px;
      border-radius: 14px;
    }
    .drawer-tab {
      flex: 1;
      border: none;
      background: transparent;
      padding: 7px 8px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 700;
      color: #6B4E3D;
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;
    }
    .drawer-tab:hover {
      color: #3B2A20;
    }
    .drawer-tab.active {
      background: #FFFFFF;
      color: #D87D4A;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .asset-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      overflow-y: auto;
      max-height: 440px;
      padding-right: 4px;
    }
    .asset-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #FAF7F2;
      border: 1px solid rgba(59, 42, 32, 0.08);
      border-radius: 12px;
      padding: 7px 10px;
      font-size: 12px;
    }
    .asset-name {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      color: #3B2A20;
    }
    .btn-toggle {
      border: none;
      padding: 4px 10px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-toggle.on {
      background: #D87D4A;
      color: #FFFFFF;
    }
    .btn-toggle.off {
      background: #E5E0D8;
      color: #8C6A54;
    }

    /* --- MODAIS DO MURAL DE POST-ITS --- */
    .corkboard-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(40, 25, 15, 0.65);
      backdrop-filter: blur(4px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }
        /* --- MODAL DA PLANTA BAIXA (BLUEPRINT MODALZINHO) --- */
    .houseplan-frame {
      background: #FDFBF7;
      border: 6px solid #633A18;
      border-radius: 14px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.45);
      width: 92%;
      max-width: 500px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      user-select: none;
      animation: modalPop 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes modalPop {
      0% { transform: scale(0.92); opacity: 0; }
      100% { transform: scale(1); opacity: 1; }
    }
    .houseplan-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 2px dashed #E2D7C8;
    }
    .blueprint-container {
      background: #2563EB10;
      background-image: 
        linear-gradient(to right, rgba(37,99,235,0.12) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(37,99,235,0.12) 1px, transparent 1px);
      background-size: 16px 16px;
      border: 2px solid #93C5FD;
      border-radius: 10px;
      padding: 14px 10px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .blueprint-row {
      display: flex;
      gap: 8px;
      justify-content: space-between;
    }
    .blueprint-room {
      flex: 1;
      max-width: 155px;
      background: #FFFFFF;
      border: 2px solid #CBD5E1;
      border-radius: 8px;
      padding: 10px 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      cursor: pointer;
      position: relative;
      transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .blueprint-room:hover:not(.room-locked) {
      border-color: #3B82F6;
      transform: translateY(-2px);
      box-shadow: 0 6px 14px rgba(59,130,246,0.22);
    }
    .blueprint-room.active-room {
      border-color: #10B981;
      background: #F0FDF4;
      box-shadow: 0 0 0 2px #A7F3D0;
    }
    .blueprint-room.room-locked {
      opacity: 0.65;
      cursor: not-allowed;
      background: #F8FAFC;
      border-style: dashed;
    }
    .room-status-badge {
      font-size: 9px;
      font-weight: bold;
      color: #059669;
      background: #D1FAE5;
      padding: 2px 6px;
      border-radius: 10px;
      margin-bottom: 4px;
    }
    .locked-badge {
      color: #64748B;
      background: #E2E8F0;
    }
    .room-icon {
      font-size: 26px;
      margin: 2px 0;
    }
    .room-name {
      font-size: 12px;
      font-weight: bold;
      color: #1E293B;
    }
    .room-desc {
      font-size: 10px;
      color: #64748B;
      margin-top: 2px;
    }
    .room-pets {
      display: flex;
      gap: 3px;
      margin-top: 6px;
      font-size: 14px;
      background: #F1F5F9;
      padding: 2px 6px;
      border-radius: 12px;
    }

.corkboard-overlay.open {
      opacity: 1;
      pointer-events: auto;
    }
    .corkboard-frame {
      background: #D4A373;
      border: 14px solid #633A18;
      border-radius: 12px;
      box-shadow: 0 25px 60px rgba(0,0,0,0.45), inset 0 0 20px rgba(74, 46, 27, 0.4);
      width: 90%;
      max-width: 680px;
      height: 480px;
      display: flex;
      flex-direction: column;
      position: relative;
      user-select: none;
    }
    .corkboard-header {
      background: #532F16;
      color: #FAF7F2;
      padding: 10px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
      font-weight: 800;
      border-bottom: 3px solid #3B2219;
    }
    .corkboard-surface {
      flex: 1;
      padding: 20px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      grid-auto-rows: 125px;
      gap: 16px;
      overflow-y: auto;
      position: relative;
    }
    .postit-card {
      padding: 10px;
      box-shadow: 2px 4px 10px rgba(0,0,0,0.18);
      cursor: pointer;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      font-weight: bold;
      color: #3B2A20;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s, box-shadow 0.15s;
      position: relative;
      border-radius: 2px;
      overflow: hidden;
      word-break: break-word;
    }
    .postit-card:hover {
      transform: scale(1.05) translateY(-4px) !important;
      box-shadow: 4px 8px 16px rgba(0,0,0,0.25);
      z-index: 10;
    }
    .postit-pin {
      position: absolute;
      top: 3px;
      left: 50%;
      transform: translateX(-50%);
      width: 7px;
      height: 7px;
      background: #EF4444;
      border-radius: 50%;
      box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    /* Bloquinho de Post-it e Caneta no canto inferior direito */
    .corkboard-pad-container {
      position: absolute;
      bottom: 14px;
      right: 18px;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transition: transform 0.15s;
      z-index: 20;
    }
    .corkboard-pad-container:hover {
      transform: scale(1.1) translateY(-3px);
    }
    .corkboard-pad {
      width: 58px;
      height: 54px;
      background: #FEF08A;
      border: 1px solid #FDE047;
      box-shadow: 2px 3px 0 #EAB308, 3px 5px 8px rgba(0,0,0,0.25);
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
    }
    .corkboard-pen {
      position: absolute;
      right: -8px;
      top: -12px;
      font-size: 24px;
      transform: rotate(25deg);
      filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3));
    }
    .corkboard-pad-label {
      font-size: 10px;
      font-weight: 800;
      color: #FAF7F2;
      background: #532F16;
      padding: 2px 6px;
      border-radius: 8px;
      margin-top: 4px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Modal de Edição do Post-it */
    .note-editor-card {
      width: 320px;
      min-height: 320px;
      padding: 16px;
      box-shadow: 4px 12px 30px rgba(0,0,0,0.35);
      border-radius: 4px;
      display: flex;
      flex-direction: column;
      position: relative;
      user-select: none;
    }
    .note-editor-textarea {
      flex: 1;
      width: 100%;
      background: transparent;
      border: none;
      outline: none;
      resize: none;
      font-family: 'Courier New', monospace;
      font-size: 14px;
      font-weight: bold;
      color: #3B2A20;
      line-height: 1.4;
      margin-top: 14px;
    }
    .color-swatches {
      display: flex;
      gap: 8px;
      margin-top: 10px;
    }
    .color-dot {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      cursor: pointer;
      border: 2px solid transparent;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .color-dot.active {
      border-color: #3B2A20;
      transform: scale(1.15);
    }
    .note-editor-actions {
      display: flex;
      justify-content: space-between;
      margin-top: 12px;
      gap: 8px;
    }

    /* Ajustes Especiais para Telas Mobile */
    @media (max-width: 768px) {
      body {
        justify-content: center;
        padding: 0;
      }
      #viewport {
        width: min(96vw, calc(100dvh - 105px));
        height: min(96vw, calc(100dvh - 105px));
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(74, 46, 27, 0.16);
      }
      .badge {
        top: 6px;
        left: 0;
        right: 0;
        padding: 0 10px;
      }
      .badge h1 {
        font-size: 13px;
        font-weight: 800;
        letter-spacing: -0.3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .badge p {
        display: none;
      }
      .banner-info {
        top: 28px;
        left: 50%;
        transform: translateX(-50%);
        padding: 4px 10px;
        font-size: 10px;
        gap: 6px;
        max-width: 95vw;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .hud {
        bottom: 8px;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 16px);
        max-width: 100%;
        padding: 5px 8px;
        gap: 6px;
        border-radius: 24px;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        justify-content: flex-start;
      }
      .hud::-webkit-scrollbar {
        display: none;
      }
      .btn {
        padding: 6px 11px;
        font-size: 11px;
        border-radius: 14px;
        white-space: nowrap;
        flex-shrink: 0;
        gap: 4px;
      }
      .label {
        font-size: 11px;
        white-space: nowrap;
        flex-shrink: 0;
        gap: 4px;
        padding-right: 4px;
      }
      input[type=range] {
        width: 50px;
      }
      .asset-drawer {
        top: auto;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        max-height: 72vh;
        border-radius: 24px 24px 0 0;
        padding: 12px 14px 20px;
        box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.25);
        z-index: 250;
      }
      .asset-drawer::before {
        content: '';
        display: block;
        width: 38px;
        height: 4px;
        background: #D5C7B7;
        border-radius: 2px;
        margin: 0 auto 8px;
      }
      .corkboard-frame {
        width: 95%;
        max-height: 85vh;
        border-width: 8px;
      }
      .note-editor-card {
        width: 92%;
        max-width: 320px;
      }
    }
  </style>
</head>
<body>

  <div class="badge">
    <h1 id="roomTitle">🛏️ Mega Quartinho 3D (Tudo Modular & Movível!)</h1>
    <p id="roomSubtitle">Explore os cômodos da casinha com seus bichinhos através da Planta Baixa!</p>
  </div>

  <div id="bannerInfo" class="banner-info" style="display: none;">
    <span>🛠️ <b>Modo Decoração:</b> Arraste móveis, prateleira, quadros, relógio ou o gatinho!</span>
    <button id="btnRotateSelected" class="btn btn-action" style="padding: 4px 12px; font-size: 11px;">↻ Girar Item (Tecla R)</button>
  </div>


  <!-- Modal do Mural de Cortiça / Post-its -->
  <div id="corkboardModal" class="corkboard-overlay">
    <div class="corkboard-frame">
      <div class="corkboard-header">
        <span>📌 Mural de Lembretes & Ideias</span>
        <button id="btnCloseCorkboard" class="btn-close" style="color:#FAF7F2;">✕</button>
      </div>
      <div id="corkboardSurface" class="corkboard-surface">
        <!-- Post-its gerados dinamicamente via JS -->
      </div>
      <div id="corkboardPadBtn" class="corkboard-pad-container" title="Clique para escrever um novo post-it!">
        <div class="corkboard-pen">✏️</div>
        <div class="corkboard-pad">📝</div>
        <span class="corkboard-pad-label">+ Post-it</span>
      </div>
    </div>
  </div>

  <!-- Modal Editor de Post-it Individual -->
  <div id="noteEditorModal" class="corkboard-overlay">
    <div id="noteEditorCard" class="note-editor-card" style="background: #FEF08A;">
      <div class="postit-pin"></div>
      <textarea id="noteTextarea" class="note-editor-textarea" placeholder="Escreva seu recado ou lembrete aqui..."></textarea>
      
      <div class="color-swatches">
        <div class="color-dot active" data-color="#FEF08A" style="background:#FEF08A;"></div>
        <div class="color-dot" data-color="#FBCFE8" style="background:#FBCFE8;"></div>
        <div class="color-dot" data-color="#BBF7D0" style="background:#BBF7D0;"></div>
        <div class="color-dot" data-color="#BAE6FD" style="background:#BAE6FD;"></div>
        <div class="color-dot" data-color="#E9D5FF" style="background:#E9D5FF;"></div>
        <div class="color-dot" data-color="#FED7AA" style="background:#FED7AA;"></div>
      </div>

      <div class="note-editor-actions">
        <button id="btnDeleteNote" class="btn" style="background:#FEE2E2; color:#DC2626; border-color:#FCA5A5; display:none;">🗑️ Excluir</button>
        <div style="flex:1;"></div>
        <button id="btnCancelNote" class="btn btn-secondary">Cancelar</button>
        <button id="btnSaveNote" class="btn" style="background:#10B981; color:#fff; border-color:#059669;">💾 Salvar</button>
      </div>
    </div>
  </div>

  <!-- Modalzinho da Planta Baixa da Casa (Blueprint) -->
  <div id="housePlanModal" class="corkboard-overlay">
    <div class="houseplan-frame">
      <div class="houseplan-header">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:22px;">🗺️</span>
          <div>
            <div style="font-size:15px; font-weight:bold; color:#2D2118;">Planta Baixa da Casa</div>
            <div style="font-size:11px; color:#856B59;">Clique em um cômodo para explorar com seus pets</div>
          </div>
        </div>
        <button id="btnCloseHousePlan" class="btn-close" style="color:#2D2118;">✕</button>
      </div>

      <div class="blueprint-container">
        <!-- Linha 1: Cozinha, Sala de Estar Central, Jardim -->
        <div class="blueprint-row">
          <!-- Cozinha (Oeste) -->
          <div class="blueprint-room room-locked" id="roomCardKitchen" title="Em breve com fogãozinho e petiscos!">
            <div class="room-status-badge locked-badge">🔒 Em Breve</div>
            <div class="room-icon">🍽️</div>
            <div class="room-name">Cozinha</div>
            <div class="room-desc">Petiscos & Leite</div>
          </div>

          <!-- Sala de Estar (Centro / Hub) -->
          <div class="blueprint-room" id="roomCardLiving">
            <div class="room-status-badge" id="badgeLiving" style="display:none;">📍 Você está aqui</div>
            <div class="room-icon">🛋️</div>
            <div class="room-name">Sala de Estar</div>
            <div class="room-desc">Sofá, TV & Jardim</div>
            <div class="room-pets" id="petsLiving"></div>
          </div>

          <!-- Jardim (Leste) -->
          <div class="blueprint-room room-locked" id="roomCardGarden" title="Em breve com flores e banho de sol!">
            <div class="room-status-badge locked-badge">🔒 Em Breve</div>
            <div class="room-icon">🌳</div>
            <div class="room-name">Jardim</div>
            <div class="room-desc">Flores & Sol</div>
          </div>
        </div>

        <!-- Linha 2: Quarto (Sul, conectado à Sala) -->
        <div class="blueprint-row" style="justify-content: center;">
          <div class="blueprint-room active-room" id="roomCardBedroom">
            <div class="room-status-badge" id="badgeBedroom">📍 Você está aqui</div>
            <div class="room-icon">🛏️</div>
            <div class="room-name">Quarto</div>
            <div class="room-desc">Mesa & Caminha</div>
            <div class="room-pets" id="petsBedroom">🐱 🐔 🐥</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Overlay de transição suave entre cômodos -->
  <div id="roomFadeOverlay" style="position:fixed; top:0; left:0; width:100vw; height:100vh; background:#1A1412; opacity:0; pointer-events:none; transition:opacity 0.28s ease; z-index:9999;"></div>

  <!-- Catálogo de Assets Drawer -->
  <div id="assetDrawer" class="asset-drawer" style="display: none;">
    <div class="drawer-header">
      <h3>📦 Catálogo de Assets</h3>
      <button id="btnCloseDrawer" class="btn-close">✕</button>
    </div>
    <div class="drawer-tabs">
      <button class="drawer-tab active" data-cat="furniture">🛋️ Móveis</button>
      <button class="drawer-tab" data-cat="decor">🧸 Objetos</button>
      <button class="drawer-tab" data-cat="pets">🐾 Pets</button>
      <button class="drawer-tab" data-cat="hats">🎩 Chapéus</button>
    </div>
    <div id="drawerActions" class="drawer-actions">
      <button id="btnShowAll" class="btn-pill">Mostrar Todos</button>
      <button id="btnHideAll" class="btn-pill btn-pill-alt">Limpar Sala</button>
    </div>
    <div id="assetList" class="asset-list">
      <!-- Gerado dinamicamente em JS -->
    </div>
  </div>

  <div class="canvas-container">
    <canvas id="viewport" width="800" height="800"></canvas>
    <button id="btnHousePlan" class="btn-house-plan-square" title="Planta Baixa da Casinha">
      <span class="plan-icon">🗺️</span>
      <span class="plan-txt">Planta</span>
    </button>
  </div>

  <div class="hud">
    <button id="btnCatalog" class="btn btn-secondary">📦 Catálogo</button>
    <button id="btnDecorMode" class="btn btn-secondary">🛠️ Mover Itens</button>
    <button id="btnRotateMob" class="btn btn-secondary" style="display: none;">↻ Girar (R)</button>
    <button id="btnAutoSpin" class="btn active">🔄 Giro Auto</button>
    <button id="btnHat" class="btn btn-secondary">🎩 Chapéu: Nenhum</button>
    <button id="btnPosture" class="btn btn-secondary">🐾 Modo: Auto</button>
    <button id="btnPet" class="btn btn-secondary">💕 Carinho</button>
    <div class="label">
      <span>Inclinação:</span>
      <input type="range" id="squashSlider" min="0.60" max="0.85" step="0.01" value="0.72">
    </div>
  </div>

  <script>
    const canvas = document.getElementById('viewport');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    // Buffer de baixa resolução amplo
    const LOW_W = 440;
    const LOW_H = 440;
    const lowCanvas = document.createElement('canvas');
    lowCanvas.width = LOW_W;
    lowCanvas.height = LOW_H;
    const lowCtx = lowCanvas.getContext('2d');
    lowCtx.imageSmoothingEnabled = false;

    // Dimensões do quarto gigante (dobrado: raio 140 = 280x280 de chão útil)
    const ROOM_R = 140;
    const WALL_H = 100;

    // Estado da câmera
    let turn = -Math.PI * 0.25;
    let targetTurn = -Math.PI * 0.25;
    let squash = 0.72;
    let autoSpin = false;
    let hearts = [];

    // Estado de Decoração / Drag & Drop
    let isDecorMode = false;
    let selectedItem = null;
    let hoveredItem = null;
    let isDraggingItem = false;
    let dragStartPos = { sx: 0, sy: 0 };
    let itemStartPos = { x: 0, y: 0, liftZ: 0 };
    let dragOffset = { x: 0, y: 0 };

    // Nuvem animada na janela
    let cloudAnimX = 0;

    // Paleta de Cores PurrModoro
    const P = {
      bg: '#F8F3EB',
      woodLight: '#E8C596',
      woodMid: '#D4A373',
      woodDark: '#B88252',
      plankLine: '#A57347',
      baseboard: '#7A4926',
      wallInner: '#F5ECE1',
      wallTrim: '#C8B7A1',
      windowFrame: '#FFFFFF',
      windowCurtain: '#E8A598',
      windowSky: '#A2CBE8',
      shelfWood: '#9E6740',
      outline: '#3B2219'
    };

    // Helper genérico para compilar dados de fatias para um Canvas Image Sheet
    function createSliceSheet(slicesData, palette, w, h) {
      const count = slicesData.length;
      const sheet = document.createElement('canvas');
      sheet.width = w * count;
      sheet.height = h;
      const sCtx = sheet.getContext('2d');
      sCtx.imageSmoothingEnabled = false;

      for (let z = 0; z < count; z++) {
        const offX = z * w;
        const rows = slicesData[z];
        for (let y = 0; y < h; y++) {
          const row = rows[y];
          for (let x = 0; x < w; x++) {
            const val = parseInt(row[x], 10);
            if (val > 0 && val < palette.length) {
              sCtx.fillStyle = palette[val];
              sCtx.fillRect(offX + x, y, 1, 1);
            }
          }
        }
      }
      return { sheet, count, w, h };
    }

    // 1. GATINHO 3D ARTICULADO (Corpo 16 slices + 4 Patinhas 4x4 com almofadinhas)
    // 6 PELAGENS DO GATINHO (Skins Personalizadas)
    const CAT_SKINS = {
      calico: {
        id: 'calico', name: 'Mochi (Calico Original)', icon: '🐱', desc: 'Pelagem tricolor clássica (laranja, branco e preto)',
        pal: ['rgba(0,0,0,0)', '#FDFBF7', '#DE864A', '#3B2219', '#F2A2AB', '#FFFFFF', '#B85820', '#E5E0D8']
      },
      black: {
        id: 'black', name: 'Kuro (Gato Preto)', icon: '🐈‍⬛', desc: 'Preto ônix brilhante com olhos dourados brilhantes',
        pal: ['rgba(0,0,0,0)', '#1E293B', '#334155', '#F59E0B', '#F472B6', '#FEF08A', '#0F172A', '#1E293B']
      },
      tuxedo: {
        id: 'tuxedo', name: 'Felix (Frajola)', icon: '🎩', desc: 'Preto e branco estilo smoking elegante com botinhas brancas',
        pal: ['rgba(0,0,0,0)', '#FFFFFF', '#1E293B', '#1E293B', '#F472B6', '#FFFFFF', '#0F172A', '#CBD5E1']
      },
      orange: {
        id: 'orange', name: 'Cheddar (Tabby Laranja)', icon: '🍊', desc: 'Gatinho ruivo tigrado e muito esfomeado',
        pal: ['rgba(0,0,0,0)', '#FED7AA', '#EA580C', '#3B2219', '#F472B6', '#FFFFFF', '#C2410C', '#FDBA74']
      },
      siamese: {
        id: 'siamese', name: 'Luna (Siamês)', icon: '☕', desc: 'Corpo creme com pontas de chocolate e olhos azuis safira',
        pal: ['rgba(0,0,0,0)', '#FAF5EE', '#5C4033', '#0EA5E9', '#F472B6', '#FFFFFF', '#3E2723', '#EADBCA']
      },
      gray: {
        id: 'gray', name: 'Misty (Cinza Chumbo)', icon: '☁️', desc: 'Pelagem cinza prateada aveludada com olhos dourados',
        pal: ['rgba(0,0,0,0)', '#94A3B8', '#64748B', '#F59E0B', '#F472B6', '#FFFFFF', '#475569', '#CBD5E1']
      }
    };

    let currentCatSkin = 'calico';
    const catSkinModels = {};
    for (const [key, skin] of Object.entries(CAT_SKINS)) {
      catSkinModels[key] = {
        body: createSliceSheet(__CAT_BODY_SLICES__, skin.pal, 32, 32),
        paw: createSliceSheet(__CAT_PAW_SLICES__, skin.pal, 4, 4),
        belly: createSliceSheet(__CAT_BELLY_SLICES__, skin.pal, 32, 32)
      };
    }

    const catPal = CAT_SKINS.calico.pal;
    const catBodyModel = catSkinModels.calico.body;
    const catPawModel = catSkinModels.calico.paw;
    const catBellyModel = catSkinModels.calico.belly;

    // CHAPÉUZINHOS PURRMODORO
    const HATS = {
      witch: createSliceSheet(__WITCH_HAT_SLICES__, ['rgba(0,0,0,0)', '#221533', '#E5A93C', '#38244F'], 16, 16),
      crown: createSliceSheet(__CROWN_HAT_SLICES__, ['rgba(0,0,0,0)', '#F4B846', '#FFD166', '#E63946'], 12, 12),
      beret: createSliceSheet(__BERET_HAT_SLICES__, ['rgba(0,0,0,0)', '#5E1428', '#B82D52', '#3D0C1A'], 14, 14),
      flower: createSliceSheet(__FLOWER_HAT_SLICES__, ['rgba(0,0,0,0)', '#FFB7C5', '#FFD166'], 10, 10),
    };

    // 2. MESA DE ESTUDO AMPLIADA (15 slices, 80x36)
    const deskPal = [
      'rgba(0,0,0,0)',
      '#633A18', // 1: perna madeira escura
      '#9E6740', // 2: tampo carvalho maciço
      '#B87E52'  // 3: chanfro de borda
    ];
    const deskModel = createSliceSheet(__DESK_SLICES__, deskPal, 80, 36);

    // 3. NOTEBOOK NO SUPORTE ERGONÔMICO (17 slices, 24x20)
    const laptopPal = [
      'rgba(0,0,0,0)',
      '#94A3B8', // 1: suporte metálico prata & logo traseiro
      '#1E293B', // 2: chassi laptop grafite (tampa e base)
      '#0F172A', // 3: bezel moldura preta e teclado
      '#475569', // 4: trackpad e barra de título
      '#181825', // 5: fundo escuro da IDE (Catppuccin / VS Code)
      '#38BDF8', // 6: sintaxe ciano brilhante
      '#F59E0B', // 7: sintaxe âmbar / amarelo dourado
      '#F43F5E', // 8: sintaxe rosa coral / botão fechar
      '#10B981'  // 9: sintaxe verde esmeralda / comentários
    ];
    const laptopModel = createSliceSheet(__LAPTOP_SLICES__, laptopPal, 24, 20);

    // 4. MESA DIGITALIZADORA COM CANETA STYLUS E SKETCH (4 slices, 22x16)
    const tabletPal = [
      'rgba(0,0,0,0)',
      '#1E293B', // 1: carcaça fina grafite
      '#FAF7F2', // 2: canvas tela branca
      '#DE864A', // 3: rascunho de gatinho na tela
      '#475569', // 4: caneta stylus
      '#38BDF8', // 5: ponta da caneta
      '#0F172A'  // 6: express keys e suporte donut da caneta
    ];
    const tabletModel = createSliceSheet(__TABLET_SLICES__, tabletPal, 22, 16);

    // 5. LIVRINHOS EMPILHADOS DA MESA (7 slices, 16x16)
    const deskBooksPal = [
      'rgba(0,0,0,0)',
      '#831843', // 1: livro inferior vinho
      '#FAF7F2', // 2: páginas
      '#0F766E', // 3: livro médio turquesa
      '#D97706', // 4: livro superior dourado
      '#2563EB'  // 5: fita azul marcadora
    ];
    const deskBooksModel = createSliceSheet(__DESK_BOOKS_SLICES__, deskBooksPal, 16, 16);

    // 6. CANECA DE CAFÉ COM VAPOR (8 slices, 10x10)
    const mugPal = [
      'rgba(0,0,0,0)',
      '#FAF7F2', // 1: cerâmica branca
      '#E2E8F0', // 2: sombra cerâmica
      '#4A2A18', // 3: café expresso
      '#CBD5E1'  // 4: vapor
    ];
    const mugModel = createSliceSheet(__MUG_SLICES__, mugPal, 10, 10);

    // 7. VASO DE PLANTA MONSTERA (16 slices)
    const plantPal = ['rgba(0,0,0,0)', '#C26A45', '#4A2E1B', '#2D5A27', '#4D8A48'];
    const plantModel = createSliceSheet(__PLANT_SLICES__, plantPal, 20, 20);

    // 8. CAMINHA NUVEM AZUL (8 slices)
    const bedPal = ['rgba(0,0,0,0)', '#385D78', '#4D7594', '#E4EFF5'];
    const bedModel = createSliceSheet(__BED_SLICES__, bedPal, 32, 32);

    // 9. TORRE DE GATO COM SISAL E CESTINHA (28 slices)
    const treePal = ['rgba(0,0,0,0)', '#7E6047', '#D9C3A3', '#C29175'];
    const treeModel = createSliceSheet(__TREE_SLICES__, treePal, 28, 28);

    // MÓVEIS DA SALA DE ESTAR (SPRITE STACKING SLICES)
    const sofaPal = ['rgba(0,0,0,0)', '#4A2E1B', '#B45339', '#C8654B', '#DC7A5F', '#F3EDE2'];
    const sofaModel = createSliceSheet(__SOFA_SLICES__, sofaPal, 56, 30);

    const coffeeTablePal = ['rgba(0,0,0,0)', '#532F16', '#9E6740', '#B87E52', '#2D6A4F', '#52B788', '#FDFBF7'];
    const coffeeTableModel = createSliceSheet(__COFFEE_TABLE_SLICES__, coffeeTablePal, 36, 24);

    const tvRackPal = ['rgba(0,0,0,0)', '#4A2E1B', '#8B5A2B', '#DDD0BF', '#181825', '#38BDF8', '#DE864A', '#E76F51'];
    const tvRackModel = createSliceSheet(__TV_RACK_SLICES__, tvRackPal, 52, 22);

    const bookshelfPal = ['rgba(0,0,0,0)', '#4A2E1B', '#8B5A2B', '#351E10', '#A26C38'];
    const bookshelfModel = createSliceSheet(__BOOKSHELF_SLICES__, bookshelfPal, 34, 18);

    const bsEncPal = ['rgba(0,0,0,0)', '#FAF7F2', '#9B2C2C', '#1D4ED8', '#15803D', '#EAB308'];
    const bsEncModel = createSliceSheet(__BS_ENC_SLICES__, bsEncPal, 16, 10);

    const bsPlantPal = ['rgba(0,0,0,0)', '#C2410C', '#3B2219', '#22C55E', '#86EFAC', '#15803D'];
    const bsPlantModel = createSliceSheet(__BS_PLANT_SLICES__, bsPlantPal, 12, 12);

    const bsCrystalPal = ['rgba(0,0,0,0)', '#475569', '#7E22CE', '#A855F7', '#FAF5FF'];
    const bsCrystalModel = createSliceSheet(__BS_CRYSTAL_SLICES__, bsCrystalPal, 10, 10);

    const bsStackPal = ['rgba(0,0,0,0)', '#FAF7F2', '#9A3412', '#1E3A8A', '#F59E0B'];
    const bsStackModel = createSliceSheet(__BS_STACK_SLICES__, bsStackPal, 14, 12);

    const bsTrophyPal = ['rgba(0,0,0,0)', '#4A2E1B', '#B45309', '#F59E0B', '#FDE047'];
    const bsTrophyModel = createSliceSheet(__BS_TROPHY_SLICES__, bsTrophyPal, 10, 10);

    // 10. GALINHA COCORICÓ 3D (16 slices)
    const __CHICKEN_SLICES__ = [[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 0, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 3, 3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 3, 3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 3, 3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 2, 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 2, 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 2, 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 4, 4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 4, 4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 4, 4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 4, 6, 6, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 4, 6, 6, 7, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 4, 6, 6, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 8, 9, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 6, 6, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 6, 6, 6, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 6, 6, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 8, 9, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 4, 5, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 4, 5, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 0, 4, 4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]];
    const chickenPal = ['rgba(0,0,0,0)', '#FFFFFF', '#F1F5F9', '#CBD5E1', '#EF4444', '#B91C1C', '#F59E0B', '#D97706', '#0F172A', '#FFFFFF'];
    const chickenModel = createSliceSheet(__CHICKEN_SLICES__, chickenPal, 24, 24);
    // CANVASES SEPARADOS DA GALINHA POPÓ (Patas, Corpo e Cabeça Articulados)
    // MODELO DA GALINHA POPÓ E DO PINTINHO PIU (Bolinha Amarela Sem Crista)
    function createPartCanvas(sliceGrid, filterFn, pal, size = 24) {
      const sc = document.createElement('canvas');
      sc.width = size; sc.height = size;
      const sctx = sc.getContext('2d');
      sctx.imageSmoothingEnabled = false;
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          const cIdx = sliceGrid[y] ? (sliceGrid[y][x] || 0) : 0;
          if (cIdx > 0) {
            if (filterFn && !filterFn(x, y)) continue;
            sctx.fillStyle = pal[cIdx] || '#FFFFFF';
            sctx.fillRect(x, y, 1, 1);
          }
        }
      }
      return sc;
    }

    // Paleta Amarela para o Pintinho Piu (Pintinho Amarelinho)
    const chickPal = ['rgba(0,0,0,0)', '#FEF08A', '#FACC15', '#EAB308', '#CA8A04', '#FB923C', '#EA580C', '#0F172A', '#FFFFFF', '#F472B6'];
    const __CHICK_SLICES__ = [[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 2, 3, 3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 2, 3, 3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0], [0, 0, 2, 0, 3, 3, 3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0], [0, 0, 2, 0, 3, 3, 3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0], [0, 0, 0, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0], [0, 0, 2, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0], [0, 0, 2, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0], [0, 0, 0, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 3, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 3, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 5, 6, 0, 0], [0, 0, 0, 3, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 5, 6, 0, 0], [0, 0, 0, 3, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 3, 1, 9, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 7, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 3, 2, 1, 1, 1, 1, 1, 5, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 3, 2, 1, 1, 1, 1, 1, 5, 0, 0, 0], [0, 0, 0, 0, 3, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 7, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 3, 1, 9, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 1, 1, 1, 7, 8, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 3, 3, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 1, 1, 1, 7, 8, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 3, 3, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]];

    const chickenLegL = [];
    const chickenLegR = [];
    for (let i = 0; i <= 3; i++) {
      chickenLegL.push(createPartCanvas(__CHICKEN_SLICES__[i], (x, y) => y < 12, chickenPal, 24));
      chickenLegR.push(createPartCanvas(__CHICKEN_SLICES__[i], (x, y) => y >= 12, chickenPal, 24));
    }
    const chickenUpper = [];
    for (let i = 4; i < __CHICKEN_SLICES__.length; i++) {
      chickenUpper.push(createPartCanvas(__CHICKEN_SLICES__[i], null, chickenPal, 24));
    }

    // Partes dedicadas do Pintinho Piu: 18x18, sem crista, pura fofura redonda
    const chickLegL = [];
    const chickLegR = [];
    for (let i = 0; i <= 1; i++) {
      chickLegL.push(createPartCanvas(__CHICK_SLICES__[i], (x, y) => y < 9, chickPal, 18));
      chickLegR.push(createPartCanvas(__CHICK_SLICES__[i], (x, y) => y >= 9, chickPal, 18));
    }
    const chickUpper = [];
    for (let i = 2; i < __CHICK_SLICES__.length; i++) {
      chickUpper.push(createPartCanvas(__CHICK_SLICES__[i], null, chickPal, 18));
    }


    // --- DEFINIÇÕES DOS CÔMODOS & ENTIDADES PERSISTENTES ---
    let currentRoomId = 'bedroom';

    // 1. Pets Persistentes (Mochi, Popó e Pintinho que migram juntos!)
    const PETS = [
      { id: 'cat',           name: 'Gatinho Mochi',        icon: '🐱', category: 'decor',     model: catBodyModel,   x: 0,   y: 0,   liftZ: 0,  selfAngle: 0,   scale: 1.5,  radius: 20, isCat: true, visible: true, state: 'idle', stateTimer: 180, isWalking: false, walkCycle: 0, idleTimer: 0, hat: 'none', posture: 'sit', forcedPosture: null, speech: null, bellyTimer: 0 },
      { id: 'chicken',       name: 'Galinha Popó',         icon: '🐔', category: 'pets',      model: chickenModel,   x: -35, y: 35,  liftZ: 0,  selfAngle: 0.6, scale: 1.35, radius: 18, isChicken: true, visible: true, state: 'idle', stateTimer: 120, isWalking: false, walkCycle: 0, animTime: 0, targetX: -35, targetY: 35 },
      { id: 'chick',         name: 'Pintinho Piu',         icon: '🐥', category: 'pets',      model: chickenModel,   x: -20, y: 48,  liftZ: 0,  selfAngle: 0.2, scale: 0.85, radius: 12, isChicken: true, visible: true, state: 'idle', stateTimer: 80,  isWalking: false, walkCycle: 0, animTime: 0, targetX: -20, targetY: 48 }
    ];

    // 2. Móveis do Quarto
    const BEDROOM_ITEMS = [
      { id: 'laptop',        name: 'Note no Suporte',      icon: '💻', category: 'decor',     model: laptopModel,    x: 55,  y: -74, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 18, isProp: true, surface: 'desk', offX: 0, offY: -9, visible: true },
      { id: 'tablet',        name: 'Tablet de Desenho',    icon: '🎨', category: 'decor',     model: tabletModel,    x: 32,  y: -62, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 16, isProp: true, surface: 'desk', offX: -23, offY: 3, visible: true },
      { id: 'desk_books',    name: 'Livros Empilhados',    icon: '📚', category: 'decor',     model: deskBooksModel, x: 80,  y: -58, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 14, isProp: true, surface: 'desk', offX: 25, offY: 7, visible: true },
      { id: 'mug',           name: 'Caneca de Café',       icon: '☕', category: 'decor',     model: mugModel,       x: 78,  y: -74, liftZ: 21, selfAngle: 0,   scale: 1.45, radius: 10, isProp: true, surface: 'desk', offX: 23, offY: -9, visible: true },
      { id: 'shelf_books',   name: 'Livros em Pé',         icon: '📖', category: 'decor',     x: -ROOM_R + 9, y: -28, liftZ: 61.5, radius: 15, isProp: true, surface: 'shelf', offY: -18, visible: true },
      { id: 'shelf_plant',   name: 'Vasinho de Suculenta', icon: '🪴', category: 'decor',     x: -ROOM_R + 9, y: -10, liftZ: 61.5, radius: 14, isProp: true, surface: 'shelf', offY: 0,   visible: true },
      { id: 'shelf_crystal', name: 'Cristal de Quartzo',   icon: '💎', category: 'decor',     x: -ROOM_R + 9, y: 8,   liftZ: 61.5, radius: 14, isProp: true, surface: 'shelf', offY: 18,  visible: true },
      { id: 'clock',         name: 'Relógio de Parede',    icon: '⏰', category: 'decor',     isWallItem: true, wall: 'west', x: -ROOM_R, y: 0, liftZ: 85, radius: 16, visible: true },
      { id: 'corkboard',     name: 'Mural de Post-its',    icon: '📌', category: 'decor',     isWallItem: true, wall: 'east', x: ROOM_R, y: -10, liftZ: 65, radius: 36, visible: true, isCorkboard: true },
      { id: 'plant',         name: 'Planta Monstera',      icon: '🌿', category: 'decor',     model: plantModel,     x: 85,  y: 65,  liftZ: 0,  selfAngle: 0.4, scale: 1.4,  radius: 20, visible: true },
      { id: 'door',          name: 'Porta para a Sala',    icon: '🚪', category: 'furniture', isWallItem: true, isDoor: true, wall: 'east', x: ROOM_R, y: 60, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'living' },
      { id: 'desk',          name: 'Mesa de Estudo',       icon: '🪵', category: 'furniture', model: deskModel,      x: 55,  y: -65, liftZ: 0,  selfAngle: 0,   scale: 1.45, radius: 46, isDesk: true, visible: true },
      { id: 'shelf',         name: 'Prateleira de Madeira',icon: '🪵', category: 'furniture', isWallItem: true, wall: 'west', x: -ROOM_R, y: -10, liftZ: 58, length: 68, radius: 24, visible: true },
      { id: 'bed',           name: 'Caminha Nuvem',        icon: '☁️', category: 'furniture', model: bedModel,       x: -75, y: -70, liftZ: 0,  selfAngle: 0,   scale: 1.4,  radius: 25, visible: true },
      { id: 'tree',          name: 'Torre de Gato',        icon: '🐾', category: 'furniture', model: treeModel,      x: -80, y: 50,  liftZ: 0,  selfAngle: 0,   scale: 1.4,  radius: 24, visible: true }
    ];

    // 3. Móveis da Sala de Estar Central (Hub com 3 portas, Sofá, Mesinha, Rack com TV Retrô, Estante)
    const LIVING_ITEMS = [
      // 3 Portas da Sala em paredes 100% VISÍVEIS (Parede Norte e Parede Leste)!
      { id: 'door_kitchen',  name: 'Porta pra Cozinha',    icon: '🍽️', category: 'furniture', isWallItem: true, isDoor: true, wall: 'north', x: -80, y: -ROOM_R, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'kitchen' },
      { id: 'door_bedroom',  name: 'Porta pro Quarto',     icon: '🛏️', category: 'furniture', isWallItem: true, isDoor: true, wall: 'north', x: 75,  y: -ROOM_R, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'bedroom' },
      { id: 'door_garden',   name: 'Porta pro Jardim',     icon: '🌳', category: 'furniture', isWallItem: true, isDoor: true, wall: 'east',  x: ROOM_R, y: 55, liftZ: 0, width: 28, height: 76, radius: 24, visible: true, isOpen: false, targetRoom: 'garden' },

      // MÓVEIS NAS PAREDES VAZIAS:
      // Sofá encostado na Parede Vazia (Oeste) virado para dentro da sala
      { id: 'sofa',          name: 'Sofá Aconchegante',    icon: '🛋️', category: 'furniture', model: sofaModel,      x: -105,y: 0,   liftZ: 0,  selfAngle: -Math.PI / 2, scale: 1.45, radius: 42, isSofa: true, visible: true },
      // Estante Alta encostada na Parede Vazia (Sul) com 3 prateleiras limpas
      { id: 'bookshelf',     name: 'Estante Alta de Livros',icon: '📚', category: 'furniture', model: bookshelfModel, x: -20, y: 112, liftZ: 0,  selfAngle: Math.PI,      scale: 1.45, radius: 28, isBookshelf: true, visible: true },

      // ACESSÓRIOS MODULARES E MÓVEIS DA ESTANTE (Arrastáveis para qualquer prateleira!)
      { id: 'bs_enc',        name: 'Coleção de Enciclopédias', icon: '📖', category: 'decor', model: bsEncModel,     x: -28, y: 112, liftZ: 2.5,  selfAngle: Math.PI, scale: 1.4, radius: 14, isProp: true, surface: 'bookshelf', tier: 1, offX: -8, offY: 0, visible: true },
      { id: 'bs_stack',      name: 'Livros de Couro Clássicos',icon: '📚', category: 'decor', model: bsStackModel,   x: -12, y: 112, liftZ: 2.5,  selfAngle: Math.PI, scale: 1.4, radius: 12, isProp: true, surface: 'bookshelf', tier: 1, offX: 8,  offY: 0, visible: true },
      { id: 'bs_plant',      name: 'Vasinho de Hera Pendente', icon: '🪴', category: 'decor', model: bsPlantModel,   x: -28, y: 112, liftZ: 15.5, selfAngle: Math.PI, scale: 1.4, radius: 12, isProp: true, surface: 'bookshelf', tier: 2, offX: -8, offY: 0, visible: true },
      { id: 'bs_trophy',     name: 'Troféu PurrModoro Ouro',   icon: '🏆', category: 'decor', model: bsTrophyModel,  x: -12, y: 112, liftZ: 15.5, selfAngle: Math.PI, scale: 1.4, radius: 10, isProp: true, surface: 'bookshelf', tier: 2, offX: 8,  offY: 0, visible: true },
      { id: 'bs_crystal',    name: 'Geodo de Ametista',        icon: '💎', category: 'decor', model: bsCrystalModel,x: -20, y: 112, liftZ: 28.5, selfAngle: Math.PI, scale: 1.4, radius: 10, isProp: true, surface: 'bookshelf', tier: 3, offX: 0,  offY: 0, visible: true },
      // Planta Monstera no cantinho entre as duas paredes vazias
      { id: 'plant_living',  name: 'Planta Monstera',      icon: '🌿', category: 'decor',     model: plantModel,     x: -112,y: 105, liftZ: 0,  selfAngle: 0.8,          scale: 1.4,  radius: 20, visible: true },

      // MEIO DA SALA:
      // Mesinha de Centro na frente do sofá
      { id: 'coffee_table',  name: 'Mesinha de Centro',    icon: '🪵', category: 'furniture', model: coffeeTableModel,x: -50, y: 0,   liftZ: 0,  selfAngle: -Math.PI / 2, scale: 1.45, radius: 26, isCoffeeTable: true, visible: true },
      // TV Retrô na frente do tapete virada de frente para o sofá!
      { id: 'tv_rack',       name: 'Rack com TV Retrô',    icon: '📺', category: 'furniture', model: tvRackModel,    x: 8,   y: 0,   liftZ: 0,  selfAngle: Math.PI / 2,  scale: 1.45, radius: 36, isTvRack: true, visible: true }
    ];

    const roomState = {
      bedroom: BEDROOM_ITEMS,
      living: LIVING_ITEMS
    };

    let items = [ ...PETS, ...roomState[currentRoomId] ];

    // Slots inteligentes no tampo da mesa (Snap-to-Slot estilo The Sims / Animal Crossing)
    const DESK_SLOTS = [
      { id: 'left',   name: 'Tablet de Desenho', offX: -28, offY: 3 },
      { id: 'center', name: 'Note no Suporte',   offX: 0,   offY: -10 },
      { id: 'front',  name: 'Centro Frontal',    offX: 0,   offY: 6 },
      { id: 'cup',    name: 'Caneca de Café',    offX: 28,  offY: -10 },
      { id: 'books',  name: 'Livros da Mesa',    offX: 30,  offY: 6 }
    ];

    // Projeção Isométrica Global do Quarto (World -> Screen)
    function project(x, y, z) {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const rx = x * cosA - y * sinA;
      const ry = x * sinA + y * cosA;
      const cx = Math.floor(LOW_W / 2);
      const cy = Math.floor(LOW_H / 2) + 48;
      return {
        x: Math.round(cx + rx),
        y: Math.round(cy + ry * squash - z),
        depth: ry
      };
    }

    // Projeção Inversa (Screen -> World no chão Z = 0)
    function unproject(screenX, screenY) {
      const cx = Math.floor(LOW_W / 2);
      const cy = Math.floor(LOW_H / 2) + 48;
      const rx = screenX - cx;
      const ry = (screenY - cy) / squash;
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);
      const x = rx * cosA + ry * sinA;
      const y = -rx * sinA + ry * cosA;
      return { x, y };
    }

    // Função para desenhar polígono 4-pontos em 3D
    function drawQuad(p1, p2, p3, p4, fillStyle, strokeStyle = null, lineWidth = 1) {
      lowCtx.beginPath();
      lowCtx.moveTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.lineTo(p4.x, p4.y);
      lowCtx.closePath();
      if (fillStyle) {
        lowCtx.fillStyle = fillStyle;
        lowCtx.fill();
      }
      if (strokeStyle) {
        lowCtx.strokeStyle = strokeStyle;
        lowCtx.lineWidth = lineWidth;
        lowCtx.stroke();
      }
    }

    // --- HELPER UNIVERSAL PARA CAIXAS 3D ---
    function draw3DBox(x0, x1, y0, y1, z0, z1, colors) {
      const faces = [
        // Top (+Z)
        {
          pts: [project(x0, y0, z1), project(x1, y0, z1), project(x1, y1, z1), project(x0, y1, z1)],
          fill: colors.top || colors.main,
          stroke: colors.stroke
        },
        // Bottom (-Z)
        {
          pts: [project(x0, y1, z0), project(x1, y1, z0), project(x1, y0, z0), project(x0, y0, z0)],
          fill: colors.bottom || colors.dark || colors.main,
          stroke: colors.stroke
        },
        // Front (+X)
        {
          pts: [project(x1, y0, z0), project(x1, y1, z0), project(x1, y1, z1), project(x1, y0, z1)],
          fill: colors.front || colors.main,
          stroke: colors.stroke
        },
        // Back (-X)
        {
          pts: [project(x0, y1, z0), project(x0, y0, z0), project(x0, y0, z1), project(x0, y1, z1)],
          fill: colors.back || colors.dark || colors.main,
          stroke: colors.stroke
        },
        // Right (+Y)
        {
          pts: [project(x0, y1, z0), project(x1, y1, z0), project(x1, y1, z1), project(x0, y1, z1)],
          fill: colors.right || colors.main,
          stroke: colors.stroke
        },
        // Left (-Y)
        {
          pts: [project(x1, y0, z0), project(x0, y0, z0), project(x0, y0, z1), project(x1, y0, z1)],
          fill: colors.left || colors.dark || colors.main,
          stroke: colors.stroke
        }
      ];

      faces.forEach(f => {
        f.depth = (f.pts[0].depth + f.pts[1].depth + f.pts[2].depth + f.pts[3].depth) / 4;
      });
      faces.sort((a, b) => a.depth - b.depth);

      for (const f of faces) {
        drawQuad(f.pts[0], f.pts[1], f.pts[2], f.pts[3], f.fill, f.stroke);
      }
    }

    // Interpolação bilinear
    function lerpP(a, b, t) {
      return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
    }

    // --- FUNÇÃO UNIVERSAL DE DESENHAR OBJETOS EM SPRITE STACKING 3D ---
    function drawStackObject(model, worldX, worldY, liftZ = 0, selfAngle = 0, scale = 1.35) {
      const p = project(worldX, worldY, liftZ);
      const totalAngle = selfAngle + turn; // GIRA JUNTO COM O QUARTO EM 360°!

      const sheet = model.sheet;
      const count = model.count;
      const w = model.w;
      const h = model.h;
      const originX = Math.floor(w / 2);
      const originY = Math.floor(h / 2);

      for (let z = 0; z < count; z++) {
        lowCtx.save();
        lowCtx.translate(p.x, Math.round(p.y - z * scale));
        lowCtx.scale(scale, squash * scale);
        lowCtx.rotate(totalAngle);
        lowCtx.drawImage(
          sheet,
          z * w, 0, w, h,
          -originX, -originY, w, h
        );
        lowCtx.restore();
      }
    }

    // Renderizador Invertido para Mostrar a Barriguinha (Belly Roll)
    function drawStackInverted(model, worldX, worldY, liftZ = 0, selfAngle = 0, scale = 1.35) {
      const p = project(worldX, worldY, liftZ);
      const totalAngle = selfAngle + turn;

      const sheet = model.sheet;
      const count = model.count;
      const w = model.w;
      const h = model.h;
      const originX = Math.floor(w / 2);
      const originY = Math.floor(h / 2);

      // Invertido: fatia count-1 fica no chão, fatia 0 (barriguinha branca) fica no topo voltada para cima!
      for (let layer = 0; layer < count; layer++) {
        const z = count - 1 - layer;
        lowCtx.save();
        lowCtx.translate(p.x, Math.round(p.y - layer * scale));
        lowCtx.scale(scale, squash * scale);
        lowCtx.rotate(totalAngle);
        lowCtx.drawImage(
          sheet,
          z * w, 0, w, h,
          -originX, -originY, w, h
        );
        lowCtx.restore();
      }
    }

    // --- 1. CHÃO DE MADEIRA COM GRID ---
    function drawFloor() {
      const p0 = project(-ROOM_R, -ROOM_R, 0);
      const p1 = project(ROOM_R, -ROOM_R, 0);
      const p2 = project(ROOM_R, ROOM_R, 0);
      const p3 = project(-ROOM_R, ROOM_R, 0);

      lowCtx.fillStyle = P.woodMid;
      lowCtx.beginPath();
      lowCtx.moveTo(p0.x, p0.y);
      lowCtx.lineTo(p1.x, p1.y);
      lowCtx.lineTo(p2.x, p2.y);
      lowCtx.lineTo(p3.x, p3.y);
      lowCtx.closePath();
      lowCtx.fill();

      // Tábuas de madeira
      lowCtx.strokeStyle = P.plankLine;
      lowCtx.lineWidth = 1;
      const step = 11;
      for (let x = -ROOM_R + step; x < ROOM_R; x += step) {
        const pa = project(x, -ROOM_R, 0);
        const pb = project(x, ROOM_R, 0);
        lowCtx.beginPath();
        lowCtx.moveTo(pa.x, pa.y);
        lowCtx.lineTo(pb.x, pb.y);
        lowCtx.stroke();
      }

      // Grid sutil no Modo Decoração
      if (isDecorMode) {
        lowCtx.strokeStyle = 'rgba(255, 255, 255, 0.32)';
        lowCtx.lineWidth = 1;
        const gridStep = 16;
        for (let gx = -ROOM_R + gridStep; gx < ROOM_R; gx += gridStep) {
          const ga = project(gx, -ROOM_R, 0);
          const gb = project(gx, ROOM_R, 0);
          lowCtx.beginPath(); lowCtx.moveTo(ga.x, ga.y); lowCtx.lineTo(gb.x, gb.y); lowCtx.stroke();
        }
        for (let gy = -ROOM_R + gridStep; gy < ROOM_R; gy += gridStep) {
          const ga = project(-ROOM_R, gy, 0);
          const gb = project(ROOM_R, gy, 0);
          lowCtx.beginPath(); lowCtx.moveTo(ga.x, ga.y); lowCtx.lineTo(gb.x, gb.y); lowCtx.stroke();
        }
      }

      // Tapete central dependendo do cômodo (100% Projetado em 3D e travado no chão!)
      if (currentRoomId === 'living') {
        // Tapete Escandinavo Retangular em espaço de mundo 3D real: rotaciona perfeito com a câmera!
        const rx0 = -85, rx1 = -15;
        const ry0 = -35, ry1 = 35;

        const pA = project(rx0, ry0, 0.1);
        const pB = project(rx1, ry0, 0.1);
        const pC = project(rx1, ry1, 0.1);
        const pD = project(rx0, ry1, 0.1);
        drawQuad(pA, pB, pC, pD, '#E8DEC8'); // Borda de tear artesanal

        // Franjas nas bordas projetadas em 3D
        lowCtx.fillStyle = '#FAF7F2';
        for (let fy = ry0 + 4; fy < ry1 - 4; fy += 5) {
          const fr1 = project(rx0 - 3, fy, 0.15);
          lowCtx.fillRect(fr1.x - 1, fr1.y - 1, 2, 2);
          const fr2 = project(rx1 + 3, fy, 0.15);
          lowCtx.fillRect(fr2.x - 1, fr2.y - 1, 2, 2);
        }

        const pA2 = project(rx0 + 5, ry0 + 5, 0.15);
        const pB2 = project(rx1 - 5, ry0 + 5, 0.15);
        const pC2 = project(rx1 - 5, ry1 - 5, 0.15);
        const pD2 = project(rx0 + 5, ry1 - 5, 0.15);
        drawQuad(pA2, pB2, pC2, pD2, '#F5EFE6'); // Centro creme acolhedor

        const pA3 = project(rx0 + 10, ry0 + 10, 0.2);
        const pB3 = project(rx1 - 10, ry0 + 10, 0.2);
        const pC3 = project(rx1 - 10, ry1 - 10, 0.2);
        const pD3 = project(rx0 + 10, ry1 - 10, 0.2);
        drawQuad(pA3, pB3, pC3, pD3, '#EADCC9'); // Detalhe geométrico
      } else {
        // Tapete Nuvem Redondo do Quarto
        const rugP = project(0, 0, 0);
        lowCtx.save();
        lowCtx.translate(rugP.x, rugP.y);
        lowCtx.scale(1, squash * 0.95);

        lowCtx.beginPath();
        lowCtx.arc(0, 0, 48, 0, Math.PI * 2);
        lowCtx.fillStyle = '#E8E0D0';
        lowCtx.fill();

        lowCtx.beginPath();
        lowCtx.arc(0, 0, 40, 0, Math.PI * 2);
        lowCtx.fillStyle = '#F2EBE0';
        lowCtx.fill();

        lowCtx.beginPath();
        lowCtx.arc(0, 0, 32, 0, Math.PI * 2);
        lowCtx.fillStyle = '#FAF7F2';
        lowCtx.fill();

        lowCtx.restore();
      }
    }

    // --- 2. PAREDES 3D INTELIGENTES COM BACK-FACE CULLING ---
    const WALLS = [
      { id: 'north', a: { x: -ROOM_R, y: -ROOM_R }, b: { x: ROOM_R, y: -ROOM_R }, normal: { x: 0, y: -1 }, decor: 'window' },
      { id: 'west',  a: { x: -ROOM_R, y: ROOM_R },  b: { x: -ROOM_R, y: -ROOM_R }, normal: { x: -1, y: 0 }, decor: null },
      { id: 'south', a: { x: ROOM_R, y: ROOM_R },   b: { x: -ROOM_R, y: ROOM_R },  normal: { x: 0, y: 1 },  decor: null },
      { id: 'east',  a: { x: ROOM_R, y: -ROOM_R },  b: { x: ROOM_R, y: ROOM_R },   normal: { x: 1, y: 0 },  decor: null },
    ];

    function drawWalls() {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);

      const sortedWalls = [...WALLS].map(w => {
        const mx = (w.a.x + w.b.x) / 2;
        const my = (w.a.y + w.b.y) / 2;
        const rCenter = project(mx, my, WALL_H / 2);
        const nyRot = w.normal.x * sinA + w.normal.y * cosA;
        return {
          ...w,
          depth: rCenter.depth,
          isFrontWall: nyRot > 0.05
        };
      });

      sortedWalls.sort((a, b) => a.depth - b.depth);

      for (const w of sortedWalls) {
        if (w.isFrontWall) {
          const pA0 = project(w.a.x, w.a.y, 0);
          const pB0 = project(w.b.x, w.b.y, 0);
          const pA1 = project(w.a.x, w.a.y, 3);
          const pB1 = project(w.b.x, w.b.y, 3);

          lowCtx.fillStyle = P.baseboard;
          lowCtx.beginPath();
          lowCtx.moveTo(pA0.x, pA0.y); lowCtx.lineTo(pB0.x, pB0.y);
          lowCtx.lineTo(pB1.x, pB1.y); lowCtx.lineTo(pA1.x, pA1.y);
          lowCtx.closePath(); lowCtx.fill();
          continue;
        }

        const bA = project(w.a.x, w.a.y, 0);
        const bB = project(w.b.x, w.b.y, 0);
        const tA = project(w.a.x, w.a.y, WALL_H);
        const tB = project(w.b.x, w.b.y, WALL_H);

        lowCtx.fillStyle = P.wallInner;
        lowCtx.beginPath();
        lowCtx.moveTo(bA.x, bA.y); lowCtx.lineTo(bB.x, bB.y);
        lowCtx.lineTo(tB.x, tB.y); lowCtx.lineTo(tA.x, tA.y);
        lowCtx.closePath(); lowCtx.fill();

        lowCtx.strokeStyle = P.wallTrim;
        lowCtx.lineWidth = 1;
        lowCtx.beginPath();
        lowCtx.moveTo(tA.x, tA.y); lowCtx.lineTo(tB.x, tB.y); lowCtx.lineTo(bB.x, bB.y);
        lowCtx.stroke();

        const rA = project(w.a.x, w.a.y, 7);
        const rB = project(w.b.x, w.b.y, 7);
        lowCtx.fillStyle = P.baseboard;
        lowCtx.beginPath();
        lowCtx.moveTo(bA.x, bA.y); lowCtx.lineTo(bB.x, bB.y);
        lowCtx.lineTo(rB.x, rB.y); lowCtx.lineTo(rA.x, rA.y);
        lowCtx.closePath(); lowCtx.fill();

        if (w.decor === 'window') drawBigWindow();
        else if (w.decor === 'pegboard') drawPegboardDecor();
        else if (w.decor === 'garden_window') drawGardenWindow();
        else if (w.decor === 'living_art') drawLivingRoomArt();
      }
    }

    // --- JANELA PANORÂMICA COM NUVENS 3D VOLUMÉTRICAS ---
    function drawBigWindow() {
      const z0 = 32, z1 = 82;
      const x0 = -45, x1 = 45;
      const yWall = -ROOM_R;

      const w1 = project(x0, yWall + 0.5, z0);
      const w2 = project(x1, yWall + 0.5, z0);
      const w3 = project(x1, yWall + 0.5, z1);
      const w4 = project(x0, yWall + 0.5, z1);
      drawQuad(w1, w2, w3, w4, P.windowSky);

      // Nuvens 3D com Parallax fora do quarto
      cloudAnimX += 0.08;
      if (cloudAnimX > 110) cloudAnimX = -110;

      lowCtx.save();
      lowCtx.beginPath();
      lowCtx.moveTo(w1.x, w1.y);
      lowCtx.lineTo(w2.x, w2.y);
      lowCtx.lineTo(w3.x, w3.y);
      lowCtx.lineTo(w4.x, w4.y);
      lowCtx.closePath();
      lowCtx.clip();

      function draw3DCloud(cx, cySky, cz) {
        draw3DBox(cx - 16, cx + 16, cySky - 4, cySky + 4, cz - 4, cz + 4, {
          top: '#FFFFFF', front: '#F0F4F8', back: '#DCE5ED', left: '#DCE5ED', right: '#F0F4F8', bottom: '#C8D7E3'
        });
        draw3DBox(cx - 8, cx + 7, cySky - 3, cySky + 3, cz + 4, cz + 10, {
          top: '#FFFFFF', front: '#F0F4F8', back: '#DCE5ED', left: '#DCE5ED', right: '#F0F4F8', bottom: '#C8D7E3'
        });
        draw3DBox(cx + 9, cx + 19, cySky - 3, cySky + 3, cz - 2, cz + 5, {
          top: '#FFFFFF', front: '#F0F4F8', back: '#DCE5ED', left: '#DCE5ED', right: '#F0F4F8', bottom: '#C8D7E3'
        });
      }

      draw3DCloud(cloudAnimX, yWall - 25, 58);
      const c2X = ((cloudAnimX + 90) % 200) - 100;
      draw3DCloud(c2X, yWall - 35, 68);

      lowCtx.restore();

      // Moldura e peitoril 3D
      const cBottom = project(0, yWall + 0.6, z0);
      const cTop = project(0, yWall + 0.6, z1);
      lowCtx.strokeStyle = P.windowFrame;
      lowCtx.lineWidth = 2.5;
      lowCtx.beginPath(); lowCtx.moveTo(cBottom.x, cBottom.y); lowCtx.lineTo(cTop.x, cTop.y); lowCtx.stroke();

      const cLeft = project(x0, yWall + 0.6, (z0 + z1) / 2);
      const cRight = project(x1, yWall + 0.6, (z0 + z1) / 2);
      lowCtx.beginPath(); lowCtx.moveTo(cLeft.x, cLeft.y); lowCtx.lineTo(cRight.x, cRight.y); lowCtx.stroke();

      draw3DBox(x0 - 5, x1 + 5, yWall, yWall + 8, z0 - 2, z0 + 1, {
        top: '#FAF7F2', front: '#E5DFD5', back: '#FAF7F2', left: '#D8D1C5', right: '#E5DFD5', bottom: '#C8BFA8', stroke: '#A89E88'
      });

      // Cortinas 3D
      draw3DBox(x0 - 14, x0 - 1, yWall, yWall + 5, z0 - 8, z1 + 6, {
        top: '#F2B2A7', front: '#E8A598', back: '#D68C7E', left: '#D68C7E', right: '#E8A598', bottom: '#C47768'
      });
      draw3DBox(x1 + 1, x1 + 14, yWall, yWall + 5, z0 - 8, z1 + 6, {
        top: '#F2B2A7', front: '#E8A598', back: '#D68C7E', left: '#E8A598', right: '#D68C7E', bottom: '#C47768'
      });
    }

    // --- PAINEL PEGBOARD (PAREDE SUL: y = ROOM_R) ---
    function drawPegboardDecor() {
      const yWall = ROOM_R;
      const pb1 = project(-30, yWall - 1.5, 42);
      const pb2 = project(15, yWall - 1.5, 42);
      const pb3 = project(15, yWall - 1.5, 82);
      const pb4 = project(-30, yWall - 1.5, 82);
      drawQuad(pb1, pb2, pb3, pb4, '#E5D6C0', '#B59D7E', 1.5);

      const nt1 = project(-22, yWall - 2, 60);
      lowCtx.fillStyle = '#FCE076'; lowCtx.fillRect(nt1.x - 4, nt1.y - 4, 8, 8);

      const nt2 = project(-8, yWall - 2, 65);
      lowCtx.fillStyle = '#A2D5F2'; lowCtx.fillRect(nt2.x - 4, nt2.y - 4, 8, 8);

      const nt3 = project(5, yWall - 2, 54);
      lowCtx.fillStyle = '#F7A8B8'; lowCtx.fillRect(nt3.x - 4, nt3.y - 4, 8, 8);
    }

    // --- JANELA DO JARDIM NA PAREDE LESTE (x = ROOM_R) ---
    function drawGardenWindow() {
      const xWall = ROOM_R;
      const y0 = -65, y1 = -15; // Lado a lado com a porta do jardim que fica em y = 55!
      const z0 = 35, z1 = 80;

      const w1 = project(xWall - 0.5, y0, z0);
      const w2 = project(xWall - 0.5, y1, z0);
      const w3 = project(xWall - 0.5, y1, z1);
      const w4 = project(xWall - 0.5, y0, z1);

      drawQuad(w1, w2, w3, w4, '#93C5FD'); // Céu azul ensolarado do jardim

      lowCtx.save();
      lowCtx.beginPath();
      lowCtx.moveTo(w1.x, w1.y); lowCtx.lineTo(w2.x, w2.y);
      lowCtx.lineTo(w3.x, w3.y); lowCtx.lineTo(w4.x, w4.y);
      lowCtx.closePath();
      lowCtx.clip();

      // Sol e colinas verdes do jardim com grama e árvores
      const sunP = project(xWall + 20, -50, 72);
      lowCtx.fillStyle = '#FEF08A';
      lowCtx.beginPath(); lowCtx.arc(sunP.x, sunP.y, 14, 0, Math.PI * 2); lowCtx.fill();

      // Copa de árvores do quintal
      const treeP1 = project(xWall + 15, -60, 48);
      const treeP2 = project(xWall + 15, -25, 44);
      lowCtx.fillStyle = '#22C55E';
      lowCtx.beginPath(); lowCtx.arc(treeP1.x, treeP1.y, 22, 0, Math.PI * 2); lowCtx.fill();
      lowCtx.fillStyle = '#16A34A';
      lowCtx.beginPath(); lowCtx.arc(treeP2.x, treeP2.y, 18, 0, Math.PI * 2); lowCtx.fill();

      // Flores cor-de-rosa (cerejeira/ipê)
      lowCtx.fillStyle = '#F472B6';
      lowCtx.fillRect(treeP1.x - 6, treeP1.y - 8, 3, 3);
      lowCtx.fillRect(treeP1.x + 8, treeP1.y + 4, 3, 3);
      lowCtx.fillRect(treeP2.x - 4, treeP2.y - 2, 3, 3);

      // Borboletinha voando no jardim
      const bTime = Date.now() * 0.003;
      const bfX = (treeP1.x + treeP2.x) / 2 + Math.sin(bTime) * 12;
      const bfY = (treeP1.y + treeP2.y) / 2 + Math.cos(bTime * 1.5) * 6;
      lowCtx.fillStyle = '#FBBF24';
      lowCtx.fillRect(bfX, bfY, 3, 2);
      lowCtx.fillRect(bfX + 3, bfY - 1, 2, 2);

      lowCtx.restore();

      // Moldura de madeira nobre e cruzeta
      const cBottom = project(xWall - 0.6, (y0 + y1) / 2, z0);
      const cTop = project(xWall - 0.6, (y0 + y1) / 2, z1);
      lowCtx.strokeStyle = '#5B371E';
      lowCtx.lineWidth = 2.2;
      lowCtx.beginPath(); lowCtx.moveTo(cBottom.x, cBottom.y); lowCtx.lineTo(cTop.x, cTop.y); lowCtx.stroke();

      const cLeft = project(xWall - 0.6, y0, (z0 + z1) / 2);
      const cRight = project(xWall - 0.6, y1, (z0 + z1) / 2);
      lowCtx.beginPath(); lowCtx.moveTo(cLeft.x, cLeft.y); lowCtx.lineTo(cRight.x, cRight.y); lowCtx.stroke();

      // Peitoril da janela com floreira
      draw3DBox(xWall - 6, xWall, y0 - 3, y1 + 3, z0 - 2, z0 + 2, {
        top: '#D49D65', front: '#BD834D', back: '#D49D65', left: '#9E6738', right: '#BD834D', bottom: '#5B371E'
      });
      // Floreira com vasinhos de flor colorida
      draw3DBox(xWall - 5, xWall - 1, y0 + 4, y1 - 4, z0 + 2, z0 + 6, {
        top: '#C2410C', front: '#9A3412', back: '#C2410C', left: '#7C2D12', right: '#9A3412', bottom: '#7C2D12'
      });
    }

    // --- QUADROS DECORATIVOS DA SALA DE ESTAR (PAREDE NORTE: y = -ROOM_R) ---
    function drawLivingRoomArt() {
      const yWall = -ROOM_R;
      // === GRANDE QUADRO DE GALINHAS ENTRE AS PORTAS (x=-25..20, z=48..82) ===
      const x0 = -25, x1 = 20;
      const z0 = 48, z1 = 82;

      // 1. Moldura rústica de madeira nobre talhada
      draw3DBox(x0 - 2, x1 + 2, yWall, yWall + 2.5, z0 - 2, z1 + 2, {
        top: '#6B3E1E', front: '#4A2A14', back: '#6B3E1E', left: '#4A2A14', right: '#4A2A14', bottom: '#351C0C'
      });

      // 2. Filete interno dourado decorativo
      const f1 = project(x0 - 0.5, yWall + 1.2, z0 - 0.5);
      const f2 = project(x1 + 0.5, yWall + 1.2, z0 - 0.5);
      const f3 = project(x1 + 0.5, yWall + 1.2, z1 + 0.5);
      const f4 = project(x0 - 0.5, yWall + 1.2, z1 + 0.5);
      drawQuad(f1, f2, f3, f4, '#D4AF37');

      // 3. Fundo da tela: Céu azul ensolarado com nuvens
      const qA = project(x0, yWall + 1.5, z0);
      const qB = project(x1, yWall + 1.5, z0);
      const qC = project(x1, yWall + 1.5, z1);
      const qD = project(x0, yWall + 1.5, z1);
      drawQuad(qA, qB, qC, qD, '#93C5FD');

      lowCtx.save();
      lowCtx.beginPath();
      lowCtx.moveTo(qA.x, qA.y); lowCtx.lineTo(qB.x, qB.y);
      lowCtx.lineTo(qC.x, qC.y); lowCtx.lineTo(qD.x, qD.y);
      lowCtx.closePath();
      lowCtx.clip();

      // Sol dourado no alto
      const sunP = project(x1 - 8, yWall + 1.6, z1 - 8);
      lowCtx.fillStyle = '#FDE047';
      lowCtx.beginPath(); lowCtx.arc(sunP.x, sunP.y, 6.5, 0, Math.PI * 2); lowCtx.fill();

      // Nuvens fofas brancas
      const clP = project(x0 + 10, yWall + 1.6, z1 - 7);
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.beginPath(); lowCtx.arc(clP.x, clP.y, 5, 0, Math.PI * 2);
      lowCtx.arc(clP.x + 5, clP.y - 1, 4, 0, Math.PI * 2);
      lowCtx.arc(clP.x - 4, clP.y + 1, 3.5, 0, Math.PI * 2);
      lowCtx.fill();

      // Colina verde suave ao fundo
      const h1A = project(x0, yWall + 1.6, z0 + 14);
      const h1B = project(x1, yWall + 1.6, z0 + 10);
      const h1C = project(x1, yWall + 1.6, z0);
      const h1D = project(x0, yWall + 1.6, z0);
      drawQuad(h1A, h1B, h1C, h1D, '#86EFAC');

      // Pasto verde principal
      const h2A = project(x0, yWall + 1.7, z0 + 8);
      const h2B = project(x1, yWall + 1.7, z0 + 7);
      const h2C = project(x1, yWall + 1.7, z0);
      const h2D = project(x0, yWall + 1.7, z0);
      drawQuad(h2A, h2B, h2C, h2D, '#22C55E');

      // Florzinhas coloridas no pasto
      const fl1 = project(x0 + 5, yWall + 1.8, z0 + 3);
      const fl2 = project(x1 - 6, yWall + 1.8, z0 + 4);
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.fillRect(fl1.x, fl1.y, 2, 2);
      lowCtx.fillRect(fl2.x, fl2.y, 2, 2);
      lowCtx.fillStyle = '#F472B6';
      lowCtx.fillRect(fl1.x + 3, fl1.y + 1, 2, 2);

      // --- GALINHA BRANCA FOFINHA (MAMA CHICKEN) ---
      const chkP = project(-8, yWall + 1.8, z0 + 8);
      // Corpinho gordinho branco
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.beginPath(); lowCtx.arc(chkP.x, chkP.y, 6.5, 0, Math.PI * 2); lowCtx.fill();
      // Asinha branca sombreada
      lowCtx.fillStyle = '#F1F5F9';
      lowCtx.beginPath(); lowCtx.arc(chkP.x - 2, chkP.y + 1, 4, 0, Math.PI * 2); lowCtx.fill();
      // Crista vermelha vibrante
      lowCtx.fillStyle = '#EF4444';
      lowCtx.fillRect(chkP.x + 1, chkP.y - 8, 3, 3);
      lowCtx.fillRect(chkP.x + 3, chkP.y - 7, 2, 2);
      // Papo vermelho
      lowCtx.fillRect(chkP.x + 5, chkP.y - 1, 2, 2.5);
      // Biquinho amarelo
      lowCtx.fillStyle = '#F59E0B';
      lowCtx.beginPath();
      lowCtx.moveTo(chkP.x + 5, chkP.y - 3);
      lowCtx.lineTo(chkP.x + 9, chkP.y - 2);
      lowCtx.lineTo(chkP.x + 5, chkP.y - 1);
      lowCtx.fill();
      // Olhinho preto kawaii
      lowCtx.fillStyle = '#0F172A';
      lowCtx.fillRect(chkP.x + 3, chkP.y - 4, 1.5, 1.5);

      // --- PINTINHO AMARELINHO (BABY CHICK) SALTITANDO ---
      const ckP = project(5, yWall + 1.8, z0 + 6);
      // Corpinho amarelo dourado
      lowCtx.fillStyle = '#FBBF24';
      lowCtx.beginPath(); lowCtx.arc(ckP.x, ckP.y, 4, 0, Math.PI * 2); lowCtx.fill();
      // Asinha fofa
      lowCtx.fillStyle = '#F59E0B';
      lowCtx.fillRect(ckP.x - 2, ckP.y, 2.5, 2);
      // Biquinho laranja
      lowCtx.fillStyle = '#EA580C';
      lowCtx.fillRect(ckP.x + 3, ckP.y - 1, 2, 1.5);
      // Olhinho brilhante
      lowCtx.fillStyle = '#0F172A';
      lowCtx.fillRect(ckP.x + 1.5, ckP.y - 2, 1.2, 1.2);
      // Coraçõezinhos de afeto subindo
      const hP = project(0, yWall + 1.8, z0 + 16);
      lowCtx.fillStyle = '#F43F5E';
      lowCtx.beginPath();
      lowCtx.arc(hP.x - 1.5, hP.y, 1.5, 0, Math.PI * 2);
      lowCtx.arc(hP.x + 1.5, hP.y, 1.5, 0, Math.PI * 2);
      lowCtx.lineTo(hP.x, hP.y + 3);
      lowCtx.fill();

      lowCtx.restore();
    }

    // --- ITENS DE PAREDE E PRATELEIRA MODULARES ---

    // 1. Tábua da Prateleira Limpa (Alargada para 1 Tile = 18px! SEM Sobreposição!)
    // Som aconchegante da porta (abrir / fechar)
    function playDoorSound(isOpen) {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = isOpen ? 'triangle' : 'sine';
        osc.frequency.setValueAtTime(isOpen ? 110 : 170, now);
        osc.frequency.exponentialRampToValueAtTime(isOpen ? 210 : 85, now + 0.16);
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.exponentialRampToValueAtTime(0.18, now + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.22);
      } catch (e) {}
    }

    // --- PORTA DE MADEIRA NOBRE NA PAREDE LESTE ---
    function drawDoor(item) {
      const wall = item.wall || 'east';
      const hw = (item.width || 28) / 2;
      const H = item.height || 76;
      const liftZ = item.liftZ || 0;
      const isOpen = item.isOpen || false;
      const openAngle = isOpen ? 0.95 : 0; // Ângulo positivo abrindo suavemente para DENTRO do cômodo!

      let pS1, pS2, pS3, pS4;
      let pB1, pB2, pT1, pT2;
      let d1, d2, d3, d4;
      let tipX, tipY, hingeX, hingeY;
      const doorW = hw * 2;
      const isGarden = (item.id === 'door_garden');

      if (wall === 'east') {
        const wallX = item.x || ROOM_R;
        const cy = item.y;
        pS1 = project(wallX, cy - hw - 2, liftZ);
        pS2 = project(wallX - 3, cy - hw - 2, liftZ);
        pS3 = project(wallX - 3, cy + hw + 2, liftZ);
        pS4 = project(wallX, cy + hw + 2, liftZ);

        pB1 = project(wallX, cy - hw - 2, liftZ);
        pB2 = project(wallX, cy + hw + 2, liftZ);
        pT1 = project(wallX, cy - hw - 2, liftZ + H + 3);
        pT2 = project(wallX, cy + hw + 2, liftZ + H + 3);

        hingeX = wallX; hingeY = cy + hw;
        // Abre para DENTRO do quarto (-X):
        tipX = wallX - doorW * Math.sin(openAngle);
        tipY = hingeY - doorW * Math.cos(openAngle);

        d1 = project(hingeX, hingeY, liftZ);
        d2 = project(tipX, tipY, liftZ);
        d3 = project(tipX, tipY, liftZ + H);
        d4 = project(hingeX, hingeY, liftZ + H);
      } else if (wall === 'north') {
        const wallY = item.y || -ROOM_R;
        const cx = item.x;
        pS1 = project(cx - hw - 2, wallY, liftZ);
        pS2 = project(cx - hw - 2, wallY + 3, liftZ);
        pS3 = project(cx + hw + 2, wallY + 3, liftZ);
        pS4 = project(cx + hw + 2, wallY, liftZ);

        pB1 = project(cx - hw - 2, wallY, liftZ);
        pB2 = project(cx + hw + 2, wallY, liftZ);
        pT1 = project(cx - hw - 2, wallY, liftZ + H + 3);
        pT2 = project(cx + hw + 2, wallY, liftZ + H + 3);

        hingeX = cx - hw; hingeY = wallY;
        // Abre para DENTRO do quarto (+Y):
        tipX = hingeX + doorW * Math.cos(openAngle);
        tipY = wallY + doorW * Math.sin(openAngle);

        d1 = project(hingeX, hingeY, liftZ);
        d2 = project(tipX, tipY, liftZ);
        d3 = project(tipX, tipY, liftZ + H);
        d4 = project(hingeX, hingeY, liftZ + H);
      } else if (wall === 'west') {
        const wallX = item.x || -ROOM_R;
        const cy = item.y;
        pS1 = project(wallX, cy - hw - 2, liftZ);
        pS2 = project(wallX + 3, cy - hw - 2, liftZ);
        pS3 = project(wallX + 3, cy + hw + 2, liftZ);
        pS4 = project(wallX, cy + hw + 2, liftZ);

        pB1 = project(wallX, cy - hw - 2, liftZ);
        pB2 = project(wallX, cy + hw + 2, liftZ);
        pT1 = project(wallX, cy - hw - 2, liftZ + H + 3);
        pT2 = project(wallX, cy + hw + 2, liftZ + H + 3);

        hingeX = wallX; hingeY = cy - hw;
        // Abre para DENTRO (+X):
        tipX = wallX + doorW * Math.sin(openAngle);
        tipY = hingeY + doorW * Math.cos(openAngle);

        d1 = project(hingeX, hingeY, liftZ);
        d2 = project(tipX, tipY, liftZ);
        d3 = project(tipX, tipY, liftZ + H);
        d4 = project(hingeX, hingeY, liftZ + H);
      } else { // south
        const wallY = item.y || ROOM_R;
        const cx = item.x;
        pS1 = project(cx - hw - 2, wallY, liftZ);
        pS2 = project(cx - hw - 2, wallY - 3, liftZ);
        pS3 = project(cx + hw + 2, wallY - 3, liftZ);
        pS4 = project(cx + hw + 2, wallY, liftZ);

        pB1 = project(cx - hw - 2, wallY, liftZ);
        pB2 = project(cx + hw + 2, wallY, liftZ);
        pT1 = project(cx - hw - 2, wallY, liftZ + H + 3);
        pT2 = project(cx + hw + 2, wallY, liftZ + H + 3);

        hingeX = cx + hw; hingeY = wallY;
        // Abre para DENTRO (-Y):
        tipX = hingeX - doorW * Math.cos(openAngle);
        tipY = wallY - doorW * Math.sin(openAngle);

        d1 = project(hingeX, hingeY, liftZ);
        d2 = project(tipX, tipY, liftZ);
        d3 = project(tipX, tipY, liftZ + H);
        d4 = project(hingeX, hingeY, liftZ + H);
      }

      // 1. Soleira da porta
      drawQuad(pS1, pS2, pS3, pS4, '#4A2E1B');

      // 2. Batente estrutural de madeira
      drawQuad(pB1, pB2, pT2, pT1, '#5A341A');

      // 3. Vão interno escuro quando aberta
      if (isOpen) {
        const vB1 = project(hingeX, hingeY, liftZ);
        const vB2 = project(wall === 'east' || wall === 'west' ? hingeX : (hingeX + (tipX > hingeX ? -doorW : doorW)), wall === 'south' || wall === 'north' ? hingeY : (hingeY + (tipY > hingeY ? -doorW : doorW)), liftZ);
        const vT2 = project(vB2.x, vB2.y, liftZ + H);
        const vT1 = project(vB1.x, vB1.y, liftZ + H);
        drawQuad(pB1, pB2, pT2, pT1, isGarden ? '#93C5FD' : '#1A1412');
      }

      // 4. Folha da porta de madeira
      drawQuad(d1, d2, d3, d4, '#8B542F', '#4A2A14', 1.2);

      // 5. Painéis entalhados em relevo
      const uX = (tipX - hingeX) / doorW;
      const uY = (tipY - hingeY) / doorW;

      function drawDoorPanel(zBot, zTop, isGlass = false) {
        const m = 3;
        const p1 = project(hingeX + uX * m, hingeY + uY * m, liftZ + zBot);
        const p2 = project(tipX - uX * m, tipY - uY * m, liftZ + zBot);
        const p3 = project(tipX - uX * m, tipY - uY * m, liftZ + zTop);
        const p4 = project(hingeX + uX * m, hingeY + uY * m, liftZ + zTop);

        const col = isGlass ? 'rgba(186, 230, 253, 0.85)' : '#784320';
        const strk = isGlass ? '#7DD3FC' : '#522A0F';
        drawQuad(p1, p2, p3, p4, col, strk, 0.8);
      }

      drawDoorPanel(6, 32, false);
      drawDoorPanel(40, 68, isGarden);

      // 6. Maçaneta Dourada de latão
      const knobX = tipX - uX * 4;
      const knobY = tipY - uY * 4;
      const knobP = project(knobX, knobY, liftZ + 36);

      lowCtx.fillStyle = '#3B2219';
      lowCtx.fillRect(knobP.x - 1, knobP.y - 4, 3, 8);
      lowCtx.fillStyle = '#F4B846';
      lowCtx.beginPath();
      lowCtx.arc(knobP.x, knobP.y, 3, 0, Math.PI * 2);
      lowCtx.fill();

      // 7. Plaquinha de madeira artesanal sobre o batente indicando o destino
      const plaqueLabel = item.id === 'door_kitchen' ? '🍽️ COZINHA' :
                          item.id === 'door_bedroom' ? '🛏️ QUARTO' :
                          item.id === 'door_garden' ? '🌳 JARDIM' :
                          (item.targetRoom === 'living' || item.id === 'door') ? '🛋️ SALA' : null;
      if (plaqueLabel) {
        const midX = (hingeX + tipX) / 2;
        const midY = (hingeY + tipY) / 2;
        const plP = project(midX, midY, liftZ + H + 8);
        lowCtx.save();
        lowCtx.font = 'bold 8px sans-serif';
        const plTw = lowCtx.measureText(plaqueLabel).width;
        const plW = plTw + 8;
        const plH = 12;
        const plX = Math.round(plP.x - plW / 2);
        const plY = Math.round(plP.y - plH / 2);

        // Moldura rústica da placa
        lowCtx.fillStyle = '#4A2A14';
        lowCtx.fillRect(plX - 1, plY - 1, plW + 2, plH + 2);
        lowCtx.fillStyle = '#D4A373';
        lowCtx.fillRect(plX, plY, plW, plH);
        lowCtx.fillStyle = '#2C1810';
        lowCtx.fillText(plaqueLabel, plX + 4, plY + 9);
        lowCtx.restore();
      }
    }

    function drawShelfItem(shelf) {
      const xWall = -ROOM_R;
      const sy = shelf.y;
      const sz = shelf.liftZ;
      const halfLen = (shelf.length || 68) / 2;

      // 1. Suportes / Mísulas desenhados PRIMEIRO (ficam estritamente ABAIXO da tábua!)
      const bOffsets = [-halfLen + 10, halfLen - 10];
      for (const bo of bOffsets) {
        const by = sy + bo;
        draw3DBox(xWall, xWall + 13, by - 1.2, by + 1.2, sz - 11, sz - 0.2, {
          top: '#633A18', front: '#633A18', back: '#532F16', left: '#532F16', right: '#7E4E2C', bottom: '#3B2219', stroke: '#3B2219'
        });
      }

      // 2. Tábua da prateleira desenhada DEPOIS (largura total de 1 Tile = 18px! Cobre 100% o topo dos suportes!)
      draw3DBox(xWall, xWall + 18, sy - halfLen, sy + halfLen, sz, sz + 3.5, {
        top: '#A06842', front: '#804E2B', back: '#6B3E1E', left: '#6B3E1E', right: '#804E2B', bottom: '#5A341A', stroke: '#3B2219'
      });
    }

    // 2. Livros em Pé (Acessório Universal 3D)
    function drawShelfBooks(item) {
      const x = item.x;
      const y = item.y;
      const z = item.liftZ;
      // Livro 1 (Vermelho em pé)
      draw3DBox(x - 5, x + 4, y - 6, y - 2, z, z + 17, {
        top: '#FAF7F2', front: '#C85A48', back: '#A03828', left: '#A03828', right: '#C85A48', bottom: '#802818', stroke: '#3B2219'
      });
      // Livro 2 (Azul em pé)
      draw3DBox(x - 5, x + 3, y - 1, y + 3, z, z + 13, {
        top: '#FAF7F2', front: '#4A7CA8', back: '#325C80', left: '#325C80', right: '#4A7CA8', bottom: '#254460', stroke: '#3B2219'
      });
      // Apoio de metal moderno
      draw3DBox(x - 5.5, x + 2.5, y + 4, y + 5.5, z, z + 9, {
        top: '#94A3B8', front: '#64748B', back: '#475569', left: '#475569', right: '#64748B', bottom: '#334155', stroke: '#1E293B'
      });
    }

    // 3. Vasinho de Suculenta Terracota (Acessório Universal 3D)
    function drawShelfPlant(item) {
      const x = item.x;
      const y = item.y;
      const z = item.liftZ;
      draw3DBox(x - 4, x + 4, y - 4, y + 4, z, z + 8, {
        top: '#4A2E1B', front: '#C26A45', back: '#A04E2D', left: '#A04E2D', right: '#C26A45', bottom: '#3B2219', stroke: '#3B2219'
      });
      draw3DBox(x - 2, x + 2, y - 3, y + 3, z + 8, z + 16, {
        top: '#5BB055', front: '#4D8A48', back: '#386A34', left: '#386A34', right: '#4D8A48', bottom: '#244520', stroke: '#244520'
      });
      draw3DBox(x - 1.5, x + 1.5, y - 5, y - 3, z + 10, z + 13, { top: '#5BB055', front: '#4D8A48', stroke: '#244520' });
      draw3DBox(x - 1.5, x + 1.5, y + 3, y + 5, z + 10, z + 13, { top: '#5BB055', front: '#4D8A48', stroke: '#244520' });
    }

    // 4. Livros Deitados com Cristal Rosa (Acessório Universal 3D)
    function drawShelfCrystal(item) {
      const x = item.x;
      const y = item.y;
      const z = item.liftZ;
      draw3DBox(x - 5, x + 5, y - 5, y + 5, z, z + 3.5, {
        top: '#0D9488', front: '#0F766E', back: '#115E59', left: '#FAF7F2', right: '#FAF7F2', bottom: '#134E4A', stroke: '#042F2C'
      });
      draw3DBox(x - 4, x + 4, y - 4, y + 4, z + 3.5, z + 7, {
        top: '#7C3AED', front: '#6D28D9', back: '#5B21B6', left: '#FAF7F2', right: '#FAF7F2', bottom: '#4C1D95', stroke: '#2E1065'
      });
      draw3DBox(x - 2, x + 2, y - 2, y + 2, z + 7, z + 13, {
        top: '#F472B6', front: '#EC4899', back: '#DB2777', left: '#DB2777', right: '#EC4899', bottom: '#BE185D', stroke: '#831843'
      });
    }

    // 5. Relógio Cilíndrico de Parede 3D com Ponteiros em Tempo Real
    function drawWallClock(item) {
      const xWall = -ROOM_R;
      const clkRadius = 10;
      const clkDepth = 4.5;
      const xBack = xWall + 0.5;
      const xFront = xWall + clkDepth;
      const yCenter = item.y;
      const zCenter = item.liftZ;
      const N = 16;

      const backPts = [];
      const frontPts = [];
      const dialPts = [];

      for (let i = 0; i < N; i++) {
        const ang = (i / N) * Math.PI * 2;
        const dy = Math.sin(ang) * clkRadius;
        const dz = Math.cos(ang) * clkRadius;
        backPts.push(project(xBack, yCenter + dy, zCenter + dz));
        frontPts.push(project(xFront, yCenter + dy, zCenter + dz));
        dialPts.push(project(xFront + 0.1, yCenter + dy * 0.76, zCenter + dz * 0.76));
      }

      const clkFacets = [];
      for (let i = 0; i < N; i++) {
        const j = (i + 1) % N;
        const p1 = backPts[i];
        const p2 = backPts[j];
        const p3 = frontPts[j];
        const p4 = frontPts[i];
        const d = (p1.depth + p2.depth + p3.depth + p4.depth) / 4;
        const ang = (i / N) * Math.PI * 2;
        const shade = Math.cos(ang) > 0 ? '#9E6740' : '#6B3E1E';
        clkFacets.push({ pts: [p1, p2, p3, p4], depth: d, fill: shade, stroke: '#532F16' });
      }

      const frontDepth = frontPts.reduce((s, p) => s + p.depth, 0) / N;
      clkFacets.push({ pts: frontPts, depth: frontDepth, fill: '#804E2B' });
      clkFacets.push({ pts: dialPts, depth: frontDepth + 0.05, fill: '#FAF7F2', stroke: '#3B2A20' });

      clkFacets.sort((a, b) => a.depth - b.depth);

      for (const f of clkFacets) {
        lowCtx.beginPath();
        lowCtx.moveTo(f.pts[0].x, f.pts[0].y);
        for (let k = 1; k < f.pts.length; k++) lowCtx.lineTo(f.pts[k].x, f.pts[k].y);
        lowCtx.closePath();
        if (f.fill) {
          lowCtx.fillStyle = f.fill;
          lowCtx.fill();
        }
        if (f.stroke) {
          lowCtx.strokeStyle = f.stroke;
          lowCtx.lineWidth = 1;
          lowCtx.stroke();
        }
      }

      // Ponteiros 3D com hora real
      const cCenter = project(xFront + 0.2, yCenter, zCenter);
      const tickAngles = [0, Math.PI / 2, Math.PI, Math.PI * 1.5];
      for (const ta of tickAngles) {
        const tA = project(xFront + 0.2, yCenter + Math.sin(ta) * 5.0, zCenter + Math.cos(ta) * 5.0);
        const tB = project(xFront + 0.2, yCenter + Math.sin(ta) * 6.8, zCenter + Math.cos(ta) * 6.8);
        lowCtx.strokeStyle = '#8C6A54';
        lowCtx.lineWidth = 1.2;
        lowCtx.beginPath(); lowCtx.moveTo(tA.x, tA.y); lowCtx.lineTo(tB.x, tB.y); lowCtx.stroke();
      }

      const now = new Date();
      const sec = now.getSeconds() + now.getMilliseconds() / 1000;
      const min = now.getMinutes() + sec / 60;
      const hr = (now.getHours() % 12) + min / 60;

      const hrAng = (hr / 12) * Math.PI * 2;
      const minAng = (min / 60) * Math.PI * 2;

      const hrEnd = project(xFront + 0.3, yCenter + Math.sin(hrAng) * 3.8, zCenter + Math.cos(hrAng) * 3.8);
      lowCtx.strokeStyle = '#3B2A20';
      lowCtx.lineWidth = 1.6;
      lowCtx.beginPath(); lowCtx.moveTo(cCenter.x, cCenter.y); lowCtx.lineTo(hrEnd.x, hrEnd.y); lowCtx.stroke();

      const minEnd = project(xFront + 0.3, yCenter + Math.sin(minAng) * 6.0, zCenter + Math.cos(minAng) * 6.0);
      lowCtx.strokeStyle = '#C85A48';
      lowCtx.lineWidth = 1.2;
      lowCtx.beginPath(); lowCtx.moveTo(cCenter.x, cCenter.y); lowCtx.lineTo(minEnd.x, minEnd.y); lowCtx.stroke();

      lowCtx.fillStyle = '#DE864A';
      lowCtx.fillRect(cCenter.x - 1, cCenter.y - 1, 2, 2);
    }

    // 6. Quadros 3D Individuais (Parede Leste: x = ROOM_R)
    function drawSingleFrame(item, type) {
      const xWall = ROOM_R;
      const frameThick = 4.0;
      // QUADRO DE POST-ITS EXPANDIDO (Quase o dobro do tamanho!)
      const halfW = (type === 'corkboard' ? 24 : 14);
      const halfH = (type === 'corkboard' ? 26 : 16);
      const y0 = item.y - halfW;
      const y1 = item.y + halfW;
      const z0 = item.liftZ - halfH;
      const z1 = item.liftZ + halfH;

      // Moldura externa de madeira bonita
      const p1 = project(xWall - 0.5, y0, z0);
      const p2 = project(xWall - 0.5, y1, z0);
      const p3 = project(xWall - 0.5, y1, z1);
      const p4 = project(xWall - 0.5, y0, z1);
      drawQuad(p1, p2, p3, p4, '#5C3823'); // Moldura de madeira maciça

      if (type === 'corkboard') {
        // Fundo de Cortiça aconchegante
        const innerP1 = lerpP(lerpP(p1, p2, 0.05), lerpP(p4, p3, 0.05), 0.05);
        const innerP2 = lerpP(lerpP(p1, p2, 0.95), lerpP(p4, p3, 0.95), 0.05);
        const innerP3 = lerpP(lerpP(p1, p2, 0.95), lerpP(p4, p3, 0.95), 0.95);
        const innerP4 = lerpP(lerpP(p1, p2, 0.05), lerpP(p4, p3, 0.05), 0.95);
        drawQuad(innerP1, innerP2, innerP3, innerP4, '#D4A373');

        // Mini Post-its Coloridos e Tachinhas espalhados pelo mural expandido!
        const nCols = ['#FEF08A', '#FBCFE8', '#BAE6FD', '#BBF7D0', '#FED7AA', '#DDD6FE'];
        const noteLocs = [
          { u0: 0.10, u1: 0.38, v0: 0.58, v1: 0.88, c: nCols[0] }, // Post-it amarelo
          { u0: 0.42, u1: 0.70, v0: 0.58, v1: 0.88, c: nCols[1] }, // Post-it rosa
          { u0: 0.73, u1: 0.95, v0: 0.52, v1: 0.82, c: nCols[2] }, // Post-it azul
          { u0: 0.12, u1: 0.40, v0: 0.14, v1: 0.46, c: nCols[3] }, // Post-it verde
          { u0: 0.44, u1: 0.72, v0: 0.14, v1: 0.46, c: nCols[4] }, // Post-it laranja
          { u0: 0.74, u1: 0.96, v0: 0.16, v1: 0.44, c: nCols[5] }  // Post-it lilás
        ];

        for (const nl of noteLocs) {
          const np1 = lerpP(lerpP(innerP1, innerP2, nl.u0), lerpP(innerP4, innerP3, nl.u0), nl.v0);
          const np2 = lerpP(lerpP(innerP1, innerP2, nl.u1), lerpP(innerP4, innerP3, nl.u1), nl.v0);
          const np3 = lerpP(lerpP(innerP1, innerP2, nl.u1), lerpP(innerP4, innerP3, nl.u1), nl.v1);
          const np4 = lerpP(lerpP(innerP1, innerP2, nl.u0), lerpP(innerP4, innerP3, nl.u0), nl.v1);
          drawQuad(np1, np2, np3, np4, nl.c);

          // Tachinha vermelha ou dourada no topo
          const pinP = lerpP(np4, np3, 0.5);
          lowCtx.fillStyle = '#EF4444';
          lowCtx.fillRect(pinP.x - 1, pinP.y - 1, 2, 2);
        }
      } else if (type === 'cat') {
        // Arte: Retrato do Gato
        const catHead1 = lerpP(lerpP(p1, p2, 0.25), lerpP(p4, p3, 0.25), 0.35);
        const catHead2 = lerpP(lerpP(p1, p2, 0.75), lerpP(p4, p3, 0.75), 0.35);
        const catHead3 = lerpP(lerpP(p1, p2, 0.75), lerpP(p4, p3, 0.75), 0.75);
        const catHead4 = lerpP(lerpP(p1, p2, 0.25), lerpP(p4, p3, 0.25), 0.75);
        drawQuad(catHead1, catHead2, catHead3, catHead4, '#DE864A');

        const earL1 = lerpP(catHead4, catHead3, 0.15);
        const earL2 = lerpP(catHead4, catHead3, 0.40);
        const earL3 = lerpP(lerpP(p1, p2, 0.30), lerpP(p4, p3, 0.30), 0.90);
        lowCtx.fillStyle = '#3B2219';
        lowCtx.beginPath(); lowCtx.moveTo(earL1.x, earL1.y); lowCtx.lineTo(earL2.x, earL2.y); lowCtx.lineTo(earL3.x, earL3.y); lowCtx.closePath(); lowCtx.fill();

        const earR1 = lerpP(catHead4, catHead3, 0.60);
        const earR2 = lerpP(catHead4, catHead3, 0.85);
        const earR3 = lerpP(lerpP(p1, p2, 0.70), lerpP(p4, p3, 0.70), 0.90);
        lowCtx.beginPath(); lowCtx.moveTo(earR1.x, earR1.y); lowCtx.lineTo(earR2.x, earR2.y); lowCtx.lineTo(earR3.x, earR3.y); lowCtx.closePath(); lowCtx.fill();

        const eyeL = lerpP(lerpP(p1, p2, 0.38), lerpP(p4, p3, 0.38), 0.55);
        const eyeR = lerpP(lerpP(p1, p2, 0.62), lerpP(p4, p3, 0.62), 0.55);
        lowCtx.fillStyle = '#3B2219';
        lowCtx.fillRect(eyeL.x - 1, eyeL.y - 1, 3, 3);
        lowCtx.fillRect(eyeR.x - 1, eyeR.y - 1, 3, 3);
      } else {
        // Arte: Botânica Verde
        const c1 = lerpP(lerpP(p1, p2, 0.4), lerpP(p4, p3, 0.4), 0.2);
        const c2 = lerpP(lerpP(p1, p2, 0.6), lerpP(p4, p3, 0.6), 0.2);
        const c3 = lerpP(lerpP(p1, p2, 0.6), lerpP(p4, p3, 0.6), 0.8);
        const c4 = lerpP(lerpP(p1, p2, 0.4), lerpP(p4, p3, 0.4), 0.8);
        drawQuad(c1, c2, c3, c4, '#4D8A48');

        const h1 = lerpP(lerpP(p1, p2, 0.2), lerpP(p4, p3, 0.2), 0.4);
        const h2 = lerpP(lerpP(p1, p2, 0.8), lerpP(p4, p3, 0.8), 0.4);
        const h3 = lerpP(lerpP(p1, p2, 0.8), lerpP(p4, p3, 0.8), 0.6);
        const h4 = lerpP(lerpP(p1, p2, 0.2), lerpP(p4, p3, 0.2), 0.6);
        drawQuad(h1, h2, h3, h4, '#4D8A48');
      }

      // Moldura 3D saliente
      const pad = 2.5;
      const fOut1 = project(xWall - frameThick, y0 - pad, z0 - pad);
      const fOut2 = project(xWall - frameThick, y1 + pad, z0 - pad);
      const fOut3 = project(xWall - frameThick, y1 + pad, z1 + pad);
      const fOut4 = project(xWall - frameThick, y0 - pad, z1 + pad);

      const fIn1 = project(xWall - frameThick, y0, z0);
      const fIn2 = project(xWall - frameThick, y1, z0);
      const fIn3 = project(xWall - frameThick, y1, z1);
      const fIn4 = project(xWall - frameThick, y0, z1);

      drawQuad(fOut1, fOut2, fIn2, fIn1, '#804E2B');
      drawQuad(fIn4, fIn3, fOut3, fOut4, '#9E6740');
      drawQuad(fOut1, fIn1, fIn4, fOut4, '#6B3E1E');
      drawQuad(fIn2, fOut2, fOut3, fIn3, '#804E2B');

      const wOut1 = project(xWall - 0.5, y0 - pad, z0 - pad);
      const wOut2 = project(xWall - 0.5, y1 + pad, z0 - pad);
      const wOut3 = project(xWall - 0.5, y1 + pad, z1 + pad);
      const wOut4 = project(xWall - 0.5, y0 - pad, z1 + pad);

      drawQuad(fOut1, fOut2, wOut2, wOut1, '#532F16');
      drawQuad(fOut4, fOut3, wOut3, wOut4, '#6B3E1E');
    }

    // --- ÁUDIO RETRO PROCEDURAL (Web Audio API - Zero assets externos!) ---
    let audioCtx = null;
    function playMeowSound() {
      try {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
          audioCtx.resume();
        }
        const now = audioCtx.currentTime;

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();

        // Miau fofinho com modulação de frequência (460Hz -> 760Hz -> 540Hz)
        osc.type = 'sine';
        osc.frequency.setValueAtTime(460, now);
        osc.frequency.exponentialRampToValueAtTime(760, now + 0.12);
        osc.frequency.exponentialRampToValueAtTime(540, now + 0.32);

        // Envelope acústico macio
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.exponentialRampToValueAtTime(0.20, now + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.15, now + 0.22);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        // Purr vibrato LFO
        const lfo = audioCtx.createOscillator();
        const lfoGain = audioCtx.createGain();
        lfo.frequency.value = 22;
        lfoGain.gain.value = 16;
        lfo.connect(osc.frequency);
        lfo.start(now);
        lfo.stop(now + 0.35);

        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
      } catch (err) {}
    }

    function triggerPetReactions(cat) {
      if (!cat) return;
      playMeowSound();

      // Coraçõezinhos flutuantes
      const p = project(cat.x, cat.y, 24);
      for (let i = 0; i < 8; i++) {
        hearts.push({
          x: p.x + (Math.random() * 28 - 14),
          y: p.y - (Math.random() * 20),
          alpha: 1.0
        });
      }

      // Balão de fala carinhoso
      const phrases = ['Purrr... ♥', 'Miau! ♪', 'Nyaa~ ✨', 'Awnn! ♥', 'Meow~ 💕'];
      const text = phrases[Math.floor(Math.random() * phrases.length)];
      cat.speech = { text, timer: 120 };

      // Reação corporal: 50% de chance de rolar e mostrar a barriguinha!
      if (!cat.forcedPosture || cat.forcedPosture === 'auto') {
        if (Math.random() < 0.55) {
          cat.posture = 'belly';
          cat.bellyTimer = 180; // 3 segundos curtindo carinho na barriga
        } else {
          cat.posture = 'sit';
          cat.stateTimer = 120;
        }
      }
    }

    function drawLoafZzz(cat) {
      const p = project(cat.x, cat.y, 22 * cat.scale);
      const time = (cat.idleTimer || 0);
      const zzzOffset = (time * 1.5) % 3;
      const alpha = Math.max(0, 1 - (zzzOffset / 3));

      lowCtx.save();
      lowCtx.fillStyle = `rgba(100, 130, 180, ${alpha * 0.85})`;
      lowCtx.font = 'bold 8px monospace';
      lowCtx.fillText('Z', p.x + 8 + zzzOffset * 2, p.y - zzzOffset * 6);
      if (zzzOffset > 0.8) {
        lowCtx.fillText('z', p.x + 13 + (zzzOffset - 0.8) * 3, p.y - 4 - (zzzOffset - 0.8) * 8);
      }
      if (zzzOffset > 1.6) {
        lowCtx.fillText('z', p.x + 18 + (zzzOffset - 1.6) * 4, p.y - 8 - (zzzOffset - 1.6) * 10);
      }
      lowCtx.restore();
    }

    function drawCatSpeech(cat) {
      if (!cat.speech) return;
      if (typeof cat.speech === 'string') {
        cat.speech = { text: cat.speech, timer: 160 };
      }
      if (cat.speech.timer <= 0) {
        cat.speech = null;
        return;
      }
      cat.speech.timer--;

      const p = project(cat.x, cat.y, 26 * cat.scale);
      const text = cat.speech.text;
      if (!text || text === 'undefined') return;

      lowCtx.save();
      lowCtx.font = 'bold 9px sans-serif';
      const tw = lowCtx.measureText(text).width;
      const bw = tw + 10;
      const bh = 14;
      const bx = Math.round(p.x - bw / 2);
      const by = Math.round(p.y - 18);

      // Balão de fala pixel art
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.strokeStyle = '#3B2219';
      lowCtx.lineWidth = 1;
      lowCtx.fillRect(bx, by, bw, bh);
      lowCtx.strokeRect(bx, by, bw, bh);

      // Rabicho do balão
      lowCtx.fillStyle = '#FFFFFF';
      lowCtx.beginPath();
      lowCtx.moveTo(p.x - 3, by + bh);
      lowCtx.lineTo(p.x, by + bh + 4);
      lowCtx.lineTo(p.x + 3, by + bh);
      lowCtx.fill();

      lowCtx.fillStyle = '#E63946';
      lowCtx.fillText(text, bx + 5, by + 10);
      lowCtx.restore();
    }

    // --- GATINHO 3D COM PATINHAS ARTICULADAS E ANIMAÇÃO PROCEDURAL ---
    function drawCat(cat, baseLiftZ = 0) {
      const posture = cat.forcedPosture || cat.posture || (cat.isWalking ? 'walk' : 'stand');
      const t = cat.walkCycle || 0;
      const isWalking = (posture === 'walk' || cat.isWalking) && (!isDraggingItem || selectedItem !== cat);

      const cosA = Math.cos(cat.selfAngle);
      const sinA = Math.sin(cat.selfAngle);

      function renderPaw(lx, ly, lift, stride, pawZ = 0, angleOffset = 0) {
        const wx = cat.x + lx * cosA - (ly + stride) * sinA;
        const wy = cat.y + lx * sinA + (ly + stride) * cosA;
        const wz = baseLiftZ + lift + pawZ;
        drawStackObject(catSkinModels[currentCatSkin].paw, wx, wy, wz, cat.selfAngle + angleOffset, cat.scale);
      }

      function renderHat(headZ, headPitchOffset = 0, rollOffset = 0) {
        if (!cat.hat || cat.hat === 'none') return;
        const hatModel = HATS[cat.hat];
        if (!hatModel) return;
        const hx = cat.x - (4.5 + headPitchOffset) * sinA;
        const hy = cat.y + (4.5 + headPitchOffset) * cosA;
        const hz = baseLiftZ + (headZ - 2.8) * cat.scale; // Ajuste fino: chapéu pousado perfeitamente no cocuruto entre as orelhinhas
        drawStackObject(hatModel, hx, hy, hz, cat.selfAngle + rollOffset, cat.scale);
      }

      if (posture === 'belly') {
        // === MOSTRAR A BARRIGUINHA (BELLY ROLL) COM CABECINHA DOBRADA OLHANDO PRA BARRIGA ===
        // O corpo apoia suavemente na espinha (chão Z=0) e a cabeça curva para frente sem encostar orelhas no chão!
        const bellyWiggle = Math.sin((cat.idleTimer || 0) * 4) * 0.05;
        drawStackObject(catSkinModels[currentCatSkin].belly, cat.x, cat.y, baseLiftZ + 0.5, cat.selfAngle + bellyWiggle, cat.scale);

        // 4 patinhas fofas abanando no ar acima da barriguinha!
        const pawTime = (cat.idleTimer || 0) * 5;
        const pBL = Math.sin(pawTime) * 1.5;
        const pBR = Math.sin(pawTime + 1.2) * 1.5;
        const pFL = Math.sin(pawTime + 2.4) * 1.5;
        const pFR = Math.sin(pawTime + 3.6) * 1.5;

        renderPaw(-4.0, -4.0, 0, 0, 7.5 + pBL, 0.4);
        renderPaw( 3.0, -4.0, 0, 0, 7.5 + pBR, -0.4);
        renderPaw(-4.0,  2.5, 0, 0, 8.0 + pFL, 0.3);
        renderPaw( 3.0,  2.5, 0, 0, 8.0 + pFR, -0.3);

        // Chapéu na cabecinha dobrada (na testa/orelhas voltadas para trás)
        renderHat(7.2, 3.5, 0.2);

      } else if (posture === 'loaf') {
        // === DEITAR / PÃOZINHO (LOAF) ===
        // 4 patinhas 100% escondidas sob o corpo, corpo no chão
        const loafBreathe = Math.sin((cat.idleTimer || 0) * 1.8) * 0.35;
        drawStackObject(catSkinModels[currentCatSkin].body, cat.x, cat.y, baseLiftZ - 2.2 + loafBreathe, cat.selfAngle, cat.scale);
        renderHat(12.0 + loafBreathe);
        drawLoafZzz(cat);

      } else if (posture === 'sit') {
        // === SENTAR (SIT) ===
        // Patas dianteiras apoiadas, traseiras recolhidas, traseira rebaixada
        renderPaw(-4.5, 3.5, 0, 0);
        renderPaw( 3.5, 3.5, 0, 0);
        const sitBreathe = Math.sin((cat.idleTimer || 0) * 2.0) * 0.3;
        drawStackObject(catSkinModels[currentCatSkin].body, cat.x, cat.y, baseLiftZ - 1.2 + sitBreathe, cat.selfAngle, cat.scale);
        renderHat(13.2 + sitBreathe);

      } else {
        // === ANDAR OU EM PÉ (WALK / STAND) ===
        const liftFL = isWalking ? Math.max(0, Math.sin(t) * 3.5) : 0;
        const strideFL = isWalking ? -Math.cos(t) * 2.5 : 0;

        const liftBR = isWalking ? Math.max(0, Math.sin(t + 0.3) * 3.5) : 0;
        const strideBR = isWalking ? -Math.cos(t + 0.3) * 2.5 : 0;

        const liftFR = isWalking ? Math.max(0, Math.sin(t + Math.PI) * 3.5) : 0;
        const strideFR = isWalking ? -Math.cos(t + Math.PI) * 2.5 : 0;

        const liftBL = isWalking ? Math.max(0, Math.sin(t + Math.PI + 0.3) * 3.5) : 0;
        const strideBL = isWalking ? -Math.cos(t + Math.PI + 0.3) * 2.5 : 0;

        const bodyBob = isWalking ? Math.abs(Math.sin(t * 2)) * 0.8 : Math.sin((cat.idleTimer || 0) * 2.2) * 0.4;
        const bodyRoll = isWalking ? Math.sin(t) * 0.04 : 0;

        renderPaw(-4.5, -7.5, liftBL, strideBL); // Traseira esquerda
        renderPaw( 3.5, -7.5, liftBR, strideBR); // Traseira direita
        renderPaw(-4.5,  3.5, liftFL, strideFL); // Dianteira esquerda
        renderPaw( 3.5,  3.5, liftFR, strideFR); // Dianteira direita

        drawStackObject(catSkinModels[currentCatSkin].body, cat.x, cat.y, baseLiftZ + bodyBob, cat.selfAngle + bodyRoll, cat.scale);
        renderHat(14.8 + bodyBob, 0, bodyRoll);
      }

      drawCatSpeech(cat);
    }

    // Funções Auxiliares de Restrição para Plataformas (Mesa e Prateleira)
    function constrainToDesk(x, y, margin = 4) {
      const desk = items.find(it => it.id === 'desk');
      if (!desk) return { x, y };
      const cosD = Math.cos(desk.selfAngle);
      const sinD = Math.sin(desk.selfAngle);
      const rwx = x - desk.x;
      const rwy = y - desk.y;
      let localX =  rwx * cosD + rwy * sinD;
      let localY = -rwx * sinD + rwy * cosD;
      const limitX = 36 - margin;
      const limitY = 14 - margin;
      localX = Math.max(-limitX, Math.min(limitX, localX));
      localY = Math.max(-limitY, Math.min(limitY, localY));
      return {
        x: desk.x + localX * cosD - localY * sinD,
        y: desk.y + localX * sinD + localY * cosD
      };
    }

    function constrainToShelf(y, margin = 6) {
      const shelf = items.find(it => it.id === 'shelf');
      if (!shelf) return { x: -ROOM_R + 9, y };
      const minY = shelf.y - shelf.length / 2 + margin;
      const maxY = shelf.y + shelf.length / 2 - margin;
      return {
        x: -ROOM_R + 9,
        y: Math.max(minY, Math.min(maxY, y))
      };
    }

    // Sistema de Colisão e Navegação do Gatinho com Móveis e Paredes
    function checkCatCollision(nx, ny) {
      // 1. Limites com as paredes do quarto
      const wallLimit = ROOM_R - 16;
      nx = Math.max(-wallLimit, Math.min(wallLimit, nx));
      ny = Math.max(-wallLimit, Math.min(wallLimit, ny));

      const catRad = 12;

      // 2. Colisão com a Mesa de Estudo Ampliada (80x36, caixa AABB orientada)
      const desk = items.find(it => it.id === 'desk');
      if (desk && desk.visible !== false) {
        const isRot = (desk.selfAngle === Math.PI / 2 || desk.selfAngle === Math.PI * 1.5);
        const halfW = (isRot ? 20 : 42) + catRad;
        const halfH = (isRot ? 42 : 20) + catRad;
        if (Math.abs(nx - desk.x) < halfW && Math.abs(ny - desk.y) < halfH) {
          const overlapX = halfW - Math.abs(nx - desk.x);
          const overlapY = halfH - Math.abs(ny - desk.y);
          if (overlapX < overlapY) {
            nx = desk.x + (nx > desk.x ? halfW : -halfW);
          } else {
            ny = desk.y + (ny > desk.y ? halfH : -halfH);
          }
        }
      }

      // 3. Colisão com outros móveis de chão (Torre de Gato, Caminha, Planta, etc.)
      const floorObstacles = items.filter(it => 
        it.visible !== false && 
        !it.isCat && 
        !it.isWallItem && 
        it.surface !== 'desk' && 
        it.surface !== 'shelf' && 
        it.id !== 'desk'
      );

      for (const obs of floorObstacles) {
        const obsRad = (obs.radius ? obs.radius * 0.75 : 16) + catRad;
        const dx = nx - obs.x;
        const dy = ny - obs.y;
        const dist = Math.hypot(dx, dy);
        if (dist < obsRad && dist > 0.001) {
          const push = obsRad - dist;
          nx += (dx / dist) * push;
          ny += (dy / dist) * push;
        }
      }

      return { x: nx, y: ny };
    }


    // --- GALINHA POPÓ 3D ARTICULADA (Andar, Rebolado, Ciscar e Chocar) ---
    function drawChicken(chk, baseLiftZ = 0) {
      const t = chk.animTime || 0;
      const isWalking = chk.isWalking && (!isDraggingItem || selectedItem !== chk);
      const isPecking = (chk.state === 'peck') && (!isDraggingItem || selectedItem !== chk);
      const isBrooding = (chk.state === 'brood');
      const chkAngle = chk.selfAngle + turn;

      const isBabyChick = (chk.id === 'chick');
      const activeLegL = isBabyChick ? chickLegL : chickenLegL;
      const activeLegR = isBabyChick ? chickLegR : chickenLegR;
      const activeUpper = isBabyChick ? chickUpper : chickenUpper;
      const legCount = isBabyChick ? 2 : 4;

      let legLOffX = 0, legLLiftZ = 0;
      let legROffX = 0, legRLiftZ = 0;
      let bodyBobZ = 0, rollWobble = 0;
      let headOffX = 0, headOffZ = 0;

      if (isWalking) {
        const swingDist = isBabyChick ? 2.4 : 3.2;
        const maxLift = isBabyChick ? 1.8 : 2.4;
        const speed = isBabyChick ? 0.75 : 0.55;

        function getLegPose(phase) {
          const u = ((phase % 1) + 1) % 1;
          if (u < 0.5) {
            const p = u / 0.5;
            return { offX: -swingDist + (2 * swingDist) * p, liftZ: Math.sin(p * Math.PI) * maxLift };
          } else {
            const p = (u - 0.5) / 0.5;
            return { offX: swingDist - (2 * swingDist) * p, liftZ: 0 };
          }
        }

        const uL = t * speed;
        const uR = uL + 0.5;
        const legL = getLegPose(uL);
        const legR = getLegPose(uR);
        legLOffX = legL.offX; legLLiftZ = legL.liftZ;
        legROffX = legR.offX; legRLiftZ = legR.liftZ;

        rollWobble = Math.sin(t * (isBabyChick ? 4.5 : 3.4)) * (isBabyChick ? 0.16 : 0.12);
        bodyBobZ = Math.abs(Math.sin(t * (isBabyChick ? 4.5 : 3.4))) * (isBabyChick ? 1.6 : 1.3);
        headOffX = Math.sin(t * 3.4) * (isBabyChick ? 1.2 : 2.2);
      } else if (isPecking) {
        // Ciscando
        const cycle = (t * 2.4) % (Math.PI * 2);
        if (cycle < Math.PI * 0.35) {
          const p = Math.sin((cycle / (Math.PI * 0.35)) * Math.PI * 0.5);
          headOffX = p * (isBabyChick ? 2.8 : 4.5);
          headOffZ = -p * (isBabyChick ? 1.2 : 1.5);
        } else if (cycle < Math.PI * 0.70) {
          const p = (cycle - Math.PI * 0.35) / (Math.PI * 0.35);
          const pSin = Math.sin(p * Math.PI * 0.5);
          headOffX = (isBabyChick ? 2.8 : 4.5) + pSin * (isBabyChick ? 0.5 : 0.8);
          headOffZ = (isBabyChick ? -1.2 : -1.5) - pSin * (isBabyChick ? 3.5 : 5.0);
        } else if (cycle < Math.PI * 1.10) {
          const p = (cycle - Math.PI * 0.70) / (Math.PI * 0.40);
          headOffX = (isBabyChick ? 3.3 : 5.3) * (1 - p * 0.3);
          headOffZ = (isBabyChick ? -4.7 : -6.5) * (1 - p);
        } else {
          const p = (cycle - Math.PI * 1.10) / (Math.PI * 0.90);
          headOffX = (isBabyChick ? 2.3 : 3.7) * (1 - p);
          headOffZ = 0;
        }

        // Grãozinhos de milho
        const pFloor = project(chk.x, chk.y, baseLiftZ);
        const dist = (isBabyChick ? 8 : 11) * chk.scale;
        const seedX = pFloor.x + Math.cos(chkAngle) * dist;
        const seedY = pFloor.y + Math.sin(chkAngle) * dist * squash;
        lowCtx.fillStyle = '#F59E0B';
        if (isBabyChick) {
          lowCtx.fillRect(seedX, seedY, 2, 2);
        } else {
          lowCtx.fillRect(seedX - 2, seedY - 1, 3, 2);
          lowCtx.fillRect(seedX + 3, seedY + 1, 2, 2);
        }
      } else if (isBrooding) {
        bodyBobZ = isBabyChick ? -1.8 : -3.2;
      } else {
        bodyBobZ = Math.sin(t * 1.5) * (isBabyChick ? 0.3 : 0.4);
      }

      const zStep = (isBabyChick ? 1.15 : 1.35) * chk.scale;
      const baseDim = isBabyChick ? 18 : 24;
      const sw = baseDim * chk.scale;
      const sh = baseDim * chk.scale;

      // 1. Patas
      if (!isBrooding) {
        for (let i = 0; i < legCount; i++) {
          // Pata Esquerda
          const zL = baseLiftZ + (i + legLLiftZ) * (chk.scale || 1.35);
          const pL = project(chk.x, chk.y, zL);
          const sxL = pL.x + (legLOffX * Math.cos(chkAngle)) * chk.scale;
          const syL = pL.y + (legLOffX * Math.sin(chkAngle)) * chk.scale * squash;
          lowCtx.save();
          lowCtx.translate(sxL, syL);
          lowCtx.scale(1, squash);
          lowCtx.rotate(chkAngle);
          lowCtx.drawImage(activeLegL[i], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();

          // Pata Direita
          const zR = baseLiftZ + (i + legRLiftZ) * (chk.scale || 1.35);
          const pR = project(chk.x, chk.y, zR);
          const sxR = pR.x + (legROffX * Math.cos(chkAngle)) * chk.scale;
          const syR = pR.y + (legROffX * Math.sin(chkAngle)) * chk.scale * squash;
          lowCtx.save();
          lowCtx.translate(sxR, syR);
          lowCtx.scale(1, squash);
          lowCtx.rotate(chkAngle);
          lowCtx.drawImage(activeLegR[i], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();
        }
      }

      // 2. Corpo & Cabeça
      if (isBabyChick) {
        if (chk.hat && chk.hat !== 'none') {
          // === PINTINHO ESCONDIDO DENTRO DO CHAPÉU GIGANTE (Oversized Walking Hat!) ===
          const hatModel = HATS[chk.hat];
          if (hatModel) {
            // O chapéu cobre o pintinho por inteiro com proporção cômica fofa
            const hatScale = 1.45; // Chapéu grandão que realmente cobre a bolinha
            const hatZ = baseLiftZ + (0.5 + bodyBobZ) * (chk.scale || 1.35);

            // Silhueta amarela aconchegada dentro do chapéu (apenas visível por leve transparência interna)
            lowCtx.save();
            lowCtx.globalAlpha = 0.40;
            const totalUpper = activeUpper.length;
            const innerScale = (chk.scale || 1.35) * 0.75; // Reduzido para caber 100% dentro da copa do chapéu
            const isw = baseDim * innerScale;
            const ish = baseDim * innerScale;
            for (let i = 0; i < totalUpper; i++) {
              const zIndex = i + 1;
              const z = baseLiftZ + (zIndex + bodyBobZ) * innerScale;
              const p = project(chk.x, chk.y, z);
              lowCtx.save();
              lowCtx.translate(p.x, p.y);
              lowCtx.scale(1, squash);
              lowCtx.rotate(chkAngle + rollWobble);
              lowCtx.drawImage(activeUpper[i], -isw / 2, -ish / 2, isw, ish);
              lowCtx.restore();
            }
            lowCtx.restore();

            // Chapéu grandão com 92% de opacidade assentado sobre ele
            lowCtx.save();
            lowCtx.globalAlpha = 0.92;
            drawStackObject(hatModel, chk.x, chk.y, hatZ, chk.selfAngle + rollWobble * 1.5, hatScale);
            lowCtx.restore();

            // Olhinhos pretos brilhantes e biquinho laranja espiando pela aba frontal do chapéu!
            const peekZ = baseLiftZ + (2.8 + bodyBobZ) * (chk.scale || 1.35);
            const pFace = project(chk.x, chk.y, peekZ);
            const faceDist = 6.2 * (chk.scale || 1.35);
            const fx = pFace.x + Math.cos(chkAngle) * faceDist;
            const fy = pFace.y + Math.sin(chkAngle) * faceDist * squash;
            lowCtx.save();
            lowCtx.translate(fx, fy);
            // Olho esquerdo
            lowCtx.fillStyle = '#1A1A1A';
            lowCtx.fillRect(-4, -2, 2, 2);
            lowCtx.fillStyle = '#FFFFFF';
            lowCtx.fillRect(-4, -2, 1, 1);
            // Olho direito
            lowCtx.fillStyle = '#1A1A1A';
            lowCtx.fillRect(3, -2, 2, 2);
            lowCtx.fillStyle = '#FFFFFF';
            lowCtx.fillRect(3, -2, 1, 1);
            // Biquinho laranja fofo
            lowCtx.fillStyle = '#F97316';
            lowCtx.fillRect(-1, 0, 3, 2);
            lowCtx.restore();

            return;
          }
        }

        // O pintinho é uma bolinha unificada (slices 2 a 9)
        const totalUpper = activeUpper.length;
        for (let i = 0; i < totalUpper; i++) {
          const zIndex = i + 2;
          // As camadas superiores (olhos e bico) mergulham junto ao ciscar
          const hRatio = i >= 4 ? (i - 3) / 5 : 0;
          const z = baseLiftZ + (zIndex + bodyBobZ + headOffZ * hRatio) * (chk.scale || 1.35);
          const p = project(chk.x, chk.y, z);
          const sx = p.x + (headOffX * hRatio * Math.cos(chkAngle)) * chk.scale;
          const sy = p.y + (headOffX * hRatio * Math.sin(chkAngle)) * chk.scale * squash;
          lowCtx.save();
          lowCtx.translate(sx, sy);
          lowCtx.scale(1, squash);
          lowCtx.rotate(chkAngle + rollWobble);
          lowCtx.drawImage(activeUpper[i], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();
        }
      } else {
        // Galinha Adulta Popó: Corpo (4..9) e Cabeça (10..15)
        for (let i = 4; i <= 9; i++) {
          const z = baseLiftZ + (i + bodyBobZ) * (chk.scale || 1.35);
          const p = project(chk.x, chk.y, z);
          lowCtx.save();
          lowCtx.translate(p.x, p.y);
          lowCtx.scale(1, squash);
          lowCtx.rotate(chkAngle + rollWobble);
          lowCtx.drawImage(activeUpper[i - 4], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();
        }

        for (let i = 10; i < __CHICKEN_SLICES__.length; i++) {
          const z = baseLiftZ + (i + bodyBobZ + headOffZ) * (chk.scale || 1.35);
          const p = project(chk.x, chk.y, z);
          const sx = p.x + (headOffX * Math.cos(chkAngle)) * chk.scale;
          const sy = p.y + (headOffX * Math.sin(chkAngle)) * chk.scale * squash;
          lowCtx.save();
          lowCtx.translate(sx, sy);
          lowCtx.scale(1, squash);
          lowCtx.rotate(chkAngle + rollWobble);
          lowCtx.drawImage(activeUpper[i - 4], -sw / 2, -sh / 2, sw, sh);
          lowCtx.restore();
        }

        // Chapéu charmoso inclinado ao lado da crista da Galinha Popó
        if (chk.hat && chk.hat !== 'none') {
          const hatModel = HATS[chk.hat];
          if (hatModel) {
            const headForward = (6.0 + headOffX) * (chk.scale || 1.35);
            const hx = chk.x + headForward * Math.cos(chkAngle - turn);
            const hy = chk.y + headForward * Math.sin(chkAngle - turn);
            const hz = baseLiftZ + (12.8 + bodyBobZ + headOffZ) * (chk.scale || 1.35);
            drawStackObject(hatModel, hx, hy, hz, chk.selfAngle + 0.18, 0.78);
          }
        }
      }
    }

    // IA Autônoma das Aves (Popó e Pintinho Piu): Passeiam rebolando, ciscam e descansam
    function updateChickenAI() {
      const chickens = items.filter(it => it.isChicken && it.visible !== false);
      const desk = items.find(it => it.id === 'desk' && it.visible !== false);
      const shelf = items.find(it => it.id === 'shelf' && it.visible !== false);

      chickens.forEach(chk => {
        chk.animTime = (chk.animTime || 0) + 0.08;

        if (isDecorMode && isDraggingItem && selectedItem === chk) {
          chk.state = 'idle';
          chk.isWalking = false;
          return;
        }

        const isBabyChick = (chk.id === 'chick');

        // === 1. COMPORTAMENTO EM PLATAFORMAS (MESA OU PRATELEIRA) ===
        if (chk.surface === 'desk' && desk) {
          chk.liftZ = 21;
          chk.stateTimer = (chk.stateTimer || 100) - 1;
          if (chk.stateTimer <= 0) {
            const r = Math.random();
            if (isBabyChick) {
              // Pintinho NÃO consegue descer! Fica sanzando pelo tampo!
              if (r < 0.50) {
                chk.state = 'walk';
                chk.stateTimer = 70 + Math.floor(Math.random() * 60);
                const targetP = constrainToDesk(desk.x + (Math.random() - 0.5) * 48, desk.y + (Math.random() - 0.5) * 18, 4);
                chk.targetX = targetP.x;
                chk.targetY = targetP.y;
                chk.isWalking = true;
              } else if (r < 0.85) {
                chk.state = 'peck';
                chk.stateTimer = 60 + Math.floor(Math.random() * 60);
                chk.isWalking = false;
                if (Math.random() < 0.4) playChickenSound();
              } else {
                chk.state = 'idle';
                chk.stateTimer = 60;
                chk.isWalking = false;
              }
            } else {
              // Galinha adulta na mesa pode ciscar ou pular pro chão
              if (r < 0.35) {
                chk.surface = null;
                chk.liftZ = 0;
                chk.x = desk.x + 24;
                chk.y = desk.y + 28;
                chk.state = 'peck';
                chk.stateTimer = 80;
                chk.isWalking = false;
                playChickenSound();
              } else if (r < 0.70) {
                chk.state = 'peck';
                chk.stateTimer = 80;
                chk.isWalking = false;
              } else {
                chk.state = 'idle';
                chk.stateTimer = 70;
                chk.isWalking = false;
              }
            }
          }

          if (chk.state === 'walk') {
            const dx = (chk.targetX || chk.x) - chk.x;
            const dy = (chk.targetY || chk.y) - chk.y;
            const dist = Math.hypot(dx, dy);
            if (dist > 3) {
              const moveSpeed = isBabyChick ? 0.38 : 0.45;
              const targetAngle = Math.atan2(dy, dx);
              let diff = targetAngle - chk.selfAngle;
              while (diff < -Math.PI) diff += Math.PI * 2;
              while (diff > Math.PI) diff -= Math.PI * 2;
              chk.selfAngle += diff * 0.12;

              const nextX = chk.x + Math.cos(chk.selfAngle) * moveSpeed;
              const nextY = chk.y + Math.sin(chk.selfAngle) * moveSpeed;
              const clamped = constrainToDesk(nextX, nextY, 4);
              chk.x = clamped.x;
              chk.y = clamped.y;
              chk.isWalking = true;
            } else {
              chk.state = 'peck';
              chk.stateTimer = 70;
              chk.isWalking = false;
            }
          }
          return;
        }

        if (chk.surface === 'shelf' && shelf) {
          chk.liftZ = shelf.liftZ + 3.5;
          chk.stateTimer = (chk.stateTimer || 120) - 1;

          if (isBabyChick) {
            // Pintinho na prateleira NÃO desce! Sanza para lá e para cá sem cair!
            if (chk.stateTimer <= 0) {
              const r = Math.random();
              if (r < 0.55) {
                chk.state = 'walk';
                chk.stateTimer = 70 + Math.floor(Math.random() * 50);
                const targetY = shelf.y + (-shelf.length / 2 + 10 + Math.random() * (shelf.length - 20));
                chk.targetX = -ROOM_R + 9;
                chk.targetY = targetY;
                chk.isWalking = true;
              } else if (r < 0.85) {
                chk.state = 'peck';
                chk.stateTimer = 60 + Math.floor(Math.random() * 50);
                chk.isWalking = false;
                if (Math.random() < 0.4) playChickenSound();
              } else {
                chk.state = 'idle';
                chk.stateTimer = 60;
                chk.isWalking = false;
              }
            }

            if (chk.state === 'walk') {
              const dy = (chk.targetY || chk.y) - chk.y;
              if (Math.abs(dy) > 2) {
                const moveSpeed = 0.32;
                chk.selfAngle = dy > 0 ? Math.PI / 2 : -Math.PI / 2;
                const nextY = chk.y + (dy > 0 ? moveSpeed : -moveSpeed);
                const clamped = constrainToShelf(nextY, 8);
                chk.x = clamped.x;
                chk.y = clamped.y;
                chk.isWalking = true;
              } else {
                chk.state = 'peck';
                chk.stateTimer = 60;
                chk.isWalking = false;
              }
            }
            return;
          } else {
            // Galinha Popó na prateleira dorme/choca no ninho entre os livros!
            chk.state = 'brood';
            chk.isWalking = false;
            if (chk.stateTimer <= 0) {
              if (Math.random() < 0.55) {
                // Voa/desce da prateleira para o chão suavemente!
                chk.surface = null;
                chk.liftZ = 0;
                chk.x = -ROOM_R + 32;
                chk.y = shelf.y + (Math.random() - 0.5) * 16;
                chk.state = 'peck';
                chk.stateTimer = 90;
                chk.isWalking = false;
                playChickenSound();
                hearts.push({ x: chk.x, y: chk.y, z: 12, life: 1.0 });
              } else {
                // Continua chocando confortavelmente
                chk.stateTimer = 180 + Math.floor(Math.random() * 150);
              }
            }
            return;
          }
        }

        // === 2. COMPORTAMENTO NO CHÃO ===
        // Se a galinha adulta Popó estiver no chão perto da prateleira, pode voar/subir nela!
        if (!isBabyChick && shelf && Math.abs(chk.x - (-ROOM_R + 28)) < 22 && Math.abs(chk.y - shelf.y) < 28 && Math.random() < 0.08) {
          chk.surface = 'shelf';
          chk.liftZ = shelf.liftZ + 3.5;
          chk.x = -ROOM_R + 9;
          chk.y = shelf.y + (Math.random() - 0.5) * 12;
          chk.state = 'brood';
          chk.stateTimer = 260 + Math.floor(Math.random() * 180);
          chk.isWalking = false;
          playChickenSound();
          hearts.push({ x: chk.x, y: chk.y, z: chk.liftZ + 12, life: 1.0 });
          return;
        }

        // Caminhar normal no chão
        chk.stateTimer = (chk.stateTimer || 100) - 1;
        if (chk.stateTimer <= 0) {
          const r = Math.random();
          if (r < 0.40) {
            chk.state = 'walk';
            chk.stateTimer = 90 + Math.floor(Math.random() * 80);
            chk.targetX = -ROOM_R * 0.7 + Math.random() * (ROOM_R * 1.4);
            chk.targetY = -ROOM_R * 0.7 + Math.random() * (ROOM_R * 1.4);
            chk.isWalking = true;
          } else if (r < 0.75) {
            chk.state = 'peck';
            chk.stateTimer = 80 + Math.floor(Math.random() * 90);
            chk.isWalking = false;
            if (Math.random() < 0.5) playChickenSound();
          } else if (r < 0.90) {
            chk.state = 'brood';
            chk.stateTimer = 120 + Math.floor(Math.random() * 100);
            chk.isWalking = false;
          } else {
            chk.state = 'idle';
            chk.stateTimer = 70 + Math.floor(Math.random() * 60);
            chk.isWalking = false;
          }
        }

        if (chk.state === 'walk') {
          const dx = (chk.targetX || chk.x) - chk.x;
          const dy = (chk.targetY || chk.y) - chk.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 4) {
            const moveSpeed = 0.45;
            const targetAngle = Math.atan2(dy, dx);
            let diff = targetAngle - chk.selfAngle;
            while (diff < -Math.PI) diff += Math.PI * 2;
            while (diff > Math.PI) diff -= Math.PI * 2;
            chk.selfAngle += diff * 0.1;

            let nextX = chk.x + Math.cos(chk.selfAngle) * moveSpeed;
            let nextY = chk.y + Math.sin(chk.selfAngle) * moveSpeed;

            const maxR = ROOM_R - 22;
            nextX = Math.max(-maxR, Math.min(maxR, nextX));
            nextY = Math.max(-maxR, Math.min(maxR, nextY));

            chk.x = nextX;
            chk.y = nextY;
            chk.isWalking = true;
          } else {
            chk.state = 'peck';
            chk.stateTimer = 90;
            chk.isWalking = false;
          }
        }
      });
    }

    // IA Autônoma do Gatinho: Passeia pelo quarto, explora e descansa
    function updateCatAI() {
      const cat = items.find(it => it.id === 'cat');
      if (!cat) return;
      const desk = items.find(it => it.id === 'desk' && it.visible !== false);

      cat.idleTimer = (cat.idleTimer || 0) + 0.05;

      // Se o usuário estiver arrastando o gato no Modo Decoração, pausa a IA
      if (isDecorMode && isDraggingItem && selectedItem === cat) {
        cat.state = 'idle';
        cat.stateTimer = 180;
        cat.isWalking = false;
        return;
      }

      // Se o usuário fixou uma postura (Sentar, Pãozinho, Barriga):
      if (cat.forcedPosture && cat.forcedPosture !== 'auto') {
        if (cat.forcedPosture === 'walk') {
          // Deixa caminhar livremente
        } else {
          cat.state = 'idle';
          cat.isWalking = false;
          cat.posture = cat.forcedPosture;
          return;
        }
      }

      // Se estiver em reação de carinho na barriguinha
      if (cat.bellyTimer > 0) {
        cat.bellyTimer--;
        cat.state = 'idle';
        cat.isWalking = false;
        cat.posture = 'belly';
        return;
      }

      // === COMPORTAMENTO DO GATO NA MESA ===
      if (cat.surface === 'desk' && desk) {
        cat.liftZ = 21;
        // Se colocado na mesa pelo usuário, dorme por um tempo garantido!
        if (cat.deskSleepTimer && cat.deskSleepTimer > 0) {
          cat.deskSleepTimer--;
          cat.state = 'idle';
          cat.isWalking = false;
          cat.posture = 'loaf';
          return;
        }

        if (cat.state === 'idle') {
          cat.stateTimer = (cat.stateTimer || 180) - 1;
          if (cat.stateTimer <= 0) {
            const r = Math.random();
            if (r < 0.40) {
              // Pula graciosamente da mesa para o chão!
              cat.surface = null;
              cat.liftZ = 0;
              const jumpTarget = checkCatCollision(desk.x + 24, desk.y + 26);
              cat.x = jumpTarget.x;
              cat.y = jumpTarget.y;
              cat.state = 'idle';
              cat.posture = 'stand';
              cat.stateTimer = 120;
              playMeowSound();
              return;
            } else if (r < 0.70) {
              // Muda de postura no tampo (sentado ou barriga relaxada)
              cat.posture = Math.random() < 0.5 ? 'sit' : 'belly';
              cat.stateTimer = 160 + Math.floor(Math.random() * 180);
            } else {
              // Anda um pouquinho pelo tampo sem cair
              cat.state = 'walking';
              cat.posture = 'walk';
              const targetP = constrainToDesk(desk.x + (Math.random() - 0.5) * 44, desk.y + (Math.random() - 0.5) * 16, 4);
              cat.targetX = targetP.x;
              cat.targetY = targetP.y;
            }
          }
        } else if (cat.state === 'walking') {
          const dx = cat.targetX - cat.x;
          const dy = cat.targetY - cat.y;
          const dist = Math.hypot(dx, dy);
          if (dist < 2.5) {
            cat.x = cat.targetX;
            cat.y = cat.targetY;
            cat.state = 'idle';
            cat.stateTimer = 160 + Math.floor(Math.random() * 200);
            cat.isWalking = false;
            cat.posture = Math.random() < 0.5 ? 'sit' : 'loaf';
          } else {
            cat.isWalking = true;
            cat.posture = 'walk';
            const targetAngle = Math.atan2(-dx, dy);
            let diff = targetAngle - cat.selfAngle;
            while (diff < -Math.PI) diff += Math.PI * 2;
            while (diff > Math.PI) diff -= Math.PI * 2;
            cat.selfAngle += diff * 0.14;
            const speed = 0.45;
            const nextX = cat.x - Math.sin(cat.selfAngle) * speed;
            const nextY = cat.y + Math.cos(cat.selfAngle) * speed;
            const resolved = constrainToDesk(nextX, nextY, 4);
            cat.x = resolved.x;
            cat.y = resolved.y;
            cat.walkCycle = (cat.walkCycle || 0) + speed * 0.35;
          }
        }
        return;
      }

      // === COMPORTAMENTO DO GATO NO CHÃO ===
      if (cat.state === 'idle') {
        cat.isWalking = false;
        cat.stateTimer = (cat.stateTimer || 180) - 1;
        if (cat.stateTimer <= 0) {
          // Se estiver perto da mesa no chão, tem chance de pular pra cima da mesa!
          if (desk && Math.hypot(cat.x - desk.x, cat.y - desk.y) < 55 && Math.random() < 0.28) {
            cat.surface = 'desk';
            cat.liftZ = 21;
            const targetOnDesk = constrainToDesk(desk.x, desk.y);
            cat.x = targetOnDesk.x;
            cat.y = targetOnDesk.y;
            cat.state = 'idle';
            cat.posture = Math.random() < 0.5 ? 'loaf' : 'sit';
            cat.deskSleepTimer = 240 + Math.floor(Math.random() * 200);
            cat.stateTimer = 180;
            playMeowSound();
            return;
          }

          // Escolhe um novo ponto aconchegante pelo quarto
          const waypoints = [
            { x: 0, y: 0 },       // Centro do tapete
            { x: 18, y: 15 },     // Borda do tapete
            { x: -35, y: -20 },   // Frente da caminha nuvem
            { x: -35, y: 25 },    // Perto do arranhador
            { x: 30, y: 35 },     // Perto da plantinha de chão
            { x: 42, y: -30 },    // Frente da cadeira da mesa
            { x: -25, y: -40 },   // Perto da janela
            { x: -10, y: 22 }     // Lado sul do tapete
          ];
          const wp = waypoints[Math.floor(Math.random() * waypoints.length)];
          const validTarget = checkCatCollision(
            wp.x + (Math.random() - 0.5) * 12,
            wp.y + (Math.random() - 0.5) * 12
          );
          cat.targetX = validTarget.x;
          cat.targetY = validTarget.y;
          cat.state = 'walking';
          cat.posture = 'walk';
        }
      } else if (cat.state === 'walking') {
        const dx = cat.targetX - cat.x;
        const dy = cat.targetY - cat.y;
        const dist = Math.hypot(dx, dy);

        if (dist < 2.5) {
          cat.x = cat.targetX;
          cat.y = cat.targetY;
          cat.state = 'idle';
          cat.stateTimer = 180 + Math.floor(Math.random() * 240); // 3 a 7 segundos relaxando
          cat.isWalking = false;
          // Escolhe uma postura aconchegante aleatória fofa!
          const r = Math.random();
          if (r < 0.40) cat.posture = 'sit';
          else if (r < 0.75) cat.posture = 'loaf';
          else if (r < 0.90) cat.posture = 'belly';
          else cat.posture = 'stand';
        } else {
          cat.isWalking = true;
          cat.posture = 'walk';
          const targetAngle = Math.atan2(-dx, dy);

          let diff = targetAngle - cat.selfAngle;
          while (diff < -Math.PI) diff += Math.PI * 2;
          while (diff > Math.PI) diff -= Math.PI * 2;
          cat.selfAngle += diff * 0.14;

          const speed = 0.55;
          const nextX = cat.x - Math.sin(cat.selfAngle) * speed;
          const nextY = cat.y + Math.cos(cat.selfAngle) * speed;

          const resolved = checkCatCollision(nextX, nextY);
          const moved = Math.hypot(resolved.x - cat.x, resolved.y - cat.y);

          if (moved < 0.04 && dist > 8) {
            cat.state = 'idle';
            cat.stateTimer = 120;
            cat.isWalking = false;
            cat.posture = Math.random() < 0.5 ? 'sit' : 'loaf';
          } else {
            cat.x = resolved.x;
            cat.y = resolved.y;
            cat.walkCycle = (cat.walkCycle || 0) + speed * 0.35;
          }
        }
      }
    }

    // --- RENDERIZADOR DE ITEM INDIVIDUAL COM INDICADORES ---
        // --- SISTEMA DE MIGRAÇÃO DE PETS & TROCA DE CÔMODOS ---
    function showToast(msg) {
      const toast = document.createElement('div');
      toast.style.cssText = 'position:fixed; bottom:70px; left:50%; transform:translateX(-50%); background:rgba(30,27,24,0.92); color:#FDFBF7; padding:8px 18px; border-radius:20px; font-size:12px; font-weight:bold; z-index:99999; box-shadow:0 6px 18px rgba(0,0,0,0.3); animation:fadeIn 0.2s ease;';
      toast.innerText = msg;
      document.body.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }, 2500);
    }

    function updateHousePlanBadges() {
      const isBed = (currentRoomId === 'bedroom');
      const bBed = document.getElementById('badgeBedroom');
      const bLiv = document.getElementById('badgeLiving');
      const cardBed = document.getElementById('roomCardBedroom');
      const cardLiv = document.getElementById('roomCardLiving');
      const pBed = document.getElementById('petsBedroom');
      const pLiv = document.getElementById('petsLiving');

      if (bBed) bBed.style.display = isBed ? 'inline-block' : 'none';
      if (bLiv) bLiv.style.display = isBed ? 'none' : 'inline-block';
      if (cardBed) cardBed.classList.toggle('active-room', isBed);
      if (cardLiv) cardLiv.classList.toggle('active-room', !isBed);
      if (pBed) pBed.innerHTML = isBed ? '🐱 🐔 🐥' : '';
      if (pLiv) pLiv.innerHTML = !isBed ? '🐱 🐔 🐥' : '';
    }

    function migratePetsToDoor(door, onComplete) {
      const cat = PETS.find(it => it.id === 'cat');
      const chicken = PETS.find(it => it.id === 'chicken');
      const chick = PETS.find(it => it.id === 'chick');

      if (cat) {
        cat.surface = null; cat.liftZ = 0;
        cat.targetX = door.x * 0.75; cat.targetY = door.y * 0.75;
        cat.state = 'walk'; cat.posture = 'walk';
        cat.speech = { text: "Nya~! Vamos lá! 🚪", timer: 160 };
        setTimeout(() => cat.speech = null, 2500);
      }
      if (chicken) {
        chicken.surface = null; chicken.liftZ = 0;
        chicken.targetX = door.x * 0.70; chicken.targetY = door.y * 0.70;
        chicken.state = 'walk';
        chicken.speech = { text: "Có có! 💕", timer: 160 };
        setTimeout(() => chicken.speech = null, 2500);
      }
      if (chick) {
        chick.surface = null; chick.liftZ = 0;
        chick.targetX = door.x * 0.65; chick.targetY = door.y * 0.65;
        chick.state = 'walk';
        chick.speech = { text: "Piu! ❤️", timer: 160 };
        setTimeout(() => chick.speech = null, 2500);
      }

      for (let i = 0; i < 5; i++) {
        hearts.push({ x: door.x * 0.7 + (Math.random() - 0.5) * 20, y: door.y * 0.7 + (Math.random() - 0.5) * 20, z: 25, life: 1.0 });
      }

      setTimeout(() => {
        if (onComplete) onComplete();
      }, 500);
    }

    function switchRoom(targetRoomId, viaDoor = false) {
      if (currentRoomId === targetRoomId) return;
      if (targetRoomId === 'kitchen') {
        showToast("🍽️ Cozinha: O cheirinho de peixe tá bom... Em breve!");
        return;
      }
      if (targetRoomId === 'garden') {
        showToast("🌳 Jardim: Portinha pro quintal ensolarado... Em breve!");
        return;
      }

      const fade = document.getElementById('roomFadeOverlay');
      if (fade) fade.style.opacity = '1';

      setTimeout(() => {
        // Salva mobília do cômodo anterior
        roomState[currentRoomId] = items.filter(it => !it.isCat && !it.isChicken);
        currentRoomId = targetRoomId;

        const cat = PETS.find(it => it.id === 'cat');
        const chicken = PETS.find(it => it.id === 'chicken');
        const chick = PETS.find(it => it.id === 'chick');

        if (targetRoomId === 'living') {
          // Entrando na Sala vindo da Porta do Quarto na Parede Norte (x=75, y=-ROOM_R)
          if (cat) {
            cat.x = 68; cat.y = -ROOM_R + 38; cat.liftZ = 0;
            cat.targetX = -25; cat.targetY = 0; cat.state = 'walk'; cat.posture = 'walk';
            cat.speech = { text: "Nya~! Chegamos na Sala! ✨", timer: 180 };
          }
          if (chicken) {
            chicken.x = 78; chicken.y = -ROOM_R + 42; chicken.liftZ = 0;
            chicken.targetX = -35; chicken.targetY = -8; chicken.state = 'walk';
            chicken.speech = { text: "Có có! 🛋️", timer: 180 };
          }
          if (chick) {
            chick.x = 74; chick.y = -ROOM_R + 48; chick.liftZ = 0;
            chick.targetX = -30; chick.targetY = 8; chick.state = 'walk';
            chick.speech = { text: "Piu piu! ❤️", timer: 180 };
          }

          WALLS[0].decor = 'living_art'; // North
          WALLS[1].decor = null;         // West
          WALLS[2].decor = null;         // South
          WALLS[3].decor = 'garden_window'; // East (Janela do Jardim lado a lado com a porta do jardim!)
        } else if (targetRoomId === 'bedroom') {
          // Entrando no Quarto vindo da porta Leste (Sala)
          if (cat) {
            cat.x = ROOM_R - 35; cat.y = 50; cat.liftZ = 0;
            cat.targetX = 10; cat.targetY = 0; cat.state = 'walk'; cat.posture = 'walk';
            cat.speech = { text: "De volta ao quartinho! 🛏️", timer: 180 };
          }
          if (chicken) {
            chicken.x = ROOM_R - 30; chicken.y = 65; chicken.liftZ = 0;
            chicken.targetX = -20; chicken.targetY = 30; chicken.state = 'walk';
          }
          if (chick) {
            chick.x = ROOM_R - 25; chick.y = 75; chick.liftZ = 0;
            chick.targetX = -10; chick.targetY = 40; chick.state = 'walk';
          }

          WALLS[0].decor = 'window';     // North
          WALLS[1].decor = null;         // West
          WALLS[2].decor = 'pegboard';   // South
          WALLS[3].decor = null;         // East
        }

        items = [ ...PETS, ...roomState[currentRoomId] ];

        const titleEl = document.getElementById('roomTitle');
        const subEl = document.getElementById('roomSubtitle');
        if (currentRoomId === 'living') {
          if (titleEl) titleEl.innerHTML = "🛋️ Sala de Estar Central (Hub da Casa)";
          if (subEl) subEl.innerHTML = "Sofá aconchegante, TV retrô vintage e vista para o jardim!";
        } else {
          if (titleEl) titleEl.innerHTML = "🛏️ Mega Quartinho 3D (Tudo Modular & Movível!)";
          if (subEl) subEl.innerHTML = "Mesa espaçosa, caminha nuvem, torre de gato e mural de post-its!";
        }

        updateHousePlanBadges();

        if (assetDrawer && assetDrawer.style.display !== 'none') {
          renderAssetList();
        }

        if (fade) fade.style.opacity = '0';
      }, 300);
    }

    function renderItem(item) {
      const isSel = (item === selectedItem);
      const isHov = (item === hoveredItem && isDecorMode);

      const targetLift = (isSel && isDraggingItem && !item.isWallItem) ? 6 : 0;
      item.dragLift = item.dragLift || 0;
      item.dragLift += (targetLift - item.dragLift) * 0.3;
      const effectiveLiftZ = item.liftZ + item.dragLift;

      // Sombras e anéis de seleção
      if (!item.isWallItem) {
        // REGRA DE OURO: Itens sobre móveis (mesa ou prateleira) NÃO têm sombra no chão!
        const hasFloorShadow = !item.surface && (item.liftZ === 0 || item.isCat || item.isDesk || item.isSofa || item.isCoffeeTable || item.isTvRack || item.isBookshelf);

        if (hasFloorShadow) {
          if (item.isDesk || item.isSofa || item.isTvRack || item.isCoffeeTable || item.isBookshelf) {
            // Sombra retangular orientada e rotacionada com o móvel!
            const cosD = Math.cos(item.selfAngle || 0);
            const sinD = Math.sin(item.selfAngle || 0);
            const hw = item.isDesk ? 39 : (item.isSofa ? 27 : (item.isTvRack ? 25 : (item.isCoffeeTable ? 17 : 16)));
            const hh = item.isDesk ? 17 : (item.isSofa ? 14 : (item.isTvRack ? 10 : (item.isCoffeeTable ? 11 : 8)));
            const corners = [
              { x: item.x - hw * cosD + hh * sinD, y: item.y - hw * sinD - hh * cosD },
              { x: item.x + hw * cosD + hh * sinD, y: item.y + hw * sinD - hh * cosD },
              { x: item.x + hw * cosD - hh * sinD, y: item.y + hw * sinD + hh * cosD },
              { x: item.x - hw * cosD - hh * sinD, y: item.y - hw * sinD + hh * cosD }
            ];
            const pC = corners.map(c => project(c.x, c.y, 0));
            lowCtx.beginPath();
            lowCtx.moveTo(pC[0].x, pC[0].y);
            for (let k = 1; k < 4; k++) lowCtx.lineTo(pC[k].x, pC[k].y);
            lowCtx.closePath();
            lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
            lowCtx.fill();

            if (isSel || isHov) {
              lowCtx.lineWidth = isSel ? 2 : 1;
              lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
              lowCtx.stroke();
            }
          } else if (false) {
            // Sombra poligonal 100% orientada e rotacionada com a mesa!
            const cosD = Math.cos(item.selfAngle);
            const sinD = Math.sin(item.selfAngle);
            const hw = 39;
            const hh = 17;
            const corners = [
              { x: item.x - hw * cosD + hh * sinD, y: item.y - hw * sinD - hh * cosD },
              { x: item.x + hw * cosD + hh * sinD, y: item.y + hw * sinD - hh * cosD },
              { x: item.x + hw * cosD - hh * sinD, y: item.y + hw * sinD + hh * cosD },
              { x: item.x - hw * cosD - hh * sinD, y: item.y - hw * sinD + hh * cosD }
            ];
            const pC = corners.map(c => project(c.x, c.y, 0));
            lowCtx.beginPath();
            lowCtx.moveTo(pC[0].x, pC[0].y);
            for (let k = 1; k < 4; k++) lowCtx.lineTo(pC[k].x, pC[k].y);
            lowCtx.closePath();
            lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
            lowCtx.fill();

            if (isSel || isHov) {
              lowCtx.lineWidth = isSel ? 2 : 1;
              lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
              lowCtx.stroke();
            }
          } else {
            const shadowP = project(item.x, item.y, 0);
            lowCtx.save();
            lowCtx.translate(shadowP.x, shadowP.y);
            lowCtx.scale(1, squash * 0.45);
            lowCtx.beginPath();
            const baseRadius = (item.isCat ? 15 : (item.isChicken ? 14 : 20)) * (item.scale ? item.scale / 1.3 : 1);
            const shadowRadius = baseRadius * (1 + (item.dragLift || 0) * 0.05);
            lowCtx.arc(0, 0, shadowRadius, 0, Math.PI * 2);
            lowCtx.fillStyle = isSel ? 'rgba(216, 125, 74, 0.40)' : 'rgba(74, 46, 27, 0.22)';
            lowCtx.fill();

            if (isSel || isHov) {
              lowCtx.lineWidth = isSel ? 2 : 1;
              lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
              lowCtx.stroke();
            }
            lowCtx.restore();
          }
        } else if ((isSel || isHov) && isDecorMode) {
          // Apenas anel de seleção luminoso no plano da própria mesa ou prateleira
          const ringP = project(item.x, item.y, effectiveLiftZ);
          lowCtx.save();
          lowCtx.translate(ringP.x, ringP.y);
          lowCtx.scale(1, squash * 0.5);
          lowCtx.beginPath();
          const ringRadius = 16 * (item.scale ? item.scale / 1.3 : 1);
          lowCtx.arc(0, 0, ringRadius, 0, Math.PI * 2);
          lowCtx.lineWidth = isSel ? 2 : 1;
          lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.7)';
          lowCtx.stroke();
          lowCtx.restore();
        }

        // Indicadores nos 4 pés da mesa quando selecionada ou em hover no Modo Decoração
        if (item.isDesk && (isSel || isHov) && isDecorMode) {
          const cosD = Math.cos(item.selfAngle);
          const sinD = Math.sin(item.selfAngle);
          const legOffsets = [
            [-33, -11], [33, -11],
            [-33,  11], [33,  11]
          ];
          for (const [ox, oy] of legOffsets) {
            const lx = item.x + ox * cosD - oy * sinD;
            const ly = item.y + ox * sinD + oy * cosD;
            const pLeg = project(lx, ly, 0);
            lowCtx.save();
            lowCtx.translate(pLeg.x, pLeg.y);
            lowCtx.scale(1, squash * 0.5);
            lowCtx.beginPath();
            lowCtx.arc(0, 0, 7, 0, Math.PI * 2);
            lowCtx.strokeStyle = isSel ? '#D87D4A' : 'rgba(216, 125, 74, 0.8)';
            lowCtx.lineWidth = isSel ? 2 : 1;
            lowCtx.stroke();
            lowCtx.restore();
          }
        }
      }

      // Desenho do objeto correspondente
      if (item.isCat) {
        drawCat(item, effectiveLiftZ);
      } else if (item.isChicken) {
        drawChicken(item, effectiveLiftZ);
      } else if (item.model) {
        drawStackObject(item.model, item.x, item.y, effectiveLiftZ, item.selfAngle, item.scale);
      } else if (item.id === 'shelf') {
        drawShelfItem(item);
      } else if (item.id === 'shelf_books') {
        drawShelfBooks(item);
      } else if (item.id === 'shelf_plant') {
        drawShelfPlant(item);
      } else if (item.id === 'shelf_crystal') {
        drawShelfCrystal(item);
      } else if (item.id === 'clock') {
        drawWallClock(item);
      } else if (item.id === 'corkboard' || item.id === 'frame_cat') {
        drawSingleFrame(item, 'corkboard');
      } else if (item.id === 'frame_plant') {
        drawSingleFrame(item, 'plant');
      } else if (item.isDoor || item.id === 'door' || (item.id && item.id.startsWith('door_'))) {
        drawDoor(item);
      }

      // Marcador e caixa de seleção no Modo Decoração
      if (isSel && isDecorMode) {
        const h = item.model ? item.model.count * (item.scale || 1.3) : 18;
        const topP = project(item.x, item.y, effectiveLiftZ + h + 10);
        lowCtx.fillStyle = '#D87D4A';
        lowCtx.beginPath();
        lowCtx.moveTo(topP.x, topP.y);
        lowCtx.lineTo(topP.x - 4, topP.y - 7);
        lowCtx.lineTo(topP.x + 4, topP.y - 7);
        lowCtx.closePath();
        lowCtx.fill();

        if (item.isWallItem) {
          const pC = project(item.x, item.y, effectiveLiftZ);
          lowCtx.strokeStyle = '#D87D4A';
          lowCtx.lineWidth = 1;
          lowCtx.strokeRect(pC.x - 14, pC.y - 14, 28, 28);
        }
      }
    }

    // --- 3. SISTEMA DE ORDENAÇÃO E RENDERIZAÇÃO 3D (ZERO CLIPPING NA MESA!) ---
    function drawAll3DObjects() {
      const cosA = Math.cos(turn);
      const sinA = Math.sin(turn);

      const activeItems = items.filter(it => it.visible !== false);

      activeItems.forEach(item => {
        item.depth = item.x * sinA + item.y * cosA;
        item.p = project(item.x, item.y, item.liftZ);
      });

      // 1. Itens da Parede Oeste (só renderiza se a parede oeste for parede de trás)
      const isWestWallVisible = (-1 * sinA <= 0.05);
      if (isWestWallVisible) {
        // Exclui itens apoiados na prateleira para renderizá-los diretamente em cima dela
        const westWallMains = activeItems.filter(it => it.isWallItem && it.wall === 'west' && it.surface !== 'shelf');
        westWallMains.sort((a, b) => a.depth - b.depth);
        for (const item of westWallMains) {
          renderItem(item);

          // Ao renderizar a prateleira, desenha IMEDIATAMENTE todos os acessórios apoiados nela!
          if (item.id === 'shelf') {
            const shelfProps = activeItems.filter(it => it.surface === 'shelf');
            shelfProps.sort((a, b) => a.depth - b.depth);
            for (const prop of shelfProps) {
              renderItem(prop);
            }
          }
        }
      }

      // 2. Itens da Parede Leste (só renderiza se a parede leste for parede de trás)
      const isEastWallVisible = (1 * sinA <= 0.05);
      if (isEastWallVisible) {
        const eastWallItems = activeItems.filter(it => it.isWallItem && it.wall === 'east');
        eastWallItems.sort((a, b) => a.depth - b.depth);
        for (const item of eastWallItems) {
          renderItem(item);
        }
      }

      // 3. Itens da Parede Sul (só renderiza se a parede sul for parede de trás)
      const isSouthWallVisible = (1 * cosA <= 0.05);
      if (isSouthWallVisible) {
        const southWallItems = activeItems.filter(it => it.isWallItem && it.wall === 'south');
        southWallItems.sort((a, b) => a.depth - b.depth);
        for (const item of southWallItems) {
          renderItem(item);
        }
      }

      // 4. Itens da Parede Norte (só renderiza se a parede norte for parede de trás)
      const isNorthWallVisible = (-1 * cosA <= 0.05);
      if (isNorthWallVisible) {
        const northWallItems = activeItems.filter(it => it.isWallItem && it.wall === 'north');
        northWallItems.sort((a, b) => a.depth - b.depth);
        for (const item of northWallItems) {
          renderItem(item);
        }
      }

      // 3. Itens de chão (exclui itens de parede, itens na mesa, prateleira e estante)
      const floorItems = activeItems.filter(it => !it.isWallItem && it.surface !== 'desk' && it.surface !== 'shelf' && it.surface !== 'bookshelf');
      floorItems.sort((a, b) => a.depth - b.depth);

      for (const item of floorItems) {
        renderItem(item);

        // SE O ITEM FOR A ESTANTE, DESENHA IMEDIATAMENTE TODOS OS ACESSÓRIOS APOIADOS NELA!
        if (item.id === 'bookshelf' || item.isBookshelf) {
          const bsProps = activeItems.filter(it => it.surface === 'bookshelf');
          bsProps.sort((a, b) => a.depth - b.depth);
          for (const prop of bsProps) {
            renderItem(prop);
          }
        }

        // SE O ITEM FOR A MESA, DESENHA IMEDIATAMENTE TODOS OS ITENS APOIADOS NELA!
        if (item.id === 'desk') {
          // Indicadores sutis de Snap-to-Slot no tampo da mesa no Modo Decoração
          if (isDecorMode && (isDraggingItem || hoveredItem)) {
            const cosD = Math.cos(item.selfAngle);
            const sinD = Math.sin(item.selfAngle);
            for (const slot of DESK_SLOTS) {
              const sx = item.x + slot.offX * cosD - slot.offY * sinD;
              const sy = item.y + slot.offX * sinD + slot.offY * cosD;
              const sp = project(sx, sy, 21.2);
              lowCtx.save();
              lowCtx.translate(sp.x, sp.y);
              lowCtx.scale(1, squash * 0.5);
              lowCtx.beginPath();
              lowCtx.arc(0, 0, 6, 0, Math.PI * 2);
              lowCtx.strokeStyle = 'rgba(216, 125, 74, 0.65)';
              lowCtx.lineWidth = 1.2;
              lowCtx.stroke();
              lowCtx.restore();
            }
          }

          const deskProps = activeItems.filter(it => it.surface === 'desk');
          deskProps.sort((a, b) => a.depth - b.depth);
          for (const prop of deskProps) {
            renderItem(prop);
          }
        }
      }
    }

    // Corações flutuantes de carinho
    function drawHearts() {
      for (let i = hearts.length - 1; i >= 0; i--) {
        const h = hearts[i];
        h.y -= 0.6;
        h.alpha -= 0.015;
        if (h.alpha <= 0) {
          hearts.splice(i, 1);
          continue;
        }
        lowCtx.fillStyle = `rgba(235, 94, 120, ${h.alpha})`;
        lowCtx.fillRect(h.x, h.y, 4, 4);
        lowCtx.fillRect(h.x - 1, h.y - 1, 2, 2);
        lowCtx.fillRect(h.x + 3, h.y - 1, 2, 2);
      }
    }

    // --- LOOP PRINCIPAL DE RENDERIZAÇÃO ---
    function render() {
      turn += (targetTurn - turn) * 0.1;

      if (autoSpin) {
        targetTurn += 0.006;
      }

      // Atualiza a IA e animação do gatinho a 60 FPS
      updateCatAI();
    updateChickenAI();

      lowCtx.fillStyle = P.bg;
      lowCtx.fillRect(0, 0, LOW_W, LOW_H);

      // 1. Paredes de trás
      drawWalls();

      // 2. Chão com grid
      drawFloor();

      // 3. Móveis e itens modulares 3D
      drawAll3DObjects();

      // 4. Efeitos
      drawHearts();

      // Upscale nítido para o viewport principal (Canvas 800x800)
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(lowCanvas, 0, 0, canvas.width, canvas.height);

      requestAnimationFrame(render);
    }

    render();

    // --- SISTEMA DE HIT DETECTION E DRAG & DROP MODULAR ---
    function getCanvasCoords(e) {
      const rect = canvas.getBoundingClientRect();
      const sx = ((e.clientX - rect.left) / rect.width) * LOW_W;
      const sy = ((e.clientY - rect.top) / rect.height) * LOW_H;
      return { sx, sy };
    }

    function findItemAt(worldPos, screenPos) {
      const sinA = Math.sin(turn);
      const isWestWallVisible = (-1 * sinA <= 0.05);
      const isEastWallVisible = (1 * sinA <= 0.05);

      const activeItems = items.filter(it => it.visible !== false);

      // FASE 1: Prioridade Máxima para acessórios universais (na mesa, na prateleira ou no chão)
      // Se o usuário clicar em qualquer acessório, SEMPRE seleciona o acessório diretamente!
      const props = activeItems.filter(it => it.isProp);
      for (const item of props) {
        const p = project(item.x, item.y, item.liftZ + 6);
        const dScreen = Math.hypot(screenPos.sx - p.x, screenPos.sy - p.y);
        if (dScreen < (item.radius || 15)) {
          return item;
        }
      }

      // FASE 2: Itens de parede (se a parede estiver visível)
      const wallProps = activeItems.filter(it => it.isWallItem);
      for (const item of wallProps) {
        if (item.wall === 'west' && !isWestWallVisible) continue;
        if (item.wall === 'east' && !isEastWallVisible) continue;
        const p = project(item.x, item.y, item.liftZ);
        const dScreen = Math.hypot(screenPos.sx - p.x, screenPos.sy - p.y);
        if (dScreen < (item.radius || 20)) {
          return item;
        }
      }

      // FASE 3: O Gatinho e outros itens de chão
      const floorMobiles = activeItems.filter(it => !it.isWallItem && !it.isProp && !it.isDesk);
      const sortedFloor = [...floorMobiles].sort((a, b) => b.depth - a.depth);
      for (const item of sortedFloor) {
        const h = item.model ? item.model.count * (item.scale || 1.3) : 20;
        const pBot = project(item.x, item.y, item.liftZ);
        const pTop = project(item.x, item.y, item.liftZ + h);
        const midY = (pBot.y + pTop.y) / 2;
        const dScreen = Math.hypot(screenPos.sx - pBot.x, screenPos.sy - midY);
        if (dScreen < (item.radius || 20)) {
          return item;
        }
        const dWorld = Math.hypot(worldPos.x - item.x, worldPos.y - item.y);
        if (dWorld < (item.radius || 20)) {
          return item;
        }
      }

      // FASE 4: Móvel Grande (A Mesa de Estudo)
      // "Pegar pelo Pé": detecta clique nos 4 pés da mesa no chão ou na base do piso!
      const desk = activeItems.find(it => it.id === 'desk');
      if (desk) {
        // Checa distância aos 4 pés no chão
        const cosD = Math.cos(desk.selfAngle);
        const sinD = Math.sin(desk.selfAngle);
        const legOffsets = [
          [-33, -11], [33, -11],
          [-33,  11], [33,  11]
        ];
        for (const [ox, oy] of legOffsets) {
          const lx = desk.x + ox * cosD - oy * sinD;
          const ly = desk.y + ox * sinD + oy * cosD;
          const pLeg = project(lx, ly, 0);
          const dLeg = Math.hypot(screenPos.sx - pLeg.x, screenPos.sy - pLeg.y);
          if (dLeg < 16) {
            return desk; // Pegou diretamente por um dos pés!
          }
        }

        // Também permite pegar clicando no centro/sombra no chão
        const pCenterFloor = project(desk.x, desk.y, 0);
        const dFloor = Math.hypot(screenPos.sx - pCenterFloor.x, screenPos.sy - pCenterFloor.y);
        if (dFloor < 30) {
          return desk;
        }

        // Ou clicando no tampo livre onde não tem acessório
        const dWorld = Math.hypot(worldPos.x - desk.x, worldPos.y - desk.y);
        if (dWorld < desk.radius) {
          return desk;
        }
      }

      return null;
    }

    function rotateSelectedItem() {
      if (selectedItem && !selectedItem.isWallItem) {
        selectedItem.selfAngle = (selectedItem.selfAngle + Math.PI / 2) % (Math.PI * 2);

        // Se o item selecionado for a mesa, rotaciona seus acessórios em +90° preservando posições exatas!
        if (selectedItem.id === 'desk') {
          for (const it of items) {
            if (it.surface === 'desk') {
              // Rotação vetorial 2D de +90 graus (PI/2): newOffX = -oldOffY, newOffY = oldOffX
              const oldOffX = it.offX || 0;
              const oldOffY = it.offY || 0;
              it.offX = -oldOffY;
              it.offY = oldOffX;
              it.x = selectedItem.x + it.offX;
              it.y = selectedItem.y + it.offY;
              it.selfAngle = (it.selfAngle + Math.PI / 2) % (Math.PI * 2);
            }
          }
        }
      }
    }

    window.addEventListener('keydown', (e) => {
      if (e.key === 'r' || e.key === 'R') {
        rotateSelectedItem();
      }
    });

    // Funções de Bounding Quad e Culling do Mural de Post-its
    function isPointInWallQuad(px, py, p1, p2, p3, p4, tolerance = 3) {
      function cross(a, b, x, y) {
        return (b.x - a.x) * (y - a.y) - (b.y - a.y) * (x - a.x);
      }
      const c1 = cross(p1, p2, px, py);
      const c2 = cross(p2, p3, px, py);
      const c3 = cross(p3, p4, px, py);
      const c4 = cross(p4, p1, px, py);
      const allPos = (c1 >= -tolerance && c2 >= -tolerance && c3 >= -tolerance && c4 >= -tolerance);
      const allNeg = (c1 <= tolerance && c2 <= tolerance && c3 <= tolerance && c4 <= tolerance);
      return allPos || allNeg;
    }

    function getCorkboardQuad() {
      const corkboard = items.find(it => (it.id === 'corkboard' || it.id === 'frame_cat') && it.visible !== false);
      if (!corkboard) return null;

      // Se a parede leste estiver sumindo ou virando para a frente (culled), a área de clique some 100%!
      const sinA = Math.sin(turn);
      if (sinA > -0.08) return null; // Parede oculta ou de perfil extremo

      const xWall = ROOM_R;
      const p1 = project(xWall - 0.5, corkboard.y - 24, corkboard.liftZ - 26);
      const p2 = project(xWall - 0.5, corkboard.y + 24, corkboard.liftZ - 26);
      const p3 = project(xWall - 0.5, corkboard.y + 24, corkboard.liftZ + 26);
      const p4 = project(xWall - 0.5, corkboard.y - 24, corkboard.liftZ + 26);

      // Conforme a parede vira, a largura na tela diminui: se for < 8px, já sumiu para o clique!
      const projW = Math.max(p1.x, p2.x, p3.x, p4.x) - Math.min(p1.x, p2.x, p3.x, p4.x);
      if (projW < 8) return null;

      return { p1, p2, p3, p4, projW };
    }

    let isDraggingView = false;
    let lastX = 0;
    let pointerDownPos = { x: 0, y: 0 };
    let isPressedOnCorkboard = false;

    canvas.addEventListener('pointerdown', (e) => {
      const { sx, sy } = getCanvasCoords(e);
      const worldPos = unproject(sx, sy);
      pointerDownPos = { x: e.clientX, y: e.clientY };
      isPressedOnCorkboard = false;

      if (!isDecorMode) {
        // A área de clique acompanha perfeitamente a perspectiva 3D e some quando a parede vira!
        const q = getCorkboardQuad();
        if (q && isPointInWallQuad(sx, sy, q.p1, q.p2, q.p3, q.p4, 3)) {
          isPressedOnCorkboard = true;
          return;
        }
      }

      if (isDecorMode) {
        const item = findItemAt(worldPos, { sx, sy });
        if (item) {
          selectedItem = item;
          isDraggingItem = true;
          dragStartPos = { sx, sy };
          itemStartPos = { x: item.x, y: item.y, liftZ: item.liftZ };
          dragOffset.x = item.x - worldPos.x;
          dragOffset.y = item.y - worldPos.y;
          btnRotateMob.style.display = item.isWallItem ? 'none' : 'inline-flex';
          canvas.classList.add('decor-dragging');
          return;
        } else {
          selectedItem = null;
          btnRotateMob.style.display = 'none';
        }
      }

      isDraggingView = true;
      lastX = e.clientX;
      autoSpin = false;
      btnAutoSpin.classList.remove('active');
    });

    window.addEventListener('pointermove', (e) => {
      const { sx, sy } = getCanvasCoords(e);
      const worldPos = unproject(sx, sy);

      if (!isDecorMode && !isDraggingView) {
        const corkboard = items.find(it => (it.id === 'corkboard' || it.id === 'frame_cat') && it.visible !== false);
        if (corkboard) {
          const pBoard = project(corkboard.x, corkboard.y, corkboard.liftZ);
          if (Math.hypot(sx - pBoard.x, sy - pBoard.y) < 48) {
            canvas.style.cursor = 'pointer';
            canvas.title = '📌 Clique para abrir o Mural de Post-its!';
          } else {
            canvas.style.cursor = '';
            canvas.title = '';
          }
        }
      }

      if (isDecorMode && !isDraggingItem && !isDraggingView) {
        hoveredItem = findItemAt(worldPos, { sx, sy });
        if (hoveredItem) {
          canvas.classList.add('decor-hover');
          if (hoveredItem.isDesk) {
            bannerInfo.innerHTML = `<span>🐾 <b>Móvel:</b> 🪵 Mesa de Estudo — arraste pelos pés para mover tudo!</span>`;
          } else if (hoveredItem.onDesk) {
            bannerInfo.innerHTML = `<span>🐾 <b>Acessório:</b> ${hoveredItem.icon || ''} ${hoveredItem.name} — clique para reposicionar no tampo!</span>`;
          } else if (hoveredItem.isWallItem) {
            bannerInfo.innerHTML = `<span>🐾 <b>Parede:</b> ${hoveredItem.icon || ''} ${hoveredItem.name} — arraste para subir, descer ou deslizar!</span>`;
          } else {
            bannerInfo.innerHTML = `<span>🐾 <b>Item:</b> ${hoveredItem.icon || ''} ${hoveredItem.name} — arraste pelo quarto!</span>`;
          }
        } else {
          canvas.classList.remove('decor-hover');
          if (selectedItem) {
            bannerInfo.innerHTML = `<span>🛠️ <b>Selecionado:</b> ${selectedItem.icon || ''} ${selectedItem.name} (Girar com Tecla R)</span>`;
          } else {
            bannerInfo.innerHTML = `<span>🛠️ <b>Modo Decoração:</b> Arraste móveis, prateleira, quadros, relógio ou o gatinho!</span>`;
          }
        }
      }

      // Arrastando objeto selecionado
      if (isDraggingItem && selectedItem) {
        if (selectedItem.isWallItem) {
          // Arrastando item de parede na horizontal e vertical (altura Z)
          const dsx = sx - dragStartPos.sx;
          const dsy = sy - dragStartPos.sy;

          const newZ = Math.round(itemStartPos.liftZ - dsy * 0.8);
          selectedItem.liftZ = Math.max(35, Math.min(92, newZ));

          const sinA = Math.sin(turn);
          // O movimento horizontal na tela dxScreen = -sinA * dy, portanto dir = (sinA > 0 ? -1 : 1)
          // Isso garante que puxar o mouse para a direita SEMPRE mova o item para a direita na tela!
          const dir = (sinA > 0 ? -1 : 1);
          const newY = Math.round(itemStartPos.y + dsx * dir * 0.8);
          const limit = ROOM_R - 30;
          selectedItem.y = Math.max(-limit, Math.min(limit, newY));

          // Se moveu a prateleira inteira, atualiza os itens apoiados nela PRESERVANDO sua posição offY exata!
          if (selectedItem.id === 'shelf') {
            for (const it of items) {
              if (it.surface === 'shelf') {
                it.x = -ROOM_R + 9;
                it.y = selectedItem.y + it.offY;
                it.liftZ = selectedItem.liftZ + 3.5;
              }
            }
          }
          return;
        }

        // Arrastando item de chão / mesa
        let newX = worldPos.x + dragOffset.x;
        let newY = worldPos.y + dragOffset.y;

        newX = Math.round(newX / 4) * 4;
        newY = Math.round(newY / 4) * 4;

        const desk = items.find(it => it.id === 'desk');

        // Cálculo de limites de colisão com a parede (SEM vazar nem atravessar!)
        let halfW = 20;
        let halfH = 20;
        if (selectedItem.id === 'desk') {
          const isRot = (selectedItem.selfAngle === Math.PI / 2 || selectedItem.selfAngle === Math.PI * 1.5);
          halfW = isRot ? 18 : 33;
          halfH = isRot ? 33 : 18;
        } else if (selectedItem.radius) {
          halfW = Math.round(selectedItem.radius * 0.85);
          halfH = Math.round(selectedItem.radius * 0.85);
        }

        const limitX = ROOM_R - halfW - 2;
        const limitY = ROOM_R - halfH - 2;

        // Snap magnético alinhando com o rodapé das paredes
        if (selectedItem.id === 'desk') {
          if (newY < -limitY + 10) newY = -limitY;
          if (newY > limitY - 10) newY = limitY;
          if (newX < -limitX + 10) newX = -limitX;
          if (newX > limitX - 10) newX = limitX;
        }

        selectedItem.x = Math.max(-limitX, Math.min(limitX, newX));
        selectedItem.y = Math.max(-limitY, Math.min(limitY, newY));

        // Se estiver arrastando a mesa inteira, move todos os itens apoiados nela juntos!
        if (selectedItem.id === 'desk') {
          for (const it of items) {
            if (it.surface === 'desk') {
              it.x = selectedItem.x + it.offX;
              it.y = selectedItem.y + it.offY;
              it.selfAngle = selectedItem.selfAngle;
            }
          }
        } else if (selectedItem.isProp || selectedItem.isCat || selectedItem.isChicken) {
          // ACESSÓRIO UNIVERSAL OU PET: pode ser colocado na mesa, sofá, mesinha, prateleira ou chão!
          const shelf = items.find(it => it.id === 'shelf');
          const sofa = items.find(it => it.id === 'sofa');
          const coffeeTable = items.find(it => it.id === 'coffee_table');

          // Checa se está sobre o SOFÁ
          const onSofaArea = sofa && sofa.visible !== false && Math.abs(selectedItem.x - sofa.x) < 32 && Math.abs(selectedItem.y - sofa.y) < 18;
          // Checa se está sobre a MESINHA DE CENTRO
          const onTableArea = coffeeTable && coffeeTable.visible !== false && Math.abs(selectedItem.x - coffeeTable.x) < 20 && Math.abs(selectedItem.y - coffeeTable.y) < 14;

          // 1. Checa se está sobre a MESA
          let onDeskArea = false;
          let localX = 0, localY = 0, cosD = 1, sinD = 0;
          if (desk) {
            cosD = Math.cos(desk.selfAngle);
            sinD = Math.sin(desk.selfAngle);
            const rwx = selectedItem.x - desk.x;
            const rwy = selectedItem.y - desk.y;
            localX =  rwx * cosD + rwy * sinD;
            localY = -rwx * sinD + rwy * cosD;
            onDeskArea = Math.abs(localX) < 44 && Math.abs(localY) < 22;
          }

          // 2. Checa se está sobre a PRATELEIRA
          const onShelfArea = shelf && Math.abs(selectedItem.x - (-ROOM_R + 9)) < 22 && Math.abs(selectedItem.y - shelf.y) < (shelf.length / 2 + 6);

          if (onBookshelfArea) {
            // Colocou NA ESTANTE!
            selectedItem.surface = 'bookshelf';
            const cosB = Math.cos(bookshelf.selfAngle);
            const sinB = Math.sin(bookshelf.selfAngle);

            // Determina a prateleira com base na altura ou ciclo
            const currentZ = selectedItem.liftZ || 0;
            let tierZ = 2.5; // Prateleira 1 (Inferior)
            let tierNum = 1;
            if (currentZ > 34) {
              tierZ = 41.5; // Topo
              tierNum = 4;
            } else if (currentZ > 20) {
              tierZ = 28.5; // Prateleira 3 (Superior)
              tierNum = 3;
            } else if (currentZ > 8) {
              tierZ = 15.5; // Prateleira 2 (Média)
              tierNum = 2;
            }
            selectedItem.liftZ = tierZ;
            selectedItem.tier = tierNum;

            // Clampa no vão da prateleira (localX: -10..10, localY: 0)
            const clampX = Math.max(-10, Math.min(10, bsLocalX));
            selectedItem.offX = clampX;
            selectedItem.offY = 0;
            selectedItem.x = bookshelf.x + clampX * cosB;
            selectedItem.y = bookshelf.y + clampX * sinB;
            selectedItem.selfAngle = bookshelf.selfAngle;

            if (selectedItem.isCat) {
              selectedItem.liftZ = 41.5; // Gatinho dorme no topo da estante!
              selectedItem.state = 'idle';
              selectedItem.posture = 'loaf';
              selectedItem.isWalking = false;
            } else if (selectedItem.isChicken) {
              selectedItem.liftZ = tierZ;
              selectedItem.state = selectedItem.id === 'chicken' ? 'brood' : 'idle';
              selectedItem.isWalking = false;
            }
          } else if (onSofaArea) {
            selectedItem.surface = 'sofa';
            selectedItem.liftZ = 9;
            if (selectedItem.isCat) {
              selectedItem.sofaSleepTimer = 360;
              selectedItem.state = 'idle';
              selectedItem.posture = 'loaf';
              selectedItem.isWalking = false;
            }
          } else if (onTableArea) {
            selectedItem.surface = 'coffee_table';
            selectedItem.liftZ = 9;
            if (selectedItem.isCat) {
              selectedItem.state = 'idle';
              selectedItem.posture = 'sit';
              selectedItem.isWalking = false;
            }
          } else if (onDeskArea) {
            // Colocou NA MESA!
            selectedItem.surface = 'desk';
            selectedItem.liftZ = 21;

            if (selectedItem.isProp) {
              // Snap magnético aos slots do tampo (The Sims / Animal Crossing)
              let closestSlot = null;
              let minDist = 14;
              for (const slot of DESK_SLOTS) {
                const d = Math.hypot(localX - slot.offX, localY - slot.offY);
                if (d < minDist) {
                  minDist = d;
                  closestSlot = slot;
                }
              }
              const snapLocalX = closestSlot ? closestSlot.offX : localX;
              const snapLocalY = closestSlot ? closestSlot.offY : localY;

              const worldOffX = snapLocalX * cosD - snapLocalY * sinD;
              const worldOffY = snapLocalX * sinD + snapLocalY * cosD;

              selectedItem.offX = worldOffX;
              selectedItem.offY = worldOffY;
              selectedItem.x = desk.x + worldOffX;
              selectedItem.y = desk.y + worldOffY;
              selectedItem.selfAngle = desk.selfAngle;
            } else if (selectedItem.isCat) {
              // Gato colocado na mesa: dorme ali por um tempo antes de descer!
              const clampLX = Math.max(-32, Math.min(32, localX));
              const clampLY = Math.max(-11, Math.min(11, localY));
              selectedItem.offX = clampLX * cosD - clampLY * sinD;
              selectedItem.offY = clampLX * sinD + clampLY * cosD;
              selectedItem.x = desk.x + selectedItem.offX;
              selectedItem.y = desk.y + selectedItem.offY;
              selectedItem.deskSleepTimer = 360 + Math.floor(Math.random() * 240); // 6 a 10s dormindo
              selectedItem.state = 'idle';
              selectedItem.posture = 'loaf';
              selectedItem.isWalking = false;
            } else if (selectedItem.isChicken) {
              // Pintinho ou Popó na mesa
              const clampLX = Math.max(-34, Math.min(34, localX));
              const clampLY = Math.max(-12, Math.min(12, localY));
              selectedItem.offX = clampLX * cosD - clampLY * sinD;
              selectedItem.offY = clampLX * sinD + clampLY * cosD;
              selectedItem.x = desk.x + selectedItem.offX;
              selectedItem.y = desk.y + selectedItem.offY;
              selectedItem.state = 'idle';
              selectedItem.stateTimer = 90;
              selectedItem.isWalking = false;
            }
          } else if (onShelfArea) {
            // Colocou NA PRATELEIRA!
            selectedItem.surface = 'shelf';
            selectedItem.liftZ = shelf.liftZ + 3.5;
            selectedItem.x = -ROOM_R + 9;
            selectedItem.offY = Math.max(-shelf.length / 2 + 8, Math.min(shelf.length / 2 - 8, selectedItem.y - shelf.y));
            selectedItem.y = shelf.y + selectedItem.offY;
            selectedItem.selfAngle = 0;
            if (selectedItem.isCat) {
              selectedItem.state = 'idle';
              selectedItem.posture = 'loaf';
              selectedItem.isWalking = false;
            } else if (selectedItem.isChicken) {
              selectedItem.state = selectedItem.id === 'chicken' ? 'brood' : 'idle';
              selectedItem.stateTimer = 240;
              selectedItem.isWalking = false;
            }
          } else {
            // Colocou NO CHÃO!
            selectedItem.surface = null;
            selectedItem.liftZ = 0;
            if (selectedItem.isCat) selectedItem.deskSleepTimer = 0;
          }
        }
        return;
      }

      // Arrastando visão do quarto
      if (isDraggingView) {
        const dx = e.clientX - lastX;
        lastX = e.clientX;
        targetTurn += dx * 0.015;
      }
    });

    window.addEventListener('pointerup', (e) => {
      if (!isDecorMode && !isDraggingItem && pointerDownPos) {
        const moved = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y);
        const { sx, sy } = getCanvasCoords(e);
        const worldPos = unproject(sx, sy);

        // Clique no Mural de Post-its abre o Zoom / Modal de Lembretes!
        const q = getCorkboardQuad();
        if (q) {
          const isInside = isPointInWallQuad(sx, sy, q.p1, q.p2, q.p3, q.p4, 4);
          if (isPressedOnCorkboard || (moved < 25 && isInside)) {
            isPressedOnCorkboard = false;
            openCorkboardModal();
            return;
          }
        }
        isPressedOnCorkboard = false;

        if (moved < 18) {

          // Clique na Galinha Cocoricó faz ela cacarejar alegremente!
          const chk = items.find(it => it.id === 'chicken' && it.visible !== false);
          if (chk) {
            const dChk = Math.hypot(worldPos.x - chk.x, worldPos.y - chk.y);
            if (dChk < 22) {
              playChickenSound();
              hearts.push({ x: chk.x, y: chk.y, z: chk.liftZ + 16, life: 1.0 });
              return;
            }
          }

          // Checa clique em qualquer porta do cômodo atual
          const clickedDoor = items.find(it => (it.isDoor || it.id === 'door' || it.id.startsWith('door_')) && it.visible !== false && (() => {
            const wallNorm = (it.wall === 'west') ? {x:-1, y:0} : (it.wall === 'south') ? {x:0, y:1} : (it.wall === 'north') ? {x:0, y:-1} : {x:1, y:0};
            const isWallVis = (wallNorm.x * Math.sin(turn) + wallNorm.y * Math.cos(turn) <= 0.05);
            if (!isWallVis) return false;
            const pDoor = project(it.x, it.y, 38);
            return Math.hypot(sx - pDoor.x, sy - pDoor.y) < 32;
          })());

          if (clickedDoor) {
            clickedDoor.isOpen = !clickedDoor.isOpen;
            playDoorSound(clickedDoor.isOpen);
            if (clickedDoor.targetRoom) {
              if (clickedDoor.targetRoom === 'kitchen' || clickedDoor.targetRoom === 'garden') {
                switchRoom(clickedDoor.targetRoom);
              } else {
                migratePetsToDoor(clickedDoor, () => switchRoom(clickedDoor.targetRoom, true));
              }
            }
            return;
          }
          const cat = items.find(it => it.id === 'cat');
          if (cat) {
            const dCat = Math.hypot(worldPos.x - cat.x, worldPos.y - cat.y);
            if (dCat < 24) {
              triggerPetReactions(cat);
            } else if (Math.abs(worldPos.x) < ROOM_R - 18 && Math.abs(worldPos.y) < ROOM_R - 18) {
              const valid = checkCatCollision(worldPos.x, worldPos.y);
              cat.targetX = valid.x;
              cat.targetY = valid.y;
              cat.state = 'walking';
              cat.posture = 'walk';
            }
          }
        }
      }
      isDraggingItem = false;
      isDraggingView = false;
      canvas.classList.remove('decor-dragging');
    });


    // --- ÁUDIO DA GALINHA E TACHINHA ---
    function playChickenSound() {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(360, now);
        osc.frequency.exponentialRampToValueAtTime(580, now + 0.05);
        osc.frequency.exponentialRampToValueAtTime(260, now + 0.16);
        const filter = audioCtx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1400, now);
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.2, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
        osc.connect(filter);
        filter.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.19);
      } catch(e) {}
    }

    function playTackSound() {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(540, now);
        osc.frequency.exponentialRampToValueAtTime(120, now + 0.04);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
      } catch(e) {}
    }

    // --- GERENCIADOR DO MURAL DE POST-ITS (localStorage) ---
    const corkboardModal = document.getElementById('corkboardModal');
    const btnCloseCorkboard = document.getElementById('btnCloseCorkboard');
    const corkboardSurface = document.getElementById('corkboardSurface');
    const corkboardPadBtn = document.getElementById('corkboardPadBtn');

    const noteEditorModal = document.getElementById('noteEditorModal');
    const noteEditorCard = document.getElementById('noteEditorCard');
    const noteTextarea = document.getElementById('noteTextarea');
    const btnSaveNote = document.getElementById('btnSaveNote');
    const btnDeleteNote = document.getElementById('btnDeleteNote');
    const btnCancelNote = document.getElementById('btnCancelNote');
    const colorDots = document.querySelectorAll('.color-dot');

    let currentEditingNoteId = null;
    let selectedNoteColor = '#FEF08A';

    const PASTEL_COLORS = ['#FEF08A', '#FBCFE8', '#BBF7D0', '#BAE6FD', '#E9D5FF', '#FED7AA'];

    function getSavedNotes() {
      try {
        const raw = localStorage.getItem('purrmodoro_notes');
        if (raw) return JSON.parse(raw);
      } catch(e) {}
      // Notas padrão de boas-vindas
      return [
        { id: 1, text: "✨ Bem-vindo ao cantinho do Mochi!\n\n- Fazer carinho no gatinho 💕\n- Regar as plantinhas 🪴\n- Tomar um café quentinho ☕", color: '#FEF08A', rot: -2 },
        { id: 2, text: "🐾 Metas:\n- Cuidar da galinha 🐔\n- Estudar 2 pomodoros 🍅\n- Testar novos chapéus!", color: '#FBCFE8', rot: 1.5 },
        { id: 3, text: "💡 Lembrete:\nVocê pode girar a mesa com a tecla R e organizar tudo!", color: '#BAE6FD', rot: -1 }
      ];
    }

    function saveNotesToStorage(notes) {
      try {
        localStorage.setItem('purrmodoro_notes', JSON.stringify(notes));
      } catch(e) {}
    }

    function renderCorkboardNotes() {
      corkboardSurface.innerHTML = '';
      const notes = getSavedNotes();
      notes.forEach(note => {
        const card = document.createElement('div');
        card.className = 'postit-card';
        card.style.background = note.color || '#FEF08A';
        card.style.transform = `rotate(${note.rot || 0}deg)`;
        card.innerHTML = `
          <div class="postit-pin"></div>
          <div style="white-space: pre-wrap; flex:1; overflow:hidden;">${note.text || ''}</div>
        `;
        card.addEventListener('click', () => {
          openNoteEditor(note.id);
        });
        corkboardSurface.appendChild(card);
      });
    }

    function openCorkboardModal() {
      playTackSound();
      renderCorkboardNotes();
      corkboardModal.classList.add('open');
    }

    function closeCorkboardModal() {
      corkboardModal.classList.remove('open');
    }

    btnCloseCorkboard.addEventListener('click', closeCorkboardModal);

    // Abrir editor para novo post-it ou editar existente
    function openNoteEditor(noteId) {
      playTackSound();
      currentEditingNoteId = noteId;
      if (noteId) {
        const notes = getSavedNotes();
        const note = notes.find(n => n.id === noteId);
        if (note) {
          noteTextarea.value = note.text;
          selectedNoteColor = note.color || '#FEF08A';
          btnDeleteNote.style.display = 'inline-flex';
        }
      } else {
        // Novo post-it: cor pastel aleatória
        selectedNoteColor = PASTEL_COLORS[Math.floor(Math.random() * PASTEL_COLORS.length)];
        noteTextarea.value = '';
        btnDeleteNote.style.display = 'none';
      }

      noteEditorCard.style.background = selectedNoteColor;
      colorDots.forEach(d => {
        d.classList.toggle('active', d.dataset.color === selectedNoteColor);
      });

      noteEditorModal.classList.add('open');
      setTimeout(() => noteTextarea.focus(), 100);
    }

    function closeNoteEditor() {
      noteEditorModal.classList.remove('open');
    }

    corkboardPadBtn.addEventListener('click', () => {
      openNoteEditor(null);
    });

    colorDots.forEach(dot => {
      dot.addEventListener('click', () => {
        selectedNoteColor = dot.dataset.color;
        colorDots.forEach(d => d.classList.remove('active'));
        dot.classList.add('active');
        noteEditorCard.style.background = selectedNoteColor;
      });
    });

    btnCancelNote.addEventListener('click', closeNoteEditor);

    btnSaveNote.addEventListener('click', () => {
      const text = noteTextarea.value.trim();
      if (!text) {
        closeNoteEditor();
        return;
      }
      playTackSound();
      const notes = getSavedNotes();
      if (currentEditingNoteId) {
        const note = notes.find(n => n.id === currentEditingNoteId);
        if (note) {
          note.text = text;
          note.color = selectedNoteColor;
        }
      } else {
        notes.push({
          id: Date.now(),
          text: text,
          color: selectedNoteColor,
          rot: Math.round((Math.random() * 6 - 3) * 10) / 10
        });
      }
      saveNotesToStorage(notes);
      closeNoteEditor();
      renderCorkboardNotes();
    });

    btnDeleteNote.addEventListener('click', () => {
      if (currentEditingNoteId) {
        playTackSound();
        let notes = getSavedNotes();
        notes = notes.filter(n => n.id !== currentEditingNoteId);
        saveNotesToStorage(notes);
        closeNoteEditor();
        renderCorkboardNotes();
      }
    });

    // Botão Modo Decoração
    const btnDecorMode = document.getElementById('btnDecorMode');
    const bannerInfo = document.getElementById('bannerInfo');
    const btnRotateMob = document.getElementById('btnRotateMob');
    const btnRotateSelected = document.getElementById('btnRotateSelected');

    btnDecorMode.addEventListener('click', () => {
      isDecorMode = !isDecorMode;
      btnDecorMode.classList.toggle('active', isDecorMode);
      bannerInfo.style.display = isDecorMode ? 'flex' : 'none';
      canvas.classList.toggle('decor-mode', isDecorMode);
      if (!isDecorMode) {
        selectedItem = null;
        btnRotateMob.style.display = 'none';
      }
    });

    btnRotateMob.addEventListener('click', rotateSelectedItem);
    btnRotateSelected.addEventListener('click', rotateSelectedItem);

    const btnAutoSpin = document.getElementById('btnAutoSpin');
    btnAutoSpin.addEventListener('click', () => {
      autoSpin = !autoSpin;
      btnAutoSpin.classList.toggle('active', autoSpin);
    });

    // Botão de Chapéu (Ciclo: Nenhum -> Bruxo -> Coroa -> Boina -> Sakura)
    const hatKeys = ['none', 'witch', 'crown', 'beret', 'flower'];
    const hatNames = {
      none: '🎩 Chapéu: Nenhum',
      witch: '🧙 Bruxo',
      crown: '👑 Coroa',
      beret: '🧑‍🎨 Boina',
      flower: '🌸 Sakura'
    };
    let currentHatIdx = 0;
    let selectedHatPetId = 'cat';
    const btnHat = document.getElementById('btnHat');
    btnHat.addEventListener('click', () => {
      currentHatIdx = (currentHatIdx + 1) % hatKeys.length;
      const hatKey = hatKeys[currentHatIdx];
      const targetPet = items.find(it => it.id === selectedHatPetId) || items.find(it => it.id === 'cat');
      if (targetPet) {
        targetPet.hat = hatKey;
        if (targetPet.id === 'cat') playMeowSound();
        else playChickenSound();
      }
      btnHat.textContent = hatNames[hatKey];
      if (currentDrawerTab === 'hats') renderAssetList();
    });

    // Botão de Postura (Ciclo: Auto -> Andar -> Sentar -> Pãozinho -> Barriga)
    const postures = [
      { key: 'auto', label: '🐾 Modo: Auto' },
      { key: 'walk', label: '🚶 Andando' },
      { key: 'sit', label: '🐱 Sentado' },
      { key: 'loaf', label: '🍞 Pãozinho' },
      { key: 'belly', label: '💖 Barriguinha' }
    ];
    let currentPostureIdx = 0;
    const btnPosture = document.getElementById('btnPosture');
    btnPosture.addEventListener('click', () => {
      currentPostureIdx = (currentPostureIdx + 1) % postures.length;
      const p = postures[currentPostureIdx];
      const cat = items.find(it => it.id === 'cat');
      if (cat) {
        cat.forcedPosture = (p.key === 'auto') ? null : p.key;
        if (p.key !== 'auto') cat.posture = p.key;
      }
      btnPosture.textContent = p.label;
    });

    // Botão de Carinho
    document.getElementById('btnPet').addEventListener('click', () => {
      const cat = items.find(it => it.id === 'cat');
      if (cat) triggerPetReactions(cat);
    });

    const squashSlider = document.getElementById('squashSlider');
    squashSlider.addEventListener('input', (e) => {
      squash = parseFloat(e.target.value);
    });

    // Gerenciador do Catálogo de Assets
    const btnCatalog = document.getElementById('btnCatalog');
    const assetDrawer = document.getElementById('assetDrawer');
    const btnCloseDrawer = document.getElementById('btnCloseDrawer');
    const btnShowAll = document.getElementById('btnShowAll');
    const btnHideAll = document.getElementById('btnHideAll');
    const assetList = document.getElementById('assetList');

    let currentDrawerTab = 'furniture';
    const drawerActions = document.getElementById('drawerActions');

    // Tab buttons wiring
    document.querySelectorAll('.drawer-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.drawer-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentDrawerTab = tab.getAttribute('data-cat');
        renderAssetList();
      });
    });

    const hatOptions = [
      { key: 'none',   name: 'Sem Chapéu',           icon: '❌', desc: 'Gatinho ao natural' },
      { key: 'witch',  name: 'Chapéu de Bruxo',      icon: '🧙', desc: 'Cone místico roxo com fivela dourada' },
      { key: 'crown',  name: 'Coroa Real',           icon: '👑', desc: 'Ouro nobre com pedras de rubi' },
      { key: 'beret',  name: 'Boina Artista',        icon: '🧑‍🎨', desc: 'Lã carmesim estilosa de pintor' },
      { key: 'flower', name: 'Flor de Sakura',       icon: '🌸', desc: 'Pétalas rosadas japonesas' },
    ];

    function renderAssetList() {
      assetList.innerHTML = '';
      const cat = items.find(it => it.id === 'cat');

      if (currentDrawerTab === 'hats') {
        drawerActions.style.display = 'none';

        // 1. SELETOR DE PET PARA VESTIR CHAPÉU (Mochi, Popó, Pintinho)
        const petSelectorRow = document.createElement('div');
        petSelectorRow.style.cssText = 'display:flex; gap:6px; margin-bottom:12px; background:#F5EDE2; padding:4px; border-radius:10px;';

        const petChoices = [
          { id: 'cat', name: '🐱 Mochi' },
          { id: 'chicken', name: '🐔 Popó' },
          { id: 'chick', name: '🐥 Pintinho' }
        ];

        petChoices.forEach(pc => {
          const btnP = document.createElement('button');
          btnP.textContent = pc.name;
          const isAct = (selectedHatPetId === pc.id);
          btnP.style.cssText = `flex:1; border:none; padding:6px 4px; border-radius:8px; font-size:11px; font-weight:700; cursor:pointer; background:${isAct ? '#D87D4A' : 'transparent'}; color:${isAct ? '#FFF' : '#6E472D'}; transition:0.2s;`;
          btnP.addEventListener('click', () => {
            selectedHatPetId = pc.id;
            renderAssetList();
          });
          petSelectorRow.appendChild(btnP);
        });
        assetList.appendChild(petSelectorRow);

        const currentTargetPet = items.find(it => it.id === selectedHatPetId);

        hatOptions.forEach(h => {
          const card = document.createElement('div');
          card.className = 'asset-card';
          const isEquipped = (currentTargetPet && (currentTargetPet.hat || 'none') === h.key);
          const hatDesc = selectedHatPetId === 'chick' && h.key !== 'none' 
            ? `${h.desc} (Pintinho fica escondido dentro!)`
            : (selectedHatPetId === 'chicken' && h.key !== 'none' ? `${h.desc} (Inclinado charmoso na crista)` : h.desc);

          card.innerHTML = `
            <div style="display:flex; flex-direction:column; gap:2px;">
              <span class="asset-name">${h.icon} ${h.name}</span>
              <span style="font-size:10px; color:#8C6A54;">${hatDesc}</span>
            </div>
            <button class="btn-toggle ${isEquipped ? 'on' : 'off'}">
              ${isEquipped ? '✓ Equipado' : 'Equipar'}
            </button>
          `;
          card.querySelector('.btn-toggle').addEventListener('click', () => {
            if (currentTargetPet) {
              currentTargetPet.hat = h.key;
              if (selectedHatPetId === 'cat') {
                currentHatIdx = hatKeys.indexOf(h.key);
                btnHat.textContent = hatNames[h.key];
                playMeowSound();
              } else {
                playChickenSound();
              }
              renderAssetList();
            }
          });
          assetList.appendChild(card);
        });

      } else if (currentDrawerTab === 'pets') {
        drawerActions.style.display = 'none';

        // 1. PRESENÇA DOS BICHINHOS NO QUARTO (Pode ter Gato, Popó e Pintinho juntos ou tirar quem quiser!)
        const hPetsPresence = document.createElement('div');
        hPetsPresence.style.cssText = 'font-size:12px; font-weight:800; color:#532F16; margin:6px 0 6px;';
        hPetsPresence.textContent = '🐾 Companheiros no Quarto (Ative até 3 bichinhos):';
        assetList.appendChild(hPetsPresence);

        const petItems = items.filter(it => it.id === 'cat' || it.id === 'chicken' || it.id === 'chick');
        petItems.forEach(pet => {
          const card = document.createElement('div');
          card.className = 'asset-card';
          const isVis = pet.visible !== false;
          card.innerHTML = `
            <div style="display:flex; flex-direction:column; gap:2px;">
              <span class="asset-name">${pet.icon || '🐾'} ${pet.name}</span>
              <span style="font-size:10px; color:#8C6A54;">${pet.id === 'cat' ? 'Gatinho companheiro de estudos' : (pet.id === 'chicken' ? 'Galinha que cisca e passeia rebolando' : 'Filhotinho fofo da Popó')}</span>
            </div>
            <button class="btn-toggle ${isVis ? 'on' : 'off'}">
              ${isVis ? '✓ No Quarto' : '+ Chamar'}
            </button>
          `;
          card.querySelector('.btn-toggle').addEventListener('click', () => {
            pet.visible = !isVis;
            if (pet.id === 'cat') playMeowSound();
            else playChickenSound();
            renderAssetList();
          });
          assetList.appendChild(card);
        });

        // 2. PELAGENS DO GATINHO MOCHI
        const hCatSkins = document.createElement('div');
        hCatSkins.style.cssText = 'font-size:12px; font-weight:800; color:#532F16; margin:16px 0 6px;';
        hCatSkins.textContent = '🎨 Escolha a Pelagem do Gatinho:';
        assetList.appendChild(hCatSkins);

        for (const [key, skin] of Object.entries(CAT_SKINS)) {
          const card = document.createElement('div');
          card.className = 'asset-card';
          const isSelected = (currentCatSkin === key);
          card.innerHTML = `
            <div style="display:flex; flex-direction:column; gap:2px;">
              <span class="asset-name">${skin.icon} ${skin.name}</span>
              <span style="font-size:10px; color:#8C6A54;">${skin.desc}</span>
            </div>
            <button class="btn-toggle ${isSelected ? 'on' : 'off'}">
              ${isSelected ? '✓ Ativo' : 'Escolher'}
            </button>
          `;
          card.querySelector('.btn-toggle').addEventListener('click', () => {
            currentCatSkin = key;
            const cat = items.find(it => it.id === 'cat');
            if (cat) cat.visible = true; // Ativa o gatinho se escolher uma pelagem
            playMeowSound();
            renderAssetList();
          });
          assetList.appendChild(card);
        }

      } else {
        drawerActions.style.display = 'flex';
        const filtered = items.filter(it => it.category === currentDrawerTab && !it.isCat && !it.isChicken);

        filtered.forEach(item => {
          const card = document.createElement('div');
          card.className = 'asset-card';
          const isVis = item.visible !== false;
          card.innerHTML = `
            <span class="asset-name">${item.icon || '📦'} ${item.name}</span>
            <div style="display:flex; gap:6px; align-items:center;">
              <button class="btn-focus" title="Focar e Selecionar" style="border:none; background:#EDE4D6; color:#3B2A20; border-radius:8px; padding:3px 7px; font-size:12px; cursor:pointer; font-weight:600;">🎯</button>
              <button class="btn-toggle ${isVis ? 'on' : 'off'}">
                ${isVis ? '✓ Ativo' : '+ Adicionar'}
              </button>
            </div>
          `;
          card.querySelector('.btn-focus').addEventListener('click', () => {
            item.visible = true;
            if (!isDecorMode) {
              isDecorMode = true;
              btnDecorMode.classList.add('active');
              bannerInfo.style.display = 'flex';
              canvas.classList.add('decor-mode');
            }
            selectedItem = item;
            btnRotateMob.style.display = item.isWallItem ? 'none' : 'inline-flex';
            bannerInfo.innerHTML = `<span>🎯 <b>Item Focado:</b> ${item.icon || ''} ${item.name} selecionado!</span>`;
            renderAssetList();
          });
          card.querySelector('.btn-toggle').addEventListener('click', () => {
            item.visible = !isVis;
            renderAssetList();
          });
          assetList.appendChild(card);
        });
      }
    }

        // --- EVENTOS DO MODAL DA PLANTA BAIXA ---
    const btnHousePlan = document.getElementById('btnHousePlan');
    const housePlanModal = document.getElementById('housePlanModal');
    const btnCloseHousePlan = document.getElementById('btnCloseHousePlan');
    const roomCardBedroom = document.getElementById('roomCardBedroom');
    const roomCardLiving = document.getElementById('roomCardLiving');
    const roomCardKitchen = document.getElementById('roomCardKitchen');
    const roomCardGarden = document.getElementById('roomCardGarden');

    if (btnHousePlan && housePlanModal) {
      btnHousePlan.addEventListener('click', () => {
        housePlanModal.classList.add('open');
        updateHousePlanBadges();
      });
      btnCloseHousePlan.addEventListener('click', () => {
        housePlanModal.classList.remove('open');
      });
      housePlanModal.addEventListener('click', (e) => {
        if (e.target === housePlanModal) housePlanModal.classList.remove('open');
      });

      roomCardBedroom.addEventListener('click', () => {
        housePlanModal.classList.remove('open');
        if (currentRoomId !== 'bedroom') {
          const doorToBed = items.find(it => it.targetRoom === 'bedroom');
          if (doorToBed) migratePetsToDoor(doorToBed, () => switchRoom('bedroom'));
          else switchRoom('bedroom');
        }
      });

      roomCardLiving.addEventListener('click', () => {
        housePlanModal.classList.remove('open');
        if (currentRoomId !== 'living') {
          const doorToLiv = items.find(it => it.targetRoom === 'living');
          if (doorToLiv) migratePetsToDoor(doorToLiv, () => switchRoom('living'));
          else switchRoom('living');
        }
      });

      roomCardKitchen.addEventListener('click', () => {
        showToast("🍽️ Cozinha: O cheirinho de peixe tá saindo do forno... Em breve!");
      });

      roomCardGarden.addEventListener('click', () => {
        showToast("🌳 Jardim: O gramado tá sendo podado para o banho de sol... Em breve!");
      });
    }

    btnCatalog.addEventListener('click', () => {
      const isVisible = assetDrawer.style.display !== 'none';
      assetDrawer.style.display = isVisible ? 'none' : 'flex';
      btnCatalog.classList.toggle('active', !isVisible);
      if (!isVisible) renderAssetList();
    });

    btnCloseDrawer.addEventListener('click', () => {
      assetDrawer.style.display = 'none';
      btnCatalog.classList.remove('active');
    });

    btnShowAll.addEventListener('click', () => {
      items.forEach(it => it.visible = true);
      renderAssetList();
    });

    btnHideAll.addEventListener('click', () => {
      items.forEach(it => it.visible = false);
      renderAssetList();
    });

    renderAssetList();
  </script>
</body>
</html>
"""

html_final = html_template.replace('__CAT_BODY_SLICES__', cat_body_slices_json)\
                          .replace('__CAT_PAW_SLICES__', cat_paw_slices_json)\
                          .replace('__CAT_BELLY_SLICES__', cat_belly_slices_json)\
                          .replace('__WITCH_HAT_SLICES__', witch_hat_slices)\
                          .replace('__CROWN_HAT_SLICES__', crown_hat_slices)\
                          .replace('__BERET_HAT_SLICES__', beret_hat_slices)\
                          .replace('__FLOWER_HAT_SLICES__', flower_hat_slices)\
                          .replace('__DESK_SLICES__', desk_slices)\
                          .replace('__LAPTOP_SLICES__', laptop_slices)\
                          .replace('__TABLET_SLICES__', tablet_slices)\
                          .replace('__DESK_BOOKS_SLICES__', desk_books_slices)\
                          .replace('__MUG_SLICES__', mug_slices)\
                          .replace('__PLANT_SLICES__', plant_slices)\
                          .replace('__BED_SLICES__', bed_slices)\
                          .replace('__TREE_SLICES__', tree_slices)\
                          .replace('__SOFA_SLICES__', sofa_slices)\
                          .replace('__COFFEE_TABLE_SLICES__', coffee_table_slices)\
                          .replace('__TV_RACK_SLICES__', tv_rack_slices)\
                          .replace('__BOOKSHELF_SLICES__', bookshelf_slices)\
                          .replace('__BS_ENC_SLICES__', bs_enc_slices)\
                          .replace('__BS_PLANT_SLICES__', bs_plant_slices)\
                          .replace('__BS_CRYSTAL_SLICES__', bs_crystal_slices)\
                          .replace('__BS_STACK_SLICES__', bs_stack_slices)\
                          .replace('__BS_TROPHY_SLICES__', bs_trophy_slices)

with open('C:/github/PixelArt/room-3d.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

with open('C:/github/PixelArt/index.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

print("SUCCESS: C:/github/PixelArt/room-3d.html and index.html generated with clean shelf and movable wall items!")
