---
name: team3d
description: Inspect, diagnose, and repair existing Blender assets against references. Use for component identification and reference crops, mesh and assembly audits, scoped scene repairs, matched before-and-after review renders, and export verification.
---

# team3d

## Direct commands

Accept `$team3d <function-command>` followed by the task. When a command is given, execute only its action plus necessary prerequisites. Read the audit guide for relevant details. Treat audit and review commands as inspection-only. Apply scene edits under `scoped-repair` or when explicitly requested. When several commands are requested, perform them in the stated order. Without an explicit command, use the workflow below.

| Function command | Inputs | Action |
| --- | --- | --- |
| `reference-analysis` | Reference images | Identify components, extract evidence crops, and flag uncertain details. |
| `component-mapping` | Existing asset and any reference evidence | Map stable component IDs to existing Blender objects and any available crops. |
| `structural-audit` | Saved Blender scene and component scope or manifest | Run the mesh audit and report findings. Create the manifest if needed. |
| `visual-assembly-audit` | Existing asset and target components or defect | Inspect parts in isolation and in assembly, including relevant existing motion. |
| `scoped-repair` | Existing asset and requested fix | Edit a versioned copy, compare against the baseline, and retest the fix. |
| `review-renders` | Existing scene or before-and-after scenes | Capture inspection views and report findings. Use matched settings when both versions are supplied. |
| `export-verification` | Existing asset or exported file and target format | Export the requested scope if needed and verify it by reimporting. |

## Default workflow

1. Identify the supplied asset, target components, reference views, reported defects, and expected result. Discover local Blender or a connected Blender tool and verify that it can inspect the scene. With images alone, deliver reference analysis and identify which scene checks need an asset.
2. Read [the asset audit guide](references/asset-audit.md). Map reference features and crops to existing scene objects using stable component IDs. Record visible evidence and uncertain areas. Use the crop helper for rectangular evidence crops. Supply a verified, source-aligned mask when a transparent cutout is needed.
3. Baseline the affected parts and nearby dependencies. Run the structural audit on the saved scene when possible. Use its reported frame, layer, and evaluation mode when interpreting findings. Inspect parts in isolation and in assembly using matched neutral views. Check relevant fit, clearance, shading, material, pivot, or pose behavior. Record a reproducible finding for each defect.
4. When a repair is requested, edit a versioned copy. Limit changes to the implicated objects or dependencies and compare unaffected components with the baseline. For assembly problems, verify the corrected relationship at rest and through relevant poses. Repeat the failed checks and capture matched before-and-after evidence.
5. When requested, export the repaired asset or named components and reimport into a clean scene. Verify the properties the target format should carry. Deliver the findings, repair evidence and revised scene if applicable, plus any requested verified exports. Mark unchecked and tool-blocked items explicitly.
