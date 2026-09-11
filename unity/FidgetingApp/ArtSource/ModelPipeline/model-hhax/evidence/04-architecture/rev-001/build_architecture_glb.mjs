import fs from "node:fs";
import * as THREE from "../../../../../../../../tools/model-provenance-explorer/node_modules/three/build/three.module.js";
import { GLTFExporter } from "../../../../../../../../tools/model-provenance-explorer/node_modules/three/examples/jsm/exporters/GLTFExporter.js";

globalThis.FileReader = class FileReader {
  readAsArrayBuffer(blob) { blob.arrayBuffer().then((value) => { this.result = value; this.onloadend?.(); }); }
  readAsDataURL(blob) { blob.arrayBuffer().then((value) => { this.result = `data:${blob.type};base64,${Buffer.from(value).toString("base64")}`; this.onloadend?.(); }); }
};

const scene = new THREE.Scene();
scene.name = "HHAX_Gate04_ExplodedArchitecture";
const materials = {
  metal: new THREE.MeshStandardMaterial({ color: 0x30283a, metalness: 0.92, roughness: 0.2 }),
  pearl: new THREE.MeshStandardMaterial({ color: 0xb9d2ce, metalness: 0.08, roughness: 0.28 }),
  coral: new THREE.MeshStandardMaterial({ color: 0xdd667b, metalness: 0.22, roughness: 0.3 }),
  glass: new THREE.MeshPhysicalMaterial({ color: 0xd9f5ff, transmission: 0.7, opacity: 0.38, transparent: true, roughness: 0.08, thickness: 0.7 }),
  track: new THREE.MeshStandardMaterial({ color: 0xc3904e, metalness: 0.9, roughness: 0.24 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x15121a, metalness: 0.5, roughness: 0.28 })
};
function shape(width, length) { const r=width/2, s=length/2-r, p=new THREE.Shape(); p.moveTo(-r,-s); p.absarc(0,-s,r,Math.PI,Math.PI*2,false); p.lineTo(r,s); p.absarc(0,s,r,0,Math.PI,false); p.closePath(); return p; }
function capsule(name, width, length, depth, material, position, scale=1) { const g=new THREE.ExtrudeGeometry(shape(width,length),{depth,bevelEnabled:true,bevelSegments:3,bevelSize:.4,bevelThickness:.35,curveSegments:32}); g.translate(0,0,-depth/2); const m=new THREE.Mesh(g,material); m.name=name; m.position.set(...position); m.scale.setScalar(scale); scene.add(m); return m; }
capsule("TransparentSealCap",29.4,49.0,.8,materials.glass,[-45,0,19]);
capsule("FrontArtworkInlay",27.8,47.2,.7,materials.pearl,[-15,0,13]);
const knight=new THREE.Mesh(new THREE.CylinderGeometry(6.5,6.5,.9,36),materials.coral); knight.name="FrontKnightInlay"; knight.rotation.x=Math.PI/2; knight.position.set(-15,7.0,14.1); scene.add(knight);
capsule("MovingUpperShell",30.9,50.5,6.55,materials.metal,[18,0,5]);
const railG=new THREE.BoxGeometry(1.7,29,1.3); for(const x of [45,58]){const rail=new THREE.Mesh(railG,materials.track);rail.name="StraightTrack_Provisional";rail.position.set(x,0,1);scene.add(rail);}
const ring=new THREE.Mesh(new THREE.TorusGeometry(10.8,1.2,12,64),materials.track);ring.name="RotaryCarrier_Provisional";ring.position.set(51.5,-4,1.2);scene.add(ring);
capsule("FixedLowerShell",30.9,50.5,6.55,materials.metal,[85,0,-4]);
const rear=new THREE.Mesh(new THREE.CylinderGeometry(10.8,10.8,1,48),materials.pearl);rear.name="MagneticReplaceableRearPatch";rear.rotation.x=Math.PI/2;rear.position.set(85,-5,-10.5);scene.add(rear);
const crest=new THREE.Mesh(new THREE.CylinderGeometry(5.4,5.4,.5,40),materials.coral);crest.name="RearKnightMedallion";crest.rotation.x=Math.PI/2;crest.position.set(85,-5,-11.3);scene.add(crest);
scene.userData={units:"millimeters",assembly:"two-exterior-shells",movingOwner:"MovingUpperShell",translationMm:[0,18.7],rotatingOwner:"MagneticReplaceableRearPatch / RotaryCarrier",rotationAxis:"Z thickness axis",magnetRole:"rear patch retention only",hiddenCoupling:"unknown",allInternalDimensions:"provisional reversible digital reconstruction"};
const exporter=new GLTFExporter();
const result=await new Promise((resolve,reject)=>exporter.parse(scene,resolve,reject,{binary:true,onlyVisible:true}));
fs.writeFileSync(new URL("./exploded-architecture.glb",import.meta.url),Buffer.from(result));
