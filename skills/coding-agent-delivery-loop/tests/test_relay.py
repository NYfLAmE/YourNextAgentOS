from __future__ import annotations

import json
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "relay.py"


class Fixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.repo = root / "repo"
        self.state = root / "state"
        self.handoff = root / "handoff"
        self.task = Path("docs/build_tasks/parent/plan.md")
        self.frontier = Path("docs/build_tasks/slice/plan.md")
        self.parent_review = Path("docs/build_tasks/parent/review.md")
        self.frontier_review = Path("docs/build_tasks/slice/review.md")
        self.progress = Path("docs/build_tasks/slice/progress.md")
        self.repo.mkdir(parents=True)
        self.git("init", "-q")
        self.git("config", "user.email", "relay-test@example.invalid")
        self.git("config", "user.name", "Relay Test")

    @property
    def env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["CODING_AGENT_DELIVERY_LOOP_STATE_DIR"] = str(self.state)
        env["CODING_AGENT_DELIVERY_LOOP_HANDOFF_DIR"] = str(self.handoff)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def write(self, relative: Path | str, text: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
        )
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
        return result.stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def approved(self, *, parent_status: str = "Approved", frontier_status: str = "Approved") -> str:
        self.write(
            self.task,
            f"# Parent\n\n> 状态：{parent_status}\n\n## Open Questions / Blockers\n\nNone.\n\n## Approval Record\n\nUser approved.\n",
        )
        self.write(
            self.frontier,
            f"# Slice\n\n> 状态：{frontier_status}\n\n## Open Questions / Blockers\n\nNone.\n\n## Approval Record\n\nUser approved.\n",
        )
        self.write(self.parent_review, "# Parent Review\n\nPre-Start Review: PASS\n")
        self.write(self.frontier_review, "# Slice Review\n\nPre-Start Review: PASS\n")
        self.write(self.progress, "# Progress\n\nNot started.\n")
        return self.commit("docs: approve fixture")

    def relay(self, *args: str | Path, expect: int = 0, env: dict[str, str] | None = None) -> dict:
        result = subprocess.run(
            ["python3", str(SCRIPT), *map(str, args)],
            cwd=self.repo,
            env=env or self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != expect:
            raise AssertionError(
                f"relay {' '.join(map(str, args))} expected {expect}, got {result.returncode}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        payload = result.stdout if result.stdout.strip() else result.stderr
        return json.loads(payload)

    def start(self, *extra: str | Path, expect: int = 0) -> dict:
        return self.relay(
            "start",
            "--worktree",
            self.repo,
            "--task",
            self.task,
            "--frontier",
            self.frontier,
            "--base",
            "HEAD",
            "--actor",
            "codex",
            "--planner",
            "codex",
            "--builder",
            "cursor",
            "--reviewer",
            "codex",
            "--approval-evidence",
            self.parent_review,
            "--approval-evidence",
            self.frontier_review,
            *extra,
            expect=expect,
        )

    def claim(self, actor: str) -> tuple[dict, str]:
        state = self.relay("claim", "--worktree", self.repo, "--actor", actor)
        return state, state["lease_token"]

    def submit_implementation(self, lease_token: str, text: str = "v1\n") -> dict:
        self.write("code.txt", text)
        self.write(self.progress, "# Progress\n\nImplementation committed; review pending.\n")
        self.commit("feat: implement fixture")
        return self.relay(
            "submit",
            "--worktree",
            self.repo,
            "--actor",
            "cursor",
            "--lease-token",
            lease_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.progress,
        )


class RelayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.fixture = Fixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_status_must_be_exact_top_level_approved(self) -> None:
        self.fixture.approved(parent_status="approved")
        error = self.fixture.relay(
            "start",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            "HEAD",
            "--actor",
            "codex",
            "--planner",
            "codex",
            "--builder",
            "cursor",
            "--reviewer",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            expect=5,
        )
        self.assertEqual("not_approved", error["kind"])
        self.assertFalse(self.fixture.state.exists())

        with self.subTest("fenced example is not metadata"):
            other = Fixture(Path(self.temporary.name) / "fenced")
            other.write(other.task, "# Parent\n\n```md\n> 状态：Approved\n```\n\n## Body\n")
            other.write(other.frontier, "# Slice\n\n> 状态：Approved\n\n## Body\n")
            other.write(other.parent_review, "Pre-Start Review: PASS\n")
            other.write(other.frontier_review, "Pre-Start Review: PASS\n")
            other.write(other.progress, "Not started\n")
            other.commit("docs: add misleading status")
            error = other.relay(
                "start",
                "--worktree",
                other.repo,
                "--task",
                other.task,
                "--frontier",
                other.frontier,
                "--base",
                "HEAD",
                "--actor",
                "codex",
                "--planner",
                "codex",
                "--builder",
                "cursor",
                "--reviewer",
                "codex",
                "--approval-evidence",
                other.parent_review,
                expect=5,
            )
            self.assertIn(error["kind"], {"not_approved", "invariant_failed"})

    def test_status_rejects_other_fences_comments_and_unterminated_frontmatter(self) -> None:
        misleading = {
            "tilde_fence": "# Parent\n\n~~~md\n> 状态：Approved\n~~~\n\n## Body\n",
            "short_fence_close": "# Parent\n\n````md\n```\n> 状态：Approved\n````\n\n## Body\n",
            "html_comment": "# Parent\n\n<!--\n> 状态：Approved\n-->\n\n## Body\n",
            "raw_html": "# Parent\n\n<pre>\n> 状态：Approved\n</pre>\n",
            "nested_blockquote": "# Parent\n\n- example only:\n  > 状态：Approved\n",
            "unterminated_frontmatter": "---\nstatus: Approved\n# no closing delimiter\n",
            "indented_frontmatter_open": "  ---\nstatus: Approved\n---\n",
            "indented_frontmatter_close": "---\nstatus: Approved\n  ---\n",
            "nested_yaml": "---\nexample:\n  status: Approved\n---\n\n# Parent\n",
            "yaml_block_scalar": "---\nexample: |\n  status: Approved\n---\n\n# Parent\n",
            "yaml_unmatched_quote": "---\nstatus: 'Approved\n---\n\n# Parent\n",
        }
        for name, parent_text in misleading.items():
            with self.subTest(name=name):
                fixture = Fixture(Path(self.temporary.name) / name)
                fixture.write(fixture.task, parent_text)
                fixture.write(fixture.frontier, "# Slice\n\n> 状态：Approved\n\n## Body\n")
                fixture.write(fixture.parent_review, "# Review\n\nPre-Start Review: PASS\n")
                fixture.write(fixture.frontier_review, "# Review\n\nPre-Start Review: PASS\n")
                fixture.write(fixture.progress, "# Progress\n\nNot started.\n")
                fixture.commit("docs: add misleading approval")
                error = fixture.start(expect=5)
                self.assertEqual("not_approved", error["kind"])
                self.assertFalse(list(fixture.state.glob("*.json")))

    def test_claim_token_fences_same_actor_and_takeover(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        _, first_token = self.fixture.claim("cursor")
        conflict = self.fixture.relay("claim", "--worktree", self.fixture.repo, "--actor", "cursor", expect=5)
        self.assertEqual("ownership_conflict", conflict["kind"])
        takeover = self.fixture.relay("takeover", "--worktree", self.fixture.repo, "--actor", "cursor")
        second_token = takeover["lease_token"]
        self.assertNotEqual(first_token, second_token)

        self.fixture.write("code.txt", "v1\n")
        self.fixture.commit("feat: implement after takeover")
        stale = self.fixture.relay(
            "submit",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            first_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.progress,
            expect=5,
        )
        self.assertEqual("ownership_conflict", stale["kind"])

    def test_dirty_environment_block_resumes_same_phase_and_base(self) -> None:
        base = self.fixture.approved()
        self.fixture.start()
        _, token = self.fixture.claim("cursor")
        self.fixture.write("partial.txt", "preserve\n")
        blocked = self.fixture.relay(
            "block",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            token,
            "--reason",
            "environment",
        )
        self.assertEqual("blocked", blocked["phase"])
        resumed = self.fixture.relay("resume", "--worktree", self.fixture.repo, "--actor", "cursor")
        self.assertEqual("executing", resumed["phase"])
        self.assertEqual(base, resumed["assignment_base"])
        self.assertTrue((self.fixture.repo / "partial.txt").is_file())

    def test_blocker_evidence_is_pinned(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        _, token = self.fixture.claim("cursor")
        blocker = Path("docs/build_tasks/slice/blocker.md")
        self.fixture.write(blocker, "# Blocker\n\nProvider unavailable.\n")
        self.fixture.commit("docs: record blocker evidence")
        blocked = self.fixture.relay(
            "block",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            token,
            "--reason",
            "evidence",
            "--evidence",
            blocker,
        )
        self.assertIn(str(blocker), blocked["evidence_refs"])
        (self.fixture.repo / blocker).unlink()
        self.fixture.commit("docs: delete blocker evidence")
        error = self.fixture.relay(
            "resume",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            expect=5,
        )
        self.assertEqual("evidence_drift", error["kind"])

    def test_blocked_restart_preserves_original_review_base(self) -> None:
        base = self.fixture.approved()
        self.fixture.start()
        _, token = self.fixture.claim("cursor")
        self.fixture.write("partial.txt", "committed partial\n")
        self.fixture.commit("wip: preserve partial work")
        self.fixture.relay(
            "block",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            token,
            "--reason",
            "environment",
        )
        wrong = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            "HEAD",
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            expect=5,
        )
        self.assertEqual("base_drift", wrong["kind"])
        restarted = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            base,
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
        )
        self.assertEqual(base, restarted["assignment_base"])

    def test_dirty_decision_block_reapproves_then_resumes_in_place(self) -> None:
        base = self.fixture.approved()
        self.fixture.start()
        _, token = self.fixture.claim("cursor")
        self.fixture.write("partial.txt", "uncommitted task-owned work\n")
        self.fixture.relay(
            "block",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            token,
            "--reason",
            "user_decision",
        )

        frontier = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.frontier, frontier.replace("## Open Questions", "## Re-approved Contract\n\nDecision fixed.\n\n## Open Questions"))
        self.fixture.write(self.fixture.parent_review, "# Parent Review\n\nPre-Start Review: PASS after decision.\n")
        self.fixture.write(self.fixture.frontier_review, "# Slice Review\n\nPre-Start Review: PASS after decision.\n")
        self.fixture.git(
            "add",
            str(self.fixture.frontier),
            str(self.fixture.parent_review),
            str(self.fixture.frontier_review),
        )
        self.fixture.git("commit", "-qm", "docs: reapprove interrupted slice")
        self.assertIn("?? partial.txt", self.fixture.git("status", "--porcelain=v1"))

        refreshed = self.fixture.relay(
            "reapprove",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            "--approval-evidence",
            self.fixture.frontier_review,
        )
        self.assertEqual("blocked", refreshed["phase"])
        self.assertEqual("reapproved", refreshed["block_reason"])
        self.assertEqual("cursor", refreshed["next_role"])
        resumed = self.fixture.relay("resume", "--worktree", self.fixture.repo, "--actor", "cursor")
        self.assertEqual("executing", resumed["phase"])
        self.assertEqual(base, resumed["assignment_base"])
        self.assertTrue((self.fixture.repo / "partial.txt").is_file())

    def test_reapprove_rejects_stale_evidence_and_frontier_replacement(self) -> None:
        with self.subTest("stale evidence"):
            fixture = Fixture(Path(self.temporary.name) / "stale-reapproval")
            base = fixture.approved()
            fixture.start()
            _, token = fixture.claim("cursor")
            fixture.relay(
                "block",
                "--worktree",
                fixture.repo,
                "--actor",
                "cursor",
                "--lease-token",
                token,
                "--reason",
                "user_decision",
            )
            restart_error = fixture.relay(
                "restart",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                fixture.frontier,
                "--base",
                base,
                "--actor",
                "codex",
                "--approval-evidence",
                fixture.parent_review,
                expect=5,
            )
            self.assertEqual("not_approved", restart_error["kind"])
            error = fixture.relay(
                "reapprove",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                fixture.frontier,
                "--actor",
                "codex",
                "--approval-evidence",
                fixture.parent_review,
                expect=5,
            )
            self.assertEqual("evidence_not_updated", error["kind"])

        with self.subTest("frontier replacement"):
            fixture = Fixture(Path(self.temporary.name) / "replacement-reapproval")
            fixture.approved()
            fixture.start()
            _, token = fixture.claim("cursor")
            fixture.relay(
                "block",
                "--worktree",
                fixture.repo,
                "--actor",
                "cursor",
                "--lease-token",
                token,
                "--reason",
                "user_decision",
            )
            replacement = Path("docs/build_tasks/other/plan.md")
            fixture.write(replacement, "# Other Slice\n\n> 状态：Approved\n\n## Contract\n\nDifferent.\n")
            fixture.write(fixture.parent_review, "# Review\n\nPre-Start Review: PASS for replacement.\n")
            fixture.commit("docs: attempt frontier replacement")
            error = fixture.relay(
                "reapprove",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                replacement,
                "--actor",
                "codex",
                "--approval-evidence",
                fixture.parent_review,
                expect=5,
            )
            self.assertEqual("authority_drift", error["kind"])

    def test_blocked_restart_cannot_migrate_branch(self) -> None:
        base = self.fixture.approved()
        self.fixture.start()
        _, token = self.fixture.claim("cursor")
        self.fixture.relay(
            "block",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            token,
            "--reason",
            "environment",
        )
        self.fixture.git("switch", "-qc", "different-owner-branch")
        error = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            base,
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            expect=5,
        )
        self.assertEqual("ownership_conflict", error["kind"])

    def test_blocked_restart_keeps_prior_transition_evidence(self) -> None:
        base = self.fixture.approved()
        self.fixture.start()
        _, builder_token = self.fixture.claim("cursor")
        submitted = self.fixture.submit_implementation(builder_token)
        self.assertEqual(1, len(submitted["transition_evidence_manifest"]))
        _, reviewer_token = self.fixture.claim("codex")
        self.fixture.relay(
            "block",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--reason",
            "environment",
        )
        restarted = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            base,
            "--phase",
            "ready_to_review",
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
        )
        self.assertEqual("ready_to_review", restarted["phase"])
        self.assertEqual([str(self.fixture.progress)], restarted["evidence_refs"])
        self.assertEqual(1, len(restarted["transition_evidence_manifest"]))

    def test_child_acceptance_cannot_mark_parent_done(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        _, builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(builder_token)
        _, reviewer_token = self.fixture.claim("codex")
        parent = (self.fixture.repo / self.fixture.task).read_text(encoding="utf-8")
        frontier = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.task, parent.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed\n")
        self.fixture.commit("docs: incorrectly complete parent")
        error = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
            expect=5,
        )
        self.assertIn(error["kind"], {"authority_drift", "not_approved"})

    def test_acceptance_allows_only_frontier_admin_status(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        _, builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(builder_token)
        _, reviewer_token = self.fixture.claim("codex")
        frontier = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed\n")
        self.fixture.commit("docs: accept child")
        accepted = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
        )
        self.assertEqual("accepted", accepted["phase"])
        self.assertEqual("codex", accepted["next_role"])

    def test_acceptance_requires_frontier_done(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        _, builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(builder_token)
        _, reviewer_token = self.fixture.claim("codex")
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed, but frontier not completed.\n")
        self.fixture.commit("docs: record review without completing frontier")
        error = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
            expect=5,
        )
        self.assertEqual("not_approved", error["kind"])

    def test_transition_evidence_must_change_in_its_phase(self) -> None:
        with self.subTest("submit"):
            fixture = Fixture(Path(self.temporary.name) / "stale-submit")
            fixture.approved()
            fixture.start()
            _, token = fixture.claim("cursor")
            fixture.write("code.txt", "implementation without progress update\n")
            fixture.commit("feat: omit progress evidence")
            error = fixture.relay(
                "submit",
                "--worktree",
                fixture.repo,
                "--actor",
                "cursor",
                "--lease-token",
                token,
                "--commit",
                "HEAD",
                "--evidence",
                fixture.progress,
                expect=5,
            )
            self.assertEqual("evidence_not_updated", error["kind"])

        with self.subTest("reject"):
            fixture = Fixture(Path(self.temporary.name) / "stale-reject")
            fixture.approved()
            fixture.start()
            _, builder_token = fixture.claim("cursor")
            fixture.submit_implementation(builder_token)
            _, reviewer_token = fixture.claim("codex")
            fixture.write("unrelated-review-note.txt", "finding was not put in canonical review\n")
            fixture.commit("docs: omit canonical findings")
            error = fixture.relay(
                "reject",
                "--worktree",
                fixture.repo,
                "--actor",
                "codex",
                "--lease-token",
                reviewer_token,
                "--commit",
                "HEAD",
                "--findings",
                fixture.frontier_review,
                expect=5,
            )
            self.assertEqual("evidence_not_updated", error["kind"])

        with self.subTest("accept"):
            fixture = Fixture(Path(self.temporary.name) / "stale-accept")
            fixture.approved()
            fixture.start()
            _, builder_token = fixture.claim("cursor")
            fixture.submit_implementation(builder_token)
            _, reviewer_token = fixture.claim("codex")
            frontier = (fixture.repo / fixture.frontier).read_text(encoding="utf-8")
            fixture.write(fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
            fixture.commit("docs: mark done without review evidence")
            error = fixture.relay(
                "accept",
                "--worktree",
                fixture.repo,
                "--actor",
                "codex",
                "--lease-token",
                reviewer_token,
                "--commit",
                "HEAD",
                "--evidence",
                fixture.frontier_review,
                expect=5,
            )
            self.assertEqual("evidence_not_updated", error["kind"])

    def test_pinned_transition_evidence_cannot_disappear(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        _, builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(builder_token)
        _, reviewer_token = self.fixture.claim("codex")
        (self.fixture.repo / self.fixture.progress).unlink()
        frontier = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed.\n")
        self.fixture.commit("docs: delete implementation evidence")
        error = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
            expect=5,
        )
        self.assertEqual("evidence_drift", error["kind"])

    def test_additional_authority_status_cannot_change_on_accept(self) -> None:
        self.fixture.approved()
        adr = Path("docs/adr/0001.md")
        self.fixture.write(adr, "# ADR\n\n> Status: Accepted\n\n## Decision\n\nStable.\n")
        self.fixture.commit("docs: add accepted ADR")
        self.fixture.start("--authority", adr)
        _, builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(builder_token)
        _, reviewer_token = self.fixture.claim("codex")
        self.fixture.write(adr, "# ADR\n\n> Status: Done\n\n## Decision\n\nStable.\n")
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed\n")
        self.fixture.commit("docs: drift ADR status")
        error = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
            expect=5,
        )
        self.assertEqual("authority_drift", error["kind"])

    def test_committed_authority_symlink_is_rejected(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        self.fixture.claim("cursor")
        original = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        copy = self.fixture.repo / "docs/build_tasks/slice/copy.md"
        copy.write_text(original, encoding="utf-8")
        target = self.fixture.repo / self.fixture.frontier
        target.unlink()
        target.symlink_to("copy.md")
        self.fixture.commit("docs: replace authority with symlink")
        error = self.fixture.relay("show", "--worktree", self.fixture.repo, expect=5)
        self.assertEqual("authority_drift", error["kind"])

    def test_deleted_prestart_evidence_blocks_transition(self) -> None:
        self.fixture.approved()
        self.fixture.start()
        self.fixture.claim("cursor")
        (self.fixture.repo / self.fixture.parent_review).unlink()
        self.fixture.commit("docs: delete approval evidence")
        error = self.fixture.relay("show", "--worktree", self.fixture.repo, expect=5)
        self.assertEqual("approval_evidence_drift", error["kind"])

    def test_corrupt_relay_id_cannot_escape_state_root(self) -> None:
        self.fixture.approved()
        state = self.fixture.start()
        state_path = self.fixture.state / f"{state['relay_id']}.json"
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        payload["relay_id"] = "../../escape"
        state_path.write_text(json.dumps(payload), encoding="utf-8")
        error = self.fixture.relay("show", "--worktree", self.fixture.repo, expect=5)
        self.assertEqual("malformed_state", error["kind"])
        self.assertFalse((self.fixture.state.parent / "escape.json").exists())

    def test_handoff_failure_does_not_commit_state_and_show_regenerates(self) -> None:
        self.fixture.approved()
        bad_handoff = self.fixture.root / "not-a-directory"
        bad_handoff.write_text("occupied", encoding="utf-8")
        bad_env = self.fixture.env
        bad_env["CODING_AGENT_DELIVERY_LOOP_HANDOFF_DIR"] = str(bad_handoff)
        error = self.fixture.relay(
            "start",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            "HEAD",
            "--actor",
            "codex",
            "--planner",
            "codex",
            "--builder",
            "cursor",
            "--reviewer",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            expect=5,
            env=bad_env,
        )
        self.assertEqual("handoff_failed", error["kind"])
        self.assertFalse(list(self.fixture.state.glob("*.json")))

        state = self.fixture.start()
        handoff = Path(state["handoff_path"])
        handoff.unlink()
        shown = self.fixture.relay("show", "--worktree", self.fixture.repo)
        self.assertTrue(Path(shown["handoff_path"]).is_file())

    def test_symlinked_managed_root_is_rejected_without_touching_target(self) -> None:
        self.fixture.approved()
        target = self.fixture.root / "attacker-selected-target"
        target.mkdir(mode=0o755)
        target.chmod(0o755)
        self.fixture.handoff.symlink_to(target, target_is_directory=True)
        error = self.fixture.start(expect=5)
        self.assertEqual("handoff_failed", error["kind"])
        self.assertEqual(0o755, target.stat().st_mode & 0o777)
        self.assertFalse(list(self.fixture.state.glob("*.json")))

    def test_symlinked_root_is_rejected_before_existing_handoff_read(self) -> None:
        self.fixture.approved()
        state = self.fixture.start()
        Path(state["handoff_path"]).unlink()
        self.fixture.handoff.rmdir()
        target = self.fixture.root / "preplanted-target"
        target.mkdir()
        self.fixture.handoff.symlink_to(target, target_is_directory=True)

        spec = importlib.util.spec_from_file_location("relay_symlink_order_test", SCRIPT)
        assert spec and spec.loader
        relay = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(relay)
        with mock.patch.dict(os.environ, self.fixture.env, clear=True), mock.patch.object(
            relay,
            "read_existing_derived_handoff",
            side_effect=AssertionError("unsafe handoff read occurred before root validation"),
        ) as read_existing:
            with self.assertRaises(relay.RelayError) as caught:
                relay.persist(state)
        self.assertEqual("handoff_failed", caught.exception.kind)
        read_existing.assert_not_called()

    def test_builder_and_reviewer_must_be_independent(self) -> None:
        self.fixture.approved()
        error = self.fixture.relay(
            "start",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.frontier,
            "--base",
            "HEAD",
            "--actor",
            "codex",
            "--planner",
            "codex",
            "--builder",
            "codex",
            "--reviewer",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            expect=5,
        )
        self.assertEqual("role_conflict", error["kind"])

    def test_full_rework_cycle_preserves_base_and_accepts(self) -> None:
        base = self.fixture.approved()
        started = self.fixture.start()

        _, first_builder_token = self.fixture.claim("cursor")
        submitted = self.fixture.submit_implementation(first_builder_token)
        first_implementation = submitted["implementation_head"]

        _, first_reviewer_token = self.fixture.claim("codex")
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Blocked\n\nFinding: fix edge case.\n")
        first_review = self.fixture.commit("docs: record review finding")
        rejected = self.fixture.relay(
            "reject",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            first_reviewer_token,
            "--commit",
            "HEAD",
            "--findings",
            self.fixture.frontier_review,
        )
        self.assertEqual("rework_ready", rejected["phase"])
        self.assertEqual(1, rejected["cycle"])

        _, second_builder_token = self.fixture.claim("cursor")
        self.fixture.write("code.txt", "v2 fixed\n")
        self.fixture.write(self.fixture.progress, "# Progress\n\nFinding fixed; review pending.\n")
        fixed = self.fixture.commit("fix: resolve review finding")
        resubmitted = self.fixture.relay(
            "submit",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            second_builder_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.progress,
        )
        self.assertEqual(fixed, resubmitted["implementation_head"])

        _, second_reviewer_token = self.fixture.claim("codex")
        frontier = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed\n\nAll gates pass.\n")
        accepted_commit = self.fixture.commit("docs: accept reviewed slice")
        accepted = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            second_reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
        )

        self.assertEqual("accepted", accepted["phase"])
        self.assertEqual("codex", accepted["next_role"])
        self.assertEqual(base, accepted["assignment_base"])
        self.assertEqual(accepted_commit, accepted["current_head"])
        self.assertTrue(self.fixture.git("merge-base", "--is-ancestor", base, first_implementation) == "")
        self.assertTrue(self.fixture.git("merge-base", "--is-ancestor", first_review, fixed) == "")
        persisted = next(self.fixture.state.glob("*.json")).read_text(encoding="utf-8")
        self.assertNotIn(first_builder_token, persisted)
        self.assertNotIn(first_reviewer_token, persisted)
        self.assertNotIn(second_builder_token, persisted)
        self.assertNotIn(second_reviewer_token, persisted)

    def test_accepted_is_globally_discoverable_until_terminal_close(self) -> None:
        base = self.fixture.approved()
        started = self.fixture.relay(
            "start",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.task,
            "--base",
            base,
            "--actor",
            "codex",
            "--planner",
            "codex",
            "--builder",
            "cursor",
            "--reviewer",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
        )
        self.assertEqual("ready_to_execute", started["phase"])
        _, builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(builder_token)
        _, reviewer_token = self.fixture.claim("codex")
        parent = (self.fixture.repo / self.fixture.task).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.task, parent.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.parent_review, "# Parent Review\n\nStatus: Passed.\n")
        self.fixture.commit("docs: accept parent final review")
        accepted = self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.parent_review,
        )
        self.assertEqual("accepted", accepted["phase"])

        discovered = subprocess.run(
            ["python3", str(SCRIPT), "show"],
            cwd=self.fixture.root,
            env=self.fixture.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, discovered.returncode, discovered.stderr)
        self.assertEqual("accepted", json.loads(discovered.stdout)["phase"])

        closed = self.fixture.relay("close", "--worktree", self.fixture.repo, "--actor", "codex")
        self.assertEqual("closed", closed["phase"])
        self.assertIsNone(closed["next_role"])
        absent = subprocess.run(
            ["python3", str(SCRIPT), "show"],
            cwd=self.fixture.root,
            env=self.fixture.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(3, absent.returncode)
        self.assertEqual("no_baton", json.loads(absent.stderr)["kind"])

    def test_accepted_restart_preserves_prior_contract_and_history(self) -> None:
        def accept_child(root: Path) -> tuple[Fixture, str, dict]:
            fixture = Fixture(root)
            base = fixture.approved()
            fixture.start()
            _, builder_token = fixture.claim("cursor")
            fixture.submit_implementation(builder_token)
            _, reviewer_token = fixture.claim("codex")
            frontier = (fixture.repo / fixture.frontier).read_text(encoding="utf-8")
            fixture.write(fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
            fixture.write(fixture.frontier_review, "# Review\n\nStatus: Passed.\n")
            fixture.commit("docs: accept first child")
            accepted = fixture.relay(
                "accept",
                "--worktree",
                fixture.repo,
                "--actor",
                "codex",
                "--lease-token",
                reviewer_token,
                "--commit",
                "HEAD",
                "--evidence",
                fixture.frontier_review,
            )
            return fixture, base, accepted

        with self.subTest("carry prior authority"):
            fixture, _, _ = accept_child(Path(self.temporary.name) / "carry-authority")
            next_plan = Path("docs/build_tasks/next/plan.md")
            next_review = Path("docs/build_tasks/next/review.md")
            fixture.write(next_plan, "# Next Slice\n\n> 状态：Approved\n\n## Contract\n\nNext only.\n")
            fixture.write(next_review, "# Review\n\nPre-Start Review: PASS.\n")
            fixture.commit("docs: approve next child")
            restarted = fixture.relay(
                "restart",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                next_plan,
                "--base",
                "HEAD",
                "--actor",
                "codex",
                "--approval-evidence",
                next_review,
            )
            authority_paths = {entry["path"] for entry in restarted["authority_manifest"]}
            self.assertIn(str(fixture.frontier), authority_paths)
            self.assertIn(str(next_plan), authority_paths)
            self.assertEqual(
                {str(fixture.frontier)},
                {entry["path"] for entry in restarted["sealed_authority_manifest"]},
            )
            self.assertGreaterEqual(len(restarted["transition_evidence_manifest"]), 2)

        with self.subTest("reject old contract rewrite"):
            fixture, _, _ = accept_child(Path(self.temporary.name) / "rewrite-authority")
            next_plan = Path("docs/build_tasks/next/plan.md")
            next_review = Path("docs/build_tasks/next/review.md")
            old = (fixture.repo / fixture.frontier).read_text(encoding="utf-8")
            fixture.write(fixture.frontier, old + "\nSilent contract rewrite.\n")
            fixture.write(next_plan, "# Next Slice\n\n> 状态：Approved\n\n## Contract\n\nNext.\n")
            fixture.write(next_review, "# Review\n\nPre-Start Review: PASS.\n")
            fixture.commit("docs: rewrite accepted contract")
            error = fixture.relay(
                "restart",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                next_plan,
                "--base",
                "HEAD",
                "--actor",
                "codex",
                "--approval-evidence",
                next_review,
                expect=5,
            )
            self.assertEqual("authority_drift", error["kind"])

        with self.subTest("reapprove cannot launder sealed child"):
            fixture, _, _ = accept_child(Path(self.temporary.name) / "launder-sealed")
            next_plan = Path("docs/build_tasks/next/plan.md")
            next_review = Path("docs/build_tasks/next/review.md")
            fixture.write(next_plan, "# Next Slice\n\n> 状态：Approved\n\n## Contract\n\nNext.\n")
            fixture.write(next_review, "# Review\n\nPre-Start Review: PASS.\n")
            fixture.commit("docs: approve next child")
            fixture.relay(
                "restart",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                next_plan,
                "--base",
                "HEAD",
                "--actor",
                "codex",
                "--approval-evidence",
                next_review,
            )
            _, token = fixture.claim("cursor")
            fixture.relay(
                "block",
                "--worktree",
                fixture.repo,
                "--actor",
                "cursor",
                "--lease-token",
                token,
                "--reason",
                "user_decision",
            )
            sealed = (fixture.repo / fixture.frontier).read_text(encoding="utf-8")
            fixture.write(fixture.frontier, sealed + "\nLaundered accepted semantics.\n")
            fixture.write(next_review, "# Review\n\nPre-Start Review: PASS after decision.\n")
            fixture.commit("docs: try to launder sealed child")
            error = fixture.relay(
                "reapprove",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                next_plan,
                "--actor",
                "codex",
                "--approval-evidence",
                next_review,
                expect=5,
            )
            self.assertEqual("authority_drift", error["kind"])

        with self.subTest("reject accepted history rewrite"):
            fixture, base, _ = accept_child(Path(self.temporary.name) / "rewrite-history")
            fixture.git("reset", "--hard", base)
            next_plan = Path("docs/build_tasks/next/plan.md")
            next_review = Path("docs/build_tasks/next/review.md")
            frontier = (fixture.repo / fixture.frontier).read_text(encoding="utf-8")
            fixture.write(fixture.frontier, frontier.replace("> 状态：Approved", "> 状态：Done"))
            fixture.write(next_plan, "# Next Slice\n\n> 状态：Approved\n\n## Contract\n\nNext.\n")
            fixture.write(next_review, "# Review\n\nPre-Start Review: PASS.\n")
            fixture.commit("docs: rebuild without accepted history")
            error = fixture.relay(
                "restart",
                "--worktree",
                fixture.repo,
                "--task",
                fixture.task,
                "--frontier",
                next_plan,
                "--base",
                "HEAD",
                "--actor",
                "codex",
                "--approval-evidence",
                next_review,
                expect=5,
            )
            self.assertEqual("base_drift", error["kind"])

    def test_parent_final_review_requires_first_baton_root_base(self) -> None:
        root_base = self.fixture.approved()
        self.fixture.start()
        _, first_builder_token = self.fixture.claim("cursor")
        self.fixture.submit_implementation(first_builder_token)
        _, first_reviewer_token = self.fixture.claim("codex")
        first = (self.fixture.repo / self.fixture.frontier).read_text(encoding="utf-8")
        self.fixture.write(self.fixture.frontier, first.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(self.fixture.frontier_review, "# Review\n\nStatus: Passed.\n")
        self.fixture.commit("docs: accept first child")
        self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            first_reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.frontier_review,
        )

        next_plan = Path("docs/build_tasks/next/plan.md")
        next_review = Path("docs/build_tasks/next/review.md")
        self.fixture.write(next_plan, "# Next Slice\n\n> 状态：Approved\n\n## Contract\n\nSecond.\n")
        self.fixture.write(next_review, "# Review\n\nPre-Start Review: PASS.\n")
        self.fixture.commit("docs: approve second child")
        second = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            next_plan,
            "--base",
            "HEAD",
            "--actor",
            "codex",
            "--approval-evidence",
            next_review,
        )
        self.assertEqual(root_base, second["root_review_base"])
        _, second_builder_token = self.fixture.claim("cursor")
        self.fixture.write("code.txt", "second slice\n")
        self.fixture.write(self.fixture.progress, "# Progress\n\nSecond slice implemented.\n")
        self.fixture.commit("feat: implement second child")
        self.fixture.relay(
            "submit",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "cursor",
            "--lease-token",
            second_builder_token,
            "--commit",
            "HEAD",
            "--evidence",
            self.fixture.progress,
        )
        _, second_reviewer_token = self.fixture.claim("codex")
        second_plan = (self.fixture.repo / next_plan).read_text(encoding="utf-8")
        self.fixture.write(next_plan, second_plan.replace("> 状态：Approved", "> 状态：Done"))
        self.fixture.write(next_review, "# Review\n\nStatus: Passed.\n")
        self.fixture.commit("docs: accept second child")
        self.fixture.relay(
            "accept",
            "--worktree",
            self.fixture.repo,
            "--actor",
            "codex",
            "--lease-token",
            second_reviewer_token,
            "--commit",
            "HEAD",
            "--evidence",
            next_review,
        )

        wrong = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.task,
            "--base",
            "HEAD",
            "--phase",
            "ready_to_review",
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
            expect=5,
        )
        self.assertEqual("base_drift", wrong["kind"])
        final_review = self.fixture.relay(
            "restart",
            "--worktree",
            self.fixture.repo,
            "--task",
            self.fixture.task,
            "--frontier",
            self.fixture.task,
            "--base",
            root_base,
            "--phase",
            "ready_to_review",
            "--actor",
            "codex",
            "--approval-evidence",
            self.fixture.parent_review,
        )
        self.assertEqual("ready_to_review", final_review["phase"])
        self.assertEqual(root_base, final_review["assignment_base"])
        self.assertEqual(root_base, final_review["root_review_base"])

    def test_state_write_failure_restores_derived_handoff(self) -> None:
        self.fixture.approved()
        state = self.fixture.start()
        state_file = self.fixture.state / f"{state['relay_id']}.json"
        state_before = state_file.read_bytes()
        handoff = Path(state["handoff_path"])
        handoff_before = handoff.read_bytes()

        spec = importlib.util.spec_from_file_location("relay_under_test", SCRIPT)
        assert spec and spec.loader
        relay = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(relay)
        loaded = json.loads(state_before)
        loaded["revision"] += 1
        real_atomic_write = relay.atomic_write

        def fail_state_write(path: Path, data: bytes) -> None:
            if path == state_file:
                raise OSError("simulated state write failure")
            real_atomic_write(path, data)

        with mock.patch.dict(os.environ, self.fixture.env, clear=True), mock.patch.object(
            relay, "atomic_write", side_effect=fail_state_write
        ):
            with self.assertRaises(relay.RelayError) as caught:
                relay.persist(loaded)
        self.assertEqual("state_write_failed", caught.exception.kind)
        self.assertEqual(state_before, state_file.read_bytes())
        self.assertEqual(handoff_before, handoff.read_bytes())


if __name__ == "__main__":
    unittest.main()
