"""Tests for Testable catalog provisioning helpers."""

import os
import unittest
from unittest.mock import Mock, patch

from lib.sa_qa import (
    _catalog_needs_provisioning,
    clone_url_for_repository_match,
    extract_task_failures,
    fetch_repository_branches,
    format_task_failure_detail,
    ingestion_url_from_env,
    is_misseeded_repository,
    list_connected_repositories,
    provision_project_for_repo,
    rank_qa_repos_for_branches,
    repository_matches_slug,
    resolve_catalog,
    resolve_github_default_branch,
    wait_for_branches,
)


class CloneUrlTests(unittest.TestCase):
    def test_builds_github_clone_url(self):
        self.assertEqual(
            clone_url_for_repository_match("Mohammed-shihaf/Test_Repo"),
            "https://github.com/Mohammed-shihaf/Test_Repo.git",
        )

    def test_strips_trailing_git(self):
        self.assertEqual(
            clone_url_for_repository_match("owner/repo.git"),
            "https://github.com/owner/repo.git",
        )


class CatalogProvisioningTests(unittest.TestCase):
    def test_needs_provisioning_for_not_found(self):
        exc = RuntimeError("Repository 'a/b' not found. Available: ['x/y']")
        self.assertTrue(_catalog_needs_provisioning(exc))

    def test_needs_provisioning_for_no_projects(self):
        self.assertTrue(_catalog_needs_provisioning(RuntimeError("No projects found for this user")))

    def test_does_not_provision_for_other_errors(self):
        self.assertFalse(_catalog_needs_provisioning(RuntimeError("HTTP 500 internal error")))

    def test_provision_always_posts(self):
        client = Mock()
        client.runtime_url = "https://runtime.test"
        client.post_json.return_value = {"id": "proj-1"}
        provision_project_for_repo(
            client, "Test Repo", "https://github.com/o/r.git", "main"
        )
        client.post_json.assert_called_once()
        body = client.post_json.call_args[0][1]
        self.assertEqual(body["clone_url"], "https://github.com/o/r.git")
        self.assertEqual(body["scm_provider"], "github")


class SeedBranchTests(unittest.TestCase):
    def test_ingestion_url_qa_default(self):
        with patch.dict(os.environ, {"IDENTITY_URL": "https://qa-api.testable.cc"}, clear=False):
            self.assertEqual(ingestion_url_from_env(), "https://qa-ingestion.testable.cc")

    def test_resolve_github_default_branch_fallback(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GITHUB_TOKEN", None)
            self.assertEqual(resolve_github_default_branch("owner/repo"), "main")

    def test_is_misseeded_repository(self):
        repo = {"default_branch": "SX_Access-Control-Verification_Bug_2.6"}
        required = [
            "SX_Access-Control-Verification_Bug_2.6",
            "SX_Access-Control-Verification_BugFX_2.6",
        ]
        self.assertTrue(is_misseeded_repository(repo, "main", required))
        self.assertFalse(is_misseeded_repository({"default_branch": "main"}, "main", required))


class WaitForBranchesTests(unittest.TestCase):
    def test_waits_until_all_branches_present(self):
        client = Mock()
        calls = {"n": 0}
        all_names = ["B1", "B2", "B3", "B4"]

        def fetch_side_effect(_client, _repo_id):
            calls["n"] += 1
            if calls["n"] < 3:
                return {"B1": {"name": "B1", "id": "1"}}, 1
            return {name: {"name": name, "id": name} for name in all_names}, len(all_names)

        with patch("lib.sa_qa.time.sleep"), patch("lib.sa_qa.refresh_branches"), patch(
            "lib.sa_qa.fetch_repository_branches", side_effect=fetch_side_effect
        ):
            result = wait_for_branches(
                client,
                "repo-1",
                all_names,
                poll_interval=1,
                timeout_sec=60,
                allow_partial=True,
                refresh_every_sec=0,
            )
        self.assertEqual(set(all_names), set(result.keys()) & set(all_names))

    def test_partial_fallback_only_after_timeout(self):
        client = Mock()
        with patch("lib.sa_qa.time.sleep"), patch("lib.sa_qa.refresh_branches"), patch(
            "lib.sa_qa.fetch_repository_branches",
            return_value=({"B1": {"name": "B1", "id": "1"}}, 1),
        ):
            with patch("lib.sa_qa.time.time") as mock_time:
                mock_time.side_effect = [0, 0, 5, 5, 11, 11]
                result = wait_for_branches(
                    client,
                    "repo-1",
                    ["B1", "B2"],
                    poll_interval=1,
                    timeout_sec=10,
                    allow_partial=True,
                    refresh_every_sec=0,
                )
        self.assertIn("B1", result)
        self.assertNotIn("B2", result)


class ResolveCatalogTests(unittest.TestCase):
    def test_repository_matches_slug(self):
        repo = {"clone_url": "https://github.com/Mohammed-shihaf/Test_Repo.git"}
        self.assertTrue(repository_matches_slug(repo, "Mohammed-shihaf/Test_Repo"))
        self.assertFalse(repository_matches_slug(repo, "shihafmohammed1/Tool_Testing"))

    def test_resolve_catalog_searches_all_projects(self):
        client = Mock()
        client.runtime_url = "https://runtime.test"
        projects = {
            "projects": [
                {"id": "p1", "name": "Tool_Testing"},
                {"id": "p2", "name": "Metric Evaluation Data Flow Testing"},
            ]
        }
        repos_by_project = {
            "p1": {"repositories": [{"id": "r1", "clone_url": "https://github.com/o/tool.git"}]},
            "p2": {"repositories": [{"id": "r2", "clone_url": "https://github.com/o/repo.git"}]},
        }
        branch_maps = {
            "r1": ({"B1": {"name": "B1"}}, 1),
            "r2": ({"B1": {"name": "B1"}, "B2": {"name": "B2"}}, 2),
        }

        def get_json(url):
            if url.endswith("/v1/projects"):
                return projects
            for pid, payload in repos_by_project.items():
                if url.endswith("/projects/%s/repositories" % pid):
                    return payload
            for rid, payload in branch_maps.items():
                if "/repositories/%s/branches" % rid in url:
                    branch_map, total = payload
                    return {
                        "branches": list(branch_map.values()),
                        "total": total,
                    }
            raise AssertionError("unexpected url: %s" % url)

        client.get_json = get_json
        catalog = resolve_catalog(
            client,
            None,
            "o/repo",
            required_branches=["B1", "B2"],
            project_name="Metric Evaluation Data Flow Testing",
        )
        self.assertEqual(catalog["repository_id"], "r2")
        self.assertEqual(catalog["project_id"], "p2")
        self.assertEqual(set(catalog["branches"].keys()), {"B1", "B2"})

    def test_resolve_catalog_does_not_switch_repos(self):
        client = Mock()
        client.runtime_url = "https://runtime.test"
        projects = {
            "projects": [
                {"id": "p1", "name": "Session Repo Project"},
                {"id": "p2", "name": "QA Catalog Project"},
            ]
        }
        repos_by_project = {
            "p1": {
                "repositories": [
                    {"id": "r1", "clone_url": "https://github.com/mohammed-shihaf/Test_Repo.git"},
                ]
            },
            "p2": {
                "repositories": [
                    {"id": "r2", "clone_url": "https://github.com/shihafmohammed1/Tool_Testing.git"},
                ]
            },
        }
        required = [
            "SX_Entry-Point-Sanitization_Bug_2.6",
            "SX_Entry-Point-Sanitization_BugFX_2.6",
            "SX_Entry-Point-Sanitization_TCC_2.6",
            "SX_Entry-Point-Sanitization_CC_2.6",
        ]
        branch_maps = {
            "r1": ({"SX_Entry-Point-Sanitization_Bug_2.6": {"name": required[0]}}, 1),
            "r2": ({name: {"name": name} for name in required}, len(required)),
        }

        def get_json(url):
            if url.endswith("/v1/projects"):
                return projects
            for pid, payload in repos_by_project.items():
                if url.endswith("/projects/%s/repositories" % pid):
                    return payload
            for rid, payload in branch_maps.items():
                if "/repositories/%s/branches" % rid in url:
                    branch_map, total = payload
                    return {"branches": list(branch_map.values()), "total": total}
            raise AssertionError("unexpected url: %s" % url)

        client.get_json = get_json
        catalog = resolve_catalog(
            client,
            None,
            "mohammed-shihaf/Test_Repo",
            required_branches=required,
        )
        self.assertEqual(catalog["repository_id"], "r1")
        self.assertEqual(catalog["project_id"], "p1")
        self.assertEqual(len(catalog["branches"]), 1)


class ListConnectedRepositoriesTests(unittest.TestCase):
    def test_lists_and_deduplicates_connected_repos(self):
        client = Mock()
        client.runtime_url = "https://runtime.test"
        projects = {
            "projects": [
                {"id": "p1", "name": "Tool Testing"},
                {"id": "p2", "name": "Other Project"},
            ]
        }
        repos_by_project = {
            "p1": {
                "repositories": [
                    {
                        "id": "r1",
                        "clone_url": "https://github.com/shihafmohammed1/Tool_Testing.git",
                    },
                    {
                        "id": "r1",
                        "clone_url": "https://github.com/shihafmohammed1/Tool_Testing",
                    },
                ]
            },
            "p2": {
                "repositories": [
                    {
                        "id": "r2",
                        "clone_url": "https://github.com/Mohammed-shihaf/Test_Repo.git",
                    },
                ]
            },
        }

        def get_json(url):
            if url.endswith("/v1/projects"):
                return projects
            for pid, payload in repos_by_project.items():
                if url.endswith("/projects/%s/repositories" % pid):
                    return payload
            raise AssertionError("unexpected url: %s" % url)

        client.get_json = get_json
        rows = list_connected_repositories(client)
        labels = [row["label"] for row in rows]
        self.assertEqual(
            labels,
            ["Mohammed-shihaf/Test_Repo", "shihafmohammed1/Tool_Testing"],
        )
        tool_row = next(row for row in rows if row["label"] == "shihafmohammed1/Tool_Testing")
        self.assertEqual(tool_row["project_name"], "Tool Testing")
        self.assertEqual(tool_row["project_id"], "p1")
        self.assertEqual(tool_row["repository_id"], "r1")


class RankQaReposTests(unittest.TestCase):
    def test_ranks_connected_repos_by_branch_coverage(self):
        client = Mock()
        client.runtime_url = "https://runtime.test"
        connected = [
            {
                "label": "Mohammed-shihaf/Test_Repo",
                "project_name": "Push Repo",
                "project_id": "p1",
                "repository_id": "r1",
            },
            {
                "label": "shihafmohammed1/Tool_Testing",
                "project_name": "QA Repo",
                "project_id": "p2",
                "repository_id": "r2",
            },
        ]
        required = [
            "SX_Entry-Point-Sanitization_Bug_2.6",
            "SX_Entry-Point-Sanitization_BugFX_2.6",
            "SX_Entry-Point-Sanitization_TCC_2.6",
            "SX_Entry-Point-Sanitization_CC_2.6",
        ]

        def resolve_side_effect(_client, _project_id, repository_match, required_branches=None, project_name=None):
            del required_branches, project_name
            if repository_match == "Mohammed-shihaf/Test_Repo":
                return {
                    "repository_label": repository_match,
                    "branches": {required[0]: {"name": required[0]}},
                    "catalog_total": 1,
                }
            return {
                "repository_label": repository_match,
                "branches": {name: {"name": name} for name in required},
                "catalog_total": len(required),
            }

        with patch("lib.sa_qa.resolve_catalog", side_effect=resolve_side_effect):
            ranked = rank_qa_repos_for_branches(client, connected, required)

        self.assertEqual(ranked[0]["label"], "shihafmohammed1/Tool_Testing")
        self.assertEqual(ranked[0]["ready_count"], 4)
        self.assertEqual(ranked[1]["ready_count"], 1)


class FetchRepositoryBranchesTests(unittest.TestCase):
    def test_paginates_until_total_reached(self):
        import re

        client = Mock()
        client.runtime_url = "https://runtime.test"

        def get_json(url):
            match = re.search(r"page=(\d+)", url)
            page = int(match.group(1)) if match else 1
            if page == 1:
                return {
                    "branches": [{"name": "B1"}, {"name": "B2"}],
                    "total": 3,
                }
            if page == 2:
                return {
                    "branches": [{"name": "B3"}],
                    "total": 3,
                }
            return {"branches": [], "total": 3}

        client.get_json = get_json
        branch_map, total = fetch_repository_branches(client, "repo-1")
        self.assertEqual(total, 3)
        self.assertEqual(set(branch_map.keys()), {"B1", "B2", "B3"})

class TaskFailureExtractionTests(unittest.TestCase):
    def test_extracts_from_tasks_list(self):
        summary = {
            "status": "failed",
            "tasks": [
                {"name": "bandit", "status": "completed"},
                {"name": "eslint", "status": "failed", "message": "timeout"},
            ],
        }
        failures = extract_task_failures(summary)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["name"], "eslint")
        self.assertEqual(failures[0]["message"], "timeout")

    def test_format_task_failure_detail(self):
        detail = format_task_failure_detail([
            {"name": "eslint", "status": "failed", "message": "timeout"},
            {"name": "bandit", "status": "failed", "message": ""},
        ])
        self.assertIn("eslint (timeout)", detail)
        self.assertIn("bandit", detail)


if __name__ == "__main__":
    unittest.main()
