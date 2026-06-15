---
name: terra-clash-node-update
description: Converts a VLESS share link into Clash/mihomo YAML and updates a named proxy group in a copied Terra Master Clash config without editing the baseline. Use when the user invokes /terra-clash-node-update, says 更新 clash2 节点, VLESS 换 terraMasterClash, 生成 terraMasterClash_YYYYMMDD, or rotates the dedicated clash2 proxy node.
---

# terra-clash-node-update

Rotate the first **vless** proxy referenced by a named `proxy-groups` entry in a **dated copy** of a Terra Master Clash config. Never edit the baseline file in place.

## Before you run

1. Read [INPUT.md](INPUT.md).
2. **Collect all required fields** and show them to the user for confirmation. Do not execute if any required field is missing.
3. Prefer the bundled script over hand-editing YAML.

## Hard constraints

- **Do not modify** `baseline_yaml` — only `cp` then edit `terraMasterClash_<date_suffix>.yaml`.
- Output names: `clash_<date_suffix>.yaml`, `terraMasterClash_<date_suffix>.yaml` under `workspace_root`.
- After replace, `proxy-groups` references and `proxies` block must use the **same** new node name.
- If output files exist, **stop** (script exit `3`) and ask the user: overwrite (`--force`), new date, or abort.

## Workflow (fixed order)

1. Collect inputs per [INPUT.md](INPUT.md).
2. Run:

```bash
python3 ~/.agents/skills/terra-clash-node-update/scripts/update_terra_clash_node.py \
  --vless '<vless_url>' \
  --date <YYYYMMDD> \
  --baseline '<baseline_yaml>' \
  --proxy-group '<proxy_group_name>' \
  --workspace '<workspace_root>'
```

Optional: `--node-name '<name>'` to override the link fragment; `--force` only after user confirms overwrite.

3. Handle exit codes:

| Code | Meaning | Agent action |
|------|---------|--------------|
| 0 | Success | Report paths, `old_node` → `new_node`, diff summary |
| 2 | Invalid input / missing baseline | Fix parameters |
| 3 | Output collision | Ask user; retry with new date or `--force` |
| 4 | Ambiguous vless in group | Ask user to fix baseline or group |
| 5 | Replace/verify failed | Show stderr; do not leave partial outputs |

4. Confirm baseline unchanged: script runs `diff` + `grep`; baseline must still contain `old_node`, copy must not.

## Replace target rule

- Read `proxy_group_name`'s `proxies` list (inline `[a, b]` or multiline).
- Pick the **first** member that exists in `proxies:` with `type: vless`.
- Replace that proxy's YAML block and update the group reference from old name to new name.

## Bundled scripts

| Script | Role |
|--------|------|
| `scripts/vless_to_clash.py` | VLESS → `clash_<date>.yaml` |
| `scripts/update_terra_clash_node.py` | Full pipeline + verify |

Keep `scripts/vless_to_clash.py` in sync with `/home/ZykLyj/yjdev/vless_to_clash.py` when the workspace converter changes:

```bash
diff ~/.agents/skills/terra-clash-node-update/scripts/vless_to_clash.py /home/ZykLyj/yjdev/vless_to_clash.py
cp /home/ZykLyj/yjdev/vless_to_clash.py ~/.agents/skills/terra-clash-node-update/scripts/
```

## Example (Terra Master clash2)

```bash
python3 ~/.agents/skills/terra-clash-node-update/scripts/update_terra_clash_node.py \
  --vless 'vless://...@host:port?...#mega-jk5-tomatoluck6' \
  --date 20260605 \
  --baseline /home/ZykLyj/yjdev/terraMasterClash.yaml \
  --proxy-group '🎯 clash2专用' \
  --workspace /home/ZykLyj/yjdev
```

## Report template

```
terra-clash-node-update 完成
- clash: <workspace>/clash_<date>.yaml
- terra: <workspace>/terraMasterClash_<date>.yaml
- 节点: <old_node> → <new_node>
- 策略组: <proxy_group_name>
- 基线未修改: <baseline_yaml>
```
