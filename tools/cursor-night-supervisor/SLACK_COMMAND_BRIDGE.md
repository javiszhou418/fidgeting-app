# Slack ↔ Cursor local command bridge

This MVP adds a narrow inbound control path beside the existing outbound
`.cursor/hooks/slack-progress.py` notification hook. The two directions are
deliberately independent: the inbound bridge never reads the existing Incoming
Webhook URL and never posts a Slack message.

Natural-language self-DM routing is a separate, currently disabled layer. See
[`SLACK_NL_CONTROL.md`](SLACK_NL_CONTROL.md); rejected `fidget…` messages never
fall through to it, and it does not weaken the exact-command rules below.

Do not infer that the two directions use the same Slack workspace or
conversation. A full round trip is not enabled until the inbound team and
conversation IDs and the outbound notification destination are explicitly
verified to match the intended user experience.

## Ingress paths and current boundary

There are two contracts. A Slack connector or Socket Mode event that exposes a
real per-message `user_id` may pass one event to
`.cursor/hooks/slack_command_bridge.py`. Native Slack CUA cannot expose that
per-message ID, so it must use the more restricted batch adapter
`.cursor/hooks/slack_command_cua_ingest.py`. Neither path needs a public
callback URL, and no persistent process is started by this repository.

The single-event connector/Socket Mode schema is:

Only these input keys are accepted:

```json
{
  "schemaVersion": "1.0",
  "team_id": "T…",
  "user_id": "U…",
  "conversation_id": "D… or C… or G…",
  "event_id": "Ev…",
  "message_ts": "1788782395.000001",
  "text": "fidget status"
}
```

`schemaVersion` is mandatory. `event_id` may be omitted when the connector does
not return one; the bridge
then derives a stable SHA-256 identifier from team, conversation, and message
timestamp. A supplied malformed `event_id` is rejected, never silently
replaced. All other fields are required. Age is calculated from Slack's
`message_ts`, never from local ingestion time. `status` is accepted for at most
15 minutes; `pause`, `resume`, and `approve-safe` are accepted for at most five
minutes. Messages more than one minute in the future are rejected.

The runtime allowlist is exact and fail-closed:

- `FIDGETING_SLACK_ALLOWED_TEAM_ID`
- `FIDGETING_SLACK_ALLOWED_USER_ID`
- `FIDGETING_SLACK_ALLOWED_CONVERSATION_ID`
- `FIDGETING_SLACK_ALLOWED_WORKSPACE_HOST` (native CUA only)

The same values can be supplied as `--allowed-team-id`, `--allowed-user-id`,
and `--allowed-conversation-id`. These Slack IDs are not access tokens. Do not
place a Slack token, webhook URL, message body, or display name in an allowlist
field. Native CUA additionally requires `--allowed-workspace-host`; its exact
value is bound into every poll digest and receipt.

The concrete IDs below are non-secret runtime examples, not code defaults:

- team `T0C00P256DA`;
- user `U0BV4S23X8B`;
- self-DM `D0C0RELGU56`.
- workspace host `jw-qgi5008.slack.com`.

## Native Slack CUA batch contract

Native CUA provenance is indirect. The team/workspace URL, exact self-DM
timeline/permalinks, and the sender shown on each self-message row must all
agree. Slack search is not a completeness proof and must not be used for this
scan. Slack's native UI does **not** expose a
per-message `user_id`; `user_id` is therefore inferred only after separately
checking the local root-state mapping
`webapp.teams.T0C00P256DA.userId == U0BV4S23X8B`. The batch field
`authorProof=native-from-me-self-dm-verified-user-map-v1` is a local caller
attestation, not a signature or cryptographic proof. Any missing, ambiguous, or
conflicting evidence means: build no batch and do not advance the cursor.

The fixed helper below accepts only Slack Desktop's canonical local
`root-state.json` path and extracts only that one mapping after parsing. It
never accesses token/cookie fields, serializes the root object, or uses
`selectedUserId`:

```sh
python3 .cursor/hooks/slack_native_identity.py \
  --team-id T0C00P256DA \
  --expected-user-id U0BV4S23X8B
```

Before the first poll, perform an explicit observe-only bootstrap. Use the
newest verified stable self-DM permalink's Slack `message_ts`; do not ingest
history on activation. The latest verified value at the time this contract was
written was `1788840299.185749`, but it is an example only and is deliberately
not hardcoded:

```sh
python3 .cursor/hooks/slack_command_cua_ingest.py \
  --allowed-team-id T0C00P256DA \
  --allowed-user-id U0BV4S23X8B \
  --allowed-conversation-id D0C0RELGU56 \
  --allowed-workspace-host jw-qgi5008.slack.com \
  bootstrap \
  --cursor 1788840299.185749 \
  --author-proof native-from-me-self-dm-verified-user-map-v1
```

Bootstrap writes one append-only `source-bootstrap` record with
`activationCutoff=cursor` and `eventCount=0`; it queues no command. A different
second bootstrap is refused. Read the current cursor with:

```sh
python3 .cursor/hooks/slack_command_cua_ingest.py \
  --allowed-team-id T0C00P256DA \
  --allowed-user-id U0BV4S23X8B \
  --allowed-conversation-id D0C0RELGU56 \
  --allowed-workspace-host jw-qgi5008.slack.com \
  cursor
```

Each later poll submits one exact batch object to the `ingest` subcommand:

```json
{
  "schemaVersion": "1.0",
  "source": {
    "kind": "slack-native-cua",
    "team_id": "T0C00P256DA",
    "user_id": "U0BV4S23X8B",
    "conversation_id": "D0C0RELGU56",
    "workspace_host": "jw-qgi5008.slack.com",
    "authorProof": "native-from-me-self-dm-verified-user-map-v1"
  },
  "baseObservedThrough": "1788840299.185749",
  "observedThrough": "1788840307.000003",
  "pollProof": {
    "pollId": "poll_EXAMPLE01",
    "result": "verified",
    "anchorSeen": true,
    "chronologyComplete": true,
    "stableBottomSeen": true
  },
  "rows": [
    {
      "message_ts": "1788840305.000001",
      "kind": "self-message",
      "permalink": "https://jw-qgi5008.slack.com/archives/D0C0RELGU56/p1788840305000001"
    },
    {
      "message_ts": "1788840306.000002",
      "kind": "app-message",
      "permalink": "https://jw-qgi5008.slack.com/archives/D0C0RELGU56/p1788840306000002"
    },
    {
      "message_ts": "1788840307.000003",
      "kind": "app-message-group-continuation",
      "permalink": "https://jw-qgi5008.slack.com/archives/D0C0RELGU56/p1788840307000003"
    }
  ],
  "events": [
    {
      "schemaVersion": "1.0",
      "team_id": "T0C00P256DA",
      "user_id": "U0BV4S23X8B",
      "conversation_id": "D0C0RELGU56",
      "message_ts": "1788840305.000001",
      "text": "fidget status"
    }
  ]
}
```

Use the exact DM timeline, not Slack search. The stored base permalink must be
visible, and the collector must scan continuously from that anchor through
every later top-level row to a stable bottom, including virtualized/paginated
rows. Every row is classified as `self-message` (visible Jiawei sender), direct
`app-message` (visible app sender plus `应用` marker), or the closed
`app-message-group-continuation` attestation. The continuation kind is allowed
only when its immediately preceding row in the same batch is a direct
`app-message`, and CUA simultaneously sees both rows as adjacent members of the
same Slack render/AX group in one uninterrupted exact-DM viewport. It cannot be
the first row, anchor across polls/loads, follow a self row, or chain from another
continuation. The adapter and authoritative store independently enforce that
sequence. Each self row has exactly one event; both app kinds have none, so
app/webhook text is never serialized into the batch or ingested by the bridge.
The heartbeat's CUA/LLM observation layer may nevertheless see rendered/AX app
body text; it is untrusted inert display data and cannot influence
classification, action, reply, or any other decision, nor be copied into a
downstream model prompt or ledger. Any gap, missing anchor, unresolved load
state, sender/app-marker/group ambiguity, edit, thread, quote, forward,
attachment, or code preview fails the entire poll.

`baseObservedThrough` is an exact compare-and-swap value. Rows must be strictly
ordered in `(baseObservedThrough, observedThrough]`, and the last row must equal
`observedThrough`. The source cursor advances only after all event/audit
records are durable, and the verified poll receipt is appended after the
cursor. A crash retry with the same poll ID and digest heals a missing receipt
without replaying commands. A complete poll with no new rows uses empty
`rows`/`events` and `observedThrough == baseObservedThrough`; it creates a fresh
verified receipt without moving the cursor.

If the exact-DM scan or identity proof fails, record the round as failed without
moving the cursor:

```sh
python3 .cursor/hooks/slack_command_cua_ingest.py \
  --allowed-team-id T0C00P256DA \
  --allowed-user-id U0BV4S23X8B \
  --allowed-conversation-id D0C0RELGU56 \
  --allowed-workspace-host jw-qgi5008.slack.com \
  poll-failure \
  --poll-id poll_EXAMPLE02 \
  --base-observed-through 1788840299.185749 \
  --reason chronology-ambiguous
```

Failure receipts are append-only and supersede a recent success for the
heartbeat gate.

Because CUA lacks real per-message identity, its adapter accepts only
`status`, `pause`, and `resume`. It rejects `approve-safe` in code even when the
attested IDs and text match. `approve-safe` remains available only to
connector/Socket Mode events carrying Slack's real `user_id`. A delayed native
`pause` after the activation cutoff still applies because it only narrows
authority and the monotonic row chain prevents pre-bootstrap replay. Native
`resume` remains limited to five minutes because it restores authority.

## Exact command grammar

The complete transport-neutral language is below. Native CUA is intentionally
restricted to the first three commands:

- `fidget status`
- `fidget pause`
- `fidget resume`
- `fidget approve-safe safe_ABCDE1` (example)

Matching is case-sensitive after trimming outer whitespace. The approval
request ID must match `^safe_[A-Za-z0-9]{5,32}$` and must be the exact
`approvalRequestId` displayed by the currently pending Cursor action. Bare
`fidget approve-safe`, other arguments, mentions, shell syntax,
natural-language prefixes, message edits, bot messages, and thread replies are
rejected. Rejected text is never copied into a log; only its SHA-256 and length
are audited.

Command meaning:

- `status`: request one read-only supervisor snapshot. It expires after 15
  minutes and is acknowledged only after the status was actually reported.
- `pause`: immediately sets the derived local control state to paused. It does
  not change or disable the Codex automation itself.
- `resume`: clears that local pause state.
- `approve-safe`: a five-minute, one-action request bound to one exact request
  ID. Its expiry is `message_ts + 5 minutes`, so delayed ingestion never extends
  it. It never makes an action safe. The current observation must expose the
  same `approvalRequestId`, and the existing task/title, preflight, command
  allowlist, UI-control, and post-click verification gates must all pass. A
  missing, expired, malformed, or mismatched ID means no click and terminal
  refusal; the request is never kept as permission for a future action. It
  cannot approve a model Gate, visual direction, device action, Git operation,
  installation, credential change, or arbitrary shell command.

The current heartbeat observation pipeline does not yet generate and persist a
stable `approvalRequestId` for a pending Cursor action. Therefore
`approve-safe` is not operational in the current automation even on the
stronger connector/Socket Mode transport. Do not enable its click path until a
separately tested producer exposes the same stable ID before claim, immediately
before click, and during finalization.

## Local durability model

The default runtime directory is
`.cursor/runtime/slack-command-bridge/`, with mode `0700`. Runtime files use
mode `0600`:

- `commands.ndjson`: append-only accepted-command queue;
- `audit.ndjson`: append-only accepted/rejected/duplicate and transport audit;
- `consumption.ndjson`: append-only terminal outcomes;
- `status-delivery.ndjson`: append-only structured status delivery outcomes;
- `source-cursors.ndjson`: authoritative append-only native-source bootstrap
  and cursor chain;
- `source-polls.ndjson`: authoritative append-only native verified/failed poll
  receipts with exact policy, workspace host, observation boundary, and digest;
- `source-cursor.json`: atomically replaced native-source cursor cache;
- `control-state.json`: atomically replaced, fully derived state cache;
- `.lock`: cross-process `flock` lock.

The append-only ledgers are authoritative. Every append is made with
`O_APPEND`, flushed with `fsync`, and protected by the same process lock. The
derived state is written to a same-directory temporary file, `fsync`ed, and
atomically renamed. Dedupe is rebuilt from the ledgers, so a stale or missing
state cache cannot replay a command. Command, audit, consumption, delivery,
source-cursor, and source-poll corruption is never skipped: readers fail closed, and the
heartbeat must perform no UI action until the ledgers are repaired from trusted
evidence.

## Offline operation

Evaluate a sanitized event without making files or contacting Slack:

```sh
python3 .cursor/hooks/slack_command_bridge.py \
  --dry-run \
  --input /absolute/path/to/sanitized-event.json \
  --allowed-team-id T… \
  --allowed-user-id U… \
  --allowed-conversation-id D…
```

Inspect pending commands and logical pause state:

```sh
python3 .cursor/hooks/slack_command_consumer.py snapshot
```

The pure heartbeat decision layer accepts the generated state cache as a
fail-closed input. Active native mode must also bind the exact policy, workspace
host, and current-round poll ID:

```sh
python3 tools/cursor-night-supervisor/heartbeat_decision.py \
  --fixture /absolute/path/to/current-observation.json \
  --control-state .cursor/runtime/slack-command-bridge/control-state.json \
  --slack-control-mode native-pause-only \
  --slack-poll-id poll_EXAMPLE01 \
  --slack-allowed-team-id T0C00P256DA \
  --slack-allowed-user-id U0BV4S23X8B \
  --slack-allowed-conversation-id D0C0RELGU56 \
  --slack-allowed-workspace-host jw-qgi5008.slack.com
```

In active `native-pause-only` mode, a click requires a structurally valid state
and a matching, cursor-consistent, verified receipt no more than 60 seconds old.
`paused=true`, stale/malformed state, missing or mismatched policy/poll ID,
failed/stale receipt, cursor inconsistency, or a ledger read error blocks the
click. Calling `snapshot` never refreshes the append-only receipt. With all
gates valid, `paused=false` preserves the supervisor's pre-existing
task/preflight/command allowlist decision. Native CUA cannot add approval
authority. The stronger
future `approval-required` mode additionally needs an unexpired entry whose
`requestId` exactly equals the observed pending action's
`approvalRequestId`; that mode is not operational until a stable action-ID
producer exists. Neither mode suppresses risky, failed, or waiting-user
notifications.

Append a terminal result only after the heartbeat verifies the result:

```sh
python3 .cursor/hooks/slack_command_consumer.py ack \
  --event-id Ev… \
  --outcome reported
```

Valid outcomes are deliberately command-specific. For example, `status`
cannot be acknowledged as `applied`, and `approve-safe` cannot be acknowledged
as `reported`. A matching approval is never acknowledged directly as applied.
It must first be atomically claimed:

```sh
python3 .cursor/hooks/slack_command_consumer.py claim \
  --event-id Ev… \
  --request-id safe_ABCDE1
```

Only a successful claim permits the heartbeat to re-check the same visible
request ID and perform the one indicated control. The claim immediately removes
the approval from future snapshots, so a crash before or after the click cannot
replay it. After post-click verification, append the final result:

```sh
python3 .cursor/hooks/slack_command_consumer.py finalize \
  --event-id Ev… \
  --request-id safe_ABCDE1 \
  --outcome applied
```

Use `--outcome refused` when the claimed click is aborted or cannot be verified.
The decision output lists every unused approval under
`slackControl.refuseApprovalEventIds`; the heartbeat must acknowledge each of
those event IDs as `refused` before its next observation.

## Structured `status` reply

`.cursor/hooks/slack_status_reply.py` is a narrow optional reply helper. It
reuses only `SLACK_WEBHOOK_URL` from the existing
`~/.cursor/slack-progress.env`; that home config does not need to change. A
real post also requires the workspace-owned destination attestation
`tools/cursor-night-supervisor/slack-status-destination.json`:

```json
{
  "schemaVersion": "1.0",
  "teamId": "T0C00P256DA",
  "conversationId": "D0C0RELGU56",
  "verifiedAt": "2026-09-08T04:27:24Z",
  "evidenceCode": "verified-outgoing-self-dm-permalink-v1",
  "webhookSha256": "14b6056eb7efe3de2cdc0044cd8ff9bd15d5beb3b7914c107eb6e81e66baeb3d"
}
```

That non-secret file records the independently verified outgoing permalink's
team and self-DM without storing the permalink or webhook. `webhookSha256` is
the SHA-256 of the exact normalized `SLACK_WEBHOOK_URL`; the helper hashes the
current env value locally and requires an exact match before any post or
delivery acknowledgement. A missing, malformed, wrong-webhook, or mismatched
attestation blocks delivery without printing either URL.

The helper accepts exactly one structured object—no title, message, body, link,
or arbitrary Slack text:

```json
{
  "schemaVersion": "1.0",
  "requestEventId": "Ev-status-001",
  "state": "safe-pending",
  "paused": false,
  "safeActionPending": true,
  "riskyActionPending": false,
  "pendingStatusCount": 1,
  "pendingApprovalCount": 0,
  "blockingCode": "none",
  "observedAt": "2026-09-08T00:00:00Z"
}
```

States, blocking codes, booleans, and counts are validated against fixed sets;
the Slack message itself is built from fixed labels. The observation may be at
most 120 seconds old. The request ID must name one live, unexpired queued
`status` command. `--dry-run` performs no network request or delivery audit;
`--send` posts once to the pinned `hooks.slack.com` host. The webhook URL is
never printed or audited.

```sh
python3 .cursor/hooks/slack_status_reply.py \
  --input /absolute/path/to/structured-status.json \
  --runtime-root .cursor/runtime/slack-command-bridge \
  --allowed-team-id T0C00P256DA \
  --allowed-user-id U0BV4S23X8B \
  --allowed-conversation-id D0C0RELGU56 \
  --send
```

Only `ackAllowed=true` means a successful HTTP response has already been
fsync'ed to `status-delivery.ndjson`. The consumer independently refuses
`ack --outcome reported` without that success record. Failures remain pending
for a later retry. A process crash after Slack accepts a webhook but before the
local audit append can still cause one duplicate on retry because Incoming
Webhooks provide no idempotency key; the request ID remains stable for manual
deduplication.

## Optional Socket Mode transport

`.cursor/hooks/slack_command_socket_mode.py` is an optional foreground adapter
for environments without the connector. It has no default start behavior and
requires an explicit `--run`. It reduces Slack envelopes to the same sanitized
schema, persists the decision before acknowledging the envelope, reconnects
with bounded exponential backoff, and honors HTTP 429 `Retry-After`. Exception
messages and ticketed WebSocket URLs are not logged.

It needs:

- an app-level `xapp-…` token in `SLACK_COMMAND_APP_TOKEN`, with
  `connections:write`;
- Socket Mode enabled;
- the app installed in the target workspace;
- one bot event subscription and matching read scope:
  - 1:1 App Home/DM: `message.im` + `im:history`;
  - public channel: `message.channels` + `channels:history`;
  - private channel: `message.groups` + `groups:history`.

The adapter itself does not use an `xoxb-…` bot token and does not need
`chat:write`, because it never posts a message. The app installation may still
issue a bot token; do not add it to this bridge unless a later, separately
reviewed feature truly requires it.

Dry-run validates configuration and the optional `websockets` dependency but
does not open a network connection or create runtime files:

```sh
SLACK_COMMAND_APP_TOKEN='xapp-…' \
python3 .cursor/hooks/slack_command_socket_mode.py \
  --dry-run \
  --allowed-team-id T… \
  --allowed-user-id U… \
  --allowed-conversation-id D…
```

Official Slack references:

- https://docs.slack.dev/apis/events-api/using-socket-mode/
- https://docs.slack.dev/reference/methods/apps.connections.open/
- https://docs.slack.dev/reference/scopes/connections.write/
- https://docs.slack.dev/reference/events/message.im/
- https://docs.slack.dev/reference/events/message/
- https://docs.slack.dev/apis/web-api/rate-limits/

## Verification

All tests are offline and use synthetic IDs and messages:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tools.cursor-night-supervisor.tests.test_slack_command_bridge -v
```

The full existing supervisor suite remains:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tools/cursor-night-supervisor/tests -v
```
