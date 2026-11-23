# team3d

`$team3d` audits and repairs existing Blender assets against visual references and verifies the results at component and assembly level.

> Use $team3d to audit this Blender asset against the attached references. Inspect the latch and housing in isolation and in assembly, fix the reported clipping in a separate editable scene, and verify the requested GLB after reimport.

## Install in a Codex project

Copy the entire [team3d](team3d) folder from this repository into `.agents/skills/` in your project. The resulting path should be `.agents/skills/team3d/SKILL.md`. Open Codex in that project and invoke `$team3d`.

For a quick structural audit, give Codex an existing `.blend` file and ask it to check the required meshes. For an image-only test, attach a reference and invoke `$team3d reference-analysis`.

For reference crops, install Pillow in the Python environment that will run the crop helper with `python -m pip install Pillow`. Scene work needs an accessible Blender scene and either a local Blender executable or a compatible connector. The command-line structural audit runs inside Blender.

## Direct commands

Type `$team3d <function-command>` followed by the asset, scope, and any constraints. For example, `$team3d structural-audit Check the latch and housing in the attached .blend.`

| Function command | Inputs | Action |
| --- | --- | --- |
| `reference-analysis` | Reference images | Identify components, extract evidence crops, and flag uncertain details. |
| `component-mapping` | Existing asset and any reference evidence | Map stable component IDs to existing Blender objects and any available crops. |
| `structural-audit` | Saved Blender scene and component scope or manifest | Run the mesh audit and report findings. Create the manifest if needed. |
| `visual-assembly-audit` | Existing asset and target components or defect | Inspect parts in isolation and in assembly, including relevant existing motion. |
| `scoped-repair` | Existing asset and requested fix | Edit a versioned copy, compare against the baseline, and retest the fix. |
| `review-renders` | Existing scene or before-and-after scenes | Capture inspection views and report findings. Use matched settings when both versions are supplied. |
| `export-verification` | Existing asset or exported file and target format | Export the requested scope if needed and verify it by reimporting. |

## Run the helpers directly

From the repository root, prepare `manifest.json` using the example in the [asset audit guide](team3d/references/asset-audit.md). For crops, supply the reference image and a pixel rectangle for each view. For a mesh audit, list the exact Blender object names. The two helpers can run independently.

```shell
python team3d/scripts/extract_crops.py manifest.json crops
blender --background asset.blend --python-exit-code 1 --python team3d/scripts/audit_scene.py -- manifest.json audit.json
```

The crop helper writes files such as `crops/housing-01.png`. Start with a fresh output directory and reuse it for later runs. To create a transparent cutout, supply a verified mask aligned to the source image. Creating a new 3D mesh from that cutout requires a separate modeling step.

The Blender helper writes mesh measurements, findings, and a status to `audit.json`. A status of `needs_review` means at least one finding needs inspection. A status of `passed_structural_checks` applies to the listed meshes at the recorded frame, view layer, and evaluation mode. Check the JSON status even if Blender exits successfully. Visual likeness, clearance, and motion require separate inspection in Blender.

For a repair, ask Codex to save a versioned editable scene and capture comparable before-and-after views. For a delivery-format check, request an export and clean reimport, specifying the parts and properties that must survive.

## Skill structure

- [SKILL.md](team3d/SKILL.md) defines the audit and repair workflow.
- [agents/openai.yaml](team3d/agents/openai.yaml) provides invocation metadata.
- [references/asset-audit.md](team3d/references/asset-audit.md) defines component manifests, diagnosis, repair, and acceptance checks.
- [scripts/extract_crops.py](team3d/scripts/extract_crops.py) uses Python and Pillow to export reference crops.
- [scripts/audit_scene.py](team3d/scripts/audit_scene.py) runs inside Blender and reports structural findings as JSON.
- [scripts/team3d_manifest.py](team3d/scripts/team3d_manifest.py) validates the shared component IDs, mesh assignments, and surface types.
- [assets/icon.svg](team3d/assets/icon.svg) supplies the skill icon referenced by the interface metadata.
