"""OpenCLI source provider for user-authorized local/browser session signals."""
from __future__ import annotations

import json
import shutil
import subprocess
from hashlib import sha1
from typing import Any

from multi_agent_brief.sources.base import SourceItem, SourceProvider, SourceQuery

OPENCLI_DEFAULT_TIMEOUT = 60

READ_ONLY_COMMANDS: dict[str, set[str]] = {
    "bilibili": {
        "dynamic", "feed-detail", "following", "me", "ranking", "search",
        "subtitle", "summary", "video", "comments", "user-videos",
    },
    "youtube": {
        "channel", "comments", "feed", "history", "playlist", "search",
        "subscriptions", "transcript", "video", "watch-later",
    },
    "zhihu": {
        "answer-comments", "answer-detail", "collection", "collections",
        "download", "hot", "question", "recommend", "search",
    },
    "xiaohongshu": {
        "search", "note", "comments", "notifications", "feed", "user",
        "creator-notes", "creator-note-detail", "creator-notes-summary",
        "creator-profile", "creator-stats",
    },
    "reddit": {
        "hot", "frontpage", "popular", "search", "subreddit", "read",
        "user", "user-posts", "user-comments", "saved", "upvoted",
    },
    "twitter": {
        "trending", "search", "timeline", "tweets", "lists", "list-tweets",
        "bookmarks", "profile", "thread", "following", "followers",
        "notifications", "likes", "article",
    },
}

WRITE_LIKE_COMMANDS = {
    "answer", "comment", "favorite", "follow", "like", "post", "publish",
    "reply", "subscribe", "unfollow", "unlike", "unsubscribe", "delete",
    "block", "unblock", "save", "upvote",
}


class OpenCliProvider(SourceProvider):
    """Collect source items by running configured read-only OpenCLI adapters.

    Example ``sources.yaml``:

    .. code-block:: yaml

        source_strategy:
          enabled_providers: [manual, opencli]
        opencli:
          enabled: true
          commands:
            - name: zhihu-hot
              site: zhihu
              command: hot
              args: ["--limit", "5"]
            - name: youtube-search
              site: youtube
              command: search
              query_from_keywords: true
              args: ["--limit", "5"]
    """

    name = "opencli"
    source_type = "cli"

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        if not config.get("enabled"):
            return []

        errors: list[str] = []
        if not shutil.which("opencli"):
            errors.append("opencli: command 'opencli' not found in PATH")

        commands = config.get("commands", [])
        if not commands:
            errors.append("opencli: enabled but no commands configured")
            return errors

        for index, command_config in enumerate(commands):
            label = command_config.get("name", f"commands[{index}]")
            site = str(command_config.get("site", "")).strip()
            command = str(command_config.get("command", "")).strip()

            if not site:
                errors.append(f"opencli.{label}: missing 'site'")
            if not command:
                errors.append(f"opencli.{label}: missing 'command'")
            if command and not self._is_read_only(site, command, config):
                errors.append(
                    f"opencli.{label}: command '{site} {command}' is not in the read-only allowlist"
                )
        return errors

    def collect(self, query: SourceQuery, config: dict[str, Any]) -> list[SourceItem]:
        if not config.get("enabled"):
            return []

        items: list[SourceItem] = []
        for command_config in config.get("commands", []):
            if command_config.get("enabled", True) is False:
                continue
            try:
                items.extend(self._run_command(command_config, query, config))
            except Exception:
                continue
        return items

    def _is_read_only(self, site: str, command: str, config: dict[str, Any]) -> bool:
        if command in WRITE_LIKE_COMMANDS:
            return False
        extra = config.get("allowed_commands", {})
        if isinstance(extra, dict):
            configured = set(str(c) for c in extra.get(site, []))
            if command in configured:
                return True
        return command in READ_ONLY_COMMANDS.get(site, set())

    def _run_command(
        self,
        command_config: dict[str, Any],
        query: SourceQuery,
        config: dict[str, Any],
    ) -> list[SourceItem]:
        site = str(command_config.get("site", "")).strip()
        command = str(command_config.get("command", "")).strip()
        name = str(command_config.get("name") or f"{site}-{command}")
        timeout = int(command_config.get("timeout", config.get("timeout", OPENCLI_DEFAULT_TIMEOUT)))

        if not site or not command or not self._is_read_only(site, command, config):
            return []

        args = [str(arg) for arg in command_config.get("args", [])]
        if command_config.get("query_from_keywords") and query.keywords:
            args.insert(0, " ".join(query.keywords))

        if "-f" not in args and "--format" not in args:
            args.extend(["-f", "json"])

        cmd = ["opencli", site, command, *args]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            return [self._error_item(name, site, command, result.returncode, result.stderr or result.stdout)]

        stdout = (result.stdout or "").strip()
        if not stdout:
            return []

        data = self._parse_json_prefix(stdout)
        if data is None:
            return [self._text_item(name, site, command, stdout, command_config)]

        records = data if isinstance(data, list) else [data]
        items: list[SourceItem] = []
        for index, record in enumerate(records):
            if isinstance(record, dict):
                items.append(self._dict_item(name, site, command, index, record, command_config))
            else:
                items.append(self._text_item(name, site, command, str(record), command_config, index=index))
        return items

    def _parse_json_prefix(self, stdout: str) -> Any | None:
        text = stdout.strip()
        try:
            value, _ = json.JSONDecoder().raw_decode(text)
            return value
        except json.JSONDecodeError:
            return None

    def _dict_item(
        self,
        name: str,
        site: str,
        command: str,
        index: int,
        record: dict[str, Any],
        command_config: dict[str, Any],
    ) -> SourceItem:
        title = str(record.get("title") or record.get("name") or record.get("question") or f"{name} item {index + 1}")[:200]
        content = str(
            record.get("content")
            or record.get("body")
            or record.get("text")
            or record.get("summary")
            or json.dumps(record, ensure_ascii=False)
        )[:8000]
        url = str(record.get("url") or record.get("link") or "")
        published_at = str(record.get("published_at") or record.get("date") or record.get("publishedAt") or "")
        dedupe_key = f"opencli_{site}_{command}_{sha1((url or title + content).encode()).hexdigest()[:12]}"

        return SourceItem(
            source_id=f"opencli_{sha1((dedupe_key + str(index)).encode()).hexdigest()[:12]}",
            source_name=f"OpenCLI: {name}",
            source_type="cli",
            title=title,
            content=content,
            url=url,
            published_at=published_at,
            reliability=str(command_config.get("reliability", "medium")),
            dedupe_key=dedupe_key,
            metadata={
                "backend": "opencli",
                "site": site,
                "command": command,
                "adapter": name,
                "index": index,
                "access_level": command_config.get("access_level", "user_authorized"),
                "source_family": command_config.get("source_family", "private_signal"),
                "evidence_quality": command_config.get("evidence_quality", "browser_or_adapter_output"),
            },
        )

    def _text_item(
        self,
        name: str,
        site: str,
        command: str,
        text: str,
        command_config: dict[str, Any],
        *,
        index: int = 0,
    ) -> SourceItem:
        title = f"OpenCLI {site} {command}: {name}"
        content = text[:8000]
        dedupe_key = f"opencli_{site}_{command}_{sha1(content.encode()).hexdigest()[:12]}"
        return SourceItem(
            source_id=f"opencli_{sha1((dedupe_key + str(index)).encode()).hexdigest()[:12]}",
            source_name=f"OpenCLI: {name}",
            source_type="cli",
            title=title,
            content=content,
            reliability=str(command_config.get("reliability", "medium")),
            dedupe_key=dedupe_key,
            metadata={
                "backend": "opencli",
                "site": site,
                "command": command,
                "adapter": name,
                "index": index,
                "access_level": command_config.get("access_level", "user_authorized"),
                "source_family": command_config.get("source_family", "private_signal"),
                "evidence_quality": "text",
            },
        )

    def _error_item(
        self,
        name: str,
        site: str,
        command: str,
        returncode: int,
        output: str,
    ) -> SourceItem:
        error_text = output.strip()[:500]
        dedupe_key = f"opencli_{site}_{command}_error_{sha1(error_text.encode()).hexdigest()[:12]}"
        return SourceItem(
            source_id=f"opencli_{sha1(dedupe_key.encode()).hexdigest()[:12]}",
            source_name=f"OpenCLI: {name}",
            source_type="cli",
            title=f"[OpenCLI Error] {name} (exit {returncode})",
            content=f"OpenCLI command failed with code {returncode}: {error_text}",
            reliability="low",
            dedupe_key=dedupe_key,
            metadata={
                "backend": "opencli",
                "site": site,
                "command": command,
                "adapter": name,
                "exit_code": returncode,
                "error_type": "OpenCliExecutionError",
            },
        )
