#!/usr/bin/env python3
"""Atomic, repository-external baton state for coding-agent-delivery-loop."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Iterator, Sequence


SCHEMA_VERSION = 5
SKILL_NAME = "coding-agent-delivery-loop"
STATE_ENV = "CODING_AGENT_DELIVERY_LOOP_STATE_DIR"
HANDOFF_ENV = "CODING_AGENT_DELIVERY_LOOP_HANDOFF_DIR"

PHASE_MODEL: dict[str, dict[str, Any]] = {
    "ready_to_execute": {
        "owner": "builder",
        "claim": "executing",
        "boundary": True,
        "discoverable": True,
        "action": "Configured builder claims and implements only the approved frontier.",
    },
    "executing": {
        "owner": "builder",
        "claim": None,
        "boundary": False,
        "discoverable": True,
        "action": "Lease owner resumes the interrupted implementation in place.",
    },
    "rework_ready": {
        "owner": "builder",
        "claim": "reworking",
        "boundary": True,
        "discoverable": True,
        "action": "Configured builder claims and resolves only canonical review findings.",
    },
    "reworking": {
        "owner": "builder",
        "claim": None,
        "boundary": False,
        "discoverable": True,
        "action": "Lease owner resumes the interrupted rework in place.",
    },
    "ready_to_review": {
        "owner": "reviewer",
        "claim": "reviewing",
        "boundary": True,
        "discoverable": True,
        "action": "Configured reviewer claims and reviews the cumulative fixed-base diff.",
    },
    "reviewing": {
        "owner": "reviewer",
        "claim": None,
        "boundary": False,
        "discoverable": True,
        "action": "Lease owner resumes independent review and records a verdict.",
    },
    "blocked": {
        "owner": "planner",
        "claim": None,
        "boundary": False,
        "discoverable": True,
        "action": "Planner reports the recorded blocker and coordinates its explicit resolution.",
    },
    "accepted": {
        "owner": "planner",
        "claim": None,
        "boundary": True,
        "discoverable": True,
        "action": "Planner reports acceptance and evaluates the next repository gate.",
    },
    "closed": {
        "owner": "planner",
        "claim": None,
        "boundary": True,
        "discoverable": False,
        "action": "Terminal parent task is complete; no further delivery action is routed.",
    },
}
VALID_PHASES = set(PHASE_MODEL)
BOUNDARY_PHASES = {phase for phase, model in PHASE_MODEL.items() if model["boundary"]}
OWNED_PHASES = {phase for phase, model in PHASE_MODEL.items() if not model["boundary"] and phase not in {"blocked"}}
BLOCK_REASONS = {"user_decision", "authority_drift", "evidence", "ownership", "environment"}
INTERNAL_BLOCK_REASONS = {"reapproved"}
RESUMABLE_BLOCK_REASONS = {"evidence", "environment", "ownership", "reapproved"}

MD_STATUS_RE = re.compile(r"^>\s*(?:状态|Status)\s*[:：]\s*(.*?)\s*$")
YAML_STATUS_RE = re.compile(
    r"^(?:status|approval_state):[ \t]*(?:\"([^\"\r\n]+)\"|'([^'\r\n]+)'|([^\"'#\r\n]+?))[ \t]*$"
)
MD_ADMIN_RE = re.compile(r"^>\s*(?:状态|Status|完成时间|Completed(?:\s+at|\s+time)?)\s*[:：]")
YAML_ADMIN_RE = re.compile(r"^(?:status|approval_state|completed_at|completed_time):")
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
RELAY_ID_RE = re.compile(r"^[0-9a-f]{20}$")
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_DERIVED_HANDOFF_BYTES = 1024 * 1024


class RelayError(Exception):
    def __init__(self, message: str, *, code: int = 5, kind: str = "invariant_failed") -> None:
        super().__init__(message)
        self.code = code
        self.kind = kind


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def state_root() -> Path:
    override = os.environ.get(STATE_ENV)
    if override:
        return Path(override).expanduser().absolute()
    xdg = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "state"
    return (base / SKILL_NAME).absolute()


def handoff_root() -> Path:
    override = os.environ.get(HANDOFF_ENV)
    if override:
        return Path(override).expanduser().absolute()
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    base = Path(runtime).expanduser() if runtime else Path(tempfile.gettempdir())
    return (base / f"{SKILL_NAME}-{os.getuid()}").absolute()


def ensure_private_dir(path: Path) -> None:
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        raise RelayError(f"cannot create managed storage root: {path}", kind="unsafe_storage") from exc
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RelayError(f"managed storage root is not a real directory: {path}", kind="unsafe_storage") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid():
            raise RelayError(f"managed storage root is not owned by this user: {path}", kind="unsafe_storage")
        os.fchmod(descriptor, 0o700)
    finally:
        os.close(descriptor)


def run_git(root: Path, args: Sequence[str], *, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RelayError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def git_root(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    if not candidate.exists():
        raise RelayError(f"worktree does not exist: {candidate}")
    result = subprocess.run(
        ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RelayError(f"not inside a Git worktree: {candidate}")
    return Path(result.stdout.strip()).resolve()


def current_branch(root: Path) -> str:
    branch = run_git(root, ["symbolic-ref", "--quiet", "--short", "HEAD"], check=False)
    if not branch:
        raise RelayError("detached HEAD cannot own a baton")
    return branch


def head_sha(root: Path) -> str:
    return run_git(root, ["rev-parse", "HEAD"])


def resolve_commit(root: Path, ref: str) -> str:
    return run_git(root, ["rev-parse", "--verify", f"{ref}^{{commit}}"])


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def dirty_entries(root: Path) -> list[str]:
    output = run_git(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    return output.splitlines() if output else []


def require_clean(root: Path) -> None:
    dirty = dirty_entries(root)
    if dirty:
        preview = "; ".join(dirty[:8])
        raise RelayError(f"handoff boundary is dirty: {preview}", kind="ownership_conflict")


def git_fingerprint(root: Path) -> str:
    common = Path(run_git(root, ["rev-parse", "--git-common-dir"]))
    if not common.is_absolute():
        common = (root / common).resolve()
    payload = f"{common.resolve()}\0{run_git(root, ['rev-parse', '--show-object-format'])}"
    return hashlib.sha256(payload.encode()).hexdigest()


def relay_id_for(root: Path) -> str:
    payload = f"{git_fingerprint(root)}\0{root.resolve()}"
    return hashlib.sha256(payload.encode()).hexdigest()[:20]


def path_inside(root: Path, value: str | Path, *, tracked_at: str | None = None) -> tuple[Path, str]:
    candidate = Path(value).expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise RelayError(f"symlink is not a valid authority/evidence path: {candidate}", kind="authority_drift")
    path = candidate.resolve()
    try:
        relative = path.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise RelayError(f"path escapes worktree: {path}") from exc
    if not path.is_file():
        raise RelayError(f"required file does not exist: {path}")
    if tracked_at is not None:
        result = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{tracked_at}:{relative}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            raise RelayError(f"evidence is not committed at {tracked_at}: {relative}")
    return path, relative


def git_blob(root: Path, ref: str, relative: str) -> tuple[str, str, bytes]:
    tree = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-z", ref, "--", relative],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if tree.returncode != 0 or not tree.stdout:
        detail = tree.stderr.decode(errors="replace").strip()
        raise RelayError(f"tracked blob missing at {ref}:{relative}: {detail}", kind="authority_drift")
    records = [record for record in tree.stdout.split(b"\0") if record]
    if len(records) != 1 or b"\t" not in records[0]:
        raise RelayError(f"ambiguous tree entry at {ref}:{relative}", kind="authority_drift")
    metadata, _ = records[0].split(b"\t", 1)
    fields = metadata.decode("ascii").split()
    if len(fields) != 3:
        raise RelayError(f"malformed tree entry at {ref}:{relative}", kind="authority_drift")
    mode, kind, oid = fields
    if kind != "blob" or not mode.startswith("100"):
        raise RelayError(f"authority/evidence is not a regular Git blob at {ref}:{relative}", kind="authority_drift")
    blob = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{relative}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if blob.returncode != 0:
        detail = blob.stderr.decode(errors="replace").strip()
        raise RelayError(f"cannot read blob at {ref}:{relative}: {detail}", kind="authority_drift")
    return mode, oid, blob.stdout


def regular_worktree_bytes(root: Path, relative: str) -> bytes:
    path = root / relative
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RelayError(f"required path disappeared: {relative}", kind="authority_drift") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise RelayError(f"required path is not a regular file: {relative}", kind="authority_drift")
    return path.read_bytes()


def dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def require_identifier(value: str, label: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value):
        raise RelayError(f"invalid {label}: {value!r}")
    return value


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frontmatter_end(lines: Sequence[str]) -> int | None:
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            return index
    raise RelayError("unterminated YAML frontmatter cannot establish approval", kind="not_approved")


def markdown_status_entry(lines: Sequence[str]) -> tuple[int, str] | None:
    if not lines or not lines[0].startswith("# "):
        return None
    index = 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines):
        return None
    match = MD_STATUS_RE.match(lines[index].rstrip("\r\n"))
    if not match:
        return None
    return index, match.group(1).strip()


def normalize_contract(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RelayError("contract authorities must be UTF-8 text") from exc
    lines = text.splitlines(keepends=True)
    yaml_end = frontmatter_end(lines)
    normalized: list[str] = []
    markdown_entry = None if yaml_end is not None else markdown_status_entry(lines)
    in_markdown_metadata = False
    for index, line in enumerate(lines):
        if yaml_end is not None and 0 < index < yaml_end and YAML_ADMIN_RE.match(line):
            continue
        if markdown_entry and index == markdown_entry[0]:
            in_markdown_metadata = True
        if in_markdown_metadata:
            if line.startswith(">"):
                if MD_ADMIN_RE.match(line):
                    continue
            else:
                in_markdown_metadata = False
        normalized.append(line)
    return "".join(normalized).encode("utf-8")


def canonical_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    values: list[str] = []
    yaml_end = frontmatter_end(lines)
    if yaml_end is not None:
        for line in lines[1:yaml_end]:
            match = YAML_STATUS_RE.match(line)
            if match:
                values.append(next(group.strip() for group in match.groups() if group is not None))
    else:
        entry = markdown_status_entry(lines)
        if entry:
            values.append(entry[1])
    if len(values) != 1:
        raise RelayError(
            f"expected exactly one canonical status field in {path}; found {len(values)}",
            kind="not_approved",
        )
    return values[0]


def require_status(path: Path, allowed: set[str]) -> None:
    actual = canonical_status(path)
    if actual not in allowed:
        expected = ", ".join(sorted(allowed))
        raise RelayError(f"{path} status is {actual!r}; expected exact value in {{{expected}}}", kind="not_approved")


def manifest_entry(
    root: Path, relative: str, snapshot: str, *, admin_status_mutable: bool = False
) -> dict[str, Any]:
    mode, blob, data = git_blob(root, snapshot, relative)
    if regular_worktree_bytes(root, relative) != data:
        raise RelayError(f"working authority differs from {snapshot}:{relative}", kind="authority_drift")
    return {
        "path": relative,
        "snapshot_commit": snapshot,
        "mode": mode,
        "blob_oid": blob,
        "sha256": sha256(data),
        "normalized_sha256": sha256(normalize_contract(data)),
        "admin_status_mutable": admin_status_mutable,
    }


def next_role(state: dict[str, Any]) -> str | None:
    if state["phase"] == "closed":
        return None
    if state["phase"] == "blocked" and state.get("block_reason") == "reapproved":
        owner = state.get("interrupted_owner")
        if owner:
            return owner
    return state["roles"][PHASE_MODEL[state["phase"]]["owner"]]


def state_path(relay_id: str) -> Path:
    if not RELAY_ID_RE.fullmatch(relay_id):
        raise RelayError(f"malformed relay id: {relay_id!r}", kind="malformed_state")
    return state_root() / f"{relay_id}.json"


def handoff_path(relay_id: str) -> Path:
    if not RELAY_ID_RE.fullmatch(relay_id):
        raise RelayError(f"malformed relay id: {relay_id!r}", kind="malformed_state")
    return handoff_root() / f"{relay_id}.md"


def atomic_write(path: Path, data: bytes) -> None:
    ensure_private_dir(path.parent)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(0o600)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_existing_derived_handoff(path: Path) -> bytes | None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or metadata.st_size > MAX_DERIVED_HANDOFF_BYTES
    ):
        raise RelayError(f"existing derived handoff is unsafe: {path}", kind="handoff_failed")
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RelayError(f"cannot safely open existing derived handoff: {path}", kind="handoff_failed") from exc
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
            raise RelayError(f"derived handoff changed during validation: {path}", kind="handoff_failed")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read(MAX_DERIVED_HANDOFF_BYTES + 1)
        if len(data) > MAX_DERIVED_HANDOFF_BYTES:
            raise RelayError(f"existing derived handoff is too large: {path}", kind="handoff_failed")
        return data
    finally:
        os.close(descriptor)


@contextlib.contextmanager
def locked_state() -> Iterator[None]:
    root = state_root()
    ensure_private_dir(root)
    lock_path = root / ".lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_handoff(state: dict[str, Any]) -> str:
    phase = state["phase"]
    action = PHASE_MODEL[phase]["action"]
    if phase == "blocked" and state.get("block_reason") == "reapproved":
        action = "Recorded interrupted owner resumes the re-approved work in place and receives a new lease."
    evidence = state.get("evidence_refs") or []
    blocker = state.get("block_reason")
    suggestions = state.get("suggested_skills") or [SKILL_NAME]
    lines = [
        "# Coding Agent Delivery Loop Handoff",
        "",
        "```yaml",
        f"task: {yaml_string(state['task'])}",
        f"current_state: {yaml_string(phase)}",
        "facts:",
        f"  - {yaml_string('worktree: ' + state['worktree'])}",
        f"  - {yaml_string('branch: ' + state['branch'])}",
        f"  - {yaml_string('assignment_base: ' + state['assignment_base'])}",
        f"  - {yaml_string('root_review_base: ' + state['root_review_base'])}",
        f"  - {yaml_string('current_head: ' + state['current_head'])}",
        f"  - {yaml_string('frontier: ' + state['frontier'])}",
        f"  - {yaml_string('baton_revision: ' + str(state['revision']))}",
        "assumptions: []",
        "decisions:",
        f"  - {yaml_string('Approved contract is referenced by the task/frontier paths and authority hashes in baton ' + state['relay_id'])}",
        "constraints:",
        f"  - {yaml_string('No next role is routed; the delivery baton is terminal' if phase == 'closed' else 'Only the configured next role may perform the phase action: ' + str(state.get('next_role')))}",
        f"  - {yaml_string('Repository authority outranks this routing baton')}",
        "risks:",
        f"  - {yaml_string('Authority, ownership, or evidence drift blocks the baton rather than changing the plan')}",
    ]
    if blocker:
        lines.extend(["open_questions:", f"  - {yaml_string('block_reason: ' + blocker)}"])
    else:
        lines.append("open_questions: []")
    lines.extend(
        [
            "allowed_actions:",
            f"  - {yaml_string(action)}",
            "forbidden_actions:",
            f"  - {yaml_string('Scope or contract changes without repository re-approval')}",
            f"  - {yaml_string('Merge, push, release, destructive cleanup, or secret persistence without explicit authority')}",
            "expected_outputs:",
            f"  - {yaml_string('Canonical progress/review evidence and the transition required by phase ' + phase)}",
            "validation:",
            f"  authority_manifest_entries: {len(state['authority_manifest'])}",
            f"  sealed_authority_entries: {len(state['sealed_authority_manifest'])}",
            f"  evidence_refs: {json.dumps(evidence, ensure_ascii=False)}",
            "```",
            "",
            "## Suggested skills",
            "",
        ]
    )
    lines.extend(f"- `${item}`" for item in suggestions)
    lines.append("")
    return "\n".join(lines)


def validate_relative_path(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise RelayError(f"malformed {label}: {value!r}", kind="malformed_state")


def validate_manifest(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
    unique_paths: bool = True,
) -> None:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise RelayError(f"malformed {label}", kind="malformed_state")
    required = {
        "path": str,
        "snapshot_commit": str,
        "mode": str,
        "blob_oid": str,
        "sha256": str,
        "normalized_sha256": str,
        "admin_status_mutable": bool,
    }
    for entry in value:
        if not isinstance(entry, dict):
            raise RelayError(f"malformed {label} entry", kind="malformed_state")
        for key, expected_type in required.items():
            if key not in entry or not isinstance(entry[key], expected_type):
                raise RelayError(f"malformed {label} entry field {key}", kind="malformed_state")
        validate_relative_path(entry["path"], f"{label} path")
        if not COMMIT_RE.fullmatch(entry["snapshot_commit"]):
            raise RelayError(f"malformed {label} snapshot commit", kind="malformed_state")
        if entry["mode"] not in {"100644", "100755"}:
            raise RelayError(f"malformed {label} blob mode", kind="malformed_state")
        if not COMMIT_RE.fullmatch(entry["blob_oid"]):
            raise RelayError(f"malformed {label} blob oid", kind="malformed_state")
        if not HASH_RE.fullmatch(entry["sha256"]) or not HASH_RE.fullmatch(entry["normalized_sha256"]):
            raise RelayError(f"malformed {label} digest", kind="malformed_state")
    identities = [entry["path"] if unique_paths else (entry["path"], entry["snapshot_commit"]) for entry in value]
    if len(identities) != len(set(identities)):
        raise RelayError(f"duplicate entries in {label}", kind="malformed_state")


def validate_state_shape(state: Any) -> None:
    required_types = {
        "schema_version": int,
        "relay_id": str,
        "revision": int,
        "phase": str,
        "roles": dict,
        "worktree": str,
        "branch": str,
        "git_fingerprint": str,
        "task": str,
        "frontier": str,
        "assignment_base": str,
        "root_review_base": str,
        "current_head": str,
        "authority_manifest": list,
        "sealed_authority_manifest": list,
        "approval_evidence_manifest": list,
        "transition_evidence_manifest": list,
        "evidence_refs": list,
        "cycle": int,
        "suggested_skills": list,
    }
    if not isinstance(state, dict):
        raise RelayError("baton state is not an object", kind="malformed_state")
    for key, expected_type in required_types.items():
        if key not in state or not isinstance(state[key], expected_type):
            raise RelayError(f"malformed baton field {key}", kind="malformed_state")
    if state["schema_version"] != SCHEMA_VERSION:
        raise RelayError(f"unsupported baton schema: {state['schema_version']}", kind="malformed_state")
    if state["phase"] not in VALID_PHASES:
        raise RelayError(f"unknown baton phase: {state['phase']}", kind="malformed_state")
    if state["revision"] < 1 or state["cycle"] < 0:
        raise RelayError("invalid baton revision/cycle", kind="malformed_state")
    if not RELAY_ID_RE.fullmatch(state["relay_id"]):
        raise RelayError(f"malformed relay id: {state['relay_id']!r}", kind="malformed_state")
    if not Path(state["worktree"]).is_absolute():
        raise RelayError("baton worktree must be absolute", kind="malformed_state")
    if set(state["roles"]) != {"planner", "builder", "reviewer"}:
        raise RelayError("malformed role map", kind="malformed_state")
    for role, actor in state["roles"].items():
        require_identifier(actor, f"{role} role")
    if state["roles"]["builder"] == state["roles"]["reviewer"]:
        raise RelayError("builder and reviewer are not independent", kind="malformed_state")
    interrupted_owner = state.get("interrupted_owner")
    if interrupted_owner is not None and (
        not isinstance(interrupted_owner, str) or not IDENTIFIER_RE.fullmatch(interrupted_owner)
    ):
        raise RelayError("malformed interrupted owner", kind="malformed_state")
    if "next_role" not in state or (state["next_role"] is not None and not isinstance(state["next_role"], str)):
        raise RelayError("malformed baton next_role", kind="malformed_state")
    if state["next_role"] != next_role(state):
        raise RelayError("baton next_role contradicts phase", kind="malformed_state")
    for field in ("assignment_base", "root_review_base", "current_head"):
        if not COMMIT_RE.fullmatch(state[field]):
            raise RelayError(f"malformed baton commit {field}", kind="malformed_state")
    validate_relative_path(state["task"], "task path")
    validate_relative_path(state["frontier"], "frontier path")
    validate_manifest(state["authority_manifest"], "authority manifest")
    validate_manifest(state["sealed_authority_manifest"], "sealed authority manifest", allow_empty=True)
    validate_manifest(state["approval_evidence_manifest"], "approval evidence manifest")
    validate_manifest(
        state["transition_evidence_manifest"],
        "transition evidence manifest",
        allow_empty=True,
        unique_paths=False,
    )
    authority_by_path = {entry["path"]: entry for entry in state["authority_manifest"]}
    if state["task"] not in authority_by_path or state["frontier"] not in authority_by_path:
        raise RelayError("task/frontier missing from authority manifest", kind="malformed_state")
    mutable_paths = {entry["path"] for entry in state["authority_manifest"] if entry["admin_status_mutable"]}
    if mutable_paths != {state["frontier"]}:
        raise RelayError("only the frontier may have mutable administrative status", kind="malformed_state")
    if any(entry["admin_status_mutable"] for entry in state["approval_evidence_manifest"]):
        raise RelayError("approval evidence cannot be administratively mutable", kind="malformed_state")
    if any(entry["admin_status_mutable"] for entry in state["sealed_authority_manifest"]):
        raise RelayError("sealed authority cannot be administratively mutable", kind="malformed_state")
    if any(entry["admin_status_mutable"] for entry in state["transition_evidence_manifest"]):
        raise RelayError("transition evidence cannot be administratively mutable", kind="malformed_state")
    for ref in state["evidence_refs"]:
        validate_relative_path(ref, "evidence reference")
    lease = state.get("lease")
    if lease is not None:
        if not isinstance(lease, dict) or set(lease) != {"actor", "claimed_at", "head", "token_sha256"}:
            raise RelayError("malformed baton lease", kind="malformed_state")
        if not all(isinstance(value, str) and value for value in lease.values()):
            raise RelayError("malformed baton lease values", kind="malformed_state")
        require_identifier(lease["actor"], "lease actor")
        if not COMMIT_RE.fullmatch(lease["head"]) or not HASH_RE.fullmatch(lease["token_sha256"]):
            raise RelayError("malformed baton lease token hash", kind="malformed_state")
    if state["phase"] in OWNED_PHASES and lease is None:
        raise RelayError("owned phase is missing its lease", kind="malformed_state")
    if state["phase"] in OWNED_PHASES and lease is not None:
        expected_lease_actor = state["roles"][PHASE_MODEL[state["phase"]]["owner"]]
        if lease["actor"] != expected_lease_actor:
            raise RelayError("owned phase lease belongs to the wrong role", kind="malformed_state")
    if state["phase"] not in OWNED_PHASES and lease is not None:
        raise RelayError("boundary/blocked phase cannot retain a lease", kind="malformed_state")
    blocked_head = state.get("blocked_head")
    if blocked_head is not None and (not isinstance(blocked_head, str) or not COMMIT_RE.fullmatch(blocked_head)):
        raise RelayError("malformed blocked_head", kind="malformed_state")
    if state["phase"] == "blocked":
        interrupted_phase = state.get("interrupted_phase")
        if state.get("block_reason") not in (BLOCK_REASONS | INTERNAL_BLOCK_REASONS) or interrupted_phase not in VALID_PHASES:
            raise RelayError("blocked baton lacks interruption metadata", kind="malformed_state")
        if interrupted_phase in OWNED_PHASES:
            expected_interrupted_owner = state["roles"][PHASE_MODEL[interrupted_phase]["owner"]]
            if interrupted_owner != expected_interrupted_owner:
                raise RelayError("blocked baton has the wrong interrupted owner", kind="malformed_state")
        elif interrupted_owner is not None:
            raise RelayError("boundary interruption cannot have an owner", kind="malformed_state")
        if state.get("block_reason") == "reapproved" and interrupted_phase not in OWNED_PHASES:
            raise RelayError("reapproved baton must route to an owned phase", kind="malformed_state")
        if blocked_head is None:
            raise RelayError("blocked baton lacks blocked_head", kind="malformed_state")
    elif blocked_head is not None:
        raise RelayError("non-blocked baton retains blocked_head", kind="malformed_state")
    elif state.get("block_reason") is not None or state.get("interrupted_phase") is not None or interrupted_owner is not None:
        raise RelayError("non-blocked baton retains interruption metadata", kind="malformed_state")


def refresh_handoff(state: dict[str, Any]) -> None:
    expected = relay_id_for(git_root(state["worktree"]))
    if state["relay_id"] != expected:
        raise RelayError("relay id does not match selected worktree", kind="malformed_state")
    state["handoff_path"] = str(handoff_path(expected))
    try:
        atomic_write(Path(state["handoff_path"]), render_handoff(state).encode("utf-8"))
    except (OSError, RelayError) as exc:
        raise RelayError(f"cannot write derived handoff: {exc}", kind="handoff_failed") from exc


def persist(state: dict[str, Any]) -> None:
    root = git_root(state["worktree"])
    expected = relay_id_for(root)
    if state["relay_id"] != expected:
        raise RelayError("relay id does not match selected worktree", kind="malformed_state")
    state["next_role"] = next_role(state)
    state["updated_at"] = now()
    state["handoff_path"] = str(handoff_path(expected))
    validate_state_shape(state)
    payload = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    derived_path = Path(state["handoff_path"])
    try:
        ensure_private_dir(derived_path.parent)
        previous_handoff = read_existing_derived_handoff(derived_path)
    except RelayError as exc:
        raise RelayError(f"cannot prepare derived handoff: {exc}", kind="handoff_failed") from exc
    refresh_handoff(state)
    try:
        atomic_write(state_path(expected), payload)
    except OSError as exc:
        try:
            if previous_handoff is None:
                derived_path.unlink(missing_ok=True)
            else:
                atomic_write(derived_path, previous_handoff)
        except OSError as rollback_exc:
            raise RelayError(
                f"cannot commit baton state ({exc}); derived handoff rollback also failed ({rollback_exc})",
                kind="state_write_failed",
            ) from exc
        raise RelayError(f"cannot commit baton state: {exc}", kind="state_write_failed") from exc


def load_path(path: Path) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RelayError(f"cannot read baton state {path}: {exc}", kind="malformed_state") from exc
    validate_state_shape(state)
    return state


def load_for_worktree(worktree: str | Path) -> dict[str, Any]:
    root = git_root(worktree)
    expected = relay_id_for(root)
    path = state_path(expected)
    if not path.is_file():
        raise RelayError(f"no baton for worktree {root}", code=3, kind="no_baton")
    state = load_path(path)
    if state["relay_id"] != expected or Path(state["worktree"]).resolve() != root:
        raise RelayError("baton identity does not match selected worktree", kind="malformed_state")
    return state


def select_state(worktree: str | None) -> dict[str, Any]:
    if worktree:
        return load_for_worktree(worktree)
    try:
        root = git_root(Path.cwd())
        candidate = state_path(relay_id_for(root))
        if candidate.is_file():
            return load_path(candidate)
        raise RelayError(f"no baton for current worktree {root}", code=3, kind="no_baton")
    except RelayError:
        if subprocess.run(
            ["git", "-C", str(Path.cwd()), "rev-parse", "--is-inside-work-tree"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0:
            raise
    root = state_root()
    if not root.is_dir():
        raise RelayError("no baton state directory", code=3, kind="no_baton")
    candidates = []
    for path in sorted(root.glob("*.json")):
        state = load_path(path)
        if PHASE_MODEL[state["phase"]]["discoverable"]:
            candidates.append(state)
    if not candidates:
        raise RelayError("no active baton", code=3, kind="no_baton")
    if len(candidates) > 1:
        summary = ", ".join(f"{item['relay_id']}:{item['worktree']}:{item['phase']}" for item in candidates)
        raise RelayError(f"multiple active batons; open the intended worktree: {summary}", code=4, kind="ambiguous")
    return candidates[0]


def verify_authority(state: dict[str, Any], *, allow_admin: bool = False) -> None:
    root = Path(state["worktree"])
    current = head_sha(root)
    for entry in state["authority_manifest"]:
        relative = entry["path"]
        worktree_data = regular_worktree_bytes(root, relative)
        mode, blob_oid, committed_data = git_blob(root, current, relative)
        if worktree_data != committed_data:
            raise RelayError(f"working authority differs from HEAD: {relative}", kind="authority_drift")
        mutable_admin = allow_admin and entry["admin_status_mutable"]
        if mode != entry["mode"]:
            raise RelayError(f"authority mode drift: {relative}", kind="authority_drift")
        if mutable_admin:
            matches = sha256(normalize_contract(committed_data)) == entry["normalized_sha256"]
        else:
            matches = sha256(committed_data) == entry["sha256"] and blob_oid == entry["blob_oid"]
        if not matches:
            raise RelayError(f"authority drift: {relative}", kind="authority_drift")

    task_allowed = {"Approved", "Done"} if allow_admin and state["task"] == state["frontier"] else {"Approved"}
    frontier_allowed = {"Approved", "Done"} if allow_admin else {"Approved"}
    require_status(root / state["task"], task_allowed)
    require_status(root / state["frontier"], frontier_allowed)


def verify_sealed_authority(state: dict[str, Any]) -> None:
    root = Path(state["worktree"])
    current = head_sha(root)
    for entry in state["sealed_authority_manifest"]:
        relative = entry["path"]
        worktree_data = regular_worktree_bytes(root, relative)
        mode, blob_oid, committed_data = git_blob(root, current, relative)
        if (
            worktree_data != committed_data
            or mode != entry["mode"]
            or blob_oid != entry["blob_oid"]
            or sha256(committed_data) != entry["sha256"]
        ):
            raise RelayError(f"sealed accepted authority drift: {relative}", kind="authority_drift")


def verify_approval_evidence(state: dict[str, Any]) -> None:
    root = Path(state["worktree"])
    current = head_sha(root)
    for entry in state["approval_evidence_manifest"]:
        relative = entry["path"]
        try:
            snapshot_mode, snapshot_oid, snapshot_data = git_blob(root, entry["snapshot_commit"], relative)
            current_mode, _, current_data = git_blob(root, current, relative)
            worktree_data = regular_worktree_bytes(root, relative)
        except RelayError as exc:
            raise RelayError(f"approval evidence drift: {relative}: {exc}", kind="approval_evidence_drift") from exc
        if (
            snapshot_mode != entry["mode"]
            or snapshot_oid != entry["blob_oid"]
            or sha256(snapshot_data) != entry["sha256"]
            or not current_mode.startswith("100")
            or worktree_data != current_data
        ):
            raise RelayError(f"approval evidence drift: {relative}", kind="approval_evidence_drift")


def verify_transition_evidence(state: dict[str, Any]) -> None:
    root = Path(state["worktree"])
    current = head_sha(root)
    for entry in state["transition_evidence_manifest"]:
        relative = entry["path"]
        try:
            snapshot_mode, snapshot_oid, snapshot_data = git_blob(root, entry["snapshot_commit"], relative)
            current_mode, _, current_data = git_blob(root, current, relative)
            worktree_data = regular_worktree_bytes(root, relative)
        except RelayError as exc:
            raise RelayError(f"transition evidence drift: {relative}: {exc}", kind="evidence_drift") from exc
        if (
            snapshot_mode != entry["mode"]
            or snapshot_oid != entry["blob_oid"]
            or sha256(snapshot_data) != entry["sha256"]
            or current_mode != entry["mode"]
            or worktree_data != current_data
        ):
            raise RelayError(f"transition evidence drift: {relative}", kind="evidence_drift")


def verify_state(state: dict[str, Any], *, allow_admin: bool = False) -> dict[str, Any]:
    root = git_root(state["worktree"])
    current = head_sha(root)
    if state["phase"] == "blocked":
        warnings = []
        if current_branch(root) != state["branch"]:
            warnings.append("worktree branch changed")
        if git_fingerprint(root) != state["git_fingerprint"]:
            warnings.append("Git common-dir fingerprint changed")
        if not is_ancestor(root, state["assignment_base"], current):
            warnings.append("assignment base is no longer an ancestor of HEAD")
        if not is_ancestor(root, state["root_review_base"], current):
            warnings.append("parent fixed review base is no longer an ancestor of HEAD")
        if not is_ancestor(root, state["current_head"], current):
            warnings.append("interrupted handoff HEAD is no longer an ancestor of HEAD")
        if not is_ancestor(root, state["blocked_head"], current):
            warnings.append("blocked HEAD is no longer an ancestor of HEAD")
        try:
            verify_authority(state)
            verify_sealed_authority(state)
            verify_approval_evidence(state)
            verify_transition_evidence(state)
        except RelayError as exc:
            warnings.append(str(exc))
        return {"head": current, "dirty": dirty_entries(root), "authority": "blocked", "warnings": warnings}
    if root != Path(state["worktree"]).resolve():
        raise RelayError("worktree root changed", kind="ownership_conflict")
    if current_branch(root) != state["branch"]:
        raise RelayError("worktree branch changed", kind="ownership_conflict")
    if git_fingerprint(root) != state["git_fingerprint"]:
        raise RelayError("Git common-dir fingerprint changed", kind="ownership_conflict")
    if not is_ancestor(root, state["assignment_base"], current):
        raise RelayError("assignment base is no longer an ancestor of HEAD", kind="base_drift")
    if not is_ancestor(root, state["root_review_base"], current):
        raise RelayError("parent fixed review base is no longer an ancestor of HEAD", kind="base_drift")
    verify_authority(state, allow_admin=allow_admin or state["phase"] in {"accepted", "closed"})
    verify_sealed_authority(state)
    verify_approval_evidence(state)
    verify_transition_evidence(state)
    if state["phase"] in BOUNDARY_PHASES:
        if current != state["current_head"]:
            raise RelayError("HEAD moved after handoff", kind="ownership_conflict")
        require_clean(root)
    elif state["phase"] in OWNED_PHASES and not is_ancestor(root, state["current_head"], current):
        raise RelayError("owner HEAD no longer descends from the claimed handoff", kind="base_drift")
    return {"head": current, "dirty": dirty_entries(root), "authority": "verified"}


def output(
    state: dict[str, Any],
    verification: dict[str, Any] | None = None,
    *,
    lease_token: str | None = None,
) -> None:
    result = dict(state)
    if verification is not None:
        result["verification"] = verification
    if lease_token is not None:
        result["lease_token"] = lease_token
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


def collect_files(root: Path, values: Iterable[str], snapshot: str) -> list[str]:
    result = []
    for value in values:
        _, relative = path_inside(root, value, tracked_at=snapshot)
        result.append(relative)
    return dedupe(result)


def make_state(args: argparse.Namespace, *, prior: dict[str, Any] | None = None) -> dict[str, Any]:
    root = git_root(args.worktree)
    head = head_sha(root)
    base = resolve_commit(root, args.base)
    if prior:
        if root != Path(prior["worktree"]).resolve():
            raise RelayError("restart cannot migrate the owning worktree", kind="ownership_conflict")
        if current_branch(root) != prior["branch"]:
            raise RelayError("restart cannot migrate the owning branch", kind="ownership_conflict")
        if git_fingerprint(root) != prior["git_fingerprint"]:
            raise RelayError("restart cannot migrate the Git common-dir", kind="ownership_conflict")
    if prior and prior["phase"] == "blocked":
        if base != prior["assignment_base"]:
            raise RelayError(
                "blocked restart must preserve the original assignment/review base",
                kind="base_drift",
            )
        if not is_ancestor(root, base, head):
            raise RelayError("original assignment base is no longer an ancestor of HEAD", kind="base_drift")
        if not is_ancestor(root, prior["blocked_head"], head):
            raise RelayError("blocked work was removed from the restart history", kind="base_drift")
        if not is_ancestor(root, prior["current_head"], head):
            raise RelayError("interrupted handoff history was removed before restart", kind="base_drift")
    elif prior and prior["phase"] == "accepted" and not is_ancestor(root, prior["current_head"], head):
        raise RelayError("accepted history was removed before the next frontier", kind="base_drift")
    elif args.phase == "ready_to_execute" and base != head:
        raise RelayError("new builder assignment base must equal current HEAD", kind="base_drift")
    if args.phase == "ready_to_review" and not is_ancestor(root, base, head):
        raise RelayError("Final Review base must be an ancestor of current HEAD", kind="base_drift")
    require_clean(root)
    task_path, task = path_inside(root, args.task, tracked_at=head)
    frontier_path, frontier = path_inside(root, args.frontier, tracked_at=head)
    require_status(task_path, {"Approved"})
    require_status(frontier_path, {"Approved"})
    root_review_base = prior["root_review_base"] if prior else base
    if args.phase == "ready_to_review" and task == frontier and base != root_review_base:
        raise RelayError(
            "Parent Final Review must use the originally pinned root review base",
            kind="base_drift",
        )
    evidence = collect_files(root, args.approval_evidence, head)
    if not evidence:
        raise RelayError("at least one committed Pre-Start approval evidence file is required")
    prior_authorities = [entry["path"] for entry in prior["authority_manifest"]] if prior else []
    authorities = collect_files(root, [task, frontier, *prior_authorities, *args.authority], head)
    roles = {
        "planner": args.planner or (prior and prior["roles"]["planner"]),
        "builder": args.builder or (prior and prior["roles"]["builder"]),
        "reviewer": args.reviewer or (prior and prior["roles"]["reviewer"]),
    }
    if not all(roles.values()):
        raise RelayError("planner, builder, and reviewer roles are required")
    roles = {key: require_identifier(value, f"{key} role") for key, value in roles.items()}
    if roles["builder"] == roles["reviewer"]:
        raise RelayError("builder and reviewer must be independent actors", kind="role_conflict")
    if args.actor != roles["planner"]:
        raise RelayError(f"only configured planner {roles['planner']!r} may create a baton", kind="wrong_role")
    relay_id = relay_id_for(root)
    created = now()
    revision = (prior["revision"] + 1) if prior else 1
    suggestions = [require_identifier(item, "suggested skill") for item in dedupe([SKILL_NAME, *(args.suggested_skill or [])])]
    return {
        "schema_version": SCHEMA_VERSION,
        "relay_id": relay_id,
        "revision": revision,
        "phase": args.phase,
        "roles": roles,
        "worktree": str(root),
        "branch": current_branch(root),
        "git_fingerprint": git_fingerprint(root),
        "task": task,
        "frontier": frontier,
        "assignment_base": base,
        "root_review_base": root_review_base,
        "current_head": head,
        "implementation_head": head if args.phase == "ready_to_review" else None,
        "authority_manifest": [
            manifest_entry(root, item, head, admin_status_mutable=item == frontier) for item in authorities
        ],
        "sealed_authority_manifest": list(prior["sealed_authority_manifest"]) if prior else [],
        "approval_evidence_manifest": [manifest_entry(root, item, head) for item in evidence],
        "transition_evidence_manifest": list(prior["transition_evidence_manifest"]) if prior else [],
        "evidence_refs": list(prior["evidence_refs"]) if prior else [],
        "findings_ref": prior.get("findings_ref") if prior and prior["phase"] == "blocked" else None,
        "block_reason": None,
        "blocked_head": None,
        "interrupted_phase": None,
        "interrupted_owner": None,
        "cycle": prior["cycle"] if prior and prior["phase"] == "blocked" else 0,
        "lease": None,
        "suggested_skills": suggestions,
        "created_at": created,
        "updated_at": created,
        "next_role": None,
        "handoff_path": "",
    }


def prevalidate_start(args: argparse.Namespace) -> None:
    root = git_root(args.worktree)
    head = head_sha(root)
    task, _ = path_inside(root, args.task, tracked_at=head)
    frontier, _ = path_inside(root, args.frontier, tracked_at=head)
    require_status(task, {"Approved"})
    require_status(frontier, {"Approved"})
    require_clean(root)


def cmd_start(args: argparse.Namespace) -> None:
    prevalidate_start(args)
    root = git_root(args.worktree)
    with locked_state():
        path = state_path(relay_id_for(root))
        if path.exists():
            raise RelayError("baton already exists; use restart only from blocked/accepted")
        state = make_state(args)
        persist(state)
    output(state, verify_state(state))


def archive_prior(state: dict[str, Any]) -> None:
    archive = state_root() / "archive"
    ensure_private_dir(archive)
    stamp = dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    destination = archive / f"{state['relay_id']}-r{state['revision']}-{stamp}.json"
    atomic_write(destination, json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True).encode() + b"\n")


def cmd_restart(args: argparse.Namespace) -> None:
    prevalidate_start(args)
    with locked_state():
        prior = load_for_worktree(args.worktree)
        if prior["phase"] not in {"blocked", "accepted"}:
            raise RelayError("restart is allowed only from blocked or accepted")
        if args.actor != prior["roles"]["planner"]:
            raise RelayError(f"only configured planner {prior['roles']['planner']!r} may restart", kind="wrong_role")
        verify_sealed_authority(prior)
        if prior["phase"] == "blocked" and prior.get("block_reason") == "reapproved":
            raise RelayError("re-approved owned work must resume with its recorded owner", kind="ownership_conflict")
        if prior["phase"] == "blocked" and prior.get("block_reason") in {"user_decision", "authority_drift"}:
            if prior.get("interrupted_phase") in OWNED_PHASES:
                raise RelayError(
                    "decision/authority changes in an owned phase require reapprove before resume",
                    kind="not_approved",
                )
            evidence_refs(
                Path(prior["worktree"]),
                args.approval_evidence,
                head_sha(Path(prior["worktree"])),
                changed_since=prior["blocked_head"],
            )
        elif prior["phase"] == "blocked":
            verify_authority(prior)
            verify_approval_evidence(prior)
        if prior["phase"] == "accepted":
            verify_authority(prior, allow_admin=True)
            verify_approval_evidence(prior)
            require_status(Path(prior["worktree"]) / prior["frontier"], {"Done"})
        verify_transition_evidence(prior)
        state = make_state(args, prior=prior)
        archive_prior(prior)
        persist(state)
    output(state, verify_state(state))


def cmd_reapprove(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] != "blocked" or state.get("interrupted_phase") not in OWNED_PHASES:
            raise RelayError("reapprove requires a blocked owned phase", kind="ownership_conflict")
        if not state.get("interrupted_owner"):
            raise RelayError("reapprove requires a recorded interrupted owner", kind="ownership_conflict")
        if args.actor != state["roles"]["planner"]:
            raise RelayError(f"only configured planner {state['roles']['planner']!r} may reapprove", kind="wrong_role")

        root = git_root(args.worktree)
        head = head_sha(root)
        if root != Path(state["worktree"]).resolve() or current_branch(root) != state["branch"]:
            raise RelayError("reapproval cannot migrate the owning worktree/branch", kind="ownership_conflict")
        if git_fingerprint(root) != state["git_fingerprint"]:
            raise RelayError("reapproval cannot migrate the Git common-dir", kind="ownership_conflict")
        if (
            not is_ancestor(root, state["assignment_base"], head)
            or not is_ancestor(root, state["root_review_base"], head)
            or not is_ancestor(root, state["current_head"], head)
            or not is_ancestor(root, state["blocked_head"], head)
        ):
            raise RelayError(
                "reapproval history no longer contains the fixed base, interrupted handoff, and blocked work",
                kind="base_drift",
            )
        verify_transition_evidence(state)
        verify_sealed_authority(state)

        task_path, task = path_inside(root, args.task, tracked_at=head)
        frontier_path, frontier = path_inside(root, args.frontier, tracked_at=head)
        require_status(task_path, {"Approved"})
        require_status(frontier_path, {"Approved"})
        if task != state["task"] or frontier != state["frontier"]:
            raise RelayError("reapproval cannot replace the parent/frontier paths", kind="authority_drift")
        evidence = evidence_refs(
            root,
            args.approval_evidence,
            head,
            changed_since=state["blocked_head"],
        )
        prior_extra = [
            entry["path"]
            for entry in state["authority_manifest"]
            if entry["path"] not in {state["task"], state["frontier"]}
        ]
        authorities = collect_files(root, [task, frontier, *prior_extra, *args.authority], head)
        state["task"] = task
        state["frontier"] = frontier
        state["authority_manifest"] = [
            manifest_entry(root, item, head, admin_status_mutable=item == frontier) for item in authorities
        ]
        state["approval_evidence_manifest"] = [manifest_entry(root, item, head) for item in evidence]
        state["block_reason"] = "reapproved"
        state["blocked_head"] = head
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state))


def cmd_show(args: argparse.Namespace) -> None:
    with locked_state():
        state = select_state(args.worktree)
        verification = verify_state(state)
        refresh_handoff(state)
    output(state, verification)


def cmd_list(_: argparse.Namespace) -> None:
    root = state_root()
    rows = []
    if root.is_dir():
        for path in sorted(root.glob("*.json")):
            state = load_path(path)
            rows.append(
                {
                    "relay_id": state["relay_id"],
                    "phase": state["phase"],
                    "next_role": state.get("next_role"),
                    "worktree": state["worktree"],
                    "task": state["task"],
                    "frontier": state["frontier"],
                }
            )
    print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_claim(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        verification = verify_state(state)
        phase = state["phase"]
        if phase in OWNED_PHASES:
            raise RelayError(
                "baton already has an active lease; use takeover only after confirming the old session ended",
                kind="ownership_conflict",
            )
        target = PHASE_MODEL[phase]["claim"]
        if target is None:
            raise RelayError(f"phase {phase!r} cannot be claimed")
        expected = expected_actor(state)
        if args.actor != expected:
            raise RelayError(f"phase {phase} belongs to {expected!r}", kind="wrong_role")
        state["phase"] = target
        token = issue_lease(state, args.actor)
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state), lease_token=token)


def issue_lease(state: dict[str, Any], actor: str) -> str:
    token = secrets.token_hex(32)
    state["lease"] = {
        "actor": actor,
        "claimed_at": now(),
        "head": head_sha(Path(state["worktree"])),
        "token_sha256": sha256(token.encode("utf-8")),
    }
    return token


def cmd_takeover(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        verify_state(state)
        if state["phase"] not in OWNED_PHASES or not state.get("lease"):
            raise RelayError("takeover requires an active owned phase", kind="ownership_conflict")
        expected = expected_actor(state)
        if args.actor != expected:
            raise RelayError(f"owned phase belongs to {expected!r}", kind="wrong_role")
        token = issue_lease(state, args.actor)
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state), lease_token=token)


def verify_resumable_block(state: dict[str, Any]) -> dict[str, Any]:
    root = git_root(state["worktree"])
    current = head_sha(root)
    if root != Path(state["worktree"]).resolve():
        raise RelayError("worktree root changed", kind="ownership_conflict")
    if current_branch(root) != state["branch"]:
        raise RelayError("worktree branch changed", kind="ownership_conflict")
    if git_fingerprint(root) != state["git_fingerprint"]:
        raise RelayError("Git common-dir fingerprint changed", kind="ownership_conflict")
    if not is_ancestor(root, state["assignment_base"], current):
        raise RelayError("assignment base is no longer an ancestor of HEAD", kind="base_drift")
    if not is_ancestor(root, state["root_review_base"], current):
        raise RelayError("parent fixed review base is no longer an ancestor of HEAD", kind="base_drift")
    if not is_ancestor(root, state["current_head"], current):
        raise RelayError("interrupted work no longer descends from its handoff", kind="base_drift")
    if not is_ancestor(root, state["blocked_head"], current):
        raise RelayError("blocked work no longer descends into current HEAD", kind="base_drift")
    verify_authority(state)
    verify_sealed_authority(state)
    verify_approval_evidence(state)
    verify_transition_evidence(state)
    return {"head": current, "dirty": dirty_entries(root), "authority": "verified"}


def cmd_resume(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] != "blocked" or state.get("block_reason") not in RESUMABLE_BLOCK_REASONS:
            raise RelayError(
                "resume is limited to evidence/environment interruptions; other blockers require planner restart",
                kind="ownership_conflict",
            )
        interrupted = state.get("interrupted_phase")
        if interrupted not in OWNED_PHASES:
            raise RelayError("blocked baton has no resumable owned phase", kind="ownership_conflict")
        expected = state["roles"][PHASE_MODEL[interrupted]["owner"]]
        if args.actor != expected or state.get("interrupted_owner") != args.actor:
            raise RelayError(f"interrupted phase belongs to {expected!r}", kind="wrong_role")
        verification = verify_resumable_block(state)
        state["phase"] = interrupted
        state["block_reason"] = None
        state["blocked_head"] = None
        state["interrupted_phase"] = None
        state["interrupted_owner"] = None
        token = issue_lease(state, args.actor)
        state["revision"] += 1
        persist(state)
    output(state, verification, lease_token=token)


def require_actor(state: dict[str, Any], actor: str, role: str, lease_token: str | None) -> None:
    expected = state["roles"][role]
    if actor != expected:
        raise RelayError(f"action belongs to configured {role} {expected!r}", kind="wrong_role")
    lease = state.get("lease")
    if not lease or lease.get("actor") != actor or not lease_token:
        raise RelayError("actor does not own the current baton lease", kind="ownership_conflict")
    actual = sha256(lease_token.encode("utf-8"))
    if not hmac.compare_digest(actual, lease.get("token_sha256", "")):
        raise RelayError("stale or invalid baton lease token", kind="ownership_conflict")


def transition_commit(root: Path, state: dict[str, Any], ref: str) -> str:
    commit = resolve_commit(root, ref)
    current = head_sha(root)
    if commit != current:
        raise RelayError(f"transition commit {commit} is not current HEAD {current}")
    if commit == state["current_head"] or not is_ancestor(root, state["current_head"], commit):
        raise RelayError("transition requires at least one new focused descendant commit")
    require_clean(root)
    return commit


def evidence_refs(
    root: Path,
    values: Iterable[str],
    snapshot: str,
    *,
    changed_since: str,
    required: bool = True,
) -> list[str]:
    refs = collect_files(root, values, snapshot)
    if required and not refs:
        raise RelayError("at least one committed canonical evidence path is required")
    for relative in refs:
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", changed_since, snapshot, "--", relative],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if changed.returncode == 0:
            raise RelayError(
                f"canonical evidence was not changed in this phase: {relative}",
                kind="evidence_not_updated",
            )
        if changed.returncode != 1:
            detail = changed.stderr.decode(errors="replace").strip()
            raise RelayError(f"cannot verify phase evidence {relative}: {detail}")
    return refs


def cmd_submit(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] not in {"executing", "reworking"}:
            raise RelayError(f"phase {state['phase']!r} cannot be submitted")
        require_actor(state, args.actor, "builder", args.lease_token)
        verify_state(state)
        root = Path(state["worktree"])
        commit = transition_commit(root, state, args.commit)
        refs = evidence_refs(root, args.evidence, commit, changed_since=state["current_head"])
        state["phase"] = "ready_to_review"
        state["current_head"] = commit
        state["implementation_head"] = commit
        state["evidence_refs"] = dedupe([*state["evidence_refs"], *refs])
        state["transition_evidence_manifest"].extend(manifest_entry(root, ref, commit) for ref in refs)
        state["lease"] = None
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state))


def cmd_reject(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] != "reviewing":
            raise RelayError(f"phase {state['phase']!r} cannot be rejected")
        require_actor(state, args.actor, "reviewer", args.lease_token)
        verify_state(state)
        root = Path(state["worktree"])
        commit = transition_commit(root, state, args.commit)
        _, finding = path_inside(root, args.findings, tracked_at=commit)
        evidence_refs(root, [finding], commit, changed_since=state["current_head"])
        state["phase"] = "rework_ready"
        state["current_head"] = commit
        state["findings_ref"] = finding
        state["evidence_refs"] = dedupe([*state["evidence_refs"], finding])
        state["transition_evidence_manifest"].append(manifest_entry(root, finding, commit))
        state["cycle"] += 1
        state["lease"] = None
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state))


def cmd_accept(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] != "reviewing":
            raise RelayError(f"phase {state['phase']!r} cannot be accepted")
        require_actor(state, args.actor, "reviewer", args.lease_token)
        verify_state(state, allow_admin=True)
        root = Path(state["worktree"])
        commit = transition_commit(root, state, args.commit)
        refs = evidence_refs(root, args.evidence, commit, changed_since=state["current_head"])
        verify_authority(state, allow_admin=True)
        require_status(root / state["frontier"], {"Done"})
        sealed_paths = {entry["path"] for entry in state["sealed_authority_manifest"]}
        if state["frontier"] in sealed_paths:
            raise RelayError("frontier was already sealed by a prior acceptance", kind="authority_drift")
        state["sealed_authority_manifest"].append(manifest_entry(root, state["frontier"], commit))
        state["phase"] = "accepted"
        state["current_head"] = commit
        state["evidence_refs"] = dedupe([*state["evidence_refs"], *refs])
        state["transition_evidence_manifest"].extend(manifest_entry(root, ref, commit) for ref in refs)
        state["lease"] = None
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state, allow_admin=True))


def cmd_close(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] != "accepted":
            raise RelayError("only an accepted parent Final Review baton can be closed")
        if args.actor != state["roles"]["planner"]:
            raise RelayError(f"only configured planner {state['roles']['planner']!r} may close", kind="wrong_role")
        verify_state(state, allow_admin=True)
        root = Path(state["worktree"])
        if state["task"] != state["frontier"]:
            raise RelayError("a child-slice acceptance cannot close the parent task", kind="not_approved")
        require_status(root / state["task"], {"Done"})
        state["phase"] = "closed"
        state["revision"] += 1
        persist(state)
    output(state, verify_state(state, allow_admin=True))


def expected_actor(state: dict[str, Any]) -> str:
    return state["roles"][PHASE_MODEL[state["phase"]]["owner"]]


def cmd_block(args: argparse.Namespace) -> None:
    with locked_state():
        state = load_for_worktree(args.worktree)
        if state["phase"] in {"blocked", "accepted", "closed"}:
            raise RelayError(f"phase {state['phase']!r} cannot be blocked")
        allowed = {expected_actor(state), state["roles"]["planner"], state["roles"]["reviewer"]}
        if args.actor not in allowed:
            raise RelayError(f"actor {args.actor!r} cannot block this phase", kind="wrong_role")
        if state["phase"] in OWNED_PHASES and state.get("lease", {}).get("actor") == args.actor:
            role = PHASE_MODEL[state["phase"]]["owner"]
            require_actor(state, args.actor, role, args.lease_token)
        root = Path(state["worktree"])
        current = head_sha(root)
        refs = []
        for value in args.evidence or []:
            _, relative = path_inside(root, value, tracked_at=current)
            refs.append(relative)
        state["interrupted_phase"] = state["phase"]
        state["interrupted_owner"] = state.get("lease", {}).get("actor") if state.get("lease") else None
        state["phase"] = "blocked"
        state["block_reason"] = args.reason
        state["blocked_head"] = current
        state["evidence_refs"] = dedupe([*state["evidence_refs"], *refs])
        recorded = {
            (entry["path"], entry["snapshot_commit"]) for entry in state["transition_evidence_manifest"]
        }
        for ref in dedupe(refs):
            if (ref, current) not in recorded:
                state["transition_evidence_manifest"].append(manifest_entry(root, ref, current))
        state["lease"] = None
        state["revision"] += 1
        persist(state)
    output(state)


def add_start_arguments(parser: argparse.ArgumentParser, *, restart: bool = False) -> None:
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--task", required=True, help="Parent Approved plan path")
    parser.add_argument("--frontier", required=True, help="Current frontier Approved plan path")
    parser.add_argument("--base", required=True, help="Builder base, or parent fixed point for Final Review")
    parser.add_argument("--phase", choices=["ready_to_execute", "ready_to_review"], default="ready_to_execute")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--planner", required=not restart)
    parser.add_argument("--builder", required=not restart)
    parser.add_argument("--reviewer", required=not restart)
    parser.add_argument("--authority", action="append", default=[], help="Immutable approved contract path; repeatable")
    parser.add_argument("--approval-evidence", action="append", default=[], required=True, help="Committed Pre-Start PASS evidence; repeatable")
    parser.add_argument("--suggested-skill", action="append", default=[])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Select and verify one baton")
    show.add_argument("--worktree")
    show.set_defaults(func=cmd_show)

    listing = subparsers.add_parser("list", help="List baton routing metadata")
    listing.set_defaults(func=cmd_list)

    start = subparsers.add_parser("start", help="Create the first baton after the full Approved gate")
    add_start_arguments(start)
    start.set_defaults(func=cmd_start)

    restart = subparsers.add_parser("restart", help="Archive accepted/blocked routing and pin a new Approved frontier")
    add_start_arguments(restart, restart=True)
    restart.set_defaults(func=cmd_restart)

    reapprove = subparsers.add_parser(
        "reapprove",
        help="Refresh an Approved contract while preserving blocked owned work and the fixed base",
    )
    reapprove.add_argument("--worktree", required=True)
    reapprove.add_argument("--task", required=True)
    reapprove.add_argument("--frontier", required=True)
    reapprove.add_argument("--actor", required=True)
    reapprove.add_argument("--authority", action="append", default=[])
    reapprove.add_argument("--approval-evidence", action="append", default=[], required=True)
    reapprove.set_defaults(func=cmd_reapprove)

    claim = subparsers.add_parser("claim", help="Atomically claim the routed phase")
    claim.add_argument("--worktree", required=True)
    claim.add_argument("--actor", required=True)
    claim.set_defaults(func=cmd_claim)

    takeover = subparsers.add_parser("takeover", help="Fence an abandoned lease after the old session is confirmed ended")
    takeover.add_argument("--worktree", required=True)
    takeover.add_argument("--actor", required=True)
    takeover.set_defaults(func=cmd_takeover)

    resume = subparsers.add_parser(
        "resume",
        help="Resume a cleared same-owner interruption or re-approved owned phase in place",
    )
    resume.add_argument("--worktree", required=True)
    resume.add_argument("--actor", required=True)
    resume.set_defaults(func=cmd_resume)

    submit = subparsers.add_parser("submit", help="Builder hands a committed slice to reviewer")
    submit.add_argument("--worktree", required=True)
    submit.add_argument("--actor", required=True)
    submit.add_argument("--lease-token", required=True)
    submit.add_argument("--commit", required=True)
    submit.add_argument("--evidence", action="append", default=[], required=True)
    submit.set_defaults(func=cmd_submit)

    reject = subparsers.add_parser("reject", help="Reviewer returns committed findings for rework")
    reject.add_argument("--worktree", required=True)
    reject.add_argument("--actor", required=True)
    reject.add_argument("--lease-token", required=True)
    reject.add_argument("--commit", required=True)
    reject.add_argument("--findings", required=True)
    reject.set_defaults(func=cmd_reject)

    accept = subparsers.add_parser("accept", help="Reviewer accepts after all gates and committed evidence")
    accept.add_argument("--worktree", required=True)
    accept.add_argument("--actor", required=True)
    accept.add_argument("--lease-token", required=True)
    accept.add_argument("--commit", required=True)
    accept.add_argument("--evidence", action="append", default=[], required=True)
    accept.set_defaults(func=cmd_accept)

    close = subparsers.add_parser("close", help="Close a terminal parent task after accepted Final Review")
    close.add_argument("--worktree", required=True)
    close.add_argument("--actor", required=True)
    close.set_defaults(func=cmd_close)

    block = subparsers.add_parser("block", help="Preserve routing while waiting for authority/evidence/ownership")
    block.add_argument("--worktree", required=True)
    block.add_argument("--actor", required=True)
    block.add_argument("--lease-token")
    block.add_argument("--reason", choices=sorted(BLOCK_REASONS), required=True)
    block.add_argument("--evidence", action="append", default=[])
    block.set_defaults(func=cmd_block)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except RelayError as exc:
        print(json.dumps({"error": str(exc), "kind": exc.kind}, ensure_ascii=False), file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())
