import fs from "node:fs";
import * as THREE from "../../../../../../../../tools/model-provenance-explorer/node_modules/three/build/three.module.js";
import { GLTFExporter } from "../../../../../../../../tools/model-provenance-explorer/node_modules/three/examples/jsm/exporters/GLTFExporter.js";

globalThis.FileReader = class FileReader {
  readAsArrayBuffer(blob) { blob.arrayBuffer().then((value) => { this.result = value; this.onloadend?.(); }); }
  readAsDataURL(blob) { blob.arrayBuffer().then((value) => { this.result = `data:${blob.type};base64,${Buffer.from(value).toString("base64")}`; this.onloadend?.(); }); }
};

const scene = new THREE.Scene();
scene.name = "HHAX_Gate02_InteractiveCAD";
const metal = new THREE.MeshStandardMaterial({ color: 0x272231, metalness: 0.9, roughness: 0.24 });
const moving = new THREE.MeshStandardMaterial({ color: 0x7d718b, metalness: 0.72, roughness: 0.3 });
const track = new THREE.MeshStandardMaterial({ color: 0xd09a54, metalness: 0.85, roughness: 0.25 });
const bead = new THREE.MeshStandardMaterial({ color: 0xd9dde4, metalness: 1, roughness: 0.12 });
const unknown = new THREE.MeshStandardMaterial({ color: 0x8b607f, metalness: 0.25, roughness: 0.45, transparent: true, opacity: 0.48 });

function capsuleShape(width, length) {
  const r = width / 2;
  const straight = Math.max(0, length / 2 - r);
  const shape = new THREE.Shape();
  shape.moveTo(-r, -straight);
  shape.absarc(0, -straight, r, Math.PI, Math.PI * 2, false);
  shape.lineTo(r, straight);
  shape.absarc(0, straight, r, 0, Math.PI, false);
  shape.closePath();
  return shape;
}
function capsule(name, width, length, depth, material, position) {
  const geometry = new THREE.ExtrudeGeometry(capsuleShape(width, length), { depth, bevelEnabled: true, bevelSegments: 3, bevelSize: 0.55, bevelThickness: 0.45, curveSegments: 32 });
  geometry.translate(0, 0, -depth / 2);
  const mesh = new THREE.Mesh(geometry, material); mesh.name = name; mesh.position.set(...position); scene.add(mesh); return mesh;
}
capsule("FixedLowerShell", 30.9, 50.5, 6.7, metal, [-28, 0, 0]);
capsule("MovingUpperShell_OpenPose", 30.9, 50.5, 6.6, moving, [28, 17.8, 7.0]);
const railGeometry = new THREE.BoxGeometry(2.0, 31.0, 1.5);
for (const x of [-35.8, -20.2]) { const rail = new THREE.Mesh(railGeometry, track); rail.name = "VisibleStraightTrack"; rail.position.set(x, 1.5, 4.2); scene.add(rail); }
const ring = new THREE.Mesh(new THREE.TorusGeometry(10.7, 1.35, 12, 64), track); ring.name = "VisibleRotaryTrack"; ring.position.set(-28, 1.8, 4.4); scene.add(ring);
const axle = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 2.4, 3, 32), bead); axle.rotation.x = Math.PI / 2; axle.position.set(-28, 1.8, 4.4); axle.name = "CentralAdjustmentRegion"; scene.add(axle);
for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; const m = new THREE.Mesh(new THREE.SphereGeometry(1.05, 16, 12), bead); m.name = `RepresentativeBead_${i + 1}`; m.position.set(-28 + Math.cos(a) * 10.7, 1.8 + Math.sin(a) * 10.7, 4.4); scene.add(m); }
const envelope = capsule("UnknownHiddenLinkageEnvelope", 16.5, 27.0, 1.1, unknown, [-28, 1.8, 5.1]);
envelope.userData = { evidenceStatus: "provisional-reversible-digital-reconstruction", physicalOrManufacturingClaim: false };
scene.userData = {
  units: "millimeters",
  publishedEnvelopeMm: [50.5, 30.9, 13.6],
  classificationCompatibilityId: "linear-magnetic-slider",
  trueDrive: "mechanical-straight-push-and-rotation-linkage",
  magnetRole: "replaceable-patch-only",
  hiddenGeometryStatus: "unknown; translucent envelope is not a physical claim"
};
const exporter = new GLTFExporter();
const result = await new Promise((resolve, reject) => exporter.parse(scene, resolve, reject, { binary: true, onlyVisible: true }));
fs.writeFileSync(new URL("./interactive-cad.glb", import.meta.url), Buffer.from(result));
