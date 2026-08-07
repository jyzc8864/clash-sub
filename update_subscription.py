"""Fetch one ZDOpen proxy and write a Clash configuration."""

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def quote_yaml(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def main() -> None:
    source_url = os.environ["ZDOPEN_API_URL"]
    request = Request(source_url, headers={"Accept": "application/json", "User-Agent": "clash-sub-updater/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = json.load(response)

    proxy = payload["data"]["proxy_list"][0]
    host = str(proxy["ip"])
    port = int(proxy["port"])
    proxy_type = str(proxy["protocol"]).lower()
    if not host or not 1 <= port <= 65535 or proxy_type not in {"http", "https", "socks4", "socks5"}:
        raise ValueError("The source did not return a usable Clash proxy")

    name = f"ZDOpen {proxy.get('adr') or 'Free Proxy'}"
    config = "\n".join(
        [
            "mixed-port: 7890",
            "allow-lan: false",
            "mode: rule",
            "log-level: info",
            "proxies:",
            f"  - name: {quote_yaml(name)}",
            f"    type: {proxy_type}",
            f"    server: {quote_yaml(host)}",
            f"    port: {port}",
            "    udp: false",
            "proxy-groups:",
            "  - name: PROXY",
            "    type: select",
            "    proxies:",
            f"      - {quote_yaml(name)}",
            "      - DIRECT",
            "rules:",
            "  - MATCH,PROXY",
            "",
        ]
    )
    Path("clash.yaml").write_text(config, encoding="utf-8")


if __name__ == "__main__":
    main()
