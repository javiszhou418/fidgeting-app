# Cursor night supervisor preflight

`preflight.py` is a read-only health snapshot for the overnight Cursor supervisor. It does not call Computer Use, click UI, approve work, start `caffeinate`, or write a report file. It prints deterministic, key-sorted JSON to stdout so the heartbeat can decide whether it is safe to inspect Cursor.

Checks:

- AC power plus both system-sleep and display-sleep assertions from `pmset`;
- repository free space (20 GiB minimum by default);
- `unity/FidgetingApp/Temp/UnityLockfile`;
- status, content hash, and Git diff summary for `pipeline-core.mjs`;
- the latest Cursor session's `terminal*.log` and `ptyhost.log`, or explicitly supplied terminal logs;
- staged, unstaged, untracked, and conflicted working-tree counts.

Run it from any directory:

```sh
python3 tools/cursor-night-supervisor/preflight.py
```

Pass task-specific logs when Cursor or a task writes a dedicated transcript:

```sh
python3 tools/cursor-night-supervisor/preflight.py \
  --terminal-log /absolute/path/to/card-draw-terminal.log \
  --terminal-log /absolute/path/to/mobile-app-terminal.log
```

The default exit code is zero even when JSON reports `blocked`, which keeps monitoring distinct from execution. `--fail-on-blocker` returns 2 for a blocked snapshot. The collector invokes only the fixed `READ_ONLY_COMMANDS` table, disables optional Git locks, bounds log reads to 64 KiB, and never prints log contents.

Focused verification:

```sh
python3 -m unittest discover -s tools/cursor-night-supervisor/tests -v
```

## Slack command bridge

The optional inbound Slack control path is documented in
[`SLACK_COMMAND_BRIDGE.md`](SLACK_COMMAND_BRIDGE.md). It accepts only sanitized,
exactly allowlisted `status`, `pause`, `resume`, and `approve-safe` commands and
does not execute Slack text. Its preferred observation surface is exactly one
dedicated background personal Slack Web tab in Google Chrome profileName
`jiawei`, owned by the `fidgeting-cursor` automation/controller task or handed
back to that same controller from its prior round, and fixed to exact team
`T0C00P256DA`, user `U0BV4S23X8B`, self-DM/sidebar
row `D0C0RELGU56`, client URL
`https://app.slack.com/client/T0C00P256DA/D0C0RELGU56`, workspace display `jw`,
and permalink host `jw-qgi5008.slack.com`. Native Slack desktop and any
Whatnot/whatnot.com Chrome surface are forbidden. The adapter retains the
legacy labels `slack-native-cua`,
`native-from-me-self-dm-verified-user-map-v1`, and `native-pause-only` so the
tested Python schema, append-only cursor, and no-replay runtime remain
unchanged; those labels do not authorize native Slack collection.

Every round's first CUA call is `cua.getState()`. The controller requires one
and only one returned browser with structured `family=chrome`,
`type=extension`, and `profileName=jiawei`, uses that round's dynamic ID to
obtain its browser instance, and calls only that instance's `tabs.list()` or
`tabs.new()`. It never caches/guesses an ID, selects a browser by URL, or calls
the default/high-level `cua.createBrowserTab` API. Gmail/tab titles are not
profile selectors.

After acquiring the round lease, the owner reuses only its own matching
handoff through that instance. If none exists, only that owner may create
exactly one background exact-URL tab with the instance's `tabs.new()` and use
it after an immediate structured profile plus login/URL/workspace/DM
reverification. Root and other tasks must not pre-create or hold it. Another
task's ownership, multiple matching tabs, login/redirect/workspace chooser,
changed browser/profile metadata, or inability to stay background-only fails
closed. Each Slack stage ends by calling `markHandoff` back to the same
controller before any Cursor CUA work.

The legacy-labeled CUA adapter is restricted in code to `status`, `pause`, and
`resume`, uses an explicit observe-only bootstrap plus append-only source
cursor and verified/failed poll receipts, and rejects `approve-safe` because it
cannot prove a trusted real per-message user ID. Its root-state helper remains
a read-only team-to-user check; it does not launch or operate Slack desktop.
Safe clicks require the current round's exact fresh poll ID and exact
team/user/DM/workspace-host binding; refreshing a snapshot cannot refresh that
receipt. A changed Chrome profile/tab/URL, an active user on the dedicated tab,
or any Slack draft fails closed without switching surfaces. The current
automation also lacks the stable
pending-action request-ID producer needed to make `approve-safe` operational on
stronger transports. A fixed-format status reply helper is available, but it
fails closed until the existing webhook's exact team/DM binding is manually
recorded. The automation integration fragment is kept in
[`SLACK_COMMAND_HEARTBEAT_PROMPT.md`](SLACK_COMMAND_HEARTBEAT_PROMPT.md) as the
source contract the all-day scheduler/prompt must match; updating repository
docs alone never mutates the live automation or runtime.

The natural-language extension is documented separately in
[`SLACK_NL_CONTROL.md`](SLACK_NL_CONTROL.md). It adds an enum-only classifier,
static task catalog, fresh-state routing, one-shot claims, protected transient
artifacts, bounded replies, and outbound echo redaction. Its automation
contract runs every five minutes all day: full supervisor at 22:00-07:59, the
existing final read-only morning snapshot at 08:00-08:04, and only the Slack
daytime dialogue pass at 08:05-21:59 (Asia/Shanghai). Empty, app-only, stale,
or duplicate daytime polls never produce a Slack reply. Fresh chat does not
read project state or open Cursor; only fresh status/action requests may
serially refresh the relevant Cursor/Codex state. Daytime never runs overnight
housekeeping, and active or ambiguous UI fails closed. Activation and dry-run
verification did not send or execute a real Slack request.

## Five-state heartbeat dry run

`heartbeat_decision.py` is the pure decision layer between an observed Cursor state and any future Computer Use action. It accepts exactly the five supervisor states and emits a decision; it never imports a UI API or performs the decision.

- `running` → inspect, no click, no notification;
- `safe_pending` → in active `native-pause-only` mode, preserve an otherwise
  allowlisted safe click only when the fresh native control state is valid and
  not paused and a same-round verified poll receipt matches; in future
  `approval-required` mode, return an atomic claim
  requirement for one unexpired Slack approval bound to the exact pending
  action request ID;
- `risky_pending`, `failed`, and `waiting_user` → no click and notify.

`Card draw scene research` is a known target but remains write-disabled at R037. `Mobile app version issue` and `Conversation freezing issue` are write-enabled targets in the overnight supervisor, but the single-writer rule still permits only one active writer at a time. Dry-run one fixture with:

```sh
python3 tools/cursor-night-supervisor/heartbeat_decision.py \
  --fixture tools/cursor-night-supervisor/tests/fixtures/heartbeat/safe_pending.json
```
