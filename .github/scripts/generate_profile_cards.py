#!/usr/bin/env python3
"""Generate self-hosted SVG cards for the GitHub profile README."""

from __future__ import annotations

import html
import json
import os
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


USERNAME = "mirror29"
FEATURED_REPOSITORIES = ("inalpha", "openfinclaw-cli")
OUTPUT_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "profile"
API_ROOT = "https://api.github.com"
GRAPHQL_API = "https://api.github.com/graphql"
CARD_WIDTH = 420
PALETTE = ("#52E0A4", "#F0B35A", "#6CB6FF", "#D2A8FF", "#FF7B72")


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


def github_graphql(query: str) -> Any:
    """Execute an authenticated query against GitHub's GraphQL API."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for contribution statistics")
    request = urllib.request.Request(
        GRAPHQL_API,
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USERNAME}-profile-card-generator",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL query failed: {payload['errors']}")
    return payload["data"]


def total_contributions_since(created_at: str) -> int:
    """Return the sum of GitHub contributions from account creation to now."""
    created_year = datetime.fromisoformat(created_at.replace("Z", "+00:00")).year
    current_year = datetime.now(UTC).year
    yearly_queries = []
    for year in range(created_year, current_year + 1):
        yearly_queries.append(
            f'y{year}: contributionsCollection('
            f'from: "{year}-01-01T00:00:00Z", '
            f'to: "{year}-12-31T23:59:59Z") '
            "{ contributionCalendar { totalContributions } }"
        )
    data = github_graphql(
        f'query {{ user(login: "{USERNAME}") {{ {" ".join(yearly_queries)} }} }}'
    )
    return sum(
        collection["contributionCalendar"]["totalContributions"]
        for collection in data["user"].values()
    )


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


def split_description(description: str, line_length: int = 47) -> tuple[str, str]:
    """Split repository copy into two short display lines."""
    words = description.split()
    lines = [""]
    for word in words:
        candidate = f"{lines[-1]} {word}".strip()
        if len(candidate) <= line_length or not lines[-1]:
            lines[-1] = candidate
        elif len(lines) == 1:
            lines.append(word)
        else:
            lines[-1] = f"{lines[-1][: line_length - 1].rstrip()}…"
            break
    if len(lines) == 1:
        lines.append("")
    if len(lines[1]) > line_length:
        lines[1] = f"{lines[1][: line_length - 1].rstrip()}…"
    return lines[0], lines[1]


def svg_shell(height: int, body: str, accent: str = "#52E0A4") -> str:
    """Wrap card content in the shared Inalpha terminal visual style."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" height="{height}" viewBox="0 0 {CARD_WIDTH} {height}" role="img">
  <defs>
    <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0C1714"/>
      <stop offset="1" stop-color="#07100E"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{accent}"/>
      <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <style>
    .eyebrow {{ fill: {accent}; font: 700 10px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; letter-spacing: 1.8px; }}
    .title {{ fill: #F2F7F5; font: 700 19px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; }}
    .text {{ fill: #AAB8B3; font: 13px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; }}
    .muted {{ fill: #64746F; font: 10px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; letter-spacing: .5px; }}
    .value {{ fill: #F2F7F5; font: 700 24px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; font-variant-numeric: tabular-nums; }}
    .metric {{ fill: #AAB8B3; font: 600 11px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; }}
  </style>
  <rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{height - 2}" rx="10" fill="url(#surface)" stroke="#263A33"/>
  <rect x="1" y="1" width="{CARD_WIDTH - 2}" height="3" rx="2" fill="url(#accent)"/>
  <circle cx="386" cy="25" r="3" fill="{accent}"/>
  <circle cx="398" cy="25" r="3" fill="#263A33"/>
{body}
</svg>
"""


def repository_card(repository: dict[str, Any]) -> str:
    """Render one featured repository card."""
    description = (repository.get("description") or "No description").lstrip("🦊 ")
    first_line, second_line = split_description(description)
    language = repository.get("language") or "Other"
    accent = "#52E0A4" if repository["name"] == "inalpha" else "#F0B35A"
    display_name = "Inalpha" if repository["name"] == "inalpha" else repository["name"]
    body = f"""  <text x="24" y="30" class="eyebrow">FEATURED / OPEN SOURCE</text>
  <path d="M24 45h10l5 9-5 9H24l-5-9z" fill="{accent}" fill-opacity=".14" stroke="{accent}"/>
  <path d="M24 50l4 4-4 4m6 0h4" fill="none" stroke="{accent}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="50" y="61" class="title">{escape(display_name)}</text>
  <text x="24" y="91" class="text">{escape(first_line)}</text>
  <text x="24" y="111" class="text">{escape(second_line)}</text>
  <line x1="24" y1="132" x2="396" y2="132" stroke="#20322C"/>
  <circle cx="29" cy="151" r="4" fill="{accent}"/>
  <text x="40" y="155" class="metric">{escape(language)}</text>
  <path d="M220 144.5l2.1 4.2 4.6.7-3.3 3.2.8 4.6-4.2-2.2-4.2 2.2.8-4.6-3.3-3.2 4.6-.7z" fill="none" stroke="#AAB8B3" stroke-width="1.2"/>
  <text x="233" y="155" class="metric">{compact_number(repository["stargazers_count"])}</text>
  <path d="M319 144v5a4 4 0 004 4h3m-7-9a2 2 0 11-4 0 2 2 0 014 0zm11 0a2 2 0 11-4 0 2 2 0 014 0zm0 0v2a4 4 0 01-4 4h-3" fill="none" stroke="#AAB8B3" stroke-width="1.2" stroke-linecap="round"/>
  <text x="337" y="155" class="metric">{compact_number(repository["forks_count"])}</text>"""
    return svg_shell(176, body, accent)


def stats_card(
    user: dict[str, Any], repositories: list[dict[str, Any]], contributions: int
) -> str:
    """Render aggregate public GitHub statistics."""
    stars = sum(repository["stargazers_count"] for repository in repositories)
    forks = sum(repository["forks_count"] for repository in repositories)
    metrics = (
        ("TOTAL CONTRIBUTIONS", contributions, "M2 3h3v3H2zm5 0h3v3H7zm5 0h2v3h-2zM2 8h3v3H2zm5 0h3v3H7zm5 0h2v3h-2z", "ALL TIME"),
        ("TOTAL STARS", stars, "M8 1.8l1.9 3.9 4.3.6-3.1 3 .8 4.3L8 11.3 4.1 13.6l.8-4.3-3.1-3 4.3-.6z", "PUBLIC"),
        ("TOTAL FORKS", forks, "M4 3v7a3 3 0 003 3h2M12 3v2a3 3 0 01-3 3H7", "PUBLIC"),
        ("FOLLOWERS", user["followers"], "M8 8a3 3 0 100-6 3 3 0 000 6zm-5 6a5 5 0 0110 0", "PUBLIC"),
    )
    cells = []
    for index, (label, value, icon_path, caption) in enumerate(metrics):
        x = 24 + (index % 2) * 190
        y = 76 + (index // 2) * 85
        cells.append(
            f'  <rect x="{x}" y="{y}" width="174" height="69" rx="6" fill="#101E19" stroke="#20322C"/>'
            f'<svg x="{x + 14}" y="{y + 13}" width="16" height="16" viewBox="0 0 16 16">'
            f'<path d="{icon_path}" fill="none" stroke="#52E0A4" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
            f'<text x="{x + 42}" y="{y + 26}" class="metric">{label}</text>'
            f'<text x="{x + 14}" y="{y + 57}" class="value">{compact_number(value)}</text>'
            f'<text x="{x + 160}" y="{y + 56}" text-anchor="end" class="muted">{caption}</text>'
        )
    body = (
        '  <text x="24" y="30" class="eyebrow">PUBLIC SIGNALS / LIVE</text>\n'
        '  <text x="24" y="58" class="title">GitHub footprint</text>\n'
        + "\n".join(cells)
    )
    return svg_shell(246, body)


def language_card(repositories: list[dict[str, Any]]) -> str:
    """Render the most-used languages by repository count."""
    counts = Counter(
        repository["language"]
        for repository in repositories
        if repository.get("language") and not repository.get("fork")
    )
    total = sum(counts.values()) or 1
    top_languages = counts.most_common(4)
    other_count = total - sum(count for _, count in top_languages)
    if other_count:
        top_languages.append(("Other", other_count))
    rows = []
    segment_x = 24.0
    segments = []
    for index, ((language, count), color) in enumerate(zip(top_languages, PALETTE)):
        percentage = count / total * 100
        segment_width = 372 * count / total
        segments.append(
            f'<rect x="{segment_x:.1f}" y="70" width="{max(2, segment_width):.1f}" height="10" fill="{color}"/>'
        )
        segment_x += segment_width
        y = 108 + index * 25
        percentage = count / total * 100
        rows.append(
            f'  <circle cx="29" cy="{y - 4}" r="4" fill="{color}"/>'
            f'<text x="42" y="{y}" class="metric">{escape(language)}</text>'
            f'<rect x="178" y="{y - 9}" width="168" height="5" rx="2.5" fill="#172923"/>'
            f'<rect x="178" y="{y - 9}" width="{168 * count / total:.1f}" height="5" rx="2.5" fill="{color}"/>'
            f'<text x="396" y="{y}" text-anchor="end" class="metric">{percentage:.1f}%</text>'
        )
    body = (
        '  <text x="24" y="30" class="eyebrow">CODE MIX / PUBLIC REPOS</text>\n'
        '  <text x="24" y="58" class="title">Primary language share</text>\n'
        '  <clipPath id="language-bar"><rect x="24" y="70" width="372" height="10" rx="5"/></clipPath>\n'
        '  <g clip-path="url(#language-bar)">' + "".join(segments) + "</g>\n"
        + "\n".join(rows)
    )
    return svg_shell(246, body)


def main() -> None:
    """Fetch profile data and update all self-hosted cards."""
    user = github_get(f"/users/{USERNAME}")
    repositories = github_get(f"/users/{USERNAME}/repos?per_page=100&sort=updated")
    contributions = total_contributions_since(user["created_at"])
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for repository_name in FEATURED_REPOSITORIES:
        repository = github_get(f"/repos/{USERNAME}/{repository_name}")
        (OUTPUT_DIRECTORY / f"{repository_name}.svg").write_text(
            repository_card(repository), encoding="utf-8"
        )

    (OUTPUT_DIRECTORY / "stats.svg").write_text(
        stats_card(user, repositories, contributions), encoding="utf-8"
    )
    (OUTPUT_DIRECTORY / "languages.svg").write_text(
        language_card(repositories), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
