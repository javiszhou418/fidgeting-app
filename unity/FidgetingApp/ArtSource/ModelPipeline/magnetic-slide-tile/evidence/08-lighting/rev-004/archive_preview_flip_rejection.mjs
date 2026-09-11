#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const source =
  "/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-fa15ff0e-86d8-4994-8c82-ffb1ef9b1b64.png";
const archived = path.join(here, "user-feedback-invalid-vertical-flip.png");
const digest = (file) =>
  crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

fs.copyFileSync(source, archived, fs.constants.COPYFILE_EXCL);
const sourceHash = digest(source);
const archivedHash = digest(archived);
if (sourceHash !== archivedHash) {
  throw new Error("Archived feedback hash mismatch.");
}

const record = {
  schemaVersion: 1,
  gate: "08-lighting",
  revision: 4,
  decision: "rejected",
  disposition: "internal-never-register-as-approval-evidence",
  attemptedVideo: {
    status: "interrupted-before-encoding",
    registered: false,
    approvalEvidence: false,
  },
  feedbackImage: {
    path:
      "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
      + "08-lighting/rev-004/user-feedback-invalid-vertical-flip.png",
    sha256: archivedHash,
  },
  userFeedbackExact:
    "The user rejects the preview video because it introduces an impossible "
    + "vertical/card flip. Interrupt the active recording task. Mark the current "
    + "invalid video as rejected/internal and do not register or present it as "
    + "approval evidence.",
  invariant:
    "BottomBase and the whole assembly remain fixed, horizontal and world-up. "
    + "Only approved local-axis slide and in-plane +Z yaw are legal. Camera orbit "
    + "keeps constant elevation, zero roll and stable world-up.",
  recordedAt: new Date().toISOString(),
};
fs.writeFileSync(
  path.join(here, "preview-flip-rejection.json"),
  `${JSON.stringify(record, null, 2)}\n`,
);
console.log(JSON.stringify(record, null, 2));
