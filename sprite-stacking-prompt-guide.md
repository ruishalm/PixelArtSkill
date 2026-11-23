# Sprite Stacking 3D Pixel Art Engine Guide
*Based on @nazim.builds (Pixel Stack / Stack Farm)*

## Core Technique
Sprite stacking achieves a 3D isometric/rotatable pixel art appearance strictly using flat 2D layers rendered on an HTML5 2D Canvas—**no WebGL, Three.js, or 3D engine required**.

### 1. Slice Sheets & Voxel Grids
- Objects are defined conceptually or programmatically as 3D voxel grids (e.g., 16x16x16 to 48x48x40 of palette indices, 0 = empty).
- The voxel grid is sliced horizontally along the Z axis (bottom-to-top).
- Each Z layer becomes an equal-sized 2D sprite slice.
- Slices are laid out in a single horizontal strip (slice sheet), from slice 0 (ground) to slice N-1 (top).

### 2. Rendering Formula (drawStack)
```typescript
function drawStack(
  ctx: CanvasRenderingContext2D,
  sheet: CanvasImageSource,
  count: number,
  pos: { x: number; y: number },
  turn: number,        // rotation in radians
  squash: number = 0.75, // camera tilt (1.0 = top-down, ~0.6 min)
  spacing: number = 1    // layer height spacing in pixels
) {
  const w = (sheet.width as number) / count;
  const h = sheet.height as number;
  const rect = [-Math.floor(w / 2), -Math.floor(h / 2), w, h];

  for (let z = 0; z < count; z++) {
    ctx.save();
    // 1. Position on canvas (integer rounded!)
    ctx.translate(Math.round(pos.x), Math.round(pos.y - Math.round(z * spacing)));
    // 2. Camera squash (vertical compression)
    ctx.scale(1, squash);
    // 3. Rotate every slice around its center before lifting
    ctx.rotate(turn);
    // 4. Draw slice with nearest-neighbor
    ctx.drawImage(sheet, z * w, 0, w, h, rect[0], rect[1], rect[2], rect[3]);
    ctx.restore();
  }
}
```

### 3. Crucial Rules for Crisp, Non-Shimmering Pixel Art
1. **Disable Image Smoothing**: `ctx.imageSmoothingEnabled = false` on every canvas and buffer.
2. **Low-Res Buffer + Integer Upscaling**:
   - Render the entire scene into an offscreen low-resolution canvas (e.g., 270x480 for 9:16 portrait or 320x180 / 480x270 for landscape).
   - Upscale onto the main viewport canvas by an exact integer factor (2x, 3x, 4x) using `imageSmoothingEnabled = false`.
   - Snap all coordinates (`Math.round`) within the low-res buffer to prevent subpixel jitter/blur.
3. **Whole-Object Silhouettes (Single Outline)**:
   - **Never** outline individual slices! (Outlining individual slices creates horizontal striped artifacts).
   - Render the full stacked object to an offscreen canvas.
   - Dilate the alpha mask by 1px (or draw 1px in 4/8 cardinal directions).
   - Fill the dilated silhouette with a dark outline color (e.g., `#3B2A20`, warm dark brown).
   - Draw the original stack on top.
4. **Depth Sorting (Z-Order)**:
   - Never interleave slices of different objects.
   - Sort entire objects by their screen ground contact point `pos.y` from back to front.
   - Tie-break equal Y positions by X, then by a stable ID.
5. **Baked Shading & Flat Palettes**:
   - Limit colors to 4-6 shades per material: Top (Highlight), Mid (Light-facing), Dark (Shadow-facing).
   - No smooth gradients or soft edges inside slices.
6. **Kinematics / Moving Entities**:
   - Moving objects turn to face direction of travel:
     `turn = Math.atan2(velocity.y, velocity.x) - Math.PI / 2 + cameraTurn`
   - Smooth heading transitions with slight angular interpolation (lerp).
