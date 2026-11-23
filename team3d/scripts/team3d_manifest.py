"""Common component manifest rules for the image and Blender helpers."""
import json
import re


def load_components(path, *, require_objects=False):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    components = data.get("components") if isinstance(data, dict) else None
    if not isinstance(components, list) or not components:
        raise ValueError("Expected a nonempty components array.")
    ids = set()
    assigned = set()
    for component in components:
        identifier = component.get("id") if isinstance(component, dict) else None
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", identifier):
            raise ValueError(f"Invalid component ID {identifier!r}. Use a lowercase file stem.")
        if identifier in ids:
            raise ValueError(f"Duplicate component ID {identifier!r}.")
        ids.add(identifier)
        if "surface" in component and component["surface"] not in ("open", "closed"):
            raise ValueError(f"{identifier}: surface must be open or closed when supplied.")
        if require_objects or "objects" in component:
            names = component.get("objects")
            if not isinstance(names, list) or any(not isinstance(n, str) or not n.strip() for n in names):
                raise ValueError(f"{identifier}: objects must be an array of mesh names.")
            for name in names:
                if name in assigned:
                    raise ValueError(f"{identifier}: mesh {name!r} is assigned more than once.")
                assigned.add(name)
    return components
