#!/usr/bin/env python3
"""Serve the site on an ephemeral port and verify every local asset over HTTP."""

from __future__ import annotations

import contextlib
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from verify import ROOT, SiteParser, local_path


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    references = {"index.html", "css/style.css"}
    references.update(
        image["src"] for image in parser.images if local_path(image["src"])
    )

    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(ROOT), **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        for reference in sorted(references):
            with contextlib.closing(urlopen(f"{base_url}/{reference}", timeout=5)) as response:
                assert response.status == 200, f"{reference} returned {response.status}"
                assert response.read(1), f"{reference} returned an empty response"
                content_type = response.headers.get_content_type()
                suffix = Path(reference).suffix.lower()
                expected_type = {
                    ".css": "text/css",
                    ".html": "text/html",
                    ".jpeg": "image/jpeg",
                }.get(suffix)
                assert content_type == expected_type, (
                    f"{reference} returned {content_type}, expected {expected_type}"
                )

        try:
            urlopen(f"{base_url}/missing-page.html", timeout=5)
        except HTTPError as error:
            assert error.code == 404, f"Missing page returned {error.code}, expected 404"
        else:
            raise AssertionError("Missing page did not return 404")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    print(f"HTTP smoke passed: {len(references)} local resources returned expected content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
