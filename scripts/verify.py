#!/usr/bin/env python3
"""Dependency-free integrity and accessibility checks for the static site."""

from __future__ import annotations

import re
import struct
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
CSS_PATH = ROOT / "css" / "style.css"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: Counter[str] = Counter()
        self.ids: list[str] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.headings: list[int] = []
        self.html_attrs: dict[str, str] = {}
        self.meta: list[dict[str, str]] = []
        self.navs: list[dict[str, str]] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        self.tags[tag] += 1
        if identifier := attributes.get("id"):
            self.ids.append(identifier)
        if tag == "html":
            self.html_attrs = attributes
        elif tag == "a":
            self.links.append(attributes)
        elif tag == "img":
            self.images.append(attributes)
        elif tag == "meta":
            self.meta.append(attributes)
        elif tag == "nav":
            self.navs.append(attributes)
        elif re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    """Read JPEG dimensions without an imaging dependency."""
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError(f"{path.relative_to(ROOT)} is not a JPEG")
    offset = 2
    start_of_frame = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9}:
            continue
        if marker == 0xDA:
            break
        length = struct.unpack(">H", data[offset : offset + 2])[0]
        if marker in start_of_frame:
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += length
    raise ValueError(f"Could not read dimensions from {path.relative_to(ROOT)}")


def local_path(reference: str) -> Path | None:
    parts = urlsplit(reference)
    if parts.scheme or parts.netloc or reference.startswith("#"):
        return None
    decoded = unquote(parts.path)
    candidate = (ROOT / decoded).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise AssertionError(f"Local path escapes the project: {reference}") from exc
    return candidate


def check_balanced_css(css: str) -> None:
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    for opening, closing, label in (("{", "}", "braces"), ("(", ")", "parentheses")):
        depth = 0
        for character in stripped:
            if character == opening:
                depth += 1
            elif character == closing:
                depth -= 1
                assert depth >= 0, f"CSS has an unmatched closing {label[:-1]}"
        assert depth == 0, f"CSS has unbalanced {label}"


def main() -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    parser.close()

    assert html.lstrip().lower().startswith("<!doctype html>"), "Missing HTML5 doctype"
    assert parser.html_attrs.get("lang"), "The html element needs a lang attribute"
    assert "".join(parser.title_parts).strip(), "The document needs a title"
    assert any("charset" in item for item in parser.meta), "Missing charset metadata"
    assert any(item.get("name") == "viewport" for item in parser.meta), (
        "Missing viewport metadata"
    )
    assert any(
        item.get("name") == "description" and item.get("content", "").strip()
        for item in parser.meta
    ), "Missing meta description"
    for landmark in ("nav", "main", "footer"):
        assert parser.tags[landmark] == 1, f"Expected exactly one {landmark} landmark"
    assert parser.navs[0].get("aria-label"), "Primary navigation needs an accessible name"
    assert parser.tags["script"] == 0, "Static-only scope must not add JavaScript"

    duplicate_ids = sorted(
        identifier for identifier, count in Counter(parser.ids).items() if count > 1
    )
    assert not duplicate_ids, f"Duplicate IDs: {', '.join(duplicate_ids)}"
    id_set = set(parser.ids)

    skip_links = [
        link
        for link in parser.links
        if "skip-link" in link.get("class", "").split()
    ]
    assert skip_links, "Missing keyboard skip link"
    assert skip_links[0].get("href", "").removeprefix("#") in id_set, (
        "Skip link target does not exist"
    )

    for link in parser.links:
        href = link.get("href", "").strip()
        assert href, "Anchor has an empty href"
        if href.startswith("#"):
            assert href[1:] in id_set, f"Broken fragment link: {href}"
        elif path := local_path(href):
            assert path.is_file(), f"Missing linked file: {href}"

    assert parser.headings.count(1) == 1, "Expected exactly one h1"
    assert parser.headings and parser.headings[0] == 1, "Heading order must begin with h1"
    for previous, current in zip(parser.headings, parser.headings[1:]):
        assert current <= previous + 1, (
            f"Heading level jumps from h{previous} to h{current}"
        )

    assert parser.images, "Expected at least one content image"
    for image in parser.images:
        source = image.get("src", "").strip()
        assert source, "Image has no src"
        assert image.get("alt", "").strip(), f"Image needs useful alt text: {source}"
        path = local_path(source)
        assert path and path.is_file(), f"Missing local image: {source}"
        width, height = jpeg_dimensions(path)
        assert image.get("width") == str(width), f"Wrong or missing width for {source}"
        assert image.get("height") == str(height), f"Wrong or missing height for {source}"

    stylesheet_links = re.findall(
        r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    assert stylesheet_links, "No stylesheet is linked"
    for reference in stylesheet_links:
        if path := local_path(reference):
            assert path.is_file(), f"Missing stylesheet: {reference}"

    check_balanced_css(css)
    for required_rule in (
        ".skip-link",
        ":focus-visible",
        "scroll-margin-top",
        "prefers-reduced-motion",
    ):
        assert required_rule in css, f"Missing accessibility rule: {required_rule}"
    assert not re.search(
        r"\.nav-links\s*\{[^}]*display\s*:\s*none", css, flags=re.DOTALL
    ), "Responsive CSS must not remove primary navigation"

    print("Site verification passed:")
    print(f"  {parser.tags['section']} sections, {len(parser.links)} links")
    print(f"  {len(parser.images)} local images with verified dimensions and alt text")
    print("  metadata, landmarks, headings, fragments, assets, and CSS are valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError) as error:
        print(f"Site verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
