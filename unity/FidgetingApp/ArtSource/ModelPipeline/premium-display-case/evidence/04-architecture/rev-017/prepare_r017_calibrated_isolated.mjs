#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const stagingRoot = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r017-test-calibration"
);
const sourceProject = "/tmp/FidgetingApp-PackOpening-R016-Repair-20260831";
const targetProject = "/tmp/FidgetingApp-PackOpening-R017-Calibration-20260831";
const sourcePackage = path.join(sourceProject, "Assets/IsolatedProofR016");
const targetPackage = path.join(targetProject, "Assets/IsolatedProofR017");
const sourceRig = path.join(
  sourceProject,
  "Assets/Source/R016/PackOpeningGate04R016PackOnlyRig.fbx"
);
const targetRig = path.join(
  targetProject,
  "Assets/Source/R017/PackOpeningGate04R017PackOnlyRig.fbx"
);
const calibrationPath = path.join(stagingRoot, "r017-test-calibration.json");
const excludedProjectDirectories = new Set([
  "Library",
  "Logs",
  "Captures",
  "Quarantine",
  "Temp",
  "obj",
  ".vs"
]);

function requireDirectory(directory) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) {
    throw new Error(`Missing required directory: ${directory}`);
  }
}

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required file: ${file}`);
  }
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function collectFiles(directory) {
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const item = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectFiles(item));
    } else {
      files.push(item);
    }
  }
  return files;
}

function replaceExactly(source, expected, replacement, label) {
  if (!source.includes(expected)) {
    throw new Error(`Could not apply R017 calibration: ${label}`);
  }
  return source.replace(expected, replacement);
}

function copyR016Project() {
  fs.cpSync(sourceProject, targetProject, {
    recursive: true,
    errorOnExist: true,
    filter: (source) => {
      const relative = path.relative(sourceProject, source);
      if (!relative) {
        return true;
      }
      return !relative
        .split(path.sep)
        .some((segment) => excludedProjectDirectories.has(segment));
    }
  });
}

function makeR017Package() {
  fs.cpSync(sourcePackage, targetPackage, {
    recursive: true,
    errorOnExist: true
  });
  const generated = path.join(targetPackage, "Generated");
  fs.rmSync(generated, { recursive: true, force: true });

  for (const file of collectFiles(targetPackage)) {
    if (!file.endsWith(".cs") && !file.endsWith(".shader")) {
      continue;
    }
    fs.writeFileSync(
      file,
      fs.readFileSync(file, "utf8")
        .replaceAll("R016", "R017")
        .replaceAll("r016", "r017"),
      "utf8"
    );
  }
  const renames = collectFiles(targetPackage)
    .filter((file) => path.basename(file).includes("R016"))
    .sort((left, right) => right.length - left.length);
  for (const file of renames) {
    fs.renameSync(file, file.replaceAll("R016", "R017"));
  }
  regeneratePackageGuids();
}

function regeneratePackageGuids() {
  for (const file of collectFiles(targetPackage)) {
    if (!file.endsWith(".meta")) {
      continue;
    }
    const source = fs.readFileSync(file, "utf8");
    if (!/^guid: .+$/m.test(source)) {
      throw new Error(`R017 metadata has no GUID: ${file}`);
    }
    fs.writeFileSync(
      file,
      source.replace(
        /^guid: .+$/m,
        `guid: ${crypto.randomBytes(16).toString("hex")}`
      ),
      "utf8"
    );
  }
}

function copyRigWithImporterSettings() {
  requireFile(sourceRig);
  requireFile(`${sourceRig}.meta`);
  fs.mkdirSync(path.dirname(targetRig), { recursive: true });
  fs.copyFileSync(sourceRig, targetRig, fs.constants.COPYFILE_EXCL);
  const importerMeta = fs.readFileSync(`${sourceRig}.meta`, "utf8")
    .replace(/^guid: .+$/m, `guid: ${crypto.randomBytes(16).toString("hex")}`);
  fs.writeFileSync(`${targetRig}.meta`, importerMeta, { encoding: "utf8", flag: "wx" });
}

function writeSourceManifest(calibration, copiedCalibration) {
  fs.writeFileSync(
    path.join(targetProject, "r017-source-manifest.json"),
    `${JSON.stringify({
      schema: "premium-display-case-gate04-r017-isolated-source.v1",
      isolatedUnityCandidate: true,
      canonicalIntegration: false,
      immutableR016Input: {
        project: sourceProject,
        rig: sourceRig,
        rigSha256: sha256(sourceRig)
      },
      calibration: {
        path: path.relative(targetProject, copiedCalibration),
        sha256: sha256(copiedCalibration),
        expectedMeters: calibration.meshDeltaAssertion.expectedMeters,
        relativeTolerance: calibration.meshDeltaAssertion.relativeTolerance
      },
      copiedR017Rig: {
        path: path.relative(targetProject, targetRig),
        sha256: sha256(targetRig)
      },
      sourceFiles: collectFiles(targetPackage).map((file) => ({
        path: path.relative(targetProject, file),
        sha256: sha256(file)
      })),
      shippingReady: false,
      physicalDeviceInstalled: false
    }, null, 2)}\n`,
    "utf8"
  );
}

function applyPreflightCalibration(calibration) {
  const capturePath = path.join(
    targetPackage,
    "Runtime/IsolatedR017ProofCapture.cs"
  );
  let source = fs.readFileSync(capturePath, "utf8");
  source = replaceExactly(
    source,
    `        private const int ScrubWidth = 603;
        private const int ScrubHeight = 1311;
        private const int TearSlowMotionScale = 4;`,
    `        // The expected value is the Blender/FBX mesh at the temporal t=0.70 mix.
        public const float SourceExportedFrontFoilDeltaMeters =
            0.0448876022f;
        public const float SourceExportedFrontFoilDeltaToleranceFraction =
            0.005f;
        private const float MinimumMouthMeanRgbDelta = 0.010f;
        private const float MinimumMouthChangedPixelFraction = 0.050f;
        private const int MouthChangedPixelChannelDelta = 8;
        private const int ScrubWidth = Width;
        private const int ScrubHeight = Height;
        private const int TearSlowMotionScale = 4;`,
    "preflight constants"
  );
  source = replaceExactly(
    source,
    `                report.frontFoilMaxBakedDeltaMeters =
                    MaximumVertexDelta(basis.vertices, opened.vertices);
                report.basisStateSetFrame = basisCapture.stateSetFrame;`,
    `                report.frontFoilMaxBakedDeltaMeters =
                    MaximumVertexDelta(basis.vertices, opened.vertices);
                report.sourceExportedExpectedFrontFoilDeltaMeters =
                    SourceExportedFrontFoilDeltaMeters;
                report.frontFoilDeltaToleranceFraction =
                    SourceExportedFrontFoilDeltaToleranceFraction;
                report.frontFoilDeltaRelativeError = RelativeError(
                    report.frontFoilMaxBakedDeltaMeters,
                    SourceExportedFrontFoilDeltaMeters);
                if (!sequence.TryGetMouthViewportBounds(out Rect mouthBounds))
                {
                    throw new InvalidOperationException(
                        "R017 could not project the formed physical mouth.");
                }
                report.mouthScreenVisibility = MeasureMouthScreenVisibility(
                    basisCapture.pixels,
                    openedCapture.pixels,
                    mouthBounds,
                    ScrubWidth,
                    ScrubHeight);
                report.basisStateSetFrame = basisCapture.stateSetFrame;`,
    "preflight measurement"
  );
  source = replaceExactly(
    source,
    `                checks.Add(new CheckResult(
                    "front-foil-baked-delta-at-070-at-least-0045m",
                    report.frontFoilMaxBakedDeltaMeters >= 0.045f,
                    $"maxDelta={report.frontFoilMaxBakedDeltaMeters:F6}m"));
                checks.Add(new CheckResult(
                    "live-case-id-readable-behind-physical-mouth-at-090",`,
    `                checks.Add(new CheckResult(
                    "front-foil-baked-delta-at-070-matches-source-export-within-05-percent",
                    report.frontFoilDeltaRelativeError
                        <= SourceExportedFrontFoilDeltaToleranceFraction,
                    $"actual={report.frontFoilMaxBakedDeltaMeters:F9}m, expected={SourceExportedFrontFoilDeltaMeters:F9}m, relativeError={report.frontFoilDeltaRelativeError:P6}"));
                checks.Add(new CheckResult(
                    "formed-mouth-render-differs-visibly-from-sealed",
                    report.mouthScreenVisibility.meanRgbDelta
                        >= MinimumMouthMeanRgbDelta
                    && report.mouthScreenVisibility.changedPixelFraction
                        >= MinimumMouthChangedPixelFraction,
                    report.mouthScreenVisibility.Summary()));
                checks.Add(new CheckResult(
                    "live-case-id-readable-behind-physical-mouth-at-090",`,
    "preflight checks"
  );
  source = replaceExactly(
    source,
    `        private static void WriteFullReport(
            string path,`,
    `        private static float RelativeError(float actual, float expected)
        {
            return Mathf.Abs(actual - expected)
                / Mathf.Max(Mathf.Epsilon, Mathf.Abs(expected));
        }

        private static MouthScreenVisibility MeasureMouthScreenVisibility(
            IReadOnlyList<Color32> sealedPixels,
            IReadOnlyList<Color32> openedPixels,
            Rect mouthBounds,
            int width,
            int height)
        {
            if (sealedPixels.Count != openedPixels.Count
                || sealedPixels.Count != width * height)
            {
                throw new InvalidOperationException(
                    "R017 mouth visibility frames have mismatched dimensions.");
            }
            Rect region = Rect.MinMaxRect(
                Mathf.Clamp01(mouthBounds.xMin - 0.04f),
                Mathf.Clamp01(mouthBounds.yMin - 0.04f),
                Mathf.Clamp01(mouthBounds.xMax + 0.04f),
                Mathf.Clamp01(mouthBounds.yMax + 0.04f));
            int minX = Mathf.FloorToInt(region.xMin * (width - 1));
            int maxX = Mathf.CeilToInt(region.xMax * (width - 1));
            int minY = Mathf.FloorToInt(region.yMin * (height - 1));
            int maxY = Mathf.CeilToInt(region.yMax * (height - 1));
            float totalDelta = 0f;
            int changed = 0;
            int samples = 0;
            for (int y = minY; y <= maxY; y++)
            {
                for (int x = minX; x <= maxX; x++)
                {
                    int index = y * width + x;
                    Color32 sealedPixel = sealedPixels[index];
                    Color32 openedPixel = openedPixels[index];
                    float delta = (Mathf.Abs(sealedPixel.r - openedPixel.r)
                        + Mathf.Abs(sealedPixel.g - openedPixel.g)
                        + Mathf.Abs(sealedPixel.b - openedPixel.b))
                        / (3f * 255f);
                    totalDelta += delta;
                    if (delta >= MouthChangedPixelChannelDelta / 255f)
                    {
                        changed++;
                    }
                    samples++;
                }
            }
            return new MouthScreenVisibility
            {
                viewportRegion = RectData.From(region),
                sampleCount = samples,
                meanRgbDelta = totalDelta / Mathf.Max(1, samples),
                changedPixelFraction = changed / (float)Mathf.Max(1, samples)
            };
        }

        private static void WriteFullReport(
            string path,`,
    "mouth screen measurement"
  );
  source = replaceExactly(
    source,
    `            public float frontFoilMaxBakedDeltaMeters;
            public int basisStateSetFrame;`,
    `            public float frontFoilMaxBakedDeltaMeters;
            public float sourceExportedExpectedFrontFoilDeltaMeters;
            public float frontFoilDeltaToleranceFraction;
            public float frontFoilDeltaRelativeError;
            public MouthScreenVisibility mouthScreenVisibility;
            public int basisStateSetFrame;`,
    "preflight report fields"
  );
  source = replaceExactly(
    source,
    `        [Serializable]
        private sealed class FrameMetric`,
    `        [Serializable]
        private sealed class MouthScreenVisibility
        {
            public RectData viewportRegion;
            public int sampleCount;
            public float meanRgbDelta;
            public float changedPixelFraction;

            public string Summary()
            {
                return $"region={viewportRegion.Summary()}, samples={sampleCount}, meanRgbDelta={meanRgbDelta:F6}, changedFraction={changedPixelFraction:P3}";
            }
        }

        [Serializable]
        private sealed class FrameMetric`,
    "mouth screen report"
  );
  fs.writeFileSync(capturePath, source, "utf8");

  const testsPath = path.join(
    targetPackage,
    "Tests/Editor/IsolatedR017ProofTests.cs"
  );
  let tests = fs.readFileSync(testsPath, "utf8");
  tests = replaceExactly(
    tests,
    `        [Test]
        public void ImportedRigIsPackOnlyAndPreservesAuthoredPoses()`,
    `        [Test]
        public void PreflightDeltaUsesSourceExportedRelativeTolerance()
        {
            Assert.That(
                IsolatedR017ProofCapture.SourceExportedFrontFoilDeltaMeters,
                Is.GreaterThan(0.04f));
            Assert.That(
                IsolatedR017ProofCapture
                    .SourceExportedFrontFoilDeltaToleranceFraction,
                Is.EqualTo(0.005f));
        }

        [Test]
        public void ImportedRigIsPackOnlyAndPreservesAuthoredPoses()`,
    "focused test"
  );
  tests = replaceExactly(
    tests,
    `            Texture2D artwork = AssetDatabase.LoadAssetAtPath<Texture2D>(
                "Assets/Source/Pack/gacha-pack-standard-body.png");
            Assert.That(artwork, Is.Not.Null);
            Assert.That(artwork.width, Is.EqualTo(384));
            Assert.That(artwork.height, Is.EqualTo(512));
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(`,
    `            Texture2D artwork = AssetDatabase.LoadAssetAtPath<Texture2D>(
                "Assets/Source/Pack/gacha-pack-standard-body.png");
            Assert.That(artwork, Is.Not.Null);
            var sourceArtwork = new Texture2D(
                2,
                2,
                TextureFormat.RGBA32,
                false);
            try
            {
                Assert.That(
                    ImageConversion.LoadImage(
                        sourceArtwork,
                        File.ReadAllBytes(AssetDatabase.GetAssetPath(artwork))),
                    Is.True);
                Assert.That(sourceArtwork.width, Is.EqualTo(384));
                Assert.That(sourceArtwork.height, Is.EqualTo(512));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(sourceArtwork);
            }
            GameObject rig = AssetDatabase.LoadAssetAtPath<GameObject>(`,
    "authored artwork canvas test"
  );
  fs.writeFileSync(testsPath, tests, "utf8");

  const copiedCalibration = path.join(
    targetPackage,
    "Calibration/r017-test-calibration.json"
  );
  fs.mkdirSync(path.dirname(copiedCalibration), { recursive: true });
  fs.copyFileSync(calibrationPath, copiedCalibration, fs.constants.COPYFILE_EXCL);
  writeSourceManifest(calibration, copiedCalibration);
}

requireDirectory(stagingRoot);
requireDirectory(sourceProject);
requireDirectory(sourcePackage);
requireFile(sourceRig);
requireFile(calibrationPath);
const calibration = JSON.parse(fs.readFileSync(calibrationPath, "utf8"));
if (
  calibration.actualTemporalSample.sourceExportedExpectedDeltaMeters
    !== calibration.meshDeltaAssertion.expectedMeters
  || calibration.meshDeltaAssertion.relativeTolerance !== 0.005
) {
  throw new Error("R017 calibration contract is internally inconsistent.");
}
if (
  process.argv.includes("--refresh-manifest")
  || process.argv.includes("--repair-package-guids")
) {
  requireDirectory(targetProject);
  requireDirectory(targetPackage);
  if (process.argv.includes("--repair-package-guids")) {
    regeneratePackageGuids();
  }
  const copiedCalibration = path.join(
    targetPackage,
    "Calibration/r017-test-calibration.json"
  );
  requireFile(copiedCalibration);
  writeSourceManifest(calibration, copiedCalibration);
} else {
  if (fs.existsSync(targetProject)) {
    throw new Error(`Refusing to overwrite isolated R017 project: ${targetProject}`);
  }
  copyR016Project();
  makeR017Package();
  copyRigWithImporterSettings();
  applyPreflightCalibration(calibration);
}
console.log(JSON.stringify({
  isolatedProject: targetProject,
  rigSha256: sha256(targetRig),
  calibrationSha256: sha256(calibrationPath),
  sourceManifest: path.join(targetProject, "r017-source-manifest.json")
}, null, 2));
