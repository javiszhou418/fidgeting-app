import * as THREE from './vendor/three.module.js';

window.__MODEL_BOOT__ = 'module-loaded';

const VIEW = new URLSearchParams(window.location.search).get('view') || 'exploded';
const VIEW_META = {
  exploded: { label: 'AXIAL EXPLODED · +Z', axis: 'X → length · Y → depth · Z ↑ stack' },
  top: { label: 'TOP · +Z ORTHO', axis: 'X → right · Y ↑ back · camera +Z' },
  front: { label: 'FRONT LONG SIDE · −Y', axis: 'X → right · Z ↑ · camera −Y' },
  back: { label: 'BACK / UNDERSIDE · −Z', axis: 'X ← mirrored · Y ↑ · camera −Z' },
  left: { label: 'LEFT SHORT END · −X', axis: 'Y → right · Z ↑ · camera −X' },
  right: { label: 'RIGHT SHORT END · +X', axis: 'Y ← mirrored · Z ↑ · camera +X' },
};

if (!VIEW_META[VIEW]) throw new Error(`Unknown view: ${VIEW}`);
document.querySelector('#view-badge').textContent = VIEW_META[VIEW].label;
document.querySelector('#axis-note').textContent = VIEW_META[VIEW].axis;
document.querySelector('#layer-legend').classList.toggle('visible', VIEW === 'exploded');

const stage = document.querySelector('#stage');
const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
window.__MODEL_BOOT__ = 'renderer-created';
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(stage.clientWidth, stage.clientHeight, false);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.96;
stage.appendChild(renderer.domElement);

const materials = {
  titanium: new THREE.MeshPhysicalMaterial({
    color: 0xaab1b4, metalness: 0.96, roughness: 0.27,
    clearcoat: 0.18, clearcoatRoughness: 0.20,
  }),
  titaniumDark: new THREE.MeshPhysicalMaterial({
    color: 0x657078, metalness: 0.92, roughness: 0.31,
    clearcoat: 0.08, clearcoatRoughness: 0.30,
  }),
  titaniumEdge: new THREE.LineBasicMaterial({ color: 0xe8edef, transparent: true, opacity: 0.42 }),
  pom: new THREE.MeshPhysicalMaterial({
    color: 0x0c1013, metalness: 0.03, roughness: 0.40,
    clearcoat: 0.20, clearcoatRoughness: 0.32,
  }),
  pomEdge: new THREE.LineBasicMaterial({ color: 0x34434b, transparent: true, opacity: 0.72 }),
  gunmetal: new THREE.MeshPhysicalMaterial({
    color: 0x29343b, metalness: 0.88, roughness: 0.25,
    clearcoat: 0.15, clearcoatRoughness: 0.20,
  }),
  gunmetalEdge: new THREE.LineBasicMaterial({ color: 0x7c929d, transparent: true, opacity: 0.45 }),
  magnet: new THREE.MeshPhysicalMaterial({
    color: 0xd0d2cf, metalness: 1.0, roughness: 0.13,
    clearcoat: 0.35, clearcoatRoughness: 0.12,
  }),
  magnetEdge: new THREE.LineBasicMaterial({ color: 0xf3f5f3, transparent: true, opacity: 0.58 }),
  recess: new THREE.MeshPhysicalMaterial({
    color: 0x070b0e, metalness: 0.18, roughness: 0.52,
  }),
};

function makeStudioEnvironment() {
  const faces = [0xffffff, 0x6b767c, 0xdbe5e9, 0x30383d, 0xbec8cd, 0x566269].map((color, index) => {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 96;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createLinearGradient(index % 2 ? 96 : 0, 0, index % 2 ? 0 : 96, 96);
    grad.addColorStop(0, `#${color.toString(16).padStart(6, '0')}`);
    grad.addColorStop(0.46, '#d7dde0');
    grad.addColorStop(1, '#242c31');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 96, 96);
    return canvas;
  });
  const cube = new THREE.CubeTexture(faces);
  cube.colorSpace = THREE.SRGBColorSpace;
  cube.needsUpdate = true;
  return cube;
}
scene.environment = makeStudioEnvironment();

scene.add(new THREE.HemisphereLight(0xddebf1, 0x10161a, 1.35));
const key = new THREE.DirectionalLight(0xffffff, 4.25);
key.position.set(-8, -11, 17);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = key.shadow.camera.bottom = -15;
key.shadow.camera.right = key.shadow.camera.top = 15;
key.shadow.bias = -0.00035;
scene.add(key);
const coolFill = new THREE.DirectionalLight(0x8edaff, 1.55);
coolFill.position.set(-10, 8, 7);
scene.add(coolFill);
const warmRim = new THREE.DirectionalLight(0xff8a42, 2.1);
warmRim.position.set(12, 8, 5);
scene.add(warmRim);

const MODEL_W = 12.0;
const MODEL_D = 6.0;
const CORNER_R = 1.18;
// One source of truth for L2 holes, L3 holes, L5 magnets and L6 recesses.
// Six equal 1.64-unit pitches keep the two outer discs fully inside the L1 window.
const MAGNET_X = [-4.10, -2.46, -0.82, 0.82, 2.46, 4.10];
const EXPLODE_STEP = VIEW === 'exploded' ? 3.00 : 0;
const ASSEMBLY_GAP = 0.042;

const layerSpecs = [
  { id: 'L1', label: 'TOP_OPENWORK_FRAME', thickness: 0.34 },
  { id: 'L2', label: 'UPPER_SIX_HOLE_CARRIER', thickness: 0.44 },
  { id: 'L3', label: 'BLACK_SIX_HOLE_SPACER', thickness: 0.22 },
  { id: 'L4', label: 'RAIL_SPRING_CAGE', thickness: 0.28 },
  { id: 'L5', label: 'MAGNETS', thickness: 0.34 },
  { id: 'L6', label: 'LOWER_SIX_RECESS_CARRIER', thickness: 0.44 },
  { id: 'L7', label: 'BACK_SHELL', thickness: 0.50 },
];

let cursor = -layerSpecs.reduce((sum, item) => sum + item.thickness, 0) / 2 - ASSEMBLY_GAP * 3;
for (let index = layerSpecs.length - 1; index >= 0; index -= 1) {
  const spec = layerSpecs[index];
  spec.assembledZ = cursor + spec.thickness / 2;
  cursor += spec.thickness + ASSEMBLY_GAP;
}

function roundedRectShape(width, depth, radius) {
  const x = -width / 2;
  const y = -depth / 2;
  const shape = new THREE.Shape();
  shape.moveTo(x + radius, y);
  shape.lineTo(x + width - radius, y);
  shape.quadraticCurveTo(x + width, y, x + width, y + radius);
  shape.lineTo(x + width, y + depth - radius);
  shape.quadraticCurveTo(x + width, y + depth, x + width - radius, y + depth);
  shape.lineTo(x + radius, y + depth);
  shape.quadraticCurveTo(x, y + depth, x, y + depth - radius);
  shape.lineTo(x, y + radius);
  shape.quadraticCurveTo(x, y, x + radius, y);
  return shape;
}

function roundedRectHole(width, depth, radius, centerX = 0, centerY = 0) {
  const left = centerX - width / 2;
  const right = centerX + width / 2;
  const bottom = centerY - depth / 2;
  const top = centerY + depth / 2;
  const path = new THREE.Path();
  path.moveTo(left, bottom + radius);
  path.lineTo(left, top - radius);
  path.quadraticCurveTo(left, top, left + radius, top);
  path.lineTo(right - radius, top);
  path.quadraticCurveTo(right, top, right, top - radius);
  path.lineTo(right, bottom + radius);
  path.quadraticCurveTo(right, bottom, right - radius, bottom);
  path.lineTo(left + radius, bottom);
  path.quadraticCurveTo(left, bottom, left, bottom + radius);
  return path;
}

function addCircleHole(shape, x, y, radius) {
  const hole = new THREE.Path();
  hole.absarc(x, y, radius, 0, Math.PI * 2, true);
  shape.holes.push(hole);
}

function addSixCircleHoles(shape, radius) {
  MAGNET_X.forEach((x) => addCircleHole(shape, x, 0, radius));
}

function addFourCornerHoles(shape, radius, x = 5.06, y = 2.08) {
  [[-x,-y],[-x,y],[x,-y],[x,y]].forEach(([px,py]) => addCircleHole(shape, px, py, radius));
}

function extrudeShape(shape, thickness, bevel = 0.065) {
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: thickness,
    curveSegments: 32,
    steps: 1,
    bevelEnabled: bevel > 0,
    bevelSegments: 3,
    bevelSize: bevel,
    bevelThickness: Math.min(bevel, thickness * 0.22),
  });
  geometry.translate(0, 0, -thickness / 2);
  geometry.computeVertexNormals();
  return geometry;
}

function addOutlinedMesh(group, geometry, material, edgeMaterial, name) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = name;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry, 28), edgeMaterial);
  edges.name = `${name}_EDGES`;
  group.add(edges);
  mesh.userData.edgeObject = edges;
  return mesh;
}

function positionOutlined(mesh, x, y, z = 0) {
  mesh.position.set(x, y, z);
  mesh.userData.edgeObject.position.copy(mesh.position);
}

function makeCapsule(group, x1, y1, x2, y2, width, thickness, material, edgeMaterial, name, z = 0) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.hypot(dx, dy);
  const bar = new THREE.Group();
  bar.position.set((x1 + x2) / 2, (y1 + y2) / 2, z);
  bar.rotation.z = Math.atan2(dy, dx);
  group.add(bar);
  addOutlinedMesh(bar, extrudeShape(roundedRectShape(length, width, width / 2), thickness, 0.045), material, edgeMaterial, name);
  return bar;
}

function makeTube(group, points, radius, material, edgeMaterial, name) {
  const curve = new THREE.CatmullRomCurve3(points.map(([x,y,z = 0]) => new THREE.Vector3(x,y,z)), false, 'centripetal', 0.35);
  const geometry = new THREE.TubeGeometry(curve, 64, radius, 12, false);
  return addOutlinedMesh(group, geometry, material, edgeMaterial, name);
}

const model = new THREE.Group();
model.name = 'PUSHCARD_CANONICAL_MODEL';
scene.add(model);
const layerGroups = [];

for (let index = 0; index < layerSpecs.length; index += 1) {
  const spec = layerSpecs[index];
  const group = new THREE.Group();
  group.name = `${spec.id}_${spec.label}`;
  group.userData.layerId = spec.id;
  group.position.z = spec.assembledZ + (3 - index) * EXPLODE_STEP;
  // L5 is dropped slightly closer to L6 in the exploded presentation. This remains
  // a pure Z-axis transform and clears the tall L4 skirt without faking lateral offsets.
  if (VIEW === 'exploded' && spec.id === 'L5') group.position.z -= 1.10;
  model.add(group);
  layerGroups.push(group);

  if (spec.id === 'L1') {
    const frame = roundedRectShape(MODEL_W, MODEL_D, CORNER_R);
    frame.holes.push(roundedRectHole(10.10, 3.70, 0.62));
    addFourCornerHoles(frame, 0.20, 5.05, 2.28);
    addOutlinedMesh(group, extrudeShape(frame, spec.thickness, 0.075), materials.titanium, materials.titaniumEdge, 'L1_CONTINUOUS_FOUR_HOLE_FRAME');
    // Two connected Z/S rib pairs keep a clear center corridor over M1–M6.
    makeCapsule(group, -4.52, 1.28, 4.48, 1.28, 0.30, spec.thickness, materials.titanium, materials.titaniumEdge, 'L1_UPPER_LONG_RIB');
    makeCapsule(group, 4.48, 1.28, 0.78, 0.66, 0.30, spec.thickness, materials.titanium, materials.titaniumEdge, 'L1_UPPER_DIAGONAL_RIB');
    makeCapsule(group, -4.48,-1.28, 4.52,-1.28, 0.30, spec.thickness, materials.titanium, materials.titaniumEdge, 'L1_LOWER_LONG_RIB');
    makeCapsule(group, -4.48,-1.28,-0.78,-0.66, 0.30, spec.thickness, materials.titanium, materials.titaniumEdge, 'L1_LOWER_DIAGONAL_RIB');
  } else if (spec.id === 'L2') {
    const carrier = roundedRectShape(MODEL_W - 0.34, MODEL_D - 0.34, CORNER_R - 0.10);
    addSixCircleHoles(carrier, 0.51);
    carrier.holes.push(roundedRectHole(9.25, 0.48, 0.22, 0, 1.67));
    carrier.holes.push(roundedRectHole(9.25, 0.48, 0.22, 0,-1.67));
    addFourCornerHoles(carrier, 0.13, 5.0, 2.03);
    addOutlinedMesh(group, extrudeShape(carrier, spec.thickness, 0.07), materials.titaniumDark, materials.titaniumEdge, 'L2_UPPER_SIX_HOLE_CARRIER');
  } else if (spec.id === 'L3') {
    const spacer = roundedRectShape(MODEL_W - 0.70, MODEL_D - 0.70, CORNER_R - 0.24);
    addSixCircleHoles(spacer, 0.53);
    spacer.holes.push(roundedRectHole(8.95, 0.42, 0.19, 0, 1.52));
    spacer.holes.push(roundedRectHole(8.95, 0.42, 0.19, 0,-1.52));
    addFourCornerHoles(spacer, 0.105, 4.86, 1.91);
    addOutlinedMesh(group, extrudeShape(spacer, spec.thickness, 0.045), materials.pom, materials.pomEdge, 'L3_BLACK_SIX_HOLE_SPACER');
  } else if (spec.id === 'L4') {
    // The perimeter skirt is part of the rail/spring cage. In assembly it spans L4+L5,
    // hiding the magnet cavity from every side while the open top still exposes the mechanism.
    const skirtShape = roundedRectShape(MODEL_W - 0.38, MODEL_D - 0.38, CORNER_R - 0.08);
    skirtShape.holes.push(roundedRectHole(10.45, 4.45, 0.75));
    const skirt = addOutlinedMesh(group, extrudeShape(skirtShape, 0.70, 0.06), materials.pom, materials.pomEdge, 'L4_PERIMETER_CAVITY_SKIRT');
    positionOutlined(skirt, 0, 0, -0.20);
    makeCapsule(group, -4.72, 1.72, 4.72, 1.72, 0.30, spec.thickness, materials.gunmetal, materials.gunmetalEdge, 'L4_UPPER_GUIDE_RAIL');
    makeCapsule(group, -4.72,-1.72, 4.72,-1.72, 0.30, spec.thickness, materials.gunmetal, materials.gunmetalEdge, 'L4_LOWER_GUIDE_RAIL');
    makeCapsule(group, -4.82,-1.52,-4.82,1.52, 0.25, spec.thickness, materials.gunmetal, materials.gunmetalEdge, 'L4_LEFT_CROSS_RAIL');
    makeCapsule(group,  4.82,-1.52, 4.82,1.52, 0.25, spec.thickness, materials.gunmetal, materials.gunmetalEdge, 'L4_RIGHT_CROSS_RAIL');
    makeCapsule(group, 0,-1.06,0,1.06, 0.18, spec.thickness * 0.72, materials.gunmetal, materials.gunmetalEdge, 'L4_CENTER_BRIDGE');
    makeTube(group, [[-4.20,0.98],[-4.58,0.78],[-4.10,0.61],[-1.12,0.61],[-0.55,0.87],[-0.15,0.87]], 0.115, materials.titaniumDark, materials.gunmetalEdge, 'L4_UPPER_LEAF_SPRING');
    makeTube(group, [[0.15,-0.87],[0.55,-0.87],[1.12,-0.61],[4.10,-0.61],[4.58,-0.78],[4.20,-0.98]], 0.115, materials.titaniumDark, materials.gunmetalEdge, 'L4_LOWER_LEAF_SPRING');
  } else if (spec.id === 'L5') {
    MAGNET_X.forEach((x, magnetIndex) => {
      const geometry = new THREE.CylinderGeometry(0.41, 0.41, spec.thickness, 64, 2, false);
      geometry.rotateX(Math.PI / 2);
      const magnet = addOutlinedMesh(group, geometry, materials.magnet, materials.magnetEdge, `M${magnetIndex + 1}`);
      positionOutlined(magnet, x, 0, 0);
    });
  } else if (spec.id === 'L6') {
    const lower = roundedRectShape(MODEL_W - 0.34, MODEL_D - 0.34, CORNER_R - 0.10);
    // Through-cut pocket mouths plus a recessed floor create real, readable shallow wells.
    addSixCircleHoles(lower, 0.455);
    lower.holes.push(roundedRectHole(9.15, 0.44, 0.21, 0, 1.67));
    lower.holes.push(roundedRectHole(9.15, 0.44, 0.21, 0,-1.67));
    addFourCornerHoles(lower, 0.13, 5.0, 2.03);
    addOutlinedMesh(group, extrudeShape(lower, spec.thickness, 0.07), materials.titanium, materials.titaniumEdge, 'L6_LOWER_SIX_RECESS_CARRIER');
    MAGNET_X.forEach((x, recessIndex) => {
      const wellGeometry = new THREE.CylinderGeometry(0.455, 0.455, 0.050, 64, 1, false);
      wellGeometry.rotateX(Math.PI / 2);
      const well = new THREE.Mesh(wellGeometry, materials.recess);
      well.name = `L6_RECESS_${recessIndex + 1}`;
      well.position.set(x, 0, spec.thickness / 2 - 0.050);
      group.add(well);
      const rimGeometry = new THREE.TorusGeometry(0.455, 0.028, 12, 64);
      const rimMesh = new THREE.Mesh(rimGeometry, materials.titaniumDark);
      rimMesh.name = `L6_RECESS_RIM_${recessIndex + 1}`;
      rimMesh.position.set(x, 0, spec.thickness / 2 - 0.025);
      group.add(rimMesh);
    });
  } else if (spec.id === 'L7') {
    const shell = roundedRectShape(MODEL_W, MODEL_D, CORNER_R);
    addOutlinedMesh(group, extrudeShape(shell, spec.thickness, 0.08), materials.titanium, materials.titaniumEdge, 'L7_TITANIUM_BACK_SHELL');
    const inset = addOutlinedMesh(group, extrudeShape(roundedRectShape(MODEL_W - 0.52, MODEL_D - 0.52, CORNER_R - 0.22), 0.055, 0.018), materials.titaniumDark, materials.titaniumEdge, 'L7_REAR_INSET');
    positionOutlined(inset, 0, 0, -spec.thickness / 2 - 0.036);
    [[-5.03,-2.05],[-5.03,2.05],[5.03,-2.05],[5.03,2.05]].forEach(([x,y], screwIndex) => {
      const screwGeometry = new THREE.CylinderGeometry(0.23, 0.23, 0.075, 48, 1, false);
      screwGeometry.rotateX(Math.PI / 2);
      const screw = new THREE.Mesh(screwGeometry, materials.gunmetal);
      screw.name = `L7_REAR_SCREW_${screwIndex + 1}`;
      screw.position.set(x, y, -spec.thickness / 2 - 0.092);
      group.add(screw);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.255, 0.042, 12, 48), materials.titanium);
      ring.name = `L7_REAR_SCREW_RING_${screwIndex + 1}`;
      ring.position.set(x, y, -spec.thickness / 2 - 0.135);
      group.add(ring);
    });
  }
}

if (VIEW === 'exploded') {
  const guideMaterial = new THREE.LineDashedMaterial({ color: 0xf47a31, dashSize: 0.20, gapSize: 0.18, transparent: true, opacity: 0.30 });
  const minZ = layerGroups[6].position.z - 0.62;
  const maxZ = layerGroups[0].position.z + 0.56;
  [[-5.10,-2.06], [5.10,-2.06], [-5.10,2.06], [5.10,2.06]].forEach(([x,y], index) => {
    const geometry = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x,y,minZ), new THREE.Vector3(x,y,maxZ)]);
    const line = new THREE.Line(geometry, guideMaterial);
    line.name = `EXPLODE_ALIGNMENT_GUIDE_${index + 1}`;
    line.computeLineDistances();
    model.add(line);
  });
  const magnetAxisMaterial = new THREE.LineDashedMaterial({ color: 0xff7a2c, dashSize: 0.16, gapSize: 0.13, transparent: true, opacity: 0.78 });
  const axisMinZ = layerGroups[5].position.z - 0.05;
  const axisMaxZ = layerGroups[1].position.z + 0.05;
  MAGNET_X.forEach((x, index) => {
    const geometry = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x, 0, axisMinZ), new THREE.Vector3(x, 0, axisMaxZ)]);
    const line = new THREE.Line(geometry, magnetAxisMaterial);
    line.name = `M${index + 1}_COAXIAL_GUIDE_L2_L3_L5_L6`;
    line.computeLineDistances();
    model.add(line);
  });
}

function makeCamera() {
  const aspect = stage.clientWidth / stage.clientHeight;
  let height = 9.2;
  let position = new THREE.Vector3(0, 0, 18);
  let target = new THREE.Vector3(0, 0, 0.12);
  let up = new THREE.Vector3(0, 1, 0);

  if (VIEW === 'exploded') {
    height = 23.8;
    position.set(6.0, -20.0, 15.0);
    target.set(-0.55, 0, 0.25);
    up.set(0, 0, 1);
  } else if (VIEW === 'top') {
    position.set(0, 0, 18);
    target.set(0, 0, 0.12);
    up.set(0, 1, 0);
  } else if (VIEW === 'back') {
    position.set(0, 0, -18);
    target.set(0, 0, 0);
    up.set(0, 1, 0);
  } else if (VIEW === 'front') {
    position.set(0, -20, 0.15);
    target.set(0, 0, 0.15);
    up.set(0, 0, 1);
  } else if (VIEW === 'left') {
    position.set(-20, 0, 0.15);
    target.set(0, 0, 0.15);
    up.set(0, 0, 1);
  } else if (VIEW === 'right') {
    position.set(20, 0, 0.15);
    target.set(0, 0, 0.15);
    up.set(0, 0, 1);
  }

  const camera = new THREE.OrthographicCamera(-height * aspect / 2, height * aspect / 2, height / 2, -height / 2, 0.1, 100);
  camera.position.copy(position);
  camera.up.copy(up);
  camera.lookAt(target);
  camera.updateProjectionMatrix();
  return camera;
}

const camera = makeCamera();
window.__MODEL_BOOT__ = 'geometry-built';
renderer.render(scene, camera);
window.__MODEL_BOOT__ = 'frame-rendered';

const magnetLayer = model.getObjectByName('L5_MAGNETS');
const invariant = {
  geometrySignature: 'pushcard-7L-6M-inlineX-zs-frame-v2-final',
  sourceGeometry: 'single-scene-deterministic',
  layerCount: layerGroups.length,
  layerIds: layerGroups.map((group) => group.userData.layerId),
  magnetCount: magnetLayer.children.filter((child) => /^M[1-6]$/.test(child.name)).length,
  magnetIds: MAGNET_X.map((_, index) => `M${index + 1}`),
  magnetPositions: MAGNET_X.map((x) => ({ x, y: 0 })),
  magnetAxis: 'X',
  alignedSixFeatureLayers: ['L2', 'L3', 'L5', 'L6'],
  magnetLayer: 'L5',
  topFrameCornerHoles: 4,
  orthographicHeight: camera.top - camera.bottom,
  zOpenworkCenterlineClear: true,
  view: VIEW,
};
window.__MODEL_MANIFEST__ = invariant;
window.__RENDER_READY__ = true;
