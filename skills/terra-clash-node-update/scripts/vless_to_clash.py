#!/usr/bin/env python3
"""
Convert one or more vless:// share links to a Clash Verge / mihomo YAML file.

Usage:
  python3 vless_to_clash.py 'vless://...' -o clash.yaml
  python3 vless_to_clash.py --snippet 'vless://...'
  printf '%s\n' 'vless://...' | python3 vless_to_clash.py - -o clash.yaml
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
SUPPORTED_NETWORKS = {"tcp", "ws", "grpc", "http", "h2", "xhttp"}


class ConvertError(Exception):
    pass


def as_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return None


def as_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def query_get(query: dict[str, list[str]], *names: str) -> str | None:
    for name in names:
        values = query.get(name)
        if values is not None and len(values) > 0:
            return values[0]
    return None


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def yaml_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value == "":
        return '""'

    reserved = {"null", "Null", "NULL", "true", "True", "TRUE", "false", "False", "FALSE"}
    safe_plain = re.fullmatch(r"[A-Za-z0-9_./:@+-]+", value) is not None
    if safe_plain and value not in reserved and not value.startswith(("-", "?", ":")):
        return value
    return json.dumps(value, ensure_ascii=False)


def emit_yaml(value: Any, indent: int = 0) -> list[str]:
    spaces = " " * indent
    lines: list[str] = []

    if isinstance(value, dict):
        if not value:
            return [spaces + "{}"]
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                if item:
                    lines.append(f"{spaces}{key}:")
                    lines.extend(emit_yaml(item, indent + 2))
                else:
                    lines.append(f"{spaces}{key}: {yaml_scalar(item)}")
            else:
                lines.append(f"{spaces}{key}: {yaml_scalar(item)}")
        return lines

    if isinstance(value, list):
        if not value:
            return [spaces + "[]"]
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(spaces + "- {}")
                    continue
                first = True
                for key, subitem in item.items():
                    prefix = spaces + "- " if first else spaces + "  "
                    if isinstance(subitem, (dict, list)):
                        if subitem:
                            lines.append(f"{prefix}{key}:")
                            lines.extend(emit_yaml(subitem, indent + 4))
                        else:
                            lines.append(f"{prefix}{key}: {yaml_scalar(subitem)}")
                    else:
                        lines.append(f"{prefix}{key}: {yaml_scalar(subitem)}")
                    first = False
            elif isinstance(item, list):
                lines.append(spaces + "-")
                lines.extend(emit_yaml(item, indent + 2))
            else:
                lines.append(f"{spaces}- {yaml_scalar(item)}")
        return lines

    return [spaces + yaml_scalar(value)]


def normalize_network(network: str | None) -> tuple[str, bool]:
    if not network:
        return "tcp", False

    normalized = network.strip().lower()
    if normalized in {"none", "raw"}:
        return "tcp", False
    if normalized in {"splithttp", "split-http", "xhttp"}:
        return "xhttp", False
    if normalized in {"httpupgrade", "http-upgrade"}:
        return "ws", True
    if normalized in SUPPORTED_NETWORKS:
        return normalized, False

    raise ConvertError(
        f"unsupported VLESS transport type '{network}'. "
        "mihomo VLESS commonly supports tcp, ws, grpc, http, h2, and xhttp."
    )


def parse_vless(uri: str, forced_name: str | None, skip_cert_verify: str) -> dict[str, Any]:
    uri = html.unescape(uri.strip())
    if not uri:
        raise ConvertError("empty link")

    parsed = urlsplit(uri)
    if parsed.scheme.lower() != "vless":
        raise ConvertError("only vless:// links are supported")

    uuid = unquote(parsed.username or "")
    server = parsed.hostname
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConvertError(f"invalid port in link: {exc}") from exc

    if not uuid:
        raise ConvertError("missing VLESS UUID/user id")
    if not server:
        raise ConvertError("missing VLESS server host")

    query = parse_qs(parsed.query, keep_blank_values=True)
    security = (query_get(query, "security") or "").strip().lower()
    network, force_http_upgrade = normalize_network(query_get(query, "type", "network", "net"))

    if port is None:
        port = 443 if security in {"tls", "reality", "xtls"} else 80

    name = forced_name or unquote(parsed.fragment or "")
    if not name:
        name = query_get(query, "remarks", "remark", "ps", "name") or server

    proxy: dict[str, Any] = {
        "name": name,
        "type": "vless",
        "server": server,
        "port": port,
        "uuid": uuid,
        "udp": True,
    }

    encryption = query_get(query, "encryption")
    if encryption is not None:
        proxy["encryption"] = "" if encryption.lower() == "none" else encryption

    flow = query_get(query, "flow")
    if flow:
        proxy["flow"] = flow

    packet_encoding = query_get(query, "packetEncoding", "packet-encoding")
    if packet_encoding:
        proxy["packet-encoding"] = packet_encoding

    tls_enabled = security in {"tls", "reality", "xtls"}
    tls_value = as_bool(query_get(query, "tls"))
    if tls_value is not None:
        tls_enabled = tls_value
    if tls_enabled:
        proxy["tls"] = True

    servername = query_get(query, "sni", "servername", "serverName", "peer")
    if servername:
        proxy["servername"] = servername

    alpn = split_csv(query_get(query, "alpn"))
    if alpn:
        proxy["alpn"] = alpn

    fingerprint = query_get(query, "fingerprint")
    if fingerprint:
        proxy["fingerprint"] = fingerprint

    client_fingerprint = query_get(query, "fp", "client-fingerprint", "clientFingerprint")
    if client_fingerprint:
        proxy["client-fingerprint"] = client_fingerprint

    allow_insecure = as_bool(query_get(query, "allowInsecure", "allow_insecure", "skip-cert-verify"))
    if skip_cert_verify == "true":
        proxy["skip-cert-verify"] = True
    elif skip_cert_verify == "false":
        proxy["skip-cert-verify"] = False
    elif allow_insecure is not None:
        proxy["skip-cert-verify"] = allow_insecure

    if security == "reality":
        reality_opts: dict[str, Any] = {}
        public_key = query_get(query, "pbk", "publicKey", "public-key")
        short_id = query_get(query, "sid", "shortId", "short-id")
        spider_x = query_get(query, "spx", "spiderX", "spider-x")
        if public_key:
            reality_opts["public-key"] = public_key
        if short_id is not None:
            reality_opts["short-id"] = short_id
        if spider_x:
            reality_opts["spider-x"] = spider_x
        if reality_opts:
            proxy["reality-opts"] = reality_opts

    proxy["network"] = network
    apply_transport_options(proxy, query, network, force_http_upgrade)

    return proxy


def apply_transport_options(
    proxy: dict[str, Any],
    query: dict[str, list[str]],
    network: str,
    force_http_upgrade: bool,
) -> None:
    path = query_get(query, "path")
    host = query_get(query, "host", "Host", "authority")

    if network == "ws":
        opts: dict[str, Any] = {}
        if path:
            opts["path"] = path
        headers: dict[str, Any] = {}
        if host:
            headers["Host"] = host
        if headers:
            opts["headers"] = headers
        early_data = as_int(query_get(query, "ed", "max-early-data"))
        if early_data is not None:
            opts["max-early-data"] = early_data
        early_header = query_get(query, "eh", "early-data-header-name")
        if early_header:
            opts["early-data-header-name"] = early_header
        http_upgrade = as_bool(query_get(query, "v2ray-http-upgrade", "http-upgrade"))
        if force_http_upgrade or http_upgrade is not None:
            opts["v2ray-http-upgrade"] = True if force_http_upgrade else http_upgrade
        fast_open = as_bool(query_get(query, "v2ray-http-upgrade-fast-open", "fast-open"))
        if fast_open is not None:
            opts["v2ray-http-upgrade-fast-open"] = fast_open
        if opts:
            proxy["ws-opts"] = opts

    elif network == "grpc":
        opts = {}
        service_name = query_get(query, "serviceName", "service-name", "grpc-service-name")
        if service_name:
            opts["grpc-service-name"] = service_name
        user_agent = query_get(query, "grpc-user-agent")
        if user_agent:
            opts["grpc-user-agent"] = user_agent
        ping_interval = as_int(query_get(query, "ping-interval"))
        if ping_interval is not None:
            opts["ping-interval"] = ping_interval
        if opts:
            proxy["grpc-opts"] = opts

    elif network == "h2":
        opts = {}
        if host:
            opts["host"] = split_csv(host) or [host]
        if path:
            opts["path"] = path
        if opts:
            proxy["h2-opts"] = opts

    elif network == "http":
        opts = {}
        method = query_get(query, "method")
        if method:
            opts["method"] = method
        if path:
            opts["path"] = split_csv(path) or [path]
        if host:
            opts["headers"] = {"Host": split_csv(host) or [host]}
        if opts:
            proxy["http-opts"] = opts

    elif network == "xhttp":
        opts = {}
        if path:
            opts["path"] = path
        if host:
            opts["host"] = host
        mode = query_get(query, "mode")
        if mode:
            opts["mode"] = mode
        no_grpc_header = as_bool(query_get(query, "no-grpc-header"))
        if no_grpc_header is not None:
            opts["no-grpc-header"] = no_grpc_header
        if opts:
            proxy["xhttp-opts"] = opts


def ensure_unique_names(proxies: list[dict[str, Any]]) -> None:
    seen: dict[str, int] = {}
    for proxy in proxies:
        original = str(proxy["name"])
        count = seen.get(original, 0) + 1
        seen[original] = count
        if count > 1:
            proxy["name"] = f"{original} {count}"


def build_config(proxies: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    names = [proxy["name"] for proxy in proxies]
    group_members = names + ["DIRECT"]
    return {
        "mixed-port": args.mixed_port,
        "allow-lan": args.allow_lan,
        "mode": args.mode,
        "log-level": args.log_level,
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": args.group,
                "type": "select",
                "proxies": group_members,
            }
        ],
        "rules": [f"MATCH,{args.group}"],
    }


def extract_links_from_text(text: str) -> list[str]:
    return re.findall(r"vless://\S+", text)


def collect_links(args: argparse.Namespace) -> list[str]:
    raw_items: list[str] = []

    if args.input:
        raw_items.append(Path(args.input).read_text(encoding="utf-8"))

    for item in args.links:
        if item == "-":
            raw_items.append(sys.stdin.read())
        else:
            raw_items.append(item)

    if not raw_items:
        if sys.stdin.isatty():
            raw_items.append(input("Paste vless:// link: ").strip())
        else:
            raw_items.append(sys.stdin.read())

    links: list[str] = []
    for item in raw_items:
        item = item.strip()
        if not item:
            continue
        if item.lower().startswith("vless://"):
            links.append(item)
        else:
            links.extend(extract_links_from_text(item))

    if not links:
        raise ConvertError("no vless:// link found")
    return links


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert vless:// links to Clash Verge / mihomo YAML.",
    )
    parser.add_argument("links", nargs="*", help="vless:// links. Use '-' to read from stdin.")
    parser.add_argument("-i", "--input", help="read links from a text file")
    parser.add_argument("-o", "--output", help="write YAML to this file")
    parser.add_argument("--snippet", action="store_true", help="output only the proxies section")
    parser.add_argument("--name", help="override node name; only valid when converting one link")
    parser.add_argument("--group", default="PROXY", help="proxy group name for full config")
    parser.add_argument("--mixed-port", type=int, default=7890, help="mixed-port for full config")
    parser.add_argument("--allow-lan", action="store_true", help="set allow-lan: true")
    parser.add_argument("--mode", choices=["rule", "global", "direct"], default="rule")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error", "silent"])
    parser.add_argument(
        "--skip-cert-verify",
        choices=["auto", "true", "false"],
        default="auto",
        help="override skip-cert-verify; auto uses allowInsecure from the link",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        links = collect_links(args)
        if args.name and len(links) != 1:
            raise ConvertError("--name can only be used when converting exactly one link")

        proxies = [
            parse_vless(link, args.name if len(links) == 1 else None, args.skip_cert_verify)
            for link in links
        ]
        ensure_unique_names(proxies)

        output_obj: dict[str, Any]
        if args.snippet:
            output_obj = {"proxies": proxies}
        else:
            output_obj = build_config(proxies, args)

        output = "\n".join(emit_yaml(output_obj)) + "\n"
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except ConvertError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
