    // =========================================================================
    // ENGINE: CONFIGURAÇÃO DO MUNDO (TAMANHO DO GRID CONFIGURÁVEL)
    // Presets: 128 (micro diorama), 256 (diorama), 512 (médio), 1080 (mundo aberto)
    // Prioridade: window.__WORLD_CFG__  >  ?grid=N na URL  >  padrão 1080
    // =========================================================================
    const WORLD_SIZE_PRESETS = [128, 256, 512, 1080];
    const WORLD_CFG = (function () {
      const user = window.__WORLD_CFG__ || {};
      const urlGrid = parseInt(new URLSearchParams(window.location.search).get('grid'), 10);
      let gridW = Number.isFinite(user.gridW) ? user.gridW : (Number.isFinite(urlGrid) ? urlGrid : 1080);
      gridW = Math.max(64, Math.min(2048, Math.round(gridW / 2) * 2));
      const gridH = Number.isFinite(user.gridH) ? Math.max(64, Math.min(2048, Math.round(user.gridH / 2) * 2)) : gridW;
      return {
        gridW,
        gridH,
        vox: Number.isFinite(user.vox) ? user.vox : 2,
        isDefault: gridW === 1080 && gridH === 1080
      };
    })();

