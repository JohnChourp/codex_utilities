#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Node:
    node_id: str
    title: str
    summary: str
    x: float
    y: float
    w: float
    h: float
    style: str


@dataclass
class Edge:
    edge_id: str
    source: str
    target: str
    label: str
    style: str


def clean_text(value: str) -> str:
    return value.strip().replace("\u2019", "'")


def parse_architecture_md(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    current_section = ""
    intro_line = ""
    start_title = "Άνοιγμα εφαρμογής"
    start_summary = "Launcher intent"

    main_activity = None
    main_pages: List[dict] = []
    sub_pages: List[dict] = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("## "):
            current_section = line[3:].strip()
            i += 1
            continue

        if line and current_section.startswith("Υποσελίδες") and not line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "##")):
            intro_line = line

        item_match = re.match(r"^(\d+)\.\s+`([^`]+)`\s*(?:\(([^)]+)\))?", line)
        if item_match:
            title = clean_text(item_match.group(2))
            subtitle = clean_text(item_match.group(3) or "")
            summary = ""
            nav = ""

            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if re.match(r"^\d+\.\s+`", next_line) or next_line.startswith("## "):
                    break
                if next_line.startswith("- Σύνοψη:"):
                    summary = clean_text(next_line.replace("- Σύνοψη:", "", 1))
                if next_line.startswith("- Πώς πας εκεί:"):
                    nav = clean_text(next_line.replace("- Πώς πας εκεί:", "", 1))
                j += 1

            item = {
                "title": title,
                "subtitle": subtitle,
                "summary": summary,
                "navigation": nav,
            }

            if current_section.startswith("Ροή από το άνοιγμα"):
                main_activity = item
            elif current_section.startswith("Σελίδες που ανοίγουν"):
                main_pages.append(item)
            elif current_section.startswith("Υποσελίδες"):
                sub_pages.append(item)

            i = j
            continue

        i += 1

    if main_activity is None:
        raise ValueError("Δεν βρέθηκε κύρια σελίδα στη section 'Ροή από το άνοιγμα της εφαρμογής'.")

    parent_activity = ""
    if intro_line:
        parent_match = re.search(r"`([^`]+)`", intro_line)
        if parent_match:
            parent_activity = clean_text(parent_match.group(1))

    if not parent_activity:
        for page in main_pages:
            if "eightmodesactivity" in page["title"].lower() or "8 ήχοι" in page["subtitle"].lower() or "8 ήχοι" in page["title"].lower():
                parent_activity = page["title"]
                break

    if not parent_activity and main_pages:
        parent_activity = main_pages[-1]["title"]

    return {
        "start_title": start_title,
        "start_summary": start_summary,
        "main_activity": main_activity,
        "main_pages": main_pages,
        "sub_pages": sub_pages,
        "sub_parent": parent_activity,
    }


def short_summary(text: str, max_len: int = 48) -> str:
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def xml_value(title: str, summary: str) -> str:
    return f"&lt;b&gt;{esc(title)}&lt;/b&gt;&lt;br/&gt;{esc(short_summary(summary))}"


def build_graph(parsed: dict):
    nodes: List[Node] = []
    edges: List[Edge] = []

    start_id = "n_start"
    main_id = "n_main"

    nodes.append(
        Node(
            node_id=start_id,
            title=parsed["start_title"],
            summary=parsed["start_summary"],
            x=520,
            y=20,
            w=250,
            h=64,
            style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;",
        )
    )

    main = parsed["main_activity"]
    nodes.append(
        Node(
            node_id=main_id,
            title=main["title"],
            summary=main["summary"] or "Κεντρική σελίδα",
            x=500,
            y=120,
            w=290,
            h=84,
            style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;",
        )
    )

    edges.append(
        Edge(
            edge_id="e_start_main",
            source=start_id,
            target=main_id,
            label="launch",
            style="endArrow=block;html=1;rounded=0;",
        )
    )

    pages = parsed["main_pages"]
    y_top = 290
    y_bottom = 410
    cols_top = min(5, len(pages))
    top_pages = pages[:cols_top]
    bottom_pages = pages[cols_top:]

    def place_row(row: List[dict], y: float, prefix: str):
        if not row:
            return []
        gap = 40
        w = 240
        total = len(row) * w + (len(row) - 1) * gap
        start_x = max(40, (1520 - total) / 2)
        ids = []
        for idx, page in enumerate(row):
            node_id = f"n_{prefix}_{idx}"
            ids.append((node_id, page))
            nodes.append(
                Node(
                    node_id=node_id,
                    title=page["title"],
                    summary=page["summary"] or "Σελίδα θεωρίας",
                    x=start_x + idx * (w + gap),
                    y=y,
                    w=w,
                    h=74,
                    style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;",
                )
            )
        return ids

    main_nodes = place_row(top_pages, y_top, "page_top") + place_row(bottom_pages, y_bottom, "page_bot")

    sub_parent_id = ""
    parent_title = parsed["sub_parent"].strip().lower()
    for node_id, page in main_nodes:
        if page["title"].strip().lower() == parent_title:
            sub_parent_id = node_id
            break

    for idx, (node_id, page) in enumerate(main_nodes):
        is_sub_parent = node_id == sub_parent_id
        label = "κουμπί"
        style = "endArrow=block;html=1;"
        if is_sub_parent:
            label = "κουμπί (υποσελίδες)"
            style = "endArrow=block;html=1;strokeColor=#b85450;"
            # tint node if it's sub parent
            for n in nodes:
                if n.node_id == node_id:
                    n.style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=13;"
        edges.append(
            Edge(
                edge_id=f"e_main_page_{idx}",
                source=main_id,
                target=node_id,
                label=label,
                style=style,
            )
        )

    sub_pages = parsed["sub_pages"]
    if sub_pages and sub_parent_id:
        cols = 4
        w = 190
        h = 72
        gap_x = 24
        gap_y = 26
        start_x = 760
        start_y = 560

        for idx, sub in enumerate(sub_pages):
            row = idx // cols
            col = idx % cols
            node_id = f"n_sub_{idx}"
            x = start_x + col * (w + gap_x)
            y = start_y + row * (h + gap_y)
            nodes.append(
                Node(
                    node_id=node_id,
                    title=sub["title"],
                    summary=sub["summary"] or "Υποσελίδα",
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;",
                )
            )
            edges.append(
                Edge(
                    edge_id=f"e_sub_{idx}",
                    source=sub_parent_id,
                    target=node_id,
                    label="selector",
                    style="endArrow=block;html=1;strokeColor=#9673a6;",
                )
            )

    return nodes, edges


def write_drawio(nodes: List[Node], edges: List[Edge], out_path: Path):
    mxfile = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2026-02-14T00:00:00.000Z",
        "agent": "codex-skill",
        "version": "24.7.17",
    })
    diagram = ET.SubElement(mxfile, "diagram", {"id": "auto-architecture", "name": "Architecture"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1860",
        "dy": "980",
        "grid": "1",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "1",
        "page": "1",
        "pageScale": "1",
        "pageWidth": "1920",
        "pageHeight": "1080",
        "math": "0",
        "shadow": "0",
    })

    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    for node in nodes:
        cell = ET.SubElement(root, "mxCell", {
            "id": node.node_id,
            "value": xml_value(node.title, node.summary),
            "style": node.style,
            "vertex": "1",
            "parent": "1",
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": f"{node.x}",
            "y": f"{node.y}",
            "width": f"{node.w}",
            "height": f"{node.h}",
            "as": "geometry",
        })

    for edge in edges:
        cell = ET.SubElement(root, "mxCell", {
            "id": edge.edge_id,
            "value": esc(edge.label),
            "style": edge.style,
            "edge": "1",
            "parent": "1",
            "source": edge.source,
            "target": edge.target,
        })
        ET.SubElement(cell, "mxGeometry", {
            "relative": "1",
            "as": "geometry",
        })

    out_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mxfile, encoding="unicode"), encoding="utf-8")


def export_png_with_drawio_cli(drawio_path: Path, png_path: Path, cli_path: str | None = None) -> bool:
    candidates: List[str] = []
    if cli_path:
        candidates.append(cli_path)

    detected = shutil.which("drawio")
    if detected:
        candidates.append(detected)

    local_cli = str(Path.home() / ".local/bin/drawio")
    if local_cli not in candidates and Path(local_cli).exists():
        candidates.append(local_cli)

    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "-x", "-f", "png", "-o", str(png_path), str(drawio_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and png_path.exists():
                return True
        except OSError:
            continue

    return False


def render_png(nodes: List[Node], edges: List[Edge], png_path: Path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Το export png απαιτεί Pillow (pip install pillow).") from exc

    def parse_style(style: str):
        out = {}
        for token in style.split(";"):
            if "=" in token:
                key, value = token.split("=", 1)
                out[key] = value
        return out

    max_x = max((n.x + n.w for n in nodes), default=1200)
    max_y = max((n.y + n.h for n in nodes), default=900)
    margin = 40

    image = Image.new("RGB", (int(max_x + margin * 2), int(max_y + margin * 2)), "white")
    draw = ImageDraw.Draw(image)

    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if font_path.exists():
        font_main = ImageFont.truetype(str(font_path), 18)
        font_sub = ImageFont.truetype(str(font_path), 15)
        font_edge = ImageFont.truetype(str(font_path), 13)
    else:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_edge = ImageFont.load_default()

    node_lookup = {n.node_id: n for n in nodes}

    for e in edges:
        s = node_lookup.get(e.source)
        t = node_lookup.get(e.target)
        if not s or not t:
            continue

        x1 = s.x + s.w / 2 + margin
        y1 = s.y + s.h / 2 + margin
        x2 = t.x + t.w / 2 + margin
        y2 = t.y + t.h / 2 + margin

        style = parse_style(e.style)
        color = style.get("strokeColor", "#666666")
        draw.line((x1, y1, x2, y2), fill=color, width=2)

        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        arrow = 10
        bx, by = x2 - ux * arrow, y2 - uy * arrow
        draw.polygon([(x2, y2), (bx + px * 4, by + py * 4), (bx - px * 4, by - py * 4)], fill=color)

        label = e.label.strip()
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            tw = draw.textlength(label, font=font_edge)
            draw.rectangle((mx - tw / 2 - 3, my - 10, mx + tw / 2 + 3, my + 10), fill="white")
            draw.text((mx - tw / 2, my - 8), label, fill="#444444", font=font_edge)

    for n in nodes:
        x0, y0 = n.x + margin, n.y + margin
        x1, y1 = x0 + n.w, y0 + n.h
        style = parse_style(n.style)
        fill = style.get("fillColor", "#f4f4f4")
        stroke = style.get("strokeColor", "#666666")
        draw.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=fill, outline=stroke, width=2)

        title = n.title
        summary = short_summary(n.summary, 58)
        wrapped_title = textwrap.wrap(title, width=22)[:2]
        wrapped_summary = textwrap.wrap(summary, width=30)[:2]

        y_cursor = y0 + 10
        for line in wrapped_title:
            tw = draw.textlength(line, font=font_main)
            draw.text((x0 + (n.w - tw) / 2, y_cursor), line, fill="#1a1a1a", font=font_main)
            y_cursor += 21

        for line in wrapped_summary:
            tw = draw.textlength(line, font=font_sub)
            draw.text((x0 + (n.w - tw) / 2, y_cursor), line, fill="#303030", font=font_sub)
            y_cursor += 18

    image.save(png_path)


def main():
    parser = argparse.ArgumentParser(
        description="Δημιούργησε ARCHITECTURE.drawio και ARCHITECTURE.png από το ARCHITECTURE.md"
    )
    parser.add_argument("--input", default="ARCHITECTURE.md", help="Input markdown architecture file")
    parser.add_argument("--drawio-output", default="ARCHITECTURE.drawio", help="Output .drawio file")
    parser.add_argument("--png-output", default="ARCHITECTURE.png", help="Output PNG file")
    parser.add_argument("--drawio-cli", default=None, help="Optional explicit path to drawio CLI binary")

    args = parser.parse_args()

    input_path = Path(args.input)
    drawio_path = Path(args.drawio_output)
    png_path = Path(args.png_output)

    if not input_path.exists():
        raise SystemExit(f"Δεν βρέθηκε το input αρχείο: {input_path}")

    parsed = parse_architecture_md(input_path)
    nodes, edges = build_graph(parsed)
    write_drawio(nodes, edges, drawio_path)
    used_cli = export_png_with_drawio_cli(drawio_path, png_path, args.drawio_cli)
    if not used_cli:
        render_png(nodes, edges, png_path)

    print(f"[OK] Drawio: {drawio_path}")
    if used_cli:
        print(f"[OK] PNG: {png_path} (via drawio CLI)")
    else:
        print(f"[OK] PNG: {png_path} (via Pillow fallback)")


if __name__ == "__main__":
    main()
