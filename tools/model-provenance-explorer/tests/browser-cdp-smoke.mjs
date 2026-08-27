import assert from "node:assert/strict";
import fs from "node:fs";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9223";
const output = process.env.BROWSER_SMOKE_SCREENSHOT || "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev15-minimum-overlap-disk-cad.png";
const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page");
assert.ok(target, "Open a CDP browser page before running this smoke test.");
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});
let sequence = 0;
const pending = new Map();
const runtimeExceptions = [];
const loadingFailures = [];
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (message.method === "Runtime.exceptionThrown") runtimeExceptions.push(message.params.exceptionDetails);
  if (message.method === "Network.loadingFailed" && !message.params.canceled) loadingFailures.push(message.params);
  if (!message.id || !pending.has(message.id)) return;
  const waiter = pending.get(message.id);
  pending.delete(message.id);
  if (message.error) waiter.reject(new Error(message.error.message));
  else waiter.resolve(message.result);
});
const call = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++sequence;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const response = await call("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text || "Browser evaluation failed.");
  return response.result.value;
};
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const eventually = async (expression, description, timeout = 8000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await delay(100);
  }
  assert.fail(`Timed out waiting for ${description}.`);
};
const clickCenter = async (selector) => {
  const point = await evaluate(`(() => {
    const node = document.querySelector(${JSON.stringify(selector)});
    node.scrollIntoView({ block: "center", behavior: "instant" });
    const rect = node.getBoundingClientRect();
    return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
  })()`);
  await call("Input.dispatchMouseEvent", { type: "mouseMoved", ...point });
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...point, button: "left", buttons: 1, clickCount: 1 });
  await call("Input.dispatchMouseEvent", { type: "mouseReleased", ...point, button: "left", buttons: 0, clickCount: 1 });
};
const dragFromCenter = async (selector, deltaX, deltaY, steps = 8) => {
  const start = await evaluate(`(() => {
    const node = document.querySelector(${JSON.stringify(selector)});
    node.scrollIntoView({ block: "center", behavior: "instant" });
    const rect = node.getBoundingClientRect();
    return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
  })()`);
  await call("Input.dispatchMouseEvent", { type: "mouseMoved", ...start });
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...start, button: "left", buttons: 1, clickCount: 1 });
  for (let index = 1; index <= steps; index += 1) {
    await call("Input.dispatchMouseEvent", {
      type: "mouseMoved",
      x: start.x + deltaX * index / steps,
      y: start.y + deltaY * index / steps,
      button: "left",
      buttons: 1
    });
  }
  await call("Input.dispatchMouseEvent", {
    type: "mouseReleased",
    x: start.x + deltaX,
    y: start.y + deltaY,
    button: "left",
    buttons: 0,
    clickCount: 1
  });
};

try {
  await call("Runtime.enable");
  await call("Page.enable");
  await call("Network.enable");
  await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await call("Page.navigate", { url: "http://127.0.0.1:8891/tools/model-provenance-explorer/" });
  await eventually(`document.readyState === "complete"`, "workbench navigation");
  await evaluate(`localStorage.setItem("fidgeting-model-pipeline-selected", "magnetic-slide-tile")`);
  await call("Page.reload", { ignoreCache: true });
  const review = await eventually(`(() => {
    const root = document.querySelector(".mechanism-review");
    const cad = document.getElementById("mechanism-sandbox");
    if (!root || cad?.dataset.ready !== "true") return null;
    return {
      currentGate: document.querySelector(".canonical-progress")?.dataset.currentGate,
      approved: document.querySelector(".canonical-progress")?.dataset.approvedCount,
      roadmap: document.querySelectorAll(".gate-roadmap-item").length,
      title: root.querySelector("h2")?.textContent,
      tabs: root.querySelectorAll("[data-review-tab]").length,
      defaultTab: root.querySelector("[data-review-tab].is-active")?.dataset.reviewTab,
      cadOnly: cad.dataset.cadOnly,
      physicalInputsBlank: [...cad.querySelectorAll("[data-cad-physical]")].every((input) => input.value === ""),
      physicsControls: cad.querySelectorAll('[name="damping"], [name="slideResistance"], [name="rotationResistance"], [name="detentStrength"], [name="breakaway"], [name="inertiaHalfLife"], [name="endStopSoftness"], #sandbox-sound').length,
      recording: cad.querySelectorAll("video, #simulator-recording-video").length,
      simulatorLocked: root.querySelector('[data-review-panel="simulator"]')?.textContent.includes("交互 CAD 批准后生成"),
      approvalDisabled: document.getElementById("approve-stage")?.disabled,
      referenceHidden: root.querySelector('[data-review-panel="references"]').hidden,
      contractHash: cad.dataset.contractSha256
    };
  })()`, "Gate 02 CAD-only review");
  assert.deepEqual(review, {
    currentGate: "2",
    approved: "1",
    roadmap: 12,
    title: "直接操作交互 CAD，再确认结构",
    tabs: 4,
    defaultTab: "cad",
    cadOnly: "true",
    physicalInputsBlank: true,
    physicsControls: 0,
    recording: 0,
    simulatorLocked: true,
    approvalDisabled: true,
    referenceHidden: true,
    contractHash: "b4318452f163ef7c105c826d4466a739a1dd0d942d4d74d921c29c39e02a84f2"
  });

  const negativeApi = await evaluate(`(() => {
    const pose = window.__mechanismCad.setPose({ travelL: -0.25, angleDeg: 0 });
    const geometry = window.__mechanismCad.geometry();
    const root = document.getElementById("mechanism-sandbox");
    return {
      pose,
      coincident: geometry.closedStop.silhouettesCoincident,
      penetrationL: geometry.closedStop.penetrationL,
      clamped: root.dataset.closedStopClamped,
      label: document.getElementById("sandbox-live-closed-stop").textContent
    };
  })()`);
  assert.deepEqual(negativeApi.pose, { travelL: 0, angleDeg: 0 });
  assert.equal(negativeApi.coincident, true);
  assert.equal(negativeApi.penetrationL, 0);
  assert.equal(negativeApi.clamped, "true");
  assert.match(negativeApi.label, /闭合端点 · 随动点触槽起点/);
  await evaluate(`document.querySelector(".cad-stage").focus()`);
  await call("Input.dispatchKeyEvent", { type: "keyDown", key: "ArrowDown", code: "ArrowDown", windowsVirtualKeyCode: 40 });
  await call("Input.dispatchKeyEvent", { type: "keyUp", key: "ArrowDown", code: "ArrowDown", windowsVirtualKeyCode: 40 });
  assert.deepEqual(await evaluate(`window.__mechanismCad.pose()`), { travelL: 0, angleDeg: 0 });
  await evaluate(`document.querySelector("[data-cad-slide-hit]").scrollIntoView({ block: "center" })`);
  await dragFromCenter("[data-cad-slide-hit]", 0, 60);
  const inwardAtClosed = await evaluate(`(() => ({
    pose: window.__mechanismCad.pose(),
    clamped: document.getElementById("mechanism-sandbox").dataset.closedStopClamped
  }))()`);
  assert.deepEqual(inwardAtClosed.pose, { travelL: 0, angleDeg: 0 });
  assert.equal(inwardAtClosed.clamped, "true");
  await dragFromCenter("[data-cad-slide-hit]", 44, 0);
  const tangentialAtClosed = await evaluate(`window.__mechanismCad.pose()`);
  assert.equal(tangentialAtClosed.travelL, 0);
  assert.ok(tangentialAtClosed.angleDeg > 1 && tangentialAtClosed.angleDeg < 359);
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0.01, angleDeg: 0 })`);
  await dragFromCenter("[data-cad-slide-hit]", 40, 100);
  const diagonalNearStop = await evaluate(`window.__mechanismCad.pose()`);
  assert.equal(diagonalNearStop.travelL, 0);
  assert.ok(diagonalNearStop.angleDeg > 1 && diagonalNearStop.angleDeg < 359);

  await clickCenter('[data-cad-inspect="fixedAxis"]');
  await clickCenter('[data-cad-inspect="rotatingCarrier"]');
  await clickCenter('[data-cad-inspect="topUndersideGrooves"]');
  await clickCenter('[data-cad-inspect="smoothBottomExterior"]');
  await clickCenter("[data-cad-overlap-inspect]");
  await clickCenter('[data-cad-view-inspect="top"]');
  await clickCenter('[data-cad-view-inspect="side"]');
  await clickCenter('[data-cad-view-inspect="section"]');
  const directionResults = [];
  for (const [angleDeg, dx, dy] of [[0, 0, -36], [90, 36, 0], [180, 0, 36]]) {
    await evaluate(`window.__mechanismCad.setPose({ travelL: 0.14, angleDeg: ${angleDeg} })`);
    await evaluate(`document.querySelector("[data-cad-slide-hit]").scrollIntoView({ block: "center", inline: "center" })`);
    const before = await evaluate(`(() => {
      const box = document.querySelector(".sandbox-top-motion").getBoundingClientRect();
      return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
    })()`);
    await dragFromCenter("[data-cad-slide-hit]", dx, dy);
    const after = await evaluate(`(() => {
      const box = document.querySelector(".sandbox-top-motion").getBoundingClientRect();
      const pose = window.__mechanismCad.pose();
      return {
        x: box.x + box.width / 2,
        y: box.y + box.height / 2,
        travelL: pose.travelL,
        angleDeg: pose.angleDeg,
        modelLength: window.__mechanismCad.geometry().upper.length
      };
    })()`);
    const radians = angleDeg * Math.PI / 180;
    const travelPixels = (after.travelL - 0.14) * after.modelLength;
    const predictedDelta = [Math.sin(radians) * travelPixels, -Math.cos(radians) * travelPixels];
    directionResults.push({
      angleDeg,
      dot: predictedDelta[0] * dx + predictedDelta[1] * dy,
      travelL: after.travelL,
      solvedAngleDeg: after.angleDeg
    });
  }
  assert.ok(
    directionResults.every((result) => result.dot > 0 && result.travelL > 0.14),
    JSON.stringify(directionResults)
  );
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0.16, angleDeg: 24 })`);
  await dragFromCenter("[data-cad-slide-hit]", 54, -110);
  const compound = await evaluate(`(() => {
    const pose = window.__mechanismCad.pose();
    const geometry = window.__mechanismCad.geometry();
    return {
      travelL: pose.travelL,
      angleDeg: pose.angleDeg,
      bottomTransform: document.querySelector(".sandbox-fixed-bottom").getAttribute("transform"),
      axisLocal: geometry.axis.localToBottom,
      axisWorld: geometry.axis.world,
      axisAttachment: geometry.axis.attachment,
      carrierTranslation: geometry.carrier.translation,
      followerCount: geometry.followers.count,
      grooveCount: geometry.grooves.count,
      grooveOwner: geometry.grooves.owner,
      groovesParallel: geometry.grooves.parallelToFollowers,
      smoothBottom: geometry.bottom.exposedRailCount === 0 && geometry.bottom.exposedGrooveCount === 0,
      axisCovered: geometry.coverage.axisCovered
    };
  })()`);
  assert.ok(compound.travelL > 0.02);
  assert.ok(compound.angleDeg > 0.5 && compound.angleDeg < 359.5);
  assert.equal(compound.bottomTransform, "translate(0 0)");
  assert.equal(compound.axisAttachment, "fixed-axis-center-in-bottom");
  assert.deepEqual(compound.axisWorld, compound.axisLocal);
  assert.deepEqual(compound.carrierTranslation, [0, 0]);
  assert.equal(compound.followerCount, 2);
  assert.equal(compound.grooveCount, 2);
  assert.equal(compound.grooveOwner, "TopPlate underside");
  assert.equal(compound.groovesParallel, true);
  assert.equal(compound.smoothBottom, true);
  assert.equal(compound.axisCovered, true);
  assert.equal(compound.axisLocal.length, 2);

  await clickCenter('[data-cad-pose="open"]');
  const endpointAndLayer = await evaluate(`(() => {
    const root = document.getElementById("mechanism-sandbox");
    const geometry = window.__mechanismCad.geometry();
    const bottom = document.querySelector('[data-cad-component="BottomExterior"]');
    const top = document.querySelector('[data-cad-component="TopPlate"]');
    return {
      atGrooveEnd: geometry.followers.atOpenEndpoint,
      engaged: geometry.followers.engaged,
      distanceToEndL: geometry.followers.distanceToEndL,
      axisCovered: geometry.coverage.axisCovered,
      diskCovered: geometry.minimumOverlapDisk.fullyCovered,
      boundaryContact: geometry.minimumOverlapDisk.boundaryContact,
      marginL: geometry.minimumOverlapDisk.containment.marginL,
      limitingCause: geometry.minimumOverlapDisk.activeLimitingCause,
      topZ: Number(top.dataset.layerZ),
      bottomZ: Number(bottom.dataset.layerZ),
      topAfterBottom: Boolean(bottom.compareDocumentPosition(top) & Node.DOCUMENT_POSITION_FOLLOWING),
      clipPaths: document.querySelectorAll("clipPath, [clip-path]").length,
      bottomMasksTop: root.dataset.bottomMasksTop
    };
  })()`);
  assert.equal(endpointAndLayer.atGrooveEnd, false);
  assert.equal(endpointAndLayer.engaged, true);
  assert.ok(endpointAndLayer.distanceToEndL > 0.09);
  assert.equal(endpointAndLayer.axisCovered, true);
  assert.equal(endpointAndLayer.diskCovered, true);
  assert.equal(endpointAndLayer.boundaryContact, true);
  assert.ok(Math.abs(endpointAndLayer.marginL) < 1e-9);
  assert.equal(endpointAndLayer.limitingCause, "MinimumOverlapDisk");
  assert.ok(endpointAndLayer.topZ > endpointAndLayer.bottomZ);
  assert.equal(endpointAndLayer.topAfterBottom, true);
  assert.equal(endpointAndLayer.clipPaths, 0);
  assert.equal(endpointAndLayer.bottomMasksTop, "false");
  await evaluate(`document.querySelector("[data-cad-slide-hit]").scrollIntoView({ block: "center" })`);
  await dragFromCenter("[data-cad-slide-hit]", 42, -70);
  const beyondOpen = await evaluate(`(() => ({
    pose: window.__mechanismCad.pose(),
    endpoint: document.getElementById("mechanism-sandbox").dataset.activeGrooveEndpoint,
    engaged: window.__mechanismCad.geometry().followers.engaged
  }))()`);
  assert.ok(Math.abs(beyondOpen.pose.travelL - 0.3615286624203821) < 1e-9);
  assert.ok(beyondOpen.pose.angleDeg > 1 && beyondOpen.pose.angleDeg < 359);
  assert.equal(beyondOpen.endpoint, "open");
  assert.equal(beyondOpen.engaged, true);
  await clickCenter('[data-detent-step="1"]');
  await clickCenter("[data-cad-sweep-toggle]");
  const debugInvalid = await evaluate(`(() => {
    const forced = window.__mechanismCad.forceDebugInvalidPose({ travelL: 0.39, angleDeg: 47 });
    const root = document.getElementById("mechanism-sandbox");
    return {
      forced,
      covered: root.dataset.minimumOverlapCovered,
      flashes: document.querySelector(".cad-minimum-overlap-disk").classList.contains("is-invalid")
    };
  })()`);
  assert.equal(debugInvalid.forced.invalid, true);
  assert.equal(debugInvalid.covered, "false");
  assert.equal(debugInvalid.flashes, true);
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0, angleDeg: 0 })`);
  const parameterSwitch = await evaluate(`(() => {
    const groove = window.__mechanismCad.updateNormalizedParameters({ minimumOverlapDiskRadiusL: 0.1 });
    const disk = window.__mechanismCad.updateNormalizedParameters({ minimumOverlapDiskRadiusL: 0.3184713375796178 });
    return { groove, disk };
  })()`);
  assert.equal(parameterSwitch.groove.limitingCause, "FiniteGrooveEndpoint");
  assert.equal(parameterSwitch.groove.maxTravelL, 0.46);
  assert.equal(parameterSwitch.disk.limitingCause, "MinimumOverlapDisk");
  assert.ok(Math.abs(parameterSwitch.disk.maxTravelL - 0.3615286624203821) < 1e-9);
  await clickCenter('[data-cad-pose="open"]');
  await evaluate(`(() => {
    const input = document.getElementById("cad-layer-separation");
    input.value = "0.6";
    input.dispatchEvent(new Event("input", { bubbles: true }));
  })()`);
  await clickCenter("#source-constraint-inspector summary");
  const approval = await eventually(`(() => {
    const root = document.getElementById("mechanism-sandbox");
    if (root.dataset.approvalReady !== "true") return null;
    const payload = window.__cadApproval.createPayload();
    return {
      count: root.querySelector("#cad-checklist-count").textContent,
      enabled: !document.getElementById("approve-stage").disabled,
      mode: payload.mode,
      views: payload.viewsInspected,
      artifactHash: payload.artifactHash,
      contractHash: payload.contractHash,
      checklist: payload.completedInteractionChecklist.length,
      pivot: payload.geometryParameterSnapshot.fixedAxisAttachment,
      axisInvariant: JSON.stringify(payload.geometryParameterSnapshot.fixedAxisBottomLocal)
        === JSON.stringify(payload.geometryParameterSnapshot.fixedAxisWorld),
      components: payload.geometryParameterSnapshot.componentLayers.length,
      followerCount: payload.geometryParameterSnapshot.followerCount,
      grooveCount: payload.geometryParameterSnapshot.grooveCount,
      smoothBottom: payload.geometryParameterSnapshot.smoothBottomExterior,
      axisCovered: payload.geometryParameterSnapshot.axisCoveredAtCurrentPose,
      closedStopL: payload.geometryParameterSnapshot.closedStopL,
      closedStopHard: payload.geometryParameterSnapshot.closedStopHard,
      negativeTravelForbidden: payload.geometryParameterSnapshot.negativeTravelForbidden,
      closedSilhouetteCoincident: payload.geometryParameterSnapshot.closedSilhouetteCoincident,
      closedStopPenetrationL: payload.geometryParameterSnapshot.closedStopPenetrationL,
      grooveLengthL: payload.geometryParameterSnapshot.grooveLengthL,
      maxTravelDerived: payload.geometryParameterSnapshot.maxTravelDerivedFromGrooveEndpoints,
      grooveEndpointLimitL: payload.geometryParameterSnapshot.grooveEndpointLimitL,
      overlapContainmentLimitL: payload.geometryParameterSnapshot.overlapContainmentLimitL,
      actualSMaxL: payload.geometryParameterSnapshot.actualSMaxL,
      activeLimitingCause: payload.geometryParameterSnapshot.activeLimitingCause,
      diskOwner: payload.geometryParameterSnapshot.minimumOverlapDiskOwner,
      diskRadiusL: payload.geometryParameterSnapshot.minimumOverlapDiskRadiusL,
      diskPhysicalMm: payload.geometryParameterSnapshot.minimumOverlapDiskPhysicalMm,
      diskCovered: payload.geometryParameterSnapshot.minimumOverlapFullyCovered,
      overlapAngleInvariant: payload.geometryParameterSnapshot.overlapAngleInvariant,
      analyticContinuous: payload.geometryParameterSnapshot.analyticContainmentContinuous,
      denseAngles: payload.geometryParameterSnapshot.denseAngleSampleCount,
      boundaryTangency: payload.geometryParameterSnapshot.exactBoundaryTangency,
      beyondBoundaryInvalid: payload.geometryParameterSnapshot.beyondBoundaryInvalid,
      followerEngagedAtClosed: payload.geometryParameterSnapshot.followerEngagedAtClosed,
      followerEngagedAtOpen: payload.geometryParameterSnapshot.followerEngagedAtOpen,
      axisCoveredAtOpen: payload.geometryParameterSnapshot.axisCoveredAtOpen,
      sweepSamples: payload.geometryParameterSnapshot.sweptEnvelopeSampleCount,
      sweepValid: payload.geometryParameterSnapshot.sweptEnvelopeAllValid,
      topZ: payload.geometryParameterSnapshot.topZ,
      bottomZ: payload.geometryParameterSnapshot.bottomZ,
      bottomMasksTop: payload.geometryParameterSnapshot.bottomMasksTop,
      hasTimestamp: Number.isFinite(Date.parse(payload.browserTimestamp))
    };
  })()`, "CAD approval checklist");
  assert.equal(approval.count, "12 / 12");
  assert.equal(approval.enabled, true);
  assert.equal(approval.mode, "interactive-cad");
  assert.deepEqual(approval.views, ["top", "side", "section"]);
  assert.equal(approval.artifactHash, "494d2d908740f42be7b74947a0d77373bd99b3346af8f72d6452f18655a98ded");
  assert.equal(approval.contractHash, review.contractHash);
  assert.equal(approval.checklist, 12);
  assert.equal(approval.pivot, "fixed-axis-center-in-bottom");
  assert.equal(approval.axisInvariant, true);
  assert.equal(approval.components, 10);
  assert.equal(approval.followerCount, 2);
  assert.equal(approval.grooveCount, 2);
  assert.equal(approval.smoothBottom, true);
  assert.equal(approval.axisCovered, true);
  assert.equal(approval.closedStopL, 0);
  assert.equal(approval.closedStopHard, true);
  assert.equal(approval.negativeTravelForbidden, true);
  assert.equal(approval.closedSilhouetteCoincident, true);
  assert.equal(approval.closedStopPenetrationL, 0);
  assert.equal(approval.grooveLengthL, 0.46);
  assert.equal(approval.maxTravelDerived, false);
  assert.equal(approval.grooveEndpointLimitL, 0.46);
  assert.ok(Math.abs(approval.overlapContainmentLimitL - 0.3615286624203821) < 1e-9);
  assert.equal(approval.actualSMaxL, approval.overlapContainmentLimitL);
  assert.equal(approval.activeLimitingCause, "MinimumOverlapDisk");
  assert.equal(approval.diskOwner, "BottomBase");
  assert.ok(Math.abs(approval.diskRadiusL - 0.3184713375796178) < 1e-9);
  assert.equal(approval.diskPhysicalMm, null);
  assert.equal(approval.diskCovered, true);
  assert.equal(approval.overlapAngleInvariant, true);
  assert.equal(approval.analyticContinuous, true);
  assert.equal(approval.denseAngles, 360);
  assert.equal(approval.boundaryTangency, true);
  assert.equal(approval.beyondBoundaryInvalid, true);
  assert.equal(approval.followerEngagedAtClosed, true);
  assert.equal(approval.followerEngagedAtOpen, true);
  assert.equal(approval.axisCoveredAtOpen, true);
  assert.equal(approval.sweepSamples, 1800);
  assert.equal(approval.sweepValid, true);
  assert.ok(approval.topZ > approval.bottomZ);
  assert.equal(approval.bottomMasksTop, false);
  assert.equal(approval.hasTimestamp, true);

  await evaluate(`window.__mechanismCad.setPose({ travelL: 0.46, angleDeg: 0 })`);
  await evaluate(`document.querySelector("[data-cad-slide-hit]").scrollIntoView({ block: "center" })`);
  await dragFromCenter("[data-cad-slide-hit]", 0, 240);
  assert.deepEqual(await evaluate(`window.__mechanismCad.pose()`), { travelL: 0, angleDeg: 0 });
  await dragFromCenter("[data-cad-slide-hit]", 0, 80);
  assert.deepEqual(await evaluate(`window.__mechanismCad.pose()`), { travelL: 0, angleDeg: 0 });
  await clickCenter("#cad-reset");
  assert.deepEqual(await evaluate(`window.__mechanismCad.pose()`), { travelL: 0, angleDeg: 0 });
  await clickCenter('[data-cad-zoom="in"]');
  await clickCenter('[data-sandbox-mode="pan"]');
  await dragFromCenter(".cad-stage", 36, 24);
  const viewport = await evaluate(`window.__mechanismCad.viewport()`);
  assert.ok(viewport.zoom > 1);
  assert.ok(Math.abs(viewport.panX) > 0 && Math.abs(viewport.panY) > 0);
  await clickCenter('[data-sandbox-mode="compound"]');
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0.14, angleDeg: 270 })`);
  await evaluate(`document.querySelector("[data-cad-slide-hit]").scrollIntoView({ block: "center", inline: "center" })`);
  await dragFromCenter("[data-cad-slide-hit]", -36, 0);
  const zoomPanDirection = await evaluate(`(() => {
    const pose = window.__mechanismCad.pose();
    return { travelL: pose.travelL, angleDeg: pose.angleDeg };
  })()`);
  assert.ok(zoomPanDirection.travelL > 0.14);
  assert.ok(Math.abs(zoomPanDirection.angleDeg - 270) < 0.1);
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0, angleDeg: 0 })`);
  await dragFromCenter("[data-cad-slide-hit]", 0, 60);
  assert.deepEqual(await evaluate(`window.__mechanismCad.pose()`), { travelL: 0, angleDeg: 0 });

  await clickCenter('[data-review-tab="references"]');
  const references = await eventually(`(() => {
    const panel = document.querySelector('[data-review-panel="references"]');
    if (panel.hidden) return null;
    const cards = [...panel.querySelectorAll(".mechanism-reference-card")];
    return {
      count: cards.length,
      everyApplied: cards.every((card) => card.querySelector(".reference-applied-to")?.textContent.includes("已应用到")),
      userVideos: cards.filter((card) => /IMG_602[234]/.test(card.textContent)).length,
      hasUrls: cards.some((card) => card.querySelector('a[href^="http"]')),
      selectedRefs: cards.filter((card) => card.dataset.referenceSource === "用户权威选图").length,
      selectedApplied: cards.filter((card) => card.dataset.referenceSource === "用户权威选图")
        .every((card) => /光滑底壳|固定轴|轴心覆盖/.test(card.querySelector(".reference-applied-to")?.textContent || "")),
      carrierMapped: cards.some((card) => card.querySelector("[data-asset-id]")?.dataset.assetId === "slider-intake-haloo-official-07"
        && card.querySelector(".reference-applied-to")?.textContent.includes("ROTATING-CARRIER")),
      groovesMapped: cards.some((card) => ["slider-intake-nxedc-ref-03", "slider-intake-nxedc-ref-04"].includes(card.querySelector("[data-asset-id]")?.dataset.assetId)
        && card.querySelector(".reference-applied-to")?.textContent.includes("TOP-UNDERSIDE-GROOVES"))
    };
  })()`, "source references");
  assert.ok(references.count >= 18);
  assert.equal(references.everyApplied, true);
  assert.equal(references.userVideos, 3);
  assert.equal(references.hasUrls, true);
  assert.equal(references.selectedRefs, 2);
  assert.equal(references.selectedApplied, true);
  assert.equal(references.carrierMapped, true);
  assert.equal(references.groovesMapped, true);
  await evaluate(`document.querySelector('.mechanism-reference-card[data-reference-source="官方同款"] [data-asset-id]').click()`);
  assert.equal(await eventually(`document.getElementById("asset-dialog")?.open === true`, "image modal"), true);
  await clickCenter("#dialog-close");
  await evaluate(`(() => {
    const card = [...document.querySelectorAll(".mechanism-reference-card")].find((item) => item.textContent.includes("IMG_6022"));
    card.querySelector("[data-asset-id]").click();
  })()`);
  const video = await eventually(`(() => {
    const node = document.querySelector("#asset-dialog video");
    if (!node || node.readyState < 1) return null;
    return { width: node.videoWidth, height: node.videoHeight, duration: node.duration, error: node.error };
  })()`, "video playback");
  assert.equal(video.error, null);
  assert.equal(video.width, 720);
  assert.equal(video.height, 1280);
  assert.ok(video.duration > 14 && video.duration < 15);
  await clickCenter("#dialog-close");

  await clickCenter('[data-review-tab="cad"]');
  await evaluate(`document.getElementById("source-constraint-inspector").open = false; document.querySelector(".gate-roadmap").open = false; window.scrollTo({ top: 0, behavior: "instant" })`);
  await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1200, deviceScaleFactor: 1, mobile: false });
  const screenshot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false, fromSurface: true });
  fs.writeFileSync(output, Buffer.from(screenshot.data, "base64"));

  await call("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 1 });
  await call("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 2,
    mobile: true,
    screenWidth: 390,
    screenHeight: 844
  });
  await call("Page.reload", { ignoreCache: true });
  const mobile = await eventually(`(() => {
    const cad = document.getElementById("mechanism-sandbox");
    if (cad?.dataset.ready !== "true") return null;
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      roadmap: document.querySelectorAll(".gate-roadmap-item").length,
      tabs: document.querySelectorAll("[data-review-tab]").length,
      cadOnly: cad.dataset.cadOnly,
      physicsControls: cad.querySelectorAll('[name="damping"], [name="slideResistance"], [name="rotationResistance"], [name="detentStrength"], [name="breakaway"], [name="inertiaHalfLife"], [name="endStopSoftness"], #sandbox-sound').length,
      layerControls: cad.querySelectorAll("#cad-layer-separation, #cad-layer-opacity, [data-cad-layer-toggle]").length
    };
  })()`, "mobile CAD view");
  assert.ok(mobile.overflow <= 1);
  assert.equal(mobile.roadmap, 12);
  assert.equal(mobile.tabs, 4);
  assert.equal(mobile.cadOnly, "true");
  assert.equal(mobile.physicsControls, 0);
  assert.equal(mobile.layerControls, 12);
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0.14, angleDeg: 90 })`);
  await evaluate(`document.querySelector("[data-cad-slide-hit]").scrollIntoView({ block: "center", inline: "center" })`);
  await dragFromCenter("[data-cad-slide-hit]", 28, 0);
  const mobileDirection = await evaluate(`(() => ({
    travelL: window.__mechanismCad.pose().travelL,
    angleDeg: window.__mechanismCad.pose().angleDeg
  }))()`);
  assert.ok(mobileDirection.travelL > 0.14);
  assert.ok(Math.abs(mobileDirection.angleDeg - 90) < 0.1);
  await evaluate(`window.__mechanismCad.setPose({ travelL: 0, angleDeg: 0 })`);
  await dragFromCenter("[data-cad-slide-hit]", 0, 44);
  const mobileClosedStop = await evaluate(`window.__mechanismCad.pose()`);
  assert.deepEqual(mobileClosedStop, { travelL: 0, angleDeg: 0 });

  assert.deepEqual(runtimeExceptions, []);
  assert.deepEqual(loadingFailures.filter((failure) => !failure.errorText.includes("ERR_ABORTED")), []);
  console.log(JSON.stringify({ review, negativeApi, inwardAtClosed, tangentialAtClosed, diagonalNearStop, directionResults, compound, approval, references, video, mobile, mobileDirection, mobileClosedStop, screenshot: output }, null, 2));
} finally {
  socket.close();
}
