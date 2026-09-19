"""Post messages to Slack channels via a bot token (chat.postMessage).

Uses a bot token rather than an incoming webhook: a webhook is locked to a
single channel at creation time, while a bot token lets any caller pick the
channel per call — one credential, any channel.

One-time Slack-side setup (you're the workspace admin, so all of this is
available to you):
1. Create an app at https://api.slack.com/apps > "Create New App" > "From
   scratch". Name + workspace, that's it.
2. Under "OAuth & Permissions" > "Scopes" > "Bot Token Scopes", add
   `chat:write`. Add `chat:write.public` too if you want to post to public
   channels without inviting the bot to them first (saves a step per
   channel while experimenting).
3. "Install to Workspace" (top of the OAuth & Permissions page), approve,
   then copy the "Bot User OAuth Token" — starts with `xoxb-`.
4. Unless you added `chat:write.public`: invite the bot to each channel
   you'll post to, with `/invite @your-app-name` typed in that channel.
5. Drop the token into config_secrets.yml under `api_keys.slack.bot_token`
   — see config_secrets_template.yml for the shape.

`channel` takes a channel ID (e.g. "C0123456789") or a name the bot can
resolve (e.g. "#general" or "general"); IDs are more reliable and what
Slack itself recommends once you're past quick experiments — find one by
right-clicking a channel > "View channel details" > bottom of the panel.
"""

from __future__ import annotations

from pathlib import Path

import requests
import yaml

_SECRETS_PATH = Path(__file__).resolve().parent.parent / "config_secrets.yml"
_POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"


def load_bot_token() -> str | None:
    if not _SECRETS_PATH.exists():
        print(f"Warning: {_SECRETS_PATH.name} not found; see config_secrets_template.yml.")
        return None
    secrets = yaml.safe_load(_SECRETS_PATH.read_text()) or {}
    token = secrets.get("api_keys", {}).get("slack", {}).get("bot_token")
    if not token:
        print("Warning: no Slack bot token set in config_secrets.yml (api_keys.slack.bot_token).")
    return token


def send_message(
    channel: str,
    text: str,
    *,
    blocks: list[dict] | None = None,
    thread_ts: str | None = None,
    token: str | None = None,
) -> dict:
    """Post a message to a Slack channel. Returns Slack's response payload.

    `text` is required by Slack even when `blocks` is set — it's the
    fallback shown in notifications/previews. Pass `blocks` on top of it
    for richer formatting (https://app.slack.com/block-kit-builder is the
    easiest way to design those). `thread_ts` (a parent message's `ts`
    from a prior response) replies in a thread instead of posting
    top-level.
    """
    token = token or load_bot_token()
    if not token:
        raise RuntimeError(
            "No Slack bot token available; see shared/slack.py docstring for setup."
        )

    payload: dict = {"channel": channel, "text": text}
    if blocks is not None:
        payload["blocks"] = blocks
    if thread_ts is not None:
        payload["thread_ts"] = thread_ts

    response = requests.post(
        _POST_MESSAGE_URL,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(f"Slack API error: {result.get('error')}")
    return result
