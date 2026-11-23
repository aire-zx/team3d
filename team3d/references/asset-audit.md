# Asset audit guide

## Image extraction and part brief

- Use the image coordinate system after EXIF orientation correction. Record one rectangle per useful view, from upper-left as `[left, top, right, bottom]` in pixels, with right and bottom exclusive. Treat a rectangular crop as visual evidence. Add a validated pixel mask and transparent cutout only when the boundary is traceable. For multi-view images, tie each view to the same component ID and note conflicts.
- Keep backgrounds, glints, shadows, printed graphics, and occluding objects distinct from geometry. Record whether a detail is modeled geometry or comes from a texture, normal map, or material.
- Record visible shape, proportions or dimension bounds, materials, surface details, side, symmetry, attachments, evidence quality, and inferred areas. Use the subject's left and right. Do not assume mirrored details without checking.
- Give each component a unique ID matching `[a-z0-9][a-z0-9_-]*`. Use this JSON shape. Paths for sources are relative to the manifest. The audit expects uniquely assigned `objects` and checks against exact Blender object names. Record purely textural details within their host component.

```json
{
  "components": [
    {
      "id": "housing",
      "objects": ["Housing"],
      "surface": "closed",
      "crops": [{"source": "front.png", "box": [20, 10, 180, 210]}],
      "evidence": "Front silhouette visible. Back depth inferred.",
      "parent": null
    }
  ]
}
```

Use `surface: "open"` for intentionally open surfaces. Omit the field where closure is unknown. Both helpers validate the lowercase surface values. List all mesh object names required for each component. A hidden-but-required component still needs an ID and a brief, with empty crops and the reason for including it.

```bash
python3 scripts/extract_crops.py manifest.json ./crops
blender --background asset.blend --python-exit-code 1 --python scripts/audit_scene.py -- manifest.json audit.json
```

The optional crop field `mask` is a manifest-relative path to a verified binary or 8-bit grayscale image. After each image's EXIF orientation is applied, the mask must match the full source dimensions and alignment. White retains opacity, black clears it, and intermediate values multiply the source alpha.

Use a fresh directory for the first extraction, including after upgrading from an untracked crop set. Subsequent runs use the same directory and its hidden ownership index. The helper stages all crops before publishing, removes obsolete tracked files, and preserves unrelated files.

## Diagnosis and scoped repair

- Record source file, component IDs, object assignments, expected behavior, and the reproducible view or frame for each reported defect. Keep a baseline snapshot with relevant geometry counts, transforms, parents, material assignments, and pose before editing.
- Inspect isolated parts and assembled views. Check visibility, silhouette, landmarks, surface shading, and texture presence. Measure joint fit, offsets, gaps, or unintended intersections where possible. Check pivots and representative motion poses when animation already exists and affects the issue.
- Save repairs to a distinct editable scene. Compare unrelated object properties against the baseline and inspect adjacent parts for regressions. Capture before-and-after evidence under the same camera, lighting, and pose.
- For requested exports, reimport in a clean scene or the target application. Verify mesh scope, transforms, pivots, hierarchy, materials, and playback as applicable. Record any differences allowed by the format.

## Review and handoff

- Inspect silhouette, landmarks, proportions, color and materials, visible seams, and absence of unintended gaps, overlaps, or missing surfaces. Check camera clipping and visibility with the review renders. Verify the outliner, pivots, scale, texture portability, and any rig or animation requirements.
- Structural audit checks original scene membership, object render hiding and collection visibility in the recorded view layer, evaluated mesh geometry, world-space zero-area faces, wire edges, edges shared by more than two faces, boundaries on closed components, and world-space bounds. It does not measure likeness, normals direction, self-intersection, or ground contact. Inspect those where relevant. Read the frame, subframe, view layer, and dependency-graph mode in the JSON report. Collection exclusions apply to the audited layer. Geometry unavailable in that graph is reported as unchecked. If viewport and render modifier settings differ, inspect the render result before accepting a render-specific fix.
- Record per issue the component, severity, view or measurement, fix, and retest. Use pass, pass with caveats, or needs revision. Treat a required missing component, unreadable export, or major visual discrepancy as needs revision. Preserve limitations from single-view inference even when the asset passes.
