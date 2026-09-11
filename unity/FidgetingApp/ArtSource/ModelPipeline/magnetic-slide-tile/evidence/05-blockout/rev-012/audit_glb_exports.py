import json
import struct
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise RuntimeError(f"Invalid GLB header: {path}")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise RuntimeError(f"Missing JSON chunk: {path}")
    return json.loads(data[20:20 + chunk_length].decode("utf-8"))


product = load_glb(HERE / "magnetic-slide-tile-fixed-axis-product-r012.glb")
technical = load_glb(HERE / "magnetic-slide-tile-fixed-axis-technical-r012.glb")
product_mesh_nodes = sorted(node["name"] for node in product["nodes"] if "mesh" in node)
technical_mesh_nodes = sorted(node["name"] for node in technical["nodes"] if "mesh" in node)
product_pivots = [
    node["name"] for node in product["nodes"]
    if node.get("extras", {}).get("pivot_id")
]
checks = {
    "productHasTwoMeshes": product_mesh_nodes == ["BottomExterior", "MovingTopBody"],
    "technicalHasNineMeshes": len(technical_mesh_nodes) == 9,
    "exactlyOnePivotNode": product_pivots == ["FixedAxis"],
    "minimumDiskHasNoMesh": all("mesh" not in node for node in product["nodes"] if node.get("name") == "MinimumOverlapDisk"),
    "noAnimations": not product.get("animations") and not technical.get("animations"),
}
report = {
    "schemaVersion": 1,
    "product": {"nodes": len(product["nodes"]), "meshes": len(product["meshes"]), "meshNodes": product_mesh_nodes},
    "technical": {"nodes": len(technical["nodes"]), "meshes": len(technical["meshes"]), "meshNodes": technical_mesh_nodes},
    "pivotNodes": product_pivots,
    "checks": checks,
    "pass": all(checks.values()),
}
(HERE / "glb-export-audit.json").write_text(json.dumps(report, indent=2))
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))

