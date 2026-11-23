"""Inspect the loaded Blender scene against a component manifest."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import bpy

# Blender runs --python files outside the normal script import path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from team3d_manifest import load_components


def inspect_mesh(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        face_edges = Counter(key for face in mesh.polygons for key in face.edge_keys)
        edge_uses = [face_edges[tuple(sorted(edge.vertices))] for edge in mesh.edges]
        positions = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        bounds = None
        if positions:
            bounds = {
                "min": [min(point[axis] for point in positions) for axis in range(3)],
                "max": [max(point[axis] for point in positions) for axis in range(3)],
            }
        # Transform edge vectors without translation so a large world offset
        # cannot cancel small edges. Blender supplies the ngon triangulation.
        linear = evaluated.matrix_world.to_3x3()
        mesh.calc_loop_triangles()
        nonzero_faces = set()
        for triangle in mesh.loop_triangles:
            a, b, c = (mesh.vertices[i].co for i in triangle.vertices)
            normal = (linear @ (b - a)).cross(linear @ (c - a))
            if any(normal):
                nonzero_faces.add(triangle.polygon_index)
        return {
            "vertices": len(mesh.vertices),
            "faces": len(mesh.polygons),
            "world_bounds": bounds,
            "zero_area_faces": len(mesh.polygons) - len(nonzero_faces),
            "wire_edges": edge_uses.count(0),
            "boundary_edges": edge_uses.count(1),
            "overused_edges": sum(uses > 2 for uses in edge_uses),
        }
    finally:
        evaluated.to_mesh_clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    try:
        components = load_components(args.manifest, require_objects=True)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    visible_collections = set()

    def collect(layer):
        if layer.exclude or layer.collection.hide_render:
            return
        visible_collections.add(layer.collection)
        for child in layer.children:
            collect(child)

    collect(bpy.context.view_layer.layer_collection)
    report = {
        "scene": scene.name, "view_layer": bpy.context.view_layer.name,
        "frame": scene.frame_current, "subframe": scene.frame_subframe,
        "depsgraph_mode": depsgraph.mode, "objects": [], "findings": [],
    }
    for component in components:
        if not component["objects"]:
            report["findings"].append({"component": component["id"], "issues": ["no_mesh_assigned"]})
        for name in component["objects"]:
            obj = scene.objects.get(name)
            issues = []
            if obj is None or obj.type != "MESH":
                issues.append("missing_mesh")
            else:
                if obj.hide_render:
                    issues.append("hidden_from_render")
                elif not visible_collections.intersection(obj.users_collection):
                    issues.append("hidden_in_audited_render_layer")
                if depsgraph.objects.get(name) is None:
                    issues.append("geometry_unavailable_in_audited_layer")
                    report["findings"].append({"component": component["id"], "object": name, "issues": issues})
                    continue
                stats = inspect_mesh(obj, depsgraph)
                report["objects"].append({"component": component["id"], "object": name, **stats})
                if not stats["faces"]:
                    issues.append("no_faces")
                issues.extend(key for key in ("zero_area_faces", "wire_edges", "overused_edges") if stats[key])
                if component.get("surface") == "closed" and stats["boundary_edges"]:
                    issues.append("unexpected_open_boundary")
            if issues:
                report["findings"].append({"component": component["id"], "object": name, "issues": issues})
    report["status"] = "needs_review" if report["findings"] else "passed_structural_checks"
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
