#!/usr/bin/env python3
"""Generate self-hosted SVG cards for the GitHub profile README."""

from __future__ import annotations

import html
import json
import os
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


USERNAME = "mirror29"
FEATURED_REPOSITORIES = ("inalpha", "openfinclaw-cli")
OUTPUT_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "profile"
API_ROOT = "https://api.github.com"


def github_get(path: str) -> Any:
    """Fetch and decode one response from GitHub's REST API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-card-generator",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def escape(value: object) -> str:
    """Escape a value before inserting it into SVG markup."""
    return html.escape(str(value), quote=True)


def compact_number(value: int) -> str:
    """Format a count without losing precision below one thousand."""
    if value < 1_000:
        return str(value)
    if value < 1_000_000:
        return f"{value / 1_000:.1f}k".replace(".0k", "k")
    return f"{value / 1_000_000:.1f}m".replace(".0m", "m")


def svg_shell(width: int, height: int, body: str) -> str:
    """Wrap card content in the shared Tokyo Night visual style."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <style>
    .title {{ fill: #70a5fd; font: 600 18px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .name {{ fill: #bf91f3; font: 600 20px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .label {{ fill: #38bdae; font: 600 13px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .text {{ fill: #a4aacb; font: 14px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .value {{ fill: #e4e7f2; font: 600 16px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
  </style>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" fill="#1a1b27" stroke="#30363d"/>
{body}
</svg>
"""


def repository_card(repository: dict[str, Any]) -> str:
    """Render one featured repository card."""
    description = repository.get("description") or "No description"
    if len(description) > 68:
        description = f"{description[:65]}..."
    language = repository.get("language") or "Other"
    body = f"""  <text x="24" y="38" class="name">{escape(repository["name"])}</text>
  <text x="24" y="70" class="text">{escape(description)}</text>
  <circle cx="30" cy="106" r="6" fill="#3572A5"/>
  <text x="42" y="111" class="text">{escape(language)}</text>
  <text x="170" y="111" class="text">★ {compact_number(repository["stargazers_count"])}</text>
  <text x="250" y="111" class="text">⑂ {compact_number(repository["forks_count"])}</text>"""
    return svg_shell(420, 138, body)


def stats_card(user: dict[str, Any], repositories: list[dict[str, Any]]) -> str:
    """Render aggregate public GitHub statistics."""
    stars = sum(repository["stargazers_count"] for repository in repositories)
    forks = sum(repository["forks_count"] for repository in repositories)
    metrics = (
        ("Public repositories", user["public_repos"]),
        ("Total stars", stars),
        ("Total forks", forks),
        ("Followers", user["followers"]),
    )
    rows = "\n".join(
        f'  <text x="28" y="{75 + index * 35}" class="text">{label}</text>'
        f'<text x="380" y="{75 + index * 35}" text-anchor="end" class="value">{compact_number(value)}</text>'
        for index, (label, value) in enumerate(metrics)
    )
    body = f'  <text x="24" y="38" class="title">Miro\'s GitHub Stats</text>\n{rows}'
    return svg_shell(420, 230, body)


def language_card(repositories: list[dict[str, Any]]) -> str:
    """Render the most-used languages by repository count."""
    colors = ("#3572A5", "#3178C6", "#f1e05a", "#41b883", "#e34c26")
    counts = Counter(
        repository["language"]
        for repository in repositories
        if repository.get("language") and not repository.get("fork")
    )
    top_languages = counts.most_common(5)
    total = sum(count for _, count in top_languages) or 1
    rows = []
    for index, ((language, count), color) in enumerate(zip(top_languages, colors)):
        y = 76 + index * 30
        percentage = count / total * 100
        rows.append(
            f'  <circle cx="30" cy="{y - 5}" r="6" fill="{color}"/>'
            f'<text x="44" y="{y}" class="text">{escape(language)}</text>'
            f'<text x="385" y="{y}" text-anchor="end" class="value">{percentage:.1f}%</text>'
        )
    body = '  <text x="24" y="38" class="title">Most Used Languages</text>\n' + "\n".join(rows)
    return svg_shell(420, 230, body)


def main() -> None:
    """Fetch profile data and update all self-hosted cards."""
    user = github_get(f"/users/{USERNAME}")
    repositories = github_get(f"/users/{USERNAME}/repos?per_page=100&sort=updated")
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for repository_name in FEATURED_REPOSITORIES:
        repository = github_get(f"/repos/{USERNAME}/{repository_name}")
        (OUTPUT_DIRECTORY / f"{repository_name}.svg").write_text(
            repository_card(repository), encoding="utf-8"
        )

    (OUTPUT_DIRECTORY / "stats.svg").write_text(
        stats_card(user, repositories), encoding="utf-8"
    )
    (OUTPUT_DIRECTORY / "languages.svg").write_text(
        language_card(repositories), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
