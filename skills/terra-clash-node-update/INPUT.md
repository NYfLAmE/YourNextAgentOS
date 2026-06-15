# terra-clash-node-update — 输入清单

Agent 被呼出后，**先展示本表并收齐全部必填项**，再执行脚本。缺一项不运行。

## 必填

| 字段 | 说明 | 示例 |
|------|------|------|
| `vless_url` | 完整 VLESS 分享链接 | `vless://uuid@host:port?...#备注` |
| `date_suffix` | 输出文件名日期后缀 `YYYYMMDD` | `20260605` |
| `baseline_yaml` | 基线 Clash 配置路径（**禁止原地修改**） | `/home/ZykLyj/yjdev/terraMasterClash.yaml` |
| `proxy_group_name` | 要更新其首个 vless 引用的策略组名 | `🎯 clash2专用` |

## 可选

| 字段 | 默认 | 说明 |
|------|------|------|
| `workspace_root` | `/home/ZykLyj/yjdev` | 输出目录：`clash_<date>.yaml`、`terraMasterClash_<date>.yaml` |
| `node_name` | （空，用链接 fragment） | 覆盖 Clash 节点 `name` |

## 输出文件（自动生成）

| 文件 | 说明 |
|------|------|
| `<workspace>/clash_<date_suffix>.yaml` | 单节点独立 Clash 配置 |
| `<workspace>/terraMasterClash_<date_suffix>.yaml` | 基线副本 + 已替换策略组内 vless 节点 |

## 收集话术模板

```
请确认以下参数后我将执行 terra-clash-node-update：

1. vless_url: ...
2. date_suffix: ...
3. baseline_yaml: ...
4. proxy_group_name: ...
5. workspace_root: （默认 /home/ZykLyj/yjdev）
6. node_name: （可选，留空则用链接 # 备注）
```
