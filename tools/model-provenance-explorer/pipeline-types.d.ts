export type StageStatus = "missing" | "blocked" | "draft" | "ready_for_review" | "approved" | "rejected" | "stale" | "legacy";
export type AssetRole = "user-input" | "external-reference" | "ai-target" | "analysis" | "contract" | "process" | "source-model" | "blender-render" | "export" | "unity-render" | "shipping-render" | "validation" | "historical";
export type AssetOrigin = "user-provided" | "assistant-generated" | "external" | "repository-generated" | "unknown-legacy";

export interface AssetRecord {
  id: string;
  stageId: string;
  slot: string;
  path: string;
  sha256: string | null;
  exists?: boolean;
  sizeBytes?: number;
  role: AssetRole;
  producer: { name: string; version: string; recipe?: string; command?: string };
  provenance?: {
    origin: AssetOrigin;
    contentClass: string;
    assertedBy: "user" | "assistant" | "repository" | "legacy-record";
    note?: string;
  };
  sourceAssetIds: string[];
  sourceClaimIds?: string[];
  view?: { id: string; camera: string; parameters?: Record<string, number | string | boolean> };
  reviewState?: "active" | "rejected" | "superseded" | "internal-only";
  supersededBy?: string;
  supersededAt?: string;
  dispositionNote?: string;
  usagePolicy?: string;
  productAnimationEligible?: boolean;
}

export interface Claim {
  id: string;
  stageId: string;
  category: string;
  statement: string;
  confidence: "measured" | "high" | "medium" | "low" | "unknown";
  sourceAssetIds: string[];
  sourceRegions?: Array<{ assetId: string; x: number; y: number; width: number; height: number }>;
  unknowns?: string[];
}

export interface StageRun {
  id: string;
  revision: number;
  status: StageStatus;
  artifactIds: string[];
  validations: Array<{ id: string; status: "pass" | "fail" | "pending"; evidence?: string }>;
  inputDigest?: string;
  outputDigest?: string;
  staleReason?: string;
  decision?: { action: "approve" | "reject"; notes: string; decidedBy: "user"; decidedAt: string };
}

export interface Issue {
  id: string;
  stageId: string;
  assetId: string;
  claimIds: string[];
  severity: "note" | "warning" | "blocker";
  status: "open" | "resolved";
  note: string;
  region: { x: number; y: number; width: number; height: number } | null;
  createdAt: string;
}

export interface DecisionEvent {
  id: string;
  type: string;
  modelId: string;
  manifestRevision: number;
  timestamp: string;
  stageId?: string;
  notes?: string;
  [key: string]: unknown;
}

export interface ReferenceDiscovery {
  status: "not-started" | "pending-stage-2" | "ready-for-stage-2-review" | "approved" | "rejected" | "stale";
  keywords: Array<{ term: string; kind: string; sourceAssetIds: string[] }>;
  queries: Array<{ query: string; language: string; status: string }>;
  candidates: Array<{ id: string; title: string; studio?: string; url: string; matchStatus: string; rationale: string; conflicts?: string[] }>;
  guardrail: string;
}

export interface PipelineManifest {
  schemaVersion: 1;
  revision: number;
  createdAt: string;
  updatedAt: string;
  model: { id: string; name: string; mechanism: string; status: string; scenePath?: string };
  route: { primary: "blender-cli"; rodinPolicy: "concept-only"; note?: string };
  currentState: {
    rebuildRequested: boolean;
    shippingAssetUnchanged: boolean;
    visualApproval: string;
    deviceStatus: string;
    diagnosis?: string;
  };
  assets: AssetRecord[];
  claims: Claim[];
  referenceDiscovery?: ReferenceDiscovery;
  stages: StageRun[];
  issues: Issue[];
}
