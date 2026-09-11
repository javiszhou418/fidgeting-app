#!/usr/bin/env python3
"""Cursor `stop` hook: post each finished agent turn in this workspace to Slack.

Config lives outside the repo in ~/.cursor/slack-progress.env:
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
    SLACK_PROGRESS_STATUSES=completed,error   # optional, default shown

No webhook configured -> exit 0 without posting. The hook never blocks the
agent and never returns a followup_message, so it cannot create a loop.
"""
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ENV_PATH = os.path.expanduser("~/.cursor/slack-progress.env")
LOG_PATH = os.path.expanduser("~/.cursor/slack-progress-hook.log")
STATE_PATH = os.path.expanduser("~/.cursor/slack-progress-state.json")
LOG_MAX_BYTES = 200_000
DEFAULT_STATUSES = "completed,error"
MAX_BODY = 2500
MAX_QUERY = 300
MAX_TITLE = 80
STATUS_LABEL = {"completed": "完成", "error": "出错", "aborted": "已中止"}
SLACK_FORWARD_MARKER = re.compile(
    r'<FIDGETING_SLACK_REQUEST_V1\s+event_id="([A-Za-z0-9._:-]{1,160})"\s+encoding="base64url">'
)
SLACK_FORWARD_LABEL = re.compile(r"^Slack request ([A-Za-z0-9._:-]{1,160})$")


def log(msg):
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > LOG_MAX_BYTES:
            os.remove(LOG_PATH)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def finish():
    sys.stdout.write("{}")
    sys.exit(0)


def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def find_transcript(payload):
    path = payload.get("transcript_path")
    if path and os.path.exists(path):
        return path
    cid = payload.get("conversation_id")
    if not cid:
        return None
    pattern = os.path.expanduser(
        "~/.cursor/projects/*/agent-transcripts/{cid}/{cid}.jsonl".format(cid=cid)
    )
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def iter_text_blocks(message):
    content = message.get("content")
    if isinstance(content, str):
        yield content
        return
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            yield block.get("text", "")


def extract_user_query(text):
    # Forwarded self-DM text is intentionally present only inside the target
    # transcript.  Never reflect it back through this Slack progress hook.
    forwarded = SLACK_FORWARD_MARKER.search(text)
    if forwarded:
        return "Slack request {}".format(forwarded.group(1))
    match = re.search(r"<user_query>\s*(.*?)\s*</user_query>", text, re.S)
    if match:
        return match.group(1).strip()
    # Untagged text is a plain query; anything else is harness context
    # (<timestamp>, <dynamic_tool_catalog>, ...) and must not start a new turn.
    if re.search(r"<\w+>", text):
        return ""
    return text.strip()


def parse_transcript(path):
    """Return (title, last_user_query, final_assistant_text)."""
    title = None
    first_query = None
    last_query = None
    turn_texts = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except ValueError:
                continue
            role = entry.get("role")
            message = entry.get("message") or {}
            if role == "user":
                query = "\n".join(t for t in iter_text_blocks(message) if t)
                query = extract_user_query(query)
                if query:
                    last_query = query
                    if first_query is None:
                        first_query = query
                    turn_texts = []
            elif role == "assistant":
                content = message.get("content") or []
                if isinstance(content, list):
                    for block in content:
                        if (
                            isinstance(block, dict)
                            and block.get("type") == "tool_use"
                            and block.get("name") == "CallDynamicTool"
                        ):
                            args = (block.get("input") or {})
                            if args.get("toolName") == "rename_chat":
                                name = (args.get("arguments") or {}).get("name")
                                if name:
                                    title = name
                texts = [t for t in iter_text_blocks(message) if t and t.strip()]
                if texts:
                    turn_texts.append("\n".join(texts))
    final_text = turn_texts[-1] if turn_texts else ""
    fallback_title = (first_query or "").strip().splitlines()[0] if first_query else ""
    return title or fallback_title, last_query or "", final_text


def read_turn(path, status, attempts=3, delay=1.0):
    """Re-read briefly when the final assistant text is not flushed yet."""
    title, query, body = parse_transcript(path)
    for _ in range(attempts - 1):
        if body or status != "completed":
            break
        time.sleep(delay)
        title, query, body = parse_transcript(path)
    return title, query, body


def truncate(text, limit):
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 8].rstrip() + "…（已截断）"


def md_to_mrkdwn(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"```[^\n]*\n", "```\n", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+(.+)$", r"*\1*", text, flags=re.M)
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    text = re.sub(r"^(\s*)[-*]\s+", r"\1• ", text, flags=re.M)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"<\2|\1>", text)
    return text


def build_slack_payload(project, title, status, query, body, meta):
    label = STATUS_LABEL.get(status, status)
    title = truncate(title or "（未命名对话）", MAX_TITLE)
    query = truncate(query or "（无）", MAX_QUERY)
    if SLACK_FORWARD_LABEL.fullmatch(query):
        # The assistant may quote the forwarded request, so suppress its body
        # as well as the query.  The fixed event ID is enough for correlation.
        body = "Slack 转发请求已处理；内容已从通知中隐藏。"
    else:
        body = truncate(body or "（本轮没有文本输出）", MAX_BODY)
    fallback = "[{project}] {title} · {label}\n{body}".format(
        project=project, title=title, label=label, body=body
    )
    return {
        "text": fallback[:3000],
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "{} · Agent 进展".format(project)[:150]},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*对话*\n" + md_to_mrkdwn(title)},
                    {"type": "mrkdwn", "text": "*状态*\n" + label},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*最近指令*\n" + md_to_mrkdwn(query)},
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": md_to_mrkdwn(body)[:3000]}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": meta}]},
        ],
    }


def already_posted(generation_id):
    if not generation_id:
        return False
    state = {}
    try:
        with open(STATE_PATH, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = {}
    if generation_id in state.get("posted", []):
        return True
    posted = (state.get("posted", []) + [generation_id])[-200:]
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump({"posted": posted}, fh)
    except OSError:
        pass
    return False


def post(url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read(200).decode("utf-8", "replace")


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        log("invalid stdin json")
        finish()

    status = payload.get("status", "completed")
    env = load_env(os.environ.get("SLACK_PROGRESS_ENV", ENV_PATH))
    webhook = env.get("SLACK_WEBHOOK_URL") or os.environ.get("SLACK_WEBHOOK_URL", "")
    allowed = {
        s.strip()
        for s in (env.get("SLACK_PROGRESS_STATUSES") or DEFAULT_STATUSES).split(",")
        if s.strip()
    }

    if not webhook:
        log("skip: SLACK_WEBHOOK_URL not set in {}".format(ENV_PATH))
        finish()
    if status not in allowed:
        log("skip: status {} not in {}".format(status, sorted(allowed)))
        finish()
    if already_posted(payload.get("generation_id")):
        log("skip: generation {} already posted".format(payload.get("generation_id")))
        finish()

    roots = payload.get("workspace_roots") or []
    project = os.path.basename(roots[0].rstrip("/")) if roots else "Cursor"
    transcript = find_transcript(payload)
    title, query, body = ("", "", "")
    if transcript:
        try:
            title, query, body = read_turn(transcript, status)
        except OSError as exc:
            log("transcript read failed: {}".format(exc))
    else:
        log("transcript not found for conversation {}".format(payload.get("conversation_id")))

    cid = (payload.get("conversation_id") or "")[:8]
    meta = " · ".join(
        part
        for part in (
            time.strftime("%Y-%m-%d %H:%M"),
            payload.get("model") or "",
            "conversation {}".format(cid) if cid else "",
        )
        if part
    )
    slack_payload = build_slack_payload(project, title, status, query, body, meta)
    try:
        code, text = post(webhook, slack_payload)
        log("posted status={} http={} {}".format(status, code, text.strip()))
    except urllib.error.HTTPError as exc:
        log("slack http error {}: {}".format(exc.code, exc.read(200).decode("utf-8", "replace")))
    except Exception as exc:  # network errors must never block the agent
        log("slack post failed: {!r}".format(exc))
    finish()


if __name__ == "__main__":
    main()
