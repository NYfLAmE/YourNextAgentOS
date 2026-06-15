#!/usr/bin/env python3
"""
Update a dated Terra Master Clash copy with a new VLESS node.

Exit codes:
  0  success
  2  preflight / usage error
  3  output file(s) already exist (collision)
  4  cannot resolve exactly one vless proxy to replace in the target group
  5  replace / verify failure
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit


SCRIPT_DIR = Path(__file__).resolve().parent
CONVERTER = SCRIPT_DIR / "vless_to_clash.py"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert VLESS to Clash and update a proxy group in a dated Terra Master copy.",
    )
    parser.add_argument("--vless", required=True, help="vless:// share link")
    parser.add_argument("--date", required=True, help="YYYYMMDD date suffix for output files")
    parser.add_argument("--baseline", required=True, help="baseline YAML path (not modified in place)")
    parser.add_argument("--proxy-group", required=True, help="proxy group name to update")
    parser.add_argument(
        "--workspace",
        default="/home/ZykLyj/yjdev",
        help="directory for clash_<date>.yaml and terraMasterClash_<date>.yaml",
    )
    parser.add_argument("--node-name", default="", help="override Clash proxy name (default: link fragment)")
    parser.add_argument("--force", action="store_true", help="overwrite existing output files")
    return parser.parse_args(argv)


def validate_date_suffix(value: str) -> None:
    if not re.fullmatch(r"\d{8}", value):
        raise ValueError(f"date_suffix must be YYYYMMDD, got: {value!r}")


def preflight_vless(url: str) -> None:
    parsed = urlsplit(url.strip())
    if parsed.scheme.lower() != "vless":
        raise ValueError("vless_url must use vless:// scheme")
    if not parsed.hostname:
        raise ValueError("vless_url missing host")


def parse_proxy_catalog(text: str) -> dict[str, str]:
    """Map proxy name -> type (vless, direct, ...) from proxies: section."""
    catalog: dict[str, str] = {}
    in_proxies = False
    current_name: str | None = None
    current_type: str | None = None

    for line in text.splitlines():
        if re.match(r"^proxies:\s*$", line):
            in_proxies = True
            continue
        if in_proxies and re.match(r"^[A-Za-z#]", line) and not line.startswith(" "):
            break
        if not in_proxies:
            continue

        inline = re.match(r"^\s+-\s+\{name:\s*([^,]+),\s*type:\s*([^,}]+)", line)
        if inline:
            name = inline.group(1).strip()
            ptype = inline.group(2).strip()
            catalog[name] = ptype
            current_name = None
            current_type = None
            continue

        name_match = re.match(r"^\s+-\s+name:\s*(.+?)\s*$", line)
        if name_match:
            if current_name and current_type:
                catalog[current_name] = current_type
            current_name = name_match.group(1).strip()
            current_type = None
            continue

        type_match = re.match(r"^\s+type:\s*(\S+)\s*$", line)
        if type_match and current_name:
            current_type = type_match.group(1).strip()

    if current_name and current_type:
        catalog[current_name] = current_type
    return catalog


def extract_group_proxy_names(text: str, group_name: str) -> list[str]:
    """Return proxy names listed under the given proxy-group."""
    names: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "proxy-groups:" not in line and not (
            i > 0 and any("proxy-groups:" in lines[j] for j in range(max(0, i - 3), i + 1))
        ):
            # quick skip until proxy-groups
            if line.strip() == "proxy-groups:":
                pass
        if line.strip() != "proxy-groups:" and "proxy-groups:" not in line:
            i += 1
            continue

        # find proxy-groups section start
        if line.strip() == "proxy-groups:":
            i += 1
            while i < len(lines):
                entry = lines[i]
                if entry and not entry.startswith(" ") and not entry.startswith("#"):
                    if not entry.startswith("-"):
                        break
                # inline: - {name: X, type: select, proxies: [a, b]}
                if f"name: {group_name}" in entry or f'name: {group_name}' in entry:
                    bracket = re.search(r"proxies:\s*\[([^\]]*)\]", entry)
                    if bracket:
                        raw = bracket.group(1)
                        names = [n.strip() for n in raw.split(",") if n.strip()]
                        return names
                    # multiline proxies list after this line
                    j = i + 1
                    while j < len(lines):
                        plist = re.match(r"^\s+proxies:\s*$", lines[j])
                        if plist:
                            j += 1
                            while j < len(lines) and lines[j].startswith(" "):
                                item = re.match(r"^\s+-\s+(.+?)\s*$", lines[j])
                                if item:
                                    names.append(item.group(1).strip())
                                j += 1
                            return names
                        if lines[j].strip().startswith("- {name:") or lines[j].strip().startswith("- name:"):
                            break
                        j += 1
                i += 1
            return names
        i += 1

    # second pass: scan from proxy-groups:
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "proxy-groups:":
            start = idx + 1
            break
    if start is None:
        return names

    i = start
    while i < len(lines):
        entry = lines[i]
        if entry and not entry.startswith(" ") and not entry.startswith("#") and not entry.startswith("-"):
            break
        escaped = re.escape(group_name)
        if re.search(rf"name:\s*{escaped}\b", entry):
            bracket = re.search(r"proxies:\s*\[([^\]]*)\]", entry)
            if bracket:
                raw = bracket.group(1)
                return [n.strip() for n in raw.split(",") if n.strip()]
            j = i + 1
            while j < len(lines):
                if re.match(r"^\s+proxies:\s*$", lines[j]):
                    j += 1
                    out: list[str] = []
                    while j < len(lines) and re.match(r"^\s+-\s+", lines[j]):
                        item = re.match(r"^\s+-\s+(.+?)\s*$", lines[j])
                        if item:
                            out.append(item.group(1).strip())
                        j += 1
                    return out
                if lines[j].strip().startswith("- "):
                    break
                j += 1
        i += 1
    return names


def resolve_old_node(text: str, group_name: str) -> str:
    catalog = parse_proxy_catalog(text)
    group_members = extract_group_proxy_names(text, group_name)
    if not group_members:
        raise RuntimeError(f"proxy group not found or has no proxies list: {group_name!r}")

    vless_candidates = [
        name for name in group_members if catalog.get(name) == "vless"
    ]
    if len(vless_candidates) == 1:
        return vless_candidates[0]
    if not vless_candidates:
        raise RuntimeError(
            f"no vless proxy referenced by group {group_name!r}; members={group_members}"
        )
    raise RuntimeError(
        f"multiple vless proxies in group {group_name!r}: {vless_candidates}; "
        "specify a narrower group or adjust baseline"
    )


def extract_vless_proxy_block(text: str, node_name: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^\s+-\s+name:\s*{re.escape(node_name)}\s*$", line):
            start = i
            break
    if start is None:
        raise RuntimeError(f"vless block not found in clash output for node {node_name!r}")

    block_lines = [lines[start]]
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if re.match(r"^\s+-\s+", line):
            break
        if line.strip() and not line.startswith(" "):
            break
        block_lines.append(line)
    return "\n".join(block_lines)


def replace_proxy_block(text: str, old_node: str, new_block: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^\s+-\s+name:\s*{re.escape(old_node)}\s*$", line):
            start = i
            break
    if start is None:
        raise RuntimeError(f"old proxy block not found: {old_node!r}")

    end = start + 1
    while end < len(lines):
        line = lines[end]
        if re.match(r"^\s+-\s+", line):
            break
        if line.strip() and not line.startswith(" "):
            break
        end += 1

    new_lines = lines[:start] + new_block.splitlines() + lines[end:]
    return "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")


def update_group_reference(text: str, group_name: str, old_node: str, new_node: str) -> str:
    if old_node == new_node:
        return text
    escaped_group = re.escape(group_name)
    escaped_old = re.escape(old_node)

    def repl_inline(match: re.Match[str]) -> str:
        block = match.group(0)
        if old_node not in block:
            return block
        return block.replace(old_node, new_node, 1)

    pattern = re.compile(
        rf"(^\s+-\s+\{{name:\s*{escaped_group}[^}}]*proxies:\s*\[[^\]]*)\b{escaped_old}\b",
        re.MULTILINE,
    )
    updated, count = pattern.subn(lambda m: m.group(0).replace(old_node, new_node, 1), text, count=1)
    if count:
        return updated

    # multiline group entry
    lines = updated.splitlines()
    in_groups = False
    in_target = False
    for i, line in enumerate(lines):
        if line.strip() == "proxy-groups:":
            in_groups = True
            continue
        if in_groups and line and not line.startswith(" ") and not line.startswith("#"):
            break
        if not in_groups:
            continue
        if re.search(rf"name:\s*{escaped_group}\b", line):
            in_target = True
            if old_node in line:
                lines[i] = line.replace(old_node, new_node, 1)
                return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
            continue
        if in_target:
            if re.match(rf"^\s+-\s+{escaped_old}\s*$", line):
                lines[i] = line.replace(old_node, new_node, 1)
                return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
            if line.strip().startswith("- {name:") or line.strip().startswith("- name:"):
                in_target = False
    raise RuntimeError(f"could not update proxy group reference for {group_name!r}")


def run_converter(vless: str, output: Path, node_name: str) -> None:
    cmd = [sys.executable, str(CONVERTER), vless, "-o", str(output)]
    if node_name:
        cmd.extend(["--name", node_name])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "converter failed")


def extract_new_node_name(clash_text: str) -> str:
    for line in clash_text.splitlines():
        match = re.match(r"^\s+-\s+name:\s*(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    raise RuntimeError("could not read new node name from clash output")


def verify(baseline: Path, copy: Path, old_node: str) -> str:
    diff = subprocess.run(
        ["diff", "-u", str(baseline), str(copy)],
        capture_output=True,
        text=True,
    )
    diff_text = diff.stdout or ""
    if not diff_text:
        raise RuntimeError("baseline and copy are identical; expected proxy changes only")

    baseline_hits = subprocess.run(
        ["grep", "-c", old_node, str(baseline)],
        capture_output=True,
        text=True,
    )
    copy_hits = subprocess.run(
        ["grep", "-c", old_node, str(copy)],
        capture_output=True,
        text=True,
    )
    if baseline_hits.returncode != 0 or baseline_hits.stdout.strip() == "0":
        raise RuntimeError(f"baseline should still reference old node {old_node!r}")
    if copy_hits.returncode == 0 and copy_hits.stdout.strip() not in ("", "0"):
        raise RuntimeError(f"copy still contains old node name {old_node!r}")

    return diff_text


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        validate_date_suffix(args.date)
        preflight_vless(args.vless)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).expanduser().resolve()
    baseline = Path(args.baseline).expanduser().resolve()
    if not baseline.is_file():
        print(f"error: baseline not found: {baseline}", file=sys.stderr)
        return 2
    if not CONVERTER.is_file():
        print(f"error: converter not found: {CONVERTER}", file=sys.stderr)
        return 2

    clash_out = workspace / f"clash_{args.date}.yaml"
    terra_out = workspace / f"terraMasterClash_{args.date}.yaml"
    existing = [p for p in (clash_out, terra_out) if p.exists()]
    if existing and not args.force:
        print("collision: output file(s) already exist:", file=sys.stderr)
        for path in existing:
            print(f"  {path}", file=sys.stderr)
        return 3

    try:
        if args.force:
            for path in (clash_out, terra_out):
                if path.exists():
                    path.unlink()

        run_converter(args.vless, clash_out, args.node_name.strip())
        clash_text = clash_out.read_text(encoding="utf-8")
        new_node = extract_new_node_name(clash_text)
        new_block = extract_vless_proxy_block(clash_text, new_node)

        baseline_text = baseline.read_text(encoding="utf-8")
        old_node = resolve_old_node(baseline_text, args.proxy_group)

        shutil.copy2(baseline, terra_out)
        terra_text = terra_out.read_text(encoding="utf-8")
        terra_text = replace_proxy_block(terra_text, old_node, new_block)
        terra_text = update_group_reference(terra_text, args.proxy_group, old_node, new_node)
        terra_out.write_text(terra_text, encoding="utf-8")

        diff_text = verify(baseline, terra_out, old_node)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        for path in (clash_out, terra_out):
            if path.exists():
                path.unlink()
        return 5

    print("ok")
    print(f"clash_output: {clash_out}")
    print(f"terra_output: {terra_out}")
    print(f"old_node: {old_node}")
    print(f"new_node: {new_node}")
    print(f"proxy_group: {args.proxy_group}")
    print("--- diff (baseline vs copy) ---")
    print(diff_text.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
