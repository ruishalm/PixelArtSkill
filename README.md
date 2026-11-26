# 🎨 `pixel-art-3d` — 3D Pixel Art & Sprite Stacking Skill (Pure HTML5 Canvas 2D)

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demos-brightgreen?logo=github)](https://ruishalm.github.io/PixelArtSkill/)
[![Tech](https://img.shields.io/badge/HTML5-Pure%20Canvas%202D-E34F26?logo=html5&logoColor=white)](#)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Vanilla%20JS)-blue)](#)
[![No WebGL](https://img.shields.io/badge/3D%20Engine-No%20WebGL%20%2F%20No%20Three.js-orange)](#)
[![Skill](https://img.shields.io/badge/Antigravity-pixel--art--3d%20Skill-purple)](./SKILL.md)

> **`pixel-art-3d`** ([`SKILL.md`](./SKILL.md)) is an engineering skill for AI agents to build **3D / pseudo-3D pixel art scenes, objects, characters, dioramas, and open worlds** in **pure HTML5 Canvas 2D** using **Sprite Stacking (Z-axis voxel slicing)** — with **zero WebGL, zero Three.js, and zero runtime dependencies**, emitting self-contained HTML files running at ~60 FPS.

---

## ⚡ Installation & Usage

### Skill Path
- **Global (Antigravity):** `~/.gemini/config/skills/pixel-art-3d/SKILL.md`
- **Local (this repository):** [`./SKILL.md`](./SKILL.md)

### Standard 3-Step Workflow
1. **Python Generator (`make_grid` / `fill_box` / `to_strings`)**: models each asset in horizontal slices `slices[z][y][x]` with a Base-36 palette (`'0'..'9'`, `'a'..'z'`).
2. **Base-36 JSON / Heightfield Pack**: exports `{ "palette": [...], "slices": [[...]] }` (or procedural `1080×1080` terrain directly in the engine).
3. **Self-Contained HTML5 Canvas 2D**: bundles the data into the engine (`imageSmoothingEnabled = false`) with a low-res offscreen buffer, `1:1` integer upscaling, and a **Hi-Res Overlay Pass** for UI and text.

### Quick Copyable Prompt

```text
NON-NEGOTIABLE PROJECT RULES (Pure Canvas 2D Sprite Stacking):
1. TECHNOLOGY: Use EXCLUSIVELY pure HTML5 Canvas 2D (ctx.imageSmoothingEnabled = false), a low-res offscreen buffer + integer upscaling, and voxel JSON matrices generated in Python. FORBIDDEN: Three.js, WebGL, GLSL shaders, or external 3D libraries.
2. PYTHON -> JSON MODELING: Build each model with make_grid(w, h, fill=0), fill_box(...) and to_strings(slices) returning list[list[str]] (NEVER flatten all rows of a slice into a single string). Support Base-36 ('0'..'9','a'..'z'), '0' transparent, y=0 BACK and y=H-1 FRONT.
3. RENDER & SILHOUETTE: Use squash = 0.75, drawStackObject with totalAngle = selfAngle + turn, and a single 1px outer silhouette (#3B2219 or #3B2A20) via offscreen canvas after stacking all slices (FORBIDDEN to outline individual slices).
4. WALLS & HOLLOW FURNITURE: Use dynamic Wall Culling (nyRot = nx*sin(turn) + ny*cos(turn) > 0.05 -> 3px baseboard + disable hitbox) and angular occlusion on shelves/niches (solid back + side walls + redraw side walls per tier when cosFront > 0.22).
5. TERRAIN & PHYSICS (if applicable): For natural landscapes, prefer the 1080x1080 Organic Micro-Voxel Engine ("Pull-Chain", VOX=2u = 2,160x2,160u, Anti-Kaiju 1.5x): sculpting via fbm2d/fbm2dFast/pullHill(cos^steepness)/pullPlateau(cliffMask; useWarp=false only on ruins)/carveRiverPath/elasticChainRelax + 6-Formula Geological Kit (warp2d with fbm2dFast, smax/smin, ridgedFbm/pullRidge, rockTerrace, carveBenchTrail, thermalAndHydraulicErosion) + addArchBridge/getBridgeDeckZ (z_deck(u) = z_base + H_arch*(1-(2u-1)^2), 3-slice deck over MAT_WATER, abutments u <= 0.09 || u >= 0.91 + railings) + organic ponds (warp2d) + foam restricted to real drops h - min8 > 4 + pullRuinsBlock (max(|dx|/halfW, |dy|/halfD) with fbm2d * 0.08), pre-baked into Tight-Crop Bounded Slices ({canvas,offX,offY,w,h} via Uint32Array) with min8-2 shell + gradient shading + organic 2-3px grass tufts (fbm2d > 0.43 + gridless hash, noOutline, 8 FPS), slice-by-slice render with O(1) culling + entityLayer (destination-out + single 1px #3B2219 outline) + particlesByZ (Math.round(p.z) drawn inside the loop after terrainSlices[z], no black outline) + 2.5D Fluid Mechanics (WindField with altBoost and leeward shadow ∇h·W<0; WaterFlow/sampleWaterFlow with Rankine Dipole around getActiveWaterObstacles + RK2 flowStreaks + smoothstep Drain Sink; conservative 40x26 Virtual Pipe waterfallSim with cliff lateral suppression latGain=0.025/latDamp=0.45 and wfBlockH coupled to isDamBoulder; walkable MAT_SHALLOW=8; 120x80 30 Hz WaveBuffer with !isWetMat + obstacle u=0 mask + upwind Kelvin V-wakes + 6-cell sponge boundary γ=0.72 vs 0.955 + |u|<0.008->0 cutoff) and continuous physics (AUTO_STEP_MAX=5.5 + ±35° tangential sliding + 5x5 standableMap/cliffTopMap).
6. 6-CLASS TAXONOMY & REACTIVE FOLIAGE (isCharacter / isFoliage): Classify every asset strictly into one of the 6 official classes: Character (isCharacter, humans/NPCs/animals/creatures; legacy alias isPet), Fixed (isFixed), Movable (isMovable), Surface Prop (isProp), Wall/Portal (isWallItem/isDoor), or Foliage (isFoliage with rigidity 0..1, windScale, pushRadius, pushStrength, leafColors). For Foliage, apply Parabolic Cantilever Bend Δp(s_z) = (s_z/(H-1))^2 * b (base s_z=0 anchored to ground, no pixel rotation blur), Damped Spring a = k_stiff*(W(x,y,t)*windScale*(1-rigidity) - b) + F_push(entities) - c_damp*v, and Fluid<->Foliage coupling.
7. PROCEDURAL DESTRUCTION (Destructible & zCut): Without modeling separate falling sprites, split the same slice sheet into a fixed base (0..zCut-1 -> 'platform' collider) and dynamic top (zCut..count-1), supporting 'chop' (3D inverted pendulum with Newton's 3rd Law — falls in hit direction + player recoil), 'crumble' (chipped 'platform' base + stone_chunk; clean shatter on isDamBoulder calling rebuildWaterfallBlocks()) and 'trim' (Foliage spring + WindField leaf burst), triggered via KeyR or canvas click (KeyQ/KeyE to rotate, KeyC for spawn) with 2x tool affinity multipliers (tool_axe, tool_pickaxe, tool_hoe).
```

---

## 🧭 What's Inside the Skill (`SKILL.md`)

1. **Paradigm Selector (Pure Canvas 2D Mandatory)**: establishes *Sprite Stacking* on Canvas 2D (`imageSmoothingEnabled = false`) as the sole official runtime architecture, forbidding Three.js/WebGL/GLSL in the standard pipeline.
2. **Strict 6-Class Asset Taxonomy**:

   | # | Class | Canonical Flag | Structural Role & Behavior |
   |---|---|---|---|
   | 1 | **Character** | `isCharacter` *(legacy `isPet`)* | Humans, NPCs, animals, and creatures; 2-phase biomechanical locomotion (*Swing* + *Stance*) and rigid articulated sub-stacks (zero horizontal slice shearing). |
   | 2 | **Fixed** | `isFixed` | Architectural and scenic anchors protected against dragging. |
   | 3 | **Movable** | `isMovable` | Repositionable, rotatable furniture with **Synchronized Hierarchical Parenting** (children rotate and translate with their parent). |
   | 4 | **Surface Prop** | `isProp` | Surface objects snapping automatically to the parent's `liftZ` height. |
   | 5 | **Wall / Portal** | `isWallItem` / `isDoor` | Wall items, windows, and doors with projected 3D hitboxes and automatic disable when the wall is culled. |
   | 6 | **Foliage** | `isFoliage` | Reactive vegetation (`rigidity` `0..1`, `windScale`, `pushRadius`, `pushStrength`, `leafColors`) with parabolic cantilever bend, damped spring (`WindField` + entities), and leaf/petal shedding into `particlesByZ` and `floatingItems`. |
3. **Canonical Axis Convention (`+Y = Front`)**: `y = 0` is back, `y = H - 1` is front, `z = 0..D-1` grows bottom-to-top; exact `selfAngle` table per wall (`0`, `π/2`, `π`, `-π/2`) for the default `-45°` camera.
4. **Python → Base-36 JSON & RLE (`*ch<len>;`)**: `make_grid(w, h, fill=0)`, `fill_box(...)`, and `to_strings(slices)` strictly returning `list[list[str]]`, with `'0'` transparent and `'1'..'z'` indexing up to 35 colors; monumental packs support per-line RLE compression (`*<ch><len>;`) cutting JSON size by ~75%.
5. **Single `1px` Silhouette & Grass Exception**: orthogonal dilation `[-1,0],[1,0],[0,-1],[0,1]` on an offscreen scratch canvas after stacking the whole object (`#3B2219` or `#3B2A20`, never pure black and never per slice); `2–3px` grass blades use `noOutline: true`.
6. **Wall Culling & Angular Occlusion**: front-facing walls (`nyRot > 0.05`) collapse to a `3px` baseboard with click hitboxes disabled; hollow furniture (`cosFront > 0.22`) interleaves Z-tiers with solid side-wall redraws over internal props.
7. **`1080×1080` Terrain Engine (`VOX = 2u` = `2,160×2,160u`), Anti-Kaiju `1.5×` & `1:1` Monumental Architecture**: *Pull-Chain* sculpting, 6-formula Geological Kit, *Tight-Crop Bounded Slices*, `destination-out` occlusion via `entityLayer`, 3D `particlesByZ`, parabolic arch bridges, organic lakes vs. waterfalls, SDF ruins, and true `1:1` scale structures without stretching `scale`.
8. **5 Prop Collider Modes**: `'solid'` (cylinder), `'box'` (rotated box), `'platform'` (top landing without unintended `AUTO_STEP`), `'arch'` (two side pillars with clear central span), and `'none'` (decorative), plus automatic trail/bridge clearance in `addProp`.
9. **Hi-Res Overlay Pass & `1:1` Responsiveness**: vector text and speech bubbles (`roundRect`) are always drawn after the nearest-neighbor upscale on the main canvas, keeping pixels 1:1 square on any viewport.
10. **8-Step Pre-Modeling Checklist & Persistence**: mandatory questionnaire before generating assets + 3-slot `DecorStorageService`.

---

## 🧮 Mathematical Formulas & Engine Engineering

### 1. 3D Projection (`project`) & Inverse Projection (`unproject` / `unprojectToGrid`)
Given $(\Delta x, \Delta y, \Delta z) = (w_x - \text{cam}_x,\, w_y - \text{cam}_y,\, w_z - \text{cam}_z)$ and orbital camera angle $\theta = \text{turn}$ (with $\text{squash} = 0.75$ official default, never $< 0.60$):

$$r_x = \Delta x \cos\theta - \Delta y \sin\theta, \qquad r_y = \Delta x \sin\theta + \Delta y \cos\theta$$

$$s_x = c_x + r_x, \qquad s_y = c_y + r_y \cdot \text{squash} - \Delta z, \qquad \text{depth} = r_y$$

- **Inverse Projection (`unproject` / `unprojectToGrid`)**: maps screen coordinates $(p_x, p_y)$ back to plane $Z$ (for drag-and-drop and visible `1080×1080` grid culling):

$$r_x = p_x - c_x, \qquad r_y = \frac{p_y - \big(c_y - (z - \text{cam}_z)\big)}{\text{squash}}$$

$$\Delta x = r_x \cos\theta + r_y \sin\theta, \qquad \Delta y = -r_x \sin\theta + r_y \cos\theta$$

$$g_x = \frac{\text{cam}_x + \Delta x}{\text{VOX}} + \text{HALF\_GRID}, \qquad g_y = \frac{\text{cam}_y + \Delta y}{\text{VOX}} + \text{HALF\_GRID}$$

### 2. Dynamic Wall Culling & Hollow Furniture Angular Occlusion
- **Dynamic Wall Culling**: for each wall with unit normal $(n_x, n_y)$:

$$n_{y,\text{rot}} = n_x \sin\theta + n_y \cos\theta > 0.05$$

  When true, the wall faces the camera, collapses to a `3px` baseboard (`z = 0..3`), and disables click hitboxes on items mounted on it.
- **Hollow Furniture Angular Occlusion** (front opening on $+Y$):

$$\cos(\text{selfAngle} + \theta) > 0.22$$

  If $> 0.22$, interleaves slices per Z-tier, depth-sorted internal props, and solid side-wall redraws (`wallThick`); if $\le 0.22$, back and side walls occlude 100% of the interior.

### 3. Camera-Relative WASD Controls & Canonical Facing (`+Y` = Front)
Given screen input vector $(i_x, i_y)$:

$$\text{moveWorld}_x = i_x \cos\theta + i_y \sin\theta, \qquad \text{moveWorld}_y = -i_x \sin\theta + i_y \cos\theta$$

$$\text{targetAngle} = \operatorname{atan2}(-\text{moveWorld}_x,\, \text{moveWorld}_y)$$

### 4. Vertical Physics (`H = 16u`), Minimum Foothold (`standableMap`) & Sliding (`±35°`)
- **Jump Kinematics (`H = 16u`, `g = 1200`)**:

$$v_0 = \sqrt{2g(2H + \text{margin})} = \sqrt{2 \cdot 1200 \cdot 35.0} \approx 289.8\,\text{u/s}$$

  Reaches ~`35u` apex, with **`AUTO_STEP_MAX = 5.5u`**, **Coyote Time (`0.11s`)**, and **Jump Buffer (`0.13s`)**.
- **Minimum Foothold (`standableMap` + `cliffTopMap`)**: **`5×5`** window requiring **`nearCount >= 14`** of `25` non-water micro-voxels with $|h_v - h_0| \le 3\text{u}$, valley-floor guard ($h_0 - \min_5 \le 2$), and narrow cliff-ledge rejection, paired with `cliffTopMap` at radius **`r = 5`**.
- **Tangential Sliding (`±35°`)**: rotates blocked movement vectors up to **`±35°`** along curved cliffs and shorelines.

### 5. Tight-Crop Slices, `min8 - 2` Shell, Gradient Shading, Grass, `1:1` Upscale, Hi-Res Overlay & `particlesByZ`
- **Tight-Crop Bounded Slices & $O(1)$ Skip**: each pre-baked slice `{ canvas, offX, offY, w, h }` in `Uint32Array` crops to its occupied bounding box and skips non-intersecting slices in $O(1)$, interleaving `entityLayer` (`destination-out` + `1px` `#3B2219` silhouette).
- **Anti-Pinhole Shell (`min8 - 2`)**: fills each column across $[\max(Z_{\min}, \min_8 - 2),\, h]$ for zero gaps in 360°.
- **Local Gradient Lighting**:

$$\nabla_x h = h_R - h_L, \qquad \nabla_y h = h_D - h_U, \qquad \text{sunShade} = \operatorname{clamp}\!\left(\operatorname{round}\big((-\nabla_x h - \nabla_y h)\cdot 1.4\big),\, -22,\, 22\right)$$

- **Grass Tufts (`fbm2d > 0.43`)**: `2–3px` blades (`noOutline: true`) animated at **8 FPS**.
- **Integer `1:1` Upscale & Hi-Res Overlay Pass**:

$$\text{pixelScale} = \operatorname{clamp}\!\left(\left\lfloor \frac{\min(W, H)}{260} \right\rfloor,\, 2,\, 4\right), \qquad \text{LOW\_W} = \left\lceil \frac{W}{\text{pixelScale}} \right\rceil, \qquad \text{LOW\_H} = \left\lceil \frac{H}{\text{pixelScale}} \right\rceil$$

- **360° 3D Particle Occlusion (`particlesByZ`)**: particles bucketed by **`Math.round(p.z)`** and drawn inside the slice-by-slice loop immediately after `terrainSlices[z]`.

### 6. 6-Formula Procedural Geological Kit
1. **2-Pass Domain Warping (`warp2d` with `fbm2dFast`)**: $\mathbf{p}' = \mathbf{p} + A \cdot \text{fbm2dFast}\!\big(\mathbf{p}f + A\,\text{fbm2dFast}(\mathbf{p}f_1)\big)$
2. **Smooth Union / Carve (`smax` / `smin`)**: polynomial blend $k$ eliminating harsh creases.
3. **Ridged Multifractal (`ridgedFbm` + `pullRidge`)**: $\sum_i w_i\,(1 - |\text{noise}_i(\mathbf{p})|)^2$
4. **Irregular Rock Strata (`rockTerrace`)**: $\text{step}_{\text{eff}} = \text{step} \cdot (1 + 0.22 \cdot \text{fbm}(\mathbf{p}))$
5. **Bench Trail (`carveBenchTrail`)**: 3D spline carved into mountain slopes with smoothstep shoulders.
6. **Thermal & Hydraulic Erosion (`thermalAndHydraulicErosion`)**: talus angle relaxation + ~260 deterministic water droplets.

### 7. Parabolic Arch Bridges, Organic Lakes, Waterfalls & SDF Ruins
- **Parabolic Arch Bridge (`addArchBridge` / `getBridgeDeckZ`)**: $z_{\text{deck}}(u) = z_{\text{base}} + H_{\text{arch}}(1 - (2u - 1)^2)$ over intact `MAT_WATER`, abutments restricted to **`u <= 0.09 || u >= 0.91`**.
- **Organic Lakes (`warp2d`) & Calm Water vs. Waterfall (`h - min8 > 4`)**: foam streaks strictly where `h - min8 > 4`.
- **Eroded Ruin Blocks (`pullRuinsBlock`)**: $d_{\text{rect}} = \max(|dx|/\text{halfW},\, |dy|/\text{halfD}) + 0.08 \cdot \text{fbm2d}(x, y)$.

### 10. 2.5D Fluid Mechanics (`WindField`, `sampleWaterFlow` + Rankine Dipole, `waterfallSim`, `MAT_SHALLOW` & 2D `WaveBuffer`)
- **Vector Wind Field (`WindField`)**: $\mathbf{W}(x,y,t) = \mathbf{W}_{\text{base}} + \mathbf{W}_{\text{gust}}\sin(\mathbf{k}\cdot\mathbf{p} - \omega t) + A_{\text{turb}}\,\text{fbm}(\mathbf{p}f - \mathbf{v}_w t) + \sum_i \mathbf{I}_i e^{-d^2/r^2}$, modulated by **`altBoost`** and **topographic wind shadow (`∇h · W < 0`)**.
- **River Current (`WaterFlow` / `sampleWaterFlow`), Rankine Dipole & Drain Sink**: analytical potential deflection around obstacles (`getActiveWaterObstacles`), RK2 `flowStreaks` (pool `180`) with 5-point obstacle splitting, and `smoothstep` drain sink (`u -> 0`).
- **Conservative Virtual-Pipe Waterfall (`waterfallSim` `40×26`, `WF_CELL = 4`)**: 4-neighbor hydraulic head fluxes ($H = h + \text{bedZ}$), cliff lateral suppression (`latGain = 0.025`, `latDamp = 0.45`) for dry rock clefts, and `wfBlockH` coupled to `isDamBoulder` (`rebuildWaterfallBlocks()`).
- **Walkable Shallow Water (`MAT_SHALLOW = 8`)**: `standable = 1`, `0.86×` wading drag, directional wake ripples, and splash particles.
- **Local 2D Wave Buffer (`WaveBuffer` `120×80`, 30 Hz)**: discrete wave equation with `!isWetMat` and obstacle $u = 0$ boundaries, upwind semi-Lagrangian advection (Kelvin V-wakes), wind-driven capillary ripples, 6-cell sponge boundary ($\gamma = 0.72$ vs $0.955$), and `|u| < 0.008 -> 0` cutoff.

### 11. Reactive Foliage (`Foliage` / `isFoliage`): Parabolic Bend, Damped Spring & Fluid Coupling
Properties: `isFoliage: true`, `rigidity` (`0..1`), `windScale`, `pushRadius`, `pushStrength`, `leafColors`.
- **Parabolic Cantilever Bend**: $\Delta\mathbf{p}(s_z) = \left(\frac{s_z}{H - 1}\right)^2 \mathbf{b}$
- **Damped Spring + Entity Push**: $\mathbf{a} = k_{\text{stiff}}\big(\mathbf{W}(x,y,t)\cdot \text{windScale}\cdot(1 - \text{rigidity}) - \mathbf{b}\big) + \mathbf{F}_{\text{push}}(\text{entities}) - c_{\text{damp}}\,\mathbf{v}$

### 12. Procedural Destruction (`zCut`, 3D Inverted Pendulum & Fracture)
- **Z-Slice Split (`zCut`)**: fixed base (`0 .. zCut - 1`, becomes `'platform'` collider) + dynamic upper body (`zCut .. count - 1`).
- **`'chop'` (3D Inverted Pendulum)**: $\ddot{\phi} = \frac{3g}{2L}\sin(\phi)$ projected slice-by-slice in the Z loop, with Newton's 3rd Law directional fall, `WaveBuffer` splash, and persistent `wood_log` drops.
- **`'crumble'` (Ruins/Boulders)**: chipped `'platform'` base + `stone_chunk` ballistics (`isDamBoulder` shatters cleanly and calls `rebuildWaterfallBlocks()`).
- **`'trim'` (Low Foliage)**: strong spring oscillation + leaf cloud in `WindField`.
- **Controls (`KeyR` / Click = Action, `KeyQ` & `KeyE` = Rotate, `KeyC` = Spawn)**: `tool_axe` (`2×` on `'chop'`), `tool_pickaxe` (`2×` on `'crumble'`), `tool_hoe` (`2×` on `'trim'`), or `1×` bare-paw default.

### 13. Archimedes Buoyancy, Local Volume Displacement & Wave Coupling
- **Vertical Buoyancy (`debrisDrops`)**: low-density bodies (`wood_log`, $\rho_{\text{rel}} < 1$) oscillate on a spring-damper equilibrium against the live `WaveBuffer` surface $z_{\text{surf}} + 1.4\,u$, while dense bodies (`stone_chunk`, $\rho_{\text{rel}} > 1$) sink to the riverbed `dc.h`.
- **Wave Slope Drift**: floating bodies read $-\nabla u = (-\partial u / \partial x,\, -\partial u / \partial y)$ from `sampleWaveHeightAndGrad(wx, wy)` to drift down wave crests.
- **Local Volume Displacement (`getLocalArchimedesRise`)**: entering/leaving water radiates a $\Delta V_{\text{sub}}$ wave crest/trough into `WaveBuffer`, while submerged bodies within `r <= 64u` at matching water elevation raise the local basin level without affecting disconnected lakes or oceans.

### 14. 2D Thermodynamics, Heat Diffusion & Combustion (`stepThermodynamics` `48×36`, 15 Hz)
- **Heat Diffusion + Wind Advection + Cooling**:
$$\frac{\partial T}{\partial t} = \alpha\,\nabla^2 T - \beta\,(\mathbf{W}\cdot\nabla T) - \lambda\,T$$
- **Moisture Evaporation & Ignition Gate**: while moisture $M > 0.05$, heat evaporates water ($dM/dt = -0.018\,T$) before $T$ can reach $T_{\text{ign}} = 42$. Only dry combustible cells (`fuel > 0.05`) ignite and release heat until `fuel` is exhausted, while `MAT_WATER` / `MAT_SHALLOW` quench $T \to 0$ and emit steam.

### 15. Granular Matter (Angle of Repose) & Incremental Dirty-Rect Re-Bake
- **Talus Avalanche (`relaxGranularBox`)**: granular cells (`MAT_SAND` `talus = 2`, `MAT_PEAK` `talus = 3`) transfer `1` height unit to lower neighbors whenever $\Delta h > \text{talus}$, conserving total mass.
- **Incremental Dirty-Rect Re-Bake (`rebakeTerrainDirtyRect`)**: updates only the affected `[mx0..mx1, my0..my1]` pixels inside `terrainSlices[z]` via `getImageData` / `putImageData`, keeping real-time digging and footprints at ~60 FPS.

### 16. 3D Verlet Cloth, Banners & Ropes (`verletChains`)
- **Position-Based Verlet Integration**:
$$\mathbf{x}_{t+1} = \mathbf{x}_t + (\mathbf{x}_t - \mathbf{x}_{t-1})\,\gamma + \mathbf{a}\,\Delta t^2, \qquad \mathbf{a} = \mathbf{g} + \mathbf{W}(x,y,t)\,k_{\text{wind}} + \mathbf{F}_{\text{cat}}$$
  Solved with 4 Gauss-Seidel distance-constraint iterations per step and rendered inside the Z-slice loop for true 3D occlusion.

---

## 🎮 Live Demos

| Demo | Skill Modules Demonstrated | Link |
|---|---|---|
| **1080×1080 Micro-Voxel Terrain** | *Pull-Chain* engine, Tight-Crop Slices, `sampleWaterFlow` (Rankine Dipole), `waterfallSim`, Archimedes buoyancy, Thermodynamics/Fire, Granular Matter (Dirty-Rect), Verlet Cloth/Ropes, Procedural Trees, `Foliage`, `Destructible`, and Hi-Res Overlay | [examples/terrain-world.html](https://ruishalm.github.io/PixelArtSkill/examples/terrain-world.html) |
| **Multi-Room Diorama** | *Wall Culling*, hollow furniture angular occlusion, `unproject` drag & drop, *Hierarchical Parenting*, and 3-slot persistence | [`index.html` / `examples/room-3d.html`](https://ruishalm.github.io/PixelArtSkill/) |
| **Quadruped Voxel Model** | Base-36 16-slice stacking, 360° orbital rotation, `squash = 0.75`, and single `1px` silhouette | [examples/cat-3d.html](https://ruishalm.github.io/PixelArtSkill/examples/cat-3d.html) |
| **Articulated Voxel Model** | Rigid anti-shearing sub-stacks and 2-phase biomechanical walk cycle (*Swing* / *Stance*) | [examples/chicken-3d.html](https://ruishalm.github.io/PixelArtSkill/examples/chicken-3d.html) |

---

## 🚀 Running Locally

Zero build, zero npm, zero WebGL:

```bash
git clone https://github.com/ruishalm/PixelArtSkill.git
cd PixelArtSkill
python -m http.server 8088
# Open http://localhost:8088/index.html or http://localhost:8088/examples/terrain-world.html
```

To rebuild `examples/terrain-world.html` from `src/terrain-world/` and `assets/voxels/`, and run the verification suite:

```bash
python scripts/generate_terrain_world.py
python tests/test_physics_invariants.py
```

---

## 📂 Repository Structure

```text
PixelArtSkill/
├── .github/workflows/deploy.yml   # GitHub Pages: automated continuous deploy on main
├── .gitignore
├── LICENSE
├── README.md                      # Official documentation, math formulas, and roadmap
├── SKILL.md                       # Antigravity Skill specification (rules, formulas, prompt)
├── index.html                     # Default entry point (GitHub Pages)
├── docs/
│   └── sprite-stacking-prompt-guide.md
├── examples/                      # Self-contained demos generated with the skill
│   ├── terrain-world.html
│   ├── room-3d.html
│   ├── cat-3d.html
│   └── chicken-3d.html
├── scripts/                       # Portable Python generators & bundlers
│   ├── generate_terrain_world.py  # Zero-dependency bundler: src/terrain-world/ → examples/terrain-world.html
│   ├── generate_terrain_props.py  # Procedural CSG voxel prop generator (--seed CLI)
│   ├── generate_mega_room.py
│   ├── generate_kitchen_and_garden_packs.py
│   ├── generate_living_room_pack.py
│   ├── generate_modular_furniture.py
│   ├── generate_full_3d_room.py
│   ├── generate_room.py
│   ├── generate_html.py
│   ├── generate_chicken_html.py
│   └── build_chicken_slices.py
├── src/
│   └── terrain-world/             # Modular JS engine (shell.html + 01..06: geology, fluids, foliage, render)
├── tests/
│   └── test_physics_invariants.py # Automated suite: voxel packs, JS syntax & physics invariants (Python + Node)
└── assets/
    ├── voxels/                    # 13 Base-36 JSON voxel packs (cabin, torii, tools, furniture...)
    └── previews/                  # 15 reference images and validation renders
```

---

## 🗺️ Roadmap — Physics & Material Formulas

Milestone tracker for the **mathematical voxel physics** lab in Pure HTML5 Canvas 2D:

- [x] **Seeded Procedural Generation (`WORLD_SEED` + `--seed`)**: deterministic PRNG (*Mulberry32* in JS + `set_seed(seed)` / `--seed` in `generate_terrain_props.py`), `?seed=<N>` URL parameter, and `🎲 Seed` HUD button varying `fbm2d`, organic contours, river meanders, lakes, mountain ridges, and **unique procedural trees** (curved trunks, woody branches, and asymmetric crowns on `pine_tree` & `sakura_oak`), while `seed=1337` preserves the classic map.
- [x] **Thermodynamics, Fire & Combustion**: 2D heat diffusion equation ($\alpha\nabla^2 T + \beta(\mathbf{W}\cdot\nabla T) - \lambda T$) + moisture ($M$) and finite `fuel` coupled to `WindField` (wind leans embers in `particlesByZ`) and `MAT_WATER` / `MAT_SHALLOW` (water quenches $T$ and emits steam), with `campfire` as an active thermal source.
- [x] **Archimedes Buoyancy & Wave ↔ Rigid-Body Coupling**: `wood_log`, `stone_chunk`, and `floatingItems` reading height $u(x,y)$ and gradient $\nabla u$ from `WaveBuffer` (`sampleWaveHeightAndGrad`) + local basin volume displacement (`getLocalArchimedesRise`): logs float and bob with waves, while stones sink to the bed.
- [ ] **Viscosity & Non-Newtonian Fluids ($\nu \nabla^2 \mathbf{u}$)**: viscous momentum diffusion and slow flow for mud, honey, or lava (temperature-coupled $\nu(T)$ — hotter means lower viscosity).
- [x] **Granular Matter & Incremental Dirty-Rect Re-Bake**: sand (`MAT_SAND`) and snow (`MAT_PEAK`) with dynamic angle-of-repose relaxation (`talus = 2`/`3` in `relaxGranularBox`), impact footprints, and digging (`KeyR` / `tool_hoe`), updating only the dirty rectangle in `terrainSlices[z]` via `rebakeTerrainDirtyRect`.
- [x] **Cloth, Ropes & Hanging Bridges (Verlet Integration)**: 3D node chains (`verletChains` — Village festive garland, Torii ribbons, Lighthouse pennant, and Sakura vine) coupled to `WindField` and `Character` push, rendered per Z-slice with real 3D occlusion.
- [ ] **Chunk Streaming (`Web Worker` + `OffscreenCanvas`)**: optional for continuous open worlds larger than `1080×1080`, keeping only a `3×3` window of pre-baked chunks in RAM at 60 FPS.
- [ ] **Modular Engine (`src/engine/`) & Browser Visual Studio (`studio.html`)**: complete separation of pure engine modules (`math-noise`, `voxel-sheets`, `slice-baker`, `fluids`, `materials`, `renderer`) + a zero-dependency in-browser visual editor (terrain/sand/water brushes, drag-and-drop procedural trees/Verlet/campfires, live physics sliders, and one-click self-contained `.html` export).

---

## 📄 License

Distributed under the **MIT** license. See [`LICENSE`](./LICENSE) for details.
