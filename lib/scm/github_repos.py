"""Discover GitHub repositories accessible to an OAuth user token."""

from __future__ import print_function

import requests

_GITHUB_API = "https://api.github.com"
_PER_PAGE = 100
_REQUEST_TIMEOUT = 30


def list_user_repositories(access_token):
    """Return repo dicts: full_name, name, html_url, default_branch, private."""
    token = (access_token or "").strip()
    if not token:
        return []
    headers = {
        "Authorization": "Bearer %s" % token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    repos = []
    page = 1
    while True:
        resp = requests.get(
            "%s/user/repos" % _GITHUB_API,
            headers=headers,
            params={
                "per_page": _PER_PAGE,
                "page": page,
                "sort": "updated",
                "direction": "desc",
                "type": "all",
            },
            timeout=_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        for row in batch:
            full_name = (row.get("full_name") or "").strip()
            if not full_name:
                continue
            repos.append({
                "full_name": full_name,
                "name": row.get("name") or full_name.split("/")[-1],
                "html_url": row.get("html_url") or ("https://github.com/%s" % full_name),
                "default_branch": row.get("default_branch") or "main",
                "private": bool(row.get("private")),
            })
        if len(batch) < _PER_PAGE:
            break
        page += 1
    return repos
