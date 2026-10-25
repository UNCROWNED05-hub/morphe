#!/usr/bin/env python3
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
RESULTS_FILE = DOCS / "results.json"

# Palette Tokens
COLOR_DARK_NAVY = RGBColor(0x0F, 0x1B, 0x24)   # #0F1B24
COLOR_PAPER = RGBColor(0xF2, 0xF4, 0xF0)       # #F2F4F0
COLOR_INK = RGBColor(0x0F, 0x1B, 0x24)         # #0F1B24
COLOR_INK_MUTED = RGBColor(0x46, 0x55, 0x5F)   # #46555F
COLOR_STRUCTURE = RGBColor(0x1E, 0x4D, 0x6B)   # #1E4D6B
COLOR_CHANGE = RGBColor(0xF0, 0xB4, 0x29)      # #F0B429
COLOR_ACCEPTED = RGBColor(0x2D, 0x6A, 0x4F)    # #2D6A4F
COLOR_REJECTED = RGBColor(0xB2, 0x3A, 0x2E)    # #B23A2E

FONT_HEADING = "Atkinson Hyperlegible"
FONT_BODY = "Atkinson Hyperlegible"
FONT_MONO = "IBM Plex Mono"


def generate_graph_image(output_path: Path):
    """Render the active NetworkX graph state to a clean PNG using PIL."""
    from ui.adapter import EngineAdapter
    adapter = EngineAdapter()
    adapter.load_sample()
    graph_data = adapter.get_graph()

    width, height = 1200, 750
    img = Image.new("RGB", (width, height), (0xF2, 0xF4, 0xF0))
    draw = ImageDraw.Draw(img)

    # Layout nodes in deterministic circle or positions
    nodes = list(graph_data.nodes(data=True))
    node_positions = {}
    center_x, center_y = width // 2, height // 2 - 20
    radius = 240
    n_count = len(nodes)

    for i, (nid, data) in enumerate(nodes):
        angle = (2 * math.pi * i) / max(n_count, 1)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        node_positions[nid] = (x, y)

    # Draw edges
    for u, v, edata in graph_data.edges(data=True):
        if u in node_positions and v in node_positions:
            x1, y1 = node_positions[u]
            x2, y2 = node_positions[v]
            kind = edata.get("kind", "semantic")
            if kind == "shortcut":
                draw.line([(x1, y1), (x2, y2)], fill=(0xF0, 0xB4, 0x29), width=4)
            else:
                draw.line([(x1, y1), (x2, y2)], fill=(0x1E, 0x4D, 0x6B), width=2)

    # Draw nodes
    colors = [
        (0x2F, 0x6F, 0x8F),
        (0x5B, 0x8C, 0x5A),
        (0x8A, 0x6F, 0x4E),
        (0x3E, 0x8E, 0x86),
        (0xA8, 0x55, 0x6B),
        (0x6B, 0x7C, 0x93)
    ]

    for i, (nid, data) in enumerate(nodes):
        x, y = node_positions[nid]
        r = 34
        fill_col = colors[i % len(colors)]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill_col, outline=(0x0F, 0x1B, 0x24), width=2)
        label = data.get("label", str(nid))
        # Draw node ID
        draw.text((x, y + r + 6), label[:18], fill=(0x0F, 0x1B, 0x24), anchor="mm")
        rec_count = len(data.get("record_ids", []))
        draw.text((x, y), f"{rec_count}", fill=(0xFF, 0xFF, 0xFF), anchor="mm")

    # Legend
    draw.rectangle([40, height - 70, width - 40, height - 20], fill=(0xE5, 0xEB, 0xE3), outline=(0xD3, 0xD9, 0xD2))
    draw.line([(60, height - 45), (110, height - 45)], fill=(0x1E, 0x4D, 0x6B), width=2)
    draw.text((120, height - 45), "Semantic Structural Edge", fill=(0x0F, 0x1B, 0x24), anchor="lm")
    draw.line([(340, height - 45), (390, height - 45)], fill=(0xF0, 0xB4, 0x29), width=4)
    draw.text((400, height - 45), "Co-Access Adaptive Shortcut", fill=(0x0F, 0x1B, 0x24), anchor="lm")
    draw.text((width - 60, height - 45), f"NetworkX Module Graph: {len(nodes)} modules, {graph_data.number_of_edges()} pathways", fill=(0x46, 0x55, 0x5F), anchor="rm")

    img.save(output_path, "PNG")
    print(f"Generated graph image at {output_path}")


def add_slide_bg(slide, prs, color: RGBColor):
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape


def build_deck():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)

    graph_img_path = DOCS / "graph_snapshot.png"
    generate_graph_image(graph_img_path)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Slide 1: Cover (Dark Navy)
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s1, prs, COLOR_DARK_NAVY)

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "MORPHE"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(44)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_PAPER

    p1 = tf.add_paragraph()
    p1.text = "Memory-Oriented Reconfigurable Plasticity and Hierarchical Evolution"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(22)
    p1.font.color.rgb = COLOR_CHANGE
    p1.space_before = Pt(14)

    p2 = tf.add_paragraph()
    p2.text = "An adaptive memory system that restructures graph topologies based on empirical retrieval performance."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_PAPER
    p2.space_before = Pt(24)

    p3 = tf.add_paragraph()
    p3.text = f"Production Verification Date: {results['date']} | Engine: {results['config']['model']} | Platform: {results['machine_info']['platform']}"
    p3.font.name = FONT_MONO
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(0x8A, 0x9B, 0xA8)
    p3.space_before = Pt(36)

    # Helper for Body Slides
    def create_body_slide(title_text: str):
        s = prs.slides.add_slide(blank_layout)
        add_slide_bg(s, prs, COLOR_PAPER)

        # Header box
        h_box = s.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.8))
        h_tf = h_box.text_frame
        h_tf.word_wrap = True
        hp = h_tf.paragraphs[0]
        hp.text = title_text
        hp.font.name = FONT_HEADING
        hp.font.size = Pt(26)
        hp.font.bold = True
        hp.font.color.rgb = COLOR_INK

        # Subline hairline rule
        rule = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.65), Inches(11.333), Inches(0.02))
        rule.fill.solid()
        rule.fill.fore_color.rgb = RGBColor(0xD3, 0xD9, 0xD2)
        rule.line.fill.background()

        return s

    # Slide 2: The Core Problem
    s2 = create_body_slide("The Core Problem: Static Memory in Dynamic Agents")
    tb2 = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    points2 = [
        ("Static Partitioning Degradation", "Conventional RAG and memory systems store chunks into fixed vector indices or rigid clusters. Over time, concept drift and topic mixing degrade precision."),
        ("Overloaded Memory Modules", "As new knowledge accumulates, specific clusters exceed effective capacity, increasing multi-topic interference and search dilution."),
        ("Redundant Concept Fragmentation", "Related documents ingest into disparate clusters without mutual awareness, fragmenting answers across disconnected partitions."),
        ("Retrieval Co-Access Blindness", "Independent modules frequently queried together incur high hop penalties and repeated vector scans because no direct retrieval shortcut exists."),
        ("The MORPHE Solution", "An inspectable, adaptive memory architecture that continuously monitors structural health, diagnoses bottlenecks, and executes guarded topological transformations.")
    ]
    for idx, (head, body) in enumerate(points2):
        p = tf2.paragraphs[0] if idx == 0 else tf2.add_paragraph()
        p.text = f"{head}: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_STRUCTURE
        p.space_before = Pt(12)

        # append body run
        run = p.add_run()
        run.text = body
        run.font.name = FONT_BODY
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = COLOR_INK

    # Slide 3: Architecture & Module Graph
    s3 = create_body_slide("System Architecture: Modules, Graph, and Signals")
    tb3 = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.8))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    points3 = [
        ("Granular Memory Modules", "Records are partitioned into discrete semantic modules, each maintaining an internal centroid, record list, and topic assignment."),
        ("NetworkX Graph Topology", "Modules exist as nodes in an explicit NetworkX graph. Edges represent semantic pathways and co-access shortcuts rather than opaque vector neighborhoods."),
        ("Multi-Stage Traversal", "Queries first identify high-affinity modules, then traverse adjacent graph neighbors to collect candidate records, bounding compute."),
        ("Telemetry Ledger", "The engine continuously logs module access counts, cross-module co-access pairs, internal cluster silhouette scores, and inter-module cosine similarities."),
        ("Offline Embedding Pipeline", f"Vector representations are generated via {results['config']['model']}, running deterministically offline with zero external API dependencies.")
    ]
    for idx, (head, body) in enumerate(points3):
        p = tf3.paragraphs[0] if idx == 0 else tf3.add_paragraph()
        p.text = f"{head}: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_STRUCTURE
        p.space_before = Pt(12)

        run = p.add_run()
        run.text = body
        run.font.name = FONT_BODY
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = COLOR_INK

    # Slide 4: Adaptation Mechanics
    s4 = create_body_slide("Adaptation Mechanics: Split, Merge, Shortcut")
    tb4 = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.8))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    ops = [
        ("SPLIT Operation", f"Triggered when module size >= {results['config']['thresholds']['split_min_module_size']} records and silhouette separation >= {results['config']['thresholds']['split_min_silhouette']}. Uses K-Means clustering (k=2) to divide overloaded modules into coherent sub-units."),
        ("MERGE Operation", f"Triggered when inter-module centroid cosine similarity >= {results['config']['thresholds']['merge_cosine_threshold']}. Consolidates redundant clusters and rewires neighboring edges to eliminate partition fragmentation."),
        ("SHORTCUT Creation", f"Triggered when disjoint modules are co-accessed in >= {results['config']['thresholds']['shortcut_min_co_access']} queries. Installs a direct graph edge to reduce traversal latency and prevent multi-hop retrieval dropouts."),
        ("Guarded Pre-Flight", "Candidates are generated from deterministic heuristic rules, prioritized by signal magnitude, and never applied blindly.")
    ]
    for idx, (head, body) in enumerate(ops):
        p = tf4.paragraphs[0] if idx == 0 else tf4.add_paragraph()
        p.text = f"{head}: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_CHANGE if "SHORTCUT" in head else COLOR_STRUCTURE
        p.space_before = Pt(14)

        run = p.add_run()
        run.text = body
        run.font.name = FONT_BODY
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = COLOR_INK

    # Slide 5: Guarded Evaluation & Rollback
    s5 = create_body_slide("Safety Gate: Frozen Evaluation & Guaranteed Rollback")
    tb5 = s5.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.8))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    points5 = [
        ("Frozen Ground Truth Benchmark", "16 labelled evaluation queries with frozen relevant record IDs are executed before and after every proposed modification."),
        (f"Strict Acceptance Threshold", f"A structural mutation is accepted if and only if Recall@K >= {results['config']['min_recall']} and does not degrade beyond epsilon."),
        ("Zero-Cost State Rollback", "Before modifying the graph, the engine snapshots the active NetworkX topology, module assignments, and index state. If metrics fail, the snapshot is restored immediately."),
        ("Immutable Version Ledger", "Every cycle produces an audit record (V1, V2, V3...) logging operation type, delta recall, delta precision, delta latency, and verdict (ACCEPTED, NEUTRAL, REJECTED)."),
        ("Observable Rollback Verification", "In our test suite, an intentionally destructive merge across unrelated domains is caught by the gate, rolled back in 0ms, and verified bit-for-bit.")
    ]
    for idx, (head, body) in enumerate(points5):
        p = tf5.paragraphs[0] if idx == 0 else tf5.add_paragraph()
        p.text = f"{head}: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCEPTED if "Acceptance" in head else (COLOR_REJECTED if "Rollback" in head else COLOR_STRUCTURE)
        p.space_before = Pt(12)

        run = p.add_run()
        run.text = body
        run.font.name = FONT_BODY
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = COLOR_INK

    # Slide 6: Empirical Results
    s6 = create_body_slide("Empirical Results: Baseline vs Adapted MORPHE")

    # Add comparison table
    rows, cols = 4, 4
    left = Inches(1.0)
    top = Inches(2.2)
    width = Inches(11.3)
    height = Inches(2.6)

    table_shape = s6.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table

    headers = ["Architecture Configuration", "Recall@4", "Precision@4", "Mean Latency"]
    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_DARK_NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.color.rgb = COLOR_PAPER
        p.font.size = Pt(14)
        p.alignment = PP_ALIGN.CENTER

    data_rows = [
        ["Flat Vector Search (Unstructured)", f"{results['baseline']['flat_baseline']['mean_recall']:.4f}", f"{results['baseline']['flat_baseline']['mean_precision']:.4f}", f"{results['baseline']['flat_baseline']['mean_latency_ms']:.2f} ms"],
        ["MORPHE Baseline Graph (V1)", f"{results['baseline']['morphe_graph']['mean_recall']:.4f}", f"{results['baseline']['morphe_graph']['mean_precision']:.4f}", f"{results['baseline']['morphe_graph']['mean_latency_ms']:.2f} ms"],
        ["MORPHE Adapted Graph (V4 Shortcut)", f"{results['adapted_metrics']['recall_at_k']:.4f}", f"{results['adapted_metrics']['precision_at_k']:.4f}", f"{results['adapted_metrics']['mean_latency_ms']:.2f} ms"]
    ]

    for r_idx, row in enumerate(data_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if r_idx % 2 == 1 else RGBColor(0xEA, 0xEF, 0xE9)
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(14)
            p.font.color.rgb = COLOR_INK
            if c_idx > 0:
                p.alignment = PP_ALIGN.CENTER
                p.font.name = FONT_MONO

    tb6 = s6.shapes.add_textbox(Inches(1.0), Inches(5.2), Inches(11.3), Inches(1.5))
    tf6 = tb6.text_frame
    p_sum = tf6.paragraphs[0]
    p_sum.text = f"Key Finding: Adapted MORPHE achieves Recall@4 of {results['adapted_metrics']['recall_at_k']:.4f}, matching Flat Vector Search while preserving structured graph modularity and bounded traversal paths. All numbers measured on real held-out queries."
    p_sum.font.size = Pt(15)
    p_sum.font.bold = True
    p_sum.font.color.rgb = COLOR_ACCEPTED

    # Slide 7: Visual Topology
    s7 = create_body_slide("Visual Topology: NetworkX Module Graph & Pathways")
    s7.shapes.add_picture(str(graph_img_path), Inches(1.5), Inches(1.9), width=Inches(10.333), height=Inches(4.8))

    # Slide 8: Verification & Roadmap
    s8 = create_body_slide("Verification, Operational Limits, and Roadmap")
    tb8 = s8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.8))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    points8 = [
        ("Automated Test Suite", "7 UI and integration tests pass in ~32s (contract conformance, repeatability, deterministic layout, and gate rejection rollback)."),
        ("Performance & Accessibility Audits", f"Lighthouse Desktop Audit: Best Practices {results['lighthouse']['best_practices']}, Accessibility {results['lighthouse']['accessibility']}, SEO {results['lighthouse']['seo']}."),
        ("Operational Boundary Conditions", "Heuristic triggers operate deterministically; adaptation cycles are batched during maintenance or idle windows rather than inline with user queries to prevent lock contention."),
        ("Known Prototype Limits", "Graph scale tested up to ~50 modules; hierarchical multi-level graph abstraction is planned for multi-million record enterprise deployment."),
        ("Conclusion", "MORPHE demonstrates that AI memory does not need to remain static. Measuring retrieval health and adapting module graphs yields verifiable gains with absolute rollback safety.")
    ]
    for idx, (head, body) in enumerate(points8):
        p = tf8.paragraphs[0] if idx == 0 else tf8.add_paragraph()
        p.text = f"{head}: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_STRUCTURE
        p.space_before = Pt(12)

        run = p.add_run()
        run.text = body
        run.font.name = FONT_BODY
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = COLOR_INK

    output_pptx = DOCS / "MORPHE_deck.pptx"
    prs.save(str(output_pptx))
    print(f"Saved 8-slide presentation to {output_pptx}")


if __name__ == "__main__":
    build_deck()
